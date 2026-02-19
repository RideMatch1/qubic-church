/**
 * Qubic Oracle Machine Client
 * Interfaces with the new Oracle Machine system (core v1.278.0+)
 *
 * The Oracle Machine brings real-world data into Qubic smart contracts.
 * Computors are obligated to run Oracle Machines for epoch revenue.
 *
 * Relevance to POCC/HASV research:
 * - Oracle provides the "verifiable via the protocol" mechanism
 * - 676 Computors must reach quorum (451+) on oracle data
 * - Could be the "signal" mechanism referenced in GENESIS token messages
 *
 * References:
 * - Oracle Machine: https://github.com/qubic/oracle-machine
 * - Core PR #758: https://github.com/qubic/core/pull/758
 * - CLI: https://github.com/qubic/qubic-cli (commands: -queryoracle, -getoraclequery)
 */

import { QUBIC_RPC_ENDPOINTS, API_CONFIG, ORACLE_CONFIG } from '@/config/api'

// ============================================================================
// Types
// ============================================================================

export interface OracleQuery {
  /** Query ID assigned by the network */
  queryId: string
  /** The data type being queried (price, event, custom) */
  dataType: string
  /** Query parameters */
  params: Record<string, unknown>
  /** Current status */
  status: 'pending' | 'committed' | 'finalized' | 'expired'
  /** Number of Computors that have committed */
  commitCount: number
  /** Quorum threshold (typically 451 of 676) */
  quorumThreshold: number
  /** Result if finalized */
  result?: OracleResult
  /** Tick when query was submitted */
  submittedAtTick: number
}

export interface OracleResult {
  /** The consensus value from 451+ Computors */
  value: string
  /** Number of Computors that agreed */
  agreementCount: number
  /** Tick when consensus was reached */
  finalizedAtTick: number
  /** Whether the result met quorum */
  quorumReached: boolean
}

export interface OracleStatus {
  /** Whether Oracle Machine is active on this node */
  active: boolean
  /** Number of connected Oracle Machine instances */
  connectedOMs: number
  /** Total oracle queries processed */
  totalQueries: number
  /** Active subscriptions */
  activeSubscriptions: number
}

export interface ComputorOracleInfo {
  /** Computor index (0-675) */
  index: number
  /** Whether this computor has an active Oracle Machine */
  oracleActive: boolean
  /** Number of oracle commits this epoch */
  oracleCommits: number
  /** Revenue impact of oracle participation */
  revenueMultiplier: number
}

export interface AddressActivity {
  /** Address being monitored */
  address: string
  /** Last known balance */
  balance: bigint
  /** Last activity tick */
  lastActivityTick: number
  /** Transaction count (if available) */
  txCount?: number
  /** Whether any oracle queries reference this address */
  oracleReferences: boolean
}

export interface SignalMonitor {
  /** Current date vs signal date */
  daysUntilSignal: number
  /** Whether we're in the signal window (March 3, 2026) */
  inSignalWindow: boolean
  /** POCC address activity */
  poccActivity: AddressActivity | null
  /** HASV address activity */
  hasvActivity: AddressActivity | null
  /** Current epoch computor count */
  computorCount: number
  /** Oracle system status */
  oracleStatus: OracleStatus | null
  /** Any oracle queries related to our watched addresses */
  relevantQueries: OracleQuery[]
}

// ============================================================================
// Oracle Client
// ============================================================================

/**
 * Qubic Oracle Machine Client
 * Monitors oracle activity and watches for GENESIS/EXODUS signal events
 */
export class QubicOracleClient {
  private static instance: QubicOracleClient
  private currentEndpointIndex = 0

  private constructor() {}

  static getInstance(): QubicOracleClient {
    if (!QubicOracleClient.instance) {
      QubicOracleClient.instance = new QubicOracleClient()
    }
    return QubicOracleClient.instance
  }

  /**
   * Make API call with fallback across endpoints
   */
  private async call<T>(endpoint: string, cacheTTL?: number): Promise<T> {
    let lastError: Error | null = null

    for (let i = 0; i < QUBIC_RPC_ENDPOINTS.length; i++) {
      const idx = (this.currentEndpointIndex + i) % QUBIC_RPC_ENDPOINTS.length
      const baseUrl = QUBIC_RPC_ENDPOINTS[idx]
      if (!baseUrl) continue

      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(
          () => controller.abort(),
          API_CONFIG.timeout
        )

        const response = await fetch(`${baseUrl}${endpoint}`, {
          method: 'GET',
          headers: { Accept: 'application/json' },
          signal: controller.signal,
        })

        clearTimeout(timeoutId)

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()
        this.currentEndpointIndex = idx
        return data as T
      } catch (error) {
        lastError =
          error instanceof Error ? error : new Error('Unknown API error')
        continue
      }
    }

    throw lastError || new Error('All Oracle API endpoints failed')
  }

  /**
   * Get address balance and activity
   */
  async getAddressActivity(address: string): Promise<AddressActivity> {
    try {
      const result = await this.call<{
        balance: {
          id: string
          balance: string | number
          validForTick?: number
          latestIncomingTransferTick?: number
          latestOutgoingTransferTick?: number
          numberOfIncomingTransfers?: number
          numberOfOutgoingTransfers?: number
        }
      }>(`/balances/${address}`)

      const balance = result.balance
      const lastTick = Math.max(
        balance.latestIncomingTransferTick ?? 0,
        balance.latestOutgoingTransferTick ?? 0
      )
      const txCount =
        (balance.numberOfIncomingTransfers ?? 0) +
        (balance.numberOfOutgoingTransfers ?? 0)

      return {
        address,
        balance: BigInt(balance.balance),
        lastActivityTick: lastTick,
        txCount: txCount > 0 ? txCount : undefined,
        oracleReferences: false, // Will be set by oracle query scan
      }
    } catch (error) {
      console.error(`[OracleClient] Activity fetch failed for ${address}:`, error)
      return {
        address,
        balance: BigInt(0),
        lastActivityTick: 0,
        oracleReferences: false,
      }
    }
  }

  /**
   * Get the full signal monitoring dashboard
   * Watches POCC/HASV addresses and oracle activity
   */
  async getSignalMonitor(): Promise<SignalMonitor> {
    const now = new Date()
    const signalDate = ORACLE_CONFIG.signalDate
    const daysUntil = Math.ceil(
      (signalDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
    )

    // Check if we're in the signal window (March 3, 2026 ±1 day)
    const inWindow = Math.abs(daysUntil) <= 1

    // Fetch POCC and HASV activity in parallel
    const [poccActivity, hasvActivity] = await Promise.all([
      this.getAddressActivity(ORACLE_CONFIG.watchAddresses.POCC).catch(
        () => null
      ),
      this.getAddressActivity(ORACLE_CONFIG.watchAddresses.HASV).catch(
        () => null
      ),
    ])

    return {
      daysUntilSignal: daysUntil,
      inSignalWindow: inWindow,
      poccActivity,
      hasvActivity,
      computorCount: 676,
      oracleStatus: null, // Oracle status endpoint TBD
      relevantQueries: [], // Oracle query scan TBD
    }
  }

  /**
   * Check if POCC or HASV addresses have new activity
   * Returns true if any balance change or transaction detected
   */
  async checkForSignalActivity(): Promise<{
    poccChanged: boolean
    hasvChanged: boolean
    details: string
  }> {
    const monitor = await this.getSignalMonitor()

    const details: string[] = []

    if (monitor.poccActivity) {
      details.push(
        `POCC balance: ${monitor.poccActivity.balance}, ` +
          `last tick: ${monitor.poccActivity.lastActivityTick}`
      )
    }

    if (monitor.hasvActivity) {
      details.push(
        `HASV balance: ${monitor.hasvActivity.balance}, ` +
          `last tick: ${monitor.hasvActivity.lastActivityTick}`
      )
    }

    details.push(`Days until signal: ${monitor.daysUntilSignal}`)
    details.push(`In signal window: ${monitor.inSignalWindow}`)

    return {
      poccChanged: false, // Need baseline comparison
      hasvChanged: false,
      details: details.join('\n'),
    }
  }
}

/**
 * Singleton instance export
 */
export const qubicOracle = QubicOracleClient.getInstance()
