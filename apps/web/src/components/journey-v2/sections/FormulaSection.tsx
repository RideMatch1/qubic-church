'use client'

import { useRef, useState, useEffect } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { JourneySection } from '../JourneySection'
import { Calculator, CheckCircle, XCircle, Lightbulb, Zap, HelpCircle, ExternalLink } from 'lucide-react'
import { useGamificationSafe } from '@/components/gamification/GamificationProvider'

export function FormulaSection() {
  const contentRef = useRef(null)
  const isInView = useInView(contentRef, { once: false, amount: 0.2 })
  const [blockInput, setBlockInput] = useState('')
  const [verificationResult, setVerificationResult] = useState<'correct' | 'incorrect' | null>(null)
  const [showFormula, setShowFormula] = useState(false)
  const [formulaStep, setFormulaStep] = useState(0)
  const [attemptCount, setAttemptCount] = useState(0)
  const [hasTriggeredDiscovery, setHasTriggeredDiscovery] = useState(false)

  // Gamification
  const gamification = useGamificationSafe()

  // Animate formula reveal
  useEffect(() => {
    if (isInView) {
      const timer1 = setTimeout(() => setShowFormula(true), 1000)
      const timer2 = setTimeout(() => setFormulaStep(1), 1500)
      const timer3 = setTimeout(() => setFormulaStep(2), 2000)
      const timer4 = setTimeout(() => setFormulaStep(3), 2500)
      return () => {
        clearTimeout(timer1)
        clearTimeout(timer2)
        clearTimeout(timer3)
        clearTimeout(timer4)
      }
    } else {
      setShowFormula(false)
      setFormulaStep(0)
    }
  }, [isInView])

  // Trigger discovery when formula fully reveals
  useEffect(() => {
    if (formulaStep >= 3 && !hasTriggeredDiscovery && gamification) {
      gamification.viewDiscovery('formula-625284')
      setHasTriggeredDiscovery(true)
    }
  }, [formulaStep, hasTriggeredDiscovery, gamification])

  const handleVerify = () => {
    const blockNum = parseInt(blockInput, 10)
    const newAttemptCount = attemptCount + 1
    setAttemptCount(newAttemptCount)

    if (blockNum === 283) {
      setVerificationResult('correct')

      // Trigger gamification achievements
      if (gamification) {
        // Core achievements
        gamification.verifyProof('formula-283')
        gamification.unlockAchievement('formula-verified')
        gamification.completeTool('formula-calculator')

        // Perfect formula - first try correct
        if (newAttemptCount === 1) {
          gamification.unlockAchievement('perfect-formula')
        }
      }
    } else {
      setVerificationResult('incorrect')
    }
  }

  return (
    <JourneySection id="formula" background="transparent" className="flex items-center justify-center py-12 md:py-20">
      <div ref={contentRef} className="relative z-10 w-full max-w-4xl mx-auto px-4">
        {/* Chapter & Story Intro */}
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
              CHAPTER 2
            </span>
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-bold text-white/90 mb-6">
            The Hidden Equation
          </h2>

          {/* Story context */}
          <motion.div
            className="max-w-2xl mx-auto space-y-4 mb-8"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <p className="text-lg text-white/50 leading-relaxed">
              Fast forward <span className="text-white/70 font-medium">15 years</span>.
              A new blockchain project called <span className="text-white/70 font-medium">Qubic</span> launches.
            </p>
            <p className="text-base text-white/40 leading-relaxed">
              Qubic is a quantum-resistant computing network —
              but hidden within its code is something extraordinary...
            </p>
          </motion.div>

          {/* What is Qubic - Quick explainer */}
          <motion.div
            className="inline-flex items-start gap-3 px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-left max-w-md mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: isInView ? 1 : 0 }}
            transition={{ delay: 0.6 }}
          >
            <HelpCircle className="h-5 w-5 text-white/40 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-white/60 font-medium mb-1">What is Qubic?</p>
              <p className="text-xs text-white/40 leading-relaxed">
                A futuristic computing network that stores data in a 128×128 grid.
                Think of it like a giant spreadsheet with 16,384 cells.
              </p>
            </div>
          </motion.div>
        </motion.div>

        {/* The Discovery Story */}
        <motion.div
          className="p-6 md:p-8 rounded-2xl bg-gradient-to-b from-purple-950/30 to-black/50 border border-purple-900/30 mb-8 relative overflow-hidden"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 30 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          {/* Lightbulb icon */}
          <div className="absolute top-4 right-4 opacity-10">
            <Lightbulb className="w-16 h-16 text-purple-500" />
          </div>

          <div className="flex items-center gap-2 mb-6">
            <Zap className="h-4 w-4 text-purple-400" />
            <span className="text-sm text-purple-400/80 font-medium">The Discovery</span>
          </div>

          <p className="text-white/60 mb-6 leading-relaxed">
            Researchers noticed something strange: a specific cell in Qubic's memory grid
            (position <span className="text-purple-400 font-mono font-bold">625,284</span>)
            seemed to connect back to Bitcoin's earliest days...
          </p>

          {/* Formula Reveal with Animation */}
          <AnimatePresence>
            {showFormula && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-6 bg-black/40 rounded-xl mb-6"
              >
                <p className="text-sm text-white/40 text-center mb-4">The equation that connects them:</p>
                <div className="flex flex-wrap items-center justify-center gap-2 md:gap-4 font-mono text-2xl md:text-4xl">
                  <motion.span
                    className="text-purple-400 font-bold relative"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: formulaStep >= 0 ? 1 : 0, y: formulaStep >= 0 ? 0 : 20 }}
                  >
                    625,284
                    {formulaStep >= 0 && (
                      <motion.span
                        className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs text-purple-400/60 whitespace-nowrap"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                      >
                        Qubic Position
                      </motion.span>
                    )}
                  </motion.span>

                  <motion.span
                    className="text-white/50"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: formulaStep >= 1 ? 1 : 0 }}
                  >
                    =
                  </motion.span>

                  <motion.span
                    className="text-orange-400 font-bold relative"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: formulaStep >= 1 ? 1 : 0, y: formulaStep >= 1 ? 0 : 20 }}
                  >
                    283
                    {formulaStep >= 1 && (
                      <motion.span
                        className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs text-orange-400/60 whitespace-nowrap"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                      >
                        Bitcoin Block
                      </motion.span>
                    )}
                  </motion.span>

                  <motion.span
                    className="text-white/50"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: formulaStep >= 2 ? 1 : 0 }}
                  >
                    ×
                  </motion.span>

                  <motion.span
                    className="text-white font-bold"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: formulaStep >= 2 ? 1 : 0, y: formulaStep >= 2 ? 0 : 20 }}
                  >
                    47²
                  </motion.span>

                  <motion.span
                    className="text-white/50"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: formulaStep >= 3 ? 1 : 0 }}
                  >
                    +
                  </motion.span>

                  <motion.span
                    className="text-green-400 font-bold relative"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: formulaStep >= 3 ? 1 : 0, y: formulaStep >= 3 ? 0 : 20 }}
                  >
                    137
                    {formulaStep >= 3 && (
                      <motion.span
                        className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs text-green-400/60 whitespace-nowrap"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                      >
                        Physics Constant
                      </motion.span>
                    )}
                  </motion.span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Step by step calculation */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: isInView && formulaStep >= 3 ? 1 : 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <div className="p-3 rounded-lg bg-black/30 text-center">
              <div className="text-xs text-white/40 mb-1">Step 1: 47² =</div>
              <div className="font-mono text-lg text-white">2,209</div>
            </div>
            <div className="p-3 rounded-lg bg-black/30 text-center">
              <div className="text-xs text-white/40 mb-1">Step 2: 283 × 2,209 =</div>
              <div className="font-mono text-lg text-white">625,147</div>
            </div>
            <div className="p-3 rounded-lg bg-black/30 text-center">
              <div className="text-xs text-white/40 mb-1">Step 3: 625,147 + 137 =</div>
              <div className="font-mono text-lg text-purple-400">625,284</div>
            </div>
          </motion.div>

          {/* The revelation */}
          <motion.p
            className="text-center text-white/50 text-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: isInView && formulaStep >= 3 ? 1 : 0 }}
            transition={{ delay: 0.8 }}
          >
            Block #283 was mined on <span className="text-orange-400">January 12, 2009</span> —
            just <span className="text-white/70">9 days</span> after Bitcoin's genesis.
          </motion.p>
        </motion.div>

        {/* Interactive Calculator */}
        <motion.div
          className="p-6 rounded-2xl bg-white/5 border border-white/10 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.6, delay: 1.2 }}
        >
          <div className="flex items-center gap-2 mb-4">
            <Calculator className="h-5 w-5 text-white/40" />
            <h3 className="font-semibold text-white/80">Try It Yourself</h3>
          </div>

          <p className="text-sm text-white/40 mb-4">
            Which Bitcoin block number produces <span className="text-purple-400 font-mono">625,284</span> using the formula <span className="font-mono text-white/60">n × 47² + 137</span>?
          </p>

          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="number"
              value={blockInput}
              onChange={(e) => {
                setBlockInput(e.target.value)
                setVerificationResult(null)
              }}
              placeholder="Enter a block number..."
              className="flex-1 px-4 py-3 rounded-lg bg-black/40 border border-white/10 text-white placeholder:text-white/50 font-mono focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 transition-colors"
              aria-label="Bitcoin block number"
              aria-describedby="formula-hint"
            />
            <button
              onClick={handleVerify}
              disabled={!blockInput}
              className="px-6 py-3 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-purple-400 font-medium"
            >
              Calculate
            </button>
          </div>

          <AnimatePresence>
            {verificationResult && (
              <motion.div
                className={`mt-4 p-4 rounded-lg flex items-center gap-3 ${
                  verificationResult === 'correct'
                    ? 'bg-green-500/10 border border-green-500/30'
                    : 'bg-orange-500/10 border border-orange-500/30'
                }`}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
              >
                {verificationResult === 'correct' ? (
                  <>
                    <CheckCircle className="h-5 w-5 text-green-400 shrink-0" />
                    <div>
                      <div className="font-medium text-green-400">Correct!</div>
                      <div className="text-sm text-green-400/70">283 × 2,209 + 137 = 625,284</div>
                    </div>
                  </>
                ) : (
                  <>
                    <XCircle className="h-5 w-5 text-orange-400 shrink-0" />
                    <div>
                      <div className="font-medium text-orange-400">Not quite — but you can see the math:</div>
                      <div className="text-sm text-orange-400/70">
                        {blockInput} × 2,209 + 137 = <span className="font-mono">{parseInt(blockInput || '0', 10) * 2209 + 137}</span>
                      </div>
                    </div>
                  </>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Why these numbers? */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ duration: 0.6, delay: 1.4 }}
        >
          <div className="p-5 rounded-xl bg-orange-500/5 border border-orange-500/20">
            <div className="text-3xl font-mono font-bold text-orange-400 mb-2">283</div>
            <div className="text-sm text-white/60 font-medium mb-1">Prime Number</div>
            <p className="text-xs text-white/40 leading-relaxed">
              Bitcoin Block #283, mined January 12, 2009 — one of Bitcoin's first blocks
            </p>
          </div>
          <div className="p-5 rounded-xl bg-white/5 border border-white/20">
            <div className="text-3xl font-mono font-bold text-white mb-2">47</div>
            <div className="text-sm text-white/60 font-medium mb-1">Prime Number</div>
            <p className="text-xs text-white/40 leading-relaxed">
              Squared (47² = 2,209) to create the multiplier in the formula
            </p>
          </div>
          <div className="p-5 rounded-xl bg-green-500/5 border border-green-500/20">
            <div className="text-3xl font-mono font-bold text-green-400 mb-2">137</div>
            <div className="text-sm text-white/60 font-medium mb-1">Fine Structure Constant</div>
            <p className="text-xs text-white/40 leading-relaxed mb-2">
              α⁻¹ ≈ 137 — a fundamental constant in physics that governs electromagnetic interactions
            </p>
            <a
              href="https://en.wikipedia.org/wiki/Fine-structure_constant"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-green-400 hover:text-green-300 transition-colors"
            >
              Learn more on Wikipedia <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </motion.div>

        {/* Transition to next section */}
        <motion.div
          className="mt-10 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 1.6 }}
        >
          <p className="text-sm text-white/50 italic">
            "Coincidence? Let's look deeper into the blockchain..."
          </p>
        </motion.div>
      </div>
    </JourneySection>
  )
}
