#!/usr/bin/env node
/**
 * ORACLE BACKTEST v2 — Strategy Backtesting Engine
 *
 * Walk-forward backtesting with time-based stepping.
 * At time T, run strategy with all data up to T,
 * then check outcome at T + horizonHours.
 *
 * v2 fixes:
 * - Time-based stepping (every 5-15 min, not every data point)
 * - Time-based lookback windows passed to strategies
 * - Proper timestamp validation
 * - Diagnostic counters for debugging
 * - Sharpe ratio, max drawdown, profit factor
 * - --verbose flag for detailed output
 * - Cross-asset context for multi-pair strategies
 *
 * Usage:
 *   node ORACLE_BACKTEST.mjs --strategy conservative --pair btc/usdt --horizon 2
 *   node ORACLE_BACKTEST.mjs --strategy all --pair all
 *   node ORACLE_BACKTEST.mjs --compare
 *   node ORACLE_BACKTEST.mjs --compare --verbose
 */

import { getDb, closeDb, getPriceHistory, insertBacktest } from './oracle-db.mjs'
import { strategies, runStrategy } from './strategies/index.mjs'
import { randomBytes } from 'crypto'

// =============================================================================
// HELPERS
// =============================================================================

function generateId() {
  return `bt_${Date.now().toString(36)}_${randomBytes(3).toString('hex')}`
}

function printHeader(title, sub) {
  console.log()
  console.log(`  ${'='.repeat(65)}`)
  console.log(`  ${title}`)
  if (sub) console.log(`  ${sub}`)
  console.log(`  ${'='.repeat(65)}`)
  console.log()
}

function getArg(args, flag) {
  const i = args.indexOf(flag)
  return i >= 0 ? args[i + 1] : null
}

// =============================================================================
// BACKTEST ENGINE v2
// =============================================================================

/**
 * Run a walk-forward backtest for a single strategy/pair/horizon combination.
 *
 * Key improvement: time-based stepping instead of evaluating every data point.
 * Step interval = max(5 min, horizon * 15 min) — avoids overlapping predictions.
 */
function backtestStrategy(strategyName, pair, horizonHours, priceData, options = {}) {
  const { verbose = false, allPriceData = {} } = options

  // priceData is sorted by timestamp DESC — reverse to chronological
  const prices = [...priceData].reverse()

  if (prices.length < 20) {
    return { totalTrades: 0, correctTrades: 0, accuracy: null, trades: [], diagnostics: { reason: 'insufficient data' } }
  }

  // Validate timestamps
  const validPrices = prices.filter(p => {
    const t = new Date(p.timestamp).getTime()
    return !isNaN(t) && t > 0
  })

  if (validPrices.length < 20) {
    return { totalTrades: 0, correctTrades: 0, accuracy: null, trades: [], diagnostics: { reason: 'invalid timestamps' } }
  }

  const trades = []
  const horizonMs = horizonHours * 3600000

  // Time-based stepping: evaluate every stepMs
  const stepMs = Math.max(5 * 60 * 1000, horizonHours * 15 * 60 * 1000)

  // Build time index for fast future price lookup
  const timeIndex = validPrices.map(p => ({
    time: new Date(p.timestamp).getTime(),
    price: p.price,
    timestamp: p.timestamp,
    oracle: p.oracle,
  }))

  const startTime = timeIndex[0].time
  const endTime = timeIndex[timeIndex.length - 1].time

  // Need at least one full horizon of data
  if (endTime - startTime < horizonMs * 2) {
    return { totalTrades: 0, correctTrades: 0, accuracy: null, trades: [], diagnostics: { reason: 'time span too short' } }
  }

  // Diagnostics
  let evaluated = 0
  let signaled = 0
  let noFuture = 0
  let nullStrategy = 0

  // Prepare cross-asset data (for cross_asset strategy)
  const allPriceTimeSeries = {}
  for (const [p, data] of Object.entries(allPriceData)) {
    allPriceTimeSeries[p] = [...data].reverse().map(r => ({
      price: r.price,
      timestamp: r.timestamp,
      oracle: r.oracle,
    }))
  }

  // Walk forward with time-based steps
  // Start from at least 30 minutes into the data (let strategies decide their own lookback needs)
  const minLookbackMs = 30 * 60 * 1000
  let evalTime = startTime + minLookbackMs

  while (evalTime < endTime - horizonMs) {
    evaluated++

    // Find the closest price point to evalTime
    let currentIdx = -1
    let closestDelta = Infinity
    for (let i = 0; i < timeIndex.length; i++) {
      const delta = Math.abs(timeIndex[i].time - evalTime)
      if (delta < closestDelta) {
        closestDelta = delta
        currentIdx = i
      }
      if (timeIndex[i].time > evalTime + stepMs) break
    }

    // Allow up to 2x step tolerance for sparse data regions
    if (currentIdx < 0 || closestDelta > stepMs * 2) {
      evalTime += stepMs
      continue
    }

    const currentPrice = timeIndex[currentIdx].price

    // Build lookback history (as strategy would see it — newest first, up to eval point)
    const lookback = timeIndex.slice(0, currentIdx + 1).reverse().map(p => ({
      price: p.price,
      timestamp: p.timestamp,
      oracle: p.oracle,
    }))

    if (lookback.length < 5) {
      evalTime += stepMs
      continue
    }

    // Build allPrices context for cross-asset strategy
    const allPricesCtx = {}
    for (const [p, series] of Object.entries(allPriceTimeSeries)) {
      const cutoffTime = timeIndex[currentIdx].time
      const filtered = series
        .filter(r => new Date(r.timestamp).getTime() <= cutoffTime)
        .reverse() // newest first
      if (filtered.length >= 5) {
        allPricesCtx[p] = filtered
      }
    }

    // Run strategy
    const ctx = {
      pair,
      currentPrice,
      priceHistory: lookback,
      horizonHours,
      allPrices: allPricesCtx,
    }

    const signal = runStrategy(strategyName, ctx)

    if (!signal) {
      nullStrategy++
      evalTime += stepMs
      continue
    }

    signaled++

    // Find the closest price at T + horizon
    const targetTime = timeIndex[currentIdx].time + horizonMs
    let futurePrice = null
    let futureDelta = Infinity

    for (let j = currentIdx + 1; j < timeIndex.length; j++) {
      const delta = Math.abs(timeIndex[j].time - targetTime)
      if (delta < futureDelta) {
        futureDelta = delta
        futurePrice = timeIndex[j].price
      }
      if (timeIndex[j].time > targetTime + horizonMs * 0.3) break
    }

    // Need future price within 30% of horizon window
    if (!futurePrice || futureDelta > horizonMs * 0.3) {
      noFuture++
      evalTime += stepMs
      continue
    }

    // Evaluate outcome
    const isCorrect = signal.direction === 'up'
      ? futurePrice >= signal.threshold
      : futurePrice <= signal.threshold

    const pctChange = (futurePrice - currentPrice) / currentPrice * 100

    trades.push({
      timestamp: timeIndex[currentIdx].timestamp,
      entryPrice: currentPrice,
      futurePrice,
      direction: signal.direction,
      threshold: signal.threshold,
      confidence: signal.confidence,
      correct: isCorrect,
      pctChange,
      strategy: signal.strategy,
    })

    evalTime += stepMs
  }

  // Calculate metrics
  const correctTrades = trades.filter(t => t.correct).length
  const accuracy = trades.length > 0 ? Number((correctTrades / trades.length * 100).toFixed(1)) : null

  // Sharpe ratio (using directional returns)
  let sharpe = null
  if (trades.length >= 5) {
    const returns = trades.map(t => {
      const r = t.pctChange / 100
      return t.direction === 'down' ? -r : r // flip sign for short predictions
    })
    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length
    const retVariance = returns.reduce((a, r) => a + (r - avgReturn) ** 2, 0) / returns.length
    const retStd = Math.sqrt(retVariance)
    sharpe = retStd > 0 ? Number((avgReturn / retStd * Math.sqrt(252)).toFixed(2)) : null
  }

  // Max drawdown
  let maxDrawdown = null
  if (trades.length >= 2) {
    let cumReturn = 0
    let peak = 0
    let maxDd = 0
    for (const t of trades) {
      const r = t.correct ? Math.abs(t.pctChange) / 100 : -Math.abs(t.pctChange) / 100
      cumReturn += r
      if (cumReturn > peak) peak = cumReturn
      const dd = peak - cumReturn
      if (dd > maxDd) maxDd = dd
      maxDrawdown = Number((maxDd * 100).toFixed(2))
    }
  }

  // Profit factor
  let profitFactor = null
  if (trades.length > 0) {
    const grossProfit = trades.filter(t => t.correct).reduce((s, t) => s + Math.abs(t.pctChange), 0)
    const grossLoss = trades.filter(t => !t.correct).reduce((s, t) => s + Math.abs(t.pctChange), 0)
    profitFactor = grossLoss > 0 ? Number((grossProfit / grossLoss).toFixed(2)) : grossProfit > 0 ? 99.9 : 0
  }

  // Win/loss streaks
  let maxWinStreak = 0, maxLossStreak = 0, currentStreak = 0, currentStreakType = null
  for (const t of trades) {
    if (t.correct) {
      if (currentStreakType === 'win') currentStreak++
      else { currentStreak = 1; currentStreakType = 'win' }
      if (currentStreak > maxWinStreak) maxWinStreak = currentStreak
    } else {
      if (currentStreakType === 'loss') currentStreak++
      else { currentStreak = 1; currentStreakType = 'loss' }
      if (currentStreak > maxLossStreak) maxLossStreak = currentStreak
    }
  }

  // Confidence calibration
  const confBins = [
    { min: 0, max: 0.4, correct: 0, total: 0 },
    { min: 0.4, max: 0.6, correct: 0, total: 0 },
    { min: 0.6, max: 0.8, correct: 0, total: 0 },
    { min: 0.8, max: 1.0, correct: 0, total: 0 },
  ]
  for (const t of trades) {
    const bin = confBins.find(b => t.confidence >= b.min && t.confidence < b.max) || confBins[confBins.length - 1]
    bin.total++
    if (t.correct) bin.correct++
  }

  return {
    totalTrades: trades.length,
    correctTrades,
    accuracy,
    sharpe,
    maxDrawdown,
    profitFactor,
    maxWinStreak,
    maxLossStreak,
    confidenceCalibration: confBins.map(b => ({
      range: `${(b.min * 100).toFixed(0)}-${(b.max * 100).toFixed(0)}%`,
      total: b.total,
      correct: b.correct,
      accuracy: b.total > 0 ? Number((b.correct / b.total * 100).toFixed(1)) : null,
    })),
    trades,
    diagnostics: { evaluated, signaled, noFuture, nullStrategy },
  }
}

// =============================================================================
// MAIN
// =============================================================================

function main() {
  const args = process.argv.slice(2)
  const verbose = args.includes('--verbose')

  if (args.includes('--compare') || (args.includes('--strategy') && getArg(args, '--strategy') === 'all')) {
    return runComparison(args, verbose)
  }

  const strategyName = getArg(args, '--strategy')
  const pair = getArg(args, '--pair')
  const horizon = parseInt(getArg(args, '--horizon') || '2', 10)

  if (!strategyName || !pair) {
    console.log(`
  ORACLE BACKTEST v2 — Strategy Backtesting Engine

  Usage:
    node ORACLE_BACKTEST.mjs --strategy conservative --pair btc/usdt --horizon 2
    node ORACLE_BACKTEST.mjs --strategy momentum --pair all --horizon 4
    node ORACLE_BACKTEST.mjs --strategy all --pair all
    node ORACLE_BACKTEST.mjs --compare
    node ORACLE_BACKTEST.mjs --compare --verbose

  Strategies: ${[...strategies.keys()].join(', ')}
  Horizons:   1, 2, 4 (hours)
  Flags:      --verbose (detailed diagnostics)
`)
    return
  }

  const db = getDb()

  // Preload all price data for cross-asset strategy
  const allPairs = db.prepare('SELECT DISTINCT pair FROM prices ORDER BY pair').all().map(r => r.pair)
  const allPriceData = {}
  for (const p of allPairs) {
    allPriceData[p] = getPriceHistory(p, 10000)
  }

  if (pair === 'all') {
    printHeader('ORACLE BACKTEST v2', `${strategyName} | ${allPairs.length} pairs | ${horizon}h horizon`)

    let totalTrades = 0
    let totalCorrect = 0

    for (const p of allPairs) {
      const priceData = allPriceData[p]
      const result = backtestStrategy(strategyName, p, horizon, priceData, { verbose, allPriceData })

      if (result.totalTrades > 0) {
        const icon = result.accuracy >= 60 ? '+' : result.accuracy >= 50 ? '~' : 'X'
        console.log(`  [${icon}] ${p.padEnd(14)} ${result.correctTrades}/${result.totalTrades} = ${result.accuracy}% | Sharpe: ${result.sharpe ?? '--'} | PF: ${result.profitFactor ?? '--'}`)
        totalTrades += result.totalTrades
        totalCorrect += result.correctTrades
      } else if (verbose) {
        console.log(`  [ ] ${p.padEnd(14)} 0 trades (${result.diagnostics.reason || `eval=${result.diagnostics.evaluated}, null=${result.diagnostics.nullStrategy}, noFuture=${result.diagnostics.noFuture}`})`)
      }
    }

    const overallAccuracy = totalTrades > 0 ? (totalCorrect / totalTrades * 100).toFixed(1) : '--'
    console.log()
    console.log(`  TOTAL: ${totalCorrect}/${totalTrades} = ${overallAccuracy}%`)

    insertBacktest({
      id: generateId(),
      strategy: strategyName,
      params: { horizon },
      pairFilter: 'all',
      horizonFilter: horizon,
      totalTrades,
      correctTrades: totalCorrect,
      accuracy: totalTrades > 0 ? Number(overallAccuracy) : null,
    })
  } else {
    printHeader('ORACLE BACKTEST v2', `${strategyName} | ${pair} | ${horizon}h horizon`)

    const priceData = allPriceData[pair] || getPriceHistory(pair, 10000)
    console.log(`  Price data points: ${priceData.length}`)

    const result = backtestStrategy(strategyName, pair, horizon, priceData, { verbose, allPriceData })

    console.log(`  Trades generated:  ${result.totalTrades}`)
    console.log(`  Correct:           ${result.correctTrades}`)
    console.log(`  Accuracy:          ${result.accuracy ?? '--'}%`)
    console.log(`  Sharpe Ratio:      ${result.sharpe ?? '--'}`)
    console.log(`  Max Drawdown:      ${result.maxDrawdown ?? '--'}%`)
    console.log(`  Profit Factor:     ${result.profitFactor ?? '--'}`)
    console.log(`  Win Streak:        ${result.maxWinStreak}`)
    console.log(`  Loss Streak:       ${result.maxLossStreak}`)
    console.log()

    if (verbose) {
      console.log(`  Diagnostics:`)
      console.log(`    Evaluated:    ${result.diagnostics.evaluated}`)
      console.log(`    Signaled:     ${result.diagnostics.signaled}`)
      console.log(`    No future:    ${result.diagnostics.noFuture}`)
      console.log(`    Null strategy:${result.diagnostics.nullStrategy}`)
      console.log()

      console.log(`  Confidence Calibration:`)
      for (const bin of result.confidenceCalibration) {
        const bar = bin.total > 0 ? '#'.repeat(Math.min(bin.total, 30)) : ''
        console.log(`    ${bin.range.padEnd(10)} ${String(bin.correct).padEnd(4)}/${String(bin.total).padEnd(4)} = ${String(bin.accuracy ?? '--').padEnd(5)}% ${bar}`)
      }
      console.log()
    }

    if (result.trades.length > 0) {
      console.log(`  Last 15 trades:`)
      for (const t of result.trades.slice(-15)) {
        const icon = t.correct ? '+' : 'X'
        console.log(`    [${icon}] ${t.timestamp.slice(0, 19)} ${t.direction.padEnd(5)} ${String(t.threshold.toPrecision(6)).padEnd(12)} → ${t.futurePrice.toPrecision(6)} (${t.pctChange > 0 ? '+' : ''}${t.pctChange.toFixed(2)}%) conf=${t.confidence}`)
      }
    }

    insertBacktest({
      id: generateId(),
      strategy: strategyName,
      params: { horizon },
      pairFilter: pair,
      horizonFilter: horizon,
      totalTrades: result.totalTrades,
      correctTrades: result.correctTrades,
      accuracy: result.accuracy,
      sharpe: result.sharpe,
      maxDrawdown: result.maxDrawdown,
      profitFactor: result.profitFactor,
    })
  }

  closeDb()
}

/**
 * Compare all strategies across all pairs and horizons.
 */
function runComparison(args, verbose) {
  const db = getDb()
  const pairs = db.prepare('SELECT DISTINCT pair FROM prices ORDER BY pair').all().map(r => r.pair)
  const horizons = [1, 2, 4]
  const stratNames = [...strategies.keys()]

  // Preload all price data
  const allPriceData = {}
  for (const p of pairs) {
    allPriceData[p] = getPriceHistory(p, 10000)
  }

  printHeader('ORACLE BACKTEST v2 — Strategy Comparison',
    `${stratNames.length} strategies | ${pairs.length} pairs | ${horizons.length} horizons`)

  // Count total prices
  const totalPrices = Object.values(allPriceData).reduce((s, d) => s + d.length, 0)
  console.log(`  Total price points: ${totalPrices.toLocaleString()}`)
  console.log()

  const results = []

  for (const stratName of stratNames) {
    for (const horizon of horizons) {
      let totalTrades = 0
      let totalCorrect = 0
      let allTrades = []

      for (const pair of pairs) {
        const priceData = allPriceData[pair]
        const result = backtestStrategy(stratName, pair, horizon, priceData, { verbose: false, allPriceData })
        totalTrades += result.totalTrades
        totalCorrect += result.correctTrades
        allTrades.push(...result.trades)
      }

      const accuracy = totalTrades > 0 ? Number((totalCorrect / totalTrades * 100).toFixed(1)) : null

      // Compute aggregate metrics
      let sharpe = null, profitFactor = null
      if (allTrades.length >= 5) {
        const returns = allTrades.map(t => {
          const r = t.pctChange / 100
          return t.direction === 'down' ? -r : r
        })
        const avgRet = returns.reduce((a, b) => a + b, 0) / returns.length
        const retVar = returns.reduce((a, r) => a + (r - avgRet) ** 2, 0) / returns.length
        const retStd = Math.sqrt(retVar)
        sharpe = retStd > 0 ? Number((avgRet / retStd * Math.sqrt(252)).toFixed(2)) : null

        const grossProfit = allTrades.filter(t => t.correct).reduce((s, t) => s + Math.abs(t.pctChange), 0)
        const grossLoss = allTrades.filter(t => !t.correct).reduce((s, t) => s + Math.abs(t.pctChange), 0)
        profitFactor = grossLoss > 0 ? Number((grossProfit / grossLoss).toFixed(2)) : grossProfit > 0 ? 99.9 : 0
      }

      results.push({ strategy: stratName, horizon, totalTrades, totalCorrect, accuracy, sharpe, profitFactor })

      insertBacktest({
        id: generateId(),
        strategy: stratName,
        params: { horizon },
        pairFilter: 'all',
        horizonFilter: horizon,
        totalTrades,
        correctTrades: totalCorrect,
        accuracy,
        sharpe,
        profitFactor,
      })
    }
  }

  // Print comparison table
  console.log(`  ${'Strategy'.padEnd(20)} ${'H'.padEnd(4)} ${'Trades'.padEnd(8)} ${'Win'.padEnd(8)} ${'Acc%'.padEnd(8)} ${'Sharpe'.padEnd(8)} ${'PF'.padEnd(8)}`)
  console.log(`  ${'-'.repeat(64)}`)

  for (const r of results) {
    if (r.totalTrades === 0) {
      if (verbose) console.log(`  [ ] ${r.strategy.padEnd(18)} ${(r.horizon + 'h').padEnd(4)} 0`)
      continue
    }
    const icon = r.accuracy >= 60 ? '+' : r.accuracy >= 50 ? '~' : 'X'
    console.log(`  [${icon}] ${r.strategy.padEnd(18)} ${(r.horizon + 'h').padEnd(4)} ${String(r.totalTrades).padEnd(8)} ${String(r.totalCorrect).padEnd(8)} ${String(r.accuracy + '%').padEnd(8)} ${String(r.sharpe ?? '--').padEnd(8)} ${String(r.profitFactor ?? '--').padEnd(8)}`)
  }

  // Overall per strategy rankings
  console.log()
  console.log(`  ${'='.repeat(64)}`)
  console.log(`  STRATEGY RANKINGS (by Accuracy):`)
  console.log(`  ${'-'.repeat(64)}`)

  const byStrategy = {}
  for (const r of results) {
    if (!byStrategy[r.strategy]) byStrategy[r.strategy] = { trades: 0, correct: 0, sharpes: [], pfs: [] }
    byStrategy[r.strategy].trades += r.totalTrades
    byStrategy[r.strategy].correct += r.totalCorrect
    if (r.sharpe != null) byStrategy[r.strategy].sharpes.push(r.sharpe)
    if (r.profitFactor != null) byStrategy[r.strategy].pfs.push(r.profitFactor)
  }

  const ranked = Object.entries(byStrategy)
    .map(([name, s]) => {
      const accuracy = s.trades > 0 ? (s.correct / s.trades * 100).toFixed(1) : '--'
      const avgSharpe = s.sharpes.length > 0 ? (s.sharpes.reduce((a, b) => a + b, 0) / s.sharpes.length).toFixed(2) : '--'
      const avgPF = s.pfs.length > 0 ? (s.pfs.reduce((a, b) => a + b, 0) / s.pfs.length).toFixed(2) : '--'
      return { name, ...s, accuracy, avgSharpe, avgPF }
    })
    .sort((a, b) => (Number(b.accuracy) || 0) - (Number(a.accuracy) || 0))

  for (let i = 0; i < ranked.length; i++) {
    const r = ranked[i]
    const medal = i === 0 ? '1st' : i === 1 ? '2nd' : i === 2 ? '3rd' : `${i + 1}th`
    console.log(`  ${medal.padEnd(5)} ${r.name.padEnd(20)} ${r.correct}/${r.trades} = ${r.accuracy}% | Sharpe: ${r.avgSharpe} | PF: ${r.avgPF}`)
  }

  console.log()
  closeDb()
}

main()
