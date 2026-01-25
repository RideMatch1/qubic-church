/**
 * AIGARTH - LOCAL NEURAL COMPUTER
 *
 * TypeScript implementation of the Aigarth ternary neural network.
 * Uses the REAL tick-loop algorithm from Qubic Core.
 *
 * @example
 * ```ts
 * import { AigarthEngine, textToTernary } from '@/lib/aigarth'
 *
 * const engine = new AigarthEngine()
 * await engine.loadMatrix()
 *
 * const input = textToTernary('Hello World')
 * const result = await engine.process(input)
 *
 * console.log(result.energy, result.ticks)
 * ```
 */

export * from './types'
export * from './ternary'
export * from './tick-loop'
export { AigarthEngine } from './engine'
