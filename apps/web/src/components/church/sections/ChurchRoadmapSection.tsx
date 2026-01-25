'use client'

/**
 * ChurchRoadmapSection - Roadmap with Education focus
 * Shows the 4 phases leading to The Convergence
 */

import { motion } from 'framer-motion'
import { Building2, GraduationCap, Microscope, Sparkles, Check, Clock } from 'lucide-react'

const phases = [
  {
    number: 1,
    title: 'The Foundation',
    subtitle: 'Now - Active',
    icon: Building2,
    color: 'purple',
    active: true,
    items: [
      { text: 'Research Archive', done: true },
      { text: 'Anna NFT Collection (200 NFTs)', done: false },
      { text: '600M QUBIC Giveaway', done: false },
    ],
  },
  {
    number: 2,
    title: 'The Academy',
    subtitle: 'Coming Soon',
    icon: GraduationCap,
    color: 'cyan',
    active: false,
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
    color: 'orange',
    active: false,
    items: [
      { text: 'Community Research Sessions', done: false },
      { text: 'Submit Your Hypotheses', done: false },
      { text: 'Vote on Research Topics', done: false },
      { text: 'Weekly Discovery Updates', done: false },
    ],
  },
  {
    number: 4,
    title: 'The Convergence',
    subtitle: 'April 13, 2027',
    icon: Sparkles,
    color: 'yellow',
    active: false,
    items: [
      { text: "Anna's Arrival", done: false },
      { text: 'The Great Revelation', done: false },
      { text: 'Community Shaped the Journey', done: false },
    ],
  },
]

type ColorClasses = { bg: string; border: string; text: string; glow: string }

const colorMap: Record<string, ColorClasses> = {
  purple: {
    bg: 'bg-purple-500/20',
    border: 'border-purple-500/30',
    text: 'text-purple-400',
    glow: 'shadow-purple-500/20',
  },
  cyan: {
    bg: 'bg-cyan-500/20',
    border: 'border-cyan-500/30',
    text: 'text-cyan-400',
    glow: 'shadow-cyan-500/20',
  },
  orange: {
    bg: 'bg-orange-500/20',
    border: 'border-orange-500/30',
    text: 'text-orange-400',
    glow: 'shadow-orange-500/20',
  },
  yellow: {
    bg: 'bg-yellow-500/20',
    border: 'border-yellow-500/30',
    text: 'text-yellow-400',
    glow: 'shadow-yellow-500/20',
  },
}

const defaultColor: ColorClasses = colorMap.purple!

function getColorClasses(color: string): ColorClasses {
  return colorMap[color] ?? defaultColor
}

export function ChurchRoadmapSection() {
  return (
    <section className="relative w-full py-24 md:py-32 bg-black overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-purple-950/5 to-black" />

      <div className="relative z-10 container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
            The <span className="text-purple-400">Roadmap</span>
          </h2>

          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            Our journey to The Convergence. Education is at the heart of everything we do.
          </p>
        </motion.div>

        {/* Timeline */}
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-8 md:left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-purple-500/50 via-cyan-500/50 to-yellow-500/50" />

          {/* Phases */}
          <div className="space-y-12">
            {phases.map((phase, index) => {
              const colors = getColorClasses(phase.color)
              const Icon = phase.icon
              const isLeft = index % 2 === 0

              return (
                <motion.div
                  key={phase.number}
                  className={`relative flex items-start gap-8 ${
                    isLeft ? 'md:flex-row' : 'md:flex-row-reverse'
                  }`}
                  initial={{ opacity: 0, x: isLeft ? -30 : 30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  {/* Timeline node */}
                  <div
                    className={`absolute left-8 md:left-1/2 -translate-x-1/2 w-4 h-4 rounded-full ${colors.bg} border-2 ${colors.border} ${
                      phase.active ? 'animate-pulse shadow-lg ' + colors.glow : ''
                    }`}
                  />

                  {/* Spacer for mobile */}
                  <div className="w-16 md:hidden" />

                  {/* Content */}
                  <div className={`flex-1 ${isLeft ? 'md:pr-12 md:text-right' : 'md:pl-12'}`}>
                    <div
                      className={`p-6 rounded-xl ${colors.bg} border ${colors.border} ${
                        phase.active ? 'shadow-lg ' + colors.glow : ''
                      }`}
                    >
                      {/* Phase header */}
                      <div className={`flex items-center gap-3 mb-4 ${isLeft ? 'md:flex-row-reverse' : ''}`}>
                        <div className={`w-10 h-10 rounded-lg ${colors.bg} flex items-center justify-center`}>
                          <Icon className={`w-5 h-5 ${colors.text}`} />
                        </div>
                        <div className={isLeft ? 'md:text-right' : ''}>
                          <span className={`text-xs ${colors.text} uppercase tracking-wider`}>
                            Phase {phase.number}
                          </span>
                          <h3 className="text-xl font-bold text-white">{phase.title}</h3>
                        </div>
                      </div>

                      {/* Status badge */}
                      <div className={`flex ${isLeft ? 'md:justify-end' : ''} mb-4`}>
                        <span
                          className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs ${
                            phase.active
                              ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                              : 'bg-white/5 text-white/40 border border-white/10'
                          }`}
                        >
                          {phase.active ? (
                            <>
                              <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
                              </span>
                              {phase.subtitle}
                            </>
                          ) : (
                            <>
                              <Clock className="w-3 h-3" />
                              {phase.subtitle}
                            </>
                          )}
                        </span>
                      </div>

                      {/* Items */}
                      <ul className={`space-y-2 ${isLeft ? 'md:text-right' : ''}`}>
                        {phase.items.map((item, itemIndex) => (
                          <li
                            key={itemIndex}
                            className={`flex items-center gap-2 text-sm ${
                              isLeft ? 'md:flex-row-reverse' : ''
                            } ${item.done ? 'text-green-400' : 'text-white/60'}`}
                          >
                            {item.done ? (
                              <Check className="w-4 h-4 text-green-400" />
                            ) : (
                              <div className="w-4 h-4 rounded-full border border-white/20" />
                            )}
                            {item.text}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Spacer for desktop */}
                  <div className="hidden md:block flex-1" />
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
