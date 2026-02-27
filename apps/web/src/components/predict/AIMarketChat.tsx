'use client'

import * as React from 'react'
import { useParams } from 'next/navigation'
import { Loader2, Send, Sparkles, CheckCircle2, XCircle, Edit3 } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  MARKET_TYPE_LABELS,
  pairLabel,
  type MarketType,
} from './types'

interface ParsedMarket {
  marketType: MarketType
  question: string
  options: string[]
  pair: string | null
  resolutionType: string | null
  resolutionTarget: number | null
  resolutionTargetHigh: number | null
  closeDate: string
  endDate: string
}

interface ParseResult {
  success: boolean
  parsed: ParsedMarket | null
  confidence: number
  error?: string
}

type ChatState = 'idle' | 'thinking' | 'preview' | 'created' | 'error'

interface AIMarketChatProps {
  creatorAddress: string
  onMarketCreated?: (marketId: string) => void
}

export function AIMarketChat({ creatorAddress, onMarketCreated }: AIMarketChatProps) {
  const routeParams = useParams()
  const locale = (routeParams?.locale as string) ?? 'en'
  const [query, setQuery] = React.useState('')
  const [state, setState] = React.useState<ChatState>('idle')
  const [parsed, setParsed] = React.useState<ParsedMarket | null>(null)
  const [confidence, setConfidence] = React.useState(0)
  const [errorMsg, setErrorMsg] = React.useState('')
  const [createdId, setCreatedId] = React.useState('')
  const [submitting, setSubmitting] = React.useState(false)
  const inputRef = React.useRef<HTMLInputElement>(null)

  async function handleParse() {
    const trimmed = query.trim()
    if (trimmed.length < 5) return

    setState('thinking')
    setErrorMsg('')
    setParsed(null)

    try {
      const res = await fetch('/api/predict/ai-parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: trimmed }),
      })

      const data: ParseResult = await res.json()

      if (!res.ok || !data.success || !data.parsed) {
        setErrorMsg(data.error ?? 'Could not parse your idea. Try rephrasing it.')
        setState('error')
        return
      }

      setParsed(data.parsed)
      setConfidence(data.confidence)
      setState('preview')
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Network error')
      setState('error')
    }
  }

  async function handleCreate() {
    if (!parsed) return

    setSubmitting(true)
    setErrorMsg('')

    try {
      const payload = {
        pair: parsed.pair ?? 'none',
        question: parsed.question,
        resolutionType: parsed.resolutionType ?? 'price_above',
        resolutionTarget: parsed.resolutionTarget ?? 0,
        resolutionTargetHigh: parsed.resolutionTargetHigh ?? undefined,
        closeDate: parsed.closeDate,
        endDate: parsed.endDate,
        creatorAddress,
        marketType: parsed.marketType,
        options: parsed.options,
        oracleFeeBps: 0,
        oracleAddresses: parsed.marketType === 'custom' ? [creatorAddress] : undefined,
      }

      const res = await fetch('/api/predict/markets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()

      if (!res.ok || !data.success) {
        setErrorMsg(data.error ?? 'Failed to create market')
        setSubmitting(false)
        return
      }

      setCreatedId(data.market?.id ?? '')
      setState('created')
      setSubmitting(false)
      onMarketCreated?.(data.market?.id ?? '')
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Network error')
      setSubmitting(false)
    }
  }

  function handleReset() {
    setState('idle')
    setQuery('')
    setParsed(null)
    setConfidence(0)
    setErrorMsg('')
    setCreatedId('')
    inputRef.current?.focus()
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleParse()
    }
  }

  return (
    <div className="rounded-lg border bg-card">
      {/* Header */}
      <div className="flex items-center gap-2 border-b px-4 py-3">
        <Sparkles className="h-4 w-4 text-purple-400" />
        <h3 className="text-sm font-semibold text-foreground">AI Market Creator</h3>
        <span className="rounded-full bg-purple-500/15 px-2 py-0.5 text-[10px] font-medium text-purple-400">
          Beta
        </span>
      </div>

      <div className="p-4">
        {/* Success state */}
        {state === 'created' && (
          <div className="flex flex-col items-center gap-3 py-4 text-center">
            <CheckCircle2 className="h-10 w-10 text-emerald-400" />
            <p className="text-sm font-medium text-foreground">Market Created!</p>
            <p className="text-xs text-muted-foreground">
              Your market is being deployed on-chain.
            </p>
            <div className="flex gap-2">
              {createdId && (
                <Button size="sm" asChild>
                  <a href={`/${locale}/predict/${createdId}`}>View Market</a>
                </Button>
              )}
              <Button size="sm" variant="outline" onClick={handleReset}>
                Create Another
              </Button>
            </div>
          </div>
        )}

        {/* Preview state */}
        {state === 'preview' && parsed && (
          <div className="space-y-3">
            <p className="text-xs text-muted-foreground">
              Here&apos;s what I parsed from your idea:
            </p>

            <div className="rounded-md border bg-muted/30 p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                  Question
                </span>
                <span className={cn(
                  'rounded-full px-2 py-0.5 text-[10px] font-medium',
                  confidence >= 0.8
                    ? 'bg-emerald-500/15 text-emerald-400'
                    : confidence >= 0.5
                      ? 'bg-yellow-500/15 text-yellow-400'
                      : 'bg-red-500/15 text-red-400',
                )}>
                  {Math.round(confidence * 100)}% confident
                </span>
              </div>
              <p className="text-sm font-medium text-foreground">{parsed.question}</p>

              <div className="grid grid-cols-2 gap-2 pt-1">
                <div>
                  <span className="text-[10px] text-muted-foreground">Type</span>
                  <p className="text-xs font-medium text-foreground">
                    {MARKET_TYPE_LABELS[parsed.marketType]}
                  </p>
                </div>
                {parsed.pair && (
                  <div>
                    <span className="text-[10px] text-muted-foreground">Pair</span>
                    <p className="text-xs font-medium text-foreground">
                      {pairLabel(parsed.pair)}
                    </p>
                  </div>
                )}
                {parsed.resolutionTarget !== null && parsed.resolutionTarget > 0 && (
                  <div>
                    <span className="text-[10px] text-muted-foreground">Target</span>
                    <p className="text-xs font-medium text-foreground">
                      ${parsed.resolutionTarget.toLocaleString()}
                    </p>
                  </div>
                )}
              </div>

              {/* Options */}
              <div className="pt-1">
                <span className="text-[10px] text-muted-foreground">Options</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {parsed.options.map((opt, i) => (
                    <span
                      key={i}
                      className="rounded-full border bg-background px-2 py-0.5 text-xs text-foreground"
                    >
                      {opt}
                    </span>
                  ))}
                </div>
              </div>

              {/* Dates */}
              <div className="grid grid-cols-2 gap-2 pt-1">
                <div>
                  <span className="text-[10px] text-muted-foreground">Closes</span>
                  <p className="text-xs text-foreground">
                    {new Date(parsed.closeDate).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground">Resolves</span>
                  <p className="text-xs text-foreground">
                    {new Date(parsed.endDate).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>

            {!creatorAddress && (
              <p className="text-xs text-yellow-400">
                Enter your Qubic address below to create this market.
              </p>
            )}

            <div className="flex gap-2">
              <Button
                size="sm"
                className="flex-1"
                disabled={!creatorAddress || submitting}
                onClick={handleCreate}
              >
                {submitting ? (
                  <>
                    <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create Market'
                )}
              </Button>
              <Button size="sm" variant="outline" onClick={handleReset}>
                <Edit3 className="mr-1 h-3 w-3" />
                Start Over
              </Button>
            </div>
          </div>
        )}

        {/* Idle / thinking / error states */}
        {(state === 'idle' || state === 'thinking' || state === 'error') && (
          <div className="space-y-3">
            <p className="text-xs text-muted-foreground">
              Describe what you want to bet on in plain language. The AI will
              structure it into a market.
            </p>

            {/* Example suggestions */}
            {state === 'idle' && !query && (
              <div className="flex flex-wrap gap-1.5">
                {[
                  'BTC above $200K by June',
                  'Will GPT-5 launch this year?',
                  'Champions League winner 2026',
                ].map((ex) => (
                  <button
                    key={ex}
                    type="button"
                    onClick={() => {
                      setQuery(ex)
                      inputRef.current?.focus()
                    }}
                    className="rounded-full border bg-muted/30 px-2.5 py-1 text-[11px] text-muted-foreground transition-colors hover:border-purple-500/40 hover:text-purple-400"
                  >
                    {ex}
                  </button>
                ))}
              </div>
            )}

            {/* Error */}
            {state === 'error' && errorMsg && (
              <div className="flex items-start gap-2 rounded-md border border-red-500/30 bg-red-500/10 p-2.5">
                <XCircle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-red-400" />
                <p className="text-xs text-red-400">{errorMsg}</p>
              </div>
            )}

            {/* Input */}
            <div className="flex gap-2">
              <Input
                ref={inputRef}
                type="text"
                placeholder="e.g. Will ETH flip BTC by 2027?"
                maxLength={500}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={state === 'thinking'}
                className="text-sm"
              />
              <Button
                size="icon"
                disabled={query.trim().length < 5 || state === 'thinking'}
                onClick={handleParse}
                className="shrink-0"
              >
                {state === 'thinking' ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>

            {state === 'thinking' && (
              <p className="text-center text-xs text-muted-foreground animate-pulse">
                Parsing your idea...
              </p>
            )}
          </div>
        )}

      </div>
    </div>
  )
}
