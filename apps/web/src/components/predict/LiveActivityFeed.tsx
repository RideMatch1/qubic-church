'use client'

import * as React from 'react'
import { CheckCircle2, Plus, TrendingUp } from 'lucide-react'

import { cn } from '@/lib/utils'
import { formatQu } from './helpers'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ActivityEventType = 'bet' | 'market_created' | 'resolved'

interface ActivityEvent {
  type: ActivityEventType
  marketId: string
  timestamp: string
  // bet fields
  address?: string
  amountQu?: number
  option?: string
  slots?: number
  status?: string
  // market fields
  question?: string
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  if (diff < 0) return 'just now'

  const seconds = Math.floor(diff / 1000)
  if (seconds < 60) return `${seconds}s ago`

  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`

  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`

  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

const EVENT_CONFIG: Record<
  ActivityEventType,
  {
    icon: typeof TrendingUp
    colorClass: string
    borderClass: string
    bgClass: string
  }
> = {
  bet: {
    icon: TrendingUp,
    colorClass: 'text-blue-400',
    borderClass: 'border-blue-500/20',
    bgClass: 'bg-blue-500/5',
  },
  market_created: {
    icon: Plus,
    colorClass: 'text-emerald-400',
    borderClass: 'border-emerald-500/20',
    bgClass: 'bg-emerald-500/5',
  },
  resolved: {
    icon: CheckCircle2,
    colorClass: 'text-amber-400',
    borderClass: 'border-amber-500/20',
    bgClass: 'bg-amber-500/5',
  },
}

function eventKey(event: ActivityEvent, index: number): string {
  return `${event.type}-${event.marketId}-${event.timestamp}-${index}`
}

function eventMessage(event: ActivityEvent): string {
  switch (event.type) {
    case 'bet':
      return `${event.address ?? 'Unknown'} bet ${event.amountQu != null ? formatQu(event.amountQu) : '?'} QU on ${event.option ?? 'Unknown'}`
    case 'market_created':
      return `New market: ${event.question ?? 'Unknown'}`
    case 'resolved':
      return `Resolved: ${event.question ?? 'Unknown'} \u2192 ${event.option ?? 'Unknown'}`
    default:
      return 'Unknown event'
  }
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

const POLL_INTERVAL = 15_000

export function LiveActivityFeed() {
  const [events, setEvents] = React.useState<ActivityEvent[]>([])
  const [prevCount, setPrevCount] = React.useState(0)

  const fetchActivity = React.useCallback(async () => {
    try {
      const res = await fetch('/api/predict/activity')
      if (!res.ok) return
      const data = await res.json()
      const latest: ActivityEvent[] = (data.events ?? []).slice(0, 5)

      setEvents((prev) => {
        setPrevCount(prev.length)
        return latest
      })
    } catch {
      // silently retry on next interval
    }
  }, [])

  React.useEffect(() => {
    let active = true
    const poll = () => {
      if (active) fetchActivity()
    }

    poll()
    const interval = setInterval(poll, POLL_INTERVAL)

    return () => {
      active = false
      clearInterval(interval)
    }
  }, [fetchActivity])

  return (
    <div className="rounded-lg border bg-card p-4">
      {/* Header */}
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">
          Recent Activity
        </h3>
        <div className="flex items-center gap-1.5">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
          </span>
          <span className="text-xs font-medium text-emerald-400">Live</span>
        </div>
      </div>

      {/* Event List */}
      {events.length === 0 ? (
        <p className="py-4 text-center text-xs text-muted-foreground">
          No recent activity
        </p>
      ) : (
        <div className="space-y-2">
          {events.map((event, index) => {
            const config = EVENT_CONFIG[event.type]
            const Icon = config.icon
            const isNew = index >= prevCount

            return (
              <div
                key={eventKey(event, index)}
                className={cn(
                  'flex items-start gap-2.5 rounded-md border p-2.5 transition-all',
                  config.borderClass,
                  config.bgClass,
                  isNew && 'animate-in slide-in-from-top-2 fade-in duration-300',
                )}
              >
                <Icon
                  className={cn('mt-0.5 h-3.5 w-3.5 shrink-0', config.colorClass)}
                />
                <div className="min-w-0 flex-1">
                  <p className="text-xs leading-relaxed text-foreground">
                    {eventMessage(event)}
                  </p>
                  <p className="mt-0.5 text-[10px] text-muted-foreground">
                    {relativeTime(event.timestamp)}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
