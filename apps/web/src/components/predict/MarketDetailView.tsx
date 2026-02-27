'use client'

import * as React from 'react'
import Link from 'next/link'
import {
  ArrowLeft,
  Clock,
  Target,
  Info,
  Loader2,
  AlertCircle,
} from 'lucide-react'

import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { MarketDetail } from './types'
import { pairLabel, RESOLUTION_TYPE_LABELS } from './types'
import {
  formatQu,
  formatProbability,
  formatPrice,
  timeRemaining,
  statusConfig,
  formatDateTime,
} from './helpers'
import { BetPanel } from './BetPanel'
import { ProbabilityChart } from './ProbabilityChart'
import { MarketBetsList } from './MarketBetsList'

interface MarketDetailViewProps {
  marketId: string
  locale?: string
}

export function MarketDetailView({
  marketId,
  locale = 'en',
}: MarketDetailViewProps) {
  const [detail, setDetail] = React.useState<MarketDetail | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')

  const fetchDetail = React.useCallback(async () => {
    try {
      const res = await fetch(`/api/predict/markets?id=${marketId}`)
      if (!res.ok) {
        const data = await res.json()
        setError(data.error ?? 'Market not found')
        return
      }
      const data: MarketDetail = await res.json()
      setDetail(data)
      setError('')
    } catch {
      setError('Failed to load market')
    } finally {
      setLoading(false)
    }
  }, [marketId])

  React.useEffect(() => {
    fetchDetail()
  }, [fetchDetail])

  // Countdown timer that re-renders every minute
  const [, setTick] = React.useState(0)
  React.useEffect(() => {
    const interval = setInterval(() => setTick((t) => t + 1), 60_000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error || !detail) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-32">
        <AlertCircle className="h-10 w-10 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">
          {error || 'Market not found'}
        </p>
        <Button variant="outline" asChild>
          <Link href={`/${locale}/predict`}>Back to Markets</Link>
        </Button>
      </div>
    )
  }

  const { market, bets, snapshots, impliedProbability } = detail
  const status = statusConfig(market.status)
  const remaining = timeRemaining(market.closeDate)
  const endRemaining = timeRemaining(market.endDate)

  return (
    <div>
      {/* Back Link */}
      <Link
        href={`/${locale}/predict`}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        All Markets
      </Link>

      {/* Market Header */}
      <div className="mb-8">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <Badge
            variant="outline"
            className="font-mono text-xs uppercase tracking-wider"
          >
            {pairLabel(market.pair)}
          </Badge>
          <Badge variant="outline" className={cn('text-xs', status.className)}>
            {status.label}
          </Badge>
          <Badge variant="outline" className="text-xs">
            {RESOLUTION_TYPE_LABELS[market.resolutionType]}
          </Badge>
        </div>

        <h1 className="mb-4 text-2xl font-bold text-foreground sm:text-3xl">
          {market.question}
        </h1>

        {/* Quick stats row */}
        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <Target className="h-4 w-4" />
            <span>
              Target: ${formatPrice(market.resolutionTarget)}
              {market.resolutionTargetHigh !== null &&
                ` - $${formatPrice(market.resolutionTargetHigh)}`}
            </span>
          </div>
          {remaining && (
            <div className="flex items-center gap-1.5">
              <Clock className="h-4 w-4" />
              <span>Betting: {remaining}</span>
            </div>
          )}
          {endRemaining && (
            <div className="flex items-center gap-1.5">
              <Clock className="h-4 w-4" />
              <span>Resolves: {endRemaining}</span>
            </div>
          )}
        </div>

        {/* Large probability display */}
        <div className="mt-6 flex items-center gap-6">
          <div className="text-center">
            <p className="text-3xl font-bold text-emerald-400">
              {formatProbability(impliedProbability)}
            </p>
            <p className="text-xs text-muted-foreground">Yes</p>
          </div>
          <div className="h-12 w-px bg-border" />
          <div className="text-center">
            <p className="text-3xl font-bold text-red-400">
              {formatProbability(1 - impliedProbability)}
            </p>
            <p className="text-xs text-muted-foreground">No</p>
          </div>
          <div className="h-12 w-px bg-border" />
          <div className="text-center">
            <p className="text-3xl font-bold text-foreground">
              {formatQu(market.totalPool)}
            </p>
            <p className="text-xs text-muted-foreground">QU in Pool</p>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Column: Chart + Info + Bets */}
        <div className="space-y-6 lg:col-span-2">
          {/* Probability Chart */}
          <ProbabilityChart
            snapshots={snapshots}
            currentProbability={impliedProbability}
          />

          {/* Resolution Info */}
          <div className="rounded-lg border bg-card p-6">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
              <Info className="h-4 w-4" />
              Resolution Details
            </h3>
            <div className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
              <div>
                <p className="text-muted-foreground">Oracle Source</p>
                <p className="font-medium text-foreground">
                  QPredict Price Oracle
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Resolution Type</p>
                <p className="font-medium text-foreground">
                  {RESOLUTION_TYPE_LABELS[market.resolutionType]}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Target Price</p>
                <p className="font-medium text-foreground">
                  ${formatPrice(market.resolutionTarget)}
                  {market.resolutionTargetHigh !== null &&
                    ` - $${formatPrice(market.resolutionTargetHigh)}`}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Min Bet</p>
                <p className="font-medium text-foreground">
                  {formatQu(market.minBetQu)} QU / slot
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Betting Closes</p>
                <p className="font-medium text-foreground">
                  {formatDateTime(market.closeDate)}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Resolution Date</p>
                <p className="font-medium text-foreground">
                  {formatDateTime(market.endDate)}
                </p>
              </div>
              {market.status === 'resolved' && (
                <>
                  <div>
                    <p className="text-muted-foreground">Resolution Price</p>
                    <p className="font-medium text-foreground">
                      {market.resolutionPrice !== null
                        ? `$${formatPrice(market.resolutionPrice)}`
                        : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Winning Side</p>
                    <p
                      className={cn(
                        'font-semibold',
                        market.winningOption === 0
                          ? 'text-emerald-400'
                          : 'text-red-400',
                      )}
                    >
                      {market.winningOption === 0 ? 'Yes' : 'No'}
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Bets List */}
          <MarketBetsList bets={bets} />
        </div>

        {/* Right Column: Bet Panel */}
        <div className="lg:col-span-1">
          <div className="lg:sticky lg:top-20">
            <BetPanel market={market} onBetPlaced={fetchDetail} />
          </div>
        </div>
      </div>
    </div>
  )
}
