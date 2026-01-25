/**
 * API & Webhook System - Type Definitions
 */

export interface APIResponse<T = any> {
  success: boolean
  data?: T
  error?: APIError
  meta?: ResponseMeta
}

export interface APIError {
  code: string
  message: string
  details?: any
  statusCode: number
}

export interface ResponseMeta {
  timestamp: string
  requestId: string
  rateLimit?: RateLimitInfo
  pagination?: PaginationInfo
}

export interface RateLimitInfo {
  limit: number
  remaining: number
  reset: number
}

export interface PaginationInfo {
  page: number
  pageSize: number
  totalPages: number
  totalItems: number
  hasNext: boolean
  hasPrev: boolean
}

export interface APIEndpoint {
  path: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  handler: (req: APIRequest) => Promise<APIResponse>
  auth?: boolean
  rateLimit?: {
    maxRequests: number
    windowMs: number
  }
}

export interface APIRequest {
  params?: Record<string, string>
  query?: Record<string, string>
  body?: any
  headers?: Record<string, string>
  user?: APIUser
}

export interface APIUser {
  id: string
  email: string
  role: 'admin' | 'user' | 'guest'
  apiKey?: string
}

export interface WebhookEvent {
  id: string
  type: WebhookEventType
  timestamp: Date
  data: any
  source: string
  version: string
}

export type WebhookEventType =
  | 'data.created'
  | 'data.updated'
  | 'data.deleted'
  | 'version.created'
  | 'audit.log'
  | 'pattern.detected'
  | 'anomaly.found'
  | 'export.completed'

export interface WebhookSubscription {
  id: string
  url: string
  events: WebhookEventType[]
  secret: string
  active: boolean
  createdAt: Date
  lastTriggeredAt?: Date
}

export interface WebhookDelivery {
  id: string
  subscriptionId: string
  event: WebhookEvent
  url: string
  status: 'pending' | 'success' | 'failed' | 'retrying'
  attempts: number
  lastAttemptAt: Date
  response?: {
    statusCode: number
    body: string
  }
}

// GraphQL Types
export interface GraphQLQuery {
  query: string
  variables?: Record<string, any>
  operationName?: string
}

export interface GraphQLResponse<T = any> {
  data?: T
  errors?: GraphQLError[]
}

export interface GraphQLError {
  message: string
  locations?: Array<{
    line: number
    column: number
  }>
  path?: string[]
  extensions?: Record<string, any>
}

export interface GraphQLContext {
  user?: APIUser
  dataSources: any
}
