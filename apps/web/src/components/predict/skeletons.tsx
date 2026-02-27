import { Skeleton } from '@/components/ui/skeleton'

/** Single market card skeleton — matches MarketCard layout */
export function MarketCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-5">
      {/* Badge row */}
      <div className="mb-3 flex items-center gap-2">
        <Skeleton className="h-5 w-14" />
        <Skeleton className="h-5 w-20" />
        <div className="flex-1" />
        <Skeleton className="h-5 w-16" />
      </div>
      {/* Question (2 lines) */}
      <Skeleton className="mb-2 h-4 w-full" />
      <Skeleton className="mb-4 h-4 w-3/4" />
      {/* Probability bar */}
      <div className="mb-1.5 flex items-center justify-between">
        <Skeleton className="h-3 w-12" />
        <Skeleton className="h-3 w-12" />
      </div>
      <Skeleton className="mb-4 h-2 w-full rounded-full" />
      {/* Footer stats */}
      <div className="flex items-center justify-between">
        <Skeleton className="h-3.5 w-20" />
        <Skeleton className="h-3.5 w-16" />
        <Skeleton className="h-3.5 w-16" />
      </div>
    </div>
  )
}

/** Market grid skeleton — 6 cards in the responsive grid */
export function MarketGridSkeleton() {
  return (
    <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <MarketCardSkeleton key={i} />
      ))}
    </div>
  )
}

/** Leaderboard skeleton — sort tabs + 8-row table */
export function LeaderboardSkeleton() {
  return (
    <div>
      {/* Sort tabs */}
      <div className="mb-6 flex gap-2">
        <Skeleton className="h-8 w-24 rounded-full" />
        <Skeleton className="h-8 w-20 rounded-full" />
        <Skeleton className="h-8 w-20 rounded-full" />
      </div>
      {/* Table header */}
      <div className="overflow-hidden rounded-lg border">
        <div className="border-b bg-muted/50 px-4 py-3">
          <Skeleton className="h-3 w-full" />
        </div>
        {/* 8 rows */}
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 border-b px-4 py-3">
            <Skeleton className="h-4 w-6" />
            <Skeleton className="h-4 w-32" />
            <div className="flex-1" />
            <Skeleton className="h-4 w-10" />
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 w-14" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-20" />
          </div>
        ))}
      </div>
    </div>
  )
}

/** History skeleton — stats grid + tab bar + activity list */
export function HistorySkeleton() {
  return (
    <div className="space-y-6">
      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {Array.from({ length: 7 }).map((_, i) => (
          <div key={i} className="rounded-lg bg-accent/30 p-3">
            <Skeleton className="mb-2 h-3 w-12" />
            <Skeleton className="h-4 w-16" />
          </div>
        ))}
      </div>
      {/* Tab bar */}
      <div className="flex gap-2 border-b border-border/50 pb-2">
        <Skeleton className="h-9 w-24 rounded-t-lg" />
        <Skeleton className="h-9 w-32 rounded-t-lg" />
        <Skeleton className="h-9 w-28 rounded-t-lg" />
      </div>
      {/* Content area */}
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="rounded-xl border bg-card p-4">
            <Skeleton className="mb-2 h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        ))}
      </div>
    </div>
  )
}

/** Portfolio skeleton — stat cards + bet list rows */
export function PortfolioSkeleton() {
  return (
    <div>
      {/* Stat cards */}
      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-lg border bg-card p-4">
            <Skeleton className="mb-2 h-3 w-16" />
            <Skeleton className="h-5 w-24" />
          </div>
        ))}
      </div>
      <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-lg border bg-card p-4">
            <Skeleton className="mb-2 h-3 w-12" />
            <Skeleton className="h-5 w-16" />
          </div>
        ))}
      </div>
      {/* Bet list */}
      <Skeleton className="mb-4 h-5 w-24" />
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="rounded-lg border bg-card p-4">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <Skeleton className="mb-2 h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </div>
              <Skeleton className="h-6 w-16 rounded-full" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

/** Verify skeleton — 3 section cards */
export function VerifySkeleton() {
  return (
    <div className="space-y-8">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="rounded-xl border border-border/50 bg-card p-6 space-y-4">
          <div className="flex items-center gap-3">
            <Skeleton className="h-5 w-5 rounded" />
            <Skeleton className="h-6 w-48" />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, j) => (
              <div key={j} className="rounded-lg bg-accent/30 p-3">
                <Skeleton className="mb-2 h-3 w-20" />
                <Skeleton className="h-4 w-16" />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
