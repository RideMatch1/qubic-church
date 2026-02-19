'use client'

/**
 * SectionDivider - Premium section transitions
 * Variants: wave, gradient, stars, grid
 */

import { motion } from 'framer-motion'
import { memo, useMemo } from 'react'

type ColorTheme = 'purple' | 'cyan' | 'orange' | 'yellow' | 'pink'
type DividerVariant = 'wave' | 'gradient' | 'stars' | 'grid'

interface SectionDividerProps {
  variant?: DividerVariant
  fromColor?: ColorTheme
  toColor?: ColorTheme
  height?: number
  flip?: boolean
  className?: string
}

const colorValues: Record<ColorTheme, { primary: string; secondary: string }> = {
  purple: { primary: 'rgb(139, 92, 246)', secondary: 'rgba(139, 92, 246, 0.3)' },
  cyan: { primary: 'rgb(34, 211, 238)', secondary: 'rgba(34, 211, 238, 0.3)' },
  orange: { primary: 'rgb(249, 115, 22)', secondary: 'rgba(249, 115, 22, 0.3)' },
  yellow: { primary: 'rgb(234, 179, 8)', secondary: 'rgba(234, 179, 8, 0.3)' },
  pink: { primary: 'rgb(236, 72, 153)', secondary: 'rgba(236, 72, 153, 0.3)' },
}

// Wave SVG Divider
const WaveDivider = memo(function WaveDivider({
  fromColor,
  toColor,
  height,
  flip
}: {
  fromColor: ColorTheme
  toColor: ColorTheme
  height: number
  flip: boolean
}) {
  const from = colorValues[fromColor]
  const to = colorValues[toColor]
  const gradientId = `wave-gradient-${fromColor}-${toColor}`

  return (
    <div
      className={`relative w-full overflow-hidden ${flip ? 'rotate-180' : ''}`}
      style={{ height: `${height}px`, marginTop: '-1px', marginBottom: '-1px' }}
    >
      <svg
        viewBox="0 0 1440 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="absolute w-full h-full"
        preserveAspectRatio="none"
      >
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={from.primary} stopOpacity="0.5" />
            <stop offset="50%" stopColor={to.primary} stopOpacity="0.3" />
            <stop offset="100%" stopColor={to.primary} stopOpacity="0.5" />
          </linearGradient>
        </defs>

        {/* Main wave */}
        <motion.path
          d="M0,60 C240,120 480,0 720,60 C960,120 1200,0 1440,60 L1440,120 L0,120 Z"
          fill={`url(#${gradientId})`}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        />

        {/* Secondary wave (subtle) */}
        <motion.path
          d="M0,80 C360,40 720,100 1080,60 C1260,40 1350,80 1440,70 L1440,120 L0,120 Z"
          fill={from.secondary}
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 0.5 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.2 }}
        />
      </svg>

      {/* Glow effect */}
      <div
        className="absolute inset-0 blur-xl opacity-30"
        style={{
          background: `linear-gradient(90deg, ${from.secondary}, ${to.secondary})`
        }}
      />
    </div>
  )
})

// Gradient Fade Divider
const GradientDivider = memo(function GradientDivider({
  fromColor,
  toColor,
  height,
}: {
  fromColor: ColorTheme
  toColor: ColorTheme
  height: number
}) {
  const from = colorValues[fromColor]
  const to = colorValues[toColor]

  return (
    <div
      className="relative w-full"
      style={{ height: `${height}px` }}
    >
      {/* Top fade from previous section */}
      <div
        className="absolute top-0 left-0 right-0 h-1/2"
        style={{
          background: `linear-gradient(180deg, black 0%, transparent 100%)`
        }}
      />

      {/* Center glow */}
      <motion.div
        className="absolute inset-0 flex items-center justify-center"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 1 }}
      >
        <div
          className="w-full h-px"
          style={{
            background: `linear-gradient(90deg, transparent 0%, ${from.primary} 20%, ${to.primary} 80%, transparent 100%)`,
            boxShadow: `0 0 20px ${from.secondary}, 0 0 40px ${to.secondary}`
          }}
        />
      </motion.div>

      {/* Bottom fade to next section */}
      <div
        className="absolute bottom-0 left-0 right-0 h-1/2"
        style={{
          background: `linear-gradient(0deg, black 0%, transparent 100%)`
        }}
      />
    </div>
  )
})

// Stars Parallax Divider
const StarsDivider = memo(function StarsDivider({ height }: { height: number }) {
  const stars = useMemo(() =>
    Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 2 + 1,
      delay: Math.random() * 2,
      duration: 2 + Math.random() * 2,
    })),
    []
  )

  return (
    <div
      className="relative w-full overflow-hidden bg-black"
      style={{ height: `${height}px` }}
    >
      {/* Static gradient base */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-950/10 to-transparent" />

      {/* Stars */}
      {stars.map((star) => (
        <motion.div
          key={star.id}
          className="absolute rounded-full bg-white"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            width: `${star.size}px`,
            height: `${star.size}px`,
          }}
          animate={{
            opacity: [0.2, 0.8, 0.2],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: star.duration,
            delay: star.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}

      {/* Shooting star (occasional) */}
      <motion.div
        className="absolute h-px bg-gradient-to-r from-transparent via-white to-transparent"
        style={{ width: '100px', top: '30%' }}
        animate={{
          x: ['-100px', '1540px'],
          opacity: [0, 1, 0],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          repeatDelay: 8,
          ease: 'easeOut',
        }}
      />
    </div>
  )
})

// Grid Dissolve Divider
const GridDivider = memo(function GridDivider({
  fromColor,
  height
}: {
  fromColor: ColorTheme
  height: number
}) {
  const color = colorValues[fromColor]
  const gridSize = 20
  const cols = Math.ceil(1440 / gridSize)
  const rows = Math.ceil(height / gridSize)

  const cells = useMemo(() =>
    Array.from({ length: cols * rows }, (_, i) => ({
      id: i,
      col: i % cols,
      row: Math.floor(i / cols),
      delay: Math.random() * 0.5,
    })),
    [cols, rows]
  )

  return (
    <div
      className="relative w-full overflow-hidden"
      style={{ height: `${height}px` }}
    >
      <svg
        viewBox={`0 0 1440 ${height}`}
        className="absolute w-full h-full"
        preserveAspectRatio="none"
      >
        {cells.map((cell) => {
          const opacity = 1 - (cell.row / rows)
          return (
            <motion.rect
              key={cell.id}
              x={cell.col * gridSize}
              y={cell.row * gridSize}
              width={gridSize - 1}
              height={gridSize - 1}
              fill={color.primary}
              initial={{ opacity: 0 }}
              whileInView={{ opacity: opacity * 0.3 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: cell.delay }}
            />
          )
        })}
      </svg>

      {/* Fade overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black" />
    </div>
  )
})

export function SectionDivider({
  variant = 'gradient',
  fromColor = 'purple',
  toColor = 'cyan',
  height = 80,
  flip = false,
  className = '',
}: SectionDividerProps) {
  return (
    <div className={`relative ${className}`} aria-hidden="true">
      {variant === 'wave' && (
        <WaveDivider
          fromColor={fromColor}
          toColor={toColor}
          height={height}
          flip={flip}
        />
      )}
      {variant === 'gradient' && (
        <GradientDivider
          fromColor={fromColor}
          toColor={toColor}
          height={height}
        />
      )}
      {variant === 'stars' && (
        <StarsDivider height={height} />
      )}
      {variant === 'grid' && (
        <GridDivider fromColor={fromColor} height={height} />
      )}
    </div>
  )
}

export default SectionDivider
