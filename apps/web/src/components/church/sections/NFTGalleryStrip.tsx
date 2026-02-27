'use client'

/**
 * NFTGalleryStrip - Section 08: The Collection
 * HUD-style horizontal scroll strip of Anna NFT images
 * No rarity system — all NFTs equal as founder tokens
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import Image from 'next/image'
import { ArrowRight, ExternalLink } from 'lucide-react'

const GALLERY_NFTS = [1, 7, 15, 23, 42, 55, 67, 3, 89, 34, 5, 100, 9, 47]

export function NFTGalleryStrip() {
  const sectionRef = useRef<HTMLElement>(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })

  return (
    <section ref={sectionRef} className="relative w-full py-16 md:py-24 overflow-hidden">
      {/* Decorative section number */}
      <div aria-hidden="true" className="absolute top-8 left-8 md:left-16 text-[80px] md:text-[120px] lg:text-[200px] font-black text-white/[0.03] leading-none select-none pointer-events-none font-mono">
        08
      </div>

      {/* Section label + title */}
      <motion.div
        className="text-center mb-10"
        initial={{ opacity: 0, y: 12 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6 }}
      >
        <div className="inline-flex items-center gap-3 mb-6">
          <div className="h-px w-12 bg-gradient-to-r from-transparent to-[#D4AF37]/30" />
          <span className="text-[#D4AF37]/50 text-[11px] uppercase tracking-[0.4em] font-mono">
            08 &mdash; Collection
          </span>
          <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#D4AF37]/30" />
        </div>
        <p className="text-sm text-white/30 max-w-lg mx-auto leading-relaxed">
          200 unique Relics forged in aNNa&apos;s image &mdash; each one a key to the Sanctuary.
          Hold one to become a Founder.
        </p>
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
          {GALLERY_NFTS.map((id, i) => (
            <motion.div
              key={id}
              className="relative flex-shrink-0 w-[180px] md:w-[220px] lg:w-[250px] aspect-[3/4] overflow-hidden group cursor-pointer border border-white/[0.04] hover:border-white/[0.08] transition-colors duration-300"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.04 }}
              whileHover={{ y: -4, transition: { duration: 0.25 } }}
            >
              <Image
                src={`/images/nfts/anna-${String(id).padStart(3, '0')}.webp`}
                alt={`Anna #${String(id).padStart(3, '0')}`}
                fill
                className="object-cover transition-transform duration-500 group-hover:scale-105"
                sizes="(max-width: 768px) 180px, (max-width: 1024px) 220px, 250px"
                loading="lazy"
              />

              {/* Corner brackets on hover */}
              <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#D4AF37]/0 group-hover:border-[#D4AF37]/40 transition-colors duration-300" />
              <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#D4AF37]/0 group-hover:border-[#D4AF37]/40 transition-colors duration-300" />

              {/* Hover overlay — simple label, no rarity */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
                <p className="text-white font-semibold text-sm font-mono">
                  Anna #{String(id).padStart(3, '0')}
                </p>
                <p className="text-white/40 text-[10px] font-mono mt-1">
                  Founder Relic
                </p>
              </div>
            </motion.div>
          ))}

          {/* Become a Founder card */}
          <motion.div
            className="relative flex-shrink-0 w-[180px] md:w-[220px] lg:w-[250px] aspect-[3/4] overflow-hidden"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <a
              href="https://qubicbay.io/collections/7"
              target="_blank"
              rel="noopener noreferrer"
              className="group flex flex-col items-center justify-center h-full border border-white/[0.04] bg-[#050505] hover:bg-[#0a0a0a] hover:border-[#D4AF37]/15 transition-all duration-300"
            >
              <ArrowRight className="w-6 h-6 text-white/30 group-hover:text-[#D4AF37]/50 group-hover:translate-x-1 transition-all mb-3" />
              <span className="text-white/50 text-sm font-mono">Become a Founder</span>
              <span className="text-white/20 text-[10px] font-mono mt-1 flex items-center gap-1">
                QubicBay <ExternalLink className="w-2.5 h-2.5" />
              </span>
            </a>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
