/**
 * TERNARY AGENT TYPES
 *
 * Type definitions for the ternary-based agent system.
 * Agents operate directly on the Anna Matrix.
 */

import type {
  TernaryState,
  StateDistribution,
  EndReason,
} from '../aigarth/types'

// Re-export for convenience
export type { TernaryState, StateDistribution, EndReason }

/** Agent specialization types */
export type AgentType = 'researcher' | 'coder' | 'coordinator'

/** Agent ternary state */
export type AgentState = TernaryState

/** Matrix region owned by an agent */
export interface MatrixRegion {
  startRow: number
  endRow: number
}

/** Agent region assignments (each = 16 rows x 128 cols = 2048 neurons) */
export const AGENT_REGIONS: Record<AgentType, MatrixRegion> = {
  researcher: { startRow: 32, endRow: 48 },
  coder: { startRow: 48, endRow: 64 },
  coordinator: { startRow: 64, endRow: 80 },
}

/** Agent processing configuration */
export interface AgentConfig {
  numInputs: number
  numOutputs: number
  numNeighbors: number
  maxTicks: number
}

/** Default configuration */
export const DEFAULT_AGENT_CONFIG: AgentConfig = {
  numInputs: 64,
  numOutputs: 64,
  numNeighbors: 8,
  maxTicks: 100,
}

/** Decision thresholds */
export const DECISION_THRESHOLDS = {
  positive: 10,
  negative: -10,
} as const

/** Agent processing result */
export interface AgentResult {
  agentId: string
  agentType: AgentType
  ticks: number
  energy: number
  endReason: EndReason
  distribution: StateDistribution
  outputs: TernaryState[]
  decision: 'yes' | 'no' | 'uncertain'
  durationMs: number
}

/** Inter-agent message */
export interface AgentMessage {
  from: string
  to: string
  timestamp: number
  signalEnergy: number
}

/** Pipeline result */
export interface PipelineResult {
  stages: AgentResult[]
  totalTicks: number
  totalEnergy: number
  totalDurationMs: number
  finalDecision: 'yes' | 'no' | 'uncertain'
}

/** Mesh state for visualization */
export interface MeshState {
  agents: AgentSnapshot[]
  connections: Connection[]
  totalEnergy: number
}

export interface AgentSnapshot {
  id: string
  type: AgentType
  energy: number
  state: AgentState
  ticks: number
}

export interface Connection {
  from: string
  to: string
  strength: number
  active: boolean
}
