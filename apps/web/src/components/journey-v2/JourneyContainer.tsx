'use client'

import { createContext, useContext, useState, useEffect, useCallback, useMemo, useRef, type ReactNode } from 'react'
import dynamic from 'next/dynamic'

// Dynamic import for LiquidEther with error fallback
const LiquidEther = dynamic(() => import('@/components/LiquidEther'), {
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-black" />,
})

// Section configuration
export const JOURNEY_SECTIONS = [
  { id: 'void', name: 'The Void', index: 0 },
  { id: 'genesis', name: 'The Genesis', index: 1 },
  { id: 'formula', name: 'The Formula', index: 2 },
  { id: 'patoshi', name: 'The Patoshi', index: 3 },
  { id: 'bridge', name: 'The Bridge', index: 4 },
  { id: 'matrix', name: 'The Matrix', index: 5 },
  { id: 'network', name: 'The Network', index: 6 },
  { id: 'countdown', name: 'The Countdown', index: 7 },
  { id: 'evidence', name: 'The Evidence', index: 8 },
  { id: 'call', name: 'The Call', index: 9 },
] as const

export type SectionId = typeof JOURNEY_SECTIONS[number]['id']

interface JourneyContextType {
  currentSection: SectionId
  currentIndex: number
  totalSections: number
  scrollProgress: number
  visitedSections: Set<SectionId>
  markSectionVisited: (id: SectionId) => void
  scrollToSection: (id: SectionId) => void
  sections: typeof JOURNEY_SECTIONS
}

const JourneyContext = createContext<JourneyContextType | null>(null)

export function useJourney() {
  const context = useContext(JourneyContext)
  if (!context) {
    throw new Error('useJourney must be used within JourneyContainer')
  }
  return context
}

// Safe hook that doesn't throw
export function useJourneySafe() {
  return useContext(JourneyContext)
}

interface JourneyContainerProps {
  children: ReactNode
}

export function JourneyContainer({ children }: JourneyContainerProps) {
  const [currentSection, setCurrentSection] = useState<SectionId>('void')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [scrollProgress, setScrollProgress] = useState(0)
  // Use ref for Set to avoid re-renders, and counter to trigger updates only when needed
  const visitedSectionsRef = useRef<Set<SectionId>>(new Set(['void']))
  const [visitedCount, setVisitedCount] = useState(1)

  // Track scroll progress
  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = docHeight > 0 ? Math.min(1, Math.max(0, scrollY / docHeight)) : 0
      setScrollProgress(progress)

      // Determine current section based on scroll
      const sectionIndex = Math.min(
        JOURNEY_SECTIONS.length - 1,
        Math.floor(progress * JOURNEY_SECTIONS.length)
      )
      const section = JOURNEY_SECTIONS[sectionIndex]
      if (section) {
        setCurrentSection(section.id)
        setCurrentIndex(sectionIndex)
      }
    }

    handleScroll()
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const markSectionVisited = useCallback((id: SectionId) => {
    // Only update if not already visited (prevents re-renders)
    if (visitedSectionsRef.current.has(id)) return
    visitedSectionsRef.current.add(id)
    setVisitedCount(visitedSectionsRef.current.size)
  }, [])

  const scrollToSection = useCallback((id: SectionId) => {
    const section = JOURNEY_SECTIONS.find(s => s.id === id)
    if (!section) return

    const element = document.getElementById(`journey-section-${id}`)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [])

  // Memoize visited sections as a stable Set reference
  const visitedSections = useMemo(() => visitedSectionsRef.current, [visitedCount])

  const contextValue = useMemo<JourneyContextType>(() => ({
    currentSection,
    currentIndex,
    totalSections: JOURNEY_SECTIONS.length,
    scrollProgress,
    visitedSections,
    markSectionVisited,
    scrollToSection,
    sections: JOURNEY_SECTIONS,
  }), [currentSection, currentIndex, scrollProgress, visitedSections, visitedCount, markSectionVisited, scrollToSection])

  return (
    <JourneyContext.Provider value={contextValue}>
      <div className="relative bg-black min-h-screen">
        {/* LiquidEther background effect - subtle blue core with orange outer */}
        <div className="fixed inset-0 z-0 pointer-events-none opacity-40">
          <LiquidEther
            colors={['#FF9F43', '#00FFFF', '#FFA500', '#00E5FF']} // Alternating: Bitcoin orange + Qubic cyan
            mouseForce={15}
            cursorSize={120}
            isViscous={false}
            viscous={25}
            iterationsViscous={32}
            iterationsPoisson={32}
            resolution={0.5}
            isBounce={false}
            autoDemo={true}
            autoSpeed={0.3}
            autoIntensity={1.5}
            takeoverDuration={0.25}
            autoResumeDelay={3000}
            autoRampDuration={0.6}
          />
        </div>
        {/* Content */}
        <div className="relative z-10">
          {children}
        </div>
      </div>
    </JourneyContext.Provider>
  )
}
