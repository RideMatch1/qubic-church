'use client'

import { useState, useRef } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import {
  Calculator, GitBranch, Clock, ChevronDown, ChevronUp, Binary, Calendar, Hash,
  ArrowRight, Sparkles, Zap, Target, Lock
} from 'lucide-react'
import { BitcoinLogoSVG, QubicLogoSVG } from '@/components/logos'
import { VerificationBadge } from '@/components/ui/VerificationBadge'
import { AnimatedCounter } from '@/components/ui/AnimatedCounter'
import {
  FormulaBreakdownDiagram,
  DataFlowDiagram,
  CountdownVisual,
} from '@/components/diagrams'

// Story steps for the bridge reveal
const storySteps = [
  {
    id: 'bitcoin',
    label: 'Bitcoin Genesis',
    icon: <BitcoinLogoSVG size={20} />,
  },
  {
    id: 'formula',
    label: 'The Formula',
    icon: <Calculator className="h-5 w-5" />,
  },
  {
    id: 'qubic',
    label: 'Qubic Network',
    icon: <QubicLogoSVG size={20} />,
  },
  {
    id: 'timelock',
    label: 'The Countdown',
    icon: <Clock className="h-5 w-5" />,
  },
]

export function TheBridgeRevealSection() {
  const [activeStep, setActiveStep] = useState(0)
  const [expandedDiscovery, setExpandedDiscovery] = useState<number | null>(null)
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })

  return (
    <section ref={sectionRef} className="py-20 px-4 bg-gradient-to-b from-muted/20 to-background">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Sparkles className="h-6 w-6 text-primary" />
            <h2 className="text-display-md font-semibold">The Bridge Revealed</h2>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto text-body-lg">
            Mathematical patterns linking the origins of Bitcoin and Qubic suggest
            intentional design rather than coincidence.
          </p>
        </motion.div>

        {/* Story Navigation */}
        <motion.div
          className="flex justify-center gap-2 mb-12 overflow-x-auto pb-2"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          {storySteps.map((step, idx) => (
            <button
              key={step.id}
              onClick={() => setActiveStep(idx)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-full transition-all whitespace-nowrap
                ${activeStep === idx
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted/50 hover:bg-muted text-muted-foreground hover:text-foreground'
                }
              `}
            >
              {step.icon}
              <span className="text-sm font-medium">{step.label}</span>
            </button>
          ))}
        </motion.div>

        {/* Step Content */}
        <AnimatePresence mode="wait">
          {activeStep === 0 && (
            <BitcoinGenesisStep key="bitcoin" isInView={isInView} />
          )}
          {activeStep === 1 && (
            <FormulaStep key="formula" isInView={isInView} />
          )}
          {activeStep === 2 && (
            <QubicNetworkStep key="qubic" isInView={isInView} />
          )}
          {activeStep === 3 && (
            <TimelockStep key="timelock" isInView={isInView} />
          )}
        </AnimatePresence>

        {/* Navigation Arrows */}
        <motion.div
          className="flex justify-center gap-4 mt-8"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 0.5 }}
        >
          <button
            onClick={() => setActiveStep(Math.max(0, activeStep - 1))}
            disabled={activeStep === 0}
            className="px-6 py-2 rounded-lg bg-muted hover:bg-muted/80 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
          >
            <ArrowRight className="h-4 w-4 rotate-180" />
            Previous
          </button>
          <button
            onClick={() => setActiveStep(Math.min(3, activeStep + 1))}
            disabled={activeStep === 3}
            className="px-6 py-2 rounded-lg bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
          >
            Next
            <ArrowRight className="h-4 w-4" />
          </button>
        </motion.div>

        {/* The Three Discoveries (Collapsible) */}
        <motion.div
          className="mt-16"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <h3 className="text-xl font-semibold text-center mb-8">Deep Dive: The Three Discoveries</h3>

          <div className="space-y-4">
            {/* Discovery 1: The Formula */}
            <DiscoveryAccordion
              index={0}
              expanded={expandedDiscovery === 0}
              onToggle={() => setExpandedDiscovery(expandedDiscovery === 0 ? null : 0)}
              icon={<Calculator className="h-5 w-5" />}
              title="625,284 = 283 × 47² + 137"
              subtitle="The Formula"
              confidence={99}
              color="blue"
              preview={
                <div className="font-mono text-xl font-bold text-center">
                  <span className="text-primary">625,284</span>
                  <span className="text-muted-foreground"> = </span>
                  <span className="text-bitcoin-orange">283</span>
                  <span className="text-muted-foreground"> × </span>
                  <span className="text-blue-500">47²</span>
                  <span className="text-muted-foreground"> + </span>
                  <span className="text-green-500">137</span>
                </div>
              }
              content={
                <div className="space-y-4 text-sm text-muted-foreground">
                  <FormulaBreakdownDiagram animated={true} />
                  <ul className="space-y-2 ml-4">
                    <li><strong className="text-bitcoin-orange">283</strong>: Bitcoin block number from January 2009</li>
                    <li><strong className="text-blue-500">47</strong>: Prime number appearing 47 times in Qubic core</li>
                    <li><strong className="text-green-500">137</strong>: Fine-structure constant from physics</li>
                    <li><strong className="text-primary">625,284</strong>: Qubic's main network address</li>
                  </ul>
                  <div className="p-4 rounded-lg bg-verified-bg border border-verified text-verified">
                    Probability of random alignment: <strong>less than 1 in 4 billion</strong>
                  </div>
                </div>
              }
            />

            {/* Discovery 2: The Data Bridge */}
            <DiscoveryAccordion
              index={1}
              expanded={expandedDiscovery === 1}
              onToggle={() => setExpandedDiscovery(expandedDiscovery === 1 ? null : 1)}
              icon={<GitBranch className="h-5 w-5" />}
              title="The Data Bridge"
              subtitle="How Data Flows"
              confidence={95}
              color="purple"
              preview={
                <div className="flex items-center justify-center gap-4 py-2">
                  <BitcoinLogoSVG size={28} />
                  <motion.div
                    className="w-24 h-1 bg-gradient-to-r from-bitcoin-orange to-qubic-purple rounded-full"
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                  <QubicLogoSVG size={28} />
                </div>
              }
              content={
                <div className="space-y-4 text-sm text-muted-foreground">
                  <DataFlowDiagram />
                  <p>Qubic's AI can retrieve specific data from Bitcoin blocks encoded in its memory structure.</p>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 rounded-lg bg-verified-bg border border-verified text-center">
                      <div className="text-xs text-verified">Block #9</div>
                      <div className="text-lg font-mono font-bold text-verified">0xCA</div>
                    </div>
                    <div className="p-3 rounded-lg bg-verified-bg border border-verified text-center">
                      <div className="text-xs text-verified">Block #16065</div>
                      <div className="text-lg font-mono font-bold text-verified">0x4A</div>
                    </div>
                  </div>
                </div>
              }
            />

            {/* Discovery 3: The Time-Lock */}
            <DiscoveryAccordion
              index={2}
              expanded={expandedDiscovery === 2}
              onToggle={() => setExpandedDiscovery(expandedDiscovery === 2 ? null : 2)}
              icon={<Lock className="h-5 w-5" />}
              title="The Time-Lock Activation"
              subtitle="March 3, 2026"
              confidence={85}
              color="amber"
              preview={<CountdownVisual size="small" />}
              content={
                <div className="space-y-4 text-sm text-muted-foreground">
                  <CountdownVisual size="large" />
                  <div className="p-4 rounded-lg bg-warning-bg border border-warning">
                    <p className="font-medium text-warning mb-2">What will happen? We don't know.</p>
                    <ul className="space-y-1 text-warning/80 text-xs">
                      <li>The math lines up perfectly</li>
                      <li>Qubic can read Bitcoin's data</li>
                      <li>Both systems point to the same date</li>
                      <li>Satoshi's bitcoins are still dormant</li>
                    </ul>
                  </div>
                </div>
              }
            />
          </div>
        </motion.div>
      </div>
    </section>
  )
}

// Step Components
function BitcoinGenesisStep({ isInView }: { isInView: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.4 }}
      className="grid grid-cols-1 lg:grid-cols-2 gap-6"
    >
      <div className="p-6 rounded-xl bg-gradient-to-b from-orange-950/40 to-orange-950/20 border border-orange-900/50">
        <div className="flex items-center gap-3 mb-6">
          <BitcoinLogoSVG size={40} />
          <div>
            <h3 className="text-xl font-semibold">Bitcoin Genesis</h3>
            <p className="text-sm text-muted-foreground">Block #0 - January 3, 2009</p>
          </div>
          <VerificationBadge level="verified" size="sm" className="ml-auto" />
        </div>

        <div className="space-y-4">
          <DataCard
            icon={<Binary className="h-4 w-4 text-bitcoin-orange" />}
            title="Genesis Block Hash"
            content={
              <>
                <div className="font-mono text-xs break-all text-muted-foreground mb-2">
                  000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-bitcoin-orange font-bold text-2xl">43</span>
                  <span className="text-sm text-muted-foreground">leading zero bits</span>
                </div>
              </>
            }
          />

          <DataCard
            icon={<Hash className="h-4 w-4 text-bitcoin-orange" />}
            title="Coinbase Message"
            content={
              <p className="text-sm italic text-bitcoin-orange/80">
                "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks"
              </p>
            }
          />

          <DataCard
            icon={<Calendar className="h-4 w-4 text-bitcoin-orange" />}
            title="Timeline"
            content={
              <div className="text-sm text-muted-foreground space-y-1">
                <div>Genesis: January 3, 2009</div>
                <div>Block #283: January 12, 2009</div>
                <div>1CFB Address: January 13, 2009</div>
              </div>
            }
          />
        </div>
      </div>

      <div className="p-6 rounded-xl bg-muted/30 border border-border flex flex-col justify-center">
        <h4 className="text-lg font-semibold mb-4">Why Block #283?</h4>
        <ul className="space-y-3 text-sm text-muted-foreground">
          <li className="flex items-start gap-2">
            <Target className="h-4 w-4 text-bitcoin-orange mt-1 flex-shrink-0" />
            One of the first 300 blocks ever created
          </li>
          <li className="flex items-start gap-2">
            <Zap className="h-4 w-4 text-bitcoin-orange mt-1 flex-shrink-0" />
            Mined by Satoshi Nakamoto himself
          </li>
          <li className="flex items-start gap-2">
            <Lock className="h-4 w-4 text-bitcoin-orange mt-1 flex-shrink-0" />
            Contains 50 BTC (~$2.5M) never moved
          </li>
          <li className="flex items-start gap-2">
            <Calculator className="h-4 w-4 text-bitcoin-orange mt-1 flex-shrink-0" />
            283 is a prime number with special properties
          </li>
        </ul>
      </div>
    </motion.div>
  )
}

function FormulaStep({ isInView }: { isInView: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.4 }}
      className="p-8 rounded-xl bg-gradient-to-r from-orange-950/20 via-purple-950/30 to-purple-950/20 border border-border"
    >
      <div className="text-center mb-8">
        <h3 className="text-xl font-semibold mb-2">The Mathematical Bridge</h3>
        <VerificationBadge level="verified" percentage={99} showPercentage />
      </div>

      <div className="flex flex-col md:flex-row items-center justify-center gap-6 mb-8">
        <div className="text-center">
          <BitcoinLogoSVG size={40} className="mx-auto mb-2" />
          <div className="text-sm text-muted-foreground">Block</div>
          <div className="text-3xl font-mono font-bold text-bitcoin-orange">#283</div>
        </div>

        <div className="text-3xl text-muted-foreground">→</div>

        <div className="text-center p-4 rounded-lg bg-black/30">
          <div className="font-mono text-2xl">
            <span className="text-bitcoin-orange">283</span>
            <span className="text-muted-foreground"> × </span>
            <span className="text-blue-500">47²</span>
            <span className="text-muted-foreground"> + </span>
            <span className="text-green-500">137</span>
          </div>
        </div>

        <div className="text-3xl text-muted-foreground">→</div>

        <div className="text-center">
          <QubicLogoSVG size={40} className="mx-auto mb-2" />
          <div className="text-sm text-muted-foreground">Position</div>
          <div className="text-3xl font-mono font-bold text-qubic-purple">
            <AnimatedCounter value={625284} duration={2000} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 text-center">
        <div className="p-3 rounded-lg bg-bitcoin-orange/10 border border-bitcoin-orange/30">
          <div className="text-bitcoin-orange font-bold text-2xl">283</div>
          <div className="text-xs text-muted-foreground">Prime Block #</div>
        </div>
        <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
          <div className="text-blue-500 font-bold text-2xl">47²</div>
          <div className="text-xs text-muted-foreground">= 2,209</div>
        </div>
        <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/30">
          <div className="text-green-500 font-bold text-2xl">137</div>
          <div className="text-xs text-muted-foreground">Fine Structure</div>
        </div>
      </div>
    </motion.div>
  )
}

function QubicNetworkStep({ isInView }: { isInView: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.4 }}
      className="p-6 rounded-xl bg-gradient-to-b from-purple-950/40 to-purple-950/20 border border-purple-900/50"
    >
      <div className="flex items-center gap-3 mb-6">
        <QubicLogoSVG size={40} />
        <div>
          <h3 className="text-xl font-semibold">Qubic Network</h3>
          <p className="text-sm text-muted-foreground">First Epoch - April 2024</p>
        </div>
        <VerificationBadge level="verified" size="sm" className="ml-auto" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <DataCard
          icon={<Binary className="h-4 w-4 text-qubic-purple" />}
          title="Jinn Memory Matrix"
          content={
            <div className="font-mono text-center">
              <span className="text-qubic-purple text-xl">128 × 128</span>
              <span className="text-muted-foreground"> = </span>
              <span className="text-xl">16,384</span>
              <div className="text-xs text-muted-foreground mt-1">addresses</div>
            </div>
          }
        />

        <DataCard
          icon={<Hash className="h-4 w-4 text-qubic-purple" />}
          title="Position 625,284"
          content={
            <div className="text-center">
              <div className="text-qubic-purple font-bold text-2xl">Row 21, Col 4</div>
              <div className="text-xs text-muted-foreground">Boot address 2,692</div>
            </div>
          }
        />

        <DataCard
          icon={<Calculator className="h-4 w-4 text-qubic-purple" />}
          title="Network Stats"
          content={
            <div className="grid grid-cols-2 gap-2 text-center">
              <div>
                <div className="text-qubic-purple font-bold">676</div>
                <div className="text-xs text-muted-foreground">Computors</div>
              </div>
              <div>
                <div className="text-qubic-purple font-bold">50K+</div>
                <div className="text-xs text-muted-foreground">Nodes</div>
              </div>
            </div>
          }
        />
      </div>
    </motion.div>
  )
}

function TimelockStep({ isInView }: { isInView: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.4 }}
      className="p-6 rounded-xl bg-gradient-to-b from-amber-950/40 to-amber-950/20 border border-amber-900/50"
    >
      <div className="text-center mb-6">
        <Lock className="h-12 w-12 text-amber-400 mx-auto mb-3" />
        <h3 className="text-xl font-semibold">The Time-Lock</h3>
        <p className="text-sm text-muted-foreground">March 3, 2026</p>
      </div>

      <CountdownVisual size="large" />

      <div className="mt-6 p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
        <p className="text-sm text-amber-200/90 text-center">
          A cryptographic safe that opens automatically on this date.
          <br />
          <strong className="text-amber-400">56 days remaining.</strong>
        </p>
      </div>
    </motion.div>
  )
}

// Helper Components
function DataCard({ icon, title, content }: { icon: React.ReactNode; title: string; content: React.ReactNode }) {
  return (
    <div className="p-4 rounded-lg bg-black/30">
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className="text-sm font-medium">{title}</span>
      </div>
      {content}
    </div>
  )
}

function DiscoveryAccordion({
  index,
  expanded,
  onToggle,
  icon,
  title,
  subtitle,
  confidence,
  color,
  preview,
  content,
}: {
  index: number
  expanded: boolean
  onToggle: () => void
  icon: React.ReactNode
  title: string
  subtitle: string
  confidence: number
  color: 'blue' | 'purple' | 'amber'
  preview: React.ReactNode
  content: React.ReactNode
}) {
  const colorClasses = {
    blue: 'border-blue-500/30 hover:border-blue-500/50',
    purple: 'border-purple-500/30 hover:border-purple-500/50',
    amber: 'border-amber-500/30 hover:border-amber-500/50',
  }

  const iconBg = {
    blue: 'bg-blue-500/10 text-blue-400',
    purple: 'bg-purple-500/10 text-purple-400',
    amber: 'bg-amber-500/10 text-amber-400',
  }

  return (
    <div className={`rounded-xl border bg-card/50 overflow-hidden transition-all ${colorClasses[color]}`}>
      <button
        onClick={onToggle}
        className="w-full p-5 flex items-center gap-4 text-left hover:bg-muted/30 transition-colors"
      >
        <div className={`p-2 rounded-lg ${iconBg[color]}`}>{icon}</div>
        <div className="flex-1">
          <div className="text-xs text-muted-foreground uppercase tracking-wider mb-0.5">{subtitle}</div>
          <div className="font-semibold">{title}</div>
        </div>
        <VerificationBadge
          level={confidence >= 95 ? 'verified' : confidence >= 70 ? 'high' : 'medium'}
          size="sm"
        />
        {expanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
      </button>

      {!expanded && <div className="px-5 pb-5">{preview}</div>}

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 border-t border-border/50 pt-4">
              {content}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
