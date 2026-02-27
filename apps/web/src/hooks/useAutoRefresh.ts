'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

/**
 * Visibility-aware polling hook for QPredict.
 *
 * - Fetches data on mount and at a configurable interval.
 * - Pauses polling when the browser tab is hidden (visibilitychange).
 * - Resumes with an immediate fetch when the tab becomes visible again.
 * - Only shows loading state on the initial fetch, not on subsequent refreshes.
 * - Resets when `deps` change.
 * - Provides a manual `refresh()` trigger.
 */
export function useAutoRefresh<T>(
  fetcher: () => Promise<T>,
  intervalMs: number = 15_000,
  deps: unknown[] = [],
): {
  data: T | null
  isLoading: boolean
  error: Error | null
  refresh: () => void
  lastUpdated: Date | null
} {
  const [data, setData] = useState<T | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  // Keep a ref to the fetcher so we always call the latest version
  // without needing it in the effect dependency array.
  const fetcherRef = useRef(fetcher)
  fetcherRef.current = fetcher

  // Track whether the initial fetch has completed so we can skip
  // setting isLoading on subsequent polls.
  const hasLoadedRef = useRef(false)

  // Track the interval id so we can clear/restart it.
  const intervalIdRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const doFetch = useCallback(async (isInitial: boolean) => {
    if (isInitial) {
      setIsLoading(true)
    }

    try {
      const result = await fetcherRef.current()
      setData(result)
      setError(null)
      setLastUpdated(new Date())
      hasLoadedRef.current = true
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)))
    } finally {
      if (isInitial) {
        setIsLoading(false)
      }
    }
  }, [])

  // Manual refresh — always immediate, never shows loading spinner.
  const refresh = useCallback(() => {
    doFetch(false)
  }, [doFetch])

  useEffect(() => {
    // Reset state when deps change.
    hasLoadedRef.current = false
    setData(null)
    setError(null)
    setLastUpdated(null)

    // Initial fetch.
    doFetch(true)

    // Start polling interval.
    const startInterval = () => {
      // Clear any existing interval first.
      if (intervalIdRef.current !== null) {
        clearInterval(intervalIdRef.current)
      }
      intervalIdRef.current = setInterval(() => {
        doFetch(false)
      }, intervalMs)
    }

    startInterval()

    // Visibility change handler: pause when hidden, resume when visible.
    const handleVisibility = () => {
      if (document.visibilityState === 'hidden') {
        // Pause polling.
        if (intervalIdRef.current !== null) {
          clearInterval(intervalIdRef.current)
          intervalIdRef.current = null
        }
      } else {
        // Tab is visible again — fetch immediately and restart interval.
        doFetch(false)
        startInterval()
      }
    }

    document.addEventListener('visibilitychange', handleVisibility)

    return () => {
      document.removeEventListener('visibilitychange', handleVisibility)
      if (intervalIdRef.current !== null) {
        clearInterval(intervalIdRef.current)
        intervalIdRef.current = null
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [intervalMs, doFetch, ...deps])

  return { data, isLoading, error, refresh, lastUpdated }
}
