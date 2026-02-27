#!/usr/bin/env node
/**
 * MARKET ENGINE — Unified Background Service
 *
 * Replaces: ESCROW_MONITOR.mjs, MARKET_RESOLVER.mjs, DEPOSIT_DETECTOR.mjs
 *
 * Combines all background operations into a single service with two cycles:
 *
 * Fast Cycle (every 10s):
 *   1. checkDeposits()         — Escrow Deposit Detection
 *   2. processJoinBets()       — joinBet TX on Quottery SC
 *   3. closeExpiredBetting()   — Close betting after close_date
 *   4. resolveExpiredMarkets() — Auto-resolve via Oracle Adapters (Price/Sports/AI/Creator)
 *   5. checkPayouts()          — Payout detection after resolution
 *   6. processSweeps()         — Sweep winnings to users
 *   7. handleExpiredEscrows()  — Expire timed-out escrows
 *   8. autoRefundExpired()     — Auto-refund unresolved Custom/AI markets
 *
 * Slow Cycle (every 6h):
 *   9. createTrendingMarkets() — AI scans news, auto-creates markets
 *
 * Usage:
 *   node MARKET_ENGINE.mjs                 # Continuous
 *   node MARKET_ENGINE.mjs --once          # Single cycle then exit
 *   node MARKET_ENGINE.mjs --status        # Show stats
 *   node MARKET_ENGINE.mjs --dry-run       # No TX, only log
 */

import { createRequire } from 'module'
import { readFileSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const require = createRequire(import.meta.url)
const __dirname = dirname(fileURLToPath(import.meta.url))

// ---------------------------------------------------------------------------
// Env
// ---------------------------------------------------------------------------

const envPath = resolve(__dirname, '../../../../.env')
try {
  const envContent = readFileSync(envPath, 'utf-8')
  for (const line of envContent.split('\n')) {
    const match = line.match(/^([^#=]+)=(.*)$/)
    if (match) {
      process.env[match[1].trim()] = match[2].trim()
    }
  }
} catch {
  // Try alternate path
  try {
    const envContent2 = readFileSync(resolve(__dirname, '../../../.env'), 'utf-8')
    for (const line of envContent2.split('\n')) {
      const match = line.match(/^([^#=]+)=(.*)$/)
      if (match) {
        process.env[match[1].trim()] = match[2].trim()
      }
    }
  } catch {
    console.error('[Engine] Warning: Could not read .env file')
  }
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const FAST_CYCLE_MS = Number(process.env.ENGINE_FAST_CYCLE_MS) || 10_000
const SLOW_CYCLE_MS = Number(process.env.ENGINE_SLOW_CYCLE_MS) || 6 * 60 * 60 * 1000 // 6h
const RPC_URL = process.env.QUBIC_RPC_URL || 'https://rpc.qubic.org/v1'
const ESCROW_MASTER_KEY = process.env.ESCROW_MASTER_KEY
const DRY_RUN = process.argv.includes('--dry-run')

const RPC_ENDPOINTS = [
  'https://rpc.qubic.org/v1',
  'https://rpc.qubic.li/v1',
  'https://rpc.qubic.network/v1',
]
let _rpcIdx = 0

// ---------------------------------------------------------------------------
// RPC Helpers
// ---------------------------------------------------------------------------

async function rpc(endpoint, options = {}) {
  for (let i = 0; i < RPC_ENDPOINTS.length; i++) {
    const base = RPC_ENDPOINTS[(_rpcIdx + i) % RPC_ENDPOINTS.length]
    try {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 10000)
      const res = await fetch(`${base}${endpoint}`, {
        ...options,
        headers: { 'Content-Type': 'application/json', ...options.headers },
        signal: controller.signal,
      })
      clearTimeout(timeout)
      if (!res.ok) throw new Error(`RPC ${res.status}`)
      _rpcIdx = (_rpcIdx + i) % RPC_ENDPOINTS.length
      return res.json()
    } catch {
      // try next endpoint
    }
  }
  throw new Error('All RPC endpoints failed')
}

async function getBalance(address) {
  try {
    const data = await rpc(`/balances/${address}`)
    if (data.balance && typeof data.balance === 'object') {
      return BigInt(data.balance.balance)
    }
    return 0n
  } catch {
    return 0n
  }
}

async function getCurrentTick() {
  const data = await rpc('/tick-info')
  const info = data.tickInfo || data
  return { tick: info.tick, epoch: info.epoch }
}

// ---------------------------------------------------------------------------
// Database (lazy import)
// ---------------------------------------------------------------------------

let _db = null
function getDB() {
  if (!_db) {
    const { getMarketDB } = require('../src/lib/predict/market-db.ts')
    _db = getMarketDB()
  }
  return _db
}

// ---------------------------------------------------------------------------
// Stats Tracking
// ---------------------------------------------------------------------------

const stats = {
  startedAt: new Date().toISOString(),
  fastCycles: 0,
  slowCycles: 0,
  depositsDetected: 0,
  joinBetsProcessed: 0,
  marketsClosed: 0,
  marketsResolved: 0,
  payoutsDetected: 0,
  sweepsProcessed: 0,
  escrowsExpired: 0,
  autoRefunds: 0,
  trendingMarketsCreated: 0,
  errors: 0,
}

// ---------------------------------------------------------------------------
// Phase 1: Deposit Detection (from ESCROW_MONITOR)
// ---------------------------------------------------------------------------

async function checkDeposits() {
  const db = getDB()
  const escrows = db.getEscrowsByStatus('awaiting_deposit')
  if (escrows.length === 0) return 0

  let detected = 0

  for (const escrow of escrows) {
    // Check if expired
    if (new Date(escrow.expiresAt) <= new Date()) {
      db.markEscrowExpired(escrow.id)
      db.updateEscrowKeyStatus(escrow.id, 'archived')
      db.setBetStatus(escrow.betId, 'refunded')
      stats.escrowsExpired++
      continue
    }

    try {
      const balance = await getBalance(escrow.escrowAddress)
      if (balance >= BigInt(escrow.expectedAmountQu)) {
        db.recordEscrowDeposit(escrow.id, Number(balance))
        console.log(`  [DEPOSIT] ${escrow.id}: ${Number(balance).toLocaleString()} QU`)
        detected++
        stats.depositsDetected++
      }
    } catch (err) {
      console.error(`  [ERROR] Deposit check ${escrow.id}: ${err.message}`)
      stats.errors++
    }
  }

  return detected
}

// ---------------------------------------------------------------------------
// Phase 2: JoinBet Execution (from ESCROW_MONITOR)
// ---------------------------------------------------------------------------

async function processJoinBets() {
  const db = getDB()
  const escrows = db.getEscrowsByStatus('deposit_detected')
  if (escrows.length === 0) return 0

  let processed = 0

  for (const escrow of escrows) {
    try {
      const market = db.getMarket(escrow.marketId)
      if (!market || !market.quotteryBetId) continue

      const keyEntry = db.getEscrowKey(escrow.id)
      if (!keyEntry) continue

      const { decryptSeed, deriveMasterKey } = require('../src/lib/predict/key-vault.ts')
      const masterKey = deriveMasterKey(ESCROW_MASTER_KEY)
      const seed = decryptSeed({
        ciphertext: keyEntry.encryptedSeed,
        iv: keyEntry.iv,
        authTag: keyEntry.authTag,
      }, masterKey)

      db.updateEscrowStatus(escrow.id, 'joining_sc')

      if (DRY_RUN) {
        console.log(`  [DRY-RUN] Would joinBet for ${escrow.id}`)
        db.updateEscrowStatus(escrow.id, 'deposit_detected')
        continue
      }

      const { joinBet } = require('../src/lib/qubic/quottery-client.ts')
      const result = await joinBet(
        seed,
        {
          betId: market.quotteryBetId,
          numberOfSlot: escrow.slots,
          option: escrow.option,
        },
        BigInt(escrow.expectedAmountQu),
      )

      if (result.success) {
        db.recordEscrowJoinBet(escrow.id, result.txId, result.targetTick)
        db.confirmBet(escrow.betId, result.txId)
        console.log(`  [JOIN] ${escrow.id}: TX ${result.txId}`)
        processed++
        stats.joinBetsProcessed++
      } else {
        db.updateEscrowStatus(escrow.id, 'deposit_detected')
        console.error(`  [FAIL] ${escrow.id}: ${result.error}`)
      }
    } catch (err) {
      try { db.updateEscrowStatus(escrow.id, 'deposit_detected') } catch {}
      console.error(`  [ERROR] JoinBet ${escrow.id}: ${err.message}`)
      stats.errors++
    }
  }

  return processed
}

// ---------------------------------------------------------------------------
// Phase 3: Close Expired Betting (from MARKET_RESOLVER)
// ---------------------------------------------------------------------------

function closeExpiredBetting() {
  const db = getDB()
  const closing = db.getClosingMarkets()

  for (const market of closing) {
    db.updateMarketStatus(market.id, 'closed')
    console.log(`  [CLOSE] ${market.id}: ${market.question}`)
    stats.marketsClosed++
  }

  return closing.length
}

// ---------------------------------------------------------------------------
// Phase 4: Resolve Expired Markets via Oracle Adapters (NEW)
// ---------------------------------------------------------------------------

async function resolveExpiredMarkets() {
  const db = getDB()
  const expired = db.getExpiredMarkets()
  if (expired.length === 0) return 0

  let resolved = 0

  // Dynamic import for oracle adapters (TypeScript)
  let tryResolveMarket
  try {
    const mod = require('../src/lib/predict/oracle-adapters.ts')
    tryResolveMarket = mod.tryResolveMarket
  } catch (err) {
    console.error(`  [ERROR] Cannot load oracle-adapters: ${err.message}`)
    return 0
  }

  // Also load market-manager for resolution logic
  let resolveMarket
  try {
    const mod = require('../src/lib/predict/market-manager.ts')
    resolveMarket = mod.resolveMarket
  } catch (err) {
    console.error(`  [ERROR] Cannot load market-manager: ${err.message}`)
    return 0
  }

  for (const market of expired) {
    try {
      if (DRY_RUN) {
        console.log(`  [DRY-RUN] Would resolve ${market.id} (${market.marketType}): ${market.question}`)
        continue
      }

      console.log(`  [RESOLVE] Attempting ${market.id} (${market.marketType}): ${market.question}`)

      // Use oracle adapter to get result
      const oracleResult = await tryResolveMarket(market)

      if (!oracleResult) {
        // AI markets: record failed attempt
        if (market.marketType === 'ai') {
          db.recordAiResolutionAttempt(market.id, null)
          console.log(`    No AI consensus for ${market.id} (attempt ${market.aiResolutionAttempts + 1}/3)`)
        } else {
          console.log(`    No oracle result for ${market.id}`)
        }
        continue
      }

      // Resolve via market manager
      const result = await resolveMarket({
        marketId: market.id,
        currentPrice: market.marketType === 'price'
          ? (oracleResult.proof.data?.medianPrice ?? undefined)
          : undefined,
        winningOption: oracleResult.winningOption,
        oracleProof: oracleResult.proof,
      })

      if (result.success) {
        const winLabel = market.options?.[oracleResult.winningOption] ?? `Option ${oracleResult.winningOption}`
        console.log(`    Resolved: ${winLabel} (${result.winners} winners, ${result.losers} losers)`)
        resolved++
        stats.marketsResolved++
      } else {
        console.error(`    Resolution failed: ${result.error}`)
      }
    } catch (err) {
      console.error(`  [ERROR] Resolving ${market.id}: ${err.message}`)
      stats.errors++
    }
  }

  return resolved
}

// ---------------------------------------------------------------------------
// Phase 5: Payout Detection (from ESCROW_MONITOR)
// ---------------------------------------------------------------------------

async function checkPayouts() {
  const db = getDB()
  const escrows = db.getEscrowsByStatus('active_in_sc')
  if (escrows.length === 0) return 0

  let detected = 0

  for (const escrow of escrows) {
    const market = db.getMarket(escrow.marketId)
    if (!market || market.status !== 'resolved') continue

    // Check if this bet won
    if (market.winningOption !== escrow.option) {
      db.markEscrowLost(escrow.id)
      db.updateEscrowKeyStatus(escrow.id, 'archived')
      continue
    }

    try {
      const balance = await getBalance(escrow.escrowAddress)
      if (balance > 0n) {
        db.recordEscrowPayout(escrow.id, Number(balance))
        console.log(`  [PAYOUT] ${escrow.id}: ${Number(balance).toLocaleString()} QU`)
        detected++
        stats.payoutsDetected++
      }
    } catch (err) {
      console.error(`  [ERROR] Payout check ${escrow.id}: ${err.message}`)
      stats.errors++
    }
  }

  return detected
}

// ---------------------------------------------------------------------------
// Phase 6: Sweep Winnings to Users (from ESCROW_MONITOR)
// ---------------------------------------------------------------------------

async function processSweeps() {
  const db = getDB()
  const escrows = db.getEscrowsByStatus('won_awaiting_sweep')
  if (escrows.length === 0) return 0

  let swept = 0

  for (const escrow of escrows) {
    try {
      const keyEntry = db.getEscrowKey(escrow.id)
      if (!keyEntry || keyEntry.status !== 'active') continue

      const { decryptSeed, deriveMasterKey } = require('../src/lib/predict/key-vault.ts')
      const masterKey = deriveMasterKey(ESCROW_MASTER_KEY)
      const seed = decryptSeed({
        ciphertext: keyEntry.encryptedSeed,
        iv: keyEntry.iv,
        authTag: keyEntry.authTag,
      }, masterKey)

      const balance = await getBalance(escrow.escrowAddress)
      if (balance <= 1000n) continue

      if (DRY_RUN) {
        console.log(`  [DRY-RUN] Would sweep ${Number(balance)} QU from ${escrow.id}`)
        continue
      }

      const sweepAmount = balance - 1000n // reserve for TX fee

      const qubicLib = require('@qubic-lib/qubic-ts-library').default
      const { QubicHelper, QubicTransaction } = qubicLib

      const helper = new QubicHelper()
      const { tick } = await getCurrentTick()
      const targetTick = tick + 5

      const txBytes = await helper.createTransaction(
        seed,
        escrow.userPayoutAddress,
        Number(sweepAmount),
        targetTick,
      )

      const tx = new QubicTransaction()
      const encoded = tx.encodeTransactionToBase64(txBytes)

      await rpc('/broadcast-transaction', {
        method: 'POST',
        body: JSON.stringify({ encodedTransaction: encoded }),
      })

      const txId = `sweep_${Date.now().toString(36)}`
      db.recordEscrowSweep(escrow.id, txId, targetTick)
      db.updateEscrowKeyStatus(escrow.id, 'swept')
      db.resolveBet(escrow.betId, true, Number(sweepAmount))

      console.log(`  [SWEEP] ${escrow.id}: ${Number(sweepAmount).toLocaleString()} QU -> ${escrow.userPayoutAddress.slice(0, 12)}...`)
      swept++
      stats.sweepsProcessed++
    } catch (err) {
      console.error(`  [ERROR] Sweep ${escrow.id}: ${err.message}`)
      stats.errors++
    }
  }

  return swept
}

// ---------------------------------------------------------------------------
// Phase 7: Auto-Refund Expired Markets (NEW)
// ---------------------------------------------------------------------------

async function autoRefundExpired() {
  const db = getDB()
  const markets = db.getMarketsNeedingAutoRefund()
  if (markets.length === 0) return 0

  let refunded = 0
  let cancelMarket
  try {
    const mod = require('../src/lib/predict/market-manager.ts')
    cancelMarket = mod.cancelMarket
  } catch {
    return 0
  }

  for (const market of markets) {
    try {
      if (DRY_RUN) {
        console.log(`  [DRY-RUN] Would auto-refund ${market.id}: ${market.question}`)
        continue
      }

      console.log(`  [REFUND] Auto-refunding ${market.id}: ${market.question}`)
      const result = await cancelMarket(market.id)
      if (result.success) {
        refunded++
        stats.autoRefunds++
      }
    } catch (err) {
      console.error(`  [ERROR] Auto-refund ${market.id}: ${err.message}`)
      stats.errors++
    }
  }

  return refunded
}

// ---------------------------------------------------------------------------
// Phase 8: Trending Market Auto-Creator (NEW — Slow Cycle)
// ---------------------------------------------------------------------------

async function createTrendingMarkets() {
  let trendingCreator, createMarket
  try {
    const trendingMod = require('../src/lib/predict/trending-creator.ts')
    trendingCreator = trendingMod.createTrendingMarkets
    const managerMod = require('../src/lib/predict/market-manager.ts')
    createMarket = managerMod.createMarket
  } catch (err) {
    console.error(`  [ERROR] Cannot load trending-creator: ${err.message}`)
    return 0
  }

  const db = getDB()

  // Get existing market questions for dedup
  const activeMarkets = db.listMarkets({ status: 'active' })
  const closedMarkets = db.listMarkets({ status: 'closed' })
  const existingQuestions = [...activeMarkets, ...closedMarkets].map((m) => m.question)

  console.log(`  [TRENDING] Scanning news (${existingQuestions.length} existing markets)...`)

  const result = await trendingCreator(existingQuestions, DRY_RUN)

  console.log(`  [TRENDING] Scanned ${result.scanned} articles, proposed ${result.proposed}, unique ${result.proposals.length}`)

  if (result.errors.length > 0) {
    for (const err of result.errors) {
      console.error(`    Error: ${err}`)
    }
  }

  if (DRY_RUN || result.proposals.length === 0) {
    if (result.proposals.length > 0) {
      console.log(`  [DRY-RUN] Would create ${result.proposals.length} markets:`)
      for (const p of result.proposals) {
        console.log(`    - ${p.question} (${p.marketType}, ${p.category})`)
      }
    }
    return 0
  }

  // Create markets from proposals
  const { getPlatformAddress } = require('../src/lib/predict/custody.ts')
  const platformAddress = getPlatformAddress()
  let created = 0

  for (const proposal of result.proposals) {
    try {
      const marketResult = await createMarket({
        pair: proposal.pair || 'btc/usdt',
        question: proposal.question,
        resolutionType: proposal.resolutionType || 'price_above',
        resolutionTarget: proposal.resolutionTarget || 0,
        closeDate: proposal.closeDate,
        endDate: proposal.endDate,
        creatorAddress: platformAddress,
        oracleFeeBps: 0,
        marketType: proposal.marketType || 'ai',
        options: proposal.options,
        category: proposal.category || 'other',
        createdBy: 'trending_agent',
      })

      if (marketResult.success) {
        console.log(`    Created: ${proposal.question} (${marketResult.market?.id})`)
        created++
        stats.trendingMarketsCreated++
      } else {
        console.error(`    Failed: ${marketResult.error}`)
      }
    } catch (err) {
      console.error(`    Error creating market: ${err.message}`)
      stats.errors++
    }
  }

  return created
}

// ---------------------------------------------------------------------------
// Status Report
// ---------------------------------------------------------------------------

function showStatus() {
  const db = getDB()

  const escrowCounts = {
    awaitingDeposit: db.getEscrowsByStatus('awaiting_deposit').length,
    depositDetected: db.getEscrowsByStatus('deposit_detected').length,
    activeInSC: db.getEscrowsByStatus('active_in_sc').length,
    wonAwaiting: db.getEscrowsByStatus('won_awaiting_sweep').length,
    swept: db.getEscrowsByStatus('swept').length,
    lost: db.getEscrowsByStatus('lost').length,
    expired: db.getEscrowsByStatus('expired').length,
  }

  const marketCounts = {
    active: db.listMarkets({ status: 'active' }).length,
    closed: db.listMarkets({ status: 'closed' }).length,
    resolved: db.listMarkets({ status: 'resolved' }).length,
    cancelled: db.listMarkets({ status: 'cancelled' }).length,
  }

  console.log('\n=== MARKET ENGINE STATUS ===')
  console.log(`Running since: ${stats.startedAt}`)
  console.log(`Fast cycles:   ${stats.fastCycles}`)
  console.log(`Slow cycles:   ${stats.slowCycles}`)
  console.log()
  console.log('--- Markets ---')
  console.log(`  Active:     ${marketCounts.active}`)
  console.log(`  Closed:     ${marketCounts.closed}`)
  console.log(`  Resolved:   ${marketCounts.resolved}`)
  console.log(`  Cancelled:  ${marketCounts.cancelled}`)
  console.log()
  console.log('--- Escrows ---')
  console.log(`  Awaiting:   ${escrowCounts.awaitingDeposit}`)
  console.log(`  Detected:   ${escrowCounts.depositDetected}`)
  console.log(`  Active SC:  ${escrowCounts.activeInSC}`)
  console.log(`  Won (pend): ${escrowCounts.wonAwaiting}`)
  console.log(`  Swept:      ${escrowCounts.swept}`)
  console.log(`  Lost:       ${escrowCounts.lost}`)
  console.log(`  Expired:    ${escrowCounts.expired}`)
  console.log()
  console.log('--- Session Stats ---')
  console.log(`  Deposits:   ${stats.depositsDetected}`)
  console.log(`  JoinBets:   ${stats.joinBetsProcessed}`)
  console.log(`  Resolved:   ${stats.marketsResolved}`)
  console.log(`  Sweeps:     ${stats.sweepsProcessed}`)
  console.log(`  Refunds:    ${stats.autoRefunds}`)
  console.log(`  Trending:   ${stats.trendingMarketsCreated}`)
  console.log(`  Errors:     ${stats.errors}`)
  console.log()
}

// ---------------------------------------------------------------------------
// Main Loop
// ---------------------------------------------------------------------------

async function runFastCycle() {
  const start = Date.now()
  stats.fastCycles++

  try {
    const deposits = await checkDeposits()
    const joined = await processJoinBets()
    const closed = closeExpiredBetting()
    const resolved = await resolveExpiredMarkets()
    const payouts = await checkPayouts()
    const swept = await processSweeps()
    const refunded = await autoRefundExpired()

    const elapsed = Date.now() - start
    const total = deposits + joined + closed + resolved + payouts + swept + refunded

    if (total > 0) {
      console.log(
        `[Fast #${stats.fastCycles}] ${elapsed}ms — ` +
        `dep:${deposits} join:${joined} close:${closed} res:${resolved} ` +
        `pay:${payouts} sweep:${swept} refund:${refunded}`
      )
    }
  } catch (err) {
    console.error(`[Fast #${stats.fastCycles} ERROR] ${err.message}`)
    stats.errors++
  }
}

async function runSlowCycle() {
  const start = Date.now()
  stats.slowCycles++

  console.log(`\n[Slow #${stats.slowCycles}] Running trending market scan...`)

  try {
    const created = await createTrendingMarkets()
    const elapsed = Date.now() - start
    console.log(`[Slow #${stats.slowCycles}] ${elapsed}ms — trending:${created}\n`)
  } catch (err) {
    console.error(`[Slow #${stats.slowCycles} ERROR] ${err.message}`)
    stats.errors++
  }
}

async function main() {
  const args = process.argv.slice(2)

  if (!ESCROW_MASTER_KEY) {
    console.error('ERROR: ESCROW_MASTER_KEY must be set in .env')
    process.exit(1)
  }

  if (args.includes('--status')) {
    showStatus()
    process.exit(0)
  }

  if (args.includes('--once')) {
    console.log('[Engine] Running single cycle...')
    await runFastCycle()
    await runSlowCycle()
    showStatus()
    process.exit(0)
  }

  // Continuous mode
  console.log('=== MARKET ENGINE ===')
  console.log(`  Fast cycle:  ${FAST_CYCLE_MS}ms`)
  console.log(`  Slow cycle:  ${SLOW_CYCLE_MS}ms (${(SLOW_CYCLE_MS / 3600000).toFixed(1)}h)`)
  console.log(`  RPC:         ${RPC_URL}`)
  console.log(`  Dry run:     ${DRY_RUN}`)
  console.log()

  showStatus()

  // Run fast cycle immediately
  await runFastCycle()

  // Schedule fast cycle
  setInterval(runFastCycle, FAST_CYCLE_MS)

  // Schedule slow cycle (trending markets)
  // Run first slow cycle after 5 minutes (let system stabilize)
  setTimeout(async () => {
    await runSlowCycle()
    setInterval(runSlowCycle, SLOW_CYCLE_MS)
  }, 5 * 60 * 1000)

  // Status report every 10 minutes
  setInterval(() => {
    const ts = new Date().toISOString().slice(0, 19)
    console.log(
      `[${ts}] cycles:${stats.fastCycles} res:${stats.marketsResolved} ` +
      `dep:${stats.depositsDetected} sweep:${stats.sweepsProcessed} err:${stats.errors}`
    )
  }, 10 * 60 * 1000)

  // Graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n[Engine] Shutting down...')
    showStatus()
    process.exit(0)
  })

  process.on('SIGTERM', () => {
    console.log('\n[Engine] Terminated.')
    process.exit(0)
  })
}

main().catch((err) => {
  console.error('Fatal error:', err)
  process.exit(1)
})
