/**
 * VOLATILITY BREAKOUT Strategy v2
 *
 * Detects Bollinger Band squeeze and predicts breakout continuation.
 * Uses CONSERVATIVE thresholds.
 *
 * v2 fix:
 * - v1 set threshold in breakout direction (above current for UP) → hard to win
 * - v2 sets threshold BELOW current for UP, ABOVE for DOWN
 * - Margin based on squeeze intensity and horizon volatility
 * - Downsample to 1-min candles for cleaner band computation
 * - Tighter squeeze detection (50% instead of 60%)
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

  const now = new Date(priceHistory[0].timestamp).getTime()
  if (isNaN(now)) return null

  // --- Downsample to 1-min candles for both windows ---
  const shortMs = Math.max(horizonHours, 1) * 60 * 60 * 1000
  const longMs = Math.max(horizonHours * 4, 4) * 60 * 60 * 1000

  const shortCandles = buildCandles(priceHistory, now - shortMs)
  const longCandles = buildCandles(priceHistory, now - longMs)

  if (shortCandles.length < 10 || longCandles.length < 20) return null

  // --- Current Bollinger Bands (short window on candles) ---
  const shortMean = shortCandles.reduce((a, b) => a + b, 0) / shortCandles.length
  const shortVar = shortCandles.reduce((a, p) => a + (p - shortMean) ** 2, 0) / shortCandles.length
  const shortStd = Math.sqrt(shortVar)
  const shortBandwidth = (shortStd * 2) / shortMean

  // --- Average bandwidth (long window on candles) ---
  const longMean = longCandles.reduce((a, b) => a + b, 0) / longCandles.length
  const longVar = longCandles.reduce((a, p) => a + (p - longMean) ** 2, 0) / longCandles.length
  const longStd = Math.sqrt(longVar)
  const longBandwidth = (longStd * 2) / longMean

  if (longBandwidth === 0 || shortBandwidth === 0) return null

  // --- Squeeze detection ---
  const squeezeRatio = shortBandwidth / longBandwidth
  const isSqueeze = squeezeRatio < 0.50

  // --- Band positions ---
  const upperBand = shortMean + 2 * shortStd
  const lowerBand = shortMean - 2 * shortStd

  const aboveUpper = currentPrice > upperBand
  const belowLower = currentPrice < lowerBand

  const zScore = shortStd > 0 ? (currentPrice - shortMean) / shortStd : 0
  const strongBreakout = Math.abs(zScore) > 2.0

  if (!aboveUpper && !belowLower) return null
  if (!isSqueeze && !strongBreakout) return null

  // --- Calculate horizon-scaled volatility for margin ---
  const returns = []
  for (let i = 1; i < shortCandles.length; i++) {
    returns.push((shortCandles[i] - shortCandles[i - 1]) / shortCandles[i - 1])
  }
  const minVol = Math.sqrt(returns.reduce((a, r) => a + r ** 2, 0) / returns.length)
  const horizonVol = minVol * Math.sqrt(60) * Math.sqrt(horizonHours)

  if (horizonVol === 0 || isNaN(horizonVol)) return null

  // --- Conservative margin ---
  // Breakout is a strong signal → 0.7x horizon vol
  let margin = horizonVol * 0.7
  // Stronger squeeze = wider margin (more confident about direction)
  const squeezeFactor = isSqueeze ? Math.min((1 - squeezeRatio) * 0.6, 0.3) : 0
  margin *= (1 + squeezeFactor)
  margin = Math.max(0.002, Math.min(margin, 0.04))

  // --- Confidence ---
  const breakoutPct = aboveUpper
    ? (currentPrice - upperBand) / upperBand
    : (lowerBand - currentPrice) / lowerBand
  const breakoutFactor = Math.min(breakoutPct * 15, 0.20)
  const squeezeConf = isSqueeze ? Math.min((1 - squeezeRatio) * 0.4, 0.15) : 0
  const confidence = Math.min(0.85, 0.40 + squeezeFactor + breakoutFactor + squeezeConf)

  if (aboveUpper) {
    // Price broke above → predict UP, threshold BELOW current
    const threshold = currentPrice * (1 - margin)
    if (threshold > currentPrice || threshold <= 0) return null

    return {
      direction: 'up',
      threshold: Number(threshold.toPrecision(8)),
      confidence: Number(confidence.toFixed(3)),
      reason: `VolBreak UP: z=${zScore.toFixed(2)}, squeeze=${(squeezeRatio * 100).toFixed(0)}%, break=${(breakoutPct * 100).toFixed(2)}%, margin=${(margin * 100).toFixed(2)}%`,
    }
  }

  if (belowLower) {
    // Price broke below → predict DOWN, threshold ABOVE current
    const threshold = currentPrice * (1 + margin * 0.8)
    if (threshold < currentPrice) return null

    return {
      direction: 'down',
      threshold: Number(threshold.toPrecision(8)),
      confidence: Number(confidence.toFixed(3)),
      reason: `VolBreak DOWN: z=${zScore.toFixed(2)}, squeeze=${(squeezeRatio * 100).toFixed(0)}%, break=${(breakoutPct * 100).toFixed(2)}%, margin=${(margin * 100).toFixed(2)}%`,
    }
  }

  return null
}

/**
 * Build 1-min candle closes from price history.
 */
function buildCandles(priceHistory, cutoff) {
  const filtered = priceHistory.filter(p => {
    const t = new Date(p.timestamp).getTime()
    return !isNaN(t) && t >= cutoff
  })
  if (filtered.length < 5) return []

  const CANDLE_MS = 60 * 1000
  const candles = []
  let bStart = new Date(filtered[filtered.length - 1].timestamp).getTime()
  let bPrices = []

  for (let i = filtered.length - 1; i >= 0; i--) {
    const t = new Date(filtered[i].timestamp).getTime()
    if (t >= bStart + CANDLE_MS && bPrices.length > 0) {
      candles.push(bPrices[bPrices.length - 1])
      bStart += CANDLE_MS * Math.floor((t - bStart) / CANDLE_MS)
      bPrices = []
    }
    bPrices.push(filtered[i].price)
  }
  if (bPrices.length > 0) candles.push(bPrices[bPrices.length - 1])

  return candles
}

export const meta = {
  name: 'volatility_breakout',
  type: 'volatility_breakout',
  description: 'Bollinger squeeze breakout with conservative thresholds and 1-min candles.',
  defaultParams: { squeezePct: 0.50, minHorizon: 1, maxHorizon: 4 },
}
