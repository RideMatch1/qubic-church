/**
 * MATRIX ORACLE
 *
 * The Anna Matrix as a data oracle - answers come from encoded data,
 * not from an LLM. Mathematically verifiable.
 *
 * How it works:
 * 1. Query → SHA-256 hash → Matrix coordinates
 * 2. Read values at those coordinates
 * 3. Interpret values against known patterns (Bitcoin addresses, etc.)
 * 4. Return deterministic, verifiable answer
 */

import { computeEnergy } from '../aigarth/ternary'
import type { TernaryState } from '../aigarth/types'

/** Oracle query result - mathematically provable */
export interface OracleResult {
  query: string
  queryHash: string
  matrixCoordinates: Array<{ row: number; col: number; value: number }>
  aggregateValue: number
  energy: number
  decision: 'yes' | 'no' | 'uncertain'
  confidence: number
  proof: {
    inputHash: string
    matrixChecksum: string
    timestamp: number
  }
  interpretation: string
}

/** Known patterns in the matrix */
const KNOWN_PATTERNS = {
  // CFB signature pattern (row 45, cells with value 123)
  cfbSignature: { row: 45, expectedValue: 123 },
  // Bitcoin genesis reference (row 0, col 0)
  genesisMarker: { row: 0, col: 0, expectedValue: -128 },
  // Satoshi pattern (diagonal cells)
  satoshiDiagonal: [
    { row: 45, col: 92 },
    { row: 46, col: 93 },
    { row: 47, col: 94 },
  ],
}

/**
 * Matrix Oracle - deterministic answers from encoded data
 */
export class MatrixOracle {
  private matrix: number[][] | null = null
  private matrixChecksum = ''

  /**
   * Load the Anna Matrix
   */
  async loadMatrix(): Promise<void> {
    const res = await fetch('/data/anna-matrix.json')
    const data = await res.json()

    const rawMatrix = data.matrix ?? data

    if (Array.isArray(rawMatrix) && Array.isArray(rawMatrix[0])) {
      this.matrix = rawMatrix
    } else if (Array.isArray(rawMatrix)) {
      this.matrix = []
      for (let i = 0; i < 128; i++) {
        this.matrix.push(rawMatrix.slice(i * 128, (i + 1) * 128))
      }
    } else {
      throw new Error('Invalid matrix format')
    }

    // Compute checksum for verification
    this.matrixChecksum = await this.computeChecksum()
  }

  /**
   * Query the oracle - returns deterministic, verifiable result
   */
  async query(input: string): Promise<OracleResult> {
    if (!this.matrix) throw new Error('Matrix not loaded')

    // Step 1: Hash the query
    const queryHash = await this.hashString(input)

    // Step 2: Map hash to matrix coordinates (deterministic)
    const coordinates = this.hashToCoordinates(queryHash)

    // Step 3: Read values at those coordinates
    const values = coordinates.map(coord => ({
      ...coord,
      value: this.matrix?.[coord.row]?.[coord.col] ?? 0,
    }))

    // Step 4: Compute aggregate (XOR-based for ternary compatibility)
    const aggregateValue = values.reduce((acc, v) => acc ^ v.value, 0)

    // Step 5: Convert to ternary states and compute energy
    const ternaryStates = values.map(v =>
      v.value > 0 ? 1 : v.value < 0 ? -1 : 0
    ) as TernaryState[]
    const energy = computeEnergy(ternaryStates)

    // Step 6: Decision based on aggregate
    let decision: 'yes' | 'no' | 'uncertain'
    if (aggregateValue > 64) decision = 'yes'
    else if (aggregateValue < -64) decision = 'no'
    else decision = 'uncertain'

    // Step 7: Confidence based on value distribution
    const positiveCount = values.filter(v => v.value > 0).length
    const confidence = Math.abs(positiveCount / values.length - 0.5) * 2

    // Step 8: Generate interpretation based on patterns found
    const interpretation = this.interpretValues(input, values, aggregateValue)

    return {
      query: input,
      queryHash,
      matrixCoordinates: values,
      aggregateValue,
      energy,
      decision,
      confidence,
      proof: {
        inputHash: queryHash,
        matrixChecksum: this.matrixChecksum,
        timestamp: Date.now(),
      },
      interpretation,
    }
  }

  /**
   * Verify a previous result (anyone can verify)
   */
  async verify(result: OracleResult): Promise<boolean> {
    // Re-compute and compare
    const queryHash = await this.hashString(result.query)
    if (queryHash !== result.queryHash) return false

    const currentChecksum = await this.computeChecksum()
    if (currentChecksum !== result.proof.matrixChecksum) return false

    // Re-query and compare aggregate
    const newResult = await this.query(result.query)
    return newResult.aggregateValue === result.aggregateValue
  }

  /**
   * Check for known patterns in the matrix
   */
  checkKnownPatterns(): Array<{
    pattern: string
    found: boolean
    value: number | null
  }> {
    if (!this.matrix) return []

    const results = []

    // Check CFB signature
    const cfbValue = this.matrix[KNOWN_PATTERNS.cfbSignature.row]?.[45]
    results.push({
      pattern: 'CFB Signature',
      found: cfbValue === KNOWN_PATTERNS.cfbSignature.expectedValue,
      value: cfbValue ?? null,
    })

    // Check Genesis marker
    const genesisValue =
      this.matrix[KNOWN_PATTERNS.genesisMarker.row]?.[
        KNOWN_PATTERNS.genesisMarker.col
      ]
    results.push({
      pattern: 'Genesis Marker',
      found: genesisValue === KNOWN_PATTERNS.genesisMarker.expectedValue,
      value: genesisValue ?? null,
    })

    // Check Satoshi diagonal
    const diagonalValues = KNOWN_PATTERNS.satoshiDiagonal.map(
      coord => this.matrix?.[coord.row]?.[coord.col] ?? 0
    )
    const diagonalSum = diagonalValues.reduce((a, b) => a + b, 0)
    results.push({
      pattern: 'Satoshi Diagonal',
      found: Math.abs(diagonalSum) > 100,
      value: diagonalSum,
    })

    return results
  }

  private async hashString(input: string): Promise<string> {
    const encoder = new TextEncoder()
    const data = encoder.encode(input.toLowerCase().trim())
    const hashBuffer = await crypto.subtle.digest('SHA-256', data)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
  }

  private hashToCoordinates(hash: string): Array<{ row: number; col: number }> {
    // Use hash bytes to deterministically select 8 matrix coordinates
    const coordinates = []
    for (let i = 0; i < 16; i += 2) {
      const rowByte = Number.parseInt(hash.slice(i * 2, i * 2 + 2), 16)
      const colByte = Number.parseInt(hash.slice(i * 2 + 2, i * 2 + 4), 16)
      coordinates.push({
        row: rowByte % 128,
        col: colByte % 128,
      })
    }
    return coordinates
  }

  private async computeChecksum(): Promise<string> {
    if (!this.matrix) return ''
    // Simple checksum of first and last rows
    const data = [...(this.matrix[0] ?? []), ...(this.matrix[127] ?? [])].join(
      ','
    )
    return this.hashString(data)
  }

  private interpretValues(
    query: string,
    values: Array<{ row: number; col: number; value: number }>,
    aggregate: number
  ): string {
    const queryLower = query.toLowerCase()

    // Pattern matching based on query content
    if (queryLower.includes('satoshi')) {
      const satoshiCells = values.filter(
        v => v.row >= 44 && v.row <= 48 && v.col >= 90 && v.col <= 96
      )
      if (satoshiCells.length > 0) {
        const sum = satoshiCells.reduce((a, b) => a + b.value, 0)
        return `Query maps to Satoshi region (rows 44-48, cols 90-96). Aggregate: ${sum}. ${
          sum > 0 ? 'Positive correlation found.' : 'No strong correlation.'
        }`
      }
    }

    if (queryLower.includes('cfb') || queryLower.includes('come-from-beyond')) {
      const cfbCells = values.filter(v => v.row === 45)
      if (cfbCells.length > 0) {
        return `Query maps to CFB signature row (45). Values: [${cfbCells.map(c => c.value).join(', ')}]. Pattern ${
          cfbCells.some(c => c.value === 123) ? 'MATCHED' : 'not found'
        }.`
      }
    }

    if (queryLower.includes('bitcoin') || queryLower.includes('btc')) {
      const bitcoinCells = values.filter(v => v.row < 32)
      if (bitcoinCells.length > 0) {
        return `Query maps to Bitcoin region (rows 0-31). ${bitcoinCells.length} cells accessed. Aggregate energy: ${aggregate}.`
      }
    }

    if (queryLower.includes('qubic')) {
      const qubicCells = values.filter(v => v.row >= 64 && v.row < 96)
      if (qubicCells.length > 0) {
        return `Query maps to Qubic region (rows 64-95). ${qubicCells.length} cells accessed. Network signature: ${
          aggregate > 0 ? 'active' : 'neutral'
        }.`
      }
    }

    // Generic interpretation
    const positives = values.filter(v => v.value > 0).length
    const negatives = values.filter(v => v.value < 0).length
    return `Query hashed to ${values.length} matrix cells. Distribution: +${positives}/-${negatives}/0:${values.length - positives - negatives}. Aggregate: ${aggregate}.`
  }
}
