/**
 * Auto-Cron — Background lifecycle processor for QPredict
 *
 * Runs the escrow lifecycle every 15 seconds in the background.
 * Starts automatically on first import from any predict API route.
 */

import crypto from 'crypto'
import {
  getAwaitingDepositEscrows,
  getActiveInScEscrows,
  getAwaitingSweepEscrows,
  getSweepingEscrows,
  getJoiningScEscrows,
  checkEscrowDeposit,
  executeJoinBet,
  verifyJoinBetConfirmation,
  checkEscrowPayout,
  executeSweep,
  verifySweepConfirmation,
  handleExpiredEscrows,
} from './escrow-manager'
import { getMarketDB } from './market-db'
import {
  closeExpiredBetting,
  getMarketsReadyForResolution,
  resolveMarketViaOracle,
  repairCommitmentHashes,
  repairSlotCounts,
  discoverPendingBetIds,
} from './market-manager'
import { rpcBreaker } from './circuit-breaker'
import { runBackupIfDue } from './db-backup'
import { recoverOrphanedEscrows } from './escrow-recovery'
import { handleStuckMarkets } from './market-manager'
import { cronLog } from './logger'
import { sendAlert } from './alerting'
import { isShuttingDown, setInflightCron, clearInflightCron } from './shutdown'

const CRON_INTERVAL_MS = 15_000 // 15 seconds

let cronStarted = false
let cronTimer: ReturnType<typeof setInterval> | null = null

export interface CronResults {
  marketsClosed: number
  marketsResolved: number
  betIdsDiscovered: number
  depositsChecked: number
  depositsFound: number
  joinBetsAttempted: number
  joinBetsSucceeded: number
  payoutsChecked: number
  payoutsFound: number
  sweepsAttempted: number
  sweepsSucceeded: number
  joinBetConfirmations: number
  joinBetReverts: number
  sweepConfirmations: number
  expiredHandled: number
  commitmentsRepaired: number
  slotsRepaired: number
  stuckMarketsRecovered: number
  escrowsRecovered: number
  backupPerformed: boolean
  rpcSkipped: boolean
  errors: string[]
}

/** Unique ID for this process — used for cron lock ownership */
const PROCESS_ID = crypto.randomBytes(8).toString('hex')

/**
 * Run one full cron cycle — all lifecycle phases.
 */
/** Monotonic cycle counter for backup scheduling */
let _cycleCount = 0

export async function runCronCycle(): Promise<CronResults> {
  _cycleCount++

  const results: CronResults = {
    marketsClosed: 0,
    marketsResolved: 0,
    betIdsDiscovered: 0,
    depositsChecked: 0,
    depositsFound: 0,
    joinBetsAttempted: 0,
    joinBetsSucceeded: 0,
    payoutsChecked: 0,
    payoutsFound: 0,
    sweepsAttempted: 0,
    sweepsSucceeded: 0,
    joinBetConfirmations: 0,
    joinBetReverts: 0,
    sweepConfirmations: 0,
    expiredHandled: 0,
    commitmentsRepaired: 0,
    slotsRepaired: 0,
    stuckMarketsRecovered: 0,
    escrowsRecovered: 0,
    backupPerformed: false,
    rpcSkipped: false,
    errors: [],
  }

  const db = getMarketDB()

  // ─── Single-Instance Lock ─────────────────────────────────────────────
  // Prevents concurrent cron runs from causing double sweeps, double joinBets, etc.
  const lockAcquired = db.acquireCronLock('qpredict_cron', PROCESS_ID, 30)
  if (!lockAcquired) {
    return results // Another instance is running — skip silently
  }

  try {
    // Phase 0: Repair commitment hashes + slot counts
    try {
      results.commitmentsRepaired = repairCommitmentHashes()
      results.slotsRepaired = repairSlotCounts()
    } catch (err) {
      results.errors.push(`Phase 0: ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 0a: Close expired betting
    try {
      results.marketsClosed = closeExpiredBetting()
      if (results.marketsClosed > 0) {
        cronLog.info({ count: results.marketsClosed }, 'closed markets for betting')
      }
    } catch (err) {
      results.errors.push(`Phase 0a: ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 0d: Handle stuck markets (pending_tx, resolving, betId=0)
    try {
      results.stuckMarketsRecovered = await handleStuckMarkets()
      if (results.stuckMarketsRecovered > 0) {
        cronLog.info({ count: results.stuckMarketsRecovered }, 'recovered stuck markets')
      }
    } catch (err) {
      results.errors.push(`Phase 0d: ${err instanceof Error ? err.message : String(err)}`)
    }

    // ── Circuit breaker gate ──────────────────────────────────────────────
    // Phases 0b-4b make RPC calls. Skip them when the breaker is open to
    // avoid hammering an unhealthy node.
    const rpcHealthy = rpcBreaker.isHealthy()
    if (!rpcHealthy) {
      results.rpcSkipped = true
      cronLog.warn({ state: rpcBreaker.getState() }, 'RPC circuit open — skipping RPC phases')
    }

    if (rpcHealthy) {
      // Phase 0b: Auto-resolve markets past endDate
      try {
        const readyMarkets = getMarketsReadyForResolution()
        for (const market of readyMarkets) {
          try {
            const result = await resolveMarketViaOracle(market)
            if (result.success) {
              results.marketsResolved++
              cronLog.info({ marketId: market.id, winner: result.winningOption }, 'resolved market')
            } else {
              cronLog.warn({ marketId: market.id, error: result.error }, 'could not resolve market')
            }
          } catch (err) {
            results.errors.push(`Resolve ${market.id}: ${err instanceof Error ? err.message : String(err)}`)
          }
        }
      } catch (err) {
        results.errors.push(`Phase 0b: ${err instanceof Error ? err.message : String(err)}`)
      }

      // Phase 0c: Discover pending betIds (markets with quotteryBetId = 0)
      try {
        results.betIdsDiscovered = await discoverPendingBetIds()
        if (results.betIdsDiscovered > 0) {
          cronLog.info({ count: results.betIdsDiscovered }, 'discovered pending betIds')
        }
      } catch (err) {
        results.errors.push(`Phase 0c: ${err instanceof Error ? err.message : String(err)}`)
      }

      // Phase 1: Check for deposits
      try {
        const awaiting = getAwaitingDepositEscrows()
        results.depositsChecked = awaiting.length
        for (const escrow of awaiting) {
          try {
            const balance = await checkEscrowDeposit(escrow.id)
            if (balance > 0n) results.depositsFound++
          } catch (err) {
            results.errors.push(`Deposit ${escrow.id}: ${err instanceof Error ? err.message : String(err)}`)
          }
        }
      } catch (err) {
        results.errors.push(`Phase 1: ${err instanceof Error ? err.message : String(err)}`)
      }

      // Phase 2: Execute joinBets
      try {
        const depositDetected = db.getEscrowsByStatus('deposit_detected')
        results.joinBetsAttempted = depositDetected.length
        for (const escrow of depositDetected) {
          try {
            const result = await executeJoinBet(escrow.id)
            if (result.success) {
              results.joinBetsSucceeded++
              cronLog.info({ escrowId: escrow.id, txId: result.txId }, 'joinBet success')
            } else {
              results.errors.push(`joinBet ${escrow.id}: ${result.error}`)
            }
          } catch (err) {
            results.errors.push(`joinBet ${escrow.id}: ${err instanceof Error ? err.message : String(err)}`)
          }
        }
      } catch (err) {
        results.errors.push(`Phase 2: ${err instanceof Error ? err.message : String(err)}`)
      }

      // Phase 2b: Verify joinBet TX confirmations (joining_sc → active_in_sc)
      try {
        const joiningEscrows = getJoiningScEscrows()
        for (const escrow of joiningEscrows) {
          try {
            const result = await verifyJoinBetConfirmation(escrow.id)
            if (result.confirmed) {
              results.joinBetConfirmations++
              cronLog.info({ escrowId: escrow.id }, 'joinBet confirmed on-chain')
            } else if (result.error?.includes('reverted')) {
              results.joinBetReverts++
              cronLog.warn({ escrowId: escrow.id, error: result.error }, 'joinBet reverted')
            }
          } catch (err) {
            results.errors.push(`JoinBetConfirm ${escrow.id}: ${err instanceof Error ? err.message : String(err)}`)
          }
        }
      } catch (err) {
        results.errors.push(`Phase 2b: ${err instanceof Error ? err.message : String(err)}`)
      }

      // Phase 3: Check for payouts
      try {
        const active = getActiveInScEscrows()
        results.payoutsChecked = active.length
        for (const escrow of active) {
          try {
            const payout = await checkEscrowPayout(escrow.id)
            if (payout > 0n) results.payoutsFound++
          } catch (err) {
            results.errors.push(`Payout ${escrow.id}: ${err instanceof Error ? err.message : String(err)}`)
          }
        }
      } catch (err) {
        results.errors.push(`Phase 3: ${err instanceof Error ? err.message : String(err)}`)
      }

      // Phase 4: Execute sweeps (won_awaiting_sweep → sweeping)
      try {
        const awaitingSweep = getAwaitingSweepEscrows()
        results.sweepsAttempted = awaitingSweep.length
        for (const escrow of awaitingSweep) {
          try {
            const result = await executeSweep(escrow.id)
            if (result.success) {
              results.sweepsSucceeded++
              cronLog.info({ escrowId: escrow.id, amountQu: result.amountQu, tick: result.tick }, 'sweep broadcast')
            } else {
              results.errors.push(`Sweep ${escrow.id}: ${result.error}`)
            }
          } catch (err) {
            results.errors.push(`Sweep ${escrow.id}: ${err instanceof Error ? err.message : String(err)}`)
          }
        }
      } catch (err) {
        results.errors.push(`Phase 4: ${err instanceof Error ? err.message : String(err)}`)
      }

      // Phase 4b: Verify sweep TX confirmations (sweeping → swept)
      try {
        const sweeping = getSweepingEscrows()
        for (const escrow of sweeping) {
          try {
            const result = await verifySweepConfirmation(escrow.id)
            if (result.confirmed) {
              results.sweepConfirmations++
              cronLog.info({ escrowId: escrow.id }, 'sweep confirmed')
            }
          } catch (err) {
            results.errors.push(`SweepConfirm ${escrow.id}: ${err instanceof Error ? err.message : String(err)}`)
          }
        }
      } catch (err) {
        results.errors.push(`Phase 4b: ${err instanceof Error ? err.message : String(err)}`)
      }
    } // end rpcHealthy gate

    // Phase 5: Handle expired escrows (async — checks balance before archiving)
    try {
      results.expiredHandled = await handleExpiredEscrows()
    } catch (err) {
      results.errors.push(`Phase 5: ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 6.5: Recover orphaned escrows (joining_sc, sweeping, won_awaiting_sweep)
    try {
      const recovery = await recoverOrphanedEscrows()
      results.escrowsRecovered = recovery.recovered
      if (recovery.recovered > 0) {
        cronLog.info({ recovered: recovery.recovered, checked: recovery.checked }, 'recovered orphaned escrows')
      }
    } catch (err) {
      results.errors.push(`Phase 6.5: ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 6: Cleanup expired nonces + idempotency keys (every cycle)
    try {
      db.cleanExpiredNonces()
      db.cleanExpiredIdempotencyKeys()
    } catch (err) {
      results.errors.push(`Phase 6 cleanup: ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 7: Database backup (every 100 cycles ≈ 25 min)
    try {
      const backupResult = runBackupIfDue(_cycleCount)
      if (backupResult) {
        results.backupPerformed = backupResult.success
        if (!backupResult.success) {
          results.errors.push(`Backup: ${backupResult.error}`)
        }
      }
    } catch (err) {
      results.errors.push(`Phase 7 backup: ${err instanceof Error ? err.message : String(err)}`)
    }
  } finally {
    // Always release the lock
    db.releaseCronLock('qpredict_cron', PROCESS_ID)

    // Record cron run timestamp + errors for health/admin endpoints
    try {
      db.setSystemStatus('last_cron_run', new Date().toISOString())
      if (results.errors.length > 0) {
        db.setSystemStatus('last_cron_errors', JSON.stringify(results.errors.slice(0, 20)))
      }
    } catch {
      // Best-effort — don't let status tracking break the cron
    }
  }

  return results
}

/**
 * Start the background cron if not already running.
 * Safe to call multiple times — only starts once.
 */
export function ensureAutoCron(): void {
  if (cronStarted) return
  cronStarted = true

  cronLog.info({ intervalMs: CRON_INTERVAL_MS }, 'starting background cron')

  cronTimer = setInterval(async () => {
    if (isShuttingDown()) return

    const cyclePromise = (async () => {
      try {
        const results = await runCronCycle()
        const hasActivity =
          results.marketsClosed > 0 ||
          results.marketsResolved > 0 ||
          results.betIdsDiscovered > 0 ||
          results.depositsFound > 0 ||
          results.joinBetsSucceeded > 0 ||
          results.joinBetConfirmations > 0 ||
          results.joinBetReverts > 0 ||
          results.payoutsFound > 0 ||
          results.sweepsSucceeded > 0 ||
          results.sweepConfirmations > 0 ||
          results.expiredHandled > 0 ||
          results.slotsRepaired > 0 ||
          results.stuckMarketsRecovered > 0 ||
          results.escrowsRecovered > 0 ||
          results.backupPerformed

        if (hasActivity) {
          cronLog.info(results, 'cycle complete')
        }

        if (results.errors.length > 0) {
          cronLog.warn({ errors: results.errors }, 'cycle errors')
          void sendAlert(
            'cron_error',
            'warning',
            `Cron cycle had ${results.errors.length} error(s)`,
            { errors: results.errors.slice(0, 5).join('; ') },
          )
        }
      } catch (err) {
        cronLog.error({ err }, 'cycle fatal error')
      }
    })()

    setInflightCron(cyclePromise)
    await cyclePromise
    clearInflightCron()
  }, CRON_INTERVAL_MS)

  // Don't prevent Node from exiting
  if (cronTimer && typeof cronTimer === 'object' && 'unref' in cronTimer) {
    cronTimer.unref()
  }
}

/**
 * Stop the background cron timer. Called during graceful shutdown.
 */
export function stopAutoCron(): void {
  if (cronTimer) {
    clearInterval(cronTimer)
    cronTimer = null
    cronStarted = false
    cronLog.info('auto-cron stopped')
  }
}
