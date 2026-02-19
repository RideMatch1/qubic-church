'use client'

/**
 * CosmicWrapper - Fixed pure black background with perspective grid & stars
 * The 3D wireframe grid adds the futuristic depth feel
 */

import { memo, type ReactNode } from 'react'
import { CosmicBackground } from './CosmicBackground'

interface CosmicWrapperProps {
  children: ReactNode
}

export const CosmicWrapper = memo(function CosmicWrapper({ children }: CosmicWrapperProps) {
  return (
    <div className="relative min-h-screen bg-black">
      {/* Fixed starfield + perspective grid */}
      <div className="fixed inset-0 z-0">
        <CosmicBackground
          intensity="medium"
          showStars
          showWireframe
        />
      </div>

      {/* Content layer */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  )
})

export default CosmicWrapper
