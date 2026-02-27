'use client'

import * as React from 'react'
import {
  CheckCircle2,
  Circle,
  Clock,
  Copy,
  Loader2,
  PartyPopper,
  RefreshCw,
  XCircle,
} from 'lucide-react'
import { QRCodeSVG } from 'qrcode.react'

import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import type { EscrowInfo, EscrowStatus as EscrowStatusType } from './types'
import { formatQu, anonymizeAddress } from './helpers'

// ---------------------------------------------------------------------------
// Step definitions for the lifecycle
// ---------------------------------------------------------------------------

interface StepDef {
  key: EscrowStatusType
  label: string
}

const LIFECYCLE_STEPS: StepDef[] = [
  { key: 'awaiting_deposit', label: 'Deposit' },
  { key: 'deposit_detected', label: 'Detected' },
  { key: 'active_in_sc', label: 'Active' },
  { key: 'won_awaiting_sweep', label: 'Result' },
  { key: 'swept', label: 'Payout' },
]

/** Map statuses to the step index they correspond to (0-based) */
function statusToStepIndex(status: EscrowStatusType): number {
  switch (status) {
    case 'awaiting_deposit':
      return 0
    case 'deposit_detected':
      return 1
    case 'joining_sc':
      return 1 // same as detected (in-progress joining)
    case 'active_in_sc':
      return 2
    case 'won_awaiting_sweep':
      return 3
    case 'swept':
    case 'completed':
      return 4
    case 'lost':
      return 3 // result step, but lost
    case 'expired':
    case 'refunded':
    case 'failed':
      return -1 // terminal error states
    default:
      return 0
  }
}

const TERMINAL_STATES = new Set<EscrowStatusType>([
  'swept',
  'completed',
  'lost',
  'expired',
  'refunded',
  'failed',
])

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface EscrowStatusProps {
  /** Initial escrow data from the create response */
  escrowId: string
  betId: string
  escrowAddress: string
  expectedAmountQu: number
  expiresAt: string
  option: number
  optionLabel?: string
  slots: number
  /** Called when the user wants to place another bet */
  onReset?: () => void
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function EscrowStatus({
  escrowId,
  betId,
  escrowAddress,
  expectedAmountQu,
  expiresAt,
  option,
  optionLabel,
  slots,
  onReset,
}: EscrowStatusProps) {
  const [status, setStatus] = React.useState<EscrowStatusType>('awaiting_deposit')
  const [info, setInfo] = React.useState<EscrowInfo | null>(null)
  const [copied, setCopied] = React.useState(false)
  const [countdown, setCountdown] = React.useState('')
  const [refreshing, setRefreshing] = React.useState(false)
  const [lastChecked, setLastChecked] = React.useState<Date | null>(null)
  const [cancelling, setCancelling] = React.useState(false)
  const [cancelError, setCancelError] = React.useState('')
  const pollRef = React.useRef<ReturnType<typeof setInterval> | null>(null)
  const countdownRef = React.useRef<ReturnType<typeof setInterval> | null>(null)

  // Core polling function — checks blockchain when awaiting_deposit
  const fetchStatus = React.useCallback(async () => {
    try {
      const res = await fetch(`/api/predict/bet/status?id=${encodeURIComponent(betId)}`)
      if (!res.ok) return
      const data: EscrowInfo = await res.json()
      setStatus(data.status)
      setInfo(data)
      setLastChecked(new Date())

      // Stop polling on terminal states
      if (TERMINAL_STATES.has(data.status)) {
        if (pollRef.current) {
          clearInterval(pollRef.current)
          pollRef.current = null
        }
      }
    } catch {
      // silently retry on next interval
    }
  }, [betId])

  // Auto-poll every 5 seconds
  React.useEffect(() => {
    let active = true

    const wrappedPoll = () => {
      if (active) fetchStatus()
    }

    // Initial poll
    wrappedPoll()

    // Poll every 5 seconds
    pollRef.current = setInterval(wrappedPoll, 5000)

    return () => {
      active = false
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [fetchStatus])

  // Countdown timer
  React.useEffect(() => {
    function updateCountdown() {
      const remaining = new Date(expiresAt).getTime() - Date.now()
      if (remaining <= 0) {
        setCountdown('Expired')
        if (countdownRef.current) {
          clearInterval(countdownRef.current)
          countdownRef.current = null
        }
        return
      }
      const h = Math.floor(remaining / (1000 * 60 * 60))
      const m = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60))
      const s = Math.floor((remaining % (1000 * 60)) / 1000)
      setCountdown(`${h}h ${m}m ${s}s`)
    }

    updateCountdown()
    countdownRef.current = setInterval(updateCountdown, 1000)

    return () => {
      if (countdownRef.current) {
        clearInterval(countdownRef.current)
        countdownRef.current = null
      }
    }
  }, [expiresAt])

  async function copyAddress() {
    try {
      await navigator.clipboard.writeText(escrowAddress)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // fallback
    }
  }

  // Manual refresh — triggers an immediate blockchain check
  async function handleRefresh() {
    setRefreshing(true)
    await fetchStatus()
    setRefreshing(false)
  }

  // Cancel bet before deposit
  async function handleCancel() {
    setCancelling(true)
    setCancelError('')
    try {
      const res = await fetch('/api/predict/bet', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ escrowId }),
      })
      if (!res.ok) {
        const data = await res.json()
        setCancelError(data.error ?? 'Failed to cancel')
        return
      }
      setStatus('expired')
      // Stop polling
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    } catch {
      setCancelError('Network error — please try again')
    } finally {
      setCancelling(false)
    }
  }

  const stepIndex = statusToStepIndex(status)
  const isTerminalError = status === 'expired' || status === 'refunded' || status === 'failed'
  const isLost = status === 'lost'
  const isWon = status === 'won_awaiting_sweep' || status === 'swept' || status === 'completed'
  const isDone = TERMINAL_STATES.has(status)
  const showDepositSection = status === 'awaiting_deposit'

  return (
    <div className="rounded-lg border bg-card p-6">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-base font-semibold text-foreground">
          Bet Status
        </h3>
        <div className="flex items-center gap-2">
          {/* Manual Refresh Button */}
          {!isDone && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 gap-1 px-2 text-xs text-muted-foreground hover:text-foreground"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              <RefreshCw className={cn('h-3 w-3', refreshing && 'animate-spin')} />
              {refreshing ? 'Checking...' : 'Refresh'}
            </Button>
          )}
          <span
            className={cn(
              'rounded-full border px-2.5 py-0.5 text-xs font-medium',
              isTerminalError
                ? 'border-red-500/30 bg-red-500/10 text-red-400'
                : isLost
                  ? 'border-zinc-500/30 bg-zinc-500/10 text-zinc-400'
                  : isWon
                    ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                    : 'border-blue-500/30 bg-blue-500/10 text-blue-400',
            )}
          >
            {statusLabel(status)}
          </span>
        </div>
      </div>

      {/* Step Progress */}
      {!isTerminalError && (
        <div className="mb-6">
          <div className="flex items-center justify-between">
            {LIFECYCLE_STEPS.map((step, i) => {
              // For terminal success states (swept/completed), mark the final step as complete too
              const isComplete = stepIndex > i || (isWon && isDone && stepIndex === i)
              const isCurrent = stepIndex === i && !(isWon && isDone)
              const isLostAtResult = isLost && i === 3

              return (
                <React.Fragment key={step.key}>
                  {i > 0 && (
                    <div
                      className={cn(
                        'h-px flex-1',
                        isComplete
                          ? 'bg-emerald-500/50'
                          : 'bg-muted',
                      )}
                    />
                  )}
                  <div className="flex flex-col items-center gap-1">
                    {isComplete ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                    ) : isCurrent ? (
                      isLostAtResult ? (
                        <XCircle className="h-5 w-5 text-red-400" />
                      ) : (
                        <Loader2 className="h-5 w-5 animate-spin text-blue-400" />
                      )
                    ) : (
                      <Circle className="h-5 w-5 text-muted-foreground/30" />
                    )}
                    <span
                      className={cn(
                        'text-[10px] font-medium',
                        isComplete
                          ? 'text-emerald-400'
                          : isCurrent
                            ? isLostAtResult
                              ? 'text-red-400'
                              : 'text-blue-400'
                            : 'text-muted-foreground/40',
                      )}
                    >
                      {step.label}
                    </span>
                  </div>
                </React.Fragment>
              )
            })}
          </div>
        </div>
      )}

      {/* Deposit Instructions */}
      {showDepositSection && (
        <div className="mb-4 rounded-md border border-blue-500/20 bg-blue-500/5 p-4">
          <p className="mb-3 text-sm font-medium text-foreground">
            Send exactly {formatQu(expectedAmountQu)} QU to:
          </p>

          {/* QR Code */}
          <div className="mb-3 flex justify-center">
            <div className="rounded-lg bg-white p-3">
              <QRCodeSVG
                value={escrowAddress}
                size={160}
                level="M"
                bgColor="#ffffff"
                fgColor="#000000"
              />
            </div>
          </div>

          {/* Address + Copy */}
          <div className="mb-2 flex items-center gap-2">
            <code className="flex-1 break-all rounded bg-muted/50 px-3 py-2 font-mono text-xs text-foreground">
              {escrowAddress}
            </code>
            <Button
              variant="outline"
              size="sm"
              className="shrink-0"
              onClick={copyAddress}
            >
              {copied ? (
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              ) : (
                <Copy className="h-3.5 w-3.5" />
              )}
            </Button>
          </div>

          {/* Amount reminder */}
          <p className="mb-2 text-center text-xs text-blue-400/80">
            Exact amount: <strong>{formatQu(expectedAmountQu)} QU</strong>
          </p>

          <div className="flex items-center justify-center gap-1.5 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>
              Deposit within: <strong className="text-foreground">{countdown}</strong>
            </span>
          </div>

          {/* Auto-polling indicator */}
          <p className="mt-3 text-center text-[10px] text-muted-foreground/60">
            Auto-checking blockchain every 5s
            {lastChecked && (
              <> &middot; Last: {lastChecked.toLocaleTimeString()}</>
            )}
          </p>
        </div>
      )}

      {/* Deposit detected but not yet on SC */}
      {status === 'deposit_detected' && (
        <div className="mb-4 flex items-start gap-2 rounded-md border border-emerald-500/30 bg-emerald-500/10 p-3">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
          <p className="text-xs text-emerald-400">
            Deposit of {info?.depositAmountQu ? formatQu(info.depositAmountQu) : formatQu(expectedAmountQu)} QU detected! Processing your bet on-chain...
          </p>
        </div>
      )}

      {status === 'joining_sc' && (
        <div className="mb-4 flex items-start gap-2 rounded-md border border-blue-500/30 bg-blue-500/10 p-3">
          <Loader2 className="mt-0.5 h-4 w-4 shrink-0 animate-spin text-blue-400" />
          <p className="text-xs text-blue-400">
            Joining Quottery Smart Contract... This may take a few ticks.
          </p>
        </div>
      )}

      {/* Active in Smart Contract */}
      {status === 'active_in_sc' && (
        <div className="mb-4 flex items-start gap-2 rounded-md border border-green-500/30 bg-green-500/10 p-3">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-green-400" />
          <p className="text-xs text-green-400">
            Your bet is LIVE in the Quottery Smart Contract! Waiting for market resolution.
          </p>
        </div>
      )}

      {/* Won - Awaiting Sweep */}
      {status === 'won_awaiting_sweep' && (
        <div className="mb-4 flex items-start gap-2 rounded-md border border-emerald-500/30 bg-emerald-500/10 p-3">
          <Loader2 className="mt-0.5 h-4 w-4 shrink-0 animate-spin text-emerald-400" />
          <p className="text-xs text-emerald-400">
            You WON! Sweeping your payout now...
          </p>
        </div>
      )}

      {/* Info Grid */}
      <div className="space-y-2 rounded-md border bg-muted/30 p-3">
        <InfoRow
          label="Bet"
          value={`${optionLabel ?? (option === 0 ? 'YES' : 'NO')} - ${slots} slot${slots > 1 ? 's' : ''}`}
        />
        <InfoRow label="Amount" value={`${formatQu(expectedAmountQu)} QU`} />
        <InfoRow
          label="Escrow"
          value={anonymizeAddress(escrowAddress)}
          mono
        />
        {info?.depositAmountQu && (
          <InfoRow label="Deposited" value={`${formatQu(info.depositAmountQu)} QU`} />
        )}
        {info?.joinBetTxId && (
          <InfoRow
            label="SC TX"
            value={info.joinBetTxId.length > 16 ? `${info.joinBetTxId.slice(0, 16)}...` : info.joinBetTxId}
            mono
          />
        )}
        {info?.payoutAmountQu && (
          <InfoRow
            label="Payout"
            value={`${formatQu(info.payoutAmountQu)} QU`}
            className="text-emerald-400"
          />
        )}
        {info?.sweepTxId && (
          <InfoRow
            label="Sweep TX"
            value={info.sweepTxId.length > 16 ? `${info.sweepTxId.slice(0, 16)}...` : info.sweepTxId}
            mono
          />
        )}
      </div>

      {/* Terminal State Messages */}
      {isLost && (
        <div className="mt-4 flex items-start gap-2 rounded-md border border-zinc-500/30 bg-zinc-500/10 p-3">
          <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-zinc-400" />
          <p className="text-xs text-zinc-400">
            Your bet did not win. The market resolved to the other option.
          </p>
        </div>
      )}

      {(status === 'swept' || status === 'completed') && (
        <div className="mt-4 flex items-start gap-2 rounded-md border border-emerald-500/30 bg-emerald-500/10 p-3">
          <PartyPopper className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
          <div className="text-xs text-emerald-400">
            <p className="font-semibold">
              Congratulations! You won {info?.payoutAmountQu ? formatQu(info.payoutAmountQu) : '...'} QU!
            </p>
            <p className="mt-0.5 text-emerald-400/80">
              Your payout has been sent to your address. Thanks for playing on QPredict!
            </p>
          </div>
        </div>
      )}

      {status === 'expired' && (
        <div className="mt-4 flex items-start gap-2 rounded-md border border-red-500/30 bg-red-500/10 p-3">
          <Clock className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
          <p className="text-xs text-red-400">
            Deposit window expired. No funds were received.
          </p>
        </div>
      )}

      {/* Cancel Error */}
      {cancelError && (
        <div className="mt-3 rounded-md border border-red-500/30 bg-red-500/10 px-3 py-2">
          <p className="text-xs text-red-400">{cancelError}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-4 flex gap-2">
        {/* Cancel Button — only when awaiting deposit */}
        {showDepositSection && (
          <Button
            variant="outline"
            size="sm"
            className="flex-1 border-red-500/30 text-red-400 hover:bg-red-500/10 hover:text-red-300"
            onClick={handleCancel}
            disabled={cancelling}
          >
            {cancelling ? (
              <>
                <Loader2 className="mr-1.5 h-3 w-3 animate-spin" />
                Cancelling...
              </>
            ) : (
              <>
                <XCircle className="mr-1.5 h-3 w-3" />
                Cancel Bet
              </>
            )}
          </Button>
        )}
        {/* New Bet Button — always available when awaiting or done */}
        {(isDone || showDepositSection) && onReset && (
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={onReset}
          >
            {isDone ? 'Place Another Bet' : 'New Bet'}
          </Button>
        )}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function statusLabel(status: EscrowStatusType): string {
  switch (status) {
    case 'awaiting_deposit':
      return 'Awaiting Deposit'
    case 'deposit_detected':
      return 'Deposit Detected'
    case 'joining_sc':
      return 'Joining SC...'
    case 'active_in_sc':
      return 'Active'
    case 'won_awaiting_sweep':
      return 'Won - Sweeping'
    case 'swept':
      return 'Paid Out'
    case 'completed':
      return 'Complete'
    case 'lost':
      return 'Lost'
    case 'expired':
      return 'Expired'
    case 'refunded':
      return 'Refunded'
    case 'failed':
      return 'Failed'
    default:
      return status
  }
}

function InfoRow({
  label,
  value,
  mono,
  className,
}: {
  label: string
  value: string
  mono?: boolean
  className?: string
}) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span
        className={cn(
          'font-medium text-foreground',
          mono && 'font-mono text-xs',
          className,
        )}
      >
        {value}
      </span>
    </div>
  )
}
