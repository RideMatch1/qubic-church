'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import type {
  AnnaCell,
  VIPCellData,
  CellNeighbors,
  MatrixStats,
  RowStats,
  RawAnnaMatrix,
  RawInterestingAddress,
  AnnaGridError,
  UseAnnaGridDataReturn,
} from './types'
import { DATA_URLS, MATRIX_SIZE, SPECIAL_ROWS, SPECIAL_ADDRESSES } from './constants'

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function addressToRowCol(address: number): { row: number; col: number } {
  return {
    row: Math.floor(address / MATRIX_SIZE),
    col: address % MATRIX_SIZE,
  }
}

function rowColToAddress(row: number, col: number): number {
  return row * MATRIX_SIZE + col
}

function valueToHex(value: number): string {
  const unsigned = value < 0 ? 256 + value : value
  return '0x' + unsigned.toString(16).toUpperCase().padStart(2, '0')
}

function valueToBinary(value: number): string {
  const unsigned = value < 0 ? 256 + value : value
  return unsigned.toString(2).padStart(8, '0')
}

function calculateRowStats(row: number[]): RowStats {
  const positiveCount = row.filter((v) => v > 0).length
  const negativeCount = row.filter((v) => v < 0).length
  const sum = row.reduce((a, b) => a + b, 0)

  return {
    min: Math.min(...row),
    max: Math.max(...row),
    mean: sum / row.length,
    sum,
    positiveCount,
    negativeCount,
  }
}

function calculateMedian(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 !== 0
    ? sorted[mid]!
    : (sorted[mid - 1]! + sorted[mid]!) / 2
}

function calculateStdDev(values: number[], mean: number): number {
  const squareDiffs = values.map((v) => Math.pow(v - mean, 2))
  const avgSquareDiff = squareDiffs.reduce((a, b) => a + b, 0) / values.length
  return Math.sqrt(avgSquareDiff)
}

// =============================================================================
// HOOK: useAnnaGridData
// =============================================================================

export function useAnnaGridData(): UseAnnaGridDataReturn {
  const [loading, setLoading] = useState(true)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<AnnaGridError | null>(null)
  const [matrix, setMatrix] = useState<number[][] | null>(null)
  const [stats, setStats] = useState<MatrixStats | null>(null)
  const [vipCells, setVipCells] = useState<Map<string, VIPCellData>>(new Map())
  const [retryCount, setRetryCount] = useState(0)

  // Load all data
  const loadData = useCallback(async () => {
    setLoading(true)
    setProgress(0)
    setError(null)

    try {
      // Phase 1: Load Anna Matrix (0-60%)
      setProgress(10)
      const matrixRes = await fetch(DATA_URLS.matrix)
      if (!matrixRes.ok) {
        throw new Error(`Failed to load matrix: ${matrixRes.status}`)
      }

      setProgress(30)
      const matrixJson: RawAnnaMatrix = await matrixRes.json()

      if (!matrixJson.matrix || !Array.isArray(matrixJson.matrix)) {
        throw new Error('Invalid matrix format')
      }

      setProgress(50)

      // Validate dimensions
      if (matrixJson.matrix.length !== MATRIX_SIZE) {
        throw new Error(`Expected ${MATRIX_SIZE} rows, got ${matrixJson.matrix.length}`)
      }

      setProgress(60)

      // Phase 2: Load Interesting Addresses (60-80%)
      const interestingRes = await fetch(DATA_URLS.interesting)
      if (!interestingRes.ok) {
        throw new Error(`Failed to load interesting addresses: ${interestingRes.status}`)
      }

      setProgress(70)
      const interestingJson = await interestingRes.json()
      const interestingAddresses: RawInterestingAddress[] = interestingJson.records || []

      setProgress(80)

      // Phase 3: Process data (80-100%)

      // Build VIP cells map
      const vipMap = new Map<string, VIPCellData>()
      interestingAddresses.forEach((addr) => {
        const key = `${addr.position[0]}-${addr.position[1]}`
        vipMap.set(key, {
          bitcoinAddress: addr.address,
          xorVariant: addr.xor,
          method: addr.method,
          compressed: addr.compressed,
          hash160: addr.hash160,
        })
      })

      setProgress(85)

      // Calculate statistics
      const allValues = matrixJson.matrix.flat()
      const positiveCount = allValues.filter((v) => v > 0).length
      const negativeCount = allValues.filter((v) => v < 0).length
      const zeroCount = allValues.filter((v) => v === 0).length
      const sum = allValues.reduce((a, b) => a + b, 0)
      const mean = sum / allValues.length
      const median = calculateMedian(allValues)
      const stdDev = calculateStdDev(allValues, mean)

      setProgress(90)

      const calculatedStats: MatrixStats = {
        totalCells: MATRIX_SIZE * MATRIX_SIZE,
        min: Math.min(...allValues),
        max: Math.max(...allValues),
        mean,
        median,
        stdDev,
        positiveCount,
        negativeCount,
        zeroCount,
        uniqueValues: new Set(allValues).size,
        specialRows: {
          row21: calculateRowStats(matrixJson.matrix[21] || []),
          row68: calculateRowStats(matrixJson.matrix[68] || []),
          row96: calculateRowStats(matrixJson.matrix[96] || []),
        },
        vipCount: vipMap.size,
        vipPositions: interestingAddresses.map((addr) => ({
          row: addr.position[0],
          col: addr.position[1],
          address: addr.address,
        })),
      }

      setProgress(100)

      // Set state
      setMatrix(matrixJson.matrix)
      setStats(calculatedStats)
      setVipCells(vipMap)
      setLoading(false)
    } catch (err) {
      console.error('Failed to load Anna Grid data:', err)
      setError({
        type: err instanceof SyntaxError ? 'PARSE_ERROR' : 'NETWORK_ERROR',
        message: 'Failed to Load Anna Matrix',
        details: err instanceof Error ? err.message : 'Unknown error',
        retryable: true,
      })
      setLoading(false)
    }
  }, [])

  // Initial load
  useEffect(() => {
    loadData()
  }, [loadData])

  // Retry handler
  const retry = useCallback(() => {
    setRetryCount((c) => c + 1)
    loadData()
  }, [loadData])

  // =============================================================================
  // HELPER FUNCTIONS
  // =============================================================================

  // Get cell by row/col
  const getCell = useCallback(
    (row: number, col: number): AnnaCell | null => {
      if (!matrix) return null
      if (row < 0 || row >= MATRIX_SIZE || col < 0 || col >= MATRIX_SIZE) return null

      const value = matrix[row]?.[col]
      if (value === undefined) return null

      const address = rowColToAddress(row, col)
      const vipKey = `${row}-${col}`
      const vipData = vipCells.get(vipKey)

      // Check special row
      const specialRow = SPECIAL_ROWS[row]
      const isBootAddress = address === SPECIAL_ADDRESSES.boot.address
      const isPoczAddress = address === SPECIAL_ADDRESSES.pocz.address

      // Normalize value to 0-1
      const normalized = (value - (-128)) / (127 - (-128))

      return {
        address,
        row,
        col,
        value,
        hex: valueToHex(value),
        binary: valueToBinary(value),
        normalized,
        isSpecialRow: !!specialRow || isBootAddress || isPoczAddress,
        specialRowType: isBootAddress
          ? 'boot'
          : isPoczAddress
            ? 'pocz'
            : specialRow?.type,
        specialRowName: isBootAddress
          ? 'Boot Address'
          : isPoczAddress
            ? 'POCZ Address'
            : specialRow?.name,
        isVIP: !!vipData,
        vipData,
      }
    },
    [matrix, vipCells]
  )

  // Get cell by linear address
  const getCellByAddress = useCallback(
    (address: number): AnnaCell | null => {
      const { row, col } = addressToRowCol(address)
      return getCell(row, col)
    },
    [getCell]
  )

  // Get neighboring cells
  const getCellNeighbors = useCallback(
    (row: number, col: number): CellNeighbors => {
      if (!matrix) return {}

      return {
        top: row > 0 ? matrix[row - 1]?.[col] : undefined,
        topRight: row > 0 && col < MATRIX_SIZE - 1 ? matrix[row - 1]?.[col + 1] : undefined,
        right: col < MATRIX_SIZE - 1 ? matrix[row]?.[col + 1] : undefined,
        bottomRight: row < MATRIX_SIZE - 1 && col < MATRIX_SIZE - 1 ? matrix[row + 1]?.[col + 1] : undefined,
        bottom: row < MATRIX_SIZE - 1 ? matrix[row + 1]?.[col] : undefined,
        bottomLeft: row < MATRIX_SIZE - 1 && col > 0 ? matrix[row + 1]?.[col - 1] : undefined,
        left: col > 0 ? matrix[row]?.[col - 1] : undefined,
        topLeft: row > 0 && col > 0 ? matrix[row - 1]?.[col - 1] : undefined,
      }
    },
    [matrix]
  )

  // Search by exact value
  const searchByValue = useCallback(
    (value: number): AnnaCell[] => {
      if (!matrix) return []

      const results: AnnaCell[] = []
      for (let row = 0; row < MATRIX_SIZE; row++) {
        for (let col = 0; col < MATRIX_SIZE; col++) {
          if (matrix[row]?.[col] === value) {
            const cell = getCell(row, col)
            if (cell) results.push(cell)
          }
        }
      }
      return results
    },
    [matrix, getCell]
  )

  // Search by value range
  const searchByRange = useCallback(
    (min: number, max: number): AnnaCell[] => {
      if (!matrix) return []

      const results: AnnaCell[] = []
      for (let row = 0; row < MATRIX_SIZE; row++) {
        for (let col = 0; col < MATRIX_SIZE; col++) {
          const val = matrix[row]?.[col]
          if (val !== undefined && val >= min && val <= max) {
            const cell = getCell(row, col)
            if (cell) results.push(cell)
          }
        }
      }
      return results
    },
    [matrix, getCell]
  )

  return {
    loading,
    progress,
    error,
    matrix,
    stats,
    vipCells,
    getCell,
    getCellByAddress,
    getCellNeighbors,
    searchByValue,
    searchByRange,
    retry,
    retryCount,
  }
}
