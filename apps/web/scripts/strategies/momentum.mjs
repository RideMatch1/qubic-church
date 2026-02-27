/**
 * MOMENTUM Strategy v3
 *
 * Trend continuation using time-based ROC with CONSERVATIVE thresholds.
 *
 * v3 fix (0% → target 70%+):
 * - v2 set threshold ABOVE current for UP → required actual price increase → 0%
 * - v3 sets threshold BELOW current for UP (like conservative)
 * - Margin width based on ROC strength: stronger trend = wider margin (more confident)
 * - Downsample to 1-min candles to reduce noise (same as conservative v3)
 * - Require minimum 10min of data for reliable ROC
 * - Cap margin at 0.2%-4%
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

  // --- Time-based lookback: 30min for short, 60min for longer ---
  const lookbackMs = (horizonHours <= 2 ? 30 : 60) * 60 * 1000
  const now = new Date(priceHistory[0].timestamp).getTime()
  if (isNaN(now)) return null
  const cutoff = now - lookbackMs

  const window = priceHistory.filter(p => {
    const t = new Date(p.timestamp).getTime()
    return !isNaN(t) && t >= cutoff
  })

  if (window.length < 10) return null

  // --- Downsample to 1-min candles ---
  const CANDLE_MS = 60 * 1000
  const candles = []
  let bucketStart = new Date(window[window.length - 1].timestamp).getTime()
  let bucketPrices = []

  for (let i = window.length - 1; i >= 0; i--) {
    const t = new Date(window[i].timestamp).getTime()
    if (t >= bucketStart + CANDLE_MS && bucketPrices.length > 0) {
      candles.push({ close: bucketPrices[bucketPrices.length - 1], time: bucketStart })
      bucketStart = bucketStart + CANDLE_MS * Math.floor((t - bucketStart) / CANDLE_MS)
      bucketPrices = []
    }
    bucketPrices.push(window[i].price)
  }
  if (bucketPrices.length > 0) {
    candles.push({ close: bucketPrices[bucketPrices.length - 1], time: bucketStart })
  }

  if (candles.length < 5) return null

  // --- Rate of Change over candle series ---
  const oldest = candles[0]
  const newest = candles[candles.length - 1]
  const roc = (newest.close - oldest.close) / oldest.close
  const rocMinutes = (newest.time - oldest.time) / 60000

  if (rocMinutes < 10) return null // need at least 10 min

  const rocPerHour = roc / (rocMinutes / 60)

  // --- Directional consistency (exponentially weighted) ---
  let weightedUp = 0
  let weightedDown = 0
  let totalWeight = 0
  const decayFactor = 0.92

  for (let i = 1; i < candles.length; i++) {
    const change = candles[i].close - candles[i - 1].close
    const weight = decayFactor ** (candles.length - 1 - i)
    if (change > 0) weightedUp += weight
    else if (change < 0) weightedDown += weight
    totalWeight += weight
  }

  const upRatio = weightedUp / totalWeight
  const downRatio = weightedDown / totalWeight

  // --- Need directional bias (>55%) AND meaningful ROC ---
  const MIN_RATIO = 0.55
  const MIN_ROC_PER_HOUR = 0.0004 // 0.04% per hour minimum

  // --- Calculate volatility for margin sizing ---
  const returns = []
  for (let i = 1; i < candles.length; i++) {
    returns.push((candles[i].close - candles[i - 1].close) / candles[i - 1].close)
  }
  const meanRet = returns.reduce((a, b) => a + b, 0) / returns.length
  const variance = returns.reduce((a, r) => a + (r - meanRet) ** 2, 0) / returns.length
  const minuteVol = Math.sqrt(variance)
  const hourlyVol = minuteVol * Math.sqrt(60)
  const horizonVol = hourlyVol * Math.sqrt(horizonHours)

  if (horizonVol === 0 || isNaN(horizonVol)) return null

  if (upRatio >= MIN_RATIO && rocPerHour > MIN_ROC_PER_HOUR) {
    // Uptrend → predict UP, threshold BELOW current
    // Margin: 0.6x horizon vol (tighter than conservative's 0.8x because we have trend confirmation)
    let margin = horizonVol * 0.6
    margin = Math.max(0.002, Math.min(margin, 0.04))

    // Stronger trend → wider margin (more confident price won't reverse)
    const trendBoost = Math.min(Math.abs(rocPerHour) * 20, 0.5) // up to 50% margin boost
    margin *= (1 + trendBoost)
    margin = Math.min(margin, 0.04) // re-cap

    const threshold = currentPrice * (1 - margin)

    const rocStrength = Math.min(Math.abs(rocPerHour) * 40, 0.15)
    const confidence = Math.min(0.88, 0.45 + upRatio * 0.25 + rocStrength)

    return {
      direction: 'up',
      threshold: Number(threshold.toPrecision(8)),
      confidence: Number(confidence.toFixed(3)),
      reason: `Momentum UP: ROC=${(roc * 100).toFixed(2)}% in ${rocMinutes.toFixed(0)}min, dir=${(upRatio * 100).toFixed(0)}%, margin=${(margin * 100).toFixed(2)}%, candles=${candles.length}`,
    }
  }

  if (downRatio >= MIN_RATIO && rocPerHour < -MIN_ROC_PER_HOUR) {
    // Downtrend → predict DOWN, threshold ABOVE current
    let margin = horizonVol * 0.6
    margin = Math.max(0.002, Math.min(margin, 0.04))

    const trendBoost = Math.min(Math.abs(rocPerHour) * 20, 0.5)
    margin *= (1 + trendBoost)
    margin = Math.min(margin, 0.04)

    const threshold = currentPrice * (1 + margin * 0.8)

    const rocStrength = Math.min(Math.abs(rocPerHour) * 40, 0.15)
    const confidence = Math.min(0.88, 0.45 + downRatio * 0.25 + rocStrength)

    return {
      direction: 'down',
      threshold: Number(threshold.toPrecision(8)),
      confidence: Number(confidence.toFixed(3)),
      reason: `Momentum DOWN: ROC=${(roc * 100).toFixed(2)}% in ${rocMinutes.toFixed(0)}min, dir=${(downRatio * 100).toFixed(0)}%, margin=${(margin * 100).toFixed(2)}%, candles=${candles.length}`,
    }
  }

  return null
}

export const meta = {
  name: 'momentum',
  type: 'momentum',
  description: 'ROC trend continuation with conservative thresholds and 1-min candle downsampling.',
  defaultParams: { lookbackMinutes: 30, minRatio: 0.58, minRocPerHour: 0.0008 },
}
