'use client'

import { Flame, Target, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'

interface WinStreakProps {
  streak: number      // positive = win streak, negative = loss streak
  bestStreak: number
  winCount: number
  lossCount: number
}

export function WinStreak({ streak, bestStreak, winCount, lossCount }: WinStreakProps) {
  const totalRounds = winCount + lossCount
  const winRate = totalRounds > 0 ? Math.round((winCount / totalRounds) * 100) : 0
  const isWinning = streak > 0
  const absStreak = Math.abs(streak)

  return (
    <div className="grid grid-cols-3 gap-3">
      {/* Current Streak */}
      <div className={cn(
        'rounded-lg border p-3 text-center',
        isWinning ? 'border-emerald-500/30 bg-emerald-500/5' : streak < 0 ? 'border-red-500/30 bg-red-500/5' : 'border-border bg-card/50',
      )}>
        <Flame className={cn(
          'mx-auto h-4 w-4 mb-1',
          isWinning ? 'text-emerald-400' : streak < 0 ? 'text-red-400' : 'text-muted-foreground',
        )} />
        <p className={cn(
          'text-lg font-bold font-mono',
          isWinning ? 'text-emerald-400' : streak < 0 ? 'text-red-400' : 'text-muted-foreground',
        )}>
          {absStreak}
        </p>
        <p className="text-[9px] text-muted-foreground uppercase tracking-wider">
          {isWinning ? 'Win Streak' : streak < 0 ? 'Loss Streak' : 'Streak'}
        </p>
      </div>

      {/* Best Streak */}
      <div className="rounded-lg border border-border bg-card/50 p-3 text-center">
        <TrendingUp className="mx-auto h-4 w-4 mb-1 text-amber-400" />
        <p className="text-lg font-bold font-mono text-amber-400">{bestStreak}</p>
        <p className="text-[9px] text-muted-foreground uppercase tracking-wider">Best Streak</p>
      </div>

      {/* Win Rate */}
      <div className="rounded-lg border border-border bg-card/50 p-3 text-center">
        <Target className="mx-auto h-4 w-4 mb-1 text-blue-400" />
        <p className="text-lg font-bold font-mono text-blue-400">{winRate}%</p>
        <p className="text-[9px] text-muted-foreground uppercase tracking-wider">Win Rate</p>
      </div>
    </div>
  )
}
