'use client'

import { useState, useMemo, Suspense, useCallback, useEffect, useRef } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Stars, Html } from '@react-three/drei'
import * as THREE from 'three'
import { useAnnaGridData } from './useAnnaGridData'
import { CellDetailPanel } from './CellDetailPanel'
import { AnnaGridControls } from './AnnaGridControls'
import type { AnnaCell, ViewMode, ColorTheme, MatrixStats } from './types'
import {
  MATRIX_SIZE,
  COLOR_THEMES,
  SPECIAL_ROWS,
  SPECIAL_ADDRESSES,
  CAMERA_PRESETS,
  KEYBOARD_SHORTCUTS,
} from './constants'
import { Button } from '@/components/ui/button'
import {
  Maximize2,
  Minimize2,
  RotateCcw,
  Keyboard,
  Download,
  RefreshCw,
  WifiOff,
  FileWarning,
  X,
  Grid3X3,
  Table2,
  Crosshair,
  Search,
  Target,
  Sparkles,
  BarChart3,
  Info,
  Map,
  Palette,
  BookOpen,
  ExternalLink,
  FileCode,
  Hash,
  ScanLine,
  Binary,
  Clock,
  Code,
  FileText,
  MessageCircle,
  Zap,
  AlertTriangle,
} from 'lucide-react'

// =============================================================================
// GRID MESH COMPONENT (3D)
// =============================================================================

function GridMesh({
  matrix,
  colorTheme,
  viewMode,
  selectedCell,
  hoveredCell,
  onCellHover,
  onCellClick,
  showVIPMarkers,
  showSpecialRows,
  showCrosshair,
  vipPositions,
}: {
  matrix: number[][]
  colorTheme: ColorTheme
  viewMode: ViewMode
  selectedCell: AnnaCell | null
  hoveredCell: { row: number; col: number } | null
  onCellHover: (pos: { row: number; col: number } | null) => void
  onCellClick: (row: number, col: number) => void
  showVIPMarkers: boolean
  showSpecialRows: boolean
  showCrosshair: boolean
  vipPositions: Array<{ row: number; col: number; address: string }>
}) {
  const meshRef = useRef<THREE.Mesh>(null)
  const crosshairRef = useRef<THREE.Group>(null)
  const theme = COLOR_THEMES[colorTheme]
  const { raycaster, camera, pointer } = useThree()

  // Create geometry with height data
  const { geometry, positions: positionsAttr } = useMemo(() => {
    const size = MATRIX_SIZE
    const heightScale = viewMode === 'terrain' ? 2 : viewMode === 'flat' ? 0.1 : 0.5
    const gridScale = 10

    const geo = new THREE.PlaneGeometry(gridScale, gridScale, size - 1, size - 1)
    const positions = geo.attributes.position
    if (!positions) return { geometry: geo, positions: null }

    const colorArray = new Float32Array(positions.count * 3)
    const negativeColor = new THREE.Color(theme.negative)
    const neutralColor = new THREE.Color(theme.neutral)
    const positiveColor = new THREE.Color(theme.positive)

    const row21Color = new THREE.Color(SPECIAL_ROWS[21]?.color || '#F7931A')
    const row68Color = new THREE.Color(SPECIAL_ROWS[68]?.color || '#8B5CF6')
    const row96Color = new THREE.Color(SPECIAL_ROWS[96]?.color || '#22C55E')

    for (let i = 0; i < positions.count; i++) {
      const ix = i % size
      const iy = Math.floor(i / size)
      const matrixRow = size - 1 - iy
      const value = matrix[matrixRow]?.[ix] ?? 0

      const normalized = (value + 128) / 255
      const height = (normalized - 0.5) * heightScale
      positions.setZ(i, height)

      let color: THREE.Color

      if (showSpecialRows && (matrixRow === 21 || matrixRow === 68 || matrixRow === 96)) {
        if (matrixRow === 21) color = row21Color.clone()
        else if (matrixRow === 68) color = row68Color.clone()
        else color = row96Color.clone()
        const intensity = 0.5 + normalized * 0.5
        color.multiplyScalar(intensity)
      } else {
        if (value < 0) {
          const t = (value + 128) / 128
          color = negativeColor.clone().lerp(neutralColor, t)
        } else {
          const t = value / 127
          color = neutralColor.clone().lerp(positiveColor, t)
        }
      }

      colorArray[i * 3] = color.r
      colorArray[i * 3 + 1] = color.g
      colorArray[i * 3 + 2] = color.b
    }

    positions.needsUpdate = true
    geo.computeVertexNormals()
    geo.setAttribute('color', new THREE.BufferAttribute(colorArray, 3))

    return { geometry: geo, positions }
  }, [matrix, theme, viewMode, showSpecialRows])

  // Animate mesh and crosshair
  useFrame((state) => {
    if (meshRef.current && viewMode === 'terrain') {
      meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.02
    }

    // Update crosshair position
    if (crosshairRef.current && hoveredCell && showCrosshair) {
      const gridScale = 10
      const cellSize = gridScale / MATRIX_SIZE
      const x = (hoveredCell.col - MATRIX_SIZE / 2) * cellSize + cellSize / 2
      const z = (MATRIX_SIZE / 2 - hoveredCell.row) * cellSize - cellSize / 2
      crosshairRef.current.position.set(x, 1.5, z)
      crosshairRef.current.visible = true
    } else if (crosshairRef.current) {
      crosshairRef.current.visible = false
    }
  })

  // Raycasting for hover/click
  const handlePointerMove = useCallback(
    (event: THREE.Event) => {
      if (!meshRef.current || !positionsAttr) return

      raycaster.setFromCamera(pointer, camera)
      const intersects = raycaster.intersectObject(meshRef.current)

      if (intersects.length > 0 && intersects[0]) {
        const point = intersects[0].point
        const gridScale = 10
        const halfGrid = gridScale / 2
        const col = Math.floor(((point.x + halfGrid) / gridScale) * MATRIX_SIZE)
        const row = MATRIX_SIZE - 1 - Math.floor(((point.z + halfGrid) / gridScale) * MATRIX_SIZE)

        if (row >= 0 && row < MATRIX_SIZE && col >= 0 && col < MATRIX_SIZE) {
          onCellHover({ row, col })
        }
      }
    },
    [raycaster, camera, pointer, positionsAttr, onCellHover]
  )

  const handleClick = useCallback(() => {
    if (hoveredCell) {
      onCellClick(hoveredCell.row, hoveredCell.col)
    }
  }, [hoveredCell, onCellClick])

  // Material based on view mode
  const material = useMemo(() => {
    switch (viewMode) {
      case 'wireframe':
        return <meshBasicMaterial color={theme.neutral} wireframe opacity={0.8} transparent />
      case 'terrain':
        return <meshStandardMaterial vertexColors metalness={0.1} roughness={0.7} />
      case 'scientific':
        return <meshStandardMaterial vertexColors metalness={0.3} roughness={0.4} flatShading />
      case 'heatmap':
        return <meshStandardMaterial vertexColors metalness={0.3} roughness={0.5} emissive="#000000" emissiveIntensity={0.1} />
      default:
        return <meshStandardMaterial vertexColors metalness={0.2} roughness={0.6} />
    }
  }, [viewMode, theme])

  return (
    <group rotation={[-Math.PI / 2, 0, 0]}>
      <mesh
        ref={meshRef}
        geometry={geometry}
        onPointerMove={handlePointerMove}
        onClick={handleClick}
        onPointerOut={() => onCellHover(null)}
      >
        {material}
      </mesh>

      {/* Crosshair indicator */}
      <group ref={crosshairRef} rotation={[Math.PI / 2, 0, 0]} visible={false}>
        <mesh>
          <ringGeometry args={[0.05, 0.08, 32]} />
          <meshBasicMaterial color="#FFFFFF" transparent opacity={0.9} />
        </mesh>
        <mesh rotation={[0, 0, Math.PI / 4]}>
          <planeGeometry args={[0.2, 0.01]} />
          <meshBasicMaterial color="#FFFFFF" />
        </mesh>
        <mesh rotation={[0, 0, -Math.PI / 4]}>
          <planeGeometry args={[0.2, 0.01]} />
          <meshBasicMaterial color="#FFFFFF" />
        </mesh>
      </group>

      {/* VIP Markers */}
      {showVIPMarkers &&
        vipPositions.map((vip, idx) => {
          const gridScale = 10
          const cellSize = gridScale / MATRIX_SIZE
          const x = (vip.col - MATRIX_SIZE / 2) * cellSize + cellSize / 2
          const z = (MATRIX_SIZE / 2 - vip.row) * cellSize - cellSize / 2
          const value = matrix[vip.row]?.[vip.col] ?? 0
          const height = ((value + 128) / 255 - 0.5) * 2 + 0.2

          const isCFB = vip.address.startsWith('1CFB')
          const isPat = vip.address.startsWith('1Pat')
          const color = isCFB ? '#FF6B35' : isPat ? '#9333EA' : '#06B6D4'

          return (
            <group key={`vip-${idx}`} position={[x, height, z]}>
              <mesh>
                <sphereGeometry args={[0.08, 16, 16]} />
                <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} />
              </mesh>
              <mesh rotation={[Math.PI / 2, 0, 0]}>
                <ringGeometry args={[0.1, 0.15, 32]} />
                <meshBasicMaterial color={color} transparent opacity={0.5} />
              </mesh>
            </group>
          )
        })}

      {/* Selected cell highlight */}
      {selectedCell && (
        <group
          position={[
            (selectedCell.col - MATRIX_SIZE / 2) * (10 / MATRIX_SIZE) + 0.04,
            ((selectedCell.value + 128) / 255 - 0.5) * 2 + 0.3,
            (MATRIX_SIZE / 2 - selectedCell.row) * (10 / MATRIX_SIZE) - 0.04,
          ]}
        >
          <mesh>
            <boxGeometry args={[0.12, 0.4, 0.12]} />
            <meshStandardMaterial color="#FFFFFF" emissive="#FFFFFF" emissiveIntensity={0.8} transparent opacity={0.9} />
          </mesh>
        </group>
      )}

      {/* Hover indicator */}
      {hoveredCell && !selectedCell && !showCrosshair && (
        <group
          position={[
            (hoveredCell.col - MATRIX_SIZE / 2) * (10 / MATRIX_SIZE) + 0.04,
            1.2,
            (MATRIX_SIZE / 2 - hoveredCell.row) * (10 / MATRIX_SIZE) - 0.04,
          ]}
        >
          <Html center>
            <div className="bg-black/80 px-2 py-1 rounded text-xs text-white whitespace-nowrap pointer-events-none">
              [{hoveredCell.row}, {hoveredCell.col}]
            </div>
          </Html>
        </group>
      )}

      {/* Boot address marker */}
      <group
        position={[
          (SPECIAL_ADDRESSES.boot.col - MATRIX_SIZE / 2) * (10 / MATRIX_SIZE) + 0.04,
          0.5,
          (MATRIX_SIZE / 2 - SPECIAL_ADDRESSES.boot.row) * (10 / MATRIX_SIZE) - 0.04,
        ]}
      >
        <mesh>
          <coneGeometry args={[0.1, 0.3, 4]} />
          <meshStandardMaterial color="#FBBF24" emissive="#FBBF24" emissiveIntensity={0.6} />
        </mesh>
      </group>

      {/* POCZ marker */}
      <group
        position={[
          (SPECIAL_ADDRESSES.pocz.col - MATRIX_SIZE / 2) * (10 / MATRIX_SIZE) + 0.04,
          0.5,
          (MATRIX_SIZE / 2 - SPECIAL_ADDRESSES.pocz.row) * (10 / MATRIX_SIZE) - 0.04,
        ]}
      >
        <mesh>
          <octahedronGeometry args={[0.12]} />
          <meshStandardMaterial color="#10B981" emissive="#10B981" emissiveIntensity={0.6} />
        </mesh>
      </group>

      <gridHelper args={[10, 16, theme.positive, theme.positive]} rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 1.5]} />
    </group>
  )
}

// =============================================================================
// 2D GRID VIEW COMPONENT
// =============================================================================

function Grid2DView({
  matrix,
  stats,
  colorTheme,
  selectedCell,
  onCellClick,
  zoomRegion,
}: {
  matrix: number[][]
  stats: MatrixStats
  colorTheme: ColorTheme
  selectedCell: AnnaCell | null
  onCellClick: (row: number, col: number) => void
  zoomRegion: 'all' | 'q1' | 'q2' | 'q3' | 'q4'
}) {
  const [hoveredCell, setHoveredCell] = useState<{ row: number; col: number } | null>(null)
  const theme = COLOR_THEMES[colorTheme]

  const { startRow, endRow, startCol, endCol } = useMemo(() => {
    switch (zoomRegion) {
      case 'q1': return { startRow: 0, endRow: 64, startCol: 0, endCol: 64 }
      case 'q2': return { startRow: 0, endRow: 64, startCol: 64, endCol: 128 }
      case 'q3': return { startRow: 64, endRow: 128, startCol: 0, endCol: 64 }
      case 'q4': return { startRow: 64, endRow: 128, startCol: 64, endCol: 128 }
      default: return { startRow: 0, endRow: 128, startCol: 0, endCol: 128 }
    }
  }, [zoomRegion])

  const visibleRows = endRow - startRow
  const visibleCols = endCol - startCol
  const cellSize = zoomRegion === 'all' ? 4 : 8

  const getCellColor = (value: number) => {
    if (value < 0) {
      const t = (value - stats.min) / (0 - stats.min)
      return `color-mix(in srgb, ${theme.negative} ${(1 - t) * 100}%, ${theme.neutral} ${t * 100}%)`
    } else {
      const t = value / stats.max
      return `color-mix(in srgb, ${theme.neutral} ${(1 - t) * 100}%, ${theme.positive} ${t * 100}%)`
    }
  }

  return (
    <div className="w-full h-full bg-black overflow-auto">
      <div className="sticky top-0 z-20 flex bg-black/90 backdrop-blur-sm">
        <div className="w-8 h-6 shrink-0" />
        <div className="flex">
          {Array.from({ length: visibleCols }, (_, i) => {
            const col = startCol + i
            return (
              <div
                key={col}
                className="text-[8px] text-white/40 text-center font-mono"
                style={{ width: cellSize, minWidth: cellSize }}
              >
                {col % (zoomRegion === 'all' ? 16 : 8) === 0 ? col : ''}
              </div>
            )
          })}
        </div>
      </div>

      <div className="flex">
        <div className="sticky left-0 z-10 flex flex-col bg-black/90 backdrop-blur-sm">
          {Array.from({ length: visibleRows }, (_, i) => {
            const row = startRow + i
            return (
              <div
                key={row}
                className="w-8 text-[8px] text-white/40 text-right pr-1 font-mono flex items-center justify-end"
                style={{ height: cellSize, minHeight: cellSize }}
              >
                {row % (zoomRegion === 'all' ? 16 : 8) === 0 ? row : ''}
              </div>
            )
          })}
        </div>

        <div
          className="grid"
          style={{
            gridTemplateColumns: `repeat(${visibleCols}, ${cellSize}px)`,
            gridTemplateRows: `repeat(${visibleRows}, ${cellSize}px)`,
          }}
        >
          {Array.from({ length: visibleRows * visibleCols }, (_, i) => {
            const row = startRow + Math.floor(i / visibleCols)
            const col = startCol + (i % visibleCols)
            const value = matrix[row]?.[col] ?? 0
            const isSelected = selectedCell?.row === row && selectedCell?.col === col
            const isHovered = hoveredCell?.row === row && hoveredCell?.col === col

            return (
              <div
                key={`${row}-${col}`}
                className={`cursor-pointer transition-all ${
                  isSelected ? 'ring-2 ring-white z-10' : ''
                } ${isHovered ? 'ring-1 ring-white/50 z-5' : ''}`}
                style={{
                  width: cellSize,
                  height: cellSize,
                  backgroundColor: getCellColor(value),
                }}
                onClick={() => onCellClick(row, col)}
                onMouseEnter={() => setHoveredCell({ row, col })}
                onMouseLeave={() => setHoveredCell(null)}
                title={`[${row}, ${col}] = ${value}`}
              />
            )
          })}
        </div>
      </div>

      {hoveredCell && (
        <div className="fixed bottom-4 right-4 bg-black/95 border border-white/20 rounded-lg px-3 py-2 text-sm font-mono text-white z-50">
          [{hoveredCell.row}, {hoveredCell.col}] = {matrix[hoveredCell.row]?.[hoveredCell.col] ?? 0}
        </div>
      )}
    </div>
  )
}

// =============================================================================
// LOADING SCREEN
// =============================================================================

function LoadingScreen({ progress }: { progress: number }) {
  return (
    <div className="w-full h-full flex items-center justify-center bg-gradient-to-b from-black via-gray-900 to-black">
      <div className="flex flex-col items-center gap-6 max-w-md px-8">
        <div className="relative w-32 h-32">
          <div className="absolute inset-0 grid grid-cols-4 grid-rows-4 gap-1 opacity-50">
            {Array.from({ length: 16 }).map((_, i) => (
              <div
                key={i}
                className="bg-gradient-to-br from-blue-500 to-orange-500 rounded-sm animate-pulse"
                style={{ animationDelay: `${i * 50}ms` }}
              />
            ))}
          </div>
          <div className="absolute inset-4 flex items-center justify-center">
            <div className="text-2xl font-bold text-white">128²</div>
          </div>
        </div>

        <div className="text-center">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-orange-400 bg-clip-text text-transparent">
            Anna Matrix Explorer
          </h2>
          <p className="text-sm text-gray-500 mt-1">Loading 16,384 cells...</p>
        </div>

        <div className="w-full space-y-2">
          <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-orange-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-600">
            <span>Initializing matrix</span>
            <span>{progress.toFixed(0)}%</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// =============================================================================
// ERROR SCREEN
// =============================================================================

function ErrorScreen({
  error,
  onRetry,
  retryCount,
}: {
  error: { type: string; message: string; details?: string; retryable: boolean }
  onRetry: () => void
  retryCount: number
}) {
  return (
    <div className="w-full h-full flex items-center justify-center bg-gradient-to-b from-black via-gray-900 to-black">
      <div className="flex flex-col items-center gap-6 max-w-md px-8 text-center">
        <div className="w-24 h-24 rounded-full bg-gray-900 border-2 border-red-500 flex items-center justify-center">
          {error.type === 'NETWORK_ERROR' ? (
            <WifiOff className="w-12 h-12 text-red-400" />
          ) : (
            <FileWarning className="w-12 h-12 text-red-400" />
          )}
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-red-400">{error.message}</h2>
          {error.details && <p className="text-sm text-gray-500">{error.details}</p>}
        </div>
        {error.retryable && retryCount < 3 && (
          <Button onClick={onRetry} className="gap-2 bg-gradient-to-r from-orange-600 to-orange-500">
            <RefreshCw className="w-4 h-4" />
            Try Again
          </Button>
        )}
      </div>
    </div>
  )
}

// =============================================================================
// STATS PANEL WITH HISTOGRAM
// =============================================================================

function StatsPanel({ stats, matrix, onClose }: { stats: MatrixStats; matrix: number[][]; onClose: () => void }) {
  const histogram = useMemo(() => {
    const bins = 32
    const binSize = (stats.max - stats.min) / bins
    const counts = new Array(bins).fill(0)

    for (const row of matrix) {
      for (const val of row) {
        const binIndex = Math.min(Math.floor((val - stats.min) / binSize), bins - 1)
        counts[binIndex]++
      }
    }

    const maxCount = Math.max(...counts)
    return counts.map((count, i) => ({
      value: stats.min + (i + 0.5) * binSize,
      count,
      height: (count / maxCount) * 100,
    }))
  }, [matrix, stats])

  return (
    <div className="absolute top-4 right-4 w-72 bg-black/90 backdrop-blur-md border border-white/10 rounded-xl p-4 pointer-events-auto z-40">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-orange-400" />
          <span className="text-sm font-semibold text-white">Statistics</span>
        </div>
        <button onClick={onClose} className="text-white/50 hover:text-white">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-white/5 rounded-lg p-2">
            <div className="text-[10px] text-white/40 uppercase">Min</div>
            <div className="text-sm font-mono text-blue-400">{stats.min}</div>
          </div>
          <div className="bg-white/5 rounded-lg p-2">
            <div className="text-[10px] text-white/40 uppercase">Max</div>
            <div className="text-sm font-mono text-orange-400">{stats.max}</div>
          </div>
          <div className="bg-white/5 rounded-lg p-2">
            <div className="text-[10px] text-white/40 uppercase">Mean</div>
            <div className="text-sm font-mono text-white/80">{stats.mean.toFixed(2)}</div>
          </div>
          <div className="bg-white/5 rounded-lg p-2">
            <div className="text-[10px] text-white/40 uppercase">Std Dev</div>
            <div className="text-sm font-mono text-white/80">{stats.stdDev.toFixed(2)}</div>
          </div>
        </div>

        <div className="space-y-2">
          <div className="text-[10px] text-white/40 uppercase">Distribution Histogram</div>
          <div className="h-20 flex items-end gap-[1px] bg-white/5 rounded-lg p-2">
            {histogram.map((bin, i) => (
              <div
                key={i}
                className="flex-1 rounded-t-sm transition-all"
                style={{
                  height: `${bin.height}%`,
                  backgroundColor: bin.value < 0 ? '#3B82F6' : bin.value > 0 ? '#F59E0B' : '#6B7280',
                }}
                title={`${bin.value.toFixed(0)}: ${bin.count} cells`}
              />
            ))}
          </div>
          <div className="flex justify-between text-[9px] text-white/30 font-mono">
            <span>{stats.min}</span>
            <span>0</span>
            <span>{stats.max}</span>
          </div>
        </div>

        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-500" />
            <span className="text-[10px] text-white/60 flex-1">Negative</span>
            <span className="text-[10px] text-blue-400 font-mono">{stats.negativeCount.toLocaleString()}</span>
            <span className="text-[10px] text-white/30">({((stats.negativeCount / stats.totalCells) * 100).toFixed(1)}%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-gray-500" />
            <span className="text-[10px] text-white/60 flex-1">Zero</span>
            <span className="text-[10px] text-gray-400 font-mono">{stats.zeroCount.toLocaleString()}</span>
            <span className="text-[10px] text-white/30">({((stats.zeroCount / stats.totalCells) * 100).toFixed(1)}%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-orange-500" />
            <span className="text-[10px] text-white/60 flex-1">Positive</span>
            <span className="text-[10px] text-orange-400 font-mono">{stats.positiveCount.toLocaleString()}</span>
            <span className="text-[10px] text-white/30">({((stats.positiveCount / stats.totalCells) * 100).toFixed(1)}%)</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// =============================================================================
// SEARCH PANEL
// =============================================================================

function SearchPanel({
  matrix,
  stats,
  onSelectCell,
  onClose,
}: {
  matrix: number[][]
  stats: MatrixStats
  onSelectCell: (row: number, col: number) => void
  onClose: () => void
}) {
  const [searchValue, setSearchValue] = useState('')
  const [results, setResults] = useState<{ row: number; col: number; value: number }[]>([])

  const handleSearch = () => {
    const target = parseInt(searchValue, 10)
    if (isNaN(target)) return

    const found: { row: number; col: number; value: number }[] = []
    for (let row = 0; row < 128; row++) {
      for (let col = 0; col < 128; col++) {
        if (matrix[row]?.[col] === target) {
          found.push({ row, col, value: target })
        }
      }
    }
    setResults(found.slice(0, 50))
  }

  return (
    <div className="absolute top-4 left-1/2 -translate-x-1/2 w-80 bg-black/95 backdrop-blur-md border border-white/10 rounded-xl p-4 pointer-events-auto z-50">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Search className="w-4 h-4 text-cyan-400" />
          <span className="text-sm font-semibold text-white">Search Value</span>
        </div>
        <button onClick={onClose} className="text-white/50 hover:text-white">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex gap-2 mb-3">
        <input
          type="number"
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          placeholder={`${stats.min} to ${stats.max}`}
          className="flex-1 bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm text-white placeholder-white/30 focus:outline-none focus:border-cyan-400"
        />
        <Button size="sm" onClick={handleSearch} className="bg-cyan-600 hover:bg-cyan-500">
          Search
        </Button>
      </div>

      {results.length > 0 && (
        <div className="space-y-1 max-h-40 overflow-y-auto">
          <div className="text-[10px] text-white/40 uppercase mb-1">
            Found {results.length} cells {results.length === 50 && '(showing first 50)'}
          </div>
          {results.map((r, i) => (
            <button
              key={i}
              onClick={() => onSelectCell(r.row, r.col)}
              className="w-full flex items-center justify-between bg-white/5 hover:bg-white/10 rounded px-2 py-1 text-sm"
            >
              <span className="font-mono text-white/70">[{r.row}, {r.col}]</span>
              <span className="font-mono text-cyan-400">{r.value}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

// =============================================================================
// COORDINATE INPUT PANEL
// =============================================================================

function CoordinateInput({
  onNavigate,
  onClose,
}: {
  onNavigate: (row: number, col: number) => void
  onClose: () => void
}) {
  const [row, setRow] = useState('')
  const [col, setCol] = useState('')

  const handleGo = () => {
    const r = parseInt(row, 10)
    const c = parseInt(col, 10)
    if (!isNaN(r) && !isNaN(c) && r >= 0 && r < 128 && c >= 0 && c < 128) {
      onNavigate(r, c)
      onClose()
    }
  }

  return (
    <div className="absolute bottom-20 left-1/2 -translate-x-1/2 bg-black/95 backdrop-blur-md border border-white/10 rounded-xl p-4 pointer-events-auto z-50">
      <div className="flex items-center gap-2 mb-3">
        <Target className="w-4 h-4 text-purple-400" />
        <span className="text-sm font-semibold text-white">Jump to Cell</span>
        <button onClick={onClose} className="ml-auto text-white/50 hover:text-white">
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="flex items-center gap-2">
        <input
          type="number"
          value={row}
          onChange={(e) => setRow(e.target.value)}
          placeholder="Row (0-127)"
          min={0}
          max={127}
          className="w-24 bg-white/10 border border-white/20 rounded-lg px-2 py-1 text-sm text-white placeholder-white/30 focus:outline-none focus:border-purple-400"
        />
        <span className="text-white/30">,</span>
        <input
          type="number"
          value={col}
          onChange={(e) => setCol(e.target.value)}
          placeholder="Col (0-127)"
          min={0}
          max={127}
          className="w-24 bg-white/10 border border-white/20 rounded-lg px-2 py-1 text-sm text-white placeholder-white/30 focus:outline-none focus:border-purple-400"
        />
        <Button size="sm" onClick={handleGo} className="bg-purple-600 hover:bg-purple-500">
          Go
        </Button>
      </div>
    </div>
  )
}

// =============================================================================
// MINI MAP COMPONENT
// =============================================================================

function MiniMap({
  matrix,
  stats,
  selectedCell,
  hoveredCell,
}: {
  matrix: number[][]
  stats: MatrixStats
  selectedCell: AnnaCell | null
  hoveredCell: { row: number; col: number } | null
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const imageData = ctx.createImageData(128, 128)
    for (let row = 0; row < 128; row++) {
      for (let col = 0; col < 128; col++) {
        const value = matrix[row]?.[col] ?? 0
        const normalized = (value - stats.min) / (stats.max - stats.min)
        const i = (row * 128 + col) * 4

        if (value < 0) {
          imageData.data[i] = 59
          imageData.data[i + 1] = 130
          imageData.data[i + 2] = 246
        } else if (value > 0) {
          imageData.data[i] = 245
          imageData.data[i + 1] = 158
          imageData.data[i + 2] = 11
        } else {
          imageData.data[i] = 107
          imageData.data[i + 1] = 114
          imageData.data[i + 2] = 128
        }
        imageData.data[i + 3] = 100 + normalized * 155
      }
    }
    ctx.putImageData(imageData, 0, 0)

    if (selectedCell) {
      ctx.fillStyle = '#FFFFFF'
      ctx.fillRect(selectedCell.col - 1, selectedCell.row - 1, 3, 3)
    }

    if (hoveredCell && (!selectedCell || hoveredCell.row !== selectedCell.row || hoveredCell.col !== selectedCell.col)) {
      ctx.fillStyle = 'rgba(255,255,255,0.5)'
      ctx.fillRect(hoveredCell.col - 1, hoveredCell.row - 1, 3, 3)
    }
  }, [matrix, stats, selectedCell, hoveredCell])

  return (
    <div className="absolute bottom-20 left-4 bg-black/80 backdrop-blur-md border border-white/10 rounded-lg p-2 pointer-events-auto">
      <div className="flex items-center gap-1 mb-1">
        <Map className="w-3 h-3 text-white/50" />
        <span className="text-[9px] text-white/50 uppercase">Overview</span>
      </div>
      <canvas
        ref={canvasRef}
        width={128}
        height={128}
        className="rounded"
        style={{ width: 80, height: 80, imageRendering: 'pixelated' }}
      />
    </div>
  )
}

// =============================================================================
// INFO PANEL - Full documentation about Anna Matrix
// =============================================================================

function InfoPanel({ onClose }: { onClose: () => void }) {
  return (
    <div className="absolute inset-4 bg-black/98 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden z-50 pointer-events-auto">
      <div className="h-full overflow-y-auto">
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-blue-500 flex items-center justify-center shadow-lg shadow-orange-500/25">
                <Grid3X3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Anna Matrix</h2>
                <p className="text-sm text-gray-400">128 × 128 Signed Byte Cryptographic Matrix</p>
              </div>
            </div>
            <button onClick={onClose} className="text-white/50 hover:text-white p-2 hover:bg-white/10 rounded-lg transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Anna AI Chatbot Section */}
          <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-xl p-4">
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shrink-0 shadow-lg">
                <MessageCircle className="w-7 h-7 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-purple-400" />
                  <h3 className="font-semibold text-white">Talk to Anna AI</h3>
                  <span className="px-2 py-0.5 bg-purple-500/30 rounded-full text-[10px] text-purple-300 uppercase">Live</span>
                </div>
                <p className="text-sm text-gray-300 mb-3">
                  Anna is an AI research assistant specialized in the Bitcoin-Qubic connection. Ask her about the matrix,
                  Patoshi patterns, seed derivation algorithms, or any aspect of the cryptographic evidence.
                </p>
                <a
                  href="https://x.com/anna_aigarth"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg text-white font-medium transition-all shadow-lg shadow-purple-500/25"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                  </svg>
                  Chat with @anna_aigarth
                </a>
              </div>
            </div>
          </div>

          {/* What is it */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-orange-400">
              <BookOpen className="w-4 h-4" />
              <h3 className="font-semibold">What is the Anna Matrix?</h3>
            </div>
            <div className="bg-white/5 rounded-xl p-4 space-y-3">
              <p className="text-sm text-gray-300 leading-relaxed">
                The <span className="text-orange-400 font-semibold">Anna Matrix</span> is a 128×128 grid of signed bytes
                (-128 to +127) discovered embedded in the original Qubic codebase by <span className="text-blue-400">Come-from-Beyond</span> (Sergey Ivancheglo).
              </p>
              <p className="text-sm text-gray-300 leading-relaxed">
                Named after the mysterious &quot;Anna&quot; referenced in early Qubic development, this matrix serves as a
                <span className="text-cyan-400 font-medium"> cryptographic lookup table</span> that potentially links
                Bitcoin&apos;s genesis block structures to the Qubic neural network architecture.
              </p>
              <div className="flex items-center gap-4 pt-2">
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-yellow-400" />
                  <span className="text-xs text-gray-400">Qortex Compatible</span>
                </div>
                <div className="flex items-center gap-2">
                  <Binary className="w-4 h-4 text-green-400" />
                  <span className="text-xs text-gray-400">Ternary Convertible</span>
                </div>
                <div className="flex items-center gap-2">
                  <ScanLine className="w-4 h-4 text-purple-400" />
                  <span className="text-xs text-gray-400">Pattern-Dense</span>
                </div>
              </div>
            </div>
          </div>

          {/* Origin */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-blue-400">
              <Hash className="w-4 h-4" />
              <h3 className="font-semibold">Origin & Technical Specifications</h3>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white/5 rounded-lg p-3">
                <div className="text-[10px] text-white/40 uppercase mb-1">Source</div>
                <div className="text-sm font-mono text-white">Qubic Core (2018)</div>
              </div>
              <div className="bg-white/5 rounded-lg p-3">
                <div className="text-[10px] text-white/40 uppercase mb-1">Author</div>
                <div className="text-sm text-white">Come-from-Beyond</div>
              </div>
              <div className="bg-white/5 rounded-lg p-3">
                <div className="text-[10px] text-white/40 uppercase mb-1">Dimensions</div>
                <div className="text-sm font-mono text-white">128 × 128</div>
              </div>
              <div className="bg-white/5 rounded-lg p-3">
                <div className="text-[10px] text-white/40 uppercase mb-1">Total Cells</div>
                <div className="text-sm font-mono text-white">16,384</div>
              </div>
              <div className="bg-white/5 rounded-lg p-3">
                <div className="text-[10px] text-white/40 uppercase mb-1">Data Type</div>
                <div className="text-sm font-mono text-white">int8 (signed byte)</div>
              </div>
              <div className="bg-white/5 rounded-lg p-3">
                <div className="text-[10px] text-white/40 uppercase mb-1">Value Range</div>
                <div className="text-sm font-mono text-white">-128 to +127</div>
              </div>
            </div>
          </div>

          {/* How to Verify */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-green-400">
              <FileCode className="w-4 h-4" />
              <h3 className="font-semibold">How to Verify & Reproduce</h3>
            </div>
            <div className="bg-white/5 rounded-xl p-4">
              <ol className="text-sm text-gray-300 space-y-3">
                <li className="flex gap-3">
                  <span className="w-6 h-6 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center text-xs font-bold shrink-0">1</span>
                  <div>
                    <div className="font-medium text-white">Download the matrix data</div>
                    <code className="text-xs bg-black/50 px-2 py-1 rounded mt-1 inline-block text-green-400">/data/anna-matrix.json</code>
                  </div>
                </li>
                <li className="flex gap-3">
                  <span className="w-6 h-6 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center text-xs font-bold shrink-0">2</span>
                  <div>
                    <div className="font-medium text-white">Verify SHA256 checksum</div>
                    <code className="text-xs bg-black/50 px-2 py-1 rounded mt-1 inline-block text-gray-400 break-all">sha256sum anna-matrix.json</code>
                  </div>
                </li>
                <li className="flex gap-3">
                  <span className="w-6 h-6 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center text-xs font-bold shrink-0">3</span>
                  <div>
                    <div className="font-medium text-white">Cross-reference with Patoshi blocks</div>
                    <span className="text-xs text-gray-400">Match public key bytes at row/col positions</span>
                  </div>
                </li>
              </ol>
            </div>
          </div>

          {/* Historical Bitcoin Artifacts */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-red-400">
              <Clock className="w-4 h-4" />
              <h3 className="font-semibold">Historical Bitcoin Artifacts</h3>
              <span className="px-2 py-0.5 bg-red-500/20 rounded-full text-[10px] text-red-300 uppercase">Critical</span>
            </div>

            <div className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/30 rounded-xl p-4 space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-red-600 to-orange-500 flex items-center justify-center shadow-lg shadow-red-500/30 shrink-0">
                  <Hash className="w-5 h-5 text-white" />
                </div>
                <div>
                  <div className="font-semibold text-white">Pre-Genesis Block (Hidden)</div>
                  <div className="text-xs text-gray-400">September 10, 2008 - Before public Bitcoin announcement</div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="text-[10px] text-white/40 uppercase">Block Hash (Never Published)</div>
                <div className="bg-black/50 rounded-lg p-3 font-mono text-xs text-orange-400 break-all border border-white/5">
                  0x000006b15d1327d67e971d1de9116bd60a3a01556c91b6ebaa416ebc0cfaa646
                </div>
                <p className="text-xs text-gray-400">
                  This hash was discovered in pre-release Bitcoin code from 2008 and was never part of the public blockchain.
                </p>
              </div>
            </div>

            {/* CFB Code Style Indicators */}
            <div className="bg-white/5 rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-green-400">
                <Code className="w-4 h-4" />
                <span className="font-medium text-sm">CFB Code Style Indicators</span>
              </div>
              <div className="space-y-2">
                <div className="flex items-start gap-3 bg-black/30 rounded-lg p-3">
                  <FileText className="w-4 h-4 text-green-400 shrink-0 mt-1" />
                  <div>
                    <div className="font-medium text-white text-sm">&quot;Four Slash&quot; Comments</div>
                    <code className="text-xs bg-black/50 px-2 py-1 rounded mt-1 block text-green-400 font-mono">
                      //// issue here: it doesn&apos;t know the version.
                    </code>
                    <p className="text-xs text-gray-400 mt-2">
                      Found in early Bitcoin code. CFB is known for idiosyncratic comment styles.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3 bg-black/30 rounded-lg p-3">
                  <Binary className="w-4 h-4 text-blue-400 shrink-0 mt-1" />
                  <div>
                    <div className="font-medium text-white text-sm">Integer-First Philosophy</div>
                    <p className="text-xs text-gray-400">
                      Early Bitcoin used &quot;Cents&quot; (10,000 units) instead of decimals.
                      CFB avoids floating-point (Qubic uses QUs as integers).
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sources */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-cyan-400">
              <ExternalLink className="w-4 h-4" />
              <h3 className="font-semibold">Sources & References</h3>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <a href="https://github.com/qubic/core" target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-2 bg-white/5 hover:bg-white/10 rounded-lg p-3 text-sm text-cyan-400 hover:text-cyan-300 transition-colors">
                <ExternalLink className="w-4 h-4 shrink-0" />
                <span>Qubic Core (GitHub)</span>
              </a>
              <a href="https://qubic.org" target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-2 bg-white/5 hover:bg-white/10 rounded-lg p-3 text-sm text-cyan-400 hover:text-cyan-300 transition-colors">
                <ExternalLink className="w-4 h-4 shrink-0" />
                <span>Qubic Official</span>
              </a>
              <a href="https://x.com/anna_aigarth" target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-2 bg-white/5 hover:bg-white/10 rounded-lg p-3 text-sm text-purple-400 hover:text-purple-300 transition-colors">
                <MessageCircle className="w-4 h-4 shrink-0" />
                <span>Anna AI (@anna_aigarth)</span>
              </a>
              <a href="/data/anna-matrix.json" download
                className="flex items-center gap-2 bg-white/5 hover:bg-white/10 rounded-lg p-3 text-sm text-green-400 hover:text-green-300 transition-colors">
                <Download className="w-4 h-4 shrink-0" />
                <span>Download JSON</span>
              </a>
            </div>
          </div>

          {/* Disclaimer */}
          <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-orange-400 shrink-0 mt-0.5" />
              <div className="text-sm">
                <div className="font-medium text-orange-400">Research Notice</div>
                <p className="text-gray-400 mt-1">
                  This visualization is provided for cryptographic research and educational purposes.
                  The relationship between the Anna Matrix and Bitcoin/Qubic is subject to ongoing investigation.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// =============================================================================
// KEYBOARD SHORTCUTS PANEL
// =============================================================================

function KeyboardShortcutsPanel({ onClose }: { onClose: () => void }) {
  const shortcuts = [
    { key: 'F', action: 'Toggle fullscreen' },
    { key: 'R', action: 'Reset camera' },
    { key: 'V', action: 'Toggle VIP markers' },
    { key: 'S', action: 'Toggle special rows' },
    { key: 'C', action: 'Toggle crosshair' },
    { key: 'M', action: 'Toggle minimap' },
    { key: 'I', action: 'Toggle info panel' },
    { key: 'T', action: 'Toggle 2D/3D view' },
    { key: 'B', action: 'Jump to Boot address' },
    { key: 'P', action: 'Jump to POCZ address' },
    { key: '1-5', action: 'Change view mode' },
    { key: 'W/↑', action: 'Navigate up' },
    { key: 'A/←', action: 'Navigate left' },
    { key: 'S/↓', action: 'Navigate down' },
    { key: 'D/→', action: 'Navigate right' },
    { key: 'Escape', action: 'Close panels / Deselect' },
    { key: '?', action: 'Show this help' },
  ]

  return (
    <div className="absolute inset-0 flex items-center justify-center bg-black/80 backdrop-blur-sm z-50 pointer-events-auto">
      <div className="bg-background border border-border rounded-xl p-6 max-w-md mx-4 shadow-2xl max-h-[80vh] overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Keyboard Shortcuts</h3>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
        <div className="space-y-2">
          {shortcuts.map(({ key, action }) => (
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

// =============================================================================
// MAIN SCENE COMPONENT
// =============================================================================

export default function AnnaGridScene() {
  const {
    loading,
    progress,
    error,
    matrix,
    stats,
    vipCells,
    getCell,
    getCellByAddress,
    getCellNeighbors,
    searchByValue,
    retry,
    retryCount,
  } = useAnnaGridData()

  // View states
  const [selectedCell, setSelectedCell] = useState<AnnaCell | null>(null)
  const [hoveredCell, setHoveredCell] = useState<{ row: number; col: number } | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('terrain')
  const [colorTheme, setColorTheme] = useState<ColorTheme>('default')
  const [displayMode, setDisplayMode] = useState<'3d' | '2d'>('3d')
  const [zoomRegion, setZoomRegion] = useState<'all' | 'q1' | 'q2' | 'q3' | 'q4'>('all')

  // Toggle states
  const [showVIPMarkers, setShowVIPMarkers] = useState(true)
  const [showSpecialRows, setShowSpecialRows] = useState(true)
  const [showCrosshair, setShowCrosshair] = useState(true)
  const [showMiniMap, setShowMiniMap] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)

  // Panel states
  const [showKeyboardShortcuts, setShowKeyboardShortcuts] = useState(false)
  const [showStats, setShowStats] = useState(false)
  const [showInfo, setShowInfo] = useState(false)
  const [showSearch, setShowSearch] = useState(false)
  const [showCoordInput, setShowCoordInput] = useState(false)
  const [showColorPicker, setShowColorPicker] = useState(false)

  const [cameraPreset, setCameraPreset] = useState<keyof typeof CAMERA_PRESETS>('overview')

  const containerRef = useRef<HTMLDivElement>(null)
  const controlsRef = useRef<any>(null)

  // VIP positions for markers
  const vipPositions = useMemo(() => {
    return stats?.vipPositions || []
  }, [stats])

  // Handle cell selection
  const handleCellClick = useCallback(
    (row: number, col: number) => {
      const cell = getCell(row, col)
      setSelectedCell(cell)
    },
    [getCell]
  )

  // Handle search
  const handleSearch = useCallback(
    (query: string): AnnaCell | null => {
      if (!query.trim()) return null

      const addressNum = parseInt(query, 10)
      if (!isNaN(addressNum) && addressNum >= 0 && addressNum < 16384) {
        return getCellByAddress(addressNum)
      }

      const match = query.match(/^(\d+)[,\s]+(\d+)$/)
      if (match && match[1] && match[2]) {
        const row = parseInt(match[1], 10)
        const col = parseInt(match[2], 10)
        return getCell(row, col)
      }

      const valueNum = parseInt(query, 10)
      if (!isNaN(valueNum) && valueNum >= -128 && valueNum <= 127) {
        const matches = searchByValue(valueNum)
        return matches[0] || null
      }

      return null
    },
    [getCell, getCellByAddress, searchByValue]
  )

  // Handle preset jumps
  const handleJumpToPreset = useCallback(
    (preset: 'boot' | 'pocz' | 'row21' | 'row68' | 'row96') => {
      let row = 0, col = 0
      switch (preset) {
        case 'boot':
          row = SPECIAL_ADDRESSES.boot.row
          col = SPECIAL_ADDRESSES.boot.col
          break
        case 'pocz':
          row = SPECIAL_ADDRESSES.pocz.row
          col = SPECIAL_ADDRESSES.pocz.col
          break
        case 'row21': row = 21; col = 0; break
        case 'row68': row = 68; col = 0; break
        case 'row96': row = 96; col = 0; break
      }
      const cell = getCell(row, col)
      if (cell) setSelectedCell(cell)
    },
    [getCell]
  )

  // Random discovery - jump to extreme value
  const handleRandomDiscovery = useCallback(() => {
    if (!matrix || !stats) return
    const threshold = 0.85
    const extremeCells: { row: number; col: number; value: number }[] = []
    for (let row = 0; row < 128; row++) {
      for (let col = 0; col < 128; col++) {
        const value = matrix[row]?.[col] ?? 0
        const normalized = (value - stats.min) / (stats.max - stats.min)
        if (normalized > threshold || normalized < (1 - threshold)) {
          extremeCells.push({ row, col, value })
        }
      }
    }
    if (extremeCells.length > 0) {
      const randomCell = extremeCells[Math.floor(Math.random() * extremeCells.length)]
      if (randomCell) {
        const cell = getCell(randomCell.row, randomCell.col)
        if (cell) setSelectedCell(cell)
      }
    }
  }, [matrix, stats, getCell])

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
    setCameraPreset('overview')
  }, [])

  // Export functionality
  const handleExport = useCallback(() => {
    if (!matrix || !stats) return

    const exportData = {
      timestamp: new Date().toISOString(),
      source: 'anna-matrix',
      dimensions: { rows: 128, cols: 128 },
      stats,
      selectedCell,
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `anna-matrix-export-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }, [matrix, stats, selectedCell])

  // Keyboard shortcuts with WASD navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement) return

      // WASD / Arrow navigation when cell is selected
      if (selectedCell) {
        let newRow = selectedCell.row
        let newCol = selectedCell.col
        let navigated = false

        switch (e.key.toLowerCase()) {
          case 'w':
          case 'arrowup':
            newRow = Math.max(0, selectedCell.row - 1)
            navigated = true
            break
          case 's':
          case 'arrowdown':
            newRow = Math.min(127, selectedCell.row + 1)
            navigated = true
            break
          case 'a':
          case 'arrowleft':
            newCol = Math.max(0, selectedCell.col - 1)
            navigated = true
            break
          case 'd':
          case 'arrowright':
            newCol = Math.min(127, selectedCell.col + 1)
            navigated = true
            break
        }

        if (navigated) {
          e.preventDefault()
          const cell = getCell(newRow, newCol)
          if (cell) setSelectedCell(cell)
          return
        }
      }

      switch (e.key.toLowerCase()) {
        case 'f':
          e.preventDefault()
          toggleFullscreen()
          break
        case 'r':
          if (!selectedCell) {
            e.preventDefault()
            resetCamera()
          }
          break
        case 'v':
          e.preventDefault()
          setShowVIPMarkers((v) => !v)
          break
        case 'c':
          e.preventDefault()
          setShowCrosshair((v) => !v)
          break
        case 'm':
          e.preventDefault()
          setShowMiniMap((v) => !v)
          break
        case 'i':
          e.preventDefault()
          setShowInfo((v) => !v)
          break
        case 't':
          e.preventDefault()
          setDisplayMode((m) => m === '3d' ? '2d' : '3d')
          break
        case 'escape':
          setSelectedCell(null)
          setShowKeyboardShortcuts(false)
          setShowInfo(false)
          setShowStats(false)
          setShowSearch(false)
          setShowCoordInput(false)
          break
        case '?':
          setShowKeyboardShortcuts((s) => !s)
          break
        case 'b':
          e.preventDefault()
          handleJumpToPreset('boot')
          break
        case 'p':
          e.preventDefault()
          handleJumpToPreset('pocz')
          break
        case '1': setViewMode('heatmap'); break
        case '2': setViewMode('terrain'); break
        case '3': setViewMode('wireframe'); break
        case '4': setViewMode('scientific'); break
        case '5': setViewMode('flat'); break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [selectedCell, getCell, toggleFullscreen, resetCamera, handleJumpToPreset])

  // Fullscreen change listener
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }, [])

  // Prevent page scroll on canvas
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const preventScroll = (e: WheelEvent) => {
      e.preventDefault()
    }

    container.addEventListener('wheel', preventScroll, { passive: false })
    return () => container.removeEventListener('wheel', preventScroll)
  }, [])

  if (loading) {
    return (
      <div ref={containerRef} className="w-full h-[700px] rounded-lg overflow-hidden border border-border">
        <LoadingScreen progress={progress} />
      </div>
    )
  }

  if (error) {
    return (
      <div ref={containerRef} className="w-full h-[700px] rounded-lg overflow-hidden border border-border">
        <ErrorScreen error={error} onRetry={retry} retryCount={retryCount} />
      </div>
    )
  }

  if (!matrix || !stats) return null

  const cameraPresetData = CAMERA_PRESETS[cameraPreset]
  const currentCameraPos: [number, number, number] = cameraPresetData?.position ?? [0, 15, 15]

  return (
    <div
      ref={containerRef}
      className={`relative w-full bg-black rounded-lg overflow-hidden border border-border transition-all duration-300 ${
        isFullscreen ? 'h-screen rounded-none' : 'h-[700px]'
      }`}
    >
      {/* 3D or 2D View */}
      {displayMode === '3d' ? (
        <Canvas gl={{ antialias: true, alpha: false }} dpr={[1, 2]}>
          <PerspectiveCamera makeDefault position={currentCameraPos} fov={50} />
          <OrbitControls
            ref={controlsRef}
            enableDamping
            dampingFactor={0.05}
            minDistance={3}
            maxDistance={30}
            maxPolarAngle={Math.PI / 2.1}
          />

          <ambientLight intensity={0.4} />
          <pointLight position={[10, 15, 10]} intensity={1} />
          <pointLight position={[-10, 15, -10]} intensity={0.5} color={COLOR_THEMES[colorTheme].negative} />
          <pointLight position={[10, 15, -10]} intensity={0.5} color={COLOR_THEMES[colorTheme].positive} />

          <Stars radius={100} depth={50} count={1500} factor={4} saturation={0} fade speed={0.3} />

          <Suspense fallback={null}>
            <GridMesh
              matrix={matrix}
              colorTheme={colorTheme}
              viewMode={viewMode}
              selectedCell={selectedCell}
              hoveredCell={hoveredCell}
              onCellHover={setHoveredCell}
              onCellClick={handleCellClick}
              showVIPMarkers={showVIPMarkers}
              showSpecialRows={showSpecialRows}
              showCrosshair={showCrosshair}
              vipPositions={vipPositions}
            />
          </Suspense>
        </Canvas>
      ) : (
        <Grid2DView
          matrix={matrix}
          stats={stats}
          colorTheme={colorTheme}
          selectedCell={selectedCell}
          onCellClick={handleCellClick}
          zoomRegion={zoomRegion}
        />
      )}

      {/* UI Overlay */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Top Left: Legend */}
        <div className="absolute top-4 left-4 bg-black/90 backdrop-blur-md border border-white/10 rounded-xl p-4 pointer-events-auto group">
          <div className="flex items-center gap-2 mb-3">
            <Grid3X3 className="w-5 h-5 text-orange-400" />
            <div>
              <div className="text-sm font-semibold text-white">Anna Matrix</div>
              <div className="text-[10px] text-gray-400">128 × 128 • {displayMode.toUpperCase()}</div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-[10px] text-white/50 uppercase">Value Scale ({COLOR_THEMES[colorTheme].name})</div>
            <div
              className="h-3 rounded-full cursor-help"
              style={{
                background: `linear-gradient(to right, ${COLOR_THEMES[colorTheme].negative}, ${COLOR_THEMES[colorTheme].neutral}, ${COLOR_THEMES[colorTheme].positive})`,
              }}
              title={`Range: ${stats.min} to ${stats.max} | Mean: ${stats.mean.toFixed(1)}`}
            />
            <div className="flex justify-between text-[10px] text-white/50">
              <span>{stats.min}</span>
              <span>0</span>
              <span>{stats.max}</span>
            </div>
          </div>

          <div className="mt-3 pt-3 border-t border-white/10 space-y-1">
            <div className="flex justify-between text-[10px]">
              <span className="text-blue-400">Negative</span>
              <span className="text-white/70 font-mono">{stats.negativeCount.toLocaleString()} ({((stats.negativeCount / stats.totalCells) * 100).toFixed(0)}%)</span>
            </div>
            <div className="flex justify-between text-[10px]">
              <span className="text-gray-400">Zero</span>
              <span className="text-white/70 font-mono">{stats.zeroCount.toLocaleString()} ({((stats.zeroCount / stats.totalCells) * 100).toFixed(0)}%)</span>
            </div>
            <div className="flex justify-between text-[10px]">
              <span className="text-orange-400">Positive</span>
              <span className="text-white/70 font-mono">{stats.positiveCount.toLocaleString()} ({((stats.positiveCount / stats.totalCells) * 100).toFixed(0)}%)</span>
            </div>
          </div>

          {selectedCell && (
            <div className="mt-3 pt-3 border-t border-white/10">
              <div className="text-[9px] text-white/30 uppercase">Navigate: WASD / Arrow keys</div>
            </div>
          )}
        </div>

        {/* Top Right: Controls */}
        <div className="absolute top-4 right-4 flex flex-col gap-2 pointer-events-auto">
          {/* Primary actions */}
          <div className="flex gap-1 bg-black/90 backdrop-blur-md border border-white/10 rounded-lg p-1">
            <Button variant="ghost" size="icon" className="h-8 w-8 text-white/70 hover:text-white hover:bg-white/10" onClick={toggleFullscreen} title="Fullscreen (F)">
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8 text-white/70 hover:text-white hover:bg-white/10" onClick={resetCamera} title="Reset Camera (R)">
              <RotateCcw className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={`h-8 w-8 ${displayMode === '2d' ? 'text-cyan-400 bg-cyan-400/20' : 'text-white/70 hover:text-white hover:bg-white/10'}`}
              onClick={() => setDisplayMode(displayMode === '3d' ? '2d' : '3d')}
              title="Toggle 2D/3D (T)"
            >
              <Table2 className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={`h-8 w-8 ${showCrosshair ? 'text-green-400 bg-green-400/20' : 'text-white/70 hover:text-white hover:bg-white/10'}`}
              onClick={() => setShowCrosshair(!showCrosshair)}
              title="Toggle Crosshair (C)"
            >
              <Crosshair className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={`h-8 w-8 ${showSearch ? 'text-yellow-400 bg-yellow-400/20' : 'text-white/70 hover:text-white hover:bg-white/10'}`}
              onClick={() => setShowSearch(!showSearch)}
              title="Search Value"
            >
              <Search className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={`h-8 w-8 ${showCoordInput ? 'text-purple-400 bg-purple-400/20' : 'text-white/70 hover:text-white hover:bg-white/10'}`}
              onClick={() => setShowCoordInput(!showCoordInput)}
              title="Jump to Cell"
            >
              <Target className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={`h-8 w-8 ${showStats ? 'text-orange-400 bg-orange-400/20' : 'text-white/70 hover:text-white hover:bg-white/10'}`}
              onClick={() => setShowStats(!showStats)}
              title="Statistics"
            >
              <BarChart3 className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={`h-8 w-8 ${showInfo ? 'text-cyan-400 bg-cyan-400/20' : 'text-white/70 hover:text-white hover:bg-white/10'}`}
              onClick={() => setShowInfo(!showInfo)}
              title="About Anna Matrix (I)"
            >
              <Info className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={`h-8 w-8 ${showMiniMap ? 'text-emerald-400 bg-emerald-400/20' : 'text-white/70 hover:text-white hover:bg-white/10'}`}
              onClick={() => setShowMiniMap(!showMiniMap)}
              title="Toggle MiniMap (M)"
            >
              <Map className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-white/70 hover:text-white hover:bg-white/10"
              onClick={handleRandomDiscovery}
              title="Random Discovery"
            >
              <Sparkles className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-white/70 hover:text-white hover:bg-white/10"
              onClick={() => setShowKeyboardShortcuts(true)}
              title="Keyboard Shortcuts (?)"
            >
              <Keyboard className="w-4 h-4" />
            </Button>
            <a
              href="/data/anna-matrix.json"
              download
              className="h-8 w-8 inline-flex items-center justify-center text-white/70 hover:text-white hover:bg-white/10 rounded-md"
              title="Download Matrix JSON"
            >
              <Download className="w-4 h-4" />
            </a>
          </div>

          {/* Color themes */}
          <div className="bg-black/90 backdrop-blur-md border border-white/10 rounded-lg p-1">
            <button
              onClick={() => setShowColorPicker(!showColorPicker)}
              className="flex items-center gap-2 px-2 py-1 text-[10px] text-gray-400 hover:text-white w-full"
            >
              <Palette className="w-3 h-3" />
              <span>Theme: {COLOR_THEMES[colorTheme].name}</span>
            </button>
            {showColorPicker && (
              <div className="grid grid-cols-5 gap-1 mt-1 p-1">
                {(Object.keys(COLOR_THEMES) as ColorTheme[]).map((theme) => (
                  <button
                    key={theme}
                    onClick={() => { setColorTheme(theme); setShowColorPicker(false) }}
                    className={`w-6 h-6 rounded ${colorTheme === theme ? 'ring-2 ring-white' : ''}`}
                    style={{ background: `linear-gradient(135deg, ${COLOR_THEMES[theme].negative}, ${COLOR_THEMES[theme].positive})` }}
                    title={COLOR_THEMES[theme].name}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Zoom regions (2D only) */}
          {displayMode === '2d' && (
            <div className="bg-black/90 backdrop-blur-md border border-white/10 rounded-lg p-1">
              <div className="text-[10px] text-gray-500 px-2 py-1">Zoom Region</div>
              <div className="grid grid-cols-3 gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  className={`h-7 text-xs col-span-3 ${zoomRegion === 'all' ? 'bg-white/20 text-white' : 'text-white/70 hover:text-white hover:bg-white/10'}`}
                  onClick={() => setZoomRegion('all')}
                >
                  Full 128×128
                </Button>
                {(['q1', 'q2', 'q3', 'q4'] as const).map((q, i) => (
                  <Button
                    key={q}
                    variant="ghost"
                    size="sm"
                    className={`h-6 text-[10px] ${zoomRegion === q ? 'bg-white/20 text-white' : 'text-white/70 hover:text-white hover:bg-white/10'}`}
                    onClick={() => setZoomRegion(q)}
                  >
                    Q{i + 1}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Camera presets (3D only) */}
          {displayMode === '3d' && (
            <div className="bg-black/90 backdrop-blur-md border border-white/10 rounded-lg p-1">
              <div className="text-[10px] text-gray-500 px-2 py-1">Camera</div>
              <div className="grid grid-cols-2 gap-1">
                {Object.entries(CAMERA_PRESETS).slice(0, 4).map(([key, preset]) => (
                  <Button
                    key={key}
                    variant="ghost"
                    size="sm"
                    className={`h-6 text-xs px-2 ${cameraPreset === key ? 'bg-white/20 text-white' : 'text-white/70 hover:text-white hover:bg-white/10'}`}
                    onClick={() => setCameraPreset(key as keyof typeof CAMERA_PRESETS)}
                  >
                    {preset.name}
                  </Button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Stats Panel */}
        {showStats && stats && <StatsPanel stats={stats} matrix={matrix} onClose={() => setShowStats(false)} />}

        {/* Info Panel */}
        {showInfo && <InfoPanel onClose={() => setShowInfo(false)} />}

        {/* Search Panel */}
        {showSearch && <SearchPanel matrix={matrix} stats={stats} onSelectCell={handleCellClick} onClose={() => setShowSearch(false)} />}

        {/* Coordinate Input */}
        {showCoordInput && <CoordinateInput onNavigate={handleCellClick} onClose={() => setShowCoordInput(false)} />}

        {/* Mini Map */}
        {showMiniMap && displayMode === '3d' && <MiniMap matrix={matrix} stats={stats} selectedCell={selectedCell} hoveredCell={hoveredCell} />}

        {/* Hover info (3D only, when no crosshair) */}
        {hoveredCell && !selectedCell && displayMode === '3d' && !showCrosshair && (
          <div className="absolute bottom-20 left-24 bg-black/95 backdrop-blur-md border border-white/10 rounded-lg px-3 py-2 pointer-events-none">
            <div className="flex items-center gap-3 text-sm">
              <span className="text-white/50 font-mono">[{hoveredCell.row}, {hoveredCell.col}]</span>
              <span className={`font-mono font-bold ${
                (matrix[hoveredCell.row]?.[hoveredCell.col] ?? 0) > 0 ? 'text-orange-400' :
                (matrix[hoveredCell.row]?.[hoveredCell.col] ?? 0) < 0 ? 'text-blue-400' : 'text-gray-400'
              }`}>
                {matrix[hoveredCell.row]?.[hoveredCell.col] ?? 0}
              </span>
            </div>
          </div>
        )}

        {/* Cell Detail Panel */}
        {selectedCell && (
          <CellDetailPanel
            cell={selectedCell}
            neighbors={getCellNeighbors(selectedCell.row, selectedCell.col)}
            onClose={() => setSelectedCell(null)}
            onNavigate={(row, col) => {
              const cell = getCell(row, col)
              if (cell) setSelectedCell(cell)
            }}
          />
        )}

        {/* Bottom Controls */}
        <AnnaGridControls
          viewMode={viewMode}
          colorTheme={colorTheme}
          showVIPMarkers={showVIPMarkers}
          showSpecialRows={showSpecialRows}
          stats={stats}
          selectedCell={selectedCell}
          onViewModeChange={setViewMode}
          onColorThemeChange={setColorTheme}
          onToggleVIP={() => setShowVIPMarkers((v) => !v)}
          onToggleSpecialRows={() => setShowSpecialRows((v) => !v)}
          onSearch={handleSearch}
          onCellFound={setSelectedCell}
          onJumpToPreset={handleJumpToPreset}
          onExport={handleExport}
        />

        {/* Keyboard shortcuts modal */}
        {showKeyboardShortcuts && <KeyboardShortcutsPanel onClose={() => setShowKeyboardShortcuts(false)} />}
      </div>

      {/* Watermark */}
      <div className="absolute bottom-16 left-4 text-[10px] text-white/20 pointer-events-none font-mono">
        Anna Matrix v2.0 • 128×128 • {stats.totalCells.toLocaleString()} cells • {COLOR_THEMES[colorTheme].name}
      </div>
    </div>
  )
}
