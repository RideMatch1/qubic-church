import { NextRequest, NextResponse } from 'next/server'
import { parseNaturalLanguageMarket } from '@/lib/predict/ai-market-creator'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

/**
 * POST /api/predict/ai-parse — Parse natural language into structured market
 *
 * Body: { query: string }
 *
 * Returns: { success, parsed, confidence, error? }
 */
export async function POST(request: NextRequest) {
  const rl = rateLimitResponse(request, 'POST /markets')
  if (rl) return rl

  try {
    const body = await request.json() as { query?: string }

    if (!body.query || typeof body.query !== 'string') {
      return NextResponse.json(
        { error: 'Missing required field: query (string)' },
        { status: 400 },
      )
    }

    if (body.query.length < 5) {
      return NextResponse.json(
        { error: 'Query too short (min 5 characters)' },
        { status: 400 },
      )
    }

    if (body.query.length > 500) {
      return NextResponse.json(
        { error: 'Query too long (max 500 characters)' },
        { status: 400 },
      )
    }

    const result = await parseNaturalLanguageMarket(body.query)

    return NextResponse.json(result)
  } catch (error) {
    return safeErrorResponse(error, 'Failed to parse market')
  }
}
