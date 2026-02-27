import crypto from 'crypto'
import { NextRequest, NextResponse } from 'next/server'
import { getMarketDB } from '@/lib/predict/market-db'
import {
  registerAccount,
  getAccountInfo,
  getTransactionHistory,
  requestWithdrawal,
} from '@/lib/predict/custody'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

// Withdrawal rate limit: 1 per 60 seconds per address (in-memory)
const withdrawalTimestamps = new Map<string, number>()
const WITHDRAWAL_RATE_LIMIT_MS = 60_000

/**
 * GET /api/predict/account — Get account info
 *
 * Query params:
 *   address: user's Qubic address (required)
 *   include: 'transactions' to include TX history
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { searchParams } = new URL(request.url)
    const address = searchParams.get('address')
    const include = searchParams.get('include')

    if (!address) {
      return NextResponse.json(
        { error: 'Missing required param: address' },
        { status: 400 },
      )
    }

    if (address.length !== 60 || !/^[A-Z]+$/.test(address)) {
      return NextResponse.json(
        { error: 'Invalid Qubic address format (60 uppercase letters)' },
        { status: 400 },
      )
    }

    const account = getAccountInfo(address)
    if (!account) {
      return NextResponse.json(
        { error: 'Account not found. Use POST to register.' },
        { status: 404 },
      )
    }

    const response: Record<string, unknown> = { account }

    if (include === 'transactions') {
      response.transactions = getTransactionHistory(address)
    }

    return NextResponse.json(response)
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch account')
  }
}

/**
 * Verify withdrawal signature using Qubic SDK or RESOLVE_SECRET fallback.
 */
async function verifyWithdrawalSignature(
  address: string,
  messageHash: Buffer,
  signatureHex: string,
): Promise<boolean> {
  try {
    const { createRequire } = await import('module')
    const require = createRequire(import.meta.url)
    const lib = require('@qubic-lib/qubic-ts-library').default
    const helper = new lib.QubicHelper()

    return await helper.verifySignature(
      address,
      messageHash,
      Buffer.from(signatureHex, 'hex'),
    )
  } catch {
    // SDK not available — use RESOLVE_SECRET for development
    const secret = process.env.RESOLVE_SECRET
    if (!secret) {
      throw new Error(
        'Neither Qubic SDK nor RESOLVE_SECRET is available for withdrawal verification',
      )
    }

    const expectedSig = crypto
      .createHmac('sha256', secret)
      .update(messageHash)
      .digest('hex')

    return signatureHex === expectedSig
  }
}

/**
 * POST /api/predict/account — Register account or request withdrawal
 *
 * Body for registration:
 *   { action: 'register', address: string, displayName?: string }
 *
 * Body for withdrawal (REQUIRES SIGNATURE):
 *   {
 *     action: 'withdraw',
 *     address: string,
 *     amountQu: number,
 *     signature: string,  // Schnorr sig of SHA256(address + amountQu + nonce)
 *     nonce: string,       // Unique nonce for replay prevention
 *   }
 */
export async function POST(request: NextRequest) {
  const rl = rateLimitResponse(request, 'POST /account/withdraw')
  if (rl) return rl

  try {
    let body: {
      action?: string
      address?: string
      displayName?: string
      amountQu?: number
      signature?: string
      nonce?: string
    }

    try {
      body = await request.json()
    } catch {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
    }

    if (!body.address) {
      return NextResponse.json(
        { error: 'Missing required field: address' },
        { status: 400 },
      )
    }

    if (body.address.length !== 60 || !/^[A-Z]+$/.test(body.address)) {
      return NextResponse.json(
        { error: 'Invalid Qubic address format (60 uppercase letters)' },
        { status: 400 },
      )
    }

    const action = body.action ?? 'register'

    switch (action) {
      case 'register': {
        const result = registerAccount(body.address, body.displayName)
        return NextResponse.json(result, { status: 201 })
      }

      case 'withdraw': {
        if (!body.amountQu || body.amountQu < 1) {
          return NextResponse.json(
            { error: 'amountQu must be at least 1' },
            { status: 400 },
          )
        }

        // SECURITY: Require signature proof of address ownership
        if (!body.signature || !body.nonce) {
          return NextResponse.json(
            { error: 'Withdrawal requires signature and nonce for authentication' },
            { status: 400 },
          )
        }

        if (body.nonce.length < 8 || body.nonce.length > 128) {
          return NextResponse.json(
            { error: 'Nonce must be 8-128 characters' },
            { status: 400 },
          )
        }

        // Rate limit: 1 withdrawal per 60 seconds per address
        const now = Date.now()
        const lastWithdrawal = withdrawalTimestamps.get(body.address) ?? 0
        if (now - lastWithdrawal < WITHDRAWAL_RATE_LIMIT_MS) {
          const retryAfter = Math.ceil((WITHDRAWAL_RATE_LIMIT_MS - (now - lastWithdrawal)) / 1000)
          return NextResponse.json(
            { error: 'Rate limited: max 1 withdrawal per 60 seconds' },
            { status: 429, headers: { 'Retry-After': String(retryAfter) } },
          )
        }

        // Replay prevention: check nonce
        const db = getMarketDB()
        const nonceValid = db.checkAndRecordNonce(body.nonce, body.address, 'withdraw')
        if (!nonceValid) {
          return NextResponse.json(
            { error: 'Nonce already used (replay attack prevented)' },
            { status: 409 },
          )
        }

        // Verify signature: proves requester controls the private key for this address
        const messagePayload = `${body.address}${body.amountQu}${body.nonce}`
        const messageHash = crypto.createHash('sha256').update(messagePayload).digest()

        let sigValid: boolean
        try {
          sigValid = await verifyWithdrawalSignature(
            body.address,
            messageHash,
            body.signature,
          )
        } catch (err) {
          return NextResponse.json(
            { error: `Signature verification unavailable: ${err instanceof Error ? err.message : 'SDK error'}` },
            { status: 503 },
          )
        }

        if (!sigValid) {
          return NextResponse.json(
            { error: 'Invalid signature: does not match address' },
            { status: 403 },
          )
        }

        // Record rate limit timestamp
        withdrawalTimestamps.set(body.address, now)

        const result = requestWithdrawal(body.address, body.amountQu)
        if (!result.success) {
          return NextResponse.json(
            { error: result.error },
            { status: 400 },
          )
        }

        return NextResponse.json(result)
      }

      default:
        return NextResponse.json(
          { error: `Unknown action: ${action}. Use 'register' or 'withdraw'.` },
          { status: 400 },
        )
    }
  } catch (error) {
    return safeErrorResponse(error, 'Account operation failed')
  }
}
