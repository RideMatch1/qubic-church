import { NextRequest, NextResponse } from 'next/server'
import { getMarketDB } from '@/lib/predict/market-db'
import {
  computeAttestationHash,
  hmacSha256,
} from '@/lib/predict/provably-fair'
import { getAttestationKeyForVerification } from '@/lib/predict/oracle-resolution'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AttestationVerification {
  id: string
  oracleSource: string
  pair: string
  price: number
  sourceTimestamp: string
  hashValid: boolean
  signatureValid: boolean
  storedHash: string
  recomputedHash: string
}

interface VerificationResult {
  marketId: string
  marketQuestion: string
  marketStatus: string
  attestationCount: number
  allHashesValid: boolean
  allSignaturesValid: boolean
  medianFromAttestations: number
  marketResolutionPrice: number | null
  medianMatchesResolution: boolean | null
  attestations: AttestationVerification[]
  verifiedAt: string
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
// GET /api/predict/verify/attestations?marketId=mkt_xxx
// ---------------------------------------------------------------------------

export async function GET(request: NextRequest) {
  // Rate limiting
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const { searchParams } = new URL(request.url)
    const marketId = searchParams.get('marketId')?.trim()

    if (!marketId) {
      return NextResponse.json(
        { error: 'Missing required query parameter: marketId' },
        { status: 400 },
      )
    }

    const db = getMarketDB()

    // Fetch the market
    const market = db.getMarket(marketId)
    if (!market) {
      return NextResponse.json(
        { error: 'Market not found' },
        { status: 404 },
      )
    }

    // Fetch attestations for this market
    const attestationRows = db.getAttestationsByMarket(marketId)

    if (attestationRows.length === 0) {
      return NextResponse.json({
        marketId,
        marketQuestion: market.question,
        marketStatus: market.status,
        attestationCount: 0,
        allHashesValid: true,
        allSignaturesValid: true,
        medianFromAttestations: 0,
        marketResolutionPrice: market.resolutionPrice,
        medianMatchesResolution: null,
        attestations: [],
        verifiedAt: new Date().toISOString(),
      } satisfies VerificationResult)
    }

    const attestationKey = getAttestationKeyForVerification()

    // Verify each attestation
    const verifiedAttestations: AttestationVerification[] = attestationRows.map(
      (att) => {
        // Re-compute the attestation hash from canonical fields
        const recomputedHash = computeAttestationHash(
          att.oracleSource,
          att.pair,
          att.price,
          att.tick,
          att.epoch,
          att.sourceTimestamp,
        )

        const hashValid = recomputedHash === att.attestationHash

        // Re-compute the HMAC signature
        const recomputedSig = hmacSha256(att.attestationHash, attestationKey)
        const signatureValid = recomputedSig === att.serverSignature

        return {
          id: att.id,
          oracleSource: att.oracleSource,
          pair: att.pair,
          price: att.price,
          sourceTimestamp: att.sourceTimestamp,
          hashValid,
          signatureValid,
          storedHash: att.attestationHash,
          recomputedHash,
        }
      },
    )

    const allHashesValid = verifiedAttestations.every((a) => a.hashValid)
    const allSignaturesValid = verifiedAttestations.every(
      (a) => a.signatureValid,
    )

    // Compute median from attestation prices
    const medianFromAttestations = computeMedian(
      attestationRows.map((a) => a.price),
    )

    // Compare with market resolution price (if resolved)
    let medianMatchesResolution: boolean | null = null
    if (market.resolutionPrice !== null) {
      // Allow a small tolerance for floating-point differences
      medianMatchesResolution =
        Math.abs(medianFromAttestations - market.resolutionPrice) < 0.01
    }

    const result: VerificationResult = {
      marketId,
      marketQuestion: market.question,
      marketStatus: market.status,
      attestationCount: verifiedAttestations.length,
      allHashesValid,
      allSignaturesValid,
      medianFromAttestations,
      marketResolutionPrice: market.resolutionPrice,
      medianMatchesResolution,
      attestations: verifiedAttestations,
      verifiedAt: new Date().toISOString(),
    }

    return NextResponse.json(result)
  } catch (error) {
    return safeErrorResponse(error, 'Failed to verify attestations')
  }
}
