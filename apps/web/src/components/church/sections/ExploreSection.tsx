'use client'

/**
 * ExploreSection - Links to Archive, Journey, and Challenges
 */

import { motion } from 'framer-motion'
import Link from 'next/link'
import { BookOpen, Rocket, Puzzle, ArrowRight, Clock } from 'lucide-react'

const sections = [
  {
    title: 'The Archive',
    description: '75+ research documents, all open source. Mathematical proofs, pattern discoveries, and verified findings.',
    href: '/docs',
    icon: BookOpen,
    color: 'orange',
    badge: '75+ Docs',
  },
  {
    title: 'The Journey',
    description: 'A 12-phase immersive story. From the Genesis Block to the ultimate revelation.',
    href: '/timeline',
    icon: Rocket,
    color: 'purple',
    badge: '12 Phases',
  },
  {
    title: 'Intelligence Challenges',
    description: 'Test your pattern recognition skills. Cryptographic puzzles with role-based bonuses.',
    href: '/challenges',
    icon: Puzzle,
    color: 'cyan',
    badge: 'Coming Soon',
    disabled: true,
  },
]

type ColorClasses = { bg: string; border: string; text: string; hover: string }

const colorMap: Record<string, ColorClasses> = {
  orange: {
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/20 hover:border-orange-500/40',
    text: 'text-orange-400',
    hover: 'group-hover:text-orange-300',
  },
  purple: {
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/20 hover:border-purple-500/40',
    text: 'text-purple-400',
    hover: 'group-hover:text-purple-300',
  },
  cyan: {
    bg: 'bg-cyan-500/10',
    border: 'border-cyan-500/20',
    text: 'text-cyan-400',
    hover: '',
  },
}

const defaultColor: ColorClasses = colorMap.purple!

function getColorClasses(color: string): ColorClasses {
  return colorMap[color] ?? defaultColor
}

export function ExploreSection() {
  return (
    <section className="relative w-full py-24 md:py-32 bg-black overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-purple-950/5 to-black" />

      <div className="relative z-10 container mx-auto px-4 max-w-5xl">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Explore the Research
          </h2>
          <p className="text-lg text-white/60 max-w-xl mx-auto">
            Dive deeper into our discoveries
          </p>
        </motion.div>

        {/* Cards */}
        <div className="grid md:grid-cols-3 gap-6">
          {sections.map((section, index) => {
            const colors = getColorClasses(section.color)
            const Icon = section.icon
            const Component = section.disabled ? 'div' : Link

            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Component
                  href={section.disabled ? '#' : section.href}
                  className={`block h-full p-6 rounded-2xl ${colors.bg} border ${colors.border} transition-all ${
                    section.disabled ? 'opacity-60 cursor-not-allowed' : 'group cursor-pointer hover:scale-[1.02]'
                  }`}
                >
                  {/* Badge */}
                  <div className="flex items-center justify-between mb-4">
                    <div className={`w-12 h-12 rounded-xl ${colors.bg} flex items-center justify-center`}>
                      <Icon className={`w-6 h-6 ${colors.text}`} />
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        section.disabled
                          ? 'bg-white/5 text-white/40'
                          : `${colors.bg} ${colors.text}`
                      }`}
                    >
                      {section.disabled && <Clock className="w-3 h-3 inline mr-1" />}
                      {section.badge}
                    </span>
                  </div>

                  {/* Title */}
                  <h3 className={`text-xl font-semibold text-white mb-2 ${colors.hover}`}>
                    {section.title}
                  </h3>

                  {/* Description */}
                  <p className="text-sm text-white/50 mb-4 leading-relaxed">
                    {section.description}
                  </p>

                  {/* CTA */}
                  {!section.disabled && (
                    <div className={`flex items-center gap-1 text-sm ${colors.text} ${colors.hover}`}>
                      <span>Explore</span>
                      <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                    </div>
                  )}
                </Component>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
