'use client'

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts'
import { TrendingUp } from 'lucide-react'

interface TimelineEvent {
  year: number
  satoshiActivity: number
  cfbActivity: number
  qubicActivity: number
  event?: string
}

const timelineData: TimelineEvent[] = [
  { year: 2007, satoshiActivity: 20, cfbActivity: 30, qubicActivity: 0 },
  { year: 2008, satoshiActivity: 80, cfbActivity: 60, qubicActivity: 0, event: 'Bitcoin Whitepaper' },
  { year: 2009, satoshiActivity: 100, cfbActivity: 40, qubicActivity: 0, event: 'Genesis Block' },
  { year: 2010, satoshiActivity: 90, cfbActivity: 35, qubicActivity: 0 },
  { year: 2011, satoshiActivity: 20, cfbActivity: 45, qubicActivity: 0, event: 'Satoshi Disappears' },
  { year: 2012, satoshiActivity: 0, cfbActivity: 70, qubicActivity: 0, event: 'NXT Development' },
  { year: 2013, satoshiActivity: 0, cfbActivity: 95, qubicActivity: 0, event: 'NXT Launch' },
  { year: 2014, satoshiActivity: 0, cfbActivity: 85, qubicActivity: 0 },
  { year: 2015, satoshiActivity: 0, cfbActivity: 75, qubicActivity: 20, event: 'IOTA Founded' },
  { year: 2016, satoshiActivity: 0, cfbActivity: 80, qubicActivity: 30 },
  { year: 2017, satoshiActivity: 0, cfbActivity: 70, qubicActivity: 40 },
  { year: 2018, satoshiActivity: 0, cfbActivity: 60, qubicActivity: 50, event: 'Qubic Announced' },
  { year: 2019, satoshiActivity: 0, cfbActivity: 55, qubicActivity: 60 },
  { year: 2020, satoshiActivity: 0, cfbActivity: 50, qubicActivity: 65 },
  { year: 2021, satoshiActivity: 0, cfbActivity: 45, qubicActivity: 70 },
  { year: 2022, satoshiActivity: 0, cfbActivity: 50, qubicActivity: 80, event: 'Qubic Mainnet' },
  { year: 2023, satoshiActivity: 0, cfbActivity: 55, qubicActivity: 90 },
  { year: 2024, satoshiActivity: 0, cfbActivity: 60, qubicActivity: 95 },
  { year: 2025, satoshiActivity: 0, cfbActivity: 65, qubicActivity: 100, event: 'GENESIS Burn' },
  { year: 2026, satoshiActivity: 0, cfbActivity: 70, qubicActivity: 100, event: 'Time-Lock Opens?' },
]

const keyEvents = [
  { year: 2008, label: 'Whitepaper', color: '#f59e0b' },
  { year: 2009, label: 'Genesis', color: '#10b981' },
  { year: 2011, label: 'Exit', color: '#ef4444' },
  { year: 2013, label: 'NXT', color: '#6366f1' },
  { year: 2022, label: 'Qubic', color: '#06b6d4' },
  { year: 2026, label: 'Reveal?', color: '#f59e0b' },
]

export function TimelineChart() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })

  return (
    <section ref={sectionRef} className="py-20 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <TrendingUp className="h-8 w-8 text-cyan-400" />
            <h2 className="text-display-md font-semibold">Activity Timeline</h2>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto text-body-lg">
            Correlation of Satoshi, CFB, and Qubic activity from 2007 to 2026.
            Notice the inverse relationship between Satoshi and CFB public activity.
          </p>
        </motion.div>

        {/* Chart */}
        <motion.div
          className="mb-8 p-6 rounded-2xl border bg-gradient-to-br from-zinc-900 to-zinc-950 border-zinc-800"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={timelineData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="satoshiGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="cfbGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="qubicGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
              <XAxis
                dataKey="year"
                stroke="#71717a"
                tick={{ fill: '#a1a1aa', fontSize: 12 }}
                tickLine={{ stroke: '#52525b' }}
              />
              <YAxis
                stroke="#71717a"
                tick={{ fill: '#a1a1aa', fontSize: 12 }}
                tickLine={{ stroke: '#52525b' }}
                label={{
                  value: 'Activity Level',
                  angle: -90,
                  position: 'insideLeft',
                  fill: '#71717a',
                  fontSize: 12
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#18181b',
                  border: '1px solid #3f3f46',
                  borderRadius: '8px',
                  color: '#fff'
                }}
                formatter={(value, name) => {
                  const labels: Record<string, string> = {
                    satoshiActivity: 'Satoshi',
                    cfbActivity: 'CFB',
                    qubicActivity: 'Qubic'
                  }
                  return [value, labels[name as string] || name]
                }}
                labelFormatter={(year) => {
                  const event = timelineData.find(d => d.year === year)?.event
                  return event ? `${year} - ${event}` : year.toString()
                }}
              />

              {/* Reference lines for key events */}
              {keyEvents.map((event) => (
                <ReferenceLine
                  key={event.year}
                  x={event.year}
                  stroke={event.color}
                  strokeDasharray="5 5"
                  strokeOpacity={0.5}
                />
              ))}

              <Area
                type="monotone"
                dataKey="satoshiActivity"
                stroke="#f59e0b"
                fillOpacity={1}
                fill="url(#satoshiGradient)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="cfbActivity"
                stroke="#10b981"
                fillOpacity={1}
                fill="url(#cfbGradient)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="qubicActivity"
                stroke="#06b6d4"
                fillOpacity={1}
                fill="url(#qubicGradient)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Legend */}
        <motion.div
          className="flex flex-wrap items-center justify-center gap-8 mb-8"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-amber-500" />
            <span className="text-muted-foreground text-sm">Satoshi Nakamoto</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-emerald-500" />
            <span className="text-muted-foreground text-sm">CFB (Sergey)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-cyan-500" />
            <span className="text-muted-foreground text-sm">Qubic Project</span>
          </div>
        </motion.div>

        {/* Key Events Timeline */}
        <motion.div
          className="p-4 rounded-xl bg-zinc-950 border border-zinc-800"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <h4 className="text-xs text-muted-foreground mb-3">KEY EVENTS</h4>
          <div className="flex flex-wrap items-center gap-2">
            {keyEvents.map((event, idx) => (
              <div
                key={event.year}
                className="flex items-center gap-2"
              >
                <div
                  className="px-3 py-1.5 rounded-lg text-xs font-medium"
                  style={{
                    backgroundColor: `${event.color}20`,
                    color: event.color,
                    borderColor: event.color,
                    borderWidth: 1
                  }}
                >
                  {event.year}: {event.label}
                </div>
                {idx < keyEvents.length - 1 && (
                  <div className="w-4 h-px bg-zinc-700 hidden sm:block" />
                )}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Insight Box */}
        <motion.div
          className="mt-8 p-6 rounded-xl bg-amber-900/20 border border-amber-800"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h4 className="text-sm font-medium text-amber-300 mb-2">Key Observation</h4>
          <p className="text-sm text-amber-200/70 leading-relaxed">
            Notice how Satoshi's activity drops to zero exactly as CFB's NXT development peaks in 2011-2012.
            This inverse correlation, combined with the stylometric match, suggests continuity of the same
            developer shifting focus between projects. The upcoming 2026 time-lock date may be significant.
          </p>
        </motion.div>
      </div>
    </section>
  )
}
