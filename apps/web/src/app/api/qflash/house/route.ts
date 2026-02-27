import { NextRequest, NextResponse } from 'next/server'
import { getHouseStats } from '@/lib/qflash/house-bank'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

/**
 * GET /api/qflash/house — House bank stats (P&L, exposure, balance)
 *
 * Public endpoint — shows house transparency stats.
 * Admin-only fields could be gated via QFLASH_ADMIN_TOKEN in the future.
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const stats = getHouseStats()

    return NextResponse.json(stats)
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch house stats')
  }
}
