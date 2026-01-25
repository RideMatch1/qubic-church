/**
 * BATCH VERIFICATION - Component
 *
 * Batch-verify addresses against the Bitcoin blockchain.
 * Supports Matrix, Patoshi, and custom address lists.
 */

'use client'

import { useState, useCallback, useRef } from 'react'
import {
  Play,
  Pause,
  Square,
  Download,
  Search,
  AlertCircle,
  CheckCircle,
  Activity,
  Bitcoin,
} from 'lucide-react'

// =============================================================================
// TYPES
// =============================================================================

interface VerificationResult {
  address: string
  status: 'active' | 'spent' | 'unused' | 'error'
  balance: number
  txCount: number
}

interface BatchStats {
  total: number
  verified: number
  active: number
  withBalance: number
  spent: number
  unused: number
  errors: number
}

type DatasetType = 'matrix' | 'patoshi' | 'derived' | 'custom'

// =============================================================================
// DATASET OPTIONS
// =============================================================================

const DATASETS: { id: DatasetType; label: string; description: string; count: string }[] = [
  { id: 'matrix', label: 'Matrix Addresses', description: 'From Anna Matrix derivation', count: '983,040' },
  { id: 'patoshi', label: 'Patoshi Addresses', description: 'Genesis-era mining addresses', count: '21,953' },
  { id: 'derived', label: 'Derived Addresses', description: 'Bitcoin key derivations', count: '20,955' },
  { id: 'custom', label: 'Custom List', description: 'Paste your own addresses', count: 'Variable' },
]

// =============================================================================
// BATCH VERIFICATION COMPONENT
// =============================================================================

export function BatchVerification() {
  // State
  const [dataset, setDataset] = useState<DatasetType>('patoshi')
  const [sampleSize, setSampleSize] = useState(100)
  const [isRunning, setIsRunning] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [results, setResults] = useState<VerificationResult[]>([])
  const [stats, setStats] = useState<BatchStats>({
    total: 0,
    verified: 0,
    active: 0,
    withBalance: 0,
    spent: 0,
    unused: 0,
    errors: 0,
  })
  const [customAddresses, setCustomAddresses] = useState('')
  const [error, setError] = useState<string | null>(null)

  // Refs for controlling the batch process
  const abortRef = useRef(false)
  const pauseRef = useRef(false)

  // Load addresses from dataset
  const loadAddresses = useCallback(async (): Promise<string[]> => {
    if (dataset === 'custom') {
      return customAddresses
        .split('\n')
        .map(a => a.trim())
        .filter(a => a.length > 0)
    }

    try {
      // Load from public data files
      const fileMap: Record<DatasetType, string> = {
        matrix: '/data/matrix-addresses.json',
        patoshi: '/data/patoshi-addresses.json',
        derived: '/data/bitcoin-derived-addresses.json',
        custom: '',
      }

      const response = await fetch(fileMap[dataset])
      if (!response.ok) throw new Error('Failed to load dataset')

      const data = await response.json()

      // Extract addresses based on dataset structure
      let addresses: string[] = []
      if (dataset === 'patoshi') {
        // Patoshi data needs address derivation from pubkey
        // For now, return empty - would need proper implementation
        addresses = data.slice(0, sampleSize).map((item: { address?: string }) => item.address).filter(Boolean)
      } else if (dataset === 'matrix') {
        addresses = data.slice(0, sampleSize).map((item: { address: string }) => item.address)
      } else if (dataset === 'derived') {
        addresses = data.slice(0, sampleSize).map((item: { address: string }) => item.address)
      }

      return addresses.slice(0, sampleSize)
    } catch (err) {
      console.error('Error loading addresses:', err)
      setError('Failed to load dataset. Using demo data.')

      // Return demo addresses for testing
      return [
        '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
        '12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX',
        '1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1',
      ]
    }
  }, [dataset, sampleSize, customAddresses])

  // Verify single address
  const verifyAddress = async (address: string): Promise<VerificationResult> => {
    try {
      const response = await fetch(`https://mempool.space/api/address/${address}`)

      if (!response.ok) {
        return { address, status: 'error', balance: 0, txCount: 0 }
      }

      const data = await response.json()
      const balance = (data.chain_stats.funded_txo_sum - data.chain_stats.spent_txo_sum) / 100000000
      const txCount = data.chain_stats.tx_count

      let status: VerificationResult['status'] = 'unused'
      if (txCount === 0) {
        status = 'unused'
      } else if (balance > 0) {
        status = 'active'
      } else {
        status = 'spent'
      }

      return { address, status, balance, txCount }
    } catch {
      return { address, status: 'error', balance: 0, txCount: 0 }
    }
  }

  // Run batch verification
  const startVerification = async () => {
    setIsRunning(true)
    setIsPaused(false)
    abortRef.current = false
    pauseRef.current = false
    setError(null)
    setResults([])
    setStats({
      total: 0,
      verified: 0,
      active: 0,
      withBalance: 0,
      spent: 0,
      unused: 0,
      errors: 0,
    })

    const addresses = await loadAddresses()
    if (addresses.length === 0) {
      setError('No addresses to verify')
      setIsRunning(false)
      return
    }

    setStats(prev => ({ ...prev, total: addresses.length }))

    // Process addresses with rate limiting
    for (let i = 0; i < addresses.length; i++) {
      if (abortRef.current) break

      // Wait while paused
      while (pauseRef.current && !abortRef.current) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }

      if (abortRef.current) break

      const address = addresses[i]
      if (!address) continue

      const result = await verifyAddress(address)

      setResults(prev => [...prev, result])
      setStats(prev => ({
        ...prev,
        verified: prev.verified + 1,
        active: prev.active + (result.status === 'active' ? 1 : 0),
        withBalance: prev.withBalance + (result.balance > 0 ? 1 : 0),
        spent: prev.spent + (result.status === 'spent' ? 1 : 0),
        unused: prev.unused + (result.status === 'unused' ? 1 : 0),
        errors: prev.errors + (result.status === 'error' ? 1 : 0),
      }))

      // Rate limiting: 1 request per second
      await new Promise(resolve => setTimeout(resolve, 1000))
    }

    setIsRunning(false)
    setIsPaused(false)
  }

  // Control functions
  const pauseVerification = () => {
    pauseRef.current = true
    setIsPaused(true)
  }

  const resumeVerification = () => {
    pauseRef.current = false
    setIsPaused(false)
  }

  const stopVerification = () => {
    abortRef.current = true
    setIsRunning(false)
    setIsPaused(false)
  }

  // Export results
  const exportResults = () => {
    const csv = [
      'Address,Status,Balance,Transactions',
      ...results.map(r => `${r.address},${r.status},${r.balance},${r.txCount}`),
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `batch-verification-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const progress = stats.total > 0 ? (stats.verified / stats.total) * 100 : 0

  return (
    <div className="space-y-6">
      {/* Configuration */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-4 space-y-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Search className="w-5 h-5 text-blue-400" />
          Batch Configuration
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Dataset Selection */}
          <div>
            <label className="block text-sm text-white/60 mb-2">Dataset</label>
            <select
              value={dataset}
              onChange={(e) => setDataset(e.target.value as DatasetType)}
              disabled={isRunning}
              className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500/50 disabled:opacity-50"
            >
              {DATASETS.map(d => (
                <option key={d.id} value={d.id}>
                  {d.label} ({d.count})
                </option>
              ))}
            </select>
          </div>

          {/* Sample Size */}
          <div>
            <label className="block text-sm text-white/60 mb-2">Sample Size</label>
            <input
              type="number"
              value={sampleSize}
              onChange={(e) => setSampleSize(Math.max(1, Math.min(1000, parseInt(e.target.value) || 100)))}
              disabled={isRunning}
              min={1}
              max={1000}
              className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-lg text-white text-sm font-mono focus:outline-none focus:border-blue-500/50 disabled:opacity-50"
            />
            <p className="text-xs text-white/40 mt-1">Max 1000 (rate limited)</p>
          </div>
        </div>

        {/* Custom Addresses */}
        {dataset === 'custom' && (
          <div>
            <label className="block text-sm text-white/60 mb-2">Custom Addresses (one per line)</label>
            <textarea
              value={customAddresses}
              onChange={(e) => setCustomAddresses(e.target.value)}
              disabled={isRunning}
              rows={4}
              className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-lg text-white text-sm font-mono focus:outline-none focus:border-blue-500/50 disabled:opacity-50"
              placeholder="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa&#10;12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"
            />
          </div>
        )}

        {/* Controls */}
        <div className="flex gap-2">
          {!isRunning ? (
            <button
              onClick={startVerification}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              Start Verification
            </button>
          ) : (
            <>
              {isPaused ? (
                <button
                  onClick={resumeVerification}
                  className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  Resume
                </button>
              ) : (
                <button
                  onClick={pauseVerification}
                  className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
                >
                  <Pause className="w-4 h-4" />
                  Pause
                </button>
              )}
              <button
                onClick={stopVerification}
                className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
              >
                <Square className="w-4 h-4" />
                Stop
              </button>
            </>
          )}
          {results.length > 0 && (
            <button
              onClick={exportResults}
              className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Progress */}
      {stats.total > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-4 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-white/60">Progress</span>
            <span className="text-sm font-mono text-white">
              {stats.verified} / {stats.total} ({progress.toFixed(1)}%)
            </span>
          </div>
          <div className="h-2 bg-black/50 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">{stats.active}</div>
              <div className="text-xs text-white/40">Active</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-400">{stats.withBalance}</div>
              <div className="text-xs text-white/40">With Balance</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-zinc-400">{stats.spent}</div>
              <div className="text-xs text-white/40">Spent</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white/40">{stats.unused}</div>
              <div className="text-xs text-white/40">Unused</div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Results */}
      {results.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-white/10">
            <h4 className="text-sm font-semibold text-white">Recent Results</h4>
          </div>
          <div className="max-h-64 overflow-y-auto">
            {results.slice(-20).reverse().map((result, i) => (
              <div
                key={`${result.address}-${i}`}
                className="px-4 py-2 border-b border-white/5 flex items-center justify-between text-sm"
              >
                <span className="font-mono text-white/80">
                  {result.address.slice(0, 12)}...{result.address.slice(-6)}
                </span>
                <div className="flex items-center gap-4">
                  {result.balance > 0 && (
                    <span className="text-green-400 font-mono">
                      {result.balance.toFixed(4)} BTC
                    </span>
                  )}
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    result.status === 'active' ? 'bg-green-500/20 text-green-400' :
                    result.status === 'spent' ? 'bg-zinc-500/20 text-zinc-400' :
                    result.status === 'error' ? 'bg-red-500/20 text-red-400' :
                    'bg-white/10 text-white/40'
                  }`}>
                    {result.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info */}
      <p className="text-xs text-white/40 text-center">
        Using Mempool.space API with 1 req/sec rate limiting. Large datasets may take time.
      </p>
    </div>
  )
}

export default BatchVerification
