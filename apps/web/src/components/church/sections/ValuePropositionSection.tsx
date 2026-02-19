'use client'

/**
 * ValuePropositionSection - Core pitch right after the hero
 * "The deepest research into Qubic's origins" with 3 animated stat cards
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import Link from 'next/link'
import { BookOpen, ImageIcon, Coins, ArrowRight } from 'lucide-react'
import { NeuralCluster } from '@/components/church/decorations/NeuralDecoration'

const stats = [
  {
    icon: BookOpen,
    value: '75+',
    label: 'Research Documents',
    description: 'Open-source analysis of Bitcoin-Qubic connections',
    href: '/docs',
    color: {
      gradient: 'from-white/[0.06] to-white/[0.02]',
      border: 'border-white/10 hover:border-white/20',
      icon: 'text-white/70',
      glow: 'bg-white/10',
      value: 'text-white',
    },
  },
  {
    icon: ImageIcon,
    value: '200',
    label: 'Anna NFTs',
    description: 'Unique collection with giveaway entry & tier benefits',
    href: '/nfts',
    color: {
      gradient: 'from-purple-500/10 to-purple-500/[0.03]',
      border: 'border-purple-500/15 hover:border-purple-400/30',
      icon: 'text-purple-400/80',
      glow: 'bg-purple-500/15',
      value: 'text-purple-300',
    },
  },
  {
    icon: Coins,
    value: '676M',
    label: 'QUBIC Giveaway',
    description: 'Hold 1 NFT = 1 entry. 3 winners, transparent draw.',
    href: '#giveaway',
    color: {
      gradient: 'from-yellow-500/10 to-yellow-500/[0.03]',
      border: 'border-yellow-500/15 hover:border-yellow-400/30',
      icon: 'text-yellow-400/80',
      glow: 'bg-yellow-500/15',
      value: 'text-yellow-300',
    },
  },
]

export function ValuePropositionSection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })

  return (
    <section ref={sectionRef} className="relative w-full py-16 md:py-24 overflow-hidden">
      {/* Neural network decoration - left side */}
      <NeuralCluster className="left-0 top-1/4 -translate-x-1/4 hidden lg:block" opacity={0.04} scale={0.8} />
      {/* Neural network decoration - right side */}
      <NeuralCluster className="right-0 bottom-1/4 translate-x-1/4 hidden lg:block" opacity={0.03} scale={0.6} />

      <div className="relative z-10 container mx-auto px-4 max-w-6xl">
        {/* Headline */}
        <motion.div
          className="text-center mb-14"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4 leading-tight">
            The deepest research into{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white/90 via-purple-300 to-white/90">
              Qubic&apos;s origins
            </span>
          </h2>
          <p className="text-lg text-white/50 max-w-2xl mx-auto">
            An open-source community exploring the mathematical bridge between Bitcoin,
            Anna, Aigarth, and the architecture of the world&apos;s first ternary neural network.
          </p>
        </motion.div>

        {/* Stat Cards */}
        <div className="grid md:grid-cols-3 gap-5">
          {stats.map((stat, idx) => {
            const Icon = stat.icon

            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.15 + idx * 0.1 }}
              >
                <Link
                  href={stat.href}
                  className={`group relative block p-6 rounded-2xl bg-gradient-to-b ${stat.color.gradient} border ${stat.color.border} transition-all duration-300 hover:scale-[1.02] hover:-translate-y-1 overflow-hidden`}
                >
                  {/* Glow behind icon */}
                  <div className={`absolute top-4 left-4 w-16 h-16 rounded-full ${stat.color.glow} blur-2xl opacity-50 group-hover:opacity-80 transition-opacity`} />

                  <div className="relative">
                    <div className="flex items-center justify-between mb-4">
                      <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                        <Icon className={`w-6 h-6 ${stat.color.icon}`} />
                      </div>
                      <ArrowRight className="w-5 h-5 text-white/20 group-hover:text-white/60 group-hover:translate-x-1 transition-all" />
                    </div>

                    <div className={`text-4xl md:text-5xl font-black ${stat.color.value} mb-1`}>
                      {stat.value}
                    </div>
                    <div className="text-white font-semibold mb-2">{stat.label}</div>
                    <p className="text-sm text-white/40 leading-relaxed">
                      {stat.description}
                    </p>
                  </div>
                </Link>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
