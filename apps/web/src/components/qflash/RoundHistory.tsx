'use client'

import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatQu, durationLabel } from './helpers'

interface HistoryEntry {
  id: string
  roundId: string
  side: string
  amountQu: number
  payoutQu: number | null
  status: string
  createdAt: string
  pair: string
  durationSecs: number
  outcome: string | null
  openingPrice: number | null
  closingPrice: number | null
  roundStatus: string
}

interface RoundHistoryProps {
  entries: HistoryEntry[]
  loading?: boolean
}

export function RoundHistory({ entries, loading }: RoundHistoryProps) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-14 rounded-lg border bg-card animate-pulse" />
        ))}
      </div>
    )
  }

  if (entries.length === 0) {
    return (
      <div className="rounded-lg border bg-card/50 p-6 text-center">
        <p className="text-sm text-muted-foreground">No rounds played yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-1.5">
      {entries.map((entry) => {
        const isWin = entry.status === 'won'
        const isLoss = entry.status === 'lost'
        const isPush = entry.status === 'push'
        const isRefund = entry.status === 'refunded'
        const profit = (entry.payoutQu ?? 0) - entry.amountQu

        const Icon = entry.side === 'up' ? TrendingUp : TrendingDown

        return (
          <div
            key={entry.id}
            className={cn(
              'flex items-center justify-between rounded-lg border px-3 py-2.5',
              isWin ? 'border-emerald-500/20 bg-emerald-500/5' :
              isLoss ? 'border-red-500/20 bg-red-500/5' :
              'border-border bg-card/50',
            )}
          >
            <div className="flex items-center gap-3">
              <Icon className={cn(
                'h-4 w-4',
                entry.side === 'up' ? 'text-emerald-400' : 'text-red-400',
              )} />
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-mono font-medium">{entry.pair.toUpperCase()}</span>
                  <span className="text-[10px] text-muted-foreground">{durationLabel(entry.durationSecs)}</span>
                  <span className={cn(
                    'text-[10px] font-semibold uppercase',
                    isWin ? 'text-emerald-400' : isLoss ? 'text-red-400' : 'text-muted-foreground',
                  )}>
                    {entry.status}
                  </span>
                </div>
                <div className="text-[10px] text-muted-foreground">
                  Bet {formatQu(entry.amountQu)} QU {entry.side.toUpperCase()}
                </div>
              </div>
            </div>
            <div className="text-right">
              {isWin && (
                <span className="text-sm font-mono font-bold text-emerald-400">
                  +{formatQu(profit)} QU
                </span>
              )}
              {isLoss && (
                <span className="text-sm font-mono font-bold text-red-400">
                  -{formatQu(entry.amountQu)} QU
                </span>
              )}
              {(isPush || isRefund) && (
                <span className="text-sm font-mono text-muted-foreground">
                  {formatQu(entry.payoutQu ?? 0)} QU
                </span>
              )}
              {entry.roundStatus === 'open' || entry.roundStatus === 'locked' ? (
                <span className="text-[10px] text-amber-400">pending</span>
              ) : null}
            </div>
          </div>
        )
      })}
    </div>
  )
}
