#!/usr/bin/env node
/**
 * DEPOSIT DETECTOR — Background Deposit Monitor
 *
 * Monitors the platform master wallet for incoming QU transfers
 * and credits user internal balances.
 *
 * Detection method:
 *   1. Poll RPC for current balance and transfer count
 *   2. Compare with last known state
 *   3. If new incoming transfers detected, query TX history
 *   4. Match sender addresses with registered users
 *   5. Credit internal balances
 *
 * Usage:
 *   node scripts/DEPOSIT_DETECTOR.mjs               # Single check
 *   node scripts/DEPOSIT_DETECTOR.mjs --loop         # Continuous (30s interval)
 *   node scripts/DEPOSIT_DETECTOR.mjs --dry-run      # No credits, just log
 */

import { createRequire } from 'module'
import { readFileSync, existsSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const require = createRequire(import.meta.url)
const __dirname = dirname(fileURLToPath(import.meta.url))

// ---------------------------------------------------------------------------
// Env + Config
// ---------------------------------------------------------------------------

const envPath = resolve(__dirname, '../../../.env')
try {
  const envContent = readFileSync(envPath, 'utf-8')
  for (const line of envContent.split('\n')) {
    const match = line.match(/^([^#=]+)=(.*)$/)
    if (match) process.env[match[1].trim()] = match[2].trim()
  }
} catch (e) {
  console.error('Could not read .env:', e.message)
}

const MASTER_IDENTITY = process.env.MASTER_IDENTITY
const INTERVAL_SEC = 30
const DRY_RUN = process.argv.includes('--dry-run')
const LOOP = process.argv.includes('--loop')
const MIN_DEPOSIT = 1000 // Minimum deposit to credit

// ---------------------------------------------------------------------------
// SQLite
// ---------------------------------------------------------------------------

const Database = require('better-sqlite3')
const PREDICT_DB_PATH = process.env.PREDICT_DB_PATH || resolve(__dirname, '../predict.sqlite3')

let predictDb = null

function getPredictDb() {
  if (!predictDb) {
    predictDb = new Database(PREDICT_DB_PATH)
    predictDb.pragma('journal_mode = WAL')
    predictDb.pragma('busy_timeout = 5000')
  }
  return predictDb
}

// ---------------------------------------------------------------------------
// RPC
// ---------------------------------------------------------------------------

const RPC_ENDPOINTS = [
  'https://rpc.qubic.org/v1',
  'https://rpc.qubic.li/v1',
  'https://rpc.qubic.network/v1',
]

let _rpcIdx = 0

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
    } catch (e) {
      // try next
    }
  }
  throw new Error('All RPC endpoints failed')
}

// ---------------------------------------------------------------------------
// State Tracking
// ---------------------------------------------------------------------------

// Track last known incoming transfer count to detect new deposits
let lastKnownIncomingCount = -1
let lastKnownIncomingTick = 0

/**
 * Check for new deposits to the platform address.
 *
 * Strategy: Compare incoming transfer count.
 * If count increased, new deposits arrived.
 *
 * Note: Qubic RPC doesn't provide a transaction list endpoint,
 * so we rely on balance changes and manual tracking.
 * For production, a proper indexer would be needed.
 */
async function checkForDeposits() {
  if (!MASTER_IDENTITY) {
    throw new Error('MASTER_IDENTITY not set')
  }

  const data = await rpc(`/balances/${MASTER_IDENTITY}`)
  const balance = data.balance

  if (!balance) {
    console.log('  Could not fetch balance')
    return 0
  }

  const currentIncoming = balance.numberOfIncomingTransfers ?? 0
  const currentBalance = Number(balance.balance ?? 0)
  const latestInTick = balance.latestIncomingTransferTick ?? 0

  // First run — just record state
  if (lastKnownIncomingCount === -1) {
    lastKnownIncomingCount = currentIncoming
    lastKnownIncomingTick = latestInTick
    console.log(`  Initial state: ${currentIncoming} incoming TXs, balance: ${currentBalance.toLocaleString()} QU`)
    return 0
  }

  // Check if new incoming transfers
  const newTxCount = currentIncoming - lastKnownIncomingCount

  if (newTxCount <= 0) {
    return 0
  }

  console.log(`  Detected ${newTxCount} new incoming transfer(s)!`)
  console.log(`  Latest incoming tick: ${latestInTick} (was: ${lastKnownIncomingTick})`)

  // Since Qubic RPC doesn't provide a TX list, we can't automatically
  // match sender addresses. For the MVP, deposits need manual confirmation
  // or a more sophisticated indexer.
  //
  // For now, log the event and check if any registered users have
  // requested deposits recently.

  const db = getPredictDb()

  // Check for pending deposit transactions in our DB
  // (Users register and we know their address — when they deposit,
  //  we can verify the on-chain balance change)
  const pendingAccounts = db.prepare(`
    SELECT address FROM accounts
    WHERE balance_qu = 0 OR address IN (
      SELECT address FROM transactions
      WHERE type = 'deposit' AND status = 'pending'
      ORDER BY created_at DESC LIMIT 50
    )
  `).all()

  let credited = 0

  for (const account of pendingAccounts) {
    try {
      // Check the user's on-chain balance (they should have sent QU to us)
      // This is a simplified approach — in production, use an indexer
      const userBalance = await rpc(`/balances/${account.address}`)
      const outgoing = userBalance?.balance?.numberOfOutgoingTransfers ?? 0
      const latestOutTick = userBalance?.balance?.latestOutgoingTransferTick ?? 0

      // If user has outgoing TXs and the latest was after our last check tick,
      // it might be a deposit to us
      if (latestOutTick > lastKnownIncomingTick) {
        console.log(`  Potential deposit from ${account.address.slice(0, 15)}... (outTick: ${latestOutTick})`)
        // Note: We can't fully verify the destination without a TX indexer
        // For MVP, manual verification or trust model
      }
    } catch {
      // Skip on error
    }
  }

  // Update tracking state
  lastKnownIncomingCount = currentIncoming
  lastKnownIncomingTick = latestInTick

  return credited
}

/**
 * Manual deposit credit — called via API when deposit is confirmed.
 * For MVP, this is the primary deposit mechanism.
 */
function creditManualDeposit(userAddress, amountQu) {
  if (DRY_RUN) {
    console.log(`  [DRY-RUN] Would credit ${amountQu} QU to ${userAddress}`)
    return
  }

  if (amountQu < MIN_DEPOSIT) {
    console.log(`  SKIP: Amount ${amountQu} below minimum ${MIN_DEPOSIT} QU`)
    return
  }

  const db = getPredictDb()

  // Ensure account exists
  db.prepare('INSERT OR IGNORE INTO accounts (address) VALUES (?)').run(userAddress)

  // Credit balance
  db.prepare(`
    UPDATE accounts SET
      balance_qu = balance_qu + ?,
      total_deposited = total_deposited + ?
    WHERE address = ?
  `).run(amountQu, amountQu, userAddress)

  // Record transaction
  const txId = `tx_dep_${Date.now().toString(36)}`
  db.prepare(`
    INSERT INTO transactions (id, address, type, amount_qu, status)
    VALUES (?, ?, 'deposit', ?, 'confirmed')
  `).run(txId, userAddress, amountQu)

  console.log(`  Credited ${amountQu.toLocaleString()} QU to ${userAddress.slice(0, 15)}...`)
}

// ---------------------------------------------------------------------------
// Entry Point
// ---------------------------------------------------------------------------

async function main() {
  console.log(`\n=== DEPOSIT DETECTOR ===`)
  console.log(`Mode: ${LOOP ? 'CONTINUOUS' : 'SINGLE CHECK'} ${DRY_RUN ? '(DRY-RUN)' : ''}`)
  console.log(`Platform: ${MASTER_IDENTITY?.slice(0, 15)}...`)
  console.log(`Predict DB: ${PREDICT_DB_PATH}`)
  console.log()

  if (!MASTER_IDENTITY) {
    console.error('ERROR: MASTER_IDENTITY not set in .env')
    process.exit(1)
  }

  // Handle manual deposit from CLI args
  // Usage: node DEPOSIT_DETECTOR.mjs --credit ADDRESS AMOUNT
  const creditIdx = process.argv.indexOf('--credit')
  if (creditIdx !== -1) {
    const address = process.argv[creditIdx + 1]
    const amount = parseInt(process.argv[creditIdx + 2] ?? '0', 10)
    if (!address || !amount) {
      console.error('Usage: --credit ADDRESS AMOUNT_QU')
      process.exit(1)
    }
    creditManualDeposit(address, amount)
    return
  }

  if (LOOP) {
    console.log(`Checking every ${INTERVAL_SEC}s. Ctrl+C to stop.\n`)
    while (true) {
      try {
        const ts = new Date().toISOString().slice(0, 19)
        console.log(`[${ts}] Checking for deposits...`)
        await checkForDeposits()
      } catch (err) {
        console.error(`  Error: ${err.message}`)
      }
      await new Promise(r => setTimeout(r, INTERVAL_SEC * 1000))
    }
  } else {
    await checkForDeposits()
    console.log('\nDone.')
  }
}

main().catch(err => {
  console.error('FATAL:', err)
  process.exit(1)
})
