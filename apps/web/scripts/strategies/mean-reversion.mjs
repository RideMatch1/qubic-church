/**
 * MEAN REVERSION Strategy v3
 *
 * Bet on reversion when price deviates significantly from mean.
 * Uses Bollinger-style bands with CONSERVATIVE thresholds.
 *
 * v3 fix (0% → target 65%+):
 * - v2 set threshold in reversion direction (e.g., below current for DOWN) → required move → 0%
 * - v3 sets threshold on the "easy" side: ABOVE current for DOWN, BELOW for UP
 * - Only triggers on strong deviation (>1.5 sigma)
 * - Margin based on z-score magnitude and horizon volatility
 * - Downsample to 1-min candles for volatility computation
 * - Stricter trend filter: reject if momentum contradicts reversion
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
  if (priceHistory.length < 20) return null
  if (horizonHours < 1 || horizonHours > 4) return null

  // --- Time-based window: 2x horizon or at least 2 hours ---
  const windowMs = Math.max(horizonHours * 2, 2) * 60 * 60 * 1000
  const now = new Date(priceHistory[0].timestamp).getTime()
  if (isNaN(now)) return null
  const cutoff = now - windowMs

  const windowData = priceHistory.filter(p => {
    const t = new Date(p.timestamp).getTime()
    return !isNaN(t) && t >= cutoff
  })

  if (windowData.length < 20) return null

  // --- Downsample to 1-min candles ---
  const CANDLE_MS = 60 * 1000
  const candles = []
  let bStart = new Date(windowData[windowData.length - 1].timestamp).getTime()
  let bPrices = []

  for (let i = windowData.length - 1; i >= 0; i--) {
    const t = new Date(windowData[i].timestamp).getTime()
    if (t >= bStart + CANDLE_MS && bPrices.length > 0) {
      candles.push(bPrices[bPrices.length - 1])
      bStart += CANDLE_MS * Math.floor((t - bStart) / CANDLE_MS)
      bPrices = []
    }
    bPrices.push(windowData[i].price)
  }
  if (bPrices.length > 0) candles.push(bPrices[bPrices.length - 1])

  if (candles.length < 10) return null

  // --- Calculate Bollinger-style bands on candle closes ---
  const candleMean = candles.reduce((a, b) => a + b, 0) / candles.length
  const candleVar = candles.reduce((a, p) => a + (p - candleMean) ** 2, 0) / candles.length
  const candleStd = Math.sqrt(candleVar)

  if (candleStd === 0 || candleMean === 0) return null

  const zScore = (currentPrice - candleMean) / candleStd

  // --- Trend filter: reject if last 15min shows strong momentum ---
  const trendCutoff = now - 15 * 60 * 1000
  const recentPrices = priceHistory.filter(p => {
    const t = new Date(p.timestamp).getTime()
    return !isNaN(t) && t >= trendCutoff
  })

  if (recentPrices.length >= 5) {
    const recentReturn = (recentPrices[0].price - recentPrices[recentPrices.length - 1].price) / recentPrices[recentPrices.length - 1].price
    const relStd = candleStd / candleMean
    const trendStrength = Math.abs(recentReturn) / relStd

    // If momentum is strong AND aligned with deviation → skip (trend, not reversion)
    if (trendStrength > 1.5) {
      if ((zScore > 0 && recentReturn > 0) || (zScore < 0 && recentReturn < 0)) {
        return null
      }
    }
  }

  // --- Need meaningful deviation (>1.2 sigma) ---
  const SIGMA_THRESHOLD = 1.2
  if (Math.abs(zScore) < SIGMA_THRESHOLD) return null

  // --- Calculate horizon-scaled volatility for margin ---
  const returns = []
  for (let i = 1; i < candles.length; i++) {
    returns.push((candles[i] - candles[i - 1]) / candles[i - 1])
  }
  const minVol = Math.sqrt(returns.reduce((a, r) => a + r ** 2, 0) / returns.length)
  const horizonVol = minVol * Math.sqrt(60) * Math.sqrt(horizonHours)

  if (horizonVol === 0 || isNaN(horizonVol)) return null

  // --- Conservative margin: 0.5x horizon vol, boosted by z-score magnitude ---
  let margin = horizonVol * 0.5
  const zBoost = Math.min((Math.abs(zScore) - SIGMA_THRESHOLD) * 0.2, 0.4)
  margin *= (1 + zBoost)
  margin = Math.max(0.002, Math.min(margin, 0.035))

  const confidence = Math.min(0.80, 0.38 + Math.abs(zScore) * 0.10)

  if (zScore > SIGMA_THRESHOLD) {
    // Price HIGH above mean → predict DOWN, threshold ABOVE current
    const threshold = currentPrice * (1 + margin * 0.8)
    if (threshold < currentPrice) return null

    return {
      direction: 'down',
      threshold: Number(threshold.toPrecision(8)),
      confidence: Number(confidence.toFixed(3)),
      reason: `MeanRev DOWN: z=${zScore.toFixed(2)}, mean=${candleMean.toPrecision(6)}, ${(Math.abs(zScore * candleStd / candleMean) * 100).toFixed(2)}% above, margin=${(margin * 100).toFixed(2)}%, candles=${candles.length}`,
    }
  }

  if (zScore < -SIGMA_THRESHOLD) {
    // Price LOW below mean → predict UP, threshold BELOW current
    const threshold = currentPrice * (1 - margin)
    if (threshold > currentPrice) return null
    if (threshold <= 0) return null

    return {
      direction: 'up',
      threshold: Number(threshold.toPrecision(8)),
      confidence: Number(confidence.toFixed(3)),
      reason: `MeanRev UP: z=${zScore.toFixed(2)}, mean=${candleMean.toPrecision(6)}, ${(Math.abs(zScore * candleStd / candleMean) * 100).toFixed(2)}% below, margin=${(margin * 100).toFixed(2)}%, candles=${candles.length}`,
    }
  }

  return null
}

export const meta = {
  name: 'mean_reversion',
  type: 'mean_reversion',
  description: 'Bollinger-band reversion with conservative thresholds, trend filter, and 1-min candles.',
  defaultParams: { sigmaThreshold: 1.5, maxHorizon: 4 },
}
