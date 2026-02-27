/**
 * QPredict Public History API
 *
 * All platform data is publicly accessible and downloadable.
 * Every action is tracked in the commitment chain and can be independently verified.
 *
 * GET /api/predict/history?type=chain              — Full commitment chain (JSON download)
 * GET /api/predict/history?type=chain&from=1&to=50 — Chain entries by range
 * GET /api/predict/history?type=markets            — All markets with full details
 * GET /api/predict/history?type=market&id=mkt_xxx  — Single market complete history
 * GET /api/predict/history?type=bets&address=XXX   — User's complete bet history
 * GET /api/predict/history?type=transactions&address=XXX — User's transaction history
 * GET /api/predict/history?type=proofs             — All solvency proofs
 * GET /api/predict/history?type=attestations       — All oracle attestations
 * GET /api/predict/history?type=full               — Complete platform export (everything)
 */

import { NextResponse, type NextRequest } from 'next/server'
import { getMarketDB } from '@/lib/predict/market-db'
import { getSolvencyProofs } from '@/lib/predict/solvency-proof'
import { buildResolutionProofPackage } from '@/lib/predict/resolution-proof-package'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /default')
  if (rl) return rl

  try {
    const url = request.nextUrl
    const type = url.searchParams.get('type')
    const download = url.searchParams.get('download') === 'true'

    let data: unknown
    let filename: string

    switch (type) {
      case 'chain':
        ({ data, filename } = handleChainExport(url.searchParams))
        break
      case 'markets':
        ({ data, filename } = handleMarketsExport())
        break
      case 'market':
        ({ data, filename } = handleMarketExport(url.searchParams))
        break
      case 'bets':
        ({ data, filename } = handleBetsExport(url.searchParams))
        break
      case 'transactions':
        ({ data, filename } = handleTransactionsExport(url.searchParams))
        break
      case 'proofs':
        ({ data, filename } = handleProofsExport())
        break
      case 'attestations':
        ({ data, filename } = handleAttestationsExport())
        break
      case 'full':
        ({ data, filename } = handleFullExport())
        break
      default:
        return NextResponse.json({
          description: 'QPredict Public History — All data is publicly accessible',
          endpoints: {
            chain: '/api/predict/history?type=chain',
            chainRange: '/api/predict/history?type=chain&from=1&to=100',
            markets: '/api/predict/history?type=markets',
            market: '/api/predict/history?type=market&id=mkt_xxx',
            bets: '/api/predict/history?type=bets&address=XXXX...',
            transactions: '/api/predict/history?type=transactions&address=XXXX...',
            proofs: '/api/predict/history?type=proofs',
            attestations: '/api/predict/history?type=attestations',
            full: '/api/predict/history?type=full',
          },
          note: 'Add &download=true to any endpoint for Content-Disposition header',
        })
    }

    if (download) {
      return new NextResponse(JSON.stringify(data, null, 2), {
        headers: {
          'Content-Type': 'application/json',
          'Content-Disposition': `attachment; filename="${filename}"`,
        },
      })
    }

    return NextResponse.json(data)
  } catch (err) {
    return safeErrorResponse(err, 'Failed to fetch history')
  }
}

// ---------------------------------------------------------------------------
// Chain Export
// ---------------------------------------------------------------------------

function handleChainExport(params: URLSearchParams) {
  const db = getMarketDB()
  const from = params.get('from')
  const to = params.get('to')

  // Paginated range query
  if (from && to) {
    const fromNum = parseInt(from, 10)
    const toNum = parseInt(to, 10)
    // Cap range to max 1000 entries per request
    const cappedTo = Math.min(toNum, fromNum + 999)
    const entries = db.getChainRange(fromNum, cappedTo)
    return {
      data: {
        exportType: 'commitment_chain_range',
        range: { from: fromNum, to: cappedTo, requestedTo: toNum },
        count: entries.length,
        hasMore: toNum > cappedTo,
        entries,
        exportedAt: new Date().toISOString(),
      },
      filename: `qpredict-chain-${from}-${cappedTo}.json`,
    }
  }

  // Paginated full chain export (default limit 100, max 1000)
  const limitParam = parseInt(params.get('limit') ?? '100', 10)
  const offsetParam = parseInt(params.get('offset') ?? '0', 10)
  const limit = Math.min(Math.max(1, isNaN(limitParam) ? 100 : limitParam), 1000)
  const offset = Math.max(0, isNaN(offsetParam) ? 0 : offsetParam)

  const totalCount = db.getChainCount()
  const latest = db.getLatestChainEntry()

  // Use range query with offset-based pagination
  const entries = db.getChainRange(offset + 1, offset + limit)

  return {
    data: {
      exportType: 'commitment_chain',
      totalEntries: totalCount,
      genesisHash: '0000000000000000000000000000000000000000000000000000000000000000',
      latestHash: latest?.chainHash ?? null,
      latestSequence: latest?.sequenceNum ?? 0,
      pagination: {
        limit,
        offset,
        returned: entries.length,
        hasMore: offset + limit < totalCount,
      },
      entries: entries.map((e) => ({
        sequence: e.sequenceNum,
        eventType: e.eventType,
        entityId: e.entityId,
        payloadHash: e.payloadHash,
        prevHash: e.prevHash,
        chainHash: e.chainHash,
        payload: JSON.parse(e.payloadJson),
        timestamp: e.createdAt,
      })),
      exportedAt: new Date().toISOString(),
      verificationNote:
        'To verify: for each entry, compute SHA-256(sequence|eventType|entityId|SHA-256(payload)|prevHash) and compare to chainHash. Genesis prevHash is all zeros.',
    },
    filename: `qpredict-chain-${offset}-${offset + limit}-${Date.now()}.json`,
  }
}

// ---------------------------------------------------------------------------
// Markets Export
// ---------------------------------------------------------------------------

function handleMarketsExport() {
  const db = getMarketDB()
  // Cap at 100 markets per request to prevent unbounded response
  const markets = db.listMarkets().slice(0, 100)

  const marketsWithBets = markets.map((market) => {
    const bets = db.getBetsByMarket(market.id)
    const escrows = db.getEscrowsByMarket(market.id)
    const escrowByBet = new Map(escrows.map((e) => [e.betId, e]))
    const chainEntries = db.getChainByEntity(market.id)
    const attestations = db.getAttestationsByMarket(market.id)
    const snapshots = db.getSnapshots(market.id)

    return {
      ...market,
      bets: bets.map((b) => {
        const esc = escrowByBet.get(b.id)
        return {
          id: b.id,
          userAddress: b.userAddress,
          option: b.option,
          optionLabel: b.option === 0 ? 'YES' : 'NO',
          slots: b.slots,
          amountQu: b.amountQu,
          status: b.status,
          payoutQu: b.payoutQu,
          commitmentHash: b.commitmentHash,
          txHash: b.txHash,
          createdAt: b.createdAt,
          escrow: esc
            ? {
                address: esc.escrowAddress,
                status: esc.status,
                depositDetectedAt: esc.depositDetectedAt,
                depositAmountQu: esc.depositAmountQu,
                joinBetTxId: esc.joinBetTxId,
                joinBetTick: esc.joinBetTick,
                payoutDetectedAt: esc.payoutDetectedAt,
                payoutAmountQu: esc.payoutAmountQu,
                sweepTxId: esc.sweepTxId,
                sweepTick: esc.sweepTick,
                createdAt: esc.createdAt,
                expiresAt: esc.expiresAt,
              }
            : null,
        }
      }),
      oracleAttestations: attestations.map((a) => ({
        source: a.oracleSource,
        price: a.price,
        timestamp: a.sourceTimestamp,
        attestationHash: a.attestationHash,
      })),
      chainEntries: chainEntries.length,
      snapshots: snapshots.map((s) => ({
        timestamp: s.timestamp,
        yesSlots: s.yesSlots,
        noSlots: s.noSlots,
        impliedProbability: s.impliedProbability,
        totalPool: s.totalPool,
      })),
    }
  })

  return {
    data: {
      exportType: 'all_markets',
      count: marketsWithBets.length,
      markets: marketsWithBets,
      exportedAt: new Date().toISOString(),
    },
    filename: `qpredict-markets-${Date.now()}.json`,
  }
}

// ---------------------------------------------------------------------------
// Single Market Export
// ---------------------------------------------------------------------------

function handleMarketExport(params: URLSearchParams) {
  const marketId = params.get('id')
  if (!marketId) {
    return {
      data: { error: 'Market ID required (?id=mkt_xxx)' },
      filename: 'error.json',
    }
  }

  const db = getMarketDB()
  const market = db.getMarket(marketId)
  if (!market) {
    return {
      data: { error: 'Market not found' },
      filename: 'error.json',
    }
  }

  const bets = db.getBetsByMarket(marketId)
  const escrows = db.getEscrowsByMarket(marketId)
  const escrowByBet = new Map(escrows.map((e) => [e.betId, e]))
  const chainEntries = db.getChainByEntity(marketId)
  const attestations = db.getAttestationsByMarket(marketId)
  const snapshots = db.getSnapshots(marketId)

  // Get chain entries for all bets too
  const betChainEntries = bets.flatMap((b) =>
    db.getChainByEntity(b.id).map((e) => ({
      sequence: e.sequenceNum,
      eventType: e.eventType,
      entityId: e.entityId,
      payloadHash: e.payloadHash,
      chainHash: e.chainHash,
      timestamp: e.createdAt,
    })),
  )

  // Build proof package if resolved
  const proofPackage =
    market.status === 'resolved' ? buildResolutionProofPackage(marketId) : null

  return {
    data: {
      exportType: 'market_complete_history',
      market: {
        ...market,
        bets: bets.map((b) => {
          const esc = escrowByBet.get(b.id)
          return {
            id: b.id,
            userAddress: b.userAddress,
            option: b.option,
            optionLabel: b.option === 0 ? 'YES' : 'NO',
            slots: b.slots,
            amountQu: b.amountQu,
            status: b.status,
            payoutQu: b.payoutQu,
            commitmentHash: b.commitmentHash,
            commitmentNonce: b.commitmentNonce,
            txHash: b.txHash,
            createdAt: b.createdAt,
            escrow: esc
              ? {
                  address: esc.escrowAddress,
                  status: esc.status,
                  depositDetectedAt: esc.depositDetectedAt,
                  depositAmountQu: esc.depositAmountQu,
                  joinBetTxId: esc.joinBetTxId,
                  joinBetTick: esc.joinBetTick,
                  payoutDetectedAt: esc.payoutDetectedAt,
                  payoutAmountQu: esc.payoutAmountQu,
                  sweepTxId: esc.sweepTxId,
                  sweepTick: esc.sweepTick,
                  createdAt: esc.createdAt,
                  expiresAt: esc.expiresAt,
                }
              : null,
          }
        }),
        oracleAttestations: attestations.map((a) => ({
          id: a.id,
          source: a.oracleSource,
          pair: a.pair,
          price: a.price,
          tick: a.tick,
          epoch: a.epoch,
          timestamp: a.sourceTimestamp,
          attestationHash: a.attestationHash,
          serverSignature: a.serverSignature,
        })),
        chainEntries: [
          ...chainEntries.map((e) => ({
            sequence: e.sequenceNum,
            eventType: e.eventType,
            entityId: e.entityId,
            payloadHash: e.payloadHash,
            chainHash: e.chainHash,
            payload: JSON.parse(e.payloadJson),
            timestamp: e.createdAt,
          })),
          ...betChainEntries,
        ].sort(
          (a, b) => a.sequence - b.sequence,
        ),
        snapshots,
      },
      proofPackage,
      exportedAt: new Date().toISOString(),
    },
    filename: `qpredict-market-${marketId}-${Date.now()}.json`,
  }
}

// ---------------------------------------------------------------------------
// User Bets Export
// ---------------------------------------------------------------------------

function handleBetsExport(params: URLSearchParams) {
  const address = params.get('address')
  if (!address) {
    return {
      data: { error: 'Address required (?address=XXXX...)' },
      filename: 'error.json',
    }
  }

  const db = getMarketDB()
  const bets = db.getBetsByUser(address)

  const betsWithContext = bets.map((bet) => {
    const market = db.getMarket(bet.marketId)
    const betChain = db.getChainByEntity(bet.id)
    return {
      ...bet,
      optionLabel: bet.option === 0 ? 'YES' : 'NO',
      market: market
        ? {
            id: market.id,
            pair: market.pair,
            question: market.question,
            status: market.status,
            resolutionPrice: market.resolutionPrice,
            winningOption: market.winningOption,
          }
        : null,
      chainEntries: betChain.map((e) => ({
        sequence: e.sequenceNum,
        eventType: e.eventType,
        chainHash: e.chainHash,
        timestamp: e.createdAt,
      })),
    }
  })

  return {
    data: {
      exportType: 'user_bet_history',
      address,
      totalBets: betsWithContext.length,
      bets: betsWithContext,
      exportedAt: new Date().toISOString(),
    },
    filename: `qpredict-bets-${address.slice(0, 12)}-${Date.now()}.json`,
  }
}

// ---------------------------------------------------------------------------
// User Transactions Export
// ---------------------------------------------------------------------------

function handleTransactionsExport(params: URLSearchParams) {
  const address = params.get('address')
  if (!address) {
    return {
      data: { error: 'Address required (?address=XXXX...)' },
      filename: 'error.json',
    }
  }

  const db = getMarketDB()
  const transactions = db.getTransactions(address)
  const account = db.getAccount(address)

  return {
    data: {
      exportType: 'user_transaction_history',
      address,
      account: account
        ? {
            balanceQu: account.balanceQu,
            totalDeposited: account.totalDeposited,
            totalWithdrawn: account.totalWithdrawn,
            totalBet: account.totalBet,
            totalWon: account.totalWon,
            createdAt: account.createdAt,
          }
        : null,
      totalTransactions: transactions.length,
      transactions,
      exportedAt: new Date().toISOString(),
    },
    filename: `qpredict-txs-${address.slice(0, 12)}-${Date.now()}.json`,
  }
}

// ---------------------------------------------------------------------------
// Solvency Proofs Export
// ---------------------------------------------------------------------------

function handleProofsExport() {
  const proofs = getSolvencyProofs(1000) // Get up to 1000 proofs

  return {
    data: {
      exportType: 'solvency_proofs',
      count: proofs.length,
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
      exportedAt: new Date().toISOString(),
    },
    filename: `qpredict-solvency-proofs-${Date.now()}.json`,
  }
}

// ---------------------------------------------------------------------------
// Oracle Attestations Export
// ---------------------------------------------------------------------------

function handleAttestationsExport() {
  const db = getMarketDB()
  const markets = db.listMarkets()

  const allAttestations = markets.flatMap((market) => {
    const attestations = db.getAttestationsByMarket(market.id)
    return attestations.map((a) => ({
      marketId: market.id,
      marketPair: market.pair,
      marketQuestion: market.question,
      source: a.oracleSource,
      pair: a.pair,
      price: a.price,
      tick: a.tick,
      epoch: a.epoch,
      timestamp: a.sourceTimestamp,
      attestationHash: a.attestationHash,
      serverSignature: a.serverSignature,
      createdAt: a.createdAt,
    }))
  })

  return {
    data: {
      exportType: 'oracle_attestations',
      count: allAttestations.length,
      attestations: allAttestations,
      verificationNote:
        'Each attestation hash = SHA-256(source|pair|price(8dp)|tick|epoch|timestamp). Server signature = HMAC-SHA256(attestationHash, ATTESTATION_SECRET_KEY).',
      exportedAt: new Date().toISOString(),
    },
    filename: `qpredict-attestations-${Date.now()}.json`,
  }
}

// ---------------------------------------------------------------------------
// Full Platform Export
// ---------------------------------------------------------------------------

function handleFullExport() {
  const db = getMarketDB()

  // All chain entries
  const chainEntries = db.getAllChainEntries()
  const latest = db.getLatestChainEntry()

  // All markets with bets
  const markets = db.listMarkets()
  const marketsData = markets.map((market) => {
    const bets = db.getBetsByMarket(market.id)
    const escrows = db.getEscrowsByMarket(market.id)
    const escrowByBet = new Map(escrows.map((e) => [e.betId, e]))
    const attestations = db.getAttestationsByMarket(market.id)
    const snapshots = db.getSnapshots(market.id)
    const proofPackage =
      market.status === 'resolved'
        ? buildResolutionProofPackage(market.id)
        : null

    return {
      ...market,
      bets: bets.map((b) => {
        const esc = escrowByBet.get(b.id)
        return {
          id: b.id,
          userAddress: b.userAddress,
          option: b.option,
          optionLabel: b.option === 0 ? 'YES' : 'NO',
          slots: b.slots,
          amountQu: b.amountQu,
          status: b.status,
          payoutQu: b.payoutQu,
          commitmentHash: b.commitmentHash,
          commitmentNonce: b.commitmentNonce,
          txHash: b.txHash,
          createdAt: b.createdAt,
          escrow: esc
            ? {
                address: esc.escrowAddress,
                status: esc.status,
                depositDetectedAt: esc.depositDetectedAt,
                depositAmountQu: esc.depositAmountQu,
                joinBetTxId: esc.joinBetTxId,
                joinBetTick: esc.joinBetTick,
                payoutDetectedAt: esc.payoutDetectedAt,
                payoutAmountQu: esc.payoutAmountQu,
                sweepTxId: esc.sweepTxId,
                sweepTick: esc.sweepTick,
                createdAt: esc.createdAt,
                expiresAt: esc.expiresAt,
              }
            : null,
        }
      }),
      oracleAttestations: attestations.map((a) => ({
        source: a.oracleSource,
        price: a.price,
        timestamp: a.sourceTimestamp,
        attestationHash: a.attestationHash,
        serverSignature: a.serverSignature,
      })),
      snapshots,
      proofPackage,
    }
  })

  // Solvency proofs
  const solvencyProofs = getSolvencyProofs(1000)

  // Platform stats
  const stats = db.getPlatformStats()

  return {
    data: {
      exportType: 'full_platform_export',
      platformStats: stats,
      commitmentChain: {
        totalEntries: chainEntries.length,
        genesisHash:
          '0000000000000000000000000000000000000000000000000000000000000000',
        latestHash: latest?.chainHash ?? null,
        latestSequence: latest?.sequenceNum ?? 0,
        entries: chainEntries.map((e) => ({
          sequence: e.sequenceNum,
          eventType: e.eventType,
          entityId: e.entityId,
          payloadHash: e.payloadHash,
          prevHash: e.prevHash,
          chainHash: e.chainHash,
          payload: JSON.parse(e.payloadJson),
          timestamp: e.createdAt,
        })),
      },
      markets: marketsData,
      solvencyProofs: solvencyProofs.map((p) => ({
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
      exportedAt: new Date().toISOString(),
      verificationGuide: {
        chainVerification:
          'For each chain entry: SHA-256(sequence|eventType|entityId|SHA-256(canonicalJSON(payload))|prevHash) must equal chainHash',
        betCommitmentVerification:
          'For each bet: SHA-256(marketId|userAddress|option|slots|nonce) must equal commitmentHash',
        marketCommitmentVerification:
          'For each market: SHA-256(canonicalJSON(marketParams)) must equal commitmentHash',
        oracleVerification:
          'For each attestation: SHA-256(source|pair|price(8dp)|tick|epoch|timestamp) must equal attestationHash',
        solvencyVerification:
          'For each solvency proof: Merkle root must be computable from leaf hashes, on-chain balance must be >= total user balance',
      },
    },
    filename: `qpredict-full-export-${Date.now()}.json`,
  }
}
