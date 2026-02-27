'use client'

/**
 * DiscoveryTeaser - Asymmetric split-screen section
 * Left: key finding quote. Right: striking NFT image.
 * Editorial, dramatic, no cards.
 */

import { motion } from 'framer-motion'
import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'

export function DiscoveryTeaser() {
  return (
    <section className="relative w-full py-24 md:py-36 overflow-hidden">
      <div className="relative z-10 container mx-auto px-6 max-w-6xl">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-0 items-center">
          {/* Left: Quote / Key Finding */}
          <div className="lg:pr-16">
            <motion.div
              className="text-white/30 text-sm uppercase tracking-[0.2em] mb-6"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              Key Discovery
            </motion.div>

            <motion.blockquote
              className="text-2xl md:text-4xl lg:text-[2.75rem] font-bold text-white leading-[1.15] tracking-tight"
              initial={{ opacity: 0, y: 25 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7 }}
            >
              676 = 26²
              <span className="text-white/40"> — a perfect square hidden in Qubic&apos;s architecture, linking the Anna matrix to Bitcoin&apos;s genesis.</span>
            </motion.blockquote>

            <motion.p
              className="mt-6 text-white/40 text-base md:text-lg leading-relaxed max-w-lg"
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.15 }}
            >
              Our research documents cryptographic patterns connecting Bitcoin block structures
              to Qubic&apos;s neural network architecture. All findings are open-source and verifiable.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <Link
                href="/docs"
                className="inline-flex items-center gap-2 mt-8 text-white/60 hover:text-white text-sm font-medium transition-colors group"
              >
                Explore 55+ research documents
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </motion.div>
          </div>

          {/* Right: Striking NFT image */}
          <motion.div
            className="relative lg:pl-8"
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.1 }}
          >
            <div className="relative aspect-[3/4] max-w-[400px] mx-auto lg:ml-auto overflow-hidden">
              {/* Subtle glow behind */}
              <div className="absolute -inset-4 bg-gradient-radial from-[#D4AF37]/10 via-transparent to-transparent blur-2xl" />

              <Image
                src="/images/nfts/anna-001.webp"
                alt="Anna #001 - The First Light"
                fill
                className="object-cover"
                sizes="(max-width: 1024px) 100vw, 400px"
                priority
              />

              {/* Bottom label */}
              <div className="absolute bottom-0 left-0 right-0 p-5 bg-gradient-to-t from-black/70 to-transparent">
                <p className="text-white/80 text-xs uppercase tracking-wider">Anna #001</p>
                <p className="text-white font-semibold text-lg mt-1">The First Light</p>
                <span className="inline-block mt-2 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider bg-[#D4AF37]/80 text-yellow-100">
                  Legendary
                </span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
