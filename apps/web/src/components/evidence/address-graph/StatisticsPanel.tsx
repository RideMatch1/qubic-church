'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart3,
  TrendingUp,
  Target,
  AlertCircle,
  CheckCircle2,
  XCircle,
  ChevronDown,
  ChevronUp,
  Info,
} from 'lucide-react'
import {
  chiSquaredTest,
  testUniformDistribution,
  pearsonCorrelation,
  statisticalSummary,
  type ChiSquaredResult,
  type PearsonCorrelationResult,
  type StatisticalSummary,
} from '@/lib/statistics/statistical-tests'

// =============================================================================
// TYPES
// =============================================================================

interface StatisticsPanelProps {
  isOpen: boolean
  onToggle: () => void
  data: {
    xorDistribution?: number[] // [xor0_count, xor7_count, xor13_count, xor27_count, xor33_count]
    methodDistribution?: number[] // [diagonal, row, col, step7, step13, step27]
    blockHeights?: number[]
    balances?: number[]
    timestamps?: number[]
  }
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export function StatisticsPanel({ isOpen, onToggle, data }: StatisticsPanelProps) {
  const [xorTest, setXorTest] = useState<ChiSquaredResult | null>(null)
  const [methodTest, setMethodTest] = useState<ChiSquaredResult | null>(null)
  const [blockHeightCorrelation, setBlockHeightCorrelation] =
    useState<PearsonCorrelationResult | null>(null)
  const [balanceSummary, setBalanceSummary] = useState<StatisticalSummary | null>(null)

  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['xor', 'method'])
  )

  useEffect(() => {
    // XOR Distribution Test
    if (data.xorDistribution && data.xorDistribution.length === 5) {
      try {
        const result = testUniformDistribution(data.xorDistribution)
        setXorTest(result)
      } catch (error) {
        console.error('XOR test failed:', error)
      }
    }

    // Method Distribution Test
    if (data.methodDistribution && data.methodDistribution.length === 6) {
      try {
        const result = testUniformDistribution(data.methodDistribution)
        setMethodTest(result)
      } catch (error) {
        console.error('Method test failed:', error)
      }
    }

    // Block Height Correlation (with index as time proxy)
    if (data.blockHeights && data.blockHeights.length > 3) {
      try {
        const indices = data.blockHeights.map((_, i) => i)
        const result = pearsonCorrelation(indices, data.blockHeights)
        setBlockHeightCorrelation(result)
      } catch (error) {
        console.error('Block height correlation failed:', error)
      }
    }

    // Balance Summary
    if (data.balances && data.balances.length > 0) {
      try {
        const nonZeroBalances = data.balances.filter((b) => b > 0)
        if (nonZeroBalances.length > 0) {
          const result = statisticalSummary(nonZeroBalances)
          setBalanceSummary(result)
        }
      } catch (error) {
        console.error('Balance summary failed:', error)
      }
    }
  }, [data])

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev)
      if (next.has(section)) {
        next.delete(section)
      } else {
        next.add(section)
      }
      return next
    })
  }

  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className="fixed bottom-6 right-6 z-50 p-4 bg-purple-600 hover:bg-purple-700 rounded-full shadow-2xl transition-all hover:scale-110"
        title="Show Statistical Analysis"
      >
        <BarChart3 className="w-6 h-6 text-white" />
      </button>
    )
  }

  return (
    <motion.div
      className="fixed bottom-6 right-6 z-50 w-96 max-h-[80vh] bg-gray-950/95 border border-white/20 rounded-2xl shadow-2xl backdrop-blur-xl overflow-hidden flex flex-col"
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 50, scale: 0.9 }}
      transition={{ type: 'spring', damping: 20 }}
    >
      {/* Header */}
      <div className="p-4 border-b border-white/10 bg-gradient-to-r from-purple-600/20 to-blue-600/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-600/30 rounded-lg">
              <BarChart3 className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white">Statistical Analysis</h2>
              <p className="text-xs text-gray-400">Pattern Significance Tests</p>
            </div>
          </div>
          <button
            onClick={onToggle}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <ChevronDown className="w-5 h-5 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* XOR Distribution Test */}
        {xorTest && (
          <TestSection
            title="XOR Distribution (χ² Test)"
            icon={<Target className="w-4 h-4" />}
            isExpanded={expandedSections.has('xor')}
            onToggle={() => toggleSection('xor')}
            result={xorTest}
          >
            <div className="space-y-2">
              <MetricRow label="χ² Statistic" value={xorTest.chiSquared.toFixed(4)} />
              <MetricRow label="Degrees of Freedom" value={String(xorTest.degreesOfFreedom)} />
              <MetricRow
                label="P-Value"
                value={xorTest.pValue.toFixed(6)}
                highlight={xorTest.isSignificant ? 'success' : 'warning'}
              />
              <MetricRow
                label="Effect Size"
                value={xorTest.effectSize.toFixed(4)}
                highlight={xorTest.effectSize > 0.3 ? 'success' : 'neutral'}
              />

              <SignificanceBadge result={xorTest} />

              <div className="p-3 bg-white/5 rounded-lg border border-white/10 mt-3">
                <p className="text-xs text-gray-300 leading-relaxed">
                  {xorTest.interpretation}
                </p>
              </div>

              {data.xorDistribution && (
                <DistributionBars
                  data={data.xorDistribution}
                  labels={['XOR 0', 'XOR 7', 'XOR 13', 'XOR 27', 'XOR 33']}
                  colors={['#60a5fa', '#34d399', '#fbbf24', '#f87171', '#a78bfa']}
                />
              )}
            </div>
          </TestSection>
        )}

        {/* Method Distribution Test */}
        {methodTest && (
          <TestSection
            title="Method Distribution (χ² Test)"
            icon={<Target className="w-4 h-4" />}
            isExpanded={expandedSections.has('method')}
            onToggle={() => toggleSection('method')}
            result={methodTest}
          >
            <div className="space-y-2">
              <MetricRow label="χ² Statistic" value={methodTest.chiSquared.toFixed(4)} />
              <MetricRow label="P-Value" value={methodTest.pValue.toFixed(6)} />

              <SignificanceBadge result={methodTest} />

              {data.methodDistribution && (
                <DistributionBars
                  data={data.methodDistribution}
                  labels={['Diagonal', 'Row', 'Col', 'Step7', 'Step13', 'Step27']}
                  colors={['#60a5fa', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#fb923c']}
                />
              )}
            </div>
          </TestSection>
        )}

        {/* Block Height Correlation */}
        {blockHeightCorrelation && (
          <TestSection
            title="Temporal Correlation (Pearson)"
            icon={<TrendingUp className="w-4 h-4" />}
            isExpanded={expandedSections.has('correlation')}
            onToggle={() => toggleSection('correlation')}
            result={blockHeightCorrelation}
          >
            <div className="space-y-2">
              <MetricRow
                label="Correlation (r)"
                value={blockHeightCorrelation.r.toFixed(4)}
                highlight={Math.abs(blockHeightCorrelation.r) > 0.5 ? 'success' : 'neutral'}
              />
              <MetricRow
                label="R²"
                value={`${(blockHeightCorrelation.rSquared * 100).toFixed(2)}%`}
              />
              <MetricRow
                label="P-Value"
                value={blockHeightCorrelation.pValue.toFixed(6)}
                highlight={blockHeightCorrelation.isSignificant ? 'success' : 'warning'}
              />

              <div className="flex items-center justify-between p-2 bg-white/5 rounded-lg">
                <span className="text-xs text-gray-400">Strength</span>
                <span
                  className={`text-xs font-semibold ${
                    blockHeightCorrelation.strength === 'very_strong' ||
                    blockHeightCorrelation.strength === 'strong'
                      ? 'text-green-400'
                      : blockHeightCorrelation.strength === 'moderate'
                      ? 'text-yellow-400'
                      : 'text-gray-400'
                  }`}
                >
                  {blockHeightCorrelation.strength.replace('_', ' ').toUpperCase()}
                </span>
              </div>

              <div className="p-3 bg-white/5 rounded-lg border border-white/10 mt-3">
                <p className="text-xs text-gray-300 leading-relaxed">
                  {blockHeightCorrelation.interpretation}
                </p>
              </div>
            </div>
          </TestSection>
        )}

        {/* Balance Summary */}
        {balanceSummary && (
          <TestSection
            title="Balance Statistics"
            icon={<Info className="w-4 h-4" />}
            isExpanded={expandedSections.has('balance')}
            onToggle={() => toggleSection('balance')}
          >
            <div className="space-y-2">
              <MetricRow label="Sample Size" value={String(balanceSummary.n)} />
              <MetricRow
                label="Mean Balance"
                value={`${balanceSummary.mean.toFixed(8)} BTC`}
              />
              <MetricRow
                label="Median Balance"
                value={`${balanceSummary.median.toFixed(8)} BTC`}
              />
              <MetricRow
                label="Std. Deviation"
                value={`${balanceSummary.standardDeviation.toFixed(8)} BTC`}
              />
              <MetricRow
                label="95% CI"
                value={`[${balanceSummary.confidenceInterval95.lower.toFixed(4)}, ${balanceSummary.confidenceInterval95.upper.toFixed(4)}]`}
              />
            </div>
          </TestSection>
        )}

        {/* Info Box */}
        <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <div className="flex items-start gap-2">
            <Info className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-xs text-blue-300 font-medium mb-1">
                Statistical Significance
              </p>
              <p className="text-xs text-blue-400/80 leading-relaxed">
                P-values &lt; 0.05 indicate patterns unlikely due to random chance.
                Chi-squared tests validate distribution uniformity. Pearson correlation
                measures linear relationships.
              </p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

interface TestSectionProps {
  title: string
  icon: React.ReactNode
  isExpanded: boolean
  onToggle: () => void
  result?: ChiSquaredResult | PearsonCorrelationResult
  children: React.ReactNode
}

function TestSection({
  title,
  icon,
  isExpanded,
  onToggle,
  result,
  children,
}: TestSectionProps) {
  const isSignificant =
    result && 'isSignificant' in result ? result.isSignificant : false

  return (
    <div className="border border-white/10 rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full p-3 bg-white/5 hover:bg-white/10 transition-colors flex items-center justify-between"
      >
        <div className="flex items-center gap-2">
          <div className="text-gray-400">{icon}</div>
          <span className="text-sm font-medium text-white">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {result && (
            <div
              className={`w-2 h-2 rounded-full ${
                isSignificant ? 'bg-green-400' : 'bg-yellow-400'
              }`}
            />
          )}
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-400" />
          )}
        </div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="p-3 space-y-2">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

interface MetricRowProps {
  label: string
  value: string
  highlight?: 'success' | 'warning' | 'error' | 'neutral'
}

function MetricRow({ label, value, highlight = 'neutral' }: MetricRowProps) {
  const colorClasses = {
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-red-400',
    neutral: 'text-white',
  }

  return (
    <div className="flex items-center justify-between p-2 bg-white/5 rounded">
      <span className="text-xs text-gray-400">{label}</span>
      <code className={`text-xs font-mono font-semibold ${colorClasses[highlight]}`}>
        {value}
      </code>
    </div>
  )
}

function SignificanceBadge({
  result,
}: {
  result: ChiSquaredResult | PearsonCorrelationResult
}) {
  const isSignificant = result.isSignificant

  let label = ''
  let icon = null
  let colorClass = ''

  if ('significance' in result) {
    // Chi-squared
    switch (result.significance) {
      case 'extremely_significant':
        label = 'Extremely Significant (p < 0.001)'
        icon = <CheckCircle2 className="w-4 h-4" />
        colorClass = 'bg-green-500/20 border-green-500/40 text-green-400'
        break
      case 'highly_significant':
        label = 'Highly Significant (p < 0.01)'
        icon = <CheckCircle2 className="w-4 h-4" />
        colorClass = 'bg-green-500/20 border-green-500/40 text-green-400'
        break
      case 'significant':
        label = 'Significant (p < 0.05)'
        icon = <CheckCircle2 className="w-4 h-4" />
        colorClass = 'bg-yellow-500/20 border-yellow-500/40 text-yellow-400'
        break
      case 'not_significant':
        label = 'Not Significant (p ≥ 0.05)'
        icon = <XCircle className="w-4 h-4" />
        colorClass = 'bg-gray-500/20 border-gray-500/40 text-gray-400'
        break
    }
  } else {
    // Pearson
    if (isSignificant) {
      label = 'Statistically Significant (p < 0.05)'
      icon = <CheckCircle2 className="w-4 h-4" />
      colorClass = 'bg-green-500/20 border-green-500/40 text-green-400'
    } else {
      label = 'Not Significant (p ≥ 0.05)'
      icon = <XCircle className="w-4 h-4" />
      colorClass = 'bg-gray-500/20 border-gray-500/40 text-gray-400'
    }
  }

  return (
    <div className={`p-3 rounded-lg border ${colorClass} flex items-center gap-2`}>
      {icon}
      <span className="text-xs font-medium">{label}</span>
    </div>
  )
}

interface DistributionBarsProps {
  data: number[]
  labels: string[]
  colors: string[]
}

function DistributionBars({ data, labels, colors }: DistributionBarsProps) {
  const total = data.reduce((sum, val) => sum + val, 0)
  const max = Math.max(...data)

  return (
    <div className="mt-3 space-y-2">
      <div className="text-xs text-gray-400 mb-2">Distribution:</div>
      {data.map((value, i) => {
        const percentage = (value / total) * 100
        const barWidth = (value / max) * 100

        return (
          <div key={i} className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">{labels[i]}</span>
              <span className="text-white font-mono">
                {value.toLocaleString()} ({percentage.toFixed(2)}%)
              </span>
            </div>
            <div className="h-2 bg-white/5 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${barWidth}%` }}
                transition={{ duration: 0.5, delay: i * 0.05 }}
                className="h-full rounded-full"
                style={{ backgroundColor: colors[i] }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
