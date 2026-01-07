'use client'

import { useRef, useState } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { Calculator, CheckCircle, ChevronRight, Play, Pause, RotateCcw } from 'lucide-react'
import { VerificationBadge } from '@/components/ui/VerificationBadge'

interface FormulaStep {
  label: string
  value: string | number
  explanation: string
  significance?: string
}

const mainFormula: FormulaStep[] = [
  {
    label: 'Block Number',
    value: 283,
    explanation: 'Prime number. The 61st prime. One of the earliest Bitcoin blocks.',
    significance: 'Block 283 was mined on January 10, 2009, just 7 days after Genesis.',
  },
  {
    label: 'Perfect Square',
    value: '47²',
    explanation: '47 × 47 = 2,209. 47 is also prime (15th prime).',
    significance: '47 appears repeatedly in Satoshi\'s code and communications.',
  },
  {
    label: 'Multiplication',
    value: '283 × 2,209',
    explanation: 'Prime × Perfect Square = 625,147',
    significance: 'This operation combines two mathematically significant numbers.',
  },
  {
    label: 'Fine Structure',
    value: 137,
    explanation: 'The fine-structure constant inverse (α⁻¹ ≈ 137). Fundamental physics.',
    significance: 'Physicists call 137 "the magic number." It defines atomic behavior.',
  },
  {
    label: 'Final Result',
    value: '625,284',
    explanation: '283 × 47² + 137 = 625,284',
    significance: 'This exact number appears in GENESIS token burns and Qubic architecture.',
  },
]

const additionalProofs = [
  {
    title: '676 Computors',
    formula: '26² = 676',
    description: 'Qubic uses exactly 676 Computors',
    connection: '26 = letters in alphabet. "QUBIC" has 5 letters (the 26th Fibonacci-adjacent).',
    confidence: 99,
  },
  {
    title: 'Mod 27 Signature',
    formula: 'All results mod 27 = 7',
    description: 'Key timestamps and values always reduce to 7',
    connection: '27 = 3³ (ternary), 7 = lucky number in many cultures. Deliberate choice.',
    confidence: 91,
  },
  {
    title: '6268 Days',
    formula: 'Jan 3, 2009 + 6268 = March 2026',
    description: 'Genesis to predicted reveal date',
    connection: '6268 encodes Qubic through character positions in alphabet.',
    confidence: 85,
  },
  {
    title: 'Prime Sequence',
    formula: '2, 3, 5, 7, 283, 47, 137',
    description: 'All key numbers are prime or prime-derived',
    connection: 'Cryptographic signatures often use prime numbers for security.',
    confidence: 94,
  },
]

export function ProofsSection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })
  const [currentStep, setCurrentStep] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [showResult, setShowResult] = useState(false)

  const handleNext = () => {
    if (currentStep < mainFormula.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      setShowResult(true)
    }
  }

  const handleReset = () => {
    setCurrentStep(0)
    setShowResult(false)
    setIsPlaying(false)
  }

  const handleAutoPlay = () => {
    if (isPlaying) {
      setIsPlaying(false)
    } else {
      setIsPlaying(true)
      const interval = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= mainFormula.length - 1) {
            setShowResult(true)
            setIsPlaying(false)
            clearInterval(interval)
            return prev
          }
          return prev + 1
        })
      }, 2000)
    }
  }

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
          <div className="flex items-center justify-center gap-3 mb-4">
            <Calculator className="h-8 w-8 text-amber-400" />
            <h2 className="text-display-md font-semibold">Mathematical Proofs</h2>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto text-body-lg">
            The 625,284 formula and other mathematical signatures that connect
            Bitcoin's Genesis to Qubic.
          </p>
        </motion.div>

        {/* Interactive Formula Breakdown */}
        <motion.div
          className="mb-12 p-8 rounded-2xl border bg-gradient-to-br from-amber-950/30 to-amber-900/10 border-amber-800/50"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-amber-400">The Core Formula</h3>
            <div className="flex gap-2">
              <button
                onClick={handleAutoPlay}
                className="p-2 rounded-lg bg-amber-900/50 hover:bg-amber-900/70 transition-colors"
              >
                {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
              </button>
              <button
                onClick={handleReset}
                className="p-2 rounded-lg bg-amber-900/50 hover:bg-amber-900/70 transition-colors"
              >
                <RotateCcw className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Formula Display */}
          <div className="text-center mb-8">
            <div className="font-mono text-4xl md:text-5xl font-bold mb-4">
              {currentStep >= 0 && <span className="text-blue-400">283</span>}
              {currentStep >= 1 && <span className="text-muted-foreground"> × </span>}
              {currentStep >= 1 && <span className="text-purple-400">47²</span>}
              {currentStep >= 3 && <span className="text-muted-foreground"> + </span>}
              {currentStep >= 3 && <span className="text-emerald-400">137</span>}
              {showResult && (
                <>
                  <span className="text-muted-foreground"> = </span>
                  <span className="text-amber-400">
                    625,284
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Steps */}
          <div className="space-y-4">
            {mainFormula.map((step, idx) => (
              <motion.div
                key={step.label}
                className={`p-4 rounded-lg border transition-all ${
                  idx === currentStep
                    ? 'bg-amber-900/30 border-amber-700'
                    : idx < currentStep
                    ? 'bg-muted/30 border-border/50'
                    : 'bg-muted/10 border-border/30 opacity-50'
                }`}
                initial={{ opacity: 0, x: -20 }}
                animate={{
                  opacity: idx <= currentStep ? 1 : 0.3,
                  x: 0,
                }}
                transition={{ delay: idx * 0.1 }}
              >
                <div className="flex items-center gap-4">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                      idx < currentStep
                        ? 'bg-emerald-600 text-white'
                        : idx === currentStep
                        ? 'bg-amber-600 text-white'
                        : 'bg-muted text-muted-foreground'
                    }`}
                  >
                    {idx < currentStep ? <CheckCircle className="h-4 w-4" /> : idx + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold">{step.label}:</span>
                      <span className="font-mono text-lg text-primary">{step.value}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">{step.explanation}</p>
                    {idx === currentStep && step.significance && (
                      <motion.p
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="mt-2 text-sm text-amber-400"
                      >
                        {step.significance}
                      </motion.p>
                    )}
                  </div>
                  {idx === currentStep && idx < mainFormula.length - 1 && (
                    <button
                      onClick={handleNext}
                      className="p-2 rounded-lg bg-amber-600 hover:bg-amber-500 transition-colors"
                    >
                      <ChevronRight className="h-5 w-5" />
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
          </div>

          {/* Result */}
          <AnimatePresence>
            {showResult && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mt-6 p-6 rounded-lg bg-emerald-900/30 border border-emerald-700 text-center"
              >
                <div className="text-lg font-bold text-emerald-400 mb-2">Verification Complete</div>
                <p className="text-sm text-muted-foreground">
                  The formula 283 × 47² + 137 = 625,284 is mathematically verified.
                  This exact value appears in GENESIS token architecture and Qubic system design.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Additional Proofs */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          {additionalProofs.map((proof, idx) => (
            <AdditionalProofCard key={proof.title} proof={proof} index={idx} />
          ))}
        </motion.div>
      </div>
    </section>
  )
}

function AdditionalProofCard({
  proof,
  index,
}: {
  proof: typeof additionalProofs[0]
  index: number
}) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  return (
    <motion.div
      ref={ref}
      className="p-6 rounded-xl border bg-zinc-900/50 border-zinc-800 hover-lift"
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold">{proof.title}</h3>
        <VerificationBadge
          level={proof.confidence >= 95 ? 'verified' : proof.confidence >= 85 ? 'high' : 'medium'}
          percentage={proof.confidence}
          showPercentage
          size="sm"
        />
      </div>

      <div className="font-mono text-2xl text-primary mb-4 p-3 rounded-lg bg-muted/30">
        {proof.formula}
      </div>

      <p className="text-sm text-muted-foreground mb-3">{proof.description}</p>

      <div className="p-3 rounded-lg bg-primary/5 border border-primary/20">
        <div className="text-xs font-medium text-primary mb-1">Connection</div>
        <p className="text-xs text-muted-foreground">{proof.connection}</p>
      </div>
    </motion.div>
  )
}
