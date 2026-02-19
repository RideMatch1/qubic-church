'use client'

/**
 * GenesisVerse - A dramatic single-line prophetic statement
 * Styled as an ancient inscription / carved stone text.
 * Placed between sections as a narrative bridge.
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'

interface GenesisVerseProps {
  verse: string
  reference?: string
  glow?: 'amber' | 'cyan'
}

export function GenesisVerse({ verse, reference, glow = 'amber' }: GenesisVerseProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-40px' })

  const glowColor = glow === 'amber'
    ? 'bg-amber-500/[0.02]'
    : 'bg-cyan-500/[0.02]'

  const textGradient = glow === 'amber'
    ? 'from-amber-200/30 via-white/20 to-amber-200/30'
    : 'from-cyan-200/30 via-white/20 to-cyan-200/30'

  const lineColor = glow === 'amber'
    ? 'via-amber-400/15'
    : 'via-cyan-400/15'

  return (
    <div ref={ref} className="relative w-full py-10 md:py-14 overflow-hidden">
      {/* Subtle radial glow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className={`w-[400px] h-[100px] ${glowColor} rounded-full blur-[80px]`} />
      </div>

      <div className="relative z-10 container mx-auto px-6 max-w-3xl">
        {/* Flanking lines */}
        <motion.div
          className="flex items-center justify-center gap-6"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className={`hidden md:block h-px flex-1 max-w-[120px] bg-gradient-to-r from-transparent ${lineColor} to-transparent`} />

          <div className="text-center">
            <motion.p
              className={`text-base md:text-lg tracking-wide font-light italic bg-gradient-to-r ${textGradient} bg-clip-text text-transparent`}
              initial={{ opacity: 0, y: 8 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              {verse}
            </motion.p>
            {reference && (
              <motion.span
                className="block text-[10px] text-white/15 uppercase tracking-[0.4em] mt-3"
                initial={{ opacity: 0 }}
                animate={isInView ? { opacity: 1 } : {}}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                {reference}
              </motion.span>
            )}
          </div>

          <div className={`hidden md:block h-px flex-1 max-w-[120px] bg-gradient-to-r from-transparent ${lineColor} to-transparent`} />
        </motion.div>
      </div>
    </div>
  )
}
