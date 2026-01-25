'use client'

import { ReactNode } from 'react'
import dynamic from 'next/dynamic'

// Dynamic import for LiquidEther background
const LiquidEther = dynamic(() => import('@/components/LiquidEther'), {
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-black" />,
})

interface JourneyWrapperProps {
  children: ReactNode
}

/**
 * Client-side wrapper for Journey sections with LiquidEther background
 * This component handles the dynamic import and client-side rendering
 */
export function JourneyWrapper({ children }: JourneyWrapperProps) {
  return (
    <div className="relative bg-black">
      {/* Shared LiquidEther background for all Journey sections */}
      <div className="fixed inset-0 z-0 pointer-events-none opacity-25">
        <LiquidEther
          colors={['#F97316', '#1e40af', '#ea580c', '#3b82f6']}
          mouseForce={8}
          cursorSize={80}
          isViscous={false}
          viscous={15}
          iterationsViscous={12}
          iterationsPoisson={12}
          resolution={0.25}
          isBounce={false}
          autoDemo={true}
          autoSpeed={0.2}
          autoIntensity={0.8}
          takeoverDuration={0.15}
          autoResumeDelay={4000}
          autoRampDuration={0.4}
        />
      </div>

      {/* Journey Story Sections */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  )
}
