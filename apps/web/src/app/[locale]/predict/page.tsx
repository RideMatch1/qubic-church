'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { Plus, TrendingUp, BarChart3, Coins, Search, X, Star, Users, Clock } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { MarketCard } from '@/components/predict/MarketCard'
import { MarketGridSkeleton } from '@/components/predict/skeletons'
import { useAutoRefresh } from '@/hooks/useAutoRefresh'
import type { Market, PlatformStats, MarketCategory } from '@/components/predict/types'
import { SUPPORTED_PAIRS, pairLabel, ALL_CATEGORIES, CATEGORY_LABELS } from '@/components/predict/types'
import { formatQu, timeRemaining, formatProbability } from '@/components/predict/helpers'

type SortBy = 'newest' | 'volume' | 'ending_soon'

export default function PredictPage() {
  const params = useParams()
  const locale = (params?.locale as string) ?? 'en'
  const [pairFilter, setPairFilter] = useState('all')
  const [sortBy, setSortBy] = useState<SortBy>('volume')
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<'all' | MarketCategory>('all')

  // Auto-refresh markets every 30 seconds (visibility-aware)
  const { data: marketsData, isLoading: marketsLoading } = useAutoRefresh<{
    markets: Market[]
  }>(
    async () => {
      const params = new URLSearchParams({ status: 'active' })
      if (pairFilter !== 'all') params.set('pair', pairFilter)
      const res = await fetch(`/api/predict/markets?${params.toString()}`)
      if (!res.ok) throw new Error('Failed to fetch markets')
      return res.json()
    },
    30_000,
    [pairFilter],
  )

  const { data: statsData } = useAutoRefresh<PlatformStats>(
    async () => {
      const res = await fetch('/api/predict/stats')
      if (!res.ok) throw new Error('Failed to fetch stats')
      return res.json()
    },
    30_000,
    [],
  )

  const { data: recentData } = useAutoRefresh<{ markets: Market[] }>(
    async () => {
      const res = await fetch('/api/predict/markets?status=resolved&limit=5')
      if (!res.ok) throw new Error('Failed to fetch recent')
      return res.json()
    },
    60_000,
    [],
  )

  const markets = marketsData?.markets ?? []
  const stats = statsData ?? null
  const recentMarkets = recentData?.markets ?? []
  const loading = marketsLoading

  // Apply search filter
  const searchFiltered = searchQuery
    ? markets.filter((m) => {
        const q = searchQuery.toLowerCase()
        return (
          m.question.toLowerCase().includes(q) ||
          m.pair.toLowerCase().includes(q)
        )
      })
    : markets

  // Apply category filter
  const categoryFiltered = categoryFilter === 'all'
    ? searchFiltered
    : searchFiltered.filter((m) => m.category === categoryFilter)

  const sorted = [...categoryFiltered].sort((a, b) => {
    switch (sortBy) {
      case 'volume':
        return b.totalPool - a.totalPool
      case 'ending_soon':
        return (
          new Date(a.closeDate).getTime() - new Date(b.closeDate).getTime()
        )
      case 'newest':
      default:
        return (
          new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        )
    }
  })

  function handleCategoryChange(category: 'all' | MarketCategory) {
    setCategoryFilter(category)
  }

  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden border-b bg-gradient-to-b from-background to-muted/20">
          <div className="mx-auto max-w-6xl px-4 py-16 sm:py-20">
            <div className="mb-10 text-center">
              <h1 className="mb-3 text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
                QPredict
              </h1>
              <p className="text-xl font-medium text-muted-foreground">
                Predict. Win. Earn.
              </p>
              <p className="mx-auto mt-3 max-w-md text-sm text-muted-foreground/80">
                Decentralized prediction markets powered by Qubic Quottery
                smart contracts. Bet on crypto prices with provably fair
                on-chain resolution.
              </p>
            </div>

            {/* Live Stats Bar */}
            {stats && (
              <div className="mx-auto max-w-2xl">
                <div className="grid grid-cols-3 divide-x divide-border rounded-lg border bg-card">
                  <StatCell
                    icon={<TrendingUp className="h-4 w-4" />}
                    label="Total Volume"
                    value={`${formatQu(stats.totalVolume)} QU`}
                  />
                  <StatCell
                    icon={<BarChart3 className="h-4 w-4" />}
                    label="Active Markets"
                    value={String(stats.activeMarkets)}
                  />
                  <StatCell
                    icon={<Coins className="h-4 w-4" />}
                    label="Total Paid Out"
                    value={`${formatQu(stats.totalPaidOut)} QU`}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Decorative gradient orbs */}
          <div className="pointer-events-none absolute -top-20 left-1/4 h-64 w-64 rounded-full bg-emerald-500/5 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-10 right-1/4 h-48 w-48 rounded-full bg-red-500/5 blur-3xl" />
        </section>

        {/* Markets Section */}
        <section className="mx-auto max-w-6xl px-4 py-10">
          {/* Toolbar: Title + Filters + Create */}
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-xl font-semibold text-foreground">
              Active Markets
            </h2>

            <div className="flex flex-wrap items-center gap-3">
              {/* Search */}
              <div className="relative">
                <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search markets..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="h-9 w-[200px] pl-8 pr-8 text-sm"
                />
                {searchQuery && (
                  <button
                    type="button"
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>

              {/* Pair Filter */}
              <Select value={pairFilter} onValueChange={setPairFilter}>
                <SelectTrigger className="w-[160px]">
                  <SelectValue placeholder="All Pairs" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Pairs</SelectItem>
                  {SUPPORTED_PAIRS.map((p) => (
                    <SelectItem key={p} value={p}>
                      {pairLabel(p)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Sort */}
              <Select
                value={sortBy}
                onValueChange={(v) => setSortBy(v as SortBy)}
              >
                <SelectTrigger className="w-[160px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="volume">Volume</SelectItem>
                  <SelectItem value="newest">Newest</SelectItem>
                  <SelectItem value="ending_soon">Ending Soon</SelectItem>
                </SelectContent>
              </Select>

              {/* Create Market */}
              <Link href={`/${locale}/predict/create`}>
                <Button size="sm">
                  <Plus className="mr-1.5 h-4 w-4" />
                  Create Market
                </Button>
              </Link>
            </div>
          </div>

          {/* Category Filter Chips */}
          <div className="mb-6 flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => handleCategoryChange('all')}
              className={cn(
                'rounded-full border px-3 py-1 text-xs font-medium transition-colors',
                categoryFilter === 'all'
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border bg-card text-muted-foreground hover:border-primary/40 hover:text-foreground',
              )}
            >
              All
            </button>
            {ALL_CATEGORIES.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => handleCategoryChange(cat)}
                className={cn(
                  'rounded-full border px-3 py-1 text-xs font-medium transition-colors',
                  categoryFilter === cat
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-border bg-card text-muted-foreground hover:border-primary/40 hover:text-foreground',
                )}
              >
                {CATEGORY_LABELS[cat]}
              </button>
            ))}
          </div>

          {/* Featured Market Hero */}
          {!loading && !searchQuery && sorted[0] && (
            <FeaturedMarketHero market={sorted[0]} locale={locale} />
          )}

          {/* Market Grid */}
          {loading ? (
            <MarketGridSkeleton />
          ) : sorted.length === 0 ? (
            <div className="rounded-lg border bg-card p-12 text-center">
              <p className="text-muted-foreground">
                No active markets found.
              </p>
              <p className="mt-1 text-sm text-muted-foreground/70">
                Try a different filter or create the first market.
              </p>
              <Link
                href={`/${locale}/predict/create`}
                className="mt-4 inline-block text-sm font-medium text-primary hover:underline"
              >
                Create a Market
              </Link>
            </div>
          ) : (
            <>
              <p className="mb-4 text-sm text-muted-foreground">
                {sorted.length} market{sorted.length !== 1 ? 's' : ''}
              </p>
              <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                {sorted.map((market) => (
                  <MarketCard key={market.id} market={market} />
                ))}
              </div>
            </>
          )}

          {/* Recent Results */}
          {recentMarkets.length > 0 && (
            <div className="mt-12">
              <h2 className="mb-4 text-xl font-semibold text-foreground">
                Recent Results
              </h2>
              <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                {recentMarkets.map((market) => (
                  <MarketCard key={market.id} market={market} />
                ))}
              </div>
            </div>
          )}

          {/* Bottom Nav */}
          <div className="mt-12 flex justify-center gap-6 text-sm text-muted-foreground">
            <Link
              href={`/${locale}/predict/history`}
              className="hover:text-foreground transition-colors"
            >
              History
            </Link>
            <Link
              href={`/${locale}/predict/leaderboard`}
              className="hover:text-foreground transition-colors"
            >
              Leaderboard
            </Link>
            <Link
              href={`/${locale}/predict/verify`}
              className="hover:text-foreground transition-colors"
            >
              Verify
            </Link>
          </div>
        </section>
      </main>
    </div>
  )
}

function FeaturedMarketHero({
  market,
  locale,
}: {
  market: Market
  locale: string
}) {
  const remaining = timeRemaining(market.closeDate)
  const totalSlots =
    Object.values(market.slotsPerOption ?? {}).reduce((a, b) => a + b, 0) ||
    market.yesSlots + market.noSlots

  return (
    <Link
      href={`/${locale}/predict/${market.id}`}
      className="group mb-6 block"
    >
      <div className="relative overflow-hidden rounded-xl border bg-gradient-to-r from-emerald-500/10 via-card to-blue-500/10 p-6 transition-all hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="mb-2 flex items-center gap-2">
              <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/15 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-amber-400">
                <Star className="h-3 w-3" />
                Featured Market
              </span>
              {market.pair && market.pair !== 'none' && (
                <span className="rounded-full border px-2 py-0.5 font-mono text-[10px] uppercase text-muted-foreground">
                  {market.pair}
                </span>
              )}
            </div>
            <h3 className="mb-2 text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
              {market.question}
            </h3>
            <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <TrendingUp className="h-3.5 w-3.5" />
                {formatQu(market.totalPool)} QU
              </span>
              <span className="flex items-center gap-1">
                <Users className="h-3.5 w-3.5" />
                {totalSlots} bets
              </span>
              {remaining && (
                <span className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  {remaining}
                </span>
              )}
            </div>
          </div>
          <div className="hidden sm:flex flex-col items-end gap-1 text-right">
            <span className="text-2xl font-bold text-emerald-400">
              {formatProbability(market.impliedProbability)}
            </span>
            <span className="text-[10px] text-muted-foreground">
              {(market.options ?? ['Yes'])[0]} probability
            </span>
          </div>
        </div>
      </div>
    </Link>
  )
}

function StatCell({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="flex flex-col items-center gap-1 px-4 py-3 sm:flex-row sm:gap-3 sm:px-6 sm:py-4">
      <span className="text-muted-foreground">{icon}</span>
      <div className="text-center sm:text-left">
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-sm font-semibold text-foreground">{value}</p>
      </div>
    </div>
  )
}
