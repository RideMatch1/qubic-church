import { NextRequest, NextResponse } from 'next/server'
import { getMarketDB } from '@/lib/predict/market-db'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

/**
 * GET /api/predict/activity — Live activity feed
 *
 * Returns recent bets, market creations, and resolutions for the activity feed.
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const db = getMarketDB()
    const events: ActivityEvent[] = []

    // Get recent bets (from escrow_addresses for richer data)
    const allMarkets = db.listMarkets()

    for (const market of allMarkets.slice(0, 10)) {
      const escrows = db.getEscrowsByMarket(market.id)
      const options = market.options ?? ['Yes', 'No']

      for (const escrow of escrows) {
        if (escrow.status === 'awaiting_deposit' || escrow.status === 'expired') continue

        const addr = escrow.userPayoutAddress
        events.push({
          type: 'bet',
          marketId: market.id,
          question: market.question,
          address: `${addr.slice(0, 4)}...${addr.slice(-4)}`,
          option: options[escrow.option] ?? `Option ${escrow.option}`,
          amountQu: escrow.expectedAmountQu,
          slots: escrow.slots,
          status: escrow.status,
          timestamp: escrow.createdAt,
        })
      }

      // Market creation event
      events.push({
        type: 'market_created',
        marketId: market.id,
        question: market.question,
        timestamp: market.createdAt,
      })

      // Resolution event
      if (market.status === 'resolved' && market.winningOption !== null) {
        events.push({
          type: 'resolved',
          marketId: market.id,
          question: market.question,
          option: options[market.winningOption] ?? `Option ${market.winningOption}`,
          timestamp: market.resolvedAt ?? market.createdAt,
        })
      }
    }

    // Sort by timestamp descending, take top 20
    events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())

    return NextResponse.json({
      events: events.slice(0, 20),
    })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to get activity')
  }
}

interface ActivityEvent {
  type: 'bet' | 'market_created' | 'resolved'
  marketId: string
  question: string
  address?: string
  option?: string
  amountQu?: number
  slots?: number
  status?: string
  timestamp: string
}
