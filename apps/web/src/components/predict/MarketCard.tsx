'use client'

import * as React from 'react'
import Link from 'next/link'
import { Clock, TrendingUp, Users, Sparkles, Bot, Gamepad2 } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import type { Market } from './types'
import {
  pairBaseAsset,
  pairLabel,
  MARKET_TYPE_LABELS,
  CATEGORY_LABELS,
  CATEGORY_COLORS,
} from './types'
import {
  formatQu,
  formatProbability,
  timeRemaining,
  statusConfig,
} from './helpers'

interface MarketCardProps {
  market: Market
  locale?: string
}

/** Color map for market type badges */
const typeColors: Record<string, string> = {
  price: 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10',
  sports: 'border-orange-500/40 text-orange-400 bg-orange-500/10',
  ai: 'border-purple-500/40 text-purple-400 bg-purple-500/10',
  custom: 'border-blue-500/40 text-blue-400 bg-blue-500/10',
}

/** Color palette for multi-option bars */
const optionColors = [
  '#10b981', // emerald
  '#3b82f6', // blue
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // violet
  '#06b6d4', // cyan
  '#f97316', // orange
  '#ec4899', // pink
]

export function MarketCard({ market, locale = 'en' }: MarketCardProps) {
  const options = market.options ?? ['Yes', 'No']
  const numOptions = market.numOptions ?? options.length
  const slotsPerOption = market.slotsPerOption ?? {}
  const totalSlots = Object.values(slotsPerOption).reduce((a, b) => a + b, 0) || 1
  const remaining = timeRemaining(market.closeDate)
  const status = statusConfig(market.status)
  const isTrending = market.createdBy === 'trending_agent'
  const isPriceMarket = market.marketType === 'price'

  return (
    <Link
      href={`/${locale}/predict/${market.id}`}
      className="group block"
    >
      <div
        className={cn(
          'relative overflow-hidden rounded-lg border bg-card p-5',
          'transition-all duration-200',
          'hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5',
        )}
      >
        {/* Header: Type badge + Category + Status */}
        <div className="mb-3 flex items-center gap-2">
          {/* Market Type Badge */}
          <Badge
            variant="outline"
            className={cn('text-[10px]', typeColors[market.marketType] ?? typeColors.custom)}
          >
            {market.marketType === 'ai' && <Bot className="mr-1 h-3 w-3" />}
            {market.marketType === 'sports' && <Gamepad2 className="mr-1 h-3 w-3" />}
            {MARKET_TYPE_LABELS[market.marketType]}
          </Badge>

          {/* Pair badge (price markets) */}
          {isPriceMarket && market.pair && market.pair !== 'none' && (
            <Badge
              variant="outline"
              className="font-mono text-[10px] uppercase tracking-wider"
            >
              {pairLabel(market.pair)}
            </Badge>
          )}

          {/* Category Badge */}
          {market.category && (
            <span
              className={cn(
                'rounded-full px-2 py-0.5 text-[10px] font-medium',
                CATEGORY_COLORS[market.category],
              )}
            >
              {CATEGORY_LABELS[market.category]}
            </span>
          )}

          {/* Trending / AI badge */}
          {isTrending && (
            <Badge
              variant="outline"
              className="border-amber-500/40 bg-amber-500/10 text-[10px] text-amber-400"
            >
              <Sparkles className="mr-0.5 h-2.5 w-2.5" />
              Trending
            </Badge>
          )}

          {/* Spacer + Status */}
          <div className="flex-1" />
          <Badge
            variant="outline"
            className={cn('text-[10px]', status.className)}
          >
            {status.label}
          </Badge>
        </div>

        {/* Question */}
        <h3 className="mb-4 text-sm font-semibold leading-snug text-foreground group-hover:text-primary transition-colors">
          {market.question}
        </h3>

        {/* Multi-Option Probability Bars */}
        <div className="mb-4 space-y-1.5">
          {numOptions <= 2 ? (
            // Binary market: single combined bar
            <>
              <div className="mb-1.5 flex items-center justify-between text-xs">
                <span className="font-medium text-emerald-400">
                  {options[0] ?? 'Yes'} {formatProbability(market.impliedProbability)}
                </span>
                <span className="font-medium text-red-400">
                  {options[1] ?? 'No'} {formatProbability(1 - market.impliedProbability)}
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.round(market.impliedProbability * 100)}%`,
                    background: 'linear-gradient(90deg, #10b981, #f59e0b)',
                  }}
                />
              </div>
            </>
          ) : (
            // Multi-option: individual bars per option
            options.slice(0, numOptions).map((label, i) => {
              const optSlots = slotsPerOption[String(i)] ?? 0
              const pct = totalSlots > 0 ? (optSlots / totalSlots) * 100 : 0
              const color = optionColors[i % optionColors.length]

              return (
                <div key={i} className="flex items-center gap-2">
                  <span className="w-20 truncate text-[11px] text-muted-foreground">
                    {label}
                  </span>
                  <div className="flex-1 h-1.5 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.max(pct, 1)}%`,
                        backgroundColor: color,
                      }}
                    />
                  </div>
                  <span className="w-10 text-right text-[10px] font-medium" style={{ color }}>
                    {Math.round(pct)}%
                  </span>
                </div>
              )
            })
          )}
        </div>

        {/* Winning Result (resolved markets) */}
        {market.status === 'resolved' && market.winningOption !== null && market.winningOption !== undefined && (
          <div className="mb-3 flex items-center gap-1.5 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1.5">
            <span className="text-xs font-medium text-emerald-400">
              Result: {options[market.winningOption] ?? `Option ${market.winningOption}`}
            </span>
          </div>
        )}

        {/* Footer Stats */}
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            <TrendingUp className="h-3.5 w-3.5" />
            <span>{formatQu(market.totalPool)} QU</span>
          </div>

          <div className="flex items-center gap-1">
            <Users className="h-3.5 w-3.5" />
            <span>
              {Object.values(slotsPerOption).reduce((a, b) => a + b, 0) || (market.yesSlots + market.noSlots)} bets
            </span>
          </div>

          {remaining && market.status !== 'resolved' && (
            <div className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" />
              <span>{remaining}</span>
            </div>
          )}
        </div>

        {/* Watermark */}
        {isPriceMarket && market.pair && market.pair !== 'none' && (
          <div className="pointer-events-none absolute -bottom-2 -right-2 text-6xl font-black uppercase leading-none text-muted-foreground/5">
            {pairBaseAsset(market.pair)}
          </div>
        )}
      </div>
    </Link>
  )
}
