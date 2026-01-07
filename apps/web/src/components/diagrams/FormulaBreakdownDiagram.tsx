'use client'

import { motion } from 'framer-motion'
import { BitcoinLogoSVG, QubicLogoSVG } from '@/components/logos'

interface FormulaBreakdownDiagramProps {
  animated?: boolean
  compact?: boolean
}

export function FormulaBreakdownDiagram({ animated = true, compact = false }: FormulaBreakdownDiagramProps) {
  const baseDelay = animated ? 0.3 : 0

  if (compact) {
    return (
      <div className="w-full">
        {/* Compact formula display */}
        <div className="text-center py-3 px-4 bg-card rounded-lg border border-border">
          <div className="font-mono text-lg md:text-xl font-bold flex flex-wrap justify-center items-baseline gap-1">
            <span className="text-primary">625,284</span>
            <span className="text-muted-foreground">=</span>
            <span className="text-orange-500">283</span>
            <span className="text-muted-foreground">x</span>
            <span className="text-blue-500">47<sup className="text-sm">2</sup></span>
            <span className="text-muted-foreground">+</span>
            <span className="text-green-500">137</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full max-w-sm mx-auto">
      <div className="space-y-4">
        {/* Main formula */}
        <motion.div
          className="text-center py-3 px-4 bg-card rounded-lg border border-border overflow-hidden"
          initial={animated ? { opacity: 0, y: 10 } : false}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="font-mono text-lg md:text-xl font-bold flex flex-wrap justify-center items-baseline gap-1">
            <motion.span
              className="text-primary"
              initial={animated ? { opacity: 0 } : false}
              animate={{ opacity: 1 }}
              transition={{ delay: baseDelay }}
            >
              625,284
            </motion.span>
            <motion.span
              className="text-muted-foreground"
              initial={animated ? { opacity: 0 } : false}
              animate={{ opacity: 1 }}
              transition={{ delay: baseDelay + 0.1 }}
            >
              =
            </motion.span>
            <motion.span
              className="text-orange-500"
              initial={animated ? { opacity: 0 } : false}
              animate={{ opacity: 1 }}
              transition={{ delay: baseDelay + 0.2 }}
            >
              283
            </motion.span>
            <motion.span
              className="text-muted-foreground"
              initial={animated ? { opacity: 0 } : false}
              animate={{ opacity: 1 }}
              transition={{ delay: baseDelay + 0.3 }}
            >
              x
            </motion.span>
            <motion.span
              className="text-blue-500"
              initial={animated ? { opacity: 0 } : false}
              animate={{ opacity: 1 }}
              transition={{ delay: baseDelay + 0.4 }}
            >
              47<sup className="text-sm">2</sup>
            </motion.span>
            <motion.span
              className="text-muted-foreground"
              initial={animated ? { opacity: 0 } : false}
              animate={{ opacity: 1 }}
              transition={{ delay: baseDelay + 0.5 }}
            >
              +
            </motion.span>
            <motion.span
              className="text-green-500"
              initial={animated ? { opacity: 0 } : false}
              animate={{ opacity: 1 }}
              transition={{ delay: baseDelay + 0.6 }}
            >
              137
            </motion.span>
          </div>
        </motion.div>

        {/* Breakdown boxes - 2x2 grid on mobile, 4 columns on larger */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <motion.div
            className="p-2 rounded-lg bg-primary/10 border border-primary/30 text-center"
            initial={animated ? { opacity: 0, y: 10 } : false}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: baseDelay + 0.8 }}
          >
            <div className="flex items-center justify-center gap-1 mb-1">
              <QubicLogoSVG size={16} />
            </div>
            <div className="font-mono text-sm font-bold text-primary">625,284</div>
            <div className="text-[9px] text-muted-foreground leading-tight">Qubic Address</div>
          </motion.div>

          <motion.div
            className="p-2 rounded-lg bg-orange-500/10 border border-orange-500/30 text-center"
            initial={animated ? { opacity: 0, y: 10 } : false}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: baseDelay + 0.9 }}
          >
            <div className="flex items-center justify-center gap-1 mb-1">
              <BitcoinLogoSVG size={16} />
            </div>
            <div className="font-mono text-sm font-bold text-orange-500">283</div>
            <div className="text-[9px] text-muted-foreground leading-tight">Block Number</div>
          </motion.div>

          <motion.div
            className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/30 text-center"
            initial={animated ? { opacity: 0, y: 10 } : false}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: baseDelay + 1.0 }}
          >
            <div className="font-mono text-sm font-bold text-blue-500">47<sup className="text-xs">2</sup></div>
            <div className="text-[9px] text-muted-foreground leading-tight">= 2,209</div>
          </motion.div>

          <motion.div
            className="p-2 rounded-lg bg-green-500/10 border border-green-500/30 text-center"
            initial={animated ? { opacity: 0, y: 10 } : false}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: baseDelay + 1.1 }}
          >
            <div className="font-mono text-sm font-bold text-green-500">137</div>
            <div className="text-[9px] text-muted-foreground leading-tight">Physics Const</div>
          </motion.div>
        </div>

        {/* Calculation steps */}
        <motion.div
          className="text-center text-xs text-muted-foreground space-y-0.5 font-mono"
          initial={animated ? { opacity: 0 } : false}
          animate={{ opacity: 1 }}
          transition={{ delay: baseDelay + 1.3 }}
        >
          <div><span className="text-orange-500">283</span> x <span className="text-blue-500">2,209</span> = 625,147</div>
          <div>625,147 + <span className="text-green-500">137</span> = <span className="text-primary font-bold">625,284</span></div>
        </motion.div>
      </div>
    </div>
  )
}
