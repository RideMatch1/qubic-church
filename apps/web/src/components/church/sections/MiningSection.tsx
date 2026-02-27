'use client'

/**
 * MiningSection - Section 07: Mine the Future
 * HUD cards about Qubic mining: train AI, earn QUBIC, join the network
 * Terminal-style stats bar, CTA to mining guide
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import Link from 'next/link'
import { Cpu, Coins, Network, ArrowRight, Terminal } from 'lucide-react'

const features = [
  {
    icon: Cpu,
    title: 'Train AI',
    stat: 'Aigarth',
    description:
      'Your compute power trains Aigarth, Qubic\'s ternary neural network. Mining is useful proof of work \u2014 every solution contributes to artificial intelligence.',
    terminal: 'aigarth.train --epoch current',
  },
  {
    icon: Coins,
    title: 'Earn QUBIC',
    stat: 'Every Epoch',
    description:
      'Mining rewards distributed every epoch. GPU and CPU supported. No specialized hardware required.',
    terminal: 'wallet.balance --rewards',
  },
  {
    icon: Network,
    title: 'Join 15K+ Miners',
    stat: 'Active',
    description:
      'Compatible with major pools like Qubic.li and Apool. Start mining in under 5 minutes.',
    terminal: 'pool.connect --qubic.li',
  },
]

export function MiningSection() {
  const sectionRef = useRef<HTMLElement>(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })

  return (
    <section ref={sectionRef} className="relative w-full py-28 md:py-36 overflow-hidden">
      {/* Decorative section number */}
      <div aria-hidden="true" className="absolute top-16 right-8 md:right-16 text-[80px] md:text-[120px] lg:text-[200px] font-black text-white/[0.03] leading-none select-none pointer-events-none font-mono">
        07
      </div>

      <div className="relative z-10 container mx-auto px-6 max-w-6xl 2xl:max-w-7xl">
        {/* Header */}
        <motion.div
          className="text-center mb-20"
          initial={{ opacity: 0, y: 24 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, ease: 'easeOut' }}
        >
          <div className="inline-flex items-center gap-3 mb-8">
            <div className="h-px w-12 bg-gradient-to-r from-transparent to-[#D4AF37]/30" />
            <span className="text-[#D4AF37]/50 text-[11px] uppercase tracking-[0.4em] font-mono">
              07 &mdash; Compute
            </span>
            <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#D4AF37]/30" />
          </div>

          <h2
            className="text-3xl sm:text-4xl md:text-6xl lg:text-7xl text-white mb-5 tracking-wide md:tracking-wider uppercase"
            style={{ fontFamily: 'var(--font-display), system-ui, sans-serif' }}
          >
            Mine the{' '}
            <span className="text-[#D4AF37]/80">Future</span>
          </h2>

          <p className="text-lg text-white/35 max-w-2xl mx-auto leading-relaxed">
            Qubic mining doesn&apos;t just secure a network &mdash; it trains an artificial intelligence.
          </p>
        </motion.div>

        {/* Feature Cards */}
        <motion.div
          className="grid md:grid-cols-3 gap-[1px] bg-white/[0.04] mb-8"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.15 }}
        >
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={feature.title}
                className="relative p-5 md:p-7 lg:p-8 bg-[#050505] border border-white/[0.04] transition-all duration-500 hover:bg-[#0a0a0a] hover:shadow-[0_0_30px_rgba(212,175,55,0.03)] group overflow-hidden"
                initial={{ opacity: 0, y: 24 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.25 + index * 0.1, ease: 'easeOut' }}
              >
                {/* Top accent line on hover */}
                <div className="absolute top-0 left-0 right-0 h-px bg-[#D4AF37]/0 group-hover:bg-[#D4AF37]/20 transition-colors duration-500" />

                {/* Corner dots */}
                <div className="absolute top-2 left-2 w-1 h-1 bg-white/0 group-hover:bg-[#D4AF37]/30 transition-colors duration-500" />
                <div className="absolute top-2 right-2 w-1 h-1 bg-white/0 group-hover:bg-[#D4AF37]/30 transition-colors duration-500" />

                {/* Icon + Status */}
                <div className="flex items-center justify-between mb-5">
                  <div className="w-10 h-10 border border-white/[0.06] flex items-center justify-center group-hover:border-[#D4AF37]/15 transition-colors">
                    <Icon className="w-5 h-5 text-[#D4AF37]/40 group-hover:text-[#D4AF37]/70 transition-colors" />
                  </div>
                  <span className="text-[9px] text-[#D4AF37]/30 uppercase tracking-[0.2em] font-mono border border-[#D4AF37]/10 px-2 py-0.5">
                    {feature.stat}
                  </span>
                </div>

                {/* Title */}
                <h3 className="text-lg font-bold text-white mb-3 group-hover:text-[#D4AF37]/90 transition-colors duration-500">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-sm text-white/30 leading-relaxed mb-5">
                  {feature.description}
                </p>

                {/* Terminal line */}
                <div className="border-t border-white/[0.04] pt-3">
                  <code className="text-[10px] text-[#D4AF37]/25 font-mono">
                    $ {feature.terminal}
                  </code>
                </div>
              </motion.div>
            )
          })}
        </motion.div>

        {/* Terminal status bar */}
        <motion.div
          className="px-4 py-3 bg-[#050505] border border-white/[0.04] mb-12"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <div className="flex items-center gap-2">
            <Terminal className="w-3 h-3 text-[#D4AF37]/25 shrink-0" />
            <code className="text-[10px] text-white/20 font-mono overflow-x-auto whitespace-nowrap">
              <span className="text-[#D4AF37]/30">$</span> status: <span className="text-[#D4AF37]/40">NETWORK_ACTIVE</span> | miners: 15,000+ | algorithm: AiTraining | pools: qubic.li, apool, minerstat
            </code>
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 16 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <Link
            href="/mine-qubic"
            className="group inline-flex items-center gap-3 px-8 py-4 bg-[#D4AF37]/[0.04] border border-[#D4AF37]/15 text-white font-bold text-base hover:bg-[#D4AF37]/[0.08] hover:border-[#D4AF37]/25 transition-all duration-500 font-mono tracking-wider"
          >
            <span className="text-[#D4AF37]/40">&gt;_</span>
            OPEN MINING GUIDE
            <ArrowRight className="w-4 h-4 text-[#D4AF37]/40 group-hover:translate-x-1 transition-transform" />
          </Link>
          <p className="text-[10px] text-white/20 mt-3 font-mono">
            GPU + CPU supported // No specialized hardware
          </p>
        </motion.div>
      </div>
    </section>
  )
}
