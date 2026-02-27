'use client'

import { Building2, TrendingUp, TrendingDown, Shield } from 'lucide-react'
import { useAutoRefresh } from '@/hooks/useAutoRefresh'
import { formatQu } from './helpers'

interface HouseStatsData {
  balanceQu: number
  totalExposureQu: number
  roundsPlayed: number
  wins: number
  losses: number
  totalWonQu: number
  totalLostQu: number
  netPnlQu: number
  feeIncomeQu: number
}

export function HouseStats() {
  const { data } = useAutoRefresh<HouseStatsData>(
    async () => {
      const res = await fetch('/api/qflash/house')
      if (!res.ok) throw new Error('Failed to fetch house stats')
      return res.json()
    },
    15_000,
    [],
  )

  if (!data) return null

  const winRate = data.roundsPlayed > 0
    ? ((data.wins / data.roundsPlayed) * 100).toFixed(1)
    : '0.0'

  const pnlColor = data.netPnlQu >= 0 ? 'text-green-500' : 'text-red-500'
  const PnlIcon = data.netPnlQu >= 0 ? TrendingUp : TrendingDown

  return (
    <div className="rounded-xl border bg-card p-4">
      <div className="mb-3 flex items-center gap-2">
        <Building2 className="h-4 w-4 text-muted-foreground" />
        <h3 className="text-sm font-medium">House Bank</h3>
        <span className="ml-auto flex items-center gap-1 text-[10px] text-muted-foreground">
          <Shield className="h-3 w-3" />
          Transparency
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs">
        <div>
          <p className="text-muted-foreground">Balance</p>
          <p className="font-mono font-semibold">{formatQu(data.balanceQu)} QU</p>
        </div>
        <div>
          <p className="text-muted-foreground">Net P&L</p>
          <p className={`font-mono font-semibold flex items-center gap-1 ${pnlColor}`}>
            <PnlIcon className="h-3 w-3" />
            {data.netPnlQu >= 0 ? '+' : ''}{formatQu(data.netPnlQu)} QU
          </p>
        </div>
        <div>
          <p className="text-muted-foreground">Win Rate</p>
          <p className="font-mono font-semibold">{winRate}%</p>
        </div>
        <div>
          <p className="text-muted-foreground">Exposure</p>
          <p className="font-mono font-semibold">{formatQu(data.totalExposureQu)} QU</p>
        </div>
        <div>
          <p className="text-muted-foreground">Rounds</p>
          <p className="font-mono font-semibold">{data.roundsPlayed}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Fee Income</p>
          <p className="font-mono font-semibold text-amber-500">{formatQu(data.feeIncomeQu)} QU</p>
        </div>
      </div>
    </div>
  )
}
