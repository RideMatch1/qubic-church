'use client'

import * as React from 'react'
import { Lock, ShieldAlert } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { formatQu } from './helpers'

interface BetLockWarningProps {
  open: boolean
  onConfirm: () => void
  onCancel: () => void
  option: string
  slots: number
  amountQu: number
}

export function BetLockWarning({
  open,
  onConfirm,
  onCancel,
  option,
  slots,
  amountQu,
}: BetLockWarningProps) {
  const [accepted, setAccepted] = React.useState(false)

  // Reset checkbox when modal opens
  React.useEffect(() => {
    if (open) {
      setAccepted(false)
    }
  }, [open])

  if (!open) return null

  return (
    <div
      className={cn(
        'fixed inset-0 z-50 flex items-center justify-center p-4',
        'bg-black/60 backdrop-blur-sm',
        'animate-in fade-in duration-200',
      )}
      onClick={(e) => {
        if (e.target === e.currentTarget) onCancel()
      }}
    >
      <div
        className={cn(
          'w-full max-w-md rounded-lg border bg-card p-6 shadow-xl',
          'animate-in zoom-in-95 fade-in duration-200',
        )}
      >
        {/* Title */}
        <div className="mb-4 flex items-center gap-2">
          <Lock className="h-5 w-5 text-amber-400" />
          <h2 className="text-lg font-semibold text-foreground">
            Your Bet is Irreversible
          </h2>
        </div>

        {/* Explanation */}
        <p className="mb-4 text-sm leading-relaxed text-muted-foreground">
          Once your deposit is sent to the escrow address, it will be
          automatically submitted to the Quottery Smart Contract. After that,
          your funds are permanently locked until the market resolves.
        </p>

        {/* Bet Summary */}
        <div className="mb-4 space-y-2 rounded-md border bg-muted/30 p-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Option</span>
            <span className="font-medium text-foreground">{option}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Slots</span>
            <span className="font-medium text-foreground">{slots}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Amount</span>
            <span className="font-semibold text-foreground">
              {formatQu(amountQu)} QU
            </span>
          </div>
        </div>

        {/* Fee Breakdown */}
        <div className="mb-4 rounded-md border border-amber-500/20 bg-amber-500/5 p-3">
          <div className="flex items-start gap-2">
            <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
            <div className="text-xs leading-relaxed text-muted-foreground">
              <p className="mb-1 font-medium text-foreground">
                SC Fee: 12.5% of losing side
              </p>
              <p>2% Burn + 10% Ecosystem + 0.5% Operator (deducted from losers&apos; pool only)</p>
              <p className="mt-1 font-medium text-emerald-400">
                Platform Fee: 0%
              </p>
            </div>
          </div>
        </div>

        {/* Checkbox */}
        <label className="mb-5 flex cursor-pointer items-start gap-3">
          <input
            type="checkbox"
            checked={accepted}
            onChange={(e) => setAccepted(e.target.checked)}
            className="mt-0.5 h-4 w-4 shrink-0 rounded border-muted-foreground accent-emerald-500"
          />
          <span className="text-sm text-muted-foreground">
            I understand that my bet cannot be withdrawn
          </span>
        </label>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            variant="ghost"
            className="flex-1"
            onClick={onCancel}
          >
            Cancel
          </Button>
          <Button
            className={cn(
              'flex-1',
              'bg-emerald-600 text-white hover:bg-emerald-700',
              'disabled:bg-emerald-600/40 disabled:text-white/50',
            )}
            disabled={!accepted}
            onClick={onConfirm}
          >
            <Lock className="mr-2 h-4 w-4" />
            Confirm Bet
          </Button>
        </div>
      </div>
    </div>
  )
}
