import { NextRequest, NextResponse } from 'next/server'
import { runQFlashCronCycle, isQFlashCronRunning, startQFlashCron } from '@/lib/qflash/round-cron'
import { safeErrorResponse } from '@/lib/predict/api-utils'

/**
 * GET /api/qflash/cron — Manual cron trigger + status
 *
 * Requires CRON_SECRET header for authentication.
 * Returns the results of a single cron cycle.
 */
export async function GET(request: NextRequest) {
  try {
    // Auth check
    const cronSecret = process.env.CRON_SECRET
    if (cronSecret) {
      const authHeader = request.headers.get('authorization')
      if (authHeader !== `Bearer ${cronSecret}`) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
      }
    }

    // Ensure cron is running
    if (!isQFlashCronRunning()) {
      startQFlashCron()
    }

    // Run one manual cycle
    const results = await runQFlashCronCycle()

    return NextResponse.json({
      cronRunning: isQFlashCronRunning(),
      results,
    })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to run cron cycle')
  }
}
