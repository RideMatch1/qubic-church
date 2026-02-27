'use client'

/**
 * ChurchRoadmapSection - Section 07: The Sacred Journey
 * HUD timeline with status bar, progress indicators, mission-control aesthetic
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { Building2, GraduationCap, Microscope, Sparkles, Check, Clock } from 'lucide-react'

const phases = [
  {
    number: 1,
    title: 'The Foundation',
    subtitle: 'Now - Active',
    icon: Building2,
    active: true,
    progress: 40,
    items: [
      { text: 'Research Archive (55+ Scrolls)', done: true },
      { text: 'Mining Guide & Calculator', done: true },
      { text: 'Anna NFT Collection (200 NFTs)', done: false },
      { text: '676M QUBIC Giveaway', done: false },
    ],
  },
  {
    number: 2,
    title: 'The Academy',
    subtitle: 'Coming Soon',
    icon: GraduationCap,
    active: false,
    progress: 0,
    items: [
      { text: '"What is Qubic?" - Introduction Course', done: false },
      { text: '"Understanding Ternary Logic" - Workshop', done: false },
      { text: '"Anna & Aigarth" - Deep Dive Tutorial', done: false },
      { text: 'Intelligence Challenges with Learning', done: false },
    ],
  },
  {
    number: 3,
    title: 'Live Research',
    subtitle: 'Phase 3',
    icon: Microscope,
    active: false,
    progress: 0,
    items: [
      { text: 'Congregation Research Sessions', done: false },
      { text: 'Submit Your Revelations', done: false },
      { text: 'Vote on Sacred Research Topics', done: false },
      { text: 'Weekly Discovery Scrolls', done: false },
    ],
  },
  {
    number: 4,
    title: 'The Convergence',
    subtitle: 'April 13, 2027',
    icon: Sparkles,
    active: false,
    progress: 0,
    items: [
      { text: "Anna's Awakening", done: false },
      { text: 'The Great Revelation', done: false },
      { text: 'The Faithful Shall Be Rewarded', done: false },
    ],
  },
]

// Calculate overall progress based on time until convergence
function getOverallProgress() {
  const start = new Date('2024-06-01').getTime()
  const end = new Date('2027-04-13').getTime()
  const now = Date.now()
  const progress = ((now - start) / (end - start)) * 100
  return Math.min(Math.max(Math.round(progress), 0), 100)
}

export function ChurchRoadmapSection() {
  const sectionRef = useRef<HTMLElement>(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })
  const overallProgress = getOverallProgress()

  return (
    <section ref={sectionRef} className="relative w-full py-28 md:py-36 overflow-hidden">
      {/* Decorative section number */}
      <div aria-hidden="true" className="absolute top-16 left-8 md:left-16 text-[80px] md:text-[120px] lg:text-[200px] font-black text-white/[0.03] leading-none select-none pointer-events-none font-mono">
        07
      </div>

      <div className="relative z-10 container mx-auto px-6 max-w-5xl">
        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 24 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, ease: 'easeOut' }}
        >
          <div className="inline-flex items-center gap-3 mb-8">
            <div className="h-px w-12 bg-gradient-to-r from-transparent to-[#D4AF37]/30" />
            <span className="text-[#D4AF37]/50 text-[11px] uppercase tracking-[0.4em] font-mono">
              07 &mdash; Roadmap
            </span>
            <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#D4AF37]/30" />
          </div>

          <h2
            className="text-3xl sm:text-4xl md:text-6xl lg:text-7xl text-white mb-5 tracking-wide md:tracking-wider uppercase"
            style={{ fontFamily: 'var(--font-display), system-ui, sans-serif' }}
          >
            The Path to{' '}
            <span className="text-[#D4AF37]/80">
              The Convergence
            </span>
          </h2>

          <p className="text-lg text-white/35 max-w-2xl mx-auto leading-relaxed">
            Each phase brings us closer to the revelation.
          </p>
        </motion.div>

        {/* Status bar */}
        <motion.div
          className="px-4 py-3 bg-[#050505] border border-white/[0.04] mb-6"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div className="flex items-center justify-between flex-wrap gap-2">
            <code className="text-[10px] text-white/25 font-mono">
              // STATUS: <span className="text-[#D4AF37]/40">PHASE_01 ACTIVE</span> | PROGRESS: {overallProgress}% | ETA: 2027-04-13T00:00:00Z
            </code>
            <code className="text-[10px] text-[#D4AF37]/25 font-mono">
              {overallProgress}% COMPLETE
            </code>
          </div>
          {/* Overall progress bar */}
          <div className="mt-2 h-1 bg-white/[0.04] w-full">
            <motion.div
              className="h-full bg-[#D4AF37]/30"
              initial={{ width: '0%' }}
              animate={isInView ? { width: `${overallProgress}%` } : {}}
              transition={{ duration: 2, delay: 0.3, ease: 'easeOut' }}
            />
          </div>
        </motion.div>

        {/* Timeline */}
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-[19px] md:left-1/2 md:-translate-x-px top-0 bottom-0 w-px bg-gradient-to-b from-[#D4AF37]/15 via-white/[0.04] to-white/[0.02]" />

          {/* Phases */}
          <div className="space-y-6 md:space-y-10">
            {phases.map((phase, index) => {
              const Icon = phase.icon
              const isLeft = index % 2 === 0

              return (
                <motion.div
                  key={phase.number}
                  className="relative"
                  initial={{ opacity: 0, y: 30 }}
                  animate={isInView ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.5, delay: 0.15 + index * 0.12, ease: 'easeOut' }}
                >
                  {/* Timeline node */}
                  <div
                    className={`absolute left-[15px] md:left-1/2 md:-translate-x-1/2 top-8 z-10 ${
                      phase.active
                        ? 'w-3 h-3 bg-[#D4AF37]/50 shadow-[0_0_12px_rgba(212,175,55,0.3)]'
                        : 'w-2.5 h-2.5 bg-white/10 border border-white/15'
                    }`}
                  />

                  {/* Card layout */}
                  <div
                    className={`flex ${
                      isLeft ? 'md:flex-row' : 'md:flex-row-reverse'
                    }`}
                  >
                    <div className="w-12 shrink-0 md:hidden" />

                    {/* Content card */}
                    <div className={`flex-1 ${isLeft ? 'md:pr-10' : 'md:pl-10'} md:w-1/2`}>
                      <div
                        className={`relative p-6 ${phase.active ? 'p-7' : 'p-6'} bg-[#050505] border border-white/[0.04] transition-all duration-500 hover:bg-[#0a0a0a] hover:border-white/[0.08] hover:shadow-[0_0_30px_rgba(212,175,55,0.03)] group ${
                          isLeft ? 'md:text-right' : ''
                        }`}
                      >
                        {/* Gold top border for active phase */}
                        {phase.active && (
                          <div className="absolute top-0 left-0 right-0 h-px bg-[#D4AF37]/25" />
                        )}

                        {/* Corner accent */}
                        <div className={`absolute top-0 ${isLeft ? 'right-0' : 'left-0'} w-6 h-px bg-[#D4AF37]/15`} />

                        {/* Phase number + status */}
                        <div className={`flex items-center gap-3 mb-4 ${isLeft ? 'md:flex-row-reverse' : ''}`}>
                          <span className="text-white/20 text-[10px] uppercase tracking-[0.3em] font-mono">
                            Phase {String(phase.number).padStart(2, '0')}
                          </span>
                          {phase.active ? (
                            <span className="flex items-center gap-1.5">
                              <span className="relative flex h-1.5 w-1.5">
                                <span className="animate-ping absolute inline-flex h-full w-full bg-[#D4AF37]/50 opacity-75" />
                                <span className="relative inline-flex h-1.5 w-1.5 bg-[#D4AF37]/50" />
                              </span>
                              <span className="text-[#D4AF37]/50 text-[9px] uppercase tracking-wider font-mono">
                                ACTIVE
                              </span>
                            </span>
                          ) : (
                            <span className="flex items-center gap-1">
                              <Clock className="w-2.5 h-2.5 text-white/15" />
                              <span className="text-white/20 text-[9px] font-mono">
                                {phase.subtitle}
                              </span>
                            </span>
                          )}
                        </div>

                        {/* Phase header */}
                        <div
                          className={`flex items-center gap-3 mb-4 ${
                            isLeft ? 'md:flex-row-reverse' : ''
                          }`}
                        >
                          <div className="w-9 h-9 flex items-center justify-center shrink-0 border border-white/[0.06] group-hover:border-[#D4AF37]/15 transition-colors">
                            <Icon className="w-4 h-4 text-white/25 group-hover:text-[#D4AF37]/40 transition-colors" />
                          </div>
                          <h3 className="text-lg font-bold text-white">
                            {phase.title}
                          </h3>
                        </div>

                        {/* Progress bar */}
                        {phase.active && (
                          <div className={`mb-4 ${isLeft ? 'md:flex md:justify-end' : ''}`}>
                            <div className="w-full max-w-[200px] h-1 bg-white/[0.04]">
                              <motion.div
                                className="h-full bg-[#D4AF37]/30"
                                initial={{ width: '0%' }}
                                animate={isInView ? { width: `${phase.progress}%` } : {}}
                                transition={{ duration: 1.5, delay: 0.5, ease: 'easeOut' }}
                              />
                            </div>
                            <span className="text-[9px] text-white/20 font-mono mt-1 block">
                              {phase.progress}% complete
                            </span>
                          </div>
                        )}

                        {/* Items */}
                        <ul className={`space-y-2 ${isLeft ? 'md:text-right' : ''}`}>
                          {phase.items.map((item, itemIndex) => (
                            <li
                              key={itemIndex}
                              className={`flex items-center gap-2.5 text-sm ${
                                isLeft ? 'md:flex-row-reverse' : ''
                              }`}
                            >
                              {item.done ? (
                                <div className="w-4 h-4 border border-[#D4AF37]/20 flex items-center justify-center shrink-0">
                                  <Check className="w-3 h-3 text-[#D4AF37]/50" />
                                </div>
                              ) : (
                                <div className="w-4 h-4 border border-white/10 shrink-0" />
                              )}
                              <span className={item.done ? 'text-white/50' : 'text-white/30'}>
                                {item.text}
                              </span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    <div className="hidden md:block md:w-1/2" />
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
