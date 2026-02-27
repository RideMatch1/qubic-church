'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts'

interface Prediction {
  id: string
  type?: string
  pair?: string
  direction?: string
  threshold?: number
  horizon?: string
  horizonHours?: number
  priceAtCommit?: number
  confidence?: number | string
  status: string
  commitTick?: number
  targetTick?: number
  commitHash?: string
  commitTimestamp?: string
  oracleName?: string
  expiresAt?: string
  committedAt?: string
  timestamp?: string
  outcome?: string
  priceAtExpiry?: number
  strategy?: string
  message?: string
  encrypted?: string
  row?: number
  col?: number
}

interface PredictionStats {
  total: number
  real: number
  symbolic: number
  correct: number
  incorrect: number
  committed: number
  revealed: number
  accuracy: number | null
}

interface PerformanceRow {
  strategy?: string
  pair?: string
  horizon_hours?: number
  total: number
  correct: number
  incorrect: number
  accuracy: number | null
}

interface StrategyInfo {
  name: string
  type: string
  description: string
  isActive: boolean
  accuracy: number | null
  totalPredictions: number
  correctPredictions: number
  lastUsed: string | null
}

interface AccuracyPoint {
  date: string
  accuracy: number
  total: number
  correct: number
}

interface ConfCalBin {
  bin: string
  total: number
  correct: number
  accuracy: number | null
}

interface PairHorizonCell {
  pair: string
  horizon: number
  total: number
  correct: number
  accuracy: number | null
}

interface StreakAnalysis {
  maxWin: number
  maxLoss: number
  currentStreak: number
  currentType: string | null
  distribution: Record<string, number>
}

interface BacktestResult {
  strategy: string
  accuracy: number | null
  totalTrades: number
  correctTrades: number
  sharpe?: number | null
  profitFactor?: number | null
  createdAt: string
}

interface OracleInfo {
  name: string
  pairsTracked: number
  totalSnapshots: number
  firstSeen: string
  lastSeen: string
}

interface SpreadInfo {
  pair: string
  oracleHigh: string
  oracleLow: string
  priceHigh: number
  priceLow: number
  spreadPct: number
  oracleCount: number
}

interface PairCoverageInfo {
  pair: string
  oracles: string[]
  oracleCount: number
  snapshotCount: number
}

interface OracleExplorer {
  oracles: OracleInfo[]
  spreads: SpreadInfo[]
  pairCoverage: PairCoverageInfo[]
}

interface CostEfficiency {
  totalCostQU: number
  revealCostQU: number
  totalSpentQU: number
  costPerCorrect: number | null
  totalRevealed: number
  totalCommitted: number
}

interface PredictionData {
  predictions: Prediction[]
  stats: PredictionStats
  strategyPerformance?: PerformanceRow[]
  pairPerformance?: PerformanceRow[]
  horizonPerformance?: PerformanceRow[]
  accuracyOverTime?: AccuracyPoint[]
  confidenceCalibration?: ConfCalBin[]
  pairHorizonMatrix?: PairHorizonCell[]
  streakAnalysis?: StreakAnalysis | null
  backtestResults?: BacktestResult[]
  strategies?: StrategyInfo[]
  oracleExplorer?: OracleExplorer | null
  costEfficiency?: CostEfficiency | null
  lastUpdated: string | null
}

type TabKey = 'predictions' | 'strategies' | 'pairs' | 'horizons' | 'analytics' | 'arbitrage' | 'explorer'

const ease = [0.22, 1, 0.36, 1] as const

export function OraclePredictionTracker() {
  const [data, setData] = useState<PredictionData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<TabKey>('predictions')

  const fetchPredictions = useCallback(async () => {
    try {
      const res = await fetch('/api/oracle/predictions')
      const json = await res.json()
      if (json.data) {
        setData(json.data)
        setError(null)
      } else {
        setError(json.message ?? 'No data')
      }
    } catch {
      setError('Failed to load predictions')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchPredictions()
    const interval = setInterval(fetchPredictions, 15000)
    return () => clearInterval(interval)
  }, [fetchPredictions])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-5 h-5 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-zinc-500 text-sm">{error ?? 'No predictions yet'}</p>
        <p className="text-zinc-600 text-xs mt-2 font-mono">
          Run: node scripts/ORACLE_PROPHECY.mjs commit --pair btc/usdt --dir up --target 70000 --horizon 24h
        </p>
      </div>
    )
  }

  const { stats } = data
  const hasAnalytics = (data.strategyPerformance?.length ?? 0) > 0

  const hasExplorer = !!data.oracleExplorer?.oracles?.length
  const hasSpreads = !!data.oracleExplorer?.spreads?.length

  const tabs: { key: TabKey; label: string }[] = [
    { key: 'predictions', label: 'Predictions' },
    ...(hasAnalytics ? [
      { key: 'strategies' as TabKey, label: 'Strategies' },
      { key: 'pairs' as TabKey, label: 'Pairs' },
      { key: 'horizons' as TabKey, label: 'Horizons' },
      { key: 'analytics' as TabKey, label: 'Analytics' },
    ] : []),
    ...(hasSpreads ? [{ key: 'arbitrage' as TabKey, label: 'Arbitrage' }] : []),
    ...(hasExplorer ? [{ key: 'explorer' as TabKey, label: 'Explorer' }] : []),
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease }}
    >
      {/* Accuracy Ring + Stats */}
      <div className="flex items-start gap-6 mb-5">
        <div className="flex-shrink-0 relative w-20 h-20">
          <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
            <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="4" />
            <circle
              cx="40" cy="40" r="34"
              fill="none"
              stroke={stats.accuracy !== null && stats.accuracy >= 60 ? '#34d399' : stats.accuracy !== null ? '#f59e0b' : '#52525b'}
              strokeWidth="4"
              strokeDasharray={`${(stats.accuracy ?? 0) * 2.136} 213.6`}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="font-mono text-lg text-zinc-200">
              {stats.accuracy !== null ? `${stats.accuracy}%` : '--'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-xs">
          <StatRow label="Total" value={stats.total} />
          <StatRow label="Correct" value={stats.correct} color="emerald" />
          <StatRow label="Committed" value={stats.committed} color="cyan" />
          <StatRow label="Incorrect" value={stats.incorrect} color="red" />
        </div>
      </div>

      {/* Tabs */}
      {tabs.length > 1 && (
        <div className="flex gap-1 mb-4 border-b border-zinc-800">
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-3 py-1.5 text-[10px] uppercase tracking-[0.15em] font-medium transition-colors ${
                activeTab === tab.key
                  ? 'text-cyan-400 border-b-2 border-cyan-400 -mb-px'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      )}

      {/* Tab Content */}
      {activeTab === 'predictions' && <PredictionsTab predictions={data.predictions} />}
      {activeTab === 'strategies' && <StrategiesTab performance={data.strategyPerformance ?? []} strategies={data.strategies ?? []} />}
      {activeTab === 'pairs' && <PerformanceTable rows={data.pairPerformance ?? []} labelKey="pair" />}
      {activeTab === 'horizons' && <PerformanceTable rows={data.horizonPerformance ?? []} labelKey="horizon_hours" suffix="h" />}
      {activeTab === 'analytics' && (
        <AnalyticsTab
          accuracyOverTime={data.accuracyOverTime ?? []}
          strategyPerformance={data.strategyPerformance ?? []}
          predictions={data.predictions}
          confidenceCalibration={data.confidenceCalibration ?? []}
          pairHorizonMatrix={data.pairHorizonMatrix ?? []}
          streakAnalysis={data.streakAnalysis ?? null}
          backtestResults={data.backtestResults ?? []}
          costEfficiency={data.costEfficiency ?? null}
        />
      )}
      {activeTab === 'arbitrage' && data.oracleExplorer && (
        <ArbitrageTab spreads={data.oracleExplorer.spreads} />
      )}
      {activeTab === 'explorer' && data.oracleExplorer && (
        <ExplorerTab explorer={data.oracleExplorer} />
      )}
    </motion.div>
  )
}

// =============================================================================
// TABS
// =============================================================================

function PredictionsTab({ predictions }: { predictions: Prediction[] }) {
  return (
    <div className="space-y-2">
      <AnimatePresence>
        {predictions.slice(0, 12).map((p, i) => (
          <PredictionCard key={p.id} prediction={p} index={i} />
        ))}
      </AnimatePresence>
    </div>
  )
}

function StrategiesTab({ performance, strategies }: { performance: PerformanceRow[]; strategies: StrategyInfo[] }) {
  return (
    <div className="space-y-3">
      {performance.map((row) => {
        const strat = strategies.find(s => s.name === row.strategy)
        const resolved = row.correct + row.incorrect
        const accuracy = resolved > 0 ? row.accuracy : null

        return (
          <div key={row.strategy} className="rounded-lg border border-zinc-800 p-3">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-zinc-200">{row.strategy}</span>
                {strat?.isActive && (
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-400/10 text-cyan-400 uppercase tracking-wider">Active</span>
                )}
              </div>
              <span className={`font-mono text-sm ${
                accuracy !== null && accuracy >= 60 ? 'text-emerald-400' :
                accuracy !== null && accuracy > 0 ? 'text-amber-400' :
                'text-zinc-500'
              }`}>
                {accuracy !== null ? `${accuracy}%` : '--'}
              </span>
            </div>

            {strat?.description && (
              <p className="text-[10px] text-zinc-600 mb-2">{strat.description}</p>
            )}

            <div className="flex gap-4 text-[10px]">
              <span className="text-zinc-500">Total: <span className="text-zinc-300">{row.total}</span></span>
              <span className="text-zinc-500">Correct: <span className="text-emerald-400">{row.correct}</span></span>
              <span className="text-zinc-500">Incorrect: <span className="text-red-400">{row.incorrect}</span></span>
              {resolved > 0 && (
                <span className="text-zinc-500">Resolved: <span className="text-zinc-300">{resolved}</span></span>
              )}
            </div>

            {/* Accuracy bar */}
            {resolved > 0 && (
              <div className="mt-2 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    accuracy !== null && accuracy >= 60 ? 'bg-emerald-400' :
                    accuracy !== null ? 'bg-amber-400' :
                    'bg-zinc-600'
                  }`}
                  style={{ width: `${accuracy ?? 0}%` }}
                />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

function AnalyticsTab({
  accuracyOverTime,
  strategyPerformance,
  predictions,
  confidenceCalibration,
  pairHorizonMatrix,
  streakAnalysis,
  backtestResults,
  costEfficiency,
}: {
  accuracyOverTime: AccuracyPoint[]
  strategyPerformance: PerformanceRow[]
  predictions: Prediction[]
  confidenceCalibration: ConfCalBin[]
  pairHorizonMatrix: PairHorizonCell[]
  streakAnalysis: StreakAnalysis | null
  backtestResults: BacktestResult[]
  costEfficiency: CostEfficiency | null
}) {
  // Build strategy comparison data for bar chart
  const strategyBars = strategyPerformance
    .filter(s => (s.correct + s.incorrect) > 0)
    .map(s => ({
      name: s.strategy ?? '?',
      accuracy: s.accuracy ?? 0,
      total: s.total,
    }))

  // Build prediction timeline from recent predictions
  const timeline = predictions
    .filter(p => p.commitTimestamp)
    .slice(0, 30)
    .map(p => {
      const ts = p.commitTimestamp ? new Date(p.commitTimestamp) : new Date()
      return {
        time: `${ts.getMonth() + 1}/${ts.getDate()} ${String(ts.getHours()).padStart(2, '0')}:${String(ts.getMinutes()).padStart(2, '0')}`,
        confidence: typeof p.confidence === 'number' ? p.confidence * 100 : 50,
        status: p.status,
        pair: p.pair ?? '?',
      }
    })
    .reverse()

  // Build confidence calibration chart data
  const calData = confidenceCalibration.map(b => ({
    bin: b.bin,
    accuracy: b.accuracy ?? 0,
    total: b.total,
  }))

  // Build pair-horizon heatmap data
  const uniquePairs = [...new Set(pairHorizonMatrix.map(c => c.pair))].sort()
  const uniqueHorizons = [...new Set(pairHorizonMatrix.map(c => c.horizon))].sort((a, b) => a - b)

  const tooltipStyle = {
    contentStyle: { background: '#18181b', border: '1px solid #3f3f46', borderRadius: 8, fontSize: 11 },
    labelStyle: { color: '#a1a1aa' },
  }

  const getHeatColor = (acc: number | null) => {
    if (acc == null) return 'bg-zinc-800/50'
    if (acc >= 70) return 'bg-emerald-500/60'
    if (acc >= 55) return 'bg-emerald-500/30'
    if (acc >= 45) return 'bg-yellow-500/30'
    return 'bg-red-500/30'
  }

  return (
    <div className="space-y-6">
      {/* Accuracy Over Time */}
      {accuracyOverTime.length > 0 && (
        <div>
          <h4 className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 mb-3">Accuracy Over Time</h4>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={accuracyOverTime}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#71717a' }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#71717a' }} width={32} />
                <Tooltip {...tooltipStyle} />
                <Line type="monotone" dataKey="accuracy" stroke="#34d399" strokeWidth={2} dot={{ r: 3, fill: '#34d399' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Strategy Comparison */}
      {strategyBars.length > 0 && (
        <div>
          <h4 className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 mb-3">Strategy Comparison</h4>
          <div className="h-36">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={strategyBars}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#71717a' }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#71717a' }} width={32} />
                <Tooltip {...tooltipStyle} />
                <Bar dataKey="accuracy" fill="#22d3ee" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Confidence Calibration */}
      {calData.length > 0 && (
        <div>
          <h4 className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 mb-3">Confidence Calibration</h4>
          <p className="text-[9px] text-zinc-600 mb-2">Does higher confidence = higher accuracy? Diagonal = perfectly calibrated.</p>
          <div className="h-36">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={calData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="bin" tick={{ fontSize: 9, fill: '#71717a' }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#71717a' }} width={32} />
                <Tooltip
                  {...tooltipStyle}
                  formatter={(value: number | undefined) => [
                    value != null ? `${Number(value).toFixed(1)}%` : '--',
                    'Accuracy',
                  ]}
                />
                <Bar dataKey="accuracy" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Pair x Horizon Heatmap */}
      {pairHorizonMatrix.length > 0 && (
        <div>
          <h4 className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 mb-3">Pair x Horizon Performance</h4>
          <div className="overflow-x-auto">
            <div className="inline-grid gap-px" style={{ gridTemplateColumns: `80px repeat(${uniqueHorizons.length}, 56px)` }}>
              {/* Header row */}
              <div className="text-[9px] text-zinc-600 p-1" />
              {uniqueHorizons.map(h => (
                <div key={h} className="text-[9px] text-zinc-500 text-center p-1 font-medium">{h}h</div>
              ))}
              {/* Data rows */}
              {uniquePairs.map(pair => (
                <>
                  <div key={pair} className="text-[9px] text-zinc-400 p-1 truncate">{pair}</div>
                  {uniqueHorizons.map(h => {
                    const cell = pairHorizonMatrix.find(c => c.pair === pair && c.horizon === h)
                    return (
                      <div
                        key={`${pair}-${h}`}
                        className={`text-[9px] text-center p-1 rounded-sm ${getHeatColor(cell?.accuracy ?? null)}`}
                        title={cell ? `${cell.correct}/${cell.total} = ${cell.accuracy}%` : 'No data'}
                      >
                        {cell?.accuracy != null ? `${cell.accuracy}%` : '-'}
                      </div>
                    )
                  })}
                </>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Streak Analysis */}
      {streakAnalysis && (streakAnalysis.maxWin > 0 || streakAnalysis.maxLoss > 0) && (
        <div>
          <h4 className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 mb-3">Streak Analysis</h4>
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
              <div className="text-emerald-400 text-lg font-bold">{streakAnalysis.maxWin}</div>
              <div className="text-[9px] text-zinc-500">Best Win Streak</div>
            </div>
            <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
              <div className="text-red-400 text-lg font-bold">{streakAnalysis.maxLoss}</div>
              <div className="text-[9px] text-zinc-500">Worst Loss Streak</div>
            </div>
            <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
              <div className={`text-lg font-bold ${streakAnalysis.currentType === 'win' ? 'text-emerald-400' : 'text-red-400'}`}>
                {streakAnalysis.currentStreak}
              </div>
              <div className="text-[9px] text-zinc-500">Current ({streakAnalysis.currentType ?? '-'})</div>
            </div>
          </div>
        </div>
      )}

      {/* Backtest Results */}
      {backtestResults.length > 0 && (
        <div>
          <h4 className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 mb-3">Latest Backtest Results</h4>
          <div className="space-y-1">
            {backtestResults
              .filter(bt => bt.totalTrades > 0)
              .sort((a, b) => (b.accuracy ?? 0) - (a.accuracy ?? 0))
              .map(bt => (
                <div key={bt.strategy + bt.createdAt} className="flex items-center justify-between text-[10px] px-2 py-1 rounded bg-zinc-800/30">
                  <span className="text-zinc-300 font-medium w-28 truncate">{bt.strategy}</span>
                  <span className="text-zinc-500">{bt.totalTrades} trades</span>
                  <span className={bt.accuracy != null && bt.accuracy >= 55 ? 'text-emerald-400' : 'text-zinc-400'}>
                    {bt.accuracy != null ? `${bt.accuracy}%` : '--'}
                  </span>
                  {bt.sharpe != null && <span className="text-zinc-500">S: {bt.sharpe}</span>}
                  {bt.profitFactor != null && <span className="text-zinc-500">PF: {bt.profitFactor}</span>}
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Prediction Confidence Timeline */}
      {timeline.length > 0 && (
        <div>
          <h4 className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 mb-3">Recent Prediction Confidence</h4>
          <div className="h-36">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={timeline}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="time" tick={{ fontSize: 9, fill: '#71717a' }} interval="preserveStartEnd" />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#71717a' }} width={32} />
                <Tooltip
                  {...tooltipStyle}
                  formatter={(value: number | undefined) => [
                    value != null ? `${Number(value).toFixed(0)}%` : '--',
                    'Confidence',
                  ]}
                />
                <Bar
                  dataKey="confidence"
                  radius={[2, 2, 0, 0]}
                  fill="#a78bfa"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Cost Efficiency */}
      {costEfficiency && (
        <div>
          <h4 className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 mb-3">Cost Efficiency</h4>
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
              <div className="text-cyan-400 text-lg font-bold font-mono">{costEfficiency.totalSpentQU}</div>
              <div className="text-[9px] text-zinc-500">Total Spent (QU)</div>
            </div>
            <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
              <div className="text-amber-400 text-lg font-bold font-mono">{costEfficiency.costPerCorrect ?? '--'}</div>
              <div className="text-[9px] text-zinc-500">QU per Correct</div>
            </div>
            <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
              <div className="text-zinc-300 text-lg font-bold font-mono">{costEfficiency.totalRevealed}/{costEfficiency.totalCommitted}</div>
              <div className="text-[9px] text-zinc-500">Revealed / Total</div>
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {accuracyOverTime.length === 0 && strategyBars.length === 0 && calData.length === 0 && (
        <div className="text-center py-8">
          <p className="text-zinc-600 text-xs">No analytics data yet. Predictions need to be revealed first.</p>
        </div>
      )}
    </div>
  )
}

function ArbitrageTab({ spreads }: { spreads: SpreadInfo[] }) {
  const getSpreadColor = (pct: number) => {
    if (pct >= 0.2) return 'text-emerald-400'
    if (pct >= 0.1) return 'text-amber-400'
    return 'text-zinc-400'
  }

  const getSpreadBg = (pct: number) => {
    if (pct >= 0.2) return 'bg-emerald-400/10'
    if (pct >= 0.1) return 'bg-amber-400/10'
    return 'bg-zinc-800/30'
  }

  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 mb-3">Live Cross-Oracle Spreads</h4>
        <p className="text-[9px] text-zinc-600 mb-3">Price differences between oracle sources. Larger spreads = potential arbitrage signals.</p>

        {spreads.length === 0 ? (
          <div className="text-center py-6">
            <p className="text-zinc-600 text-xs">No significant spreads detected. Spreads update every 15 seconds.</p>
          </div>
        ) : (
          <div className="space-y-1">
            {/* Header */}
            <div className="grid grid-cols-6 gap-1 text-[9px] text-zinc-600 uppercase tracking-wider px-2 py-1">
              <span>Pair</span>
              <span>High Oracle</span>
              <span className="text-right">High Price</span>
              <span>Low Oracle</span>
              <span className="text-right">Low Price</span>
              <span className="text-right">Spread</span>
            </div>
            {/* Rows */}
            {spreads.map((s, i) => (
              <div key={`${s.pair}-${i}`} className={`grid grid-cols-6 gap-1 text-[10px] px-2 py-1.5 rounded ${getSpreadBg(s.spreadPct)}`}>
                <span className="font-mono text-zinc-300 uppercase">{s.pair}</span>
                <span className="text-zinc-400 truncate">{s.oracleHigh}</span>
                <span className="text-right font-mono text-zinc-300">{formatThreshold(s.priceHigh)}</span>
                <span className="text-zinc-400 truncate">{s.oracleLow}</span>
                <span className="text-right font-mono text-zinc-300">{formatThreshold(s.priceLow)}</span>
                <span className={`text-right font-mono font-medium ${getSpreadColor(s.spreadPct)}`}>
                  {s.spreadPct.toFixed(3)}%
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Summary stats */}
      {spreads.length > 0 && (
        <div className="grid grid-cols-3 gap-2">
          <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
            <div className="text-emerald-400 text-lg font-bold font-mono">
              {spreads.filter(s => s.spreadPct >= 0.2).length}
            </div>
            <div className="text-[9px] text-zinc-500">High Spreads (&gt;0.2%)</div>
          </div>
          <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
            <div className="text-amber-400 text-lg font-bold font-mono">
              {spreads.length}
            </div>
            <div className="text-[9px] text-zinc-500">Active Pairs</div>
          </div>
          <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
            <div className="text-cyan-400 text-lg font-bold font-mono">
              {Math.max(...spreads.map(s => s.spreadPct)).toFixed(2)}%
            </div>
            <div className="text-[9px] text-zinc-500">Max Spread</div>
          </div>
        </div>
      )}
    </div>
  )
}

function ExplorerTab({ explorer }: { explorer: OracleExplorer }) {
  const { oracles, pairCoverage } = explorer

  const formatAge = (ts: string) => {
    const diff = Date.now() - new Date(ts).getTime()
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    return `${Math.floor(diff / 86400000)}d ago`
  }

  return (
    <div className="space-y-5">
      {/* Oracle Status Grid */}
      <div>
        <h4 className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 mb-3">Oracle Sources</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {oracles.map(o => {
            const isRecent = (Date.now() - new Date(o.lastSeen).getTime()) < 600000 // 10 min
            return (
              <div key={o.name} className="rounded-lg border border-zinc-800 p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${isRecent ? 'bg-emerald-400' : 'bg-zinc-600'}`} />
                    <span className="text-xs font-medium text-zinc-200">{o.name}</span>
                  </div>
                  <span className="text-[9px] text-zinc-500">{formatAge(o.lastSeen)}</span>
                </div>
                <div className="flex gap-4 text-[10px]">
                  <span className="text-zinc-500">Pairs: <span className="text-zinc-300">{o.pairsTracked}</span></span>
                  <span className="text-zinc-500">Snapshots: <span className="text-zinc-300">{o.totalSnapshots.toLocaleString()}</span></span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Pair Coverage Matrix */}
      <div>
        <h4 className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 mb-3">Pair Coverage</h4>
        <p className="text-[9px] text-zinc-600 mb-2">Which pairs are tracked by which oracles.</p>
        <div className="space-y-1">
          {/* Header */}
          <div className="grid grid-cols-4 gap-1 text-[9px] text-zinc-600 uppercase tracking-wider px-2 py-1">
            <span>Pair</span>
            <span>Oracles</span>
            <span className="text-right"># Sources</span>
            <span className="text-right">Snapshots</span>
          </div>
          {pairCoverage.slice(0, 20).map((pc) => (
            <div key={pc.pair} className="grid grid-cols-4 gap-1 text-[10px] px-2 py-1.5 rounded hover:bg-zinc-800/50">
              <span className="font-mono text-zinc-300 uppercase">{pc.pair}</span>
              <span className="text-zinc-500 truncate">
                {pc.oracles.map((o, i) => (
                  <span key={o} className={i > 0 ? 'ml-1' : ''}>
                    <span className="px-1 py-0.5 rounded bg-zinc-800 text-zinc-400 text-[8px]">{o}</span>
                  </span>
                ))}
              </span>
              <span className={`text-right font-mono ${pc.oracleCount >= 3 ? 'text-emerald-400' : pc.oracleCount >= 2 ? 'text-amber-400' : 'text-zinc-500'}`}>
                {pc.oracleCount}
              </span>
              <span className="text-right font-mono text-zinc-400">{pc.snapshotCount.toLocaleString()}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-2">
        <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
          <div className="text-cyan-400 text-lg font-bold font-mono">{oracles.length}</div>
          <div className="text-[9px] text-zinc-500">Oracle Sources</div>
        </div>
        <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
          <div className="text-purple-400 text-lg font-bold font-mono">{pairCoverage.length}</div>
          <div className="text-[9px] text-zinc-500">Tracked Pairs</div>
        </div>
        <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
          <div className="text-zinc-300 text-lg font-bold font-mono">
            {oracles.reduce((s, o) => s + o.totalSnapshots, 0).toLocaleString()}
          </div>
          <div className="text-[9px] text-zinc-500">Total Snapshots</div>
        </div>
      </div>
    </div>
  )
}

function PerformanceTable({ rows, labelKey, suffix = '' }: {
  rows: PerformanceRow[]
  labelKey: 'pair' | 'horizon_hours'
  suffix?: string
}) {
  return (
    <div className="space-y-1">
      <div className="grid grid-cols-5 gap-2 text-[10px] text-zinc-600 uppercase tracking-wider px-2 py-1">
        <span className="col-span-2">{labelKey === 'pair' ? 'Pair' : 'Horizon'}</span>
        <span className="text-right">Total</span>
        <span className="text-right">Win/Loss</span>
        <span className="text-right">Accuracy</span>
      </div>
      {rows.map((row) => {
        const label = String(row[labelKey] ?? '?') + suffix
        const resolved = row.correct + row.incorrect
        const accuracy = resolved > 0 ? row.accuracy : null

        return (
          <div key={label} className="grid grid-cols-5 gap-2 text-xs px-2 py-1.5 rounded hover:bg-zinc-800/50 transition-colors">
            <span className="col-span-2 font-mono text-zinc-300">{label.toUpperCase()}</span>
            <span className="text-right text-zinc-500">{row.total}</span>
            <span className="text-right">
              <span className="text-emerald-400">{row.correct}</span>
              <span className="text-zinc-700">/</span>
              <span className="text-red-400">{row.incorrect}</span>
            </span>
            <span className={`text-right font-mono ${
              accuracy !== null && accuracy >= 60 ? 'text-emerald-400' :
              accuracy !== null && accuracy > 0 ? 'text-amber-400' :
              'text-zinc-600'
            }`}>
              {accuracy !== null ? `${accuracy}%` : '--'}
            </span>
          </div>
        )
      })}
    </div>
  )
}

// =============================================================================
// PREDICTION CARD
// =============================================================================

function PredictionCard({ prediction: p, index }: { prediction: Prediction; index: number }) {
  const isSymbolic = p.type === 'symbolic'
  const statusConfig: Record<string, { border: string; label: string; bg: string }> = {
    committed: { border: 'border-cyan-400/20', label: 'COMMITTED', bg: 'bg-cyan-400/5' },
    revealed: { border: 'border-zinc-500/20', label: 'REVEALED', bg: 'bg-zinc-400/5' },
    correct: { border: 'border-emerald-400/20', label: 'CORRECT', bg: 'bg-emerald-400/5' },
    incorrect: { border: 'border-red-400/20', label: 'INCORRECT', bg: 'bg-red-400/5' },
    inscribed: { border: 'border-purple-400/20', label: 'INSCRIBED', bg: 'bg-purple-400/5' },
  }
  const config = statusConfig[p.status] ?? { border: 'border-zinc-700', label: p.status.toUpperCase(), bg: '' }

  let countdown = ''
  if (p.status === 'committed' && p.expiresAt) {
    const remaining = new Date(p.expiresAt).getTime() - Date.now()
    if (remaining > 0) {
      const hours = Math.floor(remaining / 3600000)
      const mins = Math.floor((remaining % 3600000) / 60000)
      countdown = `${hours}h ${mins}m remaining`
    } else {
      countdown = 'Expired \u2014 ready to reveal'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05, ease: [0.22, 1, 0.36, 1] }}
      className={`rounded-lg border p-3 ${config.border} ${config.bg}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          {isSymbolic ? (
            <>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] uppercase tracking-[0.2em] text-purple-400 font-medium">{config.label}</span>
                <span className="text-[10px] font-mono text-zinc-600">
                  [{p.row}][{p.col}]
                </span>
              </div>
              <p className="text-xs text-zinc-400 font-mono truncate">{p.encrypted}</p>
            </>
          ) : (
            <>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] uppercase tracking-[0.2em] text-cyan-400 font-medium">{config.label}</span>
                <span className="text-xs text-zinc-300">{p.pair?.toUpperCase()}</span>
                <span className="text-xs text-zinc-500">{p.horizonHours ? `${p.horizonHours}h` : p.horizon}</span>
                {p.strategy && p.strategy !== 'manual' && (
                  <span className="text-[9px] px-1 py-0.5 rounded bg-purple-400/10 text-purple-400">{p.strategy}</span>
                )}
              </div>
              <p className="text-xs text-zinc-400 font-mono">
                {p.direction === 'up' ? '\u25B2' : '\u25BC'} {p.direction} {formatThreshold(p.threshold)}
                {p.priceAtCommit != null && (
                  <span className="text-zinc-600 ml-2">
                    (from {formatThreshold(p.priceAtCommit)})
                  </span>
                )}
              </p>
              {p.outcome && (
                <p className={`text-[10px] mt-1 font-medium ${p.outcome === 'correct' ? 'text-emerald-400' : 'text-red-400'}`}>
                  {p.outcome === 'correct' ? '+' : 'X'} {p.outcome} | actual: {formatThreshold(p.priceAtExpiry)}
                </p>
              )}
              {countdown && !p.outcome && (
                <p className="text-[10px] text-zinc-600 mt-1">{countdown}</p>
              )}
            </>
          )}
        </div>
        <div className="text-right text-[10px] text-zinc-600 font-mono whitespace-nowrap">
          Tick {(p.commitTick ?? p.targetTick)?.toLocaleString()}
        </div>
      </div>
      {p.commitHash && (
        <div className="mt-1.5 text-[10px] text-zinc-700 font-mono truncate">
          Hash: {p.commitHash}
        </div>
      )}
    </motion.div>
  )
}

// =============================================================================
// HELPERS
// =============================================================================

function formatThreshold(v?: number | null): string {
  if (v == null) return '?'
  if (v === 0) return '0'
  if (v < 0.0001) return v.toExponential(2)
  if (v < 1) return v.toFixed(6)
  if (v >= 1000) return v.toLocaleString(undefined, { maximumFractionDigits: 2 })
  return v.toFixed(2)
}

function StatRow({ label, value, color }: { label: string; value: number; color?: string }) {
  const colorClasses: Record<string, string> = {
    emerald: 'text-emerald-400',
    red: 'text-red-400',
    cyan: 'text-cyan-400',
    purple: 'text-purple-400',
  }
  return (
    <div className="flex items-center justify-between gap-2">
      <span className="text-zinc-500">{label}</span>
      <span className={`font-mono ${colorClasses[color ?? ''] ?? 'text-zinc-300'}`}>{value}</span>
    </div>
  )
}
