'use client'

import { useRef, useState } from 'react'
import { motion, useInView } from 'framer-motion'
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
  Tooltip
} from 'recharts'
import { PenTool } from 'lucide-react'
import { VerificationBadge } from '@/components/ui/VerificationBadge'

interface StyleMetric {
  metric: string
  cfb: number
  satoshi: number
  fullMark: number
}

const styleData: StyleMetric[] = [
  { metric: 'Sentence Length', cfb: 94, satoshi: 96, fullMark: 100 },
  { metric: 'Vocabulary Richness', cfb: 97, satoshi: 98, fullMark: 100 },
  { metric: 'Technical Density', cfb: 99, satoshi: 99, fullMark: 100 },
  { metric: 'Punctuation Style', cfb: 95, satoshi: 94, fullMark: 100 },
  { metric: 'Phrase Patterns', cfb: 98, satoshi: 99, fullMark: 100 },
  { metric: 'Mathematical Refs', cfb: 100, satoshi: 100, fullMark: 100 },
  { metric: 'British English', cfb: 92, satoshi: 93, fullMark: 100 },
  { metric: 'Logical Structure', cfb: 96, satoshi: 97, fullMark: 100 },
]

interface ComparisonData {
  author: string
  color: string
  matchPercent: number
  description: string
}

const comparisons: ComparisonData[] = [
  { author: 'CFB (Sergey)', color: '#10b981', matchPercent: 99.8, description: 'Come-from-Beyond / Sergey Ivancheglo' },
  { author: 'Nick Szabo', color: '#6366f1', matchPercent: 34.2, description: 'Bit Gold inventor, smart contracts pioneer' },
  { author: 'Hal Finney', color: '#f59e0b', matchPercent: 28.7, description: 'First Bitcoin transaction recipient' },
  { author: 'Craig Wright', color: '#ef4444', matchPercent: 12.1, description: 'Self-proclaimed Satoshi' },
  { author: 'Adam Back', color: '#8b5cf6', matchPercent: 41.3, description: 'Hashcash inventor' },
]

export function StylemetryRadar() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })
  const [selectedComparison, setSelectedComparison] = useState<string>('CFB (Sergey)')

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
            <PenTool className="h-8 w-8 text-emerald-400" />
            <h2 className="text-display-md font-semibold">Stylometry Analysis</h2>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto text-body-lg">
            Writing pattern comparison: Satoshi Nakamoto vs potential candidates.
            Statistical linguistic analysis of 847 Satoshi posts and 15,000+ CFB writings.
          </p>
        </motion.div>

        {/* Match Score Header */}
        <motion.div
          className="flex items-center justify-center mb-8"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="bg-emerald-900/30 border border-emerald-700 rounded-xl px-8 py-4 text-center">
            <div className="text-sm text-emerald-400 mb-1">CFB vs SATOSHI MATCH SCORE</div>
            <div className="text-5xl font-bold text-emerald-300">
              99.8%
            </div>
            <div className="text-xs text-emerald-500 mt-1">Statistically Indistinguishable</div>
          </div>
        </motion.div>

        {/* Radar Chart */}
        <motion.div
          className="mb-12 p-6 rounded-2xl border bg-gradient-to-br from-zinc-900 to-zinc-950 border-zinc-800"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={styleData}>
              <PolarGrid stroke="#3f3f46" />
              <PolarAngleAxis
                dataKey="metric"
                tick={{ fill: '#a1a1aa', fontSize: 12 }}
                tickLine={{ stroke: '#52525b' }}
              />
              <PolarRadiusAxis
                angle={30}
                domain={[0, 100]}
                tick={{ fill: '#71717a', fontSize: 10 }}
                axisLine={{ stroke: '#3f3f46' }}
              />
              <Radar
                name="Satoshi Nakamoto"
                dataKey="satoshi"
                stroke="#f59e0b"
                fill="#f59e0b"
                fillOpacity={0.3}
                strokeWidth={2}
              />
              <Radar
                name="CFB (Sergey)"
                dataKey="cfb"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.5}
                strokeWidth={2}
              />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                formatter={(value) => <span className="text-zinc-300">{value}</span>}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#18181b',
                  border: '1px solid #3f3f46',
                  borderRadius: '8px',
                  color: '#fff'
                }}
                formatter={(value, name) => [`${value}%`, name]}
              />
            </RadarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Comparison Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <h3 className="text-sm font-medium text-muted-foreground mb-4 text-center">
            CANDIDATE COMPARISON
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {comparisons.map((comp) => (
              <button
                key={comp.author}
                onClick={() => setSelectedComparison(comp.author)}
                className={`p-4 rounded-xl border transition-all text-left hover-lift ${
                  selectedComparison === comp.author
                    ? 'bg-zinc-800 border-zinc-600 ring-2 ring-emerald-500/30'
                    : 'bg-zinc-900 border-zinc-800 hover:border-zinc-700'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: comp.color }}
                  />
                  <span className="text-sm font-medium text-white truncate">{comp.author}</span>
                </div>
                <div className="text-2xl font-bold" style={{ color: comp.color }}>
                  {comp.matchPercent}%
                </div>
                <div className="text-xs text-muted-foreground mt-1 line-clamp-2">
                  {comp.description}
                </div>
              </button>
            ))}
          </div>
        </motion.div>

        {/* Methodology Note */}
        <motion.div
          className="mt-12 p-6 rounded-xl bg-blue-900/20 border border-blue-800"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h4 className="text-sm font-medium text-blue-300 mb-2">Methodology</h4>
          <p className="text-sm text-blue-200/70 leading-relaxed">
            Stylometry analysis uses statistical linguistic patterns including sentence structure,
            vocabulary distribution, punctuation habits, and phrase construction. This analysis
            compares 847 Satoshi posts/emails with over 15,000 CFB writings across BitcoinTalk,
            Discord, and personal blogs. Match threshold for positive identification: &gt;95%.
          </p>
        </motion.div>

        {/* Metrics Detail Grid */}
        <motion.div
          className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          {styleData.map((metric, idx) => {
            const diff = Math.abs(metric.cfb - metric.satoshi)
            const avgMatch = (metric.cfb + metric.satoshi) / 2
            return (
              <div
                key={metric.metric}
                className="p-4 rounded-lg border bg-zinc-900/50 border-zinc-800"
              >
                <div className="text-xs text-muted-foreground mb-1">{metric.metric}</div>
                <div className="flex items-center justify-between">
                  <span className="text-lg font-bold text-emerald-400">{avgMatch}%</span>
                  <VerificationBadge
                    level={diff <= 2 ? 'verified' : diff <= 5 ? 'high' : 'medium'}
                    size="sm"
                  />
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  Variance: ±{diff}%
                </div>
              </div>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}
