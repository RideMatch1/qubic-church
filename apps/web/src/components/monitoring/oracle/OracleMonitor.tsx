'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { SignalCountdown } from './SignalCountdown'
import { AddressWatch } from './AddressWatch'
import { OracleInfo } from './OracleInfo'
import { OraclePriceGrid } from './OraclePriceGrid'
import { OraclePredictionTracker } from './OraclePredictionTracker'
import { OracleHealthDashboard } from './OracleHealthDashboard'
import { OracleLiveQueries } from './OracleLiveQueries'

interface OracleMonitorProps {
  tick: number
  epoch: number
  loading: boolean
}

const TABS = [
  { id: 'onchain', label: 'On-Chain', icon: '\u26D3' },
  { id: 'prices', label: 'Prices', icon: '\u25C9' },
  { id: 'prophecy', label: 'Prophecy', icon: '\u2726' },
  { id: 'protocol', label: 'Protocol', icon: '\u2261' },
] as const

type TabId = typeof TABS[number]['id']

export function OracleMonitor({ tick, epoch, loading }: OracleMonitorProps) {
  const [activeTab, setActiveTab] = useState<TabId>('onchain')

  return (
    <div className="backdrop-blur-xl bg-white/[0.02] border border-white/[0.08] rounded-xl p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-zinc-200">Oracle Machine</span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 font-medium border border-cyan-500/20">
            LIVE
          </span>
        </div>
        <span className="text-xs text-zinc-600">Launched Feb 11, 2026</span>
      </div>

      {/* 3-Column Grid (original) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-5">
        <div className="bg-zinc-950/50 rounded-lg p-4 border border-zinc-800/50">
          <SignalCountdown />
        </div>
        <div className="bg-zinc-950/50 rounded-lg p-4 border border-zinc-800/50">
          <AddressWatch />
        </div>
        <div className="bg-zinc-950/50 rounded-lg p-4 border border-zinc-800/50">
          <OracleInfo tick={tick} epoch={epoch} />
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex items-center gap-1 mb-4 border-b border-white/[0.06] pb-px">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`relative px-4 py-2 text-xs font-medium transition-colors ${
              activeTab === tab.id
                ? 'text-zinc-200'
                : 'text-zinc-500 hover:text-zinc-400'
            }`}
          >
            <span className="flex items-center gap-1.5">
              <span className="text-[10px]">{tab.icon}</span>
              <span className="uppercase tracking-[0.15em]">{tab.label}</span>
            </span>
            {activeTab === tab.id && (
              <motion.div
                layoutId="oracle-tab-indicator"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400/50"
                transition={{ type: 'spring', stiffness: 400, damping: 30 }}
              />
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
        >
          {activeTab === 'onchain' && <OracleLiveQueries />}
          {activeTab === 'prices' && <OraclePriceGrid />}
          {activeTab === 'prophecy' && <OraclePredictionTracker />}
          {activeTab === 'protocol' && <OracleHealthDashboard />}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
