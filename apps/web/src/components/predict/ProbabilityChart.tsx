'use client'

import * as React from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

import type { MarketSnapshot } from './types'

interface ProbabilityChartProps {
  snapshots: MarketSnapshot[]
  currentProbability: number
}

interface ChartDataPoint {
  time: string
  yesProbability: number
  noProbability: number
}

function formatChartTime(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function ProbabilityChart({
  snapshots,
  currentProbability,
}: ProbabilityChartProps) {
  const data: ChartDataPoint[] = React.useMemo(() => {
    if (snapshots.length === 0) {
      // Show a single point at the current probability
      return [
        {
          time: 'Now',
          yesProbability: Math.round(currentProbability * 100),
          noProbability: Math.round((1 - currentProbability) * 100),
        },
      ]
    }

    return snapshots.map((s) => ({
      time: formatChartTime(s.timestamp),
      yesProbability: Math.round(s.impliedProbability * 100),
      noProbability: Math.round((1 - s.impliedProbability) * 100),
    }))
  }, [snapshots, currentProbability])

  if (data.length <= 1) {
    return (
      <div className="flex h-48 items-center justify-center rounded-lg border bg-card">
        <p className="text-sm text-muted-foreground">
          Chart will appear after multiple bets are placed.
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="mb-4 text-sm font-semibold text-foreground">
        Probability Over Time
      </h3>
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="yesGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#10b981" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="hsl(var(--muted-foreground))"
            strokeOpacity={0.15}
          />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v: number) => `${v}%`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'hsl(var(--card))',
              border: '1px solid hsl(var(--border))',
              borderRadius: '8px',
              fontSize: '12px',
            }}
            formatter={(value, name) => [
              `${value ?? 0}%`,
              String(name) === 'yesProbability' ? 'Yes' : 'No',
            ]}
          />
          <Area
            type="monotone"
            dataKey="yesProbability"
            stroke="#10b981"
            strokeWidth={2}
            fill="url(#yesGrad)"
            name="yesProbability"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
