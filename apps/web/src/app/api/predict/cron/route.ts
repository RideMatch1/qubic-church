import { NextRequest, NextResponse } from 'next/server'
import { runCronCycle, ensureAutoCron, stopAutoCron } from '@/lib/predict/auto-cron'
import { cronLog } from '@/lib/predict/logger'
import { registerShutdownHandlers } from '@/lib/predict/shutdown'
import { getMarketDB } from '@/lib/predict/market-db'

// Start background cron on first import (any predict API call will trigger this)
ensureAutoCron()

// Register graceful shutdown handlers (idempotent — only registers once)
registerShutdownHandlers(stopAutoCron, () => {
  try { getMarketDB().close() } catch { /* ignore */ }
})

// Rate limit: max 1 manual trigger per 10 seconds
let lastManualTrigger = 0
const CRON_RATE_LIMIT_MS = 10_000

/**
 * GET /api/predict/cron — Manual cron trigger + starts background auto-cron
 *
 * Auth: Always requires CRON_SECRET via Authorization header.
 * If CRON_SECRET is not configured, the endpoint returns 503.
 * Query param auth is intentionally NOT supported (secrets in URLs leak to logs).
 */
export async function GET(request: NextRequest) {
  // Mandatory auth: CRON_SECRET must be configured
  const cronSecret = process.env.CRON_SECRET
  if (!cronSecret) {
    return NextResponse.json(
      { error: 'Cron not configured: CRON_SECRET environment variable is required' },
      { status: 503 },
    )
  }

  // Accept auth ONLY via Authorization: Bearer header (never query params)
  const authHeader = request.headers.get('authorization')
  const headerSecret = authHeader?.replace('Bearer ', '')

  if (headerSecret !== cronSecret) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Rate limit: max 1 manual trigger per 10 seconds
  const now = Date.now()
  if (now - lastManualTrigger < CRON_RATE_LIMIT_MS) {
    return NextResponse.json(
      { error: 'Rate limited: max 1 cron trigger per 10 seconds' },
      { status: 429, headers: { 'Retry-After': '10' } },
    )
  }
  lastManualTrigger = now

  const results = await runCronCycle()

  cronLog.info(results, 'manual cron cycle complete')

  return NextResponse.json({
    ok: true,
    timestamp: new Date().toISOString(),
    ...results,
  })
}
