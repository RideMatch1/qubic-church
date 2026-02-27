import { NextRequest, NextResponse } from 'next/server'
import { getPrice } from '@/lib/qflash/price-feed'
import { getPriceHistory } from '@/lib/qflash/price-history'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

/**
 * GET /api/qflash/price — Live price for a trading pair
 *
 * Query params:
 *   pair: trading pair (e.g., 'btc/usdt')
 *   history: number of history ticks to return (default 60)
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { searchParams } = new URL(request.url)
    const pair = searchParams.get('pair')
    const historyLimit = Number(searchParams.get('history') ?? '60')

    if (!pair) {
      return NextResponse.json({ error: 'Missing required param: pair' }, { status: 400 })
    }

    const result = await getPrice(pair)

    if (!result) {
      return NextResponse.json(
        { error: 'Unable to fetch price — insufficient oracle sources' },
        { status: 503 },
      )
    }

    // Include price history for chart
    const history = getPriceHistory()
    const ticks = history.getHistory(pair, historyLimit)

    return NextResponse.json({
      ...result,
      history: ticks,
    })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch price')
  }
}
