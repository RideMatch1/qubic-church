/**
 * BITCOIN BRIDGE MONITOR - Main Component
 *
 * Live Bitcoin blockchain monitoring with:
 * - Strategic address watch list
 * - Batch verification against blockchain
 * - Real-time balance and activity tracking
 */

'use client'

import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Bitcoin,
  Eye,
  Search,
  RefreshCw,
  Download,
  Plus,
  Trash2,
  ExternalLink,
  AlertCircle,
  CheckCircle,
  Clock,
  Activity,
} from 'lucide-react'
import { StatCard, StatusBadge, type StatusType } from '../MonitoringTabs'
import { AddressWatchList } from './AddressWatchList'
import { BatchVerification } from './BatchVerification'

// =============================================================================
// TYPES
// =============================================================================

export interface WatchedAddress {
  address: string
  label: string
  addedAt: Date
  category: 'genesis' | 'patoshi' | 'cfb' | 'matrix' | 'custom'
}

export interface AddressData {
  address: string
  balance: number
  txCount: number
  firstSeen: Date | null
  lastSeen: Date | null
  status: StatusType
}

// =============================================================================
// STRATEGIC ADDRESSES (Pre-populated)
// =============================================================================

export const STRATEGIC_ADDRESSES: WatchedAddress[] = [
  {
    address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
    label: 'Genesis Block (Unspendable)',
    addedAt: new Date('2009-01-03'),
    category: 'genesis',
  },
  {
    address: '12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX',
    label: 'Block 1 - First Spendable',
    addedAt: new Date('2009-01-09'),
    category: 'patoshi',
  },
  {
    address: '1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1',
    label: 'Block 2 - Satoshi Mining',
    addedAt: new Date('2009-01-09'),
    category: 'patoshi',
  },
  {
    address: '1FvzCLoTPGANNjWoUo6jUGuAG3wg1w4YjR',
    label: 'Block 3 - Early Mining',
    addedAt: new Date('2009-01-09'),
    category: 'patoshi',
  },
  {
    address: '1CFBhVCZsrwKSZMHcFcjvBDYsHzMkPJjRT',
    label: 'CFB Signature Address',
    addedAt: new Date('2022-01-01'),
    category: 'cfb',
  },
]

// =============================================================================
// BITCOIN BRIDGE MONITOR
// =============================================================================

export function BitcoinBridgeMonitor() {
  // State
  const [watchList, setWatchList] = useState<WatchedAddress[]>(STRATEGIC_ADDRESSES)
  const [addressData, setAddressData] = useState<Map<string, AddressData>>(new Map())
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [activeSection, setActiveSection] = useState<'watchlist' | 'batch'>('watchlist')

  // Calculate summary stats
  const stats = {
    tracked: watchList.length,
    totalBalance: Array.from(addressData.values()).reduce((sum, a) => sum + a.balance, 0),
    activeToday: Array.from(addressData.values()).filter(a => {
      if (!a.lastSeen) return false
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      return a.lastSeen >= today
    }).length,
    totalTx: Array.from(addressData.values()).reduce((sum, a) => sum + a.txCount, 0),
  }

  // Add address to watch list
  const addAddress = useCallback((address: string, label: string) => {
    if (watchList.some(w => w.address === address)) return
    setWatchList(prev => [...prev, {
      address,
      label,
      addedAt: new Date(),
      category: 'custom',
    }])
  }, [watchList])

  // Remove address from watch list
  const removeAddress = useCallback((address: string) => {
    setWatchList(prev => prev.filter(w => w.address !== address))
    setAddressData(prev => {
      const next = new Map(prev)
      next.delete(address)
      return next
    })
  }, [])

  // Update address data
  const updateAddressData = useCallback((address: string, data: AddressData) => {
    setAddressData(prev => new Map(prev).set(address, data))
    setLastUpdate(new Date())
  }, [])

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Tracked Addresses"
          value={stats.tracked.toLocaleString()}
          icon={<Eye className="w-4 h-4" />}
          color="text-orange-400"
        />
        <StatCard
          label="Total Balance"
          value={`${stats.totalBalance.toFixed(4)} BTC`}
          icon={<Bitcoin className="w-4 h-4" />}
          color="text-yellow-400"
          subtext={`≈ $${(stats.totalBalance * 100000).toLocaleString()}`}
        />
        <StatCard
          label="Active Today"
          value={stats.activeToday}
          icon={<Activity className="w-4 h-4" />}
          color="text-green-400"
        />
        <StatCard
          label="Total Transactions"
          value={stats.totalTx.toLocaleString()}
          icon={<RefreshCw className="w-4 h-4" />}
          color="text-blue-400"
        />
      </div>

      {/* Last Update Info */}
      {lastUpdate && (
        <div className="flex items-center gap-2 text-xs text-white/40">
          <Clock className="w-3 h-3" />
          Last updated: {lastUpdate.toLocaleTimeString()}
        </div>
      )}

      {/* Section Toggle */}
      <div className="flex gap-2 border-b border-white/10 pb-2">
        <button
          onClick={() => setActiveSection('watchlist')}
          className={`px-4 py-2 rounded-t-lg text-sm font-medium transition-colors ${
            activeSection === 'watchlist'
              ? 'bg-orange-500/20 text-orange-400'
              : 'text-white/60 hover:text-white'
          }`}
        >
          <Eye className="w-4 h-4 inline mr-2" />
          Watch List
        </button>
        <button
          onClick={() => setActiveSection('batch')}
          className={`px-4 py-2 rounded-t-lg text-sm font-medium transition-colors ${
            activeSection === 'batch'
              ? 'bg-blue-500/20 text-blue-400'
              : 'text-white/60 hover:text-white'
          }`}
        >
          <Search className="w-4 h-4 inline mr-2" />
          Batch Verification
        </button>
      </div>

      {/* Content Sections */}
      <AnimatePresence mode="wait">
        {activeSection === 'watchlist' ? (
          <motion.div
            key="watchlist"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <AddressWatchList
              watchList={watchList}
              addressData={addressData}
              onAddAddress={addAddress}
              onRemoveAddress={removeAddress}
              onUpdateData={updateAddressData}
            />
          </motion.div>
        ) : (
          <motion.div
            key="batch"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <BatchVerification />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default BitcoinBridgeMonitor
