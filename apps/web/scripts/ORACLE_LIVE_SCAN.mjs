#!/usr/bin/env node
/**
 * ORACLE LIVE SCAN — Sequential with early exit
 * Scans ticks one-by-one (stable, no disconnects).
 * Stops as soon as all 19 queries are found.
 * Writes to public/data/oracle-live-queries.json
 */
import { createConnection } from 'net'
import { randomBytes } from 'crypto'
import { writeFileSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const OUT = resolve(__dirname, '../public/data/oracle-live-queries.json')
const STATUS = { 0: 'unknown', 1: 'pending', 2: 'committed', 3: 'success', 4: 'timeout', 5: 'unresolvable' }
const QUERY_TYPE = { 0: 'contract', 1: 'subscription', 2: 'user' }
const FLAGS = { 0x001: 'INVALID_ORACLE', 0x002: 'ORACLE_UNAVAIL', 0x004: 'INVALID_TIME', 0x008: 'INVALID_PLACE', 0x010: 'INVALID_ARG', 0x100: 'REPLY_RECEIVED', 0x200: 'BAD_SIZE_REPLY', 0x400: 'OM_DISAGREE', 0x800: 'BAD_SIZE_REVEAL', 0x1000: 'FAKE_COMMITS' }

function hdr(ps, t) {
  const b = Buffer.alloc(8), s = 8 + ps
  b[0] = s & 0xFF; b[1] = (s >> 8) & 0xFF; b[2] = (s >> 16) & 0xFF; b[3] = t
  randomBytes(4).copy(b, 4)
  return b
}

function decFlags(f) { return Object.entries(FLAGS).filter(([b]) => f & Number(b)).map(([, d]) => d) }

function decQuery(buf) {
  if (buf.length < 104) return null
  const oracle = buf.slice(0, 32).toString('ascii').replace(/\0/g, '')
  const dt = buf.readBigUInt64LE(32)
  const p = n => String(n).padStart(2, '0')
  const y = Number((dt >> 46n) & 0x3FFFFn), mo = Number((dt >> 42n) & 0xFn), d = Number((dt >> 37n) & 0x1Fn)
  const h = Number((dt >> 32n) & 0x1Fn), mi = Number((dt >> 26n) & 0x3Fn), s = Number((dt >> 20n) & 0x3Fn)
  return { oracle, timestamp: `${y}-${p(mo)}-${p(d)} ${p(h)}:${p(mi)}:${p(s)}`, currency1: buf.slice(40, 72).toString('ascii').replace(/\0/g, ''), currency2: buf.slice(72, 104).toString('ascii').replace(/\0/g, '') }
}

function decReply(buf) {
  if (buf.length < 16) return null
  const n = buf.readBigInt64LE(0), d = buf.readBigInt64LE(8)
  return { numerator: Number(n), denominator: Number(d), price: d !== 0n ? Number(n) / Number(d) : 0 }
}

class C {
  constructor(ip) { this.ip = ip; this.b = Buffer.alloc(0); this.s = null }
  connect() {
    return new Promise((ok, no) => {
      const t = setTimeout(() => no(new Error('timeout')), 10000)
      this.s = createConnection({ host: this.ip, port: 21841 }, () => { clearTimeout(t); ok() })
      this.s.on('error', e => { clearTimeout(t); no(e) })
      this.s.on('data', c => { this.b = Buffer.concat([this.b, c]) })
    })
  }
  close() { this.s?.destroy(); this.s = null }
  send(d) { return new Promise((r, j) => this.s.write(d, e => e ? j(e) : r())) }
  async wait(n) { const s = Date.now(); while (this.b.length < n) { if (Date.now() - s > 10000) throw new Error('timeout'); await new Promise(r => setTimeout(r, 10)) } }
  take(n) { const r = this.b.slice(0, n); this.b = this.b.slice(n); return r }
  async msg() { await this.wait(8); const h = this.take(8); const sz = (h[0] | (h[1] << 8) | (h[2] << 16)) - 8; const t = h[3]; if (sz > 0) { await this.wait(sz); return { t, d: this.take(sz) } } return { t, d: Buffer.alloc(0) } }
  async resp() { for (let i = 0; i < 15; i++) { const m = await this.msg(); if (m.t !== 0) return m } throw new Error('flood') }
  async req(t, p) { this.b = Buffer.alloc(0); await this.send(Buffer.concat([hdr(p.length, t), p])) }

  async getTick() {
    await this.req(27, Buffer.alloc(0)); const m = await this.resp()
    return m.t === 28 ? { tick: m.d.readUInt32LE(4), epoch: m.d.readUInt16LE(2) } : null
  }

  async getStats() {
    const p = Buffer.alloc(16); p.writeUInt32LE(7, 0)
    await this.req(66, p); const m = await this.resp()
    if (m.t === 67 && m.d.readUInt32LE(0) === 7) {
      const d = m.d.slice(4); let o = 0; const r = () => { const v = Number(d.readBigUInt64LE(o)); o += 8; return v }
      return { pendingCount: r(), pendingOracleMachineCount: r(), pendingCommitCount: r(), pendingRevealCount: r(), successfulCount: r(), revealTxCount: r(), unresolvableCount: r(), timeoutCount: r(), timeoutNoReplyCount: r(), timeoutNoCommitCount: r(), timeoutNoRevealCount: r(), oracleMachineRepliesDisagreeCount: r(), oracleMachineReplyAvgMilliTicksPerQuery: r(), commitAvgMilliTicksPerQuery: r(), successAvgMilliTicksPerQuery: r(), timeoutAvgMilliTicksPerQuery: r(), wrongKnowledgeProofCount: r() }
    }
  }

  async getTickRange() {
    const p = Buffer.alloc(16); p.writeUInt32LE(0, 0); p.writeBigInt64LE(1n, 8)
    await this.req(66, p)
    let tr = null
    while (true) { const m = await this.resp(); if (m.t === 35) break; if (m.t === 67 && m.d.readUInt32LE(0) === 9) { const d = m.d.slice(4); tr = { first: d.readUInt32LE(0), current: d.readUInt32LE(4) } } }
    return tr
  }

  async getQueryIdsAtTick(tick) {
    const p = Buffer.alloc(16); p.writeUInt32LE(0, 0); p.writeBigInt64LE(BigInt(tick), 8)
    await this.req(66, p)
    const ids = []
    while (true) { const m = await this.resp(); if (m.t === 35) break; if (m.t === 67 && m.d.readUInt32LE(0) === 0) { const d = m.d.slice(4); for (let i = 0; i < d.length; i += 8) ids.push(d.readBigInt64LE(i).toString()) } }
    return ids
  }

  async getQueryInfo(qid) {
    const p = Buffer.alloc(16); p.writeUInt32LE(5, 0); p.writeBigInt64LE(BigInt(qid), 8)
    await this.req(66, p)
    let meta = null, qD = Buffer.alloc(0), rD = Buffer.alloc(0)
    while (true) {
      const m = await this.resp(); if (m.t === 35) break
      if (m.t === 67) { const rt = m.d.readUInt32LE(0), d = m.d.slice(4)
        if (rt === 1) meta = { queryId: d.readBigInt64LE(0).toString(), type: d.readUInt8(8), status: d.readUInt8(9), statusFlags: d.readUInt16LE(10), queryTick: d.readUInt32LE(12), timeout: Number(d.readBigUInt64LE(48)), interfaceIndex: d.readUInt32LE(56), revealTick: d.readUInt32LE(64), totalCommits: d.readUInt16LE(68), agreeingCommits: d.readUInt16LE(70) }
        else if (rt === 2) qD = Buffer.concat([qD, d])
        else if (rt === 3) rD = Buffer.concat([rD, d])
      }
    }
    return { meta, qD, rD }
  }
}

const SEAL_ORACLES = { genesis_1_3: 'I. BERESHIT', genesis_11_4: 'II. BABEL', genesis_28_12: 'III. SULLAM', exodus_3_14: 'IV. EHYEH', psalm_26_2: 'V. HOTAM', joel_2_31: 'VI. YOM ADONAI', revelation_22_13: 'VII. HOTAM ACHARON' }
const NODES = ['45.152.160.217', '92.118.57.14', '95.217.142.179']

async function main() {
  let c
  for (const ip of NODES) { try { c = new C(ip); await c.connect(); console.log('Connected:', ip); break } catch { } }
  if (!c) { console.error('No nodes'); process.exit(1) }

  const { tick, epoch } = await c.getTick()
  console.log(`Tick: ${tick.toLocaleString()}, Epoch: ${epoch}`)

  const stats = await c.getStats()
  const expected = stats.successfulCount + stats.timeoutCount + stats.unresolvableCount + stats.pendingCount
  console.log(`Expecting: ${expected} queries (${stats.successfulCount} success, ${stats.timeoutCount} timeout)`)

  const tr = await c.getTickRange()
  if (!tr) { console.error('No range'); process.exit(1) }
  console.log(`Range: ${tr.first}-${tr.current} (${tr.current - tr.first} ticks)`)

  // Sequential scan with early exit
  console.log(`\nScanning (stop after ${expected} found)...`)
  const t0 = Date.now()
  const foundIds = new Map()
  let emptyStreak = 0

  for (let t = tr.first; t <= tr.current; t++) {
    try {
      const ids = await c.getQueryIdsAtTick(t)
      if (ids.length > 0) {
        for (const id of ids) foundIds.set(id, t)
        emptyStreak = 0
        console.log(`  tick ${t}: ${ids.length} queries (total: ${foundIds.size}/${expected})`)
      } else {
        emptyStreak++
      }

      // Early exit: found all queries AND had 200 empty ticks after last find
      if (foundIds.size >= expected && emptyStreak > 200) {
        console.log(`  All ${expected} found + 200 empty ticks -> stopping`)
        break
      }
    } catch (e) {
      if (e.message.includes('timeout')) {
        c.close(); await new Promise(r => setTimeout(r, 500))
        for (const ip of NODES) { try { c = new C(ip); await c.connect(); console.log('  Reconnected:', ip); break } catch { } }
      }
    }

    if ((t - tr.first) % 500 === 0 && t > tr.first) {
      process.stderr.write(`  ${t - tr.first}/${tr.current - tr.first} ticks, ${foundIds.size} queries\r`)
    }
  }

  const scanSec = ((Date.now() - t0) / 1000).toFixed(1)
  console.log(`\nFound ${foundIds.size} query IDs in ${scanSec}s`)

  // Get details
  console.log('Fetching details...')
  const queries = []
  for (const [qid] of foundIds) {
    try {
      const { meta, qD, rD } = await c.getQueryInfo(qid)
      if (!meta) continue
      const q = decQuery(qD), r = decReply(rD), status = STATUS[meta.status] || '?'
      const entry = { queryId: qid, tick: meta.queryTick, type: QUERY_TYPE[meta.type] || '?', status, statusFlags: decFlags(meta.statusFlags), interfaceIndex: meta.interfaceIndex, revealTick: meta.revealTick, totalCommits: meta.totalCommits, agreeingCommits: meta.agreeingCommits }
      if (q) { entry.oracle = q.oracle; entry.queryTimestamp = q.timestamp; entry.currency1 = q.currency1; entry.currency2 = q.currency2 }
      if (r) entry.reply = r
      entry.isSeal = !!SEAL_ORACLES[entry.oracle]
      if (entry.isSeal) entry.sealName = SEAL_ORACLES[entry.oracle]
      queries.push(entry)
      const oracle = (entry.oracle || '?').padEnd(22)
      const pair = `${entry.currency1 || '?'}/${entry.currency2 || '?'}`
      const reply = r?.denominator ? `-> ${r.price.toFixed(8)}` : '(no reply)'
      const seal = entry.isSeal ? ` [${entry.sealName}]` : ''
      console.log(`  [${status.padEnd(7)}] ${oracle} ${pair.padEnd(25)} tick:${meta.queryTick}  ${reply}${seal}`)
    } catch (e) {
      if (e.message.includes('timeout')) { c.close(); await new Promise(r => setTimeout(r, 500)); for (const ip of NODES) { try { c = new C(ip); await c.connect(); break } catch { } } }
    }
  }

  c.close()
  queries.sort((a, b) => a.tick - b.tick)

  const out = { scanTimestamp: new Date().toISOString(), scanDurationSeconds: parseFloat(scanSec), epoch, currentTick: tick, tickRange: tr, stats, totalOnChain: queries.length, sealsFound: queries.filter(q => q.isSeal).length, queries }
  writeFileSync(OUT, JSON.stringify(out, null, 2))

  console.log(`\n=== ${queries.length} queries saved ===`)
  console.log(`  Seals: ${out.sealsFound}/7`)
  console.log(`  Success: ${queries.filter(q => q.status === 'success').length}`)
  console.log(`  Timeout: ${queries.filter(q => q.status === 'timeout').length}`)
  console.log(`  Time: ${scanSec}s`)
}

main().catch(e => { console.error('FATAL:', e.message); process.exit(1) })
