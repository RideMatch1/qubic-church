'use client'

import { useState, useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { Fingerprint, Calculator, Hash, Link2 } from 'lucide-react'
import { FormulaCalculator, LetterSumCalculator, GenesisConnectionViz } from '@/components/interactive'

type Tab = 'formula' | 'letters' | 'genesis'

interface TabConfig {
  id: Tab
  label: string
  icon: React.ReactNode
  description: string
}

const tabs: TabConfig[] = [
  {
    id: 'formula',
    label: 'Formula',
    icon: <Calculator className="h-4 w-4" />,
    description: 'Verify the 625,284 = 283 × 47² + 137 formula',
  },
  {
    id: 'letters',
    label: 'Letter Sums',
    icon: <Hash className="h-4 w-4" />,
    description: 'Calculate Qubic address letter sums',
  },
  {
    id: 'genesis',
    label: 'Genesis Bridge',
    icon: <Link2 className="h-4 w-4" />,
    description: 'See Bitcoin ↔ Qubic connections',
  },
]

export function InteractiveProofSection() {
  const [activeTab, setActiveTab] = useState<Tab>('formula')
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })

  return (
    <section ref={sectionRef} className="py-20 px-4 bg-gradient-to-b from-background to-muted/20">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Fingerprint className="h-8 w-8 text-primary" />
            <h2 className="text-2xl md:text-3xl font-serif font-semibold">
              Verify The Evidence Yourself
            </h2>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Don't take our word for it. Use these interactive tools to verify the mathematical
            connections between Bitcoin and Qubic yourself. Every calculation is reproducible.
          </p>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div
          className="flex flex-wrap justify-center gap-2 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === tab.id
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted/50 hover:bg-muted text-muted-foreground hover:text-foreground'
              }`}
            >
              {tab.icon}
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </motion.div>

        {/* Tab Description */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          key={activeTab}
        >
          <p className="text-sm text-muted-foreground">
            {tabs.find(t => t.id === activeTab)?.description}
          </p>
        </motion.div>

        {/* Tab Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {activeTab === 'formula' && <FormulaCalculator />}
          {activeTab === 'letters' && <LetterSumCalculator />}
          {activeTab === 'genesis' && <GenesisConnectionViz />}
        </motion.div>

        {/* Footer Note */}
        <motion.div
          className="mt-8 p-4 rounded-lg bg-muted/30 border border-border text-center"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 0.4 }}
        >
          <p className="text-xs text-muted-foreground">
            <strong>Reproducibility:</strong> All calculations use standard arithmetic.
            You can verify these results with any calculator or programming language.
            The data is sourced from public blockchain records.
          </p>
        </motion.div>
      </div>
    </section>
  )
}
