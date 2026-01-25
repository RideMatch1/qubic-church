'use client'

import { useState, useEffect, useCallback } from 'react'

// =============================================================================
// TYPES
// =============================================================================

export interface MiningPool {
  url: string
  pool_id: string
  hashrate: number
  miners: number
  workers: number
  fee: number
  feetype?: string
  country: string
  hashrate_average_7d: number
}

export interface MiningStats {
  // Network info
  height: number
  time: number
  symbol: string
  algo: string
  unit: string
  block_time_average: number
  block_time_target: number

  // Hashrate
  hashrate: number
  maxhash: number
  poolshash: number
  nethash_estimat: number

  // Pool summary
  poolsminers: number
  data: MiningPool[]

  // Supply
  supply: {
    circulating: number
    total: number
    emission24: number
  }

  // Price (from merged data)
  price: number

  // Release info
  latest_release?: {
    tag: string
    name: string
    t: number
  }

  // Fallback indicator
  _fallback?: boolean
  _source?: string
}

export interface PriceStats {
  price_USD: number
  market_cap: number
  volume_24: number
  change_7d: number
  circulating: number
  total_supply: number
  price_7d: number[]
}

export interface UseMiningStatsReturn {
  stats: MiningStats | null
  price: PriceStats | null
  pools: MiningPool[]
  isLoading: boolean
  error: string | null
  lastUpdate: number | null
  dataSource: 'miningpoolstats' | 'qubic.li' | null
  refresh: () => Promise<void>
}

// =============================================================================
// HOOK
// =============================================================================

export function useMiningStats(autoRefresh = true, refreshInterval = 30000): UseMiningStatsReturn {
  const [stats, setStats] = useState<MiningStats | null>(null)
  const [price, setPrice] = useState<PriceStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<number | null>(null)
  const [dataSource, setDataSource] = useState<'miningpoolstats' | 'qubic.li' | null>(null)

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Fetch both endpoints in parallel
      const [statsRes, priceRes] = await Promise.all([
        fetch('/api/mining-stats?type=stats'),
        fetch('/api/mining-stats?type=price'),
      ])

      if (!statsRes.ok) {
        throw new Error('Failed to fetch mining stats')
      }

      const statsData = await statsRes.json()
      const priceData = priceRes.ok ? await priceRes.json() : null

      if (statsData.error) {
        throw new Error(statsData.error)
      }

      setStats(statsData)
      setPrice(priceData?.error ? null : priceData)
      setDataSource(statsData._fallback ? 'qubic.li' : 'miningpoolstats')
      setLastUpdate(Date.now())
    } catch (err) {
      console.error('Mining stats error:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
      setDataSource(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Initial fetch
  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(fetchData, refreshInterval)
    return () => clearInterval(interval)
  }, [autoRefresh, refreshInterval, fetchData])

  // Extract pools sorted by hashrate
  const pools = stats?.data
    ?.filter((p) => p.hashrate > 0 || p.miners > 0)
    ?.sort((a, b) => b.hashrate - a.hashrate) ?? []

  return {
    stats,
    price,
    pools,
    isLoading,
    error,
    dataSource,
    lastUpdate,
    refresh: fetchData,
  }
}
