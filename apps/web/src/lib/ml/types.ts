/**
 * Machine Learning & Pattern Recognition - Type Definitions
 */

export interface PatternRecognitionResult {
  patterns: Pattern[]
  clusters: Cluster[]
  anomalies: Anomaly[]
  correlations: Correlation[]
  confidence: number
  processingTime: number
}

export interface Pattern {
  id: string
  type: PatternType
  description: string
  addresses: string[]
  confidence: number
  frequency: number
  firstSeen: Date
  lastSeen: Date
  metadata: Record<string, any>
}

export type PatternType =
  | 'SEQUENTIAL'
  | 'TEMPORAL'
  | 'BALANCE_PATTERN'
  | 'TRANSACTION_PATTERN'
  | 'ADDRESS_PREFIX'
  | 'CLUSTERING'
  | 'CORRELATION'

export interface Cluster {
  id: string
  centroid: number[]
  members: string[]
  size: number
  cohesion: number
  label?: string
  features: ClusterFeatures
}

export interface ClusterFeatures {
  avgBalance: number
  avgTransactions: number
  avgAge: number
  commonPrefix?: string
  temporalPattern?: string
}

export interface Anomaly {
  id: string
  address: string
  type: AnomalyType
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  score: number
  description: string
  detectedAt: Date
  features: Record<string, any>
}

export type AnomalyType =
  | 'OUTLIER_BALANCE'
  | 'OUTLIER_TRANSACTIONS'
  | 'UNUSUAL_TIMING'
  | 'SUSPICIOUS_PATTERN'
  | 'STATISTICAL_OUTLIER'

export interface Correlation {
  dataset1: string
  dataset2: string
  coefficient: number
  pValue: number
  significance: 'NONE' | 'WEAK' | 'MODERATE' | 'STRONG' | 'VERY_STRONG'
  method: 'PEARSON' | 'SPEARMAN' | 'KENDALL'
}

export interface MLModel {
  id: string
  name: string
  type: MLModelType
  version: string
  trained: boolean
  accuracy?: number
  trainedOn: Date
  parameters: Record<string, any>
}

export type MLModelType =
  | 'K_MEANS'
  | 'DBSCAN'
  | 'ISOLATION_FOREST'
  | 'RANDOM_FOREST'
  | 'NEURAL_NETWORK'

export interface FeatureVector {
  address: string
  features: number[]
  normalized: boolean
  metadata?: Record<string, any>
}

export interface ClusteringConfig {
  algorithm: 'kmeans' | 'dbscan' | 'hierarchical'
  k?: number
  epsilon?: number
  minSamples?: number
  features: string[]
  normalize: boolean
}

export interface AnomalyDetectionConfig {
  algorithm: 'isolation-forest' | 'local-outlier-factor' | 'statistical'
  contamination: number
  threshold: number
  features: string[]
}
