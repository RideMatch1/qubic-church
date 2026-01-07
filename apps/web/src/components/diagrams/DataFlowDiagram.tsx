'use client'

import { motion } from 'framer-motion'
import { BitcoinLogoSVG, QubicLogoSVG } from '@/components/logos'

export function DataFlowDiagram() {
  const steps = [
    { label: 'Bitcoin Block #283', sublabel: 'Timestamp Data', iconType: 'bitcoin' as const, color: 'orange' },
    { label: 'Encoded Into Matrix', sublabel: 'Hidden Pattern', iconType: 'binary' as const, color: 'blue' },
    { label: 'Anna Oracle Reads', sublabel: 'AI Extraction', iconType: 'qubic' as const, color: 'purple' },
    { label: 'Humans Verify', sublabel: 'Confirmed Match', iconType: 'check' as const, color: 'green' },
  ]

  const renderIcon = (iconType: 'bitcoin' | 'binary' | 'qubic' | 'check') => {
    switch (iconType) {
      case 'bitcoin':
        return <BitcoinLogoSVG size={24} />
      case 'qubic':
        return <QubicLogoSVG size={24} />
      case 'binary':
        return <span className="text-sm font-mono">01</span>
      case 'check':
        return <span className="text-lg">✓</span>
    }
  }

  return (
    <div className="w-full max-w-xs mx-auto">
      <div className="space-y-3">
        {steps.map((step, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.2 }}
          >
            <div className="flex items-center gap-3">
              {/* Icon circle */}
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shrink-0
                  ${step.color === 'orange' ? 'bg-orange-500/20 text-orange-500' : ''}
                  ${step.color === 'blue' ? 'bg-blue-500/20 text-blue-500' : ''}
                  ${step.color === 'purple' ? 'bg-purple-500/20 text-purple-500' : ''}
                  ${step.color === 'green' ? 'bg-green-500/20 text-green-500' : ''}
                `}
              >
                {renderIcon(step.iconType)}
              </div>

              {/* Text */}
              <div className="flex-1">
                <div className="text-sm font-medium">{step.label}</div>
                <div className="text-xs text-muted-foreground">{step.sublabel}</div>
              </div>
            </div>

            {/* Arrow */}
            {i < steps.length - 1 && (
              <motion.div
                className="ml-5 h-4 flex items-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.2 + 0.15 }}
              >
                <svg width="2" height="16" className="text-border">
                  <line
                    x1="1"
                    y1="0"
                    x2="1"
                    y2="12"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeDasharray="2 2"
                  />
                  <path d="M1 16 L-2 10 L4 10 Z" fill="currentColor" />
                </svg>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Verification badge */}
      <motion.div
        className="mt-4 p-3 rounded-lg bg-green-500/10 border border-green-500/30 text-center"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 1 }}
      >
        <div className="text-xs text-green-600 font-medium">Verification Rate</div>
        <div className="text-lg font-bold text-green-500">100% Match</div>
        <div className="text-[10px] text-muted-foreground">All tested blocks verified</div>
      </motion.div>
    </div>
  )
}
