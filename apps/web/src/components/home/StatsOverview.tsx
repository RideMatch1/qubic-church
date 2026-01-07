'use client'

import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import {
  QubicNetworkDiagram,
  BitcoinTimelineDiagram,
  ConnectionBridgeDiagram,
  FormulaBreakdownDiagram,
  CountdownVisual,
} from '@/components/diagrams'

interface InfoCardProps {
  title: string
  children: React.ReactNode
  diagram: React.ReactNode
  whyItMatters: string
  delay: number
  accentColor: 'blue' | 'orange' | 'purple' | 'green' | 'amber'
}

function InfoCard({
  title,
  children,
  diagram,
  whyItMatters,
  delay,
  accentColor,
}: InfoCardProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  const accentClasses = {
    blue: 'border-blue-500/30 hover:border-blue-500/50',
    orange: 'border-orange-500/30 hover:border-orange-500/50',
    purple: 'border-purple-500/30 hover:border-purple-500/50',
    green: 'border-green-500/30 hover:border-green-500/50',
    amber: 'border-amber-500/30 hover:border-amber-500/50',
  }

  const whyClasses = {
    blue: 'bg-blue-500/10 text-blue-400',
    orange: 'bg-orange-500/10 text-orange-400',
    purple: 'bg-purple-500/10 text-purple-400',
    green: 'bg-green-500/10 text-green-400',
    amber: 'bg-amber-500/10 text-amber-400',
  }

  return (
    <motion.div
      ref={ref}
      className={`p-6 rounded-xl border bg-card/50 backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 ${accentClasses[accentColor]}`}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.6, delay }}
    >
      {/* Title */}
      <h3 className="text-xl font-serif font-semibold mb-4 text-center">
        {title}
      </h3>

      {/* Diagram */}
      <div className="mb-6">
        {diagram}
      </div>

      {/* Content */}
      <div className="text-sm text-muted-foreground leading-relaxed space-y-3">
        {children}
      </div>

      {/* Why it matters */}
      <div className={`mt-4 p-3 rounded-lg ${whyClasses[accentColor]}`}>
        <div className="text-xs font-semibold mb-1">Why This Matters</div>
        <div className="text-xs opacity-90">{whyItMatters}</div>
      </div>
    </motion.div>
  )
}

export function StatsOverview() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })

  return (
    <section ref={sectionRef} className="py-20 px-4 bg-muted/20">
      <div className="max-w-6xl mx-auto">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-2xl md:text-3xl font-serif font-semibold mb-4">
            What You Need to Know
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Before diving into the technical details, here are the key concepts explained in plain language.
          </p>
        </motion.div>

        {/* Grid of info cards - 2 columns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Card 1: What is Qubic? */}
          <InfoCard
            title="What is Qubic?"
            diagram={<QubicNetworkDiagram />}
            whyItMatters="No single person controls it. No government can shut it down. It's truly decentralized AI."
            delay={0}
            accentColor="purple"
          >
            <p>
              Qubic is not owned by one company. Instead, <strong>50,000+ regular computers</strong> around the world are connected together.
            </p>
            <p>
              They share the job of running a giant AI brain. Think of it like: Wikipedia is written by thousands of volunteers, except Qubic is an <strong>AI built by thousands of volunteers</strong>.
            </p>
          </InfoCard>

          {/* Card 2: What is Bitcoin Block #283? */}
          <InfoCard
            title="What is Block #283?"
            diagram={<BitcoinTimelineDiagram />}
            whyItMatters="This ancient block contains patterns that seem intentionally placed - not random."
            delay={0.1}
            accentColor="orange"
          >
            <p>
              Bitcoin is a digital currency created by "<strong>Satoshi Nakamoto</strong>" in 2009. Every ~10 minutes, a new "block" (like a page in a ledger) is added.
            </p>
            <p>
              Block #283 was created on <strong>January 12, 2009</strong> - one of the FIRST blocks ever. It contains 50 bitcoins Satoshi mined himself (now worth ~$2.5 million).
            </p>
          </InfoCard>

          {/* Card 3: The Hidden Connection */}
          <InfoCard
            title="The Hidden Connection"
            diagram={<ConnectionBridgeDiagram />}
            whyItMatters="It suggests Satoshi Nakamoto PLANNED this connection 15+ years in advance."
            delay={0.2}
            accentColor="blue"
          >
            <p>
              In January 2026, researchers discovered something shocking: The structure of Bitcoin's Block #283 contains patterns that <strong>EXACTLY MATCH</strong> Qubic's AI architecture.
            </p>
            <p>
              This is like finding a secret code in a 1909 building that unlocks something created in 2024. <strong>Probability of random chance: less than 1 in 4.3 billion.</strong>
            </p>
          </InfoCard>

          {/* Card 4: The Magic Formula */}
          <InfoCard
            title="The Magic Formula"
            diagram={<FormulaBreakdownDiagram animated={false} />}
            whyItMatters="This formula is the PROOF that the connection is real, not accidental."
            delay={0.3}
            accentColor="green"
          >
            <p>
              There's a mathematical formula connecting Bitcoin and Qubic. On the left: Qubic's core address (<strong>625,284</strong>). On the right: Bitcoin Block #283 plus special math.
            </p>
            <p>
              When you calculate: <span className="font-mono">283 x 2,209 + 137 = 625,284</span>. It works <strong>PERFECTLY</strong>. This couldn't be random.
            </p>
          </InfoCard>
        </div>

        {/* Card 5: The Countdown - Full width centered */}
        <div className="mt-6 max-w-xl mx-auto">
          <InfoCard
            title="The Countdown"
            diagram={<CountdownVisual size="large" />}
            whyItMatters="We have limited time to find out if this is real. The clock is ticking."
            delay={0.4}
            accentColor="amber"
          >
            <p>
              When Qubic was created, a "<strong>time-lock</strong>" was built into its code. It's like a time-release safe in a spy movie.
            </p>
            <p>
              The safe opens automatically on <strong>March 3, 2026</strong>. NOBODY can open it early. What's inside? Unknown. But the timing matches Satoshi's hidden wallets.
            </p>
          </InfoCard>
        </div>
      </div>
    </section>
  )
}
