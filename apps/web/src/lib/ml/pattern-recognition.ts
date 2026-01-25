/**
 * Pattern Recognition Engine
 * Comprehensive pattern discovery and analysis
 */

import type {
  PatternRecognitionResult,
  Pattern,
  Correlation,
  FeatureVector,
  Cluster,
} from './types'
import { kMeansClustering, dbscanClustering, normalizeFeatures } from './clustering'
import {
  isolationForest,
  localOutlierFactor,
  statisticalOutliers,
  patternAnomalies,
} from './anomaly-detection'

/**
 * Main Pattern Recognition Engine
 * Analyzes addresses and discovers patterns, clusters, and anomalies
 */
export async function analyzePatterns(
  addresses: any[],
  config?: {
    enableClustering?: boolean
    enableAnomalyDetection?: boolean
    enableCorrelation?: boolean
    clusterAlgorithm?: 'kmeans' | 'dbscan'
    anomalyAlgorithm?: 'isolation-forest' | 'lof' | 'statistical'
  }
): Promise<PatternRecognitionResult> {
  const startTime = performance.now()

  const {
    enableClustering = true,
    enableAnomalyDetection = true,
    enableCorrelation = true,
    clusterAlgorithm = 'kmeans',
    anomalyAlgorithm = 'isolation-forest',
  } = config || {}

  // Extract features from addresses
  const featureVectors = extractFeatures(addresses)
  const normalizedVectors = normalizeFeatures(featureVectors)

  // Pattern discovery
  const patterns = discoverPatterns(addresses)

  // Clustering
  let clusters: Cluster[] = []
  if (enableClustering && normalizedVectors.length > 0) {
    clusters =
      clusterAlgorithm === 'kmeans'
        ? kMeansClustering(normalizedVectors, 5)
        : dbscanClustering(normalizedVectors, 0.3, 5)
  }

  // Anomaly detection
  let anomalies: any[] = []
  if (enableAnomalyDetection && normalizedVectors.length > 0) {
    switch (anomalyAlgorithm) {
      case 'isolation-forest':
        anomalies = isolationForest(normalizedVectors, 0.1)
        break
      case 'lof':
        anomalies = localOutlierFactor(normalizedVectors, 20)
        break
      case 'statistical':
        anomalies = statisticalOutliers(normalizedVectors, 'zscore', 3)
        break
    }

    // Add pattern-based anomalies
    anomalies.push(...patternAnomalies(addresses))
  }

  // Correlation analysis
  const correlations = enableCorrelation ? analyzeCorrelations(addresses) : []

  const processingTime = performance.now() - startTime

  return {
    patterns,
    clusters,
    anomalies,
    correlations,
    confidence: calculateConfidence(patterns, clusters, anomalies),
    processingTime,
  }
}

/**
 * Extract numerical features from address data
 */
function extractFeatures(addresses: any[]): FeatureVector[] {
  return addresses.map((addr) => {
    const features: number[] = []

    // Balance feature (log scale)
    const balance = addr.balance || 0
    features.push(balance > 0 ? Math.log10(balance + 1) : 0)

    // Transaction count feature (log scale)
    const txCount = addr.transactions || 0
    features.push(txCount > 0 ? Math.log10(txCount + 1) : 0)

    // Age feature (days since first seen)
    if (addr.firstSeen) {
      const age = (Date.now() - new Date(addr.firstSeen).getTime()) / (1000 * 60 * 60 * 24)
      features.push(Math.log10(age + 1))
    } else {
      features.push(0)
    }

    // Activity ratio (transactions per day)
    if (addr.firstSeen && addr.lastSeen && addr.transactions) {
      const timeSpan =
        (new Date(addr.lastSeen).getTime() - new Date(addr.firstSeen).getTime()) /
        (1000 * 60 * 60 * 24)
      const ratio = timeSpan > 0 ? addr.transactions / timeSpan : 0
      features.push(Math.log10(ratio + 1))
    } else {
      features.push(0)
    }

    // Address prefix hash (simple numerical encoding)
    const prefix = addr.address ? addr.address.substring(0, 4) : ''
    const prefixHash = prefix.split('').reduce((sum: number, char: string) => sum + char.charCodeAt(0), 0)
    features.push(prefixHash / 1000)

    return {
      address: addr.address,
      features,
      normalized: false,
      metadata: addr,
    }
  })
}

/**
 * Discover patterns in address data
 */
function discoverPatterns(addresses: any[]): Pattern[] {
  const patterns: Pattern[] = []

  // Sequential patterns (addresses in sequence)
  const sequentialGroups = findSequentialPatterns(addresses)
  sequentialGroups.forEach((group, idx) => {
    patterns.push({
      id: `seq-${idx}`,
      type: 'SEQUENTIAL',
      description: `Sequential address pattern with ${group.length} addresses`,
      addresses: group.map((a) => a.address),
      confidence: 0.8,
      frequency: group.length,
      firstSeen: new Date(Math.min(...group.map((a) => new Date(a.firstSeen || Date.now()).getTime()))),
      lastSeen: new Date(Math.max(...group.map((a) => new Date(a.lastSeen || Date.now()).getTime()))),
      metadata: { groupSize: group.length },
    })
  })

  // Temporal patterns (addresses active in same time period)
  const temporalGroups = findTemporalPatterns(addresses)
  temporalGroups.forEach((group, idx) => {
    patterns.push({
      id: `temp-${idx}`,
      type: 'TEMPORAL',
      description: `Addresses active in similar time period (${group.period})`,
      addresses: group.addresses.map((a: any) => a.address),
      confidence: 0.75,
      frequency: group.addresses.length,
      firstSeen: group.startDate,
      lastSeen: group.endDate,
      metadata: { period: group.period },
    })
  })

  // Balance patterns (similar balances)
  const balanceGroups = findBalancePatterns(addresses)
  balanceGroups.forEach((group, idx) => {
    patterns.push({
      id: `bal-${idx}`,
      type: 'BALANCE_PATTERN',
      description: `Addresses with similar balance (${group.avgBalance.toFixed(4)} BTC)`,
      addresses: group.addresses.map((a: any) => a.address),
      confidence: 0.7,
      frequency: group.addresses.length,
      firstSeen: new Date(),
      lastSeen: new Date(),
      metadata: { avgBalance: group.avgBalance },
    })
  })

  // Address prefix patterns
  const prefixGroups = findPrefixPatterns(addresses)
  Object.entries(prefixGroups).forEach(([prefix, group]) => {
    if (group.length >= 5) {
      patterns.push({
        id: `prefix-${prefix}`,
        type: 'ADDRESS_PREFIX',
        description: `Addresses with prefix "${prefix}"`,
        addresses: group.map((a) => a.address),
        confidence: 0.9,
        frequency: group.length,
        firstSeen: new Date(),
        lastSeen: new Date(),
        metadata: { prefix },
      })
    }
  })

  return patterns
}

/**
 * Find sequential patterns in addresses
 */
function findSequentialPatterns(addresses: any[]): any[][] {
  const groups: any[][] = []
  const sorted = [...addresses].sort((a, b) => {
    const aTime = new Date(a.firstSeen || 0).getTime()
    const bTime = new Date(b.firstSeen || 0).getTime()
    return aTime - bTime
  })

  let currentGroup: any[] = []

  for (let i = 0; i < sorted.length; i++) {
    if (currentGroup.length === 0) {
      currentGroup.push(sorted[i])
      continue
    }

    const prevTime = new Date(currentGroup[currentGroup.length - 1].firstSeen || 0).getTime()
    const currTime = new Date(sorted[i].firstSeen || 0).getTime()
    const timeDiff = (currTime - prevTime) / (1000 * 60 * 60) // hours

    if (timeDiff < 24) {
      // Within 24 hours
      currentGroup.push(sorted[i])
    } else {
      if (currentGroup.length >= 3) {
        groups.push(currentGroup)
      }
      currentGroup = [sorted[i]]
    }
  }

  if (currentGroup.length >= 3) {
    groups.push(currentGroup)
  }

  return groups
}

/**
 * Find temporal patterns (time-based clustering)
 */
function findTemporalPatterns(addresses: any[]): any[] {
  const periods = ['2009-2010', '2011-2013', '2014-2017', '2018-2021', '2022-2024']
  const groups: any[] = []

  periods.forEach((period) => {
    const [startYear, endYear] = period.split('-').map(Number)
    const periodAddresses = addresses.filter((addr) => {
      if (!addr.firstSeen) return false
      const year = new Date(addr.firstSeen).getFullYear()
      return year >= startYear! && year <= endYear!
    })

    if (periodAddresses.length >= 10) {
      groups.push({
        period,
        addresses: periodAddresses,
        startDate: new Date(startYear!, 0, 1),
        endDate: new Date(endYear!, 11, 31),
      })
    }
  })

  return groups
}

/**
 * Find balance patterns
 */
function findBalancePatterns(addresses: any[]): any[] {
  const groups: any[] = []
  const ranges = [
    { min: 0, max: 0.1, label: 'Small' },
    { min: 0.1, max: 1, label: 'Medium' },
    { min: 1, max: 10, label: 'Large' },
    { min: 10, max: 100, label: 'Very Large' },
    { min: 100, max: Infinity, label: 'Whale' },
  ]

  ranges.forEach((range) => {
    const rangeAddresses = addresses.filter(
      (addr) => addr.balance >= range.min && addr.balance < range.max
    )

    if (rangeAddresses.length >= 10) {
      const avgBalance =
        rangeAddresses.reduce((sum, addr) => sum + (addr.balance || 0), 0) /
        rangeAddresses.length

      groups.push({
        addresses: rangeAddresses,
        avgBalance,
        label: range.label,
      })
    }
  })

  return groups
}

/**
 * Find address prefix patterns
 */
function findPrefixPatterns(addresses: any[]): Record<string, any[]> {
  const groups: Record<string, any[]> = {}

  addresses.forEach((addr) => {
    if (!addr.address) return
    const prefix = addr.address.substring(0, 4)

    if (!groups[prefix]) {
      groups[prefix] = []
    }
    groups[prefix].push(addr)
  })

  return groups
}

/**
 * Analyze correlations between datasets
 */
function analyzeCorrelations(addresses: any[]): Correlation[] {
  const correlations: Correlation[] = []

  // Example: Balance vs Transaction Count correlation
  const balances = addresses.map((a) => a.balance || 0).filter((b) => b > 0)
  const transactions = addresses.map((a) => a.transactions || 0).filter((t) => t > 0)

  if (balances.length > 10 && transactions.length > 10) {
    const coefficient = pearsonCorrelation(
      balances.slice(0, Math.min(balances.length, transactions.length)),
      transactions.slice(0, Math.min(balances.length, transactions.length))
    )

    correlations.push({
      dataset1: 'balance',
      dataset2: 'transactions',
      coefficient,
      pValue: 0.001, // Simplified
      significance: getSignificance(coefficient),
      method: 'PEARSON',
    })
  }

  return correlations
}

/**
 * Calculate Pearson correlation coefficient
 */
function pearsonCorrelation(x: number[], y: number[]): number {
  const n = Math.min(x.length, y.length)
  if (n === 0) return 0

  const meanX = x.reduce((a, b) => a + b, 0) / n
  const meanY = y.reduce((a, b) => a + b, 0) / n

  let numerator = 0
  let denomX = 0
  let denomY = 0

  for (let i = 0; i < n; i++) {
    const dx = x[i]! - meanX
    const dy = y[i]! - meanY
    numerator += dx * dy
    denomX += dx * dx
    denomY += dy * dy
  }

  const denominator = Math.sqrt(denomX * denomY)
  return denominator === 0 ? 0 : numerator / denominator
}

/**
 * Get correlation significance level
 */
function getSignificance(coefficient: number): Correlation['significance'] {
  const abs = Math.abs(coefficient)
  if (abs >= 0.8) return 'VERY_STRONG'
  if (abs >= 0.6) return 'STRONG'
  if (abs >= 0.4) return 'MODERATE'
  if (abs >= 0.2) return 'WEAK'
  return 'NONE'
}

/**
 * Calculate overall confidence score
 */
function calculateConfidence(patterns: Pattern[], clusters: any[], anomalies: any[]): number {
  // Simple confidence calculation based on findings
  const patternConfidence = patterns.reduce((sum, p) => sum + p.confidence, 0) / Math.max(patterns.length, 1)
  const clusterConfidence = clusters.length > 0 ? 0.8 : 0.5
  const anomalyConfidence = anomalies.length > 0 ? 0.7 : 0.5

  return (patternConfidence + clusterConfidence + anomalyConfidence) / 3
}
