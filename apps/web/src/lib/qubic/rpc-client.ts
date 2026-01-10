/**
 * Qubic RPC Client
 * Multi-endpoint RPC client with fallback support, rate limiting, and caching
 */

import { QUBIC_RPC_ENDPOINTS, API_CONFIG } from '@/config/api'

interface RPCRequest {
  jsonrpc: string
  id: string | number
  method: string
  params?: unknown[]
}

interface RPCResponse<T = unknown> {
  jsonrpc: string
  id: string | number
  result?: T
  error?: {
    code: number
    message: string
    data?: unknown
  }
}

export interface EpochData {
  epoch: number
  tick: number
  timestamp: number
  nextEpochIn: number
}

export interface NetworkStatus {
  tick: number
  tickRate: number
  tps: number
  health: 'excellent' | 'good' | 'fair' | 'slow'
}

export interface AddressBalance {
  address: string
  balance: bigint
}

/**
 * Simple rate limiter for API calls
 */
class RateLimiter {
  private timestamps: number[] = []

  canMakeRequest(): boolean {
    const now = Date.now()
    this.timestamps = this.timestamps.filter(
      (t) => now - t < API_CONFIG.rateLimit.perMilliseconds
    )
    return this.timestamps.length < API_CONFIG.rateLimit.maxRequests
  }

  recordRequest(): void {
    this.timestamps.push(Date.now())
  }
}

/**
 * Simple cache for RPC responses
 */
class RPCCache<T> {
  private cache = new Map<string, { data: T; timestamp: number }>()

  get(key: string, ttl: number): T | null {
    const cached = this.cache.get(key)
    if (!cached) return null

    const age = Date.now() - cached.timestamp
    if (age > ttl) {
      this.cache.delete(key)
      return null
    }

    return cached.data
  }

  set(key: string, data: T): void {
    this.cache.set(key, { data, timestamp: Date.now() })
  }

  clear(): void {
    this.cache.clear()
  }
}

/**
 * Qubic RPC Client
 * Handles communication with Qubic RPC nodes with automatic fallback
 */
export class QubicRPCClient {
  private static instance: QubicRPCClient
  private currentEndpointIndex = 0
  private rateLimiter = new RateLimiter()
  private cache = new RPCCache<unknown>()

  private constructor() {}

  static getInstance(): QubicRPCClient {
    if (!QubicRPCClient.instance) {
      QubicRPCClient.instance = new QubicRPCClient()
    }
    return QubicRPCClient.instance
  }

  /**
   * Make RPC call with automatic fallback
   */
  private async call<T>(
    method: string,
    params?: unknown[],
    cacheTTL?: number
  ): Promise<T> {
    // Check cache first if TTL provided
    const cacheKey = `${method}:${JSON.stringify(params || [])}`
    if (cacheTTL) {
      const cached = this.cache.get(cacheKey, cacheTTL) as T | null
      if (cached) return cached
    }

    // Rate limiting
    if (!this.rateLimiter.canMakeRequest()) {
      await new Promise((resolve) => setTimeout(resolve, 1000))
    }

    const request: RPCRequest = {
      jsonrpc: '2.0',
      id: Date.now(),
      method,
      params,
    }

    // Try each endpoint until one succeeds
    let lastError: Error | null = null

    for (let i = 0; i < QUBIC_RPC_ENDPOINTS.length; i++) {
      const endpointIndex =
        (this.currentEndpointIndex + i) % QUBIC_RPC_ENDPOINTS.length
      const endpoint = QUBIC_RPC_ENDPOINTS[endpointIndex]

      if (!endpoint) {
        continue // Skip if endpoint is somehow undefined
      }

      try {
        this.rateLimiter.recordRequest()

        const controller = new AbortController()
        const timeoutId = setTimeout(
          () => controller.abort(),
          API_CONFIG.timeout
        )

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
          signal: controller.signal,
        })

        clearTimeout(timeoutId)

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data = (await response.json()) as RPCResponse<T>

        if (data.error) {
          throw new Error(
            `RPC Error ${data.error.code}: ${data.error.message}`
          )
        }

        if (!data.result) {
          throw new Error('No result in RPC response')
        }

        // Success - update current endpoint and cache result
        this.currentEndpointIndex =
          (this.currentEndpointIndex + i) % QUBIC_RPC_ENDPOINTS.length
        if (cacheTTL) {
          this.cache.set(cacheKey, data.result)
        }

        return data.result
      } catch (error) {
        lastError =
          error instanceof Error ? error : new Error('Unknown RPC error')
        // Continue to next endpoint
        continue
      }
    }

    // All endpoints failed
    throw lastError || new Error('All RPC endpoints failed')
  }

  /**
   * Get current epoch data
   */
  async getCurrentEpoch(): Promise<EpochData> {
    return this.call<EpochData>(
      'getCurrentEpoch',
      undefined,
      API_CONFIG.cacheTime.epoch
    )
  }

  /**
   * Get network status
   */
  async getNetworkStatus(): Promise<NetworkStatus> {
    return this.call<NetworkStatus>(
      'getNetworkStatus',
      undefined,
      API_CONFIG.cacheTime.network
    )
  }

  /**
   * Get address balance (for Genesis token verification)
   */
  async getBalance(address: string): Promise<bigint> {
    const result = await this.call<AddressBalance>(
      'getBalance',
      [address],
      API_CONFIG.cacheTime.nftOwner
    )
    return result.balance
  }

  /**
   * Clear cache (useful for testing or manual refresh)
   */
  clearCache(): void {
    this.cache.clear()
  }
}

/**
 * Singleton instance export
 */
export const qubicRPC = QubicRPCClient.getInstance()
