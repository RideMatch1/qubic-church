'use client'

/**
 * CosmicCountdown - Premium Glass Morphism Countdown
 *
 * PREMIUM FEATURES:
 * - Advanced glass morphism with frosted blur
 * - Sophisticated typography (Space Grotesk feel)
 * - Ethereal glow and particle effects
 * - Smooth pulsing animations
 * - Premium color gradients
 */

interface CosmicCountdownProps {
  countdown: {
    days: number
    hours: number
    minutes: number
    seconds: number
  }
}

export function CosmicCountdown({ countdown }: CosmicCountdownProps) {
  return (
    <div className="absolute top-8 left-8 z-10 pointer-events-none">
      {/* Minimalist countdown - top left like original */}
      <div className="relative">
        <div
          className="text-white/90 font-mono text-2xl tracking-wider"
          style={{
            fontFamily: 'var(--font-mono), "JetBrains Mono", monospace',
            textShadow: '0 0 10px rgba(255, 255, 255, 0.3)',
          }}
        >
          {countdown.days.toString().padStart(3, '0')}.{countdown.hours.toString().padStart(2, '0')}.{countdown.minutes.toString().padStart(2, '0')}.{countdown.seconds.toString().padStart(2, '0')}
        </div>
      </div>
    </div>
  )
}

// Removed unused CountdownUnit and Separator components
