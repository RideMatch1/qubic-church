/**
 * RESONANCE CORE - Echte Ternary Matrix Berechnung
 *
 * Kein Fake. Keine Marketing-Patterns.
 * Echter Tick-Loop durch die Anna Matrix.
 */

import { runTickLoop, type TickLoopConfig } from '../aigarth/tick-loop'
import type { TernaryState, InferenceResult } from '../aigarth/types'
import { createHash } from 'crypto'

// Default config für Resonance-Berechnung
const RESONANCE_CONFIG: TickLoopConfig = {
  numInputs: 64,
  numOutputs: 64,
  numNeighbors: 8,
  maxTicks: 500,
}

/**
 * Konvertiert beliebigen Input zu Ternary-States
 *
 * Methode: SHA256 → Bits → Ternary (-1 für 0-bit, +1 für 1-bit)
 */
export function inputToTernary(input: string | Buffer): TernaryState[] {
  const hash = createHash('sha256')
    .update(typeof input === 'string' ? input : input)
    .digest()

  const ternary: TernaryState[] = []

  // 256 bits = 32 bytes, wir brauchen 64 inputs
  for (let i = 0; i < 64; i++) {
    const byteIdx = Math.floor(i / 8)
    const bitIdx = i % 8
    const bit = (hash[byteIdx]! >> (7 - bitIdx)) & 1
    ternary.push(bit === 0 ? -1 : 1)
  }

  return ternary
}

/**
 * Konvertiert Bitcoin Address zu Ternary
 * Nutzt Base58-Decoding für authentischere Repräsentation
 */
export function bitcoinAddressToTernary(address: string): TernaryState[] {
  // Base58 alphabet
  const BASE58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

  // Decode Base58 to bytes
  let num = 0n
  for (const char of address) {
    const idx = BASE58.indexOf(char)
    if (idx === -1) continue
    num = num * 58n + BigInt(idx)
  }

  // Convert to bytes
  const bytes: number[] = []
  while (num > 0n) {
    bytes.unshift(Number(num & 0xFFn))
    num = num >> 8n
  }

  // Pad to 25 bytes (standard Bitcoin address)
  while (bytes.length < 25) {
    bytes.unshift(0)
  }

  // Convert bytes to ternary (64 values from 25 bytes)
  const ternary: TernaryState[] = []
  for (let i = 0; i < 64; i++) {
    const byteIdx = Math.floor(i / 3) % bytes.length
    const byte = bytes[byteIdx] ?? 0

    // Use different bit extractions for variety
    const mod = i % 3
    let value: number
    if (mod === 0) value = (byte >> 5) & 0x07
    else if (mod === 1) value = (byte >> 2) & 0x07
    else value = ((byte & 0x03) << 1) | ((bytes[(byteIdx + 1) % bytes.length] ?? 0) >> 7)

    // Map 0-7 to ternary
    ternary.push(value < 3 ? -1 : value > 4 ? 1 : 0)
  }

  return ternary
}

/**
 * Konvertiert Hex-String (Private Key, Seed) zu Ternary
 */
export function hexToTernary(hex: string): TernaryState[] {
  const clean = hex.replace(/^0x/i, '').replace(/[^0-9a-fA-F]/g, '')
  const ternary: TernaryState[] = []

  for (let i = 0; i < 64; i++) {
    const hexIdx = (i * 2) % clean.length
    const byte = parseInt(clean.slice(hexIdx, hexIdx + 2) || '00', 16)

    // Map byte to ternary based on value ranges
    if (byte < 85) ternary.push(-1)
    else if (byte > 170) ternary.push(1)
    else ternary.push(0)
  }

  return ternary
}

/**
 * Resonance Result - Was die Matrix über den Input "denkt"
 */
export interface ResonanceResult {
  // Input Info
  input: string
  inputType: 'text' | 'address' | 'hex' | 'raw'
  ternaryInput: TernaryState[]

  // Tick-Loop Results
  ticks: number
  endReason: 'converged' | 'all_nonzero' | 'max_ticks'

  // Energy Analysis
  energy: number
  normalizedEnergy: number // -1 to +1

  // State Distribution
  distribution: {
    positive: number
    negative: number
    zero: number
  }

  // Output Pattern
  outputPattern: TernaryState[]
  outputHash: string // Deterministischer Hash des Outputs

  // Interpretation
  resonance: 'strong_positive' | 'positive' | 'neutral' | 'negative' | 'strong_negative'
  convergenceQuality: 'fast' | 'normal' | 'slow' | 'timeout'

  // Raw data für weitere Analyse
  allStates: TernaryState[]
}

/**
 * Berechnet Resonance eines Inputs durch die Anna Matrix
 */
export function computeResonance(
  input: string,
  matrix: number[][],
  inputType: 'text' | 'address' | 'hex' | 'auto' = 'auto'
): ResonanceResult {
  // Auto-detect input type
  let detectedType: 'text' | 'address' | 'hex' = 'text'
  let ternaryInput: TernaryState[]

  if (inputType === 'auto') {
    if (/^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$/.test(input)) {
      detectedType = 'address'
    } else if (/^(0x)?[0-9a-fA-F]{32,}$/.test(input)) {
      detectedType = 'hex'
    } else {
      detectedType = 'text'
    }
  } else {
    detectedType = inputType === 'auto' ? 'text' : inputType
  }

  // Convert to ternary based on type
  switch (detectedType) {
    case 'address':
      ternaryInput = bitcoinAddressToTernary(input)
      break
    case 'hex':
      ternaryInput = hexToTernary(input)
      break
    default:
      ternaryInput = inputToTernary(input)
  }

  // Run tick-loop
  const result = runTickLoop(ternaryInput, matrix, RESONANCE_CONFIG, false)

  // Compute normalized energy (-1 to +1)
  const maxPossibleEnergy = RESONANCE_CONFIG.numInputs + RESONANCE_CONFIG.numOutputs
  const normalizedEnergy = result.energy / maxPossibleEnergy

  // Compute output hash for determinism verification
  const outputHash = createHash('sha256')
    .update(result.outputs.join(','))
    .digest('hex')
    .slice(0, 16)

  // Interpret resonance
  let resonance: ResonanceResult['resonance']
  if (normalizedEnergy > 0.5) resonance = 'strong_positive'
  else if (normalizedEnergy > 0.15) resonance = 'positive'
  else if (normalizedEnergy < -0.5) resonance = 'strong_negative'
  else if (normalizedEnergy < -0.15) resonance = 'negative'
  else resonance = 'neutral'

  // Interpret convergence
  let convergenceQuality: ResonanceResult['convergenceQuality']
  if (result.endReason === 'max_ticks') convergenceQuality = 'timeout'
  else if (result.ticks < 20) convergenceQuality = 'fast'
  else if (result.ticks < 100) convergenceQuality = 'normal'
  else convergenceQuality = 'slow'

  return {
    input,
    inputType: detectedType,
    ternaryInput,
    ticks: result.ticks,
    endReason: result.endReason,
    energy: result.energy,
    normalizedEnergy,
    distribution: result.distribution,
    outputPattern: result.outputs,
    outputHash,
    resonance,
    convergenceQuality,
    allStates: result.allStates,
  }
}

/**
 * Vergleicht zwei Inputs durch Matrix-Resonance
 */
export interface ComparisonResult {
  inputA: ResonanceResult
  inputB: ResonanceResult

  // Similarity Metrics
  outputSimilarity: number // 0-1, wie ähnlich die Output-Patterns sind
  energyDifference: number
  convergenceSimilarity: boolean

  // Pattern Match
  matchingOutputs: number
  totalOutputs: number

  // Interpretation
  verdict: 'very_similar' | 'similar' | 'different' | 'opposite'
}

export function compareInputs(
  inputA: string,
  inputB: string,
  matrix: number[][]
): ComparisonResult {
  const resA = computeResonance(inputA, matrix)
  const resB = computeResonance(inputB, matrix)

  // Count matching outputs
  let matching = 0
  for (let i = 0; i < resA.outputPattern.length; i++) {
    if (resA.outputPattern[i] === resB.outputPattern[i]) matching++
  }

  const outputSimilarity = matching / resA.outputPattern.length
  const energyDifference = Math.abs(resA.normalizedEnergy - resB.normalizedEnergy)
  const convergenceSimilarity = resA.endReason === resB.endReason

  // Interpret
  let verdict: ComparisonResult['verdict']
  if (outputSimilarity > 0.9 && energyDifference < 0.1) verdict = 'very_similar'
  else if (outputSimilarity > 0.7) verdict = 'similar'
  else if (outputSimilarity < 0.3) verdict = 'opposite'
  else verdict = 'different'

  return {
    inputA: resA,
    inputB: resB,
    outputSimilarity,
    energyDifference,
    convergenceSimilarity,
    matchingOutputs: matching,
    totalOutputs: resA.outputPattern.length,
    verdict,
  }
}

/**
 * Batch-Resonance für viele Inputs (z.B. Liste von Adressen)
 */
export function batchResonance(
  inputs: string[],
  matrix: number[][]
): {
  results: ResonanceResult[]
  statistics: {
    avgEnergy: number
    avgTicks: number
    strongPositive: number
    positive: number
    neutral: number
    negative: number
    strongNegative: number
    fastConvergence: number
  }
  ranked: Array<{ input: string; energy: number; rank: number }>
} {
  const results = inputs.map(input => computeResonance(input, matrix))

  // Compute statistics
  const statistics = {
    avgEnergy: results.reduce((s, r) => s + r.normalizedEnergy, 0) / results.length,
    avgTicks: results.reduce((s, r) => s + r.ticks, 0) / results.length,
    strongPositive: results.filter(r => r.resonance === 'strong_positive').length,
    positive: results.filter(r => r.resonance === 'positive').length,
    neutral: results.filter(r => r.resonance === 'neutral').length,
    negative: results.filter(r => r.resonance === 'negative').length,
    strongNegative: results.filter(r => r.resonance === 'strong_negative').length,
    fastConvergence: results.filter(r => r.convergenceQuality === 'fast').length,
  }

  // Rank by energy
  const ranked = results
    .map((r, i) => ({ input: inputs[i]!, energy: r.normalizedEnergy, rank: 0 }))
    .sort((a, b) => b.energy - a.energy)
    .map((r, i) => ({ ...r, rank: i + 1 }))

  return { results, statistics, ranked }
}

/**
 * Oracle Mode - Ja/Nein/Unsicher basierend auf Resonance
 */
export interface OracleResult {
  question: string
  answer: 'YES' | 'NO' | 'UNCERTAIN'
  confidence: number // 0-1
  reasoning: {
    energy: number
    convergence: string
    pattern: string
  }
  hash: string // Für Reproduzierbarkeit
}

export function askOracle(
  question: string,
  matrix: number[][]
): OracleResult {
  const res = computeResonance(question, matrix, 'text')

  // Determine answer based on energy and convergence
  let answer: 'YES' | 'NO' | 'UNCERTAIN'
  let confidence: number

  if (res.endReason === 'max_ticks') {
    // No convergence = uncertain
    answer = 'UNCERTAIN'
    confidence = 0.3
  } else if (res.normalizedEnergy > 0.2) {
    answer = 'YES'
    confidence = Math.min(0.5 + res.normalizedEnergy * 0.5, 0.95)
  } else if (res.normalizedEnergy < -0.2) {
    answer = 'NO'
    confidence = Math.min(0.5 + Math.abs(res.normalizedEnergy) * 0.5, 0.95)
  } else {
    answer = 'UNCERTAIN'
    confidence = 0.4 + (1 - Math.abs(res.normalizedEnergy)) * 0.2
  }

  // Adjust confidence by convergence speed
  if (res.convergenceQuality === 'fast') confidence = Math.min(confidence + 0.1, 0.95)
  if (res.convergenceQuality === 'slow') confidence = Math.max(confidence - 0.1, 0.1)

  return {
    question,
    answer,
    confidence,
    reasoning: {
      energy: res.normalizedEnergy,
      convergence: `${res.ticks} ticks (${res.endReason})`,
      pattern: `+${res.distribution.positive} / 0:${res.distribution.zero} / -${res.distribution.negative}`,
    },
    hash: res.outputHash,
  }
}
