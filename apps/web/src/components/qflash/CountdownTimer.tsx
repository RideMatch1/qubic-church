'use client'

import { useState, useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'

interface CountdownTimerProps {
  targetTime: string // ISO 8601
  label?: string
  onComplete?: () => void
}

export function CountdownTimer({ targetTime, label, onComplete }: CountdownTimerProps) {
  const [secondsLeft, setSecondsLeft] = useState(() => calcSeconds(targetTime))
  const completedRef = useRef(false)

  useEffect(() => {
    completedRef.current = false
    setSecondsLeft(calcSeconds(targetTime))

    const timer = setInterval(() => {
      const remaining = calcSeconds(targetTime)
      setSecondsLeft(remaining)

      if (remaining <= 0 && !completedRef.current) {
        completedRef.current = true
        onComplete?.()
      }
    }, 100) // 100ms for smooth countdown

    return () => clearInterval(timer)
  }, [targetTime, onComplete])

  if (secondsLeft <= 0) {
    return (
      <div className="text-center">
        {label && <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">{label}</p>}
        <div className="text-2xl font-mono font-bold text-muted-foreground">
          0:00
        </div>
      </div>
    )
  }

  const mins = Math.floor(secondsLeft / 60)
  const secs = Math.floor(secondsLeft % 60)
  const tenths = Math.floor((secondsLeft % 1) * 10)

  // Urgency levels
  const isUrgent = secondsLeft <= 10
  const isCritical = secondsLeft <= 5

  return (
    <div className="text-center">
      {label && (
        <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">
          {label}
        </p>
      )}
      <div
        className={cn(
          'text-3xl font-mono font-bold tabular-nums transition-colors',
          isCritical
            ? 'text-red-400 animate-pulse'
            : isUrgent
              ? 'text-amber-400'
              : 'text-foreground',
        )}
      >
        {mins}:{secs.toString().padStart(2, '0')}
        <span className="text-lg opacity-60">.{tenths}</span>
      </div>
    </div>
  )
}

function calcSeconds(targetTime: string): number {
  const target = new Date(targetTime).getTime()
  const now = Date.now()
  return Math.max(0, (target - now) / 1000)
}
