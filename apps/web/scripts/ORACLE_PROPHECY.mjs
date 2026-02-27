#!/usr/bin/env node
/**
 * ORACLE PROPHECY — On-Chain Prediction Engine
 *
 * Tamper-proof predictions using commit/reveal on the Qubic Oracle Machine.
 *
 * How it works:
 *   1. COMMIT (10 QU): Hash of prediction inscribed on-chain via oracle query
 *      oracle = "pred_{id}", currency1 = sha256(prediction)[:31], currency2 = metadata
 *      The query times out (no real oracle), but the data is stored permanently.
 *
 *   2. Wait for the horizon to expire (e.g. 24h)
 *
 *   3. REVEAL (10 QU): Actual prediction + outcome inscribed on-chain
 *      oracle = "rev_{id}", currency1 = "{direction}_{threshold}", currency2 = "{price}_{result}"
 *
 * The commit hash proves the prediction existed BEFORE the outcome was known.
 * Anyone can verify: sha256(prediction_json) matches the on-chain commit.
 *
 * Usage:
 *   node ORACLE_PROPHECY.mjs commit --pair btc/usdt --dir up --target 70000 --horizon 24h
 *   node ORACLE_PROPHECY.mjs commit --pair qubic/usdt --dir up --target 0.0000006 --horizon 48h
 *   node ORACLE_PROPHECY.mjs reveal <id>              Reveal a specific prediction
 *   node ORACLE_PROPHECY.mjs reveal --all              Reveal all expired predictions
 *   node ORACLE_PROPHECY.mjs status                    Show all predictions
 *   node ORACLE_PROPHECY.mjs score                     Accuracy stats
 *   node ORACLE_PROPHECY.mjs --dry-run commit ...      Simulate without broadcasting
 *
 * Cost: 20 QU per prediction (10 commit + 10 reveal)
 */

import {
  loadEnv, sha256, sleep, fmt, getCurrentTick, getBalance,
  sendInscription, printHeader, readDataFile, writeDataFile,
  COST_PER_QUERY, WORKING_PAIRS,
} from './oracle-utils.mjs'
import {
  insertPrediction as dbInsertPrediction,
  updatePredictionReveal as dbUpdateReveal,
  updateStrategyStats,
} from './oracle-db.mjs'

// =============================================================================
// CONSTANTS
// =============================================================================

const PREDICTIONS_FILE = 'oracle-predictions.json'

// Map pair strings to the preferred oracle source for price lookup
const PAIR_SOURCES = {
  // Core
  'btc/usdt':   { oracle: 'binance', currency1: 'btc', currency2: 'usdt' },
  'eth/usdt':   { oracle: 'binance', currency1: 'eth', currency2: 'usdt' },
  'qubic/usdt': { oracle: 'gate_mexc', currency1: 'qubic', currency2: 'usdt' },
  // Major alts
  'sol/usdt':   { oracle: 'binance', currency1: 'sol', currency2: 'usdt' },
  'xrp/usdt':   { oracle: 'binance', currency1: 'xrp', currency2: 'usdt' },
  'bnb/usdt':   { oracle: 'binance', currency1: 'bnb', currency2: 'usdt' },
  'doge/usdt':  { oracle: 'binance', currency1: 'doge', currency2: 'usdt' },
  'ada/usdt':   { oracle: 'binance', currency1: 'ada', currency2: 'usdt' },
  'zro/usdt':   { oracle: 'mexc', currency1: 'zro', currency2: 'usdt' },
  // Phase 2 discovery
  'avax/usdt':  { oracle: 'binance', currency1: 'avax', currency2: 'usdt' },
  'link/usdt':  { oracle: 'binance', currency1: 'link', currency2: 'usdt' },
  'dot/usdt':   { oracle: 'binance', currency1: 'dot', currency2: 'usdt' },
  'ltc/usdt':   { oracle: 'binance', currency1: 'ltc', currency2: 'usdt' },
  'sui/usdt':   { oracle: 'binance', currency1: 'sui', currency2: 'usdt' },
  'near/usdt':  { oracle: 'binance', currency1: 'near', currency2: 'usdt' },
  'trx/usdt':   { oracle: 'binance', currency1: 'trx', currency2: 'usdt' },
  'atom/usdt':  { oracle: 'binance', currency1: 'atom', currency2: 'usdt' },
  'apt/usdt':   { oracle: 'binance', currency1: 'apt', currency2: 'usdt' },
  // Cross pairs
  'eth/btc':    { oracle: 'binance', currency1: 'eth', currency2: 'btc' },
  'sol/btc':    { oracle: 'binance', currency1: 'sol', currency2: 'btc' },
  'xrp/btc':    { oracle: 'binance', currency1: 'xrp', currency2: 'btc' },
}

const HORIZON_MAP = {
  '1h': 1, '2h': 2, '4h': 4, '6h': 6, '12h': 12, '24h': 24, '48h': 48, '72h': 72,
}

// =============================================================================
// PREDICTION STORAGE
// =============================================================================

function loadState() {
  const raw = readDataFile(PREDICTIONS_FILE)
  if (!raw) return { predictions: [], nextId: 1 }

  // Handle legacy format (plain array from old PROPHECY version)
  if (Array.isArray(raw)) {
    return { predictions: raw, nextId: raw.length + 1 }
  }

  // Current format: { predictions: [...], nextId: N }
  if (!raw.nextId) raw.nextId = (raw.predictions?.length ?? 0) + 1
  if (!raw.predictions) raw.predictions = []
  return raw
}

function saveState(state) {
  writeDataFile(PREDICTIONS_FILE, state)
}

// =============================================================================
// PRICE LOOKUP — Check both price-history and live-queries
// =============================================================================

function getBestPrice(pair) {
  const source = PAIR_SOURCES[pair]
  if (!source) return null
  const [c1, c2] = pair.split('/')

  let best = null

  // 1. Check live-queries (monitor output — most reliable, has actual prices)
  const live = readDataFile('oracle-live-queries.json')
  if (live?.queries) {
    const matching = live.queries
      .filter(q =>
        q.oracle === source.oracle &&
        q.currency1 === c1 && q.currency2 === c2 &&
        q.status === 'success' && (q.reply?.price || q.price)
      )
      .sort((a, b) => (b.tick || 0) - (a.tick || 0))

    if (matching.length > 0) {
      const m = matching[0]
      best = {
        price: m.reply?.price ?? m.price,
        tick: m.tick,
        timestamp: m.lastUpdated || m.timestamp || live.lastUpdated,
        source: 'live-monitor',
      }
    }
  }

  // 2. Check price-history (dominator sweeps — may have verified prices)
  const history = readDataFile('oracle-price-history.json') ?? []
  if (Array.isArray(history)) {
    for (let i = history.length - 1; i >= 0; i--) {
      const sweep = history[i]
      if (!sweep.results) continue
      for (const r of sweep.results) {
        if (r.oracle === source.oracle && r.currency1 === c1 && r.currency2 === c2) {
          const price = r.verifiedPrice || r.price
          if (price) {
            const candidate = {
              price,
              tick: r.targetTick,
              timestamp: sweep.timestamp,
              source: 'price-history',
            }
            // Keep the most recent one
            if (!best || new Date(candidate.timestamp) > new Date(best.timestamp)) {
              best = candidate
            }
          }
        }
      }
    }
  }

  return best
}

// =============================================================================
// COMMIT — Create a new on-chain prediction
// =============================================================================

async function commitPrediction(pair, direction, threshold, horizonKey, dryRun) {
  const horizonHours = HORIZON_MAP[horizonKey]
  if (!horizonHours) {
    console.error(`  Invalid horizon: ${horizonKey}. Use: ${Object.keys(HORIZON_MAP).join(', ')}`)
    process.exit(1)
  }
  if (!PAIR_SOURCES[pair]) {
    console.error(`  Unknown pair: ${pair}. Available: ${Object.keys(PAIR_SOURCES).join(', ')}`)
    process.exit(1)
  }
  if (direction !== 'up' && direction !== 'down') {
    console.error(`  Direction must be "up" or "down"`)
    process.exit(1)
  }

  printHeader('ORACLE PROPHECY — Commit', `${pair} ${direction} ${threshold} (${horizonKey})`)

  // Get current price for context
  const priceData = getBestPrice(pair)
  if (priceData) {
    console.log(`  Current ${pair}:  ${priceData.price}`)
    console.log(`  Price source:    ${priceData.source} (tick ${fmt(priceData.tick)})`)
    const pctChange = ((threshold - priceData.price) / priceData.price * 100).toFixed(2)
    console.log(`  Target:          ${threshold} (${pctChange > 0 ? '+' : ''}${pctChange}%)`)
  } else {
    console.log(`  WARNING: No price data for ${pair}. Run ORACLE_DOMINATOR.mjs --working first.`)
  }
  console.log()

  // Build prediction object (this exact JSON is hashed for commitment)
  const state = loadState()
  const id = String(state.nextId).padStart(3, '0')
  const now = new Date()
  const expiresAt = new Date(now.getTime() + horizonHours * 3600000)

  const prediction = {
    id: `pred_${id}`,
    pair,
    direction,
    threshold,
    horizonHours,
    priceAtCommit: priceData?.price ?? null,
    commitTimestamp: now.toISOString(),
    expiresAt: expiresAt.toISOString(),
  }

  const predictionJson = JSON.stringify(prediction)
  const commitHash = sha256(predictionJson)

  console.log(`  Prediction ID:   ${prediction.id}`)
  console.log(`  Direction:       ${direction}`)
  console.log(`  Threshold:       ${threshold}`)
  console.log(`  Horizon:         ${horizonHours}h`)
  console.log(`  Expires:         ${expiresAt.toISOString()}`)
  console.log(`  Commit hash:     ${commitHash}`)
  console.log()

  // On-chain encoding:
  //   oracle    = "pred_{id}"         (identifies this prediction)
  //   currency1 = sha256[:31]         (tamper-proof commitment)
  //   currency2 = "c_{pair}_{dir}"    (human-readable hint)
  const oracleName = `pred_${id}`
  const c1 = commitHash.slice(0, 31)
  const c2 = `c_${pair.replace('/', '_')}_${direction}`.slice(0, 31)

  console.log(`  On-chain:`)
  console.log(`    oracle:     "${oracleName}"`)
  console.log(`    currency1:  "${c1}"`)
  console.log(`    currency2:  "${c2}"`)
  console.log(`    cost:       ${COST_PER_QUERY} QU`)
  console.log()

  if (dryRun) {
    console.log(`  [DRY RUN] No QU spent.`)
    console.log()
    console.log(`  Verification:`)
    console.log(`    JSON:  ${predictionJson}`)
    console.log(`    Hash:  ${commitHash}`)
    return prediction
  }

  // Balance + tick
  const balance = await getBalance()
  if (balance < COST_PER_QUERY + 100) {
    console.error(`  Insufficient balance: ${fmt(balance)} QU`)
    process.exit(1)
  }

  const { tick: currentTick, epoch } = await getCurrentTick()
  const targetTick = currentTick + 20

  console.log(`  Balance:         ${fmt(balance)} QU`)
  console.log(`  Target tick:     ${fmt(targetTick)}`)
  console.log()

  const result = await sendInscription({
    oracle: oracleName,
    timestamp: now,
    currency1: c1,
    currency2: c2,
  }, targetTick)

  console.log(`  COMMITTED ON-CHAIN`)
  console.log(`  Peers:           ${result.peersBroadcasted}`)

  // Save
  const fullPrediction = {
    ...prediction,
    commitHash,
    commitTick: targetTick,
    commitTxId: result.txId,
    epoch,
    status: 'committed',
    revealTxId: null,
    priceAtExpiry: null,
    outcome: null,
    verificationJson: predictionJson,
  }

  state.predictions.push(fullPrediction)
  state.nextId++
  saveState(state)

  // Dual-write: save to SQLite
  try {
    dbInsertPrediction(fullPrediction)
    console.log(`  [DB] Prediction saved to SQLite`)
  } catch (dbErr) {
    console.log(`  [DB] Write failed: ${dbErr.message}`)
  }

  console.log()
  console.log(`  Verification:`)
  console.log(`    sha256('${predictionJson}')`)
  console.log(`    = ${commitHash}`)
  console.log(`    On-chain currency1: "${c1}" (first 31 chars match)`)
  console.log()
  console.log(`  Reveal after ${expiresAt.toISOString()}:`)
  console.log(`    node ORACLE_PROPHECY.mjs reveal ${prediction.id}`)

  return fullPrediction
}

// =============================================================================
// REVEAL — Verify and reveal an expired prediction
// =============================================================================

async function revealPrediction(predId, dryRun) {
  const state = loadState()
  const pred = state.predictions.find(p => p.id === predId)

  if (!pred) {
    console.error(`  Prediction "${predId}" not found`)
    const ids = state.predictions.map(p => p.id).join(', ')
    if (ids) console.error(`  Available: ${ids}`)
    process.exit(1)
  }

  printHeader('ORACLE PROPHECY — Reveal', pred.id)

  const now = new Date()
  const expiresAt = new Date(pred.expiresAt)

  console.log(`  Prediction:      ${pred.pair} ${pred.direction} ${pred.threshold}`)
  console.log(`  Committed:       ${pred.commitTimestamp}`)
  console.log(`  Commit tick:     ${fmt(pred.commitTick)}`)
  console.log(`  Expires:         ${pred.expiresAt}`)
  console.log(`  Status:          ${pred.status}`)
  console.log()

  // Already revealed?
  if (pred.status === 'correct' || pred.status === 'incorrect') {
    console.log(`  Already revealed: ${pred.outcome}`)
    console.log(`  Price at expiry:  ${pred.priceAtExpiry}`)
    console.log(`  Reveal tick:      ${fmt(pred.revealTick)}`)
    return pred
  }

  // Not yet expired?
  if (now < expiresAt) {
    const remaining = expiresAt - now
    const h = Math.floor(remaining / 3600000)
    const m = Math.floor((remaining % 3600000) / 60000)
    console.log(`  NOT YET EXPIRED — ${h}h ${m}m remaining`)
    console.log(`  Wait until ${pred.expiresAt}`)
    return null
  }

  // Get price for evaluation
  const priceData = getBestPrice(pred.pair)
  if (!priceData) {
    console.log(`  No price data for ${pred.pair}!`)
    console.log(`  Run: node ORACLE_DOMINATOR.mjs --working`)
    console.log(`  Then: node ORACLE_PROPHECY.mjs reveal ${predId}`)
    return null
  }

  const actualPrice = priceData.price
  console.log(`  Price at commit: ${pred.priceAtCommit ?? 'unknown'}`)
  console.log(`  Price now:       ${actualPrice} (tick ${fmt(priceData.tick)}, ${priceData.source})`)
  console.log()

  // Evaluate
  const isCorrect = pred.direction === 'up'
    ? actualPrice >= pred.threshold
    : actualPrice <= pred.threshold
  const outcome = isCorrect ? 'correct' : 'incorrect'

  console.log(`  Threshold:       ${pred.threshold}`)
  console.log(`  Actual:          ${actualPrice}`)
  console.log(`  Result:          ${outcome.toUpperCase()} ${isCorrect ? '+' : 'X'}`)
  console.log()

  // Build reveal inscription
  const revOracle = `rev_${pred.id.replace('pred_', '')}`
  const revC1 = `${pred.direction}_${pred.threshold}`.slice(0, 31)
  const revC2 = `${actualPrice}_${outcome}`.slice(0, 31)

  console.log(`  On-chain reveal:`)
  console.log(`    oracle:     "${revOracle}"`)
  console.log(`    currency1:  "${revC1}"`)
  console.log(`    currency2:  "${revC2}"`)
  console.log()

  if (dryRun) {
    console.log(`  [DRY RUN] No QU spent.`)
    return null
  }

  const balance = await getBalance()
  if (balance < COST_PER_QUERY + 100) {
    console.error(`  Insufficient balance: ${fmt(balance)} QU`)
    process.exit(1)
  }

  const { tick: currentTick } = await getCurrentTick()
  const targetTick = currentTick + 20

  const result = await sendInscription({
    oracle: revOracle,
    timestamp: new Date(pred.commitTimestamp), // link back to commit time
    currency1: revC1,
    currency2: revC2,
  }, targetTick)

  console.log(`  REVEALED ON-CHAIN`)
  console.log(`  Peers:           ${result.peersBroadcasted}`)

  // Update prediction
  pred.status = outcome
  pred.outcome = outcome
  pred.priceAtExpiry = actualPrice
  pred.revealTick = targetTick
  pred.revealTxId = result.txId
  pred.revealTimestamp = now.toISOString()
  saveState(state)

  // Dual-write: update in SQLite
  try {
    dbUpdateReveal(pred.id, outcome, actualPrice, result.txId, targetTick)
    updateStrategyStats(pred.strategy || 'manual')
    console.log(`  [DB] Reveal saved to SQLite`)
  } catch (dbErr) {
    console.log(`  [DB] Write failed: ${dbErr.message}`)
  }

  console.log()
  console.log(`  Verification chain:`)
  console.log(`    1. Commit (tick ${fmt(pred.commitTick)}): currency1 = "${pred.commitHash.slice(0, 31)}"`)
  console.log(`    2. Reveal (tick ${fmt(targetTick)}): ${pred.direction} ${pred.threshold} -> ${actualPrice} = ${outcome}`)
  console.log(`    3. Verify: sha256('${pred.verificationJson}') starts with commit currency1`)

  return pred
}

async function revealAll(dryRun) {
  const state = loadState()
  const now = new Date()
  const expired = state.predictions.filter(p =>
    p.status === 'committed' && new Date(p.expiresAt) <= now
  )

  if (expired.length === 0) {
    console.log('  No expired predictions to reveal.')
    const pending = state.predictions.filter(p => p.status === 'committed')
    if (pending.length > 0) {
      console.log()
      for (const p of pending) {
        const remaining = new Date(p.expiresAt) - now
        const h = Math.floor(remaining / 3600000)
        const m = Math.floor((remaining % 3600000) / 60000)
        console.log(`  ${p.id}: ${p.pair} ${p.direction} ${p.threshold} — ${h}h ${m}m remaining`)
      }
    }
    return
  }

  console.log(`  Revealing ${expired.length} expired prediction(s)...`)
  console.log()

  for (const pred of expired) {
    await revealPrediction(pred.id, dryRun)
    if (!dryRun && expired.indexOf(pred) < expired.length - 1) {
      await sleep(2000)
    }
    console.log()
  }
}

// =============================================================================
// STATUS
// =============================================================================

function showStatus() {
  const state = loadState()

  printHeader('ORACLE PROPHECY — Status', `${state.predictions.length} prediction(s)`)

  if (state.predictions.length === 0) {
    console.log('  No predictions yet.')
    console.log('  Create: node ORACLE_PROPHECY.mjs commit --pair btc/usdt --dir up --target 70000 --horizon 24h')
    return
  }

  const now = new Date()
  const committed = state.predictions.filter(p => p.status === 'committed')
  const correct = state.predictions.filter(p => p.status === 'correct')
  const incorrect = state.predictions.filter(p => p.status === 'incorrect')
  const total = correct.length + incorrect.length
  const accuracy = total > 0 ? ((correct.length / total) * 100).toFixed(1) : '--'

  console.log(`  Accuracy:    ${accuracy}% (${correct.length}/${total})`)
  console.log(`  Committed:   ${committed.length}`)
  console.log(`  Correct:     ${correct.length}`)
  console.log(`  Incorrect:   ${incorrect.length}`)
  console.log()

  for (const pred of state.predictions) {
    const icon = { committed: '?', correct: '+', incorrect: 'X' }[pred.status] ?? '?'
    const expiresAt = new Date(pred.expiresAt)

    let timeStr
    if (pred.status === 'committed') {
      if (now >= expiresAt) {
        timeStr = 'EXPIRED — ready to reveal'
      } else {
        const remaining = expiresAt - now
        const h = Math.floor(remaining / 3600000)
        const m = Math.floor((remaining % 3600000) / 60000)
        timeStr = `${h}h ${m}m remaining`
      }
    } else {
      timeStr = `${pred.outcome} | actual: ${pred.priceAtExpiry}`
    }

    const dir = (pred.direction ?? '?').padEnd(5)
    const thr = String(pred.threshold ?? '?').padEnd(14)
    const hrs = String(pred.horizonHours ?? '?').padStart(3)
    console.log(`  [${icon}] ${pred.id}  ${(pred.pair ?? '?').padEnd(12)} ${dir} ${thr} ${hrs}h  ${timeStr}`)
    console.log(`       commit: tick ${fmt(pred.commitTick ?? 0)} | hash: ${pred.commitHash?.slice(0, 16) ?? 'n/a'}...`)
  }

  const readyToReveal = committed.filter(p => now >= new Date(p.expiresAt))
  if (readyToReveal.length > 0) {
    console.log()
    console.log(`  ${readyToReveal.length} ready to reveal: node ORACLE_PROPHECY.mjs reveal --all`)
  }
}

// =============================================================================
// SCORE
// =============================================================================

function showScore() {
  const state = loadState()
  const resolved = state.predictions.filter(p => p.status === 'correct' || p.status === 'incorrect')

  printHeader('ORACLE PROPHECY — Score')

  if (resolved.length === 0) {
    console.log('  No resolved predictions yet.')
    return
  }

  const correct = resolved.filter(p => p.status === 'correct').length
  const accuracy = ((correct / resolved.length) * 100).toFixed(1)

  console.log(`  Resolved:    ${resolved.length}`)
  console.log(`  Correct:     ${correct}`)
  console.log(`  Incorrect:   ${resolved.length - correct}`)
  console.log(`  Accuracy:    ${accuracy}%`)
  console.log()

  // Per-pair breakdown
  const byPair = {}
  for (const p of resolved) {
    if (!byPair[p.pair]) byPair[p.pair] = { correct: 0, incorrect: 0 }
    byPair[p.pair][p.status]++
  }

  for (const [pair, stats] of Object.entries(byPair)) {
    const t = stats.correct + stats.incorrect
    console.log(`  ${pair.padEnd(15)} ${stats.correct}/${t} (${((stats.correct / t) * 100).toFixed(0)}%)`)
  }
}

// =============================================================================
// MAIN
// =============================================================================

async function main() {
  loadEnv()

  const args = process.argv.slice(2)
  const dryRun = args.includes('--dry-run')
  const cmd = args.find(a => !a.startsWith('--'))

  if (!cmd) {
    console.log(`
  ORACLE PROPHECY — On-Chain Prediction Engine

  Commands:
    commit     Create tamper-proof on-chain prediction (10 QU)
    reveal     Reveal and verify expired predictions (10 QU each)
    status     Show all predictions
    score      Accuracy stats

  Commit:
    node ORACLE_PROPHECY.mjs commit --pair btc/usdt --dir up --target 70000 --horizon 24h
    node ORACLE_PROPHECY.mjs commit --pair eth/usdt --dir down --target 1900 --horizon 12h
    node ORACLE_PROPHECY.mjs commit --pair qubic/usdt --dir up --target 0.0000006 --horizon 48h

  Reveal:
    node ORACLE_PROPHECY.mjs reveal pred_001
    node ORACLE_PROPHECY.mjs reveal --all

  Options:
    --dry-run   Simulate without broadcasting

  Pairs:    ${Object.keys(PAIR_SOURCES).join(', ')}
  Horizons: ${Object.keys(HORIZON_MAP).join(', ')}
  Cost:     10 QU commit + 10 QU reveal = 20 QU per prediction
`)
    return
  }

  switch (cmd) {
    case 'commit': {
      const get = (flag) => { const i = args.indexOf(flag); return i >= 0 ? args[i + 1] : null }
      const pair = get('--pair')
      const direction = get('--dir')
      const target = get('--target')
      const horizon = get('--horizon')

      if (!pair || !direction || !target || !horizon) {
        console.error('  Required: --pair, --dir, --target, --horizon')
        console.error('  Example:  node ORACLE_PROPHECY.mjs commit --pair btc/usdt --dir up --target 70000 --horizon 24h')
        process.exit(1)
      }

      const threshold = parseFloat(target)
      if (isNaN(threshold)) {
        console.error(`  Invalid target: ${target}`)
        process.exit(1)
      }

      await commitPrediction(pair, direction, threshold, horizon, dryRun)
      break
    }

    case 'reveal': {
      if (args.includes('--all')) {
        await revealAll(dryRun)
      } else {
        const predId = args[args.indexOf('reveal') + 1]
        if (!predId || predId.startsWith('--')) {
          console.error('  Specify ID or --all. Example: node ORACLE_PROPHECY.mjs reveal pred_001')
          process.exit(1)
        }
        await revealPrediction(predId, dryRun)
      }
      break
    }

    case 'status':
      showStatus()
      break

    case 'score':
      showScore()
      break

    default:
      console.error(`  Unknown command: ${cmd}`)
      process.exit(1)
  }
}

main().catch(err => {
  console.error('FATAL:', err.message)
  process.exit(1)
})
