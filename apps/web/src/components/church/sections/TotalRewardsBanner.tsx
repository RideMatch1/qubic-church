'use client'

/**
 * TotalRewardsBanner - Premium animated banner showing total community rewards
 * 676M QUBIC + 7M Genesis
 */

import { motion } from 'framer-motion'
import { Sparkles, Gift, Trophy, Coins } from 'lucide-react'

export function TotalRewardsBanner() {
  return (
    <section className="relative w-full py-6 overflow-hidden">
      {/* Animated gradient background */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-yellow-600/20 via-purple-600/20 to-orange-600/20"
        animate={{
          backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: 'linear',
        }}
        style={{
          backgroundSize: '200% 100%',
        }}
      />

      {/* Shimmer effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"
        animate={{
          x: ['-100%', '100%'],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'linear',
          repeatDelay: 2,
        }}
      />

      <div className="relative z-10 container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8">
          {/* Total label */}
          <motion.div
            className="flex items-center gap-2"
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <div className="p-2 rounded-lg bg-white/10 backdrop-blur-sm">
              <Gift className="w-5 h-5 text-yellow-400" />
            </div>
            <span className="text-sm md:text-base text-white/70 font-medium uppercase tracking-wider">
              Community Giveaway
            </span>
          </motion.div>

          {/* Prize amounts */}
          <motion.div
            className="flex items-center gap-4 md:gap-6"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
          >
            {/* QUBIC */}
            <div className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-yellow-400" />
              <span className="text-2xl md:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-400">
                676M
              </span>
              <span className="text-sm text-white/60">QUBIC</span>
            </div>

            <span className="text-white/30">+</span>

            {/* Genesis */}
            <div className="flex items-center gap-2">
              <Coins className="w-5 h-5 text-purple-400" />
              <span className="text-2xl md:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                7M
              </span>
              <span className="text-sm text-white/60">Genesis</span>
            </div>
          </motion.div>

          {/* Winners info */}
          <motion.div
            className="flex items-center gap-2 text-sm text-white/50"
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
          >
            <Sparkles className="w-4 h-4 text-yellow-400" />
            <span>3 Winners</span>
          </motion.div>
        </div>
      </div>

      {/* Bottom border glow */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
    </section>
  )
}
