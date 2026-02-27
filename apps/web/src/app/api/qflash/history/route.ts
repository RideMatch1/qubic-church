import { NextRequest, NextResponse } from 'next/server'
import { getQFlashDB } from '@/lib/qflash/qflash-db'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse, validateQubicAddress } from '@/lib/predict/api-utils'

/**
 * GET /api/qflash/history — User round history
 *
 * Query params:
 *   address: Qubic address (required)
 *   limit: max entries (default 50)
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { searchParams } = new URL(request.url)
    const address = searchParams.get('address')
    const limit = Math.min(Number(searchParams.get('limit') ?? 50), 200)

    if (!address) {
      return NextResponse.json({ error: 'Missing required param: address' }, { status: 400 })
    }
    const addrError = validateQubicAddress(address)
    if (addrError) {
      return NextResponse.json({ error: addrError }, { status: 400 })
    }

    const db = getQFlashDB()
    const entries = db.getUserEntries(address, limit)

    return NextResponse.json({ entries, count: entries.length })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch history')
  }
}
