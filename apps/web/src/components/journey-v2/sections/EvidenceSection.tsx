'use client'

import { useRef, useState, useEffect, useCallback } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { JourneySection } from '../JourneySection'
import { FileSearch, ChevronDown, ChevronRight, Shield, ExternalLink, HelpCircle, CheckCircle, AlertCircle } from 'lucide-react'
import Link from 'next/link'
import { useGamificationSafe } from '@/components/gamification/GamificationProvider'

// Simplified tier structure for the journey
const EVIDENCE_TIERS = [
  {
    tier: 1,
    name: 'Cryptographically Verified',
    confidence: '99%+',
    count: 5,
    color: 'text-[#D4AF37]',
    bgColor: 'bg-[#D4AF37]/10',
    borderColor: 'border-green-500/20',
    description: 'Directly verifiable on the blockchain — anyone can check these',
    items: [
      '1CFB Bitcoin address active since January 2009',
      'Genesis block contains exactly 43 leading zero bits',
      'Block #283 exists and was mined by Patoshi',
      '21,953 blocks match the Patoshi pattern',
      'Qubic time-lock mechanism encoded in protocol',
    ],
  },
  {
    tier: 2,
    name: 'Mathematical Proofs',
    confidence: '95%+',
    count: 8,
    color: 'text-[#D4AF37]',
    bgColor: 'bg-[#D4AF37]/10',
    borderColor: 'border-[#D4AF37]/20',
    description: 'Mathematical relationships that can be calculated and verified',
    items: [
      'Formula: 625,284 = 283 × 47² + 137',
      '128 × 128 = 16,384 matrix cells',
      '283 and 47 are both prime numbers',
      '137 ≈ 1/α (fine structure constant)',
    ],
  },
  {
    tier: 3,
    name: 'Pattern Analysis',
    confidence: '90%+',
    count: 12,
    color: 'text-[#D4AF37]',
    bgColor: 'bg-[#D4AF37]/10',
    borderColor: 'border-[#D4AF37]/20',
    description: 'Patterns discovered through forensic blockchain analysis',
    items: [
      'ZgZ palindrome in CFB address',
      'PTZ location encoding (Petrozavodsk?)',
      'Anna Oracle timestamp matches',
      'Address network clustering patterns',
    ],
  },
  {
    tier: 4,
    name: 'Research Hypotheses',
    confidence: '70%+',
    count: 21,
    color: 'text-[#D4AF37]',
    bgColor: 'bg-[#D4AF37]/10',
    borderColor: 'border-orange-500/20',
    description: 'Speculative connections requiring further investigation',
    items: [
      'March 3, 2026 convergence date',
      'Isaiah 30:26 scripture encoding',
      'Lunar eclipse alignment significance',
      'Satoshi-CFB identity connection',
    ],
  },
]

interface TierCardProps {
  tier: typeof EVIDENCE_TIERS[0]
  index: number
  isExpanded: boolean
  onToggle: () => void
  onTierView: (tierNum: number) => void
  isInView: boolean
}

function TierCard({ tier, index, isExpanded, onToggle, onTierView, isInView }: TierCardProps) {
  // Track when tier is first expanded
  useEffect(() => {
    if (isExpanded) {
      onTierView(tier.tier)
    }
  }, [isExpanded, tier.tier, onTierView])

  return (
    <motion.div
      className={`rounded-xl ${tier.bgColor} border ${tier.borderColor} overflow-hidden`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
      transition={{ duration: 0.5, delay: 0.4 + index * 0.1 }}
      whileHover={{ scale: 1.01 }}
    >
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between text-left group"
        aria-expanded={isExpanded}
        aria-controls={`tier-${tier.tier}-content`}
      >
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 bg-black/30 flex items-center justify-center`}>
            {tier.tier <= 2 ? (
              <CheckCircle className={`h-5 w-5 ${tier.color}`} />
            ) : (
              <AlertCircle className={`h-5 w-5 ${tier.color}`} />
            )}
          </div>
          <div>
            <h3 className="font-semibold text-white/80 group-hover:text-white/90 transition-colors">
              {tier.name}
            </h3>
            <div className="flex items-center gap-2 text-xs">
              <span className={tier.color}>{tier.confidence} confidence</span>
              <span className="text-white/50">•</span>
              <span className="text-white/40">{tier.count} findings</span>
            </div>
          </div>
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="text-white/40 group-hover:text-white/60 transition-colors"
        >
          <ChevronDown className="h-5 w-5" />
        </motion.div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            id={`tier-${tier.tier}-content`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4">
              {/* Tier explanation for beginners */}
              <p className="text-xs text-white/40 mb-3 pl-2 border-l-2 border-white/10">
                {tier.description}
              </p>

              <div className="space-y-2">
                {tier.items.map((item, i) => (
                  <motion.div
                    key={i}
                    className="flex items-start gap-2 p-2 bg-black/20"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                  >
                    <ChevronRight className={`h-4 w-4 mt-0.5 ${tier.color} shrink-0`} />
                    <span className="text-sm text-white/60">{item}</span>
                  </motion.div>
                ))}
              </div>

              {tier.count > tier.items.length && (
                <div className="pt-3 text-center">
                  <span className="text-xs text-white/50">
                    + {tier.count - tier.items.length} more findings in full database
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export function EvidenceSection() {
  const contentRef = useRef(null)
  const isInView = useInView(contentRef, { once: false, amount: 0.2 })
  const [expandedTier, setExpandedTier] = useState<number | null>(null)
  const [animatedCount, setAnimatedCount] = useState(0)
  const [hasTriggeredSectionView, setHasTriggeredSectionView] = useState(false)

  // Gamification
  const gamification = useGamificationSafe()

  const totalFindings = EVIDENCE_TIERS.reduce((acc, tier) => acc + tier.count, 0)

  // Trigger first-discovery when section comes into view
  useEffect(() => {
    if (isInView && !hasTriggeredSectionView && gamification) {
      gamification.viewDiscovery('evidence-overview')
      setHasTriggeredSectionView(true)
    }
  }, [isInView, hasTriggeredSectionView, gamification])

  // Handle tier view for gamification
  const handleTierView = useCallback((tierNum: number) => {
    if (gamification) {
      gamification.viewTier(tierNum)
      gamification.viewDiscovery(`evidence-tier-${tierNum}`)
    }
  }, [gamification])

  // Animate the count
  useEffect(() => {
    if (isInView) {
      let current = 0
      const increment = totalFindings / 30
      const timer = setInterval(() => {
        current += increment
        if (current >= totalFindings) {
          setAnimatedCount(totalFindings)
          clearInterval(timer)
        } else {
          setAnimatedCount(Math.floor(current))
        }
      }, 50)
      return () => clearInterval(timer)
    } else {
      setAnimatedCount(0)
    }
  }, [isInView, totalFindings])

  return (
    <JourneySection id="evidence" background="transparent" className="flex items-center justify-center py-12 md:py-20">
      <div ref={contentRef} className="relative z-10 w-full max-w-4xl mx-auto px-4">
        {/* Chapter Header */}
        <motion.div
          className="text-center mb-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0.9 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/50 text-xs font-mono">
              CHAPTER 8
            </span>
          </motion.div>

          <motion.div
            className="inline-flex items-center gap-2 mb-4"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0.9 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <FileSearch className="h-8 w-8 text-white/60" />
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-bold text-white/90 mb-4">
            <span className="text-white/80">{animatedCount}</span> Discoveries
          </h2>

          {/* Story context for beginners */}
          <motion.div
            className="max-w-2xl mx-auto space-y-4 mb-8"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <p className="text-lg text-white/50 leading-relaxed">
              We've catalogued <span className="text-white/70 font-medium">{totalFindings} separate findings</span>,
              organized by how confident we are in each one.
            </p>
            <p className="text-base text-white/40 leading-relaxed">
              From <span className="text-white/60">cryptographically verifiable facts</span> to
              more <span className="text-white/60">speculative hypotheses</span> — all documented
              with sources.
            </p>
          </motion.div>

          {/* What is confidence - Quick explainer */}
          <motion.div
            className="inline-flex items-start gap-3 px-4 py-3 bg-white/5 border border-white/10 text-left max-w-lg mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: isInView ? 1 : 0 }}
            transition={{ delay: 0.5 }}
          >
            <HelpCircle className="h-5 w-5 text-white/40 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-white/60 font-medium mb-1">How to Read This</p>
              <p className="text-xs text-white/40 leading-relaxed">
                Tier 1-2 findings can be independently verified by anyone. Tier 3-4 are patterns
                and hypotheses that require more interpretation. We show our work for everything.
              </p>
            </div>
          </motion.div>
        </motion.div>

        {/* Stats Banner */}
        <motion.div
          className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          role="group"
          aria-label="Evidence tier statistics"
        >
          {EVIDENCE_TIERS.map((tier) => (
            <motion.button
              key={tier.tier}
              className={`p-3 ${tier.bgColor} border ${tier.borderColor} text-center cursor-pointer`}
              onClick={() => setExpandedTier(expandedTier === tier.tier ? null : tier.tier)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
              aria-label={`Tier ${tier.tier}: ${tier.count} findings, ${tier.confidence} confidence`}
            >
              <div className={`text-xl md:text-2xl font-mono font-bold ${tier.color}`}>
                {tier.count}
              </div>
              <div className="text-[10px] md:text-xs text-white/50 truncate">
                Tier {tier.tier}
              </div>
            </motion.button>
          ))}
        </motion.div>

        {/* Tier Cards */}
        <div className="space-y-3 mb-8" role="list" aria-label="Evidence tiers">
          {EVIDENCE_TIERS.map((tier, index) => (
            <TierCard
              key={tier.tier}
              tier={tier}
              index={index}
              isExpanded={expandedTier === tier.tier}
              onToggle={() => setExpandedTier(expandedTier === tier.tier ? null : tier.tier)}
              onTierView={handleTierView}
              isInView={isInView}
            />
          ))}
        </div>

        {/* Verification Notice */}
        <motion.div
          className="p-5 bg-white/5 border border-white/10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ delay: 0.8 }}
        >
          <div className="flex items-start gap-4">
            <Shield className="h-8 w-8 text-[#D4AF37] shrink-0" />
            <div className="flex-1">
              <h4 className="font-medium text-white/80 mb-1">Our Verification Standards</h4>
              <p className="text-sm text-white/50 mb-3">
                We don't ask you to trust us. Every finding includes source references,
                mathematical proofs, or on-chain verification steps that you can check yourself.
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1  bg-[#D4AF37]/10 text-xs text-[#D4AF37]/80">
                  Open Source
                </span>
                <span className="px-2 py-1  bg-[#D4AF37]/10 text-xs text-[#D4AF37]/80">
                  Reproducible
                </span>
                <span className="px-2 py-1  bg-[#D4AF37]/10 text-xs text-[#D4AF37]/80">
                  Peer-Reviewable
                </span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* View All Link */}
        <motion.div
          className="mt-8 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 1 }}
        >
          <Link
            href="/evidence"
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#D4AF37]/10 hover:bg-[#D4AF37]/20 transition-all text-[#D4AF37] font-medium group"
          >
            <FileSearch className="h-4 w-4" />
            Explore All {totalFindings} Findings
            <ExternalLink className="h-4 w-4 opacity-50 group-hover:opacity-100 transition-opacity" />
          </Link>
          <p className="text-xs text-white/50 mt-2">
            Complete database with methodology and sources
          </p>
        </motion.div>

        {/* Transition hint */}
        <motion.div
          className="mt-10 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 1.2 }}
        >
          <p className="text-sm text-white/50 italic">
            "Now what? Where do we go from here?"
          </p>
        </motion.div>
      </div>
    </JourneySection>
  )
}
