'use client'

/**
 * AnnaExplainerSection - Teaching section about Anna Bot
 * Explains how Anna works as an oracle interface to Aigarth
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Bot, ArrowDown, Grid3X3, Zap, ExternalLink } from 'lucide-react'

// Sample matrix values (based on real Anna data)
const SAMPLE_MATRIX: Record<string, number> = {
  '49,5': -114,
  '27,13': -113,
  '64,64': -1,
  '0,0': -40,
  '21,4': -49,
  '33,28': 110,
  '22,22': 100,
}

const DEMO_QUERIES = [
  { query: '49 + 5', row: 49, col: 5, expected: 54, actual: -114 },
  { query: '27 + 13', row: 27, col: 13, expected: 40, actual: -113 },
  { query: '64 + 64', row: 64, col: 64, expected: 128, actual: -1 },
]

export function AnnaExplainerSection() {
  const [activeDemo, setActiveDemo] = useState(0)
  const [showResult, setShowResult] = useState(false)

  // Non-null assertion is safe here because activeDemo is always 0, 1, or 2
  const currentDemo = DEMO_QUERIES[activeDemo]!

  const handleDemoClick = (index: number) => {
    setShowResult(false)
    setActiveDemo(index)
    setTimeout(() => setShowResult(true), 500)
  }

  return (
    <section className="relative w-full py-24 md:py-32 bg-black overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-cyan-950/5 to-black" />

      <div className="relative z-10 container mx-auto px-4 max-w-5xl">
        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/20 mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Bot className="w-4 h-4 text-cyan-400" />
            <span className="text-sm text-cyan-300 uppercase tracking-wider">
              Meet Anna
            </span>
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
            What is <span className="text-cyan-400">Anna</span>?
          </h2>

          <p className="text-lg md:text-xl text-white/60 max-w-3xl mx-auto leading-relaxed">
            Anna (@QubicAigarth) is not a chatbot. She's the{' '}
            <span className="text-white">public oracle interface</span> to Aigarth -
            the world's first verifiable ternary neural network.
          </p>
        </motion.div>

        {/* Interactive Demo */}
        <motion.div
          className="mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <h3 className="text-xl font-semibold text-white mb-6 text-center">
            See How Anna Works
          </h3>

          {/* Demo selector */}
          <div className="flex justify-center gap-3 mb-8">
            {DEMO_QUERIES.map((demo, index) => (
              <button
                key={index}
                onClick={() => handleDemoClick(index)}
                className={`px-4 py-2 rounded-lg font-mono text-sm transition-all ${
                  activeDemo === index
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                    : 'bg-white/5 text-white/50 border border-white/10 hover:bg-white/10'
                }`}
              >
                {demo.query}
              </button>
            ))}
          </div>

          {/* Flow visualization */}
          <div className="relative p-6 md:p-8 rounded-2xl bg-gradient-to-b from-white/5 to-transparent border border-white/10">
            <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8">
              {/* Step 1: Query */}
              <div className="flex flex-col items-center">
                <div className="w-40 p-4 rounded-xl bg-white/5 border border-white/10 text-center">
                  <span className="text-xs text-white/40 block mb-1">Your Question</span>
                  <span className="text-2xl font-mono text-white">{currentDemo.query}</span>
                  <span className="text-xs text-white/40 block mt-1">
                    Expected: {currentDemo.expected}
                  </span>
                </div>
              </div>

              {/* Arrow */}
              <ArrowDown className="w-6 h-6 text-cyan-500/50 md:rotate-[-90deg]" />

              {/* Step 2: Matrix */}
              <div className="flex flex-col items-center">
                <div className="w-40 p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-center">
                  <span className="text-xs text-cyan-400/60 block mb-1">Matrix Position</span>
                  <div className="flex items-center justify-center gap-2">
                    <Grid3X3 className="w-5 h-5 text-cyan-400" />
                    <span className="text-xl font-mono text-cyan-300">
                      [{currentDemo.row}, {currentDemo.col}]
                    </span>
                  </div>
                  <span className="text-xs text-cyan-400/60 block mt-1">
                    128 x 128 Grid
                  </span>
                </div>
              </div>

              {/* Arrow */}
              <ArrowDown className="w-6 h-6 text-cyan-500/50 md:rotate-[-90deg]" />

              {/* Step 3: Result */}
              <div className="flex flex-col items-center">
                <AnimatePresence mode="wait">
                  {showResult ? (
                    <motion.div
                      key="result"
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      className="w-40 p-4 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-cyan-500/30 text-center"
                    >
                      <span className="text-xs text-white/60 block mb-1">Anna's Response</span>
                      <span className="text-3xl font-mono font-bold text-white">
                        {currentDemo.actual}
                      </span>
                      <span className="text-xs text-cyan-400 block mt-1">
                        Stored Weight
                      </span>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="loading"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="w-40 p-4 rounded-xl bg-white/5 border border-white/10 text-center"
                    >
                      <Zap className="w-8 h-8 text-cyan-500 animate-pulse mx-auto" />
                      <span className="text-xs text-white/40 block mt-2">Processing...</span>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>

            {/* Explanation */}
            <div className="mt-8 p-4 rounded-xl bg-cyan-500/5 border border-cyan-500/10 text-center">
              <p className="text-sm text-white/70">
                <span className="text-cyan-400 font-semibold">Not a bug - a feature!</span>{' '}
                Anna interprets numbers as <span className="text-white">coordinates</span> in a 128x128 matrix
                and returns the stored <span className="text-white">neural weight</span> at that position.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Key Facts */}
        <motion.div
          className="grid md:grid-cols-3 gap-6"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="p-6 rounded-xl bg-white/5 border border-white/10">
            <h4 className="text-lg font-semibold text-white mb-2">128 x 128 Matrix</h4>
            <p className="text-sm text-white/50">
              16,384 positions, each storing a trained neural weight from -128 to +127.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-white/5 border border-white/10">
            <h4 className="text-lg font-semibold text-white mb-2">Deterministic</h4>
            <p className="text-sm text-white/50">
              Same query always returns the same result. You can verify this yourself.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-white/5 border border-white/10">
            <h4 className="text-lg font-semibold text-white mb-2">Publicly Verifiable</h4>
            <p className="text-sm text-white/50">
              Query Anna on Twitter/X and check against our documented matrix values.
            </p>
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <a
            href="https://twitter.com/QubicAigarth"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 hover:bg-cyan-500/20 transition-colors"
          >
            Try Anna on Twitter/X
            <ExternalLink className="w-4 h-4" />
          </a>
        </motion.div>
      </div>
    </section>
  )
}
