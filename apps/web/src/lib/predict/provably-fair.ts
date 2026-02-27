/**
 * QPredict Provably Fair System
 *
 * Core cryptographic module providing:
 * - Commitment chain (append-only hash chain for audit trail)
 * - Bet commitments (SHA-256 binding of bet parameters)
 * - Oracle attestations (HMAC-signed price attestations)
 * - Merkle tree (for solvency proofs)
 * - Canonical JSON hashing (deterministic serialization)
 */

import crypto from 'crypto'

// ---------------------------------------------------------------------------
// Canonical JSON
// ---------------------------------------------------------------------------

/**
 * Deterministic JSON serialization with sorted keys.
 * Ensures the same object always produces the same string.
 */
export function canonicalJSON(obj: unknown): string {
  return JSON.stringify(obj, (_key, value) => {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return Object.keys(value as Record<string, unknown>)
        .sort()
        .reduce(
          (sorted, k) => {
            sorted[k] = (value as Record<string, unknown>)[k]
            return sorted
          },
          {} as Record<string, unknown>,
        )
    }
    return value
  })
}

/**
 * SHA-256 hash of any object via canonical JSON.
 */
export function hashCanonicalJSON(obj: unknown): string {
  return sha256(canonicalJSON(obj))
}

// ---------------------------------------------------------------------------
// SHA-256 Helpers
// ---------------------------------------------------------------------------

export function sha256(input: string): string {
  return crypto.createHash('sha256').update(input, 'utf-8').digest('hex')
}

export function sha256Bytes(input: Buffer | Uint8Array): string {
  return crypto.createHash('sha256').update(input).digest('hex')
}

export function hmacSha256(data: string, key: string): string {
  return crypto.createHmac('sha256', key).update(data, 'utf-8').digest('hex')
}

// ---------------------------------------------------------------------------
// Commitment Chain
// ---------------------------------------------------------------------------

export type ChainEventType =
  | 'market_create'
  | 'bet_place'
  | 'bet_confirm'
  | 'market_resolve'
  | 'market_recovery'
  | 'payout'
  | 'deposit'
  | 'withdrawal'
  | 'solvency_proof'
  | 'solvency_violation'

export interface ChainEntry {
  sequenceNum: number
  eventType: ChainEventType
  entityId: string
  payloadHash: string
  prevHash: string
  chainHash: string
  payloadJson: string
  createdAt: string
}

const GENESIS_HASH = '0'.repeat(64)

/**
 * Compute the chain hash for a given entry.
 *
 * chainHash = SHA-256(sequenceNum | eventType | entityId | payloadHash | prevHash)
 */
export function computeChainHash(
  sequenceNum: number,
  eventType: string,
  entityId: string,
  payloadHash: string,
  prevHash: string,
): string {
  const input = `${sequenceNum}|${eventType}|${entityId}|${payloadHash}|${prevHash}`
  return sha256(input)
}

/**
 * Create a new chain entry (not yet persisted).
 * Call appendToChain() on the DB to persist.
 */
export function buildChainEntry(
  sequenceNum: number,
  eventType: ChainEventType,
  entityId: string,
  payload: unknown,
  prevHash: string,
): ChainEntry {
  const payloadJson = canonicalJSON(payload)
  const payloadHash = sha256(payloadJson)
  const chainHash = computeChainHash(
    sequenceNum,
    eventType,
    entityId,
    payloadHash,
    prevHash,
  )

  return {
    sequenceNum,
    eventType,
    entityId,
    payloadHash,
    prevHash,
    chainHash,
    payloadJson,
    createdAt: new Date().toISOString(),
  }
}

/**
 * Verify that a single chain entry's hash is correct.
 */
export function verifyChainEntry(entry: ChainEntry): boolean {
  const recomputedPayloadHash = sha256(entry.payloadJson)
  if (recomputedPayloadHash !== entry.payloadHash) return false

  const recomputedChainHash = computeChainHash(
    entry.sequenceNum,
    entry.eventType,
    entry.entityId,
    entry.payloadHash,
    entry.prevHash,
  )
  return recomputedChainHash === entry.chainHash
}

/**
 * Verify a sequence of chain entries are correctly linked.
 * Returns the index of the first broken entry, or -1 if all valid.
 */
export function verifyChainSequence(entries: ChainEntry[]): {
  valid: boolean
  brokenAt: number
  totalEntries: number
} {
  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i]!

    // Verify self-consistency
    if (!verifyChainEntry(entry)) {
      return { valid: false, brokenAt: entry.sequenceNum, totalEntries: entries.length }
    }

    // Verify linkage (only for consecutive sequence numbers)
    if (i === 0) {
      if (entry.sequenceNum === 1) {
        // First entry in global chain should reference genesis
        if (entry.prevHash !== GENESIS_HASH) {
          return { valid: false, brokenAt: entry.sequenceNum, totalEntries: entries.length }
        }
      }
    } else {
      const prevEntry = entries[i - 1]!
      // Only check linkage when sequence numbers are consecutive (no gap)
      // Non-consecutive entries come from a subset of the global chain
      // where intermediate entries for other entities were omitted
      if (entry.sequenceNum === prevEntry.sequenceNum + 1) {
        if (entry.prevHash !== prevEntry.chainHash) {
          return { valid: false, brokenAt: entry.sequenceNum, totalEntries: entries.length }
        }
      }
    }
  }

  return { valid: true, brokenAt: -1, totalEntries: entries.length }
}

export { GENESIS_HASH }

// ---------------------------------------------------------------------------
// Bet Commitments
// ---------------------------------------------------------------------------

/**
 * Generate a random nonce for bet commitments.
 */
export function generateBetNonce(): string {
  return crypto.randomBytes(16).toString('hex')
}

/**
 * Create a bet commitment hash.
 * commitmentHash = SHA-256(marketId | userAddress | option | slots | nonce)
 */
export function createBetCommitment(
  marketId: string,
  userAddress: string,
  option: number,
  slots: number,
  nonce: string,
): string {
  const input = `${marketId}|${userAddress}|${option}|${slots}|${nonce}`
  return sha256(input)
}

/**
 * Verify a bet commitment by recomputing the hash.
 */
export function verifyBetCommitment(
  commitmentHash: string,
  marketId: string,
  userAddress: string,
  option: number,
  slots: number,
  nonce: string,
): boolean {
  const recomputed = createBetCommitment(
    marketId,
    userAddress,
    option,
    slots,
    nonce,
  )
  return recomputed === commitmentHash
}

// ---------------------------------------------------------------------------
// Market Commitments
// ---------------------------------------------------------------------------

export interface MarketCommitmentData {
  pair: string
  question: string
  resolutionType: string
  resolutionTarget: number
  resolutionTargetHigh?: number | null
  closeDate: string
  endDate: string
  minBetQu: number
  maxSlots: number
  creatorAddress: string
}

/**
 * Create a market commitment hash from market parameters.
 * This binds the market terms cryptographically.
 */
export function createMarketCommitment(data: MarketCommitmentData): string {
  return hashCanonicalJSON(data)
}

// ---------------------------------------------------------------------------
// Oracle Attestations
// ---------------------------------------------------------------------------

export interface OracleAttestation {
  id: string
  marketId: string
  oracleSource: string
  pair: string
  price: number
  tick: number | null
  epoch: number | null
  sourceTimestamp: string
  attestationHash: string
  serverSignature: string
  createdAt: string
}

/**
 * Compute the attestation hash for an oracle price.
 * attestationHash = SHA-256(source | pair | price(8dp) | tick | epoch | timestamp)
 */
export function computeAttestationHash(
  oracleSource: string,
  pair: string,
  price: number,
  tick: number | null,
  epoch: number | null,
  sourceTimestamp: string,
): string {
  const input = `${oracleSource}|${pair}|${price.toFixed(8)}|${tick ?? 0}|${epoch ?? 0}|${sourceTimestamp}`
  return sha256(input)
}

/**
 * Create a signed oracle attestation.
 */
export function createOracleAttestation(
  marketId: string,
  oracleSource: string,
  pair: string,
  price: number,
  tick: number | null,
  epoch: number | null,
  sourceTimestamp: string,
  attestationKey: string,
): OracleAttestation {
  const attestationHash = computeAttestationHash(
    oracleSource,
    pair,
    price,
    tick,
    epoch,
    sourceTimestamp,
  )
  const serverSignature = hmacSha256(attestationHash, attestationKey)

  return {
    id: `att_${crypto.randomBytes(8).toString('hex')}`,
    marketId,
    oracleSource,
    pair,
    price,
    tick,
    epoch,
    sourceTimestamp,
    attestationHash,
    serverSignature,
    createdAt: new Date().toISOString(),
  }
}

/**
 * Verify an oracle attestation's integrity.
 */
export function verifyOracleAttestation(
  attestation: OracleAttestation,
  attestationKey: string,
): boolean {
  // Recompute attestation hash
  const recomputedHash = computeAttestationHash(
    attestation.oracleSource,
    attestation.pair,
    attestation.price,
    attestation.tick,
    attestation.epoch,
    attestation.sourceTimestamp,
  )
  if (recomputedHash !== attestation.attestationHash) return false

  // Verify HMAC signature
  const recomputedSig = hmacSha256(attestation.attestationHash, attestationKey)
  return recomputedSig === attestation.serverSignature
}

// ---------------------------------------------------------------------------
// Merkle Tree (for Solvency Proofs)
// ---------------------------------------------------------------------------

export interface MerkleLeaf {
  address: string
  balance: number
  leafHash: string
}

export interface MerkleTree {
  root: string
  leaves: MerkleLeaf[]
  levels: string[][]
}

export interface MerkleProof {
  address: string
  balance: number
  leafHash: string
  proof: Array<{ hash: string; position: 'left' | 'right' }>
  root: string
}

/**
 * Compute a Merkle leaf hash.
 * leaf = SHA-256(address | balance)
 */
export function computeLeafHash(address: string, balance: number): string {
  return sha256(`${address}|${balance}`)
}

/**
 * Build a Merkle tree from a sorted list of account balances.
 * Accounts are sorted by address for deterministic tree construction.
 */
export function buildMerkleTree(
  accounts: Array<{ address: string; balance: number }>,
): MerkleTree {
  // Sort by address for determinism
  const sorted = [...accounts].sort((a, b) => a.address.localeCompare(b.address))

  if (sorted.length === 0) {
    return {
      root: sha256('empty'),
      leaves: [],
      levels: [[]],
    }
  }

  // Build leaves
  const leaves: MerkleLeaf[] = sorted.map((acc) => ({
    address: acc.address,
    balance: acc.balance,
    leafHash: computeLeafHash(acc.address, acc.balance),
  }))

  // Build tree bottom-up
  const levels: string[][] = [leaves.map((l) => l.leafHash)]

  let currentLevel = levels[0]!
  while (currentLevel.length > 1) {
    const nextLevel: string[] = []
    for (let i = 0; i < currentLevel.length; i += 2) {
      const left = currentLevel[i]!
      const right = currentLevel[i + 1] ?? left // Duplicate last if odd
      nextLevel.push(sha256(left + right))
    }
    levels.push(nextLevel)
    currentLevel = nextLevel
  }

  return {
    root: currentLevel[0] ?? sha256('empty'),
    leaves,
    levels,
  }
}

/**
 * Generate a Merkle proof for a specific address.
 */
export function generateMerkleProof(
  tree: MerkleTree,
  address: string,
): MerkleProof | null {
  const leafIndex = tree.leaves.findIndex((l) => l.address === address)
  if (leafIndex === -1) return null

  const leaf = tree.leaves[leafIndex]!
  const proof: Array<{ hash: string; position: 'left' | 'right' }> = []

  let idx = leafIndex
  for (let level = 0; level < tree.levels.length - 1; level++) {
    const currentLevel = tree.levels[level]!
    const isRight = idx % 2 === 1
    const siblingIdx = isRight ? idx - 1 : idx + 1

    if (siblingIdx < currentLevel.length) {
      proof.push({
        hash: currentLevel[siblingIdx]!,
        position: isRight ? 'left' : 'right',
      })
    } else {
      // Odd node, paired with itself
      proof.push({
        hash: currentLevel[idx]!,
        position: 'right',
      })
    }

    idx = Math.floor(idx / 2)
  }

  return {
    address: leaf.address,
    balance: leaf.balance,
    leafHash: leaf.leafHash,
    proof,
    root: tree.root,
  }
}

/**
 * Verify a Merkle proof.
 */
export function verifyMerkleProof(proof: MerkleProof): boolean {
  let currentHash = proof.leafHash

  // Verify leaf hash
  const recomputedLeaf = computeLeafHash(proof.address, proof.balance)
  if (recomputedLeaf !== proof.leafHash) return false

  // Walk up the tree
  for (const step of proof.proof) {
    if (step.position === 'left') {
      currentHash = sha256(step.hash + currentHash)
    } else {
      currentHash = sha256(currentHash + step.hash)
    }
  }

  return currentHash === proof.root
}

// ---------------------------------------------------------------------------
// Resolution Proof Package
// ---------------------------------------------------------------------------

export interface ResolutionProofPackage {
  version: number
  marketId: string
  market: {
    pair: string
    question: string
    resolutionType: string
    resolutionTarget: number
    resolutionTargetHigh: number | null
    closeDate: string
    endDate: string
    minBetQu: number
    maxSlots: number
    creatorAddress: string
    commitmentHash: string
  }
  resolution: {
    resolutionPrice: number
    winningOption: number
    resolvedAt: string
    resolutionMethod: string // 'multi_oracle_median'
  }
  oracleAttestations: OracleAttestation[]
  payoutSummary: {
    totalPool: number
    winnerSlots: number
    loserSlots: number
    payoutPerSlot: number
    totalPaidOut: number
    feeBreakdown: {
      burn: number
      shareholder: number
      operator: number
      oracle: number
      total: number
    }
  }
  chainEntries: ChainEntry[]
  onChainTxIds: {
    issueBet?: string
    joinBets: Array<{ betId: string; txId: string }>
    publishResult?: string
  }
  proofHash: string // SHA-256 of this entire package (minus proofHash itself)
  generatedAt: string
}

/**
 * Compute the proof hash for a resolution package.
 * Hashes everything except the proofHash field itself.
 */
export function computeResolutionProofHash(
  pkg: Omit<ResolutionProofPackage, 'proofHash'>,
): string {
  return hashCanonicalJSON(pkg)
}

/**
 * Verify a resolution proof package's integrity.
 */
export function verifyResolutionProofPackage(
  pkg: ResolutionProofPackage,
  attestationKey?: string,
): {
  valid: boolean
  checks: Array<{ name: string; passed: boolean; detail?: string }>
} {
  const checks: Array<{ name: string; passed: boolean; detail?: string }> = []

  // 1. Verify proof hash
  const { proofHash: _, ...pkgWithoutHash } = pkg
  const recomputedProofHash = hashCanonicalJSON(pkgWithoutHash)
  checks.push({
    name: 'proof_hash',
    passed: recomputedProofHash === pkg.proofHash,
    detail: recomputedProofHash === pkg.proofHash
      ? 'Package hash matches'
      : `Expected ${pkg.proofHash}, got ${recomputedProofHash}`,
  })

  // 2. Verify market commitment hash
  const marketCommitment = createMarketCommitment({
    pair: pkg.market.pair,
    question: pkg.market.question,
    resolutionType: pkg.market.resolutionType,
    resolutionTarget: pkg.market.resolutionTarget,
    resolutionTargetHigh: pkg.market.resolutionTargetHigh ?? null,
    closeDate: pkg.market.closeDate,
    endDate: pkg.market.endDate,
    minBetQu: pkg.market.minBetQu,
    maxSlots: pkg.market.maxSlots,
    creatorAddress: pkg.market.creatorAddress,
  })
  checks.push({
    name: 'market_commitment',
    passed: marketCommitment === pkg.market.commitmentHash,
    detail: marketCommitment === pkg.market.commitmentHash
      ? 'Market parameters match commitment'
      : 'Market commitment hash mismatch!',
  })

  // 3. Verify oracle attestations
  if (attestationKey) {
    for (const att of pkg.oracleAttestations) {
      const valid = verifyOracleAttestation(att, attestationKey)
      checks.push({
        name: `oracle_${att.oracleSource}`,
        passed: valid,
        detail: valid
          ? `${att.oracleSource}: $${att.price}`
          : `${att.oracleSource}: HMAC verification failed`,
      })
    }
  }

  // 4. Verify median price matches resolution price
  if (pkg.oracleAttestations.length > 0) {
    const prices = pkg.oracleAttestations.map((a) => a.price).sort((a, b) => a - b)
    const mid = Math.floor(prices.length / 2)
    const median =
      prices.length % 2 === 0
        ? (prices[mid - 1]! + prices[mid]!) / 2
        : prices[mid]!
    const priceMatch = Math.abs(median - pkg.resolution.resolutionPrice) < 0.01
    checks.push({
      name: 'median_price',
      passed: priceMatch,
      detail: priceMatch
        ? `Median $${median} matches resolution price`
        : `Median $${median} != resolution price $${pkg.resolution.resolutionPrice}`,
    })
  }

  // 5. Verify winner determination
  let expectedWinner: number
  switch (pkg.market.resolutionType) {
    case 'price_above':
      expectedWinner =
        pkg.resolution.resolutionPrice >= pkg.market.resolutionTarget ? 0 : 1
      break
    case 'price_below':
      expectedWinner =
        pkg.resolution.resolutionPrice <= pkg.market.resolutionTarget ? 0 : 1
      break
    case 'price_range':
      expectedWinner =
        pkg.resolution.resolutionPrice >= pkg.market.resolutionTarget &&
        (pkg.market.resolutionTargetHigh === null ||
          pkg.resolution.resolutionPrice <= pkg.market.resolutionTargetHigh)
          ? 0
          : 1
      break
    default:
      expectedWinner = 1
  }
  checks.push({
    name: 'winner_determination',
    passed: expectedWinner === pkg.resolution.winningOption,
    detail:
      expectedWinner === pkg.resolution.winningOption
        ? `Winner option ${pkg.resolution.winningOption} is correct`
        : `Expected winner ${expectedWinner}, got ${pkg.resolution.winningOption}`,
  })

  // 6. Verify chain entries are self-consistent
  const chainResult = verifyChainSequence(pkg.chainEntries)
  checks.push({
    name: 'chain_integrity',
    passed: chainResult.valid,
    detail: chainResult.valid
      ? `${chainResult.totalEntries} chain entries verified`
      : `Chain broken at sequence ${chainResult.brokenAt}`,
  })

  const allPassed = checks.every((c) => c.passed)
  return { valid: allPassed, checks }
}
