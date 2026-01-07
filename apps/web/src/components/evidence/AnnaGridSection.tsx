'use client'

import { useState, useMemo, useCallback } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { VerificationBadge } from '@/components/ui/VerificationBadge'
import { ANNA_MATRIX, JINN_ARCHITECTURE } from '@/data/research-summary'

interface CellInfo {
  address: number
  row: number
  col: number
  value: number
  meaning?: string
}

// Generate Anna Matrix data (simplified version - would load from JSON in production)
function generateAnnaData(): number[][] {
  const matrix: number[][] = []
  for (let row = 0; row < 128; row++) {
    const rowData: number[] = []
    for (let col = 0; col < 128; col++) {
      // Generate deterministic values based on position
      const seed = row * 128 + col
      const value = Math.floor(Math.sin(seed * 0.05) * 64 + Math.cos(seed * 0.03) * 64)
      rowData.push(Math.max(-128, Math.min(127, value)))
    }
    matrix.push(rowData)
  }
  return matrix
}

export function AnnaGridSection() {
  const [selectedCell, setSelectedCell] = useState<CellInfo | null>(null)
  const [addressInput, setAddressInput] = useState('')
  const [hoveredCell, setHoveredCell] = useState<{ row: number; col: number } | null>(null)
  const [viewMode, setViewMode] = useState<'full' | 'zoom'>('full')

  const matrixData = useMemo(() => generateAnnaData(), [])

  // Convert address to row/col
  const addressToCell = useCallback((address: number): CellInfo | null => {
    if (address < 0 || address >= 16384) return null
    const row = Math.floor(address / 128)
    const col = address % 128
    const value = matrixData[row]?.[col] ?? 0

    // Get meaning based on special rows
    let meaning: string | undefined
    if (row === 21) meaning = 'Bitcoin Input Layer'
    else if (row === 68) meaning = 'Transformation Bridge (137 writes)'
    else if (row === 96) meaning = 'Output Layer (POCZ)'

    return { address, row, col, value, meaning }
  }, [matrixData])

  // Handle address input
  const handleAddressLookup = () => {
    const address = parseInt(addressInput, 10)
    if (!isNaN(address)) {
      const cell = addressToCell(address)
      if (cell) setSelectedCell(cell)
    }
  }

  // Get color for cell value
  const getCellColor = (value: number, row: number): string => {
    // Special row colors
    if (row === 21) return 'bg-orange-500'
    if (row === 68) return 'bg-purple-500'
    if (row === 96) return 'bg-green-500'

    // Value-based coloring
    if (value > 0) {
      const intensity = Math.min(value / 128, 1)
      return `bg-blue-500/${Math.floor(intensity * 60 + 20)}`
    } else if (value < 0) {
      const intensity = Math.min(Math.abs(value) / 128, 1)
      return `bg-red-500/${Math.floor(intensity * 60 + 20)}`
    }
    return 'bg-muted/30'
  }

  return (
    <section id="anna-grid" className="py-16 md:py-24">
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
              Interactive Tool
            </span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold mb-4">
            Anna Grid Explorer
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            The 128x128 Anna Matrix contains {ANNA_MATRIX.totalCells.toLocaleString()} cells,
            each storing values from {ANNA_MATRIX.valueRange.min} to {ANNA_MATRIX.valueRange.max}.
            Click any cell to explore its data.
          </p>
        </motion.div>

        {/* Address Calculator */}
        <motion.div
          className="max-w-xl mx-auto mb-8"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <div className="p-4 rounded-lg border border-border bg-card/50 backdrop-blur-sm">
            <h3 className="text-lg font-medium mb-3">Address Converter</h3>
            <div className="flex gap-2">
              <input
                type="number"
                value={addressInput}
                onChange={(e) => setAddressInput(e.target.value)}
                placeholder="Enter address (0-16383)"
                className="flex-1 px-4 py-2 rounded-md bg-background border border-border font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                min={0}
                max={16383}
              />
              <button
                onClick={handleAddressLookup}
                className="px-4 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
              >
                Lookup
              </button>
            </div>

            {selectedCell && (
              <div className="mt-4 p-3 rounded-md bg-muted/50 font-mono text-sm">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-muted-foreground">Address:</span>{' '}
                    <span className="text-primary font-bold">{selectedCell.address}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Value:</span>{' '}
                    <span className={cn(
                      'font-bold',
                      selectedCell.value > 0 ? 'text-blue-400' : selectedCell.value < 0 ? 'text-red-400' : 'text-muted-foreground'
                    )}>
                      {selectedCell.value}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Row:</span>{' '}
                    <span className="font-bold">{selectedCell.row}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Col:</span>{' '}
                    <span className="font-bold">{selectedCell.col}</span>
                  </div>
                </div>
                {selectedCell.meaning && (
                  <div className="mt-2 pt-2 border-t border-border">
                    <span className="text-primary">{selectedCell.meaning}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>

        {/* Quick Lookups */}
        <motion.div
          className="flex flex-wrap justify-center gap-2 mb-8"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <span className="text-sm text-muted-foreground mr-2">Quick lookup:</span>
          {[
            { label: 'Boot Address', value: 2692 },
            { label: 'Row 21 Start', value: 2688 },
            { label: 'Row 68 Start', value: 8704 },
            { label: 'POCZ Address', value: 12372 },
          ].map((preset) => (
            <button
              key={preset.label}
              onClick={() => {
                setAddressInput(preset.value.toString())
                const cell = addressToCell(preset.value)
                if (cell) setSelectedCell(cell)
              }}
              className="px-3 py-1 text-sm rounded-full bg-muted hover:bg-muted/80 transition-colors"
            >
              {preset.label}
            </button>
          ))}
        </motion.div>

        {/* Grid Visualization */}
        <motion.div
          className="relative mx-auto max-w-4xl"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
        >
          <div className="aspect-square rounded-xl border border-border bg-card/50 backdrop-blur-sm overflow-hidden p-2">
            {/* Simplified 64x64 preview (showing every 2nd cell) */}
            <div
              className="w-full h-full grid"
              style={{
                gridTemplateColumns: 'repeat(64, 1fr)',
                gridTemplateRows: 'repeat(64, 1fr)',
                gap: '1px',
              }}
            >
              {Array.from({ length: 64 * 64 }, (_, i) => {
                const displayRow = Math.floor(i / 64)
                const displayCol = i % 64
                const actualRow = displayRow * 2
                const actualCol = displayCol * 2
                const value = matrixData[actualRow]?.[actualCol] ?? 0
                const isHovered = hoveredCell?.row === actualRow && hoveredCell?.col === actualCol
                const isSelected = selectedCell?.row === actualRow && selectedCell?.col === actualCol

                return (
                  <div
                    key={i}
                    className={cn(
                      'rounded-[1px] cursor-pointer transition-all duration-75',
                      actualRow === 21 ? 'bg-orange-500/70' :
                      actualRow === 68 ? 'bg-purple-500/70' :
                      actualRow === 96 ? 'bg-green-500/70' :
                      value > 0 ? 'bg-blue-500/40' :
                      value < 0 ? 'bg-red-500/40' :
                      'bg-muted/20',
                      isHovered && 'ring-1 ring-primary scale-150 z-10',
                      isSelected && 'ring-2 ring-yellow-400'
                    )}
                    onMouseEnter={() => setHoveredCell({ row: actualRow, col: actualCol })}
                    onMouseLeave={() => setHoveredCell(null)}
                    onClick={() => {
                      const address = actualRow * 128 + actualCol
                      const cell = addressToCell(address)
                      if (cell) {
                        setSelectedCell(cell)
                        setAddressInput(address.toString())
                      }
                    }}
                  />
                )
              })}
            </div>
          </div>

          {/* Hover tooltip */}
          {hoveredCell && (
            <div className="absolute top-2 right-2 p-2 rounded-md bg-background/90 border border-border font-mono text-xs">
              Row {hoveredCell.row}, Col {hoveredCell.col}
            </div>
          )}
        </motion.div>

        {/* Special Rows Legend */}
        <motion.div
          className="mt-8 grid md:grid-cols-4 gap-4 max-w-4xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
        >
          {Object.entries(ANNA_MATRIX.specialRows).map(([rowNum, rowData]) => (
            <div
              key={rowNum}
              className="p-3 rounded-lg border border-border bg-card/50"
              style={{ borderLeftColor: rowData.color, borderLeftWidth: '4px' }}
            >
              <div className="font-bold">Row {rowNum}</div>
              <div className="text-sm text-muted-foreground">{rowData.name}</div>
              <div className="text-xs text-muted-foreground mt-1">{rowData.purpose}</div>
            </div>
          ))}
        </motion.div>

        {/* Grid Statistics */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
        >
          <h3 className="text-lg font-medium mb-4">Matrix Statistics</h3>
          <div className="flex flex-wrap justify-center gap-6 text-sm">
            <div>
              <span className="text-muted-foreground">Total Sentences:</span>{' '}
              <span className="font-bold">{ANNA_MATRIX.totalSentences.toLocaleString()}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Total Words:</span>{' '}
              <span className="font-bold">{ANNA_MATRIX.totalWords.toLocaleString()}</span>
            </div>
            <div>
              <span className="text-muted-foreground">7x7 Grid Hub:</span>{' '}
              <span className="font-bold">Column 6 ({ANNA_MATRIX.gridWordCluster.column6Hub.percentage}%)</span>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
