/**
 * Anomaly Detection Algorithms
 * Identifies outliers and unusual patterns in address data
 */

import type { Anomaly, FeatureVector, AnomalyDetectionConfig } from './types'

/**
 * Isolation Forest Algorithm
 * Efficient anomaly detection for high-dimensional data
 */
export function isolationForest(
  data: FeatureVector[],
  contamination: number = 0.1,
  numTrees: number = 100
): Anomaly[] {
  if (data.length === 0) return []

  const anomalies: Anomaly[] = []
  const scores: number[] = []

  // Build isolation trees
  const trees = buildIsolationTrees(data, numTrees)

  // Calculate anomaly scores
  data.forEach((point, idx) => {
    const avgPathLength = trees.reduce((sum, tree) => {
      return sum + getPathLength(tree, point.features)
    }, 0) / numTrees

    // Normalize score
    const expectedLength = expectedPathLength(data.length)
    const score = Math.pow(2, -avgPathLength / expectedLength)
    scores.push(score)
  })

  // Identify anomalies based on contamination threshold
  const threshold = calculateThreshold(scores, contamination)

  data.forEach((point, idx) => {
    if (scores[idx]! > threshold) {
      anomalies.push({
        id: `anomaly-${idx}`,
        address: point.address,
        type: 'STATISTICAL_OUTLIER',
        severity: getSeverity(scores[idx]!, threshold),
        score: scores[idx]!,
        description: `Anomaly detected with score ${scores[idx]!.toFixed(3)}`,
        detectedAt: new Date(),
        features: point.metadata || {},
      })
    }
  })

  return anomalies
}

/**
 * Local Outlier Factor (LOF)
 * Density-based anomaly detection
 */
export function localOutlierFactor(
  data: FeatureVector[],
  k: number = 20,
  threshold: number = 1.5
): Anomaly[] {
  if (data.length === 0) return []

  const anomalies: Anomaly[] = []

  data.forEach((point, idx) => {
    // Find k-nearest neighbors
    const neighbors = findKNearestNeighbors(data, idx, k)

    // Calculate local reachability density
    const lrd = calculateLRD(data, idx, neighbors)

    // Calculate LOF score
    const lof = calculateLOF(data, idx, neighbors, lrd)

    if (lof > threshold) {
      anomalies.push({
        id: `lof-anomaly-${idx}`,
        address: point.address,
        type: 'STATISTICAL_OUTLIER',
        severity: getSeverityFromLOF(lof, threshold),
        score: lof,
        description: `Local outlier detected (LOF: ${lof.toFixed(2)})`,
        detectedAt: new Date(),
        features: { lof, neighbors: neighbors.length, ...point.metadata },
      })
    }
  })

  return anomalies
}

/**
 * Statistical Outlier Detection
 * Z-score and IQR methods
 */
export function statisticalOutliers(
  data: FeatureVector[],
  method: 'zscore' | 'iqr' = 'zscore',
  threshold: number = 3
): Anomaly[] {
  if (data.length === 0) return []

  const anomalies: Anomaly[] = []

  if (method === 'zscore') {
    // Z-score method
    const dimensions = data[0]!.features.length

    for (let dim = 0; dim < dimensions; dim++) {
      const values = data.map((p) => p.features[dim]!)
      const mean = values.reduce((a, b) => a! + b!, 0) / values.length
      const variance =
        values.reduce((sum, val) => sum + Math.pow(val! - mean, 2), 0) / values.length
      const std = Math.sqrt(variance)

      data.forEach((point, idx) => {
        const zscore = Math.abs((point.features[dim]! - mean) / std)

        if (zscore > threshold) {
          anomalies.push({
            id: `zscore-${dim}-${idx}`,
            address: point.address,
            type: 'STATISTICAL_OUTLIER',
            severity: getSeverity(zscore / threshold, 1),
            score: zscore,
            description: `Z-score outlier in dimension ${dim} (z=${zscore.toFixed(2)})`,
            detectedAt: new Date(),
            features: { dimension: dim, zscore, mean, std, ...point.metadata },
          })
        }
      })
    }
  } else {
    // IQR method
    const dimensions = data[0]!.features.length

    for (let dim = 0; dim < dimensions; dim++) {
      const values = data.map((p) => p.features[dim]!).sort((a, b) => a! - b!)
      const q1 = values[Math.floor(values.length * 0.25)]!
      const q3 = values[Math.floor(values.length * 0.75)]!
      const iqr = q3 - q1
      const lowerBound = q1 - threshold * iqr
      const upperBound = q3 + threshold * iqr

      data.forEach((point, idx) => {
        const value = point.features[dim]!

        if (value < lowerBound || value > upperBound) {
          anomalies.push({
            id: `iqr-${dim}-${idx}`,
            address: point.address,
            type: 'STATISTICAL_OUTLIER',
            severity: 'MEDIUM',
            score: value < lowerBound ? lowerBound - value : value - upperBound,
            description: `IQR outlier in dimension ${dim}`,
            detectedAt: new Date(),
            features: { dimension: dim, value, q1, q3, iqr, ...point.metadata },
          })
        }
      })
    }
  }

  return anomalies
}

/**
 * Pattern-based Anomaly Detection
 * Detect unusual patterns in address behavior
 */
export function patternAnomalies(addresses: any[]): Anomaly[] {
  const anomalies: Anomaly[] = []

  addresses.forEach((addr, idx) => {
    // Unusual balance patterns
    if (addr.balance && addr.balance > 1000) {
      anomalies.push({
        id: `balance-${idx}`,
        address: addr.address,
        type: 'OUTLIER_BALANCE',
        severity: 'HIGH',
        score: addr.balance / 1000,
        description: `Unusually high balance: ${addr.balance} BTC`,
        detectedAt: new Date(),
        features: { balance: addr.balance },
      })
    }

    // Unusual transaction patterns
    if (addr.transactions && addr.transactions > 10000) {
      anomalies.push({
        id: `tx-${idx}`,
        address: addr.address,
        type: 'OUTLIER_TRANSACTIONS',
        severity: 'HIGH',
        score: addr.transactions / 10000,
        description: `Unusually high transaction count: ${addr.transactions}`,
        detectedAt: new Date(),
        features: { transactions: addr.transactions },
      })
    }

    // Temporal anomalies
    if (addr.firstSeen && addr.lastSeen) {
      const timeDiff =
        new Date(addr.lastSeen).getTime() - new Date(addr.firstSeen).getTime()
      const days = timeDiff / (1000 * 60 * 60 * 24)

      if (days < 1 && addr.transactions > 100) {
        anomalies.push({
          id: `temporal-${idx}`,
          address: addr.address,
          type: 'UNUSUAL_TIMING',
          severity: 'MEDIUM',
          score: addr.transactions / days,
          description: `High transaction velocity: ${addr.transactions} tx in ${days.toFixed(1)} days`,
          detectedAt: new Date(),
          features: { transactions: addr.transactions, days },
        })
      }
    }
  })

  return anomalies
}

// Helper Functions

interface IsolationTree {
  feature?: number
  splitValue?: number
  left?: IsolationTree
  right?: IsolationTree
  size?: number
}

function buildIsolationTrees(
  data: FeatureVector[],
  numTrees: number
): IsolationTree[] {
  const trees: IsolationTree[] = []
  const sampleSize = Math.min(256, data.length)

  for (let i = 0; i < numTrees; i++) {
    const sample = sampleData(data, sampleSize)
    trees.push(buildIsolationTree(sample, 0, Math.ceil(Math.log2(sampleSize))))
  }

  return trees
}

function buildIsolationTree(
  data: FeatureVector[],
  depth: number,
  maxDepth: number
): IsolationTree {
  if (depth >= maxDepth || data.length <= 1) {
    return { size: data.length }
  }

  const feature = Math.floor(Math.random() * data[0]!.features.length)
  const values = data.map((p) => p.features[feature]!)
  const min = Math.min(...values)
  const max = Math.max(...values)

  if (min === max) {
    return { size: data.length }
  }

  const splitValue = min + Math.random() * (max - min)

  const left = data.filter((p) => p.features[feature]! < splitValue)
  const right = data.filter((p) => p.features[feature]! >= splitValue)

  return {
    feature,
    splitValue,
    left: buildIsolationTree(left, depth + 1, maxDepth),
    right: buildIsolationTree(right, depth + 1, maxDepth),
  }
}

function getPathLength(tree: IsolationTree, point: number[], depth: number = 0): number {
  if (tree.size !== undefined) {
    return depth + expectedPathLength(tree.size)
  }

  if (tree.feature !== undefined && tree.splitValue !== undefined) {
    if (point[tree.feature]! < tree.splitValue && tree.left) {
      return getPathLength(tree.left, point, depth + 1)
    } else if (tree.right) {
      return getPathLength(tree.right, point, depth + 1)
    }
  }

  return depth
}

function expectedPathLength(n: number): number {
  if (n <= 1) return 0
  const harmonic = 2 * (Math.log(n - 1) + 0.5772156649) - (2 * (n - 1)) / n
  return harmonic
}

function sampleData(data: FeatureVector[], size: number): FeatureVector[] {
  const sample: FeatureVector[] = []
  const indices = new Set<number>()

  while (indices.size < size && indices.size < data.length) {
    const idx = Math.floor(Math.random() * data.length)
    if (!indices.has(idx)) {
      indices.add(idx)
      sample.push(data[idx]!)
    }
  }

  return sample
}

function calculateThreshold(scores: number[], contamination: number): number {
  const sorted = [...scores].sort((a, b) => b - a)
  const index = Math.floor(sorted.length * contamination)
  return sorted[index] || 0.5
}

function findKNearestNeighbors(
  data: FeatureVector[],
  idx: number,
  k: number
): number[] {
  const distances: Array<{ idx: number; distance: number }> = []

  data.forEach((other, otherIdx) => {
    if (otherIdx === idx) return

    const distance = euclideanDistance(data[idx]!.features, other.features)
    distances.push({ idx: otherIdx, distance })
  })

  distances.sort((a, b) => a.distance - b.distance)
  return distances.slice(0, k).map((d) => d.idx)
}

function calculateLRD(data: FeatureVector[], idx: number, neighbors: number[]): number {
  if (neighbors.length === 0) return 1

  const reachabilityDistances = neighbors.map((nIdx) => {
    const distance = euclideanDistance(data[idx]!.features, data[nIdx]!.features)
    const kDistance = findKDistance(data, nIdx, neighbors.length)
    return Math.max(distance, kDistance)
  })

  const avgReachDist =
    reachabilityDistances.reduce((a, b) => a + b, 0) / reachabilityDistances.length

  return 1 / avgReachDist
}

function calculateLOF(
  data: FeatureVector[],
  idx: number,
  neighbors: number[],
  lrd: number
): number {
  if (neighbors.length === 0) return 1

  const neighborLRDs = neighbors.map((nIdx) =>
    calculateLRD(data, nIdx, findKNearestNeighbors(data, nIdx, neighbors.length))
  )

  const avgNeighborLRD = neighborLRDs.reduce((a, b) => a + b, 0) / neighborLRDs.length

  return avgNeighborLRD / lrd
}

function findKDistance(data: FeatureVector[], idx: number, k: number): number {
  const distances = data.map((other, otherIdx) => {
    if (otherIdx === idx) return Infinity
    return euclideanDistance(data[idx]!.features, other.features)
  })

  const sorted = distances.sort((a, b) => a! - b!)
  return sorted[Math.min(k - 1, sorted.length - 1)]! || 0
}

function euclideanDistance(a: number[], b: number[]): number {
  let sum = 0
  for (let i = 0; i < a.length; i++) {
    sum += Math.pow(a[i]! - b[i]!, 2)
  }
  return Math.sqrt(sum)
}

function getSeverity(score: number, threshold: number): Anomaly['severity'] {
  const ratio = score / threshold
  if (ratio >= 2) return 'CRITICAL'
  if (ratio >= 1.5) return 'HIGH'
  if (ratio >= 1.2) return 'MEDIUM'
  return 'LOW'
}

function getSeverityFromLOF(lof: number, threshold: number): Anomaly['severity'] {
  if (lof >= threshold * 2) return 'CRITICAL'
  if (lof >= threshold * 1.5) return 'HIGH'
  if (lof >= threshold * 1.2) return 'MEDIUM'
  return 'LOW'
}
