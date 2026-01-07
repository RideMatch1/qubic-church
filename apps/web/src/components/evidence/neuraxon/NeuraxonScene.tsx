'use client'

import { useState, useMemo, Suspense, useCallback, useEffect, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Stars, PerspectiveCamera, Float, Sparkles } from '@react-three/drei'
import { useNeuraxonData } from './useNeuraxonData'
import { NeuronNode } from './NeuronNode'
import { SynapseConnection } from './SynapseConnection'
import { NeuraxonControls } from './NeuraxonControls'
import { NeuronDetailPanel } from './NeuronDetailPanel'
import type { NeuraxonNode as NeuraxonNodeType } from './types'
import { Button } from '@/components/ui/button'
import {
  Maximize2,
  Minimize2,
  Camera,
  RotateCcw,
  Info,
  Keyboard,
  Share2,
  AlertTriangle,
  WifiOff,
  FileWarning,
  RefreshCw,
  Clock,
} from 'lucide-react'
import type { NeuraxonError, NeuraxonErrorType } from './useNeuraxonData'

// Camera presets
const CAMERA_PRESETS = {
  front: { position: [0, 0, 15] as [number, number, number], name: 'Front' },
  top: { position: [0, 15, 0] as [number, number, number], name: 'Top' },
  side: { position: [15, 0, 0] as [number, number, number], name: 'Side' },
  iso: { position: [10, 10, 10] as [number, number, number], name: 'Isometric' },
}

function NetworkVisualization({
  currentNodes,
  currentEdges,
  selectedNode,
  highlightedNodes,
  showConnections,
  onNodeClick,
}: {
  currentNodes: NeuraxonNodeType[]
  currentEdges: { source: number; target: number; weight: number; type: 'fast' | 'slow' | 'meta' }[]
  selectedNode: NeuraxonNodeType | null
  highlightedNodes: Set<number>
  showConnections: boolean
  onNodeClick: (node: NeuraxonNodeType) => void
}) {
  const nodeMap = useMemo(() => {
    const map = new Map<number, NeuraxonNodeType>()
    currentNodes.forEach((node) => map.set(node.id, node))
    return map
  }, [currentNodes])

  return (
    <group>
      {/* Ambient particles for atmosphere */}
      <Sparkles
        count={100}
        scale={20}
        size={2}
        speed={0.3}
        opacity={0.3}
        color="#F59E0B"
      />

      {/* Connections */}
      {currentEdges.map((edge, i) => {
        const sourceNode = nodeMap.get(edge.source)
        const targetNode = nodeMap.get(edge.target)
        if (!sourceNode || !targetNode) return null

        const isHighlighted =
          selectedNode !== null &&
          (edge.source === selectedNode.id || edge.target === selectedNode.id)

        return (
          <SynapseConnection
            key={`${edge.source}-${edge.target}-${i}`}
            edge={edge}
            sourceNode={sourceNode}
            targetNode={targetNode}
            isHighlighted={isHighlighted}
            showAll={showConnections}
          />
        )
      })}

      {/* Nodes with subtle float animation */}
      {currentNodes.map((node) => (
        <Float
          key={node.id}
          speed={1}
          rotationIntensity={0}
          floatIntensity={0.1}
          floatingRange={[-0.05, 0.05]}
        >
          <NeuronNode
            node={node}
            isSelected={selectedNode?.id === node.id}
            isHighlighted={highlightedNodes.has(node.id)}
            onClick={onNodeClick}
          />
        </Float>
      ))}

      {/* Central glow sphere */}
      <mesh>
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshBasicMaterial color="#F59E0B" transparent opacity={0.1} />
      </mesh>
    </group>
  )
}

function LoadingScreen({ progress }: { progress: number }) {
  return (
    <div className="w-full h-full flex items-center justify-center bg-gradient-to-b from-black via-gray-900 to-black">
      <div className="flex flex-col items-center gap-6 max-w-md px-8">
        {/* Neural network animation */}
        <div className="relative w-32 h-32">
          <div className="absolute inset-0 rounded-full border-2 border-orange-500/30 animate-ping" />
          <div className="absolute inset-4 rounded-full border-2 border-blue-500/30 animate-ping animation-delay-200" />
          <div className="absolute inset-8 rounded-full border-2 border-gray-500/30 animate-ping animation-delay-400" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-orange-500 via-gray-600 to-blue-500 animate-pulse" />
          </div>
        </div>

        {/* Title */}
        <div className="text-center">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-400 via-gray-300 to-blue-400 bg-clip-text text-transparent">
            Neuraxon Ternary Network
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Initializing neural visualization...
          </p>
        </div>

        {/* Progress bar */}
        <div className="w-full space-y-2">
          <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-orange-500 via-gray-400 to-blue-500 transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-600">
            <span>Loading nodes & synapses</span>
            <span>{progress.toFixed(0)}%</span>
          </div>
        </div>

        {/* Stats preview */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-xl font-bold text-orange-400">23,765</div>
            <div className="text-xs text-gray-600">Neurons</div>
          </div>
          <div>
            <div className="text-xl font-bold text-gray-400">188,452</div>
            <div className="text-xs text-gray-600">Synapses</div>
          </div>
          <div>
            <div className="text-xl font-bold text-blue-400">47</div>
            <div className="text-xs text-gray-600">Frames</div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Error icons mapping
const ERROR_ICONS: Record<NeuraxonErrorType, React.ReactNode> = {
  NETWORK_ERROR: <WifiOff className="w-12 h-12" />,
  PARSE_ERROR: <FileWarning className="w-12 h-12" />,
  VALIDATION_ERROR: <FileWarning className="w-12 h-12" />,
  TIMEOUT_ERROR: <Clock className="w-12 h-12" />,
  UNKNOWN_ERROR: <AlertTriangle className="w-12 h-12" />,
}

const ERROR_COLORS: Record<NeuraxonErrorType, string> = {
  NETWORK_ERROR: 'text-orange-400',
  PARSE_ERROR: 'text-red-400',
  VALIDATION_ERROR: 'text-red-400',
  TIMEOUT_ERROR: 'text-yellow-400',
  UNKNOWN_ERROR: 'text-gray-400',
}

function ErrorScreen({
  error,
  onRetry,
  retryCount,
  maxRetries = 3
}: {
  error: NeuraxonError
  onRetry: () => void
  retryCount: number
  maxRetries?: number
}) {
  const canRetry = error.retryable && retryCount < maxRetries

  return (
    <div className="w-full h-full flex items-center justify-center bg-gradient-to-b from-black via-gray-900 to-black">
      <div className="flex flex-col items-center gap-6 max-w-md px-8 text-center">
        {/* Error icon with animated ring */}
        <div className="relative">
          <div className={`absolute inset-0 rounded-full border-2 ${ERROR_COLORS[error.type]} opacity-20 animate-ping`} />
          <div className={`w-24 h-24 rounded-full bg-gray-900 border-2 border-current flex items-center justify-center ${ERROR_COLORS[error.type]}`}>
            {ERROR_ICONS[error.type]}
          </div>
        </div>

        {/* Error message */}
        <div className="space-y-2">
          <h2 className={`text-xl font-bold ${ERROR_COLORS[error.type]}`}>
            {error.message}
          </h2>
          {error.details && (
            <p className="text-sm text-gray-500 max-w-sm">
              {error.details}
            </p>
          )}
        </div>

        {/* Error type badge */}
        <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-full">
          <span className="text-xs text-gray-500 uppercase tracking-wider">
            {error.type.replace('_', ' ')}
          </span>
        </div>

        {/* Retry section */}
        {canRetry ? (
          <div className="space-y-3">
            <Button
              onClick={onRetry}
              className="gap-2 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 text-white"
            >
              <RefreshCw className="w-4 h-4" />
              Try Again
            </Button>
            <p className="text-xs text-gray-600">
              Attempt {retryCount + 1} of {maxRetries}
            </p>
          </div>
        ) : retryCount >= maxRetries ? (
          <div className="space-y-2">
            <p className="text-sm text-red-400">
              Maximum retry attempts reached
            </p>
            <p className="text-xs text-gray-600">
              Please refresh the page or contact support
            </p>
          </div>
        ) : (
          <p className="text-xs text-gray-600">
            This error cannot be automatically resolved
          </p>
        )}

        {/* Troubleshooting tips */}
        <div className="pt-4 border-t border-white/10 w-full">
          <p className="text-[10px] text-gray-600 uppercase tracking-wider mb-2">
            Troubleshooting
          </p>
          <ul className="text-xs text-gray-500 space-y-1">
            <li>• Check your internet connection</li>
            <li>• Try refreshing the page</li>
            <li>• Clear browser cache if issue persists</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

function KeyboardShortcutsPanel({ onClose }: { onClose: () => void }) {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-black/80 backdrop-blur-sm z-50 pointer-events-auto">
      <div className="bg-background border border-border rounded-xl p-6 max-w-md mx-4 shadow-2xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Keyboard Shortcuts</h3>
          <Button variant="ghost" size="sm" onClick={onClose}>
            ✕
          </Button>
        </div>
        <div className="space-y-3">
          {[
            { key: 'Space', action: 'Play / Pause animation' },
            { key: '←', action: 'Previous frame' },
            { key: '→', action: 'Next frame' },
            { key: 'Home', action: 'First frame' },
            { key: 'End', action: 'Last frame' },
            { key: 'F', action: 'Toggle fullscreen' },
            { key: 'S', action: 'Toggle synapses' },
            { key: 'R', action: 'Reset camera' },
            { key: 'Esc', action: 'Deselect node' },
          ].map(({ key, action }) => (
            <div key={key} className="flex items-center gap-3">
              <kbd className="px-2 py-1 bg-muted rounded text-xs font-mono min-w-[60px] text-center">
                {key}
              </kbd>
              <span className="text-sm text-muted-foreground">{action}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function NeuraxonScene() {
  const {
    loading,
    error,
    data,
    currentNodes,
    currentEdges,
    frameIndex,
    setFrameIndex,
    totalFrames,
    searchNode,
    getNodeById,
    getConnectedNodes,
    currentFrame,
    retry,
    retryCount,
  } = useNeuraxonData()

  const [selectedNode, setSelectedNode] = useState<NeuraxonNodeType | null>(null)
  const [showConnections, setShowConnections] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showKeyboardShortcuts, setShowKeyboardShortcuts] = useState(false)
  const [playbackSpeed, setPlaybackSpeed] = useState(1)
  const [cameraPreset, setCameraPreset] = useState<keyof typeof CAMERA_PRESETS>('front')
  const containerRef = useRef<HTMLDivElement>(null)
  const controlsRef = useRef<any>(null)
  const [loadProgress, setLoadProgress] = useState(0)

  // Simulate loading progress
  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setLoadProgress((p) => Math.min(p + Math.random() * 15, 95))
      }, 200)
      return () => clearInterval(interval)
    } else {
      setLoadProgress(100)
    }
  }, [loading])

  // Highlighted nodes
  const highlightedNodes = useMemo(() => {
    if (!selectedNode) return new Set<number>()
    const { incoming, outgoing } = getConnectedNodes(selectedNode.id)
    const nodes = new Set<number>()
    incoming.forEach((e) => nodes.add(e.source))
    outgoing.forEach((e) => nodes.add(e.target))
    return nodes
  }, [selectedNode, getConnectedNodes])

  // Handlers
  const handleNodeClick = useCallback((node: NeuraxonNodeType) => {
    setSelectedNode((current) => (current?.id === node.id ? null : node))
  }, [])

  const handleNodeFound = useCallback((node: NeuraxonNodeType) => {
    setSelectedNode(node)
  }, [])

  const handleCloseDetail = useCallback(() => {
    setSelectedNode(null)
  }, [])

  // Fullscreen toggle
  const toggleFullscreen = useCallback(() => {
    if (!containerRef.current) return

    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }, [])

  // Reset camera
  const resetCamera = useCallback(() => {
    if (controlsRef.current) {
      controlsRef.current.reset()
    }
    setCameraPreset('front')
  }, [])

  // Share functionality
  const handleShare = useCallback(async () => {
    const url = `${window.location.origin}${window.location.pathname}?frame=${frameIndex}${selectedNode ? `&node=${selectedNode.id}` : ''}`

    if (navigator.share) {
      await navigator.share({
        title: 'Neuraxon Ternary Network',
        text: `Exploring frame ${frameIndex + 1} of the Neuraxon visualization with 23,765 neurons`,
        url,
      })
    } else {
      await navigator.clipboard.writeText(url)
    }
  }, [frameIndex, selectedNode])

  // Enhanced keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement) return

      switch (e.key.toLowerCase()) {
        case 'f':
          e.preventDefault()
          toggleFullscreen()
          break
        case 's':
          e.preventDefault()
          setShowConnections((s) => !s)
          break
        case 'r':
          e.preventDefault()
          resetCamera()
          break
        case 'escape':
          setSelectedNode(null)
          setShowKeyboardShortcuts(false)
          break
        case '?':
          setShowKeyboardShortcuts((s) => !s)
          break
        case 'home':
          e.preventDefault()
          setFrameIndex(0)
          break
        case 'end':
          e.preventDefault()
          setFrameIndex(totalFrames - 1)
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [toggleFullscreen, resetCamera, setFrameIndex, totalFrames])

  // Fullscreen change listener
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }, [])

  if (loading || loadProgress < 100) {
    return (
      <div
        ref={containerRef}
        className="w-full h-[700px] rounded-lg overflow-hidden border border-border"
      >
        <LoadingScreen progress={loadProgress} />
      </div>
    )
  }

  if (error) {
    return (
      <div
        ref={containerRef}
        className="w-full h-[700px] rounded-lg overflow-hidden border border-border"
      >
        <ErrorScreen
          error={error}
          onRetry={retry}
          retryCount={retryCount}
        />
      </div>
    )
  }

  const currentCameraPosition = CAMERA_PRESETS[cameraPreset].position

  return (
    <div
      ref={containerRef}
      className={`relative w-full bg-black rounded-lg overflow-hidden border border-border transition-all duration-300 ${
        isFullscreen ? 'h-screen rounded-none' : 'h-[700px]'
      }`}
    >
      {/* 3D Canvas */}
      <Canvas
        gl={{ antialias: true, alpha: false }}
        dpr={[1, 2]}
      >
        <PerspectiveCamera
          makeDefault
          position={currentCameraPosition}
          fov={60}
        />
        <OrbitControls
          ref={controlsRef}
          enableDamping
          dampingFactor={0.05}
          minDistance={3}
          maxDistance={60}
          enablePan
          panSpeed={0.5}
          rotateSpeed={0.5}
          zoomSpeed={0.8}
        />

        {/* Enhanced Lighting */}
        <ambientLight intensity={0.3} />
        <pointLight position={[15, 15, 15]} intensity={1.2} color="#ffffff" />
        <pointLight position={[-15, -15, -15]} intensity={0.6} color="#3B82F6" />
        <pointLight position={[15, -15, 15]} intensity={0.6} color="#F59E0B" />
        <pointLight position={[0, 20, 0]} intensity={0.4} color="#8B5CF6" />

        {/* Deep space background */}
        <Stars
          radius={150}
          depth={80}
          count={3000}
          factor={5}
          saturation={0}
          fade
          speed={0.5}
        />

        {/* Network */}
        <Suspense fallback={null}>
          <NetworkVisualization
            currentNodes={currentNodes}
            currentEdges={currentEdges}
            selectedNode={selectedNode}
            highlightedNodes={highlightedNodes}
            showConnections={showConnections}
            onNodeClick={handleNodeClick}
          />
        </Suspense>
      </Canvas>

      {/* UI Overlay */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Top Bar */}
        <div className="absolute top-0 left-0 right-0 p-4 flex items-start justify-between">
          {/* Legend - Enhanced */}
          <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-xl p-4 space-y-3 pointer-events-auto">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-500 via-gray-500 to-blue-500" />
              <div>
                <div className="text-sm font-semibold text-white">Neuraxon</div>
                <div className="text-[10px] text-gray-400">Ternary Neural Network</div>
              </div>
            </div>

            <div className="border-t border-white/10 pt-3 space-y-2">
              <div className="text-[10px] uppercase tracking-wider text-gray-500 font-medium">States</div>
              <div className="grid grid-cols-3 gap-2">
                <div className="flex flex-col items-center gap-1">
                  <div className="w-4 h-4 rounded-full bg-orange-500 shadow-lg shadow-orange-500/50" />
                  <span className="text-[10px] text-gray-400">+1</span>
                </div>
                <div className="flex flex-col items-center gap-1">
                  <div className="w-4 h-4 rounded-full bg-gray-500 shadow-lg shadow-gray-500/50" />
                  <span className="text-[10px] text-gray-400">0</span>
                </div>
                <div className="flex flex-col items-center gap-1">
                  <div className="w-4 h-4 rounded-full bg-blue-500 shadow-lg shadow-blue-500/50" />
                  <span className="text-[10px] text-gray-400">-1</span>
                </div>
              </div>
            </div>

            <div className="border-t border-white/10 pt-3 space-y-2">
              <div className="text-[10px] uppercase tracking-wider text-gray-500 font-medium">Synapses</div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-0.5 bg-green-500 rounded-full" />
                  <span className="text-[10px] text-gray-400">Fast &gt;70%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-0.5 bg-yellow-500 rounded-full" />
                  <span className="text-[10px] text-gray-400">Slow 40-70%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-0.5 bg-purple-500 rounded-full" />
                  <span className="text-[10px] text-gray-400">Meta &lt;40%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Top Right Controls */}
          <div className="flex flex-col gap-2 pointer-events-auto">
            {/* Main actions */}
            <div className="flex gap-1 bg-black/70 backdrop-blur-md border border-white/10 rounded-lg p-1">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-white/70 hover:text-white hover:bg-white/10"
                onClick={toggleFullscreen}
                title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
              >
                {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-white/70 hover:text-white hover:bg-white/10"
                onClick={resetCamera}
                title="Reset camera"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-white/70 hover:text-white hover:bg-white/10"
                onClick={() => setShowKeyboardShortcuts(true)}
                title="Keyboard shortcuts"
              >
                <Keyboard className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-white/70 hover:text-white hover:bg-white/10"
                onClick={handleShare}
                title="Share"
              >
                <Share2 className="w-4 h-4" />
              </Button>
            </div>

            {/* Camera presets */}
            <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-lg p-1">
              <div className="text-[10px] text-gray-500 px-2 py-1">Camera</div>
              <div className="grid grid-cols-2 gap-1">
                {Object.entries(CAMERA_PRESETS).map(([key, preset]) => (
                  <Button
                    key={key}
                    variant="ghost"
                    size="sm"
                    className={`h-7 text-xs ${
                      cameraPreset === key
                        ? 'bg-white/20 text-white'
                        : 'text-white/70 hover:text-white hover:bg-white/10'
                    }`}
                    onClick={() => setCameraPreset(key as keyof typeof CAMERA_PRESETS)}
                  >
                    {preset.name}
                  </Button>
                ))}
              </div>
            </div>

            {/* Frame info */}
            {currentFrame && (
              <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-lg p-3 text-center">
                <div className="text-[10px] text-gray-500 uppercase tracking-wider">Frame Range</div>
                <div className="text-sm font-mono text-white">
                  #{currentFrame.startId} - #{currentFrame.endId}
                </div>
                <div className="text-[10px] text-gray-500 mt-1">
                  512 neurons / frame
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Detail Panel */}
        {selectedNode && (
          <NeuronDetailPanel
            node={selectedNode}
            connections={getConnectedNodes(selectedNode.id)}
            getNodeById={getNodeById}
            onClose={handleCloseDetail}
            onNodeClick={(node) => {
              setFrameIndex(node.frame)
              setSelectedNode(node)
            }}
          />
        )}

        {/* Controls */}
        <NeuraxonControls
          frameIndex={frameIndex}
          totalFrames={totalFrames}
          onFrameChange={setFrameIndex}
          onSearch={searchNode}
          onNodeFound={handleNodeFound}
          showConnections={showConnections}
          onToggleConnections={() => setShowConnections((s) => !s)}
          metadata={data?.metadata || null}
          playbackSpeed={playbackSpeed}
          onSpeedChange={setPlaybackSpeed}
        />

        {/* Keyboard shortcuts modal */}
        {showKeyboardShortcuts && (
          <KeyboardShortcutsPanel onClose={() => setShowKeyboardShortcuts(false)} />
        )}
      </div>

      {/* Watermark */}
      <div className="absolute bottom-20 left-4 text-[10px] text-white/30 pointer-events-none">
        Neuraxon v2.0 • 23,765 neurons • 188,452 synapses • 47 frames
      </div>
    </div>
  )
}
