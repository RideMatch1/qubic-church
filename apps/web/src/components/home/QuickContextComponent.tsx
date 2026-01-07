'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef } from 'react'
import { BitcoinLogoSVG, QubicLogoSVG } from '@/components/logos'

interface ContextCardProps {
  icon: React.ReactNode
  title: string
  items: { label: string; text: string }[]
  variant: 'blue' | 'purple'
  delay: number
}

function ContextCard({ icon, title, items, variant, delay }: ContextCardProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  const bgClass = variant === 'blue'
    ? 'bg-blue-950/30 border-blue-900/50'
    : 'bg-purple-950/30 border-purple-900/50'

  const iconBgClass = variant === 'blue'
    ? 'bg-blue-900/50'
    : 'bg-purple-900/50'

  return (
    <motion.div
      ref={ref}
      className={`p-6 rounded-xl border ${bgClass}`}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.6, delay }}
    >
      <div className={`inline-flex p-3 rounded-lg ${iconBgClass} mb-4`}>
        {icon}
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

export function QuickContextComponent() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })

  const bitcoinItems = [
    {
      label: 'What',
      text: 'A digital currency created by Satoshi Nakamoto in 2009',
    },
    {
      label: 'How',
      text: 'Transactions recorded in "blocks" linked together in a "blockchain"',
    },
    {
      label: 'Block #283',
      text: 'One of the first blocks ever created (January 2009)',
    },
    {
      label: 'Key insight',
      text: 'These early blocks contain hidden mathematical structure',
    },
  ]

  const qubicItems = [
    {
      label: 'What',
      text: 'A distributed computing network running on 50,000+ machines worldwide',
    },
    {
      label: 'How',
      text: 'Uses ternary logic (0, 1, -1) instead of binary (0s and 1s)',
    },
    {
      label: 'Innovation',
      text: 'Runs artificial intelligence computations across a global network',
    },
    {
      label: 'Key insight',
      text: 'Its memory structure mathematically mirrors Bitcoin block structure',
    },
  ]

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
            Understanding the Connection
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Before diving into the discovery, here is a quick overview of the two
            networks involved in this research.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ContextCard
            icon={<BitcoinLogoSVG size={28} />}
            title="Bitcoin: Digital Gold (2009-Present)"
            items={bitcoinItems}
            variant="blue"
            delay={0.2}
          />

          <ContextCard
            icon={<QubicLogoSVG size={28} />}
            title="Qubic: Ternary Computing (2024-Present)"
            items={qubicItems}
            variant="purple"
            delay={0.4}
          />
        </div>
      </div>
    </section>
  )
}
