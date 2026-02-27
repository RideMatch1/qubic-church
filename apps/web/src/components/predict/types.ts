/**
 * QPredict Frontend Types
 *
 * Shared type definitions for the prediction market UI components.
 * These mirror the shapes returned by the API endpoints.
 */

export type MarketStatus =
  | 'draft'
  | 'pending_tx'
  | 'active'
  | 'closed'
  | 'resolving'
  | 'resolved'
  | 'cancelled'

export type MarketType = 'price' | 'sports' | 'ai' | 'custom'

export type ResolutionType = 'price_above' | 'price_below' | 'price_range' | 'price_bracket'

export type CreatedBy = 'user' | 'trending_agent' | 'ai_parsed'

export type BetStatus = 'pending_deposit' | 'pending' | 'confirmed' | 'won' | 'lost' | 'refunded'

export type MarketCategory = 'crypto' | 'sports' | 'politics' | 'tech' | 'entertainment' | 'other'

export interface Market {
  id: string
  quotteryBetId: number | null
  pair: string
  question: string
  resolutionType: ResolutionType
  resolutionTarget: number
  resolutionTargetHigh: number | null
  closeDate: string
  endDate: string
  minBetQu: number
  maxSlots: number
  status: MarketStatus
  totalPool: number
  yesSlots: number
  noSlots: number
  resolutionPrice: number | null
  winningOption: number | null
  creatorAddress: string | null
  txHash: string | null
  createdAt: string
  resolvedAt: string | null
  impliedProbability: number
  // v2 fields
  marketType: MarketType
  options: string[]
  numOptions: number
  oracleFeeBps: number
  slotsPerOption: Record<string, number>
  createdBy: CreatedBy
  sourceQuery: string | null
  category: MarketCategory | null
}

export interface UserBet {
  id: string
  marketId: string
  userAddress: string
  option: number
  slots: number
  amountQu: number
  txHash: string | null
  status: BetStatus
  payoutQu: number | null
  createdAt: string
}

export interface MarketSnapshot {
  marketId: string
  timestamp: string
  yesSlots: number
  noSlots: number
  impliedProbability: number
  totalPool: number
}

export interface PlatformStats {
  totalMarkets: number
  activeMarkets: number
  resolvedMarkets: number
  totalVolume: number
  totalBets: number
  totalUsers: number
  totalPaidOut: number
}

export interface ResolutionStats {
  winners: number
  losers: number
  winnerSlots: number
  totalPayoutQu: number
  payoutPerSlot: number
}

export interface MarketDetail {
  market: Market
  bets: UserBet[]
  snapshots: MarketSnapshot[]
  impliedProbability: number
  resolutionStats: ResolutionStats | null
}

export interface MarketsListResponse {
  markets: Market[]
  count: number
}

export interface PlaceBetPayload {
  marketId: string
  payoutAddress: string
  option: number
  slots: number
}

export type EscrowStatus =
  | 'awaiting_deposit'
  | 'deposit_detected'
  | 'joining_sc'
  | 'active_in_sc'
  | 'won_awaiting_sweep'
  | 'swept'
  | 'completed'
  | 'lost'
  | 'expired'
  | 'refunded'
  | 'failed'

export interface EscrowInfo {
  escrowId: string
  betId: string
  marketId: string
  escrowAddress: string
  userPayoutAddress: string
  option: number
  slots: number
  expectedAmountQu: number
  status: EscrowStatus
  depositAmountQu: number | null
  payoutAmountQu: number | null
  sweepTxId: string | null
  joinBetTxId: string | null
  expiresAt: string
  createdAt: string
}

export interface CreateEscrowResponse {
  betId: string
  escrowId: string
  escrowAddress: string
  expectedAmountQu: number
  expiresAt: string
  status: 'awaiting_deposit'
  market: {
    id: string
    question: string
    pair: string
    minBetQu: number
  }
  option: string
  instructions: string
}

export interface CreateMarketPayload {
  pair: string
  question: string
  resolutionType: ResolutionType
  resolutionTarget: number
  resolutionTargetHigh?: number
  closeDate: string
  endDate: string
  minBetQu?: number
  maxSlots?: number
  creatorAddress: string
  // v2 fields
  marketType?: MarketType
  options?: string[]
  oracleAddresses?: string[]
  oracleFeeBps?: number
}

/** Supported trading pairs */
export const SUPPORTED_PAIRS = [
  'btc/usdt',
  'eth/usdt',
  'sol/usdt',
  'xrp/usdt',
  'bnb/usdt',
  'doge/usdt',
  'ada/usdt',
  'avax/usdt',
  'link/usdt',
  'dot/usdt',
  'ltc/usdt',
  'sui/usdt',
  'near/usdt',
  'trx/usdt',
  'atom/usdt',
  'apt/usdt',
  'qubic/usdt',
  'eth/btc',
] as const

/** Human-readable labels for resolution types */
export const RESOLUTION_TYPE_LABELS: Record<ResolutionType, string> = {
  price_above: 'Price Above',
  price_below: 'Price Below',
  price_range: 'Price Range',
  price_bracket: 'Price Bracket',
}

/** Human-readable labels for market types */
export const MARKET_TYPE_LABELS: Record<MarketType, string> = {
  price: 'Price Prediction',
  sports: 'Sports',
  ai: 'AI-Resolved',
  custom: 'Custom',
}

/** All market types for filter dropdowns */
export const ALL_MARKET_TYPES: MarketType[] = ['price', 'sports', 'ai', 'custom']

/** All market categories for filter chips */
export const ALL_CATEGORIES: MarketCategory[] = [
  'crypto',
  'sports',
  'politics',
  'tech',
  'entertainment',
  'other',
]

/** Human-readable labels for market categories */
export const CATEGORY_LABELS: Record<MarketCategory, string> = {
  crypto: 'Crypto',
  sports: 'Sports',
  politics: 'Politics',
  tech: 'Tech',
  entertainment: 'Entertainment',
  other: 'Other',
}

/** Color classes for category badges */
export const CATEGORY_COLORS: Record<MarketCategory, string> = {
  crypto: 'bg-blue-500/10 text-blue-500',
  sports: 'bg-green-500/10 text-green-500',
  politics: 'bg-purple-500/10 text-purple-500',
  tech: 'bg-orange-500/10 text-orange-500',
  entertainment: 'bg-pink-500/10 text-pink-500',
  other: 'bg-muted text-muted-foreground',
}

/** Map pair to display name */
export function pairLabel(pair: string): string {
  return pair.toUpperCase().replace('/', ' / ')
}

/** Map pair to base asset symbol (uppercase) */
export function pairBaseAsset(pair: string): string {
  return pair.split('/')[0]?.toUpperCase() ?? pair.toUpperCase()
}
