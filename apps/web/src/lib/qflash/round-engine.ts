/**
 * QFlash Round Engine
 *
 * Manages the full round lifecycle:
 *   upcoming -> open -> locked -> resolving -> resolved | cancelled
 *
 * Each round is a binary prediction: will the price go UP or DOWN
 * between the opening and closing timestamps?
 */

import { hashCanonicalJSON } from '../predict/provably-fair'
import { getQFlashDB } from './qflash-db'
import { getPrice, invalidateCache } from './price-feed'
import {
  QFLASH_CONFIG,
  getEnabledPairs,
  getEnabledDurations,
} from './config'

import type { Round, RoundDuration, Outcome } from './types'

// ---------------------------------------------------------------------------
// Date Helpers — SQLite-compatible format
// ---------------------------------------------------------------------------

/**
 * Format a Date to SQLite-compatible string: 'YYYY-MM-DD HH:MM:SS'
 * SQLite's datetime('now') returns this format, so comparisons work correctly.
 */
function toSqliteDate(date: Date): string {
  return date.toISOString().replace('T', ' ').replace(/\.\d{3}Z$/, '')
}

// ---------------------------------------------------------------------------
// Round Creation Pipeline
// ---------------------------------------------------------------------------

/**
 * Ensure there are enough upcoming/open rounds in the pipeline
 * for all enabled pair+duration combinations.
 *
 * Pre-creates rounds up to `roundPipelineAheadSecs` in the future
 * so users always see a "next round" to bet on.
 */
export function ensureUpcomingRounds(): number {
  const db = getQFlashDB()
  const pairs = getEnabledPairs()
  const durations = getEnabledDurations()
  let created = 0

  for (const pair of pairs) {
    for (const duration of durations) {
      const existing = db.getUpcomingCountForPairDuration(pair, duration)

      // Keep at least 2 upcoming/open rounds in the pipeline
      if (existing >= 2) continue

      const toCreate = 2 - existing

      // Find the latest scheduled close time for this pair+duration
      const activeRounds = db.getActiveRounds(pair, duration)
      let lastCloseAt: Date

      if (activeRounds.length > 0) {
        const latest = activeRounds[activeRounds.length - 1]!
        lastCloseAt = parseUtc(latest.closeAt)
      } else {
        // No active rounds — start from now, aligned to duration boundary
        lastCloseAt = alignToNextBoundary(new Date(), duration)
      }

      for (let i = 0; i < toCreate; i++) {
        const openAt = new Date(lastCloseAt.getTime())
        const lockAt = new Date(openAt.getTime() + (duration - QFLASH_CONFIG.lockBeforeCloseSecs) * 1000)
        const closeAt = new Date(openAt.getTime() + duration * 1000)

        db.createRound(
          pair,
          duration,
          toSqliteDate(openAt),
          toSqliteDate(lockAt),
          toSqliteDate(closeAt),
        )

        lastCloseAt = closeAt
        created++
      }
    }
  }

  return created
}

/**
 * Align a date to the next clean boundary for a given duration.
 * E.g., for 30s rounds, aligns to the next :00 or :30 second mark.
 */
function alignToNextBoundary(date: Date, durationSecs: number): Date {
  const epochSecs = Math.floor(date.getTime() / 1000)
  const nextBoundary = Math.ceil(epochSecs / durationSecs) * durationSecs
  return new Date(nextBoundary * 1000)
}

// ---------------------------------------------------------------------------
// Phase: Open Rounds
// ---------------------------------------------------------------------------

/**
 * Transition upcoming rounds to 'open' when their open_at time has been reached.
 * Snapshots the opening price and creates a commitment hash.
 */
export async function openReadyRounds(): Promise<number> {
  const db = getQFlashDB()
  const rounds = db.getRoundsToOpen()
  let opened = 0

  for (const round of rounds) {
    const priceResult = await getPrice(round.pair, true) // force fresh for opening
    if (!priceResult) {
      // Oracle failure — cancel this round before it opens
      db.cancelRound(round.id)
      continue
    }

    // Create commitment hash: H(roundId, pair, openingPrice, openAt)
    const commitmentHash = hashCanonicalJSON({
      roundId: round.id,
      pair: round.pair,
      openingPrice: priceResult.medianPrice,
      openAt: round.openAt,
    })

    // Store opening price snapshot
    db.createSnapshot(
      round.id,
      'opening',
      round.pair,
      priceResult.medianPrice,
      JSON.stringify(priceResult.sources),
      priceResult.attestationHash,
    )

    db.openRound(round.id, priceResult.medianPrice, commitmentHash)
    opened++
  }

  return opened
}

// ---------------------------------------------------------------------------
// Phase: Lock Rounds
// ---------------------------------------------------------------------------

/**
 * Transition open rounds to 'locked' when their lock_at time has been reached.
 * No more bets accepted after this point.
 */
export function lockReadyRounds(): number {
  const db = getQFlashDB()
  const rounds = db.getRoundsToLock()
  let locked = 0

  for (const round of rounds) {
    db.lockRound(round.id)
    locked++
  }

  return locked
}

// ---------------------------------------------------------------------------
// Phase: Resolve Rounds
// ---------------------------------------------------------------------------

/**
 * Resolve locked rounds that have reached their close_at time.
 * Fetches closing price, determines outcome, and triggers settlement.
 */
export async function resolveReadyRounds(): Promise<{
  resolved: number
  cancelled: number
  settled: { winnersCount: number; losersCount: number; totalPayout: number }[]
}> {
  const db = getQFlashDB()
  const rounds = db.getRoundsToResolve()
  let resolved = 0
  let cancelled = 0
  const settled: { winnersCount: number; losersCount: number; totalPayout: number }[] = []

  for (const round of rounds) {
    // CAS: only proceed if round is still 'locked' (prevents double-resolve)
    const claimed = db.casUpdateRoundStatus(round.id, 'resolving', 'locked')
    if (!claimed) continue // another cron instance already claimed this round

    // Force fresh price for closing snapshot
    invalidateCache(round.pair)
    const priceResult = await getPrice(round.pair, true)

    if (!priceResult) {
      // Oracle failure — cancel and refund all entries
      db.cancelRound(round.id)
      db.refundAllEntries(round.id)
      refundAccountsForRound(round)
      cancelled++
      continue
    }

    // Store closing price snapshot
    db.createSnapshot(
      round.id,
      'closing',
      round.pair,
      priceResult.medianPrice,
      JSON.stringify(priceResult.sources),
      priceResult.attestationHash,
    )

    // Determine outcome
    const outcome = determineOutcome(round.openingPrice!, priceResult.medianPrice)

    // Calculate platform fee
    const platformFeeQu = calculatePlatformFee(round, outcome)

    // Resolve in DB
    db.resolveRound(round.id, priceResult.medianPrice, outcome, platformFeeQu)

    // Settle payouts
    const settleResult = db.settleRound(round.id, outcome, platformFeeQu)
    settled.push(settleResult)
    resolved++
  }

  return { resolved, cancelled, settled }
}

/**
 * Handle rounds stuck in 'resolving' state for too long.
 * Cancels and refunds if resolution delay exceeds maxResolutionDelayMs.
 */
export function handleStaleResolvingRounds(): number {
  const db = getQFlashDB()
  const stale = db.getStaleResolvingRounds()
  let handled = 0

  for (const round of stale) {
    db.cancelRound(round.id)
    db.refundAllEntries(round.id)
    refundAccountsForRound(round)
    handled++
  }

  return handled
}

// ---------------------------------------------------------------------------
// Outcome Determination
// ---------------------------------------------------------------------------

function determineOutcome(openingPrice: number, closingPrice: number): Outcome {
  if (closingPrice > openingPrice) return 'up'
  if (closingPrice < openingPrice) return 'down'
  return 'push'
}

// ---------------------------------------------------------------------------
// Fee Calculation
// ---------------------------------------------------------------------------

function calculatePlatformFee(round: Round, outcome: Outcome): number {
  if (outcome === 'push') return 0

  const winningSide = outcome
  const winnerPool = winningSide === 'up' ? round.upPoolQu : round.downPoolQu
  const loserPool = winningSide === 'up' ? round.downPoolQu : round.upPoolQu

  // One-sided round: no fee
  if (winnerPool === 0 || loserPool === 0) return 0

  return Math.floor(loserPool * QFLASH_CONFIG.platformFeeBps / 10_000)
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Refund all account balances for entries in a cancelled round.
 * Idempotent: only refunds entries still in 'active' status.
 */
function refundAccountsForRound(round: Round): void {
  const db = getQFlashDB()
  const entries = db.getEntriesByRound(round.id)
  for (const entry of entries) {
    if (entry.status !== 'active') continue // already settled/refunded
    db.creditRefund(entry.userAddress, entry.amountQu)
    db.createTransaction(entry.userAddress, 'refund', entry.amountQu, round.id, undefined, 'confirmed')
  }
}

function parseUtc(ts: string): Date {
  let s = ts
  if (!/[Z]$/i.test(s) && !/[+-]\d{2}(:\d{2})?$/.test(s)) {
    s = s.replace(' ', 'T') + 'Z'
  }
  return new Date(s)
}
