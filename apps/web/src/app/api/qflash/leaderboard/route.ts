import { NextRequest, NextResponse } from 'next/server'
import { getQFlashDB } from '@/lib/qflash/qflash-db'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

/**
 * GET /api/qflash/leaderboard — Top players by profit
 *
 * Query params:
 *   limit: max entries (default 50, max 100)
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { searchParams } = new URL(request.url)
    const limit = Math.min(Number(searchParams.get('limit') ?? 50), 100)

    const db = getQFlashDB()
    const leaderboard = db.getLeaderboard(limit)

    return NextResponse.json({ leaderboard, count: leaderboard.length })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch leaderboard')
  }
}
