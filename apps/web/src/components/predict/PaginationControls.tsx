'use client'

import { useState, useMemo, useCallback } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

/**
 * Client-side pagination hook.
 * Returns the current page slice and controls.
 */
export function usePagination<T>(items: T[], pageSize: number) {
  const [page, setPage] = useState(1)

  const totalPages = Math.max(1, Math.ceil(items.length / pageSize))

  // Clamp page if items shrink (e.g. after filter change)
  const safePage = Math.min(page, totalPages)
  if (safePage !== page) {
    // Schedule state update to avoid render-during-render
    queueMicrotask(() => setPage(safePage))
  }

  const paged = useMemo(
    () => items.slice((safePage - 1) * pageSize, safePage * pageSize),
    [items, safePage, pageSize],
  )

  const resetPage = useCallback(() => setPage(1), [])

  return { page: safePage, setPage, totalPages, paged, resetPage }
}

/**
 * Pagination UI with Prev / page numbers / Next buttons.
 */
export function PaginationControls({
  page,
  totalPages,
  onPageChange,
  className,
}: {
  page: number
  totalPages: number
  onPageChange: (page: number) => void
  className?: string
}) {
  if (totalPages <= 1) return null

  const pages = getPageNumbers(page, totalPages)

  return (
    <nav
      className={cn('flex items-center justify-center gap-1', className)}
      aria-label="Pagination"
    >
      <button
        type="button"
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className="inline-flex items-center justify-center rounded-md border px-2 py-1.5 text-sm transition-colors hover:bg-accent disabled:pointer-events-none disabled:opacity-40"
        aria-label="Previous page"
      >
        <ChevronLeft className="h-4 w-4" />
      </button>

      {pages.map((p, i) =>
        p === '...' ? (
          <span
            key={`ellipsis-${i}`}
            className="px-1.5 text-sm text-muted-foreground select-none"
          >
            ...
          </span>
        ) : (
          <button
            key={p}
            type="button"
            onClick={() => onPageChange(p as number)}
            className={cn(
              'inline-flex h-8 w-8 items-center justify-center rounded-md text-sm font-medium transition-colors',
              p === page
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-accent text-muted-foreground',
            )}
            aria-current={p === page ? 'page' : undefined}
          >
            {p}
          </button>
        ),
      )}

      <button
        type="button"
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        className="inline-flex items-center justify-center rounded-md border px-2 py-1.5 text-sm transition-colors hover:bg-accent disabled:pointer-events-none disabled:opacity-40"
        aria-label="Next page"
      >
        <ChevronRight className="h-4 w-4" />
      </button>
    </nav>
  )
}

/**
 * Build an array of page numbers with ellipsis for large ranges.
 * Always shows first, last, and up to 2 pages around current.
 */
function getPageNumbers(
  current: number,
  total: number,
): (number | '...')[] {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  const pages: (number | '...')[] = [1]

  if (current > 3) {
    pages.push('...')
  }

  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  if (current < total - 2) {
    pages.push('...')
  }

  pages.push(total)

  return pages
}
