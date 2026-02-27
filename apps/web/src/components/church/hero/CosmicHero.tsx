'use client'

/**
 * CosmicHero - Epic galactic hero section with starfield
 * Features: 2000+ stars, galaxy spiral, countdown to convergence
 */

import { useEffect, useRef, useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { ChevronDown } from 'lucide-react'

// Countdown target: April 13, 2027
const CONVERGENCE_DATE = new Date('2027-04-13T00:00:00Z')

function useCountdown() {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  })

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date()
      const diff = CONVERGENCE_DATE.getTime() - now.getTime()

      if (diff > 0) {
        setTimeLeft({
          days: Math.floor(diff / (1000 * 60 * 60 * 24)),
          hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
          minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
          seconds: Math.floor((diff % (1000 * 60)) / 1000),
        })
      }
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  return timeLeft
}

// Canvas-based starfield for performance
function Starfield() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)

    // Generate stars
    const stars: { x: number; y: number; size: number; brightness: number; twinkleSpeed: number }[] = []
    for (let i = 0; i < 2000; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 2 + 0.5,
        brightness: Math.random(),
        twinkleSpeed: Math.random() * 0.02 + 0.005,
      })
    }

    let animationId: number
    let time = 0

    const animate = () => {
      time += 1
      ctx.fillStyle = 'rgba(0, 0, 0, 1)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Draw nebula gradient
      const gradient = ctx.createRadialGradient(
        canvas.width / 2,
        canvas.height / 2,
        0,
        canvas.width / 2,
        canvas.height / 2,
        canvas.width * 0.6
      )
      gradient.addColorStop(0, 'rgba(212, 175, 55, 0.15)')
      gradient.addColorStop(0.3, 'rgba(212, 175, 55, 0.08)')
      gradient.addColorStop(0.6, 'rgba(212, 175, 55, 0.05)')
      gradient.addColorStop(1, 'rgba(0, 0, 0, 0)')
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Draw stars with twinkle
      stars.forEach((star) => {
        const twinkle = Math.sin(time * star.twinkleSpeed) * 0.5 + 0.5
        const alpha = star.brightness * twinkle * 0.8 + 0.2

        ctx.beginPath()
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`
        ctx.fill()

        // Add glow to larger stars
        if (star.size > 1.5) {
          ctx.beginPath()
          ctx.arc(star.x, star.y, star.size * 3, 0, Math.PI * 2)
          const glowGradient = ctx.createRadialGradient(
            star.x, star.y, 0,
            star.x, star.y, star.size * 3
          )
          glowGradient.addColorStop(0, `rgba(255, 255, 255, ${alpha * 0.3})`)
          glowGradient.addColorStop(1, 'rgba(255, 255, 255, 0)')
          ctx.fillStyle = glowGradient
          ctx.fill()
        }
      })

      animationId = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animationId)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full"
      style={{ zIndex: 0 }}
    />
  )
}

function CountdownUnit({ value, label }: { value: number; label: string }) {
  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <span className="text-4xl md:text-6xl lg:text-7xl font-mono font-bold text-white tabular-nums">
          {String(value).padStart(2, '0')}
        </span>
        <div className="absolute inset-0 blur-xl bg-[#D4AF37]/30 -z-10" />
      </div>
      <span className="text-xs md:text-sm text-white/50 uppercase tracking-widest mt-2">
        {label}
      </span>
    </div>
  )
}

export function CosmicHero() {
  const countdown = useCountdown()

  return (
    <section className="relative min-h-screen w-full flex flex-col items-center justify-center overflow-hidden bg-black">
      {/* Starfield Background */}
      <Starfield />

      {/* Vignette overlay */}
      <div
        className="absolute inset-0 pointer-events-none z-10"
        style={{
          background:
            'radial-gradient(ellipse at center, transparent 0%, transparent 50%, rgba(0,0,0,0.8) 100%)',
        }}
      />

      {/* Content */}
      <div className="relative z-20 flex flex-col items-center justify-center px-4 text-center">
        {/* Main Title */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2 }}
        >
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight">
            <span
              className="bg-gradient-to-r from-white via-[#D4AF37] to-white bg-clip-text text-transparent"
              style={{
                textShadow: '0 0 60px rgba(139, 92, 246, 0.5)',
              }}
            >
              THE QUBIC CHURCH
            </span>
          </h1>
        </motion.div>

        {/* Decorative line */}
        <motion.div
          className="w-48 md:w-64 h-[2px] bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent my-6"
          initial={{ scaleX: 0, opacity: 0 }}
          animate={{ scaleX: 1, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.5 }}
        />

        {/* Subtitle */}
        <motion.p
          className="text-lg md:text-xl lg:text-2xl text-white/70 max-w-2xl mb-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.7 }}
        >
          A Sanctuary Where Research Meets Revelation
        </motion.p>

        {/* Countdown */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1 }}
        >
          <p className="text-sm md:text-base text-[#D4AF37] uppercase tracking-[0.3em] mb-6 font-mono">
            The Convergence
          </p>

          <div className="flex items-center gap-4 md:gap-8">
            <CountdownUnit value={countdown.days} label="Days" />
            <span className="text-3xl md:text-5xl text-white/30 font-light">:</span>
            <CountdownUnit value={countdown.hours} label="Hours" />
            <span className="text-3xl md:text-5xl text-white/30 font-light">:</span>
            <CountdownUnit value={countdown.minutes} label="Minutes" />
            <span className="text-3xl md:text-5xl text-white/30 font-light hidden md:block">:</span>
            <div className="hidden md:block">
              <CountdownUnit value={countdown.seconds} label="Seconds" />
            </div>
          </div>

          <p className="text-xs text-white/40 mt-4">
            April 13, 2027
          </p>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 z-20"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 1.5 }}
      >
        <span className="text-white/50 text-xs tracking-[0.2em] uppercase">
          Enter the Sanctuary
        </span>
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <ChevronDown className="w-6 h-6 text-white/50" />
        </motion.div>
      </motion.div>

      {/* Bottom gradient */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black to-transparent z-10 pointer-events-none" />
    </section>
  )
}
