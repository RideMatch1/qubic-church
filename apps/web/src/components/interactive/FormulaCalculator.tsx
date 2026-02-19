'use client'

import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Calculator, Check, X, Info } from 'lucide-react'

// The correct values that produce the boot address
const CORRECT_BLOCK = 283
const CORRECT_PRIME = 47
const CORRECT_ALPHA = 137
const MEMORY_SIZE = 16384 // 128 x 128

interface CalculationStep {
  label: string
  formula: string
  result: number | string
  isCorrect?: boolean
}

export function FormulaCalculator() {
  const [blockHeight, setBlockHeight] = useState(CORRECT_BLOCK)
  const [primeValue, setPrimeValue] = useState(CORRECT_PRIME)
  const [alphaValue, setAlphaValue] = useState(CORRECT_ALPHA)
  const [showExplanation, setShowExplanation] = useState<string | null>(null)

  const calculations = useMemo(() => {
    const primeSquared = primeValue * primeValue
    const step1 = blockHeight * primeSquared
    const patternValue = step1 + alphaValue
    const bootAddress = patternValue % MEMORY_SIZE
    const row = Math.floor(bootAddress / 128)
    const col = bootAddress % 128

    const isCorrectFormula =
      blockHeight === CORRECT_BLOCK &&
      primeValue === CORRECT_PRIME &&
      alphaValue === CORRECT_ALPHA

    const steps: CalculationStep[] = [
      {
        label: 'Prime Squared',
        formula: `${primeValue}\u00B2 = ${primeValue} \u00D7 ${primeValue}`,
        result: primeSquared,
      },
      {
        label: 'Block \u00D7 Prime\u00B2',
        formula: `${blockHeight} \u00D7 ${primeSquared}`,
        result: step1.toLocaleString(),
      },
      {
        label: 'Pattern Value',
        formula: `${step1.toLocaleString()} + ${alphaValue}`,
        result: patternValue.toLocaleString(),
        isCorrect: patternValue === 625284,
      },
      {
        label: 'Boot Address',
        formula: `${patternValue.toLocaleString()} mod ${MEMORY_SIZE.toLocaleString()}`,
        result: bootAddress.toLocaleString(),
        isCorrect: bootAddress === 2692,
      },
      {
        label: 'Matrix Position',
        formula: `Row ${row}, Column ${col}`,
        result: `Address ${bootAddress}`,
        isCorrect: row === 21 && col === 4,
      },
    ]

    return { steps, isCorrectFormula, row, col, bootAddress, patternValue }
  }, [blockHeight, primeValue, alphaValue])

  const explanations: Record<string, string> = {
    block: 'Block #283 is the 61st prime number, mined on January 12, 2009. It\'s one of the earliest Bitcoin blocks from the Satoshi era.',
    prime: '47 is the 15th prime number. Its square (2,209) creates a scaling factor that maps perfectly to Jinn memory size.',
    alpha: '137 is the fine structure constant (\u03B1 \u2248 1/137.036), a fundamental physics constant that appears throughout the system.',
    row21: 'Row 21 is the Bitcoin Input Layer in Jinn architecture. This is where Block #283 data enters the ternary processing system.',
  }

  return (
    <div className="rounded-2xl bg-white/[0.02] border border-white/[0.08] backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 pt-6 pb-0 md:px-8 md:pt-8">
        <div className="flex items-center gap-3 mb-8">
          <Calculator className="h-5 w-5 text-white/40" />
          <h3 className="text-xl font-semibold text-white">Formula Calculator</h3>
        </div>
      </div>

      {/* Formula Display */}
      <div className="mx-6 md:mx-8 mb-8 p-5 md:p-6 rounded-xl backdrop-blur-xl bg-white/[0.03] border border-white/[0.08] text-center">
        <div className="text-2xl md:text-3xl lg:text-4xl font-mono mb-3 leading-relaxed">
          <span className="text-orange-400/80">{blockHeight}</span>
          <span className="text-white/30"> &times; </span>
          <span className="text-purple-400/80">{primeValue}&sup2;</span>
          <span className="text-white/30"> + </span>
          <span className="text-green-400/80">{alphaValue}</span>
          <span className="text-white/30"> = </span>
          <span className={calculations.patternValue === 625284 ? 'text-green-400/90' : 'text-red-400/70'}>
            {calculations.patternValue.toLocaleString()}
          </span>
        </div>
        {calculations.isCorrectFormula && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="inline-flex items-center gap-2 text-green-400/70 text-sm"
          >
            <Check className="h-4 w-4" />
            <span>Correct Formula: 625,284 = 283 &times; 47&sup2; + 137</span>
          </motion.div>
        )}
      </div>

      {/* Sliders */}
      <div className="px-6 md:px-8 space-y-7 mb-8">
        {/* Block Height Slider */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <label className="text-sm font-medium flex items-center gap-2">
              <span className="text-orange-400/80">Block Height</span>
              <button
                onClick={() => setShowExplanation(showExplanation === 'block' ? null : 'block')}
                className="text-white/30 hover:text-orange-400/70 transition-colors"
              >
                <Info className="h-3.5 w-3.5" />
              </button>
            </label>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm text-orange-400/80">{blockHeight}</span>
              {blockHeight === CORRECT_BLOCK ? (
                <Check className="h-3.5 w-3.5 text-green-400/60" />
              ) : (
                <X className="h-3.5 w-3.5 text-red-400/40" />
              )}
            </div>
          </div>
          <input
            type="range"
            min="1"
            max="500"
            value={blockHeight}
            onChange={(e) => setBlockHeight(Number(e.target.value))}
            className="w-full h-1.5 bg-white/[0.06] rounded-full appearance-none cursor-pointer accent-orange-400"
          />
          <div className="flex justify-between text-xs text-white/25 mt-1.5">
            <span>1</span>
            <span className={blockHeight === CORRECT_BLOCK ? 'text-orange-400/60 font-medium' : ''}>
              283 (correct)
            </span>
            <span>500</span>
          </div>
          {showExplanation === 'block' && (
            <motion.p
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="text-xs text-white/40 mt-3 p-3 bg-white/[0.02] border border-white/[0.05] rounded-lg leading-relaxed"
            >
              {explanations.block}
            </motion.p>
          )}
        </div>

        {/* Prime Value Slider */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <label className="text-sm font-medium flex items-center gap-2">
              <span className="text-purple-400/80">Prime Value (squared)</span>
              <button
                onClick={() => setShowExplanation(showExplanation === 'prime' ? null : 'prime')}
                className="text-white/30 hover:text-purple-400/70 transition-colors"
              >
                <Info className="h-3.5 w-3.5" />
              </button>
            </label>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm text-purple-400/80">
                {primeValue}&sup2; = {primeValue * primeValue}
              </span>
              {primeValue === CORRECT_PRIME ? (
                <Check className="h-3.5 w-3.5 text-green-400/60" />
              ) : (
                <X className="h-3.5 w-3.5 text-red-400/40" />
              )}
            </div>
          </div>
          <input
            type="range"
            min="2"
            max="100"
            value={primeValue}
            onChange={(e) => setPrimeValue(Number(e.target.value))}
            className="w-full h-1.5 bg-white/[0.06] rounded-full appearance-none cursor-pointer accent-purple-400"
          />
          <div className="flex justify-between text-xs text-white/25 mt-1.5">
            <span>2</span>
            <span className={primeValue === CORRECT_PRIME ? 'text-purple-400/60 font-medium' : ''}>
              47 (correct)
            </span>
            <span>100</span>
          </div>
          {showExplanation === 'prime' && (
            <motion.p
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="text-xs text-white/40 mt-3 p-3 bg-white/[0.02] border border-white/[0.05] rounded-lg leading-relaxed"
            >
              {explanations.prime}
            </motion.p>
          )}
        </div>

        {/* Alpha Slider */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <label className="text-sm font-medium flex items-center gap-2">
              <span className="text-green-400/80">Alpha Constant (&alpha;)</span>
              <button
                onClick={() => setShowExplanation(showExplanation === 'alpha' ? null : 'alpha')}
                className="text-white/30 hover:text-green-400/70 transition-colors"
              >
                <Info className="h-3.5 w-3.5" />
              </button>
            </label>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm text-green-400/80">{alphaValue}</span>
              {alphaValue === CORRECT_ALPHA ? (
                <Check className="h-3.5 w-3.5 text-green-400/60" />
              ) : (
                <X className="h-3.5 w-3.5 text-red-400/40" />
              )}
            </div>
          </div>
          <input
            type="range"
            min="1"
            max="200"
            value={alphaValue}
            onChange={(e) => setAlphaValue(Number(e.target.value))}
            className="w-full h-1.5 bg-white/[0.06] rounded-full appearance-none cursor-pointer accent-green-400"
          />
          <div className="flex justify-between text-xs text-white/25 mt-1.5">
            <span>1</span>
            <span className={alphaValue === CORRECT_ALPHA ? 'text-green-400/60 font-medium' : ''}>
              137 (correct)
            </span>
            <span>200</span>
          </div>
          {showExplanation === 'alpha' && (
            <motion.p
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="text-xs text-white/40 mt-3 p-3 bg-white/[0.02] border border-white/[0.05] rounded-lg leading-relaxed"
            >
              {explanations.alpha}
            </motion.p>
          )}
        </div>
      </div>

      {/* Calculation Steps */}
      <div className="px-6 md:px-8 pb-2">
        <div className="text-white/25 text-xs uppercase tracking-[0.2em] mb-4">
          Calculation Steps
        </div>
        <div className="space-y-2.5">
          {calculations.steps.map((step, index) => (
            <motion.div
              key={step.label}
              initial={{ opacity: 0, x: -15 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.08 }}
              className="flex items-center justify-between p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.08]"
            >
              <div>
                <div className="text-sm font-medium text-white/70">{step.label}</div>
                <div className="text-xs text-white/30 font-mono mt-0.5">{step.formula}</div>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="font-mono text-base text-white/80">{step.result}</span>
                {step.isCorrect !== undefined && (
                  step.isCorrect ? (
                    <Check className="h-4 w-4 text-green-400/60" />
                  ) : (
                    <X className="h-4 w-4 text-red-400/50" />
                  )
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Result Explanation */}
      {calculations.row === 21 && calculations.col === 4 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mx-6 md:mx-8 mt-5 p-4 rounded-xl bg-green-500/[0.04] border border-green-500/[0.12]"
        >
          <div className="flex items-start gap-3">
            <Check className="h-4 w-4 text-green-400/70 mt-0.5 shrink-0" />
            <div>
              <div className="text-sm font-medium text-green-400/80">Row 21, Column 4 -- Bitcoin Input Layer</div>
              <p className="text-xs text-white/35 mt-1.5 leading-relaxed">
                {explanations.row21}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Reset Button */}
      <div className="px-6 md:px-8 py-6 mt-2 text-center">
        <button
          onClick={() => {
            setBlockHeight(CORRECT_BLOCK)
            setPrimeValue(CORRECT_PRIME)
            setAlphaValue(CORRECT_ALPHA)
          }}
          className="px-5 py-2.5 text-sm rounded-xl bg-white/[0.06] border border-white/[0.10] text-white/60 hover:bg-white/[0.10] hover:text-white/80 transition-all duration-300"
        >
          Reset to Correct Values
        </button>
      </div>
    </div>
  )
}
