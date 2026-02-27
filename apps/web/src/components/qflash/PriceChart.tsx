'use client'

import { useMemo } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import { useAutoRefresh } from '@/hooks/useAutoRefresh'
import { formatPrice } from './helpers'

interface PriceTick {
  timestamp: number
  price: number
  pair: string
}

interface PriceChartProps {
  pair: string
  openingPrice?: number | null
  pollIntervalMs?: number
}

interface PriceApiResponse {
  medianPrice: number
  history: PriceTick[]
}

export function PriceChart({
  pair,
  openingPrice,
  pollIntervalMs = 3000,
}: PriceChartProps) {
  const { data } = useAutoRefresh<PriceApiResponse>(
    async () => {
      const res = await fetch(
        `/api/qflash/price?pair=${encodeURIComponent(pair)}&history=120`,
      )
      if (!res.ok) throw new Error('Failed to fetch price')
      return res.json()
    },
    pollIntervalMs,
    [pair],
  )

  const ticks = data?.history ?? []
  const currentPrice = data?.medianPrice ?? 0

  // Format chart data
  const chartData = useMemo(() => {
    return ticks.map((tick) => ({
      time: tick.timestamp,
      price: tick.price,
    }))
  }, [ticks])

  // Calculate price domain with padding
  const [minPrice, maxPrice] = useMemo(() => {
    if (chartData.length === 0) return [0, 0]
    const prices = chartData.map((d) => d.price)
    if (openingPrice != null) prices.push(openingPrice)
    const min = Math.min(...prices)
    const max = Math.max(...prices)
    const padding = (max - min) * 0.15 || max * 0.001
    return [min - padding, max + padding]
  }, [chartData, openingPrice])

  // Determine trend: green if current > opening, red if lower
  const isUp =
    openingPrice != null && currentPrice > 0
      ? currentPrice >= openingPrice
      : true

  if (chartData.length < 2) {
    return (
      <div className="flex h-40 items-center justify-center rounded-lg border border-border/50 bg-card/50">
        <p className="text-xs text-muted-foreground">
          Collecting price data...
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-border/50 bg-card/50 p-2">
      <ResponsiveContainer width="100%" height={160}>
        <AreaChart
          data={chartData}
          margin={{ top: 4, right: 4, bottom: 0, left: 4 }}
        >
          <defs>
            <linearGradient id="priceGradientUp" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22c55e" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#22c55e" stopOpacity={0.02} />
            </linearGradient>
            <linearGradient
              id="priceGradientDown"
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >
              <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#ef4444" stopOpacity={0.02} />
            </linearGradient>
          </defs>

          <XAxis
            dataKey="time"
            type="number"
            domain={['dataMin', 'dataMax']}
            tickFormatter={(ts: number) => {
              const d = new Date(ts)
              return `${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
            }}
            tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
            axisLine={false}
            tickLine={false}
            minTickGap={40}
          />

          <YAxis
            domain={[minPrice, maxPrice]}
            tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
            tickFormatter={(v: number) => formatPrice(v)}
            axisLine={false}
            tickLine={false}
            width={65}
          />

          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null
              const point = payload[0]!
              const price = point.value as number
              const ts = point.payload?.time as number
              return (
                <div className="rounded-md border bg-popover px-2.5 py-1.5 text-xs shadow-sm">
                  <p className="font-mono font-semibold">
                    ${formatPrice(price)}
                  </p>
                  <p className="text-muted-foreground">
                    {new Date(ts).toLocaleTimeString()}
                  </p>
                </div>
              )
            }}
          />

          {/* Opening price reference line */}
          {openingPrice != null && (
            <ReferenceLine
              y={openingPrice}
              stroke="hsl(var(--muted-foreground))"
              strokeDasharray="4 4"
              strokeOpacity={0.5}
            />
          )}

          <Area
            type="monotone"
            dataKey="price"
            stroke={isUp ? '#22c55e' : '#ef4444'}
            strokeWidth={1.5}
            fill={isUp ? 'url(#priceGradientUp)' : 'url(#priceGradientDown)'}
            dot={false}
            activeDot={{
              r: 3,
              fill: isUp ? '#22c55e' : '#ef4444',
              stroke: 'hsl(var(--background))',
              strokeWidth: 2,
            }}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
