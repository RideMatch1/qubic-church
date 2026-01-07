'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import type {
  AddressNode,
  AddressEdge,
  AddressGraphData,
  AddressGraphError,
  NetworkStats,
  LoadStats,
  RawPatoshiAddress,
  RawInterestingAddress,
  RawQubicSeed,
  RawBitcoinDerived,
  AddressType,
} from './types'
import { DATA_URLS, NODE_TYPE_CONFIG, XOR_RING_CONFIG } from './constants'
import { pubkeyToAddress } from './addressUtils'

// =============================================================================
// RAW MATRIX ADDRESS TYPE
// =============================================================================

interface RawMatrixAddress {
  id: number
  address: string
}

// =============================================================================
// HOOK: useAddressGraphData
// =============================================================================

interface UseAddressGraphDataReturn {
  loading: boolean
  progress: number
  loadStats: LoadStats
  error: AddressGraphError | null
  data: AddressGraphData | null
  retry: () => void
  retryCount: number

  // Helpers
  getNodeById: (id: string) => AddressNode | undefined
  getConnectedNodes: (nodeId: string) => { incoming: AddressEdge[]; outgoing: AddressEdge[] }
  searchNode: (query: string) => AddressNode | null
}

// Smart sampling function - select evenly distributed samples
function smartSample<T>(arr: T[], maxCount: number): T[] {
  if (arr.length <= maxCount) return arr
  const step = arr.length / maxCount
  const result: T[] = []
  for (let i = 0; i < maxCount; i++) {
    const item = arr[Math.floor(i * step)]
    if (item !== undefined) result.push(item)
  }
  return result
}

export function useAddressGraphData(): UseAddressGraphDataReturn {
  const [loading, setLoading] = useState(true)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<AddressGraphError | null>(null)
  const [data, setData] = useState<AddressGraphData | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  const [loadStats, setLoadStats] = useState<LoadStats>({
    patoshi: 0,
    cfbLinked: 0,
    matrixDerived: 0,
    totalEdges: 0,
  })

  // Load all data
  const loadData = useCallback(async () => {
    setLoading(true)
    setProgress(0)
    setError(null)

    try {
      // Phase 1: Load interesting addresses (VIP nodes) - 10%
      setProgress(5)
      const interestingRes = await fetch(DATA_URLS.interesting)
      if (!interestingRes.ok) throw new Error('Failed to load interesting addresses')
      const interestingJson = await interestingRes.json()
      const interestingAddresses: RawInterestingAddress[] = interestingJson.records || []
      setProgress(10)

      // Phase 2: Load patoshi addresses - 30%
      setProgress(15)
      const patoshiRes = await fetch(DATA_URLS.patoshi)
      if (!patoshiRes.ok) throw new Error('Failed to load patoshi addresses')
      const patoshiJson = await patoshiRes.json()
      const patoshiAddresses: RawPatoshiAddress[] = patoshiJson.records || []
      setProgress(30)

      // Phase 3: Load matrix addresses (983k) - 60%
      setProgress(35)
      const matrixRes = await fetch(DATA_URLS.matrix)
      if (!matrixRes.ok) throw new Error('Failed to load matrix addresses')
      const matrixJson = await matrixRes.json()
      const matrixAddresses: RawMatrixAddress[] = matrixJson.records || matrixJson || []
      setProgress(60)

      // Phase 4: Load qubic seeds - 70%
      setProgress(65)
      const seedsRes = await fetch(DATA_URLS.qubicSeeds)
      if (!seedsRes.ok) throw new Error('Failed to load qubic seeds')
      const seedsJson = await seedsRes.json()
      const qubicSeeds: RawQubicSeed[] = seedsJson.records || []
      setProgress(70)

      // Update load stats with FULL counts
      setLoadStats({
        patoshi: patoshiAddresses.length,
        cfbLinked: interestingAddresses.length,
        matrixDerived: matrixAddresses.length,
        totalEdges: 0, // Will be updated later
      })

      // Phase 5: Process data into nodes - 90%
      setProgress(75)

      const nodes: AddressNode[] = []
      const nodeMap = new Map<string, AddressNode>()
      const vipNodes: AddressNode[] = []

      // Process VIP nodes first (interesting addresses) - ALL 30
      interestingAddresses.forEach((addr) => {
        const isCFB = addr.address.startsWith('1CFB')
        const isPat = addr.address.startsWith('1Pat')
        const type: AddressType = isCFB ? 'cfb-vanity' : isPat ? 'patoshi-vanity' : 'matrix-derived'
        const config = NODE_TYPE_CONFIG[type]
        const xorConfig = XOR_RING_CONFIG[addr.xor] || XOR_RING_CONFIG[0]

        const node: AddressNode = {
          id: addr.address,
          address: addr.address,
          type,
          position: [
            (addr.position[0] - 64) * 0.5,
            0,
            (addr.position[1] - 64) * 0.5,
          ],
          color: config.color,
          shape: config.shape,
          size: config.size,
          glowIntensity: config.glow,
          xorRings: xorConfig?.rings ?? 1,
          matrixPosition: addr.position,
          derivationMethod: addr.method as any,
          xorVariant: addr.xor,
          compressed: addr.compressed,
          hash160: addr.hash160,
          state: 'default',
          isVIP: true,
        }

        nodes.push(node)
        nodeMap.set(addr.address, node)
        vipNodes.push(node)
      })

      // Process ALL patoshi addresses (21,953) - with smart positioning
      // First, compute all Bitcoin addresses in parallel (batch of 100 at a time for performance)
      const BATCH_SIZE = 500
      const patoshiWithAddresses: Array<{ raw: RawPatoshiAddress; derivedAddress: string }> = []

      for (let i = 0; i < patoshiAddresses.length; i += BATCH_SIZE) {
        const batch = patoshiAddresses.slice(i, i + BATCH_SIZE)
        const addresses = await Promise.all(
          batch.map(async (addr) => {
            try {
              const derivedAddress = await pubkeyToAddress(addr.pubkey)
              return { raw: addr, derivedAddress }
            } catch {
              // Fallback if address computation fails
              return { raw: addr, derivedAddress: `[Invalid pubkey]` }
            }
          })
        )
        patoshiWithAddresses.push(...addresses)

        // Update progress during address computation
        const progressPercent = 75 + (i / patoshiAddresses.length) * 8
        setProgress(Math.min(83, progressPercent))
      }

      // Now create nodes with the computed addresses
      patoshiWithAddresses.forEach(({ raw: addr, derivedAddress }, idx) => {
        const addressId = `patoshi-${addr.blockHeight}-${idx}`
        const isGenesis = addr.blockHeight <= 100
        const type: AddressType = isGenesis ? 'patoshi-genesis' : 'patoshi'
        const config = NODE_TYPE_CONFIG[type]

        // Spiral positioning based on block height for visual timeline
        const normalizedBlock = addr.blockHeight / 50000 // Normalize to 0-1
        const angle = normalizedBlock * Math.PI * 20 // 10 full rotations
        const radius = 10 + normalizedBlock * 30 // Expanding spiral
        const height = addr.blockHeight / 2000 // Y = time

        const node: AddressNode = {
          id: addressId,
          address: derivedAddress, // Use the derived Bitcoin address
          type,
          position: [
            Math.cos(angle) * radius,
            height,
            Math.sin(angle) * radius,
          ],
          color: config.color,
          shape: config.shape,
          size: config.size,
          glowIntensity: config.glow,
          xorRings: 0,
          blockHeight: addr.blockHeight,
          amount: addr.amount,
          scriptType: addr.scriptType,
          pubkey: addr.pubkey,
          derivedAddress, // Store the derived address explicitly
          state: 'default',
          isVIP: isGenesis,
        }

        nodes.push(node)
        nodeMap.set(addressId, node)
        if (isGenesis) vipNodes.push(node)
      })

      setProgress(85)

      // Process matrix addresses - SMART SAMPLE for performance
      // Sample 10,000 addresses from 983,040 to represent the full dataset
      const MATRIX_SAMPLE_SIZE = 10000
      const sampledMatrix = smartSample(matrixAddresses, MATRIX_SAMPLE_SIZE)

      sampledMatrix.forEach((addr, idx) => {
        if (nodeMap.has(addr.address)) return

        const config = NODE_TYPE_CONFIG['matrix-derived']

        // Position in a grid/ring pattern around the center
        // 128x128 matrix = positions 0-16383
        const matrixX = addr.id % 128
        const matrixY = Math.floor(addr.id / 128)

        // Map to 3D position - flat grid on XZ plane
        const scale = 0.4
        const x = (matrixX - 64) * scale
        const z = (matrixY - 64) * scale
        // Deterministic Y offset based on address ID (consistent across reloads)
        const yOffset = ((addr.id * 7919) % 1000) / 2000 // Small deterministic variation
        const y = -5 + yOffset // Slightly below patoshi spiral

        const node: AddressNode = {
          id: addr.address,
          address: addr.address,
          type: 'matrix-derived',
          position: [x, y, z],
          color: config.color,
          shape: config.shape,
          size: 'xs', // Small since there are many
          glowIntensity: 0.1,
          xorRings: 0,
          matrixPosition: [matrixX, matrixY],
          state: 'default',
          isVIP: false,
        }

        nodes.push(node)
        nodeMap.set(addr.address, node)
      })

      // Create edges based on relationships
      const edges: AddressEdge[] = []

      // Temporal edges between consecutive patoshi blocks
      const patoshiNodes = nodes.filter((n) => n.type === 'patoshi' || n.type === 'patoshi-genesis')
      patoshiNodes.sort((a, b) => (a.blockHeight || 0) - (b.blockHeight || 0))

      // Sample edges for performance - every 10th connection
      for (let i = 0; i < patoshiNodes.length - 1; i += 10) {
        const source = patoshiNodes[i]
        const target = patoshiNodes[Math.min(i + 10, patoshiNodes.length - 1)]
        if (!source || !target) continue

        edges.push({
          id: `temporal-${source.id}-${target.id}`,
          source: source.id,
          target: target.id,
          type: 'temporal',
          weight: 0.5,
          color: '#8B5CF6',
          style: 'solid',
          animated: true,
          particleCount: 2,
          blockHeight: source.blockHeight,
        })
      }

      // Matrix adjacency edges between VIP nodes
      vipNodes.forEach((nodeA, i) => {
        vipNodes.slice(i + 1).forEach((nodeB) => {
          if (!nodeA.matrixPosition || !nodeB.matrixPosition) return
          const dist = Math.abs(nodeA.matrixPosition[0] - nodeB.matrixPosition[0]) +
                       Math.abs(nodeA.matrixPosition[1] - nodeB.matrixPosition[1])
          if (dist <= 20) {
            edges.push({
              id: `matrix-${nodeA.id}-${nodeB.id}`,
              source: nodeA.id,
              target: nodeB.id,
              type: 'matrix-adjacent',
              weight: 1 - dist / 20,
              color: '#3B82F6',
              style: 'dotted',
              animated: true,
              particleCount: 3,
              matrixDistance: dist,
            })
          }
        })
      })

      setProgress(95)

      // Calculate stats with FULL counts
      const stats: NetworkStats = {
        totalNodes: nodes.length,
        totalEdges: edges.length,
        clusters: 5,
        avgConnections: edges.length / nodes.length,
        byType: {
          'patoshi-genesis': nodes.filter((n) => n.type === 'patoshi-genesis').length,
          'patoshi': nodes.filter((n) => n.type === 'patoshi').length,
          'cfb-vanity': nodes.filter((n) => n.type === 'cfb-vanity').length,
          'patoshi-vanity': nodes.filter((n) => n.type === 'patoshi-vanity').length,
          'matrix-derived': nodes.filter((n) => n.type === 'matrix-derived').length,
          'seed-validated': 0,
          'seed-mismatch': 0,
          'unknown': 0,
        },
        byMethod: {},
        byXor: {},
        patoshiBlocks: {
          min: Math.min(...patoshiAddresses.map((p) => p.blockHeight)),
          max: Math.max(...patoshiAddresses.map((p) => p.blockHeight)),
        },
        // CORRECT: amounts are already in BTC (50.0 per block)
        totalBTC: patoshiAddresses.reduce((sum, p) => sum + p.amount, 0),
        validatedSeeds: qubicSeeds.filter((s) => s.match).length,
        mismatchedSeeds: qubicSeeds.filter((s) => !s.match).length,
        // Add full dataset counts for display
        fullDatasetCounts: {
          patoshi: patoshiAddresses.length,
          matrix: matrixAddresses.length,
          interesting: interestingAddresses.length,
        },
      }

      // Update final edge count
      setLoadStats((s) => ({ ...s, totalEdges: edges.length }))

      setProgress(100)

      setData({ nodes, edges, stats, vipNodes })
      setLoading(false)
    } catch (err) {
      console.error('Failed to load address graph data:', err)
      setError({
        type: 'NETWORK_ERROR',
        message: 'Failed to Load Data',
        details: err instanceof Error ? err.message : 'Unknown error',
        retryable: true,
      })
      setLoading(false)
    }
  }, [])

  // Initial load
  useEffect(() => {
    loadData()
  }, [loadData])

  // Retry handler
  const retry = useCallback(() => {
    setRetryCount((c) => c + 1)
    loadData()
  }, [loadData])

  // Memoized node map for O(1) lookups
  const nodeMapRef = useMemo(() => {
    if (!data) return new Map<string, AddressNode>()
    const map = new Map<string, AddressNode>()
    data.nodes.forEach((n) => map.set(n.id, n))
    // Also index by address for search
    data.nodes.forEach((n) => {
      if (n.address && !map.has(n.address)) {
        map.set(n.address, n)
      }
      // Index by derived address too
      if (n.derivedAddress && !map.has(n.derivedAddress)) {
        map.set(n.derivedAddress, n)
      }
    })
    return map
  }, [data])

  // Helper: Get node by ID - O(1) Map lookup
  const getNodeById = useCallback(
    (id: string): AddressNode | undefined => {
      return nodeMapRef.get(id)
    },
    [nodeMapRef]
  )

  // Helper: Get connected nodes
  const getConnectedNodes = useCallback(
    (nodeId: string) => {
      if (!data) return { incoming: [], outgoing: [] }
      return {
        incoming: data.edges.filter((e) => e.target === nodeId),
        outgoing: data.edges.filter((e) => e.source === nodeId),
      }
    },
    [data]
  )

  // Helper: Search node - optimized with Map for exact matches
  const searchNode = useCallback(
    (query: string): AddressNode | null => {
      if (!data || !query.trim()) return null
      const q = query.trim()

      // Try exact match first (O(1))
      const exactMatch = nodeMapRef.get(q)
      if (exactMatch) return exactMatch

      // Try case-insensitive exact match on address/derivedAddress
      const lowerQ = q.toLowerCase()
      for (const node of data.nodes) {
        if (
          node.address.toLowerCase() === lowerQ ||
          node.derivedAddress?.toLowerCase() === lowerQ
        ) {
          return node
        }
      }

      // Partial match search (O(n))
      return (
        data.nodes.find(
          (n) =>
            n.address.toLowerCase().includes(lowerQ) ||
            n.derivedAddress?.toLowerCase().includes(lowerQ) ||
            n.id.toLowerCase().includes(lowerQ) ||
            n.pubkey?.toLowerCase().includes(lowerQ)
        ) || null
      )
    },
    [data, nodeMapRef]
  )

  return {
    loading,
    progress,
    loadStats,
    error,
    data,
    retry,
    retryCount,
    getNodeById,
    getConnectedNodes,
    searchNode,
  }
}
