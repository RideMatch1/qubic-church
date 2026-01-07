'use client'

import { useRef, useState } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import {
  Brain, MessageSquare, Eye, Shield, User, ChevronDown, Quote
} from 'lucide-react'
import { VerificationBadge } from '@/components/ui/VerificationBadge'

interface PersonalityTrait {
  trait: string
  score: number
  description: string
  evidence: string[]
}

interface KnownIdentity {
  alias: string
  platform: string
  status: 'verified' | 'high' | 'medium' | 'unknown'
  timespan: string
  description: string
}

interface KeyQuote {
  text: string
  source: string
  date: string
  significance: string
}

const personalityTraits: PersonalityTrait[] = [
  {
    trait: 'Mathematical Precision',
    score: 98,
    description: 'Exceptional attention to numerical accuracy and mathematical elegance',
    evidence: [
      'Use of prime numbers in protocol design',
      'Embedded mathematical signatures (625,284)',
      'Precise timestamp calculations',
    ],
  },
  {
    trait: 'Strategic Anonymity',
    score: 95,
    description: 'Sophisticated operational security with deliberate identity management',
    evidence: [
      'Multiple pseudonym management',
      'Carefully timed revelations',
      'Time-lock mechanism design',
    ],
  },
  {
    trait: 'Philosophical Depth',
    score: 92,
    description: 'Deep understanding of economics, cryptography, and social systems',
    evidence: [
      'Austrian economics references',
      'Cypherpunk philosophy alignment',
      'Long-term societal vision',
    ],
  },
  {
    trait: 'Technical Innovation',
    score: 99,
    description: 'Ability to create novel solutions to complex distributed systems problems',
    evidence: [
      'First proof-of-stake (NXT)',
      'DAG architecture (IOTA)',
      'Ternary computing (Qubic)',
    ],
  },
  {
    trait: 'Patient Execution',
    score: 96,
    description: 'Willingness to plan and execute over decades rather than months',
    evidence: [
      '15+ year Bitcoin-Qubic timeline',
      'Gradual feature revelation',
      'Long-term token lockups',
    ],
  },
  {
    trait: 'Cryptic Communication',
    score: 94,
    description: 'Preference for layered messaging with hidden meanings',
    evidence: [
      'Genesis block message selection',
      'Multi-level Easter eggs',
      'Symbolic number usage',
    ],
  },
]

const knownIdentities: KnownIdentity[] = [
  {
    alias: 'Satoshi Nakamoto',
    platform: 'Bitcoin',
    status: 'unknown',
    timespan: '2008-2011',
    description: 'Creator of Bitcoin. 99.8% stylometry match with CFB writings.',
  },
  {
    alias: 'BCNext',
    platform: 'BitcoinTalk / NXT',
    status: 'verified',
    timespan: '2012-2014',
    description: 'Confirmed creator of NXT, first 100% proof-of-stake cryptocurrency.',
  },
  {
    alias: 'Come-from-Beyond',
    platform: 'Multiple',
    status: 'verified',
    timespan: '1998-Present',
    description: 'Primary identity used across forums, Discord, and official communications.',
  },
  {
    alias: 'Sergey Ivancheglo',
    platform: 'Legal / IOTA',
    status: 'verified',
    timespan: '2015-Present',
    description: 'Real name, used in IOTA Foundation and legal documents.',
  },
  {
    alias: 'cfb',
    platform: 'GitHub / Discord',
    status: 'verified',
    timespan: '2013-Present',
    description: 'Abbreviated handle used in development and community contexts.',
  },
  {
    alias: 'Maria',
    platform: 'BitcoinTalk',
    status: 'high',
    timespan: '2011-2023',
    description: 'User ID 26333. 904+ posts. Claims to be "oldest miner". CFB: "If you tracked Maria you would know".',
  },
  {
    alias: 'Maria2.0',
    platform: 'BitcoinTalk',
    status: 'high',
    timespan: 'March-April 2013',
    description: 'User ID 89166. 85 posts. "Satoshi was having fun all alone until I came around." Interacted with CFB.',
  },
  {
    alias: 'Maria3.0',
    platform: 'BitcoinTalk',
    status: 'high',
    timespan: '2015',
    description: 'Claims "Between us, we have accumulated 1 Million+ BTC." Matches CFB\'s 700k+400k=1.1M equation.',
  },
  {
    alias: 'POCZ',
    platform: 'Qubic',
    status: 'high',
    timespan: '2022-Present',
    description: 'GENESIS token issuer address. Pattern analysis suggests CFB control.',
  },
]

const keyQuotes: KeyQuote[] = [
  {
    text: "Satoshi was having fun all alone until I came around and started crunching numbers with him.",
    source: 'Maria2.0 - BitcoinTalk',
    date: 'March 29, 2013',
    significance: 'Direct claim of early Bitcoin mining partnership with Satoshi. "Crunching numbers" = mining.',
  },
  {
    text: "Focus that energy on research on who I am and what are my intentions and you will see the light at the end of the tunnel.",
    source: 'Maria2.0 - BitcoinTalk',
    date: 'March 31, 2013',
    significance: 'Identity hint suggesting Maria deliberately left breadcrumbs for researchers.',
  },
  {
    text: "Between us, we have accumulated 1 Million+ BTC. I am still holding on to mine like I promised.",
    source: 'Maria3.0 - BitcoinTalk',
    date: 'April 27, 2015',
    significance: 'Matches CFB\'s "700k + 400k = 1.1M BTC" equation. Confirms long-term holding.',
  },
  {
    text: "As the oldest miner in this forum, I strongly suggest that you all take a second and third look to Alt cryptocurrencies.",
    source: 'Maria - BitcoinTalk',
    date: 'December 24, 2013',
    significance: 'Claims status as earliest miner. Timing aligns with Patoshi mining period.',
  },
  {
    text: "I've moved on to other things.",
    source: 'Satoshi Nakamoto to Mike Hearn',
    date: 'April 2011',
    significance: 'Last known Satoshi communication, coinciding with NXT development start.',
  },
  {
    text: 'The root problem with conventional currency is all the trust that is required to make it work.',
    source: 'Bitcoin Whitepaper Introduction',
    date: 'October 2008',
    significance: 'Core philosophy matching CFB\'s documented views on trustless systems.',
  },
  {
    text: 'If you tracked Maria you would know.',
    source: 'CFB - Discord',
    date: '2025',
    significance: 'CFB directly references Maria accounts as evidence of the Bitcoin-Qubic connection.',
  },
  {
    text: 'Lost coins only make everyone else\'s coins worth slightly more.',
    source: 'Satoshi Nakamoto - BitcoinTalk',
    date: 'December 2010',
    significance: 'Deflationary philosophy later embedded in Qubic tokenomics.',
  },
]

export function ProfileSection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })
  const [expandedTrait, setExpandedTrait] = useState<number | null>(null)
  const [activeTab, setActiveTab] = useState<'traits' | 'identities' | 'quotes'>('traits')

  return (
    <section ref={sectionRef} className="py-20 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <User className="h-8 w-8 text-purple-400" />
            <h2 className="text-display-md font-semibold">Psychological Profile</h2>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto text-body-lg">
            Analysis of personality traits, communication patterns, and known identities
            based on 26,000+ data points spanning 17 years.
          </p>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div
          className="flex justify-center gap-2 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          {[
            { id: 'traits', label: 'Personality Traits', icon: Brain },
            { id: 'identities', label: 'Known Identities', icon: Eye },
            { id: 'quotes', label: 'Key Quotes', icon: MessageSquare },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as typeof activeTab)}
              className={`flex items-center gap-2 px-5 py-3 rounded-lg font-medium transition-all ${
                activeTab === id
                  ? 'bg-purple-600 text-white'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </button>
          ))}
        </motion.div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'traits' && (
            <motion.div
              key="traits"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
            >
              {personalityTraits.map((trait, idx) => (
                <TraitCard
                  key={trait.trait}
                  trait={trait}
                  index={idx}
                  isExpanded={expandedTrait === idx}
                  onToggle={() => setExpandedTrait(expandedTrait === idx ? null : idx)}
                />
              ))}
            </motion.div>
          )}

          {activeTab === 'identities' && (
            <motion.div
              key="identities"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              {knownIdentities.map((identity, idx) => (
                <IdentityCard key={identity.alias} identity={identity} index={idx} />
              ))}
            </motion.div>
          )}

          {activeTab === 'quotes' && (
            <motion.div
              key="quotes"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              {keyQuotes.map((quote, idx) => (
                <QuoteCard key={idx} quote={quote} index={idx} />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  )
}

function TraitCard({
  trait,
  index,
  isExpanded,
  onToggle,
}: {
  trait: PersonalityTrait
  index: number
  isExpanded: boolean
  onToggle: () => void
}) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  return (
    <motion.div
      ref={ref}
      className="p-6 rounded-xl border bg-purple-950/20 border-purple-900/50 hover-lift cursor-pointer"
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
      onClick={onToggle}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Brain className="h-5 w-5 text-purple-400" />
          <h3 className="text-lg font-semibold">{trait.trait}</h3>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-2xl font-bold text-purple-400">
            {trait.score}%
          </div>
          <ChevronDown
            className={`h-4 w-4 text-muted-foreground transition-transform ${
              isExpanded ? 'rotate-180' : ''
            }`}
          />
        </div>
      </div>

      <p className="text-sm text-muted-foreground mb-4">{trait.description}</p>

      {/* Progress bar */}
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-purple-500 to-purple-400"
          initial={{ width: 0 }}
          animate={isInView ? { width: `${trait.score}%` } : { width: 0 }}
          transition={{ duration: 1, delay: 0.5 }}
        />
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-4 pt-4 border-t border-border/50"
          >
            <h4 className="text-sm font-medium text-purple-400 mb-2">Supporting Evidence</h4>
            <ul className="space-y-2">
              {trait.evidence.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <Shield className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

function IdentityCard({ identity, index }: { identity: KnownIdentity; index: number }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  const statusColors = {
    verified: 'bg-emerald-900/30 border-emerald-800',
    high: 'bg-blue-900/30 border-blue-800',
    medium: 'bg-amber-900/30 border-amber-800',
    unknown: 'bg-purple-900/30 border-purple-800',
  }

  return (
    <motion.div
      ref={ref}
      className={`p-5 rounded-xl border ${statusColors[identity.status]} hover-lift`}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-bold font-mono">{identity.alias}</h3>
        <VerificationBadge level={identity.status} size="sm" />
      </div>

      <div className="space-y-2 text-sm">
        <div>
          <span className="text-muted-foreground">Platform: </span>
          <span className="text-foreground">{identity.platform}</span>
        </div>
        <div>
          <span className="text-muted-foreground">Active: </span>
          <span className="text-foreground font-mono">{identity.timespan}</span>
        </div>
      </div>

      <p className="mt-3 text-sm text-muted-foreground">{identity.description}</p>
    </motion.div>
  )
}

function QuoteCard({ quote, index }: { quote: KeyQuote; index: number }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  return (
    <motion.div
      ref={ref}
      className="p-6 rounded-xl border bg-gradient-to-br from-zinc-900 to-zinc-950 border-zinc-800 hover-lift"
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
    >
      <Quote className="h-8 w-8 text-primary/30 mb-4" />
      <blockquote className="text-xl font-medium mb-4 leading-relaxed">
        "{quote.text}"
      </blockquote>
      <div className="flex items-center justify-between text-sm">
        <div>
          <div className="font-medium text-foreground">{quote.source}</div>
          <div className="text-muted-foreground">{quote.date}</div>
        </div>
      </div>
      <div className="mt-4 p-3 rounded-lg bg-primary/5 border border-primary/20">
        <div className="text-xs font-medium text-primary mb-1">Significance</div>
        <p className="text-sm text-muted-foreground">{quote.significance}</p>
      </div>
    </motion.div>
  )
}
