/**
 * LLM CLIENT
 *
 * Unified client for multiple LLM providers.
 * Routes to cheapest/fastest option based on task complexity.
 */

import Groq from 'groq-sdk'

export type LLMProvider = 'groq' | 'openai'
export type ModelTier = 'fast' | 'smart' | 'reasoning'

interface LLMConfig {
  provider: LLMProvider
  model: string
  maxTokens: number
  temperature: number
}

const MODEL_CONFIGS: Record<ModelTier, LLMConfig> = {
  fast: {
    provider: 'groq',
    model: 'llama-3.1-8b-instant',
    maxTokens: 1024,
    temperature: 0.3,
  },
  smart: {
    provider: 'groq',
    model: 'llama-3.3-70b-versatile',
    maxTokens: 2048,
    temperature: 0.5,
  },
  reasoning: {
    provider: 'groq',
    model: 'llama-3.3-70b-versatile',
    maxTokens: 4096,
    temperature: 0.7,
  },
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface LLMResponse {
  content: string
  provider: LLMProvider
  model: string
  usage: {
    promptTokens: number
    completionTokens: number
    totalTokens: number
  }
  durationMs: number
}

/**
 * LLM Client - routes to appropriate provider
 */
export class LLMClient {
  private groq: Groq | null = null

  constructor() {
    const groqKey = process.env.GROQ_API_KEY
    if (groqKey) {
      this.groq = new Groq({ apiKey: groqKey })
    }
  }

  /**
   * Chat completion with automatic provider selection
   */
  async chat(
    messages: ChatMessage[],
    tier: ModelTier = 'fast'
  ): Promise<LLMResponse> {
    const config = MODEL_CONFIGS[tier]
    const start = performance.now()

    if (config.provider === 'groq' && this.groq) {
      return this.chatGroq(messages, config, start)
    }

    throw new Error('No LLM provider available')
  }

  /**
   * Quick classification (always uses fastest model)
   */
  async classify(
    prompt: string,
    options: string[]
  ): Promise<{ choice: string; confidence: number }> {
    const systemPrompt = `You are a classifier. Given a query, respond with ONLY one of these options: ${options.join(', ')}
No explanation, just the option.`

    const response = await this.chat(
      [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: prompt },
      ],
      'fast'
    )

    const choice = options.find(o =>
      response.content.toLowerCase().includes(o.toLowerCase())
    ) ?? options[0]

    return {
      choice: choice ?? 'unknown',
      confidence: choice ? 0.8 : 0.3,
    }
  }

  /**
   * Structured extraction
   */
  async extract<T>(prompt: string, schema: string): Promise<T | null> {
    const systemPrompt = `Extract information from the user's input and respond with valid JSON matching this schema:
${schema}
Respond ONLY with JSON, no markdown, no explanation.`

    const response = await this.chat(
      [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: prompt },
      ],
      'smart'
    )

    try {
      return JSON.parse(response.content) as T
    } catch {
      return null
    }
  }

  private async chatGroq(
    messages: ChatMessage[],
    config: LLMConfig,
    start: number
  ): Promise<LLMResponse> {
    if (!this.groq) throw new Error('Groq not initialized')

    const completion = await this.groq.chat.completions.create({
      model: config.model,
      messages: messages.map(m => ({
        role: m.role,
        content: m.content,
      })),
      max_tokens: config.maxTokens,
      temperature: config.temperature,
    })

    const content = completion.choices[0]?.message?.content ?? ''

    return {
      content,
      provider: 'groq',
      model: config.model,
      usage: {
        promptTokens: completion.usage?.prompt_tokens ?? 0,
        completionTokens: completion.usage?.completion_tokens ?? 0,
        totalTokens: completion.usage?.total_tokens ?? 0,
      },
      durationMs: Math.round(performance.now() - start),
    }
  }

  /**
   * Check if client is ready
   */
  isReady(): boolean {
    return this.groq !== null
  }
}

// Singleton instance
let clientInstance: LLMClient | null = null

export function getLLMClient(): LLMClient {
  if (!clientInstance) {
    clientInstance = new LLMClient()
  }
  return clientInstance
}
