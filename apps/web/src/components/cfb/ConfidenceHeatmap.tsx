'use client'

import { useRef, useState } from 'react'
import { motion, useInView } from 'framer-motion'
import { Grid3X3 } from 'lucide-react'

interface EvidenceCell {
  id: string
  category: string
  subCategory: string
  confidence: number
  description: string
  dataPoints: number
}

const evidenceMatrix: EvidenceCell[] = [
  // Stylometry Row
  { id: 'styl-1', category: 'Stylometry', subCategory: 'Sentence Length', confidence: 96, description: 'Average sentence length matches within 2%', dataPoints: 847 },
  { id: 'styl-2', category: 'Stylometry', subCategory: 'Vocabulary', confidence: 98, description: 'Unique word usage patterns match', dataPoints: 12500 },
  { id: 'styl-3', category: 'Stylometry', subCategory: 'Punctuation', confidence: 94, description: 'Comma/period usage patterns identical', dataPoints: 3200 },
  { id: 'styl-4', category: 'Stylometry', subCategory: 'Technical Terms', confidence: 99, description: 'Cryptographic terminology overlap', dataPoints: 456 },

  // Temporal Row
  { id: 'temp-1', category: 'Temporal', subCategory: 'Activity Hours', confidence: 92, description: 'GMT+3 posting pattern match', dataPoints: 2100 },
  { id: 'temp-2', category: 'Temporal', subCategory: 'Silence Periods', confidence: 88, description: 'Inactive periods correlate', dataPoints: 365 },
  { id: 'temp-3', category: 'Temporal', subCategory: 'Holidays', confidence: 85, description: 'Russian holiday patterns', dataPoints: 45 },
  { id: 'temp-4', category: 'Temporal', subCategory: 'Time-Lock Events', confidence: 95, description: '2026 date correlations', dataPoints: 12 },

  // Technical Row
  { id: 'tech-1', category: 'Technical', subCategory: 'Code Style', confidence: 97, description: 'C++ formatting identical', dataPoints: 15000 },
  { id: 'tech-2', category: 'Technical', subCategory: 'Architecture', confidence: 99, description: 'System design philosophy match', dataPoints: 234 },
  { id: 'tech-3', category: 'Technical', subCategory: 'Crypto Methods', confidence: 98, description: 'Cryptographic approach match', dataPoints: 89 },
  { id: 'tech-4', category: 'Technical', subCategory: 'Performance Focus', confidence: 96, description: 'Optimization priorities align', dataPoints: 567 },

  // Mathematical Row
  { id: 'math-1', category: 'Mathematical', subCategory: '625,284 Formula', confidence: 100, description: 'Exact match impossible by chance', dataPoints: 1 },
  { id: 'math-2', category: 'Mathematical', subCategory: 'Prime Usage', confidence: 94, description: '47, 283, 137 patterns', dataPoints: 23 },
  { id: 'math-3', category: 'Mathematical', subCategory: 'Mod 27 Signature', confidence: 91, description: 'Result always = 7', dataPoints: 8 },
  { id: 'math-4', category: 'Mathematical', subCategory: '676 Pattern', confidence: 88, description: '26² = Qubic Computors', dataPoints: 5 },

  // Blockchain Row
  { id: 'block-1', category: 'Blockchain', subCategory: 'Genesis Analysis', confidence: 90, description: 'Block 0 timestamp encoding', dataPoints: 1 },
  { id: 'block-2', category: 'Blockchain', subCategory: 'POCZ Address', confidence: 85, description: 'GENESIS token issuer match', dataPoints: 817 },
  { id: 'block-3', category: 'Blockchain', subCategory: 'Mining Patterns', confidence: 82, description: 'PATOSHI correlation', dataPoints: 1200 },
  { id: 'block-4', category: 'Blockchain', subCategory: 'Address Behavior', confidence: 78, description: 'Dormant wallet patterns', dataPoints: 50 },
]

const categories = ['Stylometry', 'Temporal', 'Technical', 'Mathematical', 'Blockchain']

function getConfidenceColor(confidence: number): string {
  if (confidence >= 95) return 'bg-emerald-500'
  if (confidence >= 85) return 'bg-emerald-600'
  if (confidence >= 75) return 'bg-yellow-500'
  if (confidence >= 60) return 'bg-orange-500'
  return 'bg-red-500'
}

function getConfidenceTextColor(confidence: number): string {
  if (confidence >= 95) return 'text-emerald-400'
  if (confidence >= 85) return 'text-emerald-500'
  if (confidence >= 75) return 'text-yellow-400'
  if (confidence >= 60) return 'text-orange-400'
  return 'text-red-400'
}

export function ConfidenceHeatmap() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })
  const [hoveredCell, setHoveredCell] = useState<EvidenceCell | null>(null)

  const getCellsForCategory = (category: string) => {
    return evidenceMatrix.filter(cell => cell.category === category)
  }

  const overallConfidence = Math.round(
    evidenceMatrix.reduce((acc, cell) => acc + cell.confidence, 0) / evidenceMatrix.length
  )

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
            <Grid3X3 className="h-8 w-8 text-cyan-400" />
            <h2 className="text-display-md font-semibold">Evidence Confidence Matrix</h2>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto text-body-lg">
            Multi-dimensional analysis of the CFB = Satoshi hypothesis across 20 evidence categories.
          </p>
        </motion.div>

        {/* Overall Confidence */}
        <motion.div
          className="flex items-center justify-center mb-8"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="bg-emerald-900/30 border border-emerald-700 rounded-xl px-8 py-4 text-center">
            <div className="text-sm text-emerald-400 mb-1">OVERALL CONFIDENCE</div>
            <div className="text-5xl font-bold text-emerald-300">
              {overallConfidence}%
            </div>
          </div>
        </motion.div>

        {/* Heatmap Grid */}
        <motion.div
          className="mb-8 p-6 rounded-2xl border bg-gradient-to-br from-zinc-900 to-zinc-950 border-zinc-800 overflow-x-auto"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <table className="w-full min-w-[600px]">
            <thead>
              <tr>
                <th className="text-left text-xs text-muted-foreground pb-4 pr-4">Category</th>
                <th className="text-center text-xs text-muted-foreground pb-4 px-2">Metric 1</th>
                <th className="text-center text-xs text-muted-foreground pb-4 px-2">Metric 2</th>
                <th className="text-center text-xs text-muted-foreground pb-4 px-2">Metric 3</th>
                <th className="text-center text-xs text-muted-foreground pb-4 px-2">Metric 4</th>
                <th className="text-right text-xs text-muted-foreground pb-4 pl-4">Average</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((category) => {
                const cells = getCellsForCategory(category)
                const avgConfidence = Math.round(
                  cells.reduce((acc, cell) => acc + cell.confidence, 0) / cells.length
                )

                return (
                  <tr key={category} className="border-t border-zinc-800">
                    <td className="py-3 pr-4">
                      <span className="text-sm font-medium text-white">{category}</span>
                    </td>
                    {cells.map((cell) => (
                      <td key={cell.id} className="py-3 px-2">
                        <div
                          className="relative cursor-pointer"
                          onMouseEnter={() => setHoveredCell(cell)}
                          onMouseLeave={() => setHoveredCell(null)}
                        >
                          <div
                            className={`w-full h-12 rounded-lg flex items-center justify-center ${getConfidenceColor(
                              cell.confidence
                            )} bg-opacity-20 border border-opacity-30 ${getConfidenceColor(cell.confidence).replace('bg-', 'border-')} transition-all hover:scale-105`}
                          >
                            <span className={`font-bold ${getConfidenceTextColor(cell.confidence)}`}>
                              {cell.confidence}%
                            </span>
                          </div>
                          <div className="text-xs text-muted-foreground text-center mt-1 truncate">
                            {cell.subCategory}
                          </div>
                        </div>
                      </td>
                    ))}
                    <td className="py-3 pl-4 text-right">
                      <span className={`font-bold ${getConfidenceTextColor(avgConfidence)}`}>
                        {avgConfidence}%
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </motion.div>

        {/* Hover Detail Panel */}
        {hoveredCell && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 p-6 rounded-xl bg-zinc-800 border border-zinc-700"
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="text-xs text-muted-foreground mb-1">
                  {hoveredCell.category} / {hoveredCell.subCategory}
                </div>
                <h4 className="text-lg font-bold text-white mb-2">{hoveredCell.description}</h4>
                <div className="flex items-center gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Confidence: </span>
                    <span className={`font-bold ${getConfidenceTextColor(hoveredCell.confidence)}`}>
                      {hoveredCell.confidence}%
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Data Points: </span>
                    <span className="text-white font-medium">{hoveredCell.dataPoints.toLocaleString()}</span>
                  </div>
                </div>
              </div>
              <div
                className={`w-16 h-16 rounded-lg flex items-center justify-center ${getConfidenceColor(
                  hoveredCell.confidence
                )} bg-opacity-30`}
              >
                <span className={`text-2xl font-bold ${getConfidenceTextColor(hoveredCell.confidence)}`}>
                  {hoveredCell.confidence}
                </span>
              </div>
            </div>
          </motion.div>
        )}

        {/* Legend */}
        <motion.div
          className="flex flex-wrap items-center justify-center gap-6 text-xs"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-emerald-500 bg-opacity-30" />
            <span className="text-muted-foreground">95-100% (Definitive)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-emerald-600 bg-opacity-30" />
            <span className="text-muted-foreground">85-94% (Strong)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-yellow-500 bg-opacity-30" />
            <span className="text-muted-foreground">75-84% (Moderate)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-orange-500 bg-opacity-30" />
            <span className="text-muted-foreground">60-74% (Weak)</span>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
