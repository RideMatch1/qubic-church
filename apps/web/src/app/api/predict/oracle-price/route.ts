import { NextRequest, NextResponse } from 'next/server'
import { fetchMultiOraclePrices } from '@/lib/predict/oracle-resolution'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

// ---------------------------------------------------------------------------
// Supported Pairs (mirrors PAIR_MAP keys from oracle-resolution.ts)
// ---------------------------------------------------------------------------

const SUPPORTED_PAIRS = new Set([
  'btc/usdt', 'eth/usdt', 'sol/usdt', 'xrp/usdt', 'bnb/usdt',
  'doge/usdt', 'ada/usdt', 'avax/usdt', 'link/usdt', 'dot/usdt',
  'ltc/usdt', 'sui/usdt', 'near/usdt', 'trx/usdt', 'atom/usdt',
  'apt/usdt', 'qubic/usdt', 'eth/btc',
])

// ---------------------------------------------------------------------------
// In-Memory Price Cache (15-second TTL)
// ---------------------------------------------------------------------------

interface CacheEntry {
  data: OraclePriceResponse
  expiresAt: number
}

interface OraclePriceResponse {
  pair: string
  median: number
  sources: Array<{ name: string; price: number }>
  fetchedAt: string
  sourceCount: number
}

const priceCache = new Map<string, CacheEntry>()

const CACHE_TTL_MS = 15_000

function getCached(pair: string): OraclePriceResponse | null {
  const entry = priceCache.get(pair)
  if (!entry) return null
  if (Date.now() > entry.expiresAt) {
    priceCache.delete(pair)
    return null
  }
  return entry.data
}

function setCache(pair: string, data: OraclePriceResponse): void {
  priceCache.set(pair, { data, expiresAt: Date.now() + CACHE_TTL_MS })
}

// ---------------------------------------------------------------------------
// Median Helper
// ---------------------------------------------------------------------------

function computeMedian(values: number[]): number {
  if (values.length === 0) return 0
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0
    ? (sorted[mid - 1]! + sorted[mid]!) / 2
    : sorted[mid]!
}

// ---------------------------------------------------------------------------
// GET /api/predict/oracle-price?pair=btc/usdt
// ---------------------------------------------------------------------------

export async function GET(request: NextRequest) {
  // Rate limiting
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { searchParams } = new URL(request.url)
    const pair = searchParams.get('pair')?.toLowerCase().trim()

    if (!pair) {
      return NextResponse.json(
        { error: 'Missing required query parameter: pair' },
        { status: 400 },
      )
    }

    if (!SUPPORTED_PAIRS.has(pair)) {
      return NextResponse.json(
        {
          error: `Unsupported pair: ${pair}. Supported: ${[...SUPPORTED_PAIRS].join(', ')}`,
        },
        { status: 400 },
      )
    }

    // Check cache first
    const cached = getCached(pair)
    if (cached) {
      return NextResponse.json(cached, {
        headers: { 'X-Cache': 'HIT' },
      })
    }

    // Fetch prices from all oracle sources
    const prices = await fetchMultiOraclePrices(pair)

    if (prices.length === 0) {
      return NextResponse.json(
        { error: 'No oracle sources returned a price for this pair' },
        { status: 502 },
      )
    }

    const median = computeMedian(prices.map((p) => p.price))
    const fetchedAt = new Date().toISOString()

    const response: OraclePriceResponse = {
      pair,
      median,
      sources: prices.map((p) => ({ name: p.source, price: p.price })),
      fetchedAt,
      sourceCount: prices.length,
    }

    // Cache the result
    setCache(pair, response)

    return NextResponse.json(response, {
      headers: { 'X-Cache': 'MISS' },
    })
  } catch (error) {
    return safeErrorResponse(error, 'Failed to fetch oracle price')
  }
}
