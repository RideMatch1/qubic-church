/**
 * QFlash Background Cron
 *
 * 5-second interval that manages the round lifecycle pipeline.
 * Starts automatically on first import from any QFlash API route.
 * Follows the auto-cron.ts pattern: singleton, lock, phases, shutdown-aware.
 */

import crypto from 'crypto'
import { getQFlashDB } from './qflash-db'
import {
  ensureUpcomingRounds,
  openReadyRounds,
  lockReadyRounds,
  resolveReadyRounds,
  handleStaleResolvingRounds,
} from './round-engine'
import { initializeHouseAccount } from './house-bank'
import { checkPlatformBalance, processPendingWithdrawals } from './balance-manager'
import { getPrice } from './price-feed'
import { getPriceHistory } from './price-history'
import { QFLASH_CONFIG, getEnabledPairs } from './config'
import { isShuttingDown } from '../predict/shutdown'
import type { QFlashCronResults } from './types'

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let cronStarted = false
let cronTimer: ReturnType<typeof setInterval> | null = null
const PROCESS_ID = crypto.randomBytes(8).toString('hex')

// ---------------------------------------------------------------------------
// Cron Cycle
// ---------------------------------------------------------------------------

/**
 * Run one full cron cycle — all lifecycle phases.
 */
export async function runQFlashCronCycle(): Promise<QFlashCronResults> {
  const results: QFlashCronResults = {
    roundsCreated: 0,
    roundsOpened: 0,
    roundsLocked: 0,
    roundsResolved: 0,
    roundsSettled: 0,
    roundsCancelled: 0,
    depositsDetected: 0,
    withdrawalsProcessed: 0,
    errors: [],
  }

  const db = getQFlashDB()

  // Single-instance lock (prevents concurrent cron runs)
  const lockAcquired = db.acquireCronLock('qflash_cron', PROCESS_ID)
  if (!lockAcquired) {
    return results // Another instance is running
  }

  try {
    // Phase 0: Initialize house account (idempotent, runs once)
    try {
      initializeHouseAccount()
    } catch (err) {
      results.errors.push(`Phase 0 (house init): ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 1: Create upcoming rounds (fill pipeline)
    try {
      results.roundsCreated = ensureUpcomingRounds()
    } catch (err) {
      results.errors.push(`Phase 1 (create): ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 2: Open ready rounds (upcoming -> open, snap opening price)
    try {
      results.roundsOpened = await openReadyRounds()
    } catch (err) {
      results.errors.push(`Phase 2 (open): ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 3: Lock rounds (open -> locked at lock_at)
    try {
      results.roundsLocked = lockReadyRounds()
    } catch (err) {
      results.errors.push(`Phase 3 (lock): ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 4: Resolve rounds (locked -> resolved at close_at)
    try {
      const resolveResult = await resolveReadyRounds()
      results.roundsResolved = resolveResult.resolved
      results.roundsCancelled = resolveResult.cancelled
      results.roundsSettled = resolveResult.settled.length
    } catch (err) {
      results.errors.push(`Phase 4 (resolve): ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 5: Handle stale resolving rounds
    try {
      const staleHandled = handleStaleResolvingRounds()
      results.roundsCancelled += staleHandled
    } catch (err) {
      results.errors.push(`Phase 5 (stale): ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 5b: Push price ticks to history (for live chart)
    try {
      const pairs = getEnabledPairs()
      const history = getPriceHistory()
      for (const pair of pairs) {
        const priceResult = await getPrice(pair)
        if (priceResult) {
          history.addTick(pair, priceResult.medianPrice)
        }
      }
    } catch (err) {
      results.errors.push(`Phase 5b (price history): ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 6: Monitor platform wallet balance
    try {
      const balanceCheck = await checkPlatformBalance()
      if (balanceCheck.delta > BigInt(0)) {
        // Balance increased — possible deposit detected
        // For MVP, deposits are credited via the API manually.
        // This monitoring is for logging/alerting purposes.
        results.depositsDetected = 1
      }
    } catch (err) {
      results.errors.push(`Phase 6 (deposit monitor): ${err instanceof Error ? err.message : String(err)}`)
    }

    // Phase 7: Process pending withdrawals
    try {
      results.withdrawalsProcessed = await processPendingWithdrawals()
    } catch (err) {
      results.errors.push(`Phase 7 (withdrawals): ${err instanceof Error ? err.message : String(err)}`)
    }

  } finally {
    db.releaseCronLock('qflash_cron', PROCESS_ID)
  }

  return results
}

// ---------------------------------------------------------------------------
// Auto-Start / Stop
// ---------------------------------------------------------------------------

/**
 * Start the QFlash cron. Safe to call multiple times — only starts once.
 */
export function startQFlashCron(): void {
  if (cronStarted) return
  cronStarted = true

  // Run immediately once
  void runQFlashCronCycle()

  cronTimer = setInterval(() => {
    if (isShuttingDown()) {
      stopQFlashCron()
      return
    }
    void runQFlashCronCycle()
  }, QFLASH_CONFIG.cronIntervalMs)

  // Don't block process exit
  if (cronTimer && typeof cronTimer === 'object' && 'unref' in cronTimer) {
    cronTimer.unref()
  }
}

/**
 * Stop the QFlash cron timer.
 */
export function stopQFlashCron(): void {
  if (cronTimer) {
    clearInterval(cronTimer)
    cronTimer = null
  }
  cronStarted = false
}

/**
 * Check if the cron is currently running.
 */
export function isQFlashCronRunning(): boolean {
  return cronStarted
}
