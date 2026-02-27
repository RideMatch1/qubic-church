/**
 * QFlash Configuration
 *
 * Central configuration for the ultra-fast binary prediction system.
 * All durations, limits, and operational parameters in one place.
 */

import type { RoundDuration } from './types'

// ---------------------------------------------------------------------------
// Core Config
// ---------------------------------------------------------------------------

export const QFLASH_CONFIG = {
  /** Available round durations in seconds */
  durations: [30, 60, 120] as RoundDuration[],

  /** Default trading pairs enabled at launch */
  defaultPairs: ['btc/usdt', 'eth/usdt', 'sol/usdt'] as const,

  /** Minimum bet amount in QU */
  minBetQu: 10_000,

  /** Maximum bet amount in QU */
  maxBetQu: 10_000_000,

  /** Platform fee in basis points (taken from loser pool) */
  platformFeeBps: 300, // 3%

  /** Seconds before close to lock betting */
  lockBeforeCloseSecs: 5,

  /** Background cron cycle interval in ms */
  cronIntervalMs: 5_000,

  /** Price cache TTL in ms (faster than QPredict's 15s) */
  priceCacheTtlMs: 5_000,

  /** Minimum oracle sources required for price resolution */
  minOracleSources: 2,

  /** Maximum allowed delay before round is cancelled */
  maxResolutionDelayMs: 120_000,

  /** How far ahead to pre-create upcoming rounds (seconds) */
  roundPipelineAheadSecs: 90,

  /** Maximum entries per round (safety cap) */
  maxEntriesPerRound: 10_000,

  /** Maximum entries per user per round */
  maxEntriesPerUserPerRound: 1,

  /** Rate limit: max bets per minute per address */
  maxBetsPerMinute: 10,

  /** Archive resolved rounds older than this (ms) */
  archiveAfterMs: 24 * 60 * 60 * 1000, // 24 hours

  /** Minimum pool size for a round to resolve (otherwise cancel) */
  minPoolForResolution: 0, // 0 = even 1 bet is fine (they get refunded if one-sided)

  /** House bank configuration */
  house: {
    /** Whether the house bank is enabled */
    enabled: true,
    /** Maximum house exposure per round in QU */
    maxExposurePerRoundQu: 5_000_000,
    /** Maximum total house exposure across all open rounds in QU */
    maxTotalExposureQu: 50_000_000,
    /** Ratio of user bet to match (1.0 = match 100%) */
    matchRatio: 1.0,
    /** Internal address for house account */
    houseAddress: 'HOUSE_INTERNAL',
    /** Initial house balance (from env or default) */
    initialBalanceQu: 10_000_000,
  },
} as const

// ---------------------------------------------------------------------------
// Derived helpers
// ---------------------------------------------------------------------------

/** All enabled pairs */
export function getEnabledPairs(): string[] {
  const envPairs = process.env.QFLASH_PAIRS
  if (envPairs) {
    return envPairs.split(',').map((p) => p.trim().toLowerCase())
  }
  return [...QFLASH_CONFIG.defaultPairs]
}

/** All enabled durations */
export function getEnabledDurations(): RoundDuration[] {
  const envDurations = process.env.QFLASH_DURATIONS
  if (envDurations) {
    return envDurations
      .split(',')
      .map((d) => Number(d.trim()) as RoundDuration)
      .filter((d) => [30, 60, 120].includes(d))
  }
  return [...QFLASH_CONFIG.durations]
}

/** Human-readable pair label */
export function pairLabel(pair: string): string {
  return pair.replace('/', '/').toUpperCase()
}

/** Human-readable duration label */
export function durationLabel(secs: RoundDuration): string {
  if (secs < 60) return `${secs}s`
  return `${secs / 60}m`
}

/** Check if house bank is enabled via env override or config default */
export function isHouseEnabled(): boolean {
  const env = process.env.QFLASH_HOUSE_ENABLED
  if (env !== undefined) return env === 'true'
  return QFLASH_CONFIG.house.enabled
}

/** Get initial house balance from env or config */
export function getHouseInitialBalance(): number {
  const env = process.env.QFLASH_HOUSE_INITIAL_BALANCE_QU
  if (env) return Number(env)
  return QFLASH_CONFIG.house.initialBalanceQu
}

/** Get HMAC secret key for attestations */
export function getQFlashAttestationKey(): string {
  return process.env.QFLASH_ATTESTATION_KEY ?? process.env.ATTESTATION_SECRET_KEY ?? 'dev-qflash-key-not-for-production'
}
