'use client'

import * as React from 'react'
import { ChevronDown, ChevronUp, Info } from 'lucide-react'

import { cn } from '@/lib/utils'

const LIFECYCLE_STEPS = [
  { step: 'Deposit', description: 'Send QU to the escrow address' },
  { step: 'JoinBet', description: 'Escrow submits your bet to the SC' },
  { step: 'Lock', description: 'Funds are locked in the smart contract' },
  { step: 'Resolution', description: 'Oracle resolves the market outcome' },
  { step: 'Payout', description: 'Winners receive their share automatically' },
]

const FEE_ITEMS = [
  { label: 'Burn', pct: '2.0%', note: 'permanently destroyed' },
  { label: 'Ecosystem', pct: '10.0%', note: 'Qubic shareholders' },
  { label: 'Operator', pct: '0.5%', note: 'market creator' },
  { label: 'Platform', pct: '0%', note: 'we take nothing', highlight: true },
]

export function SmartContractRules() {
  const [expanded, setExpanded] = React.useState(false)

  return (
    <div className="rounded-lg border bg-card">
      {/* Header */}
      <button
        type="button"
        className={cn(
          'flex w-full items-center justify-between px-4 py-3 text-left transition-colors',
          'hover:bg-muted/30',
        )}
        onClick={() => setExpanded((prev) => !prev)}
        aria-expanded={expanded}
      >
        <div className="flex items-center gap-2">
          <Info className="h-4 w-4 text-blue-400" />
          <span className="text-sm font-medium text-foreground">
            How does this work?
          </span>
        </div>
        {expanded ? (
          <ChevronUp className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        )}
      </button>

      {/* Expandable Content */}
      {expanded && (
        <div className="space-y-5 border-t px-4 pb-5 pt-4">
          {/* Lifecycle */}
          <div>
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Lifecycle
            </h4>
            <div className="flex flex-col gap-0">
              {LIFECYCLE_STEPS.map((item, i) => (
                <div key={item.step} className="flex items-start gap-3">
                  {/* Connector line + dot */}
                  <div className="flex flex-col items-center">
                    <div
                      className={cn(
                        'flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-[10px] font-bold',
                        'border-blue-500/30 bg-blue-500/10 text-blue-400',
                      )}
                    >
                      {i + 1}
                    </div>
                    {i < LIFECYCLE_STEPS.length - 1 && (
                      <div className="h-4 w-px bg-muted" />
                    )}
                  </div>
                  <div className="pb-2">
                    <p className="text-sm font-medium text-foreground">
                      {item.step}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {item.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Fee Structure */}
          <div>
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Fee Structure
            </h4>
            <div className="space-y-2 rounded-md border bg-muted/30 p-3">
              {FEE_ITEMS.map((fee) => (
                <div
                  key={fee.label}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-muted-foreground">
                    {fee.label}{' '}
                    <span className="text-xs opacity-60">({fee.note})</span>
                  </span>
                  <span
                    className={cn(
                      'font-medium',
                      fee.highlight
                        ? 'text-emerald-400'
                        : 'text-foreground',
                    )}
                  >
                    {fee.pct}
                  </span>
                </div>
              ))}
              <div className="mt-1 border-t pt-2">
                <div className="flex items-center justify-between text-sm font-semibold">
                  <span className="text-foreground">Total (from losing side only)</span>
                  <span className="text-foreground">12.5%</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  Fees are deducted from the losing side&apos;s pool. Winners get their full stake back plus the remaining loser pool.
                </p>
              </div>
            </div>
          </div>

          {/* Why can't I withdraw */}
          <div>
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Why can&apos;t I withdraw?
            </h4>
            <div className="space-y-2 text-sm leading-relaxed text-muted-foreground">
              <p>
                The Quottery Smart Contract locks all bets permanently. This is
                by design &mdash; it ensures the pool is guaranteed and payouts
                are trustless.
              </p>
              <p>
                Only the market creator can cancel the entire market, which
                refunds ALL participants.
              </p>
            </div>
          </div>

        </div>
      )}
    </div>
  )
}
