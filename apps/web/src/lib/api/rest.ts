/**
 * REST API System
 * Complete REST API with authentication, rate limiting, and middleware
 */

import type {
  APIEndpoint,
  APIRequest,
  APIResponse,
  APIError,
  RateLimitInfo,
} from './types'

/**
 * API Router
 * Handles routing and middleware execution
 */
export class APIRouter {
  private endpoints: Map<string, APIEndpoint> = new Map()
  private rateLimiter: RateLimiter
  private authenticator: Authenticator

  constructor() {
    this.rateLimiter = new RateLimiter()
    this.authenticator = new Authenticator()
  }

  /**
   * Register an endpoint
   */
  register(endpoint: APIEndpoint) {
    const key = `${endpoint.method}:${endpoint.path}`
    this.endpoints.set(key, endpoint)
  }

  /**
   * Handle incoming request
   */
  async handle(method: string, path: string, request: APIRequest): Promise<APIResponse> {
    const key = `${method}:${path}`
    const endpoint = this.endpoints.get(key)

    if (!endpoint) {
      return this.errorResponse('NOT_FOUND', 'Endpoint not found', 404)
    }

    try {
      // Rate limiting
      if (endpoint.rateLimit) {
        const rateLimitResult = await this.rateLimiter.check(
          request.headers?.['x-api-key'] || 'anonymous',
          endpoint.rateLimit
        )

        if (!rateLimitResult.allowed) {
          return this.errorResponse(
            'RATE_LIMIT_EXCEEDED',
            'Too many requests',
            429,
            {
              rateLimit: rateLimitResult.info,
            }
          )
        }

        request.headers = {
          ...request.headers,
          ...rateLimitResult.headers,
        }
      }

      // Authentication
      if (endpoint.auth) {
        const authResult = await this.authenticator.authenticate(request)

        if (!authResult.success) {
          return this.errorResponse('UNAUTHORIZED', 'Authentication failed', 401)
        }

        request.user = authResult.user
      }

      // Execute handler
      const response = await endpoint.handler(request)

      // Add meta information
      response.meta = {
        timestamp: new Date().toISOString(),
        requestId: this.generateRequestId(),
        ...response.meta,
      }

      return response
    } catch (error) {
      console.error('API Error:', error)
      return this.errorResponse(
        'INTERNAL_ERROR',
        'Internal server error',
        500,
        { error: String(error) }
      )
    }
  }

  private errorResponse(
    code: string,
    message: string,
    statusCode: number,
    details?: any
  ): APIResponse {
    return {
      success: false,
      error: {
        code,
        message,
        statusCode,
        details,
      },
      meta: {
        timestamp: new Date().toISOString(),
        requestId: this.generateRequestId(),
      },
    }
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substring(7)}`
  }
}

/**
 * Rate Limiter
 * Token bucket algorithm for rate limiting
 */
class RateLimiter {
  private buckets: Map<
    string,
    {
      tokens: number
      lastRefill: number
    }
  > = new Map()

  async check(
    identifier: string,
    config: { maxRequests: number; windowMs: number }
  ): Promise<{
    allowed: boolean
    info: RateLimitInfo
    headers: Record<string, string>
  }> {
    const now = Date.now()
    const bucket = this.buckets.get(identifier) || {
      tokens: config.maxRequests,
      lastRefill: now,
    }

    // Refill tokens based on time passed
    const timePassed = now - bucket.lastRefill
    const refillAmount = (timePassed / config.windowMs) * config.maxRequests

    bucket.tokens = Math.min(config.maxRequests, bucket.tokens + refillAmount)
    bucket.lastRefill = now

    // Check if request is allowed
    const allowed = bucket.tokens >= 1

    if (allowed) {
      bucket.tokens -= 1
    }

    this.buckets.set(identifier, bucket)

    const resetTime = Math.ceil(now + config.windowMs)

    return {
      allowed,
      info: {
        limit: config.maxRequests,
        remaining: Math.floor(bucket.tokens),
        reset: resetTime,
      },
      headers: {
        'X-RateLimit-Limit': String(config.maxRequests),
        'X-RateLimit-Remaining': String(Math.floor(bucket.tokens)),
        'X-RateLimit-Reset': String(resetTime),
      },
    }
  }
}

/**
 * Authenticator
 * Handle API authentication
 */
class Authenticator {
  private apiKeys: Map<string, any> = new Map()

  constructor() {
    // Demo API keys
    this.apiKeys.set('demo_key_12345', {
      id: 'user-1',
      email: 'demo@example.com',
      role: 'user',
    })
    this.apiKeys.set('admin_key_67890', {
      id: 'admin-1',
      email: 'admin@example.com',
      role: 'admin',
    })
  }

  async authenticate(
    request: APIRequest
  ): Promise<{
    success: boolean
    user?: any
  }> {
    const apiKey =
      request.headers?.['x-api-key'] || request.headers?.['authorization']?.replace('Bearer ', '')

    if (!apiKey) {
      return { success: false }
    }

    const user = this.apiKeys.get(apiKey)

    if (!user) {
      return { success: false }
    }

    return {
      success: true,
      user: { ...user, apiKey },
    }
  }

  registerApiKey(key: string, user: any) {
    this.apiKeys.set(key, user)
  }
}

/**
 * Global API router instance
 */
export const apiRouter = new APIRouter()

/**
 * Helper to create API endpoint
 */
export function createEndpoint(config: APIEndpoint): APIEndpoint {
  return config
}

/**
 * Demo endpoints
 */
export function registerDemoEndpoints(router: APIRouter) {
  // Get all versions
  router.register(
    createEndpoint({
      path: '/api/versions',
      method: 'GET',
      handler: async (req) => {
        const { getVersions } = await import('../data-versioning/version-manager')
        const versions = getVersions()

        return {
          success: true,
          data: versions,
        }
      },
      rateLimit: {
        maxRequests: 100,
        windowMs: 60000, // 1 minute
      },
    })
  )

  // Get audit logs
  router.register(
    createEndpoint({
      path: '/api/audit',
      method: 'GET',
      handler: async (req) => {
        const { getAuditLog } = await import('../data-versioning/audit')
        const logs = getAuditLog()

        return {
          success: true,
          data: logs.slice(0, 100), // Limit to 100
        }
      },
      auth: true,
      rateLimit: {
        maxRequests: 50,
        windowMs: 60000,
      },
    })
  )

  // Analyze patterns (ML)
  router.register(
    createEndpoint({
      path: '/api/patterns/analyze',
      method: 'POST',
      handler: async (req) => {
        const { analyzePatterns } = await import('../ml/pattern-recognition')

        if (!req.body?.addresses) {
          return {
            success: false,
            error: {
              code: 'INVALID_REQUEST',
              message: 'Missing addresses in request body',
              statusCode: 400,
            },
          }
        }

        const result = await analyzePatterns(req.body.addresses, req.body.config)

        return {
          success: true,
          data: result,
        }
      },
      auth: true,
      rateLimit: {
        maxRequests: 10,
        windowMs: 60000,
      },
    })
  )

  // Export data
  router.register(
    createEndpoint({
      path: '/api/export',
      method: 'POST',
      handler: async (req) => {
        const { dataset, format = 'json' } = req.body || {}

        if (!dataset) {
          return {
            success: false,
            error: {
              code: 'INVALID_REQUEST',
              message: 'Missing dataset parameter',
              statusCode: 400,
            },
          }
        }

        // Simulate export
        return {
          success: true,
          data: {
            downloadUrl: `/downloads/${dataset}-${Date.now()}.${format}`,
            expiresAt: new Date(Date.now() + 3600000).toISOString(),
          },
        }
      },
      auth: true,
      rateLimit: {
        maxRequests: 5,
        windowMs: 60000,
      },
    })
  )
}

// Register demo endpoints
registerDemoEndpoints(apiRouter)
