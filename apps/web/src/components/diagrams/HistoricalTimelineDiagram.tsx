'use client'

import { motion } from 'framer-motion'

export function HistoricalTimelineDiagram() {
  const events = [
    { date: 'Jan 3, 2009', label: 'Bitcoin Created', color: 'orange', position: 10 },
    { date: 'Jan 12, 2009', label: 'Block #283', color: 'orange', position: 25 },
    { date: '2024', label: 'Qubic Launched', color: 'purple', position: 70 },
    { date: 'Mar 3, 2026', label: 'Time-Lock Opens', color: 'green', position: 90 },
  ]

  return (
    <div className="w-full max-w-lg mx-auto px-4">
      <svg viewBox="0 0 400 100" className="w-full h-auto" preserveAspectRatio="xMidYMid meet">
        {/* Timeline base line */}
        <motion.line
          x1="40"
          y1="50"
          x2="360"
          y2="50"
          stroke="currentColor"
          strokeWidth="2"
          className="text-border"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.5 }}
        />

        {/* Events */}
        {events.map((event, i) => {
          const x = 40 + (event.position * 320) / 100
          const isTop = i % 2 === 0

          return (
            <motion.g
              key={i}
              initial={{ opacity: 0, y: isTop ? -10 : 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + i * 0.3 }}
            >
              {/* Dot on timeline */}
              <circle
                cx={x}
                cy="50"
                r="6"
                fill="currentColor"
                className={
                  event.color === 'orange'
                    ? 'text-orange-500'
                    : event.color === 'purple'
                    ? 'text-purple-500'
                    : 'text-green-500'
                }
              />

              {/* Connecting line */}
              <line
                x1={x}
                y1={isTop ? 40 : 60}
                x2={x}
                y2={isTop ? 25 : 75}
                stroke="currentColor"
                strokeWidth="1"
                strokeDasharray="2 1"
                className="text-muted-foreground"
              />

              {/* Label */}
              <text
                x={x}
                y={isTop ? 18 : 88}
                textAnchor="middle"
                className="text-[8px] fill-foreground font-medium"
              >
                {event.label}
              </text>
              <text
                x={x}
                y={isTop ? 8 : 96}
                textAnchor="middle"
                className="text-[6px] fill-muted-foreground"
              >
                {event.date}
              </text>
            </motion.g>
          )
        })}

        {/* 15 years gap indicator */}
        <motion.g
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
        >
          <path
            d="M120 50 Q200 30 264 50"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            strokeDasharray="3 2"
            className="text-primary/40"
          />
          <text
            x="192"
            y="28"
            textAnchor="middle"
            className="text-[6px] fill-primary"
          >
            15 Years
          </text>
        </motion.g>
      </svg>
    </div>
  )
}
