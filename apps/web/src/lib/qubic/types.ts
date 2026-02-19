/**
 * Qubic API Types
 * Shared TypeScript interfaces for Qubic blockchain APIs
 */

// Re-export types from specific API clients for convenience
export type {
  EpochData,
  NetworkStatus,
  AddressBalance,
} from './rpc-client'

export type {
  NFTOwnership,
  CollectionStats,
  OwnerNFTs,
} from './qubicbay-api'

export type { EmissionData, EmissionPoint } from './emission-api'

export type { VerificationResult } from './genesis-verifier'

export type {
  OracleQuery,
  OracleResult,
  OracleStatus,
  ComputorOracleInfo,
  AddressActivity,
  SignalMonitor,
} from './oracle-client'

/**
 * API Error Types
 */
export interface APIError {
  code: string
  message: string
  details?: unknown
}

/**
 * API Response Wrapper
 */
export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: APIError
}

/**
 * Health Status
 */
export type HealthStatus = 'excellent' | 'good' | 'fair' | 'slow' | 'offline'

/**
 * Community Statistics
 */
export interface CommunityStats {
  totalHolders: number
  floorPrice: number
  volume24h: number
  totalTrades: number
  nftsSold: number
  timestamp: number
}
