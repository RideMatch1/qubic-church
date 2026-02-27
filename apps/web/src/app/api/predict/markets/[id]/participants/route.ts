import { NextRequest, NextResponse } from 'next/server'
import { getMarketDB } from '@/lib/predict/market-db'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

/**
 * GET /api/predict/markets/[id]/participants — Full transparency view
 *
 * Returns all escrow participants for a market with stats.
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { id: marketId } = await params
    const db = getMarketDB()

    const market = db.getMarket(marketId)
    if (!market) {
      return NextResponse.json({ error: 'Market not found' }, { status: 404 })
    }

    const escrows = db.getEscrowsByMarket(marketId)
    const options = market.options ?? ['Yes', 'No']

    // Build participants list (only escrows that have been deposited or further)
    const participants = escrows
      .filter((e) => e.status !== 'awaiting_deposit' && e.status !== 'expired')
      .map((e) => {
        const addr = e.userPayoutAddress
        return {
          address: `${addr.slice(0, 4)}...${addr.slice(-4)}`,
          fullAddress: addr,
          option: e.option,
          optionLabel: options[e.option] ?? `Option ${e.option}`,
          slots: e.slots,
          amountQu: e.expectedAmountQu,
          status: e.status,
          escrowAddress: e.escrowAddress,
          joinBetTxId: e.joinBetTxId,
          timestamp: e.createdAt,
        }
      })

    // Build per-option stats
    const optionStats = options.map((label, i) => {
      const optParticipants = participants.filter((p) => p.option === i)
      return {
        option: i,
        label,
        totalSlots: optParticipants.reduce((sum, p) => sum + p.slots, 0),
        totalQu: optParticipants.reduce((sum, p) => sum + p.amountQu, 0),
        participants: optParticipants.length,
      }
    })

    const totalPool = optionStats.reduce((sum, o) => sum + o.totalQu, 0)

    return NextResponse.json({
      marketId,
      totalPool,
      participants,
      optionStats,
    })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to get participants')
  }
}
