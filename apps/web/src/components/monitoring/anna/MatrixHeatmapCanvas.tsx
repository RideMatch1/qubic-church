/**
 * MATRIX HEATMAP CANVAS - Component
 *
 * Fast canvas-based rendering of the 128×128 Anna Matrix.
 * Supports zoom, pan, and cell selection.
 */

'use client'

import { useRef, useEffect, useCallback, useState } from 'react'

// =============================================================================
// TYPES
// =============================================================================

interface MatrixHeatmapCanvasProps {
  matrix: number[][]
  selectedCell: [number, number] | null
  onCellClick: (row: number, col: number) => void
  zoom: number
}

// =============================================================================
// COLOR SCALE
// =============================================================================

function getHeatmapColor(value: number): string {
  // Normalize to -127 to +127 range
  const normalized = Math.max(-127, Math.min(127, value))

  if (normalized === 0) {
    return '#1e1e2e' // Dark gray for neutral
  } else if (normalized > 0) {
    // Positive: dark to orange
    const intensity = normalized / 127
    const r = Math.floor(30 + intensity * 219) // 30 -> 249
    const g = Math.floor(30 + intensity * 85)  // 30 -> 115
    const b = Math.floor(46 - intensity * 30)  // 46 -> 16
    return `rgb(${r}, ${g}, ${b})`
  } else {
    // Negative: dark to blue
    const intensity = Math.abs(normalized) / 127
    const r = Math.floor(30 - intensity * 20)   // 30 -> 10
    const g = Math.floor(30 + intensity * 70)   // 30 -> 100
    const b = Math.floor(46 + intensity * 190)  // 46 -> 236
    return `rgb(${r}, ${g}, ${b})`
  }
}

// =============================================================================
// MATRIX HEATMAP CANVAS
// =============================================================================

export function MatrixHeatmapCanvas({
  matrix,
  selectedCell,
  onCellClick,
  zoom,
}: MatrixHeatmapCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [hoveredCell, setHoveredCell] = useState<[number, number] | null>(null)

  // Base cell size
  const BASE_CELL_SIZE = 4
  const cellSize = BASE_CELL_SIZE * zoom
  const canvasSize = 128 * cellSize

  // Draw matrix
  const drawMatrix = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear canvas
    ctx.clearRect(0, 0, canvasSize, canvasSize)

    // Draw cells
    for (let row = 0; row < 128; row++) {
      for (let col = 0; col < 128; col++) {
        const value = matrix[row]?.[col] ?? 0
        const x = col * cellSize
        const y = row * cellSize

        // Cell background
        ctx.fillStyle = getHeatmapColor(value)
        ctx.fillRect(x, y, cellSize, cellSize)
      }
    }

    // Draw grid lines (only at higher zoom levels)
    if (zoom >= 1) {
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)'
      ctx.lineWidth = 0.5

      for (let i = 0; i <= 128; i++) {
        // Vertical lines
        ctx.beginPath()
        ctx.moveTo(i * cellSize, 0)
        ctx.lineTo(i * cellSize, canvasSize)
        ctx.stroke()

        // Horizontal lines
        ctx.beginPath()
        ctx.moveTo(0, i * cellSize)
        ctx.lineTo(canvasSize, i * cellSize)
        ctx.stroke()
      }
    }

    // Draw center crosshair (origin)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)'
    ctx.lineWidth = 1
    ctx.setLineDash([4, 4])

    // Vertical center line
    ctx.beginPath()
    ctx.moveTo(64 * cellSize, 0)
    ctx.lineTo(64 * cellSize, canvasSize)
    ctx.stroke()

    // Horizontal center line
    ctx.beginPath()
    ctx.moveTo(0, 64 * cellSize)
    ctx.lineTo(canvasSize, 64 * cellSize)
    ctx.stroke()

    ctx.setLineDash([])

    // Highlight hovered cell
    if (hoveredCell) {
      const [hRow, hCol] = hoveredCell
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)'
      ctx.lineWidth = 2
      ctx.strokeRect(hCol * cellSize, hRow * cellSize, cellSize, cellSize)
    }

    // Highlight selected cell
    if (selectedCell) {
      const [sRow, sCol] = selectedCell
      ctx.strokeStyle = '#22d3ee' // Cyan
      ctx.lineWidth = 2
      ctx.strokeRect(sCol * cellSize, sRow * cellSize, cellSize, cellSize)

      // Draw crosshair
      ctx.strokeStyle = 'rgba(34, 211, 238, 0.4)'
      ctx.lineWidth = 1

      // Vertical
      ctx.beginPath()
      ctx.moveTo(sCol * cellSize + cellSize / 2, 0)
      ctx.lineTo(sCol * cellSize + cellSize / 2, canvasSize)
      ctx.stroke()

      // Horizontal
      ctx.beginPath()
      ctx.moveTo(0, sRow * cellSize + cellSize / 2)
      ctx.lineTo(canvasSize, sRow * cellSize + cellSize / 2)
      ctx.stroke()
    }
  }, [matrix, selectedCell, hoveredCell, cellSize, canvasSize, zoom])

  // Draw on matrix or selection change
  useEffect(() => {
    drawMatrix()
  }, [drawMatrix])

  // Handle mouse move
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const scaleX = canvas.width / rect.width
    const scaleY = canvas.height / rect.height

    const x = (e.clientX - rect.left) * scaleX
    const y = (e.clientY - rect.top) * scaleY

    const col = Math.floor(x / cellSize)
    const row = Math.floor(y / cellSize)

    if (row >= 0 && row < 128 && col >= 0 && col < 128) {
      setHoveredCell([row, col])
    } else {
      setHoveredCell(null)
    }
  }, [cellSize])

  // Handle mouse leave
  const handleMouseLeave = useCallback(() => {
    setHoveredCell(null)
  }, [])

  // Handle click
  const handleClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const scaleX = canvas.width / rect.width
    const scaleY = canvas.height / rect.height

    const x = (e.clientX - rect.left) * scaleX
    const y = (e.clientY - rect.top) * scaleY

    const col = Math.floor(x / cellSize)
    const row = Math.floor(y / cellSize)

    if (row >= 0 && row < 128 && col >= 0 && col < 128) {
      onCellClick(row, col)
    }
  }, [cellSize, onCellClick])

  return (
    <div
      ref={containerRef}
      className="relative overflow-auto bg-black/50 rounded-lg"
      style={{ maxHeight: '500px' }}
    >
      <canvas
        ref={canvasRef}
        width={canvasSize}
        height={canvasSize}
        onClick={handleClick}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="cursor-crosshair"
        style={{
          width: canvasSize,
          height: canvasSize,
          imageRendering: 'pixelated',
        }}
      />

      {/* Hover tooltip */}
      {hoveredCell && (
        <div className="absolute top-2 left-2 px-2 py-1 bg-black/80 rounded text-xs text-white font-mono pointer-events-none">
          [{hoveredCell[0]}, {hoveredCell[1]}] = {matrix[hoveredCell[0]]?.[hoveredCell[1]] ?? 0}
        </div>
      )}

      {/* Axis labels */}
      <div className="absolute bottom-2 right-2 text-[10px] text-white/40 font-mono">
        128×128
      </div>
    </div>
  )
}

export default MatrixHeatmapCanvas
