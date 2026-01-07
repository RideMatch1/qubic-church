'use client'

import { useRef, useState, useEffect } from 'react'
import { motion, useInView } from 'framer-motion'
import { JourneySection } from '../JourneySection'
import { BookOpen, FileSearch, User, ExternalLink, Github, ArrowRight, CheckCircle2, Sparkles } from 'lucide-react'
import Link from 'next/link'

const MAIN_CTAS = [
  {
    icon: BookOpen,
    title: 'Read the Full Research',
    description: 'Complete academic documentation with all mathematical proofs and sources',
    href: '/docs/overview',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/20',
    hoverColor: 'hover:bg-blue-500/20',
  },
  {
    icon: FileSearch,
    title: 'Explore All Evidence',
    description: '46 discoveries organized by confidence level — verify everything yourself',
    href: '/evidence',
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/20',
    hoverColor: 'hover:bg-green-500/20',
  },
  {
    icon: User,
    title: 'Who is CFB?',
    description: 'Learn about Come-From-Beyond and his revolutionary work in cryptography',
    href: '/cfb',
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/20',
    hoverColor: 'hover:bg-orange-500/20',
  },
]

// Journey highlights for recap
const JOURNEY_HIGHLIGHTS = [
  { text: 'Bitcoin created in 2009 by Satoshi Nakamoto', color: 'text-orange-400' },
  { text: '1CFB address appears just 10 days later', color: 'text-orange-400' },
  { text: 'Hidden formula connects Block #283 to Qubic', color: 'text-purple-400' },
  { text: '22,000 Patoshi blocks remain untouched', color: 'text-orange-400' },
  { text: 'Anna Matrix encodes Bitcoin timestamps', color: 'text-purple-400' },
  { text: 'All paths converge on March 3, 2026', color: 'text-orange-400' },
]

export function CallSection() {
  const contentRef = useRef(null)
  const isInView = useInView(contentRef, { once: false, amount: 0.3 })
  const [showHighlights, setShowHighlights] = useState(false)
  const [completionProgress, setCompletionProgress] = useState(0)

  // Animate completion ring
  useEffect(() => {
    if (isInView) {
      const timer = setTimeout(() => setShowHighlights(true), 500)
      const progressTimer = setInterval(() => {
        setCompletionProgress(prev => {
          if (prev >= 100) {
            clearInterval(progressTimer)
            return 100
          }
          return prev + 2
        })
      }, 30)
      return () => {
        clearTimeout(timer)
        clearInterval(progressTimer)
      }
    } else {
      setShowHighlights(false)
      setCompletionProgress(0)
    }
  }, [isInView])

  return (
    <JourneySection id="call" background="transparent" className="flex items-center justify-center py-12 md:py-20">
      <div ref={contentRef} className="relative z-10 w-full max-w-4xl mx-auto px-4">
        {/* Final Chapter Header */}
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
              CONCLUSION
            </span>
          </motion.div>

          <motion.div
            className="inline-flex items-center gap-2 mb-4"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0.9 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Sparkles className="h-8 w-8 text-white/50" />
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-bold text-white/90 mb-4">
            Your Turn to Verify
          </h2>

          {/* Final message */}
          <motion.div
            className="max-w-2xl mx-auto space-y-4 mb-8"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <p className="text-lg text-white/50 leading-relaxed">
              You've seen the evidence. You've followed the math.
              Now the question is: <span className="text-white/80 font-medium">what do you think?</span>
            </p>
            <p className="text-base text-white/40 leading-relaxed">
              Everything we've presented can be independently verified.
              The blockchain is public. The formulas are calculable. The truth is out there.
            </p>
          </motion.div>
        </motion.div>

        {/* Journey Recap */}
        {showHighlights && (
          <motion.div
            className="p-6 rounded-2xl bg-gradient-to-b from-white/5 to-transparent border border-white/10 mb-10"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h3 className="text-center font-semibold text-white/80 mb-4">What We Discovered</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {JOURNEY_HIGHLIGHTS.map((item, index) => (
                <motion.div
                  key={index}
                  className="flex items-center gap-2 p-2 rounded-lg bg-black/30"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 + index * 0.1 }}
                >
                  <CheckCircle2 className={`h-4 w-4 ${item.color} shrink-0`} />
                  <span className="text-sm text-white/60">{item.text}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Main CTAs */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 30 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          {MAIN_CTAS.map((cta, index) => {
            const Icon = cta.icon
            return (
              <motion.div
                key={cta.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
                transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
              >
                <Link
                  href={cta.href}
                  className={`block p-6 rounded-xl ${cta.bgColor} border ${cta.borderColor} ${cta.hoverColor} transition-all group hover:scale-[1.02]`}
                >
                  <div className={`p-3 rounded-lg bg-black/30 ${cta.color} w-fit mb-4`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="font-semibold text-white/90 mb-2 flex items-center gap-2">
                    {cta.title}
                    <ArrowRight className="h-4 w-4 text-white/50 group-hover:text-white/60 group-hover:translate-x-1 transition-all" />
                  </h3>
                  <p className="text-sm text-white/50">{cta.description}</p>
                </Link>
              </motion.div>
            )
          })}
        </motion.div>

        {/* The Formula - Signature */}
        <motion.div
          className="text-center mb-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 0.8 }}
        >
          <div className="inline-block p-6 rounded-xl bg-gradient-to-r from-orange-950/20 via-purple-950/30 to-purple-950/20 border border-white/10">
            <div className="font-mono text-2xl md:text-3xl mb-2">
              <span className="text-purple-400">625,284</span>
              <span className="text-white/20"> = </span>
              <span className="text-orange-400">283</span>
              <span className="text-white/20"> × 47² + </span>
              <span className="text-green-400">137</span>
            </div>
            <p className="text-xs text-white/50">The equation that bridges 2009 and 2024</p>
          </div>
        </motion.div>

        {/* Completion Ring */}
        <motion.div
          className="flex flex-col items-center justify-center mb-10"
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0 }}
          transition={{ delay: 1, type: 'spring', stiffness: 200 }}
        >
          <div className="relative">
            <svg className="w-20 h-20" viewBox="0 0 100 100">
              {/* Background circle */}
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke="rgba(255,255,255,0.1)"
                strokeWidth="4"
              />
              {/* Progress circle */}
              <motion.circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke="url(#gradient)"
                strokeWidth="4"
                strokeLinecap="round"
                strokeDasharray={283}
                strokeDashoffset={283 - (283 * completionProgress) / 100}
                style={{
                  transformOrigin: 'center',
                  transform: 'rotate(-90deg)',
                }}
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#f97316" />
                  <stop offset="100%" stopColor="#a855f7" />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-sm text-white/60 font-bold font-mono">{completionProgress}%</span>
            </div>
          </div>
          <motion.p
            className="text-sm text-white/40 mt-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: completionProgress === 100 ? 1 : 0 }}
            transition={{ delay: 0.3 }}
          >
            Journey Complete
          </motion.p>
        </motion.div>

        {/* Social & Links */}
        <motion.div
          className="flex justify-center gap-4 mb-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 1.2 }}
        >
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-white/40 hover:text-white/60 text-sm"
          >
            <Github className="h-4 w-4" />
            Source Code
          </a>
        </motion.div>

        {/* Footer Quote */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 1.4 }}
        >
          <p className="text-xs text-white/20 mb-4">
            Independent research project • Not financial advice • Verify everything
          </p>
          <div className="max-w-lg mx-auto">
            <p className="text-sm text-white/50 italic">
              "The truth is incontrovertible. Malice may attack it, ignorance may deride it,
              but in the end, there it is."
            </p>
            <p className="text-xs text-white/20 mt-2">— Winston Churchill</p>
          </div>
        </motion.div>

        {/* Final fade to black */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 1.6 }}
        >
          <p className="text-xs text-white/10 font-mono">
            March 3, 2026
          </p>
        </motion.div>
      </div>
    </JourneySection>
  )
}
