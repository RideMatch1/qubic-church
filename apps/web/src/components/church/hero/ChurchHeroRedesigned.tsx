'use client'

/**
 * ChurchHeroRedesigned Component
 * Fullscreen hero with starfield, countdown, and Anna NFT showcase
 * Design inspired by original Qubic Church
 */

import { useState, useEffect, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Points, PointMaterial } from '@react-three/drei'
import * as THREE from 'three'
import { CHURCH_CONFIG } from '@/config/church'
import { NFT_COLLECTION } from '@/config/nfts'
import Image from 'next/image'

/**
 * Starfield background with small particles
 */
function Starfield() {
  const ref = useRef<THREE.Points>(null)

  // Generate random star positions
  const [positions] = useState(() => {
    const positions = new Float32Array(5000 * 3)
    for (let i = 0; i < 5000; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 100
      positions[i * 3 + 1] = (Math.random() - 0.5) * 100
      positions[i * 3 + 2] = (Math.random() - 0.5) * 50
    }
    return positions
  })

  // Slow rotation
  useFrame((state, delta) => {
    if (ref.current) {
      ref.current.rotation.x -= delta / 20
      ref.current.rotation.y -= delta / 30
    }
  })

  return (
    <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#ffffff"
        size={0.05}
        sizeAttenuation={true}
        depthWrite={false}
      />
    </Points>
  )
}

/**
 * Countdown hook
 */
function useCountdown(targetDate: Date) {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  })

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date().getTime()
      const target = targetDate.getTime()
      const difference = target - now

      if (difference <= 0) {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 })
        clearInterval(interval)
        return
      }

      setTimeLeft({
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
        minutes: Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60)),
        seconds: Math.floor((difference % (1000 * 60)) / 1000),
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [targetDate])

  return timeLeft
}

/**
 * Rotating Anna NFT showcase
 */
function AnnaShowcase() {
  const [currentIndex, setCurrentIndex] = useState(0)

  // Rotate through featured NFTs every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % featuredNFTs.length)
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  // Select 10 featured NFTs (legendary, epic, and some with research connections)
  const featuredNFTs = NFT_COLLECTION.filter(
    (nft) => nft.rarity === 'legendary' || nft.rarity === 'epic' || nft.researchConnection
  ).slice(0, 10)

  const currentNFT = featuredNFTs[currentIndex]

  if (!currentNFT) return null

  return (
    <div className="relative">
      {/* Anna NFT Image with glow */}
      <div className="relative w-64 h-64 md:w-96 md:h-96">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/30 to-purple-500/30 rounded-full blur-3xl animate-pulse" />
        <div className="relative rounded-full overflow-hidden border-4 border-primary/50 shadow-2xl">
          <Image
            src={currentNFT.image}
            alt={currentNFT.name}
            width={384}
            height={384}
            className="object-cover"
            priority
          />
        </div>
      </div>

      {/* NFT Info */}
      <div className="mt-6 text-center">
        <div className="text-2xl font-bold mb-2">{currentNFT.name}</div>
        <div className="text-lg text-muted-foreground">{currentNFT.title}</div>
        {currentNFT.researchConnection && (
          <div className="mt-2 text-sm text-primary">
            🔗 {currentNFT.researchConnection.title}
          </div>
        )}
      </div>

      {/* Progress indicators */}
      <div className="flex justify-center gap-2 mt-4">
        {featuredNFTs.map((_, idx) => (
          <div
            key={idx}
            className={`w-2 h-2 rounded-full transition-all ${
              idx === currentIndex ? 'bg-primary w-8' : 'bg-muted-foreground/30'
            }`}
          />
        ))}
      </div>
    </div>
  )
}

export function ChurchHeroRedesigned() {
  const countdown = useCountdown(CHURCH_CONFIG.countdown.targetDate)

  return (
    <section className="relative w-full min-h-screen overflow-hidden bg-black">
      {/* 3D Starfield Background */}
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 10], fov: 75 }}>
          <Starfield />
        </Canvas>
      </div>

      {/* Content Layer */}
      <div className="relative z-10 min-h-screen flex items-center justify-center">
        <div className="container mx-auto px-4 py-20">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Side - Countdown */}
            <div className="text-center lg:text-left space-y-8">
              {/* Title */}
              <div>
                <h1 className="text-5xl md:text-7xl font-bold mb-4 bg-gradient-to-r from-white via-primary to-purple-500 bg-clip-text text-transparent">
                  {CHURCH_CONFIG.mission.title}
                </h1>
                <p className="text-xl md:text-2xl text-gray-400">
                  {CHURCH_CONFIG.countdown.label}
                </p>
              </div>

              {/* Massive Countdown Timer */}
              <div className="relative">
                {/* Glow effect */}
                <div className="absolute inset-0 bg-primary/20 blur-3xl" />

                {/* Timer */}
                <div className="relative bg-black/50 backdrop-blur-sm border-2 border-primary/30 rounded-2xl p-8 md:p-12">
                  <div className="flex items-center justify-center gap-4 font-mono text-6xl md:text-8xl font-bold">
                    <div className="flex flex-col items-center">
                      <span className="text-white">{countdown.days.toString().padStart(3, '0')}</span>
                      <span className="text-xs md:text-sm text-gray-400 mt-2 uppercase tracking-wider">Days</span>
                    </div>
                    <span className="text-primary animate-pulse">.</span>
                    <div className="flex flex-col items-center">
                      <span className="text-white">{countdown.hours.toString().padStart(2, '0')}</span>
                      <span className="text-xs md:text-sm text-gray-400 mt-2 uppercase tracking-wider">Hours</span>
                    </div>
                    <span className="text-primary animate-pulse">.</span>
                    <div className="flex flex-col items-center">
                      <span className="text-white">{countdown.minutes.toString().padStart(2, '0')}</span>
                      <span className="text-xs md:text-sm text-gray-400 mt-2 uppercase tracking-wider">Min</span>
                    </div>
                    <span className="text-primary animate-pulse">.</span>
                    <div className="flex flex-col items-center">
                      <span className="text-white">{countdown.seconds.toString().padStart(2, '0')}</span>
                      <span className="text-xs md:text-sm text-gray-400 mt-2 uppercase tracking-wider">Sec</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Subtitle */}
              <div className="text-center lg:text-left">
                <p className="text-lg text-gray-300">
                  {CHURCH_CONFIG.mission.subtitle}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  {CHURCH_CONFIG.collection.total} Unique Anna NFTs
                </p>
              </div>
            </div>

            {/* Right Side - Anna NFT Showcase */}
            <div className="flex items-center justify-center">
              <AnnaShowcase />
            </div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-10 animate-bounce">
        <div className="flex flex-col items-center gap-2 text-gray-400">
          <span className="text-sm uppercase tracking-wider">Scroll</span>
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
        </div>
      </div>
    </section>
  )
}
