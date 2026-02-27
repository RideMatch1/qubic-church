#!/usr/bin/env node
/**
 * ORACLE MONITOR — Persistent Live Daemon
 *
 * Runs continuously. Catches EVERY new oracle query within seconds.
 *
 * Architecture:
 *   1. Load existing data from previous scan (if any)
 *   2. Initial catchup: scan any ticks missed since last scan
 *   3. Enter live loop: every 3s, scan only NEW ticks
 *   4. Re-check pending queries for status changes
 *   5. Write JSON on every change → dashboard picks it up
 *
 * Usage:
 *   node ORACLE_MONITOR.mjs                  # Run forever
 *   node ORACLE_MONITOR.mjs --catchup-only   # Catchup + exit (no live loop)
 *   node ORACLE_MONITOR.mjs --reset          # Ignore existing data, full rescan
 */
import { createConnection } from 'net'
import { randomBytes } from 'crypto'
import { createRequire } from 'module'
import { writeFileSync, readFileSync, existsSync, statSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'
import { insertPrice } from './oracle-db.mjs'

const require = createRequire(import.meta.url)
const __dirname = dirname(fileURLToPath(import.meta.url))
const OUT = resolve(__dirname, '../public/data/oracle-live-queries.json')

// ─── DB Dual-Write: Dedup tracker ───────────────────────────────────
const _lastDbWrite = new Map() // pair → { price, timestamp }
const DB_WRITE_INTERVAL = 30000 // 30s minimum between writes per pair

// ─── Qubic Identity Conversion ─────────────────────────────────────
let _qubicHelper = null
async function pubKeyToIdentity(pubKeyBuffer) {
  try {
    if (!_qubicHelper) {
      const lib = require('@qubic-lib/qubic-ts-library').default
      _qubicHelper = new lib.QubicHelper()
    }
    const arr = Array.from(pubKeyBuffer)
    return await _qubicHelper.getIdentity(arr)
  } catch {
    return null
  }
}

// ─── Constants ──────────────────────────────────────────────────────
const STATUS = { 0: 'unknown', 1: 'pending', 2: 'committed', 3: 'success', 4: 'timeout', 5: 'unresolvable' }
const QUERY_TYPE = { 0: 'contract', 1: 'subscription', 2: 'user' }
const FLAGS = {
  0x001: 'INVALID_ORACLE', 0x002: 'ORACLE_UNAVAIL', 0x004: 'INVALID_TIME',
  0x008: 'INVALID_PLACE', 0x010: 'INVALID_ARG', 0x100: 'REPLY_RECEIVED',
  0x200: 'BAD_SIZE_REPLY', 0x400: 'OM_DISAGREE', 0x800: 'BAD_SIZE_REVEAL',
  0x1000: 'FAKE_COMMITS'
}
const SEAL_ORACLES = {
  genesis_1_3: 'I. BERESHIT', genesis_11_4: 'II. BABEL',
  genesis_28_12: 'III. SULLAM', exodus_3_14: 'IV. EHYEH',
  psalm_26_2: 'V. HOTAM', joel_2_31: 'VI. YOM ADONAI',
  revelation_22_13: 'VII. HOTAM ACHARON'
}
const NODES = [
  '45.152.160.217', '92.118.57.14', '95.217.142.179',
  '148.113.1.228', '91.210.226.146'
]

const POLL_INTERVAL = 3000    // 3s between incremental scans
const STATS_INTERVAL = 30000  // 30s between stats refreshes
const RECHECK_INTERVAL = 60000 // 60s between pending re-checks
const HEARTBEAT_WRITE = 10000 // 10s between file writes (keeps dashboard "LIVE")
const RECONNECT_DELAY = 2000

// ─── TCP Client (same proven protocol) ──────────────────────────────
function hdr(ps, t) {
  const b = Buffer.alloc(8), s = 8 + ps
  b[0] = s & 0xFF; b[1] = (s >> 8) & 0xFF; b[2] = (s >> 16) & 0xFF; b[3] = t
  randomBytes(4).copy(b, 4)
  return b
}

function decFlags(f) {
  return Object.entries(FLAGS).filter(([b]) => f & Number(b)).map(([, d]) => d)
}

// Interface names for display
const INTERFACE_NAMES = { 0: 'Price', 1: 'Mock' }

function decQuery(buf) {
  if (buf.length < 104) return null
  const oracle = buf.slice(0, 32).toString('ascii').replace(/\0/g, '')
  const dt = buf.readBigUInt64LE(32)
  const p = n => String(n).padStart(2, '0')
  const y = Number((dt >> 46n) & 0x3FFFFn), mo = Number((dt >> 42n) & 0xFn), d = Number((dt >> 37n) & 0x1Fn)
  const h = Number((dt >> 32n) & 0x1Fn), mi = Number((dt >> 26n) & 0x3Fn), s = Number((dt >> 20n) & 0x3Fn)
  return {
    oracle,
    timestamp: `${y}-${p(mo)}-${p(d)} ${p(h)}:${p(mi)}:${p(s)}`,
    currency1: buf.slice(40, 72).toString('ascii').replace(/\0/g, ''),
    currency2: buf.slice(72, 104).toString('ascii').replace(/\0/g, '')
  }
}

// Interface 1 (Mock) query: 8 bytes — single uint64 value
function decMockQuery(buf) {
  if (buf.length < 8) return null
  return { mockValue: Number(buf.readBigUInt64LE(0)) }
}

// Generic raw data decoder for unknown interfaces
function decRawQuery(buf) {
  if (!buf || buf.length === 0) return null
  return { rawHex: buf.toString('hex'), rawLength: buf.length }
}

function decRawReply(buf) {
  if (!buf || buf.length === 0) return null
  // Try numerator/denominator if >= 16 bytes (common pattern)
  if (buf.length >= 16) {
    const n = buf.readBigInt64LE(0), d = buf.readBigInt64LE(8)
    return {
      rawHex: buf.toString('hex'), rawLength: buf.length,
      numerator: Number(n), denominator: Number(d),
      price: d !== 0n ? Number(n) / Number(d) : 0
    }
  }
  return { rawHex: buf.toString('hex'), rawLength: buf.length }
}

function decReply(buf) {
  if (buf.length < 16) return null
  const n = buf.readBigInt64LE(0), d = buf.readBigInt64LE(8)
  return { numerator: Number(n), denominator: Number(d), price: d !== 0n ? Number(n) / Number(d) : 0 }
}

class TcpClient {
  constructor(ip) { this.ip = ip; this.b = Buffer.alloc(0); this.s = null; this.alive = false }

  connect() {
    return new Promise((ok, no) => {
      const t = setTimeout(() => no(new Error('connect timeout')), 10000)
      this.s = createConnection({ host: this.ip, port: 21841 }, () => {
        clearTimeout(t); this.alive = true; ok()
      })
      this.s.on('error', e => { clearTimeout(t); this.alive = false; no(e) })
      this.s.on('close', () => { this.alive = false })
      this.s.on('data', c => { this.b = Buffer.concat([this.b, c]) })
    })
  }

  close() { this.s?.destroy(); this.s = null; this.alive = false }

  send(d) {
    return new Promise((r, j) => {
      if (!this.s || !this.alive) return j(new Error('not connected'))
      this.s.write(d, e => e ? j(e) : r())
    })
  }

  async wait(n) {
    const s = Date.now()
    while (this.b.length < n) {
      if (Date.now() - s > 10000) throw new Error('timeout')
      if (!this.alive) throw new Error('disconnected')
      await new Promise(r => setTimeout(r, 10))
    }
  }

  take(n) { const r = this.b.slice(0, n); this.b = this.b.slice(n); return r }

  async msg() {
    await this.wait(8)
    const h = this.take(8)
    const sz = (h[0] | (h[1] << 8) | (h[2] << 16)) - 8
    const t = h[3]
    if (sz > 0) { await this.wait(sz); return { t, d: this.take(sz) } }
    return { t, d: Buffer.alloc(0) }
  }

  async resp() {
    for (let i = 0; i < 15; i++) {
      const m = await this.msg()
      if (m.t !== 0) return m
    }
    throw new Error('flood')
  }

  async req(t, p) {
    this.b = Buffer.alloc(0)
    await this.send(Buffer.concat([hdr(p.length, t), p]))
  }

  async getTick() {
    await this.req(27, Buffer.alloc(0))
    const m = await this.resp()
    return m.t === 28 ? { tick: m.d.readUInt32LE(4), epoch: m.d.readUInt16LE(2) } : null
  }

  async getStats() {
    const p = Buffer.alloc(16); p.writeUInt32LE(7, 0)
    await this.req(66, p)
    const m = await this.resp()
    if (m.t === 67 && m.d.readUInt32LE(0) === 7) {
      const d = m.d.slice(4); let o = 0
      const r = () => { const v = Number(d.readBigUInt64LE(o)); o += 8; return v }
      return {
        pendingCount: r(), pendingOracleMachineCount: r(), pendingCommitCount: r(),
        pendingRevealCount: r(), successfulCount: r(), revealTxCount: r(),
        unresolvableCount: r(), timeoutCount: r(), timeoutNoReplyCount: r(),
        timeoutNoCommitCount: r(), timeoutNoRevealCount: r(),
        oracleMachineRepliesDisagreeCount: r(), oracleMachineReplyAvgMilliTicksPerQuery: r(),
        commitAvgMilliTicksPerQuery: r(), successAvgMilliTicksPerQuery: r(),
        timeoutAvgMilliTicksPerQuery: r(), wrongKnowledgeProofCount: r()
      }
    }
    return null
  }

  async getTickRange() {
    const p = Buffer.alloc(16); p.writeUInt32LE(0, 0); p.writeBigInt64LE(1n, 8)
    await this.req(66, p)
    let tr = null
    while (true) {
      const m = await this.resp()
      if (m.t === 35) break
      if (m.t === 67 && m.d.readUInt32LE(0) === 9) {
        const d = m.d.slice(4)
        tr = { first: d.readUInt32LE(0), current: d.readUInt32LE(4) }
      }
    }
    return tr
  }

  async getQueryIdsAtTick(tick) {
    const p = Buffer.alloc(16); p.writeUInt32LE(0, 0); p.writeBigInt64LE(BigInt(tick), 8)
    await this.req(66, p)
    const ids = []
    while (true) {
      const m = await this.resp()
      if (m.t === 35) break
      if (m.t === 67 && m.d.readUInt32LE(0) === 0) {
        const d = m.d.slice(4)
        for (let i = 0; i < d.length; i += 8) ids.push(d.readBigInt64LE(i).toString())
      }
    }
    return ids
  }

  async getPendingIds() {
    const p = Buffer.alloc(16); p.writeUInt32LE(4, 0) // PENDING_QUERY_IDS
    await this.req(66, p)
    const ids = []
    while (true) {
      const m = await this.resp()
      if (m.t === 35) break
      if (m.t === 67 && m.d.readUInt32LE(0) === 0) {
        const d = m.d.slice(4)
        for (let i = 0; i < d.length; i += 8) ids.push(d.readBigInt64LE(i).toString())
      }
    }
    return ids
  }

  async getQueryInfo(qid) {
    const p = Buffer.alloc(16); p.writeUInt32LE(5, 0); p.writeBigInt64LE(BigInt(qid), 8)
    await this.req(66, p)
    let meta = null, qD = Buffer.alloc(0), rD = Buffer.alloc(0)
    while (true) {
      const m = await this.resp()
      if (m.t === 35) break
      if (m.t === 67) {
        const rt = m.d.readUInt32LE(0), d = m.d.slice(4)
        if (rt === 1) meta = {
          queryId: d.readBigInt64LE(0).toString(), type: d.readUInt8(8),
          status: d.readUInt8(9), statusFlags: d.readUInt16LE(10),
          queryTick: d.readUInt32LE(12),
          queryingEntity: d.slice(16, 48), // 32 bytes public key
          timeout: Number(d.readBigUInt64LE(48)),
          interfaceIndex: d.readUInt32LE(56), subscriptionId: d.readInt32LE(60),
          revealTick: d.readUInt32LE(64),
          totalCommits: d.readUInt16LE(68), agreeingCommits: d.readUInt16LE(70)
        }
        else if (rt === 2) qD = Buffer.concat([qD, d])
        else if (rt === 3) rD = Buffer.concat([rD, d])
      }
    }
    return { meta, qD, rD }
  }
}

// ─── Monitor State ──────────────────────────────────────────────────
let client = null
let knownQueries = new Map()  // queryId → entry
let lastScannedTick = 0
let currentEpoch = 0
let currentStats = null
let monitorStarted = null
let totalNewFound = 0

// ─── Connection Management ──────────────────────────────────────────
async function ensureConnected() {
  if (client?.alive) return

  for (const ip of NODES) {
    try {
      client?.close()
      client = new TcpClient(ip)
      await client.connect()
      log(`Connected: ${ip}`)
      return
    } catch { /* try next */ }
  }
  throw new Error('All nodes unreachable')
}

async function safeCall(fn) {
  try {
    await ensureConnected()
    return await fn(client)
  } catch (e) {
    if (e.message.includes('timeout') || e.message.includes('disconnect') || e.message.includes('not connected')) {
      client?.close()
      await sleep(RECONNECT_DELAY)
      await ensureConnected()
      return await fn(client)
    }
    throw e
  }
}

// ─── Build Query Entry ──────────────────────────────────────────────
async function buildEntry(qid, meta, qD, rD) {
  const status = STATUS[meta.status] || '?'
  const iface = meta.interfaceIndex
  const entry = {
    queryId: qid,
    tick: meta.queryTick,
    type: QUERY_TYPE[meta.type] || '?',
    status,
    statusFlags: decFlags(meta.statusFlags),
    interfaceIndex: iface,
    interfaceName: INTERFACE_NAMES[iface] || `Unknown(${iface})`,
    subscriptionId: meta.subscriptionId ?? 0,
    revealTick: meta.revealTick,
    totalCommits: meta.totalCommits,
    agreeingCommits: meta.agreeingCommits,
    firstSeen: new Date().toISOString(),
    lastUpdated: new Date().toISOString()
  }

  // Extract sender identity from queryingEntity (32-byte public key)
  if (meta.queryingEntity) {
    entry.senderPublicKey = Buffer.from(meta.queryingEntity).toString('hex')
    const identity = await pubKeyToIdentity(meta.queryingEntity)
    if (identity) entry.senderIdentity = identity
  }

  // Always store raw hex for all interfaces
  if (qD && qD.length > 0) entry.queryDataHex = qD.toString('hex')
  if (rD && rD.length > 0) entry.replyDataHex = rD.toString('hex')

  // Decode based on interface type
  if (iface === 0) {
    // Interface 0: Price Feed
    const q = decQuery(qD)
    const r = decReply(rD)
    if (q) {
      entry.oracle = q.oracle
      entry.queryTimestamp = q.timestamp
      entry.currency1 = q.currency1
      entry.currency2 = q.currency2
    }
    if (r) entry.reply = r
  } else if (iface === 1) {
    // Interface 1: Mock/Test
    const mq = decMockQuery(qD)
    if (mq) entry.mockValue = mq.mockValue
    // Mock reply uses same numerator/denominator format
    const r = decRawReply(rD)
    if (r?.numerator !== undefined) entry.reply = { numerator: r.numerator, denominator: r.denominator, price: r.price }
  } else {
    // Unknown interface — store raw decoded data
    const rq = decRawQuery(qD)
    if (rq) entry.queryRaw = rq
    const rr = decRawReply(rD)
    if (rr) entry.reply = rr
  }

  entry.isSeal = !!SEAL_ORACLES[entry.oracle]
  if (entry.isSeal) entry.sealName = SEAL_ORACLES[entry.oracle]
  return entry
}

// ─── Persistence ────────────────────────────────────────────────────
function loadExisting() {
  if (!existsSync(OUT)) return null
  try {
    const raw = readFileSync(OUT, 'utf-8')
    const data = JSON.parse(raw)
    if (data?.queries?.length > 0) return data
  } catch { /* corrupt file, ignore */ }
  return null
}

function saveState() {
  const queries = [...knownQueries.values()].sort((a, b) => a.tick - b.tick)

  // Count unique senders
  const senderMap = {}
  for (const q of queries) {
    const id = q.senderIdentity || q.senderPublicKey || 'unknown'
    senderMap[id] = (senderMap[id] || 0) + 1
  }
  const uniqueSenders = Object.keys(senderMap).filter(k => k !== 'unknown').length

  const out = {
    scanTimestamp: new Date().toISOString(),
    monitorMode: 'live',
    monitorStarted,
    monitorUptime: Math.round((Date.now() - new Date(monitorStarted).getTime()) / 1000),
    epoch: currentEpoch,
    currentTick: lastScannedTick,
    tickRange: { first: 0, current: lastScannedTick },
    stats: currentStats,
    totalOnChain: queries.length,
    sealsFound: queries.filter(q => q.isSeal).length,
    uniqueSenders,
    senderBreakdown: senderMap,
    newSinceMonitorStart: totalNewFound,
    queries
  }
  writeFileSync(OUT, JSON.stringify(out, null, 2))

  // ─── DB Dual-Write: Save successful prices to SQLite ──────────────
  try {
    const now = Date.now()
    let dbWrites = 0
    for (const q of queries) {
      if (q.interfaceIndex !== 0 || q.status !== 'success') continue
      if (!q.reply?.price || q.reply.price <= 0) continue
      if (!q.oracle || !q.currency1 || !q.currency2) continue

      const pair = `${q.currency1}/${q.currency2}`
      const last = _lastDbWrite.get(pair)

      // Skip if same price and within interval
      if (last && last.price === q.reply.price && (now - last.ts) < DB_WRITE_INTERVAL) continue

      insertPrice(q.oracle, pair, q.reply.price, q.tick, currentEpoch, 'live-monitor', new Date().toISOString())
      _lastDbWrite.set(pair, { price: q.reply.price, ts: now })
      dbWrites++
    }
    if (dbWrites > 0) log(`  [DB] ${dbWrites} prices → SQLite`)
  } catch (e) {
    log(`  [DB] Write error: ${e.message}`)
  }
}

// ─── Scan Ticks (incremental) ───────────────────────────────────────
async function scanTickRange(from, to) {
  let newIds = []

  for (let t = from; t <= to; t++) {
    try {
      const ids = await safeCall(c => c.getQueryIdsAtTick(t))
      for (const id of ids) {
        if (!knownQueries.has(id)) {
          newIds.push({ id, tick: t })
        }
      }
    } catch (e) {
      log(`  Tick ${t} error: ${e.message}`)
    }
  }

  return newIds
}

async function fetchQueryDetails(qid) {
  const { meta, qD, rD } = await safeCall(c => c.getQueryInfo(qid))
  if (!meta) return null
  return await buildEntry(qid, meta, qD, rD)
}

// ─── Gap Fill: find queries missing from tick scan ──────────────────
let gapFillScannedRanges = [] // Track which tick ranges we already scanned

async function gapFill(expectedTotal) {
  const delta = expectedTotal - knownQueries.size
  if (delta <= 0) return 0

  log(`Gap fill: ${delta} queries missing...`)
  let found = 0

  // Method 1: Check pending queries (fast, catches in-flight queries)
  try {
    const pendingIds = await safeCall(c => c.getPendingIds())
    if (pendingIds.length > 0) {
      log(`  Pending IDs from node: ${pendingIds.length}`)
    }
    for (const id of pendingIds) {
      const idStr = id.toString()
      if (!knownQueries.has(idStr)) {
        const entry = await fetchQueryDetails(idStr)
        if (entry) {
          knownQueries.set(idStr, entry)
          totalNewFound++
          found++
          logQuery(entry, 'GAP FILL')
        }
      }
    }
  } catch { /* pending might not be available */ }

  // Method 2: Scan dense tick clusters where queries are likely hiding
  // Find clusters of nearby ticks and scan around them
  if (found < delta) {
    const knownTicks = [...knownQueries.values()]
      .map(q => q.tick).filter(Boolean)
      .sort((a, b) => a - b)

    // Find clusters: group ticks that are within 100 ticks of each other
    const clusters = []
    let clusterStart = knownTicks[0], clusterEnd = knownTicks[0]
    for (let i = 1; i < knownTicks.length; i++) {
      if (knownTicks[i] - clusterEnd <= 100) {
        clusterEnd = knownTicks[i]
      } else {
        clusters.push([clusterStart - 10, clusterEnd + 10])
        clusterStart = knownTicks[i]
        clusterEnd = knownTicks[i]
      }
    }
    clusters.push([clusterStart - 10, clusterEnd + 10])

    for (const [cStart, cEnd] of clusters) {
      const alreadyScanned = gapFillScannedRanges.some(
        r => r[0] <= cStart && r[1] >= cEnd
      )
      if (alreadyScanned || found >= delta) continue

      const range = cEnd - cStart
      log(`  Scanning cluster: ${cStart} → ${cEnd} (${range} ticks)...`)
      for (let t = cStart; t <= cEnd && found < delta; t++) {
        try {
          const ids = await safeCall(c => c.getQueryIdsAtTick(t))
          for (const id of ids) {
            if (!knownQueries.has(id)) {
              const entry = await fetchQueryDetails(id)
              if (entry) {
                knownQueries.set(id, entry)
                totalNewFound++
                found++
                logQuery(entry, 'GAP FILL')
              }
            }
          }
        } catch { /* skip errors */ }
      }
      gapFillScannedRanges.push([cStart, cEnd])
    }
  }

  if (found > 0) {
    log(`Gap fill: recovered ${found}/${delta} queries`)
    saveState()
  } else if (delta > 0) {
    log(`  Gap fill: 0 recovered (${delta} still missing — may be outside scanned range)`)
  }
  return found
}

// ─── Re-check existing queries for status changes ───────────────────
async function recheckPending() {
  const pending = [...knownQueries.values()].filter(
    q => q.status === 'pending' || q.status === 'committed' || q.status === 'unknown'
  )
  if (pending.length === 0) return 0

  let updated = 0
  for (const q of pending) {
    try {
      const entry = await fetchQueryDetails(q.queryId)
      if (entry) {
        entry.firstSeen = q.firstSeen // preserve original firstSeen
        const changed = entry.status !== q.status || (!q.senderIdentity && entry.senderIdentity)
        if (changed) {
          knownQueries.set(q.queryId, entry)
          updated++
          if (entry.status !== q.status) logQuery(entry, 'STATUS CHANGE')
        }
      }
    } catch { /* skip on error */ }
  }
  return updated
}

// ─── Logging ────────────────────────────────────────────────────────
function log(msg) {
  const ts = new Date().toISOString().slice(11, 19)
  console.log(`[${ts}] ${msg}`)
}

function logQuery(entry, label = 'NEW') {
  const iface = entry.interfaceName || `IF:${entry.interfaceIndex}`
  const status = entry.status.padEnd(7)
  const sender = entry.senderIdentity ? ` from:${entry.senderIdentity.slice(0, 8)}...` : ''

  if (entry.interfaceIndex === 0) {
    // Price interface
    const oracle = (entry.oracle || '?').padEnd(22)
    const pair = `${entry.currency1 || '?'}/${entry.currency2 || '?'}`
    const reply = entry.reply?.denominator ? `-> ${entry.reply.price.toFixed(8)}` : '(no reply)'
    const seal = entry.isSeal ? ` [${entry.sealName}]` : ''
    log(`  ${label.padEnd(14)} [${status}] ${oracle} ${pair.padEnd(25)} tick:${entry.tick}  ${reply}${seal}${sender}`)
  } else if (entry.interfaceIndex === 1) {
    // Mock interface
    const val = entry.mockValue !== undefined ? `mock(${entry.mockValue})` : 'mock(?)'
    const reply = entry.reply?.denominator ? `-> ${entry.reply.numerator}/${entry.reply.denominator} = ${entry.reply.price}` : '(no reply)'
    log(`  ${label.padEnd(14)} [${status}] [${iface}] ${val.padEnd(20)} tick:${entry.tick}  ${reply}${sender}`)
  } else {
    // Unknown interface
    const hex = entry.queryDataHex ? `data:${entry.queryDataHex.slice(0, 32)}...` : 'no-data'
    log(`  ${label.padEnd(14)} [${status}] [${iface}] ${hex.padEnd(40)} tick:${entry.tick}${sender}`)
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }

// ─── Main ───────────────────────────────────────────────────────────
async function main() {
  const args = process.argv.slice(2)
  const catchupOnly = args.includes('--catchup-only')
  const reset = args.includes('--reset')

  monitorStarted = new Date().toISOString()
  log('=== ORACLE MONITOR STARTING ===')

  // Step 1: Connect
  await ensureConnected()
  const tickInfo = await safeCall(c => c.getTick())
  currentEpoch = tickInfo.epoch
  log(`Epoch: ${currentEpoch}, Current tick: ${tickInfo.tick.toLocaleString()}`)

  // Step 2: Get stats
  currentStats = await safeCall(c => c.getStats())
  const expectedTotal = currentStats
    ? currentStats.successfulCount + currentStats.timeoutCount + currentStats.unresolvableCount + currentStats.pendingCount
    : 0
  log(`Expected queries: ${expectedTotal}`)

  // Step 3: Get tick range
  const tr = await safeCall(c => c.getTickRange())
  if (!tr) { log('ERROR: No tick range'); process.exit(1) }
  log(`Tick range: ${tr.first.toLocaleString()} - ${tr.current.toLocaleString()} (${tr.current - tr.first} ticks)`)

  // Step 4: Load existing data
  let scanFrom = tr.first
  if (!reset) {
    const existing = loadExisting()
    if (existing?.queries?.length > 0) {
      log(`Loaded ${existing.queries.length} existing queries from previous scan`)
      for (const q of existing.queries) {
        knownQueries.set(q.queryId, q)
      }
      // Start scanning from the highest known tick + 1
      const maxTick = Math.max(...existing.queries.map(q => q.tick))
      if (maxTick > tr.first) {
        scanFrom = maxTick + 1
        lastScannedTick = maxTick
        log(`Resuming from tick ${scanFrom.toLocaleString()} (skipping ${scanFrom - tr.first} already-scanned ticks)`)
      }
    }
  } else {
    log('Reset mode: ignoring existing data')
  }

  // Step 5: Catchup scan — cover any ticks we missed
  const catchupEnd = tr.current
  const catchupRange = catchupEnd - scanFrom
  if (catchupRange > 0) {
    log(`\nCatchup: scanning ${catchupRange.toLocaleString()} ticks (${scanFrom} → ${catchupEnd})...`)
    const t0 = Date.now()
    let emptyStreak = 0

    for (let t = scanFrom; t <= catchupEnd; t++) {
      try {
        const ids = await safeCall(c => c.getQueryIdsAtTick(t))
        if (ids.length > 0) {
          emptyStreak = 0
          for (const id of ids) {
            if (!knownQueries.has(id)) {
              const entry = await fetchQueryDetails(id)
              if (entry) {
                knownQueries.set(id, entry)
                totalNewFound++
                logQuery(entry)
                saveState() // Write immediately on new discovery
              }
            }
          }
        } else {
          emptyStreak++
        }

        // Early exit if we found all expected + buffer
        if (knownQueries.size >= expectedTotal && emptyStreak > 200) {
          log(`  All ${expectedTotal} found + 200 empty buffer → catchup done`)
          lastScannedTick = t
          break
        }

        lastScannedTick = t

        // Progress indicator
        if ((t - scanFrom) % 500 === 0 && t > scanFrom) {
          const pct = ((t - scanFrom) / catchupRange * 100).toFixed(1)
          process.stderr.write(`  ${pct}% (${knownQueries.size} queries)    \r`)
        }
      } catch (e) {
        log(`  Tick ${t} error: ${e.message}`)
      }
    }

    const dur = ((Date.now() - t0) / 1000).toFixed(1)
    log(`Catchup complete: ${knownQueries.size} queries in ${dur}s`)
  } else {
    log('No catchup needed — already up to date')
    lastScannedTick = catchupEnd
  }

  // Save after catchup
  saveState()
  log(`\n=== ${knownQueries.size} queries tracked (${[...knownQueries.values()].filter(q => q.isSeal).length}/7 Seals) ===`)

  if (catchupOnly) {
    client?.close()
    log('Catchup-only mode. Exiting.')
    return
  }

  // ─── Step 6: Live Monitor Loop ──────────────────────────────────
  log('\n--- LIVE MONITORING ACTIVE ---')
  log(`  Poll: every ${POLL_INTERVAL / 1000}s | Stats: every ${STATS_INTERVAL / 1000}s | Recheck: every ${RECHECK_INTERVAL / 1000}s`)

  let lastStatsTime = Date.now()
  let lastRecheckTime = Date.now()
  let lastWriteTime = Date.now()
  let loopCount = 0

  while (true) {
    await sleep(POLL_INTERVAL)
    loopCount++

    try {
      // Get current tick
      const { tick: nowTick } = await safeCall(c => c.getTick())
      const newTicks = nowTick - lastScannedTick

      if (newTicks > 0) {
        // Scan new ticks
        const newIds = await scanTickRange(lastScannedTick + 1, nowTick)

        if (newIds.length > 0) {
          log(`\n>>> ${newIds.length} NEW QUERY(S) DETECTED! <<<`)
          for (const { id } of newIds) {
            const entry = await fetchQueryDetails(id)
            if (entry) {
              knownQueries.set(id, entry)
              totalNewFound++
              logQuery(entry)
            }
          }
          saveState()
        }

        lastScannedTick = nowTick
      }

      // Periodic stats refresh
      if (Date.now() - lastStatsTime > STATS_INTERVAL) {
        currentStats = await safeCall(c => c.getStats())
        lastStatsTime = Date.now()
        const expected = currentStats
          ? currentStats.successfulCount + currentStats.timeoutCount + currentStats.unresolvableCount + currentStats.pendingCount
          : 0
        if (expected !== knownQueries.size) {
          log(`Stats: expected=${expected} tracked=${knownQueries.size} (delta: ${expected - knownQueries.size})`)
          // Gap fill: try to recover missing queries
          if (expected > knownQueries.size) {
            await gapFill(expected)
          }
        }
        saveState() // Update stats in output
      }

      // Periodic re-check of pending/committed queries
      if (Date.now() - lastRecheckTime > RECHECK_INTERVAL) {
        const updated = await recheckPending()
        lastRecheckTime = Date.now()
        if (updated > 0) {
          log(`Re-check: ${updated} status change(s)`)
          saveState()
          lastWriteTime = Date.now()
        }
      }

      // Periodic heartbeat write — keeps dashboard "LIVE" indicator green
      if (Date.now() - lastWriteTime > HEARTBEAT_WRITE) {
        saveState()
        lastWriteTime = Date.now()
      }

      // Periodic heartbeat log (every 20 loops = ~60s)
      if (loopCount % 20 === 0) {
        const uptime = Math.round((Date.now() - new Date(monitorStarted).getTime()) / 1000)
        const h = Math.floor(uptime / 3600)
        const m = Math.floor((uptime % 3600) / 60)
        const s = uptime % 60
        log(`Heartbeat: tick ${nowTick.toLocaleString()} | ${knownQueries.size} queries | +${totalNewFound} new | uptime ${h}h${m}m${s}s`)
      }

    } catch (e) {
      log(`Loop error: ${e.message}`)
      client?.close()
      await sleep(RECONNECT_DELAY)
    }
  }
}

// ─── Graceful Shutdown ──────────────────────────────────────────────
process.on('SIGINT', () => {
  log('\nShutting down...')
  saveState()
  client?.close()
  log(`Final: ${knownQueries.size} queries tracked, ${totalNewFound} new since start`)
  process.exit(0)
})

process.on('SIGTERM', () => {
  saveState()
  client?.close()
  process.exit(0)
})

main().catch(e => { log(`FATAL: ${e.message}`); process.exit(1) })
