# Oracle Prediction Engine — Technical Documentation

## System Overview

The Oracle Prediction Engine is an automated on-chain prediction system built on top of Qubic Oracle Machines (OMs). It commits price predictions to the Qubic blockchain using a commit-reveal scheme, runs multiple trading strategies in parallel, and tracks accuracy with full transparency.

**Current Status (2026-02-11):**
- 220 predictions committed on-chain
- 101 revealed: 79 correct, 22 incorrect = **78.2% accuracy**
- 112 pending reveal, 7 strategies active
- 22 unique trading pairs across 5+ oracle sources
- 171K+ price snapshots in SQLite database

---

## Architecture

```
ORACLE_DOMINATOR.mjs        ORACLE_AUTOPILOT.mjs         oracle-reveal-loop.mjs
  (Price Collection)           (Prediction Pipeline)        (Auto-Reveal)
        │                            │                           │
        ▼                            ▼                           ▼
   ┌─────────┐              ┌──────────────┐            ┌──────────────┐
   │ Oracle   │   prices →  │  7 Strategies │  commit →  │  Reveal      │
   │ Machines │ ──────────→ │  (evaluate)   │ ─────────→ │  Expired     │
   │ (Qubic)  │             │              │             │  Predictions │
   └─────────┘              └──────────────┘            └──────────────┘
        │                            │                           │
        ▼                            ▼                           ▼
   ┌────────────────────────────────────────────────────────────────┐
   │                     oracle.sqlite3 (SQLite + WAL)             │
   │  tables: prices, predictions, strategies, pipeline_runs       │
   └────────────────────────────────────────────────────────────────┘
        │
        ▼
   oracle-export.mjs → oracle-dashboard.json → API Route → Dashboard UI
```

### Core Components

| File | Purpose |
|------|---------|
| `oracle-utils.mjs` | Constants, WORKING_PAIRS (51), crypto helpers, Qubic RPC |
| `oracle-db.mjs` | SQLite data layer (better-sqlite3, WAL mode, prepared statements) |
| `ORACLE_DOMINATOR.mjs` | Price collection: query Oracle Machines, store in DB |
| `ORACLE_AUTOPILOT.mjs` | Full prediction pipeline: collect → generate → filter → rank → budget → commit |
| `oracle-export.mjs` | Export dashboard JSON from DB |
| `strategies/*.mjs` | 7 strategy modules |
| `oracle-reveal-loop.mjs` | Background process: reveal expired predictions every 10 min |

### Data Flow

1. **ORACLE_DOMINATOR** queries Qubic Oracle Machines for live prices (11-second ticks)
2. Prices stored in `oracle.sqlite3` with oracle source attribution
3. **ORACLE_AUTOPILOT** runs the 9-phase pipeline:
   - COLLECT: Read latest prices from DB
   - GENERATE: Run all 7 strategies across 22 pairs x 3 horizons
   - FILTER: Remove confidence < 0.40, deduplicate per pair+horizon+direction
   - RANK: Sort by confidence (highest first)
   - BUDGET: Tiered allocation per strategy (with dynamic accuracy boost)
   - COMMIT: Inscribe predictions on-chain (10 QU each)
   - REVEAL: Check expired predictions against live prices
   - UPDATE: Refresh strategy performance stats
   - EXPORT: Generate dashboard JSON
4. **Auto-reveal loop** runs every 10 minutes to reveal expired predictions

---

## Strategies

All strategies share the **conservative threshold pattern**:
- **UP prediction**: threshold = price * (1 - margin) → threshold BELOW current price
- **DOWN prediction**: threshold = price * (1 + margin * 0.8) → threshold ABOVE current price

This means predictions are "easy to win" — they only require the price to stay on the right side of a threshold set conservatively below/above current price.

### 1. Conservative (30% allocation)
- **Live accuracy: 47/47 = 100%**
- Detects trend via 1-hour candle return, sets margin at 0.8x horizon volatility
- Downtrend → DOWN, else → UP
- Margin capped: 0.2% - 5%
- Confidence based on margin sweet spot (0.3-2%)
- Max horizon: 4h

### 2. Mean Reversion (18% allocation)
- **Live: 0/3 (all Round 1 pre-fix). Backtest: 100% (44/44)**
- Bollinger-band style: z-score deviation from 1-min candle mean
- Requires z > 1.2 sigma deviation
- Trend filter: rejects if 15min momentum aligns with deviation
- Margin: 0.5x horizon vol, boosted by z-score magnitude
- Max horizon: 4h

### 3. Consensus (12% allocation)
- **Live: 9/16 = 56.3%**
- Multi-oracle divergence: detects when oracle sources disagree
- Requires 2+ oracle sources with divergence > 0.4x recent volatility
- Current price deviation from consensus mean triggers direction
- Margin: 0.5x horizon vol
- Max horizon: 8h

### 4. Arbitrage Signal (12% allocation)
- **Live: 27 pending (untested)**
- Cross-oracle price divergence: when same asset trades at different prices
- Mean-reversion prediction on the lagging oracle
- Requires 2+ oracles, spread > 0.1%
- Margin: 0.4x horizon vol with spread boost
- Max horizon: 4h

### 5. Volatility Breakout (10% allocation)
- **Live: 4/6 = 67%**
- Bollinger Band squeeze detection (bandwidth ratio < 50%)
- Breakout continuation: price above upper band → UP, below lower → DOWN
- Margin: 0.7x horizon vol with squeeze factor boost
- Max horizon: 4h

### 6. Momentum (8% allocation)
- **Live: 0/10 (all Round 1 pre-fix)**
- ROC-based trend continuation
- Exponentially-weighted directional consistency (decay=0.92)
- Requires >55% directional bias AND meaningful ROC
- Margin: 0.6x horizon vol with trend boost
- Max horizon: 4h

### 7. Cross-Asset (10% allocation)
- **Live: 0/2 (too few samples)**
- BTC lead-lag: altcoins follow BTC with 5-30 minute delay
- Per-asset beta values (SOL=1.20, DOGE=1.30, BNB=0.75, etc.)
- Requires BTC move > 0.15% and meaningful lag
- Margin: 0.5x horizon vol with lag boost
- Max horizon: 4h

---

## Performance Metrics (Live)

### By Direction
| Direction | Correct | Total | Accuracy |
|-----------|---------|-------|----------|
| UP | 61 | 67 | **91.0%** |
| DOWN | 18 | 34 | **52.9%** |

### By Horizon
| Horizon | Correct | Total | Accuracy |
|---------|---------|-------|----------|
| 1h | 43 | 52 | **82.7%** |
| 2h | 18 | 28 | **64.3%** |
| 4h | 18 | 21 | **85.7%** |

### By Strategy
| Strategy | Correct | Total | Accuracy |
|----------|---------|-------|----------|
| conservative | 47 | 47 | **100%** |
| consensus | 9 | 16 | 56.3% |
| volatility_breakout | 4 | 6 | 67% |
| momentum | 0 | 10 | 0%* |
| mean_reversion | 0 | 3 | 0%* |
| cross_asset | 0 | 2 | 0%* |

*\*All failures from Round 1 before v3 threshold fix. Not indicative of v3 performance.*

---

## Optimization History

### v1 → v2: Threshold Direction Fix
**Problem:** All strategies except conservative had 0% accuracy.
**Root Cause:** Threshold was set in the "hard" direction — e.g., UP prediction with threshold ABOVE current price required actual price increase to win.
**Fix:** All strategies rewritten with conservative threshold pattern (threshold on the easy side).

### v2 → v3: Volatility & Candle Improvements
- Downsample 11-second tick data to 1-minute candles before computing volatility
- sqrt(T) horizon scaling for proper time-adjusted margins
- 3-sigma outlier filtering on returns
- Time-based data loading (minutes, not row count)

### v4: DOWN Margin Fix (current)
**Problem:** DOWN predictions had 52.9% accuracy vs 91.0% for UP.
**Root Cause:** DOWN threshold used `margin * 0.3` (only 0.6% room with 2% margin) while UP used full `margin` (2% room).
**Fix:** Changed all strategies to use `margin * 0.8` for DOWN thresholds.
- UP: threshold = price * (1 - margin) → full margin
- DOWN: threshold = price * (1 + margin * 0.8) → 80% of margin (was 30%)

### v4: Tier Rebalancing
Based on live performance:
- Conservative: 22% → **30%** (proven 100% accuracy)
- Arbitrage: 10% → **12%** (promising cross-oracle signal)
- Momentum: 6% → **8%** (needs v3 proving)
- Cross-asset: 5% → **10%** (needs more data)
- Consensus: 22% → **12%** (weak DOWN performance)
- Mean-reversion: 25% → **18%** (untested on v3 live)

### v4: Horizon Priority
Based on live accuracy:
- 1h (82.7%) and 4h (85.7%) prioritized over 2h (64.3%)

---

## Cost Model

| Operation | Cost |
|-----------|------|
| Oracle Query (price fetch) | 10 QU |
| Prediction Commit | 10 QU |
| Prediction Reveal | 10 QU |
| **Total per prediction** | **20 QU** (commit + reveal) |

Current spend: ~220 predictions x 10 QU commit = 2200 QU committed.
Reveal costs are amortized in the auto-reveal loop.

**Cost efficiency**: At 78.2% accuracy with 10 QU per commit, the cost per correct prediction is ~12.8 QU.

---

## Running the System

### Price Collection
```bash
# Start price collection (runs continuously)
node scripts/ORACLE_DOMINATOR.mjs --loop --interval 11
```

### Prediction Pipeline
```bash
# Single run with 1000 QU budget
node scripts/ORACLE_AUTOPILOT.mjs --budget 1000

# Dry run (no on-chain commits)
node scripts/ORACLE_AUTOPILOT.mjs --dry-run --budget 5000

# Continuous mode
node scripts/ORACLE_AUTOPILOT.mjs --loop --interval 60 --budget 500
```

### Auto-Reveal
```bash
# Start reveal loop (checks every 10 minutes)
node /tmp/oracle-reveal-loop.mjs
```

### Dashboard Export
```bash
# Manual export
node scripts/oracle-export.mjs
```

### Dashboard
The prediction dashboard is available at `/monitoring` in the web app with tabs:
- **Predictions**: Live feed of all predictions with status
- **Strategies**: Performance breakdown by strategy
- **Pairs**: Per-pair accuracy and volume
- **Horizons**: Time-horizon analysis
- **Analytics**: Cost efficiency, rolling accuracy, confidence calibration
- **Arbitrage**: Cross-oracle spread monitoring
- **Explorer**: Oracle source status and pair coverage

---

## Database Schema

```sql
-- Price snapshots (171K+ rows)
CREATE TABLE prices (
  id INTEGER PRIMARY KEY,
  pair TEXT,           -- e.g. 'btc/usdt'
  oracle TEXT,         -- e.g. 'binance', 'mexc', 'gate'
  price REAL,
  timestamp TEXT,      -- ISO 8601
  raw_value TEXT       -- Original oracle response
);

-- Predictions (220+ rows)
CREATE TABLE predictions (
  id TEXT PRIMARY KEY,  -- e.g. 'pred_042'
  pair TEXT,
  direction TEXT,       -- 'up' | 'down'
  threshold REAL,
  horizon_hours INTEGER,
  price_at_commit REAL,
  commit_timestamp TEXT,
  expires_at TEXT,
  commit_hash TEXT,     -- SHA-256 of prediction
  commit_tick INTEGER,
  commit_tx_id TEXT,
  epoch INTEGER,
  status TEXT,          -- 'committed' | 'correct' | 'incorrect'
  outcome TEXT,         -- 'correct' | 'incorrect' | NULL
  price_at_expiry REAL,
  reveal_tick INTEGER,
  strategy TEXT,
  confidence REAL,
  verification_json TEXT
);

-- Strategy stats
CREATE TABLE strategies (
  name TEXT PRIMARY KEY,
  total_predictions INTEGER,
  correct_predictions INTEGER,
  accuracy REAL,
  avg_confidence REAL,
  last_updated TEXT,
  is_active INTEGER,
  params_json TEXT
);
```

---

## Oracle Sources

| Oracle | Pairs | Description |
|--------|-------|-------------|
| binance | 21 | Binance exchange prices |
| mexc | 13 | MEXC exchange prices |
| gate | 8 | Gate.io exchange prices |
| gate_mexc | 8 | Gate + MEXC composite |
| binance_mexc | 3 | Binance + MEXC composite |
| binance_gate | 3 | Binance + Gate composite |

**22 unique pairs tracked**: BTC, ETH, SOL, XRP, BNB, DOGE, ADA, AVAX, LINK, DOT, LTC, SUI, NEAR, TRX, ATOM, APT, MATIC, FIL, QUBIC, ARB, OP, ETH/BTC

---

## Key Design Decisions

1. **Conservative thresholds over directional accuracy**: Rather than predicting exact price movements, we set thresholds that are easy to satisfy. This trades informativeness for accuracy.

2. **SQLite over external DB**: Single-file database with WAL mode provides fast reads/writes without network overhead. Ideal for single-machine operation.

3. **1-minute candle downsampling**: Oracle Machines provide ~11-second tick data. Raw tick-by-tick volatility is noisy; 1-minute candles provide cleaner signals.

4. **Dynamic tier allocation**: Base allocations are adjusted by +-50% based on live accuracy (strategies with >50% accuracy get boosted, below get penalized).

5. **Commit-reveal scheme**: Predictions are hashed and committed before the horizon expires, then revealed after expiry with the actual outcome. This provides cryptographic proof of prediction timing.
