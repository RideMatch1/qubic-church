#!/usr/bin/env node
/**
 * LIVE ORACLE QUERY
 * Sends an Oracle Machine price query from our master account.
 *
 * Based on Qubic Core oracle_interfaces/Price.h and qubic-cli oracle_utils.cpp:
 * - SC Contract Index: 10 (inputType)
 * - Destination: zero public key (32 zero bytes = SC address)
 * - Fee/Amount: 10 QU (burned)
 * - Payload: [4B interfaceIndex (uint32)][4B timeout_ms (uint32)][104B queryData] = 112 bytes
 *   queryData: [32B oracle_id][8B DateAndTime (packed uint64 bitfield)][32B currency1][32B currency2]
 *
 * Oracle IDs (lowercase ASCII, zero-padded to 32 bytes):
 *   "binance", "mexc", "gate", "coingecko", "binance_mexc", etc.
 *
 * Currency IDs (same format):
 *   "qubic", "btc", "eth", "usdt", "usd", etc.
 *
 * Usage:
 *   node ORACLE_QUERY_LIVE.mjs binance qubic usdt       # Query QUBIC/USDT price from Binance
 *   node ORACLE_QUERY_LIVE.mjs mexc qubic usdt           # Query QUBIC/USDT from MEXC
 *   node ORACLE_QUERY_LIVE.mjs gate btc usdt             # Query BTC/USDT from Gate.io
 *   node ORACLE_QUERY_LIVE.mjs binance_mexc qubic usdt   # Combined Binance+MEXC
 */

import { createRequire } from 'module'
const require = createRequire(import.meta.url)

import { readFileSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))

// Load .env
const envPath = resolve(__dirname, '../../../.env')
try {
  const envContent = readFileSync(envPath, 'utf-8')
  for (const line of envContent.split('\n')) {
    const match = line.match(/^([^#=]+)=(.*)$/)
    if (match) process.env[match[1].trim()] = match[2].trim()
  }
} catch (e) {
  console.error('Could not read .env:', e.message)
  process.exit(1)
}

const MASTER_SEED = process.env.MASTER_SEED
const RPC = 'https://rpc.qubic.org/v1'

// ============================================================================
// QPI ID Encoding
// ============================================================================

/**
 * Encode a string as a QPI `id` (m256i = 32 bytes).
 * Based on Qubic Core's QPI::id constructor:
 * - Each character is stored as its ASCII value
 * - Remaining bytes are zero-padded
 */
function encodeQpiId(str) {
  const buf = Buffer.alloc(32, 0) // 256 bits = 32 bytes
  const lower = str.toLowerCase()
  for (let i = 0; i < Math.min(lower.length, 32); i++) {
    buf[i] = lower.charCodeAt(i)
  }
  return buf
}

/**
 * Encode a DateAndTime as packed uint64 bitfield (8 bytes) for QPI.
 * From qubic core QPI:
 *   value = (year << 46) | (month << 42) | (day << 37)
 *         | (hour << 32) | (minute << 26) | (second << 20)
 *         | (millisec << 10) | (microsecDuringMillisec)
 * Total = 8 bytes (uint64)
 */
function encodeDateAndTime(date = null) {
  const buf = Buffer.alloc(8, 0)
  if (date) {
    const year = BigInt(date.getUTCFullYear())
    const month = BigInt(date.getUTCMonth() + 1)
    const day = BigInt(date.getUTCDate())
    const hour = BigInt(date.getUTCHours())
    const minute = BigInt(date.getUTCMinutes())
    const second = BigInt(date.getUTCSeconds())
    const ms = BigInt(date.getUTCMilliseconds())
    const value = (year << 46n) | (month << 42n) | (day << 37n)
                | (hour << 32n) | (minute << 26n) | (second << 20n)
                | (ms << 10n)
    buf.writeBigUInt64LE(value, 0)
  }
  return buf
}

// ============================================================================
// Transaction Building
// ============================================================================

async function rpc(endpoint, options) {
  const res = await fetch(`${RPC}${endpoint}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  })
  if (!res.ok) throw new Error(`RPC ${res.status}: ${res.statusText}`)
  return res.json()
}

async function buildOracleQueryPayload(oracle, currency1, currency2) {
  // Price Oracle interface: queryData = [32B oracle][8B timestamp][32B curr1][32B curr2] = 104 bytes
  // DateAndTime is a packed uint64 bitfield, not a struct
  const oracleId = encodeQpiId(oracle)
  const timestamp = encodeDateAndTime(new Date())
  const curr1 = encodeQpiId(currency1)
  const curr2 = encodeQpiId(currency2)

  const queryData = Buffer.concat([oracleId, timestamp, curr1, curr2])
  console.log(`  queryData size: ${queryData.length} bytes (expected: 104)`)

  // Full tx input: [4B interfaceIndex (uint32)][4B timeout_ms (uint32)][queryData]
  // From qubic-cli oracle_utils.cpp: txInputSize = 8 + queryData.size() = 116 for price
  const interfaceIndex = Buffer.alloc(4, 0)
  interfaceIndex.writeUInt32LE(0, 0) // Price = interface 0

  const timeoutMs = Buffer.alloc(4, 0) // uint32 = 4 bytes
  timeoutMs.writeUInt32LE(60000, 0) // 60 seconds timeout

  return Buffer.concat([interfaceIndex, timeoutMs, queryData])
}

async function sendOracleQuery(oracle, currency1, currency2) {
  console.log('\n=== ORACLE MACHINE PRICE QUERY ===')
  console.log(`  Oracle:    ${oracle}`)
  console.log(`  Pair:      ${currency1}/${currency2}`)
  console.log(`  Fee:       10 QU (burned)`)
  console.log(`  Interface: Price (index 0)`)
  console.log()

  // Get current tick
  const tickData = await rpc('/tick-info')
  const currentTick = tickData.tickInfo?.tick ?? tickData.tick
  const targetTick = currentTick + 20
  console.log(`  Current tick: ${currentTick.toLocaleString()}`)
  console.log(`  Target tick:  ${targetTick.toLocaleString()}`)

  // Build oracle query payload
  const txInput = await buildOracleQueryPayload(oracle, currency1, currency2)
  console.log(`  TX input size: ${txInput.length} bytes (4B interface + 4B timeout + 104B query = 112)`)

  // Import qubic library
  const qubicLib = require('@qubic-lib/qubic-ts-library').default
  const { QubicHelper, QubicTransaction, QubicPackageBuilder, Long, PublicKey } = qubicLib

  const helper = new QubicHelper()

  // Create ID package from seed
  const idPackage = await helper.createIdPackage(MASTER_SEED)
  console.log(`  Source:    ${idPackage.publicId.slice(0, 15)}...`)

  // Build transaction manually (oracle requires custom inputType)
  const tx = new QubicTransaction()
    .setSourcePublicKey(new PublicKey(idPackage.publicKey))
    .setDestinationPublicKey(new PublicKey(new Uint8Array(32))) // Zero key = SC
    .setAmount(10) // 10 QU fee
    .setTick(targetTick)
    .setInputType(10) // Oracle User Query transaction type
    .setInputSize(txInput.length)

  // Set the payload
  const { DynamicPayload } = qubicLib
  const payload = new DynamicPayload(txInput.length)
  payload.setPayload(new Uint8Array(txInput))
  tx.setPayload(payload)

  // Build and sign
  console.log('\n  Building and signing transaction...')
  const txBytes = await tx.build(MASTER_SEED)
  console.log(`  TX size: ${txBytes.length} bytes`)

  // Encode to base64
  const encodedTx = tx.encodeTransactionToBase64(txBytes)
  console.log(`  Base64: ${encodedTx.slice(0, 50)}...`)

  // Broadcast
  console.log('\n  Broadcasting to network...')
  try {
    const result = await rpc('/broadcast-transaction', {
      method: 'POST',
      body: JSON.stringify({ encodedTransaction: encodedTx }),
    })
    console.log('  Broadcast result:', JSON.stringify(result, null, 2))
    console.log(`\n  TRANSACTION BROADCAST!`)
    console.log(`  Check results with: qubic-cli -getoraclequery user+ ${targetTick}`)
  } catch (err) {
    console.error('  Broadcast error:', err.message)

    // Try alternative endpoint format
    try {
      console.log('  Trying alternative broadcast format...')
      const altResult = await rpc('/broadcast-transaction', {
        method: 'POST',
        body: JSON.stringify({ EncodedTransaction: encodedTx }),
      })
      console.log('  Alt broadcast result:', JSON.stringify(altResult, null, 2))
    } catch (altErr) {
      console.error('  Alt broadcast also failed:', altErr.message)
    }
  }

  return { targetTick, currentTick }
}

// ============================================================================
// Main
// ============================================================================

async function main() {
  if (!MASTER_SEED) {
    console.error('ERROR: MASTER_SEED not set in .env')
    process.exit(1)
  }

  const args = process.argv.slice(2)

  if (args.length < 3) {
    console.log('Usage: node ORACLE_QUERY_LIVE.mjs <oracle> <currency1> <currency2>')
    console.log()
    console.log('Available oracles:')
    console.log('  binance       - Binance exchange')
    console.log('  mexc0         - MEXC exchange (note: "mexc0" not "mexc")')
    console.log('  gate0         - Gate.io exchange (note: "gate0" not "gate")')
    console.log('  coingecko     - CoinGecko aggregator')
    console.log('  binance_mexc  - Combined Binance + MEXC')
    console.log('  binance_gate  - Combined Binance + Gate')
    console.log('  gate_mexc     - Combined Gate + MEXC')
    console.log()
    console.log('Example currencies: qubic, btc, eth, usdt, usd')
    console.log()
    console.log('Examples:')
    console.log('  node ORACLE_QUERY_LIVE.mjs binance qubic usdt')
    console.log('  node ORACLE_QUERY_LIVE.mjs mexc btc usdt')
    console.log('  node ORACLE_QUERY_LIVE.mjs gate eth usdt')
    process.exit(0)
  }

  const [oracle, curr1, curr2] = args

  // Check balance first
  const balData = await rpc(`/balances/${process.env.MASTER_IDENTITY}`)
  const balance = Number(balData.balance?.balance ?? 0)
  console.log(`Master account balance: ${balance.toLocaleString()} QU`)

  if (balance < 10) {
    console.error('ERROR: Insufficient balance. Need at least 10 QU for oracle query.')
    process.exit(1)
  }

  // Send oracle query
  const result = await sendOracleQuery(oracle, curr1, curr2)

  console.log(`\n=== DONE ===`)
  console.log(`Query sent at tick ${result.targetTick}`)
  console.log(`Wait ~5 ticks for execution, then ~60s for oracle consensus.`)
}

main().catch(err => {
  console.error('FATAL:', err)
  process.exit(1)
})
