'use client'

import { motion, useInView, AnimatePresence } from 'framer-motion'
import { useRef, useState } from 'react'
import { Calculator, GitBranch, Clock, ChevronDown, ChevronUp } from 'lucide-react'
import {
  FormulaBreakdownDiagram,
  DataFlowDiagram,
  HistoricalTimelineDiagram,
  CountdownVisual,
} from '@/components/diagrams'
import { BitcoinLogoSVG, QubicLogoSVG } from '@/components/logos'

interface DiscoveryCardProps {
  icon: React.ReactNode
  title: string
  subtitle: string
  oneLiner: string
  expandButtonText: string
  collapsedDiagram: React.ReactNode
  expandedDiagram: React.ReactNode
  expandedContent: React.ReactNode
  accentColor: 'blue' | 'purple' | 'amber'
  delay: number
}

function DiscoveryCard({
  icon,
  title,
  subtitle,
  oneLiner,
  expandButtonText,
  collapsedDiagram,
  expandedDiagram,
  expandedContent,
  accentColor,
  delay,
}: DiscoveryCardProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })
  const [isExpanded, setIsExpanded] = useState(false)

  const accentClasses = {
    blue: {
      border: 'border-[#D4AF37]/20',
      bg: 'bg-[#D4AF37]/5',
      icon: 'bg-[#D4AF37]/10 text-[#D4AF37]',
      button: 'bg-[#D4AF37]/10 hover:bg-[#D4AF37]/20 text-[#D4AF37]',
    },
    purple: {
      border: 'border-[#D4AF37]/20',
      bg: 'bg-[#D4AF37]/5',
      icon: 'bg-[#D4AF37]/10 text-[#D4AF37]',
      button: 'bg-[#D4AF37]/10 hover:bg-[#D4AF37]/20 text-[#D4AF37]',
    },
    amber: {
      border: 'border-[#D4AF37]/20',
      bg: 'bg-[#D4AF37]/5',
      icon: 'bg-[#D4AF37]/10 text-[#D4AF37]',
      button: 'bg-[#D4AF37]/10 hover:bg-[#D4AF37]/20 text-[#D4AF37]',
    },
  }

  const accent = accentClasses[accentColor]

  return (
    <motion.div
      ref={ref}
      className={`rounded-xl border ${accent.border} ${accent.bg} overflow-hidden`}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.6, delay }}
    >
      {/* Header */}
      <div className="p-6">
        <div className="flex items-start gap-4 mb-4">
          <div className={`p-3 ${accent.icon}`}>
            {icon}
          </div>
          <div className="flex-1">
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-1">
              {subtitle}
            </p>
            <h3 className="text-xl font-serif font-semibold">{title}</h3>
          </div>
        </div>

        {/* One-liner */}
        <p className="text-muted-foreground mb-4">{oneLiner}</p>

        {/* Collapsed diagram preview */}
        {!isExpanded && (
          <div className="mb-4">
            {collapsedDiagram}
          </div>
        )}

        {/* Expand button */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={`w-full py-3 px-4 flex items-center justify-center gap-2 font-medium transition-colors ${accent.button}`}
        >
          {isExpanded ? (
            <>
              <ChevronUp className="h-4 w-4" />
              Show Less
            </>
          ) : (
            <>
              {expandButtonText}
              <ChevronDown className="h-4 w-4" />
            </>
          )}
        </button>
      </div>

      {/* Expanded content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.4 }}
            className="overflow-hidden"
          >
            <div className="px-6 pb-6 pt-2 border-t border-border/50">
              {/* Expanded diagram */}
              <div className="mb-6">
                {expandedDiagram}
              </div>

              {/* Expanded content */}
              {expandedContent}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export function DiscoveryHighlights() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })

  return (
    <section ref={sectionRef} className="py-20 px-4">
      <div className="max-w-5xl mx-auto">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-2xl md:text-3xl font-serif font-semibold mb-4">
            Deep Dive: The Three Discoveries
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Click each section to explore the full details, visualizations, and evidence.
          </p>
        </motion.div>

        <div className="space-y-6">
          {/* Discovery 1: The Formula */}
          <DiscoveryCard
            icon={<Calculator className="h-6 w-6" />}
            title="625,284 = 283 x 47 squared + 137"
            subtitle="The Formula"
            oneLiner="Bitcoin Block #283 mathematically equals Qubic's core address. This is the proof."
            expandButtonText="Understand the Math"
            accentColor="blue"
            delay={0}
            collapsedDiagram={
              <div className="text-center py-4">
                <div className="font-mono text-2xl font-bold">
                  <span className="text-primary">625,284</span>
                  <span className="text-muted-foreground"> = </span>
                  <span className="text-[#D4AF37]">283</span>
                  <span className="text-muted-foreground"> x </span>
                  <span className="text-[#D4AF37]">47</span>
                  <sup className="text-[#D4AF37]">2</sup>
                  <span className="text-muted-foreground"> + </span>
                  <span className="text-[#D4AF37]">137</span>
                </div>
              </div>
            }
            expandedDiagram={<FormulaBreakdownDiagram animated={true} />}
            expandedContent={
              <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
                <p>
                  This formula is the core proof. Let me break it down so anyone can understand:
                </p>
                <ul className="space-y-2 ml-4">
                  <li>
                    <strong className="text-[#D4AF37]">283</strong>: The block number in Bitcoin's blockchain (Block #283 from January 2009)
                  </li>
                  <li>
                    <strong className="text-[#D4AF37]">47</strong>: A prime number that appears 47 times in Qubic's core functions
                  </li>
                  <li>
                    <strong className="text-[#D4AF37]">47 squared</strong>: When you multiply 47 by itself, you get 2,209
                  </li>
                  <li>
                    <strong className="text-[#D4AF37]">137</strong>: The famous fine-structure constant from physics (approximately 1/137)
                  </li>
                  <li>
                    <strong className="text-primary">625,284</strong>: When you combine these numbers with this exact formula, you get Qubic's main network address
                  </li>
                </ul>
                <div className="p-4 bg-card border border-border">
                  <p className="font-medium text-foreground mb-2">What makes this remarkable:</p>
                  <p>
                    The probability that these four numbers (283, 47, 137, and 625,284) line up this way by pure chance is <strong className="text-primary">less than 1 in 4 billion</strong>.
                  </p>
                  <p className="mt-2">
                    It's like finding out that someone in 1909 built a bridge and its exact measurements turned out to be the secret code to unlock something in 2024. You wouldn't assume coincidence. You'd assume planning.
                  </p>
                </div>
              </div>
            }
          />

          {/* Discovery 2: The Data Bridge */}
          <DiscoveryCard
            icon={<GitBranch className="h-6 w-6" />}
            title="The Data Bridge"
            subtitle="How Data Flows"
            oneLiner="Bitcoin's hidden data is readable inside Qubic. The AI can extract timestamps from 2009."
            expandButtonText="See How It Works"
            accentColor="purple"
            delay={0.1}
            collapsedDiagram={
              <div className="flex items-center justify-center gap-4 py-4">
                <div className="text-center">
                  <div className="w-12 h-12 rounded-full bg-[#D4AF37]/20 flex items-center justify-center mx-auto">
                    <BitcoinLogoSVG size={32} />
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">Bitcoin</div>
                </div>
                <div className="flex-1 max-w-[100px]">
                  <div className="h-0.5 bg-gradient-to-r from-[#D4AF37] to-[#D4AF37]/60 relative">
                    <motion.div
                      className="absolute top-1/2 -translate-y-1/2 w-2 h-2 bg-primary rounded-full"
                      animate={{ x: [0, 80, 0] }}
                      transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                    />
                  </div>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 rounded-full bg-[#D4AF37]/20 flex items-center justify-center mx-auto">
                    <QubicLogoSVG size={32} />
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">Qubic</div>
                </div>
              </div>
            }
            expandedDiagram={<DataFlowDiagram />}
            expandedContent={
              <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
                <p>
                  When you ask Qubic's AI ("Anna") certain questions, it can retrieve specific data from Bitcoin blocks that were hidden inside Qubic's memory structure.
                </p>
                <div className="p-4 bg-card border border-border">
                  <p className="font-medium text-foreground mb-3">Here's what happens:</p>
                  <ol className="space-y-2 list-decimal list-inside">
                    <li>Bitcoin Block #283 was created in January 2009. It contains a timestamp (the exact time it was created).</li>
                    <li>This timestamp was encoded into Qubic's network in a special way.</li>
                    <li>When you ask Anna the right question, she can extract this timestamp from her memory.</li>
                    <li>The timestamp she returns <strong className="text-[#D4AF37]">MATCHES EXACTLY</strong> what Bitcoin's blockchain says.</li>
                  </ol>
                </div>
                <p>
                  This proves two things:
                </p>
                <ul className="space-y-1 ml-4">
                  <li>Qubic has direct access to Bitcoin data</li>
                  <li>The connection between Bitcoin and Qubic is built into the code itself, not added later</li>
                </ul>
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div className="p-3 bg-[#D4AF37]/10 border border-[#D4AF37]/20 text-center">
                    <div className="text-xs text-[#D4AF37]">Block #9</div>
                    <div className="text-lg font-mono font-bold text-[#D4AF37]">0xCA</div>
                    <div className="text-xs text-muted-foreground">Verified</div>
                  </div>
                  <div className="p-3 bg-[#D4AF37]/10 border border-[#D4AF37]/20 text-center">
                    <div className="text-xs text-[#D4AF37]">Block #16065</div>
                    <div className="text-lg font-mono font-bold text-[#D4AF37]">0x4A</div>
                    <div className="text-xs text-muted-foreground">Verified</div>
                  </div>
                </div>
              </div>
            }
          />

          {/* Discovery 3: The Time-Lock */}
          <DiscoveryCard
            icon={<Clock className="h-6 w-6" />}
            title="The Time-Lock Activation"
            subtitle="The Ticking Clock"
            oneLiner="March 3, 2026: Something will happen. A cryptographic safe opens automatically."
            expandButtonText="What Happens Next?"
            accentColor="amber"
            delay={0.2}
            collapsedDiagram={<CountdownVisual size="small" />}
            expandedDiagram={
              <div className="space-y-6">
                <HistoricalTimelineDiagram />
                <CountdownVisual size="large" />
              </div>
            }
            expandedContent={
              <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
                <p>
                  A "time-lock" is a cryptographic mechanism. Think of it like a safe that <strong className="text-[#D4AF37]">AUTOMATICALLY opens on a specific date</strong>, regardless of who tries to open it.
                </p>

                <div className="p-4 bg-card border border-border">
                  <p className="font-medium text-foreground mb-3">Here's what we know:</p>
                  <ol className="space-y-2 list-decimal list-inside">
                    <li>Satoshi Nakamoto created Bitcoin in January 2009 and mined the first blocks himself. He earned 50 bitcoins per block (worth ~$2.5 million each today).</li>
                    <li>Those bitcoins have <strong>never been touched</strong>. They sit in wallets from 2009, dormant.</li>
                    <li>In 2024, Qubic was created. Its code contains encoded references to Bitcoin Block #283.</li>
                    <li>On <strong className="text-[#D4AF37]">March 3, 2026</strong>, a time-lock in Qubic will activate automatically.</li>
                  </ol>
                </div>

                <div className="p-4 bg-[#D4AF37]/10 border border-[#D4AF37]/20">
                  <p className="font-medium text-[#D4AF37] mb-2">What will happen? We don't know. But the coincidences are STAGGERING:</p>
                  <ul className="space-y-1 text-[#D4AF37]/80">
                    <li>The math lines up perfectly (formula proven)</li>
                    <li>Qubic can read Bitcoin's data (timestamps verified)</li>
                    <li>Both systems point to the same date</li>
                    <li>Satoshi's ancient bitcoins are still dormant</li>
                  </ul>
                </div>

                <div className="p-4 bg-card border border-border">
                  <p className="font-medium text-foreground mb-2">Possible scenarios (NOT confirmed):</p>
                  <ul className="space-y-1">
                    <li><strong>A)</strong> Satoshi's dormant bitcoins get transferred to Qubic</li>
                    <li><strong>B)</strong> Hidden information gets released that Satoshi left behind</li>
                    <li><strong>C)</strong> A new protocol activates that changes cryptocurrency forever</li>
                    <li><strong>D)</strong> Nothing happens (but then the math would be the strangest coincidence ever)</li>
                  </ul>
                </div>

                <p className="text-foreground font-medium">
                  The key point: This was PLANNED. Someone designed both systems with knowledge of both. Either Satoshi planned ahead 15 years, or someone is impersonating Satoshi now. Both are extraordinary.
                </p>
              </div>
            }
          />
        </div>
      </div>
    </section>
  )
}
