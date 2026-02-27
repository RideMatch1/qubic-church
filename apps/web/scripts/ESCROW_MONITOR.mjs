#!/usr/bin/env node
/**
 * ESCROW MONITOR — Background Service
 *
 * Monitors per-bet escrow addresses for:
 *   1. Deposit Detection — Polls awaiting_deposit escrows via RPC
 *   2. JoinBet Execution — Calls joinBet on Quottery SC when deposit detected
 *   3. Payout Detection — After market resolution, checks for SC payouts
 *   4. Sweep Execution — Sends winnings from escrow to user's payout address
 *   5. Expiry Handling — Marks timed-out escrows as expired
 *
 * Usage:
 *   node ESCROW_MONITOR.mjs                 # Run continuously
 *   node ESCROW_MONITOR.mjs --once          # Run one cycle then exit
 *   node ESCROW_MONITOR.mjs --status        # Show current escrow stats
 */

import { createRequire } from 'module'
const require = createRequire(import.meta.url)

// Load .env
import { readFileSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const envPath = resolve(__dirname, '../../../../.env')

try {
  const envContent = readFileSync(envPath, 'utf-8')
  for (const line of envContent.split('\n')) {
    const match = line.match(/^([^#=]+)=(.*)$/)
    if (match) {
      process.env[match[1].trim()] = match[2].trim()
    }
  }
} catch (e) {
  console.error('Could not read .env:', e.message)
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const DEPOSIT_POLL_MS = Number(process.env.DEPOSIT_POLL_INTERVAL_MS) || 10_000
const PAYOUT_POLL_MS = Number(process.env.PAYOUT_POLL_INTERVAL_MS) || 15_000
const RPC_URL = process.env.QUBIC_RPC_URL || 'https://rpc.qubic.org/v1'
const ESCROW_MASTER_KEY = process.env.ESCROW_MASTER_KEY

// ---------------------------------------------------------------------------
// RPC Helpers
// ---------------------------------------------------------------------------

async function rpc(endpoint, options) {
  const res = await fetch(`${RPC_URL}${endpoint}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  })
  if (!res.ok) throw new Error(`RPC ${res.status}: ${res.statusText}`)
  return res.json()
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
// Database (lazy import to let .env load first)
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
// Phase 1: Deposit Detection
// ---------------------------------------------------------------------------

async function checkDeposits() {
  const db = getDB()
  const escrows = db.getEscrowsByStatus('awaiting_deposit')

  if (escrows.length === 0) return 0

  let detected = 0
  console.log(`[Deposit] Checking ${escrows.length} escrows...`)

  for (const escrow of escrows) {
    // Check if expired
    if (new Date(escrow.expiresAt) <= new Date()) {
      db.markEscrowExpired(escrow.id)
      db.updateEscrowKeyStatus(escrow.id, 'archived')
      db.setBetStatus(escrow.betId, 'refunded')
      console.log(`  [EXPIRED] ${escrow.id} (bet ${escrow.betId})`)
      continue
    }

    try {
      const balance = await getBalance(escrow.escrowAddress)
      if (balance >= BigInt(escrow.expectedAmountQu)) {
        db.recordEscrowDeposit(escrow.id, Number(balance))
        console.log(`  [DEPOSIT] ${escrow.id}: ${Number(balance).toLocaleString()} QU (expected ${escrow.expectedAmountQu.toLocaleString()})`)
        detected++
      }
    } catch (err) {
      console.error(`  [ERROR] ${escrow.id}: ${err.message}`)
    }
  }

  return detected
}

// ---------------------------------------------------------------------------
// Phase 2: JoinBet Execution
// ---------------------------------------------------------------------------

async function processJoinBets() {
  const db = getDB()
  const escrows = db.getEscrowsByStatus('deposit_detected')

  if (escrows.length === 0) return 0

  let processed = 0
  console.log(`[JoinBet] Processing ${escrows.length} deposits...`)

  for (const escrow of escrows) {
    try {
      const market = db.getMarket(escrow.marketId)
      if (!market || !market.quotteryBetId) {
        console.error(`  [SKIP] ${escrow.id}: Market ${escrow.marketId} not found or no betId`)
        continue
      }

      // Decrypt seed
      const keyEntry = db.getEscrowKey(escrow.id)
      if (!keyEntry) {
        console.error(`  [SKIP] ${escrow.id}: No key found`)
        continue
      }

      const { decryptSeed, deriveMasterKey } = require('../src/lib/predict/key-vault.ts')
      const masterKey = deriveMasterKey(ESCROW_MASTER_KEY)
      const seed = decryptSeed({
        ciphertext: keyEntry.encryptedSeed,
        iv: keyEntry.iv,
        authTag: keyEntry.authTag,
      }, masterKey)

      // Update status
      db.updateEscrowStatus(escrow.id, 'joining_sc')

      // Call joinBet
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
        console.log(`  [JOIN] ${escrow.id}: TX ${result.txId} (tick ${result.targetTick})`)
        processed++
      } else {
        db.updateEscrowStatus(escrow.id, 'deposit_detected')
        console.error(`  [FAIL] ${escrow.id}: ${result.error}`)
      }
    } catch (err) {
      db.updateEscrowStatus(escrow.id, 'deposit_detected')
      console.error(`  [ERROR] ${escrow.id}: ${err.message}`)
    }
  }

  return processed
}

// ---------------------------------------------------------------------------
// Phase 3: Payout Detection (after market resolution)
// ---------------------------------------------------------------------------

async function checkPayouts() {
  const db = getDB()
  const escrows = db.getEscrowsByStatus('active_in_sc')

  if (escrows.length === 0) return 0

  let detected = 0

  // Only check escrows whose markets are resolved
  for (const escrow of escrows) {
    const market = db.getMarket(escrow.marketId)
    if (!market || market.status !== 'resolved') continue

    // Check if this is a winner
    if (market.winningOption !== escrow.option) {
      db.markEscrowLost(escrow.id)
      db.updateEscrowKeyStatus(escrow.id, 'archived')
      console.log(`  [LOST] ${escrow.id}: option ${escrow.option} lost (winner: ${market.winningOption})`)
      continue
    }

    // Check for payout on-chain
    try {
      const balance = await getBalance(escrow.escrowAddress)
      if (balance > 0n) {
        db.recordEscrowPayout(escrow.id, Number(balance))
        console.log(`  [PAYOUT] ${escrow.id}: ${Number(balance).toLocaleString()} QU detected`)
        detected++
      }
    } catch (err) {
      console.error(`  [ERROR] ${escrow.id}: ${err.message}`)
    }
  }

  return detected
}

// ---------------------------------------------------------------------------
// Phase 4: Sweep (send winnings to user)
// ---------------------------------------------------------------------------

async function processSweeps() {
  const db = getDB()
  const escrows = db.getEscrowsByStatus('won_awaiting_sweep')

  if (escrows.length === 0) return 0

  let swept = 0
  console.log(`[Sweep] Processing ${escrows.length} payouts...`)

  for (const escrow of escrows) {
    try {
      // Decrypt seed
      const keyEntry = db.getEscrowKey(escrow.id)
      if (!keyEntry || keyEntry.status !== 'active') {
        console.error(`  [SKIP] ${escrow.id}: Key not available (${keyEntry?.status})`)
        continue
      }

      const { decryptSeed, deriveMasterKey } = require('../src/lib/predict/key-vault.ts')
      const masterKey = deriveMasterKey(ESCROW_MASTER_KEY)
      const seed = decryptSeed({
        ciphertext: keyEntry.encryptedSeed,
        iv: keyEntry.iv,
        authTag: keyEntry.authTag,
      }, masterKey)

      // Get current balance
      const balance = await getBalance(escrow.escrowAddress)
      if (balance <= 1000n) {
        console.log(`  [SKIP] ${escrow.id}: Balance too low (${balance} QU)`)
        continue
      }

      const sweepAmount = balance - 1000n // reserve for TX fee

      // Create and broadcast transfer
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

      // Update bet payout
      db.resolveBet(escrow.betId, true, Number(sweepAmount))

      console.log(`  [SWEEP] ${escrow.id}: ${Number(sweepAmount).toLocaleString()} QU → ${escrow.userPayoutAddress.slice(0, 12)}... (tick ${targetTick})`)
      swept++
    } catch (err) {
      console.error(`  [ERROR] ${escrow.id}: ${err.message}`)
    }
  }

  return swept
}

// ---------------------------------------------------------------------------
// Status Report
// ---------------------------------------------------------------------------

function showStatus() {
  const db = getDB()

  const counts = {
    awaitingDeposit: db.getEscrowsByStatus('awaiting_deposit').length,
    depositDetected: db.getEscrowsByStatus('deposit_detected').length,
    joiningsc: db.getEscrowsByStatuses('joining_sc', 'active_in_sc').length,
    wonAwaiting: db.getEscrowsByStatus('won_awaiting_sweep').length,
    swept: db.getEscrowsByStatus('swept').length,
    lost: db.getEscrowsByStatus('lost').length,
    expired: db.getEscrowsByStatus('expired').length,
  }

  console.log('\n=== ESCROW MONITOR STATUS ===')
  console.log(`Awaiting Deposit:  ${counts.awaitingDeposit}`)
  console.log(`Deposit Detected:  ${counts.depositDetected}`)
  console.log(`Active in SC:      ${counts.joiningsc}`)
  console.log(`Won (sweep pend.): ${counts.wonAwaiting}`)
  console.log(`Swept:             ${counts.swept}`)
  console.log(`Lost:              ${counts.lost}`)
  console.log(`Expired:           ${counts.expired}`)
  console.log(`Active Escrows:    ${db.countActiveEscrows()}`)
  console.log()

  return counts
}

// ---------------------------------------------------------------------------
// Main Loop
// ---------------------------------------------------------------------------

async function runCycle() {
  const start = Date.now()

  try {
    const deposits = await checkDeposits()
    const joined = await processJoinBets()
    const payouts = await checkPayouts()
    const swept = await processSweeps()

    const elapsed = Date.now() - start

    if (deposits + joined + payouts + swept > 0) {
      console.log(`[Cycle] ${elapsed}ms — deposits:${deposits} joined:${joined} payouts:${payouts} swept:${swept}`)
    }
  } catch (err) {
    console.error(`[Cycle ERROR] ${err.message}`)
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
    console.log('[Monitor] Running single cycle...')
    await runCycle()
    showStatus()
    process.exit(0)
  }

  // Continuous mode
  console.log('[Monitor] Starting ESCROW MONITOR')
  console.log(`  Deposit poll:  ${DEPOSIT_POLL_MS}ms`)
  console.log(`  Payout poll:   ${PAYOUT_POLL_MS}ms`)
  console.log(`  RPC:           ${RPC_URL}`)
  console.log()

  showStatus()

  // Run immediately, then on interval
  await runCycle()

  const interval = Math.min(DEPOSIT_POLL_MS, PAYOUT_POLL_MS)
  setInterval(runCycle, interval)

  // Graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n[Monitor] Shutting down...')
    process.exit(0)
  })
}

main().catch((err) => {
  console.error('Fatal error:', err)
  process.exit(1)
})
