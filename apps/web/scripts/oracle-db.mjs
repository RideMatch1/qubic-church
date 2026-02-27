#!/usr/bin/env node
/**
 * ORACLE DB — SQLite Database Module
 *
 * Central data layer for the Prediction Engine.
 * Uses better-sqlite3 for synchronous, fast, embedded SQL.
 *
 * DB file: apps/web/data/oracle-engine.db (gitignored)
 *
 * Exports:
 *   getDb, initSchema, insertPrice, insertPrediction, updatePredictionReveal,
 *   getPriceHistory, getStrategyStats, getAllPredictions, getExpiredPredictions,
 *   insertBacktest, insertStrategy, updateStrategyStats, insertPipelineRun
 */

import { createRequire } from 'module'
import { dirname, join } from 'path'
import { fileURLToPath } from 'url'
import { mkdirSync, existsSync } from 'fs'

const require = createRequire(import.meta.url)
const __dirname = dirname(fileURLToPath(import.meta.url))
const DB_DIR = join(__dirname, '..', 'data')
const DB_PATH = join(DB_DIR, 'oracle-engine.db')

let _db = null

// =============================================================================
// DATABASE CONNECTION
// =============================================================================

/**
 * Get or create the SQLite database connection.
 * Uses WAL mode for concurrent read performance.
 */
export function getDb() {
  if (_db) return _db

  // Ensure data directory exists
  if (!existsSync(DB_DIR)) {
    mkdirSync(DB_DIR, { recursive: true })
  }

  const Database = require('better-sqlite3')
  _db = new Database(DB_PATH)

  // Performance settings
  _db.pragma('journal_mode = WAL')
  _db.pragma('synchronous = NORMAL')
  _db.pragma('foreign_keys = ON')

  // Auto-init schema
  initSchema(_db)

  return _db
}

/**
 * Close the database connection.
 */
export function closeDb() {
  if (_db) {
    _db.close()
    _db = null
  }
}

// =============================================================================
// SCHEMA
// =============================================================================

/**
 * Create all tables and indices (idempotent).
 */
export function initSchema(db) {
  db = db || getDb()

  db.exec(`
    -- Price snapshots from DOMINATOR sweeps and live monitor
    CREATE TABLE IF NOT EXISTS prices (
      id        INTEGER PRIMARY KEY AUTOINCREMENT,
      pair      TEXT NOT NULL,
      oracle    TEXT NOT NULL,
      price     REAL NOT NULL,
      tick      INTEGER,
      epoch     INTEGER,
      source    TEXT NOT NULL,
      timestamp TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_prices_pair_ts ON prices(pair, timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_prices_oracle_pair ON prices(oracle, pair, timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_prices_tick ON prices(tick);

    -- Predictions (replaces oracle-predictions.json)
    CREATE TABLE IF NOT EXISTS predictions (
      id                TEXT PRIMARY KEY,
      pair              TEXT NOT NULL,
      direction         TEXT NOT NULL,
      threshold         REAL NOT NULL,
      horizon_hours     INTEGER NOT NULL,
      price_at_commit   REAL,
      commit_timestamp  TEXT NOT NULL,
      expires_at        TEXT NOT NULL,
      commit_hash       TEXT NOT NULL,
      commit_tick       INTEGER,
      commit_tx_id      TEXT,
      epoch             INTEGER,
      status            TEXT NOT NULL DEFAULT 'committed',
      reveal_tx_id      TEXT,
      reveal_tick       INTEGER,
      reveal_timestamp  TEXT,
      price_at_expiry   REAL,
      outcome           TEXT,
      verification_json TEXT NOT NULL,
      strategy          TEXT DEFAULT 'manual',
      confidence        REAL,
      strategy_params   TEXT,
      created_at        TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_pred_status ON predictions(status);
    CREATE INDEX IF NOT EXISTS idx_pred_pair ON predictions(pair, status);
    CREATE INDEX IF NOT EXISTS idx_pred_strategy ON predictions(strategy, status);
    CREATE INDEX IF NOT EXISTS idx_pred_epoch ON predictions(epoch);
    CREATE INDEX IF NOT EXISTS idx_pred_expires ON predictions(expires_at);

    -- Backtest results
    CREATE TABLE IF NOT EXISTS backtests (
      id              TEXT PRIMARY KEY,
      strategy        TEXT NOT NULL,
      params          TEXT NOT NULL,
      pair_filter     TEXT,
      horizon_filter  TEXT,
      total_trades    INTEGER,
      correct_trades  INTEGER,
      accuracy        REAL,
      avg_return_pct  REAL,
      sharpe_ratio    REAL,
      max_drawdown    REAL,
      profit_factor   REAL,
      results_json    TEXT,
      created_at      TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_bt_strategy ON backtests(strategy);
  `)

  // Safe migration: add sharpe_ratio column if missing (existing DBs)
  try {
    db.exec(`ALTER TABLE backtests ADD COLUMN sharpe_ratio REAL`)
  } catch { /* column already exists */ }

  db.exec(`
    -- Strategy definitions and running performance
    CREATE TABLE IF NOT EXISTS strategies (
      name                TEXT PRIMARY KEY,
      type                TEXT NOT NULL,
      description         TEXT,
      params              TEXT NOT NULL,
      is_active           INTEGER DEFAULT 1,
      total_predictions   INTEGER DEFAULT 0,
      correct_predictions INTEGER DEFAULT 0,
      accuracy            REAL,
      last_used           TEXT,
      created_at          TEXT DEFAULT (datetime('now'))
    );

    -- Automation pipeline runs
    CREATE TABLE IF NOT EXISTS pipeline_runs (
      id                      TEXT PRIMARY KEY,
      epoch                   INTEGER NOT NULL,
      timestamp               TEXT NOT NULL,
      budget_qu               INTEGER NOT NULL DEFAULT 1000,
      predictions_generated   INTEGER,
      predictions_committed   INTEGER,
      cost_qu                 INTEGER,
      correct                 INTEGER,
      incorrect               INTEGER,
      accuracy                REAL,
      strategies_used         TEXT,
      created_at              TEXT DEFAULT (datetime('now'))
    );
  `)
}

// =============================================================================
// PRICES
// =============================================================================

const _stmtCache = new Map()

function stmt(db, sql) {
  if (!_stmtCache.has(sql)) {
    _stmtCache.set(sql, db.prepare(sql))
  }
  return _stmtCache.get(sql)
}

/**
 * Insert a price snapshot.
 */
export function insertPrice(oracle, pair, price, tick, epoch, source, timestamp) {
  const db = getDb()
  stmt(db, `
    INSERT INTO prices (pair, oracle, price, tick, epoch, source, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).run(pair, oracle, price, tick, epoch, source, timestamp)
}

/**
 * Bulk insert prices (faster for sweeps).
 */
export function insertPricesBatch(prices) {
  const db = getDb()
  const insert = stmt(db, `
    INSERT INTO prices (pair, oracle, price, tick, epoch, source, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `)
  const tx = db.transaction((rows) => {
    for (const r of rows) {
      insert.run(r.pair, r.oracle, r.price, r.tick, r.epoch, r.source, r.timestamp)
    }
  })
  tx(prices)
}

/**
 * Get price history for a pair, sorted by timestamp DESC.
 */
export function getPriceHistory(pair, limit = 500) {
  const db = getDb()
  return stmt(db, `
    SELECT * FROM prices
    WHERE pair = ?
    ORDER BY timestamp DESC
    LIMIT ?
  `).all(pair, limit)
}

/**
 * Get price history for a pair within a time window.
 * More efficient than count-based limit when data is very dense.
 * @param {string} pair
 * @param {number} windowMinutes - How many minutes of history to fetch
 * @returns {Array} rows sorted by timestamp DESC
 */
export function getPriceHistoryByTime(pair, windowMinutes = 120) {
  const db = getDb()
  const cutoff = new Date(Date.now() - windowMinutes * 60 * 1000).toISOString()
  return stmt(db, `
    SELECT * FROM prices
    WHERE pair = ? AND timestamp >= ?
    ORDER BY timestamp DESC
  `).all(pair, cutoff)
}

/**
 * Get the latest price for a pair (across all oracles).
 */
export function getLatestPrice(pair) {
  const db = getDb()
  return stmt(db, `
    SELECT * FROM prices
    WHERE pair = ?
    ORDER BY timestamp DESC
    LIMIT 1
  `).get(pair)
}

/**
 * Get latest prices for all pairs (one per pair, most recent).
 */
export function getLatestPrices() {
  const db = getDb()
  return db.prepare(`
    SELECT p.* FROM prices p
    INNER JOIN (
      SELECT pair, MAX(timestamp) as max_ts
      FROM prices
      GROUP BY pair
    ) latest ON p.pair = latest.pair AND p.timestamp = latest.max_ts
    ORDER BY p.pair
  `).all()
}

/**
 * Get price count and date range.
 */
export function getPriceStats() {
  const db = getDb()
  return db.prepare(`
    SELECT
      COUNT(*) as total,
      COUNT(DISTINCT pair) as pairs,
      COUNT(DISTINCT oracle) as oracles,
      MIN(timestamp) as earliest,
      MAX(timestamp) as latest
    FROM prices
  `).get()
}

// =============================================================================
// CROSS-ORACLE QUERIES (for Arbitrage + Explorer)
// =============================================================================

/**
 * Get latest prices per oracle for a given asset pair.
 * Returns one row per oracle (most recent price within window).
 * @param {string} pair — e.g. 'btc/usdt'
 * @param {number} windowMinutes — lookback window (default 10)
 * @returns {Array<{oracle, price, timestamp}>}
 */
export function getOraclePricesForPair(pair, windowMinutes = 10) {
  const db = getDb()
  const cutoff = new Date(Date.now() - windowMinutes * 60 * 1000).toISOString()
  return db.prepare(`
    SELECT p.oracle, p.price, p.timestamp
    FROM prices p
    INNER JOIN (
      SELECT oracle, MAX(timestamp) as max_ts
      FROM prices
      WHERE pair = ? AND timestamp >= ?
      GROUP BY oracle
    ) latest ON p.oracle = latest.oracle AND p.timestamp = latest.max_ts AND p.pair = ?
    ORDER BY p.price DESC
  `).all(pair, cutoff, pair)
}

/**
 * Get top cross-oracle spreads across all pairs.
 * For each pair that has 2+ oracle sources, computes max-min spread.
 * @param {number} windowMinutes — lookback window (default 5)
 * @param {number} minSpreadPct — minimum spread to include (default 0.05 = 0.05%)
 * @returns {Array<{pair, oracleHigh, oracleLow, priceHigh, priceLow, spreadPct}>}
 */
export function getTopSpreads(windowMinutes = 5, minSpreadPct = 0.05) {
  const db = getDb()
  const cutoff = new Date(Date.now() - windowMinutes * 60 * 1000).toISOString()

  // Get latest price per oracle per pair
  const rows = db.prepare(`
    SELECT p.pair, p.oracle, p.price, p.timestamp
    FROM prices p
    INNER JOIN (
      SELECT pair, oracle, MAX(timestamp) as max_ts
      FROM prices
      WHERE timestamp >= ?
      GROUP BY pair, oracle
    ) latest ON p.pair = latest.pair AND p.oracle = latest.oracle AND p.timestamp = latest.max_ts
    ORDER BY p.pair, p.price DESC
  `).all(cutoff)

  // Group by pair, compute spread
  const byPair = new Map()
  for (const r of rows) {
    if (!byPair.has(r.pair)) byPair.set(r.pair, [])
    byPair.get(r.pair).push(r)
  }

  const spreads = []
  for (const [pair, oracles] of byPair) {
    if (oracles.length < 2) continue
    const high = oracles[0]
    const low = oracles[oracles.length - 1]
    if (low.price <= 0) continue
    const spreadPct = ((high.price - low.price) / low.price) * 100
    if (spreadPct >= minSpreadPct) {
      spreads.push({
        pair,
        oracleHigh: high.oracle,
        oracleLow: low.oracle,
        priceHigh: high.price,
        priceLow: low.price,
        spreadPct: Number(spreadPct.toFixed(4)),
        timestamp: high.timestamp,
        oracleCount: oracles.length,
      })
    }
  }

  return spreads.sort((a, b) => b.spreadPct - a.spreadPct)
}

/**
 * Get per-oracle statistics.
 * @returns {Array<{oracle, pairCount, totalSnapshots, lastSeen}>}
 */
export function getOracleStats() {
  const db = getDb()
  return db.prepare(`
    SELECT
      oracle,
      COUNT(DISTINCT pair) as pairCount,
      COUNT(*) as totalSnapshots,
      MIN(timestamp) as firstSeen,
      MAX(timestamp) as lastSeen
    FROM prices
    GROUP BY oracle
    ORDER BY totalSnapshots DESC
  `).all()
}

/**
 * Get pair coverage: which oracles track which pairs.
 * @returns {Array<{pair, oracles: string, oracleCount: number, snapshotCount: number}>}
 */
export function getPairCoverage() {
  const db = getDb()
  return db.prepare(`
    SELECT
      pair,
      GROUP_CONCAT(DISTINCT oracle) as oracles,
      COUNT(DISTINCT oracle) as oracleCount,
      COUNT(*) as snapshotCount
    FROM prices
    GROUP BY pair
    ORDER BY oracleCount DESC, snapshotCount DESC
  `).all()
}

/**
 * Aggregate raw price snapshots into OHLCV candles.
 * @param {string} pair — e.g. 'btc/usdt'
 * @param {number} intervalMinutes — candle width (1, 5, 15, 60)
 * @param {number} limit — max candles to return (default 500)
 * @returns {Array<{open, high, low, close, count, timestamp}>} — newest first
 */
export function getCandles(pair, intervalMinutes = 5, limit = 500) {
  const db = getDb()
  const intervalMs = intervalMinutes * 60 * 1000

  // Get all prices for the pair, oldest first
  const prices = db.prepare(`
    SELECT price, timestamp FROM prices
    WHERE pair = ?
    ORDER BY timestamp ASC
  `).all(pair)

  if (prices.length === 0) return []

  const candles = []
  let bucketStart = Math.floor(new Date(prices[0].timestamp).getTime() / intervalMs) * intervalMs
  let open = prices[0].price
  let high = prices[0].price
  let low = prices[0].price
  let close = prices[0].price
  let count = 0

  for (const p of prices) {
    const t = new Date(p.timestamp).getTime()
    const bucket = Math.floor(t / intervalMs) * intervalMs

    if (bucket !== bucketStart) {
      // Finalize current candle
      if (count > 0) {
        candles.push({
          open, high, low, close, count,
          timestamp: new Date(bucketStart).toISOString(),
        })
      }
      // Start new candle
      bucketStart = bucket
      open = p.price
      high = p.price
      low = p.price
      close = p.price
      count = 1
    } else {
      high = Math.max(high, p.price)
      low = Math.min(low, p.price)
      close = p.price
      count++
    }
  }

  // Finalize last candle
  if (count > 0) {
    candles.push({
      open, high, low, close, count,
      timestamp: new Date(bucketStart).toISOString(),
    })
  }

  // Return newest first, limited
  return candles.reverse().slice(0, limit)
}

/**
 * Get prices within a time window for a specific pair.
 * @param {string} pair
 * @param {number} windowMinutes — how far back
 * @returns {Array} — newest first
 */
export function getPricesInWindow(pair, windowMinutes) {
  const db = getDb()
  const since = new Date(Date.now() - windowMinutes * 60 * 1000).toISOString()
  return db.prepare(`
    SELECT * FROM prices
    WHERE pair = ? AND timestamp >= ?
    ORDER BY timestamp DESC
  `).all(pair, since)
}

/**
 * Get latest prices for multiple pairs at once (for cross-asset strategy).
 * Returns one latest price per pair, keyed by pair name.
 */
export function getLatestPriceMap() {
  const rows = getLatestPrices()
  const map = {}
  for (const r of rows) map[r.pair] = r
  return map
}

// =============================================================================
// PREDICTIONS
// =============================================================================

/**
 * Insert a prediction (from ORACLE_PROPHECY commit).
 * Accepts the camelCase object from PROPHECY and maps to snake_case.
 */
export function insertPrediction(p) {
  const db = getDb()
  stmt(db, `
    INSERT OR REPLACE INTO predictions (
      id, pair, direction, threshold, horizon_hours,
      price_at_commit, commit_timestamp, expires_at,
      commit_hash, commit_tick, commit_tx_id, epoch,
      status, verification_json, strategy, confidence, strategy_params
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    p.id, p.pair, p.direction, p.threshold, p.horizonHours ?? p.horizon_hours,
    p.priceAtCommit ?? p.price_at_commit,
    p.commitTimestamp ?? p.commit_timestamp,
    p.expiresAt ?? p.expires_at,
    p.commitHash ?? p.commit_hash,
    p.commitTick ?? p.commit_tick,
    p.commitTxId ?? p.commit_tx_id,
    p.epoch,
    p.status || 'committed',
    p.verificationJson ?? p.verification_json ?? '',
    p.strategy || 'manual',
    p.confidence ?? null,
    p.strategyParams ?? p.strategy_params ?? null
  )
}

/**
 * Update a prediction after reveal.
 */
export function updatePredictionReveal(id, outcome, priceAtExpiry, revealTxId, revealTick) {
  const db = getDb()
  stmt(db, `
    UPDATE predictions SET
      status = ?,
      outcome = ?,
      price_at_expiry = ?,
      reveal_tx_id = ?,
      reveal_tick = ?,
      reveal_timestamp = datetime('now')
    WHERE id = ?
  `).run(outcome, outcome, priceAtExpiry, revealTxId, revealTick, id)
}

/**
 * Get all predictions with optional filters.
 */
export function getAllPredictions({ status, pair, strategy, limit, offset } = {}) {
  const db = getDb()
  let sql = 'SELECT * FROM predictions WHERE 1=1'
  const params = []

  if (status) { sql += ' AND status = ?'; params.push(status) }
  if (pair) { sql += ' AND pair = ?'; params.push(pair) }
  if (strategy) { sql += ' AND strategy = ?'; params.push(strategy) }

  sql += ' ORDER BY commit_timestamp DESC'

  if (limit) { sql += ' LIMIT ?'; params.push(limit) }
  if (offset) { sql += ' OFFSET ?'; params.push(offset) }

  return db.prepare(sql).all(...params)
}

/**
 * Get expired predictions that haven't been revealed yet.
 */
export function getExpiredPredictions() {
  const db = getDb()
  return db.prepare(`
    SELECT * FROM predictions
    WHERE status = 'committed'
      AND expires_at < datetime('now')
    ORDER BY expires_at ASC
  `).all()
}

/**
 * Get prediction stats (overall and per-strategy).
 */
export function getPredictionStats() {
  const db = getDb()

  const overall = db.prepare(`
    SELECT
      COUNT(*) as total,
      SUM(CASE WHEN status = 'committed' THEN 1 ELSE 0 END) as committed,
      SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) as correct,
      SUM(CASE WHEN status = 'incorrect' THEN 1 ELSE 0 END) as incorrect,
      CASE
        WHEN SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END) > 0
        THEN ROUND(100.0 * SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) /
             SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END), 1)
        ELSE NULL
      END as accuracy
    FROM predictions
  `).get()

  const byStrategy = db.prepare(`
    SELECT
      strategy,
      COUNT(*) as total,
      SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) as correct,
      SUM(CASE WHEN status = 'incorrect' THEN 1 ELSE 0 END) as incorrect,
      CASE
        WHEN SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END) > 0
        THEN ROUND(100.0 * SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) /
             SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END), 1)
        ELSE NULL
      END as accuracy
    FROM predictions
    GROUP BY strategy
    ORDER BY total DESC
  `).all()

  const byPair = db.prepare(`
    SELECT
      pair,
      COUNT(*) as total,
      SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) as correct,
      SUM(CASE WHEN status = 'incorrect' THEN 1 ELSE 0 END) as incorrect,
      CASE
        WHEN SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END) > 0
        THEN ROUND(100.0 * SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) /
             SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END), 1)
        ELSE NULL
      END as accuracy
    FROM predictions
    GROUP BY pair
    ORDER BY total DESC
  `).all()

  const byHorizon = db.prepare(`
    SELECT
      horizon_hours,
      COUNT(*) as total,
      SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) as correct,
      SUM(CASE WHEN status = 'incorrect' THEN 1 ELSE 0 END) as incorrect,
      CASE
        WHEN SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END) > 0
        THEN ROUND(100.0 * SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) /
             SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END), 1)
        ELSE NULL
      END as accuracy
    FROM predictions
    GROUP BY horizon_hours
    ORDER BY horizon_hours
  `).all()

  return { overall, byStrategy, byPair, byHorizon }
}

// =============================================================================
// STRATEGIES
// =============================================================================

/**
 * Insert or update a strategy definition.
 */
export function insertStrategy(name, type, description, params) {
  const db = getDb()
  stmt(db, `
    INSERT OR REPLACE INTO strategies (name, type, description, params)
    VALUES (?, ?, ?, ?)
  `).run(name, type, description, JSON.stringify(params))
}

/**
 * Get a strategy by name.
 */
export function getStrategy(name) {
  const db = getDb()
  return stmt(db, 'SELECT * FROM strategies WHERE name = ?').get(name)
}

/**
 * Get all active strategies.
 */
export function getActiveStrategies() {
  const db = getDb()
  return db.prepare('SELECT * FROM strategies WHERE is_active = 1').all()
}

/**
 * Update strategy performance stats (called after reveals).
 */
export function updateStrategyStats(name) {
  const db = getDb()
  db.prepare(`
    UPDATE strategies SET
      total_predictions = (SELECT COUNT(*) FROM predictions WHERE strategy = ?),
      correct_predictions = (SELECT COUNT(*) FROM predictions WHERE strategy = ? AND status = 'correct'),
      accuracy = (
        SELECT CASE
          WHEN SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END) > 0
          THEN ROUND(100.0 * SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) /
               SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END), 1)
          ELSE NULL
        END
        FROM predictions WHERE strategy = ?
      ),
      last_used = (SELECT MAX(commit_timestamp) FROM predictions WHERE strategy = ?)
    WHERE name = ?
  `).run(name, name, name, name, name)
}

// =============================================================================
// BACKTESTS
// =============================================================================

/**
 * Insert a backtest result.
 */
export function insertBacktest(bt) {
  const db = getDb()
  stmt(db, `
    INSERT INTO backtests (
      id, strategy, params, pair_filter, horizon_filter,
      total_trades, correct_trades, accuracy,
      avg_return_pct, sharpe_ratio, max_drawdown, profit_factor, results_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    bt.id, bt.strategy, JSON.stringify(bt.params),
    bt.pairFilter ? JSON.stringify(bt.pairFilter) : null,
    bt.horizonFilter ? JSON.stringify(bt.horizonFilter) : null,
    bt.totalTrades, bt.correctTrades, bt.accuracy,
    bt.avgReturnPct ?? null, bt.sharpe ?? null, bt.maxDrawdown ?? null, bt.profitFactor ?? null,
    bt.resultsJson ? JSON.stringify(bt.resultsJson) : null
  )
}

/**
 * Get latest backtest per strategy.
 */
export function getLatestBacktests() {
  const db = getDb()
  return db.prepare(`
    SELECT b.* FROM backtests b
    INNER JOIN (
      SELECT strategy, MAX(created_at) as max_ts
      FROM backtests
      GROUP BY strategy
    ) latest ON b.strategy = latest.strategy AND b.created_at = latest.max_ts
    ORDER BY b.accuracy DESC
  `).all()
}

// =============================================================================
// PIPELINE RUNS
// =============================================================================

/**
 * Insert a pipeline run record.
 */
export function insertPipelineRun(run) {
  const db = getDb()
  stmt(db, `
    INSERT INTO pipeline_runs (
      id, epoch, timestamp, budget_qu,
      predictions_generated, predictions_committed, cost_qu,
      strategies_used
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    run.id, run.epoch, run.timestamp, run.budgetQu,
    run.predictionsGenerated, run.predictionsCommitted, run.costQu,
    run.strategiesUsed ? JSON.stringify(run.strategiesUsed) : null
  )
}

/**
 * Update pipeline run with results after reveals.
 */
export function updatePipelineRunResults(id, correct, incorrect, accuracy) {
  const db = getDb()
  stmt(db, `
    UPDATE pipeline_runs SET correct = ?, incorrect = ?, accuracy = ?
    WHERE id = ?
  `).run(correct, incorrect, accuracy, id)
}

// =============================================================================
// EXPORT HELPERS
// =============================================================================

/**
 * Generate the complete dashboard export object.
 */
export function getDashboardExport() {
  const db = getDb()
  const stats = getPredictionStats()
  const priceStats = getPriceStats()
  const strategies = getActiveStrategies()
  const latestBacktests = getLatestBacktests()
  const recentPredictions = getAllPredictions({ limit: 50 })

  // Accuracy over time (daily)
  const accuracyOverTime = db.prepare(`
    SELECT
      DATE(commit_timestamp) as date,
      COUNT(*) as total,
      SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) as correct,
      CASE
        WHEN SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END) > 0
        THEN ROUND(100.0 * SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) /
             SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END), 1)
        ELSE NULL
      END as accuracy
    FROM predictions
    WHERE status IN ('correct', 'incorrect')
    GROUP BY DATE(commit_timestamp)
    ORDER BY date
  `).all()

  // Confidence calibration: bin predictions by confidence, measure accuracy
  const confidenceCalibration = db.prepare(`
    SELECT
      CASE
        WHEN confidence < 0.3 THEN '0-30%'
        WHEN confidence < 0.5 THEN '30-50%'
        WHEN confidence < 0.7 THEN '50-70%'
        WHEN confidence < 0.85 THEN '70-85%'
        ELSE '85-100%'
      END as bin,
      COUNT(*) as total,
      SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) as correct,
      CASE
        WHEN SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END) > 0
        THEN ROUND(100.0 * SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) /
             SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END), 1)
        ELSE NULL
      END as accuracy
    FROM predictions
    WHERE status IN ('correct', 'incorrect')
    GROUP BY bin
    ORDER BY MIN(confidence)
  `).all()

  // Pair × Horizon performance matrix
  const pairHorizonMatrix = db.prepare(`
    SELECT
      pair,
      horizon_hours as horizon,
      COUNT(*) as total,
      SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) as correct,
      CASE
        WHEN SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END) > 0
        THEN ROUND(100.0 * SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) /
             SUM(CASE WHEN status IN ('correct','incorrect') THEN 1 ELSE 0 END), 1)
        ELSE NULL
      END as accuracy
    FROM predictions
    WHERE status IN ('correct', 'incorrect')
    GROUP BY pair, horizon_hours
    ORDER BY pair, horizon_hours
  `).all()

  // Streak analysis
  const resolvedPreds = db.prepare(`
    SELECT status FROM predictions
    WHERE status IN ('correct', 'incorrect')
    ORDER BY commit_timestamp ASC
  `).all()

  let maxWin = 0, maxLoss = 0, curStreak = 0, curType = null
  const streakDist = { 1: 0, 2: 0, 3: 0, '4+': 0 }
  for (const p of resolvedPreds) {
    const isWin = p.status === 'correct'
    if ((isWin && curType === 'win') || (!isWin && curType === 'loss')) {
      curStreak++
    } else {
      // Record previous streak
      if (curStreak > 0) {
        const key = curStreak >= 4 ? '4+' : String(curStreak)
        streakDist[key] = (streakDist[key] || 0) + 1
      }
      curStreak = 1
      curType = isWin ? 'win' : 'loss'
    }
    if (isWin && curStreak > maxWin) maxWin = curStreak
    if (!isWin && curStreak > maxLoss) maxLoss = curStreak
  }
  if (curStreak > 0) {
    const key = curStreak >= 4 ? '4+' : String(curStreak)
    streakDist[key] = (streakDist[key] || 0) + 1
  }

  // Oracle Explorer data
  const oracleStatsData = getOracleStats()
  const pairCoverageData = getPairCoverage()
  const currentSpreads = getTopSpreads(5, 0.01) // last 5 min, > 0.01%

  // Cost efficiency
  const revealed = (stats.overall.correct || 0) + (stats.overall.incorrect || 0)
  const totalCostQU = stats.overall.total * 10 // 10 QU per commit
  const revealCostQU = revealed * 10 // 10 QU per reveal
  const costPerCorrect = stats.overall.correct > 0
    ? Math.round((totalCostQU + revealCostQU) / stats.overall.correct)
    : null

  return {
    generatedAt: new Date().toISOString(),
    summary: {
      totalPredictions: stats.overall.total,
      committed: stats.overall.committed,
      correct: stats.overall.correct,
      incorrect: stats.overall.incorrect,
      overallAccuracy: stats.overall.accuracy,
      totalPriceSnapshots: priceStats.total,
      uniquePairs: priceStats.pairs,
      dataRange: { from: priceStats.earliest, to: priceStats.latest },
    },
    strategyPerformance: stats.byStrategy,
    pairPerformance: stats.byPair,
    horizonPerformance: stats.byHorizon,
    recentPredictions,
    accuracyOverTime,
    confidenceCalibration,
    pairHorizonMatrix,
    streakAnalysis: { maxWin, maxLoss, currentStreak: curStreak, currentType: curType, distribution: streakDist },
    backtestResults: latestBacktests.map(bt => ({
      strategy: bt.strategy,
      accuracy: bt.accuracy,
      totalTrades: bt.total_trades,
      correctTrades: bt.correct_trades,
      sharpe: bt.sharpe_ratio,
      profitFactor: bt.profit_factor,
      createdAt: bt.created_at,
    })),
    strategies: strategies.map(s => ({
      name: s.name,
      type: s.type,
      description: s.description,
      isActive: !!s.is_active,
      accuracy: s.accuracy,
      totalPredictions: s.total_predictions,
      correctPredictions: s.correct_predictions,
      lastUsed: s.last_used,
    })),
    oracleExplorer: {
      oracles: oracleStatsData.map(o => ({
        name: o.oracle,
        pairsTracked: o.pairCount,
        totalSnapshots: o.totalSnapshots,
        firstSeen: o.firstSeen,
        lastSeen: o.lastSeen,
      })),
      spreads: currentSpreads.map(s => ({
        pair: s.pair,
        oracleHigh: s.oracleHigh,
        oracleLow: s.oracleLow,
        priceHigh: s.priceHigh,
        priceLow: s.priceLow,
        spreadPct: s.spreadPct,
        oracleCount: s.oracleCount,
      })),
      pairCoverage: pairCoverageData.map(pc => ({
        pair: pc.pair,
        oracles: pc.oracles ? pc.oracles.split(',') : [],
        oracleCount: pc.oracleCount,
        snapshotCount: pc.snapshotCount,
      })),
    },
    costEfficiency: {
      totalCostQU,
      revealCostQU,
      totalSpentQU: totalCostQU + revealCostQU,
      costPerCorrect,
      totalRevealed: revealed,
      totalCommitted: stats.overall.total,
    },
  }
}
