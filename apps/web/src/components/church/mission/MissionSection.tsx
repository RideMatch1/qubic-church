'use client'

/**
 * MissionSection Component
 * Church mission and research principles (standalone version)
 */

import { useRef, useState } from 'react'
import { motion, useInView } from 'framer-motion'
import { Target, Search, FileText, Scale, ShieldCheck } from 'lucide-react'

// Confidence meter component
function ConfidenceMeter({ value, label }: { value: number; label: string }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <div ref={ref} className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-mono">{value}%</span>
      </div>
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${
            value >= 80
              ? 'bg-green-500'
              : value >= 60
              ? 'bg-yellow-500'
              : value >= 40
              ? 'bg-orange-500'
              : 'bg-red-500'
          }`}
          initial={{ width: 0 }}
          animate={{ width: isInView ? `${value}%` : 0 }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

const researchPrinciples = [
  {
    icon: Search,
    title: 'Open Investigation',
    description: 'All research is public and verifiable. Anyone can check our work.',
  },
  {
    icon: Scale,
    title: 'Evidence-Based',
    description: 'We classify evidence into tiers: Verified, Supported, and Hypothetical.',
  },
  {
    icon: FileText,
    title: 'Full Transparency',
    description: 'Our data, scripts, and methodology are all open source.',
  },
  {
    icon: ShieldCheck,
    title: 'Academic Rigor',
    description: 'Statistical analysis with p-values and confidence intervals.',
  },
]

export function MissionSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, amount: 0.3 })
  const [activeTab, setActiveTab] = useState<'mission' | 'tiers'>('mission')

  return (
    <section className="w-full py-20 bg-gradient-to-b from-background via-primary/5 to-background">
      <div className="container mx-auto px-4 max-w-5xl">
        {/* Section Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-full px-4 py-2 mb-4">
            <Target className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-primary uppercase tracking-wide">
              Our Mission
            </span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Independent Research Collective
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Investigating mathematical connections between Bitcoin and Qubic through
            rigorous academic research - sharing all findings openly with the community.
          </p>
        </motion.div>

        <div ref={ref} className="space-y-8">
          {/* Mission & Principles Card */}
          <motion.div
            className="p-6 md:p-8 rounded-2xl bg-card border border-border"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
            transition={{ duration: 0.5 }}
          >
            {/* Tab Navigation */}
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => setActiveTab('mission')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === 'mission'
                    ? 'bg-primary/20 text-primary border border-primary/30'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                }`}
              >
                Research Principles
              </button>
              <button
                onClick={() => setActiveTab('tiers')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === 'tiers'
                    ? 'bg-purple-500/20 text-purple-500 border border-purple-500/30'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                }`}
              >
                Evidence Tiers
              </button>
            </div>

            {/* Tab Content */}
            {activeTab === 'mission' && (
              <div className="grid md:grid-cols-2 gap-4">
                {researchPrinciples.map((principle, index) => {
                  const Icon = principle.icon
                  return (
                    <motion.div
                      key={index}
                      className="p-4 rounded-xl bg-muted/50"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
                      transition={{ duration: 0.3, delay: 0.1 * index }}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <Icon className="w-4 h-4 text-muted-foreground" />
                        <span className="font-medium">{principle.title}</span>
                      </div>
                      <p className="text-sm text-muted-foreground">{principle.description}</p>
                    </motion.div>
                  )
                })}
              </div>
            )}

            {activeTab === 'tiers' && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-0.5 rounded text-xs bg-green-500/30 text-green-500">
                      Tier 1
                    </span>
                    <span className="font-medium">Mathematically Verified</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Calculator-verifiable facts. Anyone can reproduce these results.
                  </p>
                </div>
                <div className="p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/20">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-0.5 rounded text-xs bg-yellow-500/30 text-yellow-500">
                      Tier 2
                    </span>
                    <span className="font-medium">Statistically Supported</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Patterns with statistical significance (p &lt; 0.05). Multiple data points support the hypothesis.
                  </p>
                </div>
                <div className="p-4 rounded-xl bg-orange-500/10 border border-orange-500/20">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-0.5 rounded text-xs bg-orange-500/30 text-orange-500">
                      Tier 3
                    </span>
                    <span className="font-medium">Hypothetical</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Reasonable hypotheses based on observed patterns, requiring more evidence.
                  </p>
                </div>
              </div>
            )}
          </motion.div>

          {/* Confidence Levels */}
          <motion.div
            className="p-6 rounded-2xl bg-card border border-border"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <h3 className="text-lg font-semibold mb-6">
              Current Research Confidence Levels
            </h3>

            <div className="space-y-4">
              <ConfidenceMeter value={99} label="Mathematical Formula Correctness" />
              <ConfidenceMeter value={90} label="Block 576 Anomaly" />
              <ConfidenceMeter value={85} label="Anna Bot Neural Architecture" />
              <ConfidenceMeter value={70} label="CFB-Satoshi Connection" />
              <ConfidenceMeter value={60} label="Time-Lock March 2026 Event" />
            </div>

            <p className="text-xs text-muted-foreground mt-4 italic">
              Confidence levels based on evidence quality and reproducibility. Updated January 2026.
            </p>
          </motion.div>

          {/* Disclaimer */}
          <motion.div
            className="p-4 rounded-xl bg-muted/50 border border-border"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <div className="flex items-start gap-3">
              <ShieldCheck className="w-5 h-5 text-muted-foreground shrink-0 mt-0.5" />
              <div>
                <h4 className="font-medium mb-2">What we do NOT claim</h4>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  <li>- We do NOT claim CFB is definitively Satoshi</li>
                  <li>- We do NOT claim the time-lock will definitely activate</li>
                  <li>- We do NOT provide financial advice</li>
                  <li>- We present evidence and let you draw your own conclusions</li>
                </ul>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
