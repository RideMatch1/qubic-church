/**
 * QPredict Market Manager
 *
 * Business logic layer for the prediction market platform.
 * Coordinates between the Market DB, Quottery SC, and Custody system.
 *
 * Responsibilities:
 * - Market creation + Quottery SC deployment
 * - Bet placement + fund deduction
 * - Market resolution (oracle check + publishResult)
 * - Payout calculation + distribution
 */

import {
  getMarketDB,
  MarketDatabase,
  type Market,
  type UserBet,
  type MarketStatus,
  type MarketType,
  type CreatedBy,
  type ResolutionType,
  type PlatformStats,
  type LeaderboardEntry,
  type MarketSnapshot,
} from './market-db'
import {
  issueBet,
  joinBet,
  publishResult,
  cancelBet,
  estimatePayout,
  getCurrentTick,
  discoverBetId,
  type IssueBetParams,
  type JoinBetParams,
  type PublishResultParams,
  type QuotteryTxResult,
  QUOTTERY_FEES,
} from '@/lib/qubic/quottery-client'
import {
  debitForBet,
  creditWinnings,
  getPlatformSeed,
  getPlatformAddress,
} from './custody'
import {
  buildChainEntry,
  createMarketCommitment,
  createBetCommitment,
  generateBetNonce,
  GENESIS_HASH,
  type ChainEventType,
} from './provably-fair'
import { marketLog } from './logger'
import { parseUtcTimestamp } from './api-utils'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface CreateMarketInput {
  pair: string
  question: string
  resolutionType: ResolutionType
  resolutionTarget: number
  resolutionTargetHigh?: number
  closeDate: string // ISO 8601
  endDate: string // ISO 8601
  minBetQu?: number
  maxSlots?: number
  creatorAddress: string
  oracleFeeBps?: number // Oracle fee in basis points (default 0 = free)
  // v2 multi-option + AI fields
  marketType?: MarketType
  options?: string[] // 2-8 option labels (default: ["Yes","No"])
  oracleAddresses?: string[] // For custom markets -- who can resolve
  createdBy?: CreatedBy
  sourceQuery?: string // Original natural language input for AI-parsed markets
}

export interface PlaceBetInput {
  marketId: string
  userAddress: string
  option: number // 0-based option index (0-7)
  slots: number
}

export interface MarketResolutionInput {
  marketId: string
  /** For price markets: the current price for resolution */
  currentPrice?: number
  /** For non-price markets: the winning option index (from oracle adapter) */
  winningOption?: number
  /** Proof data from the oracle adapter */
  oracleProof?: { source: string; data: unknown }
}

export interface CreateMarketResult {
  success: boolean
  market?: Market
  quotteryTx?: QuotteryTxResult
  error?: string
}

export interface PlaceBetResult {
  success: boolean
  bet?: UserBet
  quotteryTx?: QuotteryTxResult
  commitmentHash?: string
  commitmentNonce?: string
  error?: string
}

export interface ResolveMarketResult {
  success: boolean
  market?: Market
  winningOption?: number
  winners?: number
  losers?: number
  payoutPerSlot?: number
  quotteryTx?: QuotteryTxResult
  error?: string
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

/** Pairs that can be used for markets (must have oracle price feeds) */
const SUPPORTED_PAIRS = [
  'btc/usdt', 'eth/usdt', 'sol/usdt', 'xrp/usdt', 'bnb/usdt',
  'doge/usdt', 'ada/usdt', 'avax/usdt', 'link/usdt', 'dot/usdt',
  'ltc/usdt', 'sui/usdt', 'near/usdt', 'trx/usdt', 'atom/usdt',
  'apt/usdt', 'qubic/usdt', 'eth/btc',
]

function validateCreateMarket(input: CreateMarketInput): string | null {
  const marketType = input.marketType ?? 'price'

  // Price markets require a supported pair
  if (marketType === 'price') {
    if (!SUPPORTED_PAIRS.includes(input.pair)) {
      return `Unsupported pair: ${input.pair}. Supported: ${SUPPORTED_PAIRS.join(', ')}`
    }
  }

  if (!input.question || input.question.length < 10) {
    return 'Question must be at least 10 characters'
  }

  if (input.question.length > 100) {
    return 'Question must be at most 100 characters'
  }

  // Validate options (2-8)
  const options = input.options ?? ['Yes', 'No']
  if (options.length < 2 || options.length > 8) {
    return 'Options must be 2-8 items'
  }
  for (const opt of options) {
    if (!opt || opt.length > 31) {
      return 'Each option must be 1-31 characters'
    }
  }

  const closeDate = new Date(input.closeDate)
  const endDate = new Date(input.endDate)
  const now = new Date()

  if (isNaN(closeDate.getTime())) return 'Invalid closeDate'
  if (isNaN(endDate.getTime())) return 'Invalid endDate'
  if (closeDate <= now) return 'closeDate must be in the future'
  if (endDate <= closeDate) return 'endDate must be after closeDate'

  // Min duration: 1 minute (relaxed for testing; raise to 30 * 60 * 1000 in production)
  const durationMs = endDate.getTime() - closeDate.getTime()
  if (durationMs < 1 * 60 * 1000) {
    return 'Resolution window (endDate - closeDate) must be at least 1 minute'
  }

  // Max duration: 90 days for non-price markets (30 for price)
  const maxDuration = marketType === 'price' ? 30 : 90
  if (durationMs > maxDuration * 24 * 60 * 60 * 1000) {
    return `Resolution window must be at most ${maxDuration} days`
  }

  // Price-specific validation
  if (marketType === 'price') {
    if (input.resolutionTarget <= 0) {
      return 'Resolution target must be positive'
    }

    if (input.resolutionType === 'price_range') {
      if (!input.resolutionTargetHigh || input.resolutionTargetHigh <= input.resolutionTarget) {
        return 'For range markets, resolutionTargetHigh must be greater than resolutionTarget'
      }
    }

    if (input.resolutionType === 'price_bracket') {
      if (!input.resolutionTargetHigh || input.resolutionTargetHigh <= input.resolutionTarget) {
        return 'For bracket markets, resolutionTargetHigh must be greater than resolutionTarget'
      }
      if (options.length < 3) {
        return 'Bracket markets need at least 3 options'
      }
    }
  }

  // Custom markets should have oracle addresses
  if (marketType === 'custom' && (!input.oracleAddresses || input.oracleAddresses.length === 0)) {
    return 'Custom markets require at least one oracle address (the creator)'
  }

  const minBet = input.minBetQu ?? 10_000
  if (minBet < Number(QUOTTERY_FEES.minAmountPerSlot)) {
    return `Minimum bet must be >= ${QUOTTERY_FEES.minAmountPerSlot} QU`
  }

  const maxSlots = input.maxSlots ?? 100
  if (maxSlots < 2 || maxSlots > QUOTTERY_FEES.maxBetSlotPerOption) {
    return `Max slots must be 2-${QUOTTERY_FEES.maxBetSlotPerOption}`
  }

  // Safety: ensure maxSlots × minBet doesn't overflow safe integer range
  const maxPossibleBet = BigInt(minBet) * BigInt(maxSlots)
  if (maxPossibleBet > BigInt(Number.MAX_SAFE_INTEGER)) {
    return 'Market configuration allows bets exceeding safe integer limits. Reduce minBetQu or maxSlots.'
  }

  return null
}

function validatePlaceBet(
  input: PlaceBetInput,
  market: Market,
): string | null {
  if (market.status !== 'active') {
    return `Market is not active (status: ${market.status})`
  }

  const now = new Date()
  const closeDate = parseUtcTimestamp(market.closeDate)
  if (now >= closeDate) {
    return 'Betting has closed for this market'
  }

  // Validate option is within range for this market's options
  if (input.option < 0 || input.option >= market.numOptions) {
    return `Option must be 0-${market.numOptions - 1} (this market has ${market.numOptions} options)`
  }

  if (input.slots < 1) {
    return 'Must buy at least 1 slot'
  }

  // Check slot limits using slotsPerOption (v2) or legacy fields
  const currentSlots = market.slotsPerOption[String(input.option)] ?? 0
  if (currentSlots + input.slots > market.maxSlots) {
    return `Exceeds max slots for option ${input.option}: ${currentSlots} + ${input.slots} > ${market.maxSlots}`
  }

  // Prevent betting on multiple sides of the same market
  const db = getMarketDB()
  const existingBets = db.getUserBetsForMarket(input.marketId, input.userAddress)
  for (const existingBet of existingBets) {
    if (existingBet.option !== input.option) {
      const existingLabel = market.options[existingBet.option] ?? `Option ${existingBet.option}`
      return `You already have a bet on "${existingLabel}". Cannot bet on multiple options.`
    }
  }

  return null
}

// ---------------------------------------------------------------------------
// Provably Fair: Chain Entry Helper
// ---------------------------------------------------------------------------

/**
 * Append an entry to the commitment chain.
 * Gets the latest chain hash (or genesis), builds the entry, and persists it.
 */
function appendToChain(
  eventType: ChainEventType,
  entityId: string,
  payload: unknown,
): void {
  const db = getMarketDB()
  const latest = db.getLatestChainEntry()
  const prevHash = latest?.chainHash ?? GENESIS_HASH
  const seqNum = (latest?.sequenceNum ?? 0) + 1

  const entry = buildChainEntry(seqNum, eventType, entityId, payload, prevHash)
  db.appendChainEntry(entry)
}

// ---------------------------------------------------------------------------
// Market Operations
// ---------------------------------------------------------------------------

/**
 * Create a new prediction market and deploy it to Quottery SC.
 */
export async function createMarket(
  input: CreateMarketInput,
): Promise<CreateMarketResult> {
  // Validate input
  const error = validateCreateMarket(input)
  if (error) return { success: false, error }

  const db = getMarketDB()
  const marketType = input.marketType ?? 'price'
  const options = input.options ?? ['Yes', 'No']

  // For custom markets, compute auto-refund date (48h after endDate)
  let autoRefundAt: string | undefined
  if (marketType === 'custom' || marketType === 'ai') {
    const endMs = new Date(input.endDate).getTime()
    autoRefundAt = new Date(endMs + 48 * 60 * 60 * 1000).toISOString()
  }

  // Create market in DB with v2 fields
  const market = db.createMarket({
    pair: input.pair,
    question: input.question,
    resolutionType: input.resolutionType,
    resolutionTarget: input.resolutionTarget,
    resolutionTargetHigh: input.resolutionTargetHigh,
    closeDate: input.closeDate,
    endDate: input.endDate,
    minBetQu: input.minBetQu ?? 10_000,
    maxSlots: input.maxSlots ?? 100,
    creatorAddress: input.creatorAddress,
    // v2 fields
    marketType,
    options,
    oracleAddresses: input.oracleAddresses,
    oracleFeeBps: input.oracleFeeBps ?? 0, // 0% oracle fee by default
    autoRefundAt,
    createdBy: input.createdBy ?? 'user',
    sourceQuery: input.sourceQuery,
  })

  // Provably Fair: Market commitment hash
  const commitmentHash = createMarketCommitment({
    pair: input.pair,
    question: input.question,
    resolutionType: input.resolutionType,
    resolutionTarget: input.resolutionTarget,
    resolutionTargetHigh: input.resolutionTargetHigh ?? null,
    closeDate: input.closeDate,
    endDate: input.endDate,
    minBetQu: input.minBetQu ?? 10_000,
    maxSlots: input.maxSlots ?? 100,
    creatorAddress: input.creatorAddress,
  })
  db.setMarketCommitment(market.id, commitmentHash)

  // Provably Fair: Chain entry for market creation
  appendToChain('market_create', market.id, {
    marketId: market.id,
    pair: input.pair,
    question: input.question,
    marketType,
    options,
    resolutionType: input.resolutionType,
    resolutionTarget: input.resolutionTarget,
    resolutionTargetHigh: input.resolutionTargetHigh ?? null,
    closeDate: input.closeDate,
    endDate: input.endDate,
    minBetQu: input.minBetQu ?? 10_000,
    maxSlots: input.maxSlots ?? 100,
    creatorAddress: input.creatorAddress,
    commitmentHash,
  })

  // Prepare Quottery issueBet parameters
  const platformAddress = getPlatformAddress()
  const oracleFeeBps = input.oracleFeeBps ?? 0 // 0% oracle fee by default

  const issueBetParams: IssueBetParams = {
    betDesc: input.question.substring(0, 31),
    options: options.map((o) => o.substring(0, 31)), // SC limit: 31 chars each
    oracleProviderIds: [platformAddress], // Platform is always the oracle
    oracleFees: [oracleFeeBps],
    closeDate: new Date(input.closeDate),
    endDate: new Date(input.endDate),
    amountPerSlot: BigInt(input.minBetQu ?? 10_000),
    maxBetSlotPerOption: input.maxSlots ?? 100,
  }

  // Deploy to Quottery SC
  try {
    db.updateMarketStatus(market.id, 'pending_tx')

    const seed = getPlatformSeed()
    const txResult = await issueBet(seed, issueBetParams)

    if (txResult.success) {
      // Discover the real on-chain betId assigned by the SC.
      // The SC assigns sequential IDs, so we poll getActiveBets + getBetInfo
      // to find our bet by matching the betDesc.
      const betDescKey = input.question.substring(0, 31).toLowerCase()
      let realBetId: number | null = null

      // Poll with retries — the TX takes 1-3 ticks (~3-9s) to confirm
      for (let attempt = 0; attempt < 5; attempt++) {
        await new Promise((r) => setTimeout(r, 3000))
        realBetId = await discoverBetId(betDescKey, 15)
        if (realBetId) break
        marketLog.info({ attempt: attempt + 1, maxAttempts: 5 }, 'betId discovery attempt — not found yet')
      }

      if (realBetId) {
        marketLog.info({ betId: realBetId, marketId: market.id }, 'discovered real betId')
      } else {
        marketLog.warn({ marketId: market.id }, 'could not discover betId — storing 0, will retry')
      }

      db.activateMarket(market.id, realBetId ?? 0)

      const updatedMarket = db.getMarket(market.id)!
      return {
        success: true,
        market: updatedMarket,
        quotteryTx: txResult,
      }
    }

    db.updateMarketStatus(market.id, 'draft')
    return {
      success: false,
      market,
      error: `Quottery TX failed: ${txResult.error ?? 'Unknown error'}`,
    }
  } catch (err) {
    db.updateMarketStatus(market.id, 'draft')
    return {
      success: false,
      market,
      error: `Failed to deploy market: ${err instanceof Error ? err.message : 'Unknown error'}`,
    }
  }
}

/**
 * Place a bet on an existing market.
 *
 * Flow:
 * 1. Validate market is active + betting open
 * 2. Debit user's internal balance
 * 3. Record bet in DB
 * 4. Send joinBet TX to Quottery SC
 * 5. Update market pool stats
 */
export async function placeBet(
  input: PlaceBetInput,
): Promise<PlaceBetResult> {
  const db = getMarketDB()
  const market = db.getMarket(input.marketId)

  if (!market) {
    return { success: false, error: 'Market not found' }
  }

  // Validate
  const error = validatePlaceBet(input, market)
  if (error) return { success: false, error }

  // BigInt safety: prevent overflow for large bets
  const amountQuBig = BigInt(market.minBetQu) * BigInt(input.slots)
  if (amountQuBig > BigInt(Number.MAX_SAFE_INTEGER)) {
    return { success: false, error: 'Bet amount exceeds safe integer limit' }
  }
  const amountQu = Number(amountQuBig)

  // Debit user balance
  const debitResult = debitForBet(input.userAddress, amountQu, input.marketId)
  if (!debitResult.success) {
    return { success: false, error: debitResult.error }
  }

  // Record bet in DB
  const bet = db.createBet({
    marketId: input.marketId,
    userAddress: input.userAddress,
    option: input.option,
    slots: input.slots,
    amountQu,
  })

  // Provably Fair: Bet commitment
  const nonce = generateBetNonce()
  const betCommitment = createBetCommitment(
    input.marketId,
    input.userAddress,
    input.option,
    input.slots,
    nonce,
  )
  db.setBetCommitment(bet.id, betCommitment, nonce)

  // Provably Fair: Chain entry for bet placement
  appendToChain('bet_place', bet.id, {
    betId: bet.id,
    marketId: input.marketId,
    userAddress: input.userAddress,
    option: input.option,
    slots: input.slots,
    amountQu,
    commitmentHash: betCommitment,
  })

  // Send joinBet TX to Quottery SC
  if (market.quotteryBetId) {
    try {
      const seed = getPlatformSeed()
      const joinParams: JoinBetParams = {
        betId: market.quotteryBetId,
        numberOfSlot: input.slots,
        option: input.option,
      }

      const txResult = await joinBet(
        seed,
        joinParams,
        BigInt(amountQu),
      )

      if (txResult.success) {
        db.confirmBet(bet.id, txResult.txId)

        // Provably Fair: Chain entry for bet confirmation
        appendToChain('bet_confirm', bet.id, {
          betId: bet.id,
          txId: txResult.txId,
          targetTick: txResult.targetTick,
        })
      }

      // Take probability snapshot
      db.recordSnapshot(input.marketId)

      const updatedBet = db.getBet(bet.id)!
      return {
        success: true,
        bet: updatedBet,
        quotteryTx: txResult,
        commitmentHash: betCommitment,
        commitmentNonce: nonce,
      }
    } catch (err) {
      // TX failed -- rollback the bet and refund the user
      marketLog.error({ err, marketId: input.marketId }, 'joinBet TX failed, rolling back')
      db.rollbackBet(bet.id, input.userAddress, amountQu, input.marketId, input.option, input.slots)
      return {
        success: false,
        error: `Failed to place on-chain bet: ${err instanceof Error ? err.message : 'Unknown'}`,
      }
    }
  }

  // Note: createBet() already updates total_pool, yes/no_slots, and slots_json

  // No Quottery bet ID yet -- bet is queued for when market deploys
  return { success: true, bet, commitmentHash: betCommitment, commitmentNonce: nonce }
}

/**
 * Resolve a market after its endDate has passed.
 *
 * Flow:
 * 1. Check current price against resolution target
 * 2. Determine winning option
 * 3. Send publishResult TX to Quottery SC
 * 4. Calculate payouts
 * 5. Credit winners
 */
export async function resolveMarket(
  input: MarketResolutionInput,
): Promise<ResolveMarketResult> {
  const db = getMarketDB()
  const market = db.getMarket(input.marketId)

  if (!market) {
    return { success: false, error: 'Market not found' }
  }

  if (market.status !== 'active' && market.status !== 'closed') {
    return {
      success: false,
      error: `Cannot resolve market with status: ${market.status}`,
    }
  }

  // Check if end date has passed
  const now = new Date()
  const endDate = parseUtcTimestamp(market.endDate)
  if (now < endDate) {
    return { success: false, error: 'Market has not expired yet' }
  }

  // Determine winning option:
  // 1. If winningOption is provided directly (from oracle adapter), use it
  // 2. For price markets, determine from currentPrice
  let winningOption: number
  if (input.winningOption !== undefined) {
    // Direct resolution from oracle adapter (AI Council, Sports, Creator)
    if (input.winningOption < 0 || input.winningOption >= market.numOptions) {
      return { success: false, error: `Invalid winningOption: ${input.winningOption} (market has ${market.numOptions} options)` }
    }
    winningOption = input.winningOption
  } else if (input.currentPrice !== undefined) {
    // Price-based resolution
    winningOption = determineWinner(market, input.currentPrice)
  } else {
    return { success: false, error: 'Must provide either winningOption or currentPrice' }
  }

  // Store oracle proof if provided (for AI/Sports resolution audit trail)
  if (input.oracleProof) {
    db.recordAiResolutionAttempt(input.marketId, input.oracleProof)
  }

  // Atomically claim this market for resolution (prevents race condition
  // where both API and background resolver try to resolve simultaneously)
  const claimed = db.tryClaimForResolution(input.marketId)
  if (!claimed) {
    return { success: false, error: 'Market is already being resolved' }
  }

  // Send publishResult TX to Quottery SC
  let quotteryTx: QuotteryTxResult | undefined
  if (market.quotteryBetId) {
    try {
      const seed = getPlatformSeed()
      const publishParams: PublishResultParams = {
        betId: market.quotteryBetId,
        winOption: winningOption,
      }

      quotteryTx = await publishResult(seed, publishParams)
    } catch (err) {
      marketLog.error({ err, marketId: input.marketId }, 'publishResult TX failed')
      // Continue with local resolution even if SC TX fails
    }
  }

  // Resolve market in DB
  db.resolveMarket(
    input.marketId,
    input.currentPrice ?? 0,
    winningOption,
  )

  // Pool integrity: Recompute pool/slots from confirmed bet records only.
  // This prevents any ghost bets or data inconsistencies from affecting payouts.
  const confirmedBets = db.getBetsByMarket(input.marketId)
  const recomputedSlots: Record<string, number> = {}
  let recomputedPool = 0
  for (const bet of confirmedBets) {
    // Only count bets that have been funded (pending = deposit confirmed, confirmed = joinBet done)
    if (bet.status === 'pending' || bet.status === 'confirmed') {
      recomputedSlots[String(bet.option)] = (recomputedSlots[String(bet.option)] ?? 0) + bet.slots
      recomputedPool += bet.amountQu
    }
  }

  const totalPool = BigInt(recomputedPool)
  const winnerSlotCount = recomputedSlots[String(winningOption)] ?? 0
  const totalSlotCount = Object.values(recomputedSlots).reduce((s, n) => s + n, 0)

  const oracleFeeBps = market.oracleFeeBps // 0% by default

  const payoutCalc = estimatePayout(
    totalPool,
    1, // per-slot calculation
    winnerSlotCount,
    oracleFeeBps,
    totalSlotCount,
  )

  // Keep payout in BigInt for precision — only convert to Number for DB storage
  // BigInt division truncates (floor), so no rounding accumulation across bets
  const payoutPerSlotBig = payoutCalc.perSlotPayout
  const payoutPerSlot = Number(payoutPerSlotBig)

  // Resolve all bets and credit winners
  const { winners, losers } = db.resolveAllBetsForMarket(
    input.marketId,
    winningOption,
    payoutPerSlot,
  )

  // Calculate total loser slots across all non-winning options (from recomputed data)
  let loserSlots = 0
  for (const [optStr, count] of Object.entries(recomputedSlots)) {
    if (optStr !== String(winningOption)) loserSlots += count
  }

  // Provably Fair: Chain entry for market resolution
  appendToChain('market_resolve', input.marketId, {
    marketId: input.marketId,
    marketType: market.marketType,
    resolutionPrice: input.currentPrice ?? null,
    winningOption,
    winningOptionLabel: market.options[winningOption] ?? `Option ${winningOption}`,
    totalPool: recomputedPool,
    winnerSlots: winnerSlotCount,
    loserSlots,
    payoutPerSlot,
    winners,
    losers,
    oracleProof: input.oracleProof ?? null,
    quotteryTxId: quotteryTx?.txId ?? null,
  })

  // Provably Fair: Chain entries for each payout
  const resolvedBets = db.getBetsByMarket(input.marketId)
  for (const bet of resolvedBets) {
    if (bet.status === 'won' && bet.payoutQu) {
      appendToChain('payout', bet.id, {
        betId: bet.id,
        userAddress: bet.userAddress,
        marketId: input.marketId,
        payoutQu: bet.payoutQu,
        winningOption,
      })
    }
  }

  // Log fee breakdown for audit trail
  marketLog.info({ marketId: input.marketId, pool: recomputedPool, winnerSlots: winnerSlotCount, totalSlots: totalSlotCount, loserPool: payoutCalc.loserPool.toString(), fees: payoutCalc.totalFees.toString(), burn: payoutCalc.burn.toString(), shareholder: payoutCalc.shareholderFee.toString(), operator: payoutCalc.gameOperatorFee.toString(), perSlot: payoutPerSlot, winnerPool: payoutCalc.winnerPool.toString() }, 'payout calculation')

  // SOLVENCY CHECK: Total payouts must never exceed pool (after Quottery SC fees)
  // Use BigInt accumulation to prevent rounding errors with large pools
  const totalPayoutsBig = resolvedBets
    .filter((b) => b.status === 'won' && b.payoutQu)
    .reduce((sum, b) => sum + BigInt(b.payoutQu ?? 0), 0n)
  const totalPayouts = Number(totalPayoutsBig)
  if (totalPayouts > recomputedPool) {
    marketLog.fatal({ marketId: input.marketId, totalPayouts, totalPool: recomputedPool, delta: totalPayouts - recomputedPool }, 'SOLVENCY VIOLATION: payouts exceed pool')
    appendToChain('solvency_violation', input.marketId, {
      totalPayouts,
      totalPool: recomputedPool,
      delta: totalPayouts - recomputedPool,
    })
    // HALT: Do not proceed — this indicates a bug in payout calculation.
    // Escrows should NOT be marked won/lost until this is investigated.
    return {
      success: false,
      winningOption,
      error: `SOLVENCY VIOLATION: payouts (${totalPayouts}) exceed pool (${recomputedPool}). Market halted for review.`,
    }
  }

  // Mark losing escrows (transition active_in_sc → lost for non-winning options)
  // Mark winning escrows (transition active_in_sc → won_awaiting_sweep)
  try {
    const { markLosingEscrows, markWinningEscrows } = await import('./escrow-manager')
    const markedLost = markLosingEscrows(input.marketId, winningOption)
    const markedWon = markWinningEscrows(input.marketId, winningOption)
    if (markedLost > 0 || markedWon > 0) {
      marketLog.info({ marketId: input.marketId, won: markedWon, lost: markedLost }, 'escrows marked for market')
    }
  } catch (err) {
    marketLog.error({ err, marketId: input.marketId }, 'escrow marking failed')
  }

  const resolvedMarket = db.getMarket(input.marketId)!

  return {
    success: true,
    market: resolvedMarket,
    winningOption,
    winners,
    losers,
    payoutPerSlot,
    quotteryTx,
  }
}

/**
 * Cancel a market (creator or admin only).
 * All bettors are refunded.
 */
export async function cancelMarket(
  marketId: string,
): Promise<{ success: boolean; error?: string }> {
  const db = getMarketDB()
  const market = db.getMarket(marketId)

  if (!market) return { success: false, error: 'Market not found' }
  if (market.status === 'resolved' || market.status === 'cancelled') {
    return { success: false, error: `Cannot cancel market with status: ${market.status}` }
  }

  // Cancel on Quottery SC
  if (market.quotteryBetId) {
    try {
      const seed = getPlatformSeed()
      await cancelBet(seed, { betId: market.quotteryBetId })
    } catch (err) {
      marketLog.error({ err, marketId }, 'cancelBet TX failed')
    }
  }

  // Refund all bets
  const bets = db.getBetsByMarket(marketId)
  for (const bet of bets) {
    if (bet.status === 'pending' || bet.status === 'confirmed') {
      // Funded bets: credit the user's internal balance back
      creditWinnings(bet.userAddress, bet.amountQu)
      db.recordTransaction({
        address: bet.userAddress,
        type: 'refund',
        amountQu: bet.amountQu,
        marketId,
        status: 'confirmed',
      })
    } else if (bet.status === 'pending_deposit') {
      // Unfunded escrow bets: no credit needed (pool was never incremented).
      // Just mark as refunded so they're cleaned up.
      db.setBetStatus(bet.id, 'refunded')
    }
  }

  db.updateMarketStatus(marketId, 'cancelled')
  return { success: true }
}

// ---------------------------------------------------------------------------
// Resolution Logic
// ---------------------------------------------------------------------------

/**
 * Determine the winning option based on market type and current price.
 *
 * Returns 0 for Yes, 1 for No.
 */
function determineWinner(market: Market, currentPrice: number): number {
  switch (market.resolutionType) {
    case 'price_above':
      // Yes = price >= target
      return currentPrice >= market.resolutionTarget ? 0 : 1

    case 'price_below':
      // Yes = price <= target
      return currentPrice <= market.resolutionTarget ? 0 : 1

    case 'price_range':
      // Yes = price in [target, targetHigh]
      if (market.resolutionTargetHigh !== null) {
        return currentPrice >= market.resolutionTarget &&
          currentPrice <= market.resolutionTargetHigh
          ? 0
          : 1
      }
      return currentPrice >= market.resolutionTarget ? 0 : 1

    case 'price_bracket': {
      // Multi-option brackets: find which bracket the price falls into
      // Options are ordered: [<bracket1, bracket1-bracket2, ..., >bracketN]
      const brackets = extractBracketBoundaries(market)
      if (!brackets || brackets.length === 0) return 0

      for (let i = 0; i < brackets.length; i++) {
        if (currentPrice < brackets[i]!) return i
      }
      return brackets.length // last option (above all brackets)
    }

    default:
      return 1 // Default to No if unknown type
  }
}

/**
 * Extract bracket boundaries for price_bracket markets.
 * Tries ai_resolution_proof.brackets first, then falls back to evenly-spaced.
 */
function extractBracketBoundaries(market: Market): number[] | null {
  // Try brackets stored in ai_resolution_proof
  try {
    const proof = market.aiResolutionProof as { brackets?: number[] } | null
    if (proof?.brackets && Array.isArray(proof.brackets)) {
      return proof.brackets
    }
  } catch { /* fallback */ }

  // Fallback: evenly spaced brackets from resolutionTarget to resolutionTargetHigh
  if (market.numOptions < 2) return null
  const base = market.resolutionTarget
  const high = market.resolutionTargetHigh
  if (!high || high <= base) return null

  const step = (high - base) / (market.numOptions - 1)
  const boundaries: number[] = []
  for (let i = 1; i < market.numOptions; i++) {
    boundaries.push(base + step * i)
  }
  return boundaries
}

// ---------------------------------------------------------------------------
// Query Functions
// ---------------------------------------------------------------------------

/**
 * Get a market by ID with all related data.
 */
export interface ResolutionStats {
  winners: number
  losers: number
  winnerSlots: number
  totalPayoutQu: number
  payoutPerSlot: number
}

export function getMarketDetail(marketId: string): {
  market: Market
  bets: UserBet[]
  snapshots: MarketSnapshot[]
  impliedProbability: number
  resolutionStats: ResolutionStats | null
} | null {
  const db = getMarketDB()
  const market = db.getMarket(marketId)
  if (!market) return null

  const bets = db.getBetsByMarket(marketId)
  const snapshots = db.getSnapshots(marketId)
  // Use slotsPerOption (v2) for implied probability — consistent with all data sources
  const yesSlots = market.slotsPerOption['0'] ?? market.yesSlots
  const noSlots = market.slotsPerOption['1'] ?? market.noSlots
  const impliedProbability = MarketDatabase.calcImpliedProbability(yesSlots, noSlots)

  // Compute resolution stats if market is resolved
  let resolutionStats: ResolutionStats | null = null
  if (market.status === 'resolved') {
    const winnerBets = bets.filter((b) => b.status === 'won')
    const loserBets = bets.filter((b) => b.status === 'lost')
    const totalPayoutQu = winnerBets.reduce((s, b) => s + (b.payoutQu ?? 0), 0)
    const winnerSlots = winnerBets.reduce((s, b) => s + b.slots, 0)
    const payoutPerSlot = winnerSlots > 0 ? Math.floor(totalPayoutQu / winnerSlots) : 0
    resolutionStats = {
      winners: winnerBets.length,
      losers: loserBets.length,
      winnerSlots,
      totalPayoutQu,
      payoutPerSlot,
    }
  }

  return { market, bets, snapshots, impliedProbability, resolutionStats }
}

/**
 * List markets with filtering.
 */
export function listMarkets(filter?: {
  status?: MarketStatus
  pair?: string
  marketType?: MarketType
}): (Market & { impliedProbability: number })[] {
  const db = getMarketDB()
  const markets = db.listMarkets(filter)

  return markets.map((m) => ({
    ...m,
    impliedProbability: MarketDatabase.calcImpliedProbability(
      m.slotsPerOption['0'] ?? m.yesSlots,
      m.slotsPerOption['1'] ?? m.noSlots,
    ),
  }))
}

/**
 * List recently resolved markets (ordered by resolved_at DESC).
 * Used for the "Recent Results" section on the predict page.
 */
export function listRecentResolvedMarkets(limit: number = 5): (Market & { impliedProbability: number })[] {
  const db = getMarketDB()
  const markets = db.listRecentResolved(limit)

  return markets.map((m) => ({
    ...m,
    impliedProbability: MarketDatabase.calcImpliedProbability(
      m.slotsPerOption['0'] ?? m.yesSlots,
      m.slotsPerOption['1'] ?? m.noSlots,
    ),
  }))
}

/**
 * Get bets for a user across all markets.
 */
export function getUserBets(
  userAddress: string,
): (UserBet & { marketQuestion?: string; marketPair?: string })[] {
  const db = getMarketDB()
  const bets = db.getBetsByUser(userAddress)

  return bets.map((bet) => {
    const market = db.getMarket(bet.marketId)
    return {
      ...bet,
      marketQuestion: market?.question,
      marketPair: market?.pair,
    }
  })
}

/**
 * Get platform stats.
 */
export function getStats(): PlatformStats {
  return getMarketDB().getPlatformStats()
}

/**
 * Get leaderboard.
 */
export function getLeaderboard(
  minBets?: number,
  limit?: number,
): LeaderboardEntry[] {
  return getMarketDB().getLeaderboard(minBets, limit)
}

/**
 * Resolve a market using the oracle adapter system.
 * Called by the Market Engine for automatic resolution.
 */
export async function resolveMarketViaOracle(
  market: Market,
): Promise<ResolveMarketResult> {
  // Dynamic import to avoid circular dependencies
  const { tryResolveMarket } = await import('./oracle-adapters')

  const oracleResult = await tryResolveMarket(market)

  if (!oracleResult) {
    // For AI markets, record the failed attempt
    if (market.marketType === 'ai') {
      const db = getMarketDB()
      db.recordAiResolutionAttempt(market.id, null)
    }
    return {
      success: false,
      error: `No oracle result available for market ${market.id} (type: ${market.marketType})`,
    }
  }

  return resolveMarket({
    marketId: market.id,
    currentPrice: market.marketType === 'price'
      ? (oracleResult.proof.data as { medianPrice?: number })?.medianPrice
      : undefined,
    winningOption: oracleResult.winningOption,
    oracleProof: oracleResult.proof,
  })
}

/**
 * Auto-refund markets that have passed their auto_refund_at deadline.
 * Called periodically by the Market Engine.
 * Returns number of markets refunded.
 */
export async function autoRefundExpiredMarkets(): Promise<number> {
  const db = getMarketDB()
  const markets = db.getMarketsNeedingAutoRefund()

  let refunded = 0
  for (const market of markets) {
    marketLog.info({ marketId: market.id, question: market.question }, 'auto-refunding market')
    const result = await cancelMarket(market.id)
    if (result.success) refunded++
  }

  return refunded
}

/**
 * Check and close markets that have passed their close date.
 * Called periodically by the background service.
 */
export function closeExpiredBetting(): number {
  const db = getMarketDB()
  const closing = db.getClosingMarkets()

  for (const market of closing) {
    db.updateMarketStatus(market.id, 'closed')
  }

  return closing.length
}

/**
 * Get markets ready for resolution (end date passed).
 * Called periodically by the market resolver service.
 */
export function getMarketsReadyForResolution(): Market[] {
  return getMarketDB().getExpiredMarkets()
}

/**
 * Get markets needing AI resolution (end date passed, AI type, attempts < 3).
 * Called by the Market Engine for AI Council resolution.
 */
export function getMarketsNeedingAiResolution(): Market[] {
  return getMarketDB().getMarketsNeedingAiResolution()
}

/**
 * Discover betIds for markets that were activated with quotteryBetId = 0.
 * Called periodically by the background service.
 * Returns number of markets with newly discovered betIds.
 */
export async function discoverPendingBetIds(): Promise<number> {
  const db = getMarketDB()
  const markets = db.listMarkets({ status: 'active' })
  let discovered = 0

  for (const market of markets) {
    if (market.quotteryBetId !== 0) continue // Already has a real betId

    const betDescKey = market.question.substring(0, 31).toLowerCase()
    const realBetId = await discoverBetId(betDescKey, 20)

    if (realBetId) {
      db.activateMarket(market.id, realBetId)
      marketLog.info({ betId: realBetId, marketId: market.id }, 'background betId discovery')
      discovered++
    }
  }

  return discovered
}

/**
 * Repair slotsPerOption by re-counting from actual bet records.
 * Fixes markets where the v2 slots_json was not updated properly.
 */
export function repairSlotCounts(): number {
  const db = getMarketDB()
  const markets = db.listMarkets()
  let repaired = 0

  for (const market of markets) {
    const bets = db.getBetsByMarket(market.id)
    const computed: Record<string, number> = {}
    // Initialize all options to 0
    for (let i = 0; i < market.numOptions; i++) {
      computed[String(i)] = 0
    }
    // Sum slots from funded bets only (skip pending_deposit and refunded)
    for (const bet of bets) {
      if (bet.status === 'pending' || bet.status === 'confirmed' || bet.status === 'won' || bet.status === 'lost') {
        computed[String(bet.option)] = (computed[String(bet.option)] ?? 0) + bet.slots
      }
      // pending_deposit bets are intentionally excluded — they haven't deposited yet
    }

    // Check if slotsPerOption needs repair
    let needsRepair = false
    for (const [opt, count] of Object.entries(computed)) {
      if ((market.slotsPerOption[opt] ?? 0) !== count) {
        needsRepair = true
        break
      }
    }

    if (needsRepair) {
      // Compute total pool from bets
      let totalPool = 0
      for (const bet of bets) {
        if (bet.status !== 'refunded') {
          totalPool += bet.amountQu
        }
      }
      db.repairSlotsJson(market.id, computed, totalPool)
      repaired++
    }
  }

  return repaired
}

/**
 * Re-compute and repair commitment hashes for all markets.
 * Needed when market parameters were manually modified after initial creation.
 */
export function repairCommitmentHashes(): number {
  const db = getMarketDB()
  const markets = db.listMarkets()
  let repaired = 0

  for (const market of markets) {
    const correct = createMarketCommitment({
      pair: market.pair,
      question: market.question,
      resolutionType: market.resolutionType,
      resolutionTarget: market.resolutionTarget,
      resolutionTargetHigh: market.resolutionTargetHigh ?? null,
      closeDate: market.closeDate,
      endDate: market.endDate,
      minBetQu: market.minBetQu,
      maxSlots: market.maxSlots,
      creatorAddress: market.creatorAddress ?? '',
    })

    if (market.commitmentHash !== correct) {
      db.setMarketCommitment(market.id, correct)
      repaired++
      marketLog.info({ marketId: market.id }, 'repaired commitment hash')
    }
  }

  return repaired
}

// ---------------------------------------------------------------------------
// Stuck Market Recovery
// ---------------------------------------------------------------------------

/** Timeout thresholds for stuck market detection */
const PENDING_TX_TIMEOUT_MS = 30 * 60 * 1000 // 30 minutes
const RESOLVING_TIMEOUT_MS = 60 * 60 * 1000 // 1 hour
const BETID_ZERO_TIMEOUT_MS = 60 * 60 * 1000 // 1 hour

/**
 * Detect and handle markets stuck in intermediate states.
 *
 * Called as Phase 0d in the auto-cron loop.
 *
 * Recovery actions:
 * - pending_tx (>30 min): Cancel with refund
 * - resolving (>1 hr): Revert to 'closed' for retry
 * - active with betId=0 (>1 hr): Retry discoverBetId, cancel if still 0
 *
 * @returns Number of markets recovered
 */
export async function handleStuckMarkets(): Promise<number> {
  const db = getMarketDB()
  const allMarkets = db.listMarkets()
  let recovered = 0
  const now = Date.now()

  for (const market of allMarkets) {
    try {
      // --- pending_tx: issueBet TX was sent but market never activated ---
      if (market.status === 'pending_tx') {
        const age = now - parseUtcTimestamp(market.createdAt).getTime()
        if (age > PENDING_TX_TIMEOUT_MS) {
          marketLog.warn(
            { marketId: market.id, ageMin: Math.floor(age / 60000) },
            'stuck market: pending_tx timeout — cancelling',
          )
          await cancelMarket(market.id)
          appendToChain('market_recovery', market.id, {
            marketId: market.id,
            stuckState: 'pending_tx',
            ageMs: age,
            action: 'cancelled',
          })
          recovered++
        }
        continue
      }

      // --- resolving: tryClaimForResolution succeeded but resolution never completed ---
      // Use endDate as the reference: resolution should happen shortly after endDate.
      // If endDate is more than 1 hour in the past and status is still 'resolving',
      // the resolution process is stuck.
      if (market.status === 'resolving') {
        const endTime = parseUtcTimestamp(market.endDate).getTime()
        if (now - endTime > RESOLVING_TIMEOUT_MS) {
          marketLog.warn(
            { marketId: market.id },
            'stuck market: resolving timeout — reverting to closed',
          )
          db.updateMarketStatus(market.id, 'closed')
          appendToChain('market_recovery', market.id, {
            marketId: market.id,
            stuckState: 'resolving',
            endDate: market.endDate,
            action: 'reverted_to_closed',
          })
          recovered++
        }
        continue
      }

      // --- active with betId=0: SC deploy succeeded but betId was never discovered ---
      if (market.status === 'active' && market.quotteryBetId === 0) {
        const age = now - parseUtcTimestamp(market.createdAt).getTime()
        if (age > BETID_ZERO_TIMEOUT_MS) {
          // One last try to discover the betId
          const betDescKey = market.question.substring(0, 31).toLowerCase()
          const realBetId = await discoverBetId(betDescKey, 20)

          if (realBetId) {
            db.activateMarket(market.id, realBetId)
            marketLog.info(
              { marketId: market.id, betId: realBetId },
              'stuck market: betId discovered on retry',
            )
            appendToChain('market_recovery', market.id, {
              marketId: market.id,
              stuckState: 'active_betid_zero',
              action: 'betid_discovered',
              betId: realBetId,
            })
            recovered++
          } else {
            marketLog.warn(
              { marketId: market.id },
              'stuck market: betId still 0 after 1hr — cancelling',
            )
            await cancelMarket(market.id)
            appendToChain('market_recovery', market.id, {
              marketId: market.id,
              stuckState: 'active_betid_zero',
              action: 'cancelled',
            })
            recovered++
          }
        }
        continue
      }
    } catch (err) {
      // Isolate failures: one market's recovery error must not block others
      marketLog.error(
        { err, marketId: market.id, status: market.status },
        'stuck market recovery failed',
      )
    }
  }

  return recovered
}
