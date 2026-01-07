'use client'

import { useRef, useState, useEffect } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { JourneySection } from '../JourneySection'
import { Clock, Calendar, Moon, BookOpen, HelpCircle, AlertTriangle, Sparkles } from 'lucide-react'

// Target date: March 3, 2026
const TARGET_DATE = new Date('2026-03-03T00:00:00Z')

interface TimeUnit {
  value: number
  label: string
}

function useCountdown(targetDate: Date): TimeUnit[] {
  const [timeLeft, setTimeLeft] = useState<TimeUnit[]>([
    { value: 0, label: 'days' },
    { value: 0, label: 'hours' },
    { value: 0, label: 'minutes' },
    { value: 0, label: 'seconds' },
  ])

  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date()
      const diff = targetDate.getTime() - now.getTime()

      if (diff <= 0) {
        return [
          { value: 0, label: 'days' },
          { value: 0, label: 'hours' },
          { value: 0, label: 'minutes' },
          { value: 0, label: 'seconds' },
        ]
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diff % (1000 * 60)) / 1000)

      return [
        { value: days, label: 'days' },
        { value: hours, label: 'hours' },
        { value: minutes, label: 'minutes' },
        { value: seconds, label: 'seconds' },
      ]
    }

    setTimeLeft(calculateTimeLeft())
    const timer = setInterval(() => {
      setTimeLeft(calculateTimeLeft())
    }, 1000)

    return () => clearInterval(timer)
  }, [targetDate])

  return timeLeft
}

const EVIDENCE_CARDS = [
  {
    icon: BookOpen,
    title: 'Biblical Reference',
    description: 'Isaiah 30:26 - "The light of the sun will be seven times brighter"',
    detail: 'Researchers found this specific date encoded in ancient texts',
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/20',
  },
  {
    icon: Moon,
    title: 'Lunar Eclipse',
    description: 'A total lunar eclipse occurs on March 3, 2026',
    detail: 'Astronomical alignment verified by NASA',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/20',
  },
  {
    icon: Clock,
    title: 'Qubic Time-Lock',
    description: 'Protocol unlocks at a specific epoch timestamp',
    detail: 'Cryptographically enforced release mechanism',
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/20',
  },
]

export function CountdownSection() {
  const contentRef = useRef(null)
  const isInView = useInView(contentRef, { once: false, amount: 0.3 })
  const timeLeft = useCountdown(TARGET_DATE)
  const [showCards, setShowCards] = useState(false)

  useEffect(() => {
    if (isInView) {
      const timer = setTimeout(() => setShowCards(true), 1000)
      return () => clearTimeout(timer)
    } else {
      setShowCards(false)
    }
  }, [isInView])

  return (
    <JourneySection id="countdown" background="transparent" className="flex items-center justify-center py-12 md:py-20">
      <div ref={contentRef} className="relative z-10 w-full max-w-5xl mx-auto px-4">
        {/* Chapter Header */}
        <motion.div
          className="text-center mb-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0.9 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/50 text-xs font-mono">
              CHAPTER 7
            </span>
          </motion.div>

          <motion.div
            className="inline-flex items-center gap-2 mb-4"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0.9 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Calendar className="h-8 w-8 text-white/60" />
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-bold text-white/90 mb-4">
            The Convergence
          </h2>

          {/* Story context for beginners */}
          <motion.div
            className="max-w-2xl mx-auto space-y-4 mb-8"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <p className="text-lg text-white/50 leading-relaxed">
              All the evidence points to a single date:{' '}
              <span className="text-white/80 font-bold">March 3, 2026</span>.
            </p>
            <p className="text-base text-white/40 leading-relaxed">
              From three completely different sources — ancient texts, astronomical events,
              and cryptographic code — the same date emerges.
            </p>
          </motion.div>
        </motion.div>

        {/* THE DATE - Dramatic reveal */}
        <motion.div
          className="p-8 md:p-12 rounded-2xl bg-gradient-to-b from-orange-950/30 to-black/50 border border-orange-900/30 mb-10 relative overflow-hidden"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0.95 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          {/* Background glow effect */}
          <motion.div
            className="absolute inset-0 bg-gradient-radial from-orange-500/10 via-transparent to-transparent"
            animate={{ opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 3, repeat: Infinity }}
          />

          {/* The Date */}
          <div className="relative text-center mb-8">
            <motion.h3
              className="text-5xl md:text-7xl lg:text-8xl font-bold text-white/90 tracking-tight"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              March 3, 2026
            </motion.h3>
            <motion.p
              className="text-lg text-white/40 mt-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: isInView ? 1 : 0 }}
              transition={{ delay: 0.8 }}
            >
              The date where all paths converge
            </motion.p>
          </div>

          {/* Countdown Timer */}
          <motion.div
            className="grid grid-cols-4 gap-3 md:gap-6 max-w-2xl mx-auto"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0.9 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          >
            {timeLeft.map((unit, index) => (
              <div key={unit.label} className="text-center">
                <div className="relative">
                  <motion.div
                    className="p-4 md:p-6 rounded-xl bg-black/50 border border-orange-500/20"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
                    transition={{ duration: 0.5, delay: 0.9 + index * 0.1 }}
                  >
                    <motion.div
                      className="text-3xl md:text-5xl font-mono font-bold text-orange-400"
                      key={unit.value}
                      initial={{ scale: 1.1 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.2 }}
                    >
                      {String(unit.value).padStart(2, '0')}
                    </motion.div>
                  </motion.div>
                  {/* Pulsing glow */}
                  <motion.div
                    className="absolute inset-0 rounded-xl border-2 border-orange-500/30 pointer-events-none"
                    animate={{
                      scale: [1, 1.02, 1],
                      opacity: [0.3, 0.1, 0.3],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: 'easeInOut',
                      delay: index * 0.2,
                    }}
                  />
                </div>
                <div className="text-xs md:text-sm text-white/40 mt-2 uppercase tracking-wider">
                  {unit.label}
                </div>
              </div>
            ))}
          </motion.div>
        </motion.div>

        {/* Why this date? */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 1.2 }}
        >
          <div className="flex items-center justify-center gap-2 mb-6">
            <Sparkles className="h-5 w-5 text-orange-400" />
            <h3 className="text-lg font-semibold text-white/80">Why March 3, 2026?</h3>
          </div>

          <p className="text-center text-white/40 max-w-2xl mx-auto mb-6">
            Three independent sources — with no apparent connection — all point to the same moment in time.
          </p>
        </motion.div>

        {/* Evidence Cards */}
        <AnimatePresence>
          {showCards && (
            <motion.div
              className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              {EVIDENCE_CARDS.map((card, index) => {
                const Icon = card.icon
                return (
                  <motion.div
                    key={card.title}
                    className={`p-5 rounded-xl ${card.bgColor} border ${card.borderColor} relative overflow-hidden`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.2 + index * 0.15 }}
                    whileHover={{ y: -2 }}
                  >
                    {/* Hover glow */}
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-t from-transparent to-white/5 opacity-0"
                      whileHover={{ opacity: 1 }}
                    />

                    <div className="relative">
                      <div className="flex items-center gap-3 mb-3">
                        <div className={`p-2 rounded-lg bg-black/30 ${card.color}`}>
                          <Icon className="h-5 w-5" />
                        </div>
                        <h4 className="font-semibold text-white/80">{card.title}</h4>
                      </div>
                      <p className="text-sm text-white/50 mb-2">{card.description}</p>
                      <p className="text-xs text-white/50">{card.detail}</p>
                    </div>
                  </motion.div>
                )
              })}
            </motion.div>
          )}
        </AnimatePresence>

        {/* What happens on this date? */}
        <motion.div
          className="p-6 rounded-xl bg-white/5 border border-white/10 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.5, delay: 1.4 }}
        >
          <div className="flex items-center gap-2 mb-4">
            <HelpCircle className="h-5 w-5 text-white/50" />
            <h4 className="font-semibold text-white/80">What happens on this date?</h4>
          </div>
          <p className="text-sm text-white/50 leading-relaxed mb-4">
            According to our research, March 3, 2026 is when Qubic's time-locked mechanisms
            are scheduled to unlock. Whether this reveals something about Satoshi's identity,
            triggers a protocol change, or does something else entirely — that remains to be seen.
          </p>
          <div className="flex items-start gap-2 p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
            <AlertTriangle className="h-4 w-4 text-orange-400 shrink-0 mt-0.5" />
            <p className="text-xs text-orange-400/70">
              <strong className="text-orange-400">Disclaimer:</strong> This is a research finding,
              not a prediction or financial advice. The outcome is speculative.
            </p>
          </div>
        </motion.div>

        {/* Heartbeat effect */}
        <motion.div
          className="flex justify-center mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 1.6 }}
        >
          <div className="relative">
            <motion.div
              className="w-4 h-4 rounded-full bg-orange-500"
              animate={{
                scale: [1, 1.5, 1],
                opacity: [1, 0.5, 1],
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
            <motion.div
              className="absolute inset-0 w-4 h-4 rounded-full bg-orange-500"
              animate={{
                scale: [1, 3],
                opacity: [0.5, 0],
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                ease: 'easeOut',
              }}
            />
          </div>
        </motion.div>

        {/* Transition hint */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 1.8 }}
        >
          <p className="text-sm text-white/50 italic">
            "Let's review all the evidence we've gathered..."
          </p>
        </motion.div>
      </div>
    </JourneySection>
  )
}
