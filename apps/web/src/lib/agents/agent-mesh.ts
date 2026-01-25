/**
 * AGENT MESH
 *
 * Coordinates multiple TernaryAgents on the Anna Matrix.
 * Handles spawning, communication, and pipeline processing.
 */

import { TernaryAgent } from './ternary-agent'
import type {
  AgentType,
  AgentConfig,
  AgentResult,
  AgentMessage,
  PipelineResult,
  MeshState,
  AgentSnapshot,
  Connection,
} from './types'

const MAX_MESSAGES = 100

/**
 * AgentMesh - Orchestrates ternary agents
 */
export class AgentMesh {
  private matrix: number[][]
  private agents = new Map<string, TernaryAgent>()
  private messages: AgentMessage[] = []
  private config: Partial<AgentConfig>
  private idCounter = 0

  constructor(matrix: number[][], config: Partial<AgentConfig> = {}) {
    this.matrix = matrix
    this.config = config
  }

  /**
   * Spawn a new agent
   */
  spawn(type: AgentType, id?: string): TernaryAgent {
    const agentId = id ?? `${type}-${++this.idCounter}`
    const agent = new TernaryAgent(agentId, type, this.matrix, this.config)
    this.agents.set(agentId, agent)
    return agent
  }

  /**
   * Get agent by ID
   */
  get(id: string): TernaryAgent | undefined {
    return this.agents.get(id)
  }

  /**
   * Get all agents
   */
  getAll(): TernaryAgent[] {
    return Array.from(this.agents.values())
  }

  /**
   * Get agents by type
   */
  getByType(type: AgentType): TernaryAgent[] {
    return this.getAll().filter(a => a.type === type)
  }

  /**
   * Remove an agent
   */
  remove(id: string): boolean {
    return this.agents.delete(id)
  }

  /**
   * Clear all agents
   */
  clear(): void {
    this.agents.clear()
  }

  /**
   * Send signal between agents
   */
  sendSignal(fromId: string, toId: string): void {
    const from = this.agents.get(fromId)
    const to = this.agents.get(toId)

    if (!from || !to) {
      throw new Error(`Agent not found: ${!from ? fromId : toId}`)
    }

    from.sendSignalTo(to)
    this.logMessage(fromId, toId, from.getEnergy())
  }

  /**
   * Process input with a single agent
   */
  processWithAgent(type: AgentType, input: string): AgentResult {
    const agent = this.spawn(type)
    agent.setInputFromText(input)
    return agent.process()
  }

  /**
   * Process through full pipeline: Researcher -> Coder -> Coordinator
   */
  processPipeline(input: string): PipelineResult {
    const start = performance.now()

    // Clear previous agents
    this.clear()

    // Stage 1: Researcher
    const researcher = this.spawn('researcher')
    researcher.setInputFromText(input)
    const r1 = researcher.process()

    // Stage 2: Coder receives researcher output
    const coder = this.spawn('coder')
    researcher.sendSignalTo(coder)
    this.logMessage(researcher.id, coder.id, researcher.getEnergy())
    const r2 = coder.process()

    // Stage 3: Coordinator combines both
    const coordinator = this.spawn('coordinator')
    coordinator.receiveSignalsFrom([researcher, coder])
    this.logMessage(researcher.id, coordinator.id, researcher.getEnergy())
    this.logMessage(coder.id, coordinator.id, coder.getEnergy())
    const r3 = coordinator.process()

    const stages = [r1, r2, r3]

    return {
      stages,
      totalTicks: stages.reduce((s, r) => s + r.ticks, 0),
      totalEnergy: stages.reduce((s, r) => s + r.energy, 0),
      totalDurationMs: Math.round((performance.now() - start) * 100) / 100,
      finalDecision: r3.decision,
    }
  }

  /**
   * Stream pipeline with callbacks
   */
  streamPipeline(
    input: string,
    onStageStart: (stage: number, agent: TernaryAgent) => void,
    onTick: (stage: number, tick: number, energy: number) => void,
    onStageComplete: (stage: number, result: AgentResult) => void,
    onComplete: (result: PipelineResult) => void
  ): () => void {
    const start = performance.now()
    const stages: AgentResult[] = []
    let cancelled = false
    let cancelFn: (() => void) | null = null

    // Clear previous agents
    this.clear()

    const agents: TernaryAgent[] = []

    const runStage = (stageNum: number): Promise<void> => {
      if (cancelled) return Promise.resolve()

      return new Promise(resolve => {
        let agent: TernaryAgent

        switch (stageNum) {
          case 0:
            agent = this.spawn('researcher')
            agent.setInputFromText(input)
            break
          case 1:
            agent = this.spawn('coder')
            if (agents[0]) {
              agents[0].sendSignalTo(agent)
              this.logMessage(agents[0].id, agent.id, agents[0].getEnergy())
            }
            break
          case 2:
            agent = this.spawn('coordinator')
            agent.receiveSignalsFrom(agents.filter(Boolean))
            for (const a of agents) {
              this.logMessage(a.id, agent.id, a.getEnergy())
            }
            break
          default:
            resolve()
            return
        }

        agents[stageNum] = agent
        onStageStart(stageNum, agent)

        cancelFn = agent.streamProcess(
          (tick, energy) => {
            if (!cancelled) onTick(stageNum, tick, energy)
          },
          result => {
            stages.push(result)
            onStageComplete(stageNum, result)
            resolve()
          }
        )
      })
    }

    // Run stages sequentially
    ;(async () => {
      await runStage(0)
      await runStage(1)
      await runStage(2)

      if (!cancelled) {
        const lastStage = stages[stages.length - 1]
        onComplete({
          stages,
          totalTicks: stages.reduce((s, r) => s + r.ticks, 0),
          totalEnergy: stages.reduce((s, r) => s + r.energy, 0),
          totalDurationMs: Math.round((performance.now() - start) * 100) / 100,
          finalDecision: lastStage?.decision ?? 'uncertain',
        })
      }
    })()

    // Return cancel function
    return () => {
      cancelled = true
      cancelFn?.()
    }
  }

  /**
   * Get mesh state for visualization
   */
  getState(): MeshState {
    const agents = this.getAll()
    const now = Date.now()

    const snapshots: AgentSnapshot[] = agents.map(a => ({
      id: a.id,
      type: a.type,
      energy: a.getEnergy(),
      state: a.getEnergy() > 0 ? 1 : a.getEnergy() < 0 ? -1 : 0,
      ticks: a.getTicks(),
    }))

    // Build connections from recent messages
    const connMap = new Map<string, { strength: number; active: boolean }>()

    for (const msg of this.messages) {
      const key = `${msg.from}:${msg.to}`
      const existing = connMap.get(key)
      const isRecent = now - msg.timestamp < 5000

      connMap.set(key, {
        strength: Math.min((existing?.strength ?? 0) + 0.3, 1),
        active: isRecent,
      })
    }

    const connections: Connection[] = Array.from(connMap.entries()).map(
      ([key, data]) => {
        const [from = '', to = ''] = key.split(':')
        return { from, to, ...data }
      }
    )

    return {
      agents: snapshots,
      connections,
      totalEnergy: agents.reduce((s, a) => s + a.getEnergy(), 0),
    }
  }

  /**
   * Reset mesh
   */
  reset(): void {
    this.agents.clear()
    this.messages = []
  }

  private logMessage(from: string, to: string, energy: number): void {
    this.messages.push({
      from,
      to,
      timestamp: Date.now(),
      signalEnergy: energy,
    })

    // Keep only recent messages
    if (this.messages.length > MAX_MESSAGES) {
      this.messages = this.messages.slice(-MAX_MESSAGES)
    }
  }
}
