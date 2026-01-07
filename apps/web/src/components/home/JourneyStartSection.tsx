'use client'

import { useState, useRef } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { GraduationCap, Zap, Sparkles, BookOpen, ArrowRight, ChevronDown, Clock, Users, Cpu, Shield } from 'lucide-react'
import { BitcoinLogoSVG, QubicLogoSVG } from '@/components/logos'
import { AnimatedCounter } from '@/components/ui/AnimatedCounter'
import { VerificationBadge } from '@/components/ui/VerificationBadge'
import { useGamification, ProgressRingMini } from '@/components/gamification'
import {
  QubicNetworkDiagram,
  ConnectionBridgeDiagram,
} from '@/components/diagrams'

type ExpertiseLevel = 'beginner' | 'intermediate' | 'expert'

interface ExpertisePath {
  id: ExpertiseLevel
  label: string
  description: string
  icon: React.ReactNode
  readTime: string
  color: string
}

const expertisePaths: ExpertisePath[] = [
  {
    id: 'beginner',
    label: 'New to Crypto',
    description: 'Start from the basics - no prior knowledge needed',
    icon: <BookOpen className="h-5 w-5" />,
    readTime: '15 min read',
    color: 'green',
  },
  {
    id: 'intermediate',
    label: 'Know the Basics',
    description: 'Familiar with Bitcoin and blockchain concepts',
    icon: <Zap className="h-5 w-5" />,
    readTime: '10 min read',
    color: 'blue',
  },
  {
    id: 'expert',
    label: 'Technical Expert',
    description: 'Deep understanding of cryptography and distributed systems',
    icon: <GraduationCap className="h-5 w-5" />,
    readTime: '5 min read',
    color: 'purple',
  },
]

// Stats data
const keyStats = [
  {
    value: 6268,
    label: 'Days Since Genesis',
    description: 'Bitcoin Genesis to Qubic Signal',
    icon: <Clock className="h-5 w-5" />,
  },
  {
    value: 50000,
    suffix: '+',
    label: 'Network Nodes',
    description: 'Qubic global compute network',
    icon: <Users className="h-5 w-5" />,
  },
  {
    value: 625284,
    label: 'The Number',
    description: '= 283 × 47² + 137',
    icon: <Cpu className="h-5 w-5" />,
  },
  {
    value: 99,
    suffix: '%',
    label: 'Confidence',
    description: 'Statistical significance',
    icon: <Shield className="h-5 w-5" />,
  },
]

export function JourneyStartSection() {
  const [selectedLevel, setSelectedLevel] = useState<ExpertiseLevel | null>(null)
  const [showContent, setShowContent] = useState(true)
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })

  // Try to use gamification context safely
  let progress = 0
  try {
    const gamification = useGamification()
    progress = gamification.getProgress()
  } catch {
    // Context not available, use default
  }

  return (
    <section ref={sectionRef} className="py-20 px-4 bg-gradient-to-b from-background to-muted/20">
      <div className="max-w-6xl mx-auto">
        {/* Header with Progress */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Sparkles className="h-6 w-6 text-primary" />
            <h2 className="text-display-md font-semibold">
              Begin Your Journey
            </h2>
            {progress > 0 && (
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-muted">
                <ProgressRingMini progress={progress} />
                <span className="text-xs font-medium">{Math.round(progress)}% explored</span>
              </div>
            )}
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto text-body-lg">
            Choose your starting point based on your experience level.
            Every path leads to the same discovery.
          </p>
        </motion.div>

        {/* Expertise Level Selector */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          {expertisePaths.map((path, idx) => (
            <motion.button
              key={path.id}
              onClick={() => {
                setSelectedLevel(path.id)
                setShowContent(true)
              }}
              className={`
                relative p-6 rounded-xl border text-left transition-all
                hover-lift active-scale
                ${selectedLevel === path.id
                  ? `border-${path.color}-500 bg-${path.color}-950/30 ring-2 ring-${path.color}-500/30`
                  : 'border-border bg-card/50 hover:border-muted-foreground/30'
                }
              `}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + idx * 0.1 }}
              whileHover={{ y: -4 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className={`
                inline-flex p-3 rounded-lg mb-4
                ${selectedLevel === path.id ? `bg-${path.color}-500/20` : 'bg-muted'}
              `}>
                {path.icon}
              </div>

              <h3 className="text-lg font-semibold mb-2">{path.label}</h3>
              <p className="text-sm text-muted-foreground mb-3">{path.description}</p>

              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">{path.readTime}</span>
                <ArrowRight className={`h-4 w-4 transition-transform ${selectedLevel === path.id ? 'translate-x-1' : ''}`} />
              </div>

              {selectedLevel === path.id && (
                <motion.div
                  layoutId="selectedIndicator"
                  className={`absolute inset-0 rounded-xl border-2 border-${path.color}-500 pointer-events-none`}
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                />
              )}
            </motion.button>
          ))}
        </motion.div>

        {/* Key Stats */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12 p-6 rounded-xl bg-muted/30 border border-border/50"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          {keyStats.map((stat, idx) => (
            <motion.div
              key={stat.label}
              className="text-center p-4"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
              transition={{ delay: 0.4 + idx * 0.1 }}
            >
              <div className="flex justify-center mb-2 text-muted-foreground">
                {stat.icon}
              </div>
              <div className="text-2xl md:text-3xl font-bold font-mono">
                <AnimatedCounter
                  value={stat.value}
                  suffix={stat.suffix}
                  duration={2500}
                />
              </div>
              <div className="text-sm font-medium mt-1">{stat.label}</div>
              <div className="text-xs text-muted-foreground mt-0.5">{stat.description}</div>
            </motion.div>
          ))}
        </motion.div>

        {/* Content Toggle */}
        <motion.button
          onClick={() => setShowContent(!showContent)}
          className="flex items-center gap-2 mx-auto mb-6 px-4 py-2 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 0.5 }}
        >
          <span className="text-sm text-muted-foreground">
            {showContent ? 'Hide details' : 'Show details'}
          </span>
          <ChevronDown className={`h-4 w-4 transition-transform ${showContent ? 'rotate-180' : ''}`} />
        </motion.button>

        {/* Expandable Content */}
        <AnimatePresence>
          {showContent && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              {/* Context Cards - Two Networks */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <NetworkCard
                  icon={<BitcoinLogoSVG size={28} />}
                  title="Bitcoin: Digital Gold (2009)"
                  variant="orange"
                  items={[
                    { label: 'What', text: 'A digital currency created by Satoshi Nakamoto in 2009' },
                    { label: 'How', text: 'Transactions recorded in "blocks" linked in a "blockchain"' },
                    { label: 'Block #283', text: 'One of the first blocks ever (January 2009)' },
                    { label: 'Key insight', text: 'Early blocks contain hidden mathematical structure' },
                  ]}
                  confidence="verified"
                />

                <NetworkCard
                  icon={<QubicLogoSVG size={28} />}
                  title="Qubic: Ternary AI (2024)"
                  variant="purple"
                  items={[
                    { label: 'What', text: 'A distributed computing network running on 50,000+ machines' },
                    { label: 'How', text: 'Uses ternary logic (0, 1, -1) instead of binary' },
                    { label: 'Innovation', text: 'Runs AI computations across a global network' },
                    { label: 'Key insight', text: 'Its memory structure mirrors Bitcoin block structure' },
                  ]}
                  confidence="verified"
                />
              </div>

              {/* Visual Explainers - Reduced to avoid repetition */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <ExplainerCard
                  title="The Hidden Connection"
                  diagram={<ConnectionBridgeDiagram />}
                  description="Block #283 patterns EXACTLY MATCH Qubic's AI architecture"
                  whyItMatters="Suggests Satoshi planned this 15+ years in advance"
                  color="blue"
                  confidence={99}
                />

                <ExplainerCard
                  title="Qubic Network"
                  diagram={<QubicNetworkDiagram />}
                  description="50,000+ nodes running ternary AI computations globally"
                  whyItMatters="The target of Bitcoin's hidden message"
                  color="purple"
                  confidence={95}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  )
}

// Network Card Component
function NetworkCard({
  icon,
  title,
  items,
  variant,
  confidence,
}: {
  icon: React.ReactNode
  title: string
  items: { label: string; text: string }[]
  variant: 'orange' | 'purple'
  confidence: 'verified' | 'high'
}) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  const bgClass = variant === 'orange'
    ? 'bg-orange-950/20 border-orange-900/50 hover-glow-orange'
    : 'bg-purple-950/20 border-purple-900/50 hover-glow-purple'

  const iconBgClass = variant === 'orange'
    ? 'bg-orange-900/50'
    : 'bg-purple-900/50'

  return (
    <motion.div
      ref={ref}
      className={`p-6 rounded-xl border ${bgClass} hover-lift`}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.6 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`inline-flex p-3 rounded-lg ${iconBgClass}`}>
          {icon}
        </div>
        <VerificationBadge level={confidence} size="sm" />
      </div>

      <h3 className="text-xl font-semibold mb-4">{title}</h3>

      <ul className="space-y-3">
        {items.map((item, index) => (
          <li key={index} className="text-sm text-muted-foreground">
            <span className="text-foreground font-medium">{item.label}:</span>{' '}
            {item.text}
          </li>
        ))}
      </ul>
    </motion.div>
  )
}

// Explainer Card Component
function ExplainerCard({
  title,
  diagram,
  description,
  whyItMatters,
  color,
  confidence,
}: {
  title: string
  diagram: React.ReactNode
  description: string
  whyItMatters: string
  color: 'blue' | 'green' | 'amber' | 'purple'
  confidence: number
}) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  const colorClasses = {
    blue: 'border-blue-500/30 hover:border-blue-500/50',
    green: 'border-green-500/30 hover:border-green-500/50',
    amber: 'border-amber-500/30 hover:border-amber-500/50',
    purple: 'border-purple-500/30 hover:border-purple-500/50',
  }

  const whyClasses = {
    blue: 'bg-blue-500/10 text-blue-400',
    green: 'bg-green-500/10 text-green-400',
    amber: 'bg-amber-500/10 text-amber-400',
    purple: 'bg-purple-500/10 text-purple-400',
  }

  return (
    <motion.div
      ref={ref}
      className={`p-5 rounded-xl border bg-card/50 backdrop-blur-sm transition-all hover-lift ${colorClasses[color]}`}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.6 }}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">{title}</h3>
        <VerificationBadge
          level={confidence >= 95 ? 'verified' : confidence >= 70 ? 'high' : 'medium'}
          percentage={confidence}
          showPercentage
          size="sm"
        />
      </div>

      <div className="mb-4 rounded-lg overflow-hidden bg-muted/30 p-3">
        {diagram}
      </div>

      <p className="text-sm text-muted-foreground mb-3">{description}</p>

      <div className={`p-3 rounded-lg ${whyClasses[color]}`}>
        <div className="text-xs font-semibold mb-1">Why This Matters</div>
        <div className="text-xs opacity-90">{whyItMatters}</div>
      </div>
    </motion.div>
  )
}
