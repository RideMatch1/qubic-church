#!/usr/bin/env node
/**
 * ORACLE HEARTBEAT — Deep Protocol Scanner
 *
 * 0 QU cost — pure TCP-based protocol analysis.
 * Connects to multiple Qubic Core nodes, collects oracle statistics,
 * compares across nodes, detects anomalies, and outputs health data.
 *
 * Usage:
 *   node ORACLE_HEARTBEAT.mjs                         # Single scan, console
 *   node ORACLE_HEARTBEAT.mjs --json                  # Save to oracle-heartbeat.json
 *   node ORACLE_HEARTBEAT.mjs --loop --interval 60    # Continuous (60s)
 *   node ORACLE_HEARTBEAT.mjs --deep                  # +500 tick scan
 */

import { createConnection } from 'net'
import { randomBytes } from 'crypto'
import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'fs'
import { resolve, dirname, join } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const DATA_DIR = resolve(__dirname, '../public/data')

// =============================================================================
// PROTOCOL CONSTANTS (from network_message_type.h)
// =============================================================================

const MSG = {
  EXCHANGE_PUBLIC_PEERS: 0,
  REQUEST_CURRENT_TICK_INFO: 27,
  RESPOND_CURRENT_TICK_INFO: 28,
  END_RESPONSE: 35,
  REQUEST_ORACLE_DATA: 66,
  RESPOND_ORACLE_DATA: 67,
}

const REQ = {
  ALL_QUERY_IDS_BY_TICK: 0,
  USER_QUERY_IDS_BY_TICK: 1,
  PENDING_QUERY_IDS: 4,
  QUERY_AND_RESPONSE: 5,
  QUERY_STATISTICS: 7,
  ORACLE_REVENUE_POINTS: 8,
}

const RES = {
  QUERY_IDS: 0,
  QUERY_METADATA: 1,
  QUERY_DATA: 2,
  REPLY_DATA: 3,
  QUERY_STATISTICS: 7,
  ORACLE_REVENUE_POINTS: 8,
  TICK_RANGE: 9,
}

const STATUS_NAMES = {
  0: 'unknown',
  1: 'pending',
  2: 'committed',
  3: 'success',
  4: 'timeout',
  5: 'unresolvable',
}

// Known public Qubic nodes
const NODES = [
  '45.152.160.217',
  '92.118.57.14',
  '95.217.142.179',
  '148.251.184.163',
  '5.9.1.90',
]

// =============================================================================
// TCP CLIENT (streamlined from ORACLE_TCP_CLIENT.mjs)
// =============================================================================

function buildHeader(payloadSize, type) {
  const totalSize = 8 + payloadSize
  const buf = Buffer.alloc(8)
  buf[0] = totalSize & 0xFF
  buf[1] = (totalSize >> 8) & 0xFF
  buf[2] = (totalSize >> 16) & 0xFF
  buf[3] = type
  randomBytes(4).copy(buf, 4)
  return buf
}

function buildOracleRequest(reqType, reqTickOrId = 0n) {
  const buf = Buffer.alloc(16)
  buf.writeUInt32LE(reqType, 0)
  buf.writeUInt32LE(0, 4)
  buf.writeBigInt64LE(BigInt(reqTickOrId), 8)
  return buf
}

class HeartbeatClient {
  constructor(ip, port = 21841, timeout = 8000) {
    this.ip = ip
    this.port = port
    this.timeout = timeout
    this.socket = null
    this.buffer = Buffer.alloc(0)
    this.latencyMs = 0
  }

  connect() {
    const start = Date.now()
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('timeout')), this.timeout)
      this.socket = createConnection({ host: this.ip, port: this.port }, () => {
        clearTimeout(timer)
        this.latencyMs = Date.now() - start
        resolve()
      })
      this.socket.on('error', (err) => { clearTimeout(timer); reject(err) })
      this.socket.on('data', (chunk) => {
        this.buffer = Buffer.concat([this.buffer, chunk])
      })
    })
  }

  close() {
    if (this.socket) { this.socket.destroy(); this.socket = null }
  }

  send(buf) {
    return new Promise((resolve, reject) => {
      if (!this.socket) return reject(new Error('not connected'))
      this.socket.write(buf, (err) => err ? reject(err) : resolve())
    })
  }

  async waitFor(bytes, ms = 8000) {
    const start = Date.now()
    while (this.buffer.length < bytes) {
      if (Date.now() - start > ms) throw new Error(`timeout waiting for ${bytes}B`)
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

  async readMsgSkipPeers() {
    for (let i = 0; i < 10; i++) {
      const msg = await this.readMsg()
      if (msg.type !== MSG.EXCHANGE_PUBLIC_PEERS) return msg
    }
    throw new Error('too many peer exchanges')
  }

  async readMultiResponse() {
    const messages = []
    while (true) {
      const msg = await this.readMsgSkipPeers()
      if (msg.type === MSG.END_RESPONSE) break
      messages.push(msg)
    }
    return messages
  }

  async getCurrentTick() {
    this.buffer = Buffer.alloc(0)
    await this.send(buildHeader(0, MSG.REQUEST_CURRENT_TICK_INFO))
    const msg = await this.readMsgSkipPeers()
    if (msg.type === MSG.RESPOND_CURRENT_TICK_INFO) {
      return {
        tick: msg.payload.readUInt32LE(4),
        epoch: msg.payload.readUInt16LE(2),
        tickDuration: msg.payload.readUInt16LE(0),
      }
    }
    throw new Error(`unexpected type ${msg.type}`)
  }

  async getOracleStats() {
    const payload = buildOracleRequest(REQ.QUERY_STATISTICS)
    this.buffer = Buffer.alloc(0)
    await this.send(Buffer.concat([buildHeader(16, MSG.REQUEST_ORACLE_DATA), payload]))
    const msg = await this.readMsgSkipPeers()
    if (msg.type === MSG.RESPOND_ORACLE_DATA) {
      const resType = msg.payload.readUInt32LE(0)
      if (resType === RES.QUERY_STATISTICS) {
        return parseQueryStatistics(msg.payload.slice(4))
      }
    }
    throw new Error(`unexpected stats response`)
  }

  async getPendingQueryIds() {
    const payload = buildOracleRequest(REQ.PENDING_QUERY_IDS)
    this.buffer = Buffer.alloc(0)
    await this.send(Buffer.concat([buildHeader(16, MSG.REQUEST_ORACLE_DATA), payload]))
    const ids = []
    const msgs = await this.readMultiResponse()
    for (const msg of msgs) {
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

  async getTickRange() {
    // Request query IDs at tick 1 to get tick range info
    const payload = buildOracleRequest(REQ.ALL_QUERY_IDS_BY_TICK, 1n)
    this.buffer = Buffer.alloc(0)
    await this.send(Buffer.concat([buildHeader(16, MSG.REQUEST_ORACLE_DATA), payload]))
    const msgs = await this.readMultiResponse()
    for (const msg of msgs) {
      if (msg.type === MSG.RESPOND_ORACLE_DATA) {
        const resType = msg.payload.readUInt32LE(0)
        if (resType === RES.TICK_RANGE) {
          const data = msg.payload.slice(4)
          return {
            firstTick: data.readUInt32LE(0),
            currentTick: data.readUInt32LE(4),
          }
        }
      }
    }
    return null
  }

  async getRevenuePoints() {
    const payload = buildOracleRequest(REQ.ORACLE_REVENUE_POINTS)
    this.buffer = Buffer.alloc(0)
    await this.send(Buffer.concat([buildHeader(16, MSG.REQUEST_ORACLE_DATA), payload]))
    try {
      const msg = await this.readMsgSkipPeers()
      if (msg.type === MSG.RESPOND_ORACLE_DATA) {
        const resType = msg.payload.readUInt32LE(0)
        if (resType === RES.ORACLE_REVENUE_POINTS) {
          return parseRevenuePoints(msg.payload.slice(4))
        }
      }
    } catch {
      return null // Not all nodes support this
    }
    return null
  }

  async getQueryIdsAtTick(tick) {
    const payload = buildOracleRequest(REQ.ALL_QUERY_IDS_BY_TICK, BigInt(tick))
    this.buffer = Buffer.alloc(0)
    await this.send(Buffer.concat([buildHeader(16, MSG.REQUEST_ORACLE_DATA), payload]))
    const ids = []
    const msgs = await this.readMultiResponse()
    for (const msg of msgs) {
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
}

// =============================================================================
// PARSERS
// =============================================================================

function parseQueryStatistics(buf) {
  let offset = 0
  const read64 = () => { const v = Number(buf.readBigUInt64LE(offset)); offset += 8; return v }
  return {
    pendingCount: read64(),
    pendingOracleMachineCount: read64(),
    pendingCommitCount: read64(),
    pendingRevealCount: read64(),
    successfulCount: read64(),
    revealTxCount: read64(),
    unresolvableCount: read64(),
    timeoutCount: read64(),
    timeoutNoReplyCount: read64(),
    timeoutNoCommitCount: read64(),
    timeoutNoRevealCount: read64(),
    oracleMachineRepliesDisagreeCount: read64(),
    oracleMachineReplyAvgMilliTicksPerQuery: read64(),
    commitAvgMilliTicksPerQuery: read64(),
    successAvgMilliTicksPerQuery: read64(),
    timeoutAvgMilliTicksPerQuery: read64(),
    wrongKnowledgeProofCount: read64(),
  }
}

function parseRevenuePoints(buf) {
  // Revenue points are an array of uint64 per computor (676 entries)
  const points = []
  for (let i = 0; i < buf.length && i < 676 * 8; i += 8) {
    points.push(Number(buf.readBigUInt64LE(i)))
  }
  const totalRevenue = points.reduce((a, b) => a + b, 0)
  const activeComputors = points.filter(p => p > 0).length
  return { totalRevenue, activeComputors, topComputors: getTopN(points, 10) }
}

function getTopN(arr, n) {
  return arr
    .map((v, i) => ({ computor: i, revenue: v }))
    .filter(x => x.revenue > 0)
    .sort((a, b) => b.revenue - a.revenue)
    .slice(0, n)
}

// =============================================================================
// MULTI-NODE SCANNER
// =============================================================================

async function scanNode(ip) {
  const client = new HeartbeatClient(ip)
  const result = {
    ip,
    status: 'offline',
    latencyMs: 0,
    tick: 0,
    epoch: 0,
    tickDuration: 0,
    stats: null,
    pendingIds: [],
    tickRange: null,
    revenuePoints: null,
    error: null,
  }

  try {
    await client.connect()
    result.latencyMs = client.latencyMs
    result.status = 'connected'

    // Get tick info
    const tickInfo = await client.getCurrentTick()
    result.tick = tickInfo.tick
    result.epoch = tickInfo.epoch
    result.tickDuration = tickInfo.tickDuration

    // Get oracle stats
    try {
      result.stats = await client.getOracleStats()
    } catch (e) {
      result.error = `stats: ${e.message}`
    }

    // Get pending queries
    try {
      result.pendingIds = await client.getPendingQueryIds()
    } catch (e) {
      // Non-critical
    }

    // Get tick range
    try {
      result.tickRange = await client.getTickRange()
    } catch (e) {
      // Non-critical
    }

    // Get revenue points
    try {
      result.revenuePoints = await client.getRevenuePoints()
    } catch (e) {
      // Not all nodes support this
    }

  } catch (e) {
    result.error = e.message
    result.status = 'offline'
  } finally {
    client.close()
  }

  return result
}

async function scanAllNodes(nodeIps) {
  const startTime = Date.now()
  const results = await Promise.allSettled(nodeIps.map(ip => scanNode(ip)))

  const nodes = results.map((r, i) => {
    if (r.status === 'fulfilled') return r.value
    return { ip: nodeIps[i], status: 'error', error: r.reason?.message, tick: 0, epoch: 0 }
  })

  const duration = Date.now() - startTime
  return { nodes, scanDurationMs: duration }
}

// =============================================================================
// CROSS-NODE ANALYSIS
// =============================================================================

function analyzeNodes(nodes) {
  const connected = nodes.filter(n => n.status === 'connected')
  const ticks = connected.map(n => n.tick).filter(t => t > 0)
  const epochs = connected.map(n => n.epoch).filter(e => e > 0)

  // Tick drift (max difference between nodes)
  const maxTick = Math.max(...ticks, 0)
  const minTick = Math.min(...ticks, Infinity)
  const tickDrift = ticks.length > 1 ? maxTick - minTick : 0

  // Consensus tick (most common)
  const tickCounts = {}
  for (const t of ticks) tickCounts[t] = (tickCounts[t] || 0) + 1
  const consensusTick = Object.entries(tickCounts).sort((a, b) => b[1] - a[1])[0]?.[0] ?? 0

  // Stats comparison
  const allStats = connected.filter(n => n.stats).map(n => n.stats)
  const statsDisagreements = findStatsDisagreements(allStats)

  // Aggregate stats (from first available node)
  const primaryStats = allStats[0] ?? null

  // Pending queries (union across all nodes)
  const allPending = new Set()
  for (const n of connected) {
    for (const id of n.pendingIds) allPending.add(id)
  }

  // Tick range
  const tickRanges = connected.filter(n => n.tickRange).map(n => n.tickRange)
  const latestRange = tickRanges[0] ?? null

  // Revenue
  const revenue = connected.find(n => n.revenuePoints)?.revenuePoints ?? null

  // Compute success rate
  let successRate = 0
  if (primaryStats) {
    const total = primaryStats.successfulCount + primaryStats.timeoutCount + primaryStats.unresolvableCount
    successRate = total > 0 ? (primaryStats.successfulCount / total * 100) : 0
  }

  return {
    nodesTotal: nodes.length,
    nodesConnected: connected.length,
    nodesOffline: nodes.length - connected.length,
    consensusTick: Number(consensusTick),
    currentEpoch: epochs[0] ?? 0,
    tickDrift,
    stats: primaryStats,
    successRate: Math.round(successRate * 100) / 100,
    pendingCount: allPending.size,
    pendingIds: [...allPending],
    tickRange: latestRange,
    revenue,
    statsDisagreements,
    nodeDetails: nodes.map(n => ({
      ip: n.ip,
      status: n.status,
      latencyMs: n.latencyMs ?? 0,
      tick: n.tick,
      epoch: n.epoch,
      error: n.error,
    })),
  }
}

function findStatsDisagreements(statsArr) {
  if (statsArr.length < 2) return []
  const disagreements = []
  const keys = Object.keys(statsArr[0] || {})
  for (const key of keys) {
    const values = statsArr.map(s => s[key])
    const uniqueValues = [...new Set(values)]
    if (uniqueValues.length > 1) {
      disagreements.push({ metric: key, values })
    }
  }
  return disagreements
}

// =============================================================================
// ANOMALY DETECTION
// =============================================================================

function detectAnomalies(analysis) {
  const anomalies = []

  // CRITICAL: Few nodes reachable
  if (analysis.nodesConnected < 2) {
    anomalies.push({
      severity: 'CRITICAL',
      type: 'low_connectivity',
      message: `Only ${analysis.nodesConnected}/${analysis.nodesTotal} nodes reachable`,
    })
  }

  // CRITICAL: Very low success rate
  if (analysis.stats && analysis.successRate < 50) {
    anomalies.push({
      severity: 'CRITICAL',
      type: 'low_success_rate',
      message: `Oracle success rate critically low: ${analysis.successRate}%`,
    })
  }

  // WARNING: Significant tick drift
  if (analysis.tickDrift > 5) {
    anomalies.push({
      severity: 'WARNING',
      type: 'tick_drift',
      message: `Tick drift between nodes: ${analysis.tickDrift} ticks`,
    })
  }

  // WARNING: Large pending backlog
  if (analysis.pendingCount > 10) {
    anomalies.push({
      severity: 'WARNING',
      type: 'pending_backlog',
      message: `${analysis.pendingCount} queries pending — possible congestion`,
    })
  }

  // WARNING: Stats disagree between nodes
  if (analysis.statsDisagreements.length > 0) {
    anomalies.push({
      severity: 'WARNING',
      type: 'stats_disagreement',
      message: `${analysis.statsDisagreements.length} stats metrics differ between nodes`,
    })
  }

  // INFO: Success rate below 90%
  if (analysis.stats && analysis.successRate >= 50 && analysis.successRate < 90) {
    anomalies.push({
      severity: 'INFO',
      type: 'moderate_success_rate',
      message: `Oracle success rate: ${analysis.successRate}% (below 90%)`,
    })
  }

  // INFO: Wrong knowledge proofs
  if (analysis.stats && analysis.stats.wrongKnowledgeProofCount > 0) {
    anomalies.push({
      severity: 'INFO',
      type: 'wrong_knowledge_proof',
      message: `${analysis.stats.wrongKnowledgeProofCount} wrong knowledge proofs detected`,
    })
  }

  // INFO: Oracle machines disagree
  if (analysis.stats && analysis.stats.oracleMachineRepliesDisagreeCount > 0) {
    anomalies.push({
      severity: 'INFO',
      type: 'om_disagreement',
      message: `${analysis.stats.oracleMachineRepliesDisagreeCount} oracle machine disagreements`,
    })
  }

  // INFO: Some nodes offline
  if (analysis.nodesOffline > 0 && analysis.nodesConnected >= 2) {
    anomalies.push({
      severity: 'INFO',
      type: 'partial_connectivity',
      message: `${analysis.nodesOffline}/${analysis.nodesTotal} nodes unreachable`,
    })
  }

  return anomalies
}

// =============================================================================
// DEEP SCAN (optional: scan recent ticks for queries)
// =============================================================================

async function deepScan(nodeIp, tickRange, limit = 500) {
  const client = new HeartbeatClient(nodeIp, 21841, 15000)
  const results = { ticksScanned: 0, queriesFound: 0, ticksWithQueries: [] }

  try {
    await client.connect()
    const endTick = tickRange.currentTick
    const startTick = Math.max(tickRange.firstTick, endTick - limit)

    for (let t = endTick; t >= startTick; t--) {
      try {
        const ids = await client.getQueryIdsAtTick(t)
        results.ticksScanned++
        if (ids.length > 0) {
          results.queriesFound += ids.length
          results.ticksWithQueries.push({ tick: t, queryCount: ids.length, queryIds: ids })
        }
      } catch {
        // Skip failed ticks
      }

      // Progress
      if (results.ticksScanned % 50 === 0) {
        process.stdout.write(`  Deep scan: ${results.ticksScanned}/${endTick - startTick} ticks...\r`)
      }
    }
    console.log(`  Deep scan complete: ${results.ticksScanned} ticks, ${results.queriesFound} queries`)
  } catch (e) {
    console.error(`  Deep scan error: ${e.message}`)
  } finally {
    client.close()
  }

  return results
}

// =============================================================================
// OUTPUT
// =============================================================================

function computeHealthScore(analysis, anomalies) {
  let score = 100

  for (const a of anomalies) {
    if (a.severity === 'CRITICAL') score -= 30
    if (a.severity === 'WARNING') score -= 10
    if (a.severity === 'INFO') score -= 2
  }

  // Bonus for high connectivity
  if (analysis.nodesConnected >= 4) score = Math.min(100, score + 5)

  return Math.max(0, Math.min(100, score))
}

function buildSnapshot(analysis, anomalies, deepScanResult, scanDurationMs) {
  const healthScore = computeHealthScore(analysis, anomalies)
  return {
    timestamp: new Date().toISOString(),
    healthScore,
    scanDurationMs,
    network: {
      nodesTotal: analysis.nodesTotal,
      nodesConnected: analysis.nodesConnected,
      consensusTick: analysis.consensusTick,
      currentEpoch: analysis.currentEpoch,
      tickDrift: analysis.tickDrift,
      tickRange: analysis.tickRange,
    },
    oracle: {
      successRate: analysis.successRate,
      stats: analysis.stats,
      pendingCount: analysis.pendingCount,
      pendingIds: analysis.pendingIds,
      revenue: analysis.revenue,
    },
    anomalies,
    nodes: analysis.nodeDetails,
    deepScan: deepScanResult,
  }
}

function printSnapshot(snapshot) {
  const s = snapshot
  const bar = '='.repeat(65)

  console.log()
  console.log(`  ${bar}`)
  console.log(`  ORACLE HEARTBEAT — Protocol Health Monitor`)
  console.log(`  ${bar}`)
  console.log()
  console.log(`  Health Score:  ${s.healthScore}/100`)
  console.log(`  Scan Time:     ${s.scanDurationMs}ms`)
  console.log(`  Timestamp:     ${s.timestamp}`)
  console.log()

  // Network
  console.log(`  NETWORK`)
  console.log(`  Nodes:         ${s.network.nodesConnected}/${s.network.nodesTotal} connected`)
  console.log(`  Consensus:     Tick ${s.network.consensusTick?.toLocaleString()}`)
  console.log(`  Epoch:         ${s.network.currentEpoch}`)
  console.log(`  Tick Drift:    ${s.network.tickDrift}`)
  if (s.network.tickRange) {
    console.log(`  Data Range:    ${s.network.tickRange.firstTick?.toLocaleString()} - ${s.network.tickRange.currentTick?.toLocaleString()}`)
  }
  console.log()

  // Oracle Stats
  if (s.oracle.stats) {
    const st = s.oracle.stats
    const total = st.successfulCount + st.timeoutCount + st.unresolvableCount
    console.log(`  ORACLE STATISTICS`)
    console.log(`  Success Rate:  ${s.oracle.successRate}% (${st.successfulCount}/${total})`)
    console.log(`  Successful:    ${st.successfulCount}`)
    console.log(`  Timeouts:      ${st.timeoutCount} (no reply: ${st.timeoutNoReplyCount}, no commit: ${st.timeoutNoCommitCount}, no reveal: ${st.timeoutNoRevealCount})`)
    console.log(`  Unresolvable:  ${st.unresolvableCount}`)
    console.log(`  Pending:       ${st.pendingCount} (OM: ${st.pendingOracleMachineCount}, commit: ${st.pendingCommitCount}, reveal: ${st.pendingRevealCount})`)
    console.log(`  OM Disagree:   ${st.oracleMachineRepliesDisagreeCount}`)
    console.log(`  Wrong KP:      ${st.wrongKnowledgeProofCount}`)
    console.log(`  Avg Latency:   OM ${(st.oracleMachineReplyAvgMilliTicksPerQuery / 1000).toFixed(1)} ticks, Success ${(st.successAvgMilliTicksPerQuery / 1000).toFixed(1)} ticks`)
    console.log()
  }

  // Pending
  if (s.oracle.pendingCount > 0) {
    console.log(`  PENDING QUERIES: ${s.oracle.pendingCount}`)
    for (const id of s.oracle.pendingIds.slice(0, 10)) {
      console.log(`    - ${id}`)
    }
    if (s.oracle.pendingIds.length > 10) {
      console.log(`    ... and ${s.oracle.pendingIds.length - 10} more`)
    }
    console.log()
  }

  // Revenue
  if (s.oracle.revenue) {
    console.log(`  COMPUTOR REVENUE`)
    console.log(`  Total Points:   ${s.oracle.revenue.totalRevenue?.toLocaleString()}`)
    console.log(`  Active Computors: ${s.oracle.revenue.activeComputors}/676`)
    if (s.oracle.revenue.topComputors?.length > 0) {
      console.log(`  Top Earners:`)
      for (const c of s.oracle.revenue.topComputors.slice(0, 5)) {
        console.log(`    Computor #${c.computor}: ${c.revenue?.toLocaleString()} pts`)
      }
    }
    console.log()
  }

  // Nodes
  console.log(`  NODE STATUS`)
  for (const n of s.nodes) {
    const icon = n.status === 'connected' ? '+' : '-'
    const lat = n.latencyMs ? `${n.latencyMs}ms` : '--'
    const tick = n.tick ? n.tick.toLocaleString() : '--'
    console.log(`  [${icon}] ${n.ip.padEnd(18)} tick: ${tick.padEnd(12)} latency: ${lat.padEnd(8)} ${n.error || ''}`)
  }
  console.log()

  // Deep Scan
  if (s.deepScan) {
    console.log(`  DEEP SCAN`)
    console.log(`  Ticks Scanned:   ${s.deepScan.ticksScanned}`)
    console.log(`  Queries Found:   ${s.deepScan.queriesFound}`)
    if (s.deepScan.ticksWithQueries?.length > 0) {
      console.log(`  Recent Activity:`)
      for (const t of s.deepScan.ticksWithQueries.slice(0, 10)) {
        console.log(`    Tick ${t.tick.toLocaleString()}: ${t.queryCount} queries`)
      }
    }
    console.log()
  }

  // Anomalies
  if (s.anomalies.length > 0) {
    console.log(`  ANOMALIES`)
    for (const a of s.anomalies) {
      const badge = a.severity === 'CRITICAL' ? '!!!' : a.severity === 'WARNING' ? ' ! ' : ' i '
      console.log(`  [${badge}] ${a.severity}: ${a.message}`)
    }
    console.log()
  } else {
    console.log(`  No anomalies detected.`)
    console.log()
  }

  console.log(`  ${bar}`)
}

function ensureDataDir() {
  if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true })
}

function saveSnapshot(snapshot) {
  ensureDataDir()

  // Save latest snapshot
  const latestPath = join(DATA_DIR, 'oracle-heartbeat.json')
  writeFileSync(latestPath, JSON.stringify(snapshot, null, 2), 'utf-8')

  // Append to rolling history (max 100)
  const historyPath = join(DATA_DIR, 'oracle-heartbeat-history.json')
  let history = []
  try {
    if (existsSync(historyPath)) {
      history = JSON.parse(readFileSync(historyPath, 'utf-8'))
    }
  } catch { /* ignore */ }
  history.push({
    timestamp: snapshot.timestamp,
    healthScore: snapshot.healthScore,
    nodesConnected: snapshot.network.nodesConnected,
    consensusTick: snapshot.network.consensusTick,
    successRate: snapshot.oracle.successRate,
    pendingCount: snapshot.oracle.pendingCount,
    anomalyCount: snapshot.anomalies.length,
  })
  while (history.length > 100) history.shift()
  writeFileSync(historyPath, JSON.stringify(history, null, 2), 'utf-8')

  console.log(`  Saved to: ${latestPath}`)
  console.log(`  History:  ${historyPath} (${history.length} entries)`)
}

// =============================================================================
// MAIN
// =============================================================================

async function runScan(options = {}) {
  const { json = false, deep = false } = options

  // Scan all nodes
  const { nodes, scanDurationMs } = await scanAllNodes(NODES)

  // Analyze
  const analysis = analyzeNodes(nodes)

  // Anomaly detection
  const anomalies = detectAnomalies(analysis)

  // Deep scan (optional)
  let deepScanResult = null
  if (deep) {
    const connectedNode = nodes.find(n => n.status === 'connected')
    if (connectedNode && analysis.tickRange) {
      deepScanResult = await deepScan(connectedNode.ip, analysis.tickRange)
    }
  }

  // Build snapshot
  const snapshot = buildSnapshot(analysis, anomalies, deepScanResult, scanDurationMs)

  // Output
  printSnapshot(snapshot)
  if (json) saveSnapshot(snapshot)

  return snapshot
}

async function main() {
  const args = process.argv.slice(2)
  const json = args.includes('--json')
  const deep = args.includes('--deep')
  const loop = args.includes('--loop')
  const intervalIdx = args.indexOf('--interval')
  const interval = intervalIdx >= 0 ? parseInt(args[intervalIdx + 1], 10) : 60

  if (loop) {
    console.log(`  Starting continuous heartbeat (interval: ${interval}s)`)
    console.log(`  Press Ctrl+C to stop`)
    while (true) {
      await runScan({ json: true, deep })
      console.log(`  Next scan in ${interval}s...`)
      await new Promise(r => setTimeout(r, interval * 1000))
    }
  } else {
    await runScan({ json, deep })
  }
}

main().catch(err => {
  console.error('FATAL:', err.message)
  process.exit(1)
})
