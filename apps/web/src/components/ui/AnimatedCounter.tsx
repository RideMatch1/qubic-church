'use client'

import React, { useEffect, useRef, useState } from 'react'
import { motion, useInView } from 'framer-motion'
import { useCounterOnView, useReducedMotion } from '@/lib/hooks'

interface AnimatedCounterProps {
  value: number
  duration?: number
  delay?: number
  suffix?: string
  prefix?: string
  separator?: string
  decimals?: number
  triggerOnView?: boolean
  className?: string
  onComplete?: () => void
}

export function AnimatedCounter({
  value,
  duration = 2000,
  delay = 0,
  suffix = '',
  prefix = '',
  separator = ',',
  decimals = 0,
  triggerOnView = true,
  className = '',
  onComplete,
}: AnimatedCounterProps) {
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })
  const prefersReducedMotion = useReducedMotion()

  const { count, triggerAnimation, hasAnimated } = useCounterOnView({
    start: 0,
    end: value,
    duration: prefersReducedMotion ? 0 : duration,
    delay,
    easing: 'easeOutExpo',
    onComplete,
  })

  // Auto-start when in view
  useEffect(() => {
    if (triggerOnView && isInView && !hasAnimated) {
      triggerAnimation()
    }
  }, [isInView, triggerOnView, hasAnimated, triggerAnimation])

  // Format number with separator
  const formatNumber = (num: number): string => {
    if (decimals > 0) {
      return num.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, separator)
    }
    return Math.round(num).toString().replace(/\B(?=(\d{3})+(?!\d))/g, separator)
  }

  return (
    <span ref={ref} className={`font-mono tabular-nums ${className}`}>
      {prefix}
      {formatNumber(prefersReducedMotion ? value : count)}
      {suffix}
    </span>
  )
}

// Countdown variant
export function AnimatedCountdown({
  targetDate,
  showDays = true,
  showHours = true,
  showMinutes = true,
  showSeconds = true,
  className = '',
  onComplete,
}: {
  targetDate: Date
  showDays?: boolean
  showHours?: boolean
  showMinutes?: boolean
  showSeconds?: boolean
  className?: string
  onComplete?: () => void
}) {
  const [timeLeft, setTimeLeft] = React.useState(calculateTimeLeft())

  function calculateTimeLeft() {
    const difference = targetDate.getTime() - Date.now()
    if (difference <= 0) {
      return { days: 0, hours: 0, minutes: 0, seconds: 0, total: 0 }
    }

    return {
      days: Math.floor(difference / (1000 * 60 * 60 * 24)),
      hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
      minutes: Math.floor((difference / 1000 / 60) % 60),
      seconds: Math.floor((difference / 1000) % 60),
      total: difference,
    }
  }

  React.useEffect(() => {
    const timer = setInterval(() => {
      const newTimeLeft = calculateTimeLeft()
      setTimeLeft(newTimeLeft)

      if (newTimeLeft.total <= 0) {
        clearInterval(timer)
        onComplete?.()
      }
    }, 1000)

    return () => clearInterval(timer)
  }, [targetDate, onComplete])

  const TimeUnit = ({ value, label }: { value: number; label: string }) => (
    <div className="flex flex-col items-center">
      <motion.span
        key={value}
        initial={{ y: -10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="text-2xl md:text-4xl font-mono font-bold"
      >
        {value.toString().padStart(2, '0')}
      </motion.span>
      <span className="text-xs text-muted-foreground uppercase tracking-wider">
        {label}
      </span>
    </div>
  )

  const Separator = () => (
    <span className="text-2xl md:text-4xl font-mono text-muted-foreground mx-1">:</span>
  )

  return (
    <div className={`flex items-center justify-center gap-2 ${className}`}>
      {showDays && (
        <>
          <TimeUnit value={timeLeft.days} label="Days" />
          <Separator />
        </>
      )}
      {showHours && (
        <>
          <TimeUnit value={timeLeft.hours} label="Hours" />
          <Separator />
        </>
      )}
      {showMinutes && (
        <>
          <TimeUnit value={timeLeft.minutes} label="Mins" />
          {showSeconds && <Separator />}
        </>
      )}
      {showSeconds && <TimeUnit value={timeLeft.seconds} label="Secs" />}
    </div>
  )
}

// Stat display with counter
export function StatCounter({
  value,
  label,
  prefix = '',
  suffix = '',
  icon,
  description,
  trend,
  className = '',
}: {
  value: number
  label: string
  prefix?: string
  suffix?: string
  icon?: React.ReactNode
  description?: string
  trend?: { value: number; isPositive: boolean }
  className?: string
}) {
  return (
    <div className={`text-center ${className}`}>
      {icon && (
        <div className="flex justify-center mb-2 text-muted-foreground">
          {icon}
        </div>
      )}
      <div className="text-3xl md:text-4xl font-bold">
        <AnimatedCounter
          value={value}
          prefix={prefix}
          suffix={suffix}
          duration={2500}
        />
      </div>
      <div className="text-sm text-muted-foreground mt-1">{label}</div>
      {description && (
        <div className="text-xs text-muted-foreground/70 mt-0.5">{description}</div>
      )}
      {trend && (
        <div
          className={`text-xs mt-1 ${
            trend.isPositive ? 'text-verified' : 'text-destructive'
          }`}
        >
          {trend.isPositive ? '+' : '-'}{trend.value}%
        </div>
      )}
    </div>
  )
}
