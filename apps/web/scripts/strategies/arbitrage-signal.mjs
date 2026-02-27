/**
 * ARBITRAGE SIGNAL Strategy v1
 *
 * Detects cross-oracle price divergence and predicts mean-reversion.
 * When the same asset trades at different prices on different oracles,
 * the lagging oracle will catch up to the leader.
 *
 * Uses CONSERVATIVE thresholds (threshold on the easy side).
 *
 * @param {Object} ctx
 * @param {string} ctx.pair
 * @param {number} ctx.currentPrice
 * @param {Array}  ctx.priceHistory - [{price, timestamp, oracle}] sorted desc
 * @param {number} ctx.horizonHours
 * @param {Object} [ctx.allPrices] - { 'btc/usdt': [...], ... }
 * @returns {{ direction, threshold, confidence, reason } | null}
 */
export function evaluate(ctx) {
  const { pair, currentPrice, priceHistory, horizonHours } = ctx

  if (!currentPrice || currentPrice <= 0) return null
  if (priceHistory.length < 10) return null
  if (horizonHours < 1 || horizonHours > 4) return null

  // Need oracle field in price history for cross-oracle analysis
  const withOracle = priceHistory.filter(p => p.oracle)
  if (withOracle.length < 5) return null

  const now = new Date(priceHistory[0].timestamp).getTime()
  if (isNaN(now)) return null

  // --- Get prices from different oracles in last 5 minutes ---
  const WINDOW_MS = 5 * 60 * 1000
  const cutoff = now - WINDOW_MS
  const recent = withOracle.filter(p => {
    const t = new Date(p.timestamp).getTime()
    return !isNaN(t) && t >= cutoff
  })

  // Group by oracle, get latest price per oracle
  const oraclePrices = new Map()
  for (const p of recent) {
    if (!oraclePrices.has(p.oracle)) {
      oraclePrices.set(p.oracle, { price: p.price, timestamp: p.timestamp })
    }
    // recent is sorted desc, so first entry per oracle is the latest
  }

  if (oraclePrices.size < 2) return null

  // --- Find max spread ---
  const prices = [...oraclePrices.entries()]
  let highOracle = prices[0][0], highPrice = prices[0][1].price
  let lowOracle = prices[0][0], lowPrice = prices[0][1].price

  for (const [oracle, data] of prices) {
    if (data.price > highPrice) { highPrice = data.price; highOracle = oracle }
    if (data.price < lowPrice) { lowPrice = data.price; lowOracle = oracle }
  }

  if (lowPrice <= 0) return null
  const spreadPct = (highPrice - lowPrice) / lowPrice

  // Need meaningful spread (> 0.1%)
  const MIN_SPREAD = 0.001
  if (spreadPct < MIN_SPREAD) return null

  // --- Determine if current price is on the low or high side ---
  const midPrice = (highPrice + lowPrice) / 2
  const isLow = currentPrice < midPrice
  const isHigh = currentPrice > midPrice

  // Predict convergence: if current is low → UP, if high → DOWN
  const direction = isLow ? 'up' : 'down'

  // --- Calculate volatility for margin ---
  const returns = []
  for (let i = 1; i < Math.min(priceHistory.length, 300); i++) {
    const r = (priceHistory[i - 1].price - priceHistory[i].price) / priceHistory[i].price
    if (isFinite(r)) returns.push(r)
  }
  if (returns.length < 10) return null

  // Filter outliers (3-sigma)
  const meanR = returns.reduce((a, b) => a + b, 0) / returns.length
  const stdR = Math.sqrt(returns.reduce((a, r) => a + (r - meanR) ** 2, 0) / returns.length)
  const filtered = stdR > 0
    ? returns.filter(r => Math.abs(r - meanR) < 3 * stdR)
    : returns

  if (filtered.length < 5) return null

  // Estimate per-tick volatility, scale to horizon
  const avgInterval = WINDOW_MS / recent.length // ms per tick
  const ticksPerHour = 3600000 / Math.max(avgInterval, 1000)
  const tickVol = Math.sqrt(filtered.reduce((a, r) => a + r ** 2, 0) / filtered.length)
  const horizonVol = tickVol * Math.sqrt(ticksPerHour * horizonHours)

  if (horizonVol === 0 || isNaN(horizonVol)) return null

  // --- Conservative margin ---
  // Arbitrage is a strong signal → 0.4x horizon vol (smaller margin = easier to win)
  let margin = horizonVol * 0.4
  // Larger spread = more confident → wider margin still easy
  const spreadBoost = Math.min(spreadPct * 20, 0.5)
  margin *= (1 + spreadBoost)
  margin = Math.max(0.002, Math.min(margin, 0.035))

  // --- Threshold ---
  let threshold
  if (direction === 'up') {
    threshold = currentPrice * (1 - margin)
    if (threshold > currentPrice || threshold <= 0) return null
  } else {
    threshold = currentPrice * (1 + margin * 0.8)
    if (threshold < currentPrice) return null
  }

  // --- Confidence ---
  // Higher spread = more confident
  const spreadConf = Math.min(spreadPct * 30, 0.20)
  // More oracles agreeing = more data
  const oracleConf = Math.min((oraclePrices.size - 2) * 0.05, 0.10)
  const confidence = Math.min(0.80, 0.40 + spreadConf + oracleConf)

  return {
    direction,
    threshold: Number(threshold.toPrecision(8)),
    confidence: Number(confidence.toFixed(3)),
    reason: `Arb ${direction.toUpperCase()}: spread=${(spreadPct * 100).toFixed(3)}%, ${highOracle}=${highPrice.toPrecision(6)} vs ${lowOracle}=${lowPrice.toPrecision(6)}, oracles=${oraclePrices.size}, margin=${(margin * 100).toFixed(2)}%`,
  }
}

export const meta = {
  name: 'arbitrage_signal',
  type: 'arbitrage_signal',
  description: 'Cross-oracle price divergence with mean-reversion prediction.',
  defaultParams: { minSpread: 0.001, maxHorizon: 4 },
}
