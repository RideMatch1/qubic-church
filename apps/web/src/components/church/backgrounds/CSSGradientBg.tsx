'use client'

/**
 * CSSGradientBg - Lightweight CSS-only background
 * Performance alternative to CosmicBackground (no Canvas)
 */

import { memo } from 'react'

type ColorTheme = 'purple' | 'cyan' | 'orange' | 'yellow' | 'mixed'

interface CSSGradientBgProps {
  variant?: ColorTheme
  intensity?: 'low' | 'medium' | 'high'
  showGlow?: boolean
  className?: string
}

const gradientConfigs: Record<ColorTheme, { primary: string; secondary: string; accent: string }> = {
  purple: {
    primary: 'rgba(212, 175, 55, 0.15)',
    secondary: 'rgba(212, 175, 55, 0.1)',
    accent: 'rgba(212, 175, 55, 0.2)',
  },
  cyan: {
    primary: 'rgba(212, 175, 55, 0.15)',
    secondary: 'rgba(212, 175, 55, 0.1)',
    accent: 'rgba(212, 175, 55, 0.2)',
  },
  orange: {
    primary: 'rgba(249, 115, 22, 0.15)',
    secondary: 'rgba(234, 88, 12, 0.1)',
    accent: 'rgba(251, 146, 60, 0.2)',
  },
  yellow: {
    primary: 'rgba(234, 179, 8, 0.15)',
    secondary: 'rgba(202, 138, 4, 0.1)',
    accent: 'rgba(250, 204, 21, 0.2)',
  },
  mixed: {
    primary: 'rgba(212, 175, 55, 0.12)',
    secondary: 'rgba(212, 175, 55, 0.08)',
    accent: 'rgba(249, 115, 22, 0.1)',
  },
}

const intensityScale = {
  low: 0.5,
  medium: 1,
  high: 1.5,
}

export const CSSGradientBg = memo(function CSSGradientBg({
  variant = 'purple',
  intensity = 'medium',
  showGlow = true,
  className = '',
}: CSSGradientBgProps) {
  const config = gradientConfigs[variant]
  const scale = intensityScale[intensity]

  // Apply intensity scaling to opacity
  const adjustOpacity = (rgba: string, multiplier: number) => {
    return rgba.replace(/[\d.]+\)$/, (match) => {
      const opacity = parseFloat(match) * multiplier
      return `${Math.min(opacity, 0.4)})`
    })
  }

  const primary = adjustOpacity(config.primary, scale)
  const secondary = adjustOpacity(config.secondary, scale)
  const accent = adjustOpacity(config.accent, scale)

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      {/* Base gradient */}
      <div
        className="absolute inset-0"
        style={{
          background: `
            radial-gradient(ellipse 80% 50% at 50% 0%, ${primary} 0%, transparent 50%),
            radial-gradient(ellipse 60% 40% at 80% 80%, ${secondary} 0%, transparent 40%),
            radial-gradient(ellipse 50% 30% at 20% 60%, ${accent} 0%, transparent 30%),
            linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,1) 100%)
          `,
        }}
      />

      {/* Animated glow orbs (CSS only) */}
      {showGlow && (
        <>
          <div
            className="absolute w-[500px] h-[500px] blur-[120px] animate-float-slow"
            style={{
              background: primary,
              top: '10%',
              left: '10%',
            }}
          />
          <div
            className="absolute w-[400px] h-[400px] blur-[100px] animate-float-medium"
            style={{
              background: secondary,
              bottom: '20%',
              right: '15%',
            }}
          />
        </>
      )}

      {/* Subtle noise texture */}
      <div
        className="absolute inset-0 opacity-[0.02] mix-blend-overlay"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Vignette */}
      <div
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.4) 100%)',
        }}
      />

      {/* CSS animations via Tailwind (add to globals.css if not present) */}
      <style jsx>{`
        @keyframes float-slow {
          0%, 100% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(30px, -20px) scale(1.1); }
        }
        @keyframes float-medium {
          0%, 100% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(-25px, 15px) scale(0.95); }
        }
        .animate-float-slow {
          animation: float-slow 20s ease-in-out infinite;
        }
        .animate-float-medium {
          animation: float-medium 15s ease-in-out infinite;
        }
      `}</style>
    </div>
  )
})

export default CSSGradientBg
