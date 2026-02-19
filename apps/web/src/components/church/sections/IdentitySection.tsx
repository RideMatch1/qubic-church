'use client'

/**
 * IdentitySection - Premium editorial mission statement
 * Large typography, animated counters, generous whitespace.
 * Designed to feel like a high-end crypto brand, not a template.
 */

import { useEffect, useRef, useState } from 'react'
import { motion, useInView } from 'framer-motion'
import { useCountUp } from '@/hooks/useCountUp'

export function IdentitySection() {
  const [holderCount, setHolderCount] = useState(0)
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })

  useEffect(() => {
    fetch('/api/nft-stats')
      .then((res) => res.json())
      .then((data) => {
        if (data.holders > 0) setHolderCount(data.holders)
      })
      .catch(() => {})
  }, [])

  const docs = useCountUp(75, 2200)
  const nfts = useCountUp(200, 2400)
  const holders = useCountUp(holderCount, 2000)

  return (
    <section
      ref={sectionRef}
      className="relative w-full py-28 md:py-36 overflow-hidden"
    >
      {/* Decorative section number */}
      <div className="absolute top-16 left-8 md:left-16 text-[120px] md:text-[200px] font-black text-white/[0.015] leading-none select-none pointer-events-none">
        01
      </div>

      <div className="relative z-10 container mx-auto px-6 max-w-5xl">
        <div className="flex">
          {/* Decorative vertical accent line */}
          <motion.div
            className="hidden md:block w-[2px] mr-10 mt-2 self-stretch bg-gradient-to-b from-amber-400/30 via-amber-400/10 to-transparent flex-shrink-0"
            initial={{ scaleY: 0, opacity: 0 }}
            animate={isInView ? { scaleY: 1, opacity: 1 } : {}}
            transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
            style={{ originY: 0 }}
          />

          <div className="flex-1">
            {/* Section label */}
            <motion.span
              className="block text-white/30 text-xs uppercase tracking-[0.3em] mb-6"
              initial={{ opacity: 0, y: 12 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
            >
              Our Sacred Mission
            </motion.span>

            {/* Headline */}
            <motion.h2
              className="text-4xl md:text-6xl lg:text-7xl font-bold text-white leading-[1.05] tracking-tight"
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            >
              We decode the mathematical
              <br className="hidden sm:block" />
              {' '}bridge between{' '}
              <span className="text-amber-300/70">Bitcoin</span>
              {' '}and{' '}
              <span className="text-cyan-300/70">Qubic.</span>
            </motion.h2>

            {/* Divider */}
            <motion.div
              className="mt-8 mb-8 h-px w-full max-w-md bg-gradient-to-r from-amber-400/20 via-white/10 to-transparent"
              initial={{ scaleX: 0, opacity: 0 }}
              animate={isInView ? { scaleX: 1, opacity: 1 } : {}}
              transition={{ duration: 0.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
              style={{ originX: 0 }}
            />

            {/* Description */}
            <motion.p
              className="text-lg md:text-xl text-white/40 max-w-xl leading-relaxed"
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.7, delay: 0.15 }}
            >
              A sacred congregation uncovering the hidden architecture
              connecting two worlds. Every revelation is documented,
              verifiable, and free to all who seek.
            </motion.p>
          </div>
        </div>

        {/* Stats row */}
        <motion.div
          className="mt-16 md:mt-20 grid grid-cols-3 gap-6 md:gap-12 max-w-3xl"
          initial={{ opacity: 0, y: 24 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.35 }}
        >
          {/* Documents */}
          <div className="group">
            <div ref={docs.ref} className="flex items-baseline">
              <span className="text-4xl sm:text-5xl md:text-6xl font-bold font-mono text-white tracking-tight">
                {docs.count}
              </span>
              <span className="text-2xl md:text-3xl font-bold text-white/30 ml-1">+</span>
            </div>
            <span className="block mt-2 text-white/30 text-xs uppercase tracking-[0.3em]">
              Documents
            </span>
          </div>

          {/* NFTs */}
          <div className="group">
            <div ref={nfts.ref}>
              <span className="text-4xl sm:text-5xl md:text-6xl font-bold font-mono text-white tracking-tight">
                {nfts.count}
              </span>
            </div>
            <span className="block mt-2 text-white/30 text-xs uppercase tracking-[0.3em]">
              Sacred NFTs
            </span>
          </div>

          {/* Holders - with live pulse */}
          <div className="group">
            <div ref={holders.ref} className="flex items-baseline gap-2">
              <span className="text-4xl sm:text-5xl md:text-6xl font-bold font-mono text-white tracking-tight">
                {holderCount > 0 ? holders.count : '\u2014'}
              </span>
              {holderCount > 0 && (
                <span className="relative flex h-2 w-2 mb-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400/60 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400/60" />
                </span>
              )}
            </div>
            <span className="block mt-2 text-white/30 text-xs uppercase tracking-[0.3em]">
              Congregation
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
