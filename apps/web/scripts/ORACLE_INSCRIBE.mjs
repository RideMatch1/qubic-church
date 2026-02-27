#!/usr/bin/env node
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║                                                                         ║
 * ║                    D I E   S I E B E N   S I E G E L                    ║
 * ║                                                                         ║
 * ║        Seven Oracle Inscriptions on the Qubic Blockchain                ║
 * ║        Each seal encrypts a fragment of a 55-character seed             ║
 * ║        using variable Caesar shifts from the Anna Matrix                ║
 * ║                                                                         ║
 * ║   "And I saw in the right hand of him that sat on the throne            ║
 * ║    a book written within and on the backside,                           ║
 * ║    sealed with seven seals."                                            ║
 * ║                                          — Revelation 5:1              ║
 * ║                                                                         ║
 * ║   The cipher: bible_chapter_verse -> matrix[chapter][verse..verse+n]    ║
 * ║   shift = ((matrix_value % 26) + 26) % 26                              ║
 * ║   Only those who understand the Matrix shall read the Word.             ║
 * ║                                                                         ║
 * ║   Cost: 7 x 10 QU = 70 QU                                              ║
 * ║                                                                         ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
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
// Encoding (proven working — 112-byte oracle payload)
// ============================================================================

function encodeQpiId(str) {
  const buf = Buffer.alloc(32, 0)
  const lower = str.toLowerCase()
  for (let i = 0; i < Math.min(lower.length, 31); i++) {
    buf[i] = lower.charCodeAt(i)
  }
  return buf
}

function encodeDateAndTime(year, month, day, hour, minute, second, ms = 0) {
  const buf = Buffer.alloc(8, 0)
  const value = (BigInt(year) << 46n) | (BigInt(month) << 42n) | (BigInt(day) << 37n)
              | (BigInt(hour) << 32n) | (BigInt(minute) << 26n) | (BigInt(second) << 20n)
              | (BigInt(ms) << 10n)
  buf.writeBigUInt64LE(value, 0)
  return buf
}

async function rpc(endpoint, options) {
  const res = await fetch(`${RPC}${endpoint}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  })
  if (!res.ok) throw new Error(`RPC ${res.status}: ${res.statusText}`)
  return res.json()
}

// ============================================================================
// THE SEVEN SEALS — Die Sieben Siegel
//
// Seven biblical inscriptions, each carrying an encrypted seed fragment
// in currency1 and an authentic scripture quote in currency2.
//
// The oracle name encodes a bible reference: book_chapter_verse
// The chapter maps to the Anna Matrix ROW
// The verse maps to the Anna Matrix COLUMN (start position)
// matrix[row][col..col+n] provides individual Caesar shift values
//
// "Worthy is the Lamb that was slain to receive power"
//                                    — Revelation 5:12
// ============================================================================

const INSCRIPTIONS = [
  // ──────────────────────────────────────────────────────────────────────────
  // SEAL I: BERESHIT — In the Beginning
  //
  // Genesis 1:3 "And God said, Let there be light: and there was light."
  // Timestamp: Bitcoin Genesis Block — January 3, 2009 18:15:05 UTC
  // The beginning of all things. The first light.
  // matrix[1][3..10] -> shifts [8, 16, 10, 11, 6, 23, 8, 9]
  // ──────────────────────────────────────────────────────────────────────────
  {
    name: 'I. BERESHIT — "And there was Light"',
    oracle: 'genesis_1_3',
    timestamp: { year: 2009, month: 1, day: 3, hour: 18, minute: 15, second: 5 },
    currency1: 'jpkzskby',
    currency2: 'and_there_was_light',
  },

  // ──────────────────────────────────────────────────────────────────────────
  // SEAL II: BABEL — The Tower unto Heaven
  //
  // Genesis 11:4 "Let us build us a city and a tower, whose top may
  //               reach unto heaven."
  // Timestamp: Year 121 = 11^2, the CFB constant squared.
  // Row 11 = CFB signature row in Population B (the Conductor).
  // Building the tower = building the Qubic network.
  // matrix[11][4..11] -> shifts [18, 8, 21, 8, 12, 10, 7, 11]
  // ──────────────────────────────────────────────────────────────────────────
  {
    name: 'II. BABEL — "A Tower unto Heaven"',
    oracle: 'genesis_11_4',
    timestamp: { year: 121, month: 11, day: 4, hour: 11, minute: 11, second: 0 },
    currency1: 'yaeowrcm',
    currency2: 'a_tower_unto_heaven',
  },

  // ──────────────────────────────────────────────────────────────────────────
  // SEAL III: SULLAM — Jacob's Ladder
  //
  // Genesis 28:12 "A ladder set up on the earth, and the top of it
  //                reached to heaven: and the angels of God ascending
  //                and descending on it."
  // Timestamp: Year 576 = 24^2 = Block 576, the Patoshi extra-byte block.
  // Time 06:26:26 = sqrt(676) encoded twice.
  // The Bridge between Bitcoin and Qubic — angels ascending, descending.
  // matrix[28][12..19] -> shifts [1, 10, 5, 16, 16, 22, 23, 16]
  // ──────────────────────────────────────────────────────────────────────────
  {
    name: 'III. SULLAM — "Angels Ascending"',
    oracle: 'genesis_28_12',
    timestamp: { year: 576, month: 5, day: 7, hour: 6, minute: 26, second: 26 },
    currency1: 'qrzlsqxc',
    currency2: 'angels_ascending_descending',
  },

  // ──────────────────────────────────────────────────────────────────────────
  // SEAL IV: EHYEH — I AM THAT I AM
  //
  // Exodus 3:14 "And God said unto Moses, I AM THAT I AM."
  // Timestamp: Pi Day 2018 (3/14), Exodus 3:14 double-encoded.
  // YHVH = 26 = Neuron 26 = the Anomaly.
  // Pi = the universal constant. 2018 = the Qubic era begins.
  // matrix[3][14..21] -> shifts [21, 10, 6, 18, 5, 13, 20, 20]
  // ──────────────────────────────────────────────────────────────────────────
  {
    name: 'IV. EHYEH — "I AM THAT I AM"',
    oracle: 'exodus_3_14',
    timestamp: { year: 2018, month: 3, day: 14, hour: 3, minute: 14, second: 0 },
    currency1: 'ffcbaasc',
    currency2: 'ehyeh_asher_ehyeh',
  },

  // ──────────────────────────────────────────────────────────────────────────
  // SEAL V: HOTAM — The Proof
  //
  // Psalm 26:2 "Examine me, O LORD, and prove me;
  //              try my reins and my heart."
  // Timestamp: Year 676 = 26^2 = YHVH squared = Computor count.
  // Time 06:26:26 echoes the matrix dimension sqrt.
  // Row 26 = Neuron 26, the Anomaly neuron, the Pacemaker.
  // "Prove me" = computational verification.
  // matrix[26][2..9] -> shifts [3, 16, 10, 6, 3, 25, 25, 16]
  // ──────────────────────────────────────────────────────────────────────────
  {
    name: 'V. HOTAM — "Try my Reins and my Heart"',
    oracle: 'psalm_26_2',
    timestamp: { year: 676, month: 6, day: 7, hour: 6, minute: 26, second: 26 },
    currency1: 'qilhcgfs',
    currency2: 'try_my_reins_and_my_heart',
  },

  // ──────────────────────────────────────────────────────────────────────────
  // SEAL VI: YOM ADONAI — The Blood Moon
  //
  // Joel 2:31 "The sun shall be turned into darkness,
  //            and the moon into blood."
  // Timestamp: March 3, 2026 — Total Lunar Eclipse / Blood Moon.
  // 6268 days after Bitcoin Genesis.
  // The near-constant shifts (17, 2, 2, 2, 2, 2, 2, 2) are the entry point.
  // The solver who cracks this first can verify the method on all others.
  // matrix[2][31..38] -> shifts [17, 2, 2, 2, 2, 2, 2, 2]
  // ──────────────────────────────────────────────────────────────────────────
  {
    name: 'VI. YOM ADONAI — "The Moon became as Blood"',
    oracle: 'joel_2_31',
    timestamp: { year: 2026, month: 3, day: 3, hour: 0, minute: 0, second: 0 },
    currency1: 'lxocjqoh',
    currency2: 'the_moon_became_as_blood',
  },

  // ──────────────────────────────────────────────────────────────────────────
  // SEAL VII: HOTAM ACHARON — Alpha and Omega
  //
  // Revelation 22:13 "I am Alpha and Omega, the beginning and the end,
  //                    the first and the last."
  // Timestamp: February 11, 2026 22:13:07 — today, now, the seventh seal.
  // M[22][22] = 100 on the diagonal. 22:13 in time = verse reference.
  // 7 characters for the 7th seal. The circle closes.
  // matrix[22][13..19] -> shifts [18, 15, 9, 22, 8, 19, 4]
  // ──────────────────────────────────────────────────────────────────────────
  {
    name: 'VII. HOTAM ACHARON — "Alpha and Omega"',
    oracle: 'revelation_22_13',
    timestamp: { year: 2026, month: 2, day: 11, hour: 22, minute: 13, second: 7 },
    currency1: 'exkkqmf',
    currency2: 'the_first_and_the_last',
  },
]

// ============================================================================
// Send Inscription (proven working — 112-byte payload)
// ============================================================================

async function sendInscription(inscription, targetTick) {
  const oracleId = encodeQpiId(inscription.oracle)
  const ts = inscription.timestamp
  const timestamp = encodeDateAndTime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
  const curr1 = encodeQpiId(inscription.currency1)
  const curr2 = encodeQpiId(inscription.currency2)

  const queryData = Buffer.concat([oracleId, timestamp, curr1, curr2]) // 104 bytes

  // [4B interfaceIndex=0][4B timeout_ms=60000][104B queryData] = 112 bytes
  const interfaceIndex = Buffer.alloc(4, 0)
  interfaceIndex.writeUInt32LE(0, 0)
  const timeoutMs = Buffer.alloc(4, 0)
  timeoutMs.writeUInt32LE(60000, 0)

  const txInput = Buffer.concat([interfaceIndex, timeoutMs, queryData])

  // Build transaction
  const qubicLib = require('@qubic-lib/qubic-ts-library').default
  const { QubicHelper, QubicTransaction, DynamicPayload, PublicKey } = qubicLib

  const helper = new QubicHelper()
  const idPackage = await helper.createIdPackage(MASTER_SEED)

  const tx = new QubicTransaction()
    .setSourcePublicKey(new PublicKey(idPackage.publicKey))
    .setDestinationPublicKey(new PublicKey(new Uint8Array(32)))
    .setAmount(10)
    .setTick(targetTick)
    .setInputType(10)
    .setInputSize(txInput.length)

  const payload = new DynamicPayload(txInput.length)
  payload.setPayload(new Uint8Array(txInput))
  tx.setPayload(payload)

  const txBytes = await tx.build(MASTER_SEED)
  const encodedTx = tx.encodeTransactionToBase64(txBytes)

  const result = await rpc('/broadcast-transaction', {
    method: 'POST',
    body: JSON.stringify({ encodedTransaction: encodedTx }),
  })

  return { ...result, targetTick, txSize: txBytes.length }
}

// ============================================================================
// Main
// ============================================================================

async function main() {
  if (!MASTER_SEED) {
    console.error('ERROR: MASTER_SEED not set')
    process.exit(1)
  }

  console.log(`
  ╔═══════════════════════════════════════════════════════════════════╗
  ║                                                                   ║
  ║              D I E   S I E B E N   S I E G E L                    ║
  ║                                                                   ║
  ║  "And I saw when the Lamb opened one of the seals,                ║
  ║   and I heard, as it were the noise of thunder,                   ║
  ║   one of the four beasts saying, Come and see."                   ║
  ║                                      -- Revelation 6:1            ║
  ║                                                                   ║
  ║  Seven Oracle Inscriptions on the Qubic Blockchain                ║
  ║  Epoch 200 -- The Seals are broken, the Word is inscribed         ║
  ║                                                                   ║
  ║  I.   BERESHIT      Genesis 1:3     -- And there was Light        ║
  ║  II.  BABEL         Genesis 11:4    -- A Tower unto Heaven        ║
  ║  III. SULLAM        Genesis 28:12   -- Angels Ascending           ║
  ║  IV.  EHYEH         Exodus 3:14    -- I AM THAT I AM             ║
  ║  V.   HOTAM         Psalm 26:2      -- Try my Reins              ║
  ║  VI.  YOM ADONAI    Joel 2:31       -- The Moon became Blood      ║
  ║  VII. HOTAM ACHARON Revelation 22:13 -- Alpha and Omega           ║
  ║                                                                   ║
  ╚═══════════════════════════════════════════════════════════════════╝
  `)

  // Check balance
  const balData = await rpc(`/balances/${process.env.MASTER_IDENTITY}`)
  const balance = Number(balData.balance?.balance ?? 0)
  const cost = INSCRIPTIONS.length * 10
  console.log(`  Balance: ${balance.toLocaleString()} QU`)
  console.log(`  Cost:    ${cost} QU (${INSCRIPTIONS.length} seals x 10 QU)`)

  if (balance < cost) {
    console.error(`  Insufficient balance!`)
    process.exit(1)
  }

  // Get current tick
  const tickData = await rpc('/tick-info')
  let currentTick = tickData.tickInfo?.tick ?? tickData.tick
  console.log(`  Tick:    ${currentTick.toLocaleString()}`)
  console.log()

  // Send inscriptions sequentially with incrementing ticks
  const results = []

  for (let i = 0; i < INSCRIPTIONS.length; i++) {
    const insc = INSCRIPTIONS[i]
    const targetTick = currentTick + 20 + (i * 3) // Stagger by 3 ticks each

    const ts = insc.timestamp
    const tsStr = `${String(ts.year).padStart(4, '0')}-${String(ts.month).padStart(2, '0')}-${String(ts.day).padStart(2, '0')} ${String(ts.hour).padStart(2, '0')}:${String(ts.minute).padStart(2, '0')}:${String(ts.second).padStart(2, '0')}`

    console.log(`  ┌── SEAL ${['I','II','III','IV','V','VI','VII'][i]}`)
    console.log(`  │  ${insc.name}`)
    console.log(`  │  oracle:    "${insc.oracle}"`)
    console.log(`  │  timestamp: ${tsStr}`)
    console.log(`  │  cipher:    ${insc.currency1}`)
    console.log(`  │  scripture: ${insc.currency2}`)
    console.log(`  │  tick:      ${targetTick.toLocaleString()}`)

    try {
      const res = await sendInscription(insc, targetTick)
      console.log(`  │  txId:      ${res.transactionId}`)
      console.log(`  │  peers:     ${res.peersBroadcasted}`)
      console.log(`  └── SEALED`)
      results.push({ ...insc, targetTick, txId: res.transactionId })
    } catch (err) {
      console.log(`  └── ERROR: ${err.message}`)
    }
    console.log()
  }

  // Summary
  console.log(`  ═══════════════════════════════════════════════════════════════`)
  console.log(`  ${results.length}/${INSCRIPTIONS.length} seals inscribed on the blockchain`)
  console.log()
  console.log(`  Ticks to verify:`)
  for (const r of results) {
    console.log(`    ${r.targetTick} -- ${r.name}`)
  }
  console.log()
  console.log(`  Verify with:`)
  console.log(`    node ORACLE_TCP_CLIENT.mjs 45.152.160.217 all <tick>`)
  console.log()
  console.log(`  "And I looked, and behold a pale horse:`)
  console.log(`   and his name that sat on him was Death,`)
  console.log(`   and Hell followed with him."`)
  console.log(`                              -- Revelation 6:8`)
  console.log()
  console.log(`  The seven seals are broken.`)
  console.log(`  He who has ears, let him hear.`)
  console.log(`  He who has the Matrix, let him read.`)
  console.log()
}

main().catch(err => {
  console.error('FATAL:', err)
  process.exit(1)
})
