/**
 * Webhook System
 * Reliable webhook delivery with retries and signature verification
 */

import type {
  WebhookEvent,
  WebhookSubscription,
  WebhookDelivery,
  WebhookEventType,
} from './types'
import crypto from 'crypto'

/**
 * Webhook Manager
 * Handles webhook subscriptions and delivery
 */
export class WebhookManager {
  private subscriptions: Map<string, WebhookSubscription> = new Map()
  private deliveries: Map<string, WebhookDelivery> = new Map()
  private maxRetries: number = 3
  private retryDelays: number[] = [1000, 5000, 30000] // 1s, 5s, 30s

  /**
   * Subscribe to webhook events
   */
  async subscribe(
    url: string,
    events: WebhookEventType[],
    options?: { secret?: string }
  ): Promise<WebhookSubscription> {
    const subscription: WebhookSubscription = {
      id: `wh_${crypto.randomUUID()}`,
      url,
      events,
      secret: options?.secret || this.generateSecret(),
      active: true,
      createdAt: new Date(),
    }

    this.subscriptions.set(subscription.id, subscription)

    return subscription
  }

  /**
   * Unsubscribe from webhooks
   */
  async unsubscribe(subscriptionId: string): Promise<boolean> {
    return this.subscriptions.delete(subscriptionId)
  }

  /**
   * Get subscription
   */
  getSubscription(subscriptionId: string): WebhookSubscription | undefined {
    return this.subscriptions.get(subscriptionId)
  }

  /**
   * Get all subscriptions
   */
  getAllSubscriptions(): WebhookSubscription[] {
    return Array.from(this.subscriptions.values())
  }

  /**
   * Trigger webhook event
   */
  async trigger(event: WebhookEvent): Promise<void> {
    const matchingSubscriptions = Array.from(this.subscriptions.values()).filter(
      (sub) => sub.active && sub.events.includes(event.type)
    )

    // Deliver to all matching subscriptions
    const deliveries = matchingSubscriptions.map((sub) =>
      this.deliver(sub, event)
    )

    await Promise.allSettled(deliveries)
  }

  /**
   * Deliver webhook to a subscription
   */
  private async deliver(
    subscription: WebhookSubscription,
    event: WebhookEvent,
    attempt: number = 1
  ): Promise<WebhookDelivery> {
    const delivery: WebhookDelivery = {
      id: `del_${crypto.randomUUID()}`,
      subscriptionId: subscription.id,
      event,
      url: subscription.url,
      status: 'pending',
      attempts: attempt,
      lastAttemptAt: new Date(),
    }

    this.deliveries.set(delivery.id, delivery)

    try {
      // Generate signature
      const signature = this.generateSignature(event, subscription.secret)

      // Send webhook
      const response = await fetch(subscription.url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Webhook-Signature': signature,
          'X-Webhook-Event': event.type,
          'X-Webhook-ID': event.id,
          'X-Webhook-Timestamp': event.timestamp.toISOString(),
        },
        body: JSON.stringify(event),
      })

      delivery.response = {
        statusCode: response.status,
        body: await response.text(),
      }

      if (response.ok) {
        delivery.status = 'success'
        subscription.lastTriggeredAt = new Date()
      } else {
        throw new Error(`HTTP ${response.status}`)
      }
    } catch (error) {
      console.error(`Webhook delivery failed:`, error)

      // Retry logic
      if (attempt < this.maxRetries) {
        delivery.status = 'retrying'

        // Schedule retry
        const delay = this.retryDelays[attempt - 1] || 30000
        setTimeout(() => {
          this.deliver(subscription, event, attempt + 1)
        }, delay)
      } else {
        delivery.status = 'failed'

        // Optionally deactivate subscription after too many failures
        // subscription.active = false
      }
    }

    this.deliveries.set(delivery.id, delivery)
    return delivery
  }

  /**
   * Generate HMAC signature for webhook verification
   */
  private generateSignature(event: WebhookEvent, secret: string): string {
    const payload = JSON.stringify(event)
    const hmac = crypto.createHmac('sha256', secret)
    hmac.update(payload)
    return `sha256=${hmac.digest('hex')}`
  }

  /**
   * Verify webhook signature
   */
  static verifySignature(
    payload: string,
    signature: string,
    secret: string
  ): boolean {
    const expectedSignature = crypto
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex')

    const providedSignature = signature.replace('sha256=', '')

    return crypto.timingSafeEqual(
      Buffer.from(expectedSignature),
      Buffer.from(providedSignature)
    )
  }

  /**
   * Generate secure secret
   */
  private generateSecret(): string {
    return `whsec_${crypto.randomBytes(32).toString('hex')}`
  }

  /**
   * Get delivery history
   */
  getDeliveries(subscriptionId?: string): WebhookDelivery[] {
    const deliveries = Array.from(this.deliveries.values())

    if (subscriptionId) {
      return deliveries.filter((d) => d.subscriptionId === subscriptionId)
    }

    return deliveries
  }

  /**
   * Get delivery statistics
   */
  getStats(subscriptionId?: string) {
    const deliveries = this.getDeliveries(subscriptionId)

    return {
      total: deliveries.length,
      successful: deliveries.filter((d) => d.status === 'success').length,
      failed: deliveries.filter((d) => d.status === 'failed').length,
      pending: deliveries.filter((d) => d.status === 'pending').length,
      retrying: deliveries.filter((d) => d.status === 'retrying').length,
    }
  }
}

/**
 * Global webhook manager instance
 */
export const webhookManager = new WebhookManager()

/**
 * Helper functions
 */
export function createWebhookEvent(
  type: WebhookEventType,
  data: any,
  source: string = 'evidence-api'
): WebhookEvent {
  return {
    id: `evt_${crypto.randomUUID()}`,
    type,
    timestamp: new Date(),
    data,
    source,
    version: '1.0.0',
  }
}

/**
 * Trigger helper for common events
 */
export async function triggerDataCreated(data: any) {
  const event = createWebhookEvent('data.created', data)
  await webhookManager.trigger(event)
}

export async function triggerDataUpdated(data: any) {
  const event = createWebhookEvent('data.updated', data)
  await webhookManager.trigger(event)
}

export async function triggerPatternDetected(pattern: any) {
  const event = createWebhookEvent('pattern.detected', pattern)
  await webhookManager.trigger(event)
}

export async function triggerAnomalyFound(anomaly: any) {
  const event = createWebhookEvent('anomaly.found', anomaly)
  await webhookManager.trigger(event)
}

// For Node.js crypto in browser environments, we need a polyfill
// This is a simplified implementation for demo purposes
const cryptoPolyfill = {
  randomUUID: () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0
      const v = c === 'x' ? r : (r & 0x3) | 0x8
      return v.toString(16)
    })
  },
  createHmac: (algorithm: string, secret: string) => {
    return {
      update: (data: string) => {
        return {
          digest: (encoding: string) => {
            // Simplified hash for demo - use proper crypto in production
            let hash = 0
            const combined = secret + data
            for (let i = 0; i < combined.length; i++) {
              const char = combined.charCodeAt(i)
              hash = (hash << 5) - hash + char
              hash = hash & hash
            }
            return Math.abs(hash).toString(16).padStart(64, '0')
          },
        }
      },
    }
  },
  timingSafeEqual: (a: Buffer, b: Buffer) => {
    return a.toString() === b.toString()
  },
  randomBytes: (size: number) => {
    const bytes = new Uint8Array(size)
    if (typeof window !== 'undefined' && window.crypto) {
      window.crypto.getRandomValues(bytes)
    }
    return {
      toString: (encoding: string) => {
        return Array.from(bytes)
          .map((b) => b.toString(16).padStart(2, '0'))
          .join('')
      },
    }
  },
}

// Use polyfill if crypto is not available
if (typeof crypto === 'undefined') {
  ;(global as any).crypto = cryptoPolyfill
}
