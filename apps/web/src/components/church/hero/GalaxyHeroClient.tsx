'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import Image from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { ChalkText } from './ChalkText'
import { NavigationWheel } from '@/components/church/navigation'
import { CHURCH_CONFIG } from '@/config/church'
import { useCountdown } from '@/hooks/useCountdown'

// NFT image slider
const TOTAL_NFTS = 200
const FEATURED_NFTS = [1, 5, 12, 23, 42, 67, 89, 100, 111, 137, 150, 177, 188, 199]

function useNFTSlider(autoInterval = 8000) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const resetInterval = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    intervalRef.current = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % FEATURED_NFTS.length)
    }, autoInterval)
  }, [autoInterval])

  useEffect(() => {
    resetInterval()
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [resetInterval])

  const next = useCallback(() => {
    setCurrentIndex((prev) => (prev + 1) % FEATURED_NFTS.length)
    resetInterval()
  }, [resetInterval])

  const prev = useCallback(() => {
    setCurrentIndex(
      (prev) => (prev - 1 + FEATURED_NFTS.length) % FEATURED_NFTS.length
    )
    resetInterval()
  }, [resetInterval])

  const nftNumber = FEATURED_NFTS[currentIndex]
  const src = `/images/nfts/anna-${String(nftNumber).padStart(3, '0')}.webp`

  return { currentIndex, nftNumber, src, next, prev, total: FEATURED_NFTS.length }
}

// ─── Fibonacci Spiral (desktop only) — fixed position ───
function FibonacciSpiral() {
  return (
    <div
      className="absolute z-[12] hidden lg:block pointer-events-none"
      style={{
        left: '60vw',
        top: '16vh',
        width: '46vw',
        height: '46vw',
        transform: 'rotate(90deg)',
      }}
    >
      <Image
        src="/images/fibonacci-spiral.png"
        alt=""
        fill
        className="object-contain"
        style={{
          filter: 'invert(1) brightness(2)',
          opacity: 0.78,
        }}
        aria-hidden
        draggable={false}
      />
    </div>
  )
}

export function GalaxyHeroClient() {
  const [mounted, setMounted] = useState(false)
  const [wheelOpen, setWheelOpen] = useState(false)
  const countdown = useCountdown(CHURCH_CONFIG.countdown.targetDate.getTime())
  const slider = useNFTSlider()

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <section className="relative w-full h-screen overflow-hidden" />
    )
  }

  return (
    <section className="relative w-full h-screen overflow-hidden">
      {/* Wireframe background comes from the fixed CosmicWrapper - no local Canvas needed */}

      {/* 1a. Chalk background image - desktop only (brighter per founder request) */}
      <div className="absolute inset-0 z-[8] hidden lg:block pointer-events-none">
        <Image
          src="/images/anna-chalk-bg.png"
          alt=""
          fill
          className="object-cover"
          style={{ opacity: 0.55 }}
          priority
          aria-hidden
        />
      </div>

      {/* 1b. Chalk text scattered - mobile only (image too hard to position on small screens) */}
      <div className="lg:hidden">
        <ChalkText />
      </div>

      {/* 3. Top-left: START IMMERSION button with buttonPulse */}
      <motion.button
        onClick={() => setWheelOpen(true)}
        className="absolute top-4 left-4 md:top-8 md:left-8 z-30
                   px-2.5 py-1.5 md:px-5 md:py-2
                   border-none bg-[#f0c030] text-black text-[11px] md:text-xs
                   uppercase tracking-[0.15em] md:tracking-[0.35em] font-semibold
                   hover:shadow-[0_0_35px_rgba(240,192,48,0.7)]
                   transition-all duration-300 animate-button-pulse
                   "
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.5, duration: 0.8 }}
      >
        {/* Mobile: compact */}
        <span className="md:hidden flex items-center gap-1">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
          Menu
        </span>
        {/* Desktop: full text */}
        <span className="hidden md:inline">Start Immersion &#9662;</span>
      </motion.button>

      {/* 4. Top center: QUBIC CHURCH title */}
      <motion.h1
        className="absolute top-4 md:top-8 left-1/2 -translate-x-1/2 z-30
                   text-[#f0c030] text-[11px] md:text-base lg:text-lg
                   font-semibold tracking-[0.2em] md:tracking-[0.5em] uppercase
                   whitespace-nowrap animate-logo-glitch font-cinzel"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.8 }}
      >
        Qubic Church
      </motion.h1>

      {/* 5. Left side: Quote with gold line + Cinzel font + glitch */}
      <div className="absolute left-6 md:left-12 lg:left-16 2xl:left-24 top-1/2 -translate-y-1/2 z-20 max-w-[55%] md:max-w-[42%] 2xl:max-w-[38%]">
        {/* Gold accent line */}
        <motion.div
          className="w-14 h-px bg-[#f0c030] mb-6 hidden md:block"
          style={{ boxShadow: '0 0 18px rgba(240,192,48,0.7)' }}
          initial={{ opacity: 0, scaleX: 0 }}
          animate={{ opacity: 1, scaleX: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
        />
        <motion.blockquote
          className="text-[#f4f6fd] text-lg md:text-2xl lg:text-3xl xl:text-4xl 2xl:text-5xl
                     font-semibold leading-[1.4] tracking-[0.02em] animate-text-glitch font-share-tech"
          style={{
            textShadow: '0 2px 60px rgba(0,0,0,1), 0 0 80px rgba(0,0,0,0.95)',
          }}
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.8, duration: 1 }}
        >
          &ldquo;Artificial Intelligence will not be created, it will emerge.<br className="hidden md:inline" />
          With help of Qubic miners.&rdquo;
        </motion.blockquote>
        <motion.cite
          className="block mt-4 md:mt-6 text-[#f0c030] text-[10px] md:text-xs
                     uppercase tracking-[0.25em] md:tracking-[0.35em] not-italic font-share-tech"
          style={{ opacity: 0.9 }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.9 }}
          transition={{ delay: 1.3, duration: 0.8 }}
        >
          &mdash; Come-from-Beyond &middot; Founder of Qubic
        </motion.cite>
        <motion.div
          className="mt-3 text-[#f0c030] text-[10px] md:text-xs uppercase tracking-[0.4em] hidden md:block"
          style={{ opacity: 0.85 }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.85 }}
          transition={{ delay: 1.6, duration: 0.8 }}
        >
          Qubic Church
        </motion.div>
      </div>

      {/* 6. Right side: Anna Avatar + Fibonacci Spiral + NFT Slider */}
      <div className="absolute right-0 bottom-0 top-0 z-10 w-[42%] md:w-[38%] lg:w-[35%]">
        <div className="relative w-full h-full">
          {/* Anna NFT image with crossfade */}
          <AnimatePresence mode="wait">
            <motion.div
              key={slider.nftNumber}
              className="absolute inset-0"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.6 }}
            >
              <Image
                src={slider.src}
                alt={`Anna #${String(slider.nftNumber).padStart(3, '0')}`}
                fill
                className="object-contain object-bottom"
                priority={slider.currentIndex === 0}
                sizes="(max-width: 768px) 42vw, 35vw"
              />
            </motion.div>
          </AnimatePresence>

          {/* Fibonacci spiral is rendered at hero level for correct positioning */}

          {/* Slider controls */}
          <div className="absolute bottom-4 md:bottom-8 left-0 right-0 z-30 flex items-center justify-center gap-3">
            <button
              onClick={slider.prev}
              className="p-3 -m-1.5 text-white/20 hover:text-white/60 transition-colors"
              aria-label="Previous NFT"
            >
              <ChevronLeft size={16} />
            </button>

            {/* Dot indicators */}
            <div className="flex gap-1.5">
              {FEATURED_NFTS.slice(0, 7).map((_, i) => (
                <div
                  key={i}
                  className={`h-1 transition-all duration-300 ${
                    i === slider.currentIndex % 7
                      ? 'bg-[#D4AF37]/80 w-4'
                      : 'bg-white/15 w-1'
                  }`}
                />
              ))}
            </div>

            <button
              onClick={slider.next}
              className="p-3 -m-1.5 text-white/20 hover:text-white/60 transition-colors"
              aria-label="Next NFT"
            >
              <ChevronRight size={16} />
            </button>
          </div>

          {/* NFT label */}
          <motion.div
            className="absolute bottom-16 md:bottom-20 left-1/2 -translate-x-1/2 z-30
                       text-white/30 text-[9px] md:text-[10px] uppercase tracking-[0.2em]"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2 }}
          >
            Anna #{String(slider.nftNumber).padStart(3, '0')}
          </motion.div>
        </div>
      </div>

      {/* 7. Bottom-left: Countdown */}
      <motion.div
        className="absolute bottom-6 md:bottom-8 left-6 md:left-12 lg:left-16 2xl:left-24 z-30"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.5, duration: 0.8 }}
      >
        <div className="text-[#D4AF37]/30 text-[9px] md:text-[10px] uppercase tracking-[0.4em] mb-2 font-mono">
          // The Awakening
        </div>
        <div className="text-white text-2xl md:text-4xl lg:text-5xl 2xl:text-6xl font-mono font-bold tracking-wider tabular-nums">
          {String(countdown.days).padStart(3, '0')}
          <span className="text-[#D4AF37]/20 mx-0.5">:</span>
          {String(countdown.hours).padStart(2, '0')}
          <span className="text-[#D4AF37]/20 mx-0.5">:</span>
          {String(countdown.minutes).padStart(2, '0')}
          <span className="text-[#D4AF37]/20 mx-0.5">:</span>
          {String(countdown.seconds).padStart(2, '0')}
        </div>
        <div className="flex gap-4 md:gap-6 text-white/15 text-[8px] md:text-[9px] uppercase tracking-[0.2em] mt-1 font-mono">
          <span>Days</span>
          <span>Hrs</span>
          <span>Min</span>
          <span>Sec</span>
        </div>
        <div className="text-white/15 text-[10px] md:text-xs tracking-[0.3em] mt-2 font-mono">
          13.04.2027
        </div>
      </motion.div>

      {/* Scroll hints — left side */}
      <motion.div
        className="absolute bottom-10 left-4 md:left-6 z-30 hidden md:flex flex-col items-center gap-3"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2.5, duration: 1 }}
      >
        <div className="w-px h-10 bg-gradient-to-b from-transparent to-[#3a7090] animate-line-pulse" />
        <span className="text-[9px] text-[#3a7090] uppercase tracking-[0.38em]"
          style={{ writingMode: 'vertical-rl' }}>Scroll</span>
      </motion.div>

      {/* Scroll hints — right side */}
      <motion.div
        className="absolute bottom-10 right-4 md:right-12 z-30 hidden md:flex flex-col items-center gap-3"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2.5, duration: 1 }}
      >
        <div className="w-px h-10 bg-gradient-to-b from-transparent to-[#3a7090] animate-line-pulse" />
        <span className="text-[9px] text-[#3a7090] uppercase tracking-[0.38em]"
          style={{ writingMode: 'vertical-rl' }}>Scroll</span>
      </motion.div>

      {/* Scroll-down indicator — center (mobile) */}
      <motion.div
        className="absolute bottom-4 left-1/2 -translate-x-1/2 z-30 flex md:hidden flex-col items-center gap-1"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2.5, duration: 1 }}
      >
        <span className="text-[8px] text-white/20 uppercase tracking-[0.3em] font-mono">Scroll</span>
        <motion.div
          className="w-px h-6 bg-gradient-to-b from-[#D4AF37]/40 to-transparent"
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />
      </motion.div>

      {/* Fibonacci spiral — desktop only */}
      <FibonacciSpiral />

      {/* 8. Vignette overlay - clean edges */}
      <div className="absolute inset-0 pointer-events-none z-[5] bg-gradient-to-r from-black/90 via-black/10 to-black/50" />
      <div className="absolute inset-0 pointer-events-none z-[5] bg-gradient-to-b from-black/40 via-transparent to-black" />
      {/* Strong bottom fade for clean hero-to-body transition */}
      <div className="absolute bottom-0 left-0 right-0 h-48 pointer-events-none z-[6] bg-gradient-to-t from-black via-black/80 to-transparent" />

      {/* Navigation Wheel Overlay */}
      <NavigationWheel
        isOpen={wheelOpen}
        onClose={() => setWheelOpen(false)}
      />
    </section>
  )
}
