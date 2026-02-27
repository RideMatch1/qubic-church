'use client'

import * as React from 'react'
import { ExternalLink, Loader2, RefreshCw, Users } from 'lucide-react'

import { cn } from '@/lib/utils'
import { useMarketUpdates } from '@/hooks/useMarketUpdates'
import { formatQu, anonymizeAddress } from './helpers'

// ---------------------------------------------------------------------------
// Option color palette (cycles through these for multi-option markets)
// ---------------------------------------------------------------------------

const OPTION_COLORS = [
  { bg: 'bg-emerald-500', text: 'text-emerald-400', badge: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' },
  { bg: 'bg-red-500', text: 'text-red-400', badge: 'bg-red-500/15 text-red-400 border-red-500/30' },
  { bg: 'bg-blue-500', text: 'text-blue-400', badge: 'bg-blue-500/15 text-blue-400 border-blue-500/30' },
  { bg: 'bg-amber-500', text: 'text-amber-400', badge: 'bg-amber-500/15 text-amber-400 border-amber-500/30' },
  { bg: 'bg-purple-500', text: 'text-purple-400', badge: 'bg-purple-500/15 text-purple-400 border-purple-500/30' },
  { bg: 'bg-cyan-500', text: 'text-cyan-400', badge: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30' },
]

function getOptionColor(index: number) {
  return OPTION_COLORS[index % OPTION_COLORS.length]!
}

// ---------------------------------------------------------------------------
// Status badge styling
// ---------------------------------------------------------------------------

function statusBadgeClass(status: string): string {
  switch (status) {
    case 'active_in_sc':
      return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
    case 'won_awaiting_sweep':
    case 'swept':
    case 'completed':
      return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
    case 'lost':
      return 'bg-zinc-500/15 text-zinc-400 border-zinc-500/30'
    case 'deposit_detected':
    case 'joining_sc':
      return 'bg-blue-500/15 text-blue-400 border-blue-500/30'
    case 'awaiting_deposit':
      return 'bg-amber-500/15 text-amber-400 border-amber-500/30'
    default:
      return 'bg-zinc-500/15 text-zinc-400 border-zinc-500/30'
  }
}

function statusDisplayLabel(status: string): string {
  switch (status) {
    case 'awaiting_deposit':
      return 'Pending'
    case 'deposit_detected':
      return 'Detected'
    case 'joining_sc':
      return 'Joining'
    case 'active_in_sc':
      return 'Active'
    case 'won_awaiting_sweep':
      return 'Won'
    case 'swept':
      return 'Paid'
    case 'completed':
      return 'Complete'
    case 'lost':
      return 'Lost'
    default:
      return status
  }
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface MarketParticipantsProps {
  marketId: string
  options: string[]
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function MarketParticipants({ marketId, options }: MarketParticipantsProps) {
  const { participants, optionStats, totalPool, isLoading, error, refresh } = useMarketUpdates(marketId)
  const [showAll, setShowAll] = React.useState(false)
  const [refreshing, setRefreshing] = React.useState(false)

  const VISIBLE_LIMIT = 10
  const hasMore = participants.length > VISIBLE_LIMIT
  const visibleParticipants = showAll ? participants : participants.slice(0, VISIBLE_LIMIT)

  async function handleRefresh() {
    setRefreshing(true)
    await refresh()
    setRefreshing(false)
  }

  // Calculate total slots for the distribution bar
  const totalSlots = optionStats.reduce((sum, s) => sum + s.totalSlots, 0)

  if (isLoading) {
    return (
      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center justify-center gap-2 py-8 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading participants...
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border bg-card p-6">
        <div className="flex flex-col items-center gap-2 py-8 text-sm text-muted-foreground">
          <p>Failed to load participants: {error}</p>
          <button
            onClick={handleRefresh}
            className="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-muted"
          >
            <RefreshCw className="h-3 w-3" />
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-lg border bg-card p-6">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-muted-foreground" />
          <h3 className="text-sm font-semibold text-foreground">
            Participants ({participants.length})
          </h3>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <RefreshCw className={cn('h-3 w-3', refreshing && 'animate-spin')} />
          {refreshing ? 'Updating...' : 'Refresh'}
        </button>
      </div>

      {/* Slot Distribution Bar */}
      {totalSlots > 0 && (
        <div className="mb-4">
          <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
            <span>Slot Distribution</span>
            <span>{formatQu(totalPool)} QU total</span>
          </div>
          <div className="flex h-3 overflow-hidden rounded-full bg-muted/50">
            {optionStats.map((stat) => {
              const pct = totalSlots > 0 ? (stat.totalSlots / totalSlots) * 100 : 0
              if (pct === 0) return null
              const color = getOptionColor(stat.option)
              return (
                <div
                  key={stat.option}
                  className={cn('h-full transition-all duration-500', color.bg)}
                  style={{ width: `${pct}%` }}
                  title={`${stat.label}: ${stat.totalSlots} slots (${Math.round(pct)}%)`}
                />
              )
            })}
          </div>
          {/* Legend */}
          <div className="mt-2 flex flex-wrap gap-3">
            {optionStats.map((stat) => {
              const color = getOptionColor(stat.option)
              const pct = totalSlots > 0 ? (stat.totalSlots / totalSlots) * 100 : 0
              return (
                <div key={stat.option} className="flex items-center gap-1.5 text-xs">
                  <div className={cn('h-2.5 w-2.5 rounded-full', color.bg)} />
                  <span className="text-muted-foreground">
                    {stat.label}: {stat.totalSlots} slots ({Math.round(pct)}%) &middot; {stat.participants} bets
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Empty State */}
      {participants.length === 0 && (
        <div className="flex flex-col items-center gap-1 py-8 text-center">
          <Users className="h-8 w-8 text-muted-foreground/30" />
          <p className="text-sm text-muted-foreground">No participants yet</p>
          <p className="text-xs text-muted-foreground/60">Be the first to place a bet on this market</p>
        </div>
      )}

      {/* Participants Table */}
      {participants.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-xs text-muted-foreground">
                <th className="pb-2 pr-3 font-medium">Address</th>
                <th className="pb-2 pr-3 font-medium">Option</th>
                <th className="pb-2 pr-3 text-right font-medium">Slots</th>
                <th className="pb-2 pr-3 text-right font-medium">Amount</th>
                <th className="pb-2 pr-3 font-medium">Status</th>
                <th className="pb-2 font-medium">TX</th>
              </tr>
            </thead>
            <tbody>
              {visibleParticipants.map((p, i) => {
                const color = getOptionColor(p.option)
                return (
                  <tr
                    key={`${p.escrowAddress}-${i}`}
                    className="border-b border-muted/30 last:border-0"
                  >
                    {/* Address */}
                    <td className="py-2.5 pr-3">
                      <a
                        href={`https://explorer.qubic.org/network/address/${p.fullAddress}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 font-mono text-xs text-foreground transition-colors hover:text-blue-400"
                      >
                        {anonymizeAddress(p.fullAddress)}
                        <ExternalLink className="h-3 w-3 text-muted-foreground" />
                      </a>
                    </td>

                    {/* Option */}
                    <td className="py-2.5 pr-3">
                      <span
                        className={cn(
                          'inline-block rounded-full border px-2 py-0.5 text-[10px] font-medium',
                          color.badge,
                        )}
                      >
                        {p.optionLabel}
                      </span>
                    </td>

                    {/* Slots */}
                    <td className="py-2.5 pr-3 text-right font-medium text-foreground">
                      {p.slots}
                    </td>

                    {/* Amount */}
                    <td className="py-2.5 pr-3 text-right font-mono text-xs text-foreground">
                      {formatQu(p.amountQu)} QU
                    </td>

                    {/* Status */}
                    <td className="py-2.5 pr-3">
                      <span
                        className={cn(
                          'inline-block rounded-full border px-2 py-0.5 text-[10px] font-medium',
                          statusBadgeClass(p.status),
                        )}
                      >
                        {statusDisplayLabel(p.status)}
                      </span>
                    </td>

                    {/* TX */}
                    <td className="py-2.5">
                      {p.joinBetTxId ? (
                        <a
                          href={`https://explorer.qubic.org/network/tx/${p.joinBetTxId}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 font-mono text-[10px] text-muted-foreground transition-colors hover:text-blue-400"
                        >
                          {p.joinBetTxId.slice(0, 8)}...
                          <ExternalLink className="h-2.5 w-2.5" />
                        </a>
                      ) : (
                        <span className="text-[10px] text-muted-foreground/40">--</span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Show All Toggle */}
      {hasMore && (
        <div className="mt-3 text-center">
          <button
            onClick={() => setShowAll(!showAll)}
            className="inline-flex items-center gap-1 rounded-md border px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            {showAll
              ? 'Show less'
              : `Show all ${participants.length} participants`}
          </button>
        </div>
      )}
    </div>
  )
}
