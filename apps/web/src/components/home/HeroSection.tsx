'use client'

import dynamic from 'next/dynamic'
import { motion } from 'framer-motion'
import { Link } from '@/navigation'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { BitcoinLogoSVG, QubicLogoSVG } from '@/components/logos'
import { GlitchText } from '@/components/ui/GlitchText'

// Dynamic import to avoid SSR issues with THREE.js
const GridScan = dynamic(() => import('@/components/ui/GridScan').then(mod => mod.GridScan), {
  ssr: false,
  loading: () => <div className="absolute inset-0 -z-10 bg-background" />,
})

function AnimatedFormula() {
  const formulaParts = ['625,284', ' = ', '283', ' x ', '47', '^2', ' + ', '137']

  return (
    <motion.div
      className="font-mono text-lg sm:text-xl md:text-2xl text-primary/80"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 1, duration: 0.5 }}
    >
      {formulaParts.map((part, index) => (
        <motion.span
          key={index}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 + index * 0.1, duration: 0.3 }}
          className={part === '625,284' ? 'text-primary font-bold' : ''}
        >
          {part}
        </motion.span>
      ))}
    </motion.div>
  )
}

export function HeroSection() {
  return (
    <section className="relative flex flex-col items-center justify-center py-24 md:py-32 text-center overflow-hidden">
      {/* Subtle GridScan background */}
      <div className="absolute inset-0 -z-10 opacity-40">
        <GridScan
          sensitivity={0.3}
          lineThickness={0.8}
          linesColor="#1a1a1a"
          gridScale={0.08}
          scanColor="#D4AF37"
          scanOpacity={0.25}
          enablePost
          bloomIntensity={0.3}
          chromaticAberration={0.001}
          noiseIntensity={0.008}
          scanDuration={4}
          scanDelay={2}
          scanGlow={0.4}
          scanSoftness={2.5}
        />
      </div>

      <div className="max-w-4xl mx-auto px-4">
        <motion.p
          className="text-sm font-medium tracking-widest text-muted-foreground uppercase mb-6"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          Academic Research Archive
        </motion.p>

        <motion.h1
          className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-serif font-bold tracking-tight mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <span className="bg-gradient-to-r from-[#D4AF37] via-[#D4AF37] to-[#D4AF37] bg-clip-text text-transparent">
            <GlitchText>The Discovery of a Hidden</GlitchText>
          </span>
          <br />
          <span className="text-foreground">
            <GlitchText minInterval={5000} maxInterval={10000}>Mathematical Bridge</GlitchText>
          </span>
        </motion.h1>

        <motion.p
          className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-6 leading-relaxed"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          How Bitcoin and Qubic are Connected Through Mathematics
        </motion.p>

        <motion.p
          className="text-sm sm:text-base text-muted-foreground/80 max-w-2xl mx-auto mb-10 leading-relaxed"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          In January 2026, a groundbreaking discovery revealed that Bitcoin's earliest
          blocks contain encoded data pointing directly to Qubic, a ternary computing
          network. This research documents the mathematical proof of this connection
          and what it means for the future of decentralized computing.
        </motion.p>

        <motion.div
          className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          <Link
            href="/docs"
            className={cn(
              buttonVariants({ size: 'lg' }),
              'font-medium px-8 transition-transform hover:scale-105'
            )}
          >
            Read the Full Research
          </Link>

          <Link
            href="/docs/results/formula-discovery"
            className={cn(
              buttonVariants({ variant: 'outline', size: 'lg' }),
              'font-medium px-8 transition-transform hover:scale-105'
            )}
          >
            See the Evidence
          </Link>
        </motion.div>

        <motion.div
          className="relative py-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.5 }}
        >
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-border" />
          </div>
          <div className="relative flex justify-center">
            <span className="bg-background px-4 sm:px-6 py-3 rounded-full border border-border flex items-center gap-3 sm:gap-4">
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 1.8, type: 'spring', stiffness: 200 }}
              >
                <BitcoinLogoSVG size={28} />
              </motion.div>
              <AnimatedFormula />
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 2, type: 'spring', stiffness: 200 }}
              >
                <QubicLogoSVG size={28} />
              </motion.div>
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
