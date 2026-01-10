'use client'

/**
 * ChurchHero Component
 * Main hero section with interactive 3D star map
 */

import { useState } from 'react'
import { StarMap3D } from './StarMap3D'
import { NFTModal } from './NFTModal'
import type { NFT } from '@/config/nfts'
import { CHURCH_CONFIG } from '@/config/church'
import { ArrowDown } from 'lucide-react'

export function ChurchHero() {
  const [selectedNFT, setSelectedNFT] = useState<NFT | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleStarClick = (nft: NFT) => {
    setSelectedNFT(nft)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    // Delay clearing selectedNFT to allow modal exit animation
    setTimeout(() => setSelectedNFT(null), 200)
  }

  return (
    <section className="relative min-h-screen w-full overflow-hidden bg-gradient-to-b from-background via-background/95 to-background">
      {/* Content Overlay */}
      <div className="absolute inset-0 z-10 pointer-events-none">
        <div className="container mx-auto px-4 h-full flex flex-col">
          {/* Top Section - Title & Mission */}
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-6 max-w-4xl pointer-events-auto">
              {/* Title */}
              <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight">
                <span className="inline-block animate-pulse">✨</span>
                <span className="bg-gradient-to-r from-primary via-purple-500 to-primary bg-clip-text text-transparent animate-gradient">
                  {' '}
                  {CHURCH_CONFIG.mission.title}{' '}
                </span>
                <span className="inline-block animate-pulse">✨</span>
              </h1>

              {/* Mission Statement */}
              <p className="text-xl md:text-2xl text-muted-foreground leading-relaxed">
                {CHURCH_CONFIG.mission.subtitle}
              </p>

              {/* Collection Info */}
              <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-full px-6 py-3">
                <span className="text-sm font-medium text-muted-foreground">
                  {CHURCH_CONFIG.collection.total} Unique NFTs
                </span>
                <span className="text-muted-foreground/50">•</span>
                <span className="text-sm font-medium text-primary">
                  Click Stars to Explore
                </span>
              </div>
            </div>
          </div>

          {/* Bottom Section - Scroll Hint */}
          <div className="pb-8 flex justify-center">
            <div className="animate-bounce">
              <ArrowDown className="w-6 h-6 text-muted-foreground" />
            </div>
          </div>
        </div>
      </div>

      {/* 3D Star Map Background */}
      <div className="absolute inset-0 z-0">
        <StarMap3D onStarClick={handleStarClick} />
      </div>

      {/* NFT Modal */}
      <NFTModal
        nft={selectedNFT}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </section>
  )
}
