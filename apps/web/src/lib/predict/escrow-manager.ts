/**
 * Escrow Manager — Per-Bet Single-Use Qubic Address Lifecycle
 *
 * Each bet gets a freshly generated Qubic address (escrow).
 * Users deposit to the escrow, the system calls joinBet on the Quottery SC,
 * and after resolution, winnings are swept from the escrow to the user's
 * payout address.
 *
 * Lifecycle:
 *   awaiting_deposit → deposit_detected → joining_sc → active_in_sc
 *   → won_awaiting_sweep → swept → completed
 *   OR: lost → completed
 *   OR: expired (no deposit after timeout)
 */

import crypto from 'crypto'
import { getMarketDB, type EscrowAddress } from './market-db'
import { encryptSeed, decryptSeed, deriveMasterKey, type EncryptedSeed } from './key-vault'
import { generateSeed, createIdentity, validatePublicId } from '@/lib/qubic/agent-integration/identity'
import { joinBet, getBalance, getCurrentTick, rpcCall } from '@/lib/qubic/quottery-client'
import type { JoinBetParams } from '@/lib/qubic/quottery-client'
import { escrowLog } from './logger'
import { parseUtcTimestamp } from './api-utils'
import { sendAlert } from './alerting'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DEFAULT_EXPIRY_HOURS = 2
// Qubic standard transfers have no explicit fee. Previous value of 1000
// left dust in every escrow. Set to 0 so sweep sends the full balance.
const QUBIC_TX_FEE_QU = 0
const JOINBET_TIMEOUT_TICKS = Number(process.env.JOINBET_TIMEOUT_TICKS) || 600 // ~10 min
const SWEEP_TIMEOUT_TICKS = Number(process.env.SWEEP_TIMEOUT_TICKS) || 300 // ~5 min

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface CreateEscrowInput {
  marketId: string
  userPayoutAddress: string
  option: number // 0=YES, 1=NO
  slots: number
  minBetQu: number // per-slot cost
  quotteryBetId: number // on-chain bet ID
}

export interface CreateEscrowResult {
  betId: string
  escrowId: string
  escrowAddress: string
  expectedAmountQu: number
  expiresAt: string
  status: 'awaiting_deposit'
}

export interface EscrowStatusResult {
  escrowId: string
  betId: string
  marketId: string
  escrowAddress: string
  userPayoutAddress: string
  option: number
  slots: number
  expectedAmountQu: number
  status: string
  depositAmountQu: number | null
  payoutAmountQu: number | null
  sweepTxId: string | null
  joinBetTxId: string | null
  expiresAt: string
  createdAt: string
}

// ---------------------------------------------------------------------------
// Create Escrow
// ---------------------------------------------------------------------------

/**
 * Generate a fresh Qubic escrow address for a new bet.
 *
 * 1. Generate seed → derive public address
 * 2. Encrypt seed with AES-256-GCM
 * 3. Store escrow + encrypted key in DB
 * 4. Return deposit instructions
 */
export async function createEscrow(input: CreateEscrowInput): Promise<CreateEscrowResult> {
  // Validate payout address
  if (!validatePublicId(input.userPayoutAddress)) {
    throw new Error('Invalid payout address: must be 60 uppercase letters')
  }

  if (input.slots < 1) {
    throw new Error('Must bet at least 1 slot')
  }

  if (input.minBetQu < 10_000) {
    throw new Error('Minimum bet per slot is 10,000 QU (Quottery SC limit)')
  }

  // BigInt safety: prevent overflow for large bets (e.g., 10B QU × 100 slots)
  const expectedAmountBig = BigInt(input.minBetQu) * BigInt(input.slots)
  if (expectedAmountBig > BigInt(Number.MAX_SAFE_INTEGER)) {
    throw new Error(`Bet amount exceeds safe integer limit: ${expectedAmountBig} QU`)
  }
  const expectedAmountQu = Number(expectedAmountBig)
  const betId = `bet_${crypto.randomBytes(8).toString('hex')}`

  // Generate a fresh Qubic identity
  const seed = generateSeed()
  const identity = await createIdentity(`escrow-${betId}`, seed)

  // Encrypt the seed
  const masterKey = deriveMasterKey()
  const encrypted = encryptSeed(seed.value, masterKey)

  // Calculate expiry
  const expiryHours = Number(process.env.ESCROW_EXPIRY_HOURS) || DEFAULT_EXPIRY_HOURS
  const expiresAt = new Date(Date.now() + expiryHours * 60 * 60 * 1000).toISOString()

  const db = getMarketDB()

  // Atomic: create escrow + bet + key + slot reservation in one transaction
  const escrow = db.transaction(() => {
    // Create the bet record with status='pending_deposit'.
    // Pool/slots are NOT updated here — they are deferred to confirmBetDeposit()
    // which is called after the on-chain deposit is verified. This prevents
    // "ghost bets" from inflating the pool before real funds arrive.
    db.createBet({
      marketId: input.marketId,
      userAddress: input.userPayoutAddress,
      option: input.option,
      slots: input.slots,
      amountQu: expectedAmountQu,
      skipPoolUpdate: true,
    })

    // Get the bet we just created (it's the most recent one)
    const bets = db.getBetsByUser(input.userPayoutAddress)
    const bet = bets[0]
    if (!bet) throw new Error('Failed to create bet record')

    // Create escrow address record
    const escrowRecord = db.createEscrow({
      betId: bet.id,
      marketId: input.marketId,
      escrowAddress: identity.publicId,
      userPayoutAddress: input.userPayoutAddress,
      option: input.option,
      slots: input.slots,
      expectedAmountQu,
      expiresAt,
    })

    // Store encrypted key
    db.insertEscrowKey({
      escrowId: escrowRecord.id,
      encryptedSeed: encrypted.ciphertext,
      iv: encrypted.iv,
      authTag: encrypted.authTag,
    })

    return escrowRecord
  })

  return {
    betId: escrow.betId,
    escrowId: escrow.id,
    escrowAddress: escrow.escrowAddress,
    expectedAmountQu,
    expiresAt,
    status: 'awaiting_deposit',
  }
}

// ---------------------------------------------------------------------------
// Check Escrow Status
// ---------------------------------------------------------------------------

/**
 * Get the current status of a bet/escrow.
 */
export function getEscrowStatus(escrowIdOrBetId: string): EscrowStatusResult | null {
  const db = getMarketDB()
  let escrow: EscrowAddress | null = null

  if (escrowIdOrBetId.startsWith('esc_')) {
    escrow = db.getEscrow(escrowIdOrBetId)
  } else if (escrowIdOrBetId.startsWith('bet_')) {
    escrow = db.getEscrowByBet(escrowIdOrBetId)
  }

  if (!escrow) return null

  return {
    escrowId: escrow.id,
    betId: escrow.betId,
    marketId: escrow.marketId,
    escrowAddress: escrow.escrowAddress,
    userPayoutAddress: escrow.userPayoutAddress,
    option: escrow.option,
    slots: escrow.slots,
    expectedAmountQu: escrow.expectedAmountQu,
    status: escrow.status,
    depositAmountQu: escrow.depositAmountQu,
    payoutAmountQu: escrow.payoutAmountQu,
    sweepTxId: escrow.sweepTxId,
    joinBetTxId: escrow.joinBetTxId,
    expiresAt: escrow.expiresAt,
    createdAt: escrow.createdAt,
  }
}

// ---------------------------------------------------------------------------
// Cancel Escrow (pre-deposit)
// ---------------------------------------------------------------------------

/**
 * Cancel an escrow that has not yet received a deposit.
 *
 * Safety checks:
 *   1. Escrow must be in 'awaiting_deposit' status
 *   2. On-chain balance must be 0 (no funds sent)
 *
 * On success:
 *   - Escrow status → 'expired'
 *   - Bet status → 'cancelled' (via refunded)
 *   - Key → archived (securely overwritten)
 *   - All changes are atomic (single SQLite transaction)
 */
export async function cancelEscrow(escrowId: string): Promise<{
  success: boolean
  error?: string
}> {
  const db = getMarketDB()
  const escrow = db.getEscrow(escrowId)

  if (!escrow) {
    return { success: false, error: 'Escrow not found' }
  }

  if (escrow.status !== 'awaiting_deposit') {
    return {
      success: false,
      error: `Cannot cancel: escrow status is '${escrow.status}', must be 'awaiting_deposit'`,
    }
  }

  // Verify no funds have been sent to the escrow address on-chain
  try {
    const balance = await getBalance(escrow.escrowAddress)
    if (balance > 0n) {
      return {
        success: false,
        error: 'Cannot cancel: funds detected on escrow address. Wait for deposit processing.',
      }
    }
  } catch (err) {
    return {
      success: false,
      error: `Cannot verify escrow balance: ${err instanceof Error ? err.message : String(err)}`,
    }
  }

  // Atomic DB transaction: expire escrow, cancel bet, archive key
  try {
    db.transaction(() => {
      db.updateEscrowStatus(escrowId, 'expired')
      db.setBetStatus(escrow.betId, 'refunded')
      db.updateEscrowKeyStatus(escrowId, 'archived')
    })

    escrowLog.info(
      { escrowId, betId: escrow.betId, marketId: escrow.marketId },
      'escrow cancelled by user (pre-deposit)',
    )

    return { success: true }
  } catch (err) {
    escrowLog.error(
      { escrowId, err },
      'failed to cancel escrow',
    )
    return {
      success: false,
      error: `Cancellation failed: ${err instanceof Error ? err.message : String(err)}`,
    }
  }
}

// ---------------------------------------------------------------------------
// Deposit Detection
// ---------------------------------------------------------------------------

/**
 * Check if a deposit has arrived at an escrow address.
 * Called by the background monitor.
 *
 * @returns The detected balance, or 0 if no deposit yet
 */
export async function checkEscrowDeposit(escrowId: string): Promise<bigint> {
  const db = getMarketDB()
  const escrow = db.getEscrow(escrowId)
  if (!escrow) throw new Error(`Escrow not found: ${escrowId}`)
  if (escrow.status !== 'awaiting_deposit') return 0n

  // Handle expired escrows — check for late deposits before archiving
  if (parseUtcTimestamp(escrow.expiresAt) < new Date()) {
    const balance = await getBalance(escrow.escrowAddress)
    if (balance > BigInt(QUBIC_TX_FEE_QU)) {
      // Late deposit arrived — trigger refund sweep (key stays active)
      escrowLog.warn({ escrowId, balance: balance.toString() }, 'late deposit on expired escrow — initiating refund')
      db.updateEscrowStatus(escrowId, 'won_awaiting_sweep')
      db.setBetStatus(escrow.betId, 'refunded')
      return balance
    }
    db.markEscrowExpired(escrowId)
    db.updateEscrowKeyStatus(escrowId, 'archived')
    db.setBetStatus(escrow.betId, 'refunded')
    return 0n
  }

  const balance = await getBalance(escrow.escrowAddress)
  if (balance >= BigInt(escrow.expectedAmountQu)) {
    db.recordEscrowDeposit(escrowId, Number(balance))
    // Confirm the bet deposit: transitions pending_deposit → pending
    // and atomically updates the market pool/slot counts.
    // This is the ONLY point where escrow bets affect the pool.
    const confirmed = db.confirmBetDeposit(escrow.betId)
    if (!confirmed) {
      // Slots no longer available — mark for refund
      escrowLog.warn({ escrowId, betId: escrow.betId }, 'slots full — marking for refund')
      db.updateEscrowStatus(escrowId, 'won_awaiting_sweep') // trigger sweep back to user
      db.setBetStatus(escrow.betId, 'refunded')
    }
    return balance
  }

  return balance
}

// ---------------------------------------------------------------------------
// Execute JoinBet
// ---------------------------------------------------------------------------

/**
 * Execute the joinBet transaction on the Quottery SC from the escrow address.
 * Called after deposit is detected.
 *
 * Decrypts the escrow seed, calls joinBet, and updates status.
 */
export async function executeJoinBet(escrowId: string): Promise<{
  success: boolean
  txId?: string
  tick?: number
  error?: string
}> {
  const db = getMarketDB()
  const escrow = db.getEscrow(escrowId)
  if (!escrow) throw new Error(`Escrow not found: ${escrowId}`)

  if (escrow.status !== 'deposit_detected') {
    throw new Error(`Cannot execute joinBet: escrow status is '${escrow.status}', expected 'deposit_detected'`)
  }

  // Get the market to find the on-chain betId
  const market = db.getMarket(escrow.marketId)
  if (!market) throw new Error(`Market not found: ${escrow.marketId}`)
  if (!market.quotteryBetId) throw new Error(`Market has no on-chain betId: ${escrow.marketId}`)

  // Decrypt the escrow seed
  const keyEntry = db.getEscrowKey(escrowId)
  if (!keyEntry) throw new Error(`Escrow key not found: ${escrowId}`)

  const masterKey = deriveMasterKey()
  const seed = decryptSeed(
    {
      ciphertext: keyEntry.encryptedSeed,
      iv: keyEntry.iv,
      authTag: keyEntry.authTag,
    },
    masterKey,
  )

  // Update status to joining_sc
  db.updateEscrowStatus(escrowId, 'joining_sc')

  try {
    const joinParams: JoinBetParams = {
      betId: market.quotteryBetId,
      numberOfSlot: escrow.slots,
      option: escrow.option,
    }

    const result = await joinBet(
      seed,
      joinParams,
      BigInt(escrow.expectedAmountQu),
    )

    if (result.success) {
      db.recordEscrowJoinBet(escrowId, result.txId, result.targetTick)
      // Confirm the bet record
      db.confirmBet(escrow.betId, result.txId)
      return { success: true, txId: result.txId, tick: result.targetTick }
    } else {
      // Revert status + increment retry counter
      db.updateEscrowStatus(escrowId, 'deposit_detected')
      db.incrementJoinBetRetries(escrowId)
      const retries = (db.getEscrow(escrowId)?.joinBetRetries ?? 0)

      if (retries >= 3) {
        // Permanent failure after 3 retries — trigger refund sweep
        escrowLog.error({ escrowId, retries }, 'joinBet failed max retries — initiating refund')
        db.updateEscrowStatus(escrowId, 'won_awaiting_sweep')
        db.setBetStatus(escrow.betId, 'refunded')
        void sendAlert('joinbet_max_retries', 'error', `joinBet failed after ${retries} retries — refunding`, { escrowId, marketId: escrow.marketId })
      }

      return { success: false, error: result.error || 'joinBet failed' }
    }
  } catch (err) {
    // Revert status on error + increment retry counter
    db.updateEscrowStatus(escrowId, 'deposit_detected')
    db.incrementJoinBetRetries(escrowId)
    const retries = (db.getEscrow(escrowId)?.joinBetRetries ?? 0)

    if (retries >= 3) {
      escrowLog.error({ escrowId, retries }, 'joinBet errored max retries — initiating refund')
      db.updateEscrowStatus(escrowId, 'won_awaiting_sweep')
      db.setBetStatus(escrow.betId, 'refunded')
      void sendAlert('joinbet_max_retries', 'error', `joinBet errored after ${retries} retries — refunding`, { escrowId, marketId: escrow.marketId })
    }

    return { success: false, error: err instanceof Error ? err.message : String(err) }
  }
}

// ---------------------------------------------------------------------------
// JoinBet On-Chain Confirmation
// ---------------------------------------------------------------------------

/**
 * Verify that a joinBet TX was actually confirmed on-chain.
 * Called by the cron job for escrows in 'joining_sc' state.
 *
 * Strategy: After joinBet broadcast, the escrow's on-chain balance should drop
 * (funds moved to the Quottery SC). If balance dropped below expectedAmountQu,
 * the joinBet landed. If balance is still >= expectedAmountQu after timeout,
 * the TX failed — revert to deposit_detected for retry.
 */
export async function verifyJoinBetConfirmation(escrowId: string): Promise<{
  confirmed: boolean
  error?: string
}> {
  const db = getMarketDB()
  const escrow = db.getEscrow(escrowId)
  if (!escrow || escrow.status !== 'joining_sc') {
    return { confirmed: false, error: `Not in joining_sc state: ${escrow?.status}` }
  }

  try {
    const balance = await getBalance(escrow.escrowAddress)
    const expectedDeposit = BigInt(escrow.expectedAmountQu)

    // If balance dropped well below the expected deposit, funds left → joinBet confirmed
    // After a successful joinBet, the escrow should have ~0 QU (or just dust/TX fee remainder)
    if (balance < expectedDeposit / 2n) {
      db.confirmJoinBet(escrowId)
      escrowLog.info({ escrowId, balance: balance.toString(), expected: escrow.expectedAmountQu }, 'joinBet confirmed')
      return { confirmed: true }
    }

    // Balance still high — joinBet TX may not have landed yet.
    // Check timeout based on tick distance.
    if (escrow.joinBetTick) {
      const { tick: currentTick } = await getCurrentTick()
      const ticksElapsed = currentTick - escrow.joinBetTick

      // After timeout, assume the TX failed
      if (ticksElapsed > JOINBET_TIMEOUT_TICKS) {
        escrowLog.warn({ escrowId, joinBetTick: escrow.joinBetTick, currentTick, balance: balance.toString() }, 'joinBet TX timed out — reverting for retry')
        db.revertJoinBet(escrowId)
        db.incrementJoinBetRetries(escrowId)

        const retries = db.getEscrow(escrowId)?.joinBetRetries ?? 0
        if (retries >= 3) {
          escrowLog.error({ escrowId, retries }, 'joinBet timed out max retries — initiating refund')
          db.updateEscrowStatus(escrowId, 'won_awaiting_sweep')
          db.setBetStatus(escrow.betId, 'refunded')
          void sendAlert('joinbet_max_retries', 'error', `joinBet timed out after ${retries} retries — refunding`, { escrowId, marketId: escrow.marketId })
        }

        return { confirmed: false, error: 'joinBet TX timed out — reverted for retry' }
      }
    }

    // Still waiting — not yet timed out
    return { confirmed: false }
  } catch (err) {
    return { confirmed: false, error: `Balance check failed: ${err instanceof Error ? err.message : String(err)}` }
  }
}

// ---------------------------------------------------------------------------
// Payout Detection
// ---------------------------------------------------------------------------

/**
 * Check if a payout has arrived at an escrow address after market resolution.
 * Called by the background monitor for winning escrows.
 *
 * IMPORTANT: Only checks AFTER the market is resolved. Before resolution,
 * the escrow address still holds the user's deposit (since joinBet is
 * simulated), which must NOT be mistaken for a SC payout.
 *
 * @returns The detected payout amount, or 0 if no payout yet
 */
export async function checkEscrowPayout(escrowId: string): Promise<bigint> {
  const db = getMarketDB()
  const escrow = db.getEscrow(escrowId)
  if (!escrow) throw new Error(`Escrow not found: ${escrowId}`)
  if (escrow.status !== 'active_in_sc') return 0n

  // Only check for payouts after market is resolved
  // Before resolution, any balance is the user's original deposit, not a SC payout
  const market = db.getMarket(escrow.marketId)
  if (!market || market.status !== 'resolved') return 0n

  const balance = await getBalance(escrow.escrowAddress)
  if (balance > 0n) {
    db.recordEscrowPayout(escrowId, Number(balance))
    return balance
  }

  return 0n
}

// ---------------------------------------------------------------------------
// Execute Sweep (Payout to User)
// ---------------------------------------------------------------------------

/**
 * Sweep funds from the escrow address to the user's payout address.
 * Called after payout is detected at the escrow.
 *
 * Uses atomic claim (won_awaiting_sweep → sweeping) to prevent double-sweep.
 * After broadcast, stays in 'sweeping' state until confirmed by verifySweepConfirmation().
 * Key is NOT archived until sweep is confirmed on-chain.
 */
export async function executeSweep(escrowId: string): Promise<{
  success: boolean
  txId?: string
  tick?: number
  amountQu?: number
  error?: string
}> {
  const db = getMarketDB()
  const escrow = db.getEscrow(escrowId)
  if (!escrow) throw new Error(`Escrow not found: ${escrowId}`)

  // Safety: only sweep after market is resolved (prevents premature payouts)
  const market = db.getMarket(escrow.marketId)
  if (market && market.status !== 'resolved' && market.status !== 'cancelled') {
    return { success: false, error: `Market not yet resolved (status: ${market.status})` }
  }

  // Atomic claim FIRST: acquire exclusive lock before any async operations.
  // This eliminates the TOCTOU window where two processes could both pass
  // the balance check and then race for the claim.
  if (escrow.status === 'won_awaiting_sweep') {
    const claimed = db.claimEscrowForSweep(escrowId)
    if (!claimed) {
      return { success: false, error: 'Escrow is already being swept by another process' }
    }
  } else if (escrow.status !== 'sweeping') {
    return { success: false, error: `Cannot sweep: escrow status is '${escrow.status}', expected 'won_awaiting_sweep' or 'sweeping'` }
  }

  // Balance check AFTER acquiring lock — safe from race conditions
  const preBalance = await getBalance(escrow.escrowAddress)
  if (preBalance <= BigInt(QUBIC_TX_FEE_QU)) {
    db.revertSweepClaim(escrowId)
    return { success: false, error: `Escrow balance too low to sweep: ${preBalance} QU — SC payout may not have arrived yet` }
  }

  // Decrypt the escrow seed — key must still be 'active'
  const keyEntry = db.getEscrowKey(escrowId)
  if (!keyEntry) {
    db.revertSweepClaim(escrowId)
    throw new Error(`Escrow key not found: ${escrowId}`)
  }
  if (keyEntry.status !== 'active') {
    db.revertSweepClaim(escrowId)
    throw new Error(`Escrow key is not active: ${keyEntry.status} — cannot sign sweep TX`)
  }

  let seed: string
  try {
    const masterKey = deriveMasterKey()
    seed = decryptSeed(
      {
        ciphertext: keyEntry.encryptedSeed,
        iv: keyEntry.iv,
        authTag: keyEntry.authTag,
      },
      masterKey,
    )
  } catch (err) {
    // Decryption failed — revert claim so cron can retry
    db.revertSweepClaim(escrowId)
    return {
      success: false,
      error: `Seed decryption failed: ${err instanceof Error ? err.message : String(err)}`,
    }
  }

  // Re-check balance after claim (in case of race with late SC payout)
  const balance = await getBalance(escrow.escrowAddress)
  if (balance <= BigInt(QUBIC_TX_FEE_QU)) {
    db.revertSweepClaim(escrowId)
    return { success: false, error: `Escrow balance dropped to ${balance} QU after claim — reverting` }
  }

  const sweepAmount = balance - BigInt(QUBIC_TX_FEE_QU)

  try {
    // Use Qubic SDK to create and send the transfer
    const { createRequire } = await import('module')
    const require = createRequire(import.meta.url)
    const qubicLib = require('@qubic-lib/qubic-ts-library').default
    const { QubicHelper, QubicTransaction } = qubicLib

    const helper = new QubicHelper()
    const { tick } = await getCurrentTick()
    const targetTick = tick + 5

    const txBytes = await helper.createTransaction(
      seed,
      escrow.userPayoutAddress,
      Number(sweepAmount),
      targetTick,
    )

    const tx = new QubicTransaction()
    const encoded = tx.encodeTransactionToBase64(txBytes)

    // Record sweep TX BEFORE broadcast — ensures sweepTxId is never null
    // when the escrow is in 'sweeping' state. This is critical for the
    // SQL-level guard in confirmSweepComplete().
    const txId = `sweep_${crypto.randomBytes(8).toString('hex')}`
    db.recordEscrowSweep(escrowId, txId, targetTick)

    try {
      // Broadcast via RPC
      await rpcCall<{ peersBroadcasted: number }>(
        '/broadcast-transaction',
        {
          method: 'POST',
          body: JSON.stringify({ encodedTransaction: encoded }),
        },
      )
    } catch (broadcastErr) {
      // Broadcast failed — clear the sweep record and revert claim for retry
      db.recordEscrowSweep(escrowId, '', 0) // Clear sweep TX
      db.revertSweepClaim(escrowId)
      return {
        success: false,
        error: `Sweep broadcast failed: ${broadcastErr instanceof Error ? broadcastErr.message : String(broadcastErr)}`,
      }
    }

    // Update payoutAmountQu with the ACTUAL swept amount (overrides the
    // pre-calculated estimate from markWinningEscrows). This is the source
    // of truth for how much QU the user actually receives.
    db.recordEscrowPayout(escrowId, Number(sweepAmount))

    escrowLog.info({ escrowId, amountQu: sweepAmount.toString(), payoutAddress: escrow.userPayoutAddress, tick: targetTick }, 'sweep TX broadcast')

    return {
      success: true,
      txId,
      tick: targetTick,
      amountQu: Number(sweepAmount),
    }
  } catch (err) {
    // TX creation failed — revert to won_awaiting_sweep so cron retries
    db.revertSweepClaim(escrowId)
    return {
      success: false,
      error: `Sweep failed: ${err instanceof Error ? err.message : String(err)}`,
    }
  }
}

/**
 * Verify that a sweep TX was confirmed on-chain.
 * Called by the cron job for escrows in 'sweeping' state.
 *
 * Checks if the escrow balance has dropped to ~0, indicating funds left.
 * If confirmed: transitions sweeping → swept, archives the key.
 * If not confirmed after timeout: reverts to won_awaiting_sweep for retry.
 */
export async function verifySweepConfirmation(escrowId: string): Promise<{
  confirmed: boolean
  error?: string
}> {
  const db = getMarketDB()
  const escrow = db.getEscrow(escrowId)
  if (!escrow || escrow.status !== 'sweeping') {
    return { confirmed: false, error: `Not in sweeping state: ${escrow?.status}` }
  }

  try {
    // CRITICAL: If no sweep TX was ever broadcast (sweepTxId is null),
    // the escrow is in an orphaned 'sweeping' state — revert immediately.
    // This prevents false confirmations when balance is 0 because joinBet
    // sent funds to the SC but the SC payout hasn't arrived yet.
    if (!escrow.sweepTxId) {
      escrowLog.warn({ escrowId }, 'orphaned sweeping state — no sweep TX recorded, reverting')
      db.revertSweepClaim(escrowId)
      return { confirmed: false, error: 'No sweep TX recorded — reverted to won_awaiting_sweep for retry' }
    }

    const balance = await getBalance(escrow.escrowAddress)

    if (balance <= BigInt(QUBIC_TX_FEE_QU)) {
      // Funds have left the escrow — attempt to confirm sweep.
      // Uses SQL-level guard: only transitions if sweep_tx_id IS NOT NULL.
      // This is the LAST LINE OF DEFENSE against false sweep confirmations.
      const confirmed = db.confirmSweepComplete(escrowId)
      if (!confirmed) {
        // SQL guard rejected the transition — sweep_tx_id is null despite balance being 0.
        // This means funds left for another reason (e.g., joinBet sent to SC, SC refund timing).
        escrowLog.error({ escrowId }, 'BLOCKED false sweep confirmation — balance=0, no sweep TX, reverting')
        db.revertSweepClaim(escrowId)
        return { confirmed: false, error: 'SQL guard blocked: sweep_tx_id is NULL but balance is 0 — reverted for investigation' }
      }
      db.updateEscrowKeyStatus(escrowId, 'swept')
      db.updateEscrowKeyStatus(escrowId, 'archived')
      escrowLog.info({ escrowId, balance: balance.toString(), sweepTxId: escrow.sweepTxId }, 'sweep confirmed')
      return { confirmed: true }
    }

    // Balance still present — sweep TX may not have landed yet.
    // Check how long we've been in 'sweeping' state.
    // If sweep was recorded > 5 minutes ago, assume TX failed and retry.
    const { tick: currentTick } = await getCurrentTick()
    if (escrow.sweepTick && currentTick - escrow.sweepTick > SWEEP_TIMEOUT_TICKS) {
      escrowLog.warn({ escrowId, sweepTick: escrow.sweepTick, currentTick }, 'sweep TX timed out — reverting for retry')
      db.revertSweepClaim(escrowId)
      return { confirmed: false, error: 'Sweep TX timed out — reverting for retry' }
    }

    return { confirmed: false }
  } catch (err) {
    return { confirmed: false, error: `Balance check failed: ${err instanceof Error ? err.message : String(err)}` }
  }
}

// ---------------------------------------------------------------------------
// Expiry & Cleanup
// ---------------------------------------------------------------------------

/**
 * Handle expired escrows (no deposit received within timeout).
 * Marks them as expired and cleans up keys.
 */
export async function handleExpiredEscrows(): Promise<number> {
  const db = getMarketDB()
  const expired = db.getExpiredEscrows()

  for (const escrow of expired) {
    // SAFETY: Check if funds arrived at the escrow address before archiving the key.
    // If a user sent funds just before expiry, we must refund them — not lock them out.
    let hasBalance = false
    try {
      const balance = await getBalance(escrow.escrowAddress)
      hasBalance = balance > BigInt(QUBIC_TX_FEE_QU)
    } catch {
      // If balance check fails, assume no balance (safe default for expiry)
    }

    if (hasBalance) {
      // Late deposit detected — trigger refund sweep instead of archiving key
      escrowLog.warn({ escrowId: escrow.id }, 'late deposit on expired escrow — initiating refund sweep')
      db.updateEscrowStatus(escrow.id, 'won_awaiting_sweep')
      db.setBetStatus(escrow.betId, 'refunded')
      // Key stays 'active' so executeSweep can sign the refund TX
      continue
    }

    // No balance — safe to expire and archive
    db.markEscrowExpired(escrow.id)
    db.updateEscrowKeyStatus(escrow.id, 'archived')

    // Clean up the bet record.
    // Since ghost-bet prevention ensures pending_deposit bets never update the pool,
    // we can safely mark them as refunded without needing to rollback pool/slots.
    const bet = db.getBet(escrow.betId)
    if (bet && bet.status === 'pending_deposit') {
      // No pool rollback needed — pool was never incremented for pending_deposit bets
      db.setBetStatus(escrow.betId, 'refunded')
    } else if (bet && (bet.status === 'pending' || bet.status === 'confirmed')) {
      // This bet WAS funded — need to rollback pool (shouldn't normally happen
      // for expired escrows, but handle defensively)
      db.rollbackBet(
        escrow.betId,
        escrow.userPayoutAddress,
        escrow.expectedAmountQu,
        escrow.marketId,
        escrow.option,
        escrow.slots,
      )
    } else {
      db.setBetStatus(escrow.betId, 'refunded')
    }
  }

  return expired.length
}

/**
 * Mark losing escrows after market resolution.
 * Also handles joining_sc escrows (joinBet never confirmed) — those get refunded.
 */
export function markLosingEscrows(marketId: string, winningOption: number): number {
  const db = getMarketDB()
  const escrows = db.getEscrowsByMarket(marketId)
  let count = 0

  for (const escrow of escrows) {
    if (escrow.status === 'active_in_sc' && escrow.option !== winningOption) {
      db.markEscrowLost(escrow.id)
      db.updateEscrowKeyStatus(escrow.id, 'archived')
      count++
    }
    // joining_sc escrows: joinBet never landed on-chain, funds still on escrow.
    // Regardless of option, these need refund (not lost/won in SC).
    if (escrow.status === 'joining_sc' && escrow.option !== winningOption) {
      escrowLog.warn({ escrowId: escrow.id }, 'losing escrow still in joining_sc — initiating refund')
      db.updateEscrowStatus(escrow.id, 'won_awaiting_sweep')
      db.setBetStatus(escrow.betId, 'refunded')
      count++
    }
  }

  return count
}

/**
 * Mark winning escrows after market resolution.
 * Transitions active_in_sc → won_awaiting_sweep for winning escrows.
 * Records the expected payout amount from the already-resolved bet record.
 *
 * Also handles joining_sc escrows (joinBet never confirmed) — those get refunded
 * since they never entered the SC pool and can't claim SC winnings.
 *
 * The actual on-chain sweep is performed by the cron job (Phase 4)
 * which calls executeSweep() for each won_awaiting_sweep escrow.
 * Keys are NOT archived until the sweep TX is confirmed.
 */
export function markWinningEscrows(marketId: string, winningOption: number): number {
  const db = getMarketDB()
  const escrows = db.getEscrowsByMarket(marketId)
  let count = 0

  for (const escrow of escrows) {
    if (escrow.status === 'active_in_sc' && escrow.option === winningOption) {
      const bet = db.getBet(escrow.betId)
      const payoutQu = bet?.payoutQu ?? 0
      db.recordEscrowPayout(escrow.id, payoutQu)
      db.updateEscrowStatus(escrow.id, 'won_awaiting_sweep')
      // Key stays 'active' — needed by executeSweep() to sign the TX
      count++
    }
    // joining_sc escrows: joinBet never landed, funds still on escrow address.
    // Refund the deposit back to the user (won_awaiting_sweep triggers sweep).
    if (escrow.status === 'joining_sc' && escrow.option === winningOption) {
      escrowLog.warn({ escrowId: escrow.id }, 'winning escrow still in joining_sc — initiating refund')
      db.updateEscrowStatus(escrow.id, 'won_awaiting_sweep')
      db.setBetStatus(escrow.betId, 'refunded')
      count++
    }
  }

  return count
}

// ---------------------------------------------------------------------------
// Refund
// ---------------------------------------------------------------------------

/**
 * Refund an escrow back to the user's payout address.
 * Used when joinBet fails permanently or market is cancelled.
 */
export async function refundEscrow(escrowId: string): Promise<{
  success: boolean
  error?: string
}> {
  const db = getMarketDB()
  const escrow = db.getEscrow(escrowId)
  if (!escrow) throw new Error(`Escrow not found: ${escrowId}`)

  // Check balance
  const balance = await getBalance(escrow.escrowAddress)
  if (balance <= BigInt(QUBIC_TX_FEE_QU)) {
    db.updateEscrowStatus(escrowId, 'refunded')
    db.updateEscrowKeyStatus(escrowId, 'archived')
    return { success: true } // Nothing to refund
  }

  // Use sweep logic for refund
  db.updateEscrowStatus(escrowId, 'won_awaiting_sweep')
  const result = await executeSweep(escrowId)

  if (result.success) {
    db.updateEscrowStatus(escrowId, 'refunded')
    db.updateEscrowKeyStatus(escrowId, 'archived')
  } else {
    db.updateEscrowStatus(escrowId, 'deposit_detected') // revert
  }

  return result
}

// ---------------------------------------------------------------------------
// Query Helpers
// ---------------------------------------------------------------------------

/**
 * Get all escrows that need deposit checking.
 */
export function getAwaitingDepositEscrows(): EscrowAddress[] {
  return getMarketDB().getEscrowsByStatus('awaiting_deposit')
}

/**
 * Get all escrows that need payout checking (post-resolution).
 */
export function getActiveInScEscrows(): EscrowAddress[] {
  return getMarketDB().getEscrowsByStatus('active_in_sc')
}

/**
 * Get all escrows awaiting sweep.
 */
export function getAwaitingSweepEscrows(): EscrowAddress[] {
  return getMarketDB().getEscrowsByStatus('won_awaiting_sweep')
}

/** Get all escrows with broadcast but unconfirmed sweep TXs. */
export function getSweepingEscrows(): EscrowAddress[] {
  return getMarketDB().getSweepingEscrows()
}

/** Get all escrows with broadcast but unconfirmed joinBet TXs. */
export function getJoiningScEscrows(): EscrowAddress[] {
  return getMarketDB().getJoiningScEscrows()
}
