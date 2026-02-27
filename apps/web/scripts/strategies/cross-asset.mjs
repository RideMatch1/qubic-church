/**
 * CROSS-ASSET Strategy v2
 *
 * BTC leads altcoins with a lag of 5-30 minutes.
 * Uses CONSERVATIVE thresholds.
 *
 * v2 fix (0% → target 65%+):
 * - v1 set threshold in direction of expected catch-up (above current for UP)
 * - v2 sets threshold BELOW current for UP, ABOVE for DOWN
 * - Margin width based on lag magnitude and BTC move strength
 * - Downsample BTC and altcoin to 1-min candles for cleaner ROC
 * - Also look at 30-min BTC move (not just 15min) for longer horizons
 *
 * @param {Object} ctx
 * @param {string} ctx.pair
 * @param {number} ctx.currentPrice
 * @param {Array}  ctx.priceHistory - [{price, timestamp, oracle}] sorted desc (newest first)
 * @param {number} ctx.horizonHours
 * @param {Object} [ctx.allPrices] - Optional: { 'btc/usdt': [{price, timestamp}], ... }
 * @returns {{ direction, threshold, confidence, reason } | null}
 */
export function evaluate(ctx) {
  const { pair, currentPrice, priceHistory, horizonHours, allPrices } = ctx

  if (!currentPrice || currentPrice <= 0) return null
  if (priceHistory.length < 10) return null
  if (horizonHours < 1 || horizonHours > 4) return null

  // Only apply to altcoin/usdt pairs
  if (pair === 'btc/usdt' || pair === 'eth/btc') return null
  if (!pair.endsWith('/usdt')) return null

  const now = new Date(priceHistory[0].timestamp).getTime()
  if (isNaN(now)) return null

  // --- Get BTC price history ---
  let btcHistory = null
  if (allPrices && allPrices['btc/usdt']) {
    btcHistory = allPrices['btc/usdt']
  }
  if (!btcHistory || btcHistory.length < 10) return null

  // --- Lookback: 15min for 1h horizon, 30min for 2h+ ---
  const lookbackMs = (horizonHours <= 1 ? 15 : 30) * 60 * 1000
  const btcCutoff = now - lookbackMs

  // --- Downsample BTC to 1-min candles ---
  const btcCandles = downsampleToCandles(btcHistory, btcCutoff)
  if (btcCandles.length < 5) return null

  const btcRoc = (btcCandles[btcCandles.length - 1] - btcCandles[0]) / btcCandles[0]

  // Need meaningful BTC move
  const MIN_BTC_MOVE = 0.0015 // 0.15%
  if (Math.abs(btcRoc) < MIN_BTC_MOVE) return null

  // --- Downsample altcoin to 1-min candles ---
  const altCandles = downsampleToCandles(priceHistory, btcCutoff)
  if (altCandles.length < 5) return null

  const altRoc = (altCandles[altCandles.length - 1] - altCandles[0]) / altCandles[0]

  // --- Calculate lag ---
  const beta = getBeta(pair)
  const expectedMove = btcRoc * beta
  const lag = expectedMove - altRoc

  // Need meaningful lag
  const MIN_LAG = 0.001 // 0.1%
  if (Math.abs(lag) < MIN_LAG) return null

  // Reject if altcoin already overshot
  if (btcRoc > 0 && altRoc > expectedMove) return null
  if (btcRoc < 0 && altRoc < expectedMove) return null

  // --- Calculate altcoin volatility for margin ---
  const altReturns = []
  for (let i = 1; i < altCandles.length; i++) {
    altReturns.push((altCandles[i] - altCandles[i - 1]) / altCandles[i - 1])
  }
  const minVol = Math.sqrt(altReturns.reduce((a, r) => a + r ** 2, 0) / altReturns.length)
  const horizonVol = minVol * Math.sqrt(60) * Math.sqrt(horizonHours)

  if (horizonVol === 0 || isNaN(horizonVol)) return null

  // --- Build prediction with conservative threshold ---
  const direction = lag > 0 ? 'up' : 'down'

  // Margin: 0.5x horizon vol (cross-asset is a moderate signal)
  let margin = horizonVol * 0.5
  // Lag strength boosts margin (more confident about direction)
  const lagBoost = Math.min(Math.abs(lag) * 15, 0.4)
  margin *= (1 + lagBoost)
  margin = Math.max(0.002, Math.min(margin, 0.035))

  const threshold = direction === 'up'
    ? currentPrice * (1 - margin)    // threshold BELOW current
    : currentPrice * (1 + margin * 0.8) // threshold ABOVE current

  // Sanity
  if (direction === 'up' && threshold > currentPrice) return null
  if (direction === 'down' && threshold < currentPrice) return null
  if (threshold <= 0) return null

  // Confidence
  const btcStrength = Math.min(Math.abs(btcRoc) * 80, 0.15)
  const lagStrength = Math.min(Math.abs(lag) * 40, 0.15)
  const confidence = Math.min(0.75, 0.35 + btcStrength + lagStrength)

  return {
    direction,
    threshold: Number(threshold.toPrecision(8)),
    confidence: Number(confidence.toFixed(3)),
    reason: `CrossAsset ${direction.toUpperCase()}: BTC=${(btcRoc * 100).toFixed(2)}%, ${pair.split('/')[0].toUpperCase()}=${(altRoc * 100).toFixed(2)}%, lag=${(lag * 100).toFixed(2)}%, beta=${beta}, margin=${(margin * 100).toFixed(2)}%`,
  }
}

/**
 * Downsample price history to 1-min candle close prices.
 * @param {Array} history - [{price, timestamp}] sorted desc
 * @param {number} cutoff - timestamp cutoff
 * @returns {number[]} - close prices ordered oldest→newest
 */
function downsampleToCandles(history, cutoff) {
  const filtered = history.filter(p => {
    const t = new Date(p.timestamp).getTime()
    return !isNaN(t) && t >= cutoff
  })
  if (filtered.length < 3) return []

  const CANDLE_MS = 60 * 1000
  const candles = []
  // Iterate oldest first
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

function getBeta(pair) {
  const betas = {
    'eth/usdt':   0.85,
    'sol/usdt':   1.20,
    'xrp/usdt':   0.90,
    'bnb/usdt':   0.75,
    'doge/usdt':  1.30,
    'ada/usdt':   1.10,
    'avax/usdt':  1.15,
    'link/usdt':  1.05,
    'dot/usdt':   1.10,
    'ltc/usdt':   0.85,
    'sui/usdt':   1.25,
    'near/usdt':  1.15,
    'trx/usdt':   0.70,
    'atom/usdt':  1.00,
    'apt/usdt':   1.20,
    'qubic/usdt': 1.50,
  }
  return betas[pair] || 1.0
}

export const meta = {
  name: 'cross_asset',
  type: 'cross_asset',
  description: 'BTC lead-lag with conservative thresholds and 1-min candle downsampling.',
  defaultParams: { minBtcMove: 0.0025, minLag: 0.0015, maxHorizon: 4 },
}
