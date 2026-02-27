/**
 * CONSERVATIVE Strategy v3
 *
 * Sets threshold below current price for "up" (or above for "down" in downtrends).
 * Uses sqrt(T) volatility scaling for proper horizon-adjustment.
 *
 * v3 improvements over v2:
 * - Downsample returns to 1-minute intervals before computing volatility
 *   (removes noise from 11s tick-by-tick data)
 * - Cap margin at 5% to prevent absurd negative thresholds
 * - Filter outlier returns (>3 sigma) that inflate volatility
 * - Tighter safety multiplier (0.8x instead of 1.5x) for more meaningful thresholds
 * - Higher confidence when margin is in sweet spot (0.3-2%)
 *
 * @param {Object} ctx
 * @param {string} ctx.pair
 * @param {number} ctx.currentPrice
 * @param {Array}  ctx.priceHistory - [{price, timestamp}] sorted desc (newest first)
 * @param {number} ctx.horizonHours
 * @returns {{ direction, threshold, confidence, reason } | null}
 */
export function evaluate(ctx) {
  const { currentPrice, priceHistory, horizonHours } = ctx

  if (!currentPrice || currentPrice <= 0) return null
  if (priceHistory.length < 10) return null
  if (horizonHours > 4) return null

  // --- Time-based volatility: use last 60 min of data ---
  const windowMs = 60 * 60 * 1000
  const now = priceHistory[0]?.timestamp ? new Date(priceHistory[0].timestamp).getTime() : Date.now()
  if (isNaN(now)) return null
  const cutoff = now - windowMs

  const windowPrices = priceHistory.filter(p => {
    const t = new Date(p.timestamp).getTime()
    return !isNaN(t) && t >= cutoff
  })

  if (windowPrices.length < 10) return null

  // --- Downsample to ~1-minute candles to reduce tick noise ---
  const CANDLE_MS = 60 * 1000
  const candles = []
  let bucketStart = new Date(windowPrices[windowPrices.length - 1].timestamp).getTime()
  let bucketPrices = []

  // windowPrices is newest-first, iterate backwards (oldest first)
  for (let i = windowPrices.length - 1; i >= 0; i--) {
    const t = new Date(windowPrices[i].timestamp).getTime()
    if (t >= bucketStart + CANDLE_MS && bucketPrices.length > 0) {
      // Close this candle
      candles.push({
        close: bucketPrices[bucketPrices.length - 1],
        time: bucketStart,
      })
      bucketStart = bucketStart + CANDLE_MS * Math.floor((t - bucketStart) / CANDLE_MS)
      bucketPrices = []
    }
    bucketPrices.push(windowPrices[i].price)
  }
  if (bucketPrices.length > 0) {
    candles.push({ close: bucketPrices[bucketPrices.length - 1], time: bucketStart })
  }

  if (candles.length < 5) return null

  // --- Calculate 1-minute returns ---
  const returns = []
  for (let i = 1; i < candles.length; i++) {
    const ret = (candles[i].close - candles[i - 1].close) / candles[i - 1].close
    returns.push(ret)
  }

  if (returns.length < 3) return null

  // --- Filter outlier returns (>3 sigma on first pass) ---
  const rawMean = returns.reduce((a, b) => a + b, 0) / returns.length
  const rawVar = returns.reduce((a, r) => a + (r - rawMean) ** 2, 0) / returns.length
  const rawStd = Math.sqrt(rawVar)

  const filtered = rawStd > 0
    ? returns.filter(r => Math.abs(r - rawMean) < rawStd * 3)
    : returns

  if (filtered.length < 3) return null

  // --- Compute per-minute volatility, scale to hourly ---
  const meanRet = filtered.reduce((a, b) => a + b, 0) / filtered.length
  const variance = filtered.reduce((a, r) => a + (r - meanRet) ** 2, 0) / filtered.length
  const minuteVol = Math.sqrt(variance)
  const hourlyVolatility = minuteVol * Math.sqrt(60) // sqrt(60) minutes per hour

  if (hourlyVolatility === 0 || isNaN(hourlyVolatility)) return null

  // sqrt(T) scaling for horizon
  const horizonVol = hourlyVolatility * Math.sqrt(horizonHours)

  // --- Detect trend direction ---
  const trendReturn = (candles[candles.length - 1].close - candles[0].close) / candles[0].close
  const isDowntrend = trendReturn < -horizonVol * 0.5

  // --- Set margin and threshold ---
  // Safety multiplier: 0.8x horizon vol (tighter than v2's 1.5x)
  const safetyMultiplier = 0.8
  let margin = horizonVol * safetyMultiplier

  // Cap margin: minimum 0.2%, maximum 5%
  margin = Math.max(0.002, Math.min(margin, 0.05))

  let direction, threshold

  if (isDowntrend) {
    direction = 'down'
    threshold = currentPrice * (1 + margin * 0.8)
  } else {
    direction = 'up'
    threshold = currentPrice * (1 - margin)
  }

  // Sanity: threshold must be positive and within reasonable range
  if (threshold <= 0) threshold = currentPrice * 0.95
  if (direction === 'up' && threshold > currentPrice) return null
  if (direction === 'down' && threshold < currentPrice) return null

  // --- Confidence calibration ---
  // Sweet spot: 0.3-2% margin = high confidence
  // Too tight (<0.2%) or too wide (>3%) = lower confidence
  let confidence
  if (margin >= 0.003 && margin <= 0.02) {
    confidence = Math.min(0.92, 0.65 + (0.02 - Math.abs(margin - 0.01)) * 10)
  } else if (margin < 0.003) {
    confidence = 0.45 + margin * 50 // low margin = risky
  } else {
    confidence = Math.max(0.50, 0.85 - (margin - 0.02) * 10) // high margin = easy but less useful
  }

  return {
    direction,
    threshold: Number(threshold.toPrecision(8)),
    confidence: Number(confidence.toFixed(3)),
    reason: `Conservative ${direction.toUpperCase()}: margin ${(margin * 100).toFixed(2)}%, hourlyVol=${(hourlyVolatility * 100).toFixed(3)}%, hVol=${(horizonVol * 100).toFixed(3)}%, candles=${candles.length}`,
  }
}

export const meta = {
  name: 'conservative',
  type: 'conservative',
  description: 'Downsample-based volatility with capped margins and outlier filtering.',
  defaultParams: { safetyMultiplier: 0.8, maxMargin: 0.05, maxHorizon: 4 },
}
