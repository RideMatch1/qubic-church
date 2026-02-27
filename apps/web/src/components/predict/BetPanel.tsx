'use client'

import * as React from 'react'
import { Loader2, XCircle, CheckCircle2, Clock, AlertTriangle } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { Market, PlaceBetPayload, CreateEscrowResponse } from './types'
import { formatQu, getStoredAddress, setStoredAddress } from './helpers'
import { EscrowStatus } from './EscrowStatus'
import { BetLockWarning } from './BetLockWarning'

interface BetPanelProps {
  market: Market
  onBetPlaced?: () => void
}

type BetState = 'idle' | 'loading' | 'escrow_created' | 'error'

export function BetPanel({ market, onBetPlaced }: BetPanelProps) {
  const [option, setOption] = React.useState(0)
  const [slots, setSlots] = React.useState(1)
  const [payoutAddress, setPayoutAddress] = React.useState(() => getStoredAddress())
  const [state, setState] = React.useState<BetState>('idle')
  const [errorMsg, setErrorMsg] = React.useState('')
  const [escrowData, setEscrowData] = React.useState<CreateEscrowResponse | null>(null)
  const [showLockWarning, setShowLockWarning] = React.useState(false)

  const options = market.options ?? ['Yes', 'No']
  const numOptions = market.numOptions ?? options.length
  const slotsPerOption = market.slotsPerOption ?? {}
  const oracleFeeBps = market.oracleFeeBps ?? 0

  const cost = slots * market.minBetQu
  const isActive = market.status === 'active'

  // Estimate potential payout — fees apply to LOSER pool only (matches Quottery SC)
  const currentWinnerSlots = slotsPerOption[String(option)] ?? (option === 0 ? market.yesSlots : market.noSlots)
  const futureWinnerSlots = currentWinnerSlots + slots
  const totalFutureSlots = Object.values(slotsPerOption).reduce((a, b) => a + b, 0) + slots
  const futurePool = market.totalPool + cost

  // Decompose: winner stake is the portion of the pool from the winning side
  const winnerStake = totalFutureSlots > 0
    ? (futurePool * futureWinnerSlots) / totalFutureSlots
    : 0
  const loserPool = futurePool - winnerStake
  // Fees are deducted from loser pool only: 2% burn + 10% shareholders + 0.5% operator + oracle
  const scFeeRate = 0.125 + oracleFeeBps / 10_000
  const totalFees = loserPool * scFeeRate
  const winnerPool = winnerStake + loserPool - totalFees
  const payoutPerSlot = futureWinnerSlots > 0 ? winnerPool / futureWinnerSlots : 0
  const potentialPayout = Math.floor(payoutPerSlot * slots)

  const addressValid =
    payoutAddress.length === 60 && /^[A-Z]+$/.test(payoutAddress)

  async function handlePlaceBet() {
    if (!addressValid) {
      setErrorMsg('Enter a valid 60-character uppercase Qubic address.')
      setState('error')
      return
    }

    setState('loading')
    setErrorMsg('')

    try {
      const payload: PlaceBetPayload = {
        marketId: market.id,
        payoutAddress,
        option,
        slots,
      }

      const res = await fetch('/api/predict/bet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()

      if (!res.ok) {
        setErrorMsg(data.error ?? 'Failed to create bet')
        setState('error')
        return
      }

      setStoredAddress(payoutAddress)
      setEscrowData(data as CreateEscrowResponse)
      setState('escrow_created')
      onBetPlaced?.()
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Network error')
      setState('error')
    }
  }

  function handleSlotsChange(e: React.ChangeEvent<HTMLInputElement>) {
    const val = parseInt(e.target.value, 10)
    if (isNaN(val) || val < 1) {
      setSlots(1)
    } else if (val > market.maxSlots) {
      setSlots(market.maxSlots)
    } else {
      setSlots(val)
    }
  }

  function handleReset() {
    setState('idle')
    setSlots(1)
    setEscrowData(null)
    setErrorMsg('')
    onBetPlaced?.() // Force market data reload
  }

  // Market resolved — show result instead of bet form
  if (market.status === 'resolved') {
    return (
      <div className="rounded-lg border bg-card p-6">
        <div className="text-center py-4">
          <CheckCircle2 className="h-8 w-8 mx-auto mb-2 text-emerald-400" />
          <h3 className="font-semibold text-foreground">Market Resolved</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Winner: {options[market.winningOption ?? 0]}
          </p>
        </div>
      </div>
    )
  }

  // Market closed / resolving — no more bets
  if (market.status === 'closed' || market.status === 'resolving') {
    return (
      <div className="rounded-lg border bg-card p-6">
        <div className="text-center py-4">
          <Clock className="h-8 w-8 mx-auto mb-2 text-amber-400" />
          <h3 className="font-semibold text-foreground">Betting Closed</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Awaiting resolution...
          </p>
        </div>
      </div>
    )
  }

  // Show EscrowStatus tracker once escrow is created
  if (state === 'escrow_created' && escrowData) {
    return (
      <EscrowStatus
        escrowId={escrowData.escrowId}
        betId={escrowData.betId}
        escrowAddress={escrowData.escrowAddress}
        expectedAmountQu={escrowData.expectedAmountQu}
        expiresAt={escrowData.expiresAt}
        option={option}
        optionLabel={options[option]}
        slots={slots}
        onReset={handleReset}
      />
    )
  }

  return (
    <div className="rounded-lg border bg-card p-6">
      <h3 className="mb-4 text-base font-semibold text-foreground">
        Place Your Bet
      </h3>

      {/* Option Selector (2-8 options) */}
      <div className={cn(
        'mb-4 grid gap-2',
        numOptions <= 2 ? 'grid-cols-2' : numOptions <= 4 ? 'grid-cols-2' : 'grid-cols-3',
      )}>
        {options.map((label, i) => {
          const isSelected = option === i
          const optSlots = slotsPerOption[String(i)] ?? 0
          const totalSlots = Object.values(slotsPerOption).reduce((a, b) => a + b, 0) || 1
          const pct = totalSlots > 0 ? Math.round((optSlots / totalSlots) * 100) : 0

          return (
            <button
              key={i}
              type="button"
              onClick={() => setOption(i)}
              className={cn(
                'relative rounded-md border px-3 py-3 text-sm font-semibold transition-all',
                isSelected
                  ? i === 0
                    ? 'border-emerald-500 bg-emerald-500/15 text-emerald-400'
                    : 'border-blue-500 bg-blue-500/15 text-blue-400'
                  : 'border-muted bg-muted/30 text-muted-foreground hover:border-blue-500/40 hover:text-blue-400',
              )}
            >
              <span className="block truncate">{label}</span>
              {optSlots > 0 && (
                <span className="mt-0.5 block text-[10px] font-normal opacity-70">
                  {pct}% ({optSlots} slots)
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Slots Input */}
      <div className="mb-4">
        <label className="mb-1.5 block text-xs font-medium text-muted-foreground">
          Number of Slots (1-{market.maxSlots})
        </label>
        <Input
          type="number"
          min={1}
          max={market.maxSlots}
          value={slots}
          onChange={handleSlotsChange}
        />
      </div>

      {/* Payout Address Input */}
      <div className="mb-4">
        <label className="mb-1.5 block text-xs font-medium text-muted-foreground">
          Your Payout Address (60 uppercase letters)
        </label>
        <Input
          type="text"
          placeholder="ABCDEFGHIJ..."
          maxLength={60}
          value={payoutAddress}
          onChange={(e) => setPayoutAddress(e.target.value.toUpperCase())}
          className="font-mono text-xs"
        />
        {payoutAddress.length > 0 && !addressValid && (
          <p className="mt-1 text-xs text-red-400">
            Address must be exactly 60 uppercase letters.
          </p>
        )}
        <p className="mt-1 text-[10px] text-muted-foreground">
          Winnings will be sent to this address automatically.
        </p>
      </div>

      {/* Cost Preview */}
      <div className="mb-4 space-y-2 rounded-md border bg-muted/30 p-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Deposit Required</span>
          <span className="font-medium text-foreground">
            {formatQu(cost)} QU
            <span className="ml-1 text-xs text-muted-foreground">
              ({slots} slot{slots > 1 ? 's' : ''} x {formatQu(market.minBetQu)}{' '}
              QU)
            </span>
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Potential Payout</span>
          <span
            className={cn(
              'font-semibold',
              option === 0 ? 'text-emerald-400' : 'text-red-400',
            )}
          >
            ~{formatQu(potentialPayout)} QU
          </span>
        </div>
        {potentialPayout > cost * 1.01 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Multiplier</span>
            <span className="font-medium text-foreground">
              {cost > 0 ? (potentialPayout / cost).toFixed(2) : '0.00'}x
            </span>
          </div>
        )}
        {(() => {
          const totalOpposingSlots = Object.entries(slotsPerOption)
            .filter(([key]) => key !== String(option))
            .reduce((sum, [, count]) => sum + count, 0)
          return totalOpposingSlots === 0 && market.totalPool > 0 ? (
            <p className="text-xs text-amber-400 flex items-center gap-1 mt-1">
              <AlertTriangle className="h-3 w-3 shrink-0" />
              No opposing bets yet. If you win, you get your deposit back (fees only apply to the losing side).
            </p>
          ) : null
        })()}
      </div>

      {/* Error */}
      {state === 'error' && errorMsg && (
        <div className="mb-4 flex items-start gap-2 rounded-md border border-red-500/30 bg-red-500/10 p-3">
          <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
          <p className="text-xs text-red-400">{errorMsg}</p>
        </div>
      )}

      {/* Submit */}
      <Button
        className="w-full"
        disabled={!isActive || state === 'loading' || !addressValid}
        onClick={() => setShowLockWarning(true)}
      >
        {state === 'loading' ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Creating Escrow...
          </>
        ) : !isActive ? (
          'Market Closed'
        ) : (
          'Get Deposit Address'
        )}
      </Button>

      {!isActive && (
        <p className="mt-2 text-center text-xs text-muted-foreground">
          This market is no longer accepting bets.
        </p>
      )}

      {/* Bet Lock Warning Modal */}
      <BetLockWarning
        open={showLockWarning}
        onConfirm={() => {
          setShowLockWarning(false)
          handlePlaceBet()
        }}
        onCancel={() => setShowLockWarning(false)}
        option={options[option] ?? `Option ${option}`}
        slots={slots}
        amountQu={cost}
      />
    </div>
  )
}
