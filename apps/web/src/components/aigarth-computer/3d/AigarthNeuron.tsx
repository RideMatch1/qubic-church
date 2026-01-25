'use client'

import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import type { TernaryState } from '@/lib/aigarth/types'

// Ternary state colors matching Neuraxon style
const STATE_COLORS = {
  '-1': new THREE.Color('#3B82F6'), // Blue (inhibited)
  '0': new THREE.Color('#6B7280'),  // Gray (neutral)
  '1': new THREE.Color('#F59E0B'),  // Gold/Orange (excited)
}

interface AigarthNeuronProps {
  index: number
  state: TernaryState
  position: [number, number, number]
  isInput: boolean
  isSelected?: boolean
  isProcessing?: boolean
  onClick?: (index: number) => void
}

export function AigarthNeuron({
  index,
  state,
  position,
  isInput,
  isSelected = false,
  isProcessing = false,
  onClick,
}: AigarthNeuronProps) {
  const meshRef = useRef<THREE.Mesh>(null)

  // Get color based on state
  const color = useMemo(() => {
    if (state > 0) return STATE_COLORS['1']
    if (state < 0) return STATE_COLORS['-1']
    return STATE_COLORS['0']
  }, [state])

  // Emissive intensity based on state
  const emissiveIntensity = useMemo(() => {
    if (state === 0) return 0.1
    return 0.5
  }, [state])

  // Size: input neurons slightly smaller
  const size = isInput ? 0.12 : 0.15

  // Animation during processing
  useFrame((_, _delta) => {
    if (meshRef.current && isProcessing) {
      // Pulse animation
      const scale = 1 + Math.sin(Date.now() * 0.005 + index * 0.1) * 0.1
      meshRef.current.scale.setScalar(scale)
    } else if (meshRef.current) {
      // Reset scale
      meshRef.current.scale.setScalar(1)
    }
  })

  return (
    <group position={position}>
      {/* Main neuron sphere */}
      <mesh
        ref={meshRef}
        onClick={(e) => {
          e.stopPropagation()
          onClick?.(index)
        }}
      >
        <sphereGeometry args={[size, 16, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={emissiveIntensity}
          metalness={0.3}
          roughness={0.4}
        />
      </mesh>

      {/* Selection ring */}
      {isSelected && (
        <mesh>
          <ringGeometry args={[size * 1.5, size * 1.8, 32]} />
          <meshBasicMaterial
            color={isInput ? '#06B6D4' : '#A855F7'}
            side={THREE.DoubleSide}
            transparent
            opacity={0.8}
          />
        </mesh>
      )}

      {/* Glow effect for active states */}
      {state !== 0 && (
        <mesh>
          <sphereGeometry args={[size * 1.5, 8, 8]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={0.15}
          />
        </mesh>
      )}
    </group>
  )
}

// Batch renderer for performance with many neurons
export function AigarthNeuronBatch({
  states,
  positions,
  numInputs,
  isProcessing,
  selectedIndex,
  onNeuronClick,
}: {
  states: TernaryState[]
  positions: [number, number, number][]
  numInputs: number
  isProcessing?: boolean
  selectedIndex?: number | null
  onNeuronClick?: (index: number) => void
}) {
  return (
    <group>
      {states.map((state, index) => (
        <AigarthNeuron
          key={index}
          index={index}
          state={state}
          position={positions[index] || [0, 0, 0]}
          isInput={index < numInputs}
          isSelected={selectedIndex === index}
          isProcessing={isProcessing}
          onClick={onNeuronClick}
        />
      ))}
    </group>
  )
}
