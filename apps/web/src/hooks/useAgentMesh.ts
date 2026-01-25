/**
 * USE AGENT MESH
 *
 * React hook for the Ternary Agent System.
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { AgentMesh, type TernaryAgent } from '@/lib/agents'
import type {
  AgentType,
  AgentResult,
  PipelineResult,
  MeshState,
} from '@/lib/agents/types'

interface UseAgentMeshReturn {
  isReady: boolean
  isLoading: boolean
  isProcessing: boolean
  error: string | null
  meshState: MeshState | null
  lastResult: PipelineResult | null
  loadMatrix: () => Promise<void>
  spawn: (type: AgentType) => TernaryAgent | null
  process: (type: AgentType, input: string) => AgentResult | null
  runPipeline: (input: string) => PipelineResult | null
  streamPipeline: (
    input: string,
    onTick?: (stage: number, tick: number, energy: number) => void
  ) => void
  cancel: () => void
  reset: () => void
}

/**
 * Hook for using the Ternary Agent Mesh
 */
export function useAgentMesh(): UseAgentMeshReturn {
  const [isReady, setIsReady] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [meshState, setMeshState] = useState<MeshState | null>(null)
  const [lastResult, setLastResult] = useState<PipelineResult | null>(null)

  const meshRef = useRef<AgentMesh | null>(null)
  const cancelRef = useRef<(() => void) | null>(null)

  /**
   * Load the Anna Matrix
   */
  const loadMatrix = useCallback(async () => {
    if (isLoading || isReady) return

    setIsLoading(true)
    setError(null)

    try {
      const res = await fetch('/data/anna-matrix.json')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const data = await res.json()
      let matrix: number[][]

      // Handle {matrix: [...]} or direct array format
      const rawMatrix = data.matrix ?? data

      if (Array.isArray(rawMatrix) && Array.isArray(rawMatrix[0])) {
        matrix = rawMatrix
      } else if (Array.isArray(rawMatrix)) {
        matrix = []
        for (let i = 0; i < 128; i++) {
          matrix.push(rawMatrix.slice(i * 128, (i + 1) * 128))
        }
      } else {
        throw new Error('Invalid format')
      }

      meshRef.current = new AgentMesh(matrix)
      setIsReady(true)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Load failed')
    } finally {
      setIsLoading(false)
    }
  }, [isLoading, isReady])

  /**
   * Auto-load on mount
   */
  useEffect(() => {
    loadMatrix()
    return () => {
      cancelRef.current?.()
    }
  }, [loadMatrix])

  /**
   * Spawn an agent
   */
  const spawn = useCallback((type: AgentType): TernaryAgent | null => {
    if (!meshRef.current) {
      setError('Not ready')
      return null
    }
    const agent = meshRef.current.spawn(type)
    setMeshState(meshRef.current.getState())
    return agent
  }, [])

  /**
   * Process with single agent
   */
  const process = useCallback(
    (type: AgentType, input: string): AgentResult | null => {
      if (!meshRef.current) {
        setError('Not ready')
        return null
      }
      setIsProcessing(true)
      try {
        const result = meshRef.current.processWithAgent(type, input)
        setMeshState(meshRef.current.getState())
        return result
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed')
        return null
      } finally {
        setIsProcessing(false)
      }
    },
    []
  )

  /**
   * Run full pipeline (sync)
   */
  const runPipeline = useCallback((input: string): PipelineResult | null => {
    if (!meshRef.current) {
      setError('Not ready')
      return null
    }
    setIsProcessing(true)
    try {
      const result = meshRef.current.processPipeline(input)
      setLastResult(result)
      setMeshState(meshRef.current.getState())
      return result
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed')
      return null
    } finally {
      setIsProcessing(false)
    }
  }, [])

  /**
   * Stream pipeline with tick updates
   */
  const streamPipeline = useCallback(
    (
      input: string,
      onTick?: (stage: number, tick: number, energy: number) => void
    ) => {
      if (!meshRef.current) {
        setError('Not ready')
        return
      }

      setIsProcessing(true)
      setError(null)

      cancelRef.current = meshRef.current.streamPipeline(
        input,
        () => setMeshState(meshRef.current?.getState() ?? null),
        (stage, tick, energy) => {
          onTick?.(stage, tick, energy)
          if (tick % 5 === 0) setMeshState(meshRef.current?.getState() ?? null)
        },
        () => setMeshState(meshRef.current?.getState() ?? null),
        result => {
          setLastResult(result)
          setMeshState(meshRef.current?.getState() ?? null)
          setIsProcessing(false)
          cancelRef.current = null
        }
      )
    },
    []
  )

  /**
   * Cancel processing
   */
  const cancel = useCallback(() => {
    cancelRef.current?.()
    cancelRef.current = null
    setIsProcessing(false)
  }, [])

  /**
   * Reset mesh
   */
  const reset = useCallback(() => {
    cancel()
    meshRef.current?.reset()
    setMeshState(meshRef.current?.getState() ?? null)
    setLastResult(null)
    setError(null)
  }, [cancel])

  return {
    isReady,
    isLoading,
    isProcessing,
    error,
    meshState,
    lastResult,
    loadMatrix,
    spawn,
    process,
    runPipeline,
    streamPipeline,
    cancel,
    reset,
  }
}
