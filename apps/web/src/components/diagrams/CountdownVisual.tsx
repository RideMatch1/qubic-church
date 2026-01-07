'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

interface CountdownVisualProps {
  size?: 'small' | 'large'
}

export function CountdownVisual({ size = 'large' }: CountdownVisualProps) {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  })

  useEffect(() => {
    const targetDate = new Date('2026-03-03T00:00:00Z')

    const updateCountdown = () => {
      const now = new Date()
      const diff = Math.max(0, targetDate.getTime() - now.getTime())

      setTimeLeft({
        days: Math.floor(diff / (1000 * 60 * 60 * 24)),
        hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
        minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
        seconds: Math.floor((diff % (1000 * 60)) / 1000),
      })
    }

    updateCountdown()
    const interval = setInterval(updateCountdown, 1000)
    return () => clearInterval(interval)
  }, [])

  if (size === 'small') {
    return (
      <div className="flex items-center gap-2 font-mono">
        <span className="text-lg font-bold text-amber-500">{timeLeft.days}</span>
        <span className="text-sm text-muted-foreground">days</span>
        <span className="text-lg font-bold text-amber-500">{timeLeft.hours}</span>
        <span className="text-sm text-muted-foreground">hrs</span>
        <span className="text-lg font-bold text-amber-500">{timeLeft.minutes}</span>
        <span className="text-sm text-muted-foreground">min</span>
      </div>
    )
  }

  return (
    <motion.div
      className="w-full max-w-sm mx-auto"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Target date with Qubic logo */}
      <div className="text-center mb-4">
        <div className="flex items-center justify-center gap-2 mb-1">
          <img src="/logos/qubic.png" alt="Qubic" className="w-5 h-5" />
          <div className="text-xs text-muted-foreground uppercase tracking-wider">Time-Lock Event</div>
        </div>
        <div className="text-xl font-bold text-amber-500">March 3, 2026</div>
      </div>

      {/* Countdown boxes */}
      <div className="grid grid-cols-4 gap-2">
        {[
          { value: timeLeft.days, label: 'Days' },
          { value: timeLeft.hours, label: 'Hours' },
          { value: timeLeft.minutes, label: 'Minutes' },
          { value: timeLeft.seconds, label: 'Seconds' },
        ].map((item, i) => (
          <motion.div
            key={item.label}
            className="relative"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <div className="bg-gradient-to-b from-amber-900/30 to-amber-950/50 rounded-lg border border-amber-500/30 p-3 text-center">
              <motion.div
                className="text-2xl md:text-3xl font-mono font-bold text-amber-400"
                key={item.value}
                initial={{ scale: 1.1 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.2 }}
              >
                {item.value.toString().padStart(2, '0')}
              </motion.div>
              <div className="text-[10px] text-amber-500/70 uppercase tracking-wider mt-1">
                {item.label}
              </div>
            </div>

            {/* Pulsing dot */}
            {item.label === 'Seconds' && (
              <motion.div
                className="absolute -top-1 -right-1 w-2 h-2 bg-amber-500 rounded-full"
                animate={{
                  scale: [1, 1.5, 1],
                  opacity: [1, 0.5, 1],
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />
            )}
          </motion.div>
        ))}
      </div>

      {/* Status indicator */}
      <motion.div
        className="mt-4 flex items-center justify-center gap-2 text-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <motion.div
          className="w-2 h-2 bg-amber-500 rounded-full"
          animate={{
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        <span className="text-muted-foreground">Time-Lock Active</span>
      </motion.div>
    </motion.div>
  )
}
