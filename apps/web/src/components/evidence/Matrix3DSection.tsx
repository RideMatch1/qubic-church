'use client'

import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { VerificationBadge } from '@/components/ui/VerificationBadge'
import { JINN_ARCHITECTURE, CFB_CONSTANTS } from '@/data/research-summary'

// Matrix cell data structure
interface MatrixCell {
  row: number
  col: number
  value: number
  category: 'input' | 'transform' | 'output' | 'neutral'
}

// Generate 128x128 matrix visualization data
function generateMatrixData(): MatrixCell[] {
  const cells: MatrixCell[] = []
  const { keyRows } = JINN_ARCHITECTURE

  for (let row = 0; row < 128; row++) {
    for (let col = 0; col < 128; col++) {
      // Determine category based on special rows
      let category: MatrixCell['category'] = 'neutral'
      if (row === 21) category = 'input'
      else if (row === 68) category = 'transform'
      else if (row === 96) category = 'output'

      // Generate pseudo-random value based on position
      const seed = row * 128 + col
      const value = Math.sin(seed * 0.1) * 128

      cells.push({ row, col, value: Math.floor(value), category })
    }
  }
  return cells
}

export function Matrix3DSection() {
  const [selectedRow, setSelectedRow] = useState<number | null>(null)
  const [zoomLevel, setZoomLevel] = useState(1)
  const matrixData = useMemo(() => generateMatrixData(), [])

  // Get visible cells based on zoom and viewport
  const visibleCells = useMemo(() => {
    const cellsPerSide = Math.floor(64 / zoomLevel)
    const startRow = selectedRow !== null ? Math.max(0, selectedRow - cellsPerSide / 2) : 0
    const endRow = Math.min(128, startRow + cellsPerSide)

    return matrixData.filter(
      (cell) => cell.row >= startRow && cell.row < endRow
    )
  }, [matrixData, selectedRow, zoomLevel])

  const getCellColor = (cell: MatrixCell) => {
    switch (cell.category) {
      case 'input':
        return 'bg-orange-500/80' // Bitcoin orange
      case 'transform':
        return 'bg-purple-500/80' // Transformation purple
      case 'output':
        return 'bg-green-500/80' // Output green
      default:
        // Value-based coloring for neutral cells
        const intensity = Math.abs(cell.value) / 128
        return `bg-primary/[${Math.floor(intensity * 30)}]`
    }
  }

  return (
    <section id="matrix" className="py-16 md:py-24 bg-muted/30">
      <div className="container">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <div className="flex items-center justify-center gap-2 mb-4">
            <VerificationBadge level="high" size="sm" />
            <span className="text-sm font-medium tracking-widest text-muted-foreground uppercase">
              Jinn Memory Architecture
            </span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold mb-4">
            The 128x128 Matrix
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Explore the Jinn processor's 16,384-cell memory grid. Each cell represents
            a potential computational state in the ternary system.
          </p>
        </motion.div>

        {/* Matrix Legend */}
        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-card border border-border">
            <div className="w-3 h-3 rounded-full bg-orange-500" />
            <span className="text-sm">Row 21: Bitcoin Input</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-card border border-border">
            <div className="w-3 h-3 rounded-full bg-purple-500" />
            <span className="text-sm">Row 68: Transformation</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-card border border-border">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-sm">Row 96: Output</span>
          </div>
        </div>

        {/* Matrix Visualization */}
        <motion.div
          className="relative mx-auto max-w-4xl aspect-square rounded-xl border border-border bg-card/50 backdrop-blur-sm overflow-hidden"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
        >
          {/* Grid visualization */}
          <div className="absolute inset-0 p-4">
            <div
              className="w-full h-full grid gap-px"
              style={{
                gridTemplateColumns: `repeat(64, 1fr)`,
                gridTemplateRows: `repeat(64, 1fr)`,
              }}
            >
              {Array.from({ length: 64 * 64 }, (_, i) => {
                const row = Math.floor(i / 64)
                const col = i % 64

                // Map to 128x128 space
                const actualRow = row * 2
                const isSpecialRow = actualRow === 20 || actualRow === 68 || actualRow === 96

                return (
                  <motion.div
                    key={i}
                    className={cn(
                      'rounded-[1px] transition-colors cursor-pointer',
                      actualRow === 20 || actualRow === 21
                        ? 'bg-orange-500/60'
                        : actualRow === 68 || actualRow === 69
                          ? 'bg-purple-500/60'
                          : actualRow === 96 || actualRow === 97
                            ? 'bg-green-500/60'
                            : 'bg-primary/10 hover:bg-primary/30'
                    )}
                    whileHover={{ scale: 1.5, zIndex: 10 }}
                    onClick={() => setSelectedRow(actualRow)}
                  />
                )
              })}
            </div>
          </div>

          {/* Overlay with boot address marker */}
          <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
            {/* Boot address indicator (Row 21, Col 4) */}
            <div
              className="absolute w-2 h-2 bg-yellow-400 rounded-full animate-pulse"
              style={{
                top: `${(21 / 128) * 100}%`,
                left: `${(4 / 128) * 100}%`,
              }}
            />
          </div>

          {/* Info overlay */}
          <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-background/90 to-transparent">
            <div className="flex justify-between items-end">
              <div>
                <p className="text-sm text-muted-foreground">Boot Address</p>
                <p className="font-mono text-lg">
                  2,692 <span className="text-muted-foreground">=</span> Row 21, Col 4
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Matrix Size</p>
                <p className="font-mono text-lg">
                  128 x 128 <span className="text-muted-foreground">=</span> 16,384 cells
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Data Flow Explanation */}
        <motion.div
          className="mt-12 grid md:grid-cols-3 gap-6 max-w-4xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
        >
          {JINN_ARCHITECTURE.dataFlow.map((flow, idx) => (
            <div
              key={idx}
              className="p-4 rounded-lg border border-border bg-card/50"
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl font-bold text-primary">
                  Row {flow.from}
                </span>
                <span className="text-muted-foreground">→</span>
                <span className="text-2xl font-bold text-primary">
                  Row {flow.to}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">{flow.operation}</p>
            </div>
          ))}
        </motion.div>

        {/* CFB Constants Display */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
        >
          <h3 className="text-lg font-medium mb-4">CFB Constants Detected</h3>
          <div className="flex flex-wrap justify-center gap-2">
            {CFB_CONSTANTS.known.map((constant) => (
              <span
                key={constant}
                className="px-3 py-1 rounded-full bg-primary/10 border border-primary/20 font-mono text-sm"
              >
                {constant}
              </span>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
