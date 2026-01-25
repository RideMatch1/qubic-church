'use client'

/**
 * NFTGalaxy - ULTRA SIMPLE - NO LAG
 * Just one sphere per star, nothing else
 */

import { useMemo } from 'react'
import { OrbitControls } from '@react-three/drei'
import { NFT_COLLECTION } from '@/config/nfts'
import type { NFT } from '@/config/nfts'

interface NFTGalaxyProps {
  onNFTClick: (nft: NFT) => void
}

// Simple background stars
function Starfield() {
  const positions = useMemo(() => {
    const count = 500
    const positions = new Float32Array(count * 3)

    for (let i = 0; i < count; i++) {
      const radius = 100 + Math.random() * 50
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)

      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
      positions[i * 3 + 2] = radius * Math.cos(phi)
    }

    return positions
  }, [])

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.3} color="#ffffff" transparent opacity={0.5} />
    </points>
  )
}

export function NFTGalaxy({ onNFTClick }: NFTGalaxyProps) {
  const nodes = useMemo(() => {
    return NFT_COLLECTION.map((nft) => {
      const x = (nft.position.x - 0.5) * 70
      const y = (nft.position.y - 0.5) * 70
      const z = ((nft.position.z ?? 0.5) - 0.5) * 70

      const colors = {
        legendary: '#FFD700',
        epic: '#A855F7',
        rare: '#3B82F6',
        common: '#ffffff',
      }

      return {
        id: nft.id,
        position: [x, y, z] as [number, number, number],
        color: colors[nft.rarity],
        nft,
      }
    })
  }, [])

  return (
    <>
      <color attach="background" args={['#000000']} />
      <ambientLight intensity={0.5} />
      <pointLight position={[50, 50, 50]} intensity={1} />

      <Starfield />

      {/* Simple spheres - one per NFT */}
      {nodes.map(({ id, position, color, nft }) => (
        <mesh
          key={id}
          position={position}
          onClick={(e) => {
            e.stopPropagation()
            onNFTClick(nft)
          }}
        >
          <sphereGeometry args={[1.5, 16, 16]} />
          <meshBasicMaterial color={color} />
        </mesh>
      ))}

      <OrbitControls
        enableZoom={false}
        enablePan={true}
        enableRotate={true}
        rotateSpeed={0.3}
        enableDamping={true}
        dampingFactor={0.05}
      />
    </>
  )
}
