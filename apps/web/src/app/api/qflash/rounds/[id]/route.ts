import { NextRequest, NextResponse } from 'next/server'
import { getQFlashDB } from '@/lib/qflash/qflash-db'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

/**
 * GET /api/qflash/rounds/[id] — Get round detail with pool sizes
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { id } = await params
    const db = getQFlashDB()
    const round = db.getRound(id)

    if (!round) {
      return NextResponse.json({ error: 'Round not found' }, { status: 404 })
    }

    // Include pool breakdown and implied odds
    const totalPool = round.upPoolQu + round.downPoolQu
    const upPct = totalPool > 0 ? round.upPoolQu / totalPool : 0.5
    const downPct = totalPool > 0 ? round.downPoolQu / totalPool : 0.5

    // Calculate potential payout multipliers
    const upMultiplier = round.downPoolQu > 0 && round.upPoolQu > 0
      ? 1 + (round.downPoolQu * 0.97) / round.upPoolQu // 3% fee deducted
      : 0
    const downMultiplier = round.upPoolQu > 0 && round.downPoolQu > 0
      ? 1 + (round.upPoolQu * 0.97) / round.downPoolQu
      : 0

    // Get price snapshots
    const snapshots = db.getSnapshotsByRound(id)

    return NextResponse.json({
      ...round,
      totalPool,
      upPercentage: Math.round(upPct * 100),
      downPercentage: Math.round(downPct * 100),
      upMultiplier: Math.round(upMultiplier * 100) / 100,
      downMultiplier: Math.round(downMultiplier * 100) / 100,
      snapshots,
    })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch round')
  }
}
