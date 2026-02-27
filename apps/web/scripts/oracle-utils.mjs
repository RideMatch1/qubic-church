#!/usr/bin/env node
/**
 * ORACLE UTILS — Shared Foundation
 *
 * Centralized utilities for all Oracle Dominance scripts.
 * Extracted from ORACLE_INSCRIBE.mjs, ORACLE_QUERY_LIVE.mjs, ORACLE_TCP_CLIENT.mjs
 *
 * Exports:
 *   loadEnv, encodeQpiId, encodeDateAndTime, rpc,
 *   buildOracleQueryPayload, sendOracleQuery, sendInscription,
 *   getBalance, getCurrentTick, PAIR_REGISTRY, COST_PER_QUERY
 */

import { createRequire } from 'module'
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs'
import { resolve, dirname, join } from 'path'
import { fileURLToPath } from 'url'
import { createHash } from 'crypto'

const require = createRequire(import.meta.url)
const __dirname = dirname(fileURLToPath(import.meta.url))

// =============================================================================
// CONSTANTS
// =============================================================================

export const COST_PER_QUERY = 10
export const RPC_URL = 'https://rpc.qubic.org/v1'
export const RPC_ENDPOINTS = [
  'https://rpc.qubic.org/v1',
  'https://rpc.qubic.li/v1',
  'https://rpc.qubic.network/v1',
]

/**
 * Complete Oracle Pair Registry — 20 pairs across 7 exchanges, 3 tiers.
 */
export const PAIR_REGISTRY = [
  // Tier 1 — Core QUBIC (7 pairs, 70 QU)
  { tier: 1, oracle: 'binance',      currency1: 'qubic', currency2: 'usdt', label: 'QUBIC/USDT Binance' },
  { tier: 1, oracle: 'mexc0',        currency1: 'qubic', currency2: 'usdt', label: 'QUBIC/USDT MEXC' },
  { tier: 1, oracle: 'gate0',        currency1: 'qubic', currency2: 'usdt', label: 'QUBIC/USDT Gate' },
  { tier: 1, oracle: 'coingecko',    currency1: 'qubic', currency2: 'usd',  label: 'QUBIC/USD CoinGecko' },
  { tier: 1, oracle: 'binance_mexc', currency1: 'qubic', currency2: 'usdt', label: 'QUBIC/USDT Bin+MEXC' },
  { tier: 1, oracle: 'binance_gate', currency1: 'qubic', currency2: 'usdt', label: 'QUBIC/USDT Bin+Gate' },
  { tier: 1, oracle: 'gate_mexc',    currency1: 'qubic', currency2: 'usdt', label: 'QUBIC/USDT Gate+MEXC' },
  // Tier 2 — BTC/ETH Majors (6 pairs, 60 QU)
  { tier: 2, oracle: 'binance',      currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Binance' },
  { tier: 2, oracle: 'binance',      currency1: 'eth',   currency2: 'usdt', label: 'ETH/USDT Binance' },
  { tier: 2, oracle: 'mexc0',        currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT MEXC' },
  { tier: 2, oracle: 'gate0',        currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Gate' },
  { tier: 2, oracle: 'coingecko',    currency1: 'btc',   currency2: 'usd',  label: 'BTC/USD CoinGecko' },
  { tier: 2, oracle: 'coingecko',    currency1: 'eth',   currency2: 'usd',  label: 'ETH/USD CoinGecko' },
  // Tier 3 — Cross Pairs / Exploratory (7 pairs, 70 QU)
  { tier: 3, oracle: 'binance',      currency1: 'qubic', currency2: 'btc',  label: 'QUBIC/BTC Binance' },
  { tier: 3, oracle: 'mexc0',        currency1: 'qubic', currency2: 'btc',  label: 'QUBIC/BTC MEXC' },
  { tier: 3, oracle: 'binance',      currency1: 'eth',   currency2: 'btc',  label: 'ETH/BTC Binance' },
  { tier: 3, oracle: 'coingecko',    currency1: 'qubic', currency2: 'btc',  label: 'QUBIC/BTC CoinGecko' },
  { tier: 3, oracle: 'gate0',        currency1: 'eth',   currency2: 'usdt', label: 'ETH/USDT Gate' },
  { tier: 3, oracle: 'binance_mexc', currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Bin+MEXC' },
  { tier: 3, oracle: 'gate_mexc',    currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Gate+MEXC' },
]

/**
 * Working pairs — confirmed SUCCESS from explore + discovery runs (Epoch 200).
 * All of these return actual price data from the Oracle Machine.
 * Updated after discovery sweep: 28 working pairs across 5 oracle sources.
 */
export const WORKING_PAIRS = [
  // =====================================================================
  // binance (18 pairs) — richest oracle source
  // =====================================================================
  { oracle: 'binance',      currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Binance' },
  { oracle: 'binance',      currency1: 'eth',   currency2: 'usdt', label: 'ETH/USDT Binance' },
  { oracle: 'binance',      currency1: 'sol',   currency2: 'usdt', label: 'SOL/USDT Binance' },
  { oracle: 'binance',      currency1: 'xrp',   currency2: 'usdt', label: 'XRP/USDT Binance' },
  { oracle: 'binance',      currency1: 'bnb',   currency2: 'usdt', label: 'BNB/USDT Binance' },
  { oracle: 'binance',      currency1: 'doge',  currency2: 'usdt', label: 'DOGE/USDT Binance' },
  { oracle: 'binance',      currency1: 'ada',   currency2: 'usdt', label: 'ADA/USDT Binance' },
  { oracle: 'binance',      currency1: 'zro',   currency2: 'usdt', label: 'ZRO/USDT Binance' },
  { oracle: 'binance',      currency1: 'avax',  currency2: 'usdt', label: 'AVAX/USDT Binance' },
  { oracle: 'binance',      currency1: 'dot',   currency2: 'usdt', label: 'DOT/USDT Binance' },
  { oracle: 'binance',      currency1: 'link',  currency2: 'usdt', label: 'LINK/USDT Binance' },
  { oracle: 'binance',      currency1: 'atom',  currency2: 'usdt', label: 'ATOM/USDT Binance' },
  { oracle: 'binance',      currency1: 'ltc',   currency2: 'usdt', label: 'LTC/USDT Binance' },
  { oracle: 'binance',      currency1: 'trx',   currency2: 'usdt', label: 'TRX/USDT Binance' },
  { oracle: 'binance',      currency1: 'near',  currency2: 'usdt', label: 'NEAR/USDT Binance' },
  { oracle: 'binance',      currency1: 'sui',   currency2: 'usdt', label: 'SUI/USDT Binance' },
  { oracle: 'binance',      currency1: 'apt',   currency2: 'usdt', label: 'APT/USDT Binance' },
  { oracle: 'binance',      currency1: 'btc',   currency2: 'usd',  label: 'BTC/USD Binance' },
  // binance cross pairs
  { oracle: 'binance',      currency1: 'eth',   currency2: 'btc',  label: 'ETH/BTC Binance' },
  { oracle: 'binance',      currency1: 'sol',   currency2: 'btc',  label: 'SOL/BTC Binance' },
  { oracle: 'binance',      currency1: 'xrp',   currency2: 'btc',  label: 'XRP/BTC Binance' },

  // =====================================================================
  // mexc (12 pairs)
  // =====================================================================
  { oracle: 'mexc',         currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT MEXC' },
  { oracle: 'mexc',         currency1: 'eth',   currency2: 'usdt', label: 'ETH/USDT MEXC' },
  { oracle: 'mexc',         currency1: 'qubic', currency2: 'usdt', label: 'QUBIC/USDT MEXC' },
  { oracle: 'mexc',         currency1: 'sol',   currency2: 'usdt', label: 'SOL/USDT MEXC' },
  { oracle: 'mexc',         currency1: 'xrp',   currency2: 'usdt', label: 'XRP/USDT MEXC' },
  { oracle: 'mexc',         currency1: 'bnb',   currency2: 'usdt', label: 'BNB/USDT MEXC' },
  { oracle: 'mexc',         currency1: 'doge',  currency2: 'usdt', label: 'DOGE/USDT MEXC' },
  { oracle: 'mexc',         currency1: 'zro',   currency2: 'usdt', label: 'ZRO/USDT MEXC' },
  { oracle: 'mexc',         currency1: 'avax',  currency2: 'usdt', label: 'AVAX/USDT MEXC' },
  { oracle: 'mexc',         currency1: 'ada',   currency2: 'usdt', label: 'ADA/USDT MEXC' },
  { oracle: 'mexc',         currency1: 'link',  currency2: 'usdt', label: 'LINK/USDT MEXC' },
  { oracle: 'mexc',         currency1: 'sui',   currency2: 'usdt', label: 'SUI/USDT MEXC' },
  // mexc cross pairs
  { oracle: 'mexc',         currency1: 'eth',   currency2: 'btc',  label: 'ETH/BTC MEXC' },

  // =====================================================================
  // gate (7 pairs)
  // =====================================================================
  { oracle: 'gate',         currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Gate' },
  { oracle: 'gate',         currency1: 'eth',   currency2: 'usdt', label: 'ETH/USDT Gate' },
  { oracle: 'gate',         currency1: 'qubic', currency2: 'usdt', label: 'QUBIC/USDT Gate' },
  { oracle: 'gate',         currency1: 'sol',   currency2: 'usdt', label: 'SOL/USDT Gate' },
  { oracle: 'gate',         currency1: 'xrp',   currency2: 'usdt', label: 'XRP/USDT Gate' },
  { oracle: 'gate',         currency1: 'doge',  currency2: 'usdt', label: 'DOGE/USDT Gate' },
  { oracle: 'gate',         currency1: 'bnb',   currency2: 'usdt', label: 'BNB/USDT Gate' },
  // gate cross pairs
  { oracle: 'gate',         currency1: 'eth',   currency2: 'btc',  label: 'ETH/BTC Gate' },

  // =====================================================================
  // gate_mexc (8 pairs)
  // =====================================================================
  { oracle: 'gate_mexc',    currency1: 'qubic', currency2: 'usdt', label: 'QUBIC/USDT Gate+MEXC' },
  { oracle: 'gate_mexc',    currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Gate+MEXC' },
  { oracle: 'gate_mexc',    currency1: 'eth',   currency2: 'usdt', label: 'ETH/USDT Gate+MEXC' },
  { oracle: 'gate_mexc',    currency1: 'sol',   currency2: 'usdt', label: 'SOL/USDT Gate+MEXC' },
  { oracle: 'gate_mexc',    currency1: 'xrp',   currency2: 'usdt', label: 'XRP/USDT Gate+MEXC' },
  { oracle: 'gate_mexc',    currency1: 'doge',  currency2: 'usdt', label: 'DOGE/USDT Gate+MEXC' },
  { oracle: 'gate_mexc',    currency1: 'bnb',   currency2: 'usdt', label: 'BNB/USDT Gate+MEXC' },
  { oracle: 'gate_mexc',    currency1: 'ada',   currency2: 'usdt', label: 'ADA/USDT Gate+MEXC' },

  // =====================================================================
  // binance_mexc (3 pairs) + binance_gate (3 pairs)
  // =====================================================================
  { oracle: 'binance_mexc', currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Bin+MEXC' },
  { oracle: 'binance_mexc', currency1: 'eth',   currency2: 'usdt', label: 'ETH/USDT Bin+MEXC' },
  { oracle: 'binance_mexc', currency1: 'sol',   currency2: 'usdt', label: 'SOL/USDT Bin+MEXC' },
  { oracle: 'binance_gate', currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Bin+Gate' },
  { oracle: 'binance_gate', currency1: 'eth',   currency2: 'usdt', label: 'ETH/USDT Bin+Gate' },
  { oracle: 'binance_gate', currency1: 'sol',   currency2: 'usdt', label: 'SOL/USDT Bin+Gate' },
]

/**
 * Discovery pairs — untested combinations to explore.
 * Includes "mexc" (without 0) which was seen working for ZRO/USDT,
 * plus altcoins and alternative oracle names.
 */
/**
 * Phase 1 discovery pairs — ALL CONFIRMED WORKING (22/22 SUCCESS, Epoch 200).
 * These have been moved to WORKING_PAIRS.
 * Kept here for reference only.
 */
export const DISCOVERY_PHASE1_DONE = true

/**
 * Phase 2 discovery pairs — New oracle names + new assets + new quote currencies.
 * Testing: kraken, bybit, htx, kucoin, okx, coinbase, upbit, bitfinex
 * Plus: avax, dot, link, matic, atom, ltc, trx, near, sui, apt
 * Plus: usd vs usdt, btc pairs on new oracles
 */
export const DISCOVERY_PAIRS = [
  // --- NEW ORACLE NAMES (BTC as canary — if btc/usdt works, try more) ---
  { oracle: 'kraken',    currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Kraken' },
  { oracle: 'bybit',     currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Bybit' },
  { oracle: 'htx',       currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT HTX' },
  { oracle: 'kucoin',    currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT KuCoin' },
  { oracle: 'okx',       currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT OKX' },
  { oracle: 'coinbase',  currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Coinbase' },
  { oracle: 'upbit',     currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Upbit' },
  { oracle: 'bitfinex',  currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Bitfinex' },
  { oracle: 'bitget',    currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Bitget' },
  // --- NEW ORACLE NAME VARIANTS (0-suffix like mexc0/gate0) ---
  { oracle: 'binance0',  currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Binance0' },
  { oracle: 'kraken0',   currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Kraken0' },
  { oracle: 'bybit0',    currency1: 'btc',   currency2: 'usdt', label: 'BTC/USDT Bybit0' },
  // --- NEW ASSETS on known-working oracles ---
  { oracle: 'binance',   currency1: 'avax',  currency2: 'usdt', label: 'AVAX/USDT Binance' },
  { oracle: 'binance',   currency1: 'dot',   currency2: 'usdt', label: 'DOT/USDT Binance' },
  { oracle: 'binance',   currency1: 'link',  currency2: 'usdt', label: 'LINK/USDT Binance' },
  { oracle: 'binance',   currency1: 'matic', currency2: 'usdt', label: 'MATIC/USDT Binance' },
  { oracle: 'binance',   currency1: 'atom',  currency2: 'usdt', label: 'ATOM/USDT Binance' },
  { oracle: 'binance',   currency1: 'ltc',   currency2: 'usdt', label: 'LTC/USDT Binance' },
  { oracle: 'binance',   currency1: 'trx',   currency2: 'usdt', label: 'TRX/USDT Binance' },
  { oracle: 'binance',   currency1: 'near',  currency2: 'usdt', label: 'NEAR/USDT Binance' },
  { oracle: 'binance',   currency1: 'sui',   currency2: 'usdt', label: 'SUI/USDT Binance' },
  { oracle: 'binance',   currency1: 'apt',   currency2: 'usdt', label: 'APT/USDT Binance' },
  // --- USD vs USDT (CoinGecko uses usd, test others) ---
  { oracle: 'binance',   currency1: 'btc',   currency2: 'usd',  label: 'BTC/USD Binance' },
  { oracle: 'mexc',      currency1: 'btc',   currency2: 'usd',  label: 'BTC/USD MEXC' },
  { oracle: 'coingecko', currency1: 'sol',   currency2: 'usd',  label: 'SOL/USD CoinGecko' },
  { oracle: 'coingecko', currency1: 'xrp',   currency2: 'usd',  label: 'XRP/USD CoinGecko' },
  { oracle: 'coingecko', currency1: 'doge',  currency2: 'usd',  label: 'DOGE/USD CoinGecko' },
  { oracle: 'coingecko', currency1: 'ada',   currency2: 'usd',  label: 'ADA/USD CoinGecko' },
  { oracle: 'coingecko', currency1: 'avax',  currency2: 'usd',  label: 'AVAX/USD CoinGecko' },
  // --- COMBINED ORACLE NAMES (new combos) ---
  { oracle: 'binance_mexc', currency1: 'eth',   currency2: 'usdt', label: 'ETH/USDT Bin+MEXC' },
  { oracle: 'binance_mexc', currency1: 'sol',   currency2: 'usdt', label: 'SOL/USDT Bin+MEXC' },
  { oracle: 'binance_mexc', currency1: 'qubic', currency2: 'usdt', label: 'QUBIC/USDT Bin+MEXC' },
  { oracle: 'binance_gate', currency1: 'sol',   currency2: 'usdt', label: 'SOL/USDT Bin+Gate' },
  { oracle: 'binance_gate', currency1: 'qubic', currency2: 'usdt', label: 'QUBIC/USDT Bin+Gate' },
  { oracle: 'gate_mexc',    currency1: 'doge',  currency2: 'usdt', label: 'DOGE/USDT Gate+MEXC' },
  { oracle: 'gate_mexc',    currency1: 'bnb',   currency2: 'usdt', label: 'BNB/USDT Gate+MEXC' },
  { oracle: 'gate_mexc',    currency1: 'ada',   currency2: 'usdt', label: 'ADA/USDT Gate+MEXC' },
  // --- NEW ALTCOINS on mexc/gate ---
  { oracle: 'mexc',      currency1: 'avax',  currency2: 'usdt', label: 'AVAX/USDT MEXC' },
  { oracle: 'mexc',      currency1: 'ada',   currency2: 'usdt', label: 'ADA/USDT MEXC' },
  { oracle: 'mexc',      currency1: 'link',  currency2: 'usdt', label: 'LINK/USDT MEXC' },
  { oracle: 'mexc',      currency1: 'sui',   currency2: 'usdt', label: 'SUI/USDT MEXC' },
  { oracle: 'gate',      currency1: 'sol',   currency2: 'usdt', label: 'SOL/USDT Gate' },
  { oracle: 'gate',      currency1: 'doge',  currency2: 'usdt', label: 'DOGE/USDT Gate' },
  { oracle: 'gate',      currency1: 'xrp',   currency2: 'usdt', label: 'XRP/USDT Gate' },
  { oracle: 'gate',      currency1: 'bnb',   currency2: 'usdt', label: 'BNB/USDT Gate' },
  // --- BTC CROSS PAIRS ---
  { oracle: 'mexc',      currency1: 'eth',   currency2: 'btc',  label: 'ETH/BTC MEXC' },
  { oracle: 'gate',      currency1: 'eth',   currency2: 'btc',  label: 'ETH/BTC Gate' },
  { oracle: 'binance',   currency1: 'sol',   currency2: 'btc',  label: 'SOL/BTC Binance' },
  { oracle: 'binance',   currency1: 'xrp',   currency2: 'btc',  label: 'XRP/BTC Binance' },
]

// =============================================================================
// ENV LOADING
// =============================================================================

/**
 * Load .env from project root. Sets process.env values.
 */
export function loadEnv() {
  const envPath = resolve(__dirname, '../../../.env')
  try {
    const envContent = readFileSync(envPath, 'utf-8')
    for (const line of envContent.split('\n')) {
      const match = line.match(/^([^#=]+)=(.*)$/)
      if (match) process.env[match[1].trim()] = match[2].trim()
    }
  } catch (e) {
    console.error('Could not read .env:', e.message)
    process.exit(1)
  }

  if (!process.env.MASTER_SEED) {
    console.error('ERROR: MASTER_SEED not set in .env')
    process.exit(1)
  }
}

// =============================================================================
// ENCODING (proven working from ORACLE_INSCRIBE.mjs + ORACLE_QUERY_LIVE.mjs)
// =============================================================================

/**
 * Encode a string as a QPI `id` (m256i = 32 bytes).
 * Each character stored as ASCII, zero-padded to 32 bytes.
 */
export function encodeQpiId(str) {
  const buf = Buffer.alloc(32, 0)
  const lower = str.toLowerCase()
  for (let i = 0; i < Math.min(lower.length, 31); i++) {
    buf[i] = lower.charCodeAt(i)
  }
  return buf
}

/**
 * Encode a DateAndTime as packed uint64 bitfield (8 bytes).
 * Supports both Date objects and explicit {year,month,day,hour,minute,second} objects.
 */
export function encodeDateAndTime(dateOrObj = null) {
  const buf = Buffer.alloc(8, 0)
  if (!dateOrObj) return buf

  let year, month, day, hour, minute, second, ms
  if (dateOrObj instanceof Date) {
    year = dateOrObj.getUTCFullYear()
    month = dateOrObj.getUTCMonth() + 1
    day = dateOrObj.getUTCDate()
    hour = dateOrObj.getUTCHours()
    minute = dateOrObj.getUTCMinutes()
    second = dateOrObj.getUTCSeconds()
    ms = dateOrObj.getUTCMilliseconds()
  } else {
    year = dateOrObj.year ?? 0
    month = dateOrObj.month ?? 0
    day = dateOrObj.day ?? 0
    hour = dateOrObj.hour ?? 0
    minute = dateOrObj.minute ?? 0
    second = dateOrObj.second ?? 0
    ms = dateOrObj.ms ?? 0
  }

  const value = (BigInt(year) << 46n) | (BigInt(month) << 42n) | (BigInt(day) << 37n)
              | (BigInt(hour) << 32n) | (BigInt(minute) << 26n) | (BigInt(second) << 20n)
              | (BigInt(ms) << 10n)
  buf.writeBigUInt64LE(value, 0)
  return buf
}

// =============================================================================
// RPC
// =============================================================================

let _currentRpcIdx = 0

/**
 * Make an RPC call with endpoint fallback.
 */
export async function rpc(endpoint, options = {}) {
  const errors = []
  for (let i = 0; i < RPC_ENDPOINTS.length; i++) {
    const baseUrl = RPC_ENDPOINTS[(_currentRpcIdx + i) % RPC_ENDPOINTS.length]
    try {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 10000)
      const res = await fetch(`${baseUrl}${endpoint}`, {
        ...options,
        headers: { 'Content-Type': 'application/json', ...options?.headers },
        signal: controller.signal,
      })
      clearTimeout(timeout)
      if (!res.ok) throw new Error(`RPC ${res.status}: ${res.statusText}`)
      _currentRpcIdx = (_currentRpcIdx + i) % RPC_ENDPOINTS.length
      return res.json()
    } catch (e) {
      errors.push(`${baseUrl}: ${e.message}`)
    }
  }
  throw new Error(`All RPC endpoints failed: ${errors.join('; ')}`)
}

// =============================================================================
// BALANCE & TICK
// =============================================================================

/**
 * Get balance for an address (defaults to MASTER_IDENTITY).
 */
export async function getBalance(address) {
  const addr = address || process.env.MASTER_IDENTITY
  if (!addr) throw new Error('No address provided and MASTER_IDENTITY not set')
  const data = await rpc(`/balances/${addr}`)
  return Number(data.balance?.balance ?? 0)
}

/**
 * Get current tick and epoch from the network.
 */
export async function getCurrentTick() {
  const data = await rpc('/tick-info')
  return {
    tick: data.tickInfo?.tick ?? data.tick,
    epoch: data.tickInfo?.epoch ?? data.epoch,
  }
}

// =============================================================================
// ORACLE QUERY PAYLOAD (from ORACLE_QUERY_LIVE.mjs)
// =============================================================================

/**
 * Build a 112-byte oracle query payload.
 * [4B interfaceIndex=0][4B timeout_ms=60000][32B oracle][8B timestamp][32B curr1][32B curr2]
 */
export function buildOracleQueryPayload(oracle, currency1, currency2, timestamp = null) {
  const oracleId = encodeQpiId(oracle)
  const ts = timestamp ? encodeDateAndTime(timestamp) : encodeDateAndTime(new Date())
  const curr1 = encodeQpiId(currency1)
  const curr2 = encodeQpiId(currency2)

  const queryData = Buffer.concat([oracleId, ts, curr1, curr2]) // 104 bytes

  const interfaceIndex = Buffer.alloc(4, 0)
  interfaceIndex.writeUInt32LE(0, 0) // Price = interface 0

  const timeoutMs = Buffer.alloc(4, 0)
  timeoutMs.writeUInt32LE(60000, 0) // 60 seconds

  return Buffer.concat([interfaceIndex, timeoutMs, queryData]) // 112 bytes
}

// =============================================================================
// TRANSACTION SENDING (from ORACLE_QUERY_LIVE.mjs + ORACLE_INSCRIBE.mjs)
// =============================================================================

let _qubicLib = null

function getQubicLib() {
  if (!_qubicLib) {
    _qubicLib = require('@qubic-lib/qubic-ts-library').default
  }
  return _qubicLib
}

/**
 * Send an oracle price query as a transaction.
 * Returns { success, txId, targetTick, error? }
 */
export async function sendOracleQuery(oracle, currency1, currency2, targetTick) {
  const txInput = buildOracleQueryPayload(oracle, currency1, currency2)
  return broadcastOracleTx(txInput, targetTick)
}

/**
 * Send a custom inscription (like the Seven Seals) as an oracle transaction.
 * inscription = { oracle, timestamp: {year,month,day,...}, currency1, currency2 }
 */
export async function sendInscription(inscription, targetTick) {
  const oracleId = encodeQpiId(inscription.oracle)
  const ts = encodeDateAndTime(inscription.timestamp)
  const curr1 = encodeQpiId(inscription.currency1)
  const curr2 = encodeQpiId(inscription.currency2)
  const queryData = Buffer.concat([oracleId, ts, curr1, curr2])

  const interfaceIndex = Buffer.alloc(4, 0)
  interfaceIndex.writeUInt32LE(0, 0)
  const timeoutMs = Buffer.alloc(4, 0)
  timeoutMs.writeUInt32LE(60000, 0)

  const txInput = Buffer.concat([interfaceIndex, timeoutMs, queryData])
  return broadcastOracleTx(txInput, targetTick)
}

/**
 * Internal: build, sign, and broadcast an oracle transaction.
 */
async function broadcastOracleTx(txInput, targetTick) {
  const { QubicHelper, QubicTransaction, DynamicPayload, PublicKey } = getQubicLib()

  const helper = new QubicHelper()
  const idPackage = await helper.createIdPackage(process.env.MASTER_SEED)

  const tx = new QubicTransaction()
    .setSourcePublicKey(new PublicKey(idPackage.publicKey))
    .setDestinationPublicKey(new PublicKey(new Uint8Array(32)))
    .setAmount(COST_PER_QUERY)
    .setTick(targetTick)
    .setInputType(10)
    .setInputSize(txInput.length)

  const payload = new DynamicPayload(txInput.length)
  payload.setPayload(new Uint8Array(txInput))
  tx.setPayload(payload)

  const txBytes = await tx.build(process.env.MASTER_SEED)
  const encodedTx = tx.encodeTransactionToBase64(txBytes)

  const result = await rpc('/broadcast-transaction', {
    method: 'POST',
    body: JSON.stringify({ encodedTransaction: encodedTx }),
  })

  return {
    success: true,
    txId: result.transactionId ?? result.peersBroadcasted ?? 'broadcast_ok',
    peersBroadcasted: result.peersBroadcasted ?? 0,
    targetTick,
    txSize: txBytes.length,
  }
}

// =============================================================================
// JSON STORAGE HELPERS
// =============================================================================

const DATA_DIR = resolve(__dirname, '../public/data')

/**
 * Ensure data directory exists.
 */
export function ensureDataDir() {
  if (!existsSync(DATA_DIR)) {
    mkdirSync(DATA_DIR, { recursive: true })
  }
}

/**
 * Read a JSON file from public/data. Returns null if not found.
 */
export function readDataFile(filename) {
  const filePath = join(DATA_DIR, filename)
  try {
    return JSON.parse(readFileSync(filePath, 'utf-8'))
  } catch {
    return null
  }
}

/**
 * Write a JSON file to public/data.
 */
export function writeDataFile(filename, data) {
  ensureDataDir()
  const filePath = join(DATA_DIR, filename)
  writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8')
}

/**
 * Append an entry to a rolling JSON array file (FIFO, max entries).
 */
export function appendToRollingFile(filename, entry, maxEntries = 500) {
  ensureDataDir()
  const existing = readDataFile(filename) ?? []
  const arr = Array.isArray(existing) ? existing : []
  arr.push(entry)
  while (arr.length > maxEntries) arr.shift()
  writeDataFile(filename, arr)
  return arr
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * SHA256 hash of a string (hex).
 */
export function sha256(str) {
  return createHash('sha256').update(str).digest('hex')
}

/**
 * Sleep for ms milliseconds.
 */
export function sleep(ms) {
  return new Promise(r => setTimeout(r, ms))
}

/**
 * Get pairs filtered by tier(s).
 * @param {number|number[]|'all'} tiers - 1, 2, 3, [1,2], or 'all'
 */
export function getPairsByTier(tiers) {
  if (tiers === 'all') return [...PAIR_REGISTRY]
  const tierArr = Array.isArray(tiers) ? tiers : [tiers]
  return PAIR_REGISTRY.filter(p => tierArr.includes(p.tier))
}

/**
 * Estimate cost for given tiers.
 */
export function estimateCost(tiers) {
  const pairs = getPairsByTier(tiers)
  const byTier = {}
  for (const p of pairs) {
    byTier[p.tier] = (byTier[p.tier] || 0) + 1
  }
  return {
    pairCount: pairs.length,
    costQU: pairs.length * COST_PER_QUERY,
    byTier,
    pairs: pairs.map(p => `${p.oracle} ${p.currency1}/${p.currency2}`),
  }
}

/**
 * Format a number with locale separators.
 */
export function fmt(n) {
  return Number(n).toLocaleString()
}

/**
 * Print a boxed header.
 */
export function printHeader(title, subtitle) {
  const w = 65
  const pad = (s, len) => s + ' '.repeat(Math.max(0, len - s.length))
  console.log()
  console.log(`  ${'='.repeat(w)}`)
  console.log(`  ${pad(title, w)}`)
  if (subtitle) console.log(`  ${pad(subtitle, w)}`)
  console.log(`  ${'='.repeat(w)}`)
  console.log()
}
