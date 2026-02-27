'use client'

import { useEffect, useState, useRef } from 'react'
import { useInView } from 'framer-motion'

/**
 * Animated counter that counts from 0 to target when element scrolls into view.
 * Uses cubic ease-out for a premium deceleration feel.
 */
export function useCountUp(target: number, duration = 2000) {
  const [count, setCount] = useState(0)
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })
  const hasAnimated = useRef(false)

  useEffect(() => {
    if (!isInView || hasAnimated.current || target <= 0) return
    hasAnimated.current = true

    const startTime = Date.now()
    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setCount(Math.floor(eased * target))
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [isInView, target, duration])

  return { count, ref }
}
