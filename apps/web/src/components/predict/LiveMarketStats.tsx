'use client'

import * as React from 'react'
import { Loader2, TrendingUp, Users } from 'lucide-react'

import { cn } from '@/lib/utils'
import { useMarketUpdates } from '@/hooks/useMarketUpdates'
import { formatQu } from './helpers'

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface LiveMarketStatsProps {
  marketId: string
  options: string[]
}

// ---------------------------------------------------------------------------
// Option colors
// ---------------------------------------------------------------------------

const OPTION_COLORS = [
  'text-emerald-400',
  'text-red-400',
  'text-blue-400',
  'text-amber-400',
  'text-purple-400',
  'text-cyan-400',
]

const OPTION_BG_COLORS = [
  'bg-emerald-500/10 border-emerald-500/20',
  'bg-red-500/10 border-red-500/20',
  'bg-blue-500/10 border-blue-500/20',
  'bg-amber-500/10 border-amber-500/20',
  'bg-purple-500/10 border-purple-500/20',
  'bg-cyan-500/10 border-cyan-500/20',
]

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function LiveMarketStats({ marketId, options }: LiveMarketStatsProps) {
  const { optionStats, totalPool, isLoading, error, participants } = useMarketUpdates(marketId)

  // Calculate total slots for probability
  const totalSlots = optionStats.reduce((sum, s) => sum + s.totalSlots, 0)

  if (isLoading) {
    return (
      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center justify-center gap-2 py-6 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading stats...
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border bg-card p-6">
        <p className="py-6 text-center text-sm text-muted-foreground">
          Unable to load live stats
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-lg border bg-card p-6">
      {/* Header */}
      <div className="mb-4 flex items-center gap-2">
        <TrendingUp className="h-4 w-4 text-muted-foreground" />
        <h3 className="text-sm font-semibold text-foreground">Live Stats</h3>
        <span className="ml-auto flex h-2 w-2 rounded-full bg-emerald-400">
          <span className="inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
        </span>
      </div>

      {/* Top-Level Stats Grid */}
      <div className="mb-4 grid grid-cols-2 gap-3">
        {/* Total Pool */}
        <div className="rounded-md border bg-muted/30 p-3">
          <p className="mb-0.5 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
            Total Pool
          </p>
          <p
            className="text-xl font-bold tabular-nums text-foreground transition-all duration-500"
            style={{ transitionProperty: 'all' }}
          >
            {formatQu(totalPool)}
          </p>
          <p className="text-[10px] text-muted-foreground">QU</p>
        </div>

        {/* Total Participants */}
        <div className="rounded-md border bg-muted/30 p-3">
          <p className="mb-0.5 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
            Participants
          </p>
          <p
            className="text-xl font-bold tabular-nums text-foreground transition-all duration-500"
            style={{ transitionProperty: 'all' }}
          >
            {participants.length}
          </p>
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground">
            <Users className="h-2.5 w-2.5" />
            bettors
          </div>
        </div>
      </div>

      {/* Per-Option Stats */}
      <div className="grid grid-cols-2 gap-3">
        {options.map((label, i) => {
          const stat = optionStats.find((s) => s.option === i)
          const slots = stat?.totalSlots ?? 0
          const probability = totalSlots > 0 ? (slots / totalSlots) * 100 : 0
          const colorText = OPTION_COLORS[i % OPTION_COLORS.length]
          const colorBg = OPTION_BG_COLORS[i % OPTION_BG_COLORS.length]

          return (
            <div
              key={i}
              className={cn('rounded-md border p-3', colorBg)}
            >
              <p className={cn('mb-1 text-xs font-semibold', colorText)}>
                {label}
              </p>
              <div className="space-y-1">
                <div className="flex items-baseline justify-between">
                  <span className="text-[10px] text-muted-foreground">Slots</span>
                  <span
                    className="font-mono text-sm font-bold tabular-nums text-foreground transition-all duration-500"
                  >
                    {slots}
                  </span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className="text-[10px] text-muted-foreground">Implied Prob.</span>
                  <span
                    className={cn(
                      'font-mono text-sm font-bold tabular-nums transition-all duration-500',
                      colorText,
                    )}
                  >
                    {Math.round(probability)}%
                  </span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className="text-[10px] text-muted-foreground">Volume</span>
                  <span className="font-mono text-xs tabular-nums text-foreground">
                    {formatQu(stat?.totalQu ?? 0)} QU
                  </span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
