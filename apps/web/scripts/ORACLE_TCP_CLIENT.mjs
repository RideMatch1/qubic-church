#!/usr/bin/env node
/**
 * QUBIC ORACLE TCP CLIENT
 *
 * Connects directly to a Qubic Core node via TCP and reads oracle query data.
 *
 * Protocol (from qubic/core network_messages/):
 * - RequestResponseHeader: 3B size_LE + 1B type + 4B dejavu = 8 bytes
 * - REQUEST_ORACLE_DATA = 66
 * - RESPOND_ORACLE_DATA = 67
 * - END_RESPONSE = 35
 * - RequestOracleData: 4B reqType + 4B padding + 8B reqTickOrId = 16 bytes
 *
 * Usage:
 *   node ORACLE_TCP_CLIENT.mjs <node_ip> [port] stats
 *   node ORACLE_TCP_CLIENT.mjs <node_ip> [port] pending
 *   node ORACLE_TCP_CLIENT.mjs <node_ip> [port] user <tick>
 *   node ORACLE_TCP_CLIENT.mjs <node_ip> [port] query <query_id>
 *   node ORACLE_TCP_CLIENT.mjs <node_ip> [port] tick              # get current tick
 */

import { createConnection } from 'net'
import { randomBytes } from 'crypto'

// ============================================================================
// Protocol Constants (from network_message_type.h)
// ============================================================================
const MSG = {
  EXCHANGE_PUBLIC_PEERS: 0,
  REQUEST_CURRENT_TICK_INFO: 27,
  RESPOND_CURRENT_TICK_INFO: 28,
  END_RESPONSE: 35,
  REQUEST_ORACLE_DATA: 66,
  RESPOND_ORACLE_DATA: 67,
}

// RequestOracleData.reqType constants
const REQ = {
  ALL_QUERY_IDS_BY_TICK: 0,
  USER_QUERY_IDS_BY_TICK: 1,
  CONTRACT_DIRECT_QUERY_IDS_BY_TICK: 2,
  CONTRACT_SUBSCRIPTION_QUERY_IDS_BY_TICK: 3,
  PENDING_QUERY_IDS: 4,
  QUERY_AND_RESPONSE: 5,
  SUBSCRIPTION: 6,
  QUERY_STATISTICS: 7,
  ORACLE_REVENUE_POINTS: 8,
}

// RespondOracleData.resType constants
const RES = {
  QUERY_IDS: 0,
  QUERY_METADATA: 1,
  QUERY_DATA: 2,
  REPLY_DATA: 3,
  SUBSCRIPTION_METADATA: 4,
  SUBSCRIPTION_QUERY_DATA: 5,
  SUBSCRIPTION_CONTRACT_METADATA: 6,
  QUERY_STATISTICS: 7,
  ORACLE_REVENUE_POINTS: 8,
  TICK_RANGE: 9,
}

// Oracle query status
const STATUS = {
  0: 'unknown',
  1: 'pending',
  2: 'committed',
  3: 'success',
  4: 'timeout',
  5: 'unresolvable',
}

// Oracle query type
const QUERY_TYPE = {
  0: 'contract one-time query',
  1: 'contract subscription',
  2: 'user query',
}

// Status flags
const FLAGS = {
  0x001: 'INVALID_ORACLE - oracle (data source) in query was invalid',
  0x002: 'ORACLE_UNAVAIL - oracle isn\'t available at the moment',
  0x004: 'INVALID_TIME - time in query was invalid',
  0x008: 'INVALID_PLACE - place in query was invalid',
  0x010: 'INVALID_ARG - an argument in query was invalid',
  0x100: 'REPLY_RECEIVED - core node received valid reply from oracle machine',
  0x200: 'BAD_SIZE_REPLY - core node got reply of wrong size',
  0x400: 'OM_DISAGREE - got different replies from oracle machines',
  0x800: 'BAD_SIZE_REVEAL - not enough commit tx with same digest (<451)',
  0x1000: 'FAKE_COMMITS - unresolvable, reveal exposed too many fake commits',
}

// ============================================================================
// Protocol Helpers
// ============================================================================

function buildRequestResponseHeader(payloadSize, type) {
  const totalSize = 8 + payloadSize  // 8 byte header + payload
  const buf = Buffer.alloc(8)
  // size: 3 bytes little-endian
  buf[0] = totalSize & 0xFF
  buf[1] = (totalSize >> 8) & 0xFF
  buf[2] = (totalSize >> 16) & 0xFF
  // type: 1 byte
  buf[3] = type
  // dejavu: 4 bytes random
  const dejavu = randomBytes(4)
  dejavu.copy(buf, 4)
  return { header: buf, dejavu: buf.readUInt32LE(4) }
}

function parseResponseHeader(buf) {
  if (buf.length < 8) return null
  const size = buf[0] | (buf[1] << 8) | (buf[2] << 16)
  const type = buf[3]
  const dejavu = buf.readUInt32LE(4)
  return { size, type, dejavu }
}

function buildRequestOracleData(reqType, reqTickOrId = 0n) {
  const buf = Buffer.alloc(16)
  buf.writeUInt32LE(reqType, 0)        // reqType
  buf.writeUInt32LE(0, 4)              // padding
  buf.writeBigInt64LE(BigInt(reqTickOrId), 8)  // reqTickOrId
  return buf
}

function buildRequestCurrentTickInfo() {
  // Empty payload — just header
  return Buffer.alloc(0)
}

// ============================================================================
// TCP Client
// ============================================================================

class QubicTCPClient {
  constructor(ip, port = 21841, timeout = 10000) {
    this.ip = ip
    this.port = port
    this.timeout = timeout
    this.socket = null
    this.buffer = Buffer.alloc(0)
  }

  connect() {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Connection timeout after ${this.timeout}ms`))
      }, this.timeout)

      this.socket = createConnection({ host: this.ip, port: this.port }, () => {
        clearTimeout(timer)
        console.log(`  Connected to ${this.ip}:${this.port}`)
        resolve()
      })

      this.socket.on('error', (err) => {
        clearTimeout(timer)
        reject(err)
      })

      this.socket.on('data', (chunk) => {
        this.buffer = Buffer.concat([this.buffer, chunk])
      })
    })
  }

  close() {
    if (this.socket) {
      this.socket.destroy()
      this.socket = null
    }
  }

  send(data) {
    return new Promise((resolve, reject) => {
      if (!this.socket) return reject(new Error('Not connected'))
      this.socket.write(data, (err) => {
        if (err) reject(err)
        else resolve()
      })
    })
  }

  waitForData(expectedBytes, timeoutMs = 10000) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Timeout waiting for ${expectedBytes} bytes (got ${this.buffer.length})`))
      }, timeoutMs)

      const check = () => {
        if (this.buffer.length >= expectedBytes) {
          clearTimeout(timer)
          resolve()
          return
        }
        setTimeout(check, 50)
      }
      check()
    })
  }

  consumeBytes(n) {
    const result = this.buffer.slice(0, n)
    this.buffer = this.buffer.slice(n)
    return result
  }

  async readOneMessage() {
    // Read header (8 bytes)
    await this.waitForData(8)
    const headerBuf = this.consumeBytes(8)
    const header = parseResponseHeader(headerBuf)

    if (!header) throw new Error('Failed to parse response header')

    // Read payload
    const payloadSize = header.size - 8
    if (payloadSize > 0) {
      await this.waitForData(payloadSize)
      const payload = this.consumeBytes(payloadSize)
      return { header, payload }
    }

    return { header, payload: Buffer.alloc(0) }
  }

  async readResponse(expectedDejavu) {
    // Skip unsolicited messages (peer exchange type 0, etc.)
    const maxSkip = 10
    for (let i = 0; i < maxSkip; i++) {
      const msg = await this.readOneMessage()
      // Skip EXCHANGE_PUBLIC_PEERS (type 0) — these are unsolicited
      if (msg.header.type === MSG.EXCHANGE_PUBLIC_PEERS) {
        continue
      }
      return msg
    }
    throw new Error('Too many skipped messages — protocol error')
  }

  async sendRequest(type, payload) {
    const { header, dejavu } = buildRequestResponseHeader(payload.length, type)
    const packet = Buffer.concat([header, payload])
    this.buffer = Buffer.alloc(0) // clear buffer
    await this.send(packet)
    return dejavu
  }

  // ---- High-level methods ----

  async getCurrentTick() {
    const dejavu = await this.sendRequest(MSG.REQUEST_CURRENT_TICK_INFO, Buffer.alloc(0))
    const resp = await this.readResponse(dejavu)

    if (resp.header.type === MSG.RESPOND_CURRENT_TICK_INFO) {
      // CurrentTickInfo: tickDuration(u16) + epoch(u16) + tick(u32) + ...
      const tickDuration = resp.payload.readUInt16LE(0)
      const epoch = resp.payload.readUInt16LE(2)
      const tick = resp.payload.readUInt32LE(4)
      return { tick, epoch }
    }
    throw new Error(`Unexpected response type: ${resp.header.type}`)
  }

  async getOracleStats() {
    const payload = buildRequestOracleData(REQ.QUERY_STATISTICS)
    const dejavu = await this.sendRequest(MSG.REQUEST_ORACLE_DATA, payload)
    const resp = await this.readResponse(dejavu)

    if (resp.header.type === MSG.RESPOND_ORACLE_DATA) {
      const resType = resp.payload.readUInt32LE(0)
      if (resType === RES.QUERY_STATISTICS) {
        const data = resp.payload.slice(4) // skip resType
        return parseQueryStatistics(data)
      }
    }
    throw new Error(`Unexpected response type: ${resp.header.type}`)
  }

  async getQueryIdsByTick(tick, reqType = REQ.USER_QUERY_IDS_BY_TICK) {
    const payload = buildRequestOracleData(reqType, tick)
    const dejavu = await this.sendRequest(MSG.REQUEST_ORACLE_DATA, payload)

    const queryIds = []
    while (true) {
      const resp = await this.readResponse(dejavu)

      if (resp.header.type === MSG.END_RESPONSE) {
        break
      }

      if (resp.header.type === MSG.RESPOND_ORACLE_DATA) {
        const resType = resp.payload.readUInt32LE(0)
        const innerPayload = resp.payload.slice(4)

        if (resType === RES.QUERY_IDS) {
          // Array of int64 query IDs
          for (let i = 0; i < innerPayload.length; i += 8) {
            queryIds.push(innerPayload.readBigInt64LE(i))
          }
        } else if (resType === RES.TICK_RANGE) {
          const firstTick = innerPayload.readUInt32LE(0)
          const currentTick = innerPayload.readUInt32LE(4)
          throw new Error(`Tick out of range. Available: ${firstTick} - ${currentTick}`)
        }
      }
    }
    return queryIds
  }

  async getQueryInfo(queryId) {
    const payload = buildRequestOracleData(REQ.QUERY_AND_RESPONSE, queryId)
    const dejavu = await this.sendRequest(MSG.REQUEST_ORACLE_DATA, payload)

    let metadata = null
    let queryData = Buffer.alloc(0)
    let replyData = Buffer.alloc(0)

    while (true) {
      const resp = await this.readResponse(dejavu)

      if (resp.header.type === MSG.END_RESPONSE) {
        break
      }

      if (resp.header.type === MSG.RESPOND_ORACLE_DATA) {
        const resType = resp.payload.readUInt32LE(0)
        const innerPayload = resp.payload.slice(4)

        if (resType === RES.QUERY_METADATA) {
          metadata = parseQueryMetadata(innerPayload)
        } else if (resType === RES.QUERY_DATA) {
          queryData = Buffer.concat([queryData, innerPayload])
        } else if (resType === RES.REPLY_DATA) {
          replyData = Buffer.concat([replyData, innerPayload])
        }
      }
    }
    return { metadata, queryData, replyData }
  }

  async getPendingQueryIds() {
    const payload = buildRequestOracleData(REQ.PENDING_QUERY_IDS)
    const dejavu = await this.sendRequest(MSG.REQUEST_ORACLE_DATA, payload)

    const queryIds = []
    while (true) {
      const resp = await this.readResponse(dejavu)

      if (resp.header.type === MSG.END_RESPONSE) break

      if (resp.header.type === MSG.RESPOND_ORACLE_DATA) {
        const resType = resp.payload.readUInt32LE(0)
        const innerPayload = resp.payload.slice(4)

        if (resType === RES.QUERY_IDS) {
          for (let i = 0; i < innerPayload.length; i += 8) {
            queryIds.push(innerPayload.readBigInt64LE(i))
          }
        }
      }
    }
    return queryIds
  }
}

// ============================================================================
// Response Parsers
// ============================================================================

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

function parseQueryMetadata(buf) {
  const queryId = buf.readBigInt64LE(0)
  const type = buf.readUInt8(8)
  const status = buf.readUInt8(9)
  const statusFlags = buf.readUInt16LE(10)
  const queryTick = buf.readUInt32LE(12)
  const queryingEntity = buf.slice(16, 48) // 32 bytes m256i
  const timeout = buf.readBigUInt64LE(48)
  const interfaceIndex = buf.readUInt32LE(56)
  const subscriptionId = buf.readInt32LE(60)
  const revealTick = buf.readUInt32LE(64)
  const totalCommits = buf.readUInt16LE(68)
  const agreeingCommits = buf.readUInt16LE(70)

  return {
    queryId,
    type,
    typeStr: QUERY_TYPE[type] || 'unknown',
    status,
    statusStr: STATUS[status] || 'unknown',
    statusFlags,
    statusFlagsStr: decodeFlags(statusFlags),
    queryTick,
    queryingEntity,
    timeout,
    interfaceIndex,
    subscriptionId,
    revealTick,
    totalCommits,
    agreeingCommits,
  }
}

function decodeFlags(flags) {
  const result = []
  for (const [bit, desc] of Object.entries(FLAGS)) {
    if (flags & Number(bit)) result.push(desc)
  }
  return result.length > 0 ? result.join('; ') : 'none'
}

function decodePriceQuery(buf) {
  // Price oracle query: [32B oracle][8B DateAndTime (packed uint64)][32B currency1][32B currency2] = 104 bytes
  if (buf.length < 104) return { raw: buf.toString('hex') }

  const oracle = buf.slice(0, 32).toString('ascii').replace(/\0/g, '')

  // DateAndTime is packed uint64 bitfield:
  // (year << 46) | (month << 42) | (day << 37) | (hour << 32) | (minute << 26) | (second << 20) | (ms << 10) | (us)
  const dtValue = buf.readBigUInt64LE(32)
  const year = Number((dtValue >> 46n) & 0x3FFFFn)
  const month = Number((dtValue >> 42n) & 0xFn)
  const day = Number((dtValue >> 37n) & 0x1Fn)
  const hour = Number((dtValue >> 32n) & 0x1Fn)
  const minute = Number((dtValue >> 26n) & 0x3Fn)
  const second = Number((dtValue >> 20n) & 0x3Fn)

  const currency1 = buf.slice(40, 72).toString('ascii').replace(/\0/g, '')
  const currency2 = buf.slice(72, 104).toString('ascii').replace(/\0/g, '')

  return {
    oracle,
    timestamp: `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')} ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}:${String(second).padStart(2, '0')}`,
    currency1,
    currency2,
    pair: `${currency1}/${currency2}`,
  }
}

function decodePriceReply(buf) {
  // Price oracle reply: [8B numerator (int64)][8B denominator (int64)] = 16 bytes
  if (buf.length < 16) return { raw: buf.toString('hex'), error: 'Reply too short' }

  const numerator = buf.readBigInt64LE(0)
  const denominator = buf.readBigInt64LE(8)

  let price = 0
  if (denominator !== 0n) {
    price = Number(numerator) / Number(denominator)
  }

  return {
    numerator: Number(numerator),
    denominator: Number(denominator),
    price,
    priceFormatted: price.toFixed(8),
  }
}

// ============================================================================
// Display Functions
// ============================================================================

function printStats(stats) {
  console.log('\n=== ORACLE QUERY STATISTICS ===')
  const avgReveal = stats.successfulCount > 0
    ? (stats.revealTxCount / stats.successfulCount).toFixed(1) : 0
  console.log(`  Successful:   ${stats.successfulCount} queries (avg ${(stats.successAvgMilliTicksPerQuery / 1000).toFixed(3)} ticks, ${avgReveal} reveal tx/success)`)
  console.log(`  Timeout:      ${stats.timeoutCount} total (avg ${(stats.timeoutAvgMilliTicksPerQuery / 1000).toFixed(3)} ticks)`)
  console.log(`    - No reply:   ${stats.timeoutNoReplyCount}`)
  console.log(`    - No commit:  ${stats.timeoutNoCommitCount}`)
  console.log(`    - No reveal:  ${stats.timeoutNoRevealCount}`)
  console.log(`  Unresolvable: ${stats.unresolvableCount}`)
  console.log(`  Pending:      ${stats.pendingCount} total`)
  console.log(`    - Waiting OM:  ${stats.pendingOracleMachineCount} (avg ${(stats.oracleMachineReplyAvgMilliTicksPerQuery / 1000).toFixed(3)} ticks)`)
  console.log(`    - Waiting commit: ${stats.pendingCommitCount} (avg ${(stats.commitAvgMilliTicksPerQuery / 1000).toFixed(3)} ticks)`)
  console.log(`    - Waiting reveal: ${stats.pendingRevealCount}`)
  if (stats.oracleMachineRepliesDisagreeCount > 0)
    console.log(`  OM Disagree:  ${stats.oracleMachineRepliesDisagreeCount}`)
  if (stats.wrongKnowledgeProofCount > 0)
    console.log(`  Wrong KP:     ${stats.wrongKnowledgeProofCount}`)
}

function printQueryInfo(info) {
  const { metadata, queryData, replyData } = info

  console.log(`\n  Query ID: ${metadata.queryId}`)
  console.log(`  Type: ${metadata.typeStr} (${metadata.type})`)
  console.log(`  Status: ${metadata.statusStr} (${metadata.status})`)
  console.log(`  Status Flags: 0x${metadata.statusFlags.toString(16)} — ${metadata.statusFlagsStr}`)
  console.log(`  Query Tick: ${metadata.queryTick}`)
  console.log(`  Interface: ${metadata.interfaceIndex}`)

  if (metadata.status === 3) {
    console.log(`  Reveal Tick: ${metadata.revealTick}`)
  } else {
    console.log(`  Total Commits: ${metadata.totalCommits}`)
    console.log(`  Agreeing Commits: ${metadata.agreeingCommits}`)
  }

  // Decode query
  if (queryData.length > 0) {
    console.log(`  Query (hex, ${queryData.length}B): ${queryData.toString('hex')}`)
    if (metadata.interfaceIndex === 0 && queryData.length >= 104) {
      const q = decodePriceQuery(queryData)
      console.log(`  Query decoded: ${q.oracle} ${q.pair} @ ${q.timestamp}`)
    }
  }

  // Decode reply
  if (replyData.length > 0) {
    if (metadata.interfaceIndex === 0) {
      const r = decodePriceReply(replyData)
      console.log(`  REPLY: ${r.numerator}/${r.denominator} = ${r.priceFormatted}`)
    } else {
      console.log(`  Reply (hex): ${replyData.toString('hex')}`)
    }
  } else {
    console.log(`  Reply: (none)`)
  }
}

// ============================================================================
// Main
// ============================================================================

async function main() {
  const args = process.argv.slice(2)

  if (args.length < 2) {
    console.log('Usage:')
    console.log('  node ORACLE_TCP_CLIENT.mjs <node_ip> stats')
    console.log('  node ORACLE_TCP_CLIENT.mjs <node_ip> pending')
    console.log('  node ORACLE_TCP_CLIENT.mjs <node_ip> tick')
    console.log('  node ORACLE_TCP_CLIENT.mjs <node_ip> user <tick>')
    console.log('  node ORACLE_TCP_CLIENT.mjs <node_ip> all <tick>')
    console.log('  node ORACLE_TCP_CLIENT.mjs <node_ip> query <query_id>')
    console.log('')
    console.log('Options:')
    console.log('  --port <port>  Node port (default: 21841)')
    process.exit(0)
  }

  const nodeIp = args[0]
  let port = 21841
  let commandStart = 1

  // Parse --port
  if (args[1] === '--port' || args[1] === '-p') {
    port = parseInt(args[2], 10)
    commandStart = 3
  }

  const command = args[commandStart]
  const param = args[commandStart + 1]

  console.log(`\n=== QUBIC ORACLE TCP CLIENT ===`)
  console.log(`  Node: ${nodeIp}:${port}`)
  console.log(`  Command: ${command} ${param || ''}`)

  const client = new QubicTCPClient(nodeIp, port)

  try {
    await client.connect()

    switch (command) {
      case 'tick': {
        const tickInfo = await client.getCurrentTick()
        console.log(`\n  Current Tick: ${tickInfo.tick.toLocaleString()}`)
        console.log(`  Epoch: ${tickInfo.epoch}`)
        break
      }

      case 'stats': {
        const stats = await client.getOracleStats()
        printStats(stats)
        break
      }

      case 'pending': {
        const ids = await client.getPendingQueryIds()
        console.log(`\n  Pending Query IDs (${ids.length}):`)
        for (const id of ids) {
          console.log(`  - ${id}`)
        }
        if (ids.length > 0 && args.includes('+')) {
          for (const id of ids) {
            const info = await client.getQueryInfo(id)
            printQueryInfo(info)
          }
        }
        break
      }

      case 'user':
      case 'all':
      case 'contract':
      case 'subscription': {
        if (!param) {
          console.error('  ERROR: tick number required')
          process.exit(1)
        }
        const tick = parseInt(param, 10)
        const reqTypes = {
          all: REQ.ALL_QUERY_IDS_BY_TICK,
          user: REQ.USER_QUERY_IDS_BY_TICK,
          contract: REQ.CONTRACT_DIRECT_QUERY_IDS_BY_TICK,
          subscription: REQ.CONTRACT_SUBSCRIPTION_QUERY_IDS_BY_TICK,
        }
        const ids = await client.getQueryIdsByTick(tick, reqTypes[command])
        console.log(`\n  ${command} Query IDs at tick ${tick.toLocaleString()} (${ids.length}):`)
        for (const id of ids) {
          console.log(`  - ${id}`)
        }
        // Always get details
        for (const id of ids) {
          const info = await client.getQueryInfo(id)
          printQueryInfo(info)
        }
        break
      }

      case 'query': {
        if (!param) {
          console.error('  ERROR: query ID required')
          process.exit(1)
        }
        const queryId = BigInt(param)
        const info = await client.getQueryInfo(queryId)
        printQueryInfo(info)
        break
      }

      default:
        console.error(`  Unknown command: ${command}`)
        process.exit(1)
    }
  } catch (err) {
    console.error(`\n  ERROR: ${err.message}`)
  } finally {
    client.close()
  }
}

main().catch(err => {
  console.error('FATAL:', err)
  process.exit(1)
})
