'use client'

/**
 * MetricsDashboard Component
 * Live metrics from Qubic blockchain and NFT marketplace
 */

import { MetricsCard } from './MetricsCard'
import {
  useEpochData,
  useNetworkStatus,
  useEmissionRate,
  useCommunityStats,
} from '@/lib/hooks'
import {
  Clock,
  Activity,
  Coins,
  Users,
  Calendar,
  Zap,
  TrendingUp,
  Award,
} from 'lucide-react'

/**
 * Format large numbers with abbreviations
 */
function formatNumber(num: number | bigint): string {
  const n = typeof num === 'bigint' ? Number(num) : num

  if (n >= 1_000_000_000) {
    return `${(n / 1_000_000_000).toFixed(2)}B`
  }
  if (n >= 1_000_000) {
    return `${(n / 1_000_000).toFixed(2)}M`
  }
  if (n >= 1_000) {
    return `${(n / 1_000).toFixed(2)}K`
  }
  return n.toFixed(0)
}

/**
 * Calculate time until next event
 */
function formatTimeUntil(date: Date): string {
  const now = Date.now()
  const target = date.getTime()
  const diff = target - now

  if (diff <= 0) return 'Now'

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))

  if (days > 0) return `${days}d ${hours}h`
  return `${hours}h`
}

export function MetricsDashboard() {
  const { epoch, error: epochError, isLoading: epochLoading } = useEpochData()
  const {
    status,
    error: statusError,
    isLoading: statusLoading,
  } = useNetworkStatus()
  const {
    emission,
    error: emissionError,
    isLoading: emissionLoading,
  } = useEmissionRate()
  const {
    stats,
    error: statsError,
    isLoading: statsLoading,
  } = useCommunityStats()

  return (
    <section className="w-full py-16 bg-gradient-to-b from-muted/30 to-background">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-12 space-y-4">
          <h2 className="text-3xl md:text-4xl font-bold">Live Qubic Metrics</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Real-time data from the Qubic blockchain and Anna NFT collection
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Current Epoch */}
          <MetricsCard
            title="Current Epoch"
            value={epoch ? `#${epoch.epoch}` : '—'}
            subtitle={
              epoch
                ? `Next epoch in ${formatTimeUntil(new Date(epoch.timestamp + epoch.nextEpochIn))}`
                : undefined
            }
            icon={<Calendar className="w-5 h-5" />}
            loading={epochLoading}
            error={!!epochError}
            trend="neutral"
          />

          {/* Network Status */}
          <MetricsCard
            title="Network Status"
            value={status ? `${status.tps} TPS` : '—'}
            subtitle={
              status ? `Tick rate: ${status.tickRate}/s` : undefined
            }
            icon={<Activity className="w-5 h-5" />}
            status={status?.health}
            loading={statusLoading}
            error={!!statusError}
          />

          {/* Current Emission */}
          <MetricsCard
            title="Epoch Emission"
            value={
              emission ? `${formatNumber(emission.baseEmission)} QUBIC` : '—'
            }
            subtitle={
              emission
                ? `Halving in ${emission.nextHalving.epochsUntil} epochs`
                : undefined
            }
            icon={<Coins className="w-5 h-5" />}
            loading={emissionLoading}
            error={!!emissionError}
            trend="down"
          />

          {/* Community Stats */}
          <MetricsCard
            title="NFT Collection"
            value={stats ? `${stats.holders} Holders` : '—'}
            subtitle={
              stats
                ? `Floor: ${stats.floorPrice} QUBIC | ${stats.totalNFTs} total`
                : undefined
            }
            icon={<Users className="w-5 h-5" />}
            loading={statsLoading}
            error={!!statsError}
            trend="up"
          />
        </div>

        {/* Additional Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          {/* Next Halving Countdown */}
          {emission && (
            <MetricsCard
              title="Next Halving"
              value={formatTimeUntil(emission.nextHalving.timeEstimate)}
              subtitle={`Epoch ${emission.nextHalving.epoch}`}
              icon={<Clock className="w-5 h-5" />}
              loading={emissionLoading}
              error={!!emissionError}
            />
          )}

          {/* 24h Volume */}
          {stats && (
            <MetricsCard
              title="24h Volume"
              value={`${formatNumber(stats.volume24h)} QUBIC`}
              subtitle={`${stats.totalTrades} total trades`}
              icon={<TrendingUp className="w-5 h-5" />}
              loading={statsLoading}
              error={!!statsError}
              status="good"
            />
          )}

          {/* Collection Progress */}
          {stats && (
            <MetricsCard
              title="Collection"
              value={
                <div className="flex items-center gap-2">
                  <Award className="w-6 h-6 text-primary" />
                  <span>{Math.floor((stats.totalNFTs / 200) * 100)}%</span>
                </div>
              }
              subtitle={`${stats.totalNFTs} / 200 NFTs`}
              icon={<Zap className="w-5 h-5" />}
              loading={statsLoading}
              error={!!statsError}
              trend={stats.totalNFTs < 200 ? 'up' : 'neutral'}
            />
          )}
        </div>

        {/* Refresh Notice */}
        <div className="mt-8 text-center">
          <p className="text-xs text-muted-foreground">
            Metrics update automatically every 5-60 seconds
          </p>
        </div>
      </div>
    </section>
  )
}
