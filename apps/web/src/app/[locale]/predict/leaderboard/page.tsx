'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'
import { cn } from '@/lib/utils'
import { LeaderboardSkeleton } from '@/components/predict/skeletons'
import { usePagination, PaginationControls } from '@/components/predict/PaginationControls'

interface LeaderboardEntry {
  address: string
  displayName: string | null
  totalBets: number
  wins: number
  losses: number
  accuracy: number
  totalWon: number
  totalBet: number
  profitQu: number
}

export default function LeaderboardPage() {
  const routeParams = useParams()
  const locale = (routeParams?.locale as string) ?? 'en'
  const [entries, setEntries] = useState<LeaderboardEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [sortBy, setSortBy] = useState<'accuracy' | 'profit' | 'volume'>(
    'accuracy',
  )

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('/api/predict/stats?type=leaderboard')
        if (res.ok) {
          const data = await res.json()
          setEntries(data.leaderboard ?? [])
        }
      } catch {
        // ignore
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const sorted = [...entries].sort((a, b) => {
    switch (sortBy) {
      case 'accuracy':
        return b.accuracy - a.accuracy || b.totalBets - a.totalBets
      case 'profit':
        return b.profitQu - a.profitQu
      case 'volume':
        return b.totalBet - a.totalBet
      default:
        return 0
    }
  })

  const { page, setPage, totalPages, paged, resetPage } = usePagination(sorted, 20)

  // Reset to page 1 when sort changes
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { resetPage() }, [sortBy])

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <Link
        href={`/${locale}/predict`}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Markets
      </Link>

      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Leaderboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Top predictors ranked by performance
        </p>
      </div>

      {/* Sort Tabs */}
      <div className="mb-6 flex gap-2">
        {(['accuracy', 'profit', 'volume'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setSortBy(tab)}
            className={cn(
              'rounded-full px-4 py-1.5 text-sm font-medium transition-colors',
              sortBy === tab
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-accent',
            )}
          >
            {tab === 'accuracy'
              ? 'Accuracy'
              : tab === 'profit'
                ? 'Profit'
                : 'Volume'}
          </button>
        ))}
      </div>

      {loading ? (
        <LeaderboardSkeleton />
      ) : sorted.length === 0 ? (
        <div className="rounded-lg border bg-card p-8 text-center text-muted-foreground">
          No predictions resolved yet. Be the first!
        </div>
      ) : (
        <>
        <div className="overflow-hidden rounded-lg border">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                <th className="px-4 py-3">#</th>
                <th className="px-4 py-3">Predictor</th>
                <th className="px-4 py-3 text-right">Bets</th>
                <th className="px-4 py-3 text-right">W/L</th>
                <th className="px-4 py-3 text-right">Accuracy</th>
                <th className="px-4 py-3 text-right">Volume</th>
                <th className="px-4 py-3 text-right">P&L</th>
              </tr>
            </thead>
            <tbody>
              {paged.map((entry, idx) => {
                const i = (page - 1) * 20 + idx
                return (
                <tr
                  key={entry.address}
                  className="border-b transition-colors hover:bg-accent/50"
                >
                  <td className="px-4 py-3 text-sm">
                    {i < 3 ? (
                      <span className="text-lg">
                        {i === 0 ? '\u{1F947}' : i === 1 ? '\u{1F948}' : '\u{1F949}'}
                      </span>
                    ) : (
                      <span className="text-muted-foreground">
                        {i + 1}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <p className="text-sm font-medium">
                      {entry.displayName ??
                        `${entry.address.slice(0, 8)}...${entry.address.slice(-4)}`}
                    </p>
                  </td>
                  <td className="px-4 py-3 text-right text-sm">
                    {entry.totalBets}
                  </td>
                  <td className="px-4 py-3 text-right text-sm">
                    <span className="text-green-500">{entry.wins}</span>
                    {' / '}
                    <span className="text-red-500">{entry.losses}</span>
                  </td>
                  <td className="px-4 py-3 text-right text-sm font-medium">
                    {(entry.accuracy * 100).toFixed(1)}%
                  </td>
                  <td className="px-4 py-3 text-right text-sm text-muted-foreground">
                    {entry.totalBet.toLocaleString()} QU
                  </td>
                  <td
                    className={cn(
                      'px-4 py-3 text-right text-sm font-medium',
                      entry.profitQu > 0
                        ? 'text-green-500'
                        : entry.profitQu < 0
                          ? 'text-red-500'
                          : '',
                    )}
                  >
                    {entry.profitQu >= 0 ? '+' : ''}
                    {entry.profitQu.toLocaleString()} QU
                  </td>
                </tr>
              )})}
            </tbody>
          </table>
        </div>
        <PaginationControls
          page={page}
          totalPages={totalPages}
          onPageChange={setPage}
          className="mt-4"
        />
      </>
      )}
    </div>
  )
}
