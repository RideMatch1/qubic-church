/**
 * QPredict Orphaned Escrow Recovery
 *
 * Detects and recovers escrows stuck in intermediate states due to
 * process restarts, RPC failures, or other transient issues.
 *
 * Called as Phase 6.5 in the auto-cron loop.
 *
 * Orphaned states detected:
 *   1. joining_sc  — depositDetectedAt > 30 min ago, joinBet never confirmed.
 *   2. sweeping    — sweepTxId is null AND createdAt > 15 min ago, sweep never broadcast.
 *   3. won_awaiting_sweep — payoutDetectedAt > 2 hours ago, sweep never initiated.
 */

import { getMarketDB } from './market-db'
import { getBalance } from '@/lib/qubic/quottery-client'
import { escrowLog } from './logger'
import { parseUtcTimestamp } from './api-utils'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface RecoveryResult {
  checked: number
  recovered: number
  actions: string[]
}

// ---------------------------------------------------------------------------
// Thresholds (minutes)
// ---------------------------------------------------------------------------

/** How long an escrow can sit in joining_sc before we consider it orphaned. */
const JOINING_SC_ORPHAN_MINUTES = 30

/** How long a sweeping escrow with no sweepTxId can sit before revert. */
const SWEEPING_ORPHAN_MINUTES = 15

/** How long a won_awaiting_sweep escrow can wait before we emit a warning. */
const WON_AWAITING_SWEEP_WARN_MINUTES = 120

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Calculate how many minutes have elapsed since the given timestamp.
 * Uses parseUtcTimestamp to correctly handle SQLite's `datetime('now')`
 * which stores UTC times without a 'Z' suffix.
 */
function minutesAgo(isoTimestamp: string): number {
  return (Date.now() - parseUtcTimestamp(isoTimestamp).getTime()) / (1000 * 60)
}

// ---------------------------------------------------------------------------
// Main Recovery Function
// ---------------------------------------------------------------------------

/**
 * Scan for and recover orphaned escrows.
 *
 * This function is safe to call repeatedly -- it only acts on escrows that
 * have exceeded the configured time thresholds and uses the same atomic
 * DB transitions that the regular cron phases use.
 */
export async function recoverOrphanedEscrows(): Promise<RecoveryResult> {
  const result: RecoveryResult = {
    checked: 0,
    recovered: 0,
    actions: [],
  }

  const db = getMarketDB()

  // ─── 1. Orphaned joining_sc ────────────────────────────────────────────
  // Escrows where joinBet was broadcast but never confirmed/reverted.
  // After 30 minutes, check the on-chain balance to determine next state.
  try {
    const joiningEscrows = db.getEscrowsByStatus('joining_sc')
    result.checked += joiningEscrows.length

    for (const escrow of joiningEscrows) {
      // Only act on escrows whose deposit was detected >30 min ago.
      // If depositDetectedAt is null we fall back to createdAt as a safety net.
      const anchorTimestamp = escrow.depositDetectedAt ?? escrow.createdAt
      if (minutesAgo(anchorTimestamp) < JOINING_SC_ORPHAN_MINUTES) {
        continue
      }

      try {
        const balance = await getBalance(escrow.escrowAddress)

        if (balance === 0n) {
          // Escrow balance is 0 -- the SC consumed the funds.
          // Transition joining_sc -> active_in_sc.
          const confirmed = db.confirmJoinBet(escrow.id)
          if (confirmed) {
            const action = `joining_sc->active_in_sc: ${escrow.id} (balance 0, SC consumed funds)`
            result.actions.push(action)
            result.recovered++
            escrowLog.info(
              { escrowId: escrow.id, marketId: escrow.marketId, age: Math.round(minutesAgo(anchorTimestamp)) },
              'recovery: orphaned joining_sc promoted to active_in_sc (balance=0)',
            )
          }
        } else {
          // Funds still sitting in the escrow -- joinBet was never executed
          // or was rejected. Revert to deposit_detected for retry.
          db.revertJoinBet(escrow.id)
          const action = `joining_sc->deposit_detected: ${escrow.id} (balance ${balance}, reverting for retry)`
          result.actions.push(action)
          result.recovered++
          escrowLog.info(
            { escrowId: escrow.id, marketId: escrow.marketId, balance: balance.toString(), age: Math.round(minutesAgo(anchorTimestamp)) },
            'recovery: orphaned joining_sc reverted to deposit_detected (funds still present)',
          )
        }
      } catch (err) {
        // RPC failure checking balance -- log and continue to next escrow.
        escrowLog.warn(
          { escrowId: escrow.id, err: err instanceof Error ? err.message : String(err) },
          'recovery: failed to check balance for orphaned joining_sc escrow',
        )
      }
    }
  } catch (err) {
    escrowLog.error(
      { err: err instanceof Error ? err.message : String(err) },
      'recovery: failed to query joining_sc escrows',
    )
  }

  // ─── 2. Orphaned sweeping (no sweepTxId) ───────────────────────────────
  // Escrows that were claimed for sweeping but the TX was never broadcast.
  // After 15 minutes, revert to won_awaiting_sweep so Phase 4 retries.
  try {
    const sweepingEscrows = db.getEscrowsByStatus('sweeping')
    result.checked += sweepingEscrows.length

    for (const escrow of sweepingEscrows) {
      // Only target escrows where sweepTxId was never recorded.
      if (escrow.sweepTxId !== null) {
        continue
      }

      if (minutesAgo(escrow.createdAt) < SWEEPING_ORPHAN_MINUTES) {
        continue
      }

      db.revertSweepClaim(escrow.id)
      const action = `sweeping->won_awaiting_sweep: ${escrow.id} (no sweepTxId after ${SWEEPING_ORPHAN_MINUTES}min)`
      result.actions.push(action)
      result.recovered++
      escrowLog.info(
        { escrowId: escrow.id, marketId: escrow.marketId, age: Math.round(minutesAgo(escrow.createdAt)) },
        'recovery: orphaned sweeping reverted to won_awaiting_sweep (no sweep TX recorded)',
      )
    }
  } catch (err) {
    escrowLog.error(
      { err: err instanceof Error ? err.message : String(err) },
      'recovery: failed to query sweeping escrows',
    )
  }

  // ─── 3. Stale won_awaiting_sweep (warning only) ───────────────────────
  // Escrows that have been waiting for a sweep for over 2 hours.
  // The regular Phase 4 should handle these, but log a warning for visibility.
  try {
    const awaitingSweep = db.getEscrowsByStatus('won_awaiting_sweep')
    result.checked += awaitingSweep.length

    for (const escrow of awaitingSweep) {
      const anchorTimestamp = escrow.payoutDetectedAt ?? escrow.createdAt
      if (minutesAgo(anchorTimestamp) < WON_AWAITING_SWEEP_WARN_MINUTES) {
        continue
      }

      const ageMinutes = Math.round(minutesAgo(anchorTimestamp))
      escrowLog.warn(
        {
          escrowId: escrow.id,
          marketId: escrow.marketId,
          payoutAmountQu: escrow.payoutAmountQu,
          ageMinutes,
        },
        `recovery: won_awaiting_sweep escrow stale for ${ageMinutes}min — Phase 4 should pick this up`,
      )
    }
  } catch (err) {
    escrowLog.error(
      { err: err instanceof Error ? err.message : String(err) },
      'recovery: failed to query won_awaiting_sweep escrows',
    )
  }

  // ─── Summary ───────────────────────────────────────────────────────────
  if (result.recovered > 0) {
    escrowLog.info(
      { checked: result.checked, recovered: result.recovered, actions: result.actions },
      'escrow recovery cycle complete',
    )
  }

  return result
}
