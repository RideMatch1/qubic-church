/**
 * QPredict Alert/Webhook System
 *
 * Sends notifications for critical system events via Discord/Slack webhooks.
 * Always logs via pino regardless of webhook configuration.
 *
 * Configuration:
 *   ALERT_WEBHOOK_URL  — Discord or Slack webhook URL (optional)
 *   ALERT_WEBHOOK_TYPE — "discord" (default) or "slack"
 */

import { cronLog } from './logger'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type AlertType =
  | 'circuit_open'
  | 'circuit_closed'
  | 'sweep_failure'
  | 'joinbet_max_retries'
  | 'cron_error'
  | 'escrow_stale'
  | 'backup_failure'
  | 'key_vault_error'
  | 'health_degraded'
  | 'system_shutdown'

export type AlertLevel = 'info' | 'warning' | 'error' | 'critical'

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const WEBHOOK_URL = process.env.ALERT_WEBHOOK_URL || ''
const WEBHOOK_TYPE = (process.env.ALERT_WEBHOOK_TYPE || 'discord') as 'discord' | 'slack'
const FETCH_TIMEOUT_MS = 5_000
const RATE_LIMIT_MS = 5 * 60 * 1000 // 5 minutes per alert type

// ---------------------------------------------------------------------------
// Rate Limiting (per alert type)
// ---------------------------------------------------------------------------

const lastAlertTimes = new Map<AlertType, number>()

function isRateLimited(type: AlertType): boolean {
  const lastTime = lastAlertTimes.get(type)
  if (!lastTime) return false
  return Date.now() - lastTime < RATE_LIMIT_MS
}

function recordAlert(type: AlertType): void {
  lastAlertTimes.set(type, Date.now())
}

// ---------------------------------------------------------------------------
// Color mapping for Discord embeds
// ---------------------------------------------------------------------------

const LEVEL_COLORS: Record<AlertLevel, number> = {
  info: 0x3498db,     // blue
  warning: 0xf39c12,  // orange
  error: 0xe74c3c,    // red
  critical: 0x8b0000, // dark red
}

const LEVEL_EMOJI: Record<AlertLevel, string> = {
  info: 'ℹ️',
  warning: '⚠️',
  error: '🔴',
  critical: '🚨',
}

// ---------------------------------------------------------------------------
// Core Alert Function
// ---------------------------------------------------------------------------

/**
 * Send an alert notification.
 *
 * 1. Always logs via pino.
 * 2. If ALERT_WEBHOOK_URL is configured, sends to Discord/Slack.
 * 3. Rate-limited per alert type (max 1 webhook per type per 5 min).
 * 4. Fire-and-forget — never throws.
 */
export async function sendAlert(
  type: AlertType,
  level: AlertLevel,
  message: string,
  metadata?: Record<string, unknown>,
): Promise<void> {
  // Always log
  const logData = { alertType: type, alertLevel: level, ...metadata }

  switch (level) {
    case 'critical':
    case 'error':
      cronLog.error(logData, `ALERT [${type}]: ${message}`)
      break
    case 'warning':
      cronLog.warn(logData, `ALERT [${type}]: ${message}`)
      break
    default:
      cronLog.info(logData, `ALERT [${type}]: ${message}`)
  }

  // Skip webhook if not configured
  if (!WEBHOOK_URL) return

  // Rate limit per type
  if (isRateLimited(type)) return
  recordAlert(type)

  // Send webhook (fire-and-forget)
  try {
    const body = WEBHOOK_TYPE === 'slack'
      ? buildSlackPayload(type, level, message, metadata)
      : buildDiscordPayload(type, level, message, metadata)

    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS)

    await fetch(WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    })

    clearTimeout(timeout)
  } catch {
    // Fire-and-forget — log failure but don't propagate
    cronLog.warn({ alertType: type }, 'failed to send webhook alert')
  }
}

// ---------------------------------------------------------------------------
// Payload Builders
// ---------------------------------------------------------------------------

function buildDiscordPayload(
  type: AlertType,
  level: AlertLevel,
  message: string,
  metadata?: Record<string, unknown>,
) {
  const fields = metadata
    ? Object.entries(metadata)
        .filter(([, v]) => v !== undefined)
        .slice(0, 10)
        .map(([k, v]) => ({
          name: k,
          value: String(v).slice(0, 256),
          inline: true,
        }))
    : []

  return {
    embeds: [
      {
        title: `${LEVEL_EMOJI[level]} QPredict: ${type}`,
        description: message.slice(0, 2048),
        color: LEVEL_COLORS[level],
        fields: [
          { name: 'Level', value: level, inline: true },
          { name: 'Type', value: type, inline: true },
          ...fields,
        ],
        timestamp: new Date().toISOString(),
        footer: { text: 'QPredict Alert System' },
      },
    ],
  }
}

function buildSlackPayload(
  type: AlertType,
  level: AlertLevel,
  message: string,
  metadata?: Record<string, unknown>,
) {
  const metaStr = metadata
    ? '\n' +
      Object.entries(metadata)
        .filter(([, v]) => v !== undefined)
        .map(([k, v]) => `*${k}*: ${String(v).slice(0, 256)}`)
        .join('\n')
    : ''

  return {
    text: `${LEVEL_EMOJI[level]} *QPredict Alert: ${type}*\n${message}${metaStr}`,
  }
}
