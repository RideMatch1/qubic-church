'use client'

/**
 * NeuralDecoration - Transparent SVG neural network patterns
 * Positioned as background decorative elements to add visual depth.
 * All elements are pointer-events-none and semi-transparent.
 */

import { memo } from 'react'
import { motion } from 'framer-motion'

/**
 * Neural network nodes connected by synapses.
 * Renders an abstract neural cluster in SVG.
 */
export const NeuralCluster = memo(function NeuralCluster({
  className = '',
  opacity = 0.06,
  scale = 1,
}: {
  className?: string
  opacity?: number
  scale?: number
}) {
  // Deterministic node positions for a neural cluster
  const nodes = [
    // Input layer
    { x: 40, y: 80, r: 3 },
    { x: 40, y: 160, r: 2.5 },
    { x: 40, y: 240, r: 3.5 },
    { x: 40, y: 320, r: 2 },
    // Hidden layer 1
    { x: 160, y: 120, r: 4 },
    { x: 160, y: 200, r: 3 },
    { x: 160, y: 280, r: 3.5 },
    // Hidden layer 2
    { x: 280, y: 140, r: 3 },
    { x: 280, y: 220, r: 4.5 },
    { x: 280, y: 300, r: 2.5 },
    // Output layer
    { x: 400, y: 180, r: 3.5 },
    { x: 400, y: 260, r: 3 },
  ]

  // Connections between layers
  const connections: [number, number][] = [
    // Input -> Hidden 1
    [0, 4], [0, 5], [1, 4], [1, 5], [1, 6], [2, 5], [2, 6], [3, 6],
    // Hidden 1 -> Hidden 2
    [4, 7], [4, 8], [5, 7], [5, 8], [5, 9], [6, 8], [6, 9],
    // Hidden 2 -> Output
    [7, 10], [7, 11], [8, 10], [8, 11], [9, 10], [9, 11],
  ]

  return (
    <div
      className={`absolute pointer-events-none ${className}`}
      style={{ opacity }}
    >
      <svg
        viewBox="0 0 440 400"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ width: 440 * scale, height: 400 * scale }}
      >
        {/* Connections */}
        {connections.map(([from, to], i) => {
          const a = nodes[from]!
          const b = nodes[to]!
          return (
            <line
              key={`c-${i}`}
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              stroke="white"
              strokeWidth={0.5}
              strokeOpacity={0.4}
            />
          )
        })}

        {/* Nodes */}
        {nodes.map((node, i) => (
          <g key={`n-${i}`}>
            {/* Outer glow */}
            <circle
              cx={node.x}
              cy={node.y}
              r={node.r * 3}
              fill="white"
              fillOpacity={0.05}
            />
            {/* Node */}
            <circle
              cx={node.x}
              cy={node.y}
              r={node.r}
              fill="white"
              fillOpacity={0.6}
            />
          </g>
        ))}
      </svg>
    </div>
  )
})

/**
 * Animated synapse pulse - a line that pulses along a neural pathway.
 */
export const SynapsePulse = memo(function SynapsePulse({
  className = '',
  direction = 'right',
  opacity = 0.04,
}: {
  className?: string
  direction?: 'right' | 'left'
  opacity?: number
}) {
  return (
    <div
      className={`absolute pointer-events-none overflow-hidden ${className}`}
      style={{ opacity }}
    >
      <svg
        viewBox="0 0 600 80"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full"
      >
        {/* Base pathway */}
        <path
          d="M0 40 C100 20, 200 60, 300 40 C400 20, 500 60, 600 40"
          stroke="white"
          strokeWidth={0.5}
          strokeOpacity={0.3}
        />

        {/* Animated pulse dot */}
        <motion.circle
          r={3}
          fill="white"
          fillOpacity={0.8}
          animate={{
            offsetDistance: direction === 'right' ? ['0%', '100%'] : ['100%', '0%'],
          }}
          transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
          style={{
            offsetPath: 'path("M0 40 C100 20, 200 60, 300 40 C400 20, 500 60, 600 40")',
          }}
        />

        {/* Small branching nodes along the path */}
        {[100, 200, 300, 400, 500].map((x, i) => (
          <circle
            key={i}
            cx={x}
            cy={40 + (i % 2 === 0 ? -10 : 10)}
            r={1.5}
            fill="white"
            fillOpacity={0.3}
          />
        ))}
      </svg>
    </div>
  )
})

/**
 * Hexagonal matrix grid - subtle tech pattern
 */
export const HexGrid = memo(function HexGrid({
  className = '',
  opacity = 0.03,
  rows = 6,
  cols = 8,
}: {
  className?: string
  opacity?: number
  rows?: number
  cols?: number
}) {
  const hexSize = 30
  const hexWidth = hexSize * 2
  const hexHeight = Math.sqrt(3) * hexSize

  const hexagons: { x: number; y: number }[] = []
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const x = col * hexWidth * 0.75 + hexSize
      const y = row * hexHeight + (col % 2 === 1 ? hexHeight / 2 : 0) + hexSize
      hexagons.push({ x, y })
    }
  }

  const hexPath = (cx: number, cy: number) => {
    const points = []
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i - Math.PI / 6
      points.push(`${cx + hexSize * Math.cos(angle)},${cy + hexSize * Math.sin(angle)}`)
    }
    return `M${points.join('L')}Z`
  }

  return (
    <div
      className={`absolute pointer-events-none ${className}`}
      style={{ opacity }}
    >
      <svg
        viewBox={`0 0 ${cols * hexWidth * 0.75 + hexSize} ${rows * hexHeight + hexHeight}`}
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full"
      >
        {hexagons.map((hex, i) => (
          <path
            key={i}
            d={hexPath(hex.x, hex.y)}
            stroke="white"
            strokeWidth={0.5}
            strokeOpacity={0.5}
            fill="white"
            fillOpacity={0.02}
          />
        ))}
      </svg>
    </div>
  )
})
