'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRouter } from 'next/navigation'
import {
  BookOpen,
  Scroll,
  Users,
  Map,
  Sparkles,
  Target,
  X,
  type LucideIcon,
} from 'lucide-react'

interface WheelSegment {
  label: string
  href: string
  icon: LucideIcon
  description: string
}

const SEGMENTS: WheelSegment[] = [
  {
    label: 'RESEARCH',
    href: '/docs',
    icon: BookOpen,
    description: 'Sacred Archive',
  },
  {
    label: 'ANNA MATRIX',
    href: '/evidence',
    icon: Sparkles,
    description: 'Neural Grid',
  },
  {
    label: 'MINE QUBIC',
    href: '/mine-qubic',
    icon: Target,
    description: 'Start Mining',
  },
  {
    label: 'GET QUBIC',
    href: '/get-qubic',
    icon: Scroll,
    description: 'Exchanges',
  },
  {
    label: 'DASHBOARD',
    href: '/monitoring',
    icon: Map,
    description: 'Live Data',
  },
  {
    label: 'GIVEAWAY',
    href: '/#giveaway',
    icon: Users,
    description: '676M Prize',
  },
]

const GOLD = '#D4AF37'
const GOLD_DIM = '#8B7328'
const DARK = '#0a0a0a'

function polarToCartesian(
  cx: number,
  cy: number,
  r: number,
  angleDeg: number
) {
  const rad = ((angleDeg - 90) * Math.PI) / 180
  return {
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad),
  }
}

function arcPath(
  cx: number,
  cy: number,
  innerR: number,
  outerR: number,
  startAngle: number,
  endAngle: number
) {
  const outerStart = polarToCartesian(cx, cy, outerR, startAngle)
  const outerEnd = polarToCartesian(cx, cy, outerR, endAngle)
  const innerEnd = polarToCartesian(cx, cy, innerR, endAngle)
  const innerStart = polarToCartesian(cx, cy, innerR, startAngle)

  return [
    `M ${outerStart.x} ${outerStart.y}`,
    `A ${outerR} ${outerR} 0 0 1 ${outerEnd.x} ${outerEnd.y}`,
    `L ${innerEnd.x} ${innerEnd.y}`,
    `A ${innerR} ${innerR} 0 0 0 ${innerStart.x} ${innerStart.y}`,
    'Z',
  ].join(' ')
}

function DesktopWheel({
  onNavigate,
}: {
  onNavigate: (href: string) => void
}) {
  const [hovered, setHovered] = useState<number | null>(null)

  const cx = 200
  const cy = 200
  const innerR = 60
  const outerR = 170
  const segmentAngle = 360 / SEGMENTS.length
  const gap = 1.5 // degree gap between segments

  return (
    <svg viewBox="0 0 400 400" className="w-[340px] h-[340px] md:w-[420px] md:h-[420px]">
      {/* Outer ring */}
      <circle
        cx={cx}
        cy={cy}
        r={outerR + 8}
        fill="none"
        stroke={GOLD_DIM}
        strokeWidth={0.5}
        opacity={0.4}
      />

      {/* Segments */}
      {SEGMENTS.map((seg, i) => {
        const startAngle = i * segmentAngle + gap / 2
        const endAngle = (i + 1) * segmentAngle - gap / 2
        const midAngle = (startAngle + endAngle) / 2
        const midR = (innerR + outerR) / 2
        const anchor = polarToCartesian(cx, cy, midR, midAngle)
        const isHovered = hovered === i
        const Icon = seg.icon

        return (
          <g
            key={i}
            className="cursor-pointer"
            onMouseEnter={() => setHovered(i)}
            onMouseLeave={() => setHovered(null)}
            onClick={() => onNavigate(seg.href)}
            role="link"
            tabIndex={0}
            aria-label={`Navigate to ${seg.label}`}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                onNavigate(seg.href)
              }
            }}
          >
            <path
              d={arcPath(cx, cy, innerR, outerR, startAngle, endAngle)}
              fill={isHovered ? `${GOLD}15` : `${DARK}cc`}
              stroke={isHovered ? GOLD : GOLD_DIM}
              strokeWidth={isHovered ? 1 : 0.5}
              strokeOpacity={isHovered ? 0.8 : 0.3}
              style={{ transition: 'all 0.3s ease' }}
            />

            {/* Icon - centered above label */}
            <foreignObject
              x={anchor.x - 10}
              y={anchor.y - 18}
              width={20}
              height={20}
            >
              <div className="flex items-center justify-center w-full h-full">
                <Icon
                  size={15}
                  strokeWidth={1.5}
                  style={{
                    color: isHovered ? GOLD : `${GOLD}80`,
                    transition: 'color 0.3s ease',
                  }}
                />
              </div>
            </foreignObject>

            {/* Label - centered below icon */}
            <text
              x={anchor.x}
              y={anchor.y + 8}
              textAnchor="middle"
              fill={isHovered ? GOLD : `${GOLD}99`}
              fontSize="7.5"
              fontWeight="500"
              letterSpacing="0.12em"
              style={{
                fontFamily: 'system-ui, sans-serif',
                transition: 'fill 0.3s ease',
              }}
            >
              {seg.label}
            </text>
          </g>
        )
      })}

      {/* Center circle */}
      <circle
        cx={cx}
        cy={cy}
        r={innerR}
        fill={DARK}
        stroke={GOLD_DIM}
        strokeWidth={0.5}
        strokeOpacity={0.5}
      />

      {/* Center icon */}
      <foreignObject x={cx - 10} y={cy - 22} width={20} height={20}>
        <div className="flex items-center justify-center w-full h-full">
          <Target size={13} strokeWidth={1.5} style={{ color: `${GOLD}80` }} />
        </div>
      </foreignObject>

      {/* Center text */}
      <text
        x={cx}
        y={cy}
        textAnchor="middle"
        dominantBaseline="central"
        fill={GOLD}
        fontSize="8"
        fontWeight="600"
        letterSpacing="0.2em"
        style={{ fontFamily: 'system-ui, sans-serif' }}
      >
        NAVIGATE
      </text>
      <text
        x={cx}
        y={cy + 13}
        textAnchor="middle"
        dominantBaseline="central"
        fill={`${GOLD}70`}
        fontSize="5.5"
        letterSpacing="0.15em"
        style={{ fontFamily: 'system-ui, sans-serif' }}
      >
        {hovered !== null && SEGMENTS[hovered] ? SEGMENTS[hovered].description.toUpperCase() : 'SELECT PATH'}
      </text>
    </svg>
  )
}

function MobileNavGrid({
  onNavigate,
}: {
  onNavigate: (href: string) => void
}) {
  return (
    <div className="grid grid-cols-2 gap-3 px-6 max-w-sm mx-auto">
      {SEGMENTS.map((seg) => {
        const Icon = seg.icon
        return (
          <button
            key={seg.label}
            onClick={() => onNavigate(seg.href)}
            className="p-4 border transition-all text-center
                       bg-[#050505] border-[#D4AF37]/15
                       hover:border-[#D4AF37]/40 hover:bg-[#D4AF37]/5
                       active:scale-95"
          >
            <Icon className="w-5 h-5 mx-auto mb-2" style={{ color: `${GOLD}80` }} />
            <span
              className="text-[10px] font-medium uppercase tracking-[0.15em]"
              style={{ color: `${GOLD}cc` }}
            >
              {seg.label}
            </span>
            <span className="block text-[9px] text-white/30 mt-0.5">
              {seg.description}
            </span>
          </button>
        )
      })}
    </div>
  )
}

export function NavigationWheel({
  isOpen,
  onClose,
}: {
  isOpen: boolean
  onClose: () => void
}) {
  const router = useRouter()

  const handleNavigate = useCallback(
    (href: string) => {
      onClose()
      router.push(href)
    },
    [onClose, router]
  )

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [isOpen, onClose])

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-[100] flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/85 backdrop-blur-md"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />

          {/* Content */}
          <motion.div
            className="relative z-10"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          >
            {/* Close button */}
            <button
              onClick={onClose}
              className="absolute -top-12 right-0 md:right-4 p-2 text-white/40 hover:text-white/80 transition-colors"
              aria-label="Close navigation"
            >
              <X size={24} />
            </button>

            {/* Desktop: SVG Wheel */}
            <div className="hidden md:block">
              <DesktopWheel onNavigate={handleNavigate} />
            </div>

            {/* Mobile: Grid */}
            <div className="md:hidden">
              <MobileNavGrid onNavigate={handleNavigate} />
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
