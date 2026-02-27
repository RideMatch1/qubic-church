/**
 * Rate Limiter — Sliding Window In-Memory Throttle for QPredict
 *
 * Per-IP, per-endpoint rate limiting using a sliding window counter.
 * Automatically cleans up expired entries to prevent memory leaks.
 */

interface WindowEntry {
  count: number
  windowStart: number
}

// Storage: Map<"ip:endpoint", WindowEntry>
const windows = new Map<string, WindowEntry>()

// Auto-cleanup interval (every 5 minutes)
let cleanupStarted = false

function startCleanup(): void {
  if (cleanupStarted) return
  cleanupStarted = true

  const timer = setInterval(() => {
    const now = Date.now()
    for (const [key, entry] of windows) {
      // Remove entries older than 5 minutes
      if (now - entry.windowStart > 5 * 60_000) {
        windows.delete(key)
      }
    }
  }, 5 * 60_000)

  if (timer && typeof timer === 'object' && 'unref' in timer) {
    timer.unref()
  }
}

/** Rate limit configuration per endpoint */
export interface RateLimitConfig {
  /** Maximum requests allowed in the window */
  maxRequests: number
  /** Window duration in milliseconds */
  windowMs: number
}

/** Predefined limits for QPredict endpoints */
export const RATE_LIMITS: Record<string, RateLimitConfig> = {
  'POST /bet': { maxRequests: 5, windowMs: 60_000 },
  'POST /markets': { maxRequests: 2, windowMs: 60_000 },
  'POST /markets/resolve': { maxRequests: 1, windowMs: 60_000 },
  'POST /account/withdraw': { maxRequests: 1, windowMs: 60_000 },
  'GET /bet/status': { maxRequests: 30, windowMs: 60_000 },
  'GET /default': { maxRequests: 60, windowMs: 60_000 },
}

export interface RateLimitResult {
  allowed: boolean
  remaining: number
  retryAfterMs: number
}

/**
 * Check rate limit for a given IP and endpoint.
 *
 * @param ip - Client IP address (from request headers)
 * @param endpoint - Rate limit bucket key (e.g., 'POST /bet')
 * @param config - Optional override for the default limit
 * @returns Whether the request is allowed, remaining quota, and retry-after
 */
export function checkRateLimit(
  ip: string,
  endpoint: string,
  config?: RateLimitConfig,
): RateLimitResult {
  startCleanup()

  const limit = config ?? RATE_LIMITS[endpoint] ?? RATE_LIMITS['GET /default']!
  const key = `${ip}:${endpoint}`
  const now = Date.now()

  const entry = windows.get(key)

  if (!entry || now - entry.windowStart >= limit.windowMs) {
    // New window
    windows.set(key, { count: 1, windowStart: now })
    return { allowed: true, remaining: limit.maxRequests - 1, retryAfterMs: 0 }
  }

  if (entry.count >= limit.maxRequests) {
    // Over limit
    const retryAfterMs = limit.windowMs - (now - entry.windowStart)
    return { allowed: false, remaining: 0, retryAfterMs }
  }

  // Within limit
  entry.count++
  return { allowed: true, remaining: limit.maxRequests - entry.count, retryAfterMs: 0 }
}

/**
 * Extract client IP from a Next.js request.
 * Checks x-forwarded-for, x-real-ip, then falls back to 'unknown'.
 */
export function getClientIp(request: Request): string {
  const forwarded = (request.headers.get('x-forwarded-for') ?? '').split(',')[0]?.trim()
  if (forwarded) return forwarded

  const realIp = request.headers.get('x-real-ip')
  if (realIp) return realIp

  return 'unknown'
}

/**
 * Convenience: check rate limit and return a 429 Response if exceeded.
 * Returns null if the request is within limits.
 */
export function rateLimitResponse(
  request: Request,
  endpoint: string,
  config?: RateLimitConfig,
): Response | null {
  const ip = getClientIp(request)
  const result = checkRateLimit(ip, endpoint, config)

  if (!result.allowed) {
    const retryAfterSec = Math.ceil(result.retryAfterMs / 1000)
    return new Response(
      JSON.stringify({ error: 'Too many requests', retryAfter: retryAfterSec }),
      {
        status: 429,
        headers: {
          'Content-Type': 'application/json',
          'Retry-After': String(retryAfterSec),
          'X-RateLimit-Remaining': '0',
        },
      },
    )
  }

  return null
}
