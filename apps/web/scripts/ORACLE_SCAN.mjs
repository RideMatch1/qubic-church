#!/usr/bin/env node
/**
 * Scan recent ticks for oracle queries
 */
import { createConnection } from 'net'
import { randomBytes } from 'crypto'

const MSG = {
  EXCHANGE_PUBLIC_PEERS: 0,
  REQUEST_CURRENT_TICK_INFO: 27,
  RESPOND_CURRENT_TICK_INFO: 28,
  END_RESPONSE: 35,
  REQUEST_ORACLE_DATA: 66,
  RESPOND_ORACLE_DATA: 67,
}

const RES = { QUERY_IDS: 0, TICK_RANGE: 9 }

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

class SimpleClient {
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

  async waitFor(bytes, ms = 5000) {
    const start = Date.now()
    while (this.buffer.length < bytes) {
      if (Date.now() - start > ms) throw new Error(`timeout waiting for ${bytes}B (have ${this.buffer.length}B)`)
      await new Promise(r => setTimeout(r, 50))
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

  async getCurrentTick() {
    this.buffer = Buffer.alloc(0)
    await this.send(buildHeader(0, MSG.REQUEST_CURRENT_TICK_INFO))
    const msg = await this.readMsgSkipPeers()
    if (msg.type === MSG.RESPOND_CURRENT_TICK_INFO) {
      return {
        tick: msg.payload.readUInt32LE(4),
        epoch: msg.payload.readUInt16LE(2),
      }
    }
    throw new Error(`unexpected type ${msg.type}`)
  }

  async getQueryIdsAtTick(tick, reqType = 0) {
    const payload = Buffer.alloc(16)
    payload.writeUInt32LE(reqType, 0) // ALL=0
    payload.writeUInt32LE(0, 4)
    payload.writeBigInt64LE(BigInt(tick), 8)
    const hdr = buildHeader(16, MSG.REQUEST_ORACLE_DATA)
    this.buffer = Buffer.alloc(0)
    await this.send(Buffer.concat([hdr, payload]))

    const queryIds = []
    let tickRange = null
    while (true) {
      const msg = await this.readMsgSkipPeers()
      if (msg.type === MSG.END_RESPONSE) break
      if (msg.type === MSG.RESPOND_ORACLE_DATA) {
        const resType = msg.payload.readUInt32LE(0)
        const data = msg.payload.slice(4)
        if (resType === RES.QUERY_IDS) {
          for (let i = 0; i < data.length; i += 8) {
            queryIds.push(data.readBigInt64LE(i))
          }
        } else if (resType === RES.TICK_RANGE) {
          tickRange = {
            firstTick: data.readUInt32LE(0),
            currentTick: data.readUInt32LE(4),
          }
        }
      }
    }
    return { queryIds, tickRange }
  }
}

async function main() {
  const ip = process.argv[2] || '45.152.160.217'
  const client = new SimpleClient(ip)

  console.log(`Connecting to ${ip}:21841...`)
  await client.connect()
  console.log('Connected!')

  const { tick, epoch } = await client.getCurrentTick()
  console.log(`Current tick: ${tick}, epoch: ${epoch}`)

  // First, get the tick range
  console.log('\nChecking tick range...')
  const { tickRange } = await client.getQueryIdsAtTick(1) // intentionally out of range
  if (tickRange) {
    console.log(`Oracle data available: tick ${tickRange.firstTick} - ${tickRange.currentTick}`)
  }

  // Scan from epoch start to now
  const scanStart = tickRange ? tickRange.firstTick : (tick - 1000)
  const scanEnd = tick
  const step = 1  // scan every tick

  console.log(`\nScanning ticks ${scanStart} to ${scanEnd} (${scanEnd - scanStart} ticks)...`)

  let found = 0
  for (let t = scanStart; t <= scanEnd; t += step) {
    try {
      const { queryIds } = await client.getQueryIdsAtTick(t)
      if (queryIds.length > 0) {
        found += queryIds.length
        console.log(`  TICK ${t}: ${queryIds.length} queries → [${queryIds.map(String).join(', ')}]`)
      }
    } catch (err) {
      if (err.message.includes('timeout')) {
        console.log(`  TICK ${t}: timeout, reconnecting...`)
        client.close()
        await new Promise(r => setTimeout(r, 500))
        await client.connect()
      }
    }

    // Progress every 100 ticks
    if ((t - scanStart) % 100 === 0 && t > scanStart) {
      process.stdout.write(`  ...scanned to tick ${t} (${found} found so far)\r`)
    }
  }

  console.log(`\nDone! Found ${found} total oracle queries.`)
  client.close()
}

main().catch(err => {
  console.error('FATAL:', err.message)
  process.exit(1)
})
