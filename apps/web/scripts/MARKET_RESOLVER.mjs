#!/usr/bin/env node
/**
 * MARKET RESOLVER — Background Oracle Resolution Service
 *
 * Checks for expired prediction markets and resolves them using oracle price data.
 *
 * Flow (every 60 seconds):
 *   1. Load all markets with status='active' AND end_date < now
 *   2. For each market:
 *      a. Get latest price from oracle DB
 *      b. Determine winning option
 *      c. Send publishResult() TX to Quottery SC
 *      d. Calculate payouts and credit winners
 *      e. Update market status to 'resolved'
 *   3. Also close betting on markets past close_date
 *
 * Usage:
 *   node scripts/MARKET_RESOLVER.mjs               # Single run
 *   node scripts/MARKET_RESOLVER.mjs --loop         # Continuous (60s interval)
 *   node scripts/MARKET_RESOLVER.mjs --dry-run      # No TX, just log
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

const MASTER_SEED = process.env.MASTER_SEED
const MASTER_IDENTITY = process.env.MASTER_IDENTITY
const INTERVAL_SEC = 60
const DRY_RUN = process.argv.includes('--dry-run')
const LOOP = process.argv.includes('--loop')

// ---------------------------------------------------------------------------
// SQLite (predict + oracle DBs)
// ---------------------------------------------------------------------------

const Database = require('better-sqlite3')

const PREDICT_DB_PATH = process.env.PREDICT_DB_PATH || resolve(__dirname, '../predict.sqlite3')
const ORACLE_DB_PATH = resolve(__dirname, 'oracle.sqlite3')

let predictDb = null
let oracleDb = null

function getPredictDb() {
  if (!predictDb) {
    predictDb = new Database(PREDICT_DB_PATH)
    predictDb.pragma('journal_mode = WAL')
    predictDb.pragma('busy_timeout = 5000')
  }
  return predictDb
}

function getOracleDb() {
  if (!oracleDb && existsSync(ORACLE_DB_PATH)) {
    oracleDb = new Database(ORACLE_DB_PATH, { readonly: true })
    oracleDb.pragma('journal_mode = WAL')
  }
  return oracleDb
}

// ---------------------------------------------------------------------------
// Qubic Library
// ---------------------------------------------------------------------------

const qubicLib = require('@qubic-lib/qubic-ts-library').default
const { QubicHelper, QubicTransaction, DynamicPayload, PublicKey } = qubicLib

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

async function getCurrentTick() {
  const data = await rpc('/tick-info')
  return data.tickInfo?.tick ?? data.tick ?? 0
}

// ---------------------------------------------------------------------------
// Price Fetcher (from oracle DB)
// ---------------------------------------------------------------------------

function getLatestPrice(pair) {
  const db = getOracleDb()
  if (!db) return null

  // Query the latest price for this pair from any oracle source
  const row = db.prepare(`
    SELECT price, timestamp, oracle
    FROM prices
    WHERE pair = ?
    ORDER BY timestamp DESC
    LIMIT 1
  `).get(pair)

  return row || null
}

// ---------------------------------------------------------------------------
// Quottery publishResult TX
// ---------------------------------------------------------------------------

async function sendPublishResult(betId, winOption, targetTick) {
  if (DRY_RUN) {
    console.log(`  [DRY-RUN] Would send publishResult(betId=${betId}, winOption=${winOption}) at tick ${targetTick}`)
    return { success: true, dryRun: true }
  }

  if (!MASTER_SEED) {
    throw new Error('MASTER_SEED not set')
  }

  const QUOTTERY_INDEX = 2
  const PUBLISH_PROCEDURE = 4

  // Build payload: betId (uint32) + winOption (uint32) = 8 bytes
  const payload = Buffer.alloc(8)
  payload.writeUInt32LE(betId, 0)
  payload.writeUInt32LE(winOption, 4)

  // SC public key for Quottery (index 2)
  const scPubKey = new Uint8Array(32)
  scPubKey[0] = QUOTTERY_INDEX

  const helper = new QubicHelper()
  const idPackage = await helper.createIdPackage(MASTER_SEED)

  const tx = new QubicTransaction()
    .setSourcePublicKey(new PublicKey(idPackage.publicKey))
    .setDestinationPublicKey(new PublicKey(scPubKey))
    .setAmount(0)
    .setTick(targetTick)
    .setInputType(PUBLISH_PROCEDURE)
    .setInputSize(payload.length)

  const dynPayload = new DynamicPayload(payload.length)
  dynPayload.setPayload(new Uint8Array(payload))
  tx.setPayload(dynPayload)

  const txBytes = await tx.build(MASTER_SEED)
  const encoded = tx.encodeTransactionToBase64(txBytes)

  const result = await rpc('/broadcast-transaction', {
    method: 'POST',
    body: JSON.stringify({ encodedTransaction: encoded }),
  })

  return {
    success: true,
    txId: result.transactionId ?? result.peersBroadcasted ?? 'ok',
    peersBroadcasted: result.peersBroadcasted ?? 0,
    targetTick,
  }
}

// ---------------------------------------------------------------------------
// Resolution Logic
// ---------------------------------------------------------------------------

function determineWinner(market, currentPrice) {
  switch (market.resolution_type) {
    case 'price_above':
      return currentPrice >= market.resolution_target ? 0 : 1
    case 'price_below':
      return currentPrice <= market.resolution_target ? 0 : 1
    case 'price_range':
      if (market.resolution_target_high !== null) {
        return currentPrice >= market.resolution_target &&
          currentPrice <= market.resolution_target_high
          ? 0 : 1
      }
      return currentPrice >= market.resolution_target ? 0 : 1
    default:
      return 1
  }
}

function calculatePayoutPerSlot(totalPool, winnerSlots) {
  if (winnerSlots <= 0) return 0
  const pool = BigInt(totalPool)
  const burn = (pool * 2n) / 100n           // 2% burn
  const shareholder = (pool * 10n) / 100n   // 10% shareholder
  const operator = (pool * 5n) / 1000n      // 0.5% operator
  const oracle = (pool * 200n) / 10000n     // 2% oracle fee
  const winnerPool = pool - burn - shareholder - operator - oracle
  return Number(winnerPool / BigInt(winnerSlots))
}

// ---------------------------------------------------------------------------
// Main Resolution Loop
// ---------------------------------------------------------------------------

async function resolveExpiredMarkets() {
  const db = getPredictDb()
  const now = new Date().toISOString()

  // 1. Close betting on markets past close_date
  const closing = db.prepare(`
    SELECT * FROM markets
    WHERE status = 'active' AND close_date <= ?
  `).all(now)

  for (const market of closing) {
    db.prepare("UPDATE markets SET status = 'closed' WHERE id = ?").run(market.id)
    console.log(`  Closed betting: ${market.id} (${market.question})`)
  }

  // 2. Find markets ready for resolution
  const expired = db.prepare(`
    SELECT * FROM markets
    WHERE status IN ('active', 'closed') AND end_date <= ?
  `).all(now)

  if (expired.length === 0) {
    console.log(`  No markets to resolve.`)
    return 0
  }

  console.log(`  Found ${expired.length} market(s) to resolve`)

  let resolvedCount = 0
  const currentTick = await getCurrentTick()

  for (const market of expired) {
    try {
      // Atomically claim for resolution (prevents race with API)
      const claimed = db.prepare(
        "UPDATE markets SET status = 'resolving' WHERE id = ? AND status IN ('active', 'closed')"
      ).run(market.id)
      if (claimed.changes === 0) {
        console.log(`  SKIP ${market.id}: Already being resolved`)
        continue
      }

      // Get current price
      const priceData = getLatestPrice(market.pair)
      if (!priceData) {
        console.log(`  SKIP ${market.id}: No price data for ${market.pair}`)
        // Revert status so it can be retried
        db.prepare("UPDATE markets SET status = 'closed' WHERE id = ?").run(market.id)
        continue
      }

      const currentPrice = priceData.price
      const winningOption = determineWinner(market, currentPrice)
      const winLabel = winningOption === 0 ? 'YES' : 'NO'

      console.log(`  Resolving ${market.id}: ${market.question}`)
      console.log(`    Price: ${currentPrice} | Target: ${market.resolution_target} | Winner: ${winLabel}`)

      // Send publishResult to Quottery SC
      if (market.quottery_bet_id) {
        try {
          const txResult = await sendPublishResult(
            market.quottery_bet_id,
            winningOption,
            currentTick + 5
          )
          console.log(`    Quottery TX: ${JSON.stringify(txResult)}`)
        } catch (err) {
          console.error(`    Quottery TX failed: ${err.message}`)
        }
      }

      // Update market in DB
      db.prepare(`
        UPDATE markets SET
          status = 'resolved',
          resolution_price = ?,
          winning_option = ?,
          resolved_at = datetime('now')
        WHERE id = ?
      `).run(currentPrice, winningOption, market.id)

      // Calculate payouts
      const winnerSlots = winningOption === 0 ? market.yes_slots : market.no_slots
      const payoutPerSlot = calculatePayoutPerSlot(market.total_pool, winnerSlots)

      // Resolve bets
      const bets = db.prepare(`
        SELECT * FROM user_bets WHERE market_id = ? AND status IN ('pending', 'confirmed')
      `).all(market.id)

      let winners = 0, losers = 0
      const resolveBets = db.transaction(() => {
        for (const bet of bets) {
          if (bet.option === winningOption) {
            const payout = payoutPerSlot * bet.slots
            db.prepare("UPDATE user_bets SET status = 'won', payout_qu = ? WHERE id = ?")
              .run(payout, bet.id)
            // Credit user
            db.prepare("UPDATE accounts SET balance_qu = balance_qu + ?, total_won = total_won + ? WHERE address = ?")
              .run(payout, payout, bet.user_address)
            winners++
          } else {
            db.prepare("UPDATE user_bets SET status = 'lost' WHERE id = ?").run(bet.id)
            losers++
          }
        }
      })
      resolveBets()

      console.log(`    Resolved: ${winners} winners, ${losers} losers, ${payoutPerSlot} QU/slot`)
      resolvedCount++
    } catch (err) {
      console.error(`  ERROR resolving ${market.id}: ${err.message}`)
    }
  }

  return resolvedCount
}

// ---------------------------------------------------------------------------
// Entry Point
// ---------------------------------------------------------------------------

async function main() {
  console.log(`\n=== MARKET RESOLVER ===`)
  console.log(`Mode: ${LOOP ? 'CONTINUOUS' : 'SINGLE RUN'} ${DRY_RUN ? '(DRY-RUN)' : ''}`)
  console.log(`Predict DB: ${PREDICT_DB_PATH}`)
  console.log(`Oracle DB: ${ORACLE_DB_PATH}`)
  console.log(`Master: ${MASTER_IDENTITY?.slice(0, 15)}...`)
  console.log()

  if (!existsSync(PREDICT_DB_PATH)) {
    console.error('ERROR: predict.sqlite3 not found. Run the platform first to create the DB.')
    process.exit(1)
  }

  if (LOOP) {
    console.log(`Running every ${INTERVAL_SEC}s. Ctrl+C to stop.\n`)
    while (true) {
      try {
        const ts = new Date().toISOString().slice(0, 19)
        console.log(`[${ts}] Checking for expired markets...`)
        const count = await resolveExpiredMarkets()
        if (count > 0) {
          console.log(`  Resolved ${count} market(s)`)
        }
      } catch (err) {
        console.error(`  Error: ${err.message}`)
      }
      await new Promise(r => setTimeout(r, INTERVAL_SEC * 1000))
    }
  } else {
    const count = await resolveExpiredMarkets()
    console.log(`\nDone. Resolved ${count} market(s).`)
  }
}

main().catch(err => {
  console.error('FATAL:', err)
  process.exit(1)
})
