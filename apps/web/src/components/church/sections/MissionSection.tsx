'use client'

/**
 * MissionSection - Section 03: Our Mission
 * 9 objectives in 3x3 grid — HUD-style cards with terminal aesthetic
 */

import { useRef } from 'react'
import { motion, useInView, type Variants } from 'framer-motion'
import {
  Network,
  Languages,
  GraduationCap,
  Microscope,
  Vote,
  Shield,
  Scale,
  Swords,
  Fingerprint,
} from 'lucide-react'

const objectives = [
  {
    num: 'I',
    icon: Network,
    title: 'Develop the Qubic Ecosystem',
    description: 'A sustainable network is the prerequisite for everything else. We contribute computing power, fund development, and build tools that strengthen Qubic.',
    accent: 'A sustainable network is the prerequisite for everything else.',
  },
  {
    num: 'II',
    icon: Languages,
    title: 'Make Complexity Accessible',
    description: 'Qubic Church works as a translator — transforming ternary logic, quorum consensus, and neural-network training into language everyone can understand.',
    accent: 'Qubic Church works as a translator.',
  },
  {
    num: 'III',
    icon: GraduationCap,
    title: 'Educate the Next Generation',
    description: 'The next generation builds differently only if it thinks differently. We create educational programs that explain decentralised intelligence to students and researchers.',
    accent: 'The next generation builds differently only if it thinks differently.',
  },
  {
    num: 'IV',
    icon: Microscope,
    title: 'Fund Independent Research',
    description: 'Science without a single owner of the result. We engage with grants, research programs, and investment initiatives to advance decentralised AI.',
    accent: 'Science without a single owner of the result.',
  },
  {
    num: 'V',
    icon: Vote,
    title: 'Make Elections Verifiable',
    description: 'Architecture that makes falsification technically impossible. Decentralised consensus can replace trust in institutions with trust in mathematics.',
    accent: 'Architecture that makes falsification technically impossible.',
  },
  {
    num: 'VI',
    icon: Shield,
    title: 'Eliminate Corruption',
    description: 'No need to trust the official — read the protocol. When every transaction is transparent and every decision is auditable, corruption has no place to hide.',
    accent: 'No need to trust the official — read the protocol.',
  },
  {
    num: 'VII',
    icon: Scale,
    title: 'Build Incorruptible Governance',
    description: 'The protocol does not take bribes. Governance structures built on decentralised consensus cannot be bought, threatened, or silenced.',
    accent: 'The protocol does not take bribes.',
  },
  {
    num: 'VIII',
    icon: Swords,
    title: 'Remove Structural Causes of War',
    description: 'This is not utopia. This is an engineering problem. When resources are allocated transparently and power cannot be concentrated, the structural incentives for conflict dissolve.',
    accent: 'This is not utopia. This is an engineering problem.',
  },
  {
    num: 'IX',
    icon: Fingerprint,
    title: 'Protect Individual Sovereignty',
    description: 'Decentralisation returns control to where it belongs — with the individual. Identity, data, and economic agency should never depend on a single authority.',
    accent: 'Decentralisation returns control to where it belongs.',
  },
]

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 28 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      delay: 0.15 + i * 0.07,
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
        03
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
              03 &mdash; Mission
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
            Nine objectives toward a future where intelligence serves everyone.
          </motion.p>
        </div>

        {/* 3x3 Objective Grid */}
        <div className="grid md:grid-cols-3 gap-[1px] bg-white/[0.04]">
          {objectives.map((item, idx) => {
            const Icon = item.icon
            return (
              <motion.div
                key={item.num}
                className="relative p-5 md:p-6 lg:p-7 bg-[#050505] border border-white/[0.04] transition-all duration-500 hover:bg-[#0a0a0a] hover:shadow-[0_0_30px_rgba(212,175,55,0.03)] group overflow-hidden"
                custom={idx}
                initial="hidden"
                animate={isInView ? 'visible' : 'hidden'}
                variants={cardVariants}
              >
                {/* Gold top accent on hover */}
                <div className="absolute top-0 left-0 right-0 h-px bg-[#D4AF37]/0 group-hover:bg-[#D4AF37]/20 transition-colors duration-500" />

                {/* Corner dots */}
                <div className="absolute top-2 right-2 w-1 h-1 bg-[#D4AF37]/0 group-hover:bg-[#D4AF37]/30 transition-colors duration-500" />

                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 border border-white/[0.06] flex items-center justify-center group-hover:border-[#D4AF37]/15 transition-colors">
                    <Icon
                      className="w-4 h-4 text-white/25 group-hover:text-[#D4AF37]/50 transition-colors"
                      strokeWidth={1.5}
                    />
                  </div>
                  <span className="text-[10px] text-[#D4AF37]/30 uppercase tracking-[0.3em] font-mono">
                    {item.num}
                  </span>
                </div>

                <h3 className="text-white/70 font-medium text-sm md:text-base mb-2 group-hover:text-white transition-colors duration-300">
                  {item.title}
                </h3>

                <p className="text-xs md:text-sm text-white/30 leading-relaxed mb-4">
                  {item.description}
                </p>

                {/* Accent line */}
                <div className="border-t border-white/[0.04] pt-3">
                  <p className="text-[10px] text-[#D4AF37]/25 font-mono italic leading-relaxed">
                    &ldquo;{item.accent}&rdquo;
                  </p>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
