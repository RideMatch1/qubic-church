#!/usr/bin/env node
/**
 * LIVE QU SENDER
 * Sends QU transactions from our master account
 *
 * Usage:
 *   node SEND_QU_LIVE.mjs <destination> <amount>
 *   node SEND_QU_LIVE.mjs POCC 1          # Send 1 QU to POCC
 *   node SEND_QU_LIVE.mjs --status         # Check account status
 */

import { createRequire } from 'module'
const require = createRequire(import.meta.url)

// Load .env from project root
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

const MASTER_SEED = process.env.MASTER_SEED
const MASTER_IDENTITY = process.env.MASTER_IDENTITY

// Known addresses
const ALIASES = {
  POCC: 'POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD',
  HASV: 'HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO',
  NULL: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
}

const RPC = 'https://rpc.qubic.org/v1'

async function rpc(endpoint, options) {
  const res = await fetch(`${RPC}${endpoint}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  })
  if (!res.ok) throw new Error(`RPC ${res.status}: ${res.statusText}`)
  return res.json()
}

async function getBalance(address) {
  const data = await rpc(`/balances/${address}`)
  return data.balance
}

async function getTick() {
  const data = await rpc('/tick-info')
  return data.tickInfo || data
}

async function showStatus() {
  console.log('\n=== MASTER ACCOUNT STATUS ===')
  console.log(`Identity: ${MASTER_IDENTITY}`)

  const bal = await getBalance(MASTER_IDENTITY)
  const tick = await getTick()

  console.log(`Balance:  ${Number(bal.balance).toLocaleString()} QU`)
  console.log(`Tick:     ${tick.tick.toLocaleString()} (Epoch ${tick.epoch})`)
  console.log(`TX:       ${bal.numberOfIncomingTransfers} in / ${bal.numberOfOutgoingTransfers} out`)
  console.log(`Last Out: Tick ${bal.latestOutgoingTransferTick?.toLocaleString()}`)
  console.log()

  return { balance: bal, tick }
}

async function sendQU(destination, amount) {
  console.log('\n=== SENDING QU TRANSACTION ===')
  console.log(`From:   ${MASTER_IDENTITY?.slice(0, 15)}...`)
  console.log(`To:     ${destination.slice(0, 15)}...${destination.slice(-8)}`)
  console.log(`Amount: ${amount} QU`)

  // Get current tick
  const tickInfo = await getTick()
  const targetTick = tickInfo.tick + 5
  console.log(`Target: Tick ${targetTick.toLocaleString()} (current: ${tickInfo.tick.toLocaleString()})`)

  // Import qubic library
  const qubicLib = require('@qubic-lib/qubic-ts-library').default
  const { QubicHelper, QubicTransaction } = qubicLib

  const helper = new QubicHelper()

  // Build transaction
  console.log('\nBuilding transaction...')
  const txBytes = await helper.createTransaction(
    MASTER_SEED,
    destination,
    amount,
    targetTick
  )

  // Encode
  const tx = new QubicTransaction()
  const encoded = tx.encodeTransactionToBase64(txBytes)
  console.log(`TX size: ${txBytes.length} bytes`)
  console.log(`Base64:  ${encoded.slice(0, 40)}...`)

  // Broadcast
  console.log('\nBroadcasting...')
  const result = await rpc('/broadcast-transaction', {
    method: 'POST',
    body: JSON.stringify({ encodedTransaction: encoded }),
  })

  console.log('Broadcast result:', JSON.stringify(result, null, 2))
  console.log(`\n✅ Transaction broadcast! Target tick: ${targetTick.toLocaleString()}`)

  return { targetTick, result }
}

// Main
async function main() {
  if (!MASTER_SEED || !MASTER_IDENTITY) {
    console.error('ERROR: MASTER_SEED and MASTER_IDENTITY must be set in .env')
    process.exit(1)
  }

  const args = process.argv.slice(2)

  if (args.length === 0 || args[0] === '--status') {
    await showStatus()
    return
  }

  let destination = args[0]
  const amount = parseInt(args[1] || '1', 10)

  // Resolve aliases
  if (ALIASES[destination.toUpperCase()]) {
    destination = ALIASES[destination.toUpperCase()]
    console.log(`Resolved alias: ${args[0]} -> ${destination.slice(0, 15)}...`)
  }

  // Validate
  if (destination.length !== 60 || !/^[A-Z]+$/.test(destination)) {
    console.error('Invalid address format. Must be 60 uppercase letters.')
    process.exit(1)
  }
  if (isNaN(amount) || amount < 1) {
    console.error('Amount must be at least 1 QU.')
    process.exit(1)
  }
  if (amount > 10000) {
    console.error('Safety limit: max 10,000 QU per transaction.')
    process.exit(1)
  }

  // Show status first
  await showStatus()

  // Send
  await sendQU(destination, amount)

  // Show status after
  console.log('\n--- Waiting 3s for propagation ---')
  await new Promise(r => setTimeout(r, 3000))
  await showStatus()
}

main().catch(err => {
  console.error('FATAL:', err)
  process.exit(1)
})
