'use client'

import { useRef, useEffect, useCallback, type ReactNode } from 'react'
import { motion, useInView } from 'framer-motion'
import { cn } from '@/lib/utils'
import { useJourneySafe, type SectionId } from './JourneyContainer'

interface JourneySectionProps {
  id: SectionId
  children: ReactNode
  className?: string
  minHeight?: string
  background?: 'black' | 'dark' | 'gradient' | 'transparent'
  onVisible?: () => void
  disableLiquidEther?: boolean
}

export function JourneySection({
  id,
  children,
  className,
  minHeight = 'min-h-screen',
  background = 'transparent', // Default to transparent for LiquidEther visibility
  onVisible,
}: JourneySectionProps) {
  const ref = useRef<HTMLElement>(null)
  const isInView = useInView(ref, {
    once: false,
    margin: '-20% 0px -20% 0px'
  })
  const journey = useJourneySafe()

  // Stable callback refs
  const onVisibleRef = useRef(onVisible)
  onVisibleRef.current = onVisible

  // Mark section as visited when it comes into view
  useEffect(() => {
    if (isInView) {
      journey?.markSectionVisited(id)
      onVisibleRef.current?.()
    }
  }, [isInView, id, journey])

  const backgroundClasses = {
    black: 'bg-transparent', // Fully transparent for LiquidEther
    dark: 'bg-transparent', // Fully transparent for LiquidEther
    gradient: 'bg-transparent', // Fully transparent for LiquidEther
    transparent: 'bg-transparent', // Fully transparent
  }

  return (
    <motion.section
      ref={ref}
      id={`journey-section-${id}`}
      className={cn(
        minHeight,
        'relative w-full overflow-hidden',
        backgroundClasses[background],
        className
      )}
      initial={{ opacity: 0 }}
      animate={{ opacity: isInView ? 1 : 0.3 }}
      transition={{ duration: 0.6 }}
    >
      {children}
    </motion.section>
  )
}

// Hook to track if current section is in view
export function useSectionInView(threshold = 0.3) {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, {
    once: false,
    amount: threshold
  })
  return { ref, isInView }
}
