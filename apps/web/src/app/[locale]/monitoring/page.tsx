'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  Activity,
  RefreshCw,
  Wallet,
  TrendingUp,
  TrendingDown,
  Server,
  Loader2,
  Copy,
  ExternalLink,
  Hash,
  Layers,
  Plus,
  Trash2,
  Eye,
  Clock,
  Zap,
  Calculator,
  ChevronRight,
  Check,
  AlertCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { qubicRPC } from '@/lib/qubic/rpc-client'
import { useQubicNetwork } from '@/components/aigarth-computer/hooks/useQubicNetwork'
import { OracleMonitor, TransactionPanel } from '@/components/monitoring/oracle'

// =============================================================================
// TYPES
// =============================================================================

interface WatchedAddress {
  address: string
  label: string
  balance: string
  lastBalance: string
  lastUpdate: number
}

interface NetworkData {
  price: { usd: number; market_cap: number; volume_24h: number; change_24h: number }
  network: {
    tick: number
    epoch: number
    initial_tick: number
    ticks_in_epoch: number
    empty_ticks: number
    tick_quality: number
    circulating_supply: string
    active_addresses: number
    burned_qus: string
  }
  timestamp: number
}

// =============================================================================
// HOOKS
// =============================================================================

function useMarketData() {
  const [data, setData] = useState<NetworkData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch('/api/mining-stats?type=all')
      if (!res.ok) throw new Error('API error')
      const json = await res.json()
      if (json.error) throw new Error(json.error)
      setData(json)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [fetchData])

  return { data, loading, error, refresh: fetchData }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

const formatNumber = (n: number, decimals = 0) => {
  if (n >= 1e12) return `${(n / 1e12).toFixed(decimals)}T`
  if (n >= 1e9) return `${(n / 1e9).toFixed(decimals)}B`
  if (n >= 1e6) return `${(n / 1e6).toFixed(decimals)}M`
  if (n >= 1e3) return `${(n / 1e3).toFixed(decimals)}K`
  return n.toLocaleString()
}

const formatPrice = (p: number) => {
  if (p === 0) return '$0.00'
  if (p < 0.000001) return `$${p.toExponential(2)}`
  if (p < 0.01) return `$${p.toFixed(6)}`
  return `$${p.toFixed(4)}`
}

// =============================================================================
// COMPONENTS
// =============================================================================

// Status Badge
function StatusBadge({ connected }: { connected: boolean }) {
  return (
    <div className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium ${
      connected ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
    }`}>
      <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-emerald-400' : 'bg-red-400'}`} />
      {connected ? 'Connected' : 'Offline'}
    </div>
  )
}

// Metric Card - Compact, professional
function MetricCard({
  label,
  value,
  subValue,
  change,
  loading,
}: {
  label: string
  value: string | number
  subValue?: string
  change?: number
  loading?: boolean
}) {
  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4">
      <div className="text-xs text-zinc-500 mb-1">{label}</div>
      {loading ? (
        <div className="h-7 flex items-center">
          <Loader2 className="w-4 h-4 animate-spin text-zinc-600" />
        </div>
      ) : (
        <>
          <div className="text-xl font-mono font-semibold text-zinc-100">{value}</div>
          <div className="flex items-center gap-2 mt-1">
            {subValue && <span className="text-xs text-zinc-500">{subValue}</span>}
            {change !== undefined && (
              <span className={`text-xs font-medium flex items-center gap-0.5 ${
                change >= 0 ? 'text-emerald-400' : 'text-red-400'
              }`}>
                {change >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {Math.abs(change).toFixed(2)}%
              </span>
            )}
          </div>
        </>
      )}
    </div>
  )
}

// Price Display with change indicator
function PriceDisplay({ data, loading }: { data: NetworkData | null; loading: boolean }) {
  const change = data?.price.change_24h ?? 0
  const isPositive = change >= 0

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-zinc-400">QUBIC/USD</span>
        <span className="text-xs text-zinc-600">CoinGecko</span>
      </div>

      {loading ? (
        <Loader2 className="w-5 h-5 animate-spin text-zinc-600" />
      ) : (
        <>
          <div className="text-3xl font-mono font-bold text-zinc-100 mb-2">
            {formatPrice(data?.price.usd ?? 0)}
          </div>

          <div className={`inline-flex items-center gap-1 px-2 py-1 rounded text-sm font-medium ${
            isPositive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
          }`}>
            {isPositive ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
            {Math.abs(change).toFixed(2)}% (24h)
          </div>

          <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-zinc-800">
            <div>
              <div className="text-xs text-zinc-500 mb-0.5">Market Cap</div>
              <div className="text-sm font-mono text-zinc-300">
                ${formatNumber(data?.price.market_cap ?? 0, 1)}
              </div>
            </div>
            <div>
              <div className="text-xs text-zinc-500 mb-0.5">24h Volume</div>
              <div className="text-sm font-mono text-zinc-300">
                ${formatNumber(data?.price.volume_24h ?? 0, 1)}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

// Epoch Progress
function EpochProgress({ epoch, tick, ticksInEpoch, initialTick }: {
  epoch: number
  tick: number
  ticksInEpoch?: number
  initialTick?: number
}) {
  // Each epoch is approximately 1 week (~604,800 seconds at ~1 tick/sec average)
  const EXPECTED_TICKS_PER_EPOCH = 604_800
  const actualTicksInEpoch = ticksInEpoch || (tick - (initialTick || 0))

  // Calculate progress based on expected epoch length
  const progress = Math.min((actualTicksInEpoch / EXPECTED_TICKS_PER_EPOCH) * 100, 100)
  const remaining = Math.max(EXPECTED_TICKS_PER_EPOCH - actualTicksInEpoch, 0)

  // Estimate time based on ~1 tick per second average
  const secondsRemaining = remaining
  const hoursRemaining = secondsRemaining / 3600
  const daysRemaining = hoursRemaining / 24

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-zinc-400">Epoch {epoch}</span>
        <span className="text-xs text-zinc-500">{progress.toFixed(1)}% complete</span>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-zinc-800 rounded-full overflow-hidden mb-4">
        <div
          className="h-full bg-gradient-to-r from-zinc-600 to-zinc-500 transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="grid grid-cols-3 gap-4 text-sm">
        <div>
          <div className="text-xs text-zinc-500 mb-0.5">Ticks Done</div>
          <div className="font-mono text-zinc-300">{formatNumber(actualTicksInEpoch)}</div>
        </div>
        <div>
          <div className="text-xs text-zinc-500 mb-0.5">Remaining</div>
          <div className="font-mono text-zinc-300">{formatNumber(remaining)}</div>
        </div>
        <div>
          <div className="text-xs text-zinc-500 mb-0.5">Est. Time</div>
          <div className="font-mono text-zinc-300">
            {daysRemaining > 1 ? `~${daysRemaining.toFixed(1)}d` : `~${hoursRemaining.toFixed(0)}h`}
          </div>
        </div>
      </div>
    </div>
  )
}

// Profitability Calculator
function ProfitabilityCalculator({ price }: { price: number }) {
  const [hashrate, setHashrate] = useState('')
  const [result, setResult] = useState<{ daily: number; weekly: number; monthly: number } | null>(null)

  const calculate = useCallback(() => {
    const hr = parseFloat(hashrate)
    if (isNaN(hr) || hr <= 0 || price <= 0) {
      setResult(null)
      return
    }

    // Rough estimation based on network stats
    // These are approximations - actual rewards depend on many factors
    const DAILY_EMISSION = 1_000_000_000_000 / 7 // ~143B per day
    const NETWORK_HASHRATE = 500_000_000 // Estimated network hashrate
    const yourShare = hr / NETWORK_HASHRATE
    const dailyQubic = DAILY_EMISSION * yourShare
    const dailyUsd = dailyQubic * price

    setResult({
      daily: dailyUsd,
      weekly: dailyUsd * 7,
      monthly: dailyUsd * 30,
    })
  }, [hashrate, price])

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5">
      <div className="flex items-center gap-2 mb-4">
        <Calculator className="w-4 h-4 text-zinc-500" />
        <span className="text-sm font-medium text-zinc-300">Mining Calculator</span>
        <span className="text-xs text-zinc-600 ml-auto">Estimate</span>
      </div>

      <div className="flex gap-2 mb-4">
        <Input
          type="number"
          placeholder="Your hashrate (It/s)"
          value={hashrate}
          onChange={(e) => setHashrate(e.target.value)}
          className="bg-zinc-800 border-zinc-700 text-zinc-200 text-sm"
        />
        <Button
          onClick={calculate}
          className="bg-zinc-700 hover:bg-zinc-600 text-zinc-200"
          size="sm"
        >
          Calculate
        </Button>
      </div>

      {result && (
        <div className="grid grid-cols-3 gap-3 p-3 bg-zinc-800/50 rounded-lg">
          <div className="text-center">
            <div className="text-xs text-zinc-500">Daily</div>
            <div className="text-sm font-mono text-emerald-400">${result.daily.toFixed(2)}</div>
          </div>
          <div className="text-center border-x border-zinc-700">
            <div className="text-xs text-zinc-500">Weekly</div>
            <div className="text-sm font-mono text-emerald-400">${result.weekly.toFixed(2)}</div>
          </div>
          <div className="text-center">
            <div className="text-xs text-zinc-500">Monthly</div>
            <div className="text-sm font-mono text-emerald-400">${result.monthly.toFixed(2)}</div>
          </div>
        </div>
      )}

      <p className="text-[10px] text-zinc-600 mt-3">
        * Estimates only. Actual earnings depend on network conditions, pool fees, and luck.
      </p>
    </div>
  )
}

// Address Watchlist - Compact version
function AddressWatchlist() {
  const [addresses, setAddresses] = useState<WatchedAddress[]>([])
  const [newAddress, setNewAddress] = useState('')
  const [isAdding, setIsAdding] = useState(false)
  const [copied, setCopied] = useState<string | null>(null)

  useEffect(() => {
    const saved = localStorage.getItem('qubic-watchlist')
    if (saved) {
      try { setAddresses(JSON.parse(saved)) } catch { /* ignore */ }
    }
  }, [])

  useEffect(() => {
    if (addresses.length > 0) {
      localStorage.setItem('qubic-watchlist', JSON.stringify(addresses))
    }
  }, [addresses])

  const addAddress = async () => {
    if (!newAddress.trim() || newAddress.length < 50) return
    const addr = newAddress.trim().toUpperCase()
    if (addresses.some((a) => a.address === addr)) return

    setIsAdding(true)
    try {
      const balance = await qubicRPC.getBalance(addr)
      setAddresses((prev) => [...prev, {
        address: addr,
        label: `Wallet ${prev.length + 1}`,
        balance: balance.toString(),
        lastBalance: balance.toString(),
        lastUpdate: Date.now(),
      }])
      setNewAddress('')
    } catch { /* ignore */ }
    setIsAdding(false)
  }

  const copyAddress = (addr: string) => {
    navigator.clipboard.writeText(addr)
    setCopied(addr)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Eye className="w-4 h-4 text-zinc-500" />
          <span className="text-sm font-medium text-zinc-300">Watchlist</span>
        </div>
        <span className="text-xs text-zinc-600">{addresses.length} addresses</span>
      </div>

      <div className="flex gap-2 mb-4">
        <Input
          placeholder="Add Qubic address..."
          value={newAddress}
          onChange={(e) => setNewAddress(e.target.value.toUpperCase())}
          onKeyDown={(e) => e.key === 'Enter' && addAddress()}
          className="bg-zinc-800 border-zinc-700 text-zinc-200 text-xs font-mono"
        />
        <Button
          onClick={addAddress}
          disabled={isAdding}
          size="sm"
          className="bg-zinc-700 hover:bg-zinc-600"
        >
          {isAdding ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
        </Button>
      </div>

      <div className="space-y-2 max-h-[200px] overflow-y-auto">
        {addresses.length === 0 ? (
          <div className="text-center py-6 text-zinc-600 text-sm">
            No addresses watched
          </div>
        ) : (
          addresses.map((addr) => (
            <div key={addr.address} className="flex items-center gap-2 p-2 bg-zinc-800/50 rounded group">
              <div className="flex-1 min-w-0">
                <code className="text-xs text-zinc-400 font-mono block truncate">
                  {addr.address.slice(0, 15)}...{addr.address.slice(-8)}
                </code>
              </div>
              <div className="text-sm font-mono text-zinc-200">
                {formatNumber(Number(addr.balance))}
              </div>
              <button
                onClick={() => copyAddress(addr.address)}
                className="p-1 hover:bg-zinc-700 rounded opacity-0 group-hover:opacity-100 transition-opacity"
              >
                {copied === addr.address ? (
                  <Check className="w-3 h-3 text-emerald-400" />
                ) : (
                  <Copy className="w-3 h-3 text-zinc-500" />
                )}
              </button>
              <button
                onClick={() => setAddresses((p) => p.filter((a) => a.address !== addr.address))}
                className="p-1 hover:bg-zinc-700 rounded opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <Trash2 className="w-3 h-3 text-zinc-500" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

// Quick Balance Check
function QuickBalanceCheck() {
  const [address, setAddress] = useState('')
  const [result, setResult] = useState<{ balance: string; address: string } | null>(null)
  const [loading, setLoading] = useState(false)

  const checkBalance = async () => {
    if (!address.trim() || address.length < 50) return
    setLoading(true)
    try {
      const balance = await qubicRPC.getBalance(address.trim().toUpperCase())
      setResult({ balance: balance.toString(), address: address.trim().toUpperCase() })
    } catch {
      setResult(null)
    }
    setLoading(false)
  }

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5">
      <div className="flex items-center gap-2 mb-4">
        <Wallet className="w-4 h-4 text-zinc-500" />
        <span className="text-sm font-medium text-zinc-300">Balance Check</span>
      </div>

      <div className="flex gap-2 mb-3">
        <Input
          placeholder="Enter address..."
          value={address}
          onChange={(e) => setAddress(e.target.value.toUpperCase())}
          onKeyDown={(e) => e.key === 'Enter' && checkBalance()}
          className="bg-zinc-800 border-zinc-700 text-zinc-200 text-xs font-mono"
        />
        <Button
          onClick={checkBalance}
          disabled={loading}
          size="sm"
          className="bg-zinc-700 hover:bg-zinc-600"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ChevronRight className="w-4 h-4" />}
        </Button>
      </div>

      {result && (
        <div className="p-3 bg-zinc-800/50 rounded-lg">
          <div className="text-xs text-zinc-500 mb-1">Balance</div>
          <div className="text-2xl font-mono font-bold text-zinc-100">
            {Number(result.balance).toLocaleString()}
            <span className="text-sm text-zinc-500 ml-2">QUBIC</span>
          </div>
        </div>
      )}
    </div>
  )
}

// Network Stats Grid - Comprehensive view
function NetworkStatsGrid({ data, rpcData, loading }: {
  data: NetworkData | null
  rpcData: { tick: number; epoch: number } | null
  loading: boolean
}) {
  const tickQuality = data?.network.tick_quality ?? 0
  const qualityColor = tickQuality > 95 ? 'text-emerald-400' : tickQuality > 90 ? 'text-yellow-400' : 'text-red-400'

  return (
    <div className="space-y-4">
      {/* Primary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard
          label="Current Tick"
          value={rpcData?.tick?.toLocaleString() ?? data?.network.tick?.toLocaleString() ?? '—'}
          subValue="Live RPC"
          loading={loading}
        />
        <MetricCard
          label="Epoch"
          value={rpcData?.epoch ?? data?.network.epoch ?? '—'}
          subValue={data?.network.initial_tick ? `Start: ${data.network.initial_tick.toLocaleString()}` : undefined}
          loading={loading}
        />
        <MetricCard
          label="Active Addresses"
          value={data?.network.active_addresses ? formatNumber(data.network.active_addresses) : '—'}
          loading={loading}
        />
        <MetricCard
          label="Circulating Supply"
          value={data?.network.circulating_supply ? `${formatNumber(Number(data.network.circulating_supply))}` : '—'}
          subValue="QUBIC"
          loading={loading}
        />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard
          label="Ticks in Epoch"
          value={data?.network.ticks_in_epoch?.toLocaleString() ?? '—'}
          loading={loading}
        />
        <MetricCard
          label="Empty Ticks"
          value={data?.network.empty_ticks?.toLocaleString() ?? '—'}
          subValue={`${((data?.network.empty_ticks ?? 0) / (data?.network.ticks_in_epoch || 1) * 100).toFixed(1)}% of epoch`}
          loading={loading}
        />
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4">
          <div className="text-xs text-zinc-500 mb-1">Tick Quality</div>
          {loading ? (
            <div className="h-7 flex items-center">
              <Loader2 className="w-4 h-4 animate-spin text-zinc-600" />
            </div>
          ) : (
            <>
              <div className={`text-xl font-mono font-semibold ${qualityColor}`}>
                {tickQuality.toFixed(2)}%
              </div>
              <div className="h-1.5 bg-zinc-800 rounded-full mt-2 overflow-hidden">
                <div
                  className={`h-full ${tickQuality > 95 ? 'bg-emerald-500' : tickQuality > 90 ? 'bg-yellow-500' : 'bg-red-500'}`}
                  style={{ width: `${tickQuality}%` }}
                />
              </div>
            </>
          )}
        </div>
        <MetricCard
          label="Burned QUs"
          value={data?.network.burned_qus ? formatNumber(Number(data.network.burned_qus)) : '—'}
          subValue="Permanently removed"
          loading={loading}
        />
      </div>
    </div>
  )
}

// =============================================================================
// MAIN PAGE
// =============================================================================

export default function MonitoringPage() {
  const { isConnected, isLoading: rpcLoading, epoch, refresh: refreshRpc } = useQubicNetwork(undefined, true)
  const { data: marketData, loading: marketLoading, refresh: refreshMarket } = useMarketData()
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const handleRefresh = async () => {
    await Promise.all([refreshRpc(), refreshMarket()])
    setLastUpdate(new Date())
  }

  useEffect(() => {
    setLastUpdate(new Date())
  }, [marketData])

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-zinc-400" />
                <h1 className="text-lg font-semibold text-zinc-100">Network Monitor</h1>
              </div>
              <StatusBadge connected={isConnected} />
            </div>

            <div className="flex items-center gap-4">
              {lastUpdate && (
                <span className="text-xs text-zinc-600">
                  Updated {lastUpdate.toLocaleTimeString()}
                </span>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={rpcLoading || marketLoading}
                className="border-zinc-700 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${(rpcLoading || marketLoading) ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Network Stats Row */}
        <section className="mb-6">
          <NetworkStatsGrid
            data={marketData}
            rpcData={epoch}
            loading={rpcLoading || marketLoading}
          />
        </section>

        {/* Oracle Machine Monitor */}
        <section className="mb-6">
          <OracleMonitor
            tick={epoch?.tick ?? marketData?.network.tick ?? 0}
            epoch={epoch?.epoch ?? marketData?.network.epoch ?? 0}
            loading={rpcLoading || marketLoading}
          />
        </section>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Price & Epoch */}
          <div className="space-y-6">
            <PriceDisplay data={marketData} loading={marketLoading} />
            {(epoch || marketData) && (
              <EpochProgress
                epoch={epoch?.epoch ?? marketData?.network.epoch ?? 0}
                tick={epoch?.tick ?? marketData?.network.tick ?? 0}
                ticksInEpoch={marketData?.network.ticks_in_epoch}
                initialTick={marketData?.network.initial_tick}
              />
            )}
          </div>

          {/* Middle Column - Tools */}
          <div className="space-y-6">
            <TransactionPanel />
            <QuickBalanceCheck />
            <ProfitabilityCalculator price={marketData?.price.usd ?? 0} />
          </div>

          {/* Right Column - Watchlist */}
          <div className="space-y-6">
            <AddressWatchlist />

            {/* Quick Links */}
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5">
              <div className="text-sm font-medium text-zinc-300 mb-3">Quick Links</div>
              <div className="space-y-2">
                {[
                  { label: 'Qubic Explorer', url: 'https://explorer.qubic.org' },
                  { label: 'Qubic.li Stats', url: 'https://app.qubic.li' },
                  { label: 'Official Wallet', url: 'https://wallet.qubic.org' },
                  { label: 'CoinGecko', url: 'https://www.coingecko.com/en/coins/qubic-network' },
                ].map((link) => (
                  <a
                    key={link.url}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between p-2 rounded bg-zinc-800/50 hover:bg-zinc-800 transition-colors group"
                  >
                    <span className="text-sm text-zinc-400 group-hover:text-zinc-200">{link.label}</span>
                    <ExternalLink className="w-3.5 h-3.5 text-zinc-600 group-hover:text-zinc-400" />
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Footer Info */}
        <footer className="mt-8 pt-6 border-t border-zinc-800">
          <div className="flex items-center justify-between text-xs text-zinc-600">
            <div className="flex items-center gap-4">
              <span>Data: CoinGecko, Qubic.li, RPC</span>
              <span>Auto-refresh: 30s</span>
            </div>
            <span>Watchlist saved locally</span>
          </div>
        </footer>
      </main>
    </div>
  )
}
