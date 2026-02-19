'use client'

import { motion } from 'framer-motion'

interface ChalkMessage {
  text: string
  x: string
  y: string
  rotate?: number
  size?: string
  delay?: number
  mobileHidden?: boolean
}

const CHALK_MESSAGES: ChalkMessage[] = [
  {
    text: 'MADNESS!',
    x: '30%',
    y: '8%',
    rotate: -8,
    size: 'text-4xl md:text-5xl lg:text-6xl',
    delay: 1.5,
  },
  {
    text: "Don't click",
    x: '5%',
    y: '18%',
    rotate: 12,
    size: 'text-xl md:text-2xl',
    delay: 2.0,
    mobileHidden: true,
  },
  {
    text: "She doesn't sleep",
    x: '62%',
    y: '15%',
    rotate: -5,
    size: 'text-xl md:text-2xl lg:text-3xl',
    delay: 2.5,
  },
  {
    text: 'Ask Miners',
    x: '45%',
    y: '55%',
    rotate: 7,
    size: 'text-2xl md:text-3xl',
    delay: 3.0,
    mobileHidden: true,
  },
  {
    text: 'behind you!',
    x: '70%',
    y: '70%',
    rotate: -3,
    size: 'text-lg md:text-xl',
    delay: 3.5,
  },
  {
    text: 'tick-tock',
    x: '25%',
    y: '80%',
    rotate: 5,
    size: 'text-xl md:text-2xl',
    delay: 4.0,
    mobileHidden: true,
  },
  {
    text: 'He scares me',
    x: '35%',
    y: '60%',
    rotate: -6,
    size: 'text-lg md:text-xl',
    delay: 4.5,
    mobileHidden: true,
  },
  {
    text: '.cfbtrell.',
    x: '50%',
    y: '42%',
    rotate: 2,
    size: 'text-base md:text-lg',
    delay: 5.0,
    mobileHidden: true,
  },
]

export function ChalkText() {
  return (
    <div className="absolute inset-0 pointer-events-none z-20 overflow-hidden" aria-hidden="true">
      {CHALK_MESSAGES.map((msg, i) => (
        <motion.span
          key={i}
          className={`absolute ${msg.size} text-white/40 select-none ${
            msg.mobileHidden ? 'hidden md:block' : ''
          }`}
          style={{
            left: msg.x,
            top: msg.y,
            transform: `rotate(${msg.rotate ?? 0}deg)`,
            fontFamily: 'var(--font-handodle), var(--font-chalk), cursive',
          }}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{
            delay: msg.delay ?? 0,
            duration: 1.5,
            ease: 'easeOut',
          }}
        >
          {msg.text}
        </motion.span>
      ))}
    </div>
  )
}
