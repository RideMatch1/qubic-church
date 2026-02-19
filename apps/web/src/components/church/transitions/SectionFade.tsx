'use client'

/**
 * SectionFade - Smooth gradient transition between homepage sections.
 * Place between sections to eliminate hard edges.
 */

export function SectionFade({ className = '' }: { className?: string }) {
  return (
    <div
      className={`relative h-24 md:h-32 w-full pointer-events-none ${className}`}
      aria-hidden
    >
      {/* Top fade from previous section */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent to-transparent" />
      {/* Subtle center glow for visual interest */}
      <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-px bg-gradient-to-r from-transparent via-white/[0.04] to-transparent" />
    </div>
  )
}
