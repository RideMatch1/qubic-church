'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface LiveQuery {
  oracle: string
  currency1: string
  currency2: string
  status: string
  tick: number
  reply?: { price: number }
  price?: number
  lastUpdated?: string
}

interface LiveData {
  queries: LiveQuery[]
  currentTick?: number
  epoch?: number
}

interface PriceEntry {
  oracle: string
  pair: string
  price: number
  tick: number
  status: string
  timestamp: string
}

const ease = [0.22, 1, 0.36, 1] as const

// All oracle sources we know work (Phase 1+2 discovery, Epoch 200)
const EXCHANGES = ['binance', 'mexc', 'gate', 'gate_mexc', 'binance_mexc', 'binance_gate']
const ASSETS = [
  // Core
  { c1: 'qubic', c2: 'usdt', label: 'QUBIC/USDT' },
  { c1: 'btc', c2: 'usdt', label: 'BTC/USDT' },
  { c1: 'eth', c2: 'usdt', label: 'ETH/USDT' },
  // Major alts
  { c1: 'sol', c2: 'usdt', label: 'SOL/USDT' },
  { c1: 'xrp', c2: 'usdt', label: 'XRP/USDT' },
  { c1: 'bnb', c2: 'usdt', label: 'BNB/USDT' },
  { c1: 'doge', c2: 'usdt', label: 'DOGE/USDT' },
  { c1: 'ada', c2: 'usdt', label: 'ADA/USDT' },
  // Phase 2 discovery
  { c1: 'avax', c2: 'usdt', label: 'AVAX/USDT' },
  { c1: 'link', c2: 'usdt', label: 'LINK/USDT' },
  { c1: 'dot', c2: 'usdt', label: 'DOT/USDT' },
  { c1: 'ltc', c2: 'usdt', label: 'LTC/USDT' },
  { c1: 'sui', c2: 'usdt', label: 'SUI/USDT' },
  { c1: 'near', c2: 'usdt', label: 'NEAR/USDT' },
  { c1: 'trx', c2: 'usdt', label: 'TRX/USDT' },
  { c1: 'atom', c2: 'usdt', label: 'ATOM/USDT' },
  { c1: 'apt', c2: 'usdt', label: 'APT/USDT' },
  { c1: 'zro', c2: 'usdt', label: 'ZRO/USDT' },
  // Cross pairs
  { c1: 'eth', c2: 'btc', label: 'ETH/BTC' },
  { c1: 'sol', c2: 'btc', label: 'SOL/BTC' },
  { c1: 'xrp', c2: 'btc', label: 'XRP/BTC' },
]

export function OraclePriceGrid() {
  const [prices, setPrices] = useState<Map<string, PriceEntry>>(new Map())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState({ total: 0, success: 0, lastUpdated: '' })

  const fetchPrices = useCallback(async () => {
    try {
      const res = await fetch('/api/oracle/live')
      const json = await res.json()
      if (!json.data?.queries) {
        setError(json.message ?? 'No data')
        setLoading(false)
        return
      }

      const queries: LiveQuery[] = json.data.queries
      const priceMap = new Map<string, PriceEntry>()
      let successCount = 0

      for (const q of queries) {
        const p = q.reply?.price ?? q.price
        if (q.status === 'success' && p && p > 0) {
          successCount++
          const key = `${q.oracle}:${q.currency1}/${q.currency2}`
          const existing = priceMap.get(key)
          // Keep the most recent tick
          if (!existing || q.tick > existing.tick) {
            priceMap.set(key, {
              oracle: q.oracle,
              pair: `${q.currency1}/${q.currency2}`,
              price: p,
              tick: q.tick,
              status: q.status,
              timestamp: q.lastUpdated ?? '',
            })
          }
        }
      }

      setPrices(priceMap)
      setStats({
        total: queries.length,
        success: successCount,
        lastUpdated: json.data.scanTimestamp ?? '',
      })
      setError(null)
    } catch {
      setError('Failed to load price data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchPrices()
    const interval = setInterval(fetchPrices, 15000)
    return () => clearInterval(interval)
  }, [fetchPrices])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-5 h-5 border-2 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin" />
      </div>
    )
  }

  if (error || prices.size === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-zinc-500 text-sm">{error ?? 'No price data available'}</p>
        <p className="text-zinc-600 text-xs mt-2 font-mono">
          Run: node scripts/ORACLE_DOMINATOR.mjs --working
        </p>
      </div>
    )
  }

  // Filter to assets that have at least one price
  const activeAssets = ASSETS.filter(a =>
    EXCHANGES.some(ex => prices.has(`${ex}:${a.c1}/${a.c2}`))
  )

  // Filter exchanges that have at least one price
  const activeExchanges = EXCHANGES.filter(ex =>
    ASSETS.some(a => prices.has(`${ex}:${a.c1}/${a.c2}`))
  )

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease }}
    >
      {/* Stats Bar */}
      <div className="flex items-center gap-4 mb-4 flex-wrap">
        <Stat label="QUERIES" value={`${stats.success}/${stats.total}`} color="cyan" />
        <Stat label="PAIRS" value={`${prices.size}`} color="amber" />
        <Stat label="EXCHANGES" value={`${activeExchanges.length}`} color="purple" />
        <Stat label="UPDATED" value={formatTime(stats.lastUpdated)} color="zinc" />
      </div>

      {/* Price Grid */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr>
              <th className="text-left text-[10px] uppercase tracking-[0.2em] text-zinc-500 pb-2 pr-3">Pair</th>
              {activeExchanges.map(ex => (
                <th key={ex} className="text-right text-[10px] uppercase tracking-[0.15em] text-zinc-500 pb-2 px-2">
                  {ex.replace('_', '+')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <AnimatePresence>
              {activeAssets.map((asset, i) => {
                // Compute median for divergence highlighting
                const assetPrices = activeExchanges
                  .map(ex => prices.get(`${ex}:${asset.c1}/${asset.c2}`)?.price)
                  .filter((p): p is number => p != null && p > 0)
                const sorted = assetPrices.sort((a, b) => a - b)
                const median = sorted.length > 0
                  ? (sorted[Math.floor(sorted.length / 2)] ?? 0)
                  : 0

                return (
                  <motion.tr
                    key={`${asset.c1}-${asset.c2}`}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: i * 0.04, ease }}
                    className="border-t border-white/[0.04]"
                  >
                    <td className="py-2 pr-3 font-mono text-zinc-300 whitespace-nowrap text-xs">
                      {asset.label}
                    </td>
                    {activeExchanges.map(ex => {
                      const entry = prices.get(`${ex}:${asset.c1}/${asset.c2}`)
                      if (!entry) {
                        return <td key={ex} className="py-2 px-2 text-right text-zinc-700 font-mono">--</td>
                      }
                      const divergence = median > 0 ? Math.abs((entry.price - median) / median) * 100 : 0
                      const divergenceColor = divergence > 3 ? 'text-red-400' : divergence > 1 ? 'text-amber-400' : 'text-emerald-400'

                      return (
                        <td key={ex} className="py-2 px-2 text-right">
                          <span className={`font-mono ${divergenceColor}`}>
                            {formatPrice(entry.price)}
                          </span>
                        </td>
                      )
                    })}
                  </motion.tr>
                )
              })}
            </AnimatePresence>
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="mt-3 text-[10px] text-zinc-600 font-mono">
        Prices from on-chain oracle replies | Divergence: green &lt;1%, amber 1-3%, red &gt;3%
      </div>
    </motion.div>
  )
}

function formatPrice(p: number): string {
  if (p === 0) return '--'
  if (p < 0.0001) return p.toExponential(2)
  if (p < 0.01) return p.toFixed(6)
  if (p < 10) return p.toFixed(4)
  if (p < 1000) return p.toFixed(2)
  return p.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function Stat({ label, value, color }: { label: string; value: string; color: string }) {
  const colorClasses: Record<string, string> = {
    cyan: 'text-cyan-400',
    amber: 'text-amber-400',
    purple: 'text-purple-400',
    emerald: 'text-emerald-400',
    zinc: 'text-zinc-400',
  }
  return (
    <div className="flex items-center gap-1.5">
      <span className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">{label}</span>
      <span className={`font-mono text-sm ${colorClasses[color] ?? 'text-zinc-400'}`}>{value}</span>
    </div>
  )
}

function formatTime(ts: string | null) {
  if (!ts) return '--'
  const d = new Date(ts)
  const now = Date.now()
  const diff = now - d.getTime()
  if (diff < 60000) return `${Math.round(diff / 1000)}s ago`
  if (diff < 3600000) return `${Math.round(diff / 60000)}m ago`
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
