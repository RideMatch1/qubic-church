'use client'

import { motion } from 'framer-motion'
import { Link } from '@/navigation'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { GlitchText } from '@/components/ui/GlitchText'
import { User, FileText, Clock, Brain } from 'lucide-react'

export function CFBHero() {
  return (
      <section className="relative flex flex-col items-center justify-center py-20 md:py-28 text-center overflow-hidden">
        {/* Animated background gradient */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-emerald-500/5 via-transparent to-transparent" />
          {/* Grid pattern overlay */}
          <div
            className="absolute inset-0 opacity-[0.02]"
            style={{
              backgroundImage: `linear-gradient(to right, currentColor 1px, transparent 1px),
                                linear-gradient(to bottom, currentColor 1px, transparent 1px)`,
              backgroundSize: '64px 64px',
            }}
          />
        </div>

        <div className="max-w-4xl mx-auto px-4">
          <motion.div
            className="flex items-center justify-center gap-2 mb-6"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span className="text-sm font-medium tracking-widest text-muted-foreground uppercase">
              Forensic Profile
            </span>
          </motion.div>

          <motion.h1
            className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-serif font-bold tracking-tight mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <span className="bg-gradient-to-r from-emerald-400 via-teal-500 to-emerald-500 bg-clip-text text-transparent">
              <GlitchText>Come-from-Beyond</GlitchText>
            </span>
            <br />
            <span className="text-foreground">
              <GlitchText minInterval={5000} maxInterval={10000}>Sergey Ivancheglo</GlitchText>
            </span>
          </motion.h1>

          <motion.p
            className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-6 leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            Comprehensive forensic analysis of the cryptographer behind NXT, IOTA, and Qubic
          </motion.p>

          <motion.p
            className="text-sm sm:text-base text-muted-foreground/80 max-w-2xl mx-auto mb-10 leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            This archive contains 26,000+ data points spanning 17 years of digital forensics,
            stylometry analysis, mathematical proofs, and the investigation into the Satoshi connection.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          >
            <Link
              href="/cfb/satoshi"
              className={cn(
                buttonVariants({ size: 'lg' }),
                'font-medium px-8 transition-transform hover:scale-105 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600'
              )}
            >
              Explore Satoshi Evidence
            </Link>

            <Link
              href="/cfb/timeline"
              className={cn(
                buttonVariants({ variant: 'outline', size: 'lg' }),
                'font-medium px-8 transition-transform hover:scale-105'
              )}
            >
              View Full Timeline
            </Link>
          </motion.div>

          {/* Quick Stats */}
          <motion.div
            className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.5 }}
          >
            {[
              { label: 'Stylometry Match', value: '99.8%', sublabel: 'vs Satoshi', icon: Brain },
              { label: 'Data Points', value: '26K+', sublabel: 'Analyzed', icon: FileText },
              { label: 'Time Span', value: '17 Years', sublabel: '2007-2024', icon: Clock },
              { label: 'Confidence', value: '91%', sublabel: 'Overall', icon: User },
            ].map((stat, idx) => {
              const Icon = stat.icon
              return (
                <motion.div
                  key={stat.label}
                  className="p-4 rounded-lg border border-border bg-card/50 backdrop-blur-sm"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.1 + idx * 0.1 }}
                >
                  <div className="flex justify-center mb-2 text-emerald-500">
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="text-2xl font-bold text-primary">{stat.value}</div>
                  <div className="text-sm font-medium text-foreground">{stat.label}</div>
                  <div className="text-xs text-muted-foreground">{stat.sublabel}</div>
                </motion.div>
              )
            })}
          </motion.div>
        </div>
      </section>
  )
}
