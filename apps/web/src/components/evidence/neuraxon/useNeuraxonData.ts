'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import type { NeuraxonData, NeuraxonNode, NeuraxonEdge, NeuraxonFrame } from './types'

// Error types for better error handling
export type NeuraxonErrorType =
  | 'NETWORK_ERROR'
  | 'PARSE_ERROR'
  | 'VALIDATION_ERROR'
  | 'TIMEOUT_ERROR'
  | 'UNKNOWN_ERROR'

export interface NeuraxonError {
  type: NeuraxonErrorType
  message: string
  details?: string
  retryable: boolean
}

interface UseNeuraxonDataReturn {
  loading: boolean
  error: NeuraxonError | null
  data: NeuraxonData | null
  currentFrame: NeuraxonFrame | null
  currentNodes: NeuraxonNode[]
  currentEdges: NeuraxonEdge[]
  frameIndex: number
  setFrameIndex: (index: number) => void
  totalFrames: number
  searchNode: (query: string) => NeuraxonNode | null
  getNodeById: (id: number) => NeuraxonNode | undefined
  getConnectedNodes: (nodeId: number) => { incoming: NeuraxonEdge[]; outgoing: NeuraxonEdge[] }
  retry: () => void
  retryCount: number
}

const FETCH_TIMEOUT = 30000 // 30 seconds
const MAX_RETRIES = 3

// Validate the data structure
function validateNeuraxonData(data: unknown): data is NeuraxonData {
  if (!data || typeof data !== 'object') return false

  const d = data as Record<string, unknown>

  // Check required fields
  if (!Array.isArray(d.nodes) || d.nodes.length === 0) return false
  if (!Array.isArray(d.edges)) return false
  if (!Array.isArray(d.frames) || d.frames.length === 0) return false
  if (!d.metadata || typeof d.metadata !== 'object') return false

  // Validate first node structure
  const firstNode = d.nodes[0] as Record<string, unknown>
  if (
    typeof firstNode.id !== 'number' ||
    typeof firstNode.seed !== 'string' ||
    typeof firstNode.realId !== 'string' ||
    !Array.isArray(firstNode.position)
  ) {
    return false
  }

  return true
}

export function useNeuraxonData(): UseNeuraxonDataReturn {
  const [data, setData] = useState<NeuraxonData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<NeuraxonError | null>(null)
  const [frameIndex, setFrameIndex] = useState(0)
  const [retryCount, setRetryCount] = useState(0)

  // Fetch with timeout
  const fetchWithTimeout = useCallback(async (url: string, timeout: number): Promise<Response> => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      const response = await fetch(url, { signal: controller.signal })
      clearTimeout(timeoutId)
      return response
    } catch (err) {
      clearTimeout(timeoutId)
      throw err
    }
  }, [])

  // Load data with error handling
  const loadData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      // Fetch with timeout
      const response = await fetchWithTimeout('/data/neuraxon-network.json', FETCH_TIMEOUT)

      // Check HTTP status
      if (!response.ok) {
        if (response.status === 404) {
          throw {
            type: 'NETWORK_ERROR' as NeuraxonErrorType,
            message: 'Neural network data not found',
            details: 'The neuraxon-network.json file could not be located. Please ensure the data has been generated.',
            retryable: false,
          }
        }
        throw {
          type: 'NETWORK_ERROR' as NeuraxonErrorType,
          message: `Server error: ${response.status}`,
          details: response.statusText,
          retryable: response.status >= 500,
        }
      }

      // Parse JSON
      let json: unknown
      try {
        json = await response.json()
      } catch {
        throw {
          type: 'PARSE_ERROR' as NeuraxonErrorType,
          message: 'Failed to parse network data',
          details: 'The data file appears to be corrupted or malformed.',
          retryable: false,
        }
      }

      // Validate data structure
      if (!validateNeuraxonData(json)) {
        throw {
          type: 'VALIDATION_ERROR' as NeuraxonErrorType,
          message: 'Invalid network data structure',
          details: 'The data file does not contain the expected neural network structure.',
          retryable: false,
        }
      }

      setData(json)
      setLoading(false)
      setError(null)

    } catch (err) {
      setLoading(false)

      // Handle abort (timeout)
      if (err instanceof Error && err.name === 'AbortError') {
        setError({
          type: 'TIMEOUT_ERROR',
          message: 'Loading timed out',
          details: 'The network data took too long to load. Please check your connection and try again.',
          retryable: true,
        })
        return
      }

      // Handle known error types
      if (err && typeof err === 'object' && 'type' in err) {
        setError(err as NeuraxonError)
        return
      }

      // Handle network errors
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError({
          type: 'NETWORK_ERROR',
          message: 'Network connection failed',
          details: 'Unable to connect to the server. Please check your internet connection.',
          retryable: true,
        })
        return
      }

      // Unknown error
      setError({
        type: 'UNKNOWN_ERROR',
        message: 'An unexpected error occurred',
        details: err instanceof Error ? err.message : 'Unknown error',
        retryable: true,
      })
    }
  }, [fetchWithTimeout])

  // Initial load
  useEffect(() => {
    loadData()
  }, [loadData])

  // Retry function
  const retry = useCallback(() => {
    if (retryCount < MAX_RETRIES) {
      setRetryCount((c) => c + 1)
      loadData()
    }
  }, [retryCount, loadData])

  // Current frame
  const currentFrame = useMemo(() => {
    if (!data) return null
    return data.frames[frameIndex] || null
  }, [data, frameIndex])

  // Nodes for current frame
  const currentNodes = useMemo(() => {
    if (!data || !currentFrame) return []
    return currentFrame.nodeIds
      .map((id) => data.nodes[id])
      .filter((node): node is NeuraxonNode => node !== undefined)
  }, [data, currentFrame])

  // Edges for current frame (both endpoints must be in frame)
  const currentEdges = useMemo(() => {
    if (!data || !currentFrame) return []
    const nodeIdSet = new Set(currentFrame.nodeIds)
    return data.edges.filter(
      (edge) => nodeIdSet.has(edge.source) && nodeIdSet.has(edge.target)
    )
  }, [data, currentFrame])

  // Search for a node by seed or realId
  const searchNode = useCallback((query: string): NeuraxonNode | null => {
    if (!data) return null
    const queryLower = query.toLowerCase().trim()
    if (!queryLower) return null

    // Try exact ID match first
    const numericId = parseInt(queryLower, 10)
    if (!isNaN(numericId) && data.nodes[numericId]) {
      return data.nodes[numericId]
    }

    // Search by seed or realId
    return (
      data.nodes.find(
        (node) =>
          node.seed.toLowerCase().includes(queryLower) ||
          node.realId.toLowerCase().includes(queryLower)
      ) || null
    )
  }, [data])

  // Get node by ID with bounds checking
  const getNodeById = useCallback((id: number): NeuraxonNode | undefined => {
    if (!data || id < 0 || id >= data.nodes.length) return undefined
    return data.nodes[id]
  }, [data])

  // Get connected nodes
  const getConnectedNodes = useCallback((
    nodeId: number
  ): { incoming: NeuraxonEdge[]; outgoing: NeuraxonEdge[] } => {
    if (!data) return { incoming: [], outgoing: [] }

    const incoming = data.edges.filter((e) => e.target === nodeId)
    const outgoing = data.edges.filter((e) => e.source === nodeId)

    return { incoming, outgoing }
  }, [data])

  // Safe setFrameIndex with bounds checking
  const safeSetFrameIndex = useCallback((index: number) => {
    if (!data) return
    const clampedIndex = Math.max(0, Math.min(index, data.frames.length - 1))
    setFrameIndex(clampedIndex)
  }, [data])

  return {
    loading,
    error,
    data,
    currentFrame,
    currentNodes,
    currentEdges,
    frameIndex,
    setFrameIndex: safeSetFrameIndex,
    totalFrames: data?.frames.length || 0,
    searchNode,
    getNodeById,
    getConnectedNodes,
    retry,
    retryCount,
  }
}
