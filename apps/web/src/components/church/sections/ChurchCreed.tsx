'use client'

/**
 * ChurchCreed - Section 01: The Manifesto
 * HUD-style sacred proclamation with angular brackets and terminal aesthetic
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'

const creeds = [
  'We believe in the Genesis Block.',
  'We believe in mathematical truth.',
  'We believe in the architecture beneath all things.',
  'We believe Satoshi left us a map.',
  'We are preparing for The Convergence.',
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

      <div className="relative z-10 container mx-auto px-6 max-w-3xl">
        {/* HUD brackets top */}
        <div className="flex items-center justify-center mb-10">
          <motion.div
            className="flex items-center gap-4"
            initial={{ opacity: 0, scaleX: 0 }}
            animate={isInView ? { opacity: 1, scaleX: 1 } : {}}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="w-8 h-px bg-[#D4AF37]/20" />
            <div className="w-2 h-2 rotate-45 border border-[#D4AF37]/30" />
            <div className="w-8 h-px bg-[#D4AF37]/20" />
          </motion.div>
        </div>

        {/* Creed lines */}
        <div className="text-center space-y-3 md:space-y-4">
          {creeds.map((line, i) => {
            const isLast = i === creeds.length - 1

            return (
              <motion.p
                key={i}
                className={`text-lg md:text-2xl lg:text-3xl font-light leading-relaxed ${
                  isLast
                    ? 'text-white/90 font-medium mt-8'
                    : i >= creeds.length - 2
                    ? 'text-white/55'
                    : 'text-white/35'
                }`}
                initial={{ opacity: 0, y: 16 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{
                  duration: 0.6,
                  delay: 0.15 + i * 0.13,
                  ease: [0.22, 1, 0.36, 1],
                }}
              >
                {isLast ? (
                  <span className="bg-gradient-to-r from-[#D4AF37]/80 via-white/90 to-[#D4AF37]/60 bg-clip-text text-transparent">
                    {line}
                  </span>
                ) : (
                  line
                )}
              </motion.p>
            )
          })}
        </div>

        {/* Decorative line */}
        <motion.div
          className="mx-auto mt-10 h-px w-24 bg-gradient-to-r from-transparent via-[#D4AF37]/20 to-transparent"
          initial={{ scaleX: 0, opacity: 0 }}
          animate={isInView ? { scaleX: 1, opacity: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.9 }}
        />

        {/* Attribution */}
        <motion.p
          className="text-center mt-5 text-[10px] text-white/15 uppercase tracking-[0.4em] font-mono"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 1.1 }}
        >
          // The Qubic Church Creed
        </motion.p>
      </div>
    </section>
  )
}
