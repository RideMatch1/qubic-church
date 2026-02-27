'use client'

import { useState, useEffect, useCallback } from 'react'
import { Loader2, Send, RefreshCw, AlertCircle, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface AccountStatus {
  identity: string
  balance: number
  incomingTx: number
  outgoingTx: number
  lastInTick: number
  lastOutTick: number
  currentTick: number
  epoch: number
  cooldownRemaining: number
}

interface TxResult {
  success: boolean
  from: string
  to: string
  amount: number
  targetTick: number
  timestamp: string
  error?: string
}

export function TransactionPanel() {
  const [status, setStatus] = useState<AccountStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [destination, setDestination] = useState('')
  const [amount, setAmount] = useState('')
  const [result, setResult] = useState<TxResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [cooldown, setCooldown] = useState(0)

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch('/api/oracle')
      if (!res.ok) {
        const data = await res.json()
        setError(data.error || 'Failed to fetch status')
        return
      }
      const data = await res.json()
      setStatus(data)
      setCooldown(Math.ceil(data.cooldownRemaining / 1000))
      setError(null)
    } catch {
      setError('Network error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 15_000)
    return () => clearInterval(interval)
  }, [fetchStatus])

  // Cooldown timer
  useEffect(() => {
    if (cooldown <= 0) return
    const timer = setInterval(() => {
      setCooldown((prev) => Math.max(0, prev - 1))
    }, 1000)
    return () => clearInterval(timer)
  }, [cooldown])

  const sendTransaction = async () => {
    if (!destination || !amount) return
    const amountNum = parseInt(amount, 10)
    if (isNaN(amountNum) || amountNum < 1) {
      setError('Amount must be at least 1 QU')
      return
    }

    setSending(true)
    setResult(null)
    setError(null)

    try {
      const res = await fetch('/api/oracle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          destination: destination.trim().toUpperCase(),
          amount: amountNum,
        }),
      })
      const data = await res.json()

      if (!res.ok) {
        setError(data.error || 'Transaction failed')
      } else {
        setResult(data)
        setCooldown(30)
        // Refresh status after 3 seconds
        setTimeout(fetchStatus, 3000)
      }
    } catch {
      setError('Network error sending transaction')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Send className="w-4 h-4 text-cyan-400" />
          <span className="text-sm font-medium text-zinc-200">Send QUBIC</span>
        </div>
        <button
          onClick={fetchStatus}
          className="p-1 hover:bg-zinc-800 rounded transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-zinc-500 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Master Account Info */}
      {status && (
        <div className="mb-4 p-3 bg-zinc-800/50 rounded-lg space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-zinc-600">Master Account</span>
            <span className="text-[10px] font-mono text-zinc-500">
              {status.identity.slice(0, 10)}...{status.identity.slice(-6)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-zinc-500">Balance</span>
            <span className="text-sm font-mono font-semibold text-zinc-200">
              {status.balance.toLocaleString()} QU
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-zinc-600">TX Count</span>
            <span className="text-[10px] font-mono text-zinc-500">
              {status.incomingTx} in / {status.outgoingTx} out
            </span>
          </div>
        </div>
      )}

      {loading && !status && (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="w-4 h-4 animate-spin text-zinc-600" />
        </div>
      )}

      {/* Send Form */}
      <div className="space-y-3">
        <div>
          <label className="text-[10px] text-zinc-600 block mb-1">Destination Address</label>
          <Input
            placeholder="ABCDEF...XYZ (60 chars)"
            value={destination}
            onChange={(e) => setDestination(e.target.value.toUpperCase())}
            className="bg-zinc-800 border-zinc-700 text-zinc-200 text-xs font-mono"
            maxLength={60}
          />
        </div>

        <div>
          <label className="text-[10px] text-zinc-600 block mb-1">Amount (QU)</label>
          <Input
            type="number"
            placeholder="10"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="bg-zinc-800 border-zinc-700 text-zinc-200 text-sm font-mono"
            min={1}
            max={10000}
          />
          <span className="text-[10px] text-zinc-600 mt-0.5 block">Max 10,000 QU per TX (safety limit)</span>
        </div>

        <Button
          onClick={sendTransaction}
          disabled={sending || cooldown > 0 || !destination || !amount || !status}
          className="w-full bg-cyan-600 hover:bg-cyan-500 text-white disabled:opacity-50"
          size="sm"
        >
          {sending ? (
            <><Loader2 className="w-3.5 h-3.5 animate-spin mr-2" /> Sending...</>
          ) : cooldown > 0 ? (
            <>Cooldown ({cooldown}s)</>
          ) : (
            <><Send className="w-3.5 h-3.5 mr-2" /> Send Transaction</>
          )}
        </Button>
      </div>

      {/* Result */}
      {result && (
        <div className="mt-3 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
          <div className="flex items-center gap-1.5 mb-2">
            <Check className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-xs font-medium text-emerald-400">Transaction Broadcast</span>
          </div>
          <div className="space-y-1 text-[10px] text-zinc-400 font-mono">
            <div>To: {result.to.slice(0, 15)}...{result.to.slice(-8)}</div>
            <div>Amount: {result.amount} QU</div>
            <div>Target Tick: {result.targetTick.toLocaleString()}</div>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
          <div className="flex items-center gap-1.5">
            <AlertCircle className="w-3.5 h-3.5 text-red-400" />
            <span className="text-xs text-red-400">{error}</span>
          </div>
        </div>
      )}
    </div>
  )
}
