/**
 * QPredict Graceful Shutdown Manager
 *
 * Handles SIGTERM/SIGINT signals to:
 * 1. Prevent new cron cycles from starting
 * 2. Wait for any in-flight cron cycle to complete (max 30s)
 * 3. Close the SQLite database connection
 * 4. Send a shutdown alert
 */

import { cronLog } from './logger'
import { sendAlert } from './alerting'

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let shuttingDown = false
let inflightPromise: Promise<unknown> | null = null
let registered = false

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/** Returns true while shutdown is in progress — cron should not start new cycles. */
export function isShuttingDown(): boolean {
  return shuttingDown
}

/** Track an in-flight cron cycle promise so shutdown can wait for it. */
export function setInflightCron(promise: Promise<unknown>): void {
  inflightPromise = promise
}

/** Clear the in-flight reference after the cron cycle completes. */
export function clearInflightCron(): void {
  inflightPromise = null
}

// ---------------------------------------------------------------------------
// Shutdown Handler
// ---------------------------------------------------------------------------

/**
 * Register SIGTERM and SIGINT handlers. Safe to call multiple times.
 *
 * @param stopCron - callback to stop the cron timer (from auto-cron.ts)
 * @param closeDb  - callback to close the database (from market-db.ts)
 */
export function registerShutdownHandlers(
  stopCron: () => void,
  closeDb: () => void,
): void {
  if (registered) return
  registered = true

  const MAX_DRAIN_MS = 30_000

  const handler = async (signal: string) => {
    if (shuttingDown) return // Already handling
    shuttingDown = true

    cronLog.info({ signal }, 'shutdown signal received — draining...')

    // Wait for in-flight cron cycle (max 30s)
    if (inflightPromise) {
      cronLog.info('waiting for in-flight cron cycle to complete...')
      const timeout = new Promise<void>((resolve) => setTimeout(resolve, MAX_DRAIN_MS))
      await Promise.race([inflightPromise, timeout])
    }

    // Stop the cron timer
    stopCron()

    // Send shutdown alert (best-effort)
    await sendAlert('system_shutdown', 'info', `QPredict shutting down (${signal})`)

    // Close DB
    try {
      closeDb()
      cronLog.info('database connection closed')
    } catch {
      // Ignore close errors
    }

    cronLog.info('graceful shutdown complete')
    process.exit(0)
  }

  process.on('SIGTERM', () => { void handler('SIGTERM') })
  process.on('SIGINT', () => { void handler('SIGINT') })

  cronLog.info('shutdown handlers registered')
}
