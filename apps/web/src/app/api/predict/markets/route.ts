import { NextRequest, NextResponse } from 'next/server'
import {
  createMarket,
  resolveMarket,
  cancelMarket,
  listMarkets,
  listRecentResolvedMarkets,
  getMarketDetail,
  type CreateMarketInput,
} from '@/lib/predict/market-manager'
import type { Category } from '@/lib/predict/market-db'
import { ensureAutoCron } from '@/lib/predict/auto-cron'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import {
  safeErrorResponse,
  validateQubicAddress,
  validateStringLength,
  validateNumericBound,
} from '@/lib/predict/api-utils'

// Start background cron on first markets API call
ensureAutoCron()

/** Valid category values for filtering. */
const VALID_CATEGORIES = new Set<Category>([
  'crypto',
  'sports',
  'politics',
  'tech',
  'entertainment',
  'other',
])

/**
 * GET /api/predict/markets -- List markets
 *
 * Query params:
 *   status: 'active' | 'closed' | 'resolved' | 'draft'
 *   pair: 'btc/usdt' etc.
 *   marketType: 'price'
 *   category: 'crypto' | 'sports' | 'politics' | 'tech' | 'entertainment' | 'other'
 *   id: specific market ID (returns detail view)
 *   limit: max results (1-100, default unlimited)
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { searchParams } = new URL(request.url)
    const id = searchParams.get('id')
    const status = searchParams.get('status') as
      | 'active'
      | 'closed'
      | 'resolved'
      | 'draft'
      | null
    const pair = searchParams.get('pair')
    const marketType = searchParams.get('marketType')
    const categoryParam = searchParams.get('category')
    const limitParam = searchParams.get('limit')

    // Single market detail
    if (id) {
      const detail = getMarketDetail(id)
      if (!detail) {
        return NextResponse.json(
          { error: 'Market not found' },
          { status: 404 },
        )
      }
      return NextResponse.json(detail)
    }

    // Dedicated path for recent resolved markets (ordered by resolved_at DESC)
    if (status === 'resolved' && limitParam) {
      const limit = Math.min(Math.max(parseInt(limitParam, 10) || 5, 1), 100)
      const markets = listRecentResolvedMarkets(limit)
      return NextResponse.json({ markets, count: markets.length })
    }

    // Validate category if provided
    const category =
      categoryParam && VALID_CATEGORIES.has(categoryParam as Category)
        ? (categoryParam as Category)
        : null

    // List markets with optional filters
    const filter: Record<string, string> = {}
    if (status) filter.status = status
    if (pair) filter.pair = pair
    if (marketType) filter.marketType = marketType

    let markets = listMarkets(filter as Parameters<typeof listMarkets>[0])

    // Apply category filter (post-query filtering since the DB query
    // does not directly combine category with other arbitrary filters)
    if (category) {
      markets = markets.filter((m) => m.category === category)
    }

    // Optional limit
    if (limitParam) {
      const limit = Math.min(Math.max(parseInt(limitParam, 10) || 50, 1), 100)
      markets = markets.slice(0, limit)
    }

    return NextResponse.json({
      markets,
      count: markets.length,
    })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch markets')
  }
}

/**
 * POST /api/predict/markets -- Create a new market
 *
 * Body: CreateMarketInput
 */
export async function POST(request: NextRequest) {
  const rl = rateLimitResponse(request, 'POST /markets')
  if (rl) return rl

  try {
    let body: CreateMarketInput
    try {
      body = await request.json()
    } catch {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
    }

    // --- Input Validation ---

    // Question: required, 5-200 chars
    const questionErr = validateStringLength(body.question, 'question', 5, 200)
    if (questionErr) {
      return NextResponse.json({ error: questionErr }, { status: 400 })
    }

    // Dates: required
    if (!body.closeDate || !body.endDate) {
      return NextResponse.json(
        { error: 'Missing required fields: closeDate, endDate' },
        { status: 400 },
      )
    }

    // Validate dates are parseable and in the future
    const closeDate = new Date(body.closeDate)
    const endDate = new Date(body.endDate)
    const now = new Date()

    if (isNaN(closeDate.getTime()) || isNaN(endDate.getTime())) {
      return NextResponse.json(
        { error: 'closeDate and endDate must be valid ISO date strings' },
        { status: 400 },
      )
    }

    if (closeDate <= now) {
      return NextResponse.json(
        { error: 'closeDate must be in the future' },
        { status: 400 },
      )
    }

    // closeDate must be at most 365 days from now
    const maxDate = new Date(now.getTime() + 365 * 24 * 60 * 60 * 1000)
    if (closeDate > maxDate) {
      return NextResponse.json(
        { error: 'closeDate must be within 365 days from now' },
        { status: 400 },
      )
    }

    // endDate must be after closeDate by at least 60 seconds
    if (endDate.getTime() - closeDate.getTime() < 60_000) {
      return NextResponse.json(
        { error: 'endDate must be at least 60 seconds after closeDate' },
        { status: 400 },
      )
    }

    // Creator address: required, valid Qubic format
    const addrErr = validateQubicAddress(body.creatorAddress ?? '')
    if (addrErr) {
      return NextResponse.json(
        { error: `creatorAddress: ${addrErr}` },
        { status: 400 },
      )
    }

    // Market type: only price markets supported
    const marketType = 'price' as const
    if (body.marketType && body.marketType !== 'price') {
      return NextResponse.json(
        { error: 'Only price markets are currently supported' },
        { status: 400 },
      )
    }

    // Numeric bounds: slots, bet amounts, fees
    if (body.maxSlots !== undefined) {
      const slotsErr = validateNumericBound(body.maxSlots, 'maxSlots', 1, 10000)
      if (slotsErr) {
        return NextResponse.json({ error: slotsErr }, { status: 400 })
      }
    }

    if (body.minBetQu !== undefined) {
      const betErr = validateNumericBound(body.minBetQu, 'minBetQu', 10000, 1e12)
      if (betErr) {
        return NextResponse.json({ error: betErr }, { status: 400 })
      }
    }

    if (body.oracleFeeBps !== undefined) {
      const feeErr = validateNumericBound(body.oracleFeeBps, 'oracleFeeBps', 0, 5000)
      if (feeErr) {
        return NextResponse.json({ error: feeErr }, { status: 400 })
      }
    }

    // Option labels: max 50 chars each, max 10 options
    if (body.options) {
      if (!Array.isArray(body.options) || body.options.length < 2 || body.options.length > 10) {
        return NextResponse.json(
          { error: 'options must be an array of 2-10 strings' },
          { status: 400 },
        )
      }
      for (const opt of body.options) {
        if (typeof opt !== 'string' || opt.length > 50) {
          return NextResponse.json(
            { error: 'Each option label must be a string of max 50 characters' },
            { status: 400 },
          )
        }
      }
    }

    // Price markets require pair + target
    if (!body.pair || !body.resolutionTarget) {
      return NextResponse.json(
        { error: 'Price markets require: pair, resolutionTarget' },
        { status: 400 },
      )
    }
    if (!body.resolutionType) {
      body.resolutionType = 'price_above'
    }

    // Default 0% oracle fee
    if (body.oracleFeeBps === undefined) {
      body.oracleFeeBps = 0
    }

    const result = await createMarket(body)

    if (!result.success) {
      return NextResponse.json(
        { error: result.error },
        { status: 400 },
      )
    }

    return NextResponse.json(result, { status: 201 })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to create market')
  }
}

/**
 * PUT /api/predict/markets -- Resolve or cancel a market
 *
 * Body: { action: 'resolve' | 'cancel', marketId: string, currentPrice?: number }
 */
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json() as {
      action: string
      marketId: string
      currentPrice?: number
      winningOption?: number
    }

    if (!body.action || !body.marketId) {
      return NextResponse.json(
        { error: 'Missing required fields: action, marketId' },
        { status: 400 },
      )
    }

    if (body.action === 'resolve') {
      // Support both price-based and direct option resolution
      if (body.currentPrice === undefined && body.winningOption === undefined) {
        return NextResponse.json(
          { error: 'Must provide either currentPrice or winningOption' },
          { status: 400 },
        )
      }
      const result = await resolveMarket({
        marketId: body.marketId,
        currentPrice: body.currentPrice,
        winningOption: body.winningOption,
      })
      if (!result.success) {
        return NextResponse.json({ error: result.error }, { status: 400 })
      }
      return NextResponse.json(result)
    }

    if (body.action === 'cancel') {
      const result = await cancelMarket(body.marketId)
      if (!result.success) {
        return NextResponse.json({ error: result.error }, { status: 400 })
      }
      return NextResponse.json(result)
    }

    return NextResponse.json(
      { error: 'Unknown action. Use "resolve" or "cancel"' },
      { status: 400 },
    )
  } catch (error) {
    return safeErrorResponse(error, 'Failed to update market')
  }
}
