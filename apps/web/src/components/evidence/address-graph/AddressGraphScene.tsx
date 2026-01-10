'use client'

import { Suspense, useRef, useMemo, useState, useCallback, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import {
  OrbitControls,
  PerspectiveCamera,
  Stars,
  Html,
  Stats,
} from '@react-three/drei'
import * as THREE from 'three'
import { AnimatePresence, motion } from 'framer-motion'
import type { AddressNode, AddressEdge, ViewState } from './types'
import { useAddressGraphData } from './useAddressGraphData'
import { LoadingScreen } from './LoadingScreen'
import { ErrorScreen } from './ErrorScreen'
import { AddressDetailPanel } from './AddressDetailPanel'
import { AddressGraphControls } from './AddressGraphControls'
import { KeyboardShortcutsPanel } from './KeyboardShortcutsPanel'
import { StatisticsPanel } from './StatisticsPanel'
import { NODE_TYPE_CONFIG, CAMERA_PRESETS, PERFORMANCE } from './constants'

// =============================================================================
// SIZE MAPPING
// =============================================================================

const SIZE_MAP: Record<string, number> = {
  xs: 0.15,
  small: 0.25,
  medium: 0.4,
  large: 0.6,
  xl: 0.9,
}

// =============================================================================
// INSTANCED NODES - HIGH PERFORMANCE
// =============================================================================

interface InstancedNodesProps {
  nodes: AddressNode[]
  selectedNodeId: string | null
  hoveredNodeId: string | null
  connectedNodeIds: Set<string>
  onNodeClick: (node: AddressNode) => void
  onNodeHover: (nodeId: string | null) => void
}

function InstancedNodes({
  nodes,
  selectedNodeId,
  hoveredNodeId,
  connectedNodeIds,
  onNodeClick,
  onNodeHover,
}: InstancedNodesProps) {
  const meshRef = useRef<THREE.InstancedMesh>(null)
  const glowMeshRef = useRef<THREE.InstancedMesh>(null)
  const tempObject = useMemo(() => new THREE.Object3D(), [])
  const tempColor = useMemo(() => new THREE.Color(), [])

  // Store nodes reference for raycasting
  const nodesRef = useRef<AddressNode[]>(nodes)
  nodesRef.current = nodes

  // Max instances for performance
  const maxInstances = Math.min(nodes.length, PERFORMANCE.MAX_VISIBLE_NODES)
  const displayNodes = nodes.slice(0, maxInstances)

  // Update instance matrices and colors every frame
  useFrame(() => {
    if (!meshRef.current || displayNodes.length === 0) return

    displayNodes.forEach((node, i) => {
      // Position
      tempObject.position.set(node.position[0], node.position[1], node.position[2])

      // Scale based on size and state
      const baseSize = SIZE_MAP[node.size] || 0.4
      const isSelected = node.id === selectedNodeId
      const isHovered = node.id === hoveredNodeId
      const isConnected = connectedNodeIds.has(node.id)

      const scale = isSelected ? baseSize * 1.5 : isHovered ? baseSize * 1.3 : isConnected ? baseSize * 1.1 : baseSize
      tempObject.scale.setScalar(scale)

      tempObject.updateMatrix()
      meshRef.current!.setMatrixAt(i, tempObject.matrix)

      // Color
      const intensity = isSelected ? 1.5 : isHovered ? 1.2 : isConnected ? 1.0 : 0.8
      tempColor.set(node.color).multiplyScalar(intensity)
      meshRef.current!.setColorAt(i, tempColor)
    })

    meshRef.current.instanceMatrix.needsUpdate = true
    if (meshRef.current.instanceColor) {
      meshRef.current.instanceColor.needsUpdate = true
    }

    // Update glow mesh
    if (glowMeshRef.current && displayNodes.length > 0) {
      displayNodes.forEach((node, i) => {
        tempObject.position.set(node.position[0], node.position[1], node.position[2])
        const baseSize = (SIZE_MAP[node.size] || 0.4) * 2
        tempObject.scale.setScalar(node.glowIntensity > 0 ? baseSize : 0)
        tempObject.updateMatrix()
        glowMeshRef.current!.setMatrixAt(i, tempObject.matrix)
        tempColor.set(node.color)
        glowMeshRef.current!.setColorAt(i, tempColor)
      })
      glowMeshRef.current.instanceMatrix.needsUpdate = true
      if (glowMeshRef.current.instanceColor) {
        glowMeshRef.current.instanceColor.needsUpdate = true
      }
    }
  })

  // Raycasting for hover/click
  const { raycaster, camera, pointer, gl } = useThree()

  useEffect(() => {
    const handleClick = () => {
      if (!meshRef.current) return
      raycaster.setFromCamera(pointer, camera)
      const intersects = raycaster.intersectObject(meshRef.current)
      const hit = intersects[0]
      if (hit && hit.instanceId !== undefined) {
        const node = nodesRef.current[hit.instanceId]
        if (node) onNodeClick(node)
      }
    }

    const handleMove = () => {
      if (!meshRef.current) return
      raycaster.setFromCamera(pointer, camera)
      const intersects = raycaster.intersectObject(meshRef.current)
      const moveHit = intersects[0]
      if (moveHit && moveHit.instanceId !== undefined) {
        const node = nodesRef.current[moveHit.instanceId]
        onNodeHover(node?.id ?? null)
        gl.domElement.style.cursor = 'pointer'
      } else {
        onNodeHover(null)
        gl.domElement.style.cursor = 'default'
      }
    }

    gl.domElement.addEventListener('click', handleClick)
    gl.domElement.addEventListener('pointermove', handleMove)
    return () => {
      gl.domElement.removeEventListener('click', handleClick)
      gl.domElement.removeEventListener('pointermove', handleMove)
    }
  }, [onNodeClick, onNodeHover, raycaster, camera, pointer, gl])

  if (displayNodes.length === 0) return null

  return (
    <group>
      {/* Glow layer */}
      <instancedMesh
        ref={glowMeshRef}
        args={[undefined, undefined, maxInstances]}
        frustumCulled={false}
      >
        <sphereGeometry args={[0.5, 8, 8]} />
        <meshBasicMaterial transparent opacity={0.15} />
      </instancedMesh>

      {/* Main nodes */}
      <instancedMesh
        ref={meshRef}
        args={[undefined, undefined, maxInstances]}
        frustumCulled={false}
      >
        <sphereGeometry args={[0.5, 12, 12]} />
        <meshStandardMaterial roughness={0.3} metalness={0.7} />
      </instancedMesh>
    </group>
  )
}

// =============================================================================
// OPTIMIZED EDGES - Line Segments
// =============================================================================

interface OptimizedEdgesProps {
  edges: AddressEdge[]
  nodeMap: Map<string, AddressNode>
  highlightedPath: string[]
}

function OptimizedEdges({ edges, nodeMap, highlightedPath }: OptimizedEdgesProps) {
  // Limit edges for performance
  const displayEdges = edges.slice(0, PERFORMANCE.MAX_VISIBLE_EDGES)

  const { positions, colors } = useMemo(() => {
    const pos: number[] = []
    const col: number[] = []
    const tempColor = new THREE.Color()

    displayEdges.forEach((edge) => {
      const source = nodeMap.get(edge.source)
      const target = nodeMap.get(edge.target)
      if (!source || !target) return

      // Source position
      pos.push(source.position[0], source.position[1], source.position[2])
      // Target position
      pos.push(target.position[0], target.position[1], target.position[2])

      // Color
      const isHighlighted = highlightedPath.includes(edge.source) && highlightedPath.includes(edge.target)
      const opacity = isHighlighted ? 0.8 : edge.weight * 0.4
      tempColor.set(edge.color)
      col.push(tempColor.r * opacity, tempColor.g * opacity, tempColor.b * opacity)
      col.push(tempColor.r * opacity, tempColor.g * opacity, tempColor.b * opacity)
    })

    return {
      positions: new Float32Array(pos),
      colors: new Float32Array(col),
    }
  }, [displayEdges, nodeMap, highlightedPath])

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3))
    return geo
  }, [positions, colors])

  if (displayEdges.length === 0) return null

  return (
    <lineSegments geometry={geometry} frustumCulled={false}>
      <lineBasicMaterial vertexColors transparent opacity={0.6} />
    </lineSegments>
  )
}

// =============================================================================
// CAMERA CONTROLLER
// =============================================================================

interface CameraControllerProps {
  preset: keyof typeof CAMERA_PRESETS | 'custom'
  presetTrigger: number // Force re-trigger when incremented
  targetNode?: AddressNode | null
  onDistanceChange: (distance: number) => void
}

function CameraController({ preset, presetTrigger, targetNode, onDistanceChange }: CameraControllerProps) {
  const { camera } = useThree()
  const controlsRef = useRef<any>(null)

  useFrame(() => {
    const distance = camera.position.length()
    onDistanceChange(distance)
  })

  // Handle camera preset changes
  useEffect(() => {
    if (targetNode) {
      const [x, y, z] = targetNode.position
      camera.position.set(x + 8, y + 5, z + 8)
      camera.lookAt(x, y, z)
    } else if (preset !== 'custom') {
      const config = CAMERA_PRESETS[preset]
      if (config) {
        camera.position.set(...config.position)
        camera.lookAt(...config.target)
      }
    }
  }, [preset, presetTrigger, targetNode, camera])

  return null
}

// =============================================================================
// TOOLTIP COMPONENT
// =============================================================================

function NodeTooltip({ node }: { node: AddressNode }) {
  const config = NODE_TYPE_CONFIG[node.type]

  return (
    <Html position={node.position} center style={{ pointerEvents: 'none' }}>
      <div className="px-3 py-2 bg-black/90 border border-white/20 rounded-lg backdrop-blur-sm min-w-[200px]">
        <div className="flex items-center gap-2 mb-1">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: node.color }}
          />
          <span className="text-xs font-medium text-white/60">{config.label}</span>
        </div>
        <div className="text-sm font-mono text-white truncate max-w-[200px]">
          {node.address}
        </div>
        {node.blockHeight !== undefined && (
          <div className="text-xs text-white/50 mt-1">
            Block #{node.blockHeight.toLocaleString()}
          </div>
        )}
        {node.amount !== undefined && (
          <div className="text-xs text-orange-400 mt-0.5">
            {node.amount.toFixed(2)} BTC
          </div>
        )}
      </div>
    </Html>
  )
}

// =============================================================================
// MAIN SCENE COMPONENT
// =============================================================================

export function AddressGraphScene() {
  const {
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
  } = useAddressGraphData()

  // View state
  const [viewState, setViewState] = useState<ViewState>({
    mode: 'force',
    cameraPreset: 'overview',
    cameraPosition: [0, 50, 50],
    showEdges: true,
    selectedNodeId: null,
    highlightedPath: [],
    playbackSpeed: 1,
    isPlaying: false,
    currentBlock: 0, // Genesis block (GRAPH_CONFIG undefined)
  })

  // Filter state - Default: Show PROVEN data (Matrix), hide HYPOTHESIS (Patoshi)
  const [filters, setFilters] = useState({
    showPatoshi: false, // Tier 2 Hypothesis - OFF by default
    showMatrix: true,   // Tier 1 Proven - ON by default
    showVIPOnly: false,
  })

  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null)
  const [showShortcuts, setShowShortcuts] = useState(false)
  const [showStats, setShowStats] = useState(false)
  const [showTierInfo, setShowTierInfo] = useState(false)
  const [showStatisticsPanel, setShowStatisticsPanel] = useState(false)
  const [cameraDistance, setCameraDistance] = useState(70)
  const [presetTrigger, setPresetTrigger] = useState(0) // Force camera update

  // Camera preset handler with forced trigger
  const handleCameraPreset = useCallback((preset: keyof typeof CAMERA_PRESETS) => {
    setViewState((s) => ({ ...s, cameraPreset: preset, selectedNodeId: null }))
    setPresetTrigger((t) => t + 1) // Force re-trigger
  }, [])

  // Handlers
  const handleNodeClick = useCallback((node: AddressNode) => {
    setViewState((s) => ({
      ...s,
      selectedNodeId: node.id,
      cameraPreset: 'custom',
    }))
    setPresetTrigger((t) => t + 1)
  }, [])

  const handleNodeHover = useCallback((nodeId: string | null) => {
    setHoveredNodeId(nodeId)
  }, [])

  const handleCloseDetail = useCallback(() => {
    setViewState((s) => ({ ...s, selectedNodeId: null }))
  }, [])

  const handleBlockChange = useCallback((block: number) => {
    setViewState((s) => ({ ...s, currentBlock: block }))
  }, [])

  const handlePlayToggle = useCallback(() => {
    setViewState((s) => ({ ...s, isPlaying: !s.isPlaying }))
  }, [])

  const handleSpeedChange = useCallback((speed: number) => {
    setViewState((s) => ({ ...s, playbackSpeed: speed }))
  }, [])

  const handleEdgesToggle = useCallback(() => {
    setViewState((s) => ({ ...s, showEdges: !s.showEdges }))
  }, [])

  const handleSearch = useCallback(
    (query: string) => {
      return searchNode(query)
    },
    [searchNode]
  )

  const handleNodeFound = useCallback((node: AddressNode) => {
    setViewState((s) => ({
      ...s,
      selectedNodeId: node.id,
      cameraPreset: 'custom',
    }))
    setPresetTrigger((t) => t + 1)
  }, [])

  const handleCameraDistanceChange = useCallback((distance: number) => {
    setCameraDistance(distance)
  }, [])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement) return

      switch (e.key.toLowerCase()) {
        case ' ':
          e.preventDefault()
          handlePlayToggle()
          break
        case 'e':
          handleEdgesToggle()
          break
        case 'r':
          handleCameraPreset('overview')
          break
        case 'f':
          setShowStats((s) => !s)
          break
        case 'p':
          setFilters((f) => ({ ...f, showPatoshi: !f.showPatoshi }))
          break
        case 'm':
          setFilters((f) => ({ ...f, showMatrix: !f.showMatrix }))
          break
        case 'v':
          setFilters((f) => ({ ...f, showVIPOnly: !f.showVIPOnly }))
          break
        case '1':
          handleCameraPreset('overview')
          break
        case '2':
          handleCameraPreset('patoshi')
          break
        case '3':
          handleCameraPreset('cfb')
          break
        case '4':
          handleCameraPreset('genesis')
          break
        case '5':
          handleCameraPreset('timeline')
          break
        case '?':
          setShowShortcuts((s) => !s)
          break
        case 'escape':
          if (viewState.selectedNodeId) {
            handleCloseDetail()
          } else if (showShortcuts) {
            setShowShortcuts(false)
          }
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handlePlayToggle, handleEdgesToggle, handleCloseDetail, handleCameraPreset, viewState.selectedNodeId, showShortcuts])

  // Playback animation
  useEffect(() => {
    if (!viewState.isPlaying || !data) return

    const maxBlock = data.stats.patoshiBlocks.max
    const interval = setInterval(() => {
      setViewState((s) => {
        const newBlock = s.currentBlock + 100 * s.playbackSpeed
        if (newBlock >= maxBlock) {
          return { ...s, currentBlock: maxBlock, isPlaying: false }
        }
        return { ...s, currentBlock: newBlock }
      })
    }, 50)

    return () => clearInterval(interval)
  }, [viewState.isPlaying, viewState.playbackSpeed, data])

  // Memoized data
  const nodeMap = useMemo(() => {
    if (!data) return new Map<string, AddressNode>()
    const map = new Map<string, AddressNode>()
    data.nodes.forEach((n) => map.set(n.id, n))
    return map
  }, [data])

  const connectedNodeIds = useMemo(() => {
    if (!viewState.selectedNodeId || !data) return new Set<string>()
    const connected = new Set<string>()
    data.edges.forEach((edge) => {
      if (edge.source === viewState.selectedNodeId) connected.add(edge.target)
      if (edge.target === viewState.selectedNodeId) connected.add(edge.source)
    })
    return connected
  }, [viewState.selectedNodeId, data])

  // Filter nodes by block height and type filters
  const visibleNodes = useMemo(() => {
    if (!data) return []
    return data.nodes.filter((n) => {
      // Block height filter
      if (n.blockHeight !== undefined && n.blockHeight > viewState.currentBlock) {
        return false
      }
      // VIP only filter
      if (filters.showVIPOnly && !n.isVIP) {
        return false
      }
      // Patoshi filter
      if (!filters.showPatoshi && (n.type === 'patoshi' || n.type === 'patoshi-genesis' || n.type === 'patoshi-vanity')) {
        return false
      }
      // Matrix filter
      if (!filters.showMatrix && (n.type === 'matrix-derived' || n.type === 'cfb-vanity')) {
        return false
      }
      return true
    })
  }, [data, viewState.currentBlock, filters])

  // Calculate statistical data from visible nodes
  const statisticalData = useMemo(() => {
    if (!visibleNodes.length) {
      return {
        xorDistribution: undefined,
        methodDistribution: undefined,
        blockHeights: undefined,
        balances: undefined,
      }
    }

    // XOR distribution (for matrix nodes)
    const xorCounts = new Map<number, number>([[0, 0], [7, 0], [13, 0], [27, 0], [33, 0]])
    const methodCounts = new Map<string, number>([
      ['diagonal', 0],
      ['row', 0],
      ['col', 0],
      ['step7', 0],
      ['step13', 0],
      ['step27', 0],
    ])
    const blockHeights: number[] = []
    const balances: number[] = []

    visibleNodes.forEach((node) => {
      // Count XOR variants
      if (node.xorVariant !== undefined && xorCounts.has(node.xorVariant)) {
        xorCounts.set(node.xorVariant, (xorCounts.get(node.xorVariant) || 0) + 1)
      }

      // Count derivation methods
      if (node.derivationMethod && methodCounts.has(node.derivationMethod)) {
        methodCounts.set(
          node.derivationMethod,
          (methodCounts.get(node.derivationMethod) || 0) + 1
        )
      }

      // Collect block heights
      if (node.blockHeight !== undefined) {
        blockHeights.push(node.blockHeight)
      }

      // Collect balances (mock data - in real implementation would come from blockchain API)
      if (node.amount !== undefined) {
        balances.push(node.amount)
      }
    })

    return {
      xorDistribution: Array.from(xorCounts.values()),
      methodDistribution: Array.from(methodCounts.values()),
      blockHeights: blockHeights.length > 0 ? blockHeights : undefined,
      balances: balances.length > 0 ? balances : undefined,
    }
  }, [visibleNodes])

  // Filter edges
  const visibleEdges = useMemo(() => {
    if (!data || !viewState.showEdges) return []
    const visibleIds = new Set(visibleNodes.map((n) => n.id))
    return data.edges.filter(
      (e) => visibleIds.has(e.source) && visibleIds.has(e.target)
    )
  }, [data, visibleNodes, viewState.showEdges])

  // Get selected node data
  const selectedNode = viewState.selectedNodeId ? getNodeById(viewState.selectedNodeId) : null
  const connections = viewState.selectedNodeId
    ? getConnectedNodes(viewState.selectedNodeId)
    : { incoming: [], outgoing: [] }

  // Hovered node for tooltip
  const hoveredNode = hoveredNodeId ? getNodeById(hoveredNodeId) : null

  // Loading state
  if (loading) {
    return <LoadingScreen progress={progress} stats={loadStats} />
  }

  // Error state
  if (error) {
    return <ErrorScreen error={error} onRetry={retry} retryCount={retryCount} />
  }

  // No data
  if (!data) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-black">
        <p className="text-gray-500">No data available</p>
      </div>
    )
  }

  return (
    <div className="relative w-full h-full bg-black">
      {/* 3D Canvas */}
      <Canvas
        gl={{ antialias: true, alpha: false, powerPreference: 'high-performance' }}
        dpr={[1, 1.5]}
        className="w-full h-full"
      >
        <color attach="background" args={['#000000']} />

        <Suspense fallback={null}>
          <PerspectiveCamera makeDefault position={[50, 30, 80]} fov={50} />
          <OrbitControls
            enableDamping
            dampingFactor={0.05} // Default camera damping
            minDistance={5}
            maxDistance={200}
            enablePan
            target={[0, 30, 0]}
          />

          {/* Lighting - Optimized for 5-Layer Matrix Cube */}
          <ambientLight intensity={0.4} />
          {/* Top light for XOR 33 layer */}
          <pointLight position={[0, 100, 0]} intensity={0.8} color="#EC4899" />
          {/* Side accent lights for depth */}
          <pointLight position={[80, 30, 80]} intensity={1.2} color="#FFFFFF" />
          <pointLight position={[-80, 30, -80]} intensity={0.6} color="#06B6D4" />
          {/* Bottom layer accent */}
          <pointLight position={[0, -20, 0]} intensity={0.4} color="#8B5CF6" />
          {/* Rotating accent light for drama */}
          <pointLight position={[40, 30, 0]} intensity={0.5} color="#F59E0B" />

          {/* Environment */}
          <Stars radius={300} depth={100} count={3000} factor={4} fade speed={0.5} />

          {/* Camera controller */}
          <CameraController
            preset={viewState.cameraPreset}
            presetTrigger={presetTrigger}
            targetNode={selectedNode}
            onDistanceChange={handleCameraDistanceChange}
          />

          {/* Edges (rendered first, behind nodes) */}
          {viewState.showEdges && visibleEdges.length > 0 && (
            <OptimizedEdges
              edges={visibleEdges}
              nodeMap={nodeMap}
              highlightedPath={viewState.highlightedPath}
            />
          )}

          {/* Nodes - Instanced for performance */}
          {visibleNodes.length > 0 && (
            <InstancedNodes
              nodes={visibleNodes}
              selectedNodeId={viewState.selectedNodeId}
              hoveredNodeId={hoveredNodeId}
              connectedNodeIds={connectedNodeIds}
              onNodeClick={handleNodeClick}
              onNodeHover={handleNodeHover}
            />
          )}

          {/* Tooltip for hovered node */}
          {hoveredNode && !selectedNode && (
            <NodeTooltip node={hoveredNode} />
          )}

          {/* FPS Stats (when enabled) */}
          {showStats && <Stats />}
        </Suspense>
      </Canvas>

      {/* UI Overlays */}

      {/* Title + Stats Header */}
      <div className="absolute top-4 left-4">
        <div className="pointer-events-none">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-400 via-purple-400 to-blue-400 bg-clip-text text-transparent">
            Address Graph
          </h2>
          <p className="text-sm text-gray-500">
            Displaying {visibleNodes.length.toLocaleString()} nodes • {visibleEdges.length.toLocaleString()} edges
          </p>
          {data.stats.fullDatasetCounts && (
            <p className="text-xs text-gray-600 mt-0.5">
              Full dataset: {(data.stats.fullDatasetCounts.patoshi + data.stats.fullDatasetCounts.matrix).toLocaleString()} addresses
            </p>
          )}
        </div>

        {/* Scientific Tier Classification - Compact Info Button */}
        <div className="mt-2 flex items-center gap-2 pointer-events-auto">
          <button
            onClick={() => setShowTierInfo(true)}
            className="px-3 py-1.5 bg-yellow-500/20 border border-yellow-500/40 rounded-lg text-[11px] font-medium text-yellow-400 hover:bg-yellow-500/30 transition-colors flex items-center gap-1.5"
          >
            <span className="text-sm">ⓘ</span>
            Tier Classification
          </button>
          {filters.showPatoshi && (
            <div className="px-2 py-1 bg-orange-500/20 border border-orange-500/40 rounded text-[10px] text-orange-400">
              ⚠️ Tier 2 Hypothesis Data Enabled
            </div>
          )}
        </div>

        {/* Quick Stats Row */}
        <div className="flex items-center gap-2 mt-3 pointer-events-auto flex-wrap">
          <div className="px-3 py-1.5 bg-orange-500/10 border border-orange-500/30 rounded-lg">
            <div className="text-sm font-bold text-orange-400">
              {data.stats.totalBTC.toLocaleString()} BTC
            </div>
            <div className="text-[9px] text-orange-400/60">Patoshi Total</div>
          </div>
          <div className="px-3 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <div className="text-sm font-bold text-blue-400">
              {(data.stats.fullDatasetCounts?.matrix || 0).toLocaleString()}
            </div>
            <div className="text-[9px] text-blue-400/60">
              Matrix Addresses
              {data.stats.byType['matrix-derived'] > 0 && (
                <span className="block text-[8px] text-blue-400/40 mt-0.5">
                  (~{data.stats.byType['matrix-derived'].toLocaleString()} shown)
                </span>
              )}
            </div>
          </div>
          <div className="px-3 py-1.5 bg-purple-500/10 border border-purple-500/30 rounded-lg">
            <div className="text-sm font-bold text-purple-400">
              {(data.stats.fullDatasetCounts?.patoshi || 0).toLocaleString()}
            </div>
            <div className="text-[9px] text-purple-400/60">Patoshi Blocks</div>
          </div>
          <div className="px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded-lg">
            <div className="text-sm font-bold text-green-400">
              {data.stats.validatedSeeds.toLocaleString()}
            </div>
            <div className="text-[9px] text-green-400/60">Validated Seeds</div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center gap-2 mt-3 pointer-events-auto">
          <button
            onClick={() => handleCameraPreset('overview')}
            className="px-2.5 py-1.5 text-xs bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-gray-400 hover:text-white transition-colors"
          >
            Reset View
          </button>
          <button
            onClick={() => {
              // Export comprehensive data including all addresses
              const exportData = {
                exportDate: new Date().toISOString(),
                summary: {
                  totalNodes: data.nodes.length,
                  visibleNodes: visibleNodes.length,
                  totalEdges: data.edges.length,
                  visibleEdges: visibleEdges.length,
                  totalBTC: data.stats.totalBTC,
                  fullDataset: data.stats.fullDatasetCounts,
                },
                stats: data.stats,
                patoshiAddresses: data.nodes
                  .filter((n) => n.type === 'patoshi' || n.type === 'patoshi-genesis')
                  .map((n) => ({
                    blockHeight: n.blockHeight,
                    address: n.derivedAddress || n.address,
                    pubkey: n.pubkey,
                    amount: n.amount,
                    type: n.type,
                  })),
                interestingAddresses: data.nodes
                  .filter((n) => n.type === 'cfb-vanity' || n.type === 'patoshi-vanity')
                  .map((n) => ({
                    address: n.address,
                    type: n.type,
                    matrixPosition: n.matrixPosition,
                    derivationMethod: n.derivationMethod,
                    xorVariant: n.xorVariant,
                  })),
              }
              const dataStr = JSON.stringify(exportData, null, 2)
              const blob = new Blob([dataStr], { type: 'application/json' })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `address-graph-export-${new Date().toISOString().split('T')[0]}.json`
              a.click()
              URL.revokeObjectURL(url)
            }}
            className="px-2.5 py-1.5 text-xs bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-gray-400 hover:text-white transition-colors"
          >
            Export Data
          </button>
          <button
            onClick={() => setShowStats((s) => !s)}
            className={`px-2.5 py-1.5 text-xs border rounded-lg transition-colors ${
              showStats
                ? 'bg-green-500/20 border-green-500/50 text-green-400'
                : 'bg-white/5 hover:bg-white/10 border-white/10 text-gray-400 hover:text-white'
            }`}
          >
            FPS {showStats ? 'ON' : 'OFF'}
          </button>
        </div>

        {/* Distance Indicator */}
        <div className="mt-2 text-[10px] text-gray-600 pointer-events-none">
          Camera Distance: {cameraDistance.toFixed(0)} • Max {PERFORMANCE.MAX_VISIBLE_NODES.toLocaleString()} nodes
        </div>
      </div>

      {/* Legend with Counts */}
      <div className="absolute top-4 right-4 p-3 bg-black/80 border border-white/10 rounded-lg backdrop-blur-sm max-w-[200px] max-h-[80vh] overflow-y-auto">
        <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Node Types</p>
        <div className="space-y-1.5 max-h-[300px] overflow-y-auto pr-1">
          {Object.entries(NODE_TYPE_CONFIG).slice(0, 6).map(([type, config]) => {
            const count = data.stats.byType[type as keyof typeof data.stats.byType] || 0
            return (
              <div key={type} className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <div
                    className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: config.color }}
                  />
                  <span className="text-xs text-gray-400 truncate">{config.label}</span>
                </div>
                <span className="text-[10px] text-gray-600 font-mono">{count.toLocaleString()}</span>
              </div>
            )
          })}
        </div>

        {/* Filters */}
        <div className="mt-3 pt-3 border-t border-white/10">
          <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Filters</p>
          <div className="flex flex-wrap gap-1">
            <button
              onClick={() => setFilters((f) => ({ ...f, showPatoshi: !f.showPatoshi }))}
              className={`px-2 py-1 text-[10px] rounded transition-colors ${
                filters.showPatoshi
                  ? 'bg-orange-500/30 text-orange-400 border border-orange-500/50'
                  : 'bg-white/5 text-gray-500 hover:text-white hover:bg-white/10 border border-transparent line-through'
              }`}
            >
              Patoshi [P]
            </button>
            <button
              onClick={() => setFilters((f) => ({ ...f, showMatrix: !f.showMatrix }))}
              className={`px-2 py-1 text-[10px] rounded transition-colors ${
                filters.showMatrix
                  ? 'bg-blue-500/30 text-blue-400 border border-blue-500/50'
                  : 'bg-white/5 text-gray-500 hover:text-white hover:bg-white/10 border border-transparent line-through'
              }`}
            >
              Matrix [M]
            </button>
            <button
              onClick={() => setFilters((f) => ({ ...f, showVIPOnly: !f.showVIPOnly }))}
              className={`px-2 py-1 text-[10px] rounded transition-colors ${
                filters.showVIPOnly
                  ? 'bg-purple-500/30 text-purple-400 border border-purple-500/50'
                  : 'bg-white/5 text-gray-500 hover:text-white hover:bg-white/10 border border-transparent'
              }`}
            >
              VIP Only [V]
            </button>
          </div>
        </div>

        {/* Camera Presets */}
        <div className="mt-3 pt-3 border-t border-white/10">
          <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Camera</p>
          <div className="flex flex-wrap gap-1">
            {(['overview', 'patoshi', 'cfb', 'genesis', 'timeline'] as const).map((preset) => (
              <button
                key={preset}
                onClick={() => handleCameraPreset(preset)}
                className={`px-2 py-1 text-[10px] rounded transition-colors ${
                  viewState.cameraPreset === preset
                    ? 'bg-orange-500/30 text-orange-400 border border-orange-500/50'
                    : 'bg-white/5 text-gray-500 hover:text-white hover:bg-white/10 border border-transparent'
                }`}
              >
                {preset.charAt(0).toUpperCase() + preset.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Controls */}
      <AddressGraphControls
        currentBlock={viewState.currentBlock}
        totalBlocks={data.stats.patoshiBlocks.max}
        isPlaying={viewState.isPlaying}
        playbackSpeed={viewState.playbackSpeed}
        showEdges={viewState.showEdges}
        visibleNodes={visibleNodes.length}
        totalNodes={data.nodes.length}
        onBlockChange={handleBlockChange}
        onPlayToggle={handlePlayToggle}
        onSpeedChange={handleSpeedChange}
        onEdgesToggle={handleEdgesToggle}
        onSearch={handleSearch}
        onNodeFound={handleNodeFound}
      />

      {/* Detail Panel */}
      <AnimatePresence>
        {selectedNode && (
          <AddressDetailPanel
            node={selectedNode}
            connections={connections}
            onClose={handleCloseDetail}
            onNodeClick={handleNodeClick}
            getNodeById={getNodeById}
          />
        )}
      </AnimatePresence>

      {/* Keyboard Shortcuts Panel */}
      <AnimatePresence>
        {showShortcuts && (
          <KeyboardShortcutsPanel onClose={() => setShowShortcuts(false)} />
        )}
      </AnimatePresence>

      {/* Shortcuts hint */}
      <div className="absolute bottom-20 right-4 text-[10px] text-gray-600">
        Press <kbd className="px-1 py-0.5 bg-gray-800 rounded text-gray-400">?</kbd> for shortcuts
      </div>

      {/* Tier Classification Modal */}
      <AnimatePresence>
        {showTierInfo && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowTierInfo(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-zinc-900 border border-yellow-500/30 rounded-xl p-6 max-w-lg w-full shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">⚠️</span>
                  <h3 className="text-lg font-bold text-yellow-400">Scientific Tier Classification</h3>
                </div>
                <button
                  onClick={() => setShowTierInfo(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4 text-sm">
                <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-blue-400 font-bold text-lg">■</span>
                    <span className="font-bold text-blue-300">Tier 1: PROVEN</span>
                    <span className="ml-auto text-xs text-blue-400/60">99% confidence</span>
                  </div>
                  <div className="text-xs text-blue-400/80 ml-7">
                    <strong>Matrix Addresses (Blue):</strong> Mathematically reproducible from Anna Matrix.
                    These addresses are PROVEN to be derived from the Qubic system using verified algorithms.
                  </div>
                  <div className="text-[10px] text-blue-400/60 ml-7 mt-1">
                    983,040 addresses • Reproducible • Verified
                  </div>
                </div>

                <div className="p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-orange-400 font-bold text-lg">■</span>
                    <span className="font-bold text-orange-300">Tier 2: HYPOTHESIS</span>
                    <span className="ml-auto text-xs text-orange-400/60">85% confidence</span>
                  </div>
                  <div className="text-xs text-orange-400/80 ml-7">
                    <strong>Patoshi Addresses (Orange):</strong> Correlation analysis suggests connection.
                    The Patoshi pattern is PROVEN (Sergio Demian Lerner), but the connection to Qubic is hypothetical.
                  </div>
                  <div className="text-[10px] text-orange-400/60 ml-7 mt-1">
                    21,953 blocks • Correlation • Not cryptographically proven
                  </div>
                </div>

                <div className="text-xs text-gray-400 border-t border-gray-700 pt-3">
                  <strong>Note:</strong> This visualization prioritizes Tier 1 proven data by default.
                  Tier 2 hypothesis data (Patoshi) can be enabled via the "P" key or filter toggle.
                </div>
              </div>

              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => setShowTierInfo(false)}
                  className="px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 border border-yellow-500/40 rounded-lg text-sm font-medium text-yellow-400 transition-colors"
                >
                  Got it
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Statistics Panel */}
      <StatisticsPanel
        isOpen={showStatisticsPanel}
        onToggle={() => setShowStatisticsPanel(!showStatisticsPanel)}
        data={statisticalData}
      />
    </div>
  )
}
