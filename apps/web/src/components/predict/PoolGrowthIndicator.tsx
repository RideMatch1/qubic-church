'use client'

import { TrendingUp } from 'lucide-react'

import { cn } from '@/lib/utils'
import { formatQu } from './helpers'

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface PoolGrowthIndicatorProps {
  totalPool: number
  className?: string
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function PoolGrowthIndicator({ totalPool, className }: PoolGrowthIndicatorProps) {
  return (
    <div className={cn('flex items-center gap-3', className)}>
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500/10">
        <TrendingUp className="h-5 w-5 text-emerald-400" />
      </div>
      <div>
        <p
          className="text-2xl font-bold tabular-nums text-foreground transition-all duration-500"
          style={{ transitionProperty: 'all' }}
        >
          {formatQu(totalPool)}
        </p>
        <p className="text-xs text-muted-foreground">QU Total Pool</p>
      </div>
    </div>
  )
}
