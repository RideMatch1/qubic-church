'use client'

import { motion } from 'framer-motion'
import { BitcoinLogoSVG, QubicLogoSVG } from '@/components/logos'

export function ConnectionBridgeDiagram() {
  return (
    <div className="w-full max-w-md mx-auto py-4">
      <div className="flex items-center justify-center gap-6">
        {/* Bitcoin side */}
        <motion.div
          className="flex flex-col items-center"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-[#D4AF37]/10 border-2 border-orange-500/50 flex items-center justify-center">
            <BitcoinLogoSVG size={40} />
          </div>
          <div className="mt-2 text-center">
            <div className="text-sm font-medium">Block #283</div>
            <div className="text-xs text-muted-foreground">(2009)</div>
          </div>
        </motion.div>

        {/* Bridge connection */}
        <motion.div
          className="flex-1 max-w-[120px] flex flex-col items-center"
          initial={{ opacity: 0, scaleX: 0 }}
          animate={{ opacity: 1, scaleX: 1 }}
          transition={{ duration: 0.8, delay: 0.5 }}
        >
          {/* 15 Years label */}
          <div className="text-xs text-muted-foreground mb-2">15 Years Apart</div>

          {/* Connection line with arrows */}
          <div className="w-full relative h-8 flex items-center">
            {/* Left arrow */}
            <svg width="12" height="12" className="text-primary absolute left-0">
              <path d="M8 2 L2 6 L8 10" fill="none" stroke="currentColor" strokeWidth="2" />
            </svg>

            {/* Line */}
            <div className="flex-1 mx-3 h-0.5 bg-gradient-to-r from-[#D4AF37] via-primary to-[#D4AF37] relative">
              {/* Animated data pulse */}
              <motion.div
                className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-primary rounded-full shadow-lg shadow-primary/50"
                animate={{ x: [0, 80, 0] }}
                transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
              />
            </div>

            {/* Right arrow */}
            <svg width="12" height="12" className="text-[#D4AF37] absolute right-0">
              <path d="M4 2 L10 6 L4 10" fill="none" stroke="currentColor" strokeWidth="2" />
            </svg>
          </div>

          {/* DATA label - centered below the line */}
          <motion.div
            className="mt-2 px-2 py-1 bg-primary/20  text-xs font-mono text-primary"
            animate={{
              opacity: [0.6, 1, 0.6],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          >
            DATA
          </motion.div>
        </motion.div>

        {/* Qubic side */}
        <motion.div
          className="flex flex-col items-center"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-[#D4AF37]/10 border-2 border-[#D4AF37]/30 flex items-center justify-center">
            <QubicLogoSVG size={40} />
          </div>
          <div className="mt-2 text-center">
            <div className="text-sm font-medium">Qubic Network</div>
            <div className="text-xs text-muted-foreground">(2024)</div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
