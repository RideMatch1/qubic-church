'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  DISCOVERIES,
  DISCOVERY_PRESETS,
  TIMELINE,
  getDiscoveriesByCategory,
  type Discovery,
  type DiscoveryCategory,
} from './discoveries'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  ChevronDown,
  ChevronUp,
  Sparkles,
  Calculator,
  FlipHorizontal,
  MessageCircle,
  Bitcoin,
  Eye,
  EyeOff,
  MapPin,
  Calendar,
  Zap,
  Target,
  X,
} from 'lucide-react'

// =============================================================================
// CATEGORY CONFIG
// =============================================================================

const CATEGORY_CONFIG: Record<
  DiscoveryCategory,
  { label: string; icon: React.ReactNode; color: string }
> = {
  'easter-egg': {
    label: 'Easter Eggs',
    icon: <Sparkles className="h-3.5 w-3.5" />,
    color: 'bg-amber-500',
  },
  mathematical: {
    label: 'Mathematical',
    icon: <Calculator className="h-3.5 w-3.5" />,
    color: 'bg-blue-500',
  },
  symmetry: {
    label: 'Symmetry',
    icon: <FlipHorizontal className="h-3.5 w-3.5" />,
    color: 'bg-cyan-500',
  },
  'word-encoding': {
    label: 'Word Encodings',
    icon: <MessageCircle className="h-3.5 w-3.5" />,
    color: 'bg-yellow-500',
  },
  'bitcoin-connection': {
    label: 'Bitcoin',
    icon: <Bitcoin className="h-3.5 w-3.5" />,
    color: 'bg-orange-500',
  },
  balance: {
    label: 'Balance',
    icon: <Target className="h-3.5 w-3.5" />,
    color: 'bg-gray-500',
  },
  'special-value': {
    label: 'Special Values',
    icon: <Zap className="h-3.5 w-3.5" />,
    color: 'bg-purple-500',
  },
}

// =============================================================================
// DISCOVERY CARD
// =============================================================================

function DiscoveryCard({
  discovery,
  isActive,
  onClick,
  onJump,
}: {
  discovery: Discovery
  isActive: boolean
  onClick: () => void
  onJump: (row: number, col: number) => void
}) {
  const category = CATEGORY_CONFIG[discovery.category]

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={`group cursor-pointer rounded-lg border p-3 transition-all ${
        isActive
          ? 'border-white/30 bg-white/10'
          : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/8'
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Badge
              variant="secondary"
              className={`${category.color} text-white text-[10px] px-1.5 py-0`}
            >
              {category.icon}
            </Badge>
            <span className="text-sm font-semibold text-white truncate">
              {discovery.name}
            </span>
          </div>
          <p className="text-xs text-white/60 line-clamp-2">{discovery.description}</p>
          {discovery.formula && (
            <code className="mt-1 block text-[10px] text-amber-400/80 font-mono truncate">
              {discovery.formula}
            </code>
          )}
        </div>
        {discovery.positions && discovery.positions.length > 0 && (
          <Button
            size="sm"
            variant="ghost"
            className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100"
            onClick={(e) => {
              e.stopPropagation()
              const pos = discovery.positions?.[0]
              if (pos) {
                onJump(pos.row, pos.col)
              }
            }}
          >
            <MapPin className="h-3.5 w-3.5" />
          </Button>
        )}
      </div>

      {/* Expanded content */}
      <AnimatePresence>
        {isActive && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="mt-3 pt-3 border-t border-white/10">
              <p className="text-xs text-green-400/90 mb-2">{discovery.significance}</p>
              {discovery.positions && (
                <div className="flex flex-wrap gap-1">
                  {discovery.positions.slice(0, 6).map((pos, i) => (
                    <button
                      key={i}
                      className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-white/10 hover:bg-white/20 text-white/80"
                      onClick={(e) => {
                        e.stopPropagation()
                        onJump(pos.row, pos.col)
                      }}
                    >
                      [{pos.row},{pos.col}]
                      {pos.label && ` ${pos.label}`}
                    </button>
                  ))}
                  {discovery.positions.length > 6 && (
                    <span className="px-1.5 py-0.5 text-[10px] text-white/50">
                      +{discovery.positions.length - 6} more
                    </span>
                  )}
                </div>
              )}
              {discovery.rowPairs && (
                <div className="flex flex-wrap gap-1">
                  {discovery.rowPairs.map((pair, i) => (
                    <span
                      key={i}
                      className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-white/10 text-white/80"
                    >
                      R{pair.row1}+R{pair.row2}={pair.sum}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// =============================================================================
// QUICK JUMP BUTTONS
// =============================================================================

function QuickJumpButtons({
  onJump,
}: {
  onJump: (row: number, col: number) => void
}) {
  return (
    <div className="flex flex-wrap gap-1">
      {DISCOVERY_PRESETS.slice(0, 8).map((preset) => (
        <button
          key={preset.id}
          className="px-2 py-1 rounded text-[10px] font-medium transition-colors"
          style={{
            backgroundColor: `${preset.color}20`,
            color: preset.color,
          }}
          onClick={() => onJump(preset.row, preset.col)}
        >
          {preset.label}
        </button>
      ))}
    </div>
  )
}

// =============================================================================
// TIMELINE WIDGET
// =============================================================================

function TimelineWidget() {
  const today = new Date()
  const bloodMoon = new Date('2026-03-03')
  const easter = new Date('2026-04-05')
  const daysToBloodMoon = Math.ceil((bloodMoon.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
  const daysToEaster = Math.ceil((easter.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))

  return (
    <div className="rounded-lg bg-gradient-to-r from-red-500/20 via-purple-500/20 to-amber-500/20 p-3 border border-white/10">
      <div className="flex items-center gap-2 mb-2">
        <Calendar className="h-4 w-4 text-amber-400" />
        <span className="text-xs font-semibold text-white">Timeline</span>
      </div>
      <div className="space-y-1.5">
        <div className="flex justify-between text-[11px]">
          <span className="text-red-400">Blood Moon</span>
          <span className="text-white/80 font-mono">{daysToBloodMoon} days</span>
        </div>
        <div className="h-1.5 rounded-full bg-white/10 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-red-500 to-purple-500"
            style={{ width: `${Math.max(0, 100 - (daysToBloodMoon / 40) * 100)}%` }}
          />
        </div>
        <div className="flex justify-between text-[11px]">
          <span className="text-amber-400">Easter</span>
          <span className="text-white/80 font-mono">{daysToEaster} days</span>
        </div>
        <div className="h-1.5 rounded-full bg-white/10 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-amber-500"
            style={{ width: `${Math.max(0, 100 - (daysToEaster / 70) * 100)}%` }}
          />
        </div>
      </div>
      <div className="mt-2 pt-2 border-t border-white/10 text-center">
        <code className="text-[10px] text-green-400">"THE" = 33 = Days between events</code>
      </div>
    </div>
  )
}

// =============================================================================
// MAIN DISCOVERIES PANEL
// =============================================================================

export interface DiscoveriesPanelProps {
  isOpen: boolean
  onClose: () => void
  onJumpToCell: (row: number, col: number) => void
  categoryVisibility: Record<string, boolean>
  onToggleCategory: (category: string) => void
  showLabels: boolean
  onToggleLabels: () => void
  showPatternLines: boolean
  onTogglePatternLines: () => void
  showRowHighlights: boolean
  onToggleRowHighlights: () => void
  activeDiscoveryId: string | null
  onSetActiveDiscovery: (id: string | null) => void
}

export function DiscoveriesPanel({
  isOpen,
  onClose,
  onJumpToCell,
  categoryVisibility,
  onToggleCategory,
  showLabels,
  onToggleLabels,
  showPatternLines,
  onTogglePatternLines,
  showRowHighlights,
  onToggleRowHighlights,
  activeDiscoveryId,
  onSetActiveDiscovery,
}: DiscoveriesPanelProps) {
  const [expandedCategory, setExpandedCategory] = useState<DiscoveryCategory | null>(
    'easter-egg'
  )

  if (!isOpen) return null

  return (
    <motion.div
      initial={{ x: 400, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 400, opacity: 0 }}
      className="absolute top-4 right-4 w-80 max-h-[calc(100vh-8rem)] bg-black/90 backdrop-blur-xl rounded-xl border border-white/20 shadow-2xl overflow-hidden z-50"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10 bg-gradient-to-r from-amber-500/10 to-purple-500/10">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-amber-400" />
          <h3 className="font-bold text-white">Discoveries</h3>
          <Badge variant="secondary" className="bg-white/10 text-white/80 text-[10px]">
            {DISCOVERIES.length}
          </Badge>
        </div>
        <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <ScrollArea className="h-[calc(100vh-16rem)]">
        <div className="p-4 space-y-4">
          {/* Timeline */}
          <TimelineWidget />

          {/* Quick Jump */}
          <div>
            <h4 className="text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">
              Quick Jump
            </h4>
            <QuickJumpButtons onJump={onJumpToCell} />
          </div>

          {/* Toggle Controls */}
          <div className="grid grid-cols-2 gap-2">
            <button
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                showLabels ? 'bg-white/20 text-white' : 'bg-white/5 text-white/60'
              }`}
              onClick={onToggleLabels}
            >
              {showLabels ? <Eye className="h-3.5 w-3.5" /> : <EyeOff className="h-3.5 w-3.5" />}
              Labels
            </button>
            <button
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                showPatternLines ? 'bg-white/20 text-white' : 'bg-white/5 text-white/60'
              }`}
              onClick={onTogglePatternLines}
            >
              Lines
            </button>
            <button
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                showRowHighlights ? 'bg-white/20 text-white' : 'bg-white/5 text-white/60'
              }`}
              onClick={onToggleRowHighlights}
            >
              Rows
            </button>
            {activeDiscoveryId && (
              <button
                className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium bg-amber-500/20 text-amber-400"
                onClick={() => onSetActiveDiscovery(null)}
              >
                Clear Focus
              </button>
            )}
          </div>

          {/* Categories */}
          {(Object.keys(CATEGORY_CONFIG) as DiscoveryCategory[]).map((category) => {
            const config = CATEGORY_CONFIG[category]
            const discoveries = getDiscoveriesByCategory(category)
            const isExpanded = expandedCategory === category
            const isVisible = categoryVisibility[category] ?? true

            return (
              <div key={category} className="space-y-2">
                <button
                  className="flex items-center justify-between w-full px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                  onClick={() => setExpandedCategory(isExpanded ? null : category)}
                >
                  <div className="flex items-center gap-2">
                    <button
                      className={`w-5 h-5 rounded flex items-center justify-center transition-colors ${
                        isVisible ? config.color : 'bg-white/10'
                      }`}
                      onClick={(e) => {
                        e.stopPropagation()
                        onToggleCategory(category)
                      }}
                    >
                      {isVisible ? (
                        <Eye className="h-3 w-3 text-white" />
                      ) : (
                        <EyeOff className="h-3 w-3 text-white/50" />
                      )}
                    </button>
                    <span className="text-sm font-medium text-white">{config.label}</span>
                    <Badge
                      variant="secondary"
                      className="bg-white/10 text-white/60 text-[10px] px-1.5"
                    >
                      {discoveries.length}
                    </Badge>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="h-4 w-4 text-white/40" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-white/40" />
                  )}
                </button>

                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="space-y-2 overflow-hidden pl-2"
                    >
                      {discoveries.map((discovery) => (
                        <DiscoveryCard
                          key={discovery.id}
                          discovery={discovery}
                          isActive={activeDiscoveryId === discovery.id}
                          onClick={() =>
                            onSetActiveDiscovery(
                              activeDiscoveryId === discovery.id ? null : discovery.id
                            )
                          }
                          onJump={onJumpToCell}
                        />
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )
          })}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-3 border-t border-white/10 bg-white/5">
        <p className="text-[10px] text-white/40 text-center">
          Analysis: January 26, 2026 | 500,000+ tests performed
        </p>
      </div>
    </motion.div>
  )
}

export default DiscoveriesPanel
