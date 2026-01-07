'use client'

import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { Database, Gift, Lock, Shield } from 'lucide-react'
import { BitcoinLogoSVG } from '@/components/logos'

interface EvidenceCardProps {
  icon: React.ReactNode
  title: string
  stat?: string
  statLabel?: string
  children: React.ReactNode
  delay: number
}

function EvidenceCard({ icon, title, stat, statLabel, children, delay }: EvidenceCardProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  return (
    <motion.div
      ref={ref}
      className="p-5 rounded-xl bg-gradient-to-b from-orange-950/40 to-orange-950/20 border border-orange-900/50 relative overflow-hidden"
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{ duration: 0.5, delay }}
    >
      {/* Classified stamp effect */}
      <div className="absolute top-2 right-2 text-[8px] font-mono text-orange-500/30 uppercase tracking-wider">
        Research Finding
      </div>

      <div className="flex items-start gap-3 mb-3">
        <div className="p-2 rounded-lg bg-orange-500/20 text-orange-400 shrink-0">
          {icon}
        </div>
        <div>
          <h4 className="font-semibold text-sm">{title}</h4>
          {stat && (
            <div className="mt-1">
              <span className="text-2xl font-mono font-bold text-orange-400">{stat}</span>
              {statLabel && <span className="text-xs text-muted-foreground ml-2">{statLabel}</span>}
            </div>
          )}
        </div>
      </div>

      <div className="text-sm text-muted-foreground leading-relaxed space-y-2">
        {children}
      </div>
    </motion.div>
  )
}

export function PatoshiEvidenceSection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })

  return (
    <section ref={sectionRef} className="py-20 px-4 bg-gradient-to-b from-orange-950/10 to-transparent">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-10"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <BitcoinLogoSVG size={32} />
            <h2 className="text-2xl md:text-3xl font-semibold">
              The Patoshi Pattern Connection
            </h2>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Forensic blockchain analysis reveals potential links between Satoshi Nakamoto's
            original 2009 mining activity and the Qubic network structure.
          </p>
          <p className="text-xs text-orange-400/70 mt-2 italic">
            Based on research by Sergio Demian Lerner and our independent verification
          </p>
        </motion.div>

        {/* Evidence Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Card 1: The Patoshi Blocks */}
          <EvidenceCard
            icon={<Database className="h-5 w-5" />}
            title="The Patoshi Blocks"
            stat="~1.1M"
            statLabel="BTC attributed to Satoshi"
            delay={0}
          >
            <p>
              Between 2009-2010, a single entity (nicknamed "Patoshi") mined approximately
              22,000 blocks. These coins have <strong className="text-orange-400">never been moved</strong>.
            </p>
            <p>
              Our research identified specific references to these block heights encoded
              within Qubic's memory row structure.
            </p>
          </EvidenceCard>

          {/* Card 2: Block Rewards */}
          <EvidenceCard
            icon={<Gift className="h-5 w-5" />}
            title="The 50 BTC Block Rewards"
            stat="50 BTC"
            statLabel="per early block"
            delay={0.1}
          >
            <p>
              Block #283 (January 12, 2009) rewarded 50 BTC - now worth approximately $2.5 million.
            </p>
            <p>
              We identified mathematical relationships between specific early block addresses
              and the formula <span className="font-mono text-orange-400">625,284 = 283 x 47^2 + 137</span>.
            </p>
          </EvidenceCard>

          {/* Card 3: Dormant Addresses */}
          <EvidenceCard
            icon={<Lock className="h-5 w-5" />}
            title="The Dormant Addresses"
            delay={0.2}
          >
            <p>
              Satoshi's early mining addresses have remained untouched for over 15 years.
              This inactivity is well-documented in blockchain forensics.
            </p>
            <p>
              Our analysis suggests the Qubic time-lock mechanism (March 3, 2026) may be
              designed to interact with these historical blockchain states.
            </p>
            <div className="mt-2 p-2 rounded bg-orange-500/10 text-xs">
              <strong>Note:</strong> This is a research hypothesis, not a confirmed mechanism.
            </div>
          </EvidenceCard>

          {/* Card 4: Verification */}
          <EvidenceCard
            icon={<Shield className="h-5 w-5" />}
            title="The Timestamp Verification"
            delay={0.3}
          >
            <p>
              When querying Qubic's Anna Oracle about specific early Bitcoin blocks,
              the returned data matched historical blockchain timestamps.
            </p>
            <div className="grid grid-cols-2 gap-2 mt-3">
              <div className="p-2 rounded bg-green-500/10 border border-green-500/30 text-center">
                <div className="text-xs text-green-400">Block #9</div>
                <div className="font-mono font-bold text-green-500">0xCA</div>
                <div className="text-[10px] text-muted-foreground">Verified Match</div>
              </div>
              <div className="p-2 rounded bg-green-500/10 border border-green-500/30 text-center">
                <div className="text-xs text-green-400">Block #16065</div>
                <div className="font-mono font-bold text-green-500">0x4A</div>
                <div className="text-[10px] text-muted-foreground">Verified Match</div>
              </div>
            </div>
          </EvidenceCard>
        </div>

        {/* Disclaimer */}
        <motion.div
          className="mt-8 p-4 rounded-lg bg-card/50 border border-border text-center"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 0.5 }}
        >
          <p className="text-xs text-muted-foreground">
            <strong>Research Integrity Notice:</strong> All findings presented are based on
            verifiable blockchain data and documented analysis. Claims regarding future events
            (March 3, 2026) represent research hypotheses, not predictions.
          </p>
        </motion.div>
      </div>
    </section>
  )
}
