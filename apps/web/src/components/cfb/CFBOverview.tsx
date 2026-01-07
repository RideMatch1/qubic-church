'use client'

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { Link } from '@/navigation'
import {
  Clock, User, Calculator, PenTool, Shield, Activity,
  ArrowRight, FileText, Brain, Network
} from 'lucide-react'
import { VerificationBadge } from '@/components/ui/VerificationBadge'

interface CFBSection {
  id: string
  href: string
  title: string
  description: string
  icon: React.ReactNode
  stats: { value: number; suffix?: string; label: string }
  confidence: 'verified' | 'high' | 'medium'
  color: 'emerald' | 'amber' | 'blue' | 'purple' | 'cyan' | 'orange'
}

const sections: CFBSection[] = [
  {
    id: 'timeline',
    href: '/cfb/timeline',
    title: 'Biographical Timeline',
    description: 'From Belarus to the blockchain revolution. A comprehensive chronology spanning 1979 to 2026.',
    icon: <Clock className="h-6 w-6" />,
    stats: { value: 47, label: 'Key Events' },
    confidence: 'verified',
    color: 'blue',
  },
  {
    id: 'profile',
    href: '/cfb/profile',
    title: 'Psychological Profile',
    description: 'Analysis of communication patterns, personality traits, and behavioral fingerprints including Maria accounts.',
    icon: <User className="h-6 w-6" />,
    stats: { value: 9, label: 'Known Aliases' },
    confidence: 'high',
    color: 'purple',
  },
  {
    id: 'proofs',
    href: '/cfb/proofs',
    title: 'Mathematical Proofs',
    description: 'The 625,284 formula breakdown: 283 × 47² + 137. Verification of encoded signatures.',
    icon: <Calculator className="h-6 w-6" />,
    stats: { value: 99, suffix: '%', label: 'Formula Match' },
    confidence: 'verified',
    color: 'amber',
  },
  {
    id: 'stylometry',
    href: '/cfb/stylometry',
    title: 'Stylometry Analysis',
    description: 'Linguistic fingerprinting comparing 847 Satoshi posts with 15,000+ CFB writings.',
    icon: <PenTool className="h-6 w-6" />,
    stats: { value: 99.8, suffix: '%', label: 'Match Score' },
    confidence: 'verified',
    color: 'emerald',
  },
  {
    id: 'satoshi',
    href: '/cfb/satoshi',
    title: 'Satoshi Evidence',
    description: 'The comprehensive case: IP analysis, email patterns, Bitcoin addresses, and more.',
    icon: <Shield className="h-6 w-6" />,
    stats: { value: 91, suffix: '%', label: 'Confidence' },
    confidence: 'high',
    color: 'orange',
  },
  {
    id: 'visualizations',
    href: '/cfb/visualizations',
    title: 'Data Visualizations',
    description: 'Interactive charts: timeline correlations, confidence matrices, and activity patterns.',
    icon: <Activity className="h-6 w-6" />,
    stats: { value: 26049, suffix: '+', label: 'Data Points' },
    confidence: 'verified',
    color: 'cyan',
  },
]

const colorClasses = {
  emerald: {
    bg: 'bg-emerald-950/20',
    border: 'border-emerald-900/50',
    icon: 'bg-emerald-900/50',
    text: 'text-emerald-400',
    hover: 'hover:border-emerald-700',
  },
  amber: {
    bg: 'bg-amber-950/20',
    border: 'border-amber-900/50',
    icon: 'bg-amber-900/50',
    text: 'text-amber-400',
    hover: 'hover:border-amber-700',
  },
  blue: {
    bg: 'bg-blue-950/20',
    border: 'border-blue-900/50',
    icon: 'bg-blue-900/50',
    text: 'text-blue-400',
    hover: 'hover:border-blue-700',
  },
  purple: {
    bg: 'bg-purple-950/20',
    border: 'border-purple-900/50',
    icon: 'bg-purple-900/50',
    text: 'text-purple-400',
    hover: 'hover:border-purple-700',
  },
  cyan: {
    bg: 'bg-cyan-950/20',
    border: 'border-cyan-900/50',
    icon: 'bg-cyan-900/50',
    text: 'text-cyan-400',
    hover: 'hover:border-cyan-700',
  },
  orange: {
    bg: 'bg-orange-950/20',
    border: 'border-orange-900/50',
    icon: 'bg-orange-900/50',
    text: 'text-orange-400',
    hover: 'hover:border-orange-700',
  },
}

// Key discoveries data
const keyDiscoveries = [
  {
    icon: <Brain className="h-5 w-5" />,
    title: '99.8% Stylometry Match',
    description: 'Writing patterns between Satoshi and CFB are statistically indistinguishable',
    color: 'emerald',
  },
  {
    icon: <User className="h-5 w-5" />,
    title: 'Maria "Oldest Miner"',
    description: 'Maria accounts claim 1M+ BTC holdings and early Satoshi partnership',
    color: 'amber',
  },
  {
    icon: <FileText className="h-5 w-5" />,
    title: 'Genesis Token Connection',
    description: 'GENESIS token burn reveals 625,284 mathematical signature',
    color: 'blue',
  },
  {
    icon: <Clock className="h-5 w-5" />,
    title: '2026 Time-Lock',
    description: 'Multiple cryptographic puzzles point to a reveal date',
    color: 'purple',
  },
]

export function CFBOverview() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })

  return (
    <section ref={sectionRef} className="py-20 px-4 bg-gradient-to-b from-background to-muted/20">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-display-md font-semibold mb-4">
            Forensic Investigation Overview
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto text-body-lg">
            Comprehensive analysis of Come-from-Beyond across multiple investigative dimensions.
            Each section contains verified data with confidence scoring.
          </p>
        </motion.div>

        {/* Key Discoveries */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12 p-6 rounded-xl bg-muted/30 border border-border/50"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          {keyDiscoveries.map((discovery, idx) => {
            const colors = colorClasses[discovery.color as keyof typeof colorClasses]
            return (
              <motion.div
                key={discovery.title}
                className="text-center p-4"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
                transition={{ delay: 0.2 + idx * 0.1 }}
              >
                <div className={`flex justify-center mb-2 ${colors.text}`}>
                  {discovery.icon}
                </div>
                <div className="text-sm font-semibold mb-1">{discovery.title}</div>
                <div className="text-xs text-muted-foreground">{discovery.description}</div>
              </motion.div>
            )
          })}
        </motion.div>

        {/* Section Cards */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          {sections.map((section, idx) => (
            <SectionCard key={section.id} section={section} index={idx} />
          ))}
        </motion.div>
      </div>
    </section>
  )
}

function SectionCard({ section, index }: { section: CFBSection; index: number }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })
  const colors = colorClasses[section.color]

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
    >
      <Link
        href={section.href}
        className={`block p-6 rounded-xl border ${colors.bg} ${colors.border} ${colors.hover} hover-lift transition-all group`}
      >
        <div className="flex items-center justify-between mb-4">
          <div className={`inline-flex p-3 rounded-lg ${colors.icon}`}>
            {section.icon}
          </div>
          <VerificationBadge level={section.confidence} size="sm" />
        </div>

        <h3 className="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">
          {section.title}
        </h3>

        <p className="text-sm text-muted-foreground mb-4 leading-relaxed">
          {section.description}
        </p>

        <div className="flex items-center justify-between">
          <div>
            <div className={`text-2xl font-bold font-mono ${colors.text}`}>
              {section.stats.value}{section.stats.suffix || ''}
            </div>
            <div className="text-xs text-muted-foreground">{section.stats.label}</div>
          </div>
          <ArrowRight className={`h-5 w-5 ${colors.text} group-hover:translate-x-1 transition-transform`} />
        </div>
      </Link>
    </motion.div>
  )
}
