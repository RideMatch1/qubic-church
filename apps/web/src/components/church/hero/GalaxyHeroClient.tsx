'use client'

/**
 * GalaxyHeroClient - PURE CLIENT COMPONENT
 * NO SERVER RENDERING AT ALL
 */

import { useState, useEffect } from 'react'
import { Canvas } from '@react-three/fiber'
import Image from 'next/image'
import { NFTGalaxy } from './NFTGalaxy'
import { NFTModal } from './NFTModal'
import { CHURCH_CONFIG } from '@/config/church'
import { NFT_COLLECTION } from '@/config/nfts'
import type { NFT } from '@/config/nfts'

function useCountdown(targetDate: Date) {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  })

  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = Date.now()
      const target = targetDate.getTime()
      const difference = target - now

      if (difference <= 0) {
        return { days: 0, hours: 0, minutes: 0, seconds: 0 }
      }

      return {
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
        minutes: Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60)),
        seconds: Math.floor((difference % (1000 * 60)) / 1000),
      }
    }

    setTimeLeft(calculateTimeLeft())

    const interval = setInterval(() => {
      setTimeLeft(calculateTimeLeft())
    }, 1000)

    return () => clearInterval(interval)
  }, [targetDate])

  return timeLeft
}

export function GalaxyHeroClient() {
  const [selectedNFT, setSelectedNFT] = useState<NFT>(NFT_COLLECTION[0]!)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [imageKey, setImageKey] = useState(0)
  const [mounted, setMounted] = useState(false)
  const countdown = useCountdown(CHURCH_CONFIG.countdown.targetDate)

  // Only render after mount to avoid hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  const handleNFTClick = (nft: NFT) => {
    setSelectedNFT(nft)
    setImageKey(prev => prev + 1)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
  }

  const soldNFTs = 47
  const totalNFTs = NFT_COLLECTION.length

  if (!mounted) {
    return (
      <section className="relative w-full h-screen overflow-hidden bg-black">
        <div className="absolute inset-0 bg-gradient-radial from-purple-900/20 via-blue-900/5 to-black" />
      </section>
    )
  }

  return (
    <section className="relative w-full h-screen overflow-hidden bg-black">
      {/* 3D Galaxy Canvas - MUST BE ON TOP */}
      <div className="absolute inset-0 z-10" style={{ touchAction: 'none' }}>
        <Canvas
          camera={{
            position: [0, 0, 50],
            fov: 60,
            near: 0.1,
            far: 1000,
          }}
          dpr={[1, 2]}
          gl={{
            antialias: true,
            alpha: true,
            powerPreference: 'high-performance',
          }}
          style={{ display: 'block', width: '100%', height: '100%' }}
        >
          <NFTGalaxy onNFTClick={handleNFTClick} />
        </Canvas>
      </div>

      {/* Countdown */}
      <div className="absolute top-24 md:top-32 lg:top-28 left-1/2 -translate-x-1/2 z-20 text-center">
        <div className="relative">
          <div className="absolute inset-0 scale-150 blur-3xl bg-white/5 animate-pulse-slow" />
          <h1
            className="text-4xl md:text-6xl lg:text-7xl font-mono tracking-wider text-white/95"
            style={{
              textShadow: '0 0 20px rgba(255, 255, 255, 0.5), 0 0 40px rgba(157, 78, 221, 0.3)',
            }}
          >
            {countdown.days.toString().padStart(3, '0')}.{countdown.hours.toString().padStart(2, '0')}.{countdown.minutes.toString().padStart(2, '0')}.{countdown.seconds.toString().padStart(2, '0')}
          </h1>
          <p className="text-white/60 text-xs md:text-sm uppercase tracking-[0.3em] mt-3 font-light">
            Until The Convergence
          </p>
        </div>
      </div>

      {/* NFT Stats */}
      <div className="absolute top-12 right-6 md:right-12 z-20">
        <div className="backdrop-blur-xl bg-black/40 border border-white/20 rounded-xl px-4 md:px-6 py-3 md:py-4">
          <div className="text-center">
            <div className="text-2xl md:text-3xl font-bold text-white">
              {soldNFTs}<span className="text-white/40">/{totalNFTs}</span>
            </div>
            <div className="text-[10px] md:text-xs text-white/60 uppercase tracking-wider mt-1">
              NFTs Claimed
            </div>
          </div>
        </div>
      </div>

      {/* NFT Display */}
      <div className="absolute right-0 md:right-8 lg:right-16 bottom-0 z-30 pointer-events-none" style={{ height: '110vh' }}>
        <div className="relative w-[220px] md:w-[380px] lg:w-[500px] h-full">
          <div className="absolute inset-0 scale-125 opacity-20 blur-3xl bg-gradient-radial from-purple-500 via-blue-500 to-transparent animate-pulse-slow" />

          <div
            key={imageKey}
            className="relative w-full h-full"
            style={{
              animation: 'fadeInScale 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
            }}
          >
            <Image
              src={selectedNFT.image}
              alt={selectedNFT.name}
              fill
              className="object-contain object-bottom drop-shadow-2xl"
              priority
              quality={95}
              sizes="(max-width: 768px) 220px, (max-width: 1024px) 380px, 500px"
            />
          </div>

          <div className="absolute bottom-4 left-2 right-2 md:bottom-6 md:left-4 md:right-4 backdrop-blur-xl bg-black/70 border border-white/30 rounded-lg md:rounded-xl px-3 py-2 md:px-4 md:py-3">
            <div className="flex items-center justify-between gap-2">
              <div className="min-w-0 flex-1">
                <h3 className="text-white font-semibold text-sm md:text-lg tracking-wide truncate">
                  {selectedNFT.name}
                </h3>
                <p className="text-white/70 text-[10px] md:text-xs mt-0.5 truncate">
                  {selectedNFT.title}
                </p>
              </div>
              <div className={`
                px-2 py-1 md:px-3 rounded-full text-[9px] md:text-xs font-semibold uppercase tracking-wider whitespace-nowrap flex-shrink-0
                ${selectedNFT.rarity === 'legendary' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50' : ''}
                ${selectedNFT.rarity === 'epic' ? 'bg-purple-500/20 text-purple-400 border border-purple-500/50' : ''}
                ${selectedNFT.rarity === 'rare' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50' : ''}
                ${selectedNFT.rarity === 'common' ? 'bg-gray-500/20 text-gray-400 border border-gray-500/50' : ''}
              `}>
                {selectedNFT.rarity}
              </div>
            </div>
          </div>
        </div>
      </div>

      <NFTModal
        nft={selectedNFT}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />

      <div className="absolute inset-0 pointer-events-none bg-gradient-radial from-transparent via-transparent to-black/80 z-40" />

      <div
        className="absolute inset-0 pointer-events-none opacity-[0.02] z-50"
        style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.1) 2px, rgba(255,255,255,0.1) 4px)',
        }}
      />

      <div className="absolute inset-0 pointer-events-none z-5">
        {[...Array(30)].map((_, i) => (
          <div
            key={i}
            className="absolute w-0.5 h-0.5 md:w-1 md:h-1 rounded-full bg-white/40"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animation: `float-cosmic ${6 + i * 0.4}s ease-in-out infinite`,
              animationDelay: `${i * 0.3}s`,
            }}
          />
        ))}
      </div>
    </section>
  )
}
