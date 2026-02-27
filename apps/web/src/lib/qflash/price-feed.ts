/**
 * QFlash Price Feed
 *
 * Wraps the existing multi-oracle price system with a 5-second
 * in-memory cache optimized for QFlash's faster polling cycle.
 *
 * Reuses fetchMultiOraclePrices() and computeMedian logic from
 * the QPredict oracle-resolution module.
 */

import { fetchMultiOraclePrices } from '../predict/oracle-resolution'
import { hashCanonicalJSON } from '../predict/provably-fair'
import { QFLASH_CONFIG, getQFlashAttestationKey } from './config'

import crypto from 'crypto'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface PriceFeedResult {
  pair: string
  medianPrice: number
  sources: { name: string; price: number }[]
  fetchedAt: string
  sourceCount: number
  attestationHash: string
}

// ---------------------------------------------------------------------------
// In-Memory Cache (5-second TTL)
// ---------------------------------------------------------------------------

interface CacheEntry {
  result: PriceFeedResult
  cachedAt: number
}

const priceCache = new Map<string, CacheEntry>()

// ---------------------------------------------------------------------------
// Core Functions
// ---------------------------------------------------------------------------

function computeMedian(values: number[]): number {
  if (values.length === 0) return 0
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0
    ? (sorted[mid - 1]! + sorted[mid]!) / 2
    : sorted[mid]!
}

/**
 * Create HMAC-SHA256 attestation hash for a price snapshot.
 */
function createAttestationHash(
  pair: string,
  medianPrice: number,
  sources: { name: string; price: number }[],
  timestamp: string,
): string {
  const payload = { pair, medianPrice, sources, timestamp }
  const canonical = hashCanonicalJSON(payload)
  const key = getQFlashAttestationKey()
  return crypto.createHmac('sha256', key).update(canonical).digest('hex')
}

/**
 * Fetch live price for a pair using multiple oracle sources.
 *
 * Uses a 5-second in-memory cache to avoid hammering APIs during
 * QFlash's fast polling cycle. Returns the cached result if fresh enough.
 *
 * @param pair - Trading pair (e.g., 'btc/usdt')
 * @param forceFresh - Skip cache and fetch fresh prices
 */
export async function getPrice(
  pair: string,
  forceFresh: boolean = false,
): Promise<PriceFeedResult | null> {
  // Check cache
  if (!forceFresh) {
    const cached = priceCache.get(pair)
    if (cached && Date.now() - cached.cachedAt < QFLASH_CONFIG.priceCacheTtlMs) {
      return cached.result
    }
  }

  // Fetch from all oracle sources
  const oraclePrices = await fetchMultiOraclePrices(pair)

  if (oraclePrices.length < QFLASH_CONFIG.minOracleSources) {
    return null
  }

  const prices = oraclePrices.map((p) => p.price)
  const medianPrice = computeMedian(prices)
  const fetchedAt = new Date().toISOString()

  const sources = oraclePrices.map((p) => ({
    name: p.source,
    price: p.price,
  }))

  const attestationHash = createAttestationHash(pair, medianPrice, sources, fetchedAt)

  const result: PriceFeedResult = {
    pair,
    medianPrice,
    sources,
    fetchedAt,
    sourceCount: sources.length,
    attestationHash,
  }

  // Update cache
  priceCache.set(pair, { result, cachedAt: Date.now() })

  return result
}

/**
 * Get prices for all enabled pairs.
 * Fetches in parallel, returns successful results only.
 */
export async function getAllPrices(pairs: string[]): Promise<Map<string, PriceFeedResult>> {
  const results = new Map<string, PriceFeedResult>()
  const fetches = pairs.map(async (pair) => {
    const price = await getPrice(pair)
    if (price) results.set(pair, price)
  })
  await Promise.allSettled(fetches)
  return results
}

/**
 * Invalidate the cache for a specific pair.
 * Useful after resolution to force fresh fetch for next round.
 */
export function invalidateCache(pair: string): void {
  priceCache.delete(pair)
}

/**
 * Clear all cached prices.
 */
export function clearPriceCache(): void {
  priceCache.clear()
}
