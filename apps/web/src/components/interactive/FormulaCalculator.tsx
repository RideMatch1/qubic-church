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
        formula: `${primeValue}² = ${primeValue} × ${primeValue}`,
        result: primeSquared,
      },
      {
        label: 'Block × Prime²',
        formula: `${blockHeight} × ${primeSquared}`,
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
    alpha: '137 is the fine structure constant (α ≈ 1/137.036), a fundamental physics constant that appears throughout the system.',
    row21: 'Row 21 is the Bitcoin Input Layer in Jinn architecture. This is where Block #283 data enters the ternary processing system.',
  }

  return (
    <div className="p-6 rounded-xl bg-gradient-to-b from-blue-950/30 to-blue-950/10 border border-blue-900/50">
      <div className="flex items-center gap-3 mb-6">
        <Calculator className="h-6 w-6 text-blue-400" />
        <h3 className="text-xl font-semibold">Formula Calculator</h3>
      </div>

      {/* The Formula Display */}
      <div className="text-center mb-8 p-4 bg-black/30 rounded-lg">
        <div className="text-2xl md:text-3xl font-mono mb-2">
          <span className="text-orange-400">{blockHeight}</span>
          <span className="text-muted-foreground"> × </span>
          <span className="text-purple-400">{primeValue}²</span>
          <span className="text-muted-foreground"> + </span>
          <span className="text-green-400">{alphaValue}</span>
          <span className="text-muted-foreground"> = </span>
          <span className={calculations.patternValue === 625284 ? 'text-green-400' : 'text-red-400'}>
            {calculations.patternValue.toLocaleString()}
          </span>
        </div>
        {calculations.isCorrectFormula && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="inline-flex items-center gap-2 text-green-400 text-sm mt-2"
          >
            <Check className="h-4 w-4" />
            Correct Formula: 625,284 = 283 × 47² + 137
          </motion.div>
        )}
      </div>

      {/* Sliders */}
      <div className="space-y-6 mb-8">
        {/* Block Height Slider */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <span className="text-orange-400">Block Height</span>
              <button
                onClick={() => setShowExplanation(showExplanation === 'block' ? null : 'block')}
                className="text-muted-foreground hover:text-orange-400 transition-colors"
              >
                <Info className="h-4 w-4" />
              </button>
            </label>
            <span className="font-mono text-orange-400">{blockHeight}</span>
          </div>
          <input
            type="range"
            min="1"
            max="500"
            value={blockHeight}
            onChange={(e) => setBlockHeight(Number(e.target.value))}
            className="w-full h-2 bg-orange-950 rounded-lg appearance-none cursor-pointer accent-orange-400"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>1</span>
            <span className={blockHeight === 283 ? 'text-orange-400 font-bold' : ''}>283 (correct)</span>
            <span>500</span>
          </div>
          {showExplanation === 'block' && (
            <motion.p
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="text-xs text-muted-foreground mt-2 p-2 bg-black/20 rounded"
            >
              {explanations.block}
            </motion.p>
          )}
        </div>

        {/* Prime Value Slider */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <span className="text-purple-400">Prime Value (squared)</span>
              <button
                onClick={() => setShowExplanation(showExplanation === 'prime' ? null : 'prime')}
                className="text-muted-foreground hover:text-purple-400 transition-colors"
              >
                <Info className="h-4 w-4" />
              </button>
            </label>
            <span className="font-mono text-purple-400">{primeValue}² = {primeValue * primeValue}</span>
          </div>
          <input
            type="range"
            min="2"
            max="100"
            value={primeValue}
            onChange={(e) => setPrimeValue(Number(e.target.value))}
            className="w-full h-2 bg-purple-950 rounded-lg appearance-none cursor-pointer accent-purple-400"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>2</span>
            <span className={primeValue === 47 ? 'text-purple-400 font-bold' : ''}>47 (correct)</span>
            <span>100</span>
          </div>
          {showExplanation === 'prime' && (
            <motion.p
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="text-xs text-muted-foreground mt-2 p-2 bg-black/20 rounded"
            >
              {explanations.prime}
            </motion.p>
          )}
        </div>

        {/* Alpha Slider */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <span className="text-green-400">Alpha Constant (α)</span>
              <button
                onClick={() => setShowExplanation(showExplanation === 'alpha' ? null : 'alpha')}
                className="text-muted-foreground hover:text-green-400 transition-colors"
              >
                <Info className="h-4 w-4" />
              </button>
            </label>
            <span className="font-mono text-green-400">{alphaValue}</span>
          </div>
          <input
            type="range"
            min="1"
            max="200"
            value={alphaValue}
            onChange={(e) => setAlphaValue(Number(e.target.value))}
            className="w-full h-2 bg-green-950 rounded-lg appearance-none cursor-pointer accent-green-400"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>1</span>
            <span className={alphaValue === 137 ? 'text-green-400 font-bold' : ''}>137 (correct)</span>
            <span>200</span>
          </div>
          {showExplanation === 'alpha' && (
            <motion.p
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="text-xs text-muted-foreground mt-2 p-2 bg-black/20 rounded"
            >
              {explanations.alpha}
            </motion.p>
          )}
        </div>
      </div>

      {/* Calculation Steps */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-muted-foreground mb-3">Calculation Steps:</h4>
        {calculations.steps.map((step, index) => (
          <motion.div
            key={step.label}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center justify-between p-3 bg-black/20 rounded-lg"
          >
            <div>
              <div className="text-sm font-medium">{step.label}</div>
              <div className="text-xs text-muted-foreground font-mono">{step.formula}</div>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-lg">{step.result}</span>
              {step.isCorrect !== undefined && (
                step.isCorrect ? (
                  <Check className="h-5 w-5 text-green-400" />
                ) : (
                  <X className="h-5 w-5 text-red-400" />
                )
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Result Explanation */}
      {calculations.row === 21 && calculations.col === 4 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-green-950/30 border border-green-900/50 rounded-lg"
        >
          <div className="flex items-start gap-3">
            <Check className="h-5 w-5 text-green-400 mt-0.5" />
            <div>
              <div className="font-medium text-green-400">Row 21, Column 4 - Bitcoin Input Layer</div>
              <p className="text-sm text-muted-foreground mt-1">
                {explanations.row21}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Reset Button */}
      <div className="mt-6 text-center">
        <button
          onClick={() => {
            setBlockHeight(CORRECT_BLOCK)
            setPrimeValue(CORRECT_PRIME)
            setAlphaValue(CORRECT_ALPHA)
          }}
          className="px-4 py-2 text-sm bg-blue-500/20 hover:bg-blue-500/30 rounded-lg transition-colors text-blue-400"
        >
          Reset to Correct Values
        </button>
      </div>
    </div>
  )
}
