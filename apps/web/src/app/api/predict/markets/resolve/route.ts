import crypto from 'crypto'
import { NextRequest, NextResponse } from 'next/server'
import { getMarketDB } from '@/lib/predict/market-db'
import { resolveMarket } from '@/lib/predict/market-manager'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse, parseUtcTimestamp } from '@/lib/predict/api-utils'

/**
 * Verify a Qubic Schnorr signature against a public address.
 * Falls back to HMAC verification using a shared secret for development.
 *
 * Returns true if signature is valid, throws if SDK unavailable.
 */
async function verifyQubicSignature(
  publicAddress: string,
  messageHash: Buffer,
  signatureHex: string,
): Promise<boolean> {
  try {
    const { createRequire } = await import('module')
    const require = createRequire(import.meta.url)
    const lib = require('@qubic-lib/qubic-ts-library').default
    const helper = new lib.QubicHelper()

    return await helper.verifySignature(
      publicAddress,
      messageHash,
      Buffer.from(signatureHex, 'hex'),
    )
  } catch {
    // SDK not available — fall back to RESOLVE_SECRET shared-secret verification.
    // In production with real on-chain operations, the Qubic SDK MUST be available.
    const resolveSecret = process.env.RESOLVE_SECRET
    if (!resolveSecret) {
      throw new Error(
        'Neither Qubic SDK nor RESOLVE_SECRET is available for signature verification',
      )
    }

    // Verify HMAC: the resolver signs SHA256(marketId+winningOption+nonce) with RESOLVE_SECRET
    const expectedSig = crypto
      .createHmac('sha256', resolveSecret)
      .update(messageHash)
      .digest('hex')

    return signatureHex === expectedSig
  }
}

/**
 * POST /api/predict/markets/resolve — Resolve a custom market
 *
 * Custom markets are resolved by the creator (whose address must be
 * in the market's oracle_addresses list).
 *
 * SECURITY: Requires cryptographic proof that the resolver controls the
 * claimed address. The request must include a signature over the
 * message SHA256(marketId + winningOption + nonce) and a unique nonce.
 *
 * Body: {
 *   marketId: string,
 *   winningOption: number,        // 0-based option index
 *   resolverAddress: string,      // Must be in oracle_addresses
 *   signature: string,            // Hex-encoded Schnorr signature
 *   nonce: string,                // Unique nonce (UUID or similar, prevents replay)
 * }
 */
export async function POST(request: NextRequest) {
  const rl = rateLimitResponse(request, 'POST /markets/resolve')
  if (rl) return rl

  try {
    const body = await request.json() as {
      marketId?: string
      winningOption?: number
      resolverAddress?: string
      signature?: string
      nonce?: string
    }

    // Validate required fields
    if (!body.marketId || body.winningOption === undefined || !body.resolverAddress) {
      return NextResponse.json(
        { error: 'Missing required fields: marketId, winningOption, resolverAddress' },
        { status: 400 },
      )
    }

    if (!body.signature || !body.nonce) {
      return NextResponse.json(
        { error: 'Missing required auth fields: signature, nonce' },
        { status: 400 },
      )
    }

    // Validate nonce format (must be non-empty, reasonable length)
    if (body.nonce.length < 8 || body.nonce.length > 128) {
      return NextResponse.json(
        { error: 'Nonce must be 8-128 characters' },
        { status: 400 },
      )
    }

    const db = getMarketDB()
    const market = db.getMarket(body.marketId)

    if (!market) {
      return NextResponse.json({ error: 'Market not found' }, { status: 404 })
    }

    // Only custom markets can be resolved via this endpoint
    if (market.marketType !== 'custom') {
      return NextResponse.json(
        { error: `Market type "${market.marketType}" cannot be manually resolved. Only "custom" markets use this endpoint.` },
        { status: 400 },
      )
    }

    // Validate resolver is authorized
    const oracleAddresses = market.oracleAddresses ?? []
    if (!oracleAddresses.includes(body.resolverAddress)) {
      return NextResponse.json(
        { error: 'Resolver address is not authorized for this market' },
        { status: 403 },
      )
    }

    // Replay attack prevention: check nonce hasn't been used
    const nonceValid = db.checkAndRecordNonce(body.nonce, body.resolverAddress, 'resolve')
    if (!nonceValid) {
      return NextResponse.json(
        { error: 'Nonce already used (replay attack prevented)' },
        { status: 409 },
      )
    }

    // Verify cryptographic signature
    const messagePayload = `${body.marketId}${body.winningOption}${body.nonce}`
    const messageHash = crypto.createHash('sha256').update(messagePayload).digest()

    let sigValid: boolean
    try {
      sigValid = await verifyQubicSignature(
        body.resolverAddress,
        messageHash,
        body.signature,
      )
    } catch (err) {
      return NextResponse.json(
        { error: `Signature verification unavailable: ${err instanceof Error ? err.message : 'SDK error'}` },
        { status: 503 },
      )
    }

    if (!sigValid) {
      return NextResponse.json(
        { error: 'Invalid signature: does not match resolver address' },
        { status: 403 },
      )
    }

    // Validate winning option
    if (body.winningOption < 0 || body.winningOption >= market.numOptions) {
      return NextResponse.json(
        { error: `winningOption must be 0-${market.numOptions - 1}` },
        { status: 400 },
      )
    }

    // Check market status
    if (market.status !== 'active' && market.status !== 'closed') {
      return NextResponse.json(
        { error: `Cannot resolve market with status: ${market.status}` },
        { status: 400 },
      )
    }

    // Check end date has passed
    if (new Date() < parseUtcTimestamp(market.endDate)) {
      return NextResponse.json(
        { error: 'Market has not reached its end date yet' },
        { status: 400 },
      )
    }

    // Resolve
    const result = await resolveMarket({
      marketId: body.marketId,
      winningOption: body.winningOption,
      oracleProof: {
        source: 'creator_resolution',
        data: {
          resolverAddress: body.resolverAddress,
          nonce: body.nonce,
          signatureVerified: true,
          resolvedAt: new Date().toISOString(),
        },
      },
    })

    if (!result.success) {
      return NextResponse.json({ error: result.error }, { status: 400 })
    }

    return NextResponse.json(result)
  } catch (error) {
    return safeErrorResponse(error, 'Failed to resolve market')
  }
}
