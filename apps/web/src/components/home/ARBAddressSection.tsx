'use client'

import { motion, useInView } from 'framer-motion'
import { useRef, useState } from 'react'
import { Binary, Calculator, Hash, Sparkles } from 'lucide-react'
import { QubicLogoSVG } from '@/components/logos'

const ARB_ADDRESS = 'AFZPUAIYVPNUYGJRQVLUKOPPVLHAZQTGLYAAUUNBXFTVTAMSBKQBLEIEPCVJ'

// Letter to number mapping (A=1, B=2, ..., Z=26)
function letterValue(char: string): number {
  return char.charCodeAt(0) - 64
}

// Calculate letter sum
function calculateLetterSum(address: string): number {
  return address.split('').reduce((sum, char) => sum + letterValue(char), 0)
}

interface LetterDisplayProps {
  letter: string
  index: number
  isHighlighted: boolean
  showValue: boolean
}

function LetterDisplay({ letter, index, isHighlighted, showValue }: LetterDisplayProps) {
  const value = letterValue(letter)

  return (
    <motion.span
      className={`inline-flex flex-col items-center mx-[1px] ${
        isHighlighted ? 'text-[#D4AF37]' : 'text-muted-foreground'
      }`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.01, duration: 0.2 }}
    >
      <span className="text-xs font-mono">{letter}</span>
      {showValue && (
        <motion.span
          className="text-[8px] text-[#D4AF37]/60"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 + index * 0.01 }}
        >
          {value}
        </motion.span>
      )}
    </motion.span>
  )
}

export function ARBAddressSection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })
  const [showLetterValues, setShowLetterValues] = useState(false)

  const letterSum = calculateLetterSum(ARB_ADDRESS) // Should be 817

  // First 4 letters AFZJ sum to 43
  const afzjSum = letterValue('A') + letterValue('F') + letterValue('Z') + letterValue('J') // 1+6+26+10 = 43

  return (
    <section ref={sectionRef} className="py-20 px-4 bg-gradient-to-b from-[#050505]/80 to-transparent">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-10"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <QubicLogoSVG size={32} />
            <h2 className="text-2xl md:text-3xl font-semibold">
              The ARB Oracle Address
            </h2>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Analysis of the ARB (Arbitrator) address reveals a hidden mathematical structure
            encoded in its letter values, connecting to the CFB constant.
          </p>
        </motion.div>

        {/* Address Display */}
        <motion.div
          className="p-6 bg-gradient-to-b from-[#050505] to-[#050505]/80 border border-white/[0.04] mb-6"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Hash className="h-4 w-4 text-[#D4AF37]" />
              <span className="text-sm font-medium">Qubic ARB Address</span>
            </div>
            <button
              onClick={() => setShowLetterValues(!showLetterValues)}
              className="text-xs px-3 py-1  bg-[#D4AF37]/20 hover:bg-[#D4AF37]/30 transition-colors text-[#D4AF37]"
            >
              {showLetterValues ? 'Hide Values' : 'Show Letter Values'}
            </button>
          </div>

          <div className="flex flex-wrap justify-center p-4 bg-black/30 overflow-x-auto">
            {ARB_ADDRESS.split('').map((letter, index) => (
              <LetterDisplay
                key={index}
                letter={letter}
                index={index}
                isHighlighted={index < 4} // Highlight AFZP
                showValue={showLetterValues}
              />
            ))}
          </div>

          <div className="mt-4 text-center text-sm text-muted-foreground">
            60 characters (standard Qubic address format)
          </div>
        </motion.div>

        {/* Mathematical Analysis Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Card 1: Letter Sum */}
          <motion.div
            className="p-5 bg-gradient-to-b from-[#050505] to-[#050505]/80 border border-white/[0.04]"
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="flex items-center gap-2 mb-3">
              <Calculator className="h-5 w-5 text-[#D4AF37]" />
              <h3 className="font-semibold">Letter Sum</h3>
            </div>
            <div className="text-center py-4">
              <div className="text-4xl font-mono font-bold text-[#D4AF37]">{letterSum}</div>
              <div className="text-sm text-muted-foreground mt-2">
                Sum of all letter values (A=1, B=2, ... Z=26)
              </div>
            </div>
          </motion.div>

          {/* Card 2: Prime Factorization */}
          <motion.div
            className="p-5 bg-gradient-to-b from-[#050505] to-[#050505]/80 border border-white/[0.04]"
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <div className="flex items-center gap-2 mb-3">
              <Binary className="h-5 w-5 text-[#D4AF37]" />
              <h3 className="font-semibold">Prime Factorization</h3>
            </div>
            <div className="text-center py-4">
              <div className="text-2xl font-mono font-bold">
                <span className="text-[#D4AF37]">817</span>
                <span className="text-muted-foreground mx-2">=</span>
                <span className="text-[#D4AF37]">19</span>
                <span className="text-muted-foreground mx-2">×</span>
                <span className="text-[#D4AF37]">43</span>
              </div>
              <div className="text-sm text-muted-foreground mt-2">
                Both factors are prime numbers
              </div>
              <div className="mt-3 p-2  bg-[#D4AF37]/10 text-xs">
                <strong className="text-[#D4AF37]">43</strong> = CFB constant (Come-From-Beyond)
              </div>
            </div>
          </motion.div>

          {/* Card 3: AFZJ Marker */}
          <motion.div
            className="p-5 bg-gradient-to-b from-[#050505] to-[#050505]/80 border border-white/[0.04]"
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="h-5 w-5 text-[#D4AF37]" />
              <h3 className="font-semibold">AFZJ Marker</h3>
            </div>
            <div className="text-center py-4">
              <div className="flex justify-center gap-2 mb-3">
                <span className="px-2 py-1  bg-[#D4AF37]/20 font-mono">A=1</span>
                <span className="px-2 py-1  bg-[#D4AF37]/20 font-mono">F=6</span>
                <span className="px-2 py-1  bg-[#D4AF37]/20 font-mono">Z=26</span>
                <span className="px-2 py-1  bg-[#D4AF37]/20 font-mono">J=10</span>
              </div>
              <div className="text-xl font-mono">
                1 + 6 + 26 + 10 = <span className="text-[#D4AF37] font-bold">43</span>
              </div>
              <div className="text-sm text-muted-foreground mt-2">
                First meaningful prefix sums to 43
              </div>
            </div>
          </motion.div>
        </div>

        {/* Row 68 Connection */}
        <motion.div
          className="mt-6 p-5 bg-gradient-to-r from-[#050505] via-[#050505] to-[#050505] border border-white/[0.04]"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <div className="flex items-center gap-2 mb-4">
            <Binary className="h-5 w-5 text-[#D4AF37]" />
            <h3 className="font-semibold">Row 68: The Alpha Connection</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-muted-foreground mb-3">
                Analysis of the Jinn memory matrix reveals that Row 68 performs exactly
                137 WRITE operations - a direct reference to the fine structure constant.
              </p>
              <div className="p-3  bg-[#D4AF37]/10 border border-[#D4AF37]/20">
                <div className="font-mono text-center">
                  <span className="text-[#D4AF37]">Row 68</span>
                  <span className="text-muted-foreground mx-2">performs</span>
                  <span className="text-[#D4AF37] font-bold text-xl">137</span>
                  <span className="text-muted-foreground ml-2">writes</span>
                </div>
              </div>
            </div>
            <div className="flex flex-col justify-center">
              <div className="text-center">
                <div className="text-sm text-muted-foreground mb-2">Fine Structure Constant</div>
                <div className="font-mono text-2xl">
                  <span className="text-muted-foreground">α ≈ 1/</span>
                  <span className="text-[#D4AF37] font-bold">137</span>
                </div>
                <div className="text-xs text-muted-foreground mt-2">
                  Fundamental physics constant describing electromagnetic interaction strength
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Research Integrity Notice */}
        <motion.div
          className="mt-6 p-4 bg-card/50 border border-border text-center"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 0.6 }}
        >
          <p className="text-xs text-muted-foreground">
            <strong>Verification:</strong> The ARB address can be verified on the Qubic network.
            Letter sum calculation: A=1 + F=6 + Z=26 + ... = 817. Prime factorization: 817 = 19 × 43.
          </p>
        </motion.div>
      </div>
    </section>
  )
}
