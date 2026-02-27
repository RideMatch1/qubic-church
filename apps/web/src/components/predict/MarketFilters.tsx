'use client'

import * as React from 'react'

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  SUPPORTED_PAIRS,
  MARKET_TYPE_LABELS,
  ALL_MARKET_TYPES,
  pairLabel,
} from './types'

export type SortOption = 'volume' | 'newest' | 'ending_soon'

interface MarketFiltersProps {
  pair: string
  sort: SortOption
  marketType: string
  onPairChange: (pair: string) => void
  onSortChange: (sort: SortOption) => void
  onMarketTypeChange: (marketType: string) => void
}

export function MarketFilters({
  pair,
  sort,
  marketType,
  onPairChange,
  onSortChange,
  onMarketTypeChange,
}: MarketFiltersProps) {
  const showPairFilter = marketType === 'all' || marketType === 'price'

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Market Type Filter */}
      <Select value={marketType} onValueChange={onMarketTypeChange}>
        <SelectTrigger className="w-[150px]">
          <SelectValue placeholder="All Types" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Types</SelectItem>
          {ALL_MARKET_TYPES.map((mt) => (
            <SelectItem key={mt} value={mt}>
              {MARKET_TYPE_LABELS[mt]}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Pair Filter (only for price or all types) */}
      {showPairFilter && (
        <Select value={pair} onValueChange={onPairChange}>
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
      )}

      {/* Sort */}
      <Select value={sort} onValueChange={(v) => onSortChange(v as SortOption)}>
        <SelectTrigger className="w-[160px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="volume">Volume</SelectItem>
          <SelectItem value="newest">Newest</SelectItem>
          <SelectItem value="ending_soon">Ending Soon</SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}
