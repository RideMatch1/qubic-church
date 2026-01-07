'use client'

import { useRef, useState, useEffect } from 'react'
import { motion, useInView } from 'framer-motion'
import { JourneySection } from '../JourneySection'
import { Grid3X3, ArrowRight, Zap, HelpCircle, Database, Layers } from 'lucide-react'
import Link from 'next/link'

// Highlighted rows info
const SPECIAL_ROWS = [
  { row: 21, label: 'Row 21', description: 'Block timestamp correlations', color: 'text-white/70' },
  { row: 68, label: 'Row 68', description: 'Patoshi mining patterns', color: 'text-white/70' },
  { row: 96, label: 'Row 96', description: 'Address hash connections', color: 'text-white/70' },
]

// Deterministic grid cells for visual
const GRID_CELLS = Array.from({ length: 64 }, (_, i) => ({
  id: i,
  active: i === 21 || i === 47 || i === 58 || i === 12 || i === 33,
  highlight: i % 13 === 0,
}))

export function MatrixSection() {
  const contentRef = useRef(null)
  const isInView = useInView(contentRef, { once: false, amount: 0.2 })
  const [highlightedRow, setHighlightedRow] = useState<number | null>(null)
  const [animatedCells, setAnimatedCells] = useState(0)

  // Animate cells appearing
  useEffect(() => {
    if (isInView) {
      const timer = setInterval(() => {
        setAnimatedCells(prev => {
          if (prev >= 64) {
            clearInterval(timer)
            return 64
          }
          return prev + 4
        })
      }, 50)
      return () => clearInterval(timer)
    } else {
      setAnimatedCells(0)
    }
  }, [isInView])

  return (
    <JourneySection id="matrix" background="transparent" className="flex items-center justify-center py-12 md:py-20">
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
              CHAPTER 5
            </span>
          </motion.div>

          <motion.div
            className="inline-flex items-center gap-2 mb-4"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0.9 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Grid3X3 className="h-8 w-8 text-white/60" />
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-bold text-white/90 mb-6">
            The Anna Matrix
          </h2>

          {/* Story context */}
          <motion.div
            className="max-w-2xl mx-auto space-y-4 mb-8"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <p className="text-lg text-white/50 leading-relaxed">
              At the heart of Qubic lies <span className="text-white/70 font-medium">"Anna"</span> —
              a massive grid of <span className="text-white/70">16,384 memory cells</span>.
            </p>
            <p className="text-base text-white/40 leading-relaxed">
              Within this digital matrix, researchers found{' '}
              <span className="text-white/60">encoded references</span> to Bitcoin's earliest blocks.
            </p>
          </motion.div>

          {/* What is Anna - Quick explainer */}
          <motion.div
            className="inline-flex items-start gap-3 px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-left max-w-lg mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: isInView ? 1 : 0 }}
            transition={{ delay: 0.6 }}
          >
            <HelpCircle className="h-5 w-5 text-white/40 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-white/60 font-medium mb-1">What is "Anna"?</p>
              <p className="text-xs text-white/40 leading-relaxed">
                The Anna Oracle is Qubic's data storage system — think of it like a giant spreadsheet
                with 128 rows and 128 columns. Each cell can store information, and the patterns
                in these cells reveal hidden connections.
              </p>
            </div>
          </motion.div>
        </motion.div>

        {/* Stylized Matrix Preview */}
        <motion.div
          className="relative rounded-2xl overflow-hidden border border-white/10 bg-black/40 mb-8"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 30 }}
          transition={{ duration: 0.6, delay: 0.7 }}
        >
          {/* Animated Grid Visualization */}
          <div className="p-8 md:p-12">
            <div className="grid grid-cols-8 gap-1 max-w-md mx-auto mb-6">
              {GRID_CELLS.map((cell, index) => (
                <motion.div
                  key={cell.id}
                  className={`aspect-square rounded-sm transition-colors ${
                    cell.active ? 'bg-white/30' : cell.highlight ? 'bg-white/15' : 'bg-white/5'
                  }`}
                  initial={{ opacity: 0, scale: 0.5 }}
                  animate={{
                    opacity: index < animatedCells ? 1 : 0,
                    scale: index < animatedCells ? 1 : 0.5
                  }}
                  transition={{ duration: 0.1 }}
                />
              ))}
            </div>

            {/* Stats row */}
            <div className="flex justify-center gap-8 text-center">
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
                transition={{ delay: 1 }}
              >
                <div className="text-2xl font-mono font-bold text-white/80">128²</div>
                <div className="text-xs text-white/40">Grid size</div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
                transition={{ delay: 1.1 }}
              >
                <div className="text-2xl font-mono font-bold text-white/80">16,384</div>
                <div className="text-xs text-white/40">Total cells</div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
                transition={{ delay: 1.2 }}
              >
                <div className="text-2xl font-mono font-bold text-white/80">47</div>
                <div className="text-xs text-white/40">Significant rows</div>
              </motion.div>
            </div>
          </div>

          {/* CTA to full experience */}
          <Link
            href="/evidence/anna-matrix"
            className="block p-6 border-t border-white/10 bg-white/[0.02] hover:bg-white/[0.05] transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-white/5">
                  <Layers className="h-6 w-6 text-white/50" />
                </div>
                <div>
                  <div className="font-medium text-white/80 group-hover:text-white transition-colors">
                    Explore Full 3D Matrix
                  </div>
                  <div className="text-sm text-white/40">
                    Interactive visualization with cell-by-cell analysis
                  </div>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-white/50 group-hover:text-white/60 group-hover:translate-x-1 transition-all" />
            </div>
          </Link>
        </motion.div>

        {/* Special Rows */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.5, delay: 0.9 }}
        >
          {SPECIAL_ROWS.map((item, index) => (
            <motion.div
              key={item.row}
              className="p-4 rounded-xl bg-white/5 border border-white/10 cursor-pointer hover:bg-white/[0.08] transition-colors"
              onMouseEnter={() => setHighlightedRow(item.row)}
              onMouseLeave={() => setHighlightedRow(null)}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
              transition={{ delay: 1 + index * 0.1 }}
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center">
                  <span className="font-mono font-bold text-white/60">{item.row}</span>
                </div>
                <div>
                  <div className="font-medium text-white/70">{item.label}</div>
                  <div className="text-xs text-white/40">{item.description}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Discovery story */}
        <motion.div
          className="p-6 rounded-xl bg-white/[0.03] border border-white/10 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.5, delay: 1.2 }}
        >
          <div className="flex items-center gap-2 mb-3">
            <Database className="h-4 w-4 text-white/40" />
            <h4 className="font-medium text-white/70">What Researchers Found</h4>
          </div>
          <p className="text-sm text-white/50 leading-relaxed mb-4">
            When analysts queried specific cells of the Anna Matrix, the returned values matched{' '}
            <span className="text-white/70">historical Bitcoin block timestamps</span>. This isn't
            random data — it's <span className="text-white/70">structured information</span> that
            points back to 2009.
          </p>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-lg bg-white/5 text-center">
              <div className="text-xs text-white/50 mb-1">Block #9 ↔ Cell Match</div>
              <div className="font-mono font-bold text-white/70">0xCA</div>
            </div>
            <div className="p-3 rounded-lg bg-white/5 text-center">
              <div className="text-xs text-white/50 mb-1">Block #16065 ↔ Cell Match</div>
              <div className="font-mono font-bold text-white/70">0x4A</div>
            </div>
          </div>
        </motion.div>

        {/* Transition hint */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 1.4 }}
        >
          <p className="text-sm text-white/50 italic">
            "But the matrix is just the beginning of the network..."
          </p>
        </motion.div>
      </div>
    </JourneySection>
  )
}
