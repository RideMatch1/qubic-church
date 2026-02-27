import { NextRequest, NextResponse } from 'next/server'
import { getQFlashDB } from '@/lib/qflash/qflash-db'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

/**
 * GET /api/qflash/stats — Platform statistics
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const db = getQFlashDB()
    const stats = db.getStats()

    return NextResponse.json(stats)
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch stats')
  }
}
