/**
 * GET /api/predict/admin/status
 *
 * Protected admin endpoint returning comprehensive system status.
 * Requires CRON_SECRET via Authorization Bearer header.
 */

import fs from 'fs'
import path from 'path'
import { NextRequest, NextResponse } from 'next/server'
import { getMarketDB } from '@/lib/predict/market-db'
import { rpcBreaker } from '@/lib/predict/circuit-breaker'
import { parseUtcTimestamp } from '@/lib/predict/api-utils'

// ---------------------------------------------------------------------------
// Auth (same pattern as cron/route.ts)
// ---------------------------------------------------------------------------

const CRON_SECRET = process.env.CRON_SECRET

function verifyAuth(request: NextRequest): NextResponse | null {
  if (!CRON_SECRET) {
    return NextResponse.json({ error: 'CRON_SECRET not configured' }, { status: 503 })
  }

  const authHeader = request.headers.get('authorization')
  if (!authHeader || authHeader !== `Bearer ${CRON_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  return null
}

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

export async function GET(request: NextRequest): Promise<NextResponse> {
  const authError = verifyAuth(request)
  if (authError) return authError

  try {
    const db = getMarketDB()

    // Platform stats
    const stats = db.getPlatformStats()

    // Circuit breaker
    const circuitBreaker = rpcBreaker.getState()

    // Escrow status breakdown
    const escrowCounts = db.getEscrowStatusCounts()

    // Market status breakdown
    const marketCounts = db.getMarketStatusCounts()

    // Markets closing/resolving soon
    const closingSoon = db.getMarketsClosingSoon(60)
    const resolvingSoon = db.getMarketsResolvingSoon(60)

    // Cron status
    const lastCronRun = db.getSystemStatus('last_cron_run')
    const lastCronErrors = db.getSystemStatus('last_cron_errors')
    let cronLastRunSecondsAgo: number | null = null
    if (lastCronRun) {
      cronLastRunSecondsAgo = Math.round(
        (Date.now() - parseUtcTimestamp(lastCronRun).getTime()) / 1000,
      )
    }

    // DB size
    let dbSizeBytes = 0
    const dbPath = path.join(process.cwd(), 'predict.sqlite3')
    try {
      const stat = fs.statSync(dbPath)
      dbSizeBytes = stat.size
    } catch {
      // DB file may not exist yet
    }

    return NextResponse.json({
      timestamp: new Date().toISOString(),
      platform: stats,
      circuitBreaker,
      escrows: escrowCounts,
      markets: {
        byStatus: marketCounts,
        closingSoon,
        resolvingSoon,
      },
      cron: {
        lastRunSecondsAgo: cronLastRunSecondsAgo,
        lastErrors: lastCronErrors ? JSON.parse(lastCronErrors) : [],
      },
      infrastructure: {
        dbSizeBytes,
        keyVaultConfigured: !!process.env.ESCROW_MASTER_KEY,
        uptime: Math.round(process.uptime()),
      },
    })
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : 'Internal error' },
      { status: 500 },
    )
  }
}
