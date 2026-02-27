#!/usr/bin/env node
/**
 * ORACLE DOMINATOR — Systematic Price Collector
 *
 * Broadcasts price queries across ALL exchange/pair combinations.
 * 20 pairs across 7 exchanges, 3 tiers. Up to 200+ QU per sweep.
 *
 * Usage:
 *   node ORACLE_DOMINATOR.mjs --estimate              # Show cost, send nothing
 *   node ORACLE_DOMINATOR.mjs --explore               # 1 query/pair, test which work
 *   node ORACLE_DOMINATOR.mjs --tier 1                # Core QUBIC only (70 QU)
 *   node ORACLE_DOMINATOR.mjs --tier 1,2              # Core + Majors (130 QU)
 *   node ORACLE_DOMINATOR.mjs --all                   # All 20 pairs (200 QU)
 *   node ORACLE_DOMINATOR.mjs --all --dry-run         # Simulate, no broadcast
 *   node ORACLE_DOMINATOR.mjs --loop --tier 1 --interval 30  # Every 30 min
 *   node ORACLE_DOMINATOR.mjs --verify <startTick>    # TCP verify past queries
 */

import {
  loadEnv, rpc, getBalance, getCurrentTick,
  sendOracleQuery, PAIR_REGISTRY, WORKING_PAIRS, DISCOVERY_PAIRS, COST_PER_QUERY,
  getPairsByTier, estimateCost, sleep, fmt,
  printHeader, readDataFile, appendToRollingFile,
} from './oracle-utils.mjs'
import { insertPricesBatch } from './oracle-db.mjs'

// TCP verification imports
import { createConnection } from 'net'
import { randomBytes } from 'crypto'

// =============================================================================
// TCP VERIFIER (lightweight, for post-broadcast verification)
// =============================================================================

const MSG = {
  EXCHANGE_PUBLIC_PEERS: 0,
  REQUEST_CURRENT_TICK_INFO: 27,
  RESPOND_CURRENT_TICK_INFO: 28,
  END_RESPONSE: 35,
  REQUEST_ORACLE_DATA: 66,
  RESPOND_ORACLE_DATA: 67,
}

const RES = { QUERY_IDS: 0, QUERY_METADATA: 1, QUERY_DATA: 2, REPLY_DATA: 3, TICK_RANGE: 9 }

class VerifyClient {
  constructor(ip, port = 21841) {
    this.ip = ip
    this.port = port
    this.buffer = Buffer.alloc(0)
    this.socket = null
  }

  connect() {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('timeout')), 10000)
      this.socket = createConnection({ host: this.ip, port: this.port }, () => {
        clearTimeout(timer)
        resolve()
      })
      this.socket.on('error', (err) => { clearTimeout(timer); reject(err) })
      this.socket.on('data', (chunk) => {
        this.buffer = Buffer.concat([this.buffer, chunk])
      })
    })
  }

  close() { if (this.socket) this.socket.destroy() }

  send(buf) {
    return new Promise((resolve, reject) => {
      this.socket.write(buf, (err) => err ? reject(err) : resolve())
    })
  }

  async waitFor(bytes, ms = 8000) {
    const start = Date.now()
    while (this.buffer.length < bytes) {
      if (Date.now() - start > ms) throw new Error(`timeout`)
      await new Promise(r => setTimeout(r, 30))
    }
  }

  consume(n) {
    const r = this.buffer.slice(0, n)
    this.buffer = this.buffer.slice(n)
    return r
  }

  async readMsg() {
    await this.waitFor(8)
    const hdr = this.consume(8)
    const size = hdr[0] | (hdr[1] << 8) | (hdr[2] << 16)
    const type = hdr[3]
    const payloadSize = size - 8
    let payload = Buffer.alloc(0)
    if (payloadSize > 0) {
      await this.waitFor(payloadSize)
      payload = this.consume(payloadSize)
    }
    return { type, payload }
  }

  async readMsgSkip() {
    for (let i = 0; i < 10; i++) {
      const msg = await this.readMsg()
      if (msg.type !== MSG.EXCHANGE_PUBLIC_PEERS) return msg
    }
    throw new Error('protocol error')
  }

  async getQueryIdsAtTick(tick) {
    const payload = Buffer.alloc(16)
    payload.writeUInt32LE(0, 0) // ALL_QUERY_IDS
    payload.writeUInt32LE(0, 4)
    payload.writeBigInt64LE(BigInt(tick), 8)
    const hdr = Buffer.alloc(8)
    const totalSize = 24
    hdr[0] = totalSize & 0xFF; hdr[1] = (totalSize >> 8) & 0xFF; hdr[2] = (totalSize >> 16) & 0xFF
    hdr[3] = MSG.REQUEST_ORACLE_DATA
    randomBytes(4).copy(hdr, 4)
    this.buffer = Buffer.alloc(0)
    await this.send(Buffer.concat([hdr, payload]))

    const ids = []
    while (true) {
      const msg = await this.readMsgSkip()
      if (msg.type === MSG.END_RESPONSE) break
      if (msg.type === MSG.RESPOND_ORACLE_DATA) {
        const resType = msg.payload.readUInt32LE(0)
        const data = msg.payload.slice(4)
        if (resType === RES.QUERY_IDS) {
          for (let i = 0; i < data.length; i += 8) {
            ids.push(Number(data.readBigInt64LE(i)))
          }
        }
      }
    }
    return ids
  }

  async getQueryInfo(queryId) {
    const payload = Buffer.alloc(16)
    payload.writeUInt32LE(5, 0) // QUERY_AND_RESPONSE
    payload.writeUInt32LE(0, 4)
    payload.writeBigInt64LE(BigInt(queryId), 8)
    const hdr = Buffer.alloc(8)
    const totalSize = 24
    hdr[0] = totalSize & 0xFF; hdr[1] = (totalSize >> 8) & 0xFF; hdr[2] = (totalSize >> 16) & 0xFF
    hdr[3] = MSG.REQUEST_ORACLE_DATA
    randomBytes(4).copy(hdr, 4)
    this.buffer = Buffer.alloc(0)
    await this.send(Buffer.concat([hdr, payload]))

    let metadata = null
    let queryData = Buffer.alloc(0)
    let replyData = Buffer.alloc(0)

    while (true) {
      const msg = await this.readMsgSkip()
      if (msg.type === MSG.END_RESPONSE) break
      if (msg.type === MSG.RESPOND_ORACLE_DATA) {
        const resType = msg.payload.readUInt32LE(0)
        const inner = msg.payload.slice(4)
        if (resType === RES.QUERY_METADATA) {
          metadata = {
            queryId: inner.readBigInt64LE(0),
            type: inner.readUInt8(8),
            status: inner.readUInt8(9),
            statusFlags: inner.readUInt16LE(10),
            queryTick: inner.readUInt32LE(12),
            revealTick: inner.readUInt32LE(64),
            totalCommits: inner.readUInt16LE(68),
            agreeingCommits: inner.readUInt16LE(70),
          }
        } else if (resType === RES.QUERY_DATA) {
          queryData = Buffer.concat([queryData, inner])
        } else if (resType === RES.REPLY_DATA) {
          replyData = Buffer.concat([replyData, inner])
        }
      }
    }

    // Decode price if available
    let price = null
    if (replyData.length >= 16) {
      const numerator = Number(replyData.readBigInt64LE(0))
      const denominator = Number(replyData.readBigInt64LE(8))
      if (denominator !== 0) {
        price = numerator / denominator
      }
    }

    // Decode query pair
    let pair = null
    if (queryData.length >= 104) {
      const oracle = queryData.slice(0, 32).toString('ascii').replace(/\0/g, '')
      const currency1 = queryData.slice(40, 72).toString('ascii').replace(/\0/g, '')
      const currency2 = queryData.slice(72, 104).toString('ascii').replace(/\0/g, '')
      pair = { oracle, currency1, currency2 }
    }

    const STATUS_NAMES = { 0: 'unknown', 1: 'pending', 2: 'committed', 3: 'success', 4: 'timeout', 5: 'unresolvable' }

    return {
      metadata,
      statusStr: STATUS_NAMES[metadata?.status] ?? 'unknown',
      pair,
      price,
    }
  }
}

// =============================================================================
// SWEEP ENGINE
// =============================================================================

async function runSweep(pairs, options = {}) {
  const { dryRun = false, explore = false } = options
  const startTime = Date.now()

  const totalCost = pairs.length * COST_PER_QUERY
  printHeader(
    'ORACLE DOMINATOR — Price Sweep',
    `${pairs.length} pairs | ${totalCost} QU | ${dryRun ? 'DRY RUN' : 'LIVE'}`
  )

  // Balance check
  if (!dryRun) {
    const balance = await getBalance()
    console.log(`  Balance:    ${fmt(balance)} QU`)
    console.log(`  Cost:       ${fmt(totalCost)} QU`)
    console.log(`  Remaining:  ${fmt(balance - totalCost)} QU`)

    if (balance < totalCost + 100) {
      console.error(`  ERROR: Insufficient balance (need ${totalCost + 100} QU min)`)
      return { success: false, error: 'insufficient_balance' }
    }
  }

  // Get current tick
  const { tick: currentTick, epoch } = await getCurrentTick()
  console.log(`  Tick:       ${fmt(currentTick)}`)
  console.log(`  Epoch:      ${epoch}`)
  console.log()

  // Broadcast queries with tick staggering
  const results = []
  for (let i = 0; i < pairs.length; i++) {
    const pair = pairs[i]
    const targetTick = currentTick + 20 + (i * 3)
    const label = `[${i + 1}/${pairs.length}] ${pair.oracle} ${pair.currency1}/${pair.currency2}`

    if (dryRun) {
      console.log(`  [DRY] ${label} -> tick ${fmt(targetTick)}`)
      results.push({
        ...pair,
        targetTick,
        status: 'dry_run',
        timestamp: new Date().toISOString(),
      })
      continue
    }

    try {
      const res = await sendOracleQuery(pair.oracle, pair.currency1, pair.currency2, targetTick)
      const statusIcon = res.success ? '+' : '!'
      console.log(`  [${statusIcon}] ${label} -> tick ${fmt(targetTick)} (${res.peersBroadcasted} peers)`)
      results.push({
        ...pair,
        targetTick,
        status: 'broadcast',
        txId: res.txId,
        peersBroadcasted: res.peersBroadcasted,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      console.log(`  [X] ${label} -> ERROR: ${err.message}`)
      // Retry once
      try {
        await sleep(2000)
        const res = await sendOracleQuery(pair.oracle, pair.currency1, pair.currency2, targetTick + 5)
        console.log(`  [R] ${label} -> RETRY OK at tick ${fmt(targetTick + 5)}`)
        results.push({
          ...pair,
          targetTick: targetTick + 5,
          status: 'broadcast_retry',
          txId: res.txId,
          timestamp: new Date().toISOString(),
        })
      } catch (retryErr) {
        results.push({
          ...pair,
          targetTick,
          status: 'error',
          error: retryErr.message,
          timestamp: new Date().toISOString(),
        })
      }
    }

    // RPC pacing: 500ms between broadcasts
    if (i < pairs.length - 1 && !dryRun) {
      await sleep(500)
    }
  }

  const duration = Date.now() - startTime
  const success = results.filter(r => r.status === 'broadcast' || r.status === 'broadcast_retry').length
  const errors = results.filter(r => r.status === 'error').length

  // Summary
  console.log()
  console.log(`  ${'='.repeat(65)}`)
  console.log(`  SWEEP COMPLETE`)
  console.log(`  Success: ${success}/${pairs.length} | Errors: ${errors} | Time: ${(duration / 1000).toFixed(1)}s`)
  console.log(`  Cost:    ${success * COST_PER_QUERY} QU`)
  console.log(`  Ticks:   ${results[0]?.targetTick} - ${results[results.length - 1]?.targetTick}`)
  console.log()

  // Build sweep record
  const sweepRecord = {
    timestamp: new Date().toISOString(),
    epoch,
    startTick: currentTick,
    pairCount: pairs.length,
    successCount: success,
    errorCount: errors,
    costQU: success * COST_PER_QUERY,
    durationMs: duration,
    results,
  }

  // Save to rolling file
  if (!dryRun) {
    appendToRollingFile('oracle-price-history.json', sweepRecord, 500)
    console.log(`  Saved to oracle-price-history.json`)
  }

  return sweepRecord
}

// =============================================================================
// TCP VERIFICATION
// =============================================================================

async function verifySweep(startTick, tickCount = 60) {
  printHeader('ORACLE DOMINATOR — TCP Verification', `Ticks ${startTick} - ${startTick + tickCount}`)

  const NODE_IP = '45.152.160.217'
  const client = new VerifyClient(NODE_IP)

  try {
    console.log(`  Connecting to ${NODE_IP}...`)
    await client.connect()
    console.log(`  Connected`)
    console.log()

    let totalQueries = 0
    let successQueries = 0
    let prices = []

    for (let tick = startTick; tick < startTick + tickCount; tick++) {
      try {
        const ids = await client.getQueryIdsAtTick(tick)
        if (ids.length === 0) continue

        totalQueries += ids.length
        console.log(`  Tick ${fmt(tick)}: ${ids.length} queries`)

        for (const id of ids) {
          try {
            const info = await client.getQueryInfo(id)
            const status = info.statusStr
            const pairStr = info.pair ? `${info.pair.oracle} ${info.pair.currency1}/${info.pair.currency2}` : 'unknown'

            if (info.price !== null) {
              console.log(`    [${status.toUpperCase()}] ${pairStr} = ${info.price.toFixed(8)}`)
              successQueries++
              prices.push({
                tick,
                queryId: id,
                ...info.pair,
                price: info.price,
                status,
              })
            } else {
              console.log(`    [${status.toUpperCase()}] ${pairStr} (no price)`)
            }
          } catch (e) {
            console.log(`    Query ${id}: ${e.message}`)
          }
        }
      } catch (e) {
        // Skip ticks that fail
      }
    }

    console.log()
    console.log(`  ${'='.repeat(65)}`)
    console.log(`  VERIFICATION COMPLETE`)
    console.log(`  Total Queries:   ${totalQueries}`)
    console.log(`  With Price:      ${successQueries}`)
    console.log()

    // Print price summary + write to DB
    if (prices.length > 0) {
      console.log(`  PRICES COLLECTED:`)
      const byPair = {}
      for (const p of prices) {
        const key = `${p.oracle} ${p.currency1}/${p.currency2}`
        if (!byPair[key]) byPair[key] = []
        byPair[key].push(p.price)
      }
      for (const [pair, vals] of Object.entries(byPair)) {
        const avg = vals.reduce((a, b) => a + b, 0) / vals.length
        console.log(`    ${pair.padEnd(35)} ${avg.toFixed(8)}`)
      }

      // Dual-write: save verified prices to SQLite
      try {
        const dbRows = prices.map(p => ({
          pair: `${p.currency1}/${p.currency2}`,
          oracle: p.oracle,
          price: p.price,
          tick: p.tick,
          epoch: null,
          source: 'tcp-verify',
          timestamp: new Date().toISOString(),
        }))
        insertPricesBatch(dbRows)
        console.log(`  [DB] ${dbRows.length} prices saved to SQLite`)
      } catch (dbErr) {
        console.log(`  [DB] Write failed: ${dbErr.message}`)
      }
    }

    return { totalQueries, successQueries, prices }
  } finally {
    client.close()
  }
}

// =============================================================================
// MAIN
// =============================================================================

async function main() {
  loadEnv()

  const args = process.argv.slice(2)

  // --estimate: show costs only
  if (args.includes('--estimate')) {
    printHeader('ORACLE DOMINATOR — Cost Estimate')
    for (const tier of [1, 2, 3]) {
      const est = estimateCost(tier)
      console.log(`  Tier ${tier}: ${est.pairCount} pairs = ${est.costQU} QU`)
      for (const p of est.pairs) console.log(`    - ${p}`)
      console.log()
    }
    const total = estimateCost('all')
    console.log(`  ALL TIERS: ${total.pairCount} pairs = ${total.costQU} QU`)
    console.log()

    const balance = await getBalance()
    console.log(`  Current Balance: ${fmt(balance)} QU`)
    console.log(`  After Full Sweep: ${fmt(balance - total.costQU)} QU`)
    return
  }

  // --verify <tick>: TCP verification
  if (args.includes('--verify')) {
    const tickIdx = args.indexOf('--verify')
    const startTick = parseInt(args[tickIdx + 1], 10)
    if (!startTick) {
      console.error('Usage: --verify <startTick>')
      process.exit(1)
    }
    await verifySweep(startTick)
    return
  }

  // Parse tiers
  let pairs
  const dryRun = args.includes('--dry-run')
  const explore = args.includes('--explore')

  if (args.includes('--discover')) {
    pairs = [...DISCOVERY_PAIRS]
  } else if (args.includes('--working')) {
    pairs = [...WORKING_PAIRS]
  } else if (args.includes('--all')) {
    pairs = getPairsByTier('all')
  } else {
    const tierIdx = args.indexOf('--tier')
    if (tierIdx >= 0) {
      const tierStr = args[tierIdx + 1] || '1'
      const tiers = tierStr.split(',').map(Number)
      pairs = getPairsByTier(tiers)
    } else if (explore) {
      pairs = getPairsByTier('all')
    } else {
      // Default: show help
      console.log(`
  ORACLE DOMINATOR — Systematic Price Collector

  Usage:
    node ORACLE_DOMINATOR.mjs --estimate                Show cost breakdown
    node ORACLE_DOMINATOR.mjs --explore                 Test all pairs (200 QU)
    node ORACLE_DOMINATOR.mjs --working                 Only confirmed working pairs (60 QU)
    node ORACLE_DOMINATOR.mjs --discover                Test new pairs: mexc, altcoins (${DISCOVERY_PAIRS.length * 10} QU)
    node ORACLE_DOMINATOR.mjs --tier 1                  Core QUBIC (70 QU)
    node ORACLE_DOMINATOR.mjs --tier 1,2                Core + Majors (130 QU)
    node ORACLE_DOMINATOR.mjs --all                     All 20 pairs (200 QU)
    node ORACLE_DOMINATOR.mjs --all --dry-run           Simulate
    node ORACLE_DOMINATOR.mjs --verify <tick>           TCP verify past queries
    node ORACLE_DOMINATOR.mjs --loop --working --interval 30  Continuous
`)
      return
    }
  }

  // Loop mode
  const loop = args.includes('--loop')
  const intervalIdx = args.indexOf('--interval')
  const intervalMin = intervalIdx >= 0 ? parseInt(args[intervalIdx + 1], 10) : 30

  if (loop) {
    console.log(`  Continuous mode: ${pairs.length} pairs every ${intervalMin} minutes`)
    while (true) {
      await runSweep(pairs, { dryRun, explore })
      console.log(`  Next sweep in ${intervalMin} minutes...`)
      await sleep(intervalMin * 60 * 1000)
    }
  } else {
    await runSweep(pairs, { dryRun, explore })
  }
}

main().catch(err => {
  console.error('FATAL:', err.message)
  process.exit(1)
})
