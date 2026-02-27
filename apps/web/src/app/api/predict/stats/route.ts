import { NextRequest, NextResponse } from 'next/server'
import { getStats, getLeaderboard } from '@/lib/predict/market-manager'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

/**
 * GET /api/predict/stats — Platform stats or leaderboard
 *
 * Query params:
 *   type: 'stats' (default) | 'leaderboard'
 *   minBets: minimum bets for leaderboard (default 3)
 *   limit: max entries for leaderboard (default 50)
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { searchParams } = new URL(request.url)
    const type = searchParams.get('type') ?? 'stats'

    if (type === 'leaderboard') {
      const minBets = parseInt(searchParams.get('minBets') ?? '3', 10)
      const limit = parseInt(searchParams.get('limit') ?? '50', 10)

      const leaderboard = getLeaderboard(
        isNaN(minBets) ? 3 : minBets,
        isNaN(limit) ? 50 : Math.min(limit, 100),
      )

      return NextResponse.json({
        leaderboard,
        count: leaderboard.length,
      })
    }

    const stats = getStats()
    return NextResponse.json(stats)
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch stats')
  }
}
