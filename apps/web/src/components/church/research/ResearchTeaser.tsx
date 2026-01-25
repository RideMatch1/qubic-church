'use client'

/**
 * ResearchTeaser Component
 * Brief mention of ongoing research with link to archives
 * Includes CFB/Satoshi research as secondary content
 */

import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  BookOpen,
  Microscope,
  FileSearch,
  ArrowRight,
  FlaskConical,
  Search,
} from 'lucide-react'

const researchHighlights = [
  {
    icon: Microscope,
    title: 'Mathematical Patterns',
    description: 'Verified formulas connecting Bitcoin genesis and Qubic architecture',
    confidence: 99,
    tier: 1,
    href: '/docs/03-results/02-formula-discovery',
  },
  {
    icon: FlaskConical,
    title: 'Anna Neural Network',
    description: 'Analysis of the Anna bot architecture and its ternary processing',
    confidence: 85,
    tier: 2,
    href: '/docs/03-results/16-anna-bot-analysis',
  },
  {
    icon: FileSearch,
    title: 'Bitcoin-Qubic Bridge',
    description: 'Documented connections between early Bitcoin patterns and Qubic',
    confidence: 90,
    tier: 2,
    href: '/docs/03-results/01-bitcoin-bridge',
  },
]

function ConfidenceBadge({ value, tier }: { value: number; tier: number }) {
  const color =
    tier === 1
      ? 'bg-green-500/20 text-green-400 border-green-500/30'
      : tier === 2
      ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      : 'bg-orange-500/20 text-orange-400 border-orange-500/30'

  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border ${color}`}>
      Tier {tier} • {value}%
    </span>
  )
}

export function ResearchTeaser() {
  return (
    <section className="w-full py-20 bg-gradient-to-b from-background via-orange-950/5 to-background">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="inline-flex items-center gap-2 bg-orange-500/10 border border-orange-500/20 rounded-full px-4 py-2 mb-4">
            <BookOpen className="w-4 h-4 text-orange-500" />
            <span className="text-sm font-medium text-orange-500 uppercase tracking-wide">
              Academic Research
            </span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Open Source Discoveries
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            All research is 100% free and transparent. We document mathematical patterns,
            present evidence with confidence tiers, and let you draw your own conclusions.
          </p>
        </motion.div>

        {/* Research Highlights Grid */}
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-12">
          {researchHighlights.map((item, index) => {
            const Icon = item.icon
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
              >
                <Link
                  href={item.href}
                  className="block p-6 rounded-2xl bg-card border border-border hover:border-primary/30 transition-all group h-full"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 rounded-xl bg-primary/10">
                      <Icon className="w-5 h-5 text-primary" />
                    </div>
                    <ConfidenceBadge value={item.confidence} tier={item.tier} />
                  </div>
                  <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {item.description}
                  </p>
                </Link>
              </motion.div>
            )
          })}
        </div>

        {/* CFB/Satoshi Brief Mention */}
        <motion.div
          className="max-w-3xl mx-auto mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="p-6 rounded-2xl bg-gradient-to-r from-orange-500/5 to-purple-500/5 border border-white/10">
            <div className="flex items-start gap-4">
              <div className="p-2 rounded-lg bg-orange-500/10 shrink-0">
                <Search className="w-5 h-5 text-orange-400" />
              </div>
              <div>
                <h4 className="font-semibold text-foreground mb-2">
                  Ongoing Investigation: CFB-Satoshi Connection
                </h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Our research explores potential connections between Qubic's architect (CFB)
                  and Bitcoin's creator. This is <strong>Tier 2-3 evidence</strong> - statistically
                  interesting but not conclusive. We present the patterns and let you decide.
                </p>
                <Link
                  href="/docs/03-results/24-cfb-satoshi-connection"
                  className="inline-flex items-center gap-1 text-sm text-orange-400 hover:text-orange-300 transition-colors"
                >
                  Read the full analysis
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        </motion.div>

        {/* CTA to Archives */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Link
            href="/docs"
            className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-8 py-4 rounded-xl font-semibold hover:bg-primary/90 transition-all"
          >
            <BookOpen className="w-5 h-5" />
            Explore Full Research Archive
            <ArrowRight className="w-5 h-5" />
          </Link>
          <p className="text-xs text-muted-foreground mt-4">
            75+ documented findings • Open methodology • Reproducible results
          </p>
        </motion.div>
      </div>
    </section>
  )
}
