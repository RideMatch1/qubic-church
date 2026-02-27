/**
 * Circuit Breaker — Fault Tolerance for Qubic RPC Calls
 *
 * Implements the circuit breaker pattern to prevent cascading failures
 * when the Qubic RPC node is unhealthy. The breaker tracks consecutive
 * failures and temporarily stops outgoing calls once a threshold is
 * reached, giving the downstream service time to recover.
 *
 * State machine:
 *   CLOSED  ──(failures >= threshold)──>  OPEN
 *   OPEN    ──(resetTimeout elapsed)───>  HALF_OPEN
 *   HALF_OPEN ──(success)──────────────>  CLOSED
 *   HALF_OPEN ──(failure)──────────────>  OPEN
 */

import { rpcLog } from './logger'
import { sendAlert } from './alerting'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type CircuitState = 'closed' | 'open' | 'half_open'

export interface CircuitBreakerOptions {
  /** Human-readable name used in log messages */
  name: string
  /** Number of consecutive failures before the circuit opens (default: 5) */
  failureThreshold?: number
  /** Milliseconds to wait before transitioning from OPEN to HALF_OPEN (default: 30 000) */
  resetTimeoutMs?: number
}

export interface CircuitBreakerSnapshot {
  state: CircuitState
  failureCount: number
  lastFailureTime: number | null
}

// ---------------------------------------------------------------------------
// CircuitOpenError
// ---------------------------------------------------------------------------

/**
 * Thrown when a call is attempted while the circuit is in the OPEN state.
 * Consumers can check `instanceof CircuitOpenError` to distinguish this
 * from real downstream errors.
 */
export class CircuitOpenError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'CircuitOpenError'
    // Maintain proper prototype chain for instanceof checks
    Object.setPrototypeOf(this, CircuitOpenError.prototype)
  }
}

// ---------------------------------------------------------------------------
// CircuitBreaker
// ---------------------------------------------------------------------------

export class CircuitBreaker {
  readonly name: string

  private readonly failureThreshold: number
  private readonly resetTimeoutMs: number

  private state: CircuitState = 'closed'
  private failureCount: number = 0
  private lastFailureTime: number = 0

  constructor(options: CircuitBreakerOptions) {
    this.name = options.name
    this.failureThreshold = options.failureThreshold ?? 5
    this.resetTimeoutMs = options.resetTimeoutMs ?? 30_000
  }

  // -----------------------------------------------------------------------
  // Public API
  // -----------------------------------------------------------------------

  /**
   * Returns `true` when calls are allowed to pass through.
   *
   * - CLOSED: always healthy
   * - OPEN: unhealthy unless the reset timeout has elapsed, in which case
   *         the breaker automatically transitions to HALF_OPEN and returns
   *         `true` to permit a single probe call.
   * - HALF_OPEN: healthy (one call is allowed to test the downstream)
   */
  isHealthy(): boolean {
    if (this.state === 'closed') return true

    if (this.state === 'open') {
      const elapsed = Date.now() - this.lastFailureTime
      if (elapsed >= this.resetTimeoutMs) {
        this.transitionTo('half_open')
        return true
      }
      return false
    }

    // half_open — allow the probe call
    return true
  }

  /**
   * Record a successful call. Resets the failure counter and transitions
   * the breaker back to CLOSED (if it was HALF_OPEN).
   */
  recordSuccess(): void {
    if (this.state === 'half_open') {
      rpcLog.info({ breaker: this.name }, 'probe call succeeded — closing circuit')
      void sendAlert('circuit_closed', 'info', `Circuit breaker ${this.name} recovered`, { breaker: this.name })
    }

    this.failureCount = 0
    this.transitionTo('closed')
  }

  /**
   * Record a failed call. Increments the failure counter and opens the
   * circuit once the threshold is reached.
   *
   * In HALF_OPEN state a single failure immediately reopens the circuit.
   */
  recordFailure(error?: Error): void {
    this.failureCount++
    this.lastFailureTime = Date.now()

    if (this.state === 'half_open') {
      rpcLog.warn({ breaker: this.name, error: error?.message }, 'probe call failed — reopening circuit')
      this.transitionTo('open')
      return
    }

    if (this.failureCount >= this.failureThreshold) {
      rpcLog.warn({ breaker: this.name, failures: this.failureCount, threshold: this.failureThreshold, error: error?.message }, 'failure threshold reached — opening circuit')
      this.transitionTo('open')
      void sendAlert('circuit_open', 'error', `Circuit breaker ${this.name} opened after ${this.failureCount} failures`, {
        breaker: this.name,
        failures: this.failureCount,
        lastError: error?.message,
      })
    }
  }

  /**
   * Return a snapshot of the breaker's current state for monitoring /
   * health-check endpoints.
   */
  getState(): CircuitBreakerSnapshot {
    // Evaluate timeout-based transitions so the snapshot is always current
    if (this.state === 'open') {
      const elapsed = Date.now() - this.lastFailureTime
      if (elapsed >= this.resetTimeoutMs) {
        this.transitionTo('half_open')
      }
    }

    return {
      state: this.state,
      failureCount: this.failureCount,
      lastFailureTime: this.lastFailureTime === 0 ? null : this.lastFailureTime,
    }
  }

  // -----------------------------------------------------------------------
  // Internal
  // -----------------------------------------------------------------------

  private transitionTo(next: CircuitState): void {
    if (this.state === next) return

    const prev = this.state
    this.state = next

    rpcLog.info({ breaker: this.name, from: prev, to: next }, 'circuit state transition')
  }
}

// ---------------------------------------------------------------------------
// Singleton — shared breaker for all Qubic RPC calls
// ---------------------------------------------------------------------------

export const rpcBreaker = new CircuitBreaker({
  name: 'qubic-rpc',
  failureThreshold: 5,
  resetTimeoutMs: 30_000,
})

// ---------------------------------------------------------------------------
// Helper — wrap any async RPC call with circuit-breaker protection
// ---------------------------------------------------------------------------

/**
 * Execute an async function with circuit-breaker protection.
 *
 * If the circuit is open, a `CircuitOpenError` is thrown immediately
 * without invoking `fn`. On success the breaker resets; on failure it
 * records the error and re-throws the original exception so callers can
 * still inspect the root cause.
 *
 * @example
 * ```ts
 * const balance = await withCircuitBreaker(() => getBalance(address))
 * ```
 */
export async function withCircuitBreaker<T>(fn: () => Promise<T>): Promise<T> {
  if (!rpcBreaker.isHealthy()) {
    throw new CircuitOpenError(`Circuit ${rpcBreaker.name} is open`)
  }

  try {
    const result = await fn()
    rpcBreaker.recordSuccess()
    return result
  } catch (err) {
    rpcBreaker.recordFailure(err instanceof Error ? err : undefined)
    throw err
  }
}
