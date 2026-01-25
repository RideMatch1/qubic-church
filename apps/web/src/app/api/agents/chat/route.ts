/**
 * HYBRID AGENT CHAT API
 *
 * POST /api/agents/chat
 * Body: { query: string, agentType?: TaskType, useMatrix?: boolean }
 */

import { NextResponse } from 'next/server'
import { AgentCoordinator, type TaskType } from '@/lib/agents/hybrid-agent'
import { MatrixOracle } from '@/lib/agents/oracle'

// Singleton coordinator (persists across requests)
let coordinator: AgentCoordinator | null = null
let oracle: MatrixOracle | null = null

async function getCoordinator(): Promise<AgentCoordinator> {
  if (!coordinator) {
    oracle = new MatrixOracle()
    // Load matrix data from file system in server context
    const fs = await import('node:fs/promises')
    const path = await import('node:path')

    const matrixPath = path.join(process.cwd(), 'public', 'data', 'anna-matrix.json')
    const data = JSON.parse(await fs.readFile(matrixPath, 'utf-8'))

    // Manually set matrix since we're on server
    const rawMatrix = data.matrix ?? data
    let matrix: number[][]

    if (Array.isArray(rawMatrix) && Array.isArray(rawMatrix[0])) {
      matrix = rawMatrix
    } else if (Array.isArray(rawMatrix)) {
      matrix = []
      for (let i = 0; i < 128; i++) {
        matrix.push(rawMatrix.slice(i * 128, (i + 1) * 128))
      }
    } else {
      throw new Error('Invalid matrix format')
    }

    // @ts-expect-error - accessing private property for server-side init
    oracle.matrix = matrix
    // @ts-expect-error - accessing private property
    oracle.matrixChecksum = 'server-loaded'

    coordinator = new AgentCoordinator(oracle)
  }
  return coordinator
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { query, agentType, useMatrix = true } = body as {
      query: string
      agentType?: TaskType
      useMatrix?: boolean
    }

    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Query is required' },
        { status: 400 }
      )
    }

    // Check for API key
    if (!process.env.GROQ_API_KEY) {
      return NextResponse.json(
        { error: 'GROQ_API_KEY not configured' },
        { status: 500 }
      )
    }

    const coord = await getCoordinator()

    let response
    if (agentType) {
      response = await coord.processWithType(query, agentType)
    } else {
      response = await coord.process(query)
    }

    return NextResponse.json({
      success: true,
      data: {
        content: response.content,
        taskType: response.taskType,
        confidence: response.confidence,
        sources: response.sources,
        matrix: response.matrixResult ? {
          decision: response.matrixResult.decision,
          aggregate: response.matrixResult.aggregateValue,
          energy: response.matrixResult.energy,
          interpretation: response.matrixResult.interpretation,
        } : null,
        usage: {
          model: response.llmResponse.model,
          tokens: response.llmResponse.usage.totalTokens,
          durationMs: response.llmResponse.durationMs,
        },
      },
    })
  } catch (error) {
    console.error('Agent chat error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal error' },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    availableAgents: ['research', 'code', 'analysis', 'blockchain', 'simple'],
    hasGroqKey: !!process.env.GROQ_API_KEY,
    hasOpenAIKey: !!process.env.OPENAI_API_KEY,
  })
}
