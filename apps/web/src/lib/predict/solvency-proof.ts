/**
 * QPredict Solvency Proof System
 *
 * Proves that the platform's on-chain balance >= sum of all user balances.
 * Uses Merkle trees for efficient, privacy-preserving proof generation.
 *
 * Flow:
 * 1. Collect all user account balances from SQLite
 * 2. Build Merkle tree from sorted account data
 * 3. Fetch on-chain balance of the platform master address
 * 4. Compare: on-chain >= total user balances
 * 5. Store proof (root, totals, leaf hashes) in DB
 * 6. Record chain entry for the solvency proof
 *
 * Users can:
 * - Verify their balance is included in the Merkle tree
 * - Verify the Merkle root matches the stored proof
 * - Independently check the on-chain balance via RPC
 */

import crypto from 'crypto'
import {
  buildMerkleTree,
  generateMerkleProof,
  buildChainEntry,
  GENESIS_HASH,
  type MerkleTree,
  type MerkleProof,
} from './provably-fair'
import { getMarketDB, type SolvencyProofRow } from './market-db'
import { getBalance, getCurrentTick } from '@/lib/qubic/quottery-client'

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

function getPlatformAddress(): string {
  const addr = process.env.MASTER_IDENTITY
  if (!addr) throw new Error('MASTER_IDENTITY not set in environment')
  return addr
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SolvencyProofResult {
  success: boolean
  proof?: {
    id: string
    merkleRoot: string
    totalUserBalance: number
    onChainBalance: number
    isSolvent: boolean
    accountCount: number
    tick: number
    epoch: number
  }
  error?: string
}

export interface UserInclusionProof {
  address: string
  balance: number
  merkleProof: MerkleProof
  latestSolvencyProof: {
    merkleRoot: string
    totalUserBalance: number
    onChainBalance: number
    isSolvent: boolean
    createdAt: string
  }
}

// ---------------------------------------------------------------------------
// Solvency Proof Generation
// ---------------------------------------------------------------------------

/**
 * Generate a solvency proof:
 * 1. Get all account balances
 * 2. Build Merkle tree
 * 3. Fetch on-chain balance
 * 4. Store proof in DB + chain entry
 */
export async function generateSolvencyProof(): Promise<SolvencyProofResult> {
  const db = getMarketDB()

  // 1. Get all accounts
  const accounts = db.getAllAccounts()
  const accountData = accounts.map((a) => ({
    address: a.address,
    balance: a.balanceQu,
  }))

  // 2. Build Merkle tree
  const tree = buildMerkleTree(accountData)
  const totalUserBalance = accountData.reduce((sum, a) => sum + a.balance, 0)

  // 3. Fetch on-chain balance
  let onChainBalance: bigint
  let tick = 0
  let epoch = 0

  try {
    const platformAddr = getPlatformAddress()
    onChainBalance = await getBalance(platformAddr)

    const tickInfo = await getCurrentTick()
    tick = tickInfo.tick
    epoch = tickInfo.epoch
  } catch (err) {
    return {
      success: false,
      error: `Failed to fetch on-chain data: ${err instanceof Error ? err.message : 'Unknown'}`,
    }
  }

  // 4. Compare
  const isSolvent = onChainBalance >= BigInt(totalUserBalance)

  // 5. Store proof
  const proofId = `sol_${crypto.randomBytes(8).toString('hex')}`
  const leafHashesJson = JSON.stringify(tree.leaves.map((l) => ({
    address: l.address,
    balance: l.balance,
    hash: l.leafHash,
  })))

  db.insertSolvencyProof({
    id: proofId,
    merkleRoot: tree.root,
    totalUserBalance,
    onChainBalance: Number(onChainBalance),
    isSolvent: isSolvent ? 1 : 0,
    accountCount: accounts.length,
    tick,
    epoch,
    leafHashesJson,
    createdAt: new Date().toISOString(),
  })

  // 6. Chain entry
  const latest = db.getLatestChainEntry()
  const prevHash = latest?.chainHash ?? GENESIS_HASH
  const seqNum = (latest?.sequenceNum ?? 0) + 1

  const chainEntry = buildChainEntry(seqNum, 'solvency_proof', proofId, {
    proofId,
    merkleRoot: tree.root,
    totalUserBalance,
    onChainBalance: Number(onChainBalance),
    isSolvent,
    accountCount: accounts.length,
    tick,
    epoch,
  }, prevHash)
  db.appendChainEntry(chainEntry)

  return {
    success: true,
    proof: {
      id: proofId,
      merkleRoot: tree.root,
      totalUserBalance,
      onChainBalance: Number(onChainBalance),
      isSolvent,
      accountCount: accounts.length,
      tick,
      epoch,
    },
  }
}

// ---------------------------------------------------------------------------
// User Inclusion Proof
// ---------------------------------------------------------------------------

/**
 * Generate a proof that a specific user's balance is included in the latest
 * solvency proof's Merkle tree.
 */
export function getUserInclusionProof(
  address: string,
): UserInclusionProof | null {
  const db = getMarketDB()

  // Get latest solvency proof
  const latestProof = db.getLatestSolvencyProof()
  if (!latestProof) return null

  // Get user account
  const account = db.getAccount(address)
  if (!account) return null

  // Rebuild Merkle tree from stored leaf hashes
  const leaves = JSON.parse(latestProof.leafHashesJson) as Array<{
    address: string
    balance: number
    hash: string
  }>

  // Build tree from the same data
  const accounts = leaves.map((l) => ({ address: l.address, balance: l.balance }))
  const tree = buildMerkleTree(accounts)

  // Generate proof for this address
  const proof = generateMerkleProof(tree, address)
  if (!proof) return null

  return {
    address,
    balance: account.balanceQu,
    merkleProof: proof,
    latestSolvencyProof: {
      merkleRoot: latestProof.merkleRoot,
      totalUserBalance: latestProof.totalUserBalance,
      onChainBalance: latestProof.onChainBalance,
      isSolvent: latestProof.isSolvent === 1,
      createdAt: latestProof.createdAt,
    },
  }
}

// ---------------------------------------------------------------------------
// Query Functions
// ---------------------------------------------------------------------------

/**
 * Get the latest solvency proof.
 */
export function getLatestSolvencyProof(): SolvencyProofRow | null {
  return getMarketDB().getLatestSolvencyProof()
}

/**
 * Get recent solvency proofs.
 */
export function getSolvencyProofs(limit: number = 20): SolvencyProofRow[] {
  return getMarketDB().getSolvencyProofs(limit)
}
