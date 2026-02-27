import { NextRequest, NextResponse } from 'next/server'
import { getQFlashDB } from '@/lib/qflash/qflash-db'
import { startQFlashCron } from '@/lib/qflash/round-cron'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'
import type { RoundDuration } from '@/lib/qflash/types'

// Auto-start cron on first API import
startQFlashCron()

/**
 * GET /api/qflash/rounds — List active/upcoming rounds
 *
 * Query params:
 *   pair: filter by pair (e.g., 'btc/usdt')
 *   duration: filter by duration (30, 60, 120)
 *   status: filter by status (default: active rounds)
 *   limit: max resolved rounds to return (default 20)
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { searchParams } = new URL(request.url)
    const pair = searchParams.get('pair')
    const duration = searchParams.get('duration')
    const status = searchParams.get('status')
    const limit = Number(searchParams.get('limit') ?? 20)

    const db = getQFlashDB()

    if (status === 'resolved') {
      const rounds = db.getRecentResolved(Math.min(limit, 100))
      return NextResponse.json({ rounds, count: rounds.length })
    }

    const durationNum = duration ? Number(duration) as RoundDuration : undefined
    const rounds = db.getActiveRounds(pair ?? undefined, durationNum)

    return NextResponse.json({ rounds, count: rounds.length })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch rounds')
  }
}
