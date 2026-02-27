/**
 * QPredict Resolution Proof Package Builder
 *
 * Generates a downloadable JSON proof package for any resolved market.
 * Contains everything needed to independently verify the resolution:
 * - Market parameters + commitment hash
 * - Oracle attestations with HMAC signatures
 * - Winner determination logic
 * - Payout calculations
 * - Chain entries (audit trail)
 * - On-chain TX IDs
 * - Self-verifying proof hash
 */

import {
  type ResolutionProofPackage,
  type ChainEntry,
  computeResolutionProofHash,
} from './provably-fair'
import { getMarketDB } from './market-db'
import { getAttestationKeyForVerification } from './oracle-resolution'

// Quottery SC fee constants (applied to LOSER pool only, not total pool)
// 2% burn + 10% shareholder + 0.5% operator = 12.5% base
// Oracle fee is per-market (QPredict default: 0%)
const FEES = {
  burnBps: 200, // 2%
  shareholderBps: 1000, // 10%
  operatorBps: 50, // 0.5%
}

/**
 * Build a complete resolution proof package for a resolved market.
 */
export function buildResolutionProofPackage(
  marketId: string,
): ResolutionProofPackage | null {
  const db = getMarketDB()
  const market = db.getMarket(marketId)

  if (!market || market.status !== 'resolved') {
    return null
  }

  // Get oracle attestations
  const attestationRows = db.getAttestationsByMarket(marketId)
  const attestations = attestationRows.map((row) => ({
    id: row.id,
    marketId: row.marketId,
    oracleSource: row.oracleSource,
    pair: row.pair,
    price: row.price,
    tick: row.tick,
    epoch: row.epoch,
    sourceTimestamp: row.sourceTimestamp,
    attestationHash: row.attestationHash,
    serverSignature: row.serverSignature,
    createdAt: row.createdAt,
  }))

  // Get chain entries for this market
  const marketChainEntries = db.getChainByEntity(marketId)

  // Also get chain entries for bets related to this market
  const bets = db.getBetsByMarket(marketId)
  const betChainEntries: ChainEntry[] = []
  for (const bet of bets) {
    const entries = db.getChainByEntity(bet.id)
    betChainEntries.push(
      ...entries.map((e) => ({
        sequenceNum: e.sequenceNum,
        eventType: e.eventType as ChainEntry['eventType'],
        entityId: e.entityId,
        payloadHash: e.payloadHash,
        prevHash: e.prevHash,
        chainHash: e.chainHash,
        payloadJson: e.payloadJson,
        createdAt: e.createdAt,
      })),
    )
  }

  // Combine and sort all chain entries
  const allChainEntries: ChainEntry[] = [
    ...marketChainEntries.map((e) => ({
      sequenceNum: e.sequenceNum,
      eventType: e.eventType as ChainEntry['eventType'],
      entityId: e.entityId,
      payloadHash: e.payloadHash,
      prevHash: e.prevHash,
      chainHash: e.chainHash,
      payloadJson: e.payloadJson,
      createdAt: e.createdAt,
    })),
    ...betChainEntries,
  ].sort((a, b) => a.sequenceNum - b.sequenceNum)

  // Calculate fee breakdown — fees apply to LOSER pool only (matches Quottery SC)
  const totalPool = market.totalPool
  const winnerSlots =
    market.winningOption === 0 ? market.yesSlots : market.noSlots
  const loserSlots =
    market.winningOption === 0 ? market.noSlots : market.yesSlots
  const totalSlots = winnerSlots + loserSlots

  // Decompose pool into winner stake + loser pool
  const winnerStake = totalSlots > 0
    ? Math.floor((totalPool * winnerSlots) / totalSlots)
    : 0
  const loserPoolAmount = totalPool - winnerStake
  const loserPoolBig = BigInt(loserPoolAmount)

  const oracleFeeBps = market.oracleFeeBps ?? 0
  const burn = Number((loserPoolBig * BigInt(FEES.burnBps)) / 10000n)
  const shareholder = Number(
    (loserPoolBig * BigInt(FEES.shareholderBps)) / 10000n,
  )
  const operator = Number(
    (loserPoolBig * BigInt(FEES.operatorBps)) / 10000n,
  )
  const oracle = Number((loserPoolBig * BigInt(oracleFeeBps)) / 10000n)
  const totalFees = burn + shareholder + operator + oracle

  const winnerPool = winnerStake + loserPoolAmount - totalFees
  const payoutPerSlot = winnerSlots > 0 ? Math.floor(winnerPool / winnerSlots) : 0
  const totalPaidOut = payoutPerSlot * winnerSlots

  // Collect on-chain TX IDs
  const joinBetTxs = bets
    .filter((b) => b.txHash)
    .map((b) => ({ betId: b.id, txId: b.txHash! }))

  // Build package (without proofHash first)
  const pkgWithoutHash: Omit<ResolutionProofPackage, 'proofHash'> = {
    version: 1,
    marketId,
    market: {
      pair: market.pair,
      question: market.question,
      resolutionType: market.resolutionType,
      resolutionTarget: market.resolutionTarget,
      resolutionTargetHigh: market.resolutionTargetHigh,
      closeDate: market.closeDate,
      endDate: market.endDate,
      minBetQu: market.minBetQu,
      maxSlots: market.maxSlots,
      creatorAddress: market.creatorAddress ?? '',
      commitmentHash: market.commitmentHash ?? '',
    },
    resolution: {
      resolutionPrice: market.resolutionPrice ?? 0,
      winningOption: market.winningOption ?? 0,
      resolvedAt: market.resolvedAt ?? '',
      resolutionMethod: attestations.length > 0
        ? 'multi_oracle_median'
        : 'single_oracle',
    },
    oracleAttestations: attestations,
    payoutSummary: {
      totalPool,
      winnerSlots,
      loserSlots,
      payoutPerSlot,
      totalPaidOut,
      feeBreakdown: {
        burn,
        shareholder,
        operator,
        oracle,
        total: totalFees,
      },
    },
    chainEntries: allChainEntries,
    onChainTxIds: {
      issueBet: market.txHash ?? undefined,
      joinBets: joinBetTxs,
      publishResult: undefined, // TODO: Store publishResult txId in market
    },
    generatedAt: new Date().toISOString(),
  }

  // Compute proof hash
  const proofHash = computeResolutionProofHash(pkgWithoutHash)

  return {
    ...pkgWithoutHash,
    proofHash,
  }
}
