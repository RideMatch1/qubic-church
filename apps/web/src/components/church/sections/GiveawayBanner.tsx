'use client'

/**
 * GiveawayBanner - Compact, single-row giveaway teaser
 * Not a full section - just enough to tease the giveaway.
 * Detailed info lives on its own page.
 */

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { GIVEAWAY_CONFIG } from '@/config/lottery'

function useCountdown(target: Date) {
  const [diff, setDiff] = useState(0)

  useEffect(() => {
    const calc = () => Math.max(0, target.getTime() - Date.now())
    setDiff(calc())
    const id = setInterval(() => setDiff(calc()), 60_000) // Update every minute (not per second - it's far away)
    return () => clearInterval(id)
  }, [target])

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))

  return { days, hours }
}

export function GiveawayBanner() {
  const { days, hours } = useCountdown(GIVEAWAY_CONFIG.drawDate)

  return (
    <section className="relative w-full py-16 md:py-20">
      <div className="container mx-auto px-6 max-w-5xl">
        <motion.div
          className="relative rounded-2xl border border-white/10 bg-white/[0.02] backdrop-blur-sm overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          {/* Subtle gradient accent */}
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500/[0.03] via-transparent to-yellow-500/[0.03] pointer-events-none" />

          <div className="relative flex flex-col md:flex-row items-center justify-between gap-6 px-8 py-8 md:px-10 md:py-7">
            {/* Left: Title + info */}
            <div className="text-center md:text-left">
              <h3 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
                676M QUBIC Giveaway
              </h3>
              <p className="text-white/40 text-sm mt-1.5">
                Hold 1 NFT = 1 Entry · 3 Winners · Draw in {days}d {hours}h
              </p>
            </div>

            {/* Right: CTA */}
            <Link
              href="/giveaway"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white/10 border border-white/15 text-white font-medium text-sm hover:bg-white/15 hover:border-white/25 transition-all group flex-shrink-0"
            >
              Enter Giveaway
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
