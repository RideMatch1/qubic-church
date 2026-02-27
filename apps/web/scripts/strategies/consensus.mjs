/**
 * CONSENSUS Strategy v3
 *
 * Multi-source oracle divergence with CONSERVATIVE thresholds.
 *
 * v3 fix (0% → target 65%+):
 * - v2 set threshold in direction of expected convergence (above current for UP)
 * - v3 sets threshold BELOW current for UP, ABOVE current for DOWN
 * - The signal quality determines the margin width
 * - Stronger divergence = wider margin (more confident about direction)
 * - Requires at least 2 oracle sources with meaningful divergence
 *
 * @param {Object} ctx
 * @param {string} ctx.pair
 * @param {number} ctx.currentPrice
 * @param {Array}  ctx.priceHistory - [{price, timestamp, oracle}] sorted desc (newest first)
 * @param {number} ctx.horizonHours
 * @returns {{ direction, threshold, confidence, reason } | null}
 */
export function evaluate(ctx) {
  const { currentPrice, priceHistory, horizonHours } = ctx

  if (!currentPrice || currentPrice <= 0) return null
  if (priceHistory.length < 10) return null
  if (horizonHours > 8) return null

  // --- Timestamp normalization: only use prices from last 5 minutes ---
  const now = new Date(priceHistory[0].timestamp).getTime()
  if (isNaN(now)) return null
  const syncWindow = 5 * 60 * 1000
  const cutoff = now - syncWindow

  const recentPrices = priceHistory.filter(p => {
    const t = new Date(p.timestamp).getTime()
    return !isNaN(t) && t >= cutoff && p.oracle
  })

  if (recentPrices.length < 3) return null

  // --- Group by oracle source, take LATEST price per source ---
  const byOracle = new Map()
  for (const p of recentPrices) {
    const src = p.oracle
    if (!byOracle.has(src)) {
      byOracle.set(src, {
        price: p.price,
        timestamp: new Date(p.timestamp).getTime(),
        count: 1,
      })
    } else {
      byOracle.get(src).count++
    }
  }

  const sources = [...byOracle.entries()]
  if (sources.length < 2) return null

  // --- Calculate recency-weighted consensus mean ---
  let weightedSum = 0
  let weightTotal = 0

  for (const [, data] of sources) {
    const age = now - data.timestamp
    const recencyWeight = Math.max(0.1, 1 - age / syncWindow)
    const dataWeight = Math.min(data.count / 3, 1.5)
    const weight = recencyWeight * dataWeight
    weightedSum += data.price * weight
    weightTotal += weight
  }

  const consensusMean = weightedSum / weightTotal

  // --- Calculate volatility for dynamic thresholds ---
  const volWindowMs = 60 * 60 * 1000 // 1 hour
  const volCutoff = now - volWindowMs
  const volPrices = priceHistory.filter(p => {
    const t = new Date(p.timestamp).getTime()
    return !isNaN(t) && t >= volCutoff
  }).map(p => p.price)

  if (volPrices.length < 10) return null

  const mean = volPrices.reduce((a, b) => a + b, 0) / volPrices.length
  const variance = volPrices.reduce((a, p) => a + (p - mean) ** 2, 0) / volPrices.length
  const stdDev = Math.sqrt(variance)
  const relVol = stdDev / mean

  if (relVol === 0 || isNaN(relVol)) return null

  // --- Calculate divergence across sources ---
  const oraclePrices = sources.map(([, d]) => d.price)
  const maxPrice = Math.max(...oraclePrices)
  const minPrice = Math.min(...oraclePrices)
  const divergencePct = (maxPrice - minPrice) / consensusMean

  // Dynamic threshold: divergence must exceed 0.4x recent volatility
  const minDivergence = Math.max(0.0015, relVol * 0.4)
  if (divergencePct < minDivergence) return null

  // --- Current price deviation from consensus ---
  const deviation = (currentPrice - consensusMean) / consensusMean
  const deviationThreshold = Math.max(0.0008, relVol * 0.2)

  if (Math.abs(deviation) < deviationThreshold) return null

  // --- Calculate horizon-scaled volatility for margin ---
  // Downsample to 1-min returns for proper vol
  const CANDLE_MS = 60 * 1000
  const candles = []
  const sorted = [...priceHistory.filter(p => {
    const t = new Date(p.timestamp).getTime()
    return !isNaN(t) && t >= volCutoff
  })].reverse() // oldest first

  if (sorted.length < 10) return null

  let bStart = new Date(sorted[0].timestamp).getTime()
  let bPrices = []
  for (const p of sorted) {
    const t = new Date(p.timestamp).getTime()
    if (t >= bStart + CANDLE_MS && bPrices.length > 0) {
      candles.push(bPrices[bPrices.length - 1])
      bStart += CANDLE_MS * Math.floor((t - bStart) / CANDLE_MS)
      bPrices = []
    }
    bPrices.push(p.price)
  }
  if (bPrices.length > 0) candles.push(bPrices[bPrices.length - 1])

  let horizonVol = relVol * Math.sqrt(horizonHours) // fallback
  if (candles.length >= 5) {
    const rets = []
    for (let i = 1; i < candles.length; i++) {
      rets.push((candles[i] - candles[i - 1]) / candles[i - 1])
    }
    const mv = Math.sqrt(rets.reduce((a, r) => a + r ** 2, 0) / rets.length)
    horizonVol = mv * Math.sqrt(60) * Math.sqrt(horizonHours)
  }

  // --- Build signal with conservative threshold ---
  const divergenceStrength = divergencePct / relVol
  const baseConf = 0.38 + Math.min(divergenceStrength * 0.12, 0.20)
  const sourceBoost = Math.min((sources.length - 2) * 0.04, 0.08)
  const confidence = Math.min(0.78, baseConf + sourceBoost)

  // Margin: 0.5x horizon vol (consensus is a weaker signal, so smaller margin)
  let margin = horizonVol * 0.5
  margin = Math.max(0.002, Math.min(margin, 0.035))

  if (deviation > deviationThreshold) {
    // Price ABOVE consensus → predict DOWN, threshold ABOVE current
    const threshold = currentPrice * (1 + margin * 0.8)

    if (threshold < currentPrice) return null // sanity

    return {
      direction: 'down',
      threshold: Number(threshold.toPrecision(8)),
      confidence: Number(confidence.toFixed(3)),
      reason: `Consensus DOWN: ${sources.length}src, div=${(divergencePct * 100).toFixed(2)}%, dev=${(deviation * 100).toFixed(2)}%, margin=${(margin * 100).toFixed(2)}%`,
    }
  }

  if (deviation < -deviationThreshold) {
    // Price BELOW consensus → predict UP, threshold BELOW current
    const threshold = currentPrice * (1 - margin)

    if (threshold > currentPrice) return null // sanity
    if (threshold <= 0) return null

    return {
      direction: 'up',
      threshold: Number(threshold.toPrecision(8)),
      confidence: Number(confidence.toFixed(3)),
      reason: `Consensus UP: ${sources.length}src, div=${(divergencePct * 100).toFixed(2)}%, dev=${(Math.abs(deviation) * 100).toFixed(2)}%, margin=${(margin * 100).toFixed(2)}%`,
    }
  }

  return null
}

export const meta = {
  name: 'consensus',
  type: 'consensus',
  description: 'Multi-source oracle divergence with conservative thresholds and vol-scaled margins.',
  defaultParams: { syncWindowMin: 5, minSources: 2, maxHorizon: 8 },
}
