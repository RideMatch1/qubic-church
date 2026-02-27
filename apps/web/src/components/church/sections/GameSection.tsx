'use client'

/**
 * GameSection - Anna Matrix RPG Game embedded on main page
 * Explore the 128×128 neural network, discover patterns, earn rewards
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { Gamepad2, ArrowRight } from 'lucide-react'
import dynamic from 'next/dynamic'

// Dynamic import for performance (game is heavy)
const AnnaMatrixGame = dynamic(
  () => import('../game/AnnaMatrixGame').then(mod => mod.AnnaMatrixGame),
  {
    ssr: false,
    loading: () => (
      <div className="w-full aspect-square bg-black/50 flex items-center justify-center">
        <div className="text-white/50">Loading game...</div>
      </div>
    ),
  }
)

export function GameSection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })

  return (
    <section ref={sectionRef} className="relative w-full py-20 md:py-28 overflow-hidden">

      <div className="relative z-10 container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 leading-tight">
            Anna Matrix Explorer
          </h2>

          <p className="text-base text-white/50 leading-relaxed max-w-2xl mx-auto mb-6">
            Navigate through the 128×128 neural network. Discover hidden patterns,
            visit special locations, and earn rewards. Use WASD or arrow keys to move.
          </p>

          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <span className="text-white/30 text-sm">7 Hidden Patterns</span>
            <span className="text-white/20">·</span>
            <span className="text-white/30 text-sm">Earn Points</span>
            <span className="text-white/20">·</span>
            <span className="text-white/30 text-sm">NFT Holder Rewards</span>
          </div>
        </motion.div>

        {/* Game Container */}
        <motion.div
          className="max-w-3xl mx-auto"
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className="border border-white/[0.04] overflow-hidden backdrop-blur-sm">
            <AnnaMatrixGame />
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          className="text-center mt-12"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ delay: 0.6 }}
        >
          <a
            href="/game"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white/[0.06] border border-white/[0.04] text-white hover:bg-white/10 hover:border-white/25 transition-all"
          >
            <Gamepad2 className="w-5 h-5 text-[#D4AF37]" />
            Play Fullscreen
            <ArrowRight className="w-4 h-4" />
          </a>
        </motion.div>
      </div>
    </section>
  )
}
