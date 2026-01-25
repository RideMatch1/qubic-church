'use client'

import { useMemo } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Activity,
  Zap,
  TrendingUp,
  TrendingDown,
  Minus,
  Clock,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
} from 'lucide-react'
import type { ProcessingResult, TernaryState } from '@/lib/aigarth/types'

interface TickHistoryPanelProps {
  result: ProcessingResult | null
  currentTick: number
  currentEnergy: number
  isProcessing: boolean
}

export function TickHistoryPanel({
  result,
  currentTick,
  currentEnergy,
  isProcessing,
}: TickHistoryPanelProps) {
  // Compute energy curve from history if available
  const energyCurve = useMemo(() => {
    if (!result?.history) return []
    return result.history.map((states) =>
      states.reduce((sum: number, s) => sum + s, 0 as number)
    )
  }, [result])

  // Compute state distribution per tick
  const distributionCurve = useMemo(() => {
    if (!result?.history) return []
    return result.history.map((states) => ({
      positive: states.filter((s) => s === 1).length,
      neutral: states.filter((s) => s === 0).length,
      negative: states.filter((s) => s === -1).length,
    }))
  }, [result])

  // If no result yet
  if (!result && !isProcessing) {
    return (
      <div className="text-center py-12">
        <Activity className="w-12 h-12 mx-auto text-gray-600 mb-4" />
        <h3 className="text-lg font-semibold text-gray-400 mb-2">
          Tick History Timeline
        </h3>
        <p className="text-sm text-gray-500 max-w-md mx-auto">
          Process an input to see the tick-by-tick state evolution,
          energy curve, and convergence analysis.
        </p>
      </div>
    )
  }

  // Processing state
  if (isProcessing) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-cyan-500 animate-pulse" />
          <span className="font-semibold text-white">Processing...</span>
          <span className="text-sm text-gray-400">Tick {currentTick}</span>
        </div>

        {/* Live energy display */}
        <Card className="bg-gray-800/30 border-gray-700/50 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              <span className="text-gray-400">Current Energy</span>
            </div>
            <span className={`text-2xl font-bold font-mono ${
              currentEnergy > 0 ? 'text-green-400' :
              currentEnergy < 0 ? 'text-red-400' : 'text-gray-400'
            }`}>
              {currentEnergy > 0 ? '+' : ''}{currentEnergy}
            </span>
          </div>
        </Card>
      </div>
    )
  }

  // Guard: if we reach here without result, show empty state
  if (!result) {
    return (
      <div className="text-center py-12">
        <Activity className="w-12 h-12 mx-auto text-gray-600 mb-4" />
        <h3 className="text-lg font-semibold text-gray-400 mb-2">
          Tick History Timeline
        </h3>
        <p className="text-sm text-gray-500 max-w-md mx-auto">
          Process an input to see the tick-by-tick state evolution,
          energy curve, and convergence analysis.
        </p>
      </div>
    )
  }

  // Completed result
  return (
    <div className="space-y-6">
      {/* Summary Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-green-400" />
          <span className="font-semibold text-white">Processing Complete</span>
        </div>
        <Badge
          variant="outline"
          className={`${
            result.endReason === 'converged' ? 'text-green-400 border-green-400/50' :
            result.endReason === 'all_nonzero' ? 'text-cyan-400 border-cyan-400/50' :
            'text-yellow-400 border-yellow-400/50'
          }`}
        >
          {result.endReason === 'converged' && <RotateCcw className="w-3 h-3 mr-1" />}
          {result.endReason === 'all_nonzero' && <Zap className="w-3 h-3 mr-1" />}
          {result.endReason === 'max_ticks' && <AlertCircle className="w-3 h-3 mr-1" />}
          {result.endReason.replace('_', ' ').toUpperCase()}
        </Badge>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Ticks */}
        <Card className="bg-gray-800/30 border-gray-700/50 p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
            <Clock className="w-4 h-4" />
            <span>Ticks</span>
          </div>
          <div className="text-2xl font-bold text-cyan-400 font-mono">
            {result.ticks}
          </div>
        </Card>

        {/* Energy */}
        <Card className="bg-gray-800/30 border-gray-700/50 p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
            <Zap className="w-4 h-4" />
            <span>Final Energy</span>
          </div>
          <div className={`text-2xl font-bold font-mono ${
            result.energy > 0 ? 'text-green-400' :
            result.energy < 0 ? 'text-red-400' : 'text-gray-400'
          }`}>
            {result.energy > 0 ? '+' : ''}{result.energy}
          </div>
        </Card>

        {/* Duration */}
        <Card className="bg-gray-800/30 border-gray-700/50 p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
            <Activity className="w-4 h-4" />
            <span>Duration</span>
          </div>
          <div className="text-2xl font-bold text-purple-400 font-mono">
            {result.durationMs.toFixed(1)}ms
          </div>
        </Card>

        {/* Tick Rate */}
        <Card className="bg-gray-800/30 border-gray-700/50 p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
            <TrendingUp className="w-4 h-4" />
            <span>Tick Rate</span>
          </div>
          <div className="text-2xl font-bold text-orange-400 font-mono">
            {result.durationMs > 0 ? (result.ticks / result.durationMs * 1000).toFixed(0) : '∞'}/s
          </div>
        </Card>
      </div>

      {/* State Distribution */}
      <Card className="bg-gray-800/30 border-gray-700/50 p-4">
        <h4 className="font-semibold text-white mb-4 flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          State Distribution
        </h4>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 mb-2">
              <TrendingUp className="w-4 h-4 text-green-400" />
              <span className="text-sm text-gray-400">Excited (+1)</span>
            </div>
            <div className="text-xl font-bold text-green-400">{result.distribution.positive}</div>
            <div className="text-xs text-gray-500">
              {((result.distribution.positive / result.stateVector.length) * 100).toFixed(1)}%
            </div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 mb-2">
              <Minus className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-400">Neutral (0)</span>
            </div>
            <div className="text-xl font-bold text-gray-400">{result.distribution.neutral}</div>
            <div className="text-xs text-gray-500">
              {((result.distribution.neutral / result.stateVector.length) * 100).toFixed(1)}%
            </div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 mb-2">
              <TrendingDown className="w-4 h-4 text-red-400" />
              <span className="text-sm text-gray-400">Inhibited (-1)</span>
            </div>
            <div className="text-xl font-bold text-red-400">{result.distribution.negative}</div>
            <div className="text-xs text-gray-500">
              {((result.distribution.negative / result.stateVector.length) * 100).toFixed(1)}%
            </div>
          </div>
        </div>

        {/* Distribution Bar */}
        <div className="mt-4 h-4 rounded-full overflow-hidden flex">
          <div
            className="bg-green-500 h-full transition-all"
            style={{ width: `${(result.distribution.positive / result.stateVector.length) * 100}%` }}
          />
          <div
            className="bg-gray-600 h-full transition-all"
            style={{ width: `${(result.distribution.neutral / result.stateVector.length) * 100}%` }}
          />
          <div
            className="bg-red-500 h-full transition-all"
            style={{ width: `${(result.distribution.negative / result.stateVector.length) * 100}%` }}
          />
        </div>
      </Card>

      {/* Energy Curve (if history available) */}
      {energyCurve.length > 0 && (
        <Card className="bg-gray-800/30 border-gray-700/50 p-4">
          <h4 className="font-semibold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-purple-400" />
            Energy Curve
          </h4>
          <div className="h-32 flex items-end gap-px">
            {energyCurve.map((energy, i) => {
              const maxEnergy = Math.max(...energyCurve.map(Math.abs), 1)
              const height = Math.abs(energy) / maxEnergy * 100
              const isPositive = energy >= 0
              return (
                <div
                  key={i}
                  className="flex-1 min-w-[2px] relative"
                  style={{ height: '100%' }}
                >
                  <div
                    className={`absolute bottom-1/2 w-full transition-all ${
                      isPositive ? 'bg-green-500' : 'bg-red-500'
                    }`}
                    style={{
                      height: `${height / 2}%`,
                      transform: isPositive ? 'translateY(0)' : 'translateY(100%)',
                    }}
                  />
                </div>
              )
            })}
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>Tick 0</span>
            <span>Tick {result.ticks}</span>
          </div>
        </Card>
      )}

      {/* Input/Output Info */}
      <Card className="bg-gray-800/30 border-gray-700/50 p-4">
        <h4 className="font-semibold text-white mb-3">Input Details</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Type:</span>
            <span className="ml-2 text-cyan-400">{result.inputType}</span>
          </div>
          <div>
            <span className="text-gray-500">Ternary Length:</span>
            <span className="ml-2 text-white font-mono">{result.inputTernaryLength}</span>
          </div>
        </div>
        <div className="mt-2">
          <span className="text-gray-500 text-sm">Raw Input:</span>
          <code className="block mt-1 text-xs text-gray-400 bg-gray-900/50 p-2 rounded overflow-x-auto">
            {result.inputRaw.length > 100
              ? `${result.inputRaw.slice(0, 100)}...`
              : result.inputRaw}
          </code>
        </div>
      </Card>
    </div>
  )
}
