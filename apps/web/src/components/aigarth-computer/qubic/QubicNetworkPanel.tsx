'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Wallet,
  RefreshCw,
  Activity,
  Clock,
  Server,
  AlertCircle,
  CheckCircle2,
  Loader2,
  ExternalLink,
  Copy,
  Check,
} from 'lucide-react'
import { useQubicNetwork } from '../hooks/useQubicNetwork'

// Default sender address for monitoring (from environment or hardcoded for demo)
const DEFAULT_SENDER_ID = process.env.NEXT_PUBLIC_QUBIC_SENDER_ID || ''

export function QubicNetworkPanel() {
  const {
    isConnected,
    isLoading,
    error,
    epoch,
    networkStatus,
    balance,
    lastUpdate,
    refresh,
    fetchBalance
  } = useQubicNetwork(DEFAULT_SENDER_ID)

  const [customAddress, setCustomAddress] = useState('')
  const [customBalance, setCustomBalance] = useState<bigint | null>(null)
  const [isLoadingCustom, setIsLoadingCustom] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleCheckBalance = async () => {
    if (!customAddress.trim() || customAddress.length !== 60) return
    setIsLoadingCustom(true)
    try {
      const bal = await fetchBalance(customAddress)
      setCustomBalance(bal)
    } catch {
      setCustomBalance(null)
    } finally {
      setIsLoadingCustom(false)
    }
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const formatBalance = (bal: bigint): string => {
    const num = Number(bal)
    if (num >= 1_000_000) {
      return `${(num / 1_000_000).toFixed(2)}M`
    }
    if (num >= 1_000) {
      return `${(num / 1_000).toFixed(1)}K`
    }
    return num.toLocaleString()
  }

  const formatTimestamp = (ts: number): string => {
    const date = new Date(ts)
    return date.toLocaleTimeString()
  }

  return (
    <div className="space-y-6">
      {/* Connection Status Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${
            isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
          }`} />
          <span className="font-semibold text-white">
            {isConnected ? 'Connected to Qubic Network' : 'Disconnected'}
          </span>
          {isLoading && <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={refresh}
          disabled={isLoading}
          className="border-gray-700 hover:bg-gray-800"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400" />
          <span className="text-sm text-red-400">{error}</span>
        </div>
      )}

      {/* Network Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Current Tick */}
        <Card className="bg-gray-800/30 border-gray-700/50 p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
            <Activity className="w-4 h-4" />
            <span>Current Tick</span>
          </div>
          <div className="text-2xl font-bold text-cyan-400 font-mono">
            {networkStatus?.tick !== undefined ? networkStatus.tick.toLocaleString() : '—'}
          </div>
        </Card>

        {/* Current Epoch */}
        <Card className="bg-gray-800/30 border-gray-700/50 p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
            <Clock className="w-4 h-4" />
            <span>Epoch</span>
          </div>
          <div className="text-2xl font-bold text-purple-400 font-mono">
            {epoch?.epoch !== undefined && !Number.isNaN(epoch.epoch) ? epoch.epoch : '—'}
          </div>
        </Card>

        {/* Network Health */}
        <Card className="bg-gray-800/30 border-gray-700/50 p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
            <Server className="w-4 h-4" />
            <span>Network Health</span>
          </div>
          <Badge
            variant="outline"
            className={`text-sm ${
              networkStatus?.health === 'excellent' ? 'text-green-400 border-green-400/50' :
              networkStatus?.health === 'good' ? 'text-cyan-400 border-cyan-400/50' :
              networkStatus?.health === 'fair' ? 'text-yellow-400 border-yellow-400/50' :
              'text-red-400 border-red-400/50'
            }`}
          >
            {networkStatus?.health?.toUpperCase() ?? '—'}
          </Badge>
        </Card>

        {/* Last Update */}
        <Card className="bg-gray-800/30 border-gray-700/50 p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>Last Update</span>
          </div>
          <div className="text-lg font-semibold text-gray-300">
            {lastUpdate ? formatTimestamp(lastUpdate) : '—'}
          </div>
        </Card>
      </div>

      {/* Wallet Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configured Wallet */}
        {DEFAULT_SENDER_ID && (
          <Card className="bg-gray-800/30 border-gray-700/50 p-4">
            <div className="flex items-center gap-2 mb-4">
              <Wallet className="w-5 h-5 text-orange-400" />
              <h4 className="font-semibold text-white">Configured Wallet</h4>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs text-gray-500 uppercase tracking-wide">Address</label>
                <div className="flex items-center gap-2 mt-1">
                  <code className="flex-1 text-xs text-cyan-400 bg-gray-900/50 p-2 rounded overflow-x-auto">
                    {DEFAULT_SENDER_ID.slice(0, 20)}...{DEFAULT_SENDER_ID.slice(-10)}
                  </code>
                  <button
                    onClick={() => handleCopy(DEFAULT_SENDER_ID)}
                    className="p-1 hover:bg-gray-700/50 rounded"
                  >
                    {copied ? (
                      <Check className="w-4 h-4 text-green-400" />
                    ) : (
                      <Copy className="w-4 h-4 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <label className="text-xs text-gray-500 uppercase tracking-wide">Balance</label>
                <div className="text-2xl font-bold text-green-400 font-mono">
                  {balance !== null ? (
                    <>
                      {formatBalance(balance)} <span className="text-sm text-gray-500">QUBIC</span>
                    </>
                  ) : '—'}
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Check Any Address */}
        <Card className="bg-gray-800/30 border-gray-700/50 p-4">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-cyan-400" />
            <h4 className="font-semibold text-white">Check Any Address</h4>
          </div>

          <div className="space-y-3">
            <div>
              <label className="text-xs text-gray-500 uppercase tracking-wide mb-1 block">
                Qubic Address (60 characters)
              </label>
              <input
                type="text"
                value={customAddress}
                onChange={(e) => setCustomAddress(e.target.value.toUpperCase())}
                placeholder="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                className="w-full bg-gray-900/50 border border-gray-700 rounded px-3 py-2 text-xs font-mono text-white placeholder-gray-600 focus:border-cyan-500 focus:outline-none"
                maxLength={60}
              />
            </div>

            <Button
              onClick={handleCheckBalance}
              disabled={isLoadingCustom || customAddress.length !== 60}
              className="w-full bg-cyan-600 hover:bg-cyan-500"
            >
              {isLoadingCustom ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Activity className="w-4 h-4 mr-2" />
              )}
              Check Balance
            </Button>

            {customBalance !== null && (
              <div className="p-3 bg-gray-900/50 rounded-lg">
                <span className="text-sm text-gray-400">Balance: </span>
                <span className="text-lg font-bold text-green-400 font-mono">
                  {formatBalance(customBalance)} QUBIC
                </span>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Network Info Footer */}
      <Card className="bg-gray-800/30 border-gray-700/50 p-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-400">
            <span className="font-semibold text-white">Qubic Network</span> — Decentralized AI Computation
          </div>
          <a
            href="https://qubic.org"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-sm text-cyan-400 hover:text-cyan-300"
          >
            <span>qubic.org</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </Card>
    </div>
  )
}
