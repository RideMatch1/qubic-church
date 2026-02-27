#!/usr/bin/env node
/**
 * ORACLE MSG — On-Chain Messaging via Oracle Machine
 *
 * Every Oracle Query = 96 bytes of on-chain text for 10 QU.
 * CFB and everyone monitoring the Oracle Machine can read them.
 *
 * Fields (all ASCII, 32 bytes max each):
 *   oracle    = "from" / topic / identifier
 *   currency1 = primary message / encrypted data
 *   currency2 = secondary message / tag / hint
 *   timestamp = any date/time (can encode numbers)
 *
 * Usage:
 *   node ORACLE_MSG.mjs "hello_cfb" "we_see_the_matrix" "from_the_church"
 *   node ORACLE_MSG.mjs "challenge_001" "solve_this_puzzle" "hint_anna_26"
 *   node ORACLE_MSG.mjs "cfb_is_satoshi" "proof_of_creation" "epoch_200"
 *   node ORACLE_MSG.mjs --list                    # Show all sent messages
 *   node ORACLE_MSG.mjs --cost 5                  # Estimate cost for 5 messages
 *   node ORACLE_MSG.mjs --batch messages.json     # Send multiple from file
 *
 * Special timestamp flags:
 *   --ts now              (default: current time)
 *   --ts genesis          (2009-01-03 18:15:05 — Bitcoin Genesis)
 *   --ts 2026-03-03       (custom date)
 *   --ts 676              (encode as year — matrix reference)
 *
 * The Monitor (ORACLE_MONITOR.mjs) catches these within seconds.
 * The Dashboard shows them live on /monitoring → On-Chain tab.
 */

import {
  loadEnv, rpc, getBalance, getCurrentTick,
  sendOracleQuery, sleep, fmt, printHeader,
  readDataFile, writeDataFile, appendToRollingFile,
  COST_PER_QUERY,
} from './oracle-utils.mjs'

// ─── Special Timestamps ─────────────────────────────────────────────
const TIMESTAMPS = {
  genesis:  { year: 2009, month: 1, day: 3, hour: 18, minute: 15, second: 5 },
  halving1: { year: 2012, month: 11, day: 28, hour: 15, minute: 24, second: 38 },
  halving2: { year: 2016, month: 7, day: 9, hour: 16, minute: 46, second: 13 },
  halving3: { year: 2020, month: 5, day: 11, hour: 19, minute: 23, second: 43 },
  halving4: { year: 2024, month: 4, day: 20, hour: 0, minute: 9, second: 27 },
  pi:       { year: 2026, month: 3, day: 14, hour: 15, minute: 9, second: 26 },
  eclipse:  { year: 2026, month: 3, day: 3, hour: 0, minute: 0, second: 0 },
  epoch200: { year: 2026, month: 2, day: 11, hour: 0, minute: 0, second: 0 },
}

function parseTimestamp(arg) {
  if (!arg || arg === 'now') return null // null = current time

  // Named timestamps
  if (TIMESTAMPS[arg]) return TIMESTAMPS[arg]

  // Pure number = encode as year (matrix reference)
  if (/^\d+$/.test(arg)) {
    const year = parseInt(arg, 10)
    return { year, month: 1, day: 1, hour: 0, minute: 0, second: 0 }
  }

  // Date string YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
  const match = arg.match(/^(\d{4})-(\d{1,2})-(\d{1,2})(?:\s+(\d{1,2}):(\d{1,2}):?(\d{1,2})?)?$/)
  if (match) {
    return {
      year: parseInt(match[1]), month: parseInt(match[2]), day: parseInt(match[3]),
      hour: parseInt(match[4] ?? '0'), minute: parseInt(match[5] ?? '0'), second: parseInt(match[6] ?? '0'),
    }
  }

  console.error(`  Unknown timestamp: "${arg}". Use: now, genesis, 676, 2026-03-03, etc.`)
  return null
}

function sanitize(str) {
  // Oracle fields: lowercase ASCII, max 31 chars, replace spaces with underscores
  return str.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '').slice(0, 31)
}

// ─── Send Single Message ─────────────────────────────────────────────
async function sendMessage(oracle, currency1, currency2, timestampArg) {
  const balance = await getBalance()
  if (balance < COST_PER_QUERY) {
    console.error(`  Insufficient balance: ${fmt(balance)} QU (need ${COST_PER_QUERY})`)
    process.exit(1)
  }

  const { tick: currentTick, epoch } = await getCurrentTick()
  const targetTick = currentTick + 20

  const oracleSafe = sanitize(oracle)
  const c1Safe = sanitize(currency1)
  const c2Safe = sanitize(currency2)

  console.log(`  Message Details:`)
  console.log(`    oracle:    "${oracleSafe}"`)
  console.log(`    currency1: "${c1Safe}"`)
  console.log(`    currency2: "${c2Safe}"`)
  console.log(`    timestamp: ${timestampArg ?? 'now'}`)
  console.log(`    tick:      ${fmt(targetTick)}`)
  console.log(`    cost:      ${COST_PER_QUERY} QU`)
  console.log(`    balance:   ${fmt(balance)} QU (after: ${fmt(balance - COST_PER_QUERY)})`)
  console.log()

  const result = await sendOracleQuery(oracleSafe, c1Safe, c2Safe, targetTick)

  const record = {
    oracle: oracleSafe,
    currency1: c1Safe,
    currency2: c2Safe,
    timestamp: timestampArg ?? 'now',
    targetTick,
    epoch,
    txId: result.txId,
    sentAt: new Date().toISOString(),
  }

  // Save to message log
  appendToRollingFile('oracle-messages.json', record, 1000)

  console.log(`  SENT! TX: ${result.txId}`)
  console.log(`  Tick: ${fmt(targetTick)} | Epoch: ${epoch}`)
  console.log()
  console.log(`  The Monitor will detect this within ~3 seconds.`)
  console.log(`  Dashboard: /monitoring → On-Chain tab`)

  return record
}

// ─── Batch Send ──────────────────────────────────────────────────────
async function sendBatch(filePath) {
  let messages
  try {
    const raw = (await import('fs')).readFileSync(filePath, 'utf-8')
    messages = JSON.parse(raw)
  } catch (e) {
    console.error(`  Could not read ${filePath}: ${e.message}`)
    process.exit(1)
  }

  if (!Array.isArray(messages)) {
    console.error('  File must contain a JSON array of {oracle, currency1, currency2, timestamp?}')
    process.exit(1)
  }

  const cost = messages.length * COST_PER_QUERY
  const balance = await getBalance()
  console.log(`  Batch: ${messages.length} messages, cost: ${cost} QU, balance: ${fmt(balance)} QU`)

  if (balance < cost + 100) {
    console.error(`  Insufficient balance! Need ${cost} + 100 buffer = ${cost + 100} QU`)
    process.exit(1)
  }

  const results = []
  for (let i = 0; i < messages.length; i++) {
    const m = messages[i]
    console.log(`\n  [${i + 1}/${messages.length}] ${m.oracle} | ${m.currency1} | ${m.currency2}`)
    const record = await sendMessage(m.oracle, m.currency1, m.currency2, m.timestamp)
    results.push(record)
    if (i < messages.length - 1) {
      console.log(`  Waiting 500ms...`)
      await sleep(500)
    }
  }

  console.log(`\n  === ${results.length}/${messages.length} messages sent ===`)
  return results
}

// ─── List Sent Messages ──────────────────────────────────────────────
function listMessages() {
  const messages = readDataFile('oracle-messages.json') ?? []

  printHeader('ORACLE MESSAGES', `${messages.length} total`)

  if (messages.length === 0) {
    console.log('  No messages sent yet.')
    console.log('  Usage: node ORACLE_MSG.mjs "oracle" "currency1" "currency2"')
    return
  }

  let totalCost = 0
  for (const m of messages) {
    totalCost += COST_PER_QUERY
    console.log(`  [${m.sentAt?.slice(0, 19) ?? '?'}] tick:${fmt(m.targetTick)}`)
    console.log(`    oracle:    ${m.oracle}`)
    console.log(`    currency1: ${m.currency1}`)
    console.log(`    currency2: ${m.currency2}`)
    console.log()
  }

  console.log(`  Total cost: ${fmt(totalCost)} QU (${messages.length} messages)`)
}

// ─── Main ────────────────────────────────────────────────────────────
async function main() {
  loadEnv()

  const args = process.argv.slice(2)

  if (args.length === 0 || args[0] === '--help') {
    console.log(`
  ORACLE MSG — On-Chain Messaging (10 QU per message)

  Send a message:
    node ORACLE_MSG.mjs "<oracle>" "<currency1>" "<currency2>" [--ts <timestamp>]

  Examples:
    node ORACLE_MSG.mjs "hello_cfb" "we_see_the_matrix" "from_the_church"
    node ORACLE_MSG.mjs "challenge_001" "solve_this_puzzle" "hint_anna_26"
    node ORACLE_MSG.mjs "satoshi_proof" "block_576_key" "try_my_reins" --ts genesis
    node ORACLE_MSG.mjs "prophecy_btc" "above_100k_march" "commit_v1" --ts eclipse

  Special timestamps:
    --ts now          Current time (default)
    --ts genesis      Bitcoin Genesis Block (2009-01-03)
    --ts eclipse      Blood Moon (2026-03-03)
    --ts epoch200     Oracle Launch (2026-02-11)
    --ts pi           Pi Day (2026-03-14)
    --ts 676          Year as number (matrix reference)
    --ts 2026-03-14   Custom date

  Other commands:
    --list            Show all sent messages
    --cost <n>        Estimate cost for n messages
    --batch <file>    Send multiple from JSON file

  Fields (each max 31 chars, lowercase ASCII):
    oracle     Topic / identifier / "from" field
    currency1  Primary message or data
    currency2  Secondary message or tag
`)
    return
  }

  if (args[0] === '--list') {
    listMessages()
    return
  }

  if (args[0] === '--cost') {
    const n = parseInt(args[1] ?? '1', 10)
    const balance = await getBalance()
    console.log(`  ${n} messages = ${n * COST_PER_QUERY} QU`)
    console.log(`  Balance: ${fmt(balance)} QU`)
    console.log(`  After: ${fmt(balance - n * COST_PER_QUERY)} QU`)
    return
  }

  if (args[0] === '--batch') {
    if (!args[1]) {
      console.error('Usage: --batch <file.json>')
      process.exit(1)
    }
    printHeader('ORACLE MSG — Batch Send')
    await sendBatch(args[1])
    return
  }

  // Single message: oracle, currency1, currency2
  if (args.length < 3) {
    console.error('  Need 3 arguments: oracle, currency1, currency2')
    console.error('  Run with --help for usage')
    process.exit(1)
  }

  const tsIdx = args.indexOf('--ts')
  const timestampArg = tsIdx >= 0 ? args[tsIdx + 1] : null

  printHeader('ORACLE MSG — Sending On-Chain Message')
  await sendMessage(args[0], args[1], args[2], timestampArg)
}

main().catch(err => {
  console.error('FATAL:', err.message)
  process.exit(1)
})
