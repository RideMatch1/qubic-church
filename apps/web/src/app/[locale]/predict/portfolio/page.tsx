'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { getStoredAddress, setStoredAddress } from '@/components/predict/helpers'

interface UserBet {
  id: string
  marketId: string
  option: number
  slots: number
  amountQu: number
  status: string
  payoutQu: number | null
  createdAt: string
  marketQuestion?: string
  marketPair?: string
}

interface Account {
  address: string
  displayName: string | null
  balanceQu: number
  totalDeposited: number
  totalWithdrawn: number
  totalBet: number
  totalWon: number
}

export default function PortfolioPage() {
  const [address, setAddress] = useState(() => getStoredAddress())
  const [submittedAddress, setSubmittedAddress] = useState('')
  const [account, setAccount] = useState<Account | null>(null)
  const [bets, setBets] = useState<UserBet[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const loadPortfolio = useCallback(async (addr: string) => {
    if (!addr || addr.length !== 60) return
    setLoading(true)
    setError('')

    try {
      const [accountRes, betsRes] = await Promise.all([
        fetch(`/api/predict/account?address=${addr}`),
        fetch(`/api/predict/bet?address=${addr}`),
      ])

      if (accountRes.ok) {
        const data = await accountRes.json()
        setAccount(data.account)
      } else {
        setAccount(null)
      }

      if (betsRes.ok) {
        const data = await betsRes.json()
        setBets(data.bets ?? [])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load portfolio')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (submittedAddress) {
      loadPortfolio(submittedAddress)
    }
  }, [submittedAddress, loadPortfolio])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (address.length === 60 && /^[A-Z]+$/.test(address)) {
      setStoredAddress(address)
      setSubmittedAddress(address)
    } else {
      setError('Invalid address format. Must be 60 uppercase letters.')
    }
  }

  const wins = bets.filter((b) => b.status === 'won').length
  const losses = bets.filter((b) => b.status === 'lost').length
  const pending = bets.filter(
    (b) => b.status === 'pending' || b.status === 'confirmed',
  ).length
  const totalBet = bets.reduce((a, b) => a + b.amountQu, 0)
  const totalWon = bets
    .filter((b) => b.status === 'won')
    .reduce((a, b) => a + (b.payoutQu ?? 0), 0)
  const pnl = totalWon - totalBet
  const accuracy =
    wins + losses > 0
      ? ((wins / (wins + losses)) * 100).toFixed(1)
      : '—'

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Portfolio</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Track your prediction market performance
        </p>
      </div>

      {/* Address Input */}
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex gap-3">
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value.toUpperCase())}
            placeholder="Enter your Qubic address (60 uppercase letters)"
            className="flex-1 rounded-lg border bg-background px-4 py-2.5 text-sm font-mono placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            maxLength={60}
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'View'}
          </button>
        </div>
        {error && (
          <p className="mt-2 text-sm text-red-500">{error}</p>
        )}
      </form>

      {/* Account Overview */}
      {account && (
        <>
          <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
            <StatCard
              label="Balance"
              value={`${account.balanceQu.toLocaleString()} QU`}
            />
            <StatCard
              label="Total Bet"
              value={`${totalBet.toLocaleString()} QU`}
            />
            <StatCard
              label="Total Won"
              value={`${totalWon.toLocaleString()} QU`}
              className={totalWon > 0 ? 'text-green-500' : ''}
            />
            <StatCard
              label="P&L"
              value={`${pnl >= 0 ? '+' : ''}${pnl.toLocaleString()} QU`}
              className={pnl > 0 ? 'text-green-500' : pnl < 0 ? 'text-red-500' : ''}
            />
          </div>

          <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
            <StatCard label="Wins" value={String(wins)} className="text-green-500" />
            <StatCard label="Losses" value={String(losses)} className="text-red-500" />
            <StatCard label="Pending" value={String(pending)} />
            <StatCard label="Accuracy" value={`${accuracy}%`} />
          </div>
        </>
      )}

      {/* Bets List */}
      {submittedAddress && bets.length > 0 && (
        <div>
          <h2 className="mb-4 text-lg font-semibold">Your Bets</h2>
          <div className="space-y-3">
            {bets.map((bet) => (
              <Link
                key={bet.id}
                href={`/predict/${bet.marketId}`}
                className="block rounded-lg border bg-card p-4 transition-colors hover:bg-accent/50"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="font-medium">
                      {bet.marketQuestion ?? bet.marketId}
                    </p>
                    <div className="mt-1 flex items-center gap-3 text-sm text-muted-foreground">
                      {bet.marketPair && (
                        <span className="uppercase">{bet.marketPair}</span>
                      )}
                      <span>
                        {bet.option === 0 ? 'YES' : 'NO'} x {bet.slots} slot
                        {bet.slots > 1 ? 's' : ''}
                      </span>
                      <span>{bet.amountQu.toLocaleString()} QU</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <BetStatusBadge status={bet.status} />
                    {bet.payoutQu !== null && bet.payoutQu > 0 && (
                      <p className="mt-1 text-sm font-medium text-green-500">
                        +{bet.payoutQu.toLocaleString()} QU
                      </p>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {submittedAddress && bets.length === 0 && !loading && (
        <div className="rounded-lg border bg-card p-8 text-center">
          <p className="text-muted-foreground">
            No bets found for this address.
          </p>
          <Link
            href="/predict"
            className="mt-3 inline-block text-sm font-medium text-primary hover:underline"
          >
            Browse Markets
          </Link>
        </div>
      )}
    </div>
  )
}

function StatCard({
  label,
  value,
  className,
}: {
  label: string
  value: string
  className?: string
}) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={cn('mt-1 text-lg font-semibold', className)}>
        {value}
      </p>
    </div>
  )
}

function BetStatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    pending: 'bg-yellow-500/10 text-yellow-500',
    confirmed: 'bg-blue-500/10 text-blue-500',
    won: 'bg-green-500/10 text-green-500',
    lost: 'bg-red-500/10 text-red-500',
    refunded: 'bg-gray-500/10 text-gray-500',
  }

  const labels: Record<string, string> = {
    pending: 'Pending',
    confirmed: 'Active',
    won: 'Won',
    lost: 'Lost',
    refunded: 'Refunded',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        styles[status] ?? 'bg-gray-500/10 text-gray-500',
      )}
    >
      {labels[status] ?? status}
    </span>
  )
}
