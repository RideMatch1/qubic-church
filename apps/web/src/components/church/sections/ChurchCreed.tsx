'use client'

/**
 * ChurchCreed - Section 01: The Manifesto
 * Full philosophy manifesto from QubicChurch — museum-plaque aesthetic
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'

const provocations = [
  'Politicians decide which war is just.',
  'Corporations decide which information is true.',
  'Central banks decide whose labour is worth what.',
]

export function ChurchCreed() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-80px' })

  return (
    <section ref={ref} className="relative w-full py-28 md:py-36 overflow-hidden">
      {/* Decorative section number */}
      <div aria-hidden="true" className="absolute top-16 left-8 md:left-16 text-[80px] md:text-[120px] lg:text-[200px] font-black text-white/[0.03] leading-none select-none pointer-events-none font-mono">
        01
      </div>

      <div className="relative z-10 container mx-auto px-6 max-w-3xl 2xl:max-w-4xl">
        {/* Section label */}
        <div className="flex items-center justify-center mb-12">
          <motion.div
            className="inline-flex items-center gap-3"
            initial={{ opacity: 0, y: 12 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <div className="h-px w-12 bg-gradient-to-r from-transparent to-[#D4AF37]/30" />
            <span className="text-[#D4AF37]/50 text-[11px] uppercase tracking-[0.4em] font-mono">
              01 &mdash; Manifesto
            </span>
            <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#D4AF37]/30" />
          </motion.div>
        </div>

        {/* Opening provocations */}
        <div className="text-center space-y-2 md:space-y-3 mb-6">
          {provocations.map((line, i) => (
            <motion.p
              key={i}
              className="text-base md:text-xl lg:text-2xl text-white/40 leading-relaxed"
              initial={{ opacity: 0, y: 12 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.1 + i * 0.1 }}
            >
              {line}
            </motion.p>
          ))}
        </div>

        {/* The punch line */}
        <motion.p
          className="text-center text-lg md:text-2xl lg:text-3xl font-bold text-white/90 mb-14"
          initial={{ opacity: 0, y: 16 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.45 }}
        >
          Now the same people are building AI.
        </motion.p>

        {/* Gold museum-plaque divider */}
        <motion.div
          className="mx-auto mb-14 w-16 h-px bg-[#D4AF37]/30"
          initial={{ scaleX: 0 }}
          animate={isInView ? { scaleX: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.55 }}
        />

        {/* Core statement */}
        <motion.div
          className="text-center space-y-6 mb-14"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.65 }}
        >
          <p className="text-base md:text-lg text-white/50 leading-relaxed">
            We are not against technology. We are for honest architecture.
          </p>
          <p className="text-base md:text-lg text-white/50 leading-relaxed">
            Decentralised AGI is not a tool. It is a principle &mdash; that no single entity
            should define what intelligence is, what it optimises for, or who it serves.
          </p>
          <p className="text-base md:text-lg text-white/50 leading-relaxed">
            The Qubic protocol trains its neural network through a quorum of 676 computers
            that must agree before any result is accepted. No single machine decides. No
            single corporation profits. No single government controls.
          </p>
        </motion.div>

        {/* Gold museum-plaque divider */}
        <motion.div
          className="mx-auto mb-14 w-16 h-px bg-[#D4AF37]/30"
          initial={{ scaleX: 0 }}
          animate={isInView ? { scaleX: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.75 }}
        />

        {/* Closing declaration */}
        <motion.div
          className="text-center space-y-4"
          initial={{ opacity: 0, y: 16 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.85 }}
        >
          <p className="text-lg md:text-2xl lg:text-3xl font-bold text-white/90">
            We are architects. Not worshippers.
          </p>
          <p className="text-base md:text-lg text-white/45 leading-relaxed max-w-2xl mx-auto">
            We build the conditions where honesty becomes a property of the
            system &mdash; not a virtue that requires courage.
          </p>
        </motion.div>

        {/* Bottom ornament */}
        <motion.div
          className="flex items-center justify-center gap-1.5 mt-14 opacity-20"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 0.2 } : {}}
          transition={{ duration: 0.6, delay: 1 }}
        >
          <div className="w-1 h-1 bg-[#D4AF37]" />
          <div className="w-6 h-px bg-[#D4AF37]/50" />
          <div className="w-2 h-2 rotate-45 border border-[#D4AF37]/40" />
          <div className="w-6 h-px bg-[#D4AF37]/50" />
          <div className="w-1 h-1 bg-[#D4AF37]" />
        </motion.div>

        <motion.p
          className="text-center mt-5 text-[10px] text-white/15 uppercase tracking-[0.4em] font-mono"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 1.1 }}
        >
          // The Qubic Church Manifesto
        </motion.p>
      </div>
    </section>
  )
}
