/**
 * MONITORING TABS - Navigation Component
 *
 * Tab navigation for the unified monitoring center.
 * Handles Qubic Network and Bitcoin Bridge monitors.
 */

'use client'

import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { Bitcoin, Zap } from 'lucide-react'

// =============================================================================
// TYPES
// =============================================================================

export type MonitoringTabId = 'qubic' | 'bitcoin'

interface MonitoringTab {
  id: MonitoringTabId
  label: string
  shortLabel: string
  icon: ReactNode
  description: string
  color: string
  bgColor: string
}

interface MonitoringTabsProps {
  activeTab: MonitoringTabId
  onTabChange: (tab: MonitoringTabId) => void
  children: ReactNode
}

// =============================================================================
// TAB CONFIGURATION
// =============================================================================

export const MONITORING_TABS: MonitoringTab[] = [
  {
    id: 'qubic',
    label: 'Qubic Network',
    shortLabel: 'Qubic',
    icon: <Zap className="w-4 h-4" />,
    description: 'Live network metrics, epoch data, computor stats',
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/20',
  },
  {
    id: 'bitcoin',
    label: 'Bitcoin Bridge',
    shortLabel: 'Bitcoin',
    icon: <Bitcoin className="w-4 h-4" />,
    description: 'Address verification, watch list, blockchain data',
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/20',
  },
]

// =============================================================================
// MONITORING TABS COMPONENT
// =============================================================================

export function MonitoringTabs({ activeTab, onTabChange, children }: MonitoringTabsProps) {
  return (
    <div className="w-full">
      {/* Tab Navigation */}
      <div className="border-b border-white/10 bg-black/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4">
          <nav className="flex gap-1 py-2" role="tablist">
            {MONITORING_TABS.map((tab) => {
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  role="tab"
                  aria-selected={isActive}
                  aria-controls={`panel-${tab.id}`}
                  onClick={() => onTabChange(tab.id)}
                  className={`
                    relative flex items-center gap-2 px-4 py-3 rounded-t-lg
                    font-medium text-sm transition-all duration-200
                    ${isActive
                      ? `${tab.bgColor} ${tab.color} border-b-2 border-current`
                      : 'text-white/60 hover:text-white hover:bg-white/5'
                    }
                  `}
                >
                  {/* Icon */}
                  <span className={isActive ? tab.color : 'text-white/40'}>
                    {tab.icon}
                  </span>

                  {/* Label - Hide on mobile, show short version on tablet */}
                  <span className="hidden sm:inline md:hidden">{tab.shortLabel}</span>
                  <span className="hidden md:inline">{tab.label}</span>

                  {/* Active indicator */}
                  {isActive && (
                    <motion.div
                      layoutId="activeTabIndicator"
                      className={`absolute bottom-0 left-0 right-0 h-0.5 ${tab.bgColor.replace('/20', '')}`}
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                    />
                  )}
                </button>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <div className="container mx-auto px-4 py-6">
        {children}
      </div>
    </div>
  )
}

// =============================================================================
// TAB PANEL WRAPPER
// =============================================================================

interface TabPanelProps {
  id: MonitoringTabId
  activeTab: MonitoringTabId
  children: ReactNode
}

export function TabPanel({ id, activeTab, children }: TabPanelProps) {
  if (id !== activeTab) return null

  const tab = MONITORING_TABS.find(t => t.id === id)

  return (
    <motion.div
      id={`panel-${id}`}
      role="tabpanel"
      aria-labelledby={`tab-${id}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
    >
      {/* Tab Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className={`p-2 rounded-lg ${tab?.bgColor}`}>
            <span className={tab?.color}>{tab?.icon}</span>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">{tab?.label}</h2>
            <p className="text-sm text-white/60">{tab?.description}</p>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      {children}
    </motion.div>
  )
}

// =============================================================================
// STATS CARD COMPONENT (Reusable)
// =============================================================================

interface StatCardProps {
  label: string
  value: string | number
  icon?: ReactNode
  color?: string
  loading?: boolean
  subtext?: string
}

export function StatCard({ label, value, icon, color = 'text-white', loading, subtext }: StatCardProps) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/[0.07] transition-colors">
      <div className="flex items-center gap-2 mb-2">
        {icon && <span className="text-white/40">{icon}</span>}
        <span className="text-xs font-medium text-white/60 uppercase tracking-wider">{label}</span>
      </div>
      {loading ? (
        <div className="h-8 w-24 bg-white/10 animate-pulse rounded" />
      ) : (
        <>
          <div className={`text-2xl font-bold ${color}`}>{value}</div>
          {subtext && <div className="text-xs text-white/40 mt-1">{subtext}</div>}
        </>
      )}
    </div>
  )
}

// =============================================================================
// STATUS BADGE COMPONENT (Reusable)
// =============================================================================

export type StatusType = 'active' | 'dormant' | 'spent' | 'unused' | 'error' | 'loading'

interface StatusBadgeProps {
  status: StatusType
  label?: string
}

const STATUS_STYLES: Record<StatusType, { bg: string; text: string; label: string }> = {
  active: { bg: 'bg-green-500/20', text: 'text-green-400', label: 'Active' },
  dormant: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', label: 'Dormant' },
  spent: { bg: 'bg-zinc-500/20', text: 'text-zinc-400', label: 'Spent' },
  unused: { bg: 'bg-zinc-700/30', text: 'text-zinc-500', label: 'Unused' },
  error: { bg: 'bg-red-500/20', text: 'text-red-400', label: 'Error' },
  loading: { bg: 'bg-blue-500/20', text: 'text-blue-400', label: 'Loading' },
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const style = STATUS_STYLES[status]
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${style.bg} ${style.text}`}>
      {label || style.label}
    </span>
  )
}

export default MonitoringTabs
