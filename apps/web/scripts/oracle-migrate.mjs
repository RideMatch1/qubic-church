#!/usr/bin/env node
/**
 * ORACLE MIGRATE — One-time JSON → SQLite migration
 *
 * Reads all existing Oracle JSON data files and populates the SQLite database.
 * Safe to run multiple times (uses INSERT OR REPLACE for predictions).
 *
 * Usage: node scripts/oracle-migrate.mjs
 */

import { readFileSync, existsSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'
import {
  getDb, closeDb, insertPrediction, insertPricesBatch,
  insertStrategy, getPriceStats, getPredictionStats
} from './oracle-db.mjs'

const __dirname = dirname(fileURLToPath(import.meta.url))
const DATA_DIR = join(__dirname, '..', 'public', 'data')

function readJson(filename) {
  const path = join(DATA_DIR, filename)
  if (!existsSync(path)) {
    console.log(`  [skip] ${filename} not found`)
    return null
  }
  const raw = readFileSync(path, 'utf-8')
  const data = JSON.parse(raw)
  console.log(`  [read] ${filename} (${(raw.length / 1024).toFixed(1)} KB)`)
  return data
}

// =============================================================================
// MAIN
// =============================================================================

console.log('=================================================================')
console.log('  ORACLE MIGRATE — JSON → SQLite')
console.log('=================================================================')
console.log()

const db = getDb()
let totalPrices = 0
let totalPredictions = 0

// ─── 1. Migrate predictions ─────────────────────────────────────────────────

console.log('1. Migrating predictions...')
const predData = readJson('oracle-predictions.json')
if (predData) {
  const predictions = Array.isArray(predData) ? predData : (predData.predictions ?? [])
  for (const p of predictions) {
    insertPrediction(p)
    totalPredictions++
  }
  console.log(`   → ${totalPredictions} predictions inserted`)
}
console.log()

// ─── 2. Migrate live queries (prices from monitor) ──────────────────────────

console.log('2. Migrating live query prices...')
const liveData = readJson('oracle-live-queries.json')
if (liveData?.queries) {
  const priceBatch = []
  for (const q of liveData.queries) {
    const price = q.reply?.price ?? q.price
    if (q.status === 'success' && price && price > 0 && q.oracle && q.currency1 && q.currency2) {
      priceBatch.push({
        pair: `${q.currency1}/${q.currency2}`,
        oracle: q.oracle,
        price,
        tick: q.tick ?? null,
        epoch: liveData.epoch ?? null,
        source: 'live-monitor',
        timestamp: q.lastUpdated ?? q.firstSeen ?? liveData.scanTimestamp ?? new Date().toISOString(),
      })
    }
  }
  if (priceBatch.length > 0) {
    insertPricesBatch(priceBatch)
    totalPrices += priceBatch.length
  }
  console.log(`   → ${priceBatch.length} price snapshots from live queries`)
}
console.log()

// ─── 3. Migrate price history (from DOMINATOR sweeps) ───────────────────────

console.log('3. Migrating price history...')
const historyData = readJson('oracle-price-history.json')
if (historyData && Array.isArray(historyData)) {
  const priceBatch = []
  for (const sweep of historyData) {
    if (!sweep.results) continue
    for (const r of sweep.results) {
      const price = r.verifiedPrice ?? r.price
      if (price && price > 0 && r.status !== 'error') {
        priceBatch.push({
          pair: `${r.currency1}/${r.currency2}`,
          oracle: r.oracle,
          price,
          tick: r.targetTick ?? sweep.startTick ?? null,
          epoch: sweep.epoch ?? null,
          source: 'sweep',
          timestamp: r.timestamp ?? sweep.timestamp ?? new Date().toISOString(),
        })
      }
    }
  }
  if (priceBatch.length > 0) {
    insertPricesBatch(priceBatch)
    totalPrices += priceBatch.length
  }
  console.log(`   → ${priceBatch.length} price snapshots from sweep history`)
}
console.log()

// ─── 4. Create default strategies ───────────────────────────────────────────

console.log('4. Creating default strategies...')

insertStrategy('manual', 'manual',
  'Manual predictions with explicit direction/threshold',
  { note: 'User specifies all parameters' })

insertStrategy('conservative', 'conservative',
  'Set threshold below current price for up (margin 0.5%). High accuracy, low return.',
  { marginPct: 0.5, horizons: [1, 2] })

insertStrategy('momentum', 'momentum',
  'Trend continuation based on recent price movement direction.',
  { lookbackCandles: 3, thresholdPct: 1.5, horizons: [2, 4] })

insertStrategy('mean_reversion', 'mean_reversion',
  'Reversion bet when price deviates >2 sigma from recent mean.',
  { lookbackHours: 24, sigmaThreshold: 2.0, revertPct: 50, horizons: [12, 24] })

insertStrategy('consensus', 'consensus',
  'Multi-source oracle divergence as directional signal.',
  { divergenceThresholdPct: 1.0, horizons: [2, 4] })

console.log('   → 5 strategies created (manual + 4 automated)')
console.log()

// ─── 5. Summary ─────────────────────────────────────────────────────────────

const priceStats = getPriceStats()
const predStats = getPredictionStats()

console.log('=================================================================')
console.log('  MIGRATION COMPLETE')
console.log('=================================================================')
console.log()
console.log(`  Predictions:  ${predStats.overall.total}`)
console.log(`    Committed:  ${predStats.overall.committed ?? 0}`)
console.log(`    Correct:    ${predStats.overall.correct ?? 0}`)
console.log(`    Incorrect:  ${predStats.overall.incorrect ?? 0}`)
console.log(`    Accuracy:   ${predStats.overall.accuracy ?? '--'}%`)
console.log()
console.log(`  Prices:       ${priceStats.total}`)
console.log(`    Pairs:      ${priceStats.pairs}`)
console.log(`    Oracles:    ${priceStats.oracles}`)
console.log(`    Range:      ${priceStats.earliest ?? '--'} → ${priceStats.latest ?? '--'}`)
console.log()
console.log(`  Strategies:   5`)
console.log()

closeDb()
