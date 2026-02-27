#!/usr/bin/env node
/**
 * ORACLE AUTOPILOT — Automated Prediction Pipeline
 *
 * Full automation cycle:
 *   1. COLLECT — Get fresh prices
 *   2. GENERATE — Run all strategies on all pairs
 *   3. FILTER — Remove duplicates, low-confidence
 *   4. RANK — Sort by confidence * backtest_accuracy
 *   5. BUDGET — Select top N within QU budget
 *   6. COMMIT — On-chain inscribe
 *   7. REVEAL — Reveal all expired predictions
 *   8. UPDATE — Refresh strategy performance
 *   9. EXPORT — Dashboard JSON export
 *
 * Usage:
 *   node ORACLE_AUTOPILOT.mjs                        # Single run, 1000 QU budget
 *   node ORACLE_AUTOPILOT.mjs --budget 500           # Custom budget
 *   node ORACLE_AUTOPILOT.mjs --dry-run              # Show plan, commit nothing
 *   node ORACLE_AUTOPILOT.mjs --loop --interval 60   # Every 60 minutes
 */

import {
  loadEnv, sha256, sleep, fmt, getCurrentTick, getBalance,
  sendInscription, printHeader, readDataFile, writeDataFile,
  COST_PER_QUERY, WORKING_PAIRS,
} from './oracle-utils.mjs'
import {
  getDb, closeDb, insertPrediction as dbInsertPrediction,
  updatePredictionReveal, updateStrategyStats,
  getPriceHistory, getPriceHistoryByTime, getLatestPrice, getLatestPrices,
  getAllPredictions, getExpiredPredictions,
  insertPipelineRun, updatePipelineRunResults,
  getActiveStrategies,
} from './oracle-db.mjs'
import { runAllStrategies, strategies } from './strategies/index.mjs'
import { exportDashboard } from './oracle-export.mjs'
import { randomBytes } from 'crypto'

// =============================================================================
// CONSTANTS
// =============================================================================

const PREDICTIONS_FILE = 'oracle-predictions.json'
const COST_PER_PREDICTION = COST_PER_QUERY // 10 QU commit + 10 QU reveal = 20 total, but commit is 10

// Dynamic PAIR_SOURCES — generated from WORKING_PAIRS
// For predictions: pick best oracle per unique pair (binance preferred)
// Oracle preference: binance > gate > mexc > composite oracles
const ORACLE_PRIORITY = ['binance', 'gate', 'mexc', 'gate_mexc', 'binance_mexc', 'binance_gate']

function buildPairSources() {
  const sources = {}
  for (const wp of WORKING_PAIRS) {
    const key = `${wp.currency1}/${wp.currency2}`
    const existing = sources[key]
    if (!existing) {
      sources[key] = { oracle: wp.oracle, currency1: wp.currency1, currency2: wp.currency2 }
    } else {
      // Replace if new oracle has higher priority
      const newPri = ORACLE_PRIORITY.indexOf(wp.oracle)
      const oldPri = ORACLE_PRIORITY.indexOf(existing.oracle)
      if (newPri >= 0 && (oldPri < 0 || newPri < oldPri)) {
        sources[key] = { oracle: wp.oracle, currency1: wp.currency1, currency2: wp.currency2 }
      }
    }
  }
  return sources
}

const PAIR_SOURCES = buildPairSources()

/**
 * Get ALL oracle sources for a pair (for arbitrage / cross-oracle analysis).
 * @param {string} pair — e.g. 'btc/usdt'
 * @returns {Array<{oracle, currency1, currency2}>}
 */
function getAllOraclesForPair(pair) {
  const [c1, c2] = pair.split('/')
  return WORKING_PAIRS.filter(wp => wp.currency1 === c1 && wp.currency2 === c2)
}

// Ordered by live accuracy: 4h=85.7%, 1h=82.7%, 2h=64.3%
const HORIZONS = [1, 4, 2]

// =============================================================================
// PIPELINE
// =============================================================================

async function runPipeline(options = {}) {
  const { budget = 1000, dryRun = false } = options
  const startTime = Date.now()
  const runId = `run_${Date.now().toString(36)}_${randomBytes(3).toString('hex')}`

  printHeader('ORACLE AUTOPILOT', `Budget: ${budget} QU | ${dryRun ? 'DRY RUN' : 'LIVE'}`)

  const db = getDb()

  // ─── 1. COLLECT — Get latest prices from DB ───────────────────────────
  console.log('  1. COLLECT — Fetching latest prices...')
  const latestPrices = getLatestPrices()
  console.log(`     ${latestPrices.length} pairs with price data`)

  if (latestPrices.length === 0) {
    console.log('     No prices in DB. Run ORACLE_DOMINATOR first.')
    return
  }

  // ─── 2. GENERATE — Run all strategies ─────────────────────────────────
  console.log()
  console.log('  2. GENERATE — Running strategies...')

  const candidates = []

  // Preload all price histories — use time-based query (120 min window)
  // to get enough data for strategies that need 30-60 min of candles
  const allPricesMap = {}
  for (const priceRow of latestPrices) {
    const pair = priceRow.pair
    if (!PAIR_SOURCES[pair]) continue
    const history = getPriceHistoryByTime(pair, 120)
    allPricesMap[pair] = history.map(r => ({
      price: r.price,
      timestamp: r.timestamp,
      oracle: r.oracle,
    }))
  }
  const totalPreloaded = Object.values(allPricesMap).reduce((s, h) => s + h.length, 0)
  console.log(`     Preloaded ${totalPreloaded} price points across ${Object.keys(allPricesMap).length} pairs`)

  for (const priceRow of latestPrices) {
    const pair = priceRow.pair
    if (!PAIR_SOURCES[pair]) continue

    const currentPrice = priceRow.price
    const history = allPricesMap[pair] || []

    for (const horizon of HORIZONS) {
      const ctx = {
        pair,
        currentPrice,
        priceHistory: history,
        horizonHours: horizon,
        allPrices: allPricesMap,
      }

      const signals = runAllStrategies(ctx)
      for (const signal of signals) {
        candidates.push({
          ...signal,
          pair,
          currentPrice,
          horizonHours: horizon,
        })
      }
    }
  }

  console.log(`     ${candidates.length} raw signals generated`)

  // ─── 3. FILTER — Remove low confidence ────────────────────────────────
  console.log()
  console.log('  3. FILTER — Removing low-confidence...')

  // Higher min confidence (0.40) filters out noise — round 1 showed low-conf predictions underperform
  const filtered = candidates.filter(c => c.confidence >= 0.40)

  // Remove duplicate pair+horizon+direction combos (keep highest confidence)
  const deduped = new Map()
  for (const c of filtered) {
    const key = `${c.pair}_${c.horizonHours}_${c.direction}`
    const existing = deduped.get(key)
    if (!existing || c.confidence > existing.confidence) {
      deduped.set(key, c)
    }
  }

  const unique = [...deduped.values()]
  console.log(`     ${filtered.length} above threshold → ${unique.length} unique`)

  // ─── 4. RANK — Sort by confidence ─────────────────────────────────────
  console.log()
  console.log('  4. RANK — Sorting by confidence...')

  unique.sort((a, b) => b.confidence - a.confidence)

  // ─── 5. BUDGET — Tiered strategy allocation ─────────────────────────────
  console.log()
  console.log('  5. BUDGET — Tiered strategy allocation...')

  const maxPredictions = Math.floor(budget / COST_PER_PREDICTION)

  // Strategy tiers — optimized from LIVE results (Round 2+):
  // conservative: 47/47 = 100% (proven star)
  // mean_reversion: 0/3 live (all Round 1 pre-fix), backtest 100% → keep moderate
  // consensus: 9/16 = 56.3% (DOWN margin was too tight, now fixed to 0.8x)
  // volatility_breakout: 4/6 = 67% (decent)
  // arbitrage_signal: 27 pending (untested but promising signals)
  // momentum: 0/10 (all Round 1 pre-fix, untested on v3)
  // cross_asset: 0/2 (too few samples)
  const TIERS = [
    { strategy: 'conservative',        pct: 0.30 },
    { strategy: 'mean_reversion',      pct: 0.18 },
    { strategy: 'consensus',           pct: 0.12 },
    { strategy: 'arbitrage_signal',    pct: 0.12 },
    { strategy: 'volatility_breakout', pct: 0.10 },
    { strategy: 'momentum',            pct: 0.08 },
    { strategy: 'cross_asset',         pct: 0.10 },
  ]

  // Dynamic adjustment: boost strategies with good backtest accuracy
  try {
    const activeStrats = getActiveStrategies()
    if (activeStrats.length > 0) {
      for (const tier of TIERS) {
        const stats = activeStrats.find(s => s.name === tier.strategy)
        if (stats && stats.accuracy != null && stats.totalPredictions >= 5) {
          // Boost/penalize: +/- up to 50% of base allocation
          const accDelta = (stats.accuracy - 50) / 100 // e.g. 65% → +0.15
          tier.pct *= (1 + Math.max(-0.5, Math.min(0.5, accDelta)))
        }
      }
      // Renormalize to 100%
      const totalPct = TIERS.reduce((s, t) => s + t.pct, 0)
      for (const tier of TIERS) tier.pct /= totalPct
    }
  } catch { /* use base allocation */ }

  // Group candidates by strategy
  const byStrategy = new Map()
  for (const c of unique) {
    const list = byStrategy.get(c.strategy) || []
    list.push(c)
    byStrategy.set(c.strategy, list)
  }

  // Allocate slots per tier, overflow goes to next tier
  const selected = []
  let slotsRemaining = maxPredictions
  const overflow = [] // candidates from tiers that had fewer than their allocation

  for (const tier of TIERS) {
    const tierSlots = Math.max(1, Math.round(maxPredictions * tier.pct))
    const pool = byStrategy.get(tier.strategy) || []
    pool.sort((a, b) => b.confidence - a.confidence)

    const take = Math.min(tierSlots, pool.length, slotsRemaining)
    for (let i = 0; i < take; i++) {
      selected.push(pool[i])
      slotsRemaining--
    }
    // Track unused candidates for overflow
    for (let i = take; i < pool.length; i++) {
      overflow.push(pool[i])
    }

    console.log(`     ${tier.strategy}: ${take}/${tierSlots} slots (${pool.length} available)`)
  }

  // Fill remaining slots from overflow (best confidence first)
  if (slotsRemaining > 0 && overflow.length > 0) {
    overflow.sort((a, b) => b.confidence - a.confidence)
    const extra = overflow.slice(0, slotsRemaining)
    selected.push(...extra)
    slotsRemaining -= extra.length
    console.log(`     overflow: ${extra.length} extra slots filled`)
  }

  const totalCost = selected.length * COST_PER_PREDICTION

  console.log(`     Budget: ${budget} QU → max ${maxPredictions} predictions`)
  console.log(`     Selected: ${selected.length} predictions (${totalCost} QU)`)
  console.log()

  // Print selection table
  console.log(`  ${'#'.padEnd(4)} ${'Pair'.padEnd(14)} ${'Dir'.padEnd(6)} ${'Threshold'.padEnd(14)} ${'Horizon'.padEnd(8)} ${'Conf'.padEnd(6)} ${'Strategy'.padEnd(16)} Reason`)
  console.log(`  ${'-'.repeat(90)}`)
  for (let i = 0; i < selected.length; i++) {
    const s = selected[i]
    console.log(`  ${String(i + 1).padEnd(4)} ${s.pair.padEnd(14)} ${s.direction.padEnd(6)} ${String(s.threshold.toPrecision(6)).padEnd(14)} ${(s.horizonHours + 'h').padEnd(8)} ${String(s.confidence).padEnd(6)} ${s.strategy.padEnd(16)} ${s.reason.slice(0, 40)}`)
  }
  console.log()

  if (dryRun) {
    console.log('  [DRY RUN] No predictions committed.')
    console.log()

    // Still do reveals + export in dry run
    await revealExpired(dryRun)
    exportDashboard()
    return
  }

  // ─── 6. COMMIT — Inscribe on-chain ────────────────────────────────────
  console.log('  6. COMMIT — Inscribing on-chain...')

  const balance = await getBalance()
  if (balance < totalCost + 200) {
    console.log(`     Insufficient balance: ${fmt(balance)} QU (need ${totalCost + 200})`)
    return
  }

  const { tick: currentTick, epoch } = await getCurrentTick()
  const state = loadPredictionState()
  let committed = 0

  for (let i = 0; i < selected.length; i++) {
    const s = selected[i]
    const id = String(state.nextId).padStart(3, '0')
    const now = new Date()
    const expiresAt = new Date(now.getTime() + s.horizonHours * 3600000)

    const prediction = {
      id: `pred_${id}`,
      pair: s.pair,
      direction: s.direction,
      threshold: s.threshold,
      horizonHours: s.horizonHours,
      priceAtCommit: s.currentPrice,
      commitTimestamp: now.toISOString(),
      expiresAt: expiresAt.toISOString(),
    }

    const predictionJson = JSON.stringify(prediction)
    const commitHash = sha256(predictionJson)

    const oracleName = `pred_${id}`
    const c1 = commitHash.slice(0, 31)
    const c2 = `c_${s.pair.replace('/', '_')}_${s.direction}`.slice(0, 31)
    const targetTick = currentTick + 20 + (i * 3)

    try {
      const result = await sendInscription({
        oracle: oracleName,
        timestamp: now,
        currency1: c1,
        currency2: c2,
      }, targetTick)

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
        strategy: s.strategy,
        confidence: s.confidence,
        strategyParams: s.reason,
      }

      // Save to JSON (backward compat)
      state.predictions.push(fullPrediction)
      state.nextId++

      // Save to DB
      try { dbInsertPrediction(fullPrediction) } catch (e) { /* ignore dup */ }

      console.log(`     [+] ${prediction.id} ${s.pair} ${s.direction} ${s.threshold} (${s.strategy}, ${s.confidence})`)
      committed++

      if (i < selected.length - 1) await sleep(500)
    } catch (err) {
      console.log(`     [X] ${prediction.id} FAILED: ${err.message}`)
    }
  }

  savePredictionState(state)
  console.log(`     ${committed}/${selected.length} committed`)
  console.log()

  // ─── 7. REVEAL — Reveal expired predictions ───────────────────────────
  await revealExpired(dryRun)

  // ─── 8. UPDATE — Refresh strategy stats ───────────────────────────────
  console.log('  8. UPDATE — Refreshing strategy stats...')
  for (const [name] of strategies) {
    try { updateStrategyStats(name) } catch (e) { /* skip */ }
  }
  console.log('     Done')
  console.log()

  // ─── 9. EXPORT — Dashboard JSON ───────────────────────────────────────
  console.log('  9. EXPORT — Generating dashboard JSON...')
  exportDashboard()
  console.log()

  // ─── Pipeline Run Record ──────────────────────────────────────────────
  try {
    insertPipelineRun({
      id: runId,
      epoch,
      timestamp: new Date().toISOString(),
      budgetQu: budget,
      predictionsGenerated: candidates.length,
      predictionsCommitted: committed,
      costQu: committed * COST_PER_PREDICTION,
      strategiesUsed: [...new Set(selected.map(s => s.strategy))],
    })
  } catch (e) { /* skip */ }

  const duration = Date.now() - startTime
  console.log(`  ${'='.repeat(65)}`)
  console.log(`  AUTOPILOT COMPLETE`)
  console.log(`  Committed: ${committed} | Cost: ${committed * COST_PER_PREDICTION} QU | Time: ${(duration / 1000).toFixed(1)}s`)
  console.log(`  ${'='.repeat(65)}`)
}

// =============================================================================
// REVEAL EXPIRED
// =============================================================================

async function revealExpired(dryRun) {
  console.log('  7. REVEAL — Checking expired predictions...')

  const state = loadPredictionState()
  const now = new Date()
  const expired = state.predictions.filter(p =>
    p.status === 'committed' && new Date(p.expiresAt) <= now
  )

  if (expired.length === 0) {
    console.log('     No expired predictions to reveal.')
    console.log()
    return
  }

  console.log(`     ${expired.length} expired prediction(s)`)

  if (dryRun) {
    for (const p of expired) {
      console.log(`     [DRY] ${p.id} ${p.pair} ${p.direction} ${p.threshold}`)
    }
    console.log()
    return
  }

  let revealed = 0
  for (const pred of expired) {
    const priceData = getBestPrice(pred.pair)
    if (!priceData) {
      console.log(`     [!] ${pred.id} — No price data for ${pred.pair}`)
      continue
    }

    const actualPrice = priceData.price
    const isCorrect = pred.direction === 'up'
      ? actualPrice >= pred.threshold
      : actualPrice <= pred.threshold
    const outcome = isCorrect ? 'correct' : 'incorrect'

    const revOracle = `rev_${pred.id.replace('pred_', '')}`
    const revC1 = `${pred.direction}_${pred.threshold}`.slice(0, 31)
    const revC2 = `${actualPrice}_${outcome}`.slice(0, 31)

    try {
      const { tick: currentTick } = await getCurrentTick()
      const targetTick = currentTick + 20

      const result = await sendInscription({
        oracle: revOracle,
        timestamp: new Date(pred.commitTimestamp),
        currency1: revC1,
        currency2: revC2,
      }, targetTick)

      pred.status = outcome
      pred.outcome = outcome
      pred.priceAtExpiry = actualPrice
      pred.revealTick = targetTick
      pred.revealTxId = result.txId
      pred.revealTimestamp = now.toISOString()

      // DB update
      try {
        updatePredictionReveal(pred.id, outcome, actualPrice, result.txId, targetTick)
        updateStrategyStats(pred.strategy || 'manual')
      } catch (e) { /* skip */ }

      const icon = isCorrect ? '+' : 'X'
      console.log(`     [${icon}] ${pred.id} ${pred.pair} ${pred.direction} ${pred.threshold} → ${actualPrice} = ${outcome}`)
      revealed++

      await sleep(1500)
    } catch (err) {
      console.log(`     [!] ${pred.id} reveal failed: ${err.message}`)
    }
  }

  savePredictionState(state)
  console.log(`     ${revealed}/${expired.length} revealed`)
  console.log()
}

// =============================================================================
// HELPERS
// =============================================================================

function loadPredictionState() {
  const raw = readDataFile(PREDICTIONS_FILE)
  if (!raw) return { predictions: [], nextId: 1 }
  if (Array.isArray(raw)) return { predictions: raw, nextId: raw.length + 1 }
  if (!raw.nextId) raw.nextId = (raw.predictions?.length ?? 0) + 1
  if (!raw.predictions) raw.predictions = []
  return raw
}

function savePredictionState(state) {
  writeDataFile(PREDICTIONS_FILE, state)
}

function getBestPrice(pair) {
  const source = PAIR_SOURCES[pair]
  if (!source) return null

  // Try DB first
  const dbPrice = getLatestPrice(pair)
  if (dbPrice) {
    return { price: dbPrice.price, tick: dbPrice.tick, source: 'db' }
  }

  // Fallback to JSON
  const live = readDataFile('oracle-live-queries.json')
  if (live?.queries) {
    const [c1, c2] = pair.split('/')
    const matching = live.queries
      .filter(q =>
        q.oracle === source.oracle &&
        q.currency1 === c1 && q.currency2 === c2 &&
        q.status === 'success' && (q.reply?.price || q.price)
      )
      .sort((a, b) => (b.tick || 0) - (a.tick || 0))

    if (matching.length > 0) {
      const m = matching[0]
      return { price: m.reply?.price ?? m.price, tick: m.tick, source: 'live-json' }
    }
  }

  return null
}

// =============================================================================
// MAIN
// =============================================================================

async function main() {
  loadEnv()

  const args = process.argv.slice(2)
  const dryRun = args.includes('--dry-run')
  const revealOnly = args.includes('--reveal-only')
  const budget = parseInt(getArg(args, '--budget') || '1000', 10)
  const loop = args.includes('--loop')
  const interval = parseInt(getArg(args, '--interval') || '60', 10)

  // Reveal-only mode: just reveal expired + export, no new commits
  if (revealOnly) {
    printHeader('ORACLE AUTOPILOT', 'REVEAL-ONLY MODE')
    getDb()
    await revealExpired(false)
    for (const [name] of strategies) {
      try { updateStrategyStats(name) } catch { /* skip */ }
    }
    exportDashboard()
    closeDb()
    return
  }

  if (loop) {
    console.log(`  AUTOPILOT LOOP MODE: every ${interval} minutes, budget ${budget} QU`)
    while (true) {
      try {
        await runPipeline({ budget, dryRun })
      } catch (err) {
        console.error(`  Pipeline error: ${err.message}`)
      }
      console.log(`  Next run in ${interval} minutes...`)
      await sleep(interval * 60 * 1000)
    }
  } else {
    await runPipeline({ budget, dryRun })
  }

  closeDb()
}

function getArg(args, flag) {
  const i = args.indexOf(flag)
  return i >= 0 ? args[i + 1] : null
}

main().catch(err => {
  console.error('FATAL:', err.message)
  process.exit(1)
})
