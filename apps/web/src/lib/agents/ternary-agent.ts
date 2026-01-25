/**
 * TERNARY AGENT
 *
 * Neural network agent operating on the Anna Matrix.
 * Pure ternary computation - no external API calls.
 */

import type { TernaryState, InferenceResult } from '../aigarth/types'
import { runTickLoop, streamTickLoop } from '../aigarth/tick-loop'
import { ternaryClamp, computeEnergy, textToTernary } from '../aigarth/ternary'
import type { AgentType, AgentConfig, AgentResult, MatrixRegion } from './types'
import {
  DEFAULT_AGENT_CONFIG,
  AGENT_REGIONS,
  DECISION_THRESHOLDS,
} from './types'

/**
 * TernaryAgent - Neural network agent on the Anna Matrix
 */
export class TernaryAgent {
  readonly id: string
  readonly type: AgentType
  readonly region: MatrixRegion

  private matrix: number[][]
  private config: AgentConfig
  private states: TernaryState[]
  private result: InferenceResult | null = null
  private tickCount = 0

  constructor(
    id: string,
    type: AgentType,
    matrix: number[][],
    config: Partial<AgentConfig> = {}
  ) {
    this.id = id
    this.type = type
    this.matrix = matrix
    this.region = AGENT_REGIONS[type]
    this.config = { ...DEFAULT_AGENT_CONFIG, ...config }

    const population = this.config.numInputs + this.config.numOutputs
    this.states = new Array(population).fill(0) as TernaryState[]
  }

  /**
   * Set input from text (uses existing ternary encoding)
   */
  setInputFromText(text: string): void {
    const ternary = textToTernary(text, Math.ceil(this.config.numInputs / 8))
    this.setInput(ternary.slice(0, this.config.numInputs) as TernaryState[])
  }

  /**
   * Set input from ternary array
   */
  setInput(input: TernaryState[]): void {
    const len = Math.min(input.length, this.config.numInputs)
    for (let i = 0; i < len; i++) {
      const val = input[i]
      if (val !== undefined) this.states[i] = val
    }
  }

  /**
   * Process through neural network (synchronous)
   */
  process(): AgentResult {
    const start = performance.now()
    const agentMatrix = this.getAgentMatrix()

    this.result = runTickLoop(this.states, agentMatrix, this.config, false)
    this.states = [...this.result.allStates]
    this.tickCount = this.result.ticks

    return this.buildResult(performance.now() - start)
  }

  /**
   * Stream processing with tick callbacks
   */
  streamProcess(
    onTick: (tick: number, energy: number) => void,
    onComplete: (result: AgentResult) => void
  ): () => void {
    const start = performance.now()
    const agentMatrix = this.getAgentMatrix()

    return streamTickLoop(
      this.states,
      agentMatrix,
      this.config,
      (tick, _states, energy) => {
        this.tickCount = tick
        onTick(tick, energy)
      },
      result => {
        this.result = result
        this.states = [...result.allStates]
        onComplete(this.buildResult(performance.now() - start))
      }
    )
  }

  /**
   * Get output vector
   */
  getOutput(): TernaryState[] {
    return this.result?.outputs ?? []
  }

  /**
   * Get current energy
   */
  getEnergy(): number {
    return this.result?.energy ?? computeEnergy(this.states)
  }

  /**
   * Get tick count
   */
  getTicks(): number {
    return this.tickCount
  }

  /**
   * Get decision based on energy
   */
  getDecision(): 'yes' | 'no' | 'uncertain' {
    const energy = this.getEnergy()
    if (energy > DECISION_THRESHOLDS.positive) return 'yes'
    if (energy < DECISION_THRESHOLDS.negative) return 'no'
    return 'uncertain'
  }

  /**
   * Send signal to another agent
   */
  sendSignalTo(target: TernaryAgent): void {
    target.setInput(this.getOutput())
  }

  /**
   * Receive and combine signals from multiple agents
   */
  receiveSignalsFrom(sources: TernaryAgent[]): void {
    const combined = new Array(this.config.numInputs).fill(0)

    for (const source of sources) {
      const output = source.getOutput()
      for (let i = 0; i < Math.min(output.length, combined.length); i++) {
        combined[i] += output[i] ?? 0
      }
    }

    this.setInput(combined.map(v => ternaryClamp(v)) as TernaryState[])
  }

  /**
   * Reset agent state
   */
  reset(): void {
    const population = this.config.numInputs + this.config.numOutputs
    this.states = new Array(population).fill(0) as TernaryState[]
    this.result = null
    this.tickCount = 0
  }

  private getAgentMatrix(): number[][] {
    return this.matrix.slice(this.region.startRow, this.region.endRow)
  }

  private buildResult(durationMs: number): AgentResult {
    return {
      agentId: this.id,
      agentType: this.type,
      ticks: this.result?.ticks ?? 0,
      energy: this.result?.energy ?? 0,
      endReason: this.result?.endReason ?? 'max_ticks',
      distribution: this.result?.distribution ?? {
        positive: 0,
        neutral: 0,
        negative: 0,
      },
      outputs: this.result?.outputs ?? [],
      decision: this.getDecision(),
      durationMs: Math.round(durationMs * 100) / 100,
    }
  }
}
