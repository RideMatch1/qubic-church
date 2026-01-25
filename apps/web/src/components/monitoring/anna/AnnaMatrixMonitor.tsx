/**
 * ANNA MATRIX MONITOR - Main Component
 *
 * Live visualization of the 128×128 Anna Matrix with:
 * - Interactive heatmap showing blockchain activity
 * - XOR layer filtering
 * - Cell detail panel
 * - Activity statistics
 */

'use client'

import { useState, useCallback, useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  Grid3X3,
  Layers,
  Activity,
  Eye,
  Target,
  ZoomIn,
  ZoomOut,
  Download,
  RefreshCw,
} from 'lucide-react'
import { StatCard } from '../MonitoringTabs'
import { MatrixHeatmapCanvas } from './MatrixHeatmapCanvas'
import { CellDetailPanel } from './CellDetailPanel'

// =============================================================================
// TYPES
// =============================================================================

export interface MatrixCell {
  row: number
  col: number
  annaX: number
  annaY: number
  value: number
  addresses: MatrixAddress[]
  totalBalance: number
  totalTxCount: number
  activityLevel: 0 | 1 | 2 | 3 | 4
}

export interface MatrixAddress {
  address: string
  xor: number
  balance?: number
  txCount?: number
  status?: 'active' | 'spent' | 'unused' | 'unknown'
}

// =============================================================================
// XOR LAYER CONFIGURATION
// =============================================================================

export const XOR_LAYERS = [
  { xor: 0, label: 'XOR 0', color: '#ffffff', bgColor: 'bg-white/20' },
  { xor: 7, label: 'XOR 7', color: '#f97316', bgColor: 'bg-orange-500/20' },
  { xor: 13, label: 'XOR 13', color: '#a855f7', bgColor: 'bg-purple-500/20' },
  { xor: 27, label: 'XOR 27', color: '#06b6d4', bgColor: 'bg-cyan-500/20' },
  { xor: 33, label: 'XOR 33', color: '#ec4899', bgColor: 'bg-pink-500/20' },
]

// =============================================================================
// ANNA MATRIX MONITOR
// =============================================================================

export function AnnaMatrixMonitor() {
  // State
  const [matrixData, setMatrixData] = useState<number[][] | null>(null)
  const [selectedCell, setSelectedCell] = useState<[number, number] | null>(null)
  const [activeXorLayers, setActiveXorLayers] = useState<number[]>([0, 7, 13, 27, 33])
  const [zoom, setZoom] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load matrix data
  useEffect(() => {
    const loadMatrix = async () => {
      try {
        setIsLoading(true)
        const response = await fetch('/data/anna-matrix.json')
        if (!response.ok) throw new Error('Failed to load matrix data')

        const data = await response.json()

        // Data is a flat array or 2D array - normalize to 2D
        let matrix: number[][]
        if (Array.isArray(data) && Array.isArray(data[0])) {
          matrix = data
        } else if (Array.isArray(data)) {
          // Convert flat array to 128x128
          matrix = []
          for (let i = 0; i < 128; i++) {
            matrix[i] = data.slice(i * 128, (i + 1) * 128)
          }
        } else if (data.matrix) {
          matrix = data.matrix
        } else {
          throw new Error('Invalid matrix format')
        }

        setMatrixData(matrix)
      } catch (err) {
        console.error('Error loading matrix:', err)
        setError('Failed to load Anna Matrix data')

        // Generate demo data
        const demo: number[][] = Array.from({ length: 128 }, () =>
          Array.from({ length: 128 }, () => Math.floor(Math.random() * 255) - 127)
        )
        setMatrixData(demo)
      } finally {
        setIsLoading(false)
      }
    }

    loadMatrix()
  }, [])

  // Calculate statistics
  const stats = useMemo(() => {
    if (!matrixData) return { total: 0, positive: 0, negative: 0, zero: 0, hotZones: 0 }

    let positive = 0
    let negative = 0
    let zero = 0
    let hotZones = 0

    for (let row = 0; row < 128; row++) {
      for (let col = 0; col < 128; col++) {
        const value = matrixData[row]?.[col] ?? 0
        if (value > 0) positive++
        else if (value < 0) negative++
        else zero++

        if (Math.abs(value) > 100) hotZones++
      }
    }

    return {
      total: 16384,
      positive,
      negative,
      zero,
      hotZones,
    }
  }, [matrixData])

  // Get cell info
  const selectedCellInfo = useMemo(() => {
    if (!selectedCell || !matrixData) return null

    const [row, col] = selectedCell
    const value = matrixData[row]?.[col] ?? 0

    const ternaryState: 'EXCITED' | 'INHIBITED' | 'NEUTRAL' =
      value > 0 ? 'EXCITED' : value < 0 ? 'INHIBITED' : 'NEUTRAL'

    return {
      row,
      col,
      annaX: col - 64,
      annaY: 63 - row,
      value,
      ternaryState,
      ternaryColor: value > 0 ? 'text-orange-400' : value < 0 ? 'text-blue-400' : 'text-zinc-400',
    }
  }, [selectedCell, matrixData])

  // Toggle XOR layer
  const toggleXorLayer = (xor: number) => {
    setActiveXorLayers(prev =>
      prev.includes(xor)
        ? prev.filter(x => x !== xor)
        : [...prev, xor]
    )
  }

  // Handle cell click
  const handleCellClick = useCallback((row: number, col: number) => {
    setSelectedCell([row, col])
  }, [])

  // Export matrix as CSV
  const exportMatrix = () => {
    if (!matrixData) return

    const csv = matrixData.map(row => row.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'anna-matrix.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard
          label="Total Cells"
          value={stats.total.toLocaleString()}
          icon={<Grid3X3 className="w-4 h-4" />}
          color="text-cyan-400"
          subtext="128 × 128"
        />
        <StatCard
          label="Excited (+)"
          value={stats.positive.toLocaleString()}
          icon={<Activity className="w-4 h-4" />}
          color="text-orange-400"
          subtext={`${((stats.positive / stats.total) * 100).toFixed(1)}%`}
        />
        <StatCard
          label="Inhibited (-)"
          value={stats.negative.toLocaleString()}
          icon={<Activity className="w-4 h-4" />}
          color="text-blue-400"
          subtext={`${((stats.negative / stats.total) * 100).toFixed(1)}%`}
        />
        <StatCard
          label="Neutral (0)"
          value={stats.zero.toLocaleString()}
          icon={<Target className="w-4 h-4" />}
          color="text-zinc-400"
          subtext={`${((stats.zero / stats.total) * 100).toFixed(1)}%`}
        />
        <StatCard
          label="Hot Zones"
          value={stats.hotZones}
          icon={<Eye className="w-4 h-4" />}
          color="text-red-400"
          subtext="|value| > 100"
        />
      </div>

      {/* XOR Layer Toggles */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            XOR Layers
          </h3>
          <div className="flex gap-2">
            <button
              onClick={() => setZoom(Math.max(0.5, zoom - 0.25))}
              className="p-1.5 text-white/40 hover:text-white hover:bg-white/10 rounded transition-colors"
              title="Zoom out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="text-xs text-white/60 px-2 py-1">{(zoom * 100).toFixed(0)}%</span>
            <button
              onClick={() => setZoom(Math.min(2, zoom + 0.25))}
              className="p-1.5 text-white/40 hover:text-white hover:bg-white/10 rounded transition-colors"
              title="Zoom in"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={exportMatrix}
              className="p-1.5 text-white/40 hover:text-white hover:bg-white/10 rounded transition-colors"
              title="Export CSV"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {XOR_LAYERS.map(layer => (
            <button
              key={layer.xor}
              onClick={() => toggleXorLayer(layer.xor)}
              className={`
                px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                ${activeXorLayers.includes(layer.xor)
                  ? `${layer.bgColor} border-2`
                  : 'bg-white/5 border border-white/10 opacity-50'
                }
              `}
              style={{
                borderColor: activeXorLayers.includes(layer.xor) ? layer.color : undefined,
                color: layer.color,
              }}
            >
              {layer.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Heatmap */}
        <div className="lg:col-span-2 bg-white/5 border border-white/10 rounded-xl p-4">
          <h3 className="text-sm font-semibold text-white mb-3">
            Live Heatmap (128×128)
          </h3>
          {isLoading ? (
            <div className="aspect-square flex items-center justify-center">
              <RefreshCw className="w-8 h-8 text-white/40 animate-spin" />
            </div>
          ) : error ? (
            <div className="aspect-square flex items-center justify-center text-red-400">
              {error}
            </div>
          ) : matrixData ? (
            <MatrixHeatmapCanvas
              matrix={matrixData}
              selectedCell={selectedCell}
              onCellClick={handleCellClick}
              zoom={zoom}
            />
          ) : null}
          <p className="text-xs text-white/40 mt-2 text-center">
            Click any cell to see details. Colors: Blue (negative) → White (zero) → Orange (positive)
          </p>
        </div>

        {/* Cell Detail Panel */}
        <div className="lg:col-span-1">
          <CellDetailPanel
            cellInfo={selectedCellInfo}
            activeXorLayers={activeXorLayers}
          />
        </div>
      </div>

      {/* Info */}
      <p className="text-xs text-white/40 text-center">
        Anna Matrix: 128×128 neural network weight matrix from Aigarth architecture.
        Each cell contains a ternary value (-127 to +127).
      </p>
    </div>
  )
}

export default AnnaMatrixMonitor
