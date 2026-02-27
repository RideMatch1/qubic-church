import { NextRequest, NextResponse } from 'next/server'
import { placeWager, validateAuthToken } from '@/lib/qflash/balance-manager'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse, validateQubicAddress } from '@/lib/predict/api-utils'
import type { Side } from '@/lib/qflash/types'

/**
 * POST /api/qflash/bet — Place a bet on a round
 *
 * Headers: Authorization: Bearer <api_token>
 * Body: { roundId, side, amountQu, address }
 */
export async function POST(request: NextRequest) {
  const rl = rateLimitResponse(request, 'POST /bet')
  if (rl) return rl

  try {
    // Auth check
    const authAccount = validateAuthToken(request.headers.get('authorization'))
    if (!authAccount) {
      return NextResponse.json({ error: 'Unauthorized — provide Bearer token' }, { status: 401 })
    }

    let body: {
      roundId?: string
      side?: string
      amountQu?: number
      address?: string
    }
    try {
      body = await request.json()
    } catch {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
    }

    // Validate required fields
    if (!body.roundId) {
      return NextResponse.json({ error: 'Missing required field: roundId' }, { status: 400 })
    }

    // Use the authenticated account's address
    const address = body.address ?? authAccount.address
    if (address !== authAccount.address) {
      return NextResponse.json({ error: 'Address does not match authenticated account' }, { status: 403 })
    }

    const addrError = validateQubicAddress(address)
    if (addrError) {
      return NextResponse.json({ error: addrError }, { status: 400 })
    }
    if (!body.side || !['up', 'down'].includes(body.side)) {
      return NextResponse.json({ error: 'side must be "up" or "down"' }, { status: 400 })
    }
    if (!body.amountQu || body.amountQu <= 0) {
      return NextResponse.json({ error: 'amountQu must be positive' }, { status: 400 })
    }

    const result = placeWager(
      address,
      body.roundId,
      body.side as Side,
      body.amountQu,
    )

    return NextResponse.json({
      entryId: result.entryId,
      roundId: body.roundId,
      side: body.side,
      amountQu: body.amountQu,
      newBalance: result.newBalance,
    }, { status: 201 })
  } catch (error) {
    const msg = error instanceof Error ? error.message : 'Failed to place bet'
    const isClientError = [
      'Insufficient balance',
      'Round is not open',
      'Already placed a bet',
      'Account not found',
      'Round not found',
      'Minimum bet',
      'Maximum bet',
      'Rate limit',
    ].some((prefix) => msg.includes(prefix))

    if (isClientError) {
      return NextResponse.json({ error: msg }, { status: 400 })
    }
    return safeErrorResponse(error, 'Failed to place bet')
  }
}
