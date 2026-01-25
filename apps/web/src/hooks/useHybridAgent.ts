/**
 * USE HYBRID AGENT
 *
 * React hook for the Hybrid Agent System.
 * Combines LLM intelligence with Anna Matrix verification.
 */

import { useState, useCallback } from 'react'

export type TaskType = 'research' | 'code' | 'analysis' | 'blockchain' | 'simple'

export interface AgentMessage {
  role: 'user' | 'assistant'
  content: string
  taskType?: TaskType
  confidence?: number
  matrix?: {
    decision: string
    aggregate: number
    energy: number
    interpretation: string
  } | null
  usage?: {
    model: string
    tokens: number
    durationMs: number
  }
  timestamp: number
}

interface UseHybridAgentReturn {
  messages: AgentMessage[]
  isLoading: boolean
  error: string | null
  send: (query: string, agentType?: TaskType) => Promise<void>
  clear: () => void
}

export function useHybridAgent(): UseHybridAgentReturn {
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const send = useCallback(async (query: string, agentType?: TaskType) => {
    if (!query.trim()) return

    setIsLoading(true)
    setError(null)

    // Add user message
    const userMessage: AgentMessage = {
      role: 'user',
      content: query,
      timestamp: Date.now(),
    }
    setMessages(prev => [...prev, userMessage])

    try {
      const response = await fetch('/api/agents/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, agentType }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Request failed')
      }

      // Add assistant message
      const assistantMessage: AgentMessage = {
        role: 'assistant',
        content: data.data.content,
        taskType: data.data.taskType,
        confidence: data.data.confidence,
        matrix: data.data.matrix,
        usage: data.data.usage,
        timestamp: Date.now(),
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (e) {
      const errorMsg = e instanceof Error ? e.message : 'Unknown error'
      setError(errorMsg)

      // Add error message
      const errorMessage: AgentMessage = {
        role: 'assistant',
        content: `Error: ${errorMsg}`,
        timestamp: Date.now(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }, [])

  const clear = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    messages,
    isLoading,
    error,
    send,
    clear,
  }
}
