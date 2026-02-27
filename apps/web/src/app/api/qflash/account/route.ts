import { NextRequest, NextResponse } from 'next/server'
import {
  getAccountBalance,
  getAccountTransactions,
  getOrCreateAccount,
  verifyAndCreditDeposit,
  validateAuthToken,
} from '@/lib/qflash/balance-manager'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse, validateQubicAddress } from '@/lib/predict/api-utils'

/**
 * GET /api/qflash/account — Get account balance + stats + recent transactions
 *
 * Query params:
 *   address: Qubic address (required)
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { searchParams } = new URL(request.url)
    const address = searchParams.get('address')

    if (!address) {
      return NextResponse.json({ error: 'Missing required param: address' }, { status: 400 })
    }
    const addrError = validateQubicAddress(address)
    if (addrError) {
      return NextResponse.json({ error: addrError }, { status: 400 })
    }

    const account = getAccountBalance(address)
    if (!account) {
      return NextResponse.json({ error: 'Account not found. Create one first via POST.' }, { status: 404 })
    }

    const transactions = getAccountTransactions(address, 20)

    // Strip apiToken from response
    const { apiToken: _token, ...safeAccount } = account

    return NextResponse.json({ account: safeAccount, recentTransactions: transactions })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch account')
  }
}

/**
 * POST /api/qflash/account — Create account or credit deposit
 *
 * Body: { address } — Create account (returns API token once)
 * Body: { address, amountQu, txHash } — Credit a deposit (requires auth)
 */
export async function POST(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    let body: { address?: string; amountQu?: number; txHash?: string }
    try {
      body = await request.json()
    } catch {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
    }

    if (!body.address) {
      return NextResponse.json({ error: 'Missing required field: address' }, { status: 400 })
    }
    const addrError = validateQubicAddress(body.address)
    if (addrError) {
      return NextResponse.json({ error: addrError }, { status: 400 })
    }

    // If amountQu provided, this is a deposit credit (requires auth)
    if (body.amountQu && body.amountQu > 0 && body.txHash) {
      const authAccount = validateAuthToken(request.headers.get('authorization'))
      if (!authAccount) {
        return NextResponse.json({ error: 'Unauthorized — provide Bearer token for deposits' }, { status: 401 })
      }
      if (authAccount.address !== body.address) {
        return NextResponse.json({ error: 'Address does not match authenticated account' }, { status: 403 })
      }

      const result = await verifyAndCreditDeposit(body.address, body.amountQu, body.txHash)
      const { apiToken: _token, ...safeAccount } = result.account
      return NextResponse.json({
        account: safeAccount,
        transaction: result.transaction,
        message: `Deposited ${body.amountQu.toLocaleString()} QU`,
      }, { status: 201 })
    }

    // Otherwise create/get account (public, returns token on first creation)
    const account = getOrCreateAccount(body.address)

    // Return token only on creation (when it exists)
    // The client should save it — it won't be shown again in GET responses
    const response: Record<string, unknown> = {
      account: {
        address: account.address,
        balanceQu: account.balanceQu,
        totalDeposited: account.totalDeposited,
        totalWithdrawn: account.totalWithdrawn,
        totalWagered: account.totalWagered,
        totalWon: account.totalWon,
        totalRefunded: account.totalRefunded,
        totalLost: account.totalLost,
        winCount: account.winCount,
        lossCount: account.lossCount,
        pushCount: account.pushCount,
        streak: account.streak,
        bestStreak: account.bestStreak,
        createdAt: account.createdAt,
      },
    }
    if (account.apiToken) {
      response.apiToken = account.apiToken
      response.message = 'Save your API token — it will not be shown again.'
    }

    return NextResponse.json(response, { status: 201 })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to create account')
  }
}
