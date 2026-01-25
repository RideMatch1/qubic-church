'use client'

import { useRef, useState, useEffect } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { JourneySection } from '../JourneySection'
import { ArrowRight, Binary, Calendar, Hash, Layers, HelpCircle, Link2, Sparkles, ExternalLink } from 'lucide-react'
import { BitcoinLogoSVG, QubicLogoSVG } from '@/components/logos'

export function BridgeSection() {
  const contentRef = useRef(null)
  const isInView = useInView(contentRef, { once: false, amount: 0.2 })
  const [connectionStep, setConnectionStep] = useState(0)
  const [showBridge, setShowBridge] = useState(false)

  // Animated connection reveal
  useEffect(() => {
    if (isInView) {
      const timers = [
        setTimeout(() => setConnectionStep(1), 800),
        setTimeout(() => setConnectionStep(2), 1600),
        setTimeout(() => setShowBridge(true), 2400),
      ]
      return () => timers.forEach(clearTimeout)
    } else {
      setConnectionStep(0)
      setShowBridge(false)
    }
  }, [isInView])

  return (
    <JourneySection id="bridge" background="transparent" className="flex items-center justify-center py-12 md:py-20">
      <div ref={contentRef} className="relative z-10 w-full max-w-5xl mx-auto px-4">
        {/* Chapter Header */}
        <motion.div
          className="text-center mb-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0.9 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/50 text-xs font-mono">
              CHAPTER 4
            </span>
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-bold text-white/90 mb-6">
            The Mathematical Bridge
          </h2>

          {/* Story context for beginners */}
          <motion.div
            className="max-w-2xl mx-auto space-y-4 mb-8"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <p className="text-lg text-white/50 leading-relaxed">
              Now comes the <span className="text-white/70 font-medium">impossible part</span>:
              how can a project from <span className="text-white/70">2024</span> contain references
              to Bitcoin blocks from <span className="text-white/70">2009</span>?
            </p>
            <p className="text-base text-white/40 leading-relaxed">
              Either it's an incredible <span className="text-white/60">coincidence</span>...
              or someone planned this <span className="text-white/60">15 years in advance</span>.
            </p>
          </motion.div>

          {/* The impossible question */}
          <motion.div
            className="inline-flex items-center gap-3 px-5 py-3 rounded-lg bg-white/5 border border-white/10"
            initial={{ opacity: 0 }}
            animate={{ opacity: isInView ? 1 : 0 }}
            transition={{ delay: 0.6 }}
          >
            <Sparkles className="h-5 w-5 text-white/50" />
            <span className="text-white/60">
              The evidence suggests <span className="text-white/80 font-medium">the same mind</span> created both.
            </span>
          </motion.div>
        </motion.div>

        {/* Split View: Bitcoin | Qubic with animated reveal */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Bitcoin Side */}
          <motion.div
            className={`p-6 rounded-xl bg-gradient-to-b from-orange-950/30 to-black/30 border transition-all duration-500 ${
              connectionStep >= 1 ? 'border-orange-500/40' : 'border-orange-900/30'
            }`}
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: isInView ? 1 : 0, x: isInView ? 0 : -30 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="flex items-center gap-3 mb-6">
              <BitcoinLogoSVG size={40} />
              <div>
                <h3 className="text-xl font-semibold text-white/90">Bitcoin</h3>
                <p className="text-sm text-orange-400/70">Created 2009</p>
              </div>
            </div>

            <div className="space-y-4">
              {/* Key fact 1 */}
              <motion.div
                className="p-4 rounded-lg bg-black/40"
                initial={{ opacity: 0.5 }}
                animate={{ opacity: connectionStep >= 1 ? 1 : 0.5 }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Binary className="h-4 w-4 text-orange-400" />
                  <span className="text-sm font-medium text-white/70">Genesis Block Hash</span>
                </div>
                <div className="font-mono text-xs text-white/50 mb-2 break-all">
                  000000000019d6689c085ae165831e934ff763ae...
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-orange-400 font-bold text-2xl">43</span>
                  <span className="text-sm text-white/40">leading zero bits</span>
                </div>
                <motion.div
                  className="mt-2 p-2 rounded bg-orange-500/10 text-xs space-y-1"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: connectionStep >= 1 ? 1 : 0 }}
                >
                  <div>
                    <span className="text-orange-400 font-bold">43</span>
                    <span className="text-orange-400/70"> = CFB constant</span>
                  </div>
                  <div className="text-white/50">
                    Only <strong>32 bits</strong> were required for difficulty.
                    The extra <strong>11 bits</strong> appear intentional.
                  </div>
                </motion.div>
                <a
                  href="https://blockchair.com/bitcoin/block/0"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-orange-400 hover:text-orange-300 transition-colors mt-2"
                >
                  Verify on blockchain <ExternalLink className="h-3 w-3" />
                </a>
              </motion.div>

              {/* Key fact 2 */}
              <motion.div
                className="p-4 rounded-lg bg-black/40"
                initial={{ opacity: 0.5 }}
                animate={{ opacity: connectionStep >= 1 ? 1 : 0.5 }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Calendar className="h-4 w-4 text-orange-400" />
                  <span className="text-sm font-medium text-white/70">Timeline</span>
                </div>
                <div className="text-sm text-white/40 space-y-1">
                  <div className="flex justify-between">
                    <span>Genesis Block:</span>
                    <span className="text-orange-400">Jan 3, 2009</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Block #283:</span>
                    <span className="text-orange-400">Jan 12, 2009</span>
                  </div>
                  <div className="flex justify-between">
                    <span>1CFB Address:</span>
                    <span className="text-orange-400">Jan 13, 2009</span>
                  </div>
                </div>
              </motion.div>
            </div>
          </motion.div>

          {/* Qubic Side */}
          <motion.div
            className={`p-6 rounded-xl bg-gradient-to-b from-purple-950/30 to-black/30 border transition-all duration-500 ${
              connectionStep >= 2 ? 'border-purple-500/40' : 'border-purple-900/30'
            }`}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: isInView ? 1 : 0, x: isInView ? 0 : 30 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="flex items-center gap-3 mb-6">
              <QubicLogoSVG size={40} />
              <div>
                <h3 className="text-xl font-semibold text-white/90">Qubic</h3>
                <p className="text-sm text-purple-400/70">Launched 2024</p>
              </div>
            </div>

            <div className="space-y-4">
              {/* What is Qubic - beginner box */}
              <motion.div
                className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/20"
                initial={{ opacity: 0.5 }}
                animate={{ opacity: connectionStep >= 2 ? 1 : 0.5 }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <HelpCircle className="h-4 w-4 text-purple-400" />
                  <span className="text-sm font-medium text-purple-400/80">What is Qubic?</span>
                </div>
                <p className="text-xs text-white/40 leading-relaxed">
                  A next-generation computing network that uses a 128×128 memory grid.
                  Think of it as a massive spreadsheet where each cell stores data.
                </p>
              </motion.div>

              {/* Key fact */}
              <motion.div
                className="p-4 rounded-lg bg-black/40"
                initial={{ opacity: 0.5 }}
                animate={{ opacity: connectionStep >= 2 ? 1 : 0.5 }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Layers className="h-4 w-4 text-purple-400" />
                  <span className="text-sm font-medium text-white/70">Memory Matrix</span>
                </div>
                <div className="font-mono text-center py-2">
                  <span className="text-purple-400 text-xl">128 × 128</span>
                  <span className="text-white/50"> = </span>
                  <span className="text-white text-xl">16,384</span>
                  <span className="text-white/50 text-sm"> addresses</span>
                </div>
              </motion.div>

              {/* The encoded formula */}
              <motion.div
                className="p-4 rounded-lg bg-black/40"
                initial={{ opacity: 0.5 }}
                animate={{ opacity: connectionStep >= 2 ? 1 : 0.5 }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Hash className="h-4 w-4 text-purple-400" />
                  <span className="text-sm font-medium text-white/70">Position #625,284</span>
                </div>
                <div className="font-mono text-center text-lg">
                  <span className="text-purple-400">625,284</span>
                  <span className="text-white/50"> = </span>
                  <span className="text-orange-400">283</span>
                  <span className="text-white/50"> × 47² + </span>
                  <span className="text-green-400">137</span>
                </div>
                <p className="text-xs text-white/50 text-center mt-2">
                  Points directly to Bitcoin Block #283
                </p>
              </motion.div>
            </div>
          </motion.div>
        </div>

        {/* The Bridge Visualization */}
        <AnimatePresence>
          {showBridge && (
            <motion.div
              className="p-6 md:p-8 rounded-2xl bg-gradient-to-r from-orange-950/20 via-purple-950/30 to-purple-950/20 border border-white/10 mb-8 relative overflow-hidden"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              {/* Background glow */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-orange-500/5 via-purple-500/10 to-purple-500/5"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 3, repeat: Infinity }}
              />

              <div className="relative">
                <div className="flex items-center justify-center gap-2 mb-6">
                  <Link2 className="h-5 w-5 text-white/50" />
                  <h3 className="text-center font-semibold text-white/80">The Connection</h3>
                </div>

                {/* Visual bridge */}
                <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-6">
                  {/* Bitcoin Block #283 */}
                  <motion.div
                    className="text-center p-4 rounded-xl bg-black/30"
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    <BitcoinLogoSVG size={32} className="mx-auto mb-2" />
                    <div className="text-sm text-white/40">Block</div>
                    <div className="text-2xl font-mono font-bold text-orange-400">#283</div>
                    <div className="text-xs text-white/50">Jan 12, 2009</div>
                  </motion.div>

                  {/* Animated connection line */}
                  <div className="flex items-center gap-2">
                    <motion.div
                      className="hidden md:block w-12 h-0.5 bg-gradient-to-r from-orange-500 to-purple-500"
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ delay: 0.4, duration: 0.5 }}
                    />
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.6 }}
                    >
                      <ArrowRight className="h-6 w-6 text-white/50" />
                    </motion.div>
                    <motion.div
                      className="hidden md:block w-12 h-0.5 bg-gradient-to-r from-purple-500 to-purple-500"
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ delay: 0.4, duration: 0.5 }}
                    />
                  </div>

                  {/* Formula Transform */}
                  <motion.div
                    className="text-center p-4 rounded-xl bg-black/30"
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.5 }}
                  >
                    <div className="text-xs text-white/40 mb-2">Transform</div>
                    <div className="font-mono text-lg">
                      <span className="text-orange-400">283</span>
                      <span className="text-white/50"> × </span>
                      <span className="text-white">47²</span>
                      <span className="text-white/50"> + </span>
                      <span className="text-green-400">137</span>
                    </div>
                  </motion.div>

                  {/* Arrow */}
                  <div className="flex items-center gap-2">
                    <motion.div
                      className="hidden md:block w-12 h-0.5 bg-gradient-to-r from-purple-500 to-purple-500"
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ delay: 0.7, duration: 0.5 }}
                    />
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.9 }}
                    >
                      <ArrowRight className="h-6 w-6 text-white/50" />
                    </motion.div>
                    <motion.div
                      className="hidden md:block w-12 h-0.5 bg-purple-500"
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ delay: 0.7, duration: 0.5 }}
                    />
                  </div>

                  {/* Qubic Position */}
                  <motion.div
                    className="text-center p-4 rounded-xl bg-black/30"
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.8 }}
                  >
                    <QubicLogoSVG size={32} className="mx-auto mb-2" />
                    <div className="text-sm text-white/40">Position</div>
                    <div className="text-2xl font-mono font-bold text-purple-400">625,284</div>
                    <div className="text-xs text-white/50">Memory Address</div>
                  </motion.div>
                </div>

                {/* Explanation */}
                <motion.div
                  className="mt-6 text-center"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1.2 }}
                >
                  <p className="text-sm text-white/40">
                    A specific memory position in <span className="text-purple-400">Qubic</span>{' '}
                    mathematically encodes a reference to <span className="text-orange-400">Bitcoin</span> Block #283.
                  </p>
                  <p className="text-xs text-white/50 mt-2">
                    Using primes <span className="text-white/50">283, 47</span> and the physics constant <span className="text-green-400/70">137</span>
                  </p>
                </motion.div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* The implications */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 gap-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.6, delay: 1.4 }}
        >
          <div className="p-5 rounded-xl bg-white/5 border border-white/10">
            <h4 className="font-semibold text-white/80 mb-2">If Coincidence...</h4>
            <p className="text-sm text-white/50 leading-relaxed">
              The probability of these exact numbers aligning by chance is
              <span className="text-orange-400"> astronomically low</span>.
              Multiple primes, physics constants, and Bitcoin references — all random?
            </p>
          </div>

          <div className="p-5 rounded-xl bg-white/5 border border-white/10">
            <h4 className="font-semibold text-white/80 mb-2">If Intentional...</h4>
            <p className="text-sm text-white/50 leading-relaxed">
              It means someone in 2009 was already planning something that
              <span className="text-purple-400"> wouldn't launch until 2024</span>.
              A 15-year masterplan hidden in plain sight.
            </p>
          </div>
        </motion.div>

        {/* Transition hint */}
        <motion.div
          className="mt-10 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 1.6 }}
        >
          <p className="text-sm text-white/50 italic">
            "Let's explore the deeper structure..."
          </p>
        </motion.div>
      </div>
    </JourneySection>
  )
}
