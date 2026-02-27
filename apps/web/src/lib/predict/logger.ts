/**
 * QPredict Structured Logging
 *
 * Centralised Pino logger for the prediction market platform.
 * Each subsystem gets a child logger with a `module` binding so log
 * lines are easy to filter (e.g. `jq 'select(.module=="escrow")'`).
 *
 * Configuration:
 *   LOG_LEVEL  env var sets the minimum level (default: "info").
 *   NODE_ENV   "production" emits pure JSON; all other values do too
 *              — pipe through `pino-pretty` locally if you want colour:
 *              `pnpm dev | pnpm exec pino-pretty`
 *
 * NOTE: pino-pretty is intentionally NOT listed as a runtime dependency.
 * Next.js serverless / edge bundles choke on the worker-thread transport
 * that pino-pretty requires. Plain JSON is the safest default.
 */

import pino from 'pino'

// ---------------------------------------------------------------------------
// Root logger
// ---------------------------------------------------------------------------

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  timestamp: pino.stdTimeFunctions.isoTime,

  // Keep serialisation lightweight — no extra redaction or hooks.
  // Add `formatters.level` so the level name is a readable string rather
  // than a numeric value (much nicer for grep / jq).
  formatters: {
    level(label) {
      return { level: label }
    },
  },
})

// ---------------------------------------------------------------------------
// Child loggers — one per subsystem
// ---------------------------------------------------------------------------

/** Background lifecycle processor (escrow ticks, resolution checks) */
export const cronLog = logger.child({ module: 'cron' })

/** Per-bet single-use escrow address management */
export const escrowLog = logger.child({ module: 'escrow' })

/** Market creation, betting, resolution business logic */
export const marketLog = logger.child({ module: 'market' })

/** Oracle adapter layer (price feeds, event outcomes) */
export const oracleLog = logger.child({ module: 'oracle' })

/** SQLite / market-db persistence layer */
export const dbLog = logger.child({ module: 'db' })

/** Qubic RPC communication (quottery-client, balance checks) */
export const rpcLog = logger.child({ module: 'rpc' })

// ---------------------------------------------------------------------------
// Default export is the root logger (useful for one-off or ad-hoc logging)
// ---------------------------------------------------------------------------

export default logger
