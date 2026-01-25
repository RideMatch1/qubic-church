'use client'

import { useRef, useState, useEffect } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { JourneySection } from '../JourneySection'
import { Database, Gift, Lock, Shield, HelpCircle, Eye, TrendingUp, ExternalLink } from 'lucide-react'
import { BitcoinLogoSVG } from '@/components/logos'

export function PatoshiSection() {
  const contentRef = useRef(null)
  const isInView = useInView(contentRef, { once: false, amount: 0.2 })
  const [revealStep, setRevealStep] = useState(0)
  const [showMiningViz, setShowMiningViz] = useState(false)

  // Staggered reveal animation
  useEffect(() => {
    if (isInView) {
      const timers = [
        setTimeout(() => setRevealStep(1), 500),
        setTimeout(() => setRevealStep(2), 1000),
        setTimeout(() => setRevealStep(3), 1500),
        setTimeout(() => setShowMiningViz(true), 2000),
      ]
      return () => timers.forEach(clearTimeout)
    } else {
      setRevealStep(0)
      setShowMiningViz(false)
    }
  }, [isInView])

  return (
    <JourneySection id="patoshi" background="transparent" className="flex items-center justify-center py-12 md:py-20">
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
              CHAPTER 3
            </span>
          </motion.div>

          <motion.div
            className="flex items-center justify-center gap-3 mb-4"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0.9 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <BitcoinLogoSVG size={48} />
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-bold text-white/90 mb-6">
            The Phantom Miner
          </h2>

          {/* Story context for beginners */}
          <motion.div
            className="max-w-2xl mx-auto space-y-4 mb-8"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <p className="text-lg text-white/50 leading-relaxed">
              In Bitcoin's earliest days, someone was quietly mining{' '}
              <span className="text-white/70 font-medium">22,000 blocks</span>.
              Researchers call this entity <span className="text-white/70 font-medium">"Patoshi"</span>.
            </p>
            <p className="text-base text-white/40 leading-relaxed">
              These coins — worth <span className="text-white/60">billions of dollars today</span> —
              have <span className="text-green-400">never been moved</span>. Not once. In 17 years.
            </p>
          </motion.div>

          {/* What is Mining - Quick explainer */}
          <motion.div
            className="inline-flex items-start gap-3 px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-left max-w-md mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: isInView ? 1 : 0 }}
            transition={{ delay: 0.6 }}
          >
            <HelpCircle className="h-5 w-5 text-white/40 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-white/60 font-medium mb-1">What is Bitcoin Mining?</p>
              <p className="text-xs text-white/40 leading-relaxed">
                Special computers solve math puzzles to add new transactions to Bitcoin.
                As a reward, miners receive newly created Bitcoin — 50 BTC per block in 2009.
              </p>
            </div>
          </motion.div>
        </motion.div>

        {/* The Discovery - Animated reveal */}
        <motion.div
          className="p-6 md:p-8 rounded-2xl bg-gradient-to-b from-orange-950/30 to-black/50 border border-orange-900/30 mb-8 relative overflow-hidden"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 30 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          {/* Background icon */}
          <div className="absolute top-4 right-4 opacity-10">
            <Eye className="w-16 h-16 text-orange-500" />
          </div>

          <div className="flex items-center gap-2 mb-6">
            <Database className="h-4 w-4 text-orange-400" />
            <span className="text-sm text-orange-400/80 font-medium">The Forensic Discovery</span>
          </div>

          <p className="text-white/60 mb-6 leading-relaxed">
            In <span className="text-orange-400">2013</span>, researcher{' '}
            <a
              href="https://bitslog.com/2013/04/17/the-well-deserved-fortune-of-satoshi-nakamoto/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-white/80 font-medium hover:text-orange-400 transition-colors inline-flex items-center gap-1"
            >
              Sergio Demian Lerner <ExternalLink className="h-3 w-3" />
            </a> discovered
            a unique pattern in Bitcoin's early mining data...
          </p>

          {/* Mining Visualization */}
          <AnimatePresence>
            {showMiningViz && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-6 bg-black/40 rounded-xl mb-6"
              >
                <p className="text-sm text-white/40 text-center mb-4">The Patoshi Mining Pattern:</p>

                {/* Animated mining blocks */}
                <div className="flex flex-wrap justify-center gap-1 mb-4">
                  {Array.from({ length: 40 }, (_, i) => (
                    <motion.div
                      key={i}
                      className={`w-3 h-3 rounded-sm ${
                        i % 5 === 0 ? 'bg-orange-500' : 'bg-white/10'
                      }`}
                      initial={{ opacity: 0, scale: 0 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.03 }}
                    />
                  ))}
                </div>

                <div className="flex items-center justify-center gap-6 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-sm bg-orange-500" />
                    <span className="text-white/40">Patoshi blocks</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-sm bg-white/10" />
                    <span className="text-white/40">Other miners</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <p className="text-sm text-white/50 text-center">
            The pattern shows one entity (Patoshi) was mining with a{' '}
            <span className="text-orange-400">distinctive fingerprint</span> —
            likely <span className="text-white/70">Satoshi Nakamoto himself</span>.
          </p>
        </motion.div>

        {/* Stats - Dramatic reveal */}
        <motion.div
          className="grid grid-cols-3 gap-4 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.6, delay: 1 }}
        >
          <motion.div
            className="text-center p-4 rounded-xl bg-orange-500/10 border border-orange-500/20 relative overflow-hidden"
            whileHover={{ scale: 1.02 }}
          >
            <motion.div
              className="absolute inset-0 bg-orange-500/5"
              animate={{ opacity: [0, 0.5, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <div className="text-2xl md:text-3xl font-mono font-bold text-orange-400">21,953</div>
            <div className="text-xs text-white/40">Patoshi blocks mined</div>
          </motion.div>

          <motion.div
            className="text-center p-4 rounded-xl bg-orange-500/10 border border-orange-500/20"
            whileHover={{ scale: 1.02 }}
          >
            <div className="text-2xl md:text-3xl font-mono font-bold text-orange-400">~1.1M</div>
            <div className="text-xs text-white/40">BTC attributed</div>
            <div className="text-[10px] text-white/50 mt-1">≈ $70+ billion today</div>
          </motion.div>

          <motion.div
            className="text-center p-4 rounded-xl bg-green-500/10 border border-green-500/20"
            whileHover={{ scale: 1.02 }}
          >
            <div className="text-2xl md:text-3xl font-mono font-bold text-green-400">0</div>
            <div className="text-xs text-white/40">Coins ever moved</div>
            <div className="text-[10px] text-white/50 mt-1">17 years dormant</div>
          </motion.div>
        </motion.div>

        {/* The Connection to Block #283 */}
        <motion.div
          className="p-6 rounded-xl bg-gradient-to-r from-orange-950/20 via-purple-950/20 to-orange-950/20 border border-white/10 mb-8"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 30 }}
          transition={{ duration: 0.5, delay: 1.2 }}
        >
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="h-4 w-4 text-purple-400" />
            <span className="text-sm text-purple-400/80 font-medium">The Connection</span>
          </div>

          <p className="text-white/60 mb-4 leading-relaxed">
            Remember <span className="text-orange-400 font-mono font-bold">Block #283</span> from the formula?
            It's one of the <span className="text-white/80">Patoshi blocks</span>.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-black/30">
              <div className="text-xs text-white/40 mb-1">Block #283 Details</div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-white/50">Date:</span>
                  <span className="text-orange-400 font-mono">Jan 12, 2009</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-white/50">Reward:</span>
                  <span className="text-orange-400 font-mono">50 BTC</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-white/50">Miner:</span>
                  <span className="text-white/70">Patoshi</span>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-black/30">
              <div className="text-xs text-white/40 mb-1">Today's Value</div>
              <div className="text-2xl font-mono font-bold text-green-400 mb-1">~$2.5M</div>
              <div className="text-xs text-white/50">
                Still sitting untouched at its original address
              </div>
            </div>
          </div>
        </motion.div>

        {/* Key Evidence Points */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 gap-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.6, delay: 1.4 }}
        >
          <div className="p-5 rounded-xl bg-white/5 border border-white/10">
            <div className="flex items-center gap-2 mb-3">
              <Lock className="h-5 w-5 text-orange-400" />
              <h4 className="font-semibold text-white/80">Why Never Moved?</h4>
            </div>
            <p className="text-sm text-white/50 leading-relaxed">
              Either the owner lost access... or they're{' '}
              <span className="text-white/70">waiting for something</span>.
              March 3, 2026 is encoded in the Qubic time-lock.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-white/5 border border-white/10">
            <div className="flex items-center gap-2 mb-3">
              <Shield className="h-5 w-5 text-green-400" />
              <h4 className="font-semibold text-white/80">Verified Data</h4>
            </div>
            <p className="text-sm text-white/50 leading-relaxed">
              This isn't speculation — the Patoshi pattern is{' '}
              <span className="text-green-400">cryptographically verifiable</span>{' '}
              by anyone with blockchain access.
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
            "So how does an anonymous 2009 miner connect to a 2024 project?"
          </p>
        </motion.div>
      </div>
    </JourneySection>
  )
}
