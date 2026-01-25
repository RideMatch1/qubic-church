/**
 * RESONANCE API - Echte Ternary Matrix Berechnung
 *
 * POST /api/agents/resonance
 *
 * Modes:
 * - single: Berechne Resonance für einen Input
 * - compare: Vergleiche zwei Inputs
 * - batch: Analysiere viele Inputs
 * - oracle: Ja/Nein Antwort auf eine Frage
 */

import { NextResponse } from 'next/server'
import {
  computeResonance,
  compareInputs,
  batchResonance,
  askOracle,
  type ResonanceResult,
} from '@/lib/agents/resonance-core'

// Matrix cache
let matrixCache: number[][] | null = null

async function getMatrix(): Promise<number[][]> {
  if (matrixCache) return matrixCache

  const fs = await import('node:fs/promises')
  const path = await import('node:path')
  const matrixPath = path.join(process.cwd(), 'public', 'data', 'anna-matrix.json')
  const data = JSON.parse(await fs.readFile(matrixPath, 'utf-8'))
  const rawMatrix = data.matrix ?? data

  if (Array.isArray(rawMatrix) && Array.isArray(rawMatrix[0])) {
    matrixCache = rawMatrix
  } else {
    matrixCache = []
    for (let i = 0; i < 128; i++) {
      matrixCache.push(rawMatrix.slice(i * 128, (i + 1) * 128))
    }
  }

  return matrixCache
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { mode, input, inputA, inputB, inputs, question } = body as {
      mode: 'single' | 'compare' | 'batch' | 'oracle'
      input?: string
      inputA?: string
      inputB?: string
      inputs?: string[]
      question?: string
    }

    const startTime = Date.now()
    const matrix = await getMatrix()

    let result: unknown

    switch (mode) {
      case 'single': {
        if (!input) {
          return NextResponse.json({ error: 'Input required for single mode' }, { status: 400 })
        }
        result = computeResonance(input, matrix)
        break
      }

      case 'compare': {
        if (!inputA || !inputB) {
          return NextResponse.json({ error: 'inputA and inputB required for compare mode' }, { status: 400 })
        }
        result = compareInputs(inputA, inputB, matrix)
        break
      }

      case 'batch': {
        if (!inputs || !Array.isArray(inputs) || inputs.length === 0) {
          return NextResponse.json({ error: 'inputs array required for batch mode' }, { status: 400 })
        }
        // Limit batch size
        const limitedInputs = inputs.slice(0, 50)
        result = batchResonance(limitedInputs, matrix)
        break
      }

      case 'oracle': {
        if (!question) {
          return NextResponse.json({ error: 'Question required for oracle mode' }, { status: 400 })
        }
        result = askOracle(question, matrix)
        break
      }

      default:
        return NextResponse.json({ error: 'Invalid mode. Use: single, compare, batch, oracle' }, { status: 400 })
    }

    return NextResponse.json({
      success: true,
      mode,
      durationMs: Date.now() - startTime,
      data: result,
    })
  } catch (error) {
    console.error('Resonance error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Resonance computation failed' },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json({
    name: 'Resonance Engine',
    description: 'Echte Ternary Matrix Berechnung durch die Anna Matrix',
    version: '1.0',
    modes: {
      single: {
        description: 'Berechne Resonance für einen einzelnen Input',
        body: '{ "mode": "single", "input": "your input here" }',
        inputTypes: ['text', 'Bitcoin address (1... or 3...)', 'hex string'],
      },
      compare: {
        description: 'Vergleiche zwei Inputs durch Matrix-Resonance',
        body: '{ "mode": "compare", "inputA": "first", "inputB": "second" }',
      },
      batch: {
        description: 'Analysiere bis zu 50 Inputs und ranke nach Energy',
        body: '{ "mode": "batch", "inputs": ["input1", "input2", ...] }',
      },
      oracle: {
        description: 'Stelle eine Ja/Nein Frage',
        body: '{ "mode": "oracle", "question": "Is CFB Satoshi?" }',
      },
    },
    howItWorks: [
      '1. Input wird zu 64 Ternary-Werten (-1, 0, +1) konvertiert',
      '2. Tick-Loop läuft durch die 128x128 Anna Matrix',
      '3. Neuronen berechnen gewichtete Summen der Nachbarn',
      '4. Loop endet bei Konvergenz oder nach max 500 Ticks',
      '5. Energy und Output-Pattern werden analysiert',
      '6. Ergebnis ist 100% deterministisch und reproduzierbar',
    ],
    technical: {
      matrixSize: '128x128 = 16,384 Zellen',
      inputNeurons: 64,
      outputNeurons: 64,
      neighborsPerNeuron: 8,
      maxTicks: 500,
      valueRange: '-128 to +127 (ternary clamped to -1, 0, +1)',
    },
  })
}
