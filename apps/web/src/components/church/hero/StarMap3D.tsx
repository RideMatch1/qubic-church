'use client'

/**
 * StarMap3D Component
 * Interactive 3D visualization of 200 Anna NFTs
 * Uses React Three Fiber for WebGL rendering
 */

import { Canvas } from '@react-three/fiber'
import { OrbitControls, Stars as DustStars, Html } from '@react-three/drei'
import { Suspense, useState, useRef, useMemo } from 'react'
import type { Mesh } from 'three'
import { NFT_COLLECTION } from '@/config/nfts'
import type { NFT, NFTRarity } from '@/config/nfts'

interface StarProps {
  nft: NFT
  onClick: (nft: NFT) => void
}

/**
 * Get color based on NFT rarity
 */
function getRarityColor(rarity: NFTRarity): string {
  switch (rarity) {
    case 'legendary':
      return '#FFD700' // Gold
    case 'epic':
      return '#9D4EDD' // Purple
    case 'rare':
      return '#4CC9F0' // Blue
    case 'common':
      return '#F8F9FA' // White
  }
}

/**
 * Get glow intensity based on rarity
 */
function getGlowIntensity(rarity: NFTRarity): number {
  switch (rarity) {
    case 'legendary':
      return 2.0
    case 'epic':
      return 1.5
    case 'rare':
      return 1.2
    case 'common':
      return 0.8
  }
}

/**
 * Individual Star (NFT)
 */
function Star({ nft, onClick }: StarProps) {
  const meshRef = useRef<Mesh>(null)
  const [hovered, setHovered] = useState(false)

  // Convert viewport positions to 3D coordinates
  // Spread stars across a 20x20x6 unit cube, centered at origin
  const position = useMemo(() => {
    const x = (nft.position.x - 0.5) * 20 // -10 to +10
    const y = (nft.position.y - 0.5) * 20 // -10 to +10
    const z = ((nft.position.z ?? 0.5) - 0.5) * 6 // -3 to +3
    return [x, y, z] as [number, number, number]
  }, [nft.position])

  const color = getRarityColor(nft.rarity)
  const baseIntensity = getGlowIntensity(nft.rarity)
  const glowIntensity = hovered ? baseIntensity * 2 : baseIntensity
  const scale = hovered ? 1.5 : 1

  return (
    <mesh
      ref={meshRef}
      position={position}
      scale={scale}
      onClick={(e) => {
        e.stopPropagation()
        onClick(nft)
      }}
      onPointerOver={(e) => {
        e.stopPropagation()
        setHovered(true)
        document.body.style.cursor = 'pointer'
      }}
      onPointerOut={() => {
        setHovered(false)
        document.body.style.cursor = 'default'
      }}
    >
      {/* Star sphere */}
      <sphereGeometry args={[0.15, 16, 16]} />
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={glowIntensity}
        toneMapped={false}
      />

      {/* Glow effect on hover */}
      {hovered && (
        <pointLight
          color={color}
          intensity={3}
          distance={5}
          decay={2}
        />
      )}

      {/* Tooltip on hover */}
      {hovered && (
        <Html
          position={[0, 0.5, 0]}
          center
          distanceFactor={10}
          style={{
            pointerEvents: 'none',
            userSelect: 'none',
            transition: 'opacity 0.2s',
          }}
        >
          <div className="bg-background/95 backdrop-blur-sm border border-border rounded-lg px-3 py-2 shadow-lg">
            <div className="text-sm font-semibold text-foreground whitespace-nowrap">
              {nft.name}
            </div>
            <div className="text-xs text-muted-foreground whitespace-nowrap">
              {nft.title}
            </div>
            {nft.owner && (
              <div className="text-xs text-green-500 mt-1 whitespace-nowrap">
                ✓ Owned
              </div>
            )}
          </div>
        </Html>
      )}
    </mesh>
  )
}

/**
 * Scene with all stars
 */
function StarField({ onStarClick }: { onStarClick: (nft: NFT) => void }) {
  return (
    <>
      {/* Ambient lighting */}
      <ambientLight intensity={0.3} />

      {/* Main directional light */}
      <directionalLight position={[10, 10, 5]} intensity={0.5} />

      {/* Background dust stars */}
      <DustStars
        radius={100}
        depth={50}
        count={5000}
        factor={4}
        saturation={0}
        fade
        speed={1}
      />

      {/* NFT Stars */}
      {NFT_COLLECTION.map((nft) => (
        <Star key={nft.id} nft={nft} onClick={onStarClick} />
      ))}
    </>
  )
}

/**
 * Loading fallback
 */
function LoadingFallback() {
  return (
    <Html center>
      <div className="flex items-center gap-2 text-foreground">
        <div className="animate-spin h-5 w-5 border-2 border-primary border-t-transparent rounded-full" />
        <span className="text-sm">Loading Star Map...</span>
      </div>
    </Html>
  )
}

/**
 * Main StarMap3D Component
 */
interface StarMap3DProps {
  onStarClick?: (nft: NFT) => void
  className?: string
}

export function StarMap3D({ onStarClick, className = '' }: StarMap3DProps) {
  const handleStarClick = (nft: NFT) => {
    if (onStarClick) {
      onStarClick(nft)
    }
  }

  return (
    <div className={`w-full h-full ${className}`}>
      <Canvas
        camera={{
          position: [0, 0, 25],
          fov: 50,
          near: 0.1,
          far: 200,
        }}
        dpr={[1, 2]} // Pixel ratio for sharp rendering
        gl={{
          antialias: true,
          alpha: true,
        }}
        style={{
          background: 'transparent',
        }}
      >
        <Suspense fallback={<LoadingFallback />}>
          <StarField onStarClick={handleStarClick} />

          {/* Camera controls */}
          <OrbitControls
            enableZoom={true}
            enablePan={true}
            enableRotate={true}
            zoomSpeed={0.6}
            panSpeed={0.5}
            rotateSpeed={0.4}
            minDistance={10}
            maxDistance={50}
            maxPolarAngle={Math.PI}
            minPolarAngle={0}
            // Smooth damping
            enableDamping={true}
            dampingFactor={0.05}
            // Mobile touch support
            touches={{
              ONE: 2, // Rotate
              TWO: 0, // Zoom
            }}
          />
        </Suspense>
      </Canvas>
    </div>
  )
}
