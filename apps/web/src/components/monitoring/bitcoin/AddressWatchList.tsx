/**
 * ADDRESS WATCH LIST - Component
 *
 * Displays and manages the list of watched Bitcoin addresses.
 * Fetches live data from blockchain APIs.
 */

'use client'

import { useState, useCallback, useEffect } from 'react'
import {
  Plus,
  Trash2,
  ExternalLink,
  RefreshCw,
  Copy,
  Check,
  AlertCircle,
} from 'lucide-react'
import { StatusBadge } from '../MonitoringTabs'
import type { WatchedAddress, AddressData } from './BitcoinBridgeMonitor'

// =============================================================================
// TYPES
// =============================================================================

interface AddressWatchListProps {
  watchList: WatchedAddress[]
  addressData: Map<string, AddressData>
  onAddAddress: (address: string, label: string) => void
  onRemoveAddress: (address: string) => void
  onUpdateData: (address: string, data: AddressData) => void
}

// =============================================================================
// CATEGORY STYLES
// =============================================================================

const CATEGORY_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  genesis: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', label: 'Genesis' },
  patoshi: { bg: 'bg-orange-500/20', text: 'text-orange-400', label: 'Patoshi' },
  cfb: { bg: 'bg-purple-500/20', text: 'text-purple-400', label: 'CFB' },
  matrix: { bg: 'bg-cyan-500/20', text: 'text-cyan-400', label: 'Matrix' },
  custom: { bg: 'bg-zinc-500/20', text: 'text-zinc-400', label: 'Custom' },
}

// =============================================================================
// ADDRESS WATCH LIST COMPONENT
// =============================================================================

export function AddressWatchList({
  watchList,
  addressData,
  onAddAddress,
  onRemoveAddress,
  onUpdateData,
}: AddressWatchListProps) {
  // State
  const [newAddress, setNewAddress] = useState('')
  const [newLabel, setNewLabel] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [loadingAddresses, setLoadingAddresses] = useState<Set<string>>(new Set())
  const [copiedAddress, setCopiedAddress] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Fetch address data from blockchain
  const fetchAddressData = useCallback(async (address: string) => {
    setLoadingAddresses(prev => new Set(prev).add(address))
    setError(null)

    try {
      // Use Mempool.space API with proper CORS headers
      const response = await fetch(`https://mempool.space/api/address/${address}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      })

      if (!response.ok) {
        if (response.status === 429) {
          throw new Error('Rate limited - please wait before retrying')
        }
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      // Calculate status
      let status: AddressData['status'] = 'unused'
      const balance = (data.chain_stats.funded_txo_sum - data.chain_stats.spent_txo_sum) / 100000000
      const txCount = data.chain_stats.tx_count

      if (txCount === 0) {
        status = 'unused'
      } else if (balance > 0) {
        status = 'active'
      } else if (data.chain_stats.spent_txo_count > 0) {
        status = 'spent'
      } else {
        status = 'dormant'
      }

      const addressInfo: AddressData = {
        address,
        balance,
        txCount,
        firstSeen: null,
        lastSeen: null,
        status,
      }

      onUpdateData(address, addressInfo)
      setError(null)
    } catch (err) {
      console.error('Error fetching address:', err)
      // Don't show error for every address, just log it
      // The UI will show "—" for addresses without data
    } finally {
      setLoadingAddresses(prev => {
        const next = new Set(prev)
        next.delete(address)
        return next
      })
    }
  }, [onUpdateData])

  // Fetch all addresses with delay to avoid rate limiting
  const fetchAllAddresses = useCallback(() => {
    watchList.forEach(({ address }, index) => {
      // Stagger requests by 1 second each to avoid rate limiting
      const delay = index * 1000
      setTimeout(() => fetchAddressData(address), delay)
    })
  }, [watchList, fetchAddressData])

  // Don't auto-fetch on mount - let user click refresh
  // This avoids hitting rate limits on page load

  // Add new address
  const handleAddAddress = () => {
    if (!newAddress.trim()) return

    // Basic validation
    if (!newAddress.match(/^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$/)) {
      setError('Invalid Bitcoin address format')
      return
    }

    onAddAddress(newAddress.trim(), newLabel.trim() || 'Custom Address')
    setNewAddress('')
    setNewLabel('')
    setShowAddForm(false)

    // Fetch data for new address
    setTimeout(() => fetchAddressData(newAddress.trim()), 100)
  }

  // Copy address to clipboard
  const copyAddress = async (address: string) => {
    await navigator.clipboard.writeText(address)
    setCopiedAddress(address)
    setTimeout(() => setCopiedAddress(null), 2000)
  }

  // Refresh single address
  const refreshAddress = (address: string) => {
    fetchAddressData(address)
  }

  // Refresh all addresses
  const refreshAll = () => {
    watchList.forEach(({ address }, index) => {
      setTimeout(() => fetchAddressData(address), index * 500)
    })
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">
          Strategic Address Watch List
        </h3>
        <div className="flex gap-2">
          <button
            onClick={refreshAll}
            disabled={loadingAddresses.size > 0}
            className="px-3 py-1.5 text-xs font-medium bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white/80 transition-colors disabled:opacity-50 flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3 h-3 ${loadingAddresses.size > 0 ? 'animate-spin' : ''}`} />
            Refresh All
          </button>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="px-3 py-1.5 text-xs font-medium bg-orange-500/20 hover:bg-orange-500/30 border border-orange-500/30 rounded-lg text-orange-400 transition-colors flex items-center gap-1.5"
          >
            <Plus className="w-3 h-3" />
            Add Address
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
          <button onClick={() => setError(null)} className="ml-auto text-red-400/60 hover:text-red-400">
            &times;
          </button>
        </div>
      )}

      {/* Add Address Form */}
      {showAddForm && (
        <div className="p-4 bg-white/5 border border-white/10 rounded-lg space-y-3">
          <input
            type="text"
            value={newAddress}
            onChange={(e) => setNewAddress(e.target.value)}
            placeholder="Bitcoin address (1xxx... or 3xxx...)"
            className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-lg text-white placeholder:text-white/40 text-sm font-mono focus:outline-none focus:border-orange-500/50"
          />
          <input
            type="text"
            value={newLabel}
            onChange={(e) => setNewLabel(e.target.value)}
            placeholder="Label (optional)"
            className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-lg text-white placeholder:text-white/40 text-sm focus:outline-none focus:border-orange-500/50"
          />
          <div className="flex gap-2">
            <button
              onClick={handleAddAddress}
              className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Add to Watch List
            </button>
            <button
              onClick={() => setShowAddForm(false)}
              className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white/60 text-sm font-medium rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Address List */}
      <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
        {/* Table Header */}
        <div className="grid grid-cols-12 gap-4 px-4 py-3 border-b border-white/10 text-xs font-medium text-white/60 uppercase tracking-wider">
          <div className="col-span-4">Address</div>
          <div className="col-span-2">Balance</div>
          <div className="col-span-2">Transactions</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-2 text-right">Actions</div>
        </div>

        {/* Address Rows */}
        <div className="divide-y divide-white/5">
          {watchList.map((watched) => {
            const data = addressData.get(watched.address)
            const isLoading = loadingAddresses.has(watched.address)
            const categoryStyle = CATEGORY_STYLES[watched.category] ?? CATEGORY_STYLES.custom!
            // categoryStyle is guaranteed to be defined due to fallback

            return (
              <div
                key={watched.address}
                className="grid grid-cols-12 gap-4 px-4 py-3 hover:bg-white/[0.02] transition-colors items-center"
              >
                {/* Address */}
                <div className="col-span-4">
                  <div className="flex items-center gap-2">
                    <span className={`px-1.5 py-0.5 text-[10px] font-medium rounded ${categoryStyle.bg} ${categoryStyle.text}`}>
                      {categoryStyle.label}
                    </span>
                    <div>
                      <div className="text-sm text-white font-mono">
                        {watched.address.slice(0, 8)}...{watched.address.slice(-6)}
                      </div>
                      <div className="text-xs text-white/40">{watched.label}</div>
                    </div>
                  </div>
                </div>

                {/* Balance */}
                <div className="col-span-2">
                  {isLoading ? (
                    <div className="h-5 w-20 bg-white/10 animate-pulse rounded" />
                  ) : data ? (
                    <span className={`text-sm font-mono ${data.balance > 0 ? 'text-green-400' : 'text-white/60'}`}>
                      {data.balance.toFixed(4)} BTC
                    </span>
                  ) : (
                    <span className="text-sm text-white/40">—</span>
                  )}
                </div>

                {/* Transactions */}
                <div className="col-span-2">
                  {isLoading ? (
                    <div className="h-5 w-12 bg-white/10 animate-pulse rounded" />
                  ) : data ? (
                    <span className="text-sm font-mono text-white/80">
                      {data.txCount.toLocaleString()}
                    </span>
                  ) : (
                    <span className="text-sm text-white/40">—</span>
                  )}
                </div>

                {/* Status */}
                <div className="col-span-2">
                  {isLoading ? (
                    <StatusBadge status="loading" />
                  ) : data ? (
                    <StatusBadge status={data.status} />
                  ) : (
                    <span className="text-sm text-white/40">—</span>
                  )}
                </div>

                {/* Actions */}
                <div className="col-span-2 flex justify-end gap-1">
                  <button
                    onClick={() => copyAddress(watched.address)}
                    className="p-1.5 text-white/40 hover:text-white hover:bg-white/10 rounded transition-colors"
                    title="Copy address"
                  >
                    {copiedAddress === watched.address ? (
                      <Check className="w-3.5 h-3.5 text-green-400" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                  </button>
                  <button
                    onClick={() => refreshAddress(watched.address)}
                    disabled={isLoading}
                    className="p-1.5 text-white/40 hover:text-white hover:bg-white/10 rounded transition-colors disabled:opacity-50"
                    title="Refresh"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                  </button>
                  <a
                    href={`https://mempool.space/address/${watched.address}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1.5 text-white/40 hover:text-white hover:bg-white/10 rounded transition-colors"
                    title="View on Mempool.space"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                  {watched.category === 'custom' && (
                    <button
                      onClick={() => onRemoveAddress(watched.address)}
                      className="p-1.5 text-red-400/60 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                      title="Remove"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Info */}
      <p className="text-xs text-white/40 text-center">
        Data from Mempool.space API. Rate limited to prevent abuse.
      </p>
    </div>
  )
}

export default AddressWatchList
