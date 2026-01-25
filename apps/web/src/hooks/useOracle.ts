/**
 * USE ORACLE
 *
 * React hook for the Matrix Oracle.
 * Provides deterministic, verifiable answers from matrix data.
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { MatrixOracle, type OracleResult } from '@/lib/agents/oracle'

interface UseOracleReturn {
  isReady: boolean
  isLoading: boolean
  isQuerying: boolean
  error: string | null
  lastResult: OracleResult | null
  patterns: Array<{ pattern: string; found: boolean; value: number | null }>
  query: (input: string) => Promise<OracleResult | null>
  verify: (result: OracleResult) => Promise<boolean>
  checkPatterns: () => void
}

export function useOracle(): UseOracleReturn {
  const [isReady, setIsReady] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isQuerying, setIsQuerying] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastResult, setLastResult] = useState<OracleResult | null>(null)
  const [patterns, setPatterns] = useState<
    Array<{ pattern: string; found: boolean; value: number | null }>
  >([])

  const oracleRef = useRef<MatrixOracle | null>(null)

  // Initialize oracle on mount
  useEffect(() => {
    const init = async () => {
      if (isLoading || isReady) return

      setIsLoading(true)
      setError(null)

      try {
        const oracle = new MatrixOracle()
        await oracle.loadMatrix()
        oracleRef.current = oracle
        setIsReady(true)

        // Check patterns on init
        setPatterns(oracle.checkKnownPatterns())
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load oracle')
      } finally {
        setIsLoading(false)
      }
    }

    init()
  }, [isLoading, isReady])

  const query = useCallback(
    async (input: string): Promise<OracleResult | null> => {
      if (!oracleRef.current) {
        setError('Oracle not ready')
        return null
      }

      setIsQuerying(true)
      setError(null)

      try {
        const result = await oracleRef.current.query(input)
        setLastResult(result)
        return result
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Query failed')
        return null
      } finally {
        setIsQuerying(false)
      }
    },
    []
  )

  const verify = useCallback(async (result: OracleResult): Promise<boolean> => {
    if (!oracleRef.current) {
      setError('Oracle not ready')
      return false
    }

    try {
      return await oracleRef.current.verify(result)
    } catch {
      return false
    }
  }, [])

  const checkPatterns = useCallback(() => {
    if (!oracleRef.current) return
    setPatterns(oracleRef.current.checkKnownPatterns())
  }, [])

  return {
    isReady,
    isLoading,
    isQuerying,
    error,
    lastResult,
    patterns,
    query,
    verify,
    checkPatterns,
  }
}
