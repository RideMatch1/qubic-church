/**
 * QFlash Types — Ultra-Fast Binary Prediction Rounds
 *
 * Type definitions for the QFlash system: 30s/60s/120s binary predictions
 * on crypto prices with pool-based settlement.
 */

// ---------------------------------------------------------------------------
// Round
// ---------------------------------------------------------------------------

export type RoundStatus =
  | 'upcoming'  // created but not yet open for betting
  | 'open'      // accepting bets
  | 'locked'    // no more bets (5s before close)
  | 'resolving' // close reached, fetching closing price
  | 'resolved'  // outcome determined, payouts settled
  | 'cancelled' // oracle failure or no counterparty

export type Side = 'up' | 'down'

export type Outcome = 'up' | 'down' | 'push'

export type RoundDuration = 30 | 60 | 120

export interface Round {
  id: string
  pair: string
  durationSecs: RoundDuration
  status: RoundStatus
  openAt: string   // ISO 8601
  lockAt: string   // ISO 8601 (openAt + duration - lockBeforeCloseSecs)
  closeAt: string  // ISO 8601 (openAt + duration)
  openingPrice: number | null
  closingPrice: number | null
  outcome: Outcome | null
  upPoolQu: number
  downPoolQu: number
  entryCount: number
  platformFeeQu: number
  commitmentHash: string | null
  resolvedAt: string | null
  createdAt: string
}

// ---------------------------------------------------------------------------
// Entry (a user's bet in a round)
// ---------------------------------------------------------------------------

export type EntryStatus =
  | 'active'   // placed during open round
  | 'won'      // round resolved in user's favor
  | 'lost'     // round resolved against user
  | 'push'     // no price movement, refunded
  | 'refunded' // cancelled round, refunded

export interface Entry {
  id: string
  roundId: string
  userAddress: string
  side: Side
  amountQu: number
  payoutQu: number | null
  status: EntryStatus
  isHouse: boolean
  createdAt: string
}

// ---------------------------------------------------------------------------
// Account
// ---------------------------------------------------------------------------

export interface QFlashAccount {
  address: string
  balanceQu: number
  totalDeposited: number
  totalWithdrawn: number
  totalWagered: number
  totalWon: number
  totalRefunded: number
  totalLost: number
  winCount: number
  lossCount: number
  pushCount: number
  streak: number       // current win streak (negative for loss streak)
  bestStreak: number   // all-time best win streak
  apiToken: string | null
  createdAt: string
}

// ---------------------------------------------------------------------------
// Transaction
// ---------------------------------------------------------------------------

export type QFlashTxType =
  | 'deposit'
  | 'withdrawal'
  | 'wager'
  | 'payout'
  | 'refund'
  | 'platform_fee'

export type QFlashTxStatus = 'pending' | 'confirmed' | 'failed'

export interface QFlashTransaction {
  id: string
  address: string
  type: QFlashTxType
  amountQu: number
  roundId: string | null
  txHash: string | null
  status: QFlashTxStatus
  createdAt: string
}

// ---------------------------------------------------------------------------
// Price Snapshot
// ---------------------------------------------------------------------------

export type SnapshotType = 'opening' | 'closing'

export interface PriceSnapshot {
  id: string
  roundId: string
  snapshotType: SnapshotType
  pair: string
  medianPrice: number
  sourcesJson: string    // JSON array of { name, price }
  attestationHash: string
  createdAt: string
}

// ---------------------------------------------------------------------------
// Leaderboard
// ---------------------------------------------------------------------------

export interface QFlashLeaderboardEntry {
  address: string
  totalRounds: number
  wins: number
  losses: number
  pushes: number
  winRate: number
  totalWagered: number
  totalWon: number
  profitQu: number
  bestStreak: number
}

// ---------------------------------------------------------------------------
// Platform Stats
// ---------------------------------------------------------------------------

export interface QFlashStats {
  totalRounds: number
  activeRounds: number
  resolvedRounds: number
  totalVolume: number
  totalEntries: number
  totalAccounts: number
  totalPaidOut: number
  totalPlatformFees: number
  avgRoundPool: number
}

// ---------------------------------------------------------------------------
// API Response Types
// ---------------------------------------------------------------------------

export interface RoundListResponse {
  rounds: Round[]
  count: number
}

export interface BetResponse {
  entryId: string
  roundId: string
  side: Side
  amountQu: number
  newBalance: number
}

export interface AccountResponse {
  account: QFlashAccount
  recentTransactions: QFlashTransaction[]
}

// ---------------------------------------------------------------------------
// House Bank
// ---------------------------------------------------------------------------

export type HouseLedgerType = 'match_bet' | 'win' | 'loss' | 'refund' | 'fee_income'

export interface HouseLedgerEntry {
  id: string
  roundId: string
  entryId: string
  type: HouseLedgerType
  amountQu: number
  balanceAfterQu: number
  createdAt: string
}

export interface HouseStats {
  balanceQu: number
  totalExposureQu: number
  roundsPlayed: number
  wins: number
  losses: number
  totalWonQu: number
  totalLostQu: number
  netPnlQu: number
  feeIncomeQu: number
  recentLedger: HouseLedgerEntry[]
}

// ---------------------------------------------------------------------------
// Cron Results
// ---------------------------------------------------------------------------

export interface QFlashCronResults {
  roundsCreated: number
  roundsOpened: number
  roundsLocked: number
  roundsResolved: number
  roundsSettled: number
  roundsCancelled: number
  depositsDetected: number
  withdrawalsProcessed: number
  errors: string[]
}
