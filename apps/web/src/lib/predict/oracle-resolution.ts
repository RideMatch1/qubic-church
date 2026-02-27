/**
 * QPredict Multi-Oracle Price Resolution
 *
 * Fetches prices from 3+ independent sources, computes median,
 * and creates HMAC-signed attestations for each price point.
 *
 * Oracle sources:
 * - Binance (via public API)
 * - MEXC (via public API)
 * - Gate.io (via public API)
 * - CoinGecko (aggregated, as fallback)
 *
 * Security:
 * - Each price is signed with HMAC-SHA256 using ATTESTATION_SECRET_KEY
 * - Attestations are stored in the DB and included in resolution proof packages
 * - Median price (not mean) prevents single-source manipulation
 */

import {
  createOracleAttestation,
  type OracleAttestation,
} from './provably-fair'
import { getMarketDB } from './market-db'

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const MIN_ORACLE_SOURCES = Number(process.env.MIN_ORACLE_SOURCES ?? 2)

function getAttestationKey(): string {
  const key = process.env.ATTESTATION_SECRET_KEY
  if (!key) {
    // Generate a deterministic fallback for development
    // In production, ATTESTATION_SECRET_KEY must be set
    return 'dev-attestation-key-not-for-production'
  }
  return key
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface OraclePrice {
  source: string
  pair: string
  price: number
  timestamp: string
  tick?: number
  epoch?: number
}

export interface MultiOracleResult {
  success: boolean
  medianPrice: number
  prices: OraclePrice[]
  attestations: OracleAttestation[]
  sourceCount: number
  error?: string
}

// ---------------------------------------------------------------------------
// Pair Mapping (our format -> exchange format)
// ---------------------------------------------------------------------------

const PAIR_MAP: Record<string, { binance: string; mexc: string; gateio: string; coingecko: string }> = {
  'btc/usdt': { binance: 'BTCUSDT', mexc: 'BTCUSDT', gateio: 'BTC_USDT', coingecko: 'bitcoin' },
  'eth/usdt': { binance: 'ETHUSDT', mexc: 'ETHUSDT', gateio: 'ETH_USDT', coingecko: 'ethereum' },
  'sol/usdt': { binance: 'SOLUSDT', mexc: 'SOLUSDT', gateio: 'SOL_USDT', coingecko: 'solana' },
  'xrp/usdt': { binance: 'XRPUSDT', mexc: 'XRPUSDT', gateio: 'XRP_USDT', coingecko: 'ripple' },
  'bnb/usdt': { binance: 'BNBUSDT', mexc: 'BNBUSDT', gateio: 'BNB_USDT', coingecko: 'binancecoin' },
  'doge/usdt': { binance: 'DOGEUSDT', mexc: 'DOGEUSDT', gateio: 'DOGE_USDT', coingecko: 'dogecoin' },
  'ada/usdt': { binance: 'ADAUSDT', mexc: 'ADAUSDT', gateio: 'ADA_USDT', coingecko: 'cardano' },
  'avax/usdt': { binance: 'AVAXUSDT', mexc: 'AVAXUSDT', gateio: 'AVAX_USDT', coingecko: 'avalanche-2' },
  'link/usdt': { binance: 'LINKUSDT', mexc: 'LINKUSDT', gateio: 'LINK_USDT', coingecko: 'chainlink' },
  'dot/usdt': { binance: 'DOTUSDT', mexc: 'DOTUSDT', gateio: 'DOT_USDT', coingecko: 'polkadot' },
  'ltc/usdt': { binance: 'LTCUSDT', mexc: 'LTCUSDT', gateio: 'LTC_USDT', coingecko: 'litecoin' },
  'sui/usdt': { binance: 'SUIUSDT', mexc: 'SUIUSDT', gateio: 'SUI_USDT', coingecko: 'sui' },
  'near/usdt': { binance: 'NEARUSDT', mexc: 'NEARUSDT', gateio: 'NEAR_USDT', coingecko: 'near' },
  'trx/usdt': { binance: 'TRXUSDT', mexc: 'TRXUSDT', gateio: 'TRX_USDT', coingecko: 'tron' },
  'atom/usdt': { binance: 'ATOMUSDT', mexc: 'ATOMUSDT', gateio: 'ATOM_USDT', coingecko: 'cosmos' },
  'apt/usdt': { binance: 'APTUSDT', mexc: 'APTUSDT', gateio: 'APT_USDT', coingecko: 'aptos' },
  'qubic/usdt': { binance: '', mexc: 'QUBICUSDT', gateio: 'QUBIC_USDT', coingecko: 'qubic-network' },
  'eth/btc': { binance: 'ETHBTC', mexc: 'ETHBTC', gateio: 'ETH_BTC', coingecko: '' },
}

// ---------------------------------------------------------------------------
// Price Fetchers
// ---------------------------------------------------------------------------

async function fetchWithTimeout(url: string, timeoutMs: number = 5000): Promise<Response> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const res = await fetch(url, { signal: controller.signal })
    return res
  } finally {
    clearTimeout(timeout)
  }
}

async function fetchBinancePrice(pair: string): Promise<OraclePrice | null> {
  const symbol = PAIR_MAP[pair]?.binance
  if (!symbol) return null

  try {
    const res = await fetchWithTimeout(
      `https://api.binance.com/api/v3/ticker/price?symbol=${symbol}`,
    )
    if (!res.ok) return null
    const data = await res.json() as { price: string }
    return {
      source: 'binance',
      pair,
      price: parseFloat(data.price),
      timestamp: new Date().toISOString(),
    }
  } catch {
    return null
  }
}

async function fetchMexcPrice(pair: string): Promise<OraclePrice | null> {
  const symbol = PAIR_MAP[pair]?.mexc
  if (!symbol) return null

  try {
    const res = await fetchWithTimeout(
      `https://api.mexc.com/api/v3/ticker/price?symbol=${symbol}`,
    )
    if (!res.ok) return null
    const data = await res.json() as { price: string }
    return {
      source: 'mexc',
      pair,
      price: parseFloat(data.price),
      timestamp: new Date().toISOString(),
    }
  } catch {
    return null
  }
}

async function fetchGateioPrice(pair: string): Promise<OraclePrice | null> {
  const symbol = PAIR_MAP[pair]?.gateio
  if (!symbol) return null

  try {
    const res = await fetchWithTimeout(
      `https://api.gateio.ws/api/v4/spot/tickers?currency_pair=${symbol}`,
    )
    if (!res.ok) return null
    const data = await res.json() as Array<{ last: string }>
    if (!data[0]) return null
    return {
      source: 'gateio',
      pair,
      price: parseFloat(data[0].last),
      timestamp: new Date().toISOString(),
    }
  } catch {
    return null
  }
}

async function fetchCoingeckoPrice(pair: string): Promise<OraclePrice | null> {
  const coinId = PAIR_MAP[pair]?.coingecko
  if (!coinId) return null

  // CoinGecko only supports vs USD(T)-type quotes
  const isUsdtPair = pair.endsWith('/usdt')
  if (!isUsdtPair) return null

  try {
    const res = await fetchWithTimeout(
      `https://api.coingecko.com/api/v3/simple/price?ids=${coinId}&vs_currencies=usd`,
    )
    if (!res.ok) return null
    const data = await res.json() as Record<string, { usd: number }>
    const price = data[coinId]?.usd
    if (!price) return null
    return {
      source: 'coingecko',
      pair,
      price,
      timestamp: new Date().toISOString(),
    }
  } catch {
    return null
  }
}

// ---------------------------------------------------------------------------
// Multi-Oracle Resolution
// ---------------------------------------------------------------------------

/**
 * Fetch prices from all available oracle sources for a given pair.
 * Returns all successful price fetches.
 */
export async function fetchMultiOraclePrices(pair: string): Promise<OraclePrice[]> {
  const fetchers = [
    fetchBinancePrice(pair),
    fetchMexcPrice(pair),
    fetchGateioPrice(pair),
    fetchCoingeckoPrice(pair),
  ]

  const results = await Promise.allSettled(fetchers)
  const prices: OraclePrice[] = []

  for (const result of results) {
    if (result.status === 'fulfilled' && result.value) {
      prices.push(result.value)
    }
  }

  return prices
}

/**
 * Compute the median of an array of numbers.
 */
function computeMedian(values: number[]): number {
  if (values.length === 0) return 0
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0
    ? (sorted[mid - 1]! + sorted[mid]!) / 2
    : sorted[mid]!
}

/**
 * Resolve a market's price using multiple oracle sources.
 *
 * 1. Fetches prices from all available sources
 * 2. Requires at least MIN_ORACLE_SOURCES prices
 * 3. Computes median price
 * 4. Creates HMAC-signed attestations for each price
 * 5. Stores attestations in the DB
 *
 * @returns MultiOracleResult with median price and attestations
 */
export async function resolvePrice(
  marketId: string,
  pair: string,
  tick?: number,
  epoch?: number,
): Promise<MultiOracleResult> {
  // Fetch from all sources
  const prices = await fetchMultiOraclePrices(pair)

  if (prices.length < MIN_ORACLE_SOURCES) {
    return {
      success: false,
      medianPrice: 0,
      prices,
      attestations: [],
      sourceCount: prices.length,
      error: `Insufficient oracle sources: got ${prices.length}, need ${MIN_ORACLE_SOURCES}`,
    }
  }

  // Compute median
  const medianPrice = computeMedian(prices.map((p) => p.price))

  // Create signed attestations
  const attestationKey = getAttestationKey()
  const attestations: OracleAttestation[] = prices.map((p) =>
    createOracleAttestation(
      marketId,
      p.source,
      p.pair,
      p.price,
      tick ?? null,
      epoch ?? null,
      p.timestamp,
      attestationKey,
    ),
  )

  // Store attestations in DB
  const db = getMarketDB()
  for (const att of attestations) {
    db.insertAttestation(att)
  }

  return {
    success: true,
    medianPrice,
    prices,
    attestations,
    sourceCount: prices.length,
  }
}

/**
 * Get the attestation key for verification (used by the verify API).
 */
export function getAttestationKeyForVerification(): string {
  return getAttestationKey()
}
