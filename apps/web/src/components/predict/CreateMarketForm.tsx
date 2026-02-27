'use client'

import * as React from 'react'
import { useRouter, useParams } from 'next/navigation'
import { Loader2, CheckCircle2, XCircle, Info } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  SUPPORTED_PAIRS,
  RESOLUTION_TYPE_LABELS,
  pairLabel,
  type ResolutionType,
  type CreateMarketPayload,
} from './types'

type FormState = 'idle' | 'loading' | 'success' | 'error'

interface FormErrors {
  pair?: string
  question?: string
  resolutionType?: string
  resolutionTarget?: string
  resolutionTargetHigh?: string
  closeDate?: string
  endDate?: string
  minBetQu?: string
  maxSlots?: string
  creatorAddress?: string
}

export function CreateMarketForm() {
  const router = useRouter()
  const routeParams = useParams()
  const locale = (routeParams?.locale as string) ?? 'en'

  const [pair, setPair] = React.useState('')
  const [question, setQuestion] = React.useState('')
  const [resolutionType, setResolutionType] =
    React.useState<ResolutionType>('price_above')
  const [resolutionTarget, setResolutionTarget] = React.useState('')
  const [resolutionTargetHigh, setResolutionTargetHigh] = React.useState('')
  const [closeDate, setCloseDate] = React.useState('')
  const [endDate, setEndDate] = React.useState('')
  const [minBetQu, setMinBetQu] = React.useState('10000')
  const [maxSlots, setMaxSlots] = React.useState('100')
  const [creatorAddress, setCreatorAddress] = React.useState('')

  const [state, setState] = React.useState<FormState>('idle')
  const [errors, setErrors] = React.useState<FormErrors>({})
  const [serverError, setServerError] = React.useState('')
  const [createdMarketId, setCreatedMarketId] = React.useState('')

  function validate(): boolean {
    const errs: FormErrors = {}

    if (!pair) errs.pair = 'Select a trading pair'
    if (!question || question.length < 10)
      errs.question = 'Question must be at least 10 characters'
    if (question.length > 100)
      errs.question = 'Question must be at most 100 characters'

    const target = parseFloat(resolutionTarget)
    if (isNaN(target) || target <= 0)
      errs.resolutionTarget = 'Enter a positive target price'

    if (resolutionType === 'price_range' || resolutionType === 'price_bracket') {
      const high = parseFloat(resolutionTargetHigh)
      if (isNaN(high) || high <= target)
        errs.resolutionTargetHigh =
          'High target must be greater than the target price'
    }

    if (!closeDate) errs.closeDate = 'Select a close date'
    else if (new Date(closeDate) <= new Date())
      errs.closeDate = 'Close date must be in the future'

    if (!endDate) errs.endDate = 'Select an end date'
    else if (closeDate && new Date(endDate) <= new Date(closeDate))
      errs.endDate = 'End date must be after close date'

    const minBet = parseInt(minBetQu, 10)
    if (isNaN(minBet) || minBet < 100)
      errs.minBetQu = 'Minimum bet must be at least 100 QU'

    const maxS = parseInt(maxSlots, 10)
    if (isNaN(maxS) || maxS < 2 || maxS > 15000)
      errs.maxSlots = 'Max slots must be between 2 and 15,000'

    if (
      !creatorAddress ||
      creatorAddress.length !== 60 ||
      !/^[A-Z]+$/.test(creatorAddress)
    )
      errs.creatorAddress =
        'Enter a valid 60-character uppercase Qubic address'

    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setServerError('')

    if (!validate()) return

    setState('loading')

    try {
      const payload: CreateMarketPayload = {
        pair,
        question,
        resolutionType,
        resolutionTarget: parseFloat(resolutionTarget),
        closeDate: new Date(closeDate).toISOString(),
        endDate: new Date(endDate).toISOString(),
        minBetQu: parseInt(minBetQu, 10),
        maxSlots: parseInt(maxSlots, 10),
        creatorAddress,
        marketType: 'price',
        options: ['Yes', 'No'],
        oracleFeeBps: 0,
      }

      if (resolutionType === 'price_range' || resolutionType === 'price_bracket') {
        payload.resolutionTargetHigh = parseFloat(resolutionTargetHigh)
      }

      const res = await fetch('/api/predict/markets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()

      if (!res.ok || !data.success) {
        setServerError(data.error ?? 'Failed to create market')
        setState('error')
        return
      }

      setCreatedMarketId(data.market?.id ?? '')
      setState('success')
    } catch (err) {
      setServerError(err instanceof Error ? err.message : 'Network error')
      setState('error')
    }
  }

  if (state === 'success') {
    return (
      <div className="rounded-lg border bg-card p-8">
        <div className="flex flex-col items-center gap-4 py-6 text-center">
          <CheckCircle2 className="h-14 w-14 text-emerald-400" />
          <h3 className="text-xl font-semibold text-foreground">
            Market Created
          </h3>
          <p className="max-w-md text-sm text-muted-foreground">
            Your prediction market has been deployed. It may take a moment for
            the on-chain transaction to confirm.
          </p>
          <div className="flex gap-3">
            {createdMarketId && (
              <Button
                onClick={() =>
                  router.push(`/${locale}/predict/${createdMarketId}`)
                }
              >
                View Market
              </Button>
            )}
            <Button variant="outline" onClick={() => router.push(`/${locale}/predict`)}>
              Back to Markets
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Trading Pair */}
      <div>
        <label className="mb-1.5 block text-sm font-medium text-foreground">
          Trading Pair
        </label>
        <Select value={pair} onValueChange={setPair}>
          <SelectTrigger>
            <SelectValue placeholder="Select pair..." />
          </SelectTrigger>
          <SelectContent>
            {SUPPORTED_PAIRS.map((p) => (
              <SelectItem key={p} value={p}>
                {pairLabel(p)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.pair && (
          <p className="mt-1 text-xs text-red-400">{errors.pair}</p>
        )}
      </div>

      {/* Question */}
      <div>
        <label className="mb-1.5 block text-sm font-medium text-foreground">
          Market Question
        </label>
        <Input
          type="text"
          placeholder="Will BTC be above $100,000 by March 1st?"
          maxLength={100}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <div className="mt-1 flex items-center justify-between">
          {errors.question ? (
            <p className="text-xs text-red-400">{errors.question}</p>
          ) : (
            <span />
          )}
          <span className="text-xs text-muted-foreground">
            {question.length}/100
          </span>
        </div>
      </div>

      {/* Resolution Type */}
      <div>
        <label className="mb-1.5 block text-sm font-medium text-foreground">
          Resolution Type
        </label>
        <Select
          value={resolutionType}
          onValueChange={(v) => setResolutionType(v as ResolutionType)}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {(Object.keys(RESOLUTION_TYPE_LABELS) as ResolutionType[]).map(
              (rt) => (
                <SelectItem key={rt} value={rt}>
                  {RESOLUTION_TYPE_LABELS[rt]}
                </SelectItem>
              ),
            )}
          </SelectContent>
        </Select>
        {errors.resolutionType && (
          <p className="mt-1 text-xs text-red-400">{errors.resolutionType}</p>
        )}
      </div>

      {/* Target Price(s) */}
      <div
        className={cn(
          'grid gap-4',
          resolutionType === 'price_range' || resolutionType === 'price_bracket'
            ? 'grid-cols-2'
            : 'grid-cols-1',
        )}
      >
        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground">
            {resolutionType === 'price_range' || resolutionType === 'price_bracket'
              ? 'Lower Target Price'
              : 'Target Price'}
          </label>
          <Input
            type="number"
            step="any"
            min="0"
            placeholder="70000"
            value={resolutionTarget}
            onChange={(e) => setResolutionTarget(e.target.value)}
          />
          {errors.resolutionTarget && (
            <p className="mt-1 text-xs text-red-400">
              {errors.resolutionTarget}
            </p>
          )}
        </div>

        {(resolutionType === 'price_range' || resolutionType === 'price_bracket') && (
          <div>
            <label className="mb-1.5 block text-sm font-medium text-foreground">
              Upper Target Price
            </label>
            <Input
              type="number"
              step="any"
              min="0"
              placeholder="75000"
              value={resolutionTargetHigh}
              onChange={(e) => setResolutionTargetHigh(e.target.value)}
            />
            {errors.resolutionTargetHigh && (
              <p className="mt-1 text-xs text-red-400">
                {errors.resolutionTargetHigh}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Dates */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground">
            Betting Closes
          </label>
          <Input
            type="datetime-local"
            value={closeDate}
            onChange={(e) => setCloseDate(e.target.value)}
          />
          <p className="mt-1 text-xs text-muted-foreground">
            No more bets after this time
          </p>
          {errors.closeDate && (
            <p className="mt-1 text-xs text-red-400">{errors.closeDate}</p>
          )}
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground">
            Resolution Date
          </label>
          <Input
            type="datetime-local"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
          <p className="mt-1 text-xs text-muted-foreground">
            Market resolves at this time
          </p>
          {errors.endDate && (
            <p className="mt-1 text-xs text-red-400">{errors.endDate}</p>
          )}
        </div>
      </div>

      {/* Bet Limits */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground">
            Minimum Bet (QU per slot)
          </label>
          <Input
            type="number"
            min="100"
            value={minBetQu}
            onChange={(e) => setMinBetQu(e.target.value)}
          />
          {errors.minBetQu && (
            <p className="mt-1 text-xs text-red-400">{errors.minBetQu}</p>
          )}
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground">
            Max Slots per Option
          </label>
          <Input
            type="number"
            min="2"
            max="15000"
            value={maxSlots}
            onChange={(e) => setMaxSlots(e.target.value)}
          />
          {errors.maxSlots && (
            <p className="mt-1 text-xs text-red-400">{errors.maxSlots}</p>
          )}
        </div>
      </div>

      {/* Creator Address */}
      <div>
        <label className="mb-1.5 block text-sm font-medium text-foreground">
          Creator Address
        </label>
        <Input
          type="text"
          placeholder="ABCDEFGHIJ..."
          maxLength={60}
          value={creatorAddress}
          onChange={(e) => setCreatorAddress(e.target.value.toUpperCase())}
          className="font-mono text-xs"
        />
        {errors.creatorAddress && (
          <p className="mt-1 text-xs text-red-400">{errors.creatorAddress}</p>
        )}
      </div>

      {/* Info Box */}
      <div className="flex items-start gap-2 rounded-md border border-blue-500/30 bg-blue-500/5 p-3">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-blue-400" />
        <div className="text-xs text-blue-400/90">
          <p>
            Creating a market deploys a Quottery bet on-chain.
            The Qubic SC charges a 12.5% fee on the <strong>losing side&apos;s pool</strong> (2% burn +
            10% shareholders + 0.5% game operator). Winners get their full stake back plus the remaining loser pool. <strong>QPredict takes 0% oracle fee.</strong>
          </p>
        </div>
      </div>

      {/* Server Error */}
      {state === 'error' && serverError && (
        <div className="flex items-start gap-2 rounded-md border border-red-500/30 bg-red-500/10 p-3">
          <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
          <p className="text-xs text-red-400">{serverError}</p>
        </div>
      )}

      {/* Submit */}
      <Button type="submit" className="w-full" disabled={state === 'loading'}>
        {state === 'loading' ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Creating Market...
          </>
        ) : (
          'Create Market'
        )}
      </Button>
    </form>
  )
}
