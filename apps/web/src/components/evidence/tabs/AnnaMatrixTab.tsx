'use client'

import { motion } from 'framer-motion'
import dynamic from 'next/dynamic'
import { Download, Share2, ExternalLink, Keyboard, Sparkles, Grid3X3, Binary, Target, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

// Dynamic import for 3D scene to avoid SSR issues
const AnnaGridScene = dynamic(
  () => import('../anna-grid/AnnaGridScene'),
  {
    loading: () => (
      <div className="w-full h-[700px] bg-gradient-to-b from-black via-gray-900 to-black rounded-lg border border-border flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="relative w-24 h-24">
            <div className="absolute inset-0 grid grid-cols-4 grid-rows-4 gap-1 opacity-50">
              {Array.from({ length: 16 }).map((_, i) => (
                <div
                  key={i}
                  className="bg-gradient-to-br from-blue-500 to-orange-500 rounded-sm animate-pulse"
                  style={{ animationDelay: `${i * 50}ms` }}
                />
              ))}
            </div>
            <div className="absolute inset-4 flex items-center justify-center">
              <div className="text-lg font-bold text-white">128²</div>
            </div>
          </div>
          <span className="text-muted-foreground text-sm">Loading Anna Matrix Explorer...</span>
        </div>
      </div>
    ),
    ssr: false,
  }
)

// Quick action buttons config
const QUICK_ACTIONS = [
  {
    id: 'download',
    label: 'Download JSON',
    icon: Download,
    href: '/data/anna-matrix.json',
    download: true,
  },
  {
    id: 'docs',
    label: 'Documentation',
    icon: ExternalLink,
    href: '/docs/anna-matrix',
  },
]

// Keyboard shortcuts for this tab
const KEYBOARD_HINTS = [
  { keys: ['F'], action: 'Fullscreen' },
  { keys: ['T'], action: '2D/3D Toggle' },
  { keys: ['W', 'A', 'S', 'D'], action: 'Navigate' },
  { keys: ['?'], action: 'All Shortcuts' },
]

// Stats with enhanced styling
const MATRIX_STATS = [
  {
    value: '16,384',
    label: 'Total Cells',
    description: '128 × 128 grid',
    icon: Grid3X3,
    color: 'text-primary',
    bgColor: 'bg-primary/10',
    borderColor: 'border-primary/30',
  },
  {
    value: '30',
    label: 'VIP Addresses',
    description: 'Bitcoin connections',
    icon: Sparkles,
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30',
  },
  {
    value: '3',
    label: 'Special Rows',
    description: 'Row 21, 68, 96',
    icon: Target,
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
  },
  {
    value: '[-128, 127]',
    label: 'Value Range',
    description: 'Signed byte',
    icon: Binary,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
  },
]

// Special row explanations
const SPECIAL_ROWS = [
  {
    row: 21,
    name: 'Bitcoin Input',
    description: 'Receives Block #283 data. Boot address 2692 starts execution here.',
    color: '#F7931A',
    bgClass: 'bg-orange-500/10 border-orange-500/30',
    textClass: 'text-orange-400',
  },
  {
    row: 68,
    name: 'Transformation',
    description: 'Bitcoin → Qubic conversion. 137 writes match the fine structure constant α.',
    color: '#8B5CF6',
    bgClass: 'bg-purple-500/10 border-purple-500/30',
    textClass: 'text-purple-400',
  },
  {
    row: 96,
    name: 'Output',
    description: 'Final computation output. Contains POCZ address at position [96, 84].',
    color: '#22C55E',
    bgClass: 'bg-emerald-500/10 border-emerald-500/30',
    textClass: 'text-emerald-400',
  },
]

export default function AnnaMatrixTab() {
  const [showShortcuts, setShowShortcuts] = useState(false)

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Anna Matrix Explorer',
          text: 'Explore the 128×128 cryptographic matrix connecting Bitcoin and Qubic',
          url: window.location.href + '#matrix',
        })
      } catch {
        // User cancelled or error
      }
    } else {
      // Fallback: copy to clipboard
      await navigator.clipboard.writeText(window.location.href + '#matrix')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header with quick actions */}
      <motion.div
        className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-gradient-to-br from-orange-500/20 to-purple-500/20 border border-orange-500/30">
              <Grid3X3 className="w-5 h-5 text-orange-400" />
            </div>
            <div>
              <h3 className="text-xl font-semibold">Anna Matrix Explorer</h3>
              <p className="text-sm text-muted-foreground">128×128 Cryptographic Matrix</p>
            </div>
          </div>
          <p className="text-sm text-muted-foreground max-w-2xl">
            Interactive 3D visualization of the mathematical structure connecting Bitcoin and Qubic.
            Real data from anna-matrix.json with 16,384 cells and 30 VIP addresses.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center gap-2 flex-wrap">
          {QUICK_ACTIONS.map((action) => {
            const Icon = action.icon
            return action.download ? (
              <a
                key={action.id}
                href={action.href}
                download
                className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-card hover:bg-muted border border-border rounded-lg transition-colors"
              >
                <Icon className="w-4 h-4" />
                <span>{action.label}</span>
              </a>
            ) : (
              <a
                key={action.id}
                href={action.href}
                className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-card hover:bg-muted border border-border rounded-lg transition-colors"
              >
                <Icon className="w-4 h-4" />
                <span>{action.label}</span>
              </a>
            )
          })}
          <Button
            variant="outline"
            size="sm"
            onClick={handleShare}
            className="gap-2"
          >
            <Share2 className="w-4 h-4" />
            Share
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowShortcuts(!showShortcuts)}
            className="gap-2"
          >
            <Keyboard className="w-4 h-4" />
          </Button>
        </div>
      </motion.div>

      {/* Keyboard shortcuts hint */}
      {showShortcuts && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="flex flex-wrap items-center gap-4 p-3 bg-muted/50 rounded-lg border border-border"
        >
          <span className="text-xs text-muted-foreground font-medium">Shortcuts:</span>
          {KEYBOARD_HINTS.map((hint) => (
            <div key={hint.action} className="flex items-center gap-1.5 text-xs">
              <div className="flex gap-0.5">
                {hint.keys.map((key) => (
                  <kbd
                    key={key}
                    className="px-1.5 py-0.5 bg-background border border-border rounded text-[10px] font-mono"
                  >
                    {key}
                  </kbd>
                ))}
              </div>
              <span className="text-muted-foreground">{hint.action}</span>
            </div>
          ))}
        </motion.div>
      )}

      {/* 3D Scene */}
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        <AnnaGridScene />
      </motion.div>

      {/* Statistics Grid */}
      <motion.div
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        {MATRIX_STATS.map((stat, idx) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              className={`relative p-4 rounded-xl border overflow-hidden group hover:scale-[1.02] transition-transform ${stat.bgColor} ${stat.borderColor}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + idx * 0.05 }}
            >
              <div className="absolute -right-4 -top-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <Icon className="w-16 h-16" />
              </div>
              <div className="relative">
                <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
                <div className="text-sm font-medium text-foreground">{stat.label}</div>
                <div className="text-xs text-muted-foreground">{stat.description}</div>
              </div>
            </motion.div>
          )
        })}
      </motion.div>

      {/* Special Rows Explanation */}
      <motion.div
        className="grid md:grid-cols-3 gap-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        {SPECIAL_ROWS.map((row, idx) => (
          <motion.div
            key={row.row}
            className={`p-4 rounded-xl border ${row.bgClass} hover:scale-[1.01] transition-transform`}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 + idx * 0.1 }}
          >
            <div className="flex items-center gap-2 mb-2">
              <div
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: row.color }}
              />
              <span className={`font-semibold ${row.textClass}`}>
                Row {row.row} - {row.name}
              </span>
            </div>
            <p className="text-sm text-muted-foreground">{row.description}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* Footer hint */}
      <motion.div
        className="flex items-center justify-center gap-4 pt-4 text-xs text-muted-foreground/50"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <div className="flex items-center gap-1">
          <Zap className="w-3 h-3" />
          <span>Real-time 3D rendering</span>
        </div>
        <span className="text-muted-foreground/20">•</span>
        <div className="flex items-center gap-1">
          <Grid3X3 className="w-3 h-3" />
          <span>Verified on-chain data</span>
        </div>
        <span className="text-muted-foreground/20">•</span>
        <div className="flex items-center gap-1">
          <Sparkles className="w-3 h-3" />
          <span>30 VIP Bitcoin addresses</span>
        </div>
      </motion.div>
    </div>
  )
}
