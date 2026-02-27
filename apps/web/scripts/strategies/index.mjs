/**
 * Strategy Registry
 *
 * All prediction strategies are registered here.
 * Each strategy exports:
 *   evaluate(ctx) -> { direction, threshold, confidence, reason } | null
 *   meta -> { name, type, description, defaultParams }
 *
 * Context (ctx):
 *   { pair, currentPrice, priceHistory: [{price, timestamp, oracle?}], horizonHours, allPrices? }
 */

import * as conservative from './conservative.mjs'
import * as momentum from './momentum.mjs'
import * as meanReversion from './mean-reversion.mjs'
import * as consensus from './consensus.mjs'
import * as volatilityBreakout from './volatility-breakout.mjs'
import * as crossAsset from './cross-asset.mjs'
import * as arbitrageSignal from './arbitrage-signal.mjs'

export const strategies = new Map([
  ['conservative', conservative],
  ['momentum', momentum],
  ['mean_reversion', meanReversion],
  ['consensus', consensus],
  ['volatility_breakout', volatilityBreakout],
  ['cross_asset', crossAsset],
  ['arbitrage_signal', arbitrageSignal],
])

/**
 * Run a single strategy against context.
 * @returns {{ direction, threshold, confidence, reason, strategy } | null}
 */
export function runStrategy(name, ctx) {
  const strat = strategies.get(name)
  if (!strat) return null

  const result = strat.evaluate(ctx)
  if (!result) return null

  return { ...result, strategy: name }
}

/**
 * Run all active strategies against context.
 * @returns {Array<{ direction, threshold, confidence, reason, strategy }>}
 */
export function runAllStrategies(ctx) {
  const results = []
  for (const [name, strat] of strategies) {
    try {
      const result = strat.evaluate(ctx)
      if (result) {
        results.push({ ...result, strategy: name })
      }
    } catch (err) {
      // Skip failing strategies
    }
  }
  return results.sort((a, b) => b.confidence - a.confidence)
}

/**
 * Get metadata for all strategies.
 */
export function getStrategyMetas() {
  const metas = []
  for (const [name, strat] of strategies) {
    metas.push(strat.meta)
  }
  return metas
}
