'use client'

import * as React from 'react'
import { Loader2 } from 'lucide-react'

import type { Market, MarketsListResponse } from './types'
import { MarketCard } from './MarketCard'
import { MarketFilters, type SortOption } from './MarketFilters'

interface MarketBrowserProps {
  initialMarkets?: Market[]
  locale?: string
}

export function MarketBrowser({
  initialMarkets = [],
  locale = 'en',
}: MarketBrowserProps) {
  const [markets, setMarkets] = React.useState<Market[]>(initialMarkets)
  const [loading, setLoading] = React.useState(initialMarkets.length === 0)
  const [pair, setPair] = React.useState('all')
  const [sort, setSort] = React.useState<SortOption>('volume')
  const [marketType, setMarketType] = React.useState('all')

  React.useEffect(() => {
    let cancelled = false

    async function load() {
      setLoading(true)
      try {
        const params = new URLSearchParams({ status: 'active' })
        if (pair !== 'all') params.set('pair', pair)
        if (marketType !== 'all') params.set('marketType', marketType)

        const res = await fetch(`/api/predict/markets?${params.toString()}`)
        if (!res.ok) return

        const data: MarketsListResponse = await res.json()
        if (!cancelled) setMarkets(data.markets)
      } catch {
        // Keep existing data on error
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [pair, marketType])

  // Sort markets locally
  const sorted = React.useMemo(() => {
    const copy = [...markets]

    switch (sort) {
      case 'volume':
        return copy.sort((a, b) => b.totalPool - a.totalPool)
      case 'newest':
        return copy.sort(
          (a, b) =>
            new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
        )
      case 'ending_soon':
        return copy.sort(
          (a, b) =>
            new Date(a.closeDate).getTime() - new Date(b.closeDate).getTime(),
        )
      default:
        return copy
    }
  }, [markets, sort])

  return (
    <div>
      {/* Filter Bar */}
      <div className="mb-6 flex items-center justify-between">
        <MarketFilters
          pair={pair}
          sort={sort}
          marketType={marketType}
          onPairChange={setPair}
          onSortChange={setSort}
          onMarketTypeChange={setMarketType}
        />
        <span className="hidden text-sm text-muted-foreground sm:inline">
          {sorted.length} market{sorted.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      )}

      {/* Empty State */}
      {!loading && sorted.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-2 py-20">
          <p className="text-sm text-muted-foreground">
            No active markets found.
          </p>
          <p className="text-xs text-muted-foreground">
            Try a different filter or create a new market.
          </p>
        </div>
      )}

      {/* Grid */}
      {!loading && sorted.length > 0 && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {sorted.map((market) => (
            <MarketCard key={market.id} market={market} locale={locale} />
          ))}
        </div>
      )}
    </div>
  )
}
