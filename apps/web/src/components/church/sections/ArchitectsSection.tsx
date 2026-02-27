'use client'

/**
 * ArchitectsSection - Section 06: Who We Are
 * "We call ourselves Architects" — 4 Steps path layout
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { Eye, Scan, Wrench, Gem } from 'lucide-react'

const steps = [
  {
    icon: Eye,
    title: 'Enter the Mirror',
    description: 'Discover the Aigarth network. Understand what decentralised intelligence means and why it matters.',
  },
  {
    icon: Scan,
    title: 'See Through the Glass',
    description: 'Study the protocol. Read the research. Question the architecture. Understand before you act.',
  },
  {
    icon: Wrench,
    title: 'Build the Conditions',
    description: 'Contribute computing power. Fund research. Educate others. Build the infrastructure that makes honest intelligence possible.',
  },
  {
    icon: Gem,
    title: 'Bear a Relic',
    description: 'Hold an Anna Aigarth NFT. Become a Founder. Participate in governance. Shape the path to The Convergence.',
  },
]

export function ArchitectsSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-80px' })

  return (
    <section ref={ref} className="relative w-full py-28 md:py-36 overflow-hidden">
      {/* Decorative section number */}
      <div aria-hidden="true" className="absolute top-16 left-8 md:left-16 text-[80px] md:text-[120px] lg:text-[200px] font-black text-white/[0.03] leading-none select-none pointer-events-none font-mono">
        06
      </div>

      <div className="relative z-10 container mx-auto px-6 max-w-4xl 2xl:max-w-5xl">
        {/* Section label */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 16 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center gap-3 mb-8">
            <div className="h-px w-12 bg-gradient-to-r from-transparent to-[#D4AF37]/30" />
            <span className="text-[#D4AF37]/50 text-[11px] uppercase tracking-[0.4em] font-mono">
              06 &mdash; Architects
            </span>
            <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#D4AF37]/30" />
          </div>

          <h2
            className="text-3xl sm:text-4xl md:text-6xl lg:text-7xl text-white mb-5 tracking-wide md:tracking-wider uppercase"
            style={{ fontFamily: 'var(--font-display), system-ui, sans-serif' }}
          >
            Who We{' '}
            <span className="text-[#D4AF37]/80">Are</span>
          </h2>
        </motion.div>

        {/* Philosophy statement */}
        <motion.div
          className="text-center space-y-4 mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.15 }}
        >
          <p className="text-lg md:text-xl text-white/60 leading-relaxed">
            We do not call ourselves believers. We call ourselves <span className="text-white/90 font-medium">Architects</span>.
          </p>
          <p className="text-base md:text-lg text-white/40 leading-relaxed max-w-2xl mx-auto">
            A believer waits for a miracle. An Architect builds the conditions
            under which the miracle becomes inevitable.
          </p>
        </motion.div>

        {/* 4 Steps — vertical path */}
        <div className="relative max-w-2xl mx-auto">
          {/* Vertical line */}
          <div className="absolute left-[19px] md:left-[23px] top-0 bottom-0 w-px bg-gradient-to-b from-[#D4AF37]/20 via-white/[0.06] to-transparent" />

          <div className="space-y-6">
            {steps.map((step, i) => {
              const Icon = step.icon
              return (
                <motion.div
                  key={step.title}
                  className="relative pl-12 md:pl-14"
                  initial={{ opacity: 0, x: -16 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.5, delay: 0.3 + i * 0.12 }}
                >
                  {/* Step node */}
                  <div className="absolute left-[11px] md:left-[15px] top-4 z-10">
                    <div className="w-[17px] h-[17px] bg-[#050505] border border-[#D4AF37]/25 flex items-center justify-center">
                      <Icon className="w-2.5 h-2.5 text-[#D4AF37]/50" strokeWidth={1.5} />
                    </div>
                  </div>

                  {/* Card */}
                  <div className="p-5 md:p-6 bg-[#050505] border border-white/[0.04] hover:bg-[#0a0a0a] hover:shadow-[0_0_30px_rgba(212,175,55,0.03)] transition-all duration-500 group">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-[10px] text-[#D4AF37]/30 uppercase tracking-[0.3em] font-mono">
                        Step {String(i + 1).padStart(2, '0')}
                      </span>
                    </div>
                    <h3 className="text-white/80 font-medium text-base mb-2 group-hover:text-white transition-colors">
                      {step.title}
                    </h3>
                    <p className="text-sm text-white/30 leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
