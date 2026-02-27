/**
 * API Utilities — Shared helpers for QPredict API routes
 *
 * Provides consistent error handling and input validation across all endpoints.
 */

import crypto from 'crypto'
import { NextResponse } from 'next/server'
import logger from './logger'

const IS_PRODUCTION = process.env.NODE_ENV === 'production'

/**
 * Create a safe error response that never leaks internal details in production.
 * In development, the full error message is included for debugging.
 * A correlation ID is always returned so users can reference support tickets.
 */
export function safeErrorResponse(
  error: unknown,
  fallbackMessage: string,
  status: number = 500,
): NextResponse {
  const correlationId = crypto.randomBytes(8).toString('hex')

  // Always log the full error server-side
  logger.error({ correlationId, err: error }, 'API error')

  const message = IS_PRODUCTION
    ? fallbackMessage
    : error instanceof Error
      ? error.message
      : fallbackMessage

  return NextResponse.json(
    {
      error: message,
      correlationId,
    },
    { status },
  )
}

/**
 * Validate a Qubic address (60 uppercase letters).
 * Returns an error message if invalid, null if valid.
 */
export function validateQubicAddress(address: string): string | null {
  if (!address) return 'Address is required'
  if (address.length !== 60) return 'Address must be exactly 60 characters'
  if (!/^[A-Z]+$/.test(address)) return 'Address must contain only uppercase letters'
  return null
}

/**
 * Validate numeric input within bounds.
 */
export function validateNumericBound(
  value: number | undefined | null,
  name: string,
  min: number,
  max: number,
): string | null {
  if (value === undefined || value === null) return `${name} is required`
  if (typeof value !== 'number' || isNaN(value)) return `${name} must be a number`
  if (value < min || value > max) return `${name} must be between ${min} and ${max}`
  return null
}

/**
 * Validate string length.
 */
export function validateStringLength(
  value: string | undefined | null,
  name: string,
  minLen: number,
  maxLen: number,
): string | null {
  if (!value) return `${name} is required`
  if (value.length < minLen) return `${name} must be at least ${minLen} characters`
  if (value.length > maxLen) return `${name} must be at most ${maxLen} characters`
  return null
}

/**
 * Parse a timestamp from SQLite as UTC.
 *
 * SQLite's `datetime('now')` produces strings like `2026-02-13 21:07:28`
 * which are UTC but lack a timezone indicator. JavaScript's `new Date()`
 * parses such strings as **local time**, creating a phantom offset equal
 * to the machine's UTC offset (e.g. +60 min on CET).
 *
 * This function normalises the timestamp to ISO 8601 with a 'Z' suffix
 * so it is always interpreted as UTC.
 */
export function parseUtcTimestamp(ts: string): Date {
  let s = ts
  if (!/[Z]$/i.test(s) && !/[+-]\d{2}(:\d{2})?$/.test(s)) {
    s = s.replace(' ', 'T') + 'Z'
  }
  return new Date(s)
}
