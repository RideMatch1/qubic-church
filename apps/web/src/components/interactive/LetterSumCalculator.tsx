'use client'

import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Hash, Play, RotateCcw, ChevronDown, Sparkles } from 'lucide-react'

// Pre-loaded addresses
const PRESET_ADDRESSES = {
  ARB: {
    address: 'AFZPUAIYVPNUYGJRQVLUKOPPVLHAZQTGLYAAUUNBXFTVTAMSBKQBLEIEPCVJ',
    name: 'ARB Oracle',
    expectedSum: 817,
    factorization: '19 × 43',
    significance: 'ARB sum factorizes to Genesis Block constants: 19 (range start) × 43 (zero bits)',
  },
  POCZ: {
    address: 'POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD',
    name: 'POCZ Seed Holder',
    expectedSum: 672,
    factorization: '2⁵ × 21',
    significance: 'POCZ is the private key holder at Row 96, Column 84 (address 12,372)',
  },
}

// Calculate letter value (A=1, B=2, ... Z=26)
function getLetterValue(letter: string): number {
  const upper = letter.toUpperCase()
  if (upper >= 'A' && upper <= 'Z') {
    return upper.charCodeAt(0) - 64
  }
  return 0
}

interface LetterData {
  letter: string
  value: number
  runningSum: number
  index: number
}

export function LetterSumCalculator() {
  const [address, setAddress] = useState(PRESET_ADDRESSES.ARB.address)
  const [isAnimating, setIsAnimating] = useState(false)
  const [animationIndex, setAnimationIndex] = useState(-1)
  const [selectedPreset, setSelectedPreset] = useState<'ARB' | 'POCZ' | 'custom'>('ARB')
  const [showDropdown, setShowDropdown] = useState(false)

  const letterData = useMemo((): LetterData[] => {
    let runningSum = 0
    return address.split('').map((letter, index) => {
      const value = getLetterValue(letter)
      runningSum += value
      return { letter, value, runningSum, index }
    })
  }, [address])

  const totalSum = letterData.length > 0 ? (letterData[letterData.length - 1]?.runningSum ?? 0) : 0

  // Calculate AFZJ marker (first 3 letters + position 10 which is J in ARB)
  const afzjSum = useMemo(() => {
    if (address.length >= 10) {
      const chars = address.split('')
      const a = getLetterValue(chars[0] ?? '')
      const f = getLetterValue(chars[1] ?? '')
      const z = getLetterValue(chars[2] ?? '')
      const j = getLetterValue(chars[9] ?? '') // 10th character (index 9)
      return { a, f, z, j, sum: a + f + z + j }
    }
    return null
  }, [address])

  // Prime factorization helper
  const factorize = (n: number): string => {
    if (n === 817) return '19 × 43'
    if (n === 672) return '2⁵ × 21 = 32 × 21'
    const factors: number[] = []
    let remaining = n
    for (let i = 2; i <= Math.sqrt(remaining); i++) {
      while (remaining % i === 0) {
        factors.push(i)
        remaining /= i
      }
    }
    if (remaining > 1) factors.push(remaining)
    return factors.join(' × ') || n.toString()
  }

  const startAnimation = async () => {
    setIsAnimating(true)
    setAnimationIndex(-1)

    for (let i = 0; i < letterData.length; i++) {
      setAnimationIndex(i)
      await new Promise(resolve => setTimeout(resolve, 50))
    }

    setIsAnimating(false)
  }

  const resetAnimation = () => {
    setIsAnimating(false)
    setAnimationIndex(-1)
  }

  const selectPreset = (preset: 'ARB' | 'POCZ') => {
    setAddress(PRESET_ADDRESSES[preset].address)
    setSelectedPreset(preset)
    setShowDropdown(false)
    resetAnimation()
  }

  const currentPreset = selectedPreset !== 'custom' ? PRESET_ADDRESSES[selectedPreset] : null

  return (
    <div className="p-6 rounded-xl bg-gradient-to-b from-purple-950/30 to-purple-950/10 border border-purple-900/50">
      <div className="flex items-center gap-3 mb-6">
        <Hash className="h-6 w-6 text-purple-400" />
        <h3 className="text-xl font-semibold">Letter Sum Calculator</h3>
      </div>

      {/* Preset Selector */}
      <div className="mb-6">
        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="w-full flex items-center justify-between p-3 bg-black/30 rounded-lg border border-purple-900/50 hover:border-purple-700/50 transition-colors"
          >
            <span className="text-sm">
              {currentPreset ? currentPreset.name : 'Custom Address'}
            </span>
            <ChevronDown className={`h-4 w-4 transition-transform ${showDropdown ? 'rotate-180' : ''}`} />
          </button>

          <AnimatePresence>
            {showDropdown && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute top-full left-0 right-0 mt-1 bg-black/90 border border-purple-900/50 rounded-lg overflow-hidden z-10"
              >
                <button
                  onClick={() => selectPreset('ARB')}
                  className="w-full p-3 text-left hover:bg-purple-900/30 transition-colors"
                >
                  <div className="font-medium">ARB Oracle</div>
                  <div className="text-xs text-muted-foreground">Sum: 817 = 19 × 43</div>
                </button>
                <button
                  onClick={() => selectPreset('POCZ')}
                  className="w-full p-3 text-left hover:bg-purple-900/30 transition-colors border-t border-purple-900/30"
                >
                  <div className="font-medium">POCZ Seed Holder</div>
                  <div className="text-xs text-muted-foreground">Sum: 672</div>
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Address Input */}
      <div className="mb-6">
        <label className="text-sm text-muted-foreground mb-2 block">
          60-character Qubic Address:
        </label>
        <input
          type="text"
          value={address}
          onChange={(e) => {
            setAddress(e.target.value.toUpperCase())
            setSelectedPreset('custom')
            resetAnimation()
          }}
          maxLength={60}
          className="w-full p-3 bg-black/30 border border-purple-900/50 rounded-lg font-mono text-xs focus:outline-none focus:border-purple-500 transition-colors"
          placeholder="Enter Qubic address..."
        />
        <div className="text-xs text-muted-foreground mt-1 text-right">
          {address.length}/60 characters
        </div>
      </div>

      {/* Letter Grid with Values */}
      <div className="mb-6 p-4 bg-black/30 rounded-lg overflow-x-auto">
        <div className="flex flex-wrap gap-1 justify-center min-w-max">
          {letterData.map((data, idx) => (
            <motion.div
              key={idx}
              initial={false}
              animate={{
                scale: animationIndex === idx ? 1.2 : 1,
                backgroundColor: animationIndex >= idx && isAnimating
                  ? 'rgba(168, 85, 247, 0.3)'
                  : 'rgba(0, 0, 0, 0.3)',
              }}
              className="flex flex-col items-center p-1 rounded text-xs"
              style={{ minWidth: '24px' }}
            >
              <span className="font-mono font-bold text-purple-400">{data.letter}</span>
              <span className="text-muted-foreground text-[10px]">{data.value}</span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Controls */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={startAnimation}
          disabled={isAnimating}
          className="flex-1 flex items-center justify-center gap-2 p-3 bg-purple-500/20 hover:bg-purple-500/30 disabled:opacity-50 rounded-lg transition-colors text-purple-400"
        >
          <Play className="h-4 w-4" />
          Animate Sum
        </button>
        <button
          onClick={resetAnimation}
          className="flex items-center justify-center gap-2 p-3 bg-black/30 hover:bg-black/40 rounded-lg transition-colors"
        >
          <RotateCcw className="h-4 w-4" />
        </button>
      </div>

      {/* Results */}
      <div className="space-y-4">
        {/* Total Sum */}
        <div className="p-4 bg-black/30 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">Total Letter Sum:</span>
            <motion.span
              key={animationIndex}
              initial={{ scale: 1 }}
              animate={{ scale: isAnimating ? [1, 1.1, 1] : 1 }}
              className="text-3xl font-mono font-bold text-purple-400"
            >
              {isAnimating && animationIndex >= 0
                ? letterData[animationIndex]?.runningSum || 0
                : totalSum}
            </motion.span>
          </div>
          <div className="text-sm text-muted-foreground">
            Prime Factorization: <span className="text-purple-400 font-mono">{factorize(totalSum)}</span>
          </div>
        </div>

        {/* AFZJ Marker (only for ARB) */}
        {selectedPreset === 'ARB' && afzjSum && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 bg-gradient-to-r from-orange-950/30 to-purple-950/30 rounded-lg border border-orange-900/30"
          >
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="h-4 w-4 text-orange-400" />
              <span className="text-sm font-medium">AFZJ Marker Discovery</span>
            </div>
            <div className="font-mono text-sm space-y-1">
              <div>
                <span className="text-orange-400">A</span>({afzjSum.a}) +
                <span className="text-orange-400"> F</span>({afzjSum.f}) +
                <span className="text-orange-400"> Z</span>({afzjSum.z}) +
                <span className="text-orange-400"> J</span>({afzjSum.j}) =
                <span className="text-green-400 font-bold"> {afzjSum.sum}</span>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              43 = Bitcoin Genesis Block leading zero bits (only 32 required, 11 extra!)
            </p>
          </motion.div>
        )}

        {/* Significance */}
        {currentPreset && (
          <div className="p-4 bg-black/20 rounded-lg border border-purple-900/30">
            <p className="text-sm text-muted-foreground">
              <span className="text-purple-400 font-medium">Significance: </span>
              {currentPreset.significance}
            </p>
          </div>
        )}
      </div>

      {/* Letter Values Reference */}
      <details className="mt-6">
        <summary className="text-sm text-muted-foreground cursor-pointer hover:text-purple-400 transition-colors">
          Show letter values (A=1, B=2, ... Z=26)
        </summary>
        <div className="mt-3 p-3 bg-black/20 rounded-lg">
          <div className="grid grid-cols-13 gap-1 text-xs font-mono text-center">
            {'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').map((letter, i) => (
              <div key={letter} className="p-1">
                <div className="text-purple-400">{letter}</div>
                <div className="text-muted-foreground">{i + 1}</div>
              </div>
            ))}
          </div>
        </div>
      </details>
    </div>
  )
}
