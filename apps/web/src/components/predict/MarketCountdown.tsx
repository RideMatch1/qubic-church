'use client'

import * as React from 'react'
import { Clock } from 'lucide-react'

import { cn } from '@/lib/utils'

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface MarketCountdownProps {
  closeDate: string
  endDate: string
  compact?: boolean
}

// ---------------------------------------------------------------------------
// Time formatting helpers
// ---------------------------------------------------------------------------

interface TimeBreakdown {
  days: number
  hours: number
  minutes: number
  seconds: number
  totalMs: number
}

function getTimeBreakdown(targetIso: string): TimeBreakdown {
  const diff = new Date(targetIso).getTime() - Date.now()
  if (diff <= 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0, totalMs: 0 }
  }
  return {
    days: Math.floor(diff / (1000 * 60 * 60 * 24)),
    hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
    minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
    seconds: Math.floor((diff % (1000 * 60)) / 1000),
    totalMs: diff,
  }
}

function formatCompact(t: TimeBreakdown): string {
  if (t.totalMs <= 0) return 'now'
  if (t.days > 0) return `${t.days}d ${t.hours}h`
  if (t.hours > 0) return `${t.hours}h ${t.minutes}m`
  if (t.minutes > 0) return `${t.minutes}m ${t.seconds}s`
  return `${t.seconds}s`
}

function formatFull(t: TimeBreakdown): string {
  if (t.totalMs <= 0) return 'now'
  const parts: string[] = []
  if (t.days > 0) parts.push(`${t.days} day${t.days !== 1 ? 's' : ''}`)
  if (t.hours > 0) parts.push(`${t.hours} hour${t.hours !== 1 ? 's' : ''}`)
  if (t.minutes > 0 && t.days === 0) parts.push(`${t.minutes} min`)
  if (t.days === 0 && t.hours === 0 && t.seconds > 0) parts.push(`${t.seconds}s`)
  return parts.join(', ')
}

// ---------------------------------------------------------------------------
// Urgency helpers
// ---------------------------------------------------------------------------

const ONE_HOUR = 1000 * 60 * 60
const ONE_DAY = ONE_HOUR * 24
const SEVEN_DAYS = ONE_DAY * 7

function urgencyColor(totalMs: number): string {
  if (totalMs <= 0) return 'text-muted-foreground'
  if (totalMs < ONE_DAY) return 'text-red-400'
  if (totalMs < SEVEN_DAYS) return 'text-yellow-400'
  return 'text-emerald-400'
}

function shouldPulse(totalMs: number): boolean {
  return totalMs > 0 && totalMs < ONE_HOUR
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function MarketCountdown({ closeDate, endDate, compact = false }: MarketCountdownProps) {
  const [now, setNow] = React.useState(Date.now())

  React.useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(timer)
  }, [])

  // Determine which phase we are in
  const closeTime = new Date(closeDate).getTime()
  const isClosed = now >= closeTime

  const targetDate = isClosed ? endDate : closeDate
  const breakdown = getTimeBreakdown(targetDate)
  const label = isClosed ? 'Resolves in' : 'Betting closes in'
  const display = compact ? formatCompact(breakdown) : formatFull(breakdown)
  const color = urgencyColor(breakdown.totalMs)
  const pulse = shouldPulse(breakdown.totalMs)

  // Both dates passed
  const endTime = new Date(endDate).getTime()
  const isFullyPast = now >= endTime

  if (isFullyPast) {
    return (
      <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
        <Clock className="h-3.5 w-3.5" />
        <span>Market ended</span>
      </div>
    )
  }

  return (
    <div
      className={cn(
        'flex items-center gap-1.5 text-sm',
        color,
        pulse && 'animate-pulse',
      )}
    >
      <Clock className="h-3.5 w-3.5" />
      <span>
        {label} <span className="font-semibold tabular-nums">{display}</span>
      </span>
    </div>
  )
}
