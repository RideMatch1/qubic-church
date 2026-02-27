import { NextRequest, NextResponse } from 'next/server'
import {
  getUserBets,
} from '@/lib/predict/market-manager'
import { createEscrow, getEscrowStatus, cancelEscrow, type CreateEscrowInput } from '@/lib/predict/escrow-manager'
import { getMarketDB } from '@/lib/predict/market-db'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

/**
 * GET /api/predict/bet — Get bets for a user
 *
 * Query params:
 *   address: user's Qubic payout address (required)
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { searchParams } = new URL(request.url)
    const address = searchParams.get('address')

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

    const bets = getUserBets(address)

    // Enrich bets with escrow status
    const db = getMarketDB()
    const enriched = bets.map((bet) => {
      const escrow = db.getEscrowByBet(bet.id)
      return {
        ...bet,
        escrow: escrow
          ? {
              escrowId: escrow.id,
              escrowAddress: escrow.escrowAddress,
              status: escrow.status,
              depositAmountQu: escrow.depositAmountQu,
              payoutAmountQu: escrow.payoutAmountQu,
              sweepTxId: escrow.sweepTxId,
            }
          : null,
      }
    })

    return NextResponse.json({
      bets: enriched,
      count: enriched.length,
    })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch bets')
  }
}

/**
 * POST /api/predict/bet — Create a bet with per-bet escrow address
 *
 * Body: { marketId, payoutAddress, option, slots }
 *
 * Returns: escrow address + deposit instructions
 * The user must send the exact amount to the escrow address within 2 hours.
 */
export async function POST(request: NextRequest) {
  const rl = rateLimitResponse(request, 'POST /bet')
  if (rl) return rl

  try {
    // Idempotency: check for duplicate requests
    const idempotencyKey = request.headers.get('idempotency-key')
    if (idempotencyKey) {
      const db = getMarketDB()
      const cached = db.getIdempotencyResponse(idempotencyKey)
      if (cached) {
        return NextResponse.json(JSON.parse(cached), { status: 201 })
      }
    }

    let body: {
      marketId?: string
      payoutAddress?: string
      option?: number
      slots?: number
    }
    try {
      body = await request.json()
    } catch {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
    }

    if (!body.marketId) {
      return NextResponse.json(
        { error: 'Missing required field: marketId' },
        { status: 400 },
      )
    }

    if (!body.payoutAddress) {
      return NextResponse.json(
        { error: 'Missing required field: payoutAddress' },
        { status: 400 },
      )
    }

    if (
      body.payoutAddress.length !== 60 ||
      !/^[A-Z]+$/.test(body.payoutAddress)
    ) {
      return NextResponse.json(
        { error: 'Invalid Qubic address format for payoutAddress (60 uppercase letters)' },
        { status: 400 },
      )
    }

    if (body.option === undefined || body.option === null || body.option < 0) {
      return NextResponse.json(
        { error: 'Missing or invalid field: option (must be >= 0)' },
        { status: 400 },
      )
    }

    if (!body.slots || body.slots < 1) {
      return NextResponse.json(
        { error: 'Slots must be at least 1' },
        { status: 400 },
      )
    }

    if (body.slots > 10_000) {
      return NextResponse.json(
        { error: 'Maximum 10,000 slots per bet' },
        { status: 400 },
      )
    }

    // Get market details for validation
    const db = getMarketDB()
    const market = db.getMarket(body.marketId)

    if (!market) {
      return NextResponse.json(
        { error: 'Market not found' },
        { status: 404 },
      )
    }

    if (market.status !== 'active') {
      return NextResponse.json(
        { error: `Market is not active (status: ${market.status})` },
        { status: 400 },
      )
    }

    if (!market.quotteryBetId) {
      return NextResponse.json(
        { error: 'Market has no on-chain bet ID (not deployed to Quottery SC yet)' },
        { status: 400 },
      )
    }

    // Validate option is in range for this market
    const numOptions = market.numOptions ?? 2
    if (body.option >= numOptions) {
      const optionLabels = market.options ?? ['Yes', 'No']
      return NextResponse.json(
        { error: `Option must be 0-${numOptions - 1}. Available: ${optionLabels.join(', ')}` },
        { status: 400 },
      )
    }

    // Check if user already has bets on a different option
    const existingBets = db.getUserBetsForMarket(body.marketId, body.payoutAddress)
    for (const existingBet of existingBets) {
      if (existingBet.option !== body.option) {
        const optionLabels = market.options ?? ['Yes', 'No']
        const existingLabel = optionLabels[existingBet.option] ?? `Option ${existingBet.option}`
        return NextResponse.json(
          {
            error: `You already bet on "${existingLabel}" in this market. Cannot bet on multiple options.`,
          },
          { status: 400 },
        )
      }
    }

    // Soft slot check for fast UX feedback — real atomic enforcement is in
    // confirmBetDeposit() inside a SQLite transaction after deposit arrives.
    const slotsPerOption = market.slotsPerOption ?? {}
    const currentSlots = slotsPerOption[String(body.option)] ?? 0
    if (currentSlots + body.slots > market.maxSlots) {
      return NextResponse.json(
        { error: `Exceeds max slots for this option (${currentSlots}/${market.maxSlots} used)` },
        { status: 400 },
      )
    }

    // Create escrow
    const input: CreateEscrowInput = {
      marketId: body.marketId,
      userPayoutAddress: body.payoutAddress,
      option: body.option,
      slots: body.slots,
      minBetQu: market.minBetQu,
      quotteryBetId: market.quotteryBetId,
    }

    const result = await createEscrow(input)

    const optionLabels = market.options ?? ['Yes', 'No']
    const optionLabel = optionLabels[body.option] ?? `Option ${body.option}`

    const responseData = {
      ...result,
      market: {
        id: market.id,
        question: market.question,
        pair: market.pair,
        minBetQu: market.minBetQu,
      },
      option: optionLabel,
      instructions: `Send exactly ${result.expectedAmountQu.toLocaleString()} QU to ${result.escrowAddress} within 2 hours to confirm your bet.`,
    }

    // Store idempotency key for 24h dedup
    if (idempotencyKey) {
      const db2 = getMarketDB()
      db2.setIdempotencyResponse(idempotencyKey, JSON.stringify(responseData))
    }

    return NextResponse.json(responseData, { status: 201 })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to create bet')
  }
}

/**
 * DELETE /api/predict/bet — Cancel a bet before deposit
 *
 * Body: { escrowId: string }
 *
 * Only works for escrows in `awaiting_deposit` status with zero balance.
 */
export async function DELETE(request: NextRequest) {
  const rl = rateLimitResponse(request, 'POST /bet')
  if (rl) return rl

  try {
    let body: { escrowId?: string }
    try {
      body = await request.json()
    } catch {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
    }

    if (!body.escrowId) {
      return NextResponse.json(
        { error: 'Missing required field: escrowId' },
        { status: 400 },
      )
    }

    const result = await cancelEscrow(body.escrowId)

    if (!result.success) {
      return NextResponse.json(
        { error: result.error },
        { status: 400 },
      )
    }

    return NextResponse.json({ ok: true, escrowId: body.escrowId })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to cancel bet')
  }
}
