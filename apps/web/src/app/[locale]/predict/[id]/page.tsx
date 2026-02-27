'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import {
  ArrowLeft,
  Clock,
  Target,
  TrendingUp,
  CheckCircle2,
  Info,
  Loader2,
  AlertCircle,
  Shield,
  Trophy,
  Download,
} from 'lucide-react'

import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { BetPanel } from '@/components/predict/BetPanel'
import { OraclePriceContext } from '@/components/predict/OraclePriceContext'
import { ProbabilityChart } from '@/components/predict/ProbabilityChart'
import { MarketParticipants } from '@/components/predict/MarketParticipants'
import { LiveMarketStats } from '@/components/predict/LiveMarketStats'
import { SmartContractRules } from '@/components/predict/SmartContractRules'
import { MarketCountdown } from '@/components/predict/MarketCountdown'
import type { Market, UserBet, MarketSnapshot, ResolutionStats } from '@/components/predict/types'
import {
  formatQu,
  formatProbability,
  formatPrice,
  formatDateTime,
  timeRemaining,
  statusConfig,
  anonymizeAddress,
} from '@/components/predict/helpers'
import { pairLabel, RESOLUTION_TYPE_LABELS } from '@/components/predict/types'

export default function MarketDetailPage() {
  const params = useParams()
  const locale = (params?.locale as string) ?? 'en'
  const marketId = params?.id as string

  const [market, setMarket] = useState<Market | null>(null)
  const [bets, setBets] = useState<UserBet[]>([])
  const [snapshots, setSnapshots] = useState<MarketSnapshot[]>([])
  const [impliedProbability, setImpliedProbability] = useState(0.5)
  const [resolutionStats, setResolutionStats] = useState<ResolutionStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [downloadingProof, setDownloadingProof] = useState(false)

  const loadMarket = useCallback(async () => {
    if (!marketId) return
    try {
      const res = await fetch(`/api/predict/markets?id=${marketId}`)
      if (!res.ok) {
        const data = await res.json()
        setError(data.error ?? 'Market not found')
        return
      }
      const data = await res.json()
      setMarket(data.market ?? null)
      setBets(data.bets ?? [])
      setSnapshots(data.snapshots ?? [])
      setImpliedProbability(data.impliedProbability ?? 0.5)
      setResolutionStats(data.resolutionStats ?? null)
      setError('')
    } catch {
      setError('Failed to load market')
    } finally {
      setLoading(false)
    }
  }, [marketId])

  // Track last known status to detect changes without full re-render
  const lastStatusRef = useRef<string | null>(null)

  useEffect(() => {
    loadMarket()
  }, [loadMarket])

  // Lightweight status poll — only full-reload when status actually changes
  useEffect(() => {
    if (!market || market.status === 'resolved') return
    lastStatusRef.current = market.status

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/predict/markets?id=${marketId}`)
        if (!res.ok) return
        const data = await res.json()
        const newStatus = data.market?.status
        // Only trigger full state update when status changed or pool changed
        if (
          newStatus !== lastStatusRef.current ||
          data.market?.totalPool !== market.totalPool
        ) {
          lastStatusRef.current = newStatus
          setMarket(data.market ?? null)
          setBets(data.bets ?? [])
          setSnapshots(data.snapshots ?? [])
          setImpliedProbability(data.impliedProbability ?? 0.5)
          setResolutionStats(data.resolutionStats ?? null)
        }
      } catch {
        // silently retry
      }
    }, 15_000)

    return () => clearInterval(interval)
  }, [market?.status, market?.totalPool, marketId])

  // Countdown timer that re-renders every 30 seconds
  const [, setTick] = useState(0)
  useEffect(() => {
    const interval = setInterval(() => setTick((t) => t + 1), 30_000)
    return () => clearInterval(interval)
  }, [])

  async function handleDownloadProof() {
    if (!market) return
    setDownloadingProof(true)
    try {
      const res = await fetch(
        `/api/predict/verify?format=proof-package&marketId=${encodeURIComponent(market.id)}`,
      )
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.error ?? 'Failed to download proof package')
      }
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `qpredict-proof-${market.id.replace(/[^a-zA-Z0-9_-]/g, '_')}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch {
      // Download failed silently — user can retry
    } finally {
      setDownloadingProof(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error || !market) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="flex flex-col items-center justify-center gap-4 rounded-lg border bg-card p-12">
          <AlertCircle className="h-10 w-10 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            {error || 'Market not found'}
          </p>
          <Button variant="outline" asChild>
            <Link href={`/${locale}/predict`}>Back to Markets</Link>
          </Button>
        </div>
      </div>
    )
  }

  const yesPct = impliedProbability
  const noPct = 1 - yesPct
  const remaining = timeRemaining(market.closeDate)
  const endRemaining = timeRemaining(market.endDate)
  const status = statusConfig(market.status)
  const isResolved = market.status === 'resolved'

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      {/* Back Link */}
      <Link
        href={`/${locale}/predict`}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
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

        <h1 className="mb-4 text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
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
          {isResolved ? (
            <div className="flex items-center gap-1.5 text-sm text-emerald-400">
              <CheckCircle2 className="h-4 w-4" />
              <span>
                Resolved{market.resolvedAt ? ` ${formatDateTime(market.resolvedAt)}` : ''}
              </span>
            </div>
          ) : (
            <MarketCountdown
              closeDate={market.closeDate}
              endDate={market.endDate}
            />
          )}
        </div>

        {/* Large probability display */}
        <div className="mt-6 flex items-center gap-6">
          <div className="text-center">
            <p className="text-3xl font-bold text-emerald-400">
              {formatProbability(yesPct)}
            </p>
            <p className="text-xs text-muted-foreground">Yes</p>
          </div>
          <div className="h-12 w-px bg-border" />
          <div className="text-center">
            <p className="text-3xl font-bold text-red-400">
              {formatProbability(noPct)}
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

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Left: Market Info (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Probability Bar */}
          <div className="rounded-lg border bg-card p-5">
            <div className="mb-3 flex items-center justify-between text-sm">
              <span className="font-semibold text-emerald-400">
                Yes {formatProbability(yesPct)}
              </span>
              <span className="font-semibold text-red-400">
                No {formatProbability(noPct)}
              </span>
            </div>
            <div className="h-3 w-full overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${Math.round(yesPct * 100)}%`,
                  background: 'linear-gradient(90deg, #10b981, #f59e0b)',
                }}
              />
            </div>
            <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
              <span>{market.yesSlots} slots</span>
              <span>{formatQu(market.totalPool)} QU pool</span>
              <span>{market.noSlots} slots</span>
            </div>
          </div>

          {/* Resolved Result */}
          {isResolved && market.winningOption !== null && (
            <div
              className={cn(
                'rounded-lg border p-5',
                market.winningOption === 0
                  ? 'border-emerald-500/30 bg-emerald-500/5'
                  : 'border-red-500/30 bg-red-500/5',
              )}
            >
              <div className="flex items-center gap-2">
                <CheckCircle2
                  className={cn(
                    'h-5 w-5',
                    market.winningOption === 0
                      ? 'text-emerald-400'
                      : 'text-red-400',
                  )}
                />
                <h3 className="font-semibold">
                  Resolved: {market.options?.[market.winningOption] ?? (market.winningOption === 0 ? 'YES' : 'NO')}
                </h3>
              </div>
              {market.resolutionPrice !== null && (
                <p className="mt-1 text-sm text-muted-foreground">
                  Price at resolution: ${formatPrice(market.resolutionPrice)}
                  {market.resolvedAt && (
                    <> &middot; {formatDateTime(market.resolvedAt)}</>
                  )}
                </p>
              )}
              {resolutionStats && (
                <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-sm">
                  <span className="flex items-center gap-1 text-muted-foreground">
                    <Trophy className="h-3.5 w-3.5 text-emerald-400" />
                    {resolutionStats.winners} winner{resolutionStats.winners !== 1 ? 's' : ''} ({resolutionStats.winnerSlots} slot{resolutionStats.winnerSlots !== 1 ? 's' : ''})
                  </span>
                  {resolutionStats.losers > 0 && (
                    <span className="text-muted-foreground">
                      {resolutionStats.losers} loser{resolutionStats.losers !== 1 ? 's' : ''}
                    </span>
                  )}
                  {resolutionStats.payoutPerSlot > 0 && (
                    <span className="text-muted-foreground">
                      {formatQu(resolutionStats.payoutPerSlot)} QU/slot
                    </span>
                  )}
                  {resolutionStats.totalPayoutQu > 0 && (
                    <span className="font-medium text-foreground">
                      Total: {formatQu(resolutionStats.totalPayoutQu)} QU
                    </span>
                  )}
                </div>
              )}
              <div className="mt-3 flex flex-wrap items-center gap-3">
                <Link
                  href={`/${locale}/predict/verify/${market.id}`}
                  className="inline-flex items-center gap-1.5 text-sm font-medium text-emerald-500 hover:text-emerald-400 transition-colors"
                >
                  <Shield className="h-3.5 w-3.5" />
                  Verify Resolution
                </Link>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 gap-1.5 text-xs"
                  onClick={handleDownloadProof}
                  disabled={downloadingProof}
                >
                  {downloadingProof ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Download className="h-3.5 w-3.5" />
                  )}
                  Download Resolution Proof
                </Button>
              </div>
            </div>
          )}

          {/* Chart */}
          <ProbabilityChart
            snapshots={snapshots}
            currentProbability={impliedProbability}
          />

          {/* Live Market Stats */}
          <LiveMarketStats
            marketId={market.id}
            options={market.options ?? ['Yes', 'No']}
          />

          {/* Participants Transparency */}
          <MarketParticipants
            marketId={market.id}
            options={market.options ?? ['Yes', 'No']}
          />

          {/* Resolution Info */}
          <div className="rounded-lg border bg-card p-5">
            <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-foreground">
              <Info className="h-4 w-4" />
              Resolution Details
            </h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <DetailRow
                icon={<Target className="h-3.5 w-3.5" />}
                label="Oracle Source"
                value="QPredict Price Oracle"
              />
              <DetailRow
                icon={<Target className="h-3.5 w-3.5" />}
                label="Resolution"
                value={`${RESOLUTION_TYPE_LABELS[market.resolutionType]} $${formatPrice(market.resolutionTarget)}`}
              />
              <DetailRow
                icon={<Clock className="h-3.5 w-3.5" />}
                label="Betting Closes"
                value={formatDateTime(market.closeDate)}
              />
              <DetailRow
                icon={<Clock className="h-3.5 w-3.5" />}
                label="Resolution Date"
                value={formatDateTime(market.endDate)}
              />
              <DetailRow
                icon={<TrendingUp className="h-3.5 w-3.5" />}
                label="Min Bet"
                value={`${formatQu(market.minBetQu)} QU/slot`}
              />
              <DetailRow
                icon={<TrendingUp className="h-3.5 w-3.5" />}
                label="Max Slots"
                value={`${market.maxSlots} per option`}
              />
              {remaining && (
                <DetailRow
                  icon={<Clock className="h-3.5 w-3.5" />}
                  label="Time Left"
                  value={remaining}
                />
              )}
            </div>
          </div>

          {/* Recent Bets */}
          <div className="rounded-lg border bg-card p-5">
            <h3 className="mb-4 text-sm font-semibold text-foreground">
              Recent Bets ({bets.length})
            </h3>
            {bets.length === 0 ? (
              <p className="text-center text-sm text-muted-foreground py-4">
                No bets placed yet. Be the first!
              </p>
            ) : (
              <div className="space-y-2">
                {bets.slice(0, 20).map((bet) => (
                  <div
                    key={bet.id}
                    className="flex items-center justify-between rounded-md bg-muted/30 px-3 py-2 text-sm"
                  >
                    <div className="flex items-center gap-2">
                      <span
                        className={cn(
                          'rounded-full px-2 py-0.5 text-xs font-medium',
                          bet.option === 0
                            ? 'bg-emerald-500/15 text-emerald-400'
                            : 'bg-red-500/15 text-red-400',
                        )}
                      >
                        {bet.option === 0 ? 'YES' : 'NO'}
                      </span>
                      <span className="font-mono text-xs text-muted-foreground">
                        {anonymizeAddress(bet.userAddress)}
                      </span>
                    </div>
                    <span className="text-muted-foreground">
                      {bet.slots} slot{bet.slots > 1 ? 's' : ''} &middot;{' '}
                      {formatQu(bet.amountQu)} QU
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: Bet Panel (1 col) */}
        <div className="lg:col-span-1">
          <div className="sticky top-24 space-y-4">
            {market.marketType === 'price' && market.pair && market.pair !== 'none' && (
              <OraclePriceContext
                pair={market.pair}
                resolutionTarget={market.resolutionTarget}
                resolutionType={market.resolutionType}
                resolutionTargetHigh={market.resolutionTargetHigh}
              />
            )}
            <BetPanel market={market} onBetPlaced={loadMarket} />
            <SmartContractRules />
          </div>
        </div>
      </div>
    </div>
  )
}

function DetailRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="flex items-start gap-2">
      <span className="mt-0.5 text-muted-foreground">{icon}</span>
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="font-medium">{value}</p>
      </div>
    </div>
  )
}
