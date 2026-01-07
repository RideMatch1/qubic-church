'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X,
  Copy,
  Check,
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Hash,
  Binary,
  Grid3X3,
  Sparkles,
  Target,
  ArrowUpRight,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import type { CellDetailPanelProps, CellNeighbors } from './types'
import { SPECIAL_ROWS, SPECIAL_ADDRESSES, FORMULA_REFERENCES } from './constants'

export function CellDetailPanel({
  cell,
  neighbors,
  onClose,
  onNavigate,
}: CellDetailPanelProps) {
  const [copied, setCopied] = useState<string | null>(null)

  const handleCopy = async (text: string, label: string) => {
    await navigator.clipboard.writeText(text)
    setCopied(label)
    setTimeout(() => setCopied(null), 2000)
  }

  const neighborValues = [
    { key: 'topLeft', value: neighbors.topLeft, row: cell.row - 1, col: cell.col - 1 },
    { key: 'top', value: neighbors.top, row: cell.row - 1, col: cell.col },
    { key: 'topRight', value: neighbors.topRight, row: cell.row - 1, col: cell.col + 1 },
    { key: 'left', value: neighbors.left, row: cell.row, col: cell.col - 1 },
    { key: 'center', value: cell.value, row: cell.row, col: cell.col, isCenter: true },
    { key: 'right', value: neighbors.right, row: cell.row, col: cell.col + 1 },
    { key: 'bottomLeft', value: neighbors.bottomLeft, row: cell.row + 1, col: cell.col - 1 },
    { key: 'bottom', value: neighbors.bottom, row: cell.row + 1, col: cell.col },
    { key: 'bottomRight', value: neighbors.bottomRight, row: cell.row + 1, col: cell.col + 1 },
  ]

  const getValueColor = (value: number | undefined) => {
    if (value === undefined) return 'bg-gray-800 text-gray-600'
    if (value > 0) return 'bg-orange-500/20 text-orange-400'
    if (value < 0) return 'bg-blue-500/20 text-blue-400'
    return 'bg-gray-500/20 text-gray-400'
  }

  // Check for special addresses
  const isBootAddress = cell.address === SPECIAL_ADDRESSES.boot.address
  const isPoczAddress = cell.address === SPECIAL_ADDRESSES.pocz.address
  const specialRow = SPECIAL_ROWS[cell.row]

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="absolute top-4 right-4 w-80 bg-black/90 backdrop-blur-md border border-white/10 rounded-xl shadow-2xl pointer-events-auto overflow-hidden"
      style={{ maxHeight: 'calc(100% - 140px)' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <Hash className="w-4 h-4 text-purple-400" />
          <span className="font-bold text-white">Cell Details</span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 text-gray-400 hover:text-white"
          onClick={onClose}
        >
          <X className="w-4 h-4" />
        </Button>
      </div>

      <div className="overflow-y-auto p-4 space-y-4" style={{ maxHeight: 'calc(100% - 60px)' }}>
        {/* VIP Badge */}
        {cell.isVIP && cell.vipData && (
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="p-3 rounded-lg bg-gradient-to-r from-purple-500/20 to-orange-500/20 border border-purple-500/30"
          >
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-yellow-400" />
              <span className="text-sm font-bold text-yellow-400">VIP Address</span>
            </div>
            <div className="font-mono text-xs text-white break-all">
              {cell.vipData.bitcoinAddress}
            </div>
            <div className="mt-2 flex items-center gap-2 text-xs text-gray-400">
              <span>XOR: {cell.vipData.xorVariant}</span>
              <span>•</span>
              <span>{cell.vipData.method}</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="mt-2 h-7 text-xs text-purple-400 hover:text-purple-300 p-0"
              onClick={() =>
                window.open(
                  `https://mempool.space/address/${cell.vipData?.bitcoinAddress}`,
                  '_blank'
                )
              }
            >
              <ExternalLink className="w-3 h-3 mr-1" />
              View on Mempool
            </Button>
          </motion.div>
        )}

        {/* Special Address Badge */}
        {(isBootAddress || isPoczAddress) && (
          <div
            className={`p-3 rounded-lg border ${
              isBootAddress
                ? 'bg-yellow-500/10 border-yellow-500/30'
                : 'bg-emerald-500/10 border-emerald-500/30'
            }`}
          >
            <div className="flex items-center gap-2">
              <Target
                className={`w-4 h-4 ${isBootAddress ? 'text-yellow-400' : 'text-emerald-400'}`}
              />
              <span
                className={`text-sm font-bold ${
                  isBootAddress ? 'text-yellow-400' : 'text-emerald-400'
                }`}
              >
                {isBootAddress ? 'Boot Address' : 'POCZ Address'}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              {isBootAddress
                ? SPECIAL_ADDRESSES.boot.description
                : SPECIAL_ADDRESSES.pocz.description}
            </p>
            {isBootAddress && (
              <div className="mt-2 font-mono text-xs text-yellow-400/70">
                {FORMULA_REFERENCES.bootDerivation.equation}
              </div>
            )}
          </div>
        )}

        {/* Special Row Badge */}
        {specialRow && (
          <div
            className="p-3 rounded-lg border"
            style={{
              backgroundColor: `${specialRow.color}10`,
              borderColor: `${specialRow.color}40`,
            }}
          >
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: specialRow.color }}
              />
              <span className="text-sm font-bold" style={{ color: specialRow.color }}>
                {specialRow.name}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1">{specialRow.description}</p>
          </div>
        )}

        {/* Primary Info */}
        <div className="space-y-3">
          {/* Address */}
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">Address</span>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm text-white">{cell.address}</span>
              <Button
                variant="ghost"
                size="icon"
                className="h-5 w-5"
                onClick={() => handleCopy(cell.address.toString(), 'address')}
              >
                {copied === 'address' ? (
                  <Check className="w-3 h-3 text-green-400" />
                ) : (
                  <Copy className="w-3 h-3 text-gray-500" />
                )}
              </Button>
            </div>
          </div>

          {/* Position */}
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">Position</span>
            <span className="font-mono text-sm text-white">
              [{cell.row}, {cell.col}]
            </span>
          </div>

          {/* Value */}
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">Value</span>
            <span
              className={`font-mono text-lg font-bold ${
                cell.value > 0
                  ? 'text-orange-400'
                  : cell.value < 0
                    ? 'text-blue-400'
                    : 'text-gray-400'
              }`}
            >
              {cell.value}
            </span>
          </div>

          {/* Hex & Binary */}
          <div className="grid grid-cols-2 gap-2">
            <div className="p-2 rounded bg-white/5">
              <div className="text-[10px] text-gray-500 mb-1">Hex</div>
              <div className="font-mono text-sm text-purple-400">{cell.hex}</div>
            </div>
            <div className="p-2 rounded bg-white/5">
              <div className="text-[10px] text-gray-500 mb-1">Binary</div>
              <div className="font-mono text-xs text-cyan-400">{cell.binary}</div>
            </div>
          </div>
        </div>

        {/* Neighbor Grid */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Grid3X3 className="w-4 h-4 text-gray-500" />
            <span className="text-xs text-gray-500">Neighborhood</span>
          </div>
          <div className="grid grid-cols-3 gap-1">
            {neighborValues.map((n) => (
              <button
                key={n.key}
                className={`aspect-square rounded flex items-center justify-center font-mono text-xs transition-colors ${
                  (n as any).isCenter
                    ? 'ring-2 ring-white bg-white/20 text-white font-bold'
                    : n.value !== undefined
                      ? `${getValueColor(n.value)} hover:ring-1 hover:ring-white/50 cursor-pointer`
                      : 'bg-gray-800/50 text-gray-700 cursor-not-allowed'
                }`}
                onClick={() => {
                  if (n.value !== undefined && !(n as any).isCenter) {
                    onNavigate(n.row, n.col)
                  }
                }}
                disabled={n.value === undefined || (n as any).isCenter}
              >
                {n.value !== undefined ? n.value : '—'}
              </button>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div>
          <div className="text-xs text-gray-500 mb-2">Navigate</div>
          <div className="flex justify-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onNavigate(cell.row - 1, cell.col)}
              disabled={cell.row === 0}
            >
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex justify-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onNavigate(cell.row, cell.col - 1)}
              disabled={cell.col === 0}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onNavigate(cell.row, cell.col + 1)}
              disabled={cell.col === 127}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex justify-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onNavigate(cell.row + 1, cell.col)}
              disabled={cell.row === 127}
            >
              <ChevronDown className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Formula Reference (for Row 68) */}
        {cell.row === 68 && (
          <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/30">
            <div className="text-xs text-purple-400 font-medium mb-1">Row 68 Operations</div>
            <div className="font-mono text-xs text-gray-400 space-y-1">
              <div>Reads: {FORMULA_REFERENCES.row68Operations.reads}</div>
              <div>Writes: {FORMULA_REFERENCES.row68Operations.writes} (α)</div>
              <div>Ratio: {FORMULA_REFERENCES.row68Operations.ratio}</div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}
