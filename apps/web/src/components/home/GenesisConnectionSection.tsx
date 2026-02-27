'use client'

import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { ArrowRight, Binary, Calendar, Hash, Layers } from 'lucide-react'
import { BitcoinLogoSVG, QubicLogoSVG } from '@/components/logos'

export function GenesisConnectionSection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })

  return (
    <section ref={sectionRef} className="py-20 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-2xl md:text-3xl font-semibold mb-4">
            Genesis Connections
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Mathematical patterns linking the origins of Bitcoin and Qubic suggest
            intentional design rather than coincidence.
          </p>
        </motion.div>

        {/* Split View: Bitcoin | Qubic */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Bitcoin Genesis */}
          <motion.div
            className="p-6 bg-gradient-to-b from-[#050505] to-[#050505]/80 border border-white/[0.04]"
            initial={{ opacity: 0, x: -30 }}
            animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -30 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="flex items-center gap-3 mb-6">
              <BitcoinLogoSVG size={40} />
              <div>
                <h3 className="text-xl font-semibold">Bitcoin Genesis</h3>
                <p className="text-sm text-muted-foreground">Block #0 - January 3, 2009</p>
              </div>
            </div>

            <div className="space-y-4">
              {/* 43 Leading Zeros */}
              <div className="p-4 bg-black/30">
                <div className="flex items-center gap-2 mb-2">
                  <Binary className="h-4 w-4 text-[#D4AF37]" />
                  <span className="text-sm font-medium">Genesis Block Hash</span>
                </div>
                <div className="font-mono text-xs break-all text-muted-foreground mb-2">
                  000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[#D4AF37] font-bold text-2xl">43</span>
                  <span className="text-sm text-muted-foreground">leading zero bits</span>
                </div>
                <div className="mt-2 p-2  bg-[#D4AF37]/10 text-xs">
                  <strong className="text-[#D4AF37]">43</strong> = CFB constant (Come-From-Beyond)
                </div>
              </div>

              {/* Genesis Message */}
              <div className="p-4 bg-black/30">
                <div className="flex items-center gap-2 mb-2">
                  <Hash className="h-4 w-4 text-[#D4AF37]" />
                  <span className="text-sm font-medium">Coinbase Message</span>
                </div>
                <p className="text-sm italic text-[#D4AF37]/80">
                  "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks"
                </p>
                <div className="text-xs text-muted-foreground mt-2">
                  Embedded in the genesis block - proof of date and political statement
                </div>
              </div>

              {/* Timeline */}
              <div className="p-4 bg-black/30">
                <div className="flex items-center gap-2 mb-2">
                  <Calendar className="h-4 w-4 text-[#D4AF37]" />
                  <span className="text-sm font-medium">Timeline</span>
                </div>
                <div className="text-sm text-muted-foreground">
                  <div>Genesis: January 3, 2009</div>
                  <div>Block #283: January 12, 2009</div>
                  <div>1CFB Address: January 13, 2009</div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Qubic Genesis */}
          <motion.div
            className="p-6 bg-gradient-to-b from-[#050505] to-[#050505]/80 border border-white/[0.04]"
            initial={{ opacity: 0, x: 30 }}
            animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 30 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="flex items-center gap-3 mb-6">
              <QubicLogoSVG size={40} />
              <div>
                <h3 className="text-xl font-semibold">Qubic Genesis</h3>
                <p className="text-sm text-muted-foreground">First Epoch - April 2024</p>
              </div>
            </div>

            <div className="space-y-4">
              {/* Network Stats */}
              <div className="p-4 bg-black/30">
                <div className="flex items-center gap-2 mb-2">
                  <Layers className="h-4 w-4 text-[#D4AF37]" />
                  <span className="text-sm font-medium">Network Architecture</span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <div className="text-[#D4AF37] font-bold text-2xl">23,477</div>
                    <div className="text-xs text-muted-foreground">verified identities</div>
                  </div>
                  <div>
                    <div className="text-[#D4AF37] font-bold text-2xl">676</div>
                    <div className="text-xs text-muted-foreground">computors</div>
                  </div>
                </div>
              </div>

              {/* Jinn Matrix */}
              <div className="p-4 bg-black/30">
                <div className="flex items-center gap-2 mb-2">
                  <Binary className="h-4 w-4 text-[#D4AF37]" />
                  <span className="text-sm font-medium">Jinn Memory Matrix</span>
                </div>
                <div className="font-mono text-center py-2">
                  <span className="text-[#D4AF37] text-xl">128 × 128</span>
                  <span className="text-muted-foreground"> = </span>
                  <span className="text-white text-xl">16,384</span>
                  <span className="text-muted-foreground text-sm"> addresses</span>
                </div>
                <div className="text-xs text-muted-foreground text-center mt-1">
                  Ternary computing architecture
                </div>
              </div>

              {/* The Formula */}
              <div className="p-4 bg-black/30">
                <div className="flex items-center gap-2 mb-2">
                  <Hash className="h-4 w-4 text-[#D4AF37]" />
                  <span className="text-sm font-medium">The Formula</span>
                </div>
                <div className="font-mono text-center text-lg">
                  <span className="text-[#D4AF37]">625,284</span>
                  <span className="text-muted-foreground"> = </span>
                  <span className="text-[#D4AF37]">283</span>
                  <span className="text-muted-foreground"> × 47² + </span>
                  <span className="text-[#D4AF37]">137</span>
                </div>
                <div className="text-xs text-muted-foreground text-center mt-2">
                  Connects Block #283 to Qubic memory position
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Connection Bridge */}
        <motion.div
          className="p-6 bg-gradient-to-r from-[#050505] via-[#050505] to-[#050505] border border-border"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <h3 className="text-center font-semibold mb-6">The Mathematical Bridge</h3>

          <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8">
            {/* Bitcoin Block #283 */}
            <div className="text-center">
              <BitcoinLogoSVG size={32} className="mx-auto mb-2" />
              <div className="text-sm text-muted-foreground">Block</div>
              <div className="text-2xl font-mono font-bold text-[#D4AF37]">#283</div>
              <div className="text-xs text-muted-foreground">Jan 12, 2009</div>
            </div>

            {/* Arrow */}
            <div className="flex items-center gap-2 text-muted-foreground">
              <div className="hidden md:block w-16 h-px bg-gradient-to-r from-[#D4AF37]/50 to-[#D4AF37]/30"></div>
              <ArrowRight className="h-6 w-6" />
              <div className="hidden md:block w-16 h-px bg-gradient-to-r from-[#D4AF37]/30 to-[#D4AF37]/30"></div>
            </div>

            {/* Formula */}
            <div className="text-center p-4 bg-black/30">
              <div className="text-xs text-muted-foreground mb-1">Transform</div>
              <div className="font-mono text-lg">
                <span className="text-[#D4AF37]">283</span>
                <span className="text-muted-foreground"> × </span>
                <span className="text-white">47²</span>
                <span className="text-muted-foreground"> + </span>
                <span className="text-[#D4AF37]">137</span>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex items-center gap-2 text-muted-foreground">
              <div className="hidden md:block w-16 h-px bg-gradient-to-r from-[#D4AF37]/30 to-[#D4AF37]/30"></div>
              <ArrowRight className="h-6 w-6" />
              <div className="hidden md:block w-16 h-px bg-gradient-to-r from-[#D4AF37]/30 to-[#D4AF37]/30"></div>
            </div>

            {/* Qubic Position */}
            <div className="text-center">
              <QubicLogoSVG size={32} className="mx-auto mb-2" />
              <div className="text-sm text-muted-foreground">Position</div>
              <div className="text-2xl font-mono font-bold text-[#D4AF37]">625,284</div>
              <div className="text-xs text-muted-foreground">Memory Address</div>
            </div>
          </div>

          <div className="mt-6 text-center text-sm text-muted-foreground">
            <strong>Constants used:</strong>{' '}
            <span className="text-[#D4AF37]">283</span> (prime, Bitcoin block),{' '}
            <span className="text-white">47</span> (prime),{' '}
            <span className="text-[#D4AF37]">137</span> (fine structure constant)
          </div>
        </motion.div>

        {/* Research Integrity Notice */}
        <motion.div
          className="mt-6 p-4 bg-card/50 border border-border text-center"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 0.5 }}
        >
          <p className="text-xs text-muted-foreground">
            <strong>Verification:</strong> Bitcoin genesis block data can be verified on any blockchain explorer.
            Qubic network statistics are available through the official Qubic API. The formula produces
            exact integer results with no rounding.
          </p>
        </motion.div>
      </div>
    </section>
  )
}
