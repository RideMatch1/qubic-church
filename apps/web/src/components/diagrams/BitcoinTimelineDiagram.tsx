'use client'

import { motion } from 'framer-motion'

export function BitcoinTimelineDiagram() {
  const blocks = [
    { num: 1, label: 'Genesis', date: 'Jan 3' },
    { num: 100, label: '', date: '' },
    { num: 283, label: 'HERE', date: 'Jan 12', highlight: true },
    { num: 500, label: '', date: '' },
    { num: 1000, label: '', date: 'Jan 20' },
  ]

  return (
    <div className="w-full max-w-md mx-auto">
      <svg viewBox="0 0 300 90" className="w-full h-auto">
        {/* Bitcoin logo at left */}
        <motion.g
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <circle cx="8" cy="40" r="7" fill="#F7931A" />
          <text x="8" y="43" textAnchor="middle" fill="white" fontSize="8" fontWeight="bold">₿</text>
        </motion.g>
        {/* Timeline base line */}
        <motion.line
          x1="20"
          y1="40"
          x2="280"
          y2="40"
          stroke="currentColor"
          strokeWidth="2"
          className="text-border"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1 }}
        />

        {/* Blocks */}
        {blocks.map((block, i) => {
          const x = 20 + (i * 260) / (blocks.length - 1)
          return (
            <motion.g
              key={block.num}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + i * 0.15 }}
            >
              {/* Block rectangle */}
              <rect
                x={x - 12}
                y="28"
                width="24"
                height="24"
                rx="3"
                fill={block.highlight ? 'currentColor' : 'none'}
                stroke="currentColor"
                strokeWidth={block.highlight ? 0 : 1.5}
                className={block.highlight ? 'text-orange-500' : 'text-muted-foreground'}
              />

              {/* Block number */}
              <text
                x={x}
                y="44"
                textAnchor="middle"
                className={`text-[8px] font-mono ${
                  block.highlight ? 'fill-white font-bold' : 'fill-muted-foreground'
                }`}
              >
                #{block.num}
              </text>

              {/* Date label below */}
              {block.date && (
                <text
                  x={x}
                  y="65"
                  textAnchor="middle"
                  className="text-[6px] fill-muted-foreground"
                >
                  {block.date}
                </text>
              )}

              {/* Special label above */}
              {block.label && (
                <motion.g
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.2 }}
                >
                  {block.highlight && (
                    <motion.path
                      d={`M${x} 18 L${x} 24`}
                      stroke="currentColor"
                      strokeWidth="1.5"
                      className="text-orange-500"
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: 1 }}
                      transition={{ delay: 1.3 }}
                    />
                  )}
                  <text
                    x={x}
                    y="14"
                    textAnchor="middle"
                    className={`text-[7px] font-bold ${
                      block.highlight ? 'fill-orange-500' : 'fill-muted-foreground'
                    }`}
                  >
                    {block.label}
                  </text>
                </motion.g>
              )}
            </motion.g>
          )
        })}

        {/* Year label */}
        <motion.text
          x="150"
          y="76"
          textAnchor="middle"
          className="text-[7px] fill-muted-foreground font-medium"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
        >
          January 2009 - The First Weeks of Bitcoin
        </motion.text>
      </svg>
    </div>
  )
}
