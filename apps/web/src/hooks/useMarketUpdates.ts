'use client'

import { useState, useEffect, useCallback } from 'react'

interface Participant {
  address: string
  fullAddress: string
  option: number
  optionLabel: string
  slots: number
  amountQu: number
  status: string
  escrowAddress: string
  joinBetTxId: string | null
  timestamp: string
}

interface OptionStat {
  option: number
  label: string
  totalSlots: number
  totalQu: number
  participants: number
}

interface MarketUpdates {
  participants: Participant[]
  optionStats: OptionStat[]
  totalPool: number
  isLoading: boolean
  error: string | null
  refresh: () => Promise<void>
}

export function useMarketUpdates(marketId: string, interval = 10000): MarketUpdates {
  const [participants, setParticipants] = useState<Participant[]>([])
  const [optionStats, setOptionStats] = useState<OptionStat[]>([])
  const [totalPool, setTotalPool] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      const res = await fetch(`/api/predict/markets/${encodeURIComponent(marketId)}/participants`)
      if (!res.ok) throw new Error('Failed to fetch participants')
      const data = await res.json()
      setParticipants(data.participants ?? [])
      setOptionStats(data.optionStats ?? [])
      setTotalPool(data.totalPool ?? 0)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load')
    } finally {
      setIsLoading(false)
    }
  }, [marketId])

  useEffect(() => {
    refresh()
    const timer = setInterval(refresh, interval)
    return () => clearInterval(timer)
  }, [refresh, interval])

  return { participants, optionStats, totalPool, isLoading, error, refresh }
}
