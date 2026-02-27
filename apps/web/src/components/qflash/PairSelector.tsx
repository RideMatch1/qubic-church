'use client'

import { cn } from '@/lib/utils'

interface PairSelectorProps {
  pairs: string[]
  selected: string
  onSelect: (pair: string) => void
}

const PAIR_COLORS: Record<string, string> = {
  'btc/usdt': 'border-orange-500/40 text-orange-400 bg-orange-500/10',
  'eth/usdt': 'border-blue-500/40 text-blue-400 bg-blue-500/10',
  'sol/usdt': 'border-purple-500/40 text-purple-400 bg-purple-500/10',
}

export function PairSelector({ pairs, selected, onSelect }: PairSelectorProps) {
  return (
    <div className="flex items-center gap-2">
      {pairs.map((pair) => {
        const isSelected = pair === selected
        const activeColor = PAIR_COLORS[pair] ?? 'border-primary/40 text-primary bg-primary/10'

        return (
          <button
            key={pair}
            type="button"
            onClick={() => onSelect(pair)}
            className={cn(
              'rounded-lg border px-3 py-1.5 text-sm font-bold font-mono uppercase transition-all',
              isSelected
                ? activeColor
                : 'border-border text-muted-foreground hover:border-primary/30 hover:text-foreground bg-card',
            )}
          >
            {pair.split('/')[0]}
          </button>
        )
      })}
    </div>
  )
}
