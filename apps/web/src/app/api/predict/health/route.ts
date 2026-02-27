/**
 * GET /api/predict/health
 *
 * Public health check endpoint for monitoring tools.
 * Returns system health status without requiring authentication.
 * No sensitive data is exposed.
 */

import { NextResponse } from 'next/server'
import { getMarketDB } from '@/lib/predict/market-db'
import { rpcBreaker, type CircuitBreakerSnapshot } from '@/lib/predict/circuit-breaker'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { parseUtcTimestamp } from '@/lib/predict/api-utils'
import type { NextRequest } from 'next/server'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface HealthCheck {
  database: { ok: boolean; error?: string }
  rpcCircuit: CircuitBreakerSnapshot
  cronFreshness: { ok: boolean; lastRunSecondsAgo: number | null }
  escrows: { activeCount: number }
  keyVault: { configured: boolean }
}

interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  timestamp: string
  checks: HealthCheck
  uptime: number
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Cron is considered stale if it hasn't run in this many seconds. */
const CRON_STALE_THRESHOLD_S = 300 // 5 minutes

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

export async function GET(request: NextRequest): Promise<NextResponse<HealthResponse>> {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl as NextResponse<HealthResponse>

  const checks: HealthCheck = {
    database: { ok: false },
    rpcCircuit: { state: 'closed', failureCount: 0, lastFailureTime: null },
    cronFreshness: { ok: false, lastRunSecondsAgo: null },
    escrows: { activeCount: 0 },
    keyVault: { configured: false },
  }

  // 1. Database connectivity
  let db: ReturnType<typeof getMarketDB> | null = null
  try {
    db = getMarketDB()
    db.getPlatformStats()
    checks.database = { ok: true }
  } catch (err) {
    checks.database = { ok: false, error: err instanceof Error ? err.message : 'DB unreachable' }
  }

  // 2. Circuit breaker state
  checks.rpcCircuit = rpcBreaker.getState()

  // 3. Cron freshness
  try {
    if (db) {
      const lastRun = db.getSystemStatus('last_cron_run')
      if (lastRun) {
        const lastRunDate = parseUtcTimestamp(lastRun)
        const secondsAgo = Math.round((Date.now() - lastRunDate.getTime()) / 1000)
        checks.cronFreshness = {
          ok: secondsAgo < CRON_STALE_THRESHOLD_S,
          lastRunSecondsAgo: secondsAgo,
        }
      }
    }
  } catch {
    checks.cronFreshness = { ok: false, lastRunSecondsAgo: null }
  }

  // 4. Active escrow count
  try {
    if (db) {
      const row = db.countActiveEscrows()
      checks.escrows = { activeCount: row }
    }
  } catch {
    // leave default
  }

  // 5. Key vault configuration
  checks.keyVault = { configured: !!process.env.ESCROW_MASTER_KEY }

  // Determine overall status
  let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy'

  if (!checks.database.ok || (checks.cronFreshness.lastRunSecondsAgo !== null && !checks.cronFreshness.ok)) {
    status = 'unhealthy'
  } else if (checks.rpcCircuit.state !== 'closed') {
    status = 'degraded'
  }

  return NextResponse.json({
    status,
    timestamp: new Date().toISOString(),
    checks,
    uptime: Math.round(process.uptime()),
  })
}
