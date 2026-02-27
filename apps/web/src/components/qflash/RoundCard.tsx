'use client'

import { cn } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus, Users } from 'lucide-react'
import { CountdownTimer } from './CountdownTimer'
import { formatQu, durationLabel } from './helpers'

interface Round {
  id: string
  pair: string
  durationSecs: number
  status: string
  openAt: string
  lockAt: string
  closeAt: string
  openingPrice: number | null
  closingPrice: number | null
  outcome: string | null
  upPoolQu: number
  downPoolQu: number
  entryCount: number
}

interface RoundCardProps {
  round: Round
  isActive?: boolean
  onClick?: () => void
  onCountdownComplete?: () => void
}

export function RoundCard({ round, isActive, onClick, onCountdownComplete }: RoundCardProps) {
  const totalPool = round.upPoolQu + round.downPoolQu
  const upPct = totalPool > 0 ? Math.round((round.upPoolQu / totalPool) * 100) : 50
  const downPct = 100 - upPct

  // Multipliers (with 3% fee)
  const upMultiplier = round.downPoolQu > 0 && round.upPoolQu > 0
    ? (1 + (round.downPoolQu * 0.97) / round.upPoolQu).toFixed(2)
    : '-'
  const downMultiplier = round.upPoolQu > 0 && round.downPoolQu > 0
    ? (1 + (round.upPoolQu * 0.97) / round.downPoolQu).toFixed(2)
    : '-'

  const statusColors: Record<string, string> = {
    upcoming: 'border-zinc-600/50',
    open: 'border-emerald-500/50',
    locked: 'border-amber-500/50',
    resolving: 'border-blue-500/50',
    resolved: 'border-zinc-500/30',
    cancelled: 'border-red-500/30',
  }

  const OutcomeIcon = round.outcome === 'up' ? TrendingUp : round.outcome === 'down' ? TrendingDown : Minus

  return (
    <div
      onClick={onClick}
      className={cn(
        'rounded-xl border bg-card p-4 transition-all',
        statusColors[round.status] ?? 'border-border',
        isActive && 'ring-2 ring-primary/30',
        onClick && 'cursor-pointer hover:border-primary/40',
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold text-muted-foreground">
            {durationLabel(round.durationSecs)}
          </span>
          <span className={cn(
            'rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase',
            round.status === 'open' ? 'bg-emerald-500/15 text-emerald-400' :
            round.status === 'locked' ? 'bg-amber-500/15 text-amber-400' :
            round.status === 'resolved' ? 'bg-zinc-500/15 text-zinc-400' :
            round.status === 'cancelled' ? 'bg-red-500/15 text-red-400' :
            'bg-zinc-500/15 text-zinc-500',
          )}>
            {round.status}
          </span>
        </div>
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <Users className="h-3 w-3" />
          {round.entryCount}
        </div>
      </div>

      {/* Countdown or Result */}
      {['open', 'locked'].includes(round.status) ? (
        <div className="mb-4">
          <CountdownTimer
            targetTime={round.status === 'open' ? round.lockAt : round.closeAt}
            label={round.status === 'open' ? 'Betting closes in' : 'Resolves in'}
            onComplete={onCountdownComplete}
          />
        </div>
      ) : round.status === 'resolved' && round.outcome ? (
        <div className="mb-4 text-center">
          <OutcomeIcon className={cn(
            'mx-auto h-8 w-8 mb-1',
            round.outcome === 'up' ? 'text-emerald-400' : round.outcome === 'down' ? 'text-red-400' : 'text-muted-foreground',
          )} />
          <span className={cn(
            'text-lg font-bold uppercase',
            round.outcome === 'up' ? 'text-emerald-400' : round.outcome === 'down' ? 'text-red-400' : 'text-muted-foreground',
          )}>
            {round.outcome === 'push' ? 'PUSH' : round.outcome.toUpperCase()}
          </span>
        </div>
      ) : round.status === 'upcoming' ? (
        <div className="mb-4">
          <CountdownTimer targetTime={round.openAt} label="Opens in" />
        </div>
      ) : null}

      {/* Pool Bar */}
      <div className="mb-2">
        <div className="flex justify-between text-[10px] mb-1">
          <span className="text-emerald-400 font-medium">UP {upPct}%</span>
          <span className="text-red-400 font-medium">DOWN {downPct}%</span>
        </div>
        <div className="flex h-2 rounded-full overflow-hidden bg-zinc-800">
          <div
            className="bg-emerald-500 transition-all duration-500"
            style={{ width: `${upPct}%` }}
          />
          <div
            className="bg-red-500 transition-all duration-500"
            style={{ width: `${downPct}%` }}
          />
        </div>
      </div>

      {/* Pool & Multiplier */}
      <div className="flex justify-between text-xs">
        <div>
          <span className="text-muted-foreground">Pool: </span>
          <span className="font-mono font-medium">{formatQu(totalPool)} QU</span>
        </div>
        <div className="flex gap-3">
          <span className="text-emerald-400 font-mono">{upMultiplier}x</span>
          <span className="text-red-400 font-mono">{downMultiplier}x</span>
        </div>
      </div>
    </div>
  )
}
