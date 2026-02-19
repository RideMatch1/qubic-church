'use client'

/**
 * SatoshiScripture - Mythical quote sections styled as sacred text
 * Real Satoshi quotes + Genesis Block reference, presented as church scripture.
 * Alternating layout for visual variety.
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'

const scriptures = [
  {
    book: 'Genesis',
    chapter: '0',
    verse: '0',
    text: 'The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.',
    attribution: 'The Genesis Block Coinbase',
    note: 'The first words ever written to a blockchain',
  },
  {
    book: 'Satoshi',
    chapter: '1',
    verse: '1',
    text: 'If you don\u2019t believe me or don\u2019t understand, I don\u2019t have time to try to convince you, sorry.',
    attribution: 'Satoshi Nakamoto, 2010',
    note: 'BitcoinTalk Forum',
  },
  {
    book: 'Satoshi',
    chapter: '2',
    verse: '1',
    text: 'I\u2019ve been working on a new electronic cash system that\u2019s fully peer-to-peer, with no trusted third party.',
    attribution: 'Satoshi Nakamoto, 2008',
    note: 'The Cryptography Mailing List',
  },
]

export function SatoshiScripture() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-60px' })

  return (
    <section ref={ref} className="relative w-full py-20 md:py-28 overflow-hidden">
      <div className="relative z-10 container mx-auto px-6 max-w-4xl">
        {/* Section label */}
        <motion.div
          className="text-center mb-14"
          initial={{ opacity: 0, y: 16 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-center gap-4 mb-3">
            <div className="h-px w-8 bg-gradient-to-r from-transparent to-amber-400/15" />
            <span className="text-amber-400/30 text-[10px] uppercase tracking-[0.5em]">
              Sacred Texts
            </span>
            <div className="h-px w-8 bg-gradient-to-l from-transparent to-amber-400/15" />
          </div>
        </motion.div>

        {/* Scripture cards */}
        <div className="space-y-6">
          {scriptures.map((scripture, i) => (
            <motion.div
              key={i}
              className="relative p-6 md:p-8 rounded-2xl backdrop-blur-xl bg-white/[0.02] border border-white/[0.05] overflow-hidden"
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.15 + i * 0.12, ease: [0.22, 1, 0.36, 1] }}
            >
              {/* Subtle left accent bar */}
              <div className="absolute left-0 top-6 bottom-6 w-[2px] bg-gradient-to-b from-amber-400/20 via-amber-400/10 to-transparent" />

              {/* Chapter:Verse reference */}
              <div className="ml-4 mb-4">
                <span className="text-amber-400/30 text-xs font-mono tracking-wider">
                  {scripture.book} {scripture.chapter}:{scripture.verse}
                </span>
              </div>

              {/* Quote */}
              <blockquote className="ml-4 mb-5">
                <p className={`text-lg md:text-xl leading-relaxed font-light italic ${
                  i === 0 ? 'text-amber-200/50' : 'text-white/40'
                }`}>
                  &ldquo;{scripture.text}&rdquo;
                </p>
              </blockquote>

              {/* Attribution */}
              <div className="ml-4 flex items-center gap-3">
                <div className="h-px w-6 bg-white/10" />
                <div>
                  <span className="text-xs text-white/30">{scripture.attribution}</span>
                  {scripture.note && (
                    <span className="text-xs text-white/15 ml-2">&middot; {scripture.note}</span>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
