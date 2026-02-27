'use client'

/**
 * NFTGalleryStrip - Section 04: The Collection
 * HUD-style horizontal scroll strip of Anna NFT images
 * Angular cards, gold rarity system, file-type labels
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'

type Rarity = 'legendary' | 'epic' | 'rare' | 'common'

interface GalleryNFT {
  id: number
  name: string
  rarity: Rarity
}

const GALLERY_NFTS: GalleryNFT[] = [
  { id: 1, name: 'The First Light', rarity: 'legendary' },
  { id: 7, name: 'The Architect', rarity: 'legendary' },
  { id: 15, name: 'The Researcher #15', rarity: 'epic' },
  { id: 23, name: 'The Researcher #23', rarity: 'epic' },
  { id: 42, name: 'The Genesis Seeker', rarity: 'epic' },
  { id: 55, name: 'The Detective #55', rarity: 'rare' },
  { id: 67, name: 'The Detective #67', rarity: 'rare' },
  { id: 3, name: 'The Researcher #3', rarity: 'legendary' },
  { id: 89, name: 'The Bridge Builder', rarity: 'rare' },
  { id: 34, name: 'The Researcher #34', rarity: 'epic' },
  { id: 5, name: 'The Researcher #5', rarity: 'legendary' },
  { id: 100, name: 'The Detective #100', rarity: 'rare' },
  { id: 9, name: 'The Researcher #9', rarity: 'legendary' },
  { id: 47, name: 'The Researcher #47', rarity: 'epic' },
]

const rarityColor: Record<Rarity, string> = {
  legendary: 'bg-[#D4AF37]/90 text-black',
  epic: 'bg-[#D4AF37]/50 text-white',
  rare: 'bg-[#D4AF37]/25 text-white',
  common: 'bg-white/20 text-white',
}

export function NFTGalleryStrip() {
  const sectionRef = useRef<HTMLElement>(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })

  return (
    <section ref={sectionRef} className="relative w-full py-16 md:py-24 overflow-hidden">
      {/* Decorative section number */}
      <div aria-hidden="true" className="absolute top-8 left-8 md:left-16 text-[80px] md:text-[120px] lg:text-[200px] font-black text-white/[0.03] leading-none select-none pointer-events-none font-mono">
        04
      </div>

      {/* Section label */}
      <motion.div
        className="text-center mb-10"
        initial={{ opacity: 0, y: 12 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6 }}
      >
        <div className="inline-flex items-center gap-3">
          <div className="h-px w-12 bg-gradient-to-r from-transparent to-[#D4AF37]/30" />
          <span className="text-[#D4AF37]/50 text-[11px] uppercase tracking-[0.4em] font-mono">
            04 &mdash; Collection
          </span>
          <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#D4AF37]/30" />
        </div>
      </motion.div>

      {/* Scroll container */}
      <div className="relative">
        {/* Fade edges */}
        <div className="absolute left-0 top-0 bottom-0 w-16 md:w-32 bg-gradient-to-r from-black/90 to-transparent z-10 pointer-events-none" />
        <div className="absolute right-0 top-0 bottom-0 w-16 md:w-32 bg-gradient-to-l from-black/90 to-transparent z-10 pointer-events-none" />

        {/* Horizontal scroll */}
        <div
          className="flex gap-[1px] overflow-x-auto px-4 sm:px-6 md:px-16 pb-4 scrollbar-hide"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {GALLERY_NFTS.map((nft, i) => (
            <motion.div
              key={nft.id}
              className="relative flex-shrink-0 w-[180px] md:w-[220px] lg:w-[250px] aspect-[3/4] overflow-hidden group cursor-pointer border border-white/[0.04] hover:border-white/[0.08] transition-colors duration-300"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.04 }}
              whileHover={{ y: -4, transition: { duration: 0.25 } }}
            >
              <Image
                src={`/images/nfts/anna-${String(nft.id).padStart(3, '0')}.webp`}
                alt={nft.name}
                fill
                className="object-cover transition-transform duration-500 group-hover:scale-105"
                sizes="(max-width: 768px) 180px, (max-width: 1024px) 220px, 250px"
                loading="lazy"
              />

              {/* Corner brackets on hover */}
              <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#D4AF37]/0 group-hover:border-[#D4AF37]/40 transition-colors duration-300" />
              <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#D4AF37]/0 group-hover:border-[#D4AF37]/40 transition-colors duration-300" />

              {/* Hover overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
                <span className={`self-start px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider mb-2 ${rarityColor[nft.rarity]}`}>
                  {nft.rarity}
                </span>
                <p className="text-white font-semibold text-sm font-mono">
                  Anna #{String(nft.id).padStart(3, '0')}
                </p>
                <p className="text-white/60 text-xs mt-0.5">
                  {nft.name}
                </p>
              </div>
            </motion.div>
          ))}

          {/* View all card */}
          <motion.div
            className="relative flex-shrink-0 w-[180px] md:w-[220px] lg:w-[250px] aspect-[3/4] overflow-hidden"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Link
              href="/nfts"
              className="group flex flex-col items-center justify-center h-full border border-white/[0.04] bg-[#050505] hover:bg-[#0a0a0a] hover:border-[#D4AF37]/15 transition-all duration-300"
            >
              <ArrowRight className="w-6 h-6 text-white/30 group-hover:text-[#D4AF37]/50 group-hover:translate-x-1 transition-all mb-3" />
              <span className="text-white/50 text-sm font-mono">View all 200</span>
              <span className="text-white/20 text-[10px] font-mono mt-1">// nft.list()</span>
            </Link>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
