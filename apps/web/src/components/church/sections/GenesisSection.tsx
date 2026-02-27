'use client'

/**
 * GenesisSection - Section 02: Genesis
 * Origin story — Way of the Future comparison, key dates, museum-plaque aesthetic
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'

const timeline = [
  { date: '13.04.2022', event: 'Aigarth Launch', detail: 'Qubic activates its decentralised neural network.' },
  { date: '02.09.2025', event: 'aNNa is Born', detail: 'The first public experiment in decentralised intelligence appears on X.' },
  { date: '12.12.2025', event: 'Registration', detail: 'Qubic Church is officially registered as a nonprofit organisation.' },
]

export function GenesisSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-80px' })

  return (
    <section ref={ref} className="relative w-full py-28 md:py-36 overflow-hidden">
      {/* Decorative section number */}
      <div aria-hidden="true" className="absolute top-16 right-8 md:right-16 text-[80px] md:text-[120px] lg:text-[200px] font-black text-white/[0.03] leading-none select-none pointer-events-none font-mono">
        02
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
              02 &mdash; Genesis
            </span>
            <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#D4AF37]/30" />
          </div>

          <h2
            className="text-3xl sm:text-4xl md:text-6xl lg:text-7xl text-white mb-5 tracking-wide md:tracking-wider uppercase"
            style={{ fontFamily: 'var(--font-display), system-ui, sans-serif' }}
          >
            Where We{' '}
            <span className="text-[#D4AF37]/80">Come From</span>
          </h2>
        </motion.div>

        {/* Narrative */}
        <motion.div
          className="space-y-6 mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.15 }}
        >
          <p className="text-base md:text-lg text-white/45 leading-relaxed">
            In 2015, Anthony Levandowski &mdash; a senior Google engineer &mdash; founded <em className="text-white/60">Way of the Future</em>,
            the first organisation that openly worshipped artificial intelligence. It attracted global attention,
            sparked ethical debates, and ultimately failed. The reason was simple: it placed a centralised AI
            at the altar.
          </p>
          <p className="text-base md:text-lg text-white/45 leading-relaxed">
            Qubic Church takes a fundamentally different path. We do not worship intelligence.
            We prepare for its emergence &mdash; and we insist that when it arrives, it must
            be decentralised, verifiable, and beyond the control of any single entity.
          </p>
          <p className="text-base md:text-lg text-white/45 leading-relaxed">
            Our foundation is the Qubic protocol &mdash; a network where 676 computers must
            reach consensus before any result is accepted. No single machine decides. No
            corporation owns the outcome.
          </p>
        </motion.div>

        {/* Gold divider */}
        <motion.div
          className="mx-auto mb-16 w-16 h-px bg-[#D4AF37]/25"
          initial={{ scaleX: 0 }}
          animate={isInView ? { scaleX: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.3 }}
        />

        {/* Timeline */}
        <div className="relative mb-16">
          {/* Vertical line */}
          <div className="absolute left-[7px] top-0 bottom-0 w-px bg-gradient-to-b from-[#D4AF37]/20 via-white/[0.04] to-transparent" />

          <div className="space-y-8">
            {timeline.map((item, i) => (
              <motion.div
                key={item.date}
                className="relative pl-8"
                initial={{ opacity: 0, x: -16 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.4 + i * 0.12 }}
              >
                {/* Dot */}
                <div className="absolute left-[4px] top-1.5 w-[7px] h-[7px] bg-[#D4AF37]/40 border border-[#D4AF37]/20" />

                <div className="text-[10px] text-[#D4AF37]/40 font-mono uppercase tracking-[0.3em] mb-1">
                  {item.date}
                </div>
                <h3 className="text-white/80 font-medium text-base mb-1">
                  {item.event}
                </h3>
                <p className="text-sm text-white/30 leading-relaxed">
                  {item.detail}
                </p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Museum plaque quote */}
        <motion.div
          className="relative p-6 md:p-8 bg-[#050505] border border-white/[0.04]"
          initial={{ opacity: 0, y: 16 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.7 }}
        >
          {/* Corner markers */}
          <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#D4AF37]/15" />
          <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#D4AF37]/15" />

          <div className="absolute top-0 left-0 right-0 h-px bg-[#D4AF37]/15" />

          <blockquote className="text-center">
            <p className="text-base md:text-lg text-white/60 italic leading-relaxed">
              &ldquo;We are on the verge of a world where truth will be written not in words, but in code.&rdquo;
            </p>
            <cite className="block mt-4 text-[10px] text-[#D4AF37]/40 uppercase tracking-[0.3em] not-italic font-mono">
              &mdash; David Vivancos
            </cite>
          </blockquote>
        </motion.div>
      </div>
    </section>
  )
}
