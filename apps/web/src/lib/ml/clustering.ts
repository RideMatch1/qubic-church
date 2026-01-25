/**
 * Clustering Algorithms for Address Pattern Recognition
 */

import type { Cluster, ClusteringConfig, FeatureVector } from './types'

/**
 * K-Means Clustering Algorithm
 * Groups addresses into k clusters based on feature similarity
 */
export function kMeansClustering(
  data: FeatureVector[],
  k: number = 5,
  maxIterations: number = 100
): Cluster[] {
  if (data.length === 0 || k <= 0) return []

  // Initialize centroids randomly
  let centroids = initializeCentroids(data, k)
  let clusters: Cluster[] = []
  let iterations = 0

  while (iterations < maxIterations) {
    // Assign points to nearest centroid
    const assignments = assignToClusters(data, centroids)

    // Update centroids
    const newCentroids = updateCentroids(data, assignments, k)

    // Check convergence
    if (centroidsConverged(centroids, newCentroids)) {
      break
    }

    centroids = newCentroids
    iterations++
  }

  // Build cluster objects
  const assignments = assignToClusters(data, centroids)
  clusters = buildClusters(data, assignments, centroids)

  return clusters
}

/**
 * DBSCAN (Density-Based Spatial Clustering)
 * Discovers clusters of arbitrary shape
 */
export function dbscanClustering(
  data: FeatureVector[],
  epsilon: number = 0.5,
  minSamples: number = 5
): Cluster[] {
  if (data.length === 0) return []

  const visited = new Set<number>()
  const clusters: Cluster[] = []
  let clusterId = 0

  for (let i = 0; i < data.length; i++) {
    if (visited.has(i)) continue

    visited.add(i)
    const neighbors = getNeighbors(data, i, epsilon)

    if (neighbors.length < minSamples) {
      // Mark as noise (could be added to separate noise cluster)
      continue
    }

    // Start new cluster
    const clusterMembers: number[] = []
    const seeds = [...neighbors]

    while (seeds.length > 0) {
      const current = seeds.pop()!

      if (!visited.has(current)) {
        visited.add(current)
        const currentNeighbors = getNeighbors(data, current, epsilon)

        if (currentNeighbors.length >= minSamples) {
          seeds.push(...currentNeighbors)
        }
      }

      clusterMembers.push(current)
    }

    // Calculate centroid for this cluster
    const centroid = calculateCentroid(data, clusterMembers)

    clusters.push({
      id: `cluster-${clusterId++}`,
      centroid,
      members: clusterMembers.map((idx) => data[idx]!.address),
      size: clusterMembers.length,
      cohesion: calculateCohesion(data, clusterMembers, centroid),
      features: extractClusterFeatures(data, clusterMembers),
    })
  }

  return clusters
}

/**
 * Hierarchical Clustering (Agglomerative)
 * Bottom-up clustering approach
 */
export function hierarchicalClustering(
  data: FeatureVector[],
  k: number = 5
): Cluster[] {
  if (data.length === 0) return []

  // Start with each point as its own cluster
  let clusters: Set<number>[] = data.map((_, idx) => new Set([idx]))

  // Merge until we have k clusters
  while (clusters.length > k) {
    // Find closest pair of clusters
    let minDistance = Infinity
    let mergeIdx1 = 0
    let mergeIdx2 = 1

    for (let i = 0; i < clusters.length; i++) {
      for (let j = i + 1; j < clusters.length; j++) {
        const dist = clusterDistance(data, clusters[i]!, clusters[j]!)
        if (dist < minDistance) {
          minDistance = dist
          mergeIdx1 = i
          mergeIdx2 = j
        }
      }
    }

    // Merge clusters
    const merged = new Set([...clusters[mergeIdx1]!, ...clusters[mergeIdx2]!])
    clusters = clusters.filter((_, idx) => idx !== mergeIdx1 && idx !== mergeIdx2)
    clusters.push(merged)
  }

  // Convert to Cluster objects
  return clusters.map((clusterSet, idx) => {
    const members = Array.from(clusterSet)
    const centroid = calculateCentroid(data, members)

    return {
      id: `cluster-${idx}`,
      centroid,
      members: members.map((idx) => data[idx]!.address),
      size: members.length,
      cohesion: calculateCohesion(data, members, centroid),
      features: extractClusterFeatures(data, members),
    }
  })
}

// Helper Functions

function initializeCentroids(data: FeatureVector[], k: number): number[][] {
  const centroids: number[][] = []
  const indices = new Set<number>()

  while (indices.size < k) {
    const idx = Math.floor(Math.random() * data.length)
    if (!indices.has(idx)) {
      indices.add(idx)
      centroids.push([...data[idx]!.features])
    }
  }

  return centroids
}

function assignToClusters(data: FeatureVector[], centroids: number[][]): number[] {
  return data.map((point) => {
    let minDistance = Infinity
    let closestCentroid = 0

    centroids.forEach((centroid, idx) => {
      const distance = euclideanDistance(point.features, centroid)
      if (distance < minDistance) {
        minDistance = distance
        closestCentroid = idx
      }
    })

    return closestCentroid
  })
}

function updateCentroids(
  data: FeatureVector[],
  assignments: number[],
  k: number
): number[][] {
  const centroids: number[][] = []

  for (let i = 0; i < k; i++) {
    const clusterPoints = data.filter((_, idx) => assignments[idx] === i)

    if (clusterPoints.length === 0) {
      // Keep old centroid if cluster is empty
      centroids.push(new Array(data[0]!.features.length).fill(0))
      continue
    }

    const centroid = new Array(clusterPoints[0]!.features.length).fill(0)

    clusterPoints.forEach((point) => {
      point.features.forEach((val, idx) => {
        centroid[idx]! += val!
      })
    })

    centroids.push(centroid.map((val) => val / clusterPoints.length))
  }

  return centroids
}

function centroidsConverged(old: number[][], newCentroids: number[][]): boolean {
  const threshold = 0.0001

  for (let i = 0; i < old.length; i++) {
    const distance = euclideanDistance(old[i]!, newCentroids[i]!)
    if (distance > threshold) return false
  }

  return true
}

function buildClusters(
  data: FeatureVector[],
  assignments: number[],
  centroids: number[][]
): Cluster[] {
  const clusters: Cluster[] = []

  centroids.forEach((centroid, idx) => {
    const members = data
      .map((point, pointIdx) => (assignments[pointIdx] === idx ? pointIdx : -1))
      .filter((idx) => idx !== -1)

    if (members.length === 0) return

    clusters.push({
      id: `cluster-${idx}`,
      centroid,
      members: members.map((idx) => data[idx]!.address),
      size: members.length,
      cohesion: calculateCohesion(data, members, centroid),
      features: extractClusterFeatures(data, members),
    })
  })

  return clusters
}

function getNeighbors(
  data: FeatureVector[],
  index: number,
  epsilon: number
): number[] {
  const neighbors: number[] = []
  const point = data[index]!

  data.forEach((other, idx) => {
    if (idx === index) return

    const distance = euclideanDistance(point.features, other.features)
    if (distance <= epsilon) {
      neighbors.push(idx)
    }
  })

  return neighbors
}

function calculateCentroid(data: FeatureVector[], indices: number[]): number[] {
  if (indices.length === 0) return []

  const dimensions = data[0]!.features.length
  const centroid = new Array(dimensions).fill(0)

  indices.forEach((idx) => {
    data[idx]!.features.forEach((val, dim) => {
      centroid[dim]! += val!
    })
  })

  return centroid.map((val) => val! / indices.length)
}

function calculateCohesion(
  data: FeatureVector[],
  indices: number[],
  centroid: number[]
): number {
  if (indices.length === 0) return 0

  const distances = indices.map((idx) =>
    euclideanDistance(data[idx]!.features, centroid)
  )

  const avgDistance = distances.reduce((a, b) => a + b, 0) / distances.length
  return 1 / (1 + avgDistance) // Cohesion score between 0 and 1
}

function clusterDistance(
  data: FeatureVector[],
  cluster1: Set<number>,
  cluster2: Set<number>
): number {
  const centroid1 = calculateCentroid(data, Array.from(cluster1))
  const centroid2 = calculateCentroid(data, Array.from(cluster2))
  return euclideanDistance(centroid1, centroid2)
}

function euclideanDistance(a: number[], b: number[]): number {
  let sum = 0
  for (let i = 0; i < a.length; i++) {
    sum += Math.pow(a[i]! - b[i]!, 2)
  }
  return Math.sqrt(sum)
}

function extractClusterFeatures(
  data: FeatureVector[],
  indices: number[]
): any {
  if (indices.length === 0) {
    return {
      avgBalance: 0,
      avgTransactions: 0,
      avgAge: 0,
    }
  }

  // Extract features from metadata if available
  const balances = indices
    .map((idx) => data[idx]!.metadata?.balance || 0)
    .filter((b) => b > 0)
  const transactions = indices
    .map((idx) => data[idx]!.metadata?.transactions || 0)
    .filter((t) => t > 0)

  return {
    avgBalance: balances.length > 0 ? balances.reduce((a, b) => a + b) / balances.length : 0,
    avgTransactions:
      transactions.length > 0 ? transactions.reduce((a, b) => a + b) / transactions.length : 0,
    avgAge: 0,
  }
}

/**
 * Normalize features to [0, 1] range
 */
export function normalizeFeatures(data: FeatureVector[]): FeatureVector[] {
  if (data.length === 0) return []

  const dimensions = data[0]!.features.length
  const mins = new Array(dimensions).fill(Infinity)
  const maxs = new Array(dimensions).fill(-Infinity)

  // Find min/max for each dimension
  data.forEach((point) => {
    point.features.forEach((val, dim) => {
      mins[dim]! = Math.min(mins[dim]!, val!)
      maxs[dim]! = Math.max(maxs[dim]!, val!)
    })
  })

  // Normalize
  return data.map((point) => ({
    ...point,
    features: point.features.map((val, dim) => {
      const range = maxs[dim]! - mins[dim]!
      return range === 0 ? 0 : (val! - mins[dim]!) / range
    }),
    normalized: true,
  }))
}
