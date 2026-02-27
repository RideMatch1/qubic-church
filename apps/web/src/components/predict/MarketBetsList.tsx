'use client'

import * as React from 'react'
import { ArrowUpRight, ArrowDownRight } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import type { UserBet } from './types'
import { formatQu, anonymizeAddress, formatDateTime } from './helpers'
import { usePagination, PaginationControls } from './PaginationControls'

interface MarketBetsListProps {
  bets: UserBet[]
}

export function MarketBetsList({ bets }: MarketBetsListProps) {
  const { page, setPage, totalPages, paged } = usePagination(bets, 10)

  if (bets.length === 0) {
    return (
      <div className="rounded-lg border bg-card p-6">
        <h3 className="mb-3 text-sm font-semibold text-foreground">
          Recent Bets
        </h3>
        <p className="text-center text-sm text-muted-foreground py-4">
          No bets placed yet. Be the first!
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-lg border bg-card p-6">
      <h3 className="mb-4 text-sm font-semibold text-foreground">
        Recent Bets ({bets.length})
      </h3>

      <div className="space-y-2">
        {paged.map((bet) => (
          <div
            key={bet.id}
            className="flex items-center justify-between rounded-md border bg-muted/20 px-3 py-2.5"
          >
            <div className="flex items-center gap-3">
              <div
                className={cn(
                  'flex h-7 w-7 items-center justify-center rounded-full',
                  bet.option === 0
                    ? 'bg-emerald-500/15 text-emerald-400'
                    : 'bg-red-500/15 text-red-400',
                )}
              >
                {bet.option === 0 ? (
                  <ArrowUpRight className="h-3.5 w-3.5" />
                ) : (
                  <ArrowDownRight className="h-3.5 w-3.5" />
                )}
              </div>
              <div>
                <p className="text-xs font-medium text-foreground">
                  {anonymizeAddress(bet.userAddress)}
                </p>
                <p className="text-xs text-muted-foreground">
                  {bet.slots} slot{bet.slots > 1 ? 's' : ''}
                </p>
              </div>
            </div>

            <div className="text-right">
              <p className="text-xs font-medium text-foreground">
                {formatQu(bet.amountQu)} QU
              </p>
              <div className="flex items-center justify-end gap-1.5">
                <Badge
                  variant="outline"
                  className={cn(
                    'text-[10px] px-1.5 py-0',
                    bet.option === 0
                      ? 'text-emerald-400 border-emerald-500/30'
                      : 'text-red-400 border-red-500/30',
                  )}
                >
                  {bet.option === 0 ? 'Yes' : 'No'}
                </Badge>
                <span className="text-[10px] text-muted-foreground">
                  {formatDateTime(bet.createdAt)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <PaginationControls
        page={page}
        totalPages={totalPages}
        onPageChange={setPage}
        className="mt-4"
      />
    </div>
  )
}
