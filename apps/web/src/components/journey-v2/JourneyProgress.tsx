'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { useJourney } from './JourneyContainer'
import { useGamificationSafe, ACHIEVEMENTS } from '@/components/gamification/GamificationProvider'
import { Trophy } from 'lucide-react'

interface JourneyProgressProps {
  className?: string
  position?: 'left' | 'right'
  showLabels?: boolean
  showGamification?: boolean
}

export function JourneyProgress({
  className,
  position = 'right',
  showLabels = false,
  showGamification = true,
}: JourneyProgressProps) {
  const { currentSection, currentIndex, scrollProgress, visitedSections, scrollToSection, sections } = useJourney()
  const gamification = useGamificationSafe()

  const totalAchievements = Object.keys(ACHIEVEMENTS).length
  const unlockedCount = gamification?.state.unlockedAchievements.length ?? 0

  return (
    <div
      className={cn(
        'fixed top-1/2 -translate-y-1/2 z-50 flex flex-col items-center gap-3',
        position === 'right' ? 'right-4 md:right-6' : 'left-4 md:left-6',
        className
      )}
      role="navigation"
      aria-label="Journey navigation"
    >
      {/* Progress line background */}
      <div className="absolute left-1/2 -translate-x-1/2 w-px h-full bg-white/10" />

      {/* Progress line fill */}
      <motion.div
        className="absolute left-1/2 -translate-x-1/2 w-px bg-gradient-to-b from-orange-500/80 to-purple-500/80 origin-top"
        style={{ height: `${scrollProgress * 100}%`, top: 0 }}
        transition={{ type: 'spring', stiffness: 100, damping: 30 }}
      />

      {/* Section dots */}
      {sections.map((section, index) => {
        const isActive = index === currentIndex
        const isVisited = visitedSections.has(section.id)
        const isPast = index < currentIndex

        return (
          <button
            key={section.id}
            onClick={() => scrollToSection(section.id)}
            className={cn(
              'relative group flex items-center gap-3 z-10',
              position === 'right' ? 'flex-row-reverse' : 'flex-row'
            )}
            aria-label={`Go to ${section.name}`}
          >
            {/* Dot */}
            <motion.div
              className={cn(
                'relative w-2.5 h-2.5 rounded-full border transition-all duration-300',
                isActive && 'border-orange-500 bg-orange-500 scale-150',
                isPast && isVisited && 'border-orange-500/60 bg-orange-500/40',
                !isActive && !isPast && isVisited && 'border-white/40 bg-white/20',
                !isActive && !isVisited && 'border-white/20 bg-transparent'
              )}
              whileHover={{ scale: 1.5 }}
              whileTap={{ scale: 0.9 }}
            >
              {/* Active pulse */}
              {isActive && (
                <motion.div
                  className="absolute inset-0 rounded-full bg-orange-500"
                  animate={{
                    scale: [1, 2, 1],
                    opacity: [0.5, 0, 0.5],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                />
              )}
            </motion.div>

            {/* Label (on hover) */}
            <motion.span
              className={cn(
                'text-xs font-medium whitespace-nowrap px-2 py-1 rounded bg-black/80 backdrop-blur-sm',
                isActive ? 'text-orange-400' : 'text-white/60',
                !showLabels && 'opacity-0 group-hover:opacity-100',
                'transition-opacity duration-200'
              )}
            >
              {section.name}
            </motion.span>
          </button>
        )
      })}

      {/* Gamification Counter */}
      {showGamification && gamification && (
        <motion.div
          className="mt-4 flex items-center gap-1.5 px-2 py-1 rounded-full bg-black/60 backdrop-blur-sm border border-white/10"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5 }}
          aria-label={`${unlockedCount} of ${totalAchievements} achievements unlocked`}
        >
          <Trophy className="h-3 w-3 text-yellow-400" aria-hidden="true" />
          <span className="text-[10px] font-mono text-white/60">
            {unlockedCount}/{totalAchievements}
          </span>
        </motion.div>
      )}
    </div>
  )
}

/**
 * Compact progress bar for mobile
 */
export function JourneyProgressBar({ className }: { className?: string }) {
  const { scrollProgress, currentSection, sections } = useJourney()
  const currentSectionData = sections.find(s => s.id === currentSection)

  return (
    <div
      className={cn('fixed top-0 left-0 right-0 z-50', className)}
      role="progressbar"
      aria-valuenow={Math.round(scrollProgress * 100)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Journey progress: ${Math.round(scrollProgress * 100)}%`}
    >
      {/* Progress bar */}
      <div className="h-0.5 bg-white/10">
        <motion.div
          className="h-full bg-gradient-to-r from-orange-500 to-purple-500"
          style={{ width: `${scrollProgress * 100}%` }}
          transition={{ type: 'spring', stiffness: 100, damping: 20 }}
        />
      </div>

      {/* Section name */}
      <motion.div
        className="absolute top-2 left-4 text-xs text-white/50 font-medium"
        key={currentSection}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        aria-live="polite"
      >
        {currentSectionData?.name}
      </motion.div>
    </div>
  )
}

/**
 * Hook for reduced motion support
 */
export function useReducedMotion(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}
