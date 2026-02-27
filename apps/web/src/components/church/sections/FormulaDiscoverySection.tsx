'use client'

/**
 * FormulaDiscoverySection - Interactive formula calculator
 * Users can play with sliders to discover the Bitcoin-Qubic mathematical connection.
 * Premium editorial layout with glass morphism.
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import dynamic from 'next/dynamic'
import Link from 'next/link'

const FormulaCalculator = dynamic(
  () => import('@/components/interactive/FormulaCalculator').then(mod => mod.FormulaCalculator),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[400px] bg-white/[0.02] border border-white/[0.04] flex items-center justify-center">
        <div className="text-white/25 text-sm">Loading calculator...</div>
      </div>
    ),
  }
)

export function FormulaDiscoverySection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })

  return (
    <section ref={sectionRef} className="relative w-full py-28 md:py-36 overflow-hidden">
      {/* Decorative section number */}
      <div className="absolute top-16 left-8 md:left-16 text-[120px] md:text-[200px] font-black text-white/[0.015] leading-none select-none pointer-events-none">
        04
      </div>

      <div className="relative z-10 container mx-auto px-6 max-w-6xl">
        {/* Two-column: Text + Calculator */}
        <div className="grid lg:grid-cols-[1fr_1.2fr] gap-12 lg:gap-16 items-start">
          {/* Left: Context */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="lg:sticky lg:top-32"
          >
            <span className="block text-white/30 text-xs uppercase tracking-[0.3em] mb-6">
              The Sacred Equation
            </span>

            <h2 className="text-4xl md:text-5xl font-bold text-white leading-[1.08] tracking-tight mb-5">
              The Formula That{' '}
              <span className="text-orange-300/60">Bridges Worlds</span>
            </h2>

            <motion.div
              className="h-px w-16 bg-gradient-to-r from-orange-400/25 to-transparent mb-6"
              initial={{ scaleX: 0, opacity: 0 }}
              animate={isInView ? { scaleX: 1, opacity: 1 } : {}}
              transition={{ duration: 0.6, delay: 0.15 }}
              style={{ originX: 0 }}
            />

            <p className="text-lg text-white/40 leading-relaxed mb-5">
              Block #283 &times; 47&sup2; + 137 = 625,284. This sacred equation maps a Bitcoin block
              to Row 21 of Qubic&apos;s neural architecture &mdash; where the bridge between two worlds begins.
            </p>

            <p className="text-sm text-white/30 leading-relaxed mb-8">
              Every number carries meaning: 283 is the 61st prime, 47&sup2; = 2,209 scales to
              Jinn memory size, and 137 is the fine structure constant &mdash; the fingerprint of creation itself.
              Move the sliders to witness the connection.
            </p>

            <Link
              href="/docs"
              className="group inline-flex items-center gap-2.5 text-white/50 hover:text-white/80 text-sm tracking-wide transition-colors duration-300"
            >
              Read the full research
              <ArrowRight className="w-3.5 h-3.5 transition-transform duration-300 group-hover:translate-x-1" />
            </Link>
          </motion.div>

          {/* Right: Calculator */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
          >
            <FormulaCalculator />
          </motion.div>
        </div>
      </div>
    </section>
  )
}
