'use client'

import { useState, useEffect, useRef } from 'react'
import { Activity, TrendingUp, TrendingDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatPrice } from './helpers'

interface PriceSource {
  name: string
  price: number
}

interface LivePriceBarProps {
  pair: string
  pollIntervalMs?: number
}

export function LivePriceBar({ pair, pollIntervalMs = 3000 }: LivePriceBarProps) {
  const [price, setPrice] = useState<number | null>(null)
  const [sources, setSources] = useState<PriceSource[]>([])
  const [prevPrice, setPrevPrice] = useState<number | null>(null)
  const [error, setError] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchPrice = async () => {
    try {
      const res = await fetch(`/api/qflash/price?pair=${encodeURIComponent(pair)}`)
      if (!res.ok) {
        setError(true)
        return
      }
      const data = await res.json()
      setPrevPrice(price)
      setPrice(data.medianPrice)
      setSources(data.sources ?? [])
      setError(false)
    } catch {
      setError(true)
    }
  }

  useEffect(() => {
    fetchPrice()

    const start = () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
      intervalRef.current = setInterval(fetchPrice, pollIntervalMs)
    }
    start()

    const handleVis = () => {
      if (document.visibilityState === 'hidden') {
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
          intervalRef.current = null
        }
      } else {
        fetchPrice()
        start()
      }
    }
    document.addEventListener('visibilitychange', handleVis)

    return () => {
      document.removeEventListener('visibilitychange', handleVis)
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pair, pollIntervalMs])

  if (error || price === null) {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-border/50 bg-card/50 px-4 py-3">
        <Activity className="h-4 w-4 text-muted-foreground animate-pulse" />
        <span className="text-sm text-muted-foreground">Loading price...</span>
      </div>
    )
  }

  const direction = prevPrice !== null
    ? price > prevPrice ? 'up' : price < prevPrice ? 'down' : 'flat'
    : 'flat'

  return (
    <div className="rounded-lg border border-border/50 bg-card/50 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              LIVE
            </span>
          </div>
          <div className="flex items-center gap-2">
            {direction === 'up' && <TrendingUp className="h-5 w-5 text-emerald-400" />}
            {direction === 'down' && <TrendingDown className="h-5 w-5 text-red-400" />}
            <span
              className={cn(
                'text-2xl font-bold font-mono tabular-nums transition-colors',
                direction === 'up' ? 'text-emerald-400' : direction === 'down' ? 'text-red-400' : 'text-foreground',
              )}
            >
              ${formatPrice(price)}
            </span>
          </div>
          <span className="text-xs text-muted-foreground">
            {pair.toUpperCase()}
          </span>
        </div>

        {/* Source breakdown */}
        <div className="hidden sm:flex gap-3 text-[10px]">
          {sources.map((s) => (
            <div key={s.name} className="flex items-center gap-1">
              <span className="capitalize text-muted-foreground">{s.name}:</span>
              <span className="font-mono text-foreground/80">${formatPrice(s.price)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
