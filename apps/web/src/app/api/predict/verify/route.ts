/**
 * QPredict Verification API
 *
 * Endpoints for provably fair verification:
 *
 * GET /api/predict/verify?type=chain              — Get commitment chain status
 * GET /api/predict/verify?type=chain&validate=true — Validate full chain integrity
 * GET /api/predict/verify?type=chain&entity=xxx    — Get chain entries for entity
 * GET /api/predict/verify?type=market&id=xxx       — Get market resolution proof
 * GET /api/predict/verify?type=solvency            — Get latest solvency proof
 * GET /api/predict/verify?type=solvency&history=20 — Get solvency proof history
 * GET /api/predict/verify?type=inclusion&address=x — Get user inclusion proof
 * GET /api/predict/verify?type=proof&id=xxx        — Download full proof package
 * GET /api/predict/verify?format=proof-package&marketId=xxx — Download proof package as file
 */

import { NextResponse, type NextRequest } from 'next/server'
import { getMarketDB } from '@/lib/predict/market-db'
import { verifyChainSequence, verifyResolutionProofPackage, type ChainEntry } from '@/lib/predict/provably-fair'
import { buildResolutionProofPackage } from '@/lib/predict/resolution-proof-package'
import { getLatestSolvencyProof, getSolvencyProofs, getUserInclusionProof } from '@/lib/predict/solvency-proof'
import { getAttestationKeyForVerification } from '@/lib/predict/oracle-resolution'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const url = request.nextUrl
    const format = url.searchParams.get('format')

    // Handle proof-package download format
    if (format === 'proof-package') {
      return handleProofPackageDownload(url.searchParams)
    }

    const type = url.searchParams.get('type')

    switch (type) {
      case 'chain':
        return handleChainVerification(url.searchParams)
      case 'market':
        return handleMarketVerification(url.searchParams)
      case 'solvency':
        return handleSolvencyVerification(url.searchParams)
      case 'inclusion':
        return handleInclusionProof(url.searchParams)
      case 'proof':
        return handleProofDownload(url.searchParams)
      default:
        return NextResponse.json({
          endpoints: {
            chain: '/api/predict/verify?type=chain',
            chainValidate: '/api/predict/verify?type=chain&validate=true',
            market: '/api/predict/verify?type=market&id=mkt_xxx',
            solvency: '/api/predict/verify?type=solvency',
            inclusion: '/api/predict/verify?type=inclusion&address=XXXX...',
            proof: '/api/predict/verify?type=proof&id=mkt_xxx',
            proofPackage: '/api/predict/verify?format=proof-package&marketId=mkt_xxx',
          },
        })
    }
  } catch (err) {
    return safeErrorResponse(err, 'Verification failed')
  }
}

// ---------------------------------------------------------------------------
// Chain Verification
// ---------------------------------------------------------------------------

function handleChainVerification(params: URLSearchParams) {
  const db = getMarketDB()
  const validate = params.get('validate') === 'true'
  const entity = params.get('entity')

  if (entity) {
    // Get chain entries for a specific entity
    const entries = db.getChainByEntity(entity)
    return NextResponse.json({
      entityId: entity,
      entries: entries.length,
      chainEntries: entries,
    })
  }

  // Get chain status
  const count = db.getChainCount()
  const latest = db.getLatestChainEntry()

  const result: Record<string, unknown> = {
    totalEntries: count,
    latestSequence: latest?.sequenceNum ?? 0,
    latestHash: latest?.chainHash ?? null,
    latestEvent: latest?.eventType ?? null,
    latestEntity: latest?.entityId ?? null,
    latestTimestamp: latest?.createdAt ?? null,
  }

  if (validate) {
    // Full chain validation
    const allEntries = db.getAllChainEntries()
    const chainEntries: ChainEntry[] = allEntries.map((e) => ({
      sequenceNum: e.sequenceNum,
      eventType: e.eventType as ChainEntry['eventType'],
      entityId: e.entityId,
      payloadHash: e.payloadHash,
      prevHash: e.prevHash,
      chainHash: e.chainHash,
      payloadJson: e.payloadJson,
      createdAt: e.createdAt,
    }))

    const verification = verifyChainSequence(chainEntries)
    result.validation = verification
  }

  return NextResponse.json(result)
}

// ---------------------------------------------------------------------------
// Market Verification
// ---------------------------------------------------------------------------

function handleMarketVerification(params: URLSearchParams) {
  const marketId = params.get('id')
  if (!marketId) {
    return NextResponse.json(
      { error: 'Market ID required (?id=mkt_xxx)' },
      { status: 400 },
    )
  }

  const db = getMarketDB()
  const market = db.getMarket(marketId)
  if (!market) {
    return NextResponse.json({ error: 'Market not found' }, { status: 404 })
  }

  // Get attestations
  const attestations = db.getAttestationsByMarket(marketId)

  // Get chain entries
  const chainEntries = db.getChainByEntity(marketId)

  // Get bets with their chain entries
  const bets = db.getBetsByMarket(marketId)
  const betVerification = bets.map((bet) => ({
    betId: bet.id,
    userAddress: bet.userAddress,
    option: bet.option,
    slots: bet.slots,
    amountQu: bet.amountQu,
    commitmentHash: bet.commitmentHash,
    hasNonce: !!bet.commitmentNonce,
    status: bet.status,
    payoutQu: bet.payoutQu,
    chainEntries: db.getChainByEntity(bet.id).length,
  }))

  return NextResponse.json({
    market: {
      id: market.id,
      pair: market.pair,
      question: market.question,
      resolutionType: market.resolutionType,
      resolutionTarget: market.resolutionTarget,
      resolutionTargetHigh: market.resolutionTargetHigh,
      status: market.status,
      commitmentHash: market.commitmentHash,
      resolutionPrice: market.resolutionPrice,
      winningOption: market.winningOption,
      resolvedAt: market.resolvedAt,
    },
    oracleAttestations: attestations.map((a) => ({
      source: a.oracleSource,
      price: a.price,
      timestamp: a.sourceTimestamp,
      attestationHash: a.attestationHash,
    })),
    chainEntries: chainEntries.length,
    bets: betVerification,
    proofAvailable: market.status === 'resolved',
  })
}

// ---------------------------------------------------------------------------
// Solvency Verification
// ---------------------------------------------------------------------------

function handleSolvencyVerification(params: URLSearchParams) {
  const historyCount = params.get('history')

  if (historyCount) {
    const proofs = getSolvencyProofs(parseInt(historyCount, 10) || 20)
    return NextResponse.json({
      proofs: proofs.map((p) => ({
        id: p.id,
        merkleRoot: p.merkleRoot,
        totalUserBalance: p.totalUserBalance,
        onChainBalance: p.onChainBalance,
        isSolvent: p.isSolvent === 1,
        accountCount: p.accountCount,
        tick: p.tick,
        epoch: p.epoch,
        createdAt: p.createdAt,
      })),
    })
  }

  const latest = getLatestSolvencyProof()
  if (!latest) {
    return NextResponse.json({
      hasSolvencyProof: false,
      message: 'No solvency proofs generated yet',
    })
  }

  return NextResponse.json({
    hasSolvencyProof: true,
    proof: {
      id: latest.id,
      merkleRoot: latest.merkleRoot,
      totalUserBalance: latest.totalUserBalance,
      onChainBalance: latest.onChainBalance,
      isSolvent: latest.isSolvent === 1,
      accountCount: latest.accountCount,
      tick: latest.tick,
      epoch: latest.epoch,
      createdAt: latest.createdAt,
    },
  })
}

// ---------------------------------------------------------------------------
// User Inclusion Proof
// ---------------------------------------------------------------------------

function handleInclusionProof(params: URLSearchParams) {
  const address = params.get('address')
  if (!address) {
    return NextResponse.json(
      { error: 'Address required (?address=XXXX...)' },
      { status: 400 },
    )
  }

  const proof = getUserInclusionProof(address)
  if (!proof) {
    return NextResponse.json(
      { error: 'No inclusion proof available (no solvency proof or account not found)' },
      { status: 404 },
    )
  }

  return NextResponse.json(proof)
}

// ---------------------------------------------------------------------------
// Full Proof Package Download
// ---------------------------------------------------------------------------

function handleProofDownload(params: URLSearchParams) {
  const marketId = params.get('id')
  if (!marketId) {
    return NextResponse.json(
      { error: 'Market ID required (?id=mkt_xxx)' },
      { status: 400 },
    )
  }

  const pkg = buildResolutionProofPackage(marketId)
  if (!pkg) {
    return NextResponse.json(
      { error: 'Proof package not available (market not resolved or not found)' },
      { status: 404 },
    )
  }

  // Optionally verify the package
  const verify = params.get('verify') === 'true'
  if (verify) {
    const attestationKey = getAttestationKeyForVerification()
    const verification = verifyResolutionProofPackage(pkg, attestationKey)
    return NextResponse.json({
      package: pkg,
      verification,
    })
  }

  return NextResponse.json(pkg)
}

// ---------------------------------------------------------------------------
// Proof Package File Download (format=proof-package)
// ---------------------------------------------------------------------------

function handleProofPackageDownload(params: URLSearchParams) {
  const marketId = params.get('marketId')
  if (!marketId) {
    return NextResponse.json(
      { error: 'Market ID required (?marketId=mkt_xxx)' },
      { status: 400 },
    )
  }

  const pkg = buildResolutionProofPackage(marketId)
  if (!pkg) {
    return NextResponse.json(
      { error: 'Proof package not available (market not resolved or not found)' },
      { status: 404 },
    )
  }

  const jsonBody = JSON.stringify(pkg, null, 2)
  const sanitizedId = marketId.replace(/[^a-zA-Z0-9_-]/g, '_')
  const filename = `qpredict-proof-${sanitizedId}.json`

  return new NextResponse(jsonBody, {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Content-Disposition': `attachment; filename="${filename}"`,
    },
  })
}
