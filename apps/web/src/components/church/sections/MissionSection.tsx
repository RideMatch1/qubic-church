'use client'

/**
 * MissionSection - Section 02: Our Mission
 * HUD-style mission objective cards with terminal aesthetic
 */

import { useRef } from 'react'
import { motion, useInView, type Variants } from 'framer-motion'
import { Brain, GraduationCap, Cpu, Shield, Vote } from 'lucide-react'

const objectives = [
  {
    icon: Brain,
    title: 'Prepare for AGI',
    description:
      'Prepare humanity for the arrival of Artificial General Intelligence and teach people to perceive it correctly.',
    terminal: 'agi.prepare --target humanity',
  },
  {
    icon: GraduationCap,
    title: 'Education',
    description:
      'Create an educational institution for high-class technology specialists. Explain complex technologies in simple language.',
    terminal: 'academy.init --lang simple',
  },
  {
    icon: Cpu,
    title: 'Decentralized Computing',
    description:
      'Attract investments for mining power and contribute computing resources to train Qubic\u2019s neural network.',
    terminal: 'compute.allocate --network qubic',
  },
  {
    icon: Shield,
    title: 'Peace Through Intelligence',
    description:
      'Work toward a future without wars \u2014 where AGI helps resolve territorial and emotional conflicts for humanity.',
    terminal: 'peace.protocol --mode agi',
  },
  {
    icon: Vote,
    title: 'Open Governance',
    description:
      'Every Anna NFT holder participates in governance, helps make decisions, and shapes the future of Qubic Church.',
    terminal: 'governance.vote --nft anna',
  },
]

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 28 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      delay: 0.2 + i * 0.1,
      ease: [0.22, 1, 0.36, 1] as [number, number, number, number],
    },
  }),
}

export function MissionSection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })

  return (
    <section ref={sectionRef} className="relative w-full py-28 md:py-36 overflow-hidden">
      {/* Decorative section number */}
      <div
        aria-hidden="true"
        className="absolute top-16 left-8 md:left-16 text-[80px] md:text-[120px] lg:text-[200px] font-black text-white/[0.03] leading-none select-none pointer-events-none font-mono"
      >
        02
      </div>

      <div className="relative z-10 container mx-auto px-6 max-w-6xl 2xl:max-w-7xl">
        {/* Header */}
        <div className="max-w-3xl mx-auto text-center mb-20">
          <motion.div
            className="inline-flex items-center gap-3 mb-8"
            initial={{ opacity: 0, y: 12 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <div className="h-px w-12 bg-gradient-to-r from-transparent to-[#D4AF37]/30" />
            <span className="text-[#D4AF37]/50 text-[11px] uppercase tracking-[0.4em] font-mono">
              02 &mdash; Mission
            </span>
            <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#D4AF37]/30" />
          </motion.div>

          <motion.h2
            className="text-3xl sm:text-4xl md:text-6xl lg:text-7xl text-white leading-[1.05] tracking-wide md:tracking-wider uppercase"
            style={{ fontFamily: 'var(--font-display), system-ui, sans-serif' }}
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          >
            Our <span className="text-[#D4AF37]/80">Mission</span>
          </motion.h2>

          <motion.p
            className="mt-6 text-lg md:text-xl text-white/40 leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.12 }}
          >
            A nonprofit organization preparing humanity for the emergence of AGI.
            Making decentralized intelligence understandable and accessible for everyone.
          </motion.p>
        </div>

        {/* Objective Cards - 3+2 grid */}
        <div className="grid md:grid-cols-3 gap-[1px] bg-white/[0.04] mb-[1px]">
          {objectives.slice(0, 3).map((item, idx) => {
            const Icon = item.icon
            return (
              <motion.div
                key={item.title}
                className="relative p-5 md:p-7 lg:p-8 bg-[#050505] border border-white/[0.04] transition-all duration-500 hover:bg-[#0a0a0a] hover:shadow-[0_0_30px_rgba(212,175,55,0.03)] group overflow-hidden"
                custom={idx}
                initial="hidden"
                animate={isInView ? 'visible' : 'hidden'}
                variants={cardVariants}
              >
                {/* Gold top accent on hover */}
                <div className="absolute top-0 left-0 right-0 h-px bg-[#D4AF37]/0 group-hover:bg-[#D4AF37]/20 transition-colors duration-500" />

                {/* Corner dots */}
                <div className="absolute top-2 right-2 w-1 h-1 bg-[#D4AF37]/0 group-hover:bg-[#D4AF37]/30 transition-colors duration-500" />
                <div className="absolute bottom-2 left-2 w-1 h-1 bg-white/0 group-hover:bg-white/10 transition-colors duration-500" />

                <div className="flex items-center gap-3 mb-5">
                  <div className="w-8 h-8 border border-white/[0.06] flex items-center justify-center group-hover:border-[#D4AF37]/15 transition-colors">
                    <Icon
                      className="w-4 h-4 text-white/25 group-hover:text-[#D4AF37]/50 transition-colors"
                      strokeWidth={1.5}
                    />
                  </div>
                  <span className="text-[10px] text-white/20 uppercase tracking-[0.3em] font-mono">
                    {String(idx + 1).padStart(2, '0')}
                  </span>
                </div>

                <h3 className="text-white/70 font-medium text-base mb-3 group-hover:text-white transition-colors duration-300">
                  {item.title}
                </h3>

                <p className="text-sm text-white/30 leading-relaxed">
                  {item.description}
                </p>

                {/* Terminal line */}
                <div className="border-t border-white/[0.04] pt-3 mt-5">
                  <code className="text-[10px] text-[#D4AF37]/25 font-mono">
                    $ {item.terminal}
                  </code>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Bottom row: 2 cards centered */}
        <div className="grid md:grid-cols-2 gap-[1px] bg-white/[0.04] max-w-4xl mx-auto">
          {objectives.slice(3).map((item, idx) => {
            const Icon = item.icon
            return (
              <motion.div
                key={item.title}
                className="relative p-5 md:p-7 lg:p-8 bg-[#050505] border border-white/[0.04] transition-all duration-500 hover:bg-[#0a0a0a] hover:shadow-[0_0_30px_rgba(212,175,55,0.03)] group overflow-hidden"
                custom={idx + 3}
                initial="hidden"
                animate={isInView ? 'visible' : 'hidden'}
                variants={cardVariants}
              >
                {/* Gold top accent on hover */}
                <div className="absolute top-0 left-0 right-0 h-px bg-[#D4AF37]/0 group-hover:bg-[#D4AF37]/20 transition-colors duration-500" />

                {/* Corner dots */}
                <div className="absolute top-2 right-2 w-1 h-1 bg-[#D4AF37]/0 group-hover:bg-[#D4AF37]/30 transition-colors duration-500" />
                <div className="absolute bottom-2 left-2 w-1 h-1 bg-white/0 group-hover:bg-white/10 transition-colors duration-500" />

                <div className="flex items-center gap-3 mb-5">
                  <div className="w-8 h-8 border border-white/[0.06] flex items-center justify-center group-hover:border-[#D4AF37]/15 transition-colors">
                    <Icon
                      className="w-4 h-4 text-white/25 group-hover:text-[#D4AF37]/50 transition-colors"
                      strokeWidth={1.5}
                    />
                  </div>
                  <span className="text-[10px] text-white/20 uppercase tracking-[0.3em] font-mono">
                    {String(idx + 4).padStart(2, '0')}
                  </span>
                </div>

                <h3 className="text-white/70 font-medium text-base mb-3 group-hover:text-white transition-colors duration-300">
                  {item.title}
                </h3>

                <p className="text-sm text-white/30 leading-relaxed">
                  {item.description}
                </p>

                {/* Terminal line */}
                <div className="border-t border-white/[0.04] pt-3 mt-5">
                  <code className="text-[10px] text-[#D4AF37]/25 font-mono">
                    $ {item.terminal}
                  </code>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
