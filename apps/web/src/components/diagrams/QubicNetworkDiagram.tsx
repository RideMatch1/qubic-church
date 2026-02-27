'use client'

import { motion } from 'framer-motion'

// Pre-computed node positions to avoid hydration mismatches from floating-point precision
const nodes = [
  { id: 0, x: 85, y: 50 },
  { id: 1, x: 80.31, y: 67.5 },
  { id: 2, x: 67.5, y: 80.31 },
  { id: 3, x: 50, y: 85 },
  { id: 4, x: 32.5, y: 80.31 },
  { id: 5, x: 19.69, y: 67.5 },
  { id: 6, x: 15, y: 50 },
  { id: 7, x: 19.69, y: 32.5 },
  { id: 8, x: 32.5, y: 19.69 },
  { id: 9, x: 50, y: 15 },
  { id: 10, x: 67.5, y: 19.69 },
  { id: 11, x: 80.31, y: 32.5 },
]

export function QubicNetworkDiagram() {
  return (
    <div className="w-full max-w-xs mx-auto">
      <svg viewBox="0 0 100 120" className="w-full h-auto">
        {/* Connection lines */}
        {nodes.map((node, i) =>
          nodes.slice(i + 1).map((otherNode, j) => (
            <motion.line
              key={`${i}-${j}`}
              x1={node.x}
              y1={node.y}
              x2={otherNode.x}
              y2={otherNode.y}
              stroke="currentColor"
              strokeWidth="0.3"
              className="text-primary/20"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ duration: 1, delay: 0.5 + i * 0.05 }}
            />
          ))
        )}

        {/* Qubic Logo in center */}
        <motion.g
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <image href="/logos/qubic.png" x="38" y="38" width="24" height="24" />
        </motion.g>

        {/* Computer nodes */}
        {nodes.map((node, i) => (
          <motion.g key={node.id}>
            <motion.rect
              x={node.x - 4}
              y={node.y - 3}
              width="8"
              height="6"
              rx="1"
              fill="currentColor"
              className="text-[#D4AF37]"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3, delay: 0.8 + i * 0.05 }}
            />
            <motion.rect
              x={node.x - 2}
              y={node.y + 3}
              width="4"
              height="1"
              fill="currentColor"
              className="text-[#D4AF37]"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3, delay: 0.9 + i * 0.05 }}
            />
          </motion.g>
        ))}

        {/* Labels */}
        <motion.text
          x="50"
          y="75"
          textAnchor="middle"
          className="text-[4px] fill-muted-foreground font-medium"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
        >
          50,000+ Computers
        </motion.text>

        {/* Arrow down */}
        <motion.path
          d="M50 82 L50 90 M46 86 L50 90 L54 86"
          fill="none"
          stroke="currentColor"
          strokeWidth="1"
          className="text-primary"
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.7 }}
        />

        {/* Brain icon */}
        <motion.circle
          cx="50"
          cy="100"
          r="8"
          fill="currentColor"
          className="text-[#D4AF37]/20"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 1.9 }}
        />
        <motion.text
          x="50"
          y="103"
          textAnchor="middle"
          className="text-[6px] fill-[#D4AF37]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
        >
          AI
        </motion.text>

        <motion.text
          x="50"
          y="115"
          textAnchor="middle"
          className="text-[3.5px] fill-muted-foreground"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2.2 }}
        >
          One Distributed Brain
        </motion.text>
      </svg>
    </div>
  )
}
