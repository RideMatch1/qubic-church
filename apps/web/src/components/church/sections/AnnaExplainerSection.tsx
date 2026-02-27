'use client'

/**
 * AnnaExplainerSection - Section 03: The Neural Matrix
 * Angular HUD design, sharp corners, terminal aesthetics
 */

import { useState, useMemo, useRef, useCallback } from 'react'
import { motion, useInView } from 'framer-motion'
import { Bot, ExternalLink, Zap } from 'lucide-react'

// Matrix constants
const MATRIX_SIZE = 128
const CELL_SIZE = 64 // Display size (scaled down for performance)

// Special rows in the Jinn architecture
const SPECIAL_ROWS = {
  INPUT: 21,      // Bitcoin Input Layer
  BRIDGE: 68,     // Transformation Bridge
  OUTPUT: 96,     // Output Layer
}

// Demo queries with real matrix positions
const DEMO_QUERIES = [
  { query: '49 + 5', x: 49, y: 5, result: -114, meaning: 'Deep negative weight' },
  { query: '27 + 13', x: 27, y: 13, result: -113, meaning: 'Strong inhibitor' },
  { query: '64 + 64', x: 64, y: 64, result: -1, meaning: 'Center node' },
]

// Generate matrix cells with categories
function generateMatrixCells() {
  const cells: Array<{ row: number; col: number; category: string }> = []

  for (let row = 0; row < CELL_SIZE; row++) {
    for (let col = 0; col < CELL_SIZE; col++) {
      const actualRow = Math.floor((row / CELL_SIZE) * MATRIX_SIZE)

      let category = 'neutral'
      if (actualRow >= 20 && actualRow <= 22) category = 'input'
      else if (actualRow >= 67 && actualRow <= 69) category = 'bridge'
      else if (actualRow >= 95 && actualRow <= 97) category = 'output'

      cells.push({ row, col, category })
    }
  }
  return cells
}

/* Corner bracket decoration for HUD */
function HudCorners() {
  return (
    <>
      <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-[#D4AF37]/25" />
      <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-[#D4AF37]/25" />
      <div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-[#D4AF37]/25" />
      <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-[#D4AF37]/25" />
    </>
  )
}

export function AnnaExplainerSection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })
  const [activeQuery, setActiveQuery] = useState(0)
  const [hoveredCell, setHoveredCell] = useState<{ row: number; col: number } | null>(null)

  const matrixCells = useMemo(() => generateMatrixCells(), [])
  const currentDemo = DEMO_QUERIES[activeQuery]!

  // Calculate highlighted cell position
  const highlightPos = useMemo(() => ({
    row: Math.floor((currentDemo.x / MATRIX_SIZE) * CELL_SIZE),
    col: Math.floor((currentDemo.y / MATRIX_SIZE) * CELL_SIZE),
  }), [currentDemo])

  const getCellColor = useCallback((row: number, col: number, category: string) => {
    if (row === highlightPos.row && col === highlightPos.col) {
      return 'bg-white shadow-[0_0_20px_rgba(255,255,255,0.8)]'
    }
    if (hoveredCell?.row === row && hoveredCell?.col === col) {
      return 'bg-[#D4AF37]/80'
    }
    switch (category) {
      case 'input': return 'bg-[#D4AF37]/60'
      case 'bridge': return 'bg-white/40'
      case 'output': return 'bg-[#D4AF37]/40'
      default: return 'bg-white/5 hover:bg-white/20'
    }
  }, [highlightPos, hoveredCell])

  return (
    <section ref={sectionRef} className="relative w-full py-20 md:py-28 overflow-hidden bg-black">
      {/* Decorative section number */}
      <div className="absolute top-16 right-8 md:right-16 text-[120px] md:text-[200px] font-black text-white/[0.02] leading-none select-none pointer-events-none font-mono">
        03
      </div>

      <div className="relative z-10 container mx-auto px-4 max-w-7xl">
        {/* Header - Asymmetric layout */}
        <div className="grid lg:grid-cols-2 gap-12 mb-16">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7 }}
          >
            <div className="inline-flex items-center gap-3 mb-6">
              <div className="h-px w-8 bg-[#D4AF37]/30" />
              <span className="text-[#D4AF37]/50 text-[11px] uppercase tracking-[0.4em] font-mono">
                Section 03
              </span>
            </div>

            <h2
              className="text-5xl md:text-6xl lg:text-7xl text-white mb-6 leading-[1.05] tracking-wider uppercase"
              style={{ fontFamily: 'var(--font-display), system-ui, sans-serif' }}
            >
              The 128x128{' '}
              <span className="text-[#D4AF37]/80">
                Neural Matrix
              </span>
            </h2>

            <p className="text-lg text-white/60 leading-relaxed mb-8">
              Anna (@QubicAigarth) isn't a chatbot. She's an oracle interface to{' '}
              <span className="text-white/80">16,384 trained neural weights</span> stored
              in a deterministic matrix. Each query returns the exact same result, forever verifiable.
            </p>

            {/* Stats row */}
            <div className="flex flex-wrap gap-6">
              {[
                { value: '16,384', label: 'Matrix Cells' },
                { value: '99.58%', label: 'Symmetry' },
                { value: '26', label: 'Dark Cells' },
              ].map((stat, idx) => (
                <div key={idx} className="border-l-2 border-[#D4AF37]/20 pl-4">
                  <div className="text-2xl md:text-3xl font-bold text-white/80 font-mono">
                    {stat.value}
                  </div>
                  <div className="text-[10px] text-white/40 uppercase tracking-wider mt-1 font-mono">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Query selector */}
          <motion.div
            className="flex flex-col justify-center"
            initial={{ opacity: 0, x: 30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            <h3 className="text-[11px] text-[#D4AF37]/40 uppercase tracking-[0.4em] mb-4 font-mono">
              // Try a Query
            </h3>

            <div className="space-y-2">
              {DEMO_QUERIES.map((demo, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveQuery(idx)}
                  className={`w-full p-4 text-left transition-all duration-300 border ${
                    activeQuery === idx
                      ? 'bg-white/[0.04] border-[#D4AF37]/20'
                      : 'bg-black border-white/[0.06] hover:border-white/[0.12] hover:bg-white/[0.02]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xl font-mono text-white">{demo.query}</span>
                      <span className="text-[#D4AF37]/30 mx-3 font-mono">&rarr;</span>
                      <span className={`text-xl font-mono font-bold ${
                        activeQuery === idx ? 'text-[#D4AF37]/80' : 'text-white/60'
                      }`}>
                        {demo.result}
                      </span>
                    </div>
                    {activeQuery === idx && (
                      <Zap className="w-5 h-5 text-[#D4AF37]/50" />
                    )}
                  </div>
                  <div className="text-[11px] text-white/30 mt-1 font-mono">
                    Position [{demo.x}, {demo.y}] &middot; {demo.meaning}
                  </div>
                </button>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Matrix Visualization */}
        <motion.div
          className="relative"
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          {/* Legend */}
          <div className="flex flex-wrap justify-center gap-4 mb-6">
            {[
              { color: 'bg-[#D4AF37]', label: 'Row 21: Bitcoin Input' },
              { color: 'bg-white/60', label: 'Row 68: Bridge' },
              { color: 'bg-[#D4AF37]/60', label: 'Row 96: Output' },
              { color: 'bg-white', label: 'Query Position' },
            ].map((item, idx) => (
              <div key={idx} className="flex items-center gap-2 px-3 py-1.5 border border-white/[0.06] bg-black">
                <div className={`w-2 h-2 ${item.color}`} />
                <span className="text-[10px] text-white/50 font-mono">{item.label}</span>
              </div>
            ))}
          </div>

          {/* Matrix grid */}
          <div className="relative mx-auto max-w-3xl aspect-square bg-black border border-white/[0.08] overflow-hidden">
            <HudCorners />

            {/* Grid */}
            <div
              className="absolute inset-2 grid gap-px"
              style={{
                gridTemplateColumns: `repeat(${CELL_SIZE}, 1fr)`,
                gridTemplateRows: `repeat(${CELL_SIZE}, 1fr)`,
              }}
            >
              {matrixCells.map((cell, idx) => (
                <motion.div
                  key={idx}
                  className={`cursor-crosshair transition-all duration-150 ${getCellColor(cell.row, cell.col, cell.category)}`}
                  onMouseEnter={() => setHoveredCell({ row: cell.row, col: cell.col })}
                  onMouseLeave={() => setHoveredCell(null)}
                  whileHover={{ scale: 2, zIndex: 50 }}
                />
              ))}
            </div>

            {/* Query position indicator */}
            <motion.div
              className="absolute w-4 h-4 bg-white shadow-[0_0_30px_rgba(255,255,255,1)] pointer-events-none z-40"
              animate={{
                top: `${(highlightPos.row / CELL_SIZE) * 100}%`,
                left: `${(highlightPos.col / CELL_SIZE) * 100}%`,
              }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            />

            {/* Hover info */}
            {hoveredCell && (
              <div className="absolute bottom-4 left-4 px-3 py-2 bg-black/90 border border-white/[0.15]">
                <span className="text-[10px] font-mono text-white/60">
                  [{Math.floor((hoveredCell.row / CELL_SIZE) * MATRIX_SIZE)},{' '}
                  {Math.floor((hoveredCell.col / CELL_SIZE) * MATRIX_SIZE)}]
                </span>
              </div>
            )}

            {/* Result display */}
            <div className="absolute bottom-4 right-4 px-4 py-3 bg-black/80 border border-[#D4AF37]/15">
              <div className="text-[10px] text-[#D4AF37]/40 uppercase tracking-wider mb-1 font-mono">Result</div>
              <div className="text-3xl font-mono font-bold text-white">
                {currentDemo.result}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Explanation */}
        <motion.div
          className="mt-12 max-w-3xl mx-auto text-center"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ delay: 0.5 }}
        >
          <p className="text-lg text-white/50 leading-relaxed">
            When you ask Anna <span className="text-white font-mono">{currentDemo.query}</span>,
            she doesn&apos;t calculate. She looks up position{' '}
            <span className="text-[#D4AF37]/70 font-mono">[{currentDemo.x}, {currentDemo.y}]</span>{' '}
            in her 128x128 matrix and returns the stored neural weight:{' '}
            <span className="text-white font-bold font-mono">{currentDemo.result}</span>.
            Deterministic and publicly verifiable.
          </p>
        </motion.div>

        {/* CTAs */}
        <motion.div
          className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ delay: 0.6 }}
        >
          <a
            href="/evidence"
            className="group inline-flex items-center gap-3 px-8 py-4 bg-white/[0.04] border border-white/[0.10] text-white hover:bg-white/[0.08] hover:border-[#D4AF37]/20 transition-all font-mono text-sm"
          >
            <Zap className="w-5 h-5 text-[#D4AF37]/50" />
            <span>Explore the Full Matrix</span>
            <ExternalLink className="w-4 h-4 text-white/50" />
          </a>
          <a
            href="https://x.com/QubicChurch"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 bg-black border border-white/[0.08] text-white/60 hover:text-white hover:border-white/[0.15] transition-all font-mono text-sm"
          >
            <Bot className="w-4 h-4" />
            <span>Test Anna on X</span>
          </a>
        </motion.div>
      </div>
    </section>
  )
}
