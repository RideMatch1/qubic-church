'use client'

import * as React from 'react'
import { TrendingUp, BarChart3, Coins } from 'lucide-react'

import { formatQu } from './helpers'
import type { PlatformStats } from './types'

interface StatsBarProps {
  initialStats?: PlatformStats | null
}

export function StatsBar({ initialStats }: StatsBarProps) {
  const [stats, setStats] = React.useState<PlatformStats | null>(
    initialStats ?? null,
  )

  React.useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const res = await fetch('/api/predict/stats')
        if (!res.ok) return
        const data = await res.json()
        if (!cancelled) setStats(data)
      } catch {
        // Silently fail; keep initial stats
      }
    }

    load()
    const interval = setInterval(load, 30_000)

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [])

  const items = [
    {
      label: 'Total Volume',
      value: stats ? `${formatQu(stats.totalVolume)} QU` : '--',
      icon: TrendingUp,
    },
    {
      label: 'Active Markets',
      value: stats ? stats.activeMarkets.toString() : '--',
      icon: BarChart3,
    },
    {
      label: 'Total Paid Out',
      value: stats ? `${formatQu(stats.totalPaidOut)} QU` : '--',
      icon: Coins,
    },
  ]

  return (
    <div className="grid grid-cols-3 divide-x divide-border rounded-lg border bg-card">
      {items.map((item) => (
        <div
          key={item.label}
          className="flex flex-col items-center gap-1 px-4 py-3 sm:flex-row sm:gap-3 sm:px-6 sm:py-4"
        >
          <item.icon className="h-4 w-4 text-muted-foreground" />
          <div className="text-center sm:text-left">
            <p className="text-xs text-muted-foreground">{item.label}</p>
            <p className="text-sm font-semibold text-foreground">
              {item.value}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
