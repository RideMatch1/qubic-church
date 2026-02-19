'use client'

import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Html, Line, Text } from '@react-three/drei'
import * as THREE from 'three'
import {
  DISCOVERIES,
  PATTERN_LINES,
  SPECIAL_ROW_SUMS,
  type Discovery,
  type PatternLine,
} from './discoveries'
import { MATRIX_SIZE } from './constants'

// =============================================================================
// HELPER: Convert matrix position to 3D coordinates
// =============================================================================

function matrixTo3D(
  row: number,
  col: number,
  gridScale: number = 10
): [number, number, number] {
  const cellSize = gridScale / MATRIX_SIZE
  const x = (col - MATRIX_SIZE / 2) * cellSize + cellSize / 2
  const z = (MATRIX_SIZE / 2 - row) * cellSize - cellSize / 2
  return [x, 0.15, z]
}

// =============================================================================
// DISCOVERY MARKER COMPONENT
// =============================================================================

function DiscoveryMarker({
  discovery,
  showLabels,
  animate,
}: {
  discovery: Discovery
  showLabels: boolean
  animate: boolean
}) {
  const groupRef = useRef<THREE.Group>(null)
  const ringRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (animate && ringRef.current) {
      ringRef.current.rotation.z = state.clock.elapsedTime * 0.5
      const scale = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.1
      ringRef.current.scale.setScalar(scale)
    }
    if (animate && groupRef.current) {
      groupRef.current.position.y = 0.15 + Math.sin(state.clock.elapsedTime * 1.5) * 0.05
    }
  })

  if (!discovery.positions || discovery.positions.length === 0) return null

  const color = new THREE.Color(discovery.color)
  const gridScale = 10

  return (
    <group ref={groupRef}>
      {discovery.positions.map((pos, idx) => {
        const [x, y, z] = matrixTo3D(pos.row, pos.col, gridScale)
        return (
          <group key={`${discovery.id}-${idx}`} position={[x, y, z]}>
            {/* Glowing ring */}
            <mesh ref={idx === 0 ? ringRef : undefined} rotation={[-Math.PI / 2, 0, 0]}>
              <ringGeometry args={[0.04, 0.06, 32]} />
              <meshBasicMaterial
                color={color}
                transparent
                opacity={0.8}
                side={THREE.DoubleSide}
              />
            </mesh>

            {/* Inner dot */}
            <mesh rotation={[-Math.PI / 2, 0, 0]}>
              <circleGeometry args={[0.02, 16]} />
              <meshBasicMaterial color={color} />
            </mesh>

            {/* Vertical beam */}
            <mesh position={[0, 0.3, 0]}>
              <cylinderGeometry args={[0.005, 0.005, 0.6, 8]} />
              <meshBasicMaterial color={color} transparent opacity={0.4} />
            </mesh>

            {/* Label */}
            {showLabels && pos.label && (
              <Html
                position={[0, 0.7, 0]}
                center
                style={{
                  pointerEvents: 'none',
                  userSelect: 'none',
                }}
              >
                <div
                  className="whitespace-nowrap rounded-md px-2 py-1 text-xs font-mono"
                  style={{
                    backgroundColor: `${discovery.color}CC`,
                    color: 'white',
                    boxShadow: `0 0 10px ${discovery.glowColor}`,
                  }}
                >
                  {pos.label}
                </div>
              </Html>
            )}
          </group>
        )
      })}

      {/* Connection lines between positions */}
      {discovery.positions.length > 1 && (
        <Line
          points={discovery.positions.map((p) => matrixTo3D(p.row, p.col, gridScale))}
          color={discovery.color}
          lineWidth={2}
          transparent
          opacity={0.6}
        />
      )}
    </group>
  )
}

// =============================================================================
// PATTERN LINE COMPONENT
// =============================================================================

function PatternLineOverlay({
  pattern,
  visible,
}: {
  pattern: PatternLine
  visible: boolean
}) {
  if (!visible) return null

  const gridScale = 10
  const points = pattern.points.map((p) => matrixTo3D(p.row, p.col, gridScale))

  return (
    <Line
      points={points}
      color={pattern.color}
      lineWidth={pattern.type === 'horizontal' ? 1 : 2}
      transparent
      opacity={pattern.type === 'horizontal' ? 0.3 : 0.6}
      dashed={pattern.type === 'horizontal'}
      dashSize={0.05}
      gapSize={0.02}
    />
  )
}

// =============================================================================
// ROW HIGHLIGHT COMPONENT
// =============================================================================

function RowHighlight({
  row,
  color,
  meaning,
  showLabel,
}: {
  row: number
  color: string
  meaning: string
  showLabel: boolean
}) {
  const gridScale = 10
  const cellSize = gridScale / MATRIX_SIZE
  const z = (MATRIX_SIZE / 2 - row) * cellSize - cellSize / 2
  const width = gridScale

  return (
    <group position={[0, 0.05, z]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[width, cellSize]} />
        <meshBasicMaterial color={color} transparent opacity={0.15} side={THREE.DoubleSide} />
      </mesh>
      {showLabel && (
        <Html position={[-gridScale / 2 - 0.3, 0.1, 0]} center>
          <div
            className="whitespace-nowrap rounded px-1.5 py-0.5 text-[10px] font-mono"
            style={{ backgroundColor: `${color}CC`, color: 'white' }}
          >
            R{row}: {meaning}
          </div>
        </Html>
      )}
    </group>
  )
}

// =============================================================================
// CORNER MARKERS
// =============================================================================

function CornerMarkers({ visible }: { visible: boolean }) {
  if (!visible) return null

  const gridScale = 10
  const corners = [
    { row: 0, col: 0, label: 'α-α', value: -68 },
    { row: 0, col: 127, label: 'α-ω', value: 91 },
    { row: 127, col: 0, label: 'ω-α', value: -92 },
    { row: 127, col: 127, label: 'ω-ω', value: 67 },
  ]

  return (
    <group>
      {corners.map((corner) => {
        const [x, y, z] = matrixTo3D(corner.row, corner.col, gridScale)
        return (
          <group key={corner.label} position={[x, y, z]}>
            <mesh>
              <boxGeometry args={[0.1, 0.3, 0.1]} />
              <meshBasicMaterial color="#06B6D4" transparent opacity={0.7} />
            </mesh>
            <Html position={[0, 0.3, 0]} center>
              <div className="whitespace-nowrap rounded bg-cyan-500/90 px-1.5 py-0.5 text-[10px] font-mono text-white">
                {corner.label}: {corner.value}
              </div>
            </Html>
          </group>
        )
      })}

      {/* XOR = 0 indicator at center */}
      <Html position={[0, 1, 0]} center>
        <div className="rounded-lg bg-cyan-500/80 px-3 py-1.5 text-sm font-bold text-white shadow-lg">
          XOR = 0
        </div>
      </Html>
    </group>
  )
}

// =============================================================================
// ZZZ MAGIC SQUARE HIGHLIGHT
// =============================================================================

function ZZZMagicSquare({ visible }: { visible: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (meshRef.current && meshRef.current.material) {
      const mat = meshRef.current.material as THREE.MeshBasicMaterial
      if (mat.opacity !== undefined) {
        mat.opacity = 0.3 + Math.sin(state.clock.elapsedTime * 2) * 0.15
      }
    }
  })

  if (!visible) return null

  const gridScale = 10
  const cellSize = gridScale / MATRIX_SIZE
  // Center of 3x3 square starting at (36, 36)
  const [x, , z] = matrixTo3D(37, 37, gridScale)

  return (
    <group position={[x, 0.1, z]}>
      <mesh ref={meshRef} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[cellSize * 3, cellSize * 3]} />
        <meshBasicMaterial color="#22C55E" transparent opacity={0.4} side={THREE.DoubleSide} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <ringGeometry args={[cellSize * 1.5, cellSize * 1.7, 6]} />
        <meshBasicMaterial color="#22C55E" transparent opacity={0.6} side={THREE.DoubleSide} />
      </mesh>
      <Html position={[0, 0.5, 0]} center>
        <div className="rounded-lg bg-green-500/90 px-3 py-1.5 text-sm font-bold text-white shadow-lg">
          ZZZ Magic Square
        </div>
      </Html>
    </group>
  )
}

// =============================================================================
// MAIN DISCOVERIES OVERLAY COMPONENT
// =============================================================================

export interface DiscoveriesOverlayProps {
  showEasterEggs: boolean
  showMathematical: boolean
  showSymmetry: boolean
  showWordEncodings: boolean
  showBitcoinConnections: boolean
  showPatternLines: boolean
  showRowHighlights: boolean
  showLabels: boolean
  animate: boolean
  activeDiscoveryId?: string | null
}

export function DiscoveriesOverlay({
  showEasterEggs,
  showMathematical,
  showSymmetry,
  showWordEncodings,
  showBitcoinConnections,
  showPatternLines,
  showRowHighlights,
  showLabels,
  animate,
  activeDiscoveryId,
}: DiscoveriesOverlayProps) {
  // Filter discoveries by category visibility
  const visibleDiscoveries = useMemo(() => {
    return DISCOVERIES.filter((d) => {
      if (activeDiscoveryId && d.id !== activeDiscoveryId) return false
      switch (d.category) {
        case 'easter-egg':
          return showEasterEggs
        case 'mathematical':
          return showMathematical
        case 'symmetry':
          return showSymmetry
        case 'word-encoding':
          return showWordEncodings
        case 'bitcoin-connection':
          return showBitcoinConnections
        case 'balance':
        case 'special-value':
          return showMathematical || showEasterEggs
        default:
          return false
      }
    })
  }, [
    showEasterEggs,
    showMathematical,
    showSymmetry,
    showWordEncodings,
    showBitcoinConnections,
    activeDiscoveryId,
  ])

  // Get special rows to highlight
  const rowsToHighlight = useMemo(() => {
    if (!showRowHighlights) return []
    return Object.entries(SPECIAL_ROW_SUMS).map(([row, data]) => ({
      row: parseInt(row),
      ...data,
    }))
  }, [showRowHighlights])

  return (
    <group>
      {/* Discovery markers */}
      {visibleDiscoveries.map((discovery) => (
        <DiscoveryMarker
          key={discovery.id}
          discovery={discovery}
          showLabels={showLabels}
          animate={animate}
        />
      ))}

      {/* Pattern lines */}
      {showPatternLines &&
        PATTERN_LINES.map((pattern) => (
          <PatternLineOverlay key={pattern.id} pattern={pattern} visible={true} />
        ))}

      {/* Row highlights */}
      {rowsToHighlight.map((row) => (
        <RowHighlight
          key={row.row}
          row={row.row}
          color={row.color}
          meaning={row.meaning}
          showLabel={showLabels}
        />
      ))}

      {/* Corner markers for XOR symmetry */}
      <CornerMarkers visible={showSymmetry} />

      {/* ZZZ Magic Square */}
      <ZZZMagicSquare visible={showEasterEggs} />
    </group>
  )
}

export default DiscoveriesOverlay
