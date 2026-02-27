'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRouter } from 'next/navigation'
import {
  BookOpen,
  Sparkles,
  Target,
  Scroll,
  Map,
  FileText,
  Compass,
  Users,
  Milestone,
  Cpu,
  Wallet,
  X,
  type LucideIcon,
} from 'lucide-react'

interface WheelSegment {
  label: string
  href: string
  icon: LucideIcon
  description: string
  isHighlighted?: boolean
}

const SEGMENTS: WheelSegment[] = [
  // Philosophy (scroll to sections)
  {
    label: 'CFB',
    href: '/#cfb',
    icon: Sparkles,
    description: 'The Architect',
    isHighlighted: true,
  },
  {
    label: 'MANIFESTO',
    href: '/#creed',
    icon: FileText,
    description: 'Our Declaration',
  },
  {
    label: 'GENESIS',
    href: '/#genesis',
    icon: Compass,
    description: 'Origin Story',
  },
  {
    label: 'MISSION',
    href: '/#mission',
    icon: Target,
    description: '9 Objectives',
  },
  {
    label: 'RELICS',
    href: '/#relics',
    icon: Scroll,
    description: 'NFT Collection',
  },
  {
    label: 'FOUNDERS',
    href: '/#founders',
    icon: Users,
    description: '200 Slots',
  },
  {
    label: 'THE PATH',
    href: '/#path',
    icon: Milestone,
    description: 'How to Begin',
  },
  {
    label: 'LEXICON',
    href: '/#lexicon',
    icon: BookOpen,
    description: 'Glossary',
  },
  {
    label: 'ROADMAP',
    href: '/#roadmap',
    icon: Map,
    description: 'Timeline',
  },
  // Practical (page navigation)
  {
    label: 'ANNA MATRIX',
    href: '/evidence',
    icon: Sparkles,
    description: 'Neural Grid',
  },
  {
    label: 'MINE QUBIC',
    href: '/mine-qubic',
    icon: Cpu,
    description: 'Start Mining',
  },
  {
    label: 'GET QUBIC',
    href: '/get-qubic',
    icon: Wallet,
    description: 'Exchanges',
  },
  {
    label: 'RESEARCH',
    href: '/docs',
    icon: BookOpen,
    description: 'Sacred Archive',
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

  const cx = 220
  const cy = 220
  const innerR = 65
  const outerR = 195
  const segmentAngle = 360 / SEGMENTS.length
  const gap = 1.2

  return (
    <svg viewBox="0 0 440 440" className="w-[380px] h-[380px] md:w-[460px] md:h-[460px]">
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
        const isHighlighted = seg.isHighlighted
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
              fill={isHovered ? `${GOLD}15` : isHighlighted ? `${GOLD}08` : `${DARK}cc`}
              stroke={isHovered || isHighlighted ? GOLD : GOLD_DIM}
              strokeWidth={isHovered ? 1 : isHighlighted ? 0.8 : 0.5}
              strokeOpacity={isHovered ? 0.8 : isHighlighted ? 0.5 : 0.3}
              style={{ transition: 'all 0.3s ease' }}
            />

            {/* Glow for highlighted (CfB) segment */}
            {isHighlighted && !isHovered && (
              <path
                d={arcPath(cx, cy, innerR, outerR, startAngle, endAngle)}
                fill="none"
                stroke={GOLD}
                strokeWidth={2}
                strokeOpacity={0.1}
                style={{ filter: 'blur(4px)' }}
              />
            )}

            {/* Icon */}
            <foreignObject
              x={anchor.x - 9}
              y={anchor.y - 16}
              width={18}
              height={18}
            >
              <div className="flex items-center justify-center w-full h-full">
                <Icon
                  size={13}
                  strokeWidth={1.5}
                  style={{
                    color: isHovered ? GOLD : isHighlighted ? `${GOLD}cc` : `${GOLD}70`,
                    transition: 'color 0.3s ease',
                  }}
                />
              </div>
            </foreignObject>

            {/* Label */}
            <text
              x={anchor.x}
              y={anchor.y + 6}
              textAnchor="middle"
              fill={isHovered ? GOLD : isHighlighted ? `${GOLD}bb` : `${GOLD}80`}
              fontSize="6"
              fontWeight="500"
              letterSpacing="0.1em"
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
          <Scroll size={13} strokeWidth={1.5} style={{ color: `${GOLD}80` }} />
        </div>
      </foreignObject>

      {/* Center text */}
      <text
        x={cx}
        y={cy}
        textAnchor="middle"
        dominantBaseline="central"
        fill={GOLD}
        fontSize="7.5"
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
        fontSize="5"
        letterSpacing="0.12em"
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
    <div className="grid grid-cols-2 gap-2 px-4 max-w-sm mx-auto max-h-[70vh] overflow-y-auto">
      {SEGMENTS.map((seg) => {
        const Icon = seg.icon
        return (
          <button
            key={`${seg.label}-${seg.href}`}
            onClick={() => onNavigate(seg.href)}
            className={`p-3 border transition-all text-center
                       bg-[#050505] hover:bg-[#D4AF37]/5 active:scale-95
                       ${seg.isHighlighted ? 'border-[#D4AF37]/25' : 'border-[#D4AF37]/15'}
                       hover:border-[#D4AF37]/40`}
          >
            <Icon className="w-4 h-4 mx-auto mb-1.5" style={{ color: `${GOLD}80` }} />
            <span
              className="text-[9px] font-medium uppercase tracking-[0.1em] block"
              style={{ color: `${GOLD}cc` }}
            >
              {seg.label}
            </span>
            <span className="block text-[8px] text-white/25 mt-0.5">
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
      if (href.startsWith('/#')) {
        const hash = href.replace('/', '')
        const el = document.querySelector(hash)
        if (el) {
          el.scrollIntoView({ behavior: 'smooth' })
          return
        }
      }
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
