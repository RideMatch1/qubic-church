/**
 * HYBRID AGENT SYSTEM
 *
 * Combines:
 * - LLM (Groq/OpenAI) for intelligence
 * - Anna Matrix for deterministic state/patterns
 * - Specialized agents for different tasks
 */

import { getLLMClient, type ChatMessage, type LLMResponse } from './llm-client'
import { MatrixOracle, type OracleResult } from './oracle'

export type TaskType = 'research' | 'code' | 'analysis' | 'simple' | 'blockchain'

export interface AgentContext {
  matrixState?: OracleResult
  previousMessages: ChatMessage[]
  metadata: Record<string, unknown>
}

export interface AgentResponse {
  content: string
  taskType: TaskType
  llmResponse: LLMResponse
  matrixResult?: OracleResult
  sources: string[]
  confidence: number
}

/**
 * Router - classifies queries and routes to appropriate handler
 */
export class QueryRouter {
  private llm = getLLMClient()

  async route(query: string): Promise<TaskType> {
    const result = await this.llm.classify(query, [
      'research',
      'code',
      'analysis',
      'blockchain',
      'simple',
    ])
    return result.choice as TaskType
  }
}

/**
 * Hybrid Agent - combines LLM + Matrix
 */
export class HybridAgent {
  private llm = getLLMClient()
  private oracle: MatrixOracle
  private context: AgentContext
  private systemPrompt: string

  constructor(
    type: TaskType,
    oracle: MatrixOracle
  ) {
    this.oracle = oracle
    this.context = {
      previousMessages: [],
      metadata: { type },
    }
    this.systemPrompt = this.getSystemPrompt(type)
  }

  private getSystemPrompt(type: TaskType): string {
    const prompts: Record<TaskType, string> = {
      research: `You are a research agent specializing in Bitcoin, Qubic, and cryptocurrency analysis.
You have access to the Anna Matrix - a 128x128 data structure containing encoded patterns.
When analyzing queries, consider:
- Historical Bitcoin data and patterns
- CFB (Come-From-Beyond) connections
- Qubic network information
- Patoshi mining patterns
Be precise, cite specific data points, and distinguish between verified facts and speculation.`,

      code: `You are a code review and development agent.
You help with:
- Code analysis and review
- Bug identification
- Architecture suggestions
- Best practices
Be concise and practical. Focus on actionable improvements.`,

      analysis: `You are an analytical agent combining AI reasoning with deterministic matrix computations.
You can query the Anna Matrix for pattern verification.
When the matrix returns a result, treat it as cryptographically verifiable data.
Combine your reasoning with matrix-verified facts for comprehensive analysis.`,

      blockchain: `You are a blockchain specialist agent.
You understand:
- Bitcoin transaction structures
- Qubic's unique tick-based consensus
- Cross-chain patterns and bridges
- Cryptographic signatures and addresses
Provide technical accuracy and reference specific block heights or addresses when relevant.`,

      simple: `You are a helpful assistant. Answer questions directly and concisely.`,
    }
    return prompts[type]
  }

  /**
   * Process a query with optional matrix consultation
   */
  async process(
    query: string,
    useMatrix: boolean = true
  ): Promise<AgentResponse> {
    const sources: string[] = []
    let matrixResult: OracleResult | undefined

    // Step 1: Consult matrix if relevant
    if (useMatrix) {
      try {
        matrixResult = await this.oracle.query(query)
        sources.push('Anna Matrix')
      } catch {
        // Matrix not available, continue without
      }
    }

    // Step 2: Build context-aware prompt
    const messages = this.buildMessages(query, matrixResult)

    // Step 3: Get LLM response
    const llmResponse = await this.llm.chat(messages, 'smart')

    // Step 4: Update context
    this.context.previousMessages.push(
      { role: 'user', content: query },
      { role: 'assistant', content: llmResponse.content }
    )
    this.context.matrixState = matrixResult

    return {
      content: llmResponse.content,
      taskType: this.context.metadata.type as TaskType,
      llmResponse,
      matrixResult,
      sources,
      confidence: this.calculateConfidence(llmResponse, matrixResult),
    }
  }

  private buildMessages(
    query: string,
    matrixResult?: OracleResult
  ): ChatMessage[] {
    const messages: ChatMessage[] = [
      { role: 'system', content: this.systemPrompt },
    ]

    // Add recent context (last 4 exchanges)
    const recentContext = this.context.previousMessages.slice(-8)
    messages.push(...recentContext)

    // Add matrix context if available
    if (matrixResult) {
      const matrixContext = `[MATRIX DATA]
Query Hash: ${matrixResult.queryHash.slice(0, 16)}...
Decision: ${matrixResult.decision.toUpperCase()}
Aggregate: ${matrixResult.aggregateValue}
Energy: ${matrixResult.energy}
Interpretation: ${matrixResult.interpretation}
[END MATRIX DATA]

This is cryptographically verifiable data from the Anna Matrix. Consider it when forming your response.`

      messages.push({
        role: 'system',
        content: matrixContext,
      })
    }

    messages.push({ role: 'user', content: query })

    return messages
  }

  private calculateConfidence(
    llm: LLMResponse,
    matrix?: OracleResult
  ): number {
    let confidence = 0.5 // Base confidence

    // Longer responses often more detailed
    if (llm.content.length > 500) confidence += 0.1

    // Matrix agreement boosts confidence
    if (matrix) {
      if (matrix.decision === 'yes') confidence += 0.2
      if (matrix.decision === 'no') confidence += 0.15
      confidence += matrix.confidence * 0.1
    }

    return Math.min(confidence, 1.0)
  }

  /**
   * Reset context
   */
  reset(): void {
    this.context = {
      previousMessages: [],
      metadata: this.context.metadata,
    }
  }
}

/**
 * Agent Coordinator - manages multiple agents
 */
export class AgentCoordinator {
  private router = new QueryRouter()
  private oracle: MatrixOracle
  private agents = new Map<TaskType, HybridAgent>()

  constructor(oracle: MatrixOracle) {
    this.oracle = oracle
  }

  /**
   * Process query with automatic routing
   */
  async process(query: string): Promise<AgentResponse> {
    // Route to appropriate agent type
    const taskType = await this.router.route(query)

    // Get or create agent
    let agent = this.agents.get(taskType)
    if (!agent) {
      agent = new HybridAgent(taskType, this.oracle)
      this.agents.set(taskType, agent)
    }

    // Process with agent
    return agent.process(query)
  }

  /**
   * Direct query to specific agent type
   */
  async processWithType(
    query: string,
    taskType: TaskType
  ): Promise<AgentResponse> {
    let agent = this.agents.get(taskType)
    if (!agent) {
      agent = new HybridAgent(taskType, this.oracle)
      this.agents.set(taskType, agent)
    }
    return agent.process(query)
  }

  /**
   * Get available agents
   */
  getAgentTypes(): TaskType[] {
    return ['research', 'code', 'analysis', 'blockchain', 'simple']
  }

  /**
   * Reset all agents
   */
  reset(): void {
    for (const agent of this.agents.values()) {
      agent.reset()
    }
  }
}
