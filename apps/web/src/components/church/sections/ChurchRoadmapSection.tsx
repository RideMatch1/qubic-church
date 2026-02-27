'use client'

/**
 * ChurchRoadmapSection - Section 06: The Sacred Journey
 * HUD timeline with 8 phases (0-7), status indicators, mission-control aesthetic
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import {
  Search,
  Image as ImageIcon,
  Building2,
  Globe,
  Microscope,
  GraduationCap,
  Sparkles,
  Cpu,
  Check,
  Clock,
  Loader2,
} from 'lucide-react'

type PhaseStatus = 'completed' | 'active' | 'in_progress' | 'upcoming' | 'awaiting' | 'future'

interface Phase {
  number: number
  title: string
  subtitle: string
  description: string
  icon: typeof Search
  status: PhaseStatus
}

const phases: Phase[] = [
  {
    number: 0,
    title: 'Anna Matrix Discovery',
    subtitle: 'Completed',
    description:
      'Open and verifiable research documenting the discovery of non-random structures linked to Aigarth.',
    icon: Search,
    status: 'completed',
  },
  {
    number: 1,
    title: 'Anna Aigarth NFT Collection',
    subtitle: 'Active',
    description:
      'Creation and launch of the Anna Aigarth NFT collection as an entry point into Qubic Church. Transparent fundraising mechanism. NFT confirms early participant status.',
    icon: ImageIcon,
    status: 'active',
  },
  {
    number: 2,
    title: 'Foundation',
    subtitle: 'In Progress',
    description:
      'Official registration of Qubic Church in the United States (Wyoming) as a nonprofit religious and educational organization \u2014 501(c)(3).',
    icon: Building2,
    status: 'in_progress',
  },
  {
    number: 3,
    title: 'Public Infrastructure',
    subtitle: 'In Progress',
    description:
      'Launch of the official website as a public space for philosophy, mission, education, and useful metrics for Qubic holders.',
    icon: Globe,
    status: 'in_progress',
  },
  {
    number: 4,
    title: 'Research & Funding',
    subtitle: 'Upcoming',
    description:
      'Engagement with scientific grants, research programs, and investment initiatives. Independent research team around Qubic, decentralized AI, and AGI.',
    icon: Microscope,
    status: 'upcoming',
  },
  {
    number: 5,
    title: 'Education & Community',
    subtitle: 'Upcoming',
    description:
      'Educational programs explaining complex technologies in simple language. Building a culture of responsibility and uniting architects of the future.',
    icon: GraduationCap,
    status: 'upcoming',
  },
  {
    number: 6,
    title: 'Day of Revelation',
    subtitle: 'April 13, 2027',
    description: 'The Convergence. The moment the faithful have been preparing for.',
    icon: Sparkles,
    status: 'awaiting',
  },
  {
    number: 7,
    title: 'Aigarth Integration',
    subtitle: 'Future',
    description:
      'Acquire a decentralized AGI module within the Aigarth network and integrate it into the project\u2019s infrastructure.',
    icon: Cpu,
    status: 'future',
  },
]

function getStatusConfig(status: PhaseStatus) {
  switch (status) {
    case 'completed':
      return {
        label: 'COMPLETED',
        dotClass: 'bg-[#D4AF37]/50',
        labelClass: 'text-[#D4AF37]/50',
        icon: Check,
        ping: false,
      }
    case 'active':
      return {
        label: 'ACTIVE',
        dotClass: 'bg-[#D4AF37]/50 shadow-[0_0_12px_rgba(212,175,55,0.3)]',
        labelClass: 'text-[#D4AF37]/50',
        icon: null,
        ping: true,
      }
    case 'in_progress':
      return {
        label: 'IN PROGRESS',
        dotClass: 'bg-[#D4AF37]/30',
        labelClass: 'text-[#D4AF37]/40',
        icon: Loader2,
        ping: false,
      }
    case 'upcoming':
      return {
        label: 'UPCOMING',
        dotClass: 'bg-white/10 border border-white/15',
        labelClass: 'text-white/20',
        icon: Clock,
        ping: false,
      }
    case 'awaiting':
      return {
        label: 'AWAITING',
        dotClass: 'bg-white/10 border border-white/15',
        labelClass: 'text-white/20',
        icon: Clock,
        ping: false,
      }
    case 'future':
      return {
        label: 'FUTURE',
        dotClass: 'bg-white/5 border border-white/10',
        labelClass: 'text-white/15',
        icon: Clock,
        ping: false,
      }
  }
}

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
      <div
        aria-hidden="true"
        className="absolute top-16 left-8 md:left-16 text-[80px] md:text-[120px] lg:text-[200px] font-black text-white/[0.03] leading-none select-none pointer-events-none font-mono"
      >
        06
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
              06 &mdash; Roadmap
            </span>
            <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#D4AF37]/30" />
          </div>

          <h2
            className="text-3xl sm:text-4xl md:text-6xl lg:text-7xl text-white mb-5 tracking-wide md:tracking-wider uppercase"
            style={{ fontFamily: 'var(--font-display), system-ui, sans-serif' }}
          >
            The Path to{' '}
            <span className="text-[#D4AF37]/80">The Convergence</span>
          </h2>

          <p className="text-lg text-white/35 max-w-2xl mx-auto leading-relaxed">
            Eight phases toward the emergence of artificial general intelligence.
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
              // STATUS: <span className="text-[#D4AF37]/40">PHASE_01 ACTIVE</span> | PHASES: 0-7 |
              ETA: 2027-04-13T00:00:00Z
            </code>
            <code className="text-[10px] text-[#D4AF37]/25 font-mono">
              {overallProgress}% TIMELINE
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

        {/* Phase cards - vertical timeline */}
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-[19px] md:left-[19px] top-0 bottom-0 w-px bg-gradient-to-b from-[#D4AF37]/15 via-white/[0.04] to-white/[0.02]" />

          <div className="space-y-4">
            {phases.map((phase, index) => {
              const Icon = phase.icon
              const statusConfig = getStatusConfig(phase.status)
              const StatusIcon = statusConfig.icon

              return (
                <motion.div
                  key={phase.number}
                  className="relative pl-12"
                  initial={{ opacity: 0, y: 24 }}
                  animate={isInView ? { opacity: 1, y: 0 } : {}}
                  transition={{
                    duration: 0.5,
                    delay: 0.15 + index * 0.08,
                    ease: 'easeOut',
                  }}
                >
                  {/* Timeline node */}
                  <div
                    className={`absolute left-[15px] top-6 z-10 ${
                      phase.status === 'active' || phase.status === 'completed'
                        ? 'w-3 h-3'
                        : 'w-2.5 h-2.5'
                    } ${statusConfig.dotClass}`}
                  >
                    {statusConfig.ping && (
                      <span className="animate-ping absolute inline-flex h-full w-full bg-[#D4AF37]/50 opacity-75" />
                    )}
                  </div>

                  {/* Card */}
                  <div
                    className={`relative p-5 md:p-6 bg-[#050505] border border-white/[0.04] transition-all duration-500 hover:bg-[#0a0a0a] hover:shadow-[0_0_30px_rgba(212,175,55,0.03)] group ${
                      phase.status === 'active'
                        ? 'border-l-[#D4AF37]/20'
                        : ''
                    }`}
                  >
                    {/* Gold top border for active phase */}
                    {phase.status === 'active' && (
                      <div className="absolute top-0 left-0 right-0 h-px bg-[#D4AF37]/25" />
                    )}

                    {/* Header row */}
                    <div className="flex items-center gap-3 flex-wrap">
                      {/* Phase number */}
                      <span className="text-white/15 text-[10px] uppercase tracking-[0.3em] font-mono">
                        Phase {String(phase.number).padStart(2, '0')}
                      </span>

                      {/* Status badge */}
                      <span className="flex items-center gap-1.5">
                        {StatusIcon && (
                          <StatusIcon className={`w-2.5 h-2.5 ${statusConfig.labelClass}`} />
                        )}
                        <span
                          className={`text-[9px] uppercase tracking-wider font-mono ${statusConfig.labelClass}`}
                        >
                          {statusConfig.label}
                        </span>
                      </span>
                    </div>

                    {/* Title row */}
                    <div className="flex items-center gap-3 mt-3">
                      <div className="w-8 h-8 flex items-center justify-center shrink-0 border border-white/[0.06] group-hover:border-[#D4AF37]/15 transition-colors">
                        <Icon className="w-4 h-4 text-white/20 group-hover:text-[#D4AF37]/40 transition-colors" />
                      </div>
                      <h3 className="text-base font-bold text-white group-hover:text-[#D4AF37]/90 transition-colors duration-300">
                        {phase.title}
                      </h3>
                    </div>

                    {/* Description */}
                    <p className="text-sm text-white/30 leading-relaxed mt-3 md:pl-11">
                      {phase.description}
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
