/**
 * QPredict Custodial Balance System
 *
 * Manages user funds in a custodial model:
 * - Users deposit QU to platform address
 * - Internal balances tracked in SQLite
 * - Platform master wallet signs all Quottery TXs
 * - Users can withdraw to their own address
 *
 * Security model:
 * - All on-chain TXs use the platform master seed
 * - User funds are tracked off-chain in the DB
 * - Deposit detection runs as background service
 * - Withdrawals require sufficient internal balance
 */

import {
  getMarketDB,
  type Account,
  type Transaction,
} from './market-db'
import { getBalance, getCurrentTick } from '@/lib/qubic/quottery-client'
import {
  buildChainEntry,
  GENESIS_HASH,
  type ChainEventType,
} from './provably-fair'

// ---------------------------------------------------------------------------
// Provably Fair: Chain Entry Helper
// ---------------------------------------------------------------------------

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
// Configuration
// ---------------------------------------------------------------------------

/** Platform master wallet address (from env) */
function getPlatformAddress(): string {
  const addr = process.env.MASTER_IDENTITY
  if (!addr) throw new Error('MASTER_IDENTITY not set in environment')
  return addr
}

/** Platform master seed (from env, never exposed) */
function getPlatformSeed(): string {
  const seed = process.env.MASTER_SEED
  if (!seed) throw new Error('MASTER_SEED not set in environment')
  return seed
}

/** Minimum deposit amount (QU) */
const MIN_DEPOSIT = 1_000

/** Maximum single withdrawal (QU) */
const MAX_WITHDRAWAL = 10_000_000

/** Withdrawal fee (QU) — covers TX cost */
const WITHDRAWAL_FEE = 10

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface DepositResult {
  success: boolean
  account: Account
  amountQu: number
  error?: string
}

export interface WithdrawalResult {
  success: boolean
  txId?: string
  amountQu: number
  fee: number
  error?: string
}

export interface BetDebitResult {
  success: boolean
  amountQu: number
  error?: string
}

export interface WinCreditResult {
  success: boolean
  amountQu: number
  error?: string
}

// ---------------------------------------------------------------------------
// Custody Operations
// ---------------------------------------------------------------------------

/**
 * Register a new user account or return existing.
 * The user gets the platform deposit address to send QU.
 */
export function registerAccount(
  userAddress: string,
  displayName?: string,
): {
  account: Account
  depositAddress: string
  depositInstructions: string
} {
  const db = getMarketDB()
  const account = db.ensureAccount(userAddress, displayName)

  return {
    account,
    depositAddress: getPlatformAddress(),
    depositInstructions: `Send QU to ${getPlatformAddress()} from your address ${userAddress}. Deposits are detected automatically within ~60 seconds. Minimum deposit: ${MIN_DEPOSIT} QU.`,
  }
}

/**
 * Credit a deposit to a user's internal balance.
 * Called by the deposit detector when an incoming TX is found.
 */
export function creditDeposit(
  userAddress: string,
  amountQu: number,
  txHash?: string,
): DepositResult {
  if (amountQu < MIN_DEPOSIT) {
    return {
      success: false,
      account: getMarketDB().ensureAccount(userAddress),
      amountQu,
      error: `Deposit below minimum: ${amountQu} < ${MIN_DEPOSIT} QU`,
    }
  }

  const db = getMarketDB()
  db.creditDeposit(userAddress, amountQu)

  // Record the TX hash if provided
  if (txHash) {
    db.recordTransaction({
      address: userAddress,
      type: 'deposit',
      amountQu,
      txHash,
      status: 'confirmed',
    })
  }

  // Provably Fair: Chain entry for deposit
  appendToChain('deposit', userAddress, {
    userAddress,
    amountQu,
    txHash: txHash ?? null,
  })

  const account = db.getAccount(userAddress)!
  return { success: true, account, amountQu }
}

/**
 * Request a withdrawal from internal balance to user's on-chain address.
 *
 * Flow:
 * 1. Check sufficient balance
 * 2. Debit internal balance
 * 3. Queue on-chain TX (sent by background service or immediately)
 */
export function requestWithdrawal(
  userAddress: string,
  amountQu: number,
): WithdrawalResult {
  if (amountQu <= WITHDRAWAL_FEE) {
    return {
      success: false,
      amountQu,
      fee: WITHDRAWAL_FEE,
      error: `Amount must be greater than withdrawal fee (${WITHDRAWAL_FEE} QU)`,
    }
  }

  if (amountQu > MAX_WITHDRAWAL) {
    return {
      success: false,
      amountQu,
      fee: WITHDRAWAL_FEE,
      error: `Amount exceeds maximum withdrawal (${MAX_WITHDRAWAL} QU)`,
    }
  }

  const db = getMarketDB()
  const account = db.getAccount(userAddress)

  if (!account) {
    return {
      success: false,
      amountQu,
      fee: WITHDRAWAL_FEE,
      error: 'Account not found',
    }
  }

  if (account.balanceQu < amountQu) {
    return {
      success: false,
      amountQu,
      fee: WITHDRAWAL_FEE,
      error: `Insufficient balance: ${account.balanceQu} < ${amountQu} QU`,
    }
  }

  // Debit internal balance (amount includes fee)
  db.debitWithdrawal(userAddress, amountQu)

  // Provably Fair: Chain entry for withdrawal
  appendToChain('withdrawal', userAddress, {
    userAddress,
    amountQu,
    netAmount: amountQu - WITHDRAWAL_FEE,
    fee: WITHDRAWAL_FEE,
  })

  return {
    success: true,
    amountQu: amountQu - WITHDRAWAL_FEE,
    fee: WITHDRAWAL_FEE,
  }
}

/**
 * Debit user balance for placing a bet.
 * Called when a user places a bet on a market.
 */
export function debitForBet(
  userAddress: string,
  amountQu: number,
  marketId: string,
): BetDebitResult {
  const db = getMarketDB()
  const account = db.getAccount(userAddress)

  if (!account) {
    return {
      success: false,
      amountQu,
      error: 'Account not found. Please register first.',
    }
  }

  // Atomic check+debit to prevent race conditions with concurrent bets
  const success = db.atomicDebitBet(userAddress, amountQu, marketId)
  if (!success) {
    return {
      success: false,
      amountQu,
      error: `Insufficient balance for ${amountQu} QU bet. Please deposit more.`,
    }
  }

  return { success: true, amountQu }
}

/**
 * Credit winnings to user balance after market resolution.
 * Called by the market resolver when a user wins.
 */
export function creditWinnings(
  userAddress: string,
  amountQu: number,
): WinCreditResult {
  const db = getMarketDB()
  db.creditWinnings(userAddress, amountQu)
  return { success: true, amountQu }
}

/**
 * Get account info with balance.
 */
export function getAccountInfo(userAddress: string): Account | null {
  return getMarketDB().getAccount(userAddress)
}

/**
 * Get transaction history for a user.
 */
export function getTransactionHistory(userAddress: string): Transaction[] {
  return getMarketDB().getTransactions(userAddress)
}

/**
 * Get the platform wallet balance (on-chain).
 * Used by admin to monitor the platform's QU reserves.
 */
export async function getPlatformBalance(): Promise<{
  onChainBalance: bigint
  totalUserBalances: number
  reserve: bigint
}> {
  const platformAddr = getPlatformAddress()
  const onChainBalance = await getBalance(platformAddr)

  // Precise sum of all user balances from accounts table
  const db = getMarketDB()
  const totalUserBalances = db.getTotalUserBalance()

  // Reserve = on-chain balance minus total owed to users
  const reserve = onChainBalance - BigInt(totalUserBalances)

  return {
    onChainBalance,
    totalUserBalances,
    reserve,
  }
}

/**
 * Get the platform master seed for signing TXs.
 * Only accessible server-side.
 */
export { getPlatformSeed, getPlatformAddress }
