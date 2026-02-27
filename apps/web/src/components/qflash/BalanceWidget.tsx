'use client'

import { useState } from 'react'
import { Wallet, Copy, Check, LogOut } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { formatQu, anonymizeAddress } from './helpers'

interface BalanceWidgetProps {
  address: string
  balance: number
  onAddressChange: (address: string) => void
  onWithdraw: () => void
}

export function BalanceWidget({ address, balance, onAddressChange, onWithdraw }: BalanceWidgetProps) {
  const [editing, setEditing] = useState(!address)
  const [inputValue, setInputValue] = useState(address)
  const [copied, setCopied] = useState(false)

  // Platform deposit address (in production, this would be per-user)
  const depositAddress = process.env.NEXT_PUBLIC_QFLASH_DEPOSIT_ADDRESS ?? 'DEPOSIT_ADDRESS_NOT_CONFIGURED'

  const handleSubmitAddress = () => {
    const trimmed = inputValue.trim().toUpperCase()
    if (trimmed.length === 60 && /^[A-Z]+$/.test(trimmed)) {
      onAddressChange(trimmed)
      setEditing(false)
    }
  }

  const copyDepositAddress = async () => {
    try {
      await navigator.clipboard.writeText(depositAddress)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard API not available
    }
  }

  if (editing || !address) {
    return (
      <div className="rounded-xl border bg-card p-4">
        <div className="flex items-center gap-2 mb-3">
          <Wallet className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium">Connect Your Address</span>
        </div>
        <div className="flex gap-2">
          <Input
            placeholder="Enter Qubic address (60 chars)"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value.toUpperCase())}
            maxLength={60}
            className="font-mono text-xs"
          />
          <Button size="sm" onClick={handleSubmitAddress}>
            Go
          </Button>
        </div>
        <p className="mt-2 text-[10px] text-muted-foreground">
          Your address is used for deposits and payouts. No wallet connection needed.
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border bg-card p-4">
      {/* Balance Display */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Wallet className="h-4 w-4 text-primary" />
          <span className="text-xs text-muted-foreground">
            {anonymizeAddress(address)}
          </span>
          <button
            type="button"
            onClick={() => {
              setInputValue(address)
              setEditing(true)
            }}
            className="text-[10px] text-muted-foreground hover:text-foreground"
          >
            <LogOut className="h-3 w-3" />
          </button>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-0.5">Balance</p>
        <p className="text-2xl font-bold font-mono tabular-nums">{formatQu(balance)} <span className="text-sm text-muted-foreground">QU</span></p>
      </div>

      {/* Deposit Section */}
      <div className="mb-3 rounded-lg bg-muted/30 p-3">
        <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1.5">
          Deposit QU
        </p>
        <div className="flex items-center gap-2">
          <code className="flex-1 truncate text-[10px] font-mono text-foreground/80 bg-background/50 rounded px-2 py-1">
            {depositAddress}
          </code>
          <button
            type="button"
            onClick={copyDepositAddress}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
          </button>
        </div>
        <p className="mt-1.5 text-[9px] text-muted-foreground">
          Send any amount of QU. Deposits detected automatically within ~15 seconds.
        </p>
      </div>

      {/* Withdraw Button */}
      {balance > 0 && (
        <Button
          variant="outline"
          size="sm"
          onClick={onWithdraw}
          className="w-full"
        >
          Withdraw
        </Button>
      )}
    </div>
  )
}
