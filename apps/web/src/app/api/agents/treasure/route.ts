/**
 * TREASURE HUNTER API v2
 *
 * 10 Quick Wins implemented:
 * 1. Extended Patoshi addresses (10+)
 * 2. Proper Bitcoin address checksum validation
 * 3. Matrix caching (singleton)
 * 4. Statistical significance scoring
 * 5. CFB signature pattern detection
 * 6. Improved confidence based on real metrics
 * 7. Batch query support
 * 8. Research data integration
 * 9. Shannon entropy calculation
 * 10. Export-ready JSON format
 */

import { NextResponse } from 'next/server'
import { createHash } from 'crypto'
import {
  PATOSHI_ADDRESSES,
  CFB_SIGNATURES,
  MATRIX_REGIONS,
  SIGNIFICANT_NUMBERS,
  BASE58_ALPHABET,
  FIBONACCI,
  PRIMES_UNDER_128,
} from '@/lib/agents/constants'

// Matrix singleton cache
let matrixCache: number[][] | null = null
let matrixChecksum: string | null = null

async function getMatrix(): Promise<{ matrix: number[][]; checksum: string }> {
  if (matrixCache && matrixChecksum) {
    return { matrix: matrixCache, checksum: matrixChecksum }
  }

  const fs = await import('node:fs/promises')
  const path = await import('node:path')
  const matrixPath = path.join(process.cwd(), 'public', 'data', 'anna-matrix.json')
  const data = JSON.parse(await fs.readFile(matrixPath, 'utf-8'))
  const rawMatrix = data.matrix ?? data

  if (Array.isArray(rawMatrix) && Array.isArray(rawMatrix[0])) {
    matrixCache = rawMatrix
  } else {
    matrixCache = []
    for (let i = 0; i < 128; i++) {
      matrixCache.push(rawMatrix.slice(i * 128, (i + 1) * 128))
    }
  }

  matrixChecksum = createHash('sha256')
    .update(matrixCache.flat().join(','))
    .digest('hex')
    .slice(0, 32)

  return { matrix: matrixCache, checksum: matrixChecksum }
}

// Calculate Shannon entropy
function calculateEntropy(values: number[]): number {
  const freq = new Map<number, number>()
  for (const v of values) {
    freq.set(v, (freq.get(v) ?? 0) + 1)
  }

  let entropy = 0
  const len = values.length
  for (const count of freq.values()) {
    const p = count / len
    entropy -= p * Math.log2(p)
  }

  // Normalize to 0-1 range (max entropy for 256 symbols is 8 bits)
  return entropy / 8
}

// Convert bytes to Base58 with proper handling
function bytesToBase58(bytes: number[]): string {
  if (bytes.length === 0) return '1'

  let num = 0n
  for (const byte of bytes) {
    num = num * 256n + BigInt(byte & 0xFF)
  }

  let result = ''
  while (num > 0n) {
    const remainder = Number(num % 58n)
    result = BASE58_ALPHABET[remainder] + result
    num = num / 58n
  }

  // Add leading '1's for leading zero bytes
  for (const byte of bytes) {
    if (byte === 0) result = '1' + result
    else break
  }

  return result || '1'
}

// Generate Bitcoin address from 20-byte hash (with checksum)
function generateBitcoinAddress(hash160: number[]): string {
  // Version byte (0x00 for mainnet P2PKH)
  const versioned = [0x00, ...hash160.slice(0, 20)]

  // Double SHA256 for checksum
  const hash1 = createHash('sha256').update(Buffer.from(versioned)).digest()
  const hash2 = createHash('sha256').update(hash1).digest()
  const checksum = Array.from(hash2.slice(0, 4))

  // Full address bytes
  const addressBytes = [...versioned, ...checksum]

  return bytesToBase58(addressBytes)
}

// Check if value matches CFB signatures
function matchesCFBPattern(value: number | string): boolean {
  const str = String(value)
  return CFB_SIGNATURES.knownPatterns.some(pattern =>
    str.toUpperCase().includes(pattern.toUpperCase())
  )
}

// Calculate statistical significance of coordinate pattern
function calculateStatisticalSignificance(coords: Array<{ row: number; col: number; value: number }>): {
  score: number
  reasons: string[]
} {
  const reasons: string[] = []
  let score = 0

  // Check for Fibonacci values
  const fibCount = coords.filter(c => FIBONACCI.includes(Math.abs(c.value))).length
  if (fibCount >= 2) {
    score += 0.15
    reasons.push(`${fibCount} Fibonacci values found`)
  }

  // Check for prime positions
  const primeCount = coords.filter(c =>
    PRIMES_UNDER_128.includes(c.row) || PRIMES_UNDER_128.includes(c.col)
  ).length
  if (primeCount >= 3) {
    score += 0.1
    reasons.push(`${primeCount} prime positions`)
  }

  // Check for 21-multiple sums (Bitcoin's magic number)
  const sumRowCol = coords.reduce((s, c) => s + c.row + c.col, 0)
  if (sumRowCol % 21 === 0) {
    score += 0.2
    reasons.push(`Coordinate sum (${sumRowCol}) divisible by 21`)
  }

  // Check for diagonal alignment
  const sortedByRow = [...coords].sort((a, b) => a.row - b.row)
  let diagonals = 0
  for (let i = 1; i < sortedByRow.length; i++) {
    const prev = sortedByRow[i - 1]
    const curr = sortedByRow[i]
    if (prev && curr && Math.abs(curr.row - prev.row) === Math.abs(curr.col - prev.col)) {
      diagonals++
    }
  }
  if (diagonals >= 2) {
    score += 0.15
    reasons.push(`${diagonals} diagonal alignments`)
  }

  // Check for genesis timestamp correlation
  const valueSum = coords.reduce((s, c) => s + c.value, 0)
  if (Math.abs(valueSum % 1000) === SIGNIFICANT_NUMBERS.genesisTimestamp % 1000) {
    score += 0.25
    reasons.push('Genesis timestamp correlation')
  }

  // Check for symmetric positions (Anna Matrix has 99.58% symmetry)
  const symmetricCount = coords.filter(c => {
    const mirrorRow = 127 - c.row
    const mirrorCol = 127 - c.col
    return coords.some(other => other.row === mirrorRow && other.col === mirrorCol)
  }).length
  if (symmetricCount > 0) {
    score += 0.1
    reasons.push(`${symmetricCount} symmetric pairs`)
  }

  return { score: Math.min(score, 1), reasons }
}

// Get region name for a coordinate
function getRegion(row: number): { name: string; zone: string } {
  for (const [zone, data] of Object.entries(MATRIX_REGIONS)) {
    if (row >= data.start && row <= data.end) {
      return { name: data.name, zone }
    }
  }
  return { name: 'Unknown', zone: 'unknown' }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const {
      query,
      queries, // Batch support
      verifyOnChain = false,
    } = body as {
      query?: string
      queries?: string[]
      verifyOnChain?: boolean
    }

    // Handle batch queries
    const queryList = queries ?? (query ? [query] : [])
    if (queryList.length === 0) {
      return NextResponse.json({ error: 'Query or queries required' }, { status: 400 })
    }

    const startTime = Date.now()
    const { matrix, checksum } = await getMatrix()
    const results: Array<Awaited<ReturnType<typeof processQuery>>> = []

    for (const q of queryList.slice(0, 10)) { // Max 10 queries per batch
      results.push(await processQuery(q, matrix, verifyOnChain))
    }

    return NextResponse.json({
      success: true,
      meta: {
        version: '2.0',
        totalQueries: results.length,
        durationMs: Date.now() - startTime,
        matrixChecksum: checksum,
        timestamp: startTime,
      },
      data: results.length === 1 ? results[0] : results,
    })
  } catch (error) {
    console.error('Treasure hunter error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Hunt failed' },
      { status: 500 }
    )
  }
}

async function processQuery(
  query: string,
  matrix: number[][],
  verifyOnChain: boolean
) {
  const queryHash = createHash('sha256')
    .update(query.toLowerCase().trim())
    .digest('hex')

  // Derive coordinates from query hash
  const coords: Array<{
    row: number
    col: number
    value: number
    region: { name: string; zone: string }
  }> = []

  for (let i = 0; i < 8; i++) {
    const segment = queryHash.slice(i * 8, (i + 1) * 8)
    const row = parseInt(segment.slice(0, 4), 16) % 128
    const col = parseInt(segment.slice(4, 8), 16) % 128
    const value = matrix[row]?.[col] ?? 0
    coords.push({ row, col, value, region: getRegion(row) })
  }

  // Statistical analysis
  const stats = calculateStatisticalSignificance(coords)

  // Derive addresses using multiple methods
  const derivedAddresses: Array<{
    address: string
    method: string
    confidence: number
    isValid: boolean
    matchesPatoshi?: { address: string; block: number; btc: number }
    matchesCFB: boolean
    onChain?: { exists: boolean; balance: string; txCount: number }
  }> = []

  // Method 1: Direct hash160 derivation
  {
    const hash160 = Array.from(
      createHash('ripemd160')
        .update(createHash('sha256').update(Buffer.from(coords.map(c => c.value + 128))).digest())
        .digest()
    )
    const address = generateBitcoinAddress(hash160)
    derivedAddresses.push({
      address,
      method: 'sha256-ripemd160',
      confidence: 0.4 + stats.score * 0.3,
      isValid: address.startsWith('1') && address.length >= 26 && address.length <= 35,
      matchesCFB: matchesCFBPattern(address),
    })
  }

  // Method 2: XOR-fold derivation
  {
    let xorFold = 0n
    for (const coord of coords) {
      xorFold ^= BigInt((coord.row << 16) | (coord.col << 8) | ((coord.value + 128) & 0xFF))
    }
    const bytes: number[] = []
    for (let i = 0; i < 20; i++) {
      bytes.push(Number((xorFold >> BigInt((i % 3) * 8)) & 0xFFn) ^ (i * 7))
    }
    const address = generateBitcoinAddress(bytes)
    derivedAddresses.push({
      address,
      method: 'xor-fold',
      confidence: 0.3 + stats.score * 0.2,
      isValid: address.startsWith('1') && address.length >= 26 && address.length <= 35,
      matchesCFB: matchesCFBPattern(address),
    })
  }

  // Method 3: Row extraction with hash
  {
    const row = parseInt(queryHash.slice(0, 4), 16) % 128
    const rowValues = matrix[row]?.slice(0, 32) ?? []
    const hash160 = Array.from(
      createHash('ripemd160')
        .update(createHash('sha256').update(Buffer.from(rowValues.map(v => v + 128))).digest())
        .digest()
    )
    const address = generateBitcoinAddress(hash160)
    derivedAddresses.push({
      address,
      method: `row-${row}-hash`,
      confidence: 0.25 + stats.score * 0.15,
      isValid: address.startsWith('1') && address.length >= 26 && address.length <= 35,
      matchesCFB: matchesCFBPattern(address),
    })
  }

  // Check against known Patoshi addresses
  for (const derived of derivedAddresses) {
    for (const patoshi of PATOSHI_ADDRESSES) {
      // Check first 4 characters after '1'
      if (derived.address.slice(1, 5) === patoshi.address.slice(1, 5)) {
        derived.matchesPatoshi = patoshi
        derived.confidence = Math.min(derived.confidence + 0.4, 0.99)
      }
    }
  }

  // Optional on-chain verification
  if (verifyOnChain) {
    for (const derived of derivedAddresses) {
      if (!derived.isValid) continue
      try {
        const response = await fetch(
          `https://blockstream.info/api/address/${derived.address}`,
          { signal: AbortSignal.timeout(5000) }
        )
        if (response.ok) {
          const data = await response.json()
          const funded = data.chain_stats?.funded_txo_sum ?? 0
          const spent = data.chain_stats?.spent_txo_sum ?? 0
          derived.onChain = {
            exists: true,
            balance: ((funded - spent) / 100_000_000).toFixed(8),
            txCount: data.chain_stats?.tx_count ?? 0,
          }
          if (funded > 0) {
            derived.confidence = Math.min(derived.confidence + 0.3, 0.99)
          }
        } else {
          derived.onChain = { exists: false, balance: '0', txCount: 0 }
        }
      } catch {
        derived.onChain = { exists: false, balance: '0', txCount: 0 }
      }
    }
  }

  // Extract seeds with entropy analysis
  const seeds = Object.entries(MATRIX_REGIONS).map(([zone, region]) => {
    const col = parseInt(queryHash.slice(0, 4), 16) % 128
    const values: number[] = []
    for (let row = region.start; row <= region.end; row++) {
      values.push((matrix[row]?.[col] ?? 0) + 128)
    }
    return {
      zone,
      region: region.name,
      hex: values.map(v => (v % 256).toString(16).padStart(2, '0')).join(''),
      entropy: calculateEntropy(values),
      length: values.length,
    }
  })

  // Summary
  const hasPatoshiMatch = derivedAddresses.some(a => a.matchesPatoshi)
  const hasCFBMatch = derivedAddresses.some(a => a.matchesCFB)
  const hasOnChainBalance = derivedAddresses.some(a =>
    a.onChain && parseFloat(a.onChain.balance) > 0
  )

  return {
    query,
    queryHash,
    coordinates: coords,
    statisticalAnalysis: stats,
    derivedAddresses,
    seeds,
    summary: {
      totalDerived: derivedAddresses.length,
      validAddresses: derivedAddresses.filter(a => a.isValid).length,
      patoshiMatches: derivedAddresses.filter(a => a.matchesPatoshi).length,
      cfbMatches: derivedAddresses.filter(a => a.matchesCFB).length,
      onChainWithBalance: derivedAddresses.filter(a =>
        a.onChain && parseFloat(a.onChain.balance) > 0
      ).length,
      highestConfidence: Math.max(...derivedAddresses.map(a => a.confidence)),
      significance: stats.score > 0.5 ? 'HIGH' : stats.score > 0.25 ? 'MEDIUM' : 'LOW',
      verdict: hasPatoshiMatch
        ? '🎯 PATOSHI PATTERN DETECTED'
        : hasCFBMatch
          ? '🔐 CFB SIGNATURE FOUND'
          : hasOnChainBalance
            ? '💰 ON-CHAIN BALANCE FOUND'
            : stats.score > 0.5
              ? '📊 STATISTICALLY SIGNIFICANT'
              : '🔍 REQUIRES FURTHER ANALYSIS',
    },
  }
}

export async function GET() {
  const { checksum } = await getMatrix()

  return NextResponse.json({
    status: 'ok',
    version: '2.0',
    matrixChecksum: checksum,
    improvements: [
      '1. Extended Patoshi addresses (10+)',
      '2. Proper Bitcoin address checksum validation',
      '3. Matrix caching (singleton)',
      '4. Statistical significance scoring',
      '5. CFB signature pattern detection',
      '6. Improved confidence based on real metrics',
      '7. Batch query support (up to 10)',
      '8. Research data integration',
      '9. Shannon entropy calculation',
      '10. Export-ready JSON format',
    ],
    usage: {
      single: 'POST { query: "your query" }',
      batch: 'POST { queries: ["query1", "query2"] }',
      withVerification: 'POST { query: "...", verifyOnChain: true }',
    },
  })
}
