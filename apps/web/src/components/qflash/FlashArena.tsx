'use client'

import { useState, useCallback } from 'react'
import { Zap, Clock, BarChart3 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAutoRefresh } from '@/hooks/useAutoRefresh'
import { PairSelector } from './PairSelector'
import { LivePriceBar } from './LivePriceBar'
import { PriceChart } from './PriceChart'
import { RoundCard } from './RoundCard'
import { BetControls } from './BetControls'
import { BalanceWidget } from './BalanceWidget'
import { WinStreak } from './WinStreak'
import { RoundHistory } from './RoundHistory'
import { HouseStats } from './HouseStats'
import { formatQu, getStoredAddress, setStoredAddress, durationLabel } from './helpers'

import type { RoundDuration } from '@/lib/qflash/types'

const PAIRS = ['btc/usdt', 'eth/usdt', 'sol/usdt']
const DURATIONS: RoundDuration[] = [30, 60, 120]

export function FlashArena() {
  const [selectedPair, setSelectedPair] = useState('btc/usdt')
  const [selectedDuration, setSelectedDuration] = useState<RoundDuration>(30)
  const [address, setAddress] = useState(getStoredAddress)
  const [refreshKey, setRefreshKey] = useState(0)

  const triggerRefresh = useCallback(() => setRefreshKey((k) => k + 1), [])

  // Fetch active rounds (3s polling for fast updates)
  const { data: roundsData } = useAutoRefresh<{ rounds: Round[] }>(
    async () => {
      const params = new URLSearchParams({ pair: selectedPair, duration: String(selectedDuration) })
      const res = await fetch(`/api/qflash/rounds?${params.toString()}`)
      if (!res.ok) throw new Error('Failed to fetch rounds')
      return res.json()
    },
    3_000,
    [selectedPair, selectedDuration, refreshKey],
  )

  // Fetch account data (5s polling)
  const { data: accountData } = useAutoRefresh<AccountData | null>(
    async () => {
      if (!address) return null
      const res = await fetch(`/api/qflash/account?address=${encodeURIComponent(address)}`)
      if (!res.ok) return null
      return res.json()
    },
    5_000,
    [address, refreshKey],
  )

  // Fetch user history (10s polling)
  const { data: historyData } = useAutoRefresh<{ entries: HistoryEntry[] }>(
    async () => {
      if (!address) return { entries: [] }
      const res = await fetch(`/api/qflash/history?address=${encodeURIComponent(address)}&limit=20`)
      if (!res.ok) return { entries: [] }
      return res.json()
    },
    10_000,
    [address, refreshKey],
  )

  // Fetch platform stats (30s polling)
  const { data: statsData } = useAutoRefresh<StatsData>(
    async () => {
      const res = await fetch('/api/qflash/stats')
      if (!res.ok) throw new Error('Failed to fetch stats')
      return res.json()
    },
    30_000,
    [],
  )

  const rounds = roundsData?.rounds ?? []
  const account = accountData?.account ?? null
  const balance = account?.balanceQu ?? 0
  const history = historyData?.entries ?? []
  const stats = statsData ?? null

  // Find the current active round (first open, or first upcoming)
  const currentRound = rounds.find((r) => r.status === 'open')
    ?? rounds.find((r) => r.status === 'locked')
    ?? rounds.find((r) => r.status === 'upcoming')
    ?? null

  const handleAddressChange = (addr: string) => {
    setAddress(addr)
    setStoredAddress(addr)
  }

  const handleBetPlaced = () => {
    triggerRefresh()
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      {/* Header */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Zap className="h-7 w-7 text-amber-400" />
          <div>
            <h1 className="text-2xl font-bold tracking-tight">QFlash</h1>
            <p className="text-sm text-muted-foreground">
              Ultra-fast binary predictions. Zero fees.
            </p>
          </div>
        </div>

        {/* Stats bar */}
        {stats && (
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <BarChart3 className="h-3.5 w-3.5" />
              {formatQu(stats.totalVolume)} QU volume
            </span>
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" />
              {stats.totalRounds} rounds
            </span>
          </div>
        )}
      </div>

      {/* Pair + Duration Selectors */}
      <div className="mb-4 flex flex-wrap items-center gap-4">
        <PairSelector
          pairs={PAIRS}
          selected={selectedPair}
          onSelect={setSelectedPair}
        />
        <div className="flex items-center gap-1.5">
          {DURATIONS.map((d) => (
            <button
              key={d}
              type="button"
              onClick={() => setSelectedDuration(d)}
              className={cn(
                'rounded-lg border px-2.5 py-1 text-xs font-mono font-bold transition-all',
                d === selectedDuration
                  ? 'border-primary/40 text-primary bg-primary/10'
                  : 'border-border text-muted-foreground hover:border-primary/30 bg-card',
              )}
            >
              {durationLabel(d)}
            </button>
          ))}
        </div>
      </div>

      {/* Live Price Bar */}
      <div className="mb-4">
        <LivePriceBar pair={selectedPair} pollIntervalMs={3000} />
      </div>

      {/* Live Price Chart */}
      <div className="mb-6">
        <PriceChart
          pair={selectedPair}
          openingPrice={currentRound?.openingPrice}
          pollIntervalMs={3000}
        />
      </div>

      {/* Main Layout: Arena + Sidebar */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left: Active Round + Upcoming */}
        <div className="lg:col-span-2 space-y-4">
          {/* Active Round */}
          {currentRound ? (
            <div className="rounded-xl border-2 border-primary/30 bg-card p-6">
              <div className="grid gap-6 md:grid-cols-2">
                {/* Round Info */}
                <RoundCard
                  round={currentRound}
                  isActive
                  onCountdownComplete={triggerRefresh}
                />

                {/* Bet Controls */}
                <BetControls
                  roundId={currentRound.id}
                  roundStatus={currentRound.status}
                  address={address}
                  balance={balance}
                  onBetPlaced={handleBetPlaced}
                />
              </div>
            </div>
          ) : (
            <div className="rounded-xl border bg-card p-8 text-center">
              <Zap className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
              <p className="text-muted-foreground">No active rounds</p>
              <p className="text-xs text-muted-foreground/70 mt-1">
                Rounds will appear automatically once the system is running.
              </p>
            </div>
          )}

          {/* Upcoming Rounds */}
          {rounds.filter((r) => r.id !== currentRound?.id).length > 0 && (
            <div>
              <h2 className="text-sm font-medium text-muted-foreground mb-3">
                Next Rounds
              </h2>
              <div className="grid gap-3 sm:grid-cols-2">
                {rounds
                  .filter((r) => r.id !== currentRound?.id)
                  .slice(0, 4)
                  .map((round) => (
                    <RoundCard
                      key={round.id}
                      round={round}
                      onCountdownComplete={triggerRefresh}
                    />
                  ))}
              </div>
            </div>
          )}

          {/* Round History */}
          {address && (
            <div>
              <h2 className="text-sm font-medium text-muted-foreground mb-3">
                Your Recent Rounds
              </h2>
              <RoundHistory entries={history} />
            </div>
          )}
        </div>

        {/* Right Sidebar: Balance + Stats */}
        <div className="space-y-4">
          <BalanceWidget
            address={address}
            balance={balance}
            onAddressChange={handleAddressChange}
            onWithdraw={() => {
              // Open withdraw dialog (simplified for now)
              window.alert('Withdrawal feature coming soon. Contact support.')
            }}
          />

          {account && (
            <WinStreak
              streak={account.streak}
              bestStreak={account.bestStreak}
              winCount={account.winCount}
              lossCount={account.lossCount}
            />
          )}

          {/* House Bank Stats */}
          <HouseStats />

          {/* How It Works */}
          <div className="rounded-xl border bg-card p-4">
            <h3 className="text-sm font-medium mb-3">How It Works</h3>
            <ol className="space-y-2 text-xs text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[10px] font-bold text-primary">1</span>
                <span>Deposit QU to your QFlash balance (one-time)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[10px] font-bold text-primary">2</span>
                <span>Pick UP or DOWN before the countdown ends</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[10px] font-bold text-primary">3</span>
                <span>Round resolves via 4-source oracle median price</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[10px] font-bold text-primary">4</span>
                <span>Winners split the loser pool instantly (3% fee)</span>
              </li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Internal Types (API response shapes)
// ---------------------------------------------------------------------------

interface Round {
  id: string
  pair: string
  durationSecs: number
  status: string
  openAt: string
  lockAt: string
  closeAt: string
  openingPrice: number | null
  closingPrice: number | null
  outcome: string | null
  upPoolQu: number
  downPoolQu: number
  entryCount: number
}

interface AccountData {
  account: {
    balanceQu: number
    streak: number
    bestStreak: number
    winCount: number
    lossCount: number
    totalWagered: number
    totalWon: number
  }
}

interface HistoryEntry {
  id: string
  roundId: string
  side: string
  amountQu: number
  payoutQu: number | null
  status: string
  createdAt: string
  pair: string
  durationSecs: number
  outcome: string | null
  openingPrice: number | null
  closingPrice: number | null
  roundStatus: string
}

interface StatsData {
  totalRounds: number
  activeRounds: number
  resolvedRounds: number
  totalVolume: number
  totalEntries: number
  totalAccounts: number
  totalPaidOut: number
  totalPlatformFees: number
}
