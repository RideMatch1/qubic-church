/**
 * QFlash House Bank
 *
 * Automatic counterparty that takes the opposite side of user bets,
 * guaranteeing liquidity even without concurrent opposing players.
 *
 * The house has its own internal account balance and exposure limits.
 * All house P&L is tracked in the house_ledger table.
 */

import { getQFlashDB } from './qflash-db'
import { QFLASH_CONFIG, isHouseEnabled, getHouseInitialBalance } from './config'

import type { Entry, Side, HouseStats } from './types'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const HOUSE_ADDRESS = QFLASH_CONFIG.house.houseAddress

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

let _initialized = false

/**
 * Ensure the house account exists with initial balance.
 * Called once on first cron cycle. Idempotent.
 */
export function initializeHouseAccount(): void {
  if (_initialized) return
  if (!isHouseEnabled()) {
    _initialized = true
    return
  }

  const db = getQFlashDB()
  const existing = db.getAccount(HOUSE_ADDRESS)

  if (!existing) {
    const initialBalance = getHouseInitialBalance()
    db.ensureAccount(HOUSE_ADDRESS)
    if (initialBalance > 0) {
      db.creditDeposit(HOUSE_ADDRESS, initialBalance)
    }
  }

  _initialized = true
}

// ---------------------------------------------------------------------------
// Matching Logic
// ---------------------------------------------------------------------------

/**
 * Check if the house can afford to match a bet.
 *
 * Checks:
 * 1. House enabled
 * 2. House has sufficient balance
 * 3. Per-round exposure limit not exceeded
 * 4. Total exposure limit not exceeded
 */
export function canMatch(amountQu: number, roundId: string): boolean {
  if (!isHouseEnabled()) return false

  const db = getQFlashDB()
  const houseAccount = db.getAccount(HOUSE_ADDRESS)
  if (!houseAccount) return false

  const matchAmount = Math.floor(amountQu * QFLASH_CONFIG.house.matchRatio)
  if (matchAmount <= 0) return false

  // Check house balance
  if (houseAccount.balanceQu < matchAmount) return false

  // Check per-round exposure
  const roundExposure = db.getHouseExposureForRound(roundId)
  if (roundExposure + matchAmount > QFLASH_CONFIG.house.maxExposurePerRoundQu) return false

  // Check total exposure
  const totalExposure = db.getHouseTotalExposure()
  if (totalExposure + matchAmount > QFLASH_CONFIG.house.maxTotalExposureQu) return false

  return true
}

/**
 * Match a user's bet with an opposite house bet.
 *
 * When a user bets 100K QU on UP, the house places 100K QU on DOWN.
 * This ensures the round always has both sides covered.
 *
 * @returns The house entry, or null if house can't/won't match
 */
export function matchBet(
  roundId: string,
  userSide: Side,
  userAmountQu: number,
): Entry | null {
  if (!isHouseEnabled()) return null

  const matchAmount = Math.floor(userAmountQu * QFLASH_CONFIG.house.matchRatio)
  if (matchAmount <= 0) return null

  if (!canMatch(matchAmount, roundId)) return null

  const db = getQFlashDB()
  const oppositeSide: Side = userSide === 'up' ? 'down' : 'up'

  // Debit house balance (wager)
  db.debitWager(HOUSE_ADDRESS, matchAmount)

  // Create house entry
  const entry = db.createHouseEntry(roundId, oppositeSide, matchAmount)

  // Record in house ledger
  const houseAccount = db.getAccount(HOUSE_ADDRESS)
  db.recordHouseLedger(
    roundId,
    entry.id,
    'match_bet',
    matchAmount,
    houseAccount?.balanceQu ?? 0,
  )

  // Create transaction record
  db.createTransaction(HOUSE_ADDRESS, 'wager', matchAmount, roundId, undefined, 'confirmed')

  return entry
}

// ---------------------------------------------------------------------------
// Stats
// ---------------------------------------------------------------------------

/**
 * Get current house exposure across all open rounds.
 */
export function getTotalExposure(): number {
  const db = getQFlashDB()
  return db.getHouseTotalExposure()
}

/**
 * Get comprehensive house P&L stats.
 */
export function getHouseStats(): HouseStats {
  const db = getQFlashDB()
  return db.getHouseStats()
}

/**
 * Get house account balance.
 */
export function getHouseBalance(): number {
  const db = getQFlashDB()
  const account = db.getAccount(HOUSE_ADDRESS)
  return account?.balanceQu ?? 0
}
