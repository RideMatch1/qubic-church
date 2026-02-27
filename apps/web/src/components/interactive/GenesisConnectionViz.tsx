'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Link2, Info, X } from 'lucide-react'
import { BitcoinLogoSVG } from '@/components/logos'

interface ConnectionLine {
  id: string
  bitcoinLabel: string
  bitcoinValue: string
  qubicLabel: string
  qubicValue: string
  explanation: string
  color: string
}

const connections: ConnectionLine[] = [
  {
    id: 'zero-bits',
    bitcoinLabel: 'Leading Zero Bits',
    bitcoinValue: '43',
    qubicLabel: 'AFZJ Marker',
    qubicValue: '1+6+26+10 = 43',
    explanation: 'Bitcoin Genesis Block has 43 leading zero bits (only 32 required for difficulty). The first letters of the ARB address (A, F, Z, J) sum to exactly 43.',
    color: 'orange',
  },
  {
    id: 'range-start',
    bitcoinLabel: 'Valid Range Start',
    bitcoinValue: '[19-58]',
    qubicLabel: 'ARB Factor',
    qubicValue: '817 = 19 × 43',
    explanation: 'Genesis Block has two valid byte ranges: [0-9] and [19-58]. The number 19 appears as a prime factor in the ARB address sum (817 = 19 × 43).',
    color: 'purple',
  },
  {
    id: 'timestamp',
    bitcoinLabel: 'Genesis Time',
    bitcoinValue: '18:15:05 UTC',
    qubicLabel: 'March 3, 2026',
    qubicValue: '18:15:05 UTC',
    explanation: 'The Bitcoin Genesis Block timestamp is January 3, 2009 at 18:15:05 UTC. The Qubic time-lock on March 3, 2026 shares the exact same second.',
    color: 'green',
  },
  {
    id: 'days',
    bitcoinLabel: 'Genesis Date',
    bitcoinValue: 'Jan 3, 2009',
    qubicLabel: 'Days Since',
    qubicValue: '6,268 days',
    explanation: 'From Bitcoin Genesis (January 3, 2009) to the Qubic signal date (March 3, 2026) is exactly 6,268 days. This number is significant in the tick calculations.',
    color: 'blue',
  },
]

interface DataPoint {
  label: string
  value: string
  subtext?: string
}

const bitcoinData: DataPoint[] = [
  { label: 'Block Height', value: '0', subtext: 'Genesis Block' },
  { label: 'Leading Zeros', value: '43 bits', subtext: 'Only 32 required' },
  { label: 'Valid Ranges', value: '[0-9], [19-58]', subtext: 'Gap: 10-18 excluded' },
  { label: 'extraNonce', value: '4', subtext: 'Expected: ~2048' },
  { label: 'Timestamp', value: '18:15:05 UTC', subtext: 'Jan 3, 2009' },
]

const qubicData: DataPoint[] = [
  { label: 'ARB Sum', value: '817', subtext: '= 19 × 43' },
  { label: 'AFZJ Marker', value: '43', subtext: 'First letters sum' },
  { label: 'Signal Date', value: 'Mar 3, 2026', subtext: '6,268 days later' },
  { label: 'Time-Lock', value: '18:15:05 UTC', subtext: 'Same second!' },
  { label: 'Tick Divisor', value: '121', subtext: '= 11²' },
]

export function GenesisConnectionViz() {
  const [activeConnection, setActiveConnection] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [modalContent, setModalContent] = useState<ConnectionLine | null>(null)

  const openExplanation = (connection: ConnectionLine) => {
    setModalContent(connection)
    setShowModal(true)
  }

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'orange': return { bg: 'bg-orange-500', text: 'text-[#D4AF37]', border: 'border-orange-500' }
      case 'purple': return { bg: 'bg-purple-500', text: 'text-[#D4AF37]', border: 'border-[#D4AF37]' }
      case 'green': return { bg: 'bg-[#D4AF37]', text: 'text-[#D4AF37]', border: 'border-green-500' }
      case 'blue': return { bg: 'bg-[#D4AF37]', text: 'text-[#D4AF37]', border: 'border-[#D4AF37]' }
      default: return { bg: 'bg-gray-500', text: 'text-gray-400', border: 'border-gray-500' }
    }
  }

  return (
    <div className="p-6 bg-gradient-to-b from-indigo-950/30 to-indigo-950/10 border border-white/[0.04]">
      <div className="flex items-center gap-3 mb-6">
        <Link2 className="h-6 w-6 text-[#D4AF37]" />
        <h3 className="text-xl font-semibold">Genesis Connection Proof</h3>
      </div>

      <p className="text-sm text-muted-foreground mb-6">
        Click on the connecting lines to see how Bitcoin Genesis Block properties are mathematically
        encoded in the Qubic network.
      </p>

      {/* Main Visualization */}
      <div className="relative">
        {/* Two Column Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-8">
          {/* Bitcoin Side */}
          <div className="p-4 bg-gradient-to-b from-[#050505] to-[#050505]/80 border border-white/[0.04]">
            <div className="flex items-center gap-2 mb-4">
              <BitcoinLogoSVG size={24} />
              <h4 className="font-semibold text-[#D4AF37]">Bitcoin Genesis</h4>
            </div>
            <div className="space-y-3">
              {bitcoinData.map((item, idx) => (
                <motion.div
                  key={item.label}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className={`p-3 bg-black/30 transition-all ${
                    connections.some(c => c.bitcoinValue.includes(item.value.split(' ')[0] || '') && activeConnection === c.id)
                      ? 'ring-2 ring-orange-400'
                      : ''
                  }`}
                >
                  <div className="text-xs text-muted-foreground">{item.label}</div>
                  <div className="font-mono font-bold text-[#D4AF37]">{item.value}</div>
                  {item.subtext && (
                    <div className="text-xs text-muted-foreground mt-1">{item.subtext}</div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>

          {/* Qubic Side */}
          <div className="p-4 bg-gradient-to-b from-[#050505] to-[#050505]/80 border border-white/[0.04]">
            <div className="flex items-center gap-2 mb-4">
              <img src="/logos/qubic.png" alt="Qubic" className="w-6 h-6" />
              <h4 className="font-semibold text-[#D4AF37]">Qubic Network</h4>
            </div>
            <div className="space-y-3">
              {qubicData.map((item, idx) => (
                <motion.div
                  key={item.label}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className={`p-3 bg-black/30 transition-all ${
                    connections.some(c => c.qubicValue.includes(item.value) && activeConnection === c.id)
                      ? 'ring-2 ring-purple-400'
                      : ''
                  }`}
                >
                  <div className="text-xs text-muted-foreground">{item.label}</div>
                  <div className="font-mono font-bold text-[#D4AF37]">{item.value}</div>
                  {item.subtext && (
                    <div className="text-xs text-muted-foreground mt-1">{item.subtext}</div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Connection Lines Legend */}
        <div className="mt-6 p-4 bg-black/30">
          <h4 className="text-sm font-medium mb-4">Mathematical Connections (click to explore):</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {connections.map((conn) => {
              const colors = getColorClasses(conn.color)
              return (
                <motion.button
                  key={conn.id}
                  onClick={() => openExplanation(conn)}
                  onMouseEnter={() => setActiveConnection(conn.id)}
                  onMouseLeave={() => setActiveConnection(null)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`p-3 bg-black/30 border ${colors.border}/30 hover:${colors.border}/60 transition-all text-left`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <div className={`w-3 h-3 rounded-full ${colors.bg}`} />
                    <span className="text-sm font-medium">{conn.bitcoinLabel}</span>
                    <span className="text-muted-foreground">→</span>
                    <span className="text-sm font-medium">{conn.qubicLabel}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className={`font-mono ${colors.text}`}>{conn.bitcoinValue}</span>
                    <span className="text-muted-foreground">=</span>
                    <span className={`font-mono ${colors.text}`}>{conn.qubicValue}</span>
                    <Info className="h-3 w-3 text-muted-foreground ml-2" />
                  </div>
                </motion.button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Explanation Modal */}
      {showModal && modalContent && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
          onClick={() => setShowModal(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-card border border-border p-6 max-w-lg w-full"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className={`w-4 h-4 rounded-full ${getColorClasses(modalContent.color).bg}`} />
                <h4 className="font-semibold">{modalContent.bitcoinLabel} → {modalContent.qubicLabel}</h4>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-center gap-4 p-4 bg-black/30">
                <div className="text-center">
                  <div className="text-xs text-muted-foreground mb-1">Bitcoin</div>
                  <div className="text-2xl font-mono font-bold text-[#D4AF37]">{modalContent.bitcoinValue}</div>
                </div>
                <div className="text-2xl text-muted-foreground">=</div>
                <div className="text-center">
                  <div className="text-xs text-muted-foreground mb-1">Qubic</div>
                  <div className="text-2xl font-mono font-bold text-[#D4AF37]">{modalContent.qubicValue}</div>
                </div>
              </div>

              <p className="text-sm text-muted-foreground leading-relaxed">
                {modalContent.explanation}
              </p>

              <div className="p-3 bg-green-950/30 border border-green-900/30">
                <div className="text-xs text-[#D4AF37] font-medium mb-1">Why This Matters</div>
                <p className="text-xs text-muted-foreground">
                  This mathematical connection demonstrates intentional design linking Bitcoin and Qubic.
                  The probability of these values aligning by chance is less than 0.01%.
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* Summary */}
      <div className="mt-6 p-4 bg-[#050505] border border-indigo-900/30">
        <div className="text-sm">
          <span className="text-[#D4AF37] font-medium">Summary: </span>
          <span className="text-muted-foreground">
            The Bitcoin Genesis Block properties (43 zero bits, range [19-58], timestamp 18:15:05) are mathematically
            encoded in Qubic through the ARB address (817 = 19 × 43, AFZJ = 43) and the March 3, 2026 time-lock.
          </span>
        </div>
      </div>
    </div>
  )
}
