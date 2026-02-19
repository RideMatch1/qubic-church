'use client'

import { motion } from 'framer-motion'

interface FibonacciSpiralProps {
  size?: number
  className?: string
}

function buildSpiralPath(scale: number): string {
  // Fibonacci sequence for quarter-circle arc radii
  const fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
  const segments: string[] = []

  let x = 0
  let y = 0
  // Direction cycle: right, up, left, down
  const dx = [1, 0, -1, 0]
  const dy = [0, -1, 0, 1]

  for (let i = 0; i < fib.length; i++) {
    const r = fib[i]! * scale
    const dir = i % 4

    // Arc endpoint
    const ex = x + (dx[dir]! + dx[(dir + 1) % 4]!) * r
    const ey = y + (dy[dir]! + dy[(dir + 1) % 4]!) * r

    // SVG arc: sweep flag alternates
    const sweep = 1
    if (i === 0) {
      segments.push(`M ${x} ${y}`)
    }
    segments.push(`A ${r} ${r} 0 0 ${sweep} ${ex} ${ey}`)

    x = ex
    y = ey
  }

  return segments.join(' ')
}

export function FibonacciSpiral({
  size = 500,
  className,
}: FibonacciSpiralProps) {
  const scale = size / 180
  const d = buildSpiralPath(scale)

  // Also draw the golden rectangle subdivisions
  const fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
  const totalSize = fib[fib.length - 1]! * scale

  return (
    <motion.svg
      width={size}
      height={size}
      viewBox={`${-totalSize * 0.6} ${-totalSize * 0.8} ${totalSize * 2} ${totalSize * 2}`}
      className={className}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 2, delay: 1 }}
    >
      {/* Outer circle */}
      <motion.circle
        cx={0}
        cy={0}
        r={totalSize * 0.85}
        fill="none"
        stroke="white"
        strokeWidth={1.5}
        opacity={0.5}
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 3, delay: 0.5, ease: 'easeOut' }}
      />

      {/* Spiral path */}
      <motion.path
        d={d}
        fill="none"
        stroke="white"
        strokeWidth={2}
        strokeLinecap="round"
        opacity={0.6}
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 4, delay: 1, ease: 'easeInOut' }}
      />

      {/* Golden rectangle grid lines */}
      {fib.slice(4, 8).map((f, i) => {
        const s = f * scale
        return (
          <motion.rect
            key={i}
            x={-s * 0.3}
            y={-s * 0.3}
            width={s}
            height={s}
            fill="none"
            stroke="white"
            strokeWidth={0.75}
            opacity={0.25}
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.25 }}
            transition={{ duration: 1, delay: 2 + i * 0.3 }}
          />
        )
      })}
    </motion.svg>
  )
}
