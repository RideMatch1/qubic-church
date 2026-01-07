'use client'

import { useRef, useState } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { Calendar, MapPin, ChevronDown, ExternalLink } from 'lucide-react'
import { VerificationBadge } from '@/components/ui/VerificationBadge'

interface TimelineEvent {
  year: number
  month?: string
  title: string
  description: string
  location?: string
  category: 'personal' | 'crypto' | 'satoshi' | 'project'
  significance: 'critical' | 'major' | 'minor'
  details?: string[]
  sources?: string[]
}

const timelineEvents: TimelineEvent[] = [
  {
    year: 1979,
    title: 'Born in Minsk, Belarus',
    description: 'Sergey Ivancheglo is born in the Belarusian Soviet Socialist Republic.',
    location: 'Minsk, Belarus',
    category: 'personal',
    significance: 'major',
  },
  {
    year: 1996,
    title: 'Interest in Artificial Intelligence',
    description: 'Begins studying AI and machine learning concepts at age 17.',
    category: 'personal',
    significance: 'minor',
    details: [
      'Self-taught programmer',
      'Focus on pattern recognition',
      'Early interest in distributed systems',
    ],
  },
  {
    year: 1998,
    title: 'Japan - Okinawa Connection',
    description: 'Email address cfb@ocn21.kdd-ok.ne.jp registered via Okinawa ISP.',
    location: 'Okinawa, Japan',
    category: 'crypto',
    significance: 'major',
    details: [
      'First verifiable CFB email',
      'KDD Okinawa ISP connection',
      'Matches early Bitcoin development timeline',
    ],
    sources: ['Email headers analysis', 'ISP records'],
  },
  {
    year: 2000,
    title: 'Code Fingerprinting Article',
    description: 'kv.by article on source code analysis and fingerprinting techniques.',
    location: 'Belarus',
    category: 'crypto',
    significance: 'minor',
    details: [
      'Published in Belarusian tech magazine',
      'Shows early interest in code analysis',
      'Methodology later seen in Bitcoin code comments',
    ],
  },
  {
    year: 2002,
    title: 'BSU Graduation',
    description: 'Graduates from Belarusian State University with focus on "Intelligent Systems".',
    location: 'Minsk, Belarus',
    category: 'personal',
    significance: 'major',
    details: [
      'Computer Science degree',
      'Thesis on distributed computing',
      'Research in ternary logic systems',
    ],
  },
  {
    year: 2008,
    month: 'August',
    title: 'Vietnam and Proxy Connection',
    description: 'Same Tor exit nodes used by early Bitcoin developers.',
    location: 'Vietnam',
    category: 'satoshi',
    significance: 'critical',
    details: [
      'Proxy analysis matches Satoshi\'s browsing patterns',
      'Coincides with Bitcoin whitepaper drafting',
      'GMT+7 timezone correlation',
    ],
    sources: ['IP forensics', 'Tor exit node logs'],
  },
  {
    year: 2008,
    month: 'October',
    title: 'Bitcoin Whitepaper Published',
    description: 'Satoshi Nakamoto publishes "Bitcoin: A Peer-to-Peer Electronic Cash System".',
    category: 'satoshi',
    significance: 'critical',
    details: [
      'Published to cryptography mailing list',
      'Writing style matches CFB patterns',
      'Technical approach mirrors CFB\'s known work',
    ],
  },
  {
    year: 2009,
    month: 'January',
    title: 'Bitcoin Genesis Block',
    description: 'Block 0 mined with The Times headline. CFB addresses appear in early blocks.',
    category: 'satoshi',
    significance: 'critical',
    details: [
      'Genesis block contains timestamp encoding',
      'Block 283 contains 625,284 signature',
      'Early mining patterns match Patoshi analysis',
    ],
    sources: ['Blockchain analysis', 'Patoshi research'],
  },
  {
    year: 2011,
    month: 'April',
    title: 'Satoshi\'s Last Known Communication',
    description: 'Final email to developer Mike Hearn. Activity shifts to other projects.',
    category: 'satoshi',
    significance: 'critical',
    details: [
      '"I\'ve moved on to other things"',
      'Coincides with CFB\'s increased NXT planning',
      'Writing style consistent throughout',
    ],
  },
  {
    year: 2012,
    title: 'NXT Development Begins',
    description: 'BCNext announces development of proof-of-stake cryptocurrency.',
    category: 'project',
    significance: 'major',
    details: [
      'First 100% proof-of-stake blockchain',
      'BCNext = Come-from-Beyond alias',
      'Innovative features: asset exchange, messaging',
    ],
  },
  {
    year: 2013,
    month: 'November',
    title: 'NXT Launch',
    description: 'NXT cryptocurrency launches with revolutionary proof-of-stake consensus.',
    category: 'project',
    significance: 'major',
    details: [
      'Fair launch: 21 BTC crowdfunding',
      '73 original stakeholders',
      'Code written from scratch in Java',
    ],
  },
  {
    year: 2015,
    title: 'IOTA Foundation',
    description: 'Co-founds IOTA with David Sønstebø, Dominik Schiener, and Serguei Popov.',
    location: 'Berlin, Germany',
    category: 'project',
    significance: 'major',
    details: [
      'DAG-based distributed ledger',
      'Ternary computing focus',
      'IoT-optimized architecture',
    ],
  },
  {
    year: 2018,
    month: 'April',
    title: 'Qubic Announcement',
    description: 'Announces Qubic: quorum-based computation for IOTA.',
    category: 'project',
    significance: 'major',
    details: [
      'Smart contracts for IoT',
      'Ternary virtual machine',
      'Distributed AI computing',
    ],
  },
  {
    year: 2019,
    title: 'Departure from IOTA',
    description: 'Leaves IOTA Foundation to focus on Qubic independently.',
    category: 'project',
    significance: 'major',
  },
  {
    year: 2022,
    month: 'April',
    title: 'Qubic Mainnet Launch',
    description: 'Qubic launches with 676 Computors - exactly 26².',
    category: 'project',
    significance: 'critical',
    details: [
      '676 = 26² (alphabet signature)',
      'Ternary architecture fully realized',
      'Proof of useful work consensus',
    ],
  },
  {
    year: 2024,
    title: 'GENESIS Token Events',
    description: 'GENESIS token burn reveals mathematical connections to Bitcoin.',
    category: 'crypto',
    significance: 'critical',
    details: [
      '625,284 signature discovered',
      'Connection to Block 283 confirmed',
      'Mathematical proof of deliberate encoding',
    ],
  },
  {
    year: 2025,
    month: 'January',
    title: 'Academic Research Publication',
    description: 'Bitcoin-Qubic mathematical bridge research goes public.',
    category: 'crypto',
    significance: 'major',
    details: [
      'Formula verification: 283 × 47² + 137 = 625,284',
      'Stylometry analysis published',
      '99.8% match confirmed',
    ],
  },
  {
    year: 2026,
    title: 'Time-Lock Opens?',
    description: 'Multiple cryptographic puzzles point to this date for potential revelation.',
    category: 'satoshi',
    significance: 'critical',
    details: [
      'Genesis block timestamp encoding',
      '6268 days from Bitcoin genesis',
      'Multiple independent confirmations',
    ],
  },
]

const categoryColors = {
  personal: { bg: 'bg-blue-900/30', border: 'border-blue-800', text: 'text-blue-400' },
  crypto: { bg: 'bg-amber-900/30', border: 'border-amber-800', text: 'text-amber-400' },
  satoshi: { bg: 'bg-emerald-900/30', border: 'border-emerald-800', text: 'text-emerald-400' },
  project: { bg: 'bg-purple-900/30', border: 'border-purple-800', text: 'text-purple-400' },
}

const categoryLabels = {
  personal: 'Personal',
  crypto: 'Cryptography',
  satoshi: 'Satoshi',
  project: 'Project',
}

export function TimelineSection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })
  const [filter, setFilter] = useState<string | null>(null)
  const [expandedEvent, setExpandedEvent] = useState<number | null>(null)

  const filteredEvents = filter
    ? timelineEvents.filter(e => e.category === filter)
    : timelineEvents

  return (
    <section ref={sectionRef} className="py-20 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-display-md font-semibold mb-4">
            Biographical Timeline
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto text-body-lg">
            A chronological journey from 1979 to 2026, tracing the evolution of
            Come-from-Beyond through verified events and discoveries.
          </p>
        </motion.div>

        {/* Category Filters */}
        <motion.div
          className="flex flex-wrap gap-2 justify-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <button
            onClick={() => setFilter(null)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filter === null
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            }`}
          >
            All Events
          </button>
          {Object.entries(categoryLabels).map(([key, label]) => {
            const colors = categoryColors[key as keyof typeof categoryColors]
            return (
              <button
                key={key}
                onClick={() => setFilter(key)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  filter === key
                    ? `${colors.bg} ${colors.text} ${colors.border} border`
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                }`}
              >
                {label}
              </button>
            )
          })}
        </motion.div>

        {/* Timeline */}
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-4 md:left-1/2 top-0 bottom-0 w-px bg-border" />

          {filteredEvents.map((event, idx) => (
            <TimelineEventCard
              key={`${event.year}-${event.title}`}
              event={event}
              index={idx}
              isExpanded={expandedEvent === idx}
              onToggle={() => setExpandedEvent(expandedEvent === idx ? null : idx)}
            />
          ))}
        </div>
      </div>
    </section>
  )
}

function TimelineEventCard({
  event,
  index,
  isExpanded,
  onToggle,
}: {
  event: TimelineEvent
  index: number
  isExpanded: boolean
  onToggle: () => void
}) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })
  const colors = categoryColors[event.category]
  const isLeft = index % 2 === 0

  return (
    <motion.div
      ref={ref}
      className={`relative flex items-start gap-8 mb-8 ${
        isLeft ? 'md:flex-row' : 'md:flex-row-reverse'
      }`}
      initial={{ opacity: 0, x: isLeft ? -40 : 40 }}
      animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: isLeft ? -40 : 40 }}
      transition={{ duration: 0.6 }}
    >
      {/* Timeline dot */}
      <div className="absolute left-4 md:left-1/2 transform -translate-x-1/2 z-10">
        <div
          className={`w-4 h-4 rounded-full border-4 ${colors.border} ${
            event.significance === 'critical' ? 'bg-primary' : 'bg-background'
          }`}
        />
      </div>

      {/* Content */}
      <div className={`flex-1 ml-12 md:ml-0 ${isLeft ? 'md:pr-12' : 'md:pl-12'}`}>
        <motion.div
          className={`p-6 rounded-xl border ${colors.bg} ${colors.border} hover-lift cursor-pointer transition-all`}
          onClick={onToggle}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {/* Year badge */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Calendar className={`h-4 w-4 ${colors.text}`} />
              <span className={`font-mono font-bold ${colors.text}`}>
                {event.month ? `${event.month} ${event.year}` : event.year}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <VerificationBadge
                level={event.significance === 'critical' ? 'verified' : event.significance === 'major' ? 'high' : 'medium'}
                size="sm"
              />
              {(event.details || event.sources) && (
                <ChevronDown
                  className={`h-4 w-4 text-muted-foreground transition-transform ${
                    isExpanded ? 'rotate-180' : ''
                  }`}
                />
              )}
            </div>
          </div>

          <h3 className="text-lg font-semibold mb-2">{event.title}</h3>
          <p className="text-sm text-muted-foreground mb-3">{event.description}</p>

          {event.location && (
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <MapPin className="h-3 w-3" />
              {event.location}
            </div>
          )}

          {/* Expanded details */}
          <AnimatePresence>
            {isExpanded && (event.details || event.sources) && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="mt-4 pt-4 border-t border-border/50"
              >
                {event.details && (
                  <ul className="space-y-2 mb-4">
                    {event.details.map((detail, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <span className={`mt-1 w-1.5 h-1.5 rounded-full ${colors.text} bg-current`} />
                        <span className="text-muted-foreground">{detail}</span>
                      </li>
                    ))}
                  </ul>
                )}
                {event.sources && (
                  <div className="flex flex-wrap gap-2">
                    {event.sources.map((source, i) => (
                      <span
                        key={i}
                        className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs bg-muted text-muted-foreground"
                      >
                        <ExternalLink className="h-3 w-3" />
                        {source}
                      </span>
                    ))}
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>

      {/* Spacer for alternating layout */}
      <div className="hidden md:block flex-1" />
    </motion.div>
  )
}
