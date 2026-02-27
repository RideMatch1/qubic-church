'use client'

import * as React from 'react'
import { CheckCircle2, Share2 } from 'lucide-react'

import { cn } from '@/lib/utils'
import { formatQu } from './helpers'

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface ShareBetProps {
  question: string
  option: string
  amountQu: number
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function ShareBet({ question, option, amountQu }: ShareBetProps) {
  const [copied, setCopied] = React.useState(false)

  async function handleShare() {
    const text = `I just bet ${formatQu(amountQu)} QU on ${option} for '${question}' on QPredict!`

    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2500)
    } catch {
      // Clipboard API not available - silent fail
    }
  }

  return (
    <button
      onClick={handleShare}
      className={cn(
        'inline-flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium transition-all',
        copied
          ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
          : 'border-muted bg-card text-foreground hover:bg-muted',
      )}
    >
      {copied ? (
        <>
          <CheckCircle2 className="h-4 w-4" />
          Copied!
        </>
      ) : (
        <>
          <Share2 className="h-4 w-4" />
          Share your bet!
        </>
      )}
    </button>
  )
}
