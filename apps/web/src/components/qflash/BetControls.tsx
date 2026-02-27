'use client'

import { useState } from 'react'
import { ArrowUp, ArrowDown, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { formatQu } from './helpers'

interface BetControlsProps {
  roundId: string
  roundStatus: string
  address: string
  balance: number
  onBetPlaced: () => void
}

const QUICK_AMOUNTS = [10_000, 50_000, 100_000, 500_000, 1_000_000]

export function BetControls({
  roundId,
  roundStatus,
  address,
  balance,
  onBetPlaced,
}: BetControlsProps) {
  const [amount, setAmount] = useState(10_000)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastResult, setLastResult] = useState<{ side: string; entryId: string } | null>(null)

  const canBet = roundStatus === 'open' && address && balance >= amount && amount >= 10_000

  const placeBet = async (side: 'up' | 'down') => {
    if (!canBet) return
    setLoading(true)
    setError(null)
    setLastResult(null)

    try {
      const res = await fetch('/api/qflash/bet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ roundId, side, amountQu: amount, address }),
      })

      const data = await res.json()
      if (!res.ok) {
        setError(data.error || 'Failed to place bet')
        return
      }

      setLastResult({ side, entryId: data.entryId })
      onBetPlaced()
    } catch {
      setError('Network error — try again')
    } finally {
      setLoading(false)
    }
  }

  const isDisabled = !canBet || loading

  return (
    <div className="space-y-4">
      {/* Amount Input */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-xs font-medium text-muted-foreground">
            Bet Amount
          </label>
          <span className="text-xs text-muted-foreground">
            Balance: <span className="font-mono font-medium text-foreground">{formatQu(balance)}</span> QU
          </span>
        </div>
        <div className="relative">
          <Input
            type="number"
            min={10000}
            max={Math.min(10_000_000, balance)}
            step={10000}
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
            className="pr-10 font-mono text-right"
          />
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
            QU
          </span>
        </div>
      </div>

      {/* Quick Amount Chips */}
      <div className="flex flex-wrap gap-1.5">
        {QUICK_AMOUNTS.filter((a) => a <= balance).map((a) => (
          <button
            key={a}
            type="button"
            onClick={() => setAmount(a)}
            className={cn(
              'rounded-full border px-2.5 py-0.5 text-[10px] font-mono font-medium transition-colors',
              amount === a
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-border text-muted-foreground hover:border-primary/40',
            )}
          >
            {a >= 1_000_000 ? `${a / 1_000_000}M` : `${a / 1_000}K`}
          </button>
        ))}
        {balance > 0 && (
          <button
            type="button"
            onClick={() => setAmount(Math.min(balance, 10_000_000))}
            className={cn(
              'rounded-full border px-2.5 py-0.5 text-[10px] font-medium transition-colors',
              amount === Math.min(balance, 10_000_000)
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-border text-muted-foreground hover:border-primary/40',
            )}
          >
            MAX
          </button>
        )}
      </div>

      {/* UP / DOWN Buttons */}
      <div className="grid grid-cols-2 gap-3">
        <Button
          size="lg"
          disabled={isDisabled}
          onClick={() => placeBet('up')}
          className={cn(
            'h-16 text-lg font-bold transition-all',
            'bg-emerald-600 hover:bg-emerald-500 text-white',
            'disabled:bg-emerald-600/30 disabled:text-white/40',
          )}
        >
          {loading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <>
              <ArrowUp className="mr-2 h-6 w-6" />
              UP
            </>
          )}
        </Button>
        <Button
          size="lg"
          disabled={isDisabled}
          onClick={() => placeBet('down')}
          className={cn(
            'h-16 text-lg font-bold transition-all',
            'bg-red-600 hover:bg-red-500 text-white',
            'disabled:bg-red-600/30 disabled:text-white/40',
          )}
        >
          {loading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <>
              <ArrowDown className="mr-2 h-6 w-6" />
              DOWN
            </>
          )}
        </Button>
      </div>

      {/* Status line */}
      {roundStatus !== 'open' && (
        <p className="text-center text-xs text-muted-foreground">
          {roundStatus === 'locked' ? 'Round locked — wait for next round' :
           roundStatus === 'upcoming' ? 'Round opening soon...' :
           roundStatus === 'resolving' ? 'Resolving...' :
           `Round is ${roundStatus}`}
        </p>
      )}

      {!address && (
        <p className="text-center text-xs text-amber-400">
          Enter your address to place bets
        </p>
      )}

      {address && balance < 10_000 && (
        <p className="text-center text-xs text-amber-400">
          Deposit QU to start betting
        </p>
      )}

      {/* Error / Success */}
      {error && (
        <p className="text-center text-xs text-red-400">{error}</p>
      )}
      {lastResult && (
        <p className="text-center text-xs text-emerald-400">
          Bet placed: {lastResult.side.toUpperCase()} for {formatQu(amount)} QU
        </p>
      )}
    </div>
  )
}
