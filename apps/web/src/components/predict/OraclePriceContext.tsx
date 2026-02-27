'use client'

import { useState, useEffect, useRef } from 'react'
import { Activity, TrendingUp, TrendingDown, Minus } from 'lucide-react'

import { cn } from '@/lib/utils'
import { formatPrice } from './helpers'

interface OracleSource {
  name: string
  price: number
}

interface OraclePriceData {
  pair: string
  median: number
  sources: OracleSource[]
  fetchedAt: string
  sourceCount: number
}

interface OraclePriceContextProps {
  pair: string
  resolutionTarget: number
  resolutionType: string
  resolutionTargetHigh?: number | null
}

const POLL_INTERVAL_MS = 30_000

/**
 * Live Oracle Price Bar for market detail pages.
 *
 * Displays current median price from 4 oracle sources with a visual indicator
 * showing whether the price is above (green) or below (red) the target.
 * Auto-refreshes every 30 seconds, pauses when tab is hidden.
 */
export function OraclePriceContext({
  pair,
  resolutionTarget,
  resolutionType,
  resolutionTargetHigh,
}: OraclePriceContextProps) {
  const [data, setData] = useState<OraclePriceData | null>(null)
  const [error, setError] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchPrice = async () => {
    try {
      const res = await fetch(`/api/predict/oracle-price?pair=${encodeURIComponent(pair)}`)
      if (!res.ok) {
        setError(true)
        return
      }
      const json: OraclePriceData = await res.json()
      setData(json)
      setError(false)
    } catch {
      setError(true)
    }
  }

  useEffect(() => {
    fetchPrice()

    const startInterval = () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
      intervalRef.current = setInterval(fetchPrice, POLL_INTERVAL_MS)
    }

    startInterval()

    const handleVisibility = () => {
      if (document.visibilityState === 'hidden') {
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
          intervalRef.current = null
        }
      } else {
        fetchPrice()
        startInterval()
      }
    }

    document.addEventListener('visibilitychange', handleVisibility)

    return () => {
      document.removeEventListener('visibilitychange', handleVisibility)
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pair])

  if (error || !data) return null

  // Determine direction based on resolution type
  const isAbove = data.median > resolutionTarget
  const isBelow = data.median < resolutionTarget
  const isInRange =
    resolutionTargetHigh != null
      ? data.median >= resolutionTarget && data.median <= resolutionTargetHigh
      : false

  let directionColor = 'text-muted-foreground'
  let directionBg = 'bg-muted/50'
  let DirectionIcon = Minus

  if (resolutionType === 'above') {
    directionColor = isAbove ? 'text-emerald-400' : 'text-red-400'
    directionBg = isAbove ? 'bg-emerald-500/10' : 'bg-red-500/10'
    DirectionIcon = isAbove ? TrendingUp : TrendingDown
  } else if (resolutionType === 'below') {
    directionColor = isBelow ? 'text-emerald-400' : 'text-red-400'
    directionBg = isBelow ? 'bg-emerald-500/10' : 'bg-red-500/10'
    DirectionIcon = isBelow ? TrendingDown : TrendingUp
  } else if (resolutionType === 'range') {
    directionColor = isInRange ? 'text-emerald-400' : 'text-red-400'
    directionBg = isInRange ? 'bg-emerald-500/10' : 'bg-red-500/10'
    DirectionIcon = isInRange ? TrendingUp : TrendingDown
  }

  return (
    <div className={cn('rounded-lg border p-4', directionBg)}>
      {/* Header */}
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className={cn('h-4 w-4', directionColor)} />
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Live Oracle Price
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[10px] text-muted-foreground">
            {data.sourceCount} sources
          </span>
        </div>
      </div>

      {/* Median Price */}
      <div className="mb-3 flex items-center gap-3">
        <DirectionIcon className={cn('h-5 w-5', directionColor)} />
        <span className={cn('text-2xl font-bold', directionColor)}>
          ${formatPrice(data.median)}
        </span>
        <span className="text-xs text-muted-foreground">
          {pair.toUpperCase()} median
        </span>
      </div>

      {/* Per-Source Breakdown */}
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs">
        {data.sources.map((source) => (
          <div key={source.name} className="flex items-center gap-1.5">
            <span className="capitalize text-muted-foreground">
              {source.name}:
            </span>
            <span className="font-mono font-medium text-foreground">
              ${formatPrice(source.price)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
