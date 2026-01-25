/**
 * CELL DETAIL PANEL - Component
 *
 * Displays detailed information about a selected matrix cell.
 * Shows coordinates, value, ternary state, and associated addresses.
 */

'use client'

import { useState } from 'react'
import {
  Target,
  Grid3X3,
  Activity,
  Copy,
  Check,
  ExternalLink,
  Hash,
  Layers,
} from 'lucide-react'
import { XOR_LAYERS } from './AnnaMatrixMonitor'

// =============================================================================
// TYPES
// =============================================================================

interface CellInfo {
  row: number
  col: number
  annaX: number
  annaY: number
  value: number
  ternaryState: 'EXCITED' | 'INHIBITED' | 'NEUTRAL'
  ternaryColor: string
}

interface CellDetailPanelProps {
  cellInfo: CellInfo | null
  activeXorLayers: number[]
}

// =============================================================================
// CELL DETAIL PANEL
// =============================================================================

export function CellDetailPanel({ cellInfo, activeXorLayers }: CellDetailPanelProps) {
  const [copiedCoords, setCopiedCoords] = useState(false)

  if (!cellInfo) {
    return (
      <div className="bg-white/5 border border-white/10 rounded-xl p-6 h-full flex items-center justify-center">
        <div className="text-center text-white/40">
          <Target className="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p className="text-sm">Click a cell in the heatmap</p>
          <p className="text-xs mt-1">to see its details</p>
        </div>
      </div>
    )
  }

  const copyCoordinates = async () => {
    const coords = `[${cellInfo.row}, ${cellInfo.col}] / Anna(${cellInfo.annaX}, ${cellInfo.annaY})`
    await navigator.clipboard.writeText(coords)
    setCopiedCoords(true)
    setTimeout(() => setCopiedCoords(false), 2000)
  }

  // Get ternary background color
  const ternaryBg = cellInfo.value > 0
    ? 'bg-orange-500/20 border-orange-500/30'
    : cellInfo.value < 0
      ? 'bg-blue-500/20 border-blue-500/30'
      : 'bg-zinc-500/20 border-zinc-500/30'

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-4 space-y-4">
      <h3 className="text-sm font-semibold text-white flex items-center gap-2">
        <Target className="w-4 h-4 text-cyan-400" />
        Selected Cell
      </h3>

      {/* Coordinates */}
      <div className="bg-black/30 rounded-lg p-3 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-white/60 flex items-center gap-1.5">
            <Grid3X3 className="w-3 h-3" />
            Matrix Position
          </span>
          <button
            onClick={copyCoordinates}
            className="p-1 text-white/40 hover:text-white hover:bg-white/10 rounded transition-colors"
            title="Copy coordinates"
          >
            {copiedCoords ? (
              <Check className="w-3 h-3 text-green-400" />
            ) : (
              <Copy className="w-3 h-3" />
            )}
          </button>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-lg font-mono text-white font-bold">
            [{cellInfo.row}, {cellInfo.col}]
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-xs text-white/60">Anna Coordinates</span>
          <span className="text-sm font-mono text-cyan-400">
            ({cellInfo.annaX}, {cellInfo.annaY})
          </span>
        </div>
      </div>

      {/* Value & Ternary State */}
      <div className={`rounded-lg p-3 border ${ternaryBg}`}>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-white/60 flex items-center gap-1.5">
            <Activity className="w-3 h-3" />
            Cell Value
          </span>
          <span className={`text-xs font-bold ${cellInfo.ternaryColor}`}>
            {cellInfo.ternaryState}
          </span>
        </div>
        <div className="text-3xl font-mono font-bold text-white text-center py-2">
          {cellInfo.value}
        </div>
        <p className="text-xs text-white/40 text-center mt-2">
          {cellInfo.value > 0
            ? 'Positive activation - neural excitation'
            : cellInfo.value < 0
              ? 'Negative activation - neural inhibition'
              : 'Zero activation - neutral state'}
        </p>
      </div>

      {/* Derived Address Info */}
      <div className="bg-black/30 rounded-lg p-3 space-y-2">
        <span className="text-xs text-white/60 flex items-center gap-1.5">
          <Hash className="w-3 h-3" />
          Derived Address Formula
        </span>
        <div className="text-xs font-mono text-white/80 space-y-1">
          <div>row = SHA256(seed)[0] % 128</div>
          <div>col = SHA256(seed)[1] % 128</div>
          <div className="text-cyan-400 mt-2">
            x = col - 64 = {cellInfo.col} - 64 = {cellInfo.annaX}
          </div>
          <div className="text-cyan-400">
            y = 63 - row = 63 - {cellInfo.row} = {cellInfo.annaY}
          </div>
        </div>
      </div>

      {/* XOR Layer Addresses */}
      <div className="bg-black/30 rounded-lg p-3 space-y-2">
        <span className="text-xs text-white/60 flex items-center gap-1.5">
          <Layers className="w-3 h-3" />
          XOR Layer Addresses
        </span>
        <div className="space-y-1">
          {XOR_LAYERS.map(layer => (
            <div
              key={layer.xor}
              className={`flex items-center justify-between text-xs py-1 px-2 rounded ${
                activeXorLayers.includes(layer.xor)
                  ? layer.bgColor
                  : 'opacity-40'
              }`}
            >
              <span style={{ color: layer.color }}>{layer.label}</span>
              <span className="text-white/60 font-mono">
                addr_{layer.xor}_{cellInfo.row}_{cellInfo.col}
              </span>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-white/30 mt-2">
          Each cell can generate 5 different Bitcoin addresses (one per XOR layer)
        </p>
      </div>

      {/* Quick Actions */}
      <div className="flex gap-2">
        <button className="flex-1 px-3 py-2 text-xs font-medium bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/30 rounded-lg text-cyan-400 transition-colors">
          View Addresses
        </button>
        <button className="flex-1 px-3 py-2 text-xs font-medium bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white/60 transition-colors">
          Check Blockchain
        </button>
      </div>
    </div>
  )
}

export default CellDetailPanel
