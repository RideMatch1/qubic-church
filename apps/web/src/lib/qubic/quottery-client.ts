/**
 * Quottery Smart Contract Client
 *
 * Transaction builder and query interface for Qubic's Quottery SC (Index 2).
 * Quottery is a P2P betting contract with pooled funds, oracle-based resolution,
 * and automated payouts.
 *
 * Used by QPredict prediction market as the settlement layer.
 *
 * SC Procedures:
 *   1 = issueBet    — Create a new bet/market
 *   2 = joinBet     — Place a bet on an option
 *   3 = cancelBet   — Cancel a bet (creator only, before end)
 *   4 = publishResult — Oracle resolves the outcome
 *
 * SC Functions (read-only, verified against official Quottery frontend):
 *   1 = getNodeInfo      — SC global config (fees, limits)
 *   2 = getBetInfo        — Bet details by ID
 *   3 = getBetByCreator   — Bets created by a given address
 *   4 = getActiveBet      — All active bet IDs
 */

import { QUBIC_RPC_ENDPOINTS, API_CONFIG } from '@/config/api'
import { rpcBreaker, CircuitOpenError } from '@/lib/predict/circuit-breaker'
import { rpcLog } from '@/lib/predict/logger'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Quottery is contract index 2 on Qubic mainnet */
export const QUOTTERY_CONTRACT_INDEX = 2

/**
 * SC public key: for contract index N, the 32-byte key is [N, 0, 0, ..., 0].
 * Address: CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACNKL
 */
function getQuotteryPublicKeyBytes(): Uint8Array {
  const key = new Uint8Array(32)
  key[0] = QUOTTERY_CONTRACT_INDEX
  return key
}

/** Procedure indices within the Quottery SC */
export const PROCEDURES = {
  issueBet: 1,
  joinBet: 2,
  cancelBet: 3,
  publishResult: 4,
} as const

/** Read-only function indices (verified against official Quottery frontend) */
export const FUNCTIONS = {
  getNodeInfo: 1,
  getBetInfo: 2,
  getBetByCreator: 3,
  getActiveBet: 4,
} as const

/** Binary payload sizes for each procedure */
const INPUT_SIZES = {
  issueBet: 600, // 32 + 256 + 256 + 32 + 4 + 4 + 8 + 4 + 4 = 600
  joinBet: 12,
  cancelBet: 4,
  publishResult: 8,
} as const

/** Quottery fee structure (from Quottery.h) */
export const QUOTTERY_FEES = {
  /** 2% of pool burned (mandatory, hardcoded in SC) */
  burnPercent: 2,
  /** 10% of pool to shareholders (hardcoded) */
  shareholderPercent: 10,
  /** 0.5% of pool to game operator / bet creator */
  gameOperatorPercent: 0.5,
  /** Minimum bet per slot: 10,000 QU */
  minAmountPerSlot: 10_000n,
  /** Max options per bet */
  maxOptions: 8,
  /** Max concurrent bets */
  maxActiveBets: 1024,
  /** Max bettors per option */
  maxBetSlotPerOption: 2048,
} as const

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface IssueBetParams {
  /** Short description (max 31 chars, will be encoded to 32-byte id) */
  betDesc: string
  /** Option labels (2-8 items, each max 31 chars) */
  options: string[]
  /** Oracle provider Qubic addresses (60-char uppercase, 1-8 providers) */
  oracleProviderIds: string[]
  /** Oracle provider raw 32-byte public keys (resolved from addresses) */
  oraclePublicKeys?: Uint8Array[]
  /** Fee per oracle provider in basis points (0-10000) */
  oracleFees: number[]
  /** When betting closes (UTC) */
  closeDate: Date
  /** When market resolves / expires (UTC) */
  endDate: Date
  /** QU per betting slot (min 10,000) */
  amountPerSlot: bigint
  /** Max slots per option (1-2048) */
  maxBetSlotPerOption: number
}

export interface JoinBetParams {
  /** On-chain bet ID (uint32) */
  betId: number
  /** Number of slots to buy */
  numberOfSlot: number
  /** Option index (0-based) */
  option: number
}

export interface PublishResultParams {
  /** On-chain bet ID (uint32) */
  betId: number
  /** Winning option index (0-based) */
  winOption: number
}

export interface CancelBetParams {
  /** On-chain bet ID (uint32) */
  betId: number
}

export interface BetInfo {
  betId: number
  numberOfOption: number
  creator: string // hex-encoded 32-byte public key
  betDesc: string
  options: string[]
  oracleProviderIds: string[] // hex-encoded public keys
  oracleFees: number[]
  openDate: Date | null
  closeDate: Date | null
  endDate: Date | null
  amountPerSlot: bigint
  maxBetSlotPerOption: number
  /** Current bet count per option (8 slots) */
  currentNumSelection: number[]
  /** Oracle votes for winning option (8 int8s) */
  betResultWonOption: number[]
  /** Oracle provider index per vote (8 int8s) */
  betResultOPId: number[]
}

export interface QuotteryTxResult {
  success: boolean
  txId: string
  peersBroadcasted: number
  targetTick: number
  txSize: number
  error?: string
}

// ---------------------------------------------------------------------------
// Binary Encoding Helpers
// ---------------------------------------------------------------------------

/**
 * Encode a string as a Qubic `id` (m256i = 32 bytes).
 * Each character stored as lowercase ASCII, zero-padded to 32 bytes.
 */
function encodeId(str: string): Uint8Array {
  const buf = new Uint8Array(32)
  const lower = str.toLowerCase()
  for (let i = 0; i < Math.min(lower.length, 31); i++) {
    buf[i] = lower.charCodeAt(i)
  }
  return buf
}

/**
 * Decode a 32-byte id back to a string (strips null bytes).
 */
function decodeId(buf: Uint8Array): string {
  let str = ''
  for (let i = 0; i < 32; i++) {
    const byte = buf[i]
    if (byte === undefined || byte === 0) break
    str += String.fromCharCode(byte)
  }
  return str
}

/**
 * Encode a Date as a Quottery packed uint32 date (4 bytes LE).
 *
 * Bit layout (verified against official Quottery frontend packQuotteryDate):
 *   bits 26-31: (year - 2024) (6 bits, range 0-63 = years 2024-2087)
 *   bits 22-25: month (4 bits, 1-12)
 *   bits 17-21: day (5 bits, 1-31)
 *   bits 12-16: hour (5 bits, 0-23)
 *   bits 6-11:  minute (6 bits, 0-59)
 *   bits 0-5:   second (6 bits, 0-59)
 *
 * Official code: `year = year - 2000; return ((year - 24) << 26) | ...`
 * Which simplifies to: `(fullYear - 2024) << 26`
 */
function packQuotteryDate(date: Date): number {
  const year = date.getUTCFullYear() - 2024
  const month = date.getUTCMonth() + 1
  const day = date.getUTCDate()
  const hour = date.getUTCHours()
  const minute = date.getUTCMinutes()
  const second = date.getUTCSeconds()

  if (year < 0 || year > 63) {
    throw new Error(`Year ${date.getUTCFullYear()} out of Quottery range (2024-2087)`)
  }

  return (
    ((year & 0x3F) << 26) |
    ((month & 0x0F) << 22) |
    ((day & 0x1F) << 17) |
    ((hour & 0x1F) << 12) |
    ((minute & 0x3F) << 6) |
    (second & 0x3F)
  )
}

/**
 * Decode a Quottery packed uint32 date back to a Date.
 *
 * Official unpack: `year = ((data >> 26) & 0x3F) + 24` (returns 2-digit year)
 * Full year = 2000 + (stored + 24) = stored + 2024
 */
function unpackQuotteryDate(packed: number): Date {
  const year = ((packed >> 26) & 0x3F) + 2024
  const month = (packed >> 22) & 0x0F
  const day = (packed >> 17) & 0x1F
  const hour = (packed >> 12) & 0x1F
  const minute = (packed >> 6) & 0x3F
  const second = packed & 0x3F
  return new Date(Date.UTC(year, month - 1, day, hour, minute, second))
}

/**
 * Write a uint32 to a Uint8Array at the given offset (little-endian).
 */
function writeUint32LE(buf: Uint8Array, value: number, offset: number): void {
  const view = new DataView(buf.buffer, buf.byteOffset, buf.byteLength)
  view.setUint32(offset, value, true)
}

/**
 * Write a sint64 (bigint) to a Uint8Array at the given offset (little-endian).
 */
function writeInt64LE(buf: Uint8Array, value: bigint, offset: number): void {
  const view = new DataView(buf.buffer, buf.byteOffset, buf.byteLength)
  view.setBigInt64(offset, value, true)
}

/**
 * Convert a 60-char Qubic public ID to 32-byte public key.
 * Uses QubicHelper.getIdentityBytes() from @qubic-lib/qubic-ts-library.
 */
async function addressToPublicKey(
  address: string,
): Promise<Uint8Array> {
  const lib = await loadQubicLib()
  const helper = new lib.QubicHelper()
  return helper.getIdentityBytes(address)
}

// ---------------------------------------------------------------------------
// Payload Builders
// ---------------------------------------------------------------------------

/**
 * Build the binary payload for issueBet (600 bytes).
 *
 * Struct layout (verified against official Quottery frontend):
 *   [0..31]     betDesc (id, 32B)
 *   [32..287]   optionDesc[8] (8 x id, 256B)
 *   [288..543]  oracleProviderId[8] (8 x 32-byte public key, 256B)
 *   [544..575]  oracleFees[8] (8 x uint32, 32B)
 *   [576..579]  closeDate (packed uint32, 4B)
 *   [580..583]  endDate (packed uint32, 4B)
 *   [584..591]  amountPerSlot (sint64, 8B)
 *   [592..595]  maxBetSlotPerOption (uint32, 4B)
 *   [596..599]  numberOfOption (uint32, 4B)
 *   Total: 32 + 256 + 256 + 32 + 4 + 4 + 8 + 4 + 4 = 600
 */
export function buildIssueBetPayload(params: IssueBetParams): Uint8Array {
  const buf = new Uint8Array(INPUT_SIZES.issueBet)

  // Validate
  if (params.options.length < 2 || params.options.length > 8) {
    throw new Error(
      `Options must be 2-8, got ${params.options.length}`,
    )
  }
  if (params.oracleProviderIds.length < 1 || params.oracleProviderIds.length > 8) {
    throw new Error(
      `Oracle providers must be 1-8, got ${params.oracleProviderIds.length}`,
    )
  }
  if (params.oracleProviderIds.length !== params.oracleFees.length) {
    throw new Error('Oracle provider IDs and fees must have same length')
  }
  if (params.amountPerSlot < QUOTTERY_FEES.minAmountPerSlot) {
    throw new Error(
      `Amount per slot must be >= ${QUOTTERY_FEES.minAmountPerSlot}, got ${params.amountPerSlot}`,
    )
  }
  if (
    params.maxBetSlotPerOption < 1 ||
    params.maxBetSlotPerOption > QUOTTERY_FEES.maxBetSlotPerOption
  ) {
    throw new Error(
      `Max bet slots must be 1-${QUOTTERY_FEES.maxBetSlotPerOption}, got ${params.maxBetSlotPerOption}`,
    )
  }

  let offset = 0

  // betDesc (32 bytes)
  const desc = encodeId(params.betDesc)
  buf.set(desc, offset)
  offset += 32

  // optionDesc[8] (256 bytes)
  for (let i = 0; i < 8; i++) {
    const optLabel = params.options[i]
    const optDesc = optLabel !== undefined ? encodeId(optLabel) : new Uint8Array(32)
    buf.set(optDesc, offset)
    offset += 32
  }

  // oracleProviderId[8] (256 bytes) — must be raw 32-byte public keys
  for (let i = 0; i < 8; i++) {
    const pubKey = params.oraclePublicKeys?.[i]
    if (pubKey) {
      buf.set(pubKey, offset)
    }
    offset += 32
  }

  // oracleFees[8] (32 bytes)
  for (let i = 0; i < 8; i++) {
    const fee = params.oracleFees[i] ?? 0
    writeUint32LE(buf, fee, offset)
    offset += 4
  }

  // closeDate (4 bytes — packed Quottery uint32 date)
  writeUint32LE(buf, packQuotteryDate(params.closeDate), offset)
  offset += 4

  // endDate (4 bytes — packed Quottery uint32 date)
  writeUint32LE(buf, packQuotteryDate(params.endDate), offset)
  offset += 4

  // amountPerSlot (8 bytes, sint64)
  writeInt64LE(buf, params.amountPerSlot, offset)
  offset += 8

  // maxBetSlotPerOption (4 bytes)
  writeUint32LE(buf, params.maxBetSlotPerOption, offset)
  offset += 4

  // numberOfOption (4 bytes)
  writeUint32LE(buf, params.options.length, offset)

  return buf
}

/**
 * Build the binary payload for joinBet (12 bytes).
 *
 * Struct layout:
 *   [0..3]   betId (uint32)
 *   [4..7]   numberOfSlot (uint32)
 *   [8..11]  option (uint32)
 */
export function buildJoinBetPayload(params: JoinBetParams): Uint8Array {
  const buf = new Uint8Array(INPUT_SIZES.joinBet)
  writeUint32LE(buf, params.betId, 0)
  writeUint32LE(buf, params.numberOfSlot, 4)
  writeUint32LE(buf, params.option, 8)
  return buf
}

/**
 * Build the binary payload for publishResult (8 bytes).
 *
 * Struct layout:
 *   [0..3]   betId (uint32)
 *   [4..7]   winOption (uint32)
 */
export function buildPublishResultPayload(
  params: PublishResultParams,
): Uint8Array {
  const buf = new Uint8Array(INPUT_SIZES.publishResult)
  writeUint32LE(buf, params.betId, 0)
  writeUint32LE(buf, params.winOption, 4)
  return buf
}

/**
 * Build the binary payload for cancelBet (4 bytes).
 *
 * Struct layout:
 *   [0..3]   betId (uint32)
 */
export function buildCancelBetPayload(params: CancelBetParams): Uint8Array {
  const buf = new Uint8Array(INPUT_SIZES.cancelBet)
  writeUint32LE(buf, params.betId, 0)
  return buf
}

// ---------------------------------------------------------------------------
// Qubic Library Loader
// ---------------------------------------------------------------------------

interface QubicLib {
  QubicHelper: new () => QubicHelperInstance
  QubicTransaction: new () => QubicTxInstance
  DynamicPayload: new (size: number) => DynamicPayloadInstance
  PublicKey: new (data: Uint8Array) => PublicKeyInstance
}

interface QubicHelperInstance {
  createIdPackage(seed: string): Promise<{ publicKey: Uint8Array; privateKey: Uint8Array; publicId: string }>
  createTransaction(
    seed: string,
    dest: string,
    amount: number,
    tick: number,
  ): Promise<Uint8Array>
  /** Convert 60-char Qubic identity to 32-byte public key */
  getIdentityBytes(identity: string): Uint8Array
  /** Convert 32-byte public key to 60-char Qubic identity */
  getIdentity(publicKey: Uint8Array, lowerCase?: boolean): Promise<string>
  /** Verify if a Qubic identity string is valid */
  verifyIdentity(identity: string): Promise<boolean>
}

interface QubicTxInstance {
  setSourcePublicKey(key: PublicKeyInstance): QubicTxInstance
  setDestinationPublicKey(key: PublicKeyInstance): QubicTxInstance
  setAmount(amount: number | bigint): QubicTxInstance
  setTick(tick: number): QubicTxInstance
  setInputType(type: number): QubicTxInstance
  setInputSize(size: number): QubicTxInstance
  setPayload(payload: DynamicPayloadInstance): QubicTxInstance
  build(seed: string): Promise<Uint8Array>
  encodeTransactionToBase64(bytes: Uint8Array): string
}

interface DynamicPayloadInstance {
  setPayload(data: Uint8Array): void
}

interface PublicKeyInstance {
  _data: Uint8Array
}

let _qubicLib: QubicLib | null = null

async function loadQubicLib(): Promise<QubicLib> {
  if (_qubicLib) return _qubicLib

  try {
    // @qubic-lib/qubic-ts-library exports as CommonJS with default
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const createRequire = (await import('module')).createRequire
    const require = createRequire(import.meta.url)
    const lib = require('@qubic-lib/qubic-ts-library').default
    _qubicLib = lib as QubicLib
    return _qubicLib
  } catch {
    throw new Error(
      '@qubic-lib/qubic-ts-library not available. Install with: pnpm add @qubic-lib/qubic-ts-library',
    )
  }
}

// ---------------------------------------------------------------------------
// RPC Helper
// ---------------------------------------------------------------------------

let _currentRpcIdx = 0

async function rpcCall<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  // Circuit breaker: reject immediately if the breaker is open
  if (!rpcBreaker.isHealthy()) {
    throw new CircuitOpenError(
      `Circuit ${rpcBreaker.name} is open — skipping RPC call to ${endpoint}`,
    )
  }

  const errors: string[] = []

  for (let i = 0; i < QUBIC_RPC_ENDPOINTS.length; i++) {
    const baseUrl =
      QUBIC_RPC_ENDPOINTS[(_currentRpcIdx + i) % QUBIC_RPC_ENDPOINTS.length]
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(
        () => controller.abort(),
        API_CONFIG.timeout,
      )

      const res = await fetch(`${baseUrl}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        signal: controller.signal,
      })
      clearTimeout(timeoutId)

      if (!res.ok) throw new Error(`RPC ${res.status}: ${res.statusText}`)
      _currentRpcIdx = (_currentRpcIdx + i) % QUBIC_RPC_ENDPOINTS.length
      rpcBreaker.recordSuccess()
      return (await res.json()) as T
    } catch (e) {
      errors.push(
        `${baseUrl}: ${e instanceof Error ? e.message : 'Unknown error'}`,
      )
    }
  }

  const error = new Error(`All RPC endpoints failed: ${errors.join('; ')}`)
  rpcBreaker.recordFailure(error)
  throw error
}

async function getCurrentTick(): Promise<{
  tick: number
  epoch: number
}> {
  const data = await rpcCall<{
    tickInfo?: { tick: number; epoch: number }
    tick?: number
    epoch?: number
  }>('/tick-info')
  return {
    tick: data.tickInfo?.tick ?? data.tick ?? 0,
    epoch: data.tickInfo?.epoch ?? data.epoch ?? 0,
  }
}

// ---------------------------------------------------------------------------
// Core Transaction Sender
// ---------------------------------------------------------------------------

/**
 * Build, sign, and broadcast a Quottery SC transaction.
 *
 * @param seed - 55-char lowercase Qubic seed
 * @param procedure - Procedure index (1-4)
 * @param payload - Binary encoded input struct
 * @param amount - QU to send with the TX (for joinBet: bet amount)
 * @param targetTick - Target tick for the TX (current + offset)
 */
async function sendQuotteryTx(
  seed: string,
  procedure: number,
  payload: Uint8Array,
  amount: number | bigint,
  targetTick: number,
): Promise<QuotteryTxResult> {
  const lib = await loadQubicLib()

  const helper = new lib.QubicHelper()
  const idPackage = await helper.createIdPackage(seed)

  // Build transaction to Quottery SC
  const tx = new lib.QubicTransaction()
    .setSourcePublicKey(new lib.PublicKey(idPackage.publicKey))
    .setDestinationPublicKey(
      new lib.PublicKey(getQuotteryPublicKeyBytes()),
    )
    .setAmount(Number(amount))
    .setTick(targetTick)
    .setInputType(procedure)
    .setInputSize(payload.length)

  const dynPayload = new lib.DynamicPayload(payload.length)
  dynPayload.setPayload(payload)
  tx.setPayload(dynPayload)

  const txBytes = await tx.build(seed)
  const encoded = tx.encodeTransactionToBase64(txBytes)

  // Broadcast
  const result = await rpcCall<{
    transactionId?: string
    peersBroadcasted?: number
  }>('/broadcast-transaction', {
    method: 'POST',
    body: JSON.stringify({ encodedTransaction: encoded }),
  })

  return {
    success: true,
    txId:
      result.transactionId ??
      String(result.peersBroadcasted ?? 'broadcast_ok'),
    peersBroadcasted: result.peersBroadcasted ?? 0,
    targetTick,
    txSize: txBytes.length,
  }
}

// ---------------------------------------------------------------------------
// Public API — Write Operations
// ---------------------------------------------------------------------------

/**
 * Create a new bet/market on Quottery SC.
 *
 * The caller (seed owner) becomes the Game Operator and receives 0.5% fee.
 * Amount sent = maxSlots × numOptions × feePerSlotPerHour × hours (storage fee).
 */
export async function issueBet(
  seed: string,
  params: IssueBetParams,
  targetTick?: number,
): Promise<QuotteryTxResult> {
  // Resolve oracle addresses to 32-byte public keys
  if (!params.oraclePublicKeys || params.oraclePublicKeys.length === 0) {
    const lib = await loadQubicLib()
    const helper = new lib.QubicHelper()
    params.oraclePublicKeys = []
    for (const addr of params.oracleProviderIds) {
      const bytes = helper.getIdentityBytes(addr)
      params.oraclePublicKeys.push(bytes)
    }
  }

  const payload = buildIssueBetPayload(params)

  if (!targetTick) {
    const { tick } = await getCurrentTick()
    targetTick = tick + 5
  }

  // Calculate issueBet fee: maxSlots × numOptions × feePerSlotPerHour × hoursUntilEnd
  // Query actual feePerSlotPerHour from the SC instead of hardcoding
  let feePerSlotPerHour = 10 // fallback if SC query fails
  try {
    const nodeInfo = await getNodeInfo()
    if (nodeInfo && nodeInfo.feePerSlotPerHour > 0) {
      feePerSlotPerHour = nodeInfo.feePerSlotPerHour
    }
  } catch {
    rpcLog.warn('Could not query SC nodeInfo for fee — using fallback 10/hr')
  }

  const now = new Date()
  const diffMs = params.endDate.getTime() - now.getTime()
  const diffHours = Math.max(Math.ceil(diffMs / (1000 * 60 * 60)), 1)
  const issueFee = BigInt(params.maxBetSlotPerOption) *
    BigInt(params.options.length) *
    BigInt(feePerSlotPerHour) *
    BigInt(diffHours)

  rpcLog.info({ issueFee: issueFee.toString(), slots: params.maxBetSlotPerOption, opts: params.options.length, feePerHour: feePerSlotPerHour, hours: diffHours }, 'issueBet fee calculated')

  return sendQuotteryTx(seed, PROCEDURES.issueBet, payload, issueFee, targetTick)
}

/**
 * Place a bet on an existing market.
 *
 * The caller sends (amountPerSlot * numberOfSlot) QU to the SC.
 */
export async function joinBet(
  seed: string,
  params: JoinBetParams,
  amountQU: bigint,
  targetTick?: number,
): Promise<QuotteryTxResult> {
  const payload = buildJoinBetPayload(params)

  if (!targetTick) {
    const { tick } = await getCurrentTick()
    targetTick = tick + 5
  }

  return sendQuotteryTx(
    seed,
    PROCEDURES.joinBet,
    payload,
    amountQU,
    targetTick,
  )
}

/**
 * Publish the result of a bet (oracle resolution).
 *
 * Only callable by registered oracle providers for the bet.
 * When 2/3 of oracles agree, the SC distributes the pool.
 */
export async function publishResult(
  seed: string,
  params: PublishResultParams,
  targetTick?: number,
): Promise<QuotteryTxResult> {
  const payload = buildPublishResultPayload(params)

  if (!targetTick) {
    const { tick } = await getCurrentTick()
    targetTick = tick + 5
  }

  return sendQuotteryTx(
    seed,
    PROCEDURES.publishResult,
    payload,
    0,
    targetTick,
  )
}

/**
 * Cancel a bet (creator only, before endDate).
 *
 * All participants are refunded.
 */
export async function cancelBet(
  seed: string,
  params: CancelBetParams,
  targetTick?: number,
): Promise<QuotteryTxResult> {
  const payload = buildCancelBetPayload(params)

  if (!targetTick) {
    const { tick } = await getCurrentTick()
    targetTick = tick + 5
  }

  return sendQuotteryTx(
    seed,
    PROCEDURES.cancelBet,
    payload,
    0,
    targetTick,
  )
}

// ---------------------------------------------------------------------------
// Public API — Read Operations (SC Queries)
// ---------------------------------------------------------------------------

/**
 * Query Quottery SC for bet information.
 *
 * Uses the /querySmartContract RPC endpoint.
 */
export async function getBetInfo(betId: number): Promise<BetInfo | null> {
  try {
    // Build input: uint32 betId (4 bytes)
    const input = new Uint8Array(4)
    writeUint32LE(input, betId, 0)

    // Convert to base64
    const inputBase64 = btoa(
      String.fromCharCode(...input),
    )

    const result = await rpcCall<{
      responseData?: string
    }>('/querySmartContract', {
      method: 'POST',
      body: JSON.stringify({
        contractIndex: QUOTTERY_CONTRACT_INDEX,
        inputType: FUNCTIONS.getBetInfo,
        inputSize: input.length,
        requestData: inputBase64,
      }),
    })

    if (!result.responseData) return null

    // Decode response — the exact layout depends on Quottery's output struct
    return parseBetInfoResponse(result.responseData)
  } catch (error) {
    rpcLog.error({ err: error }, 'getBetInfo error')
    return null
  }
}

/**
 * Query for all active bets on the Quottery SC.
 */
export async function getActiveBets(): Promise<number[]> {
  try {
    const result = await rpcCall<{
      responseData?: string
    }>('/querySmartContract', {
      method: 'POST',
      body: JSON.stringify({
        contractIndex: QUOTTERY_CONTRACT_INDEX,
        inputType: FUNCTIONS.getActiveBet,
        inputSize: 0,
        requestData: '',
      }),
    })

    if (!result.responseData) return []

    return parseActiveBetsResponse(result.responseData)
  } catch (error) {
    rpcLog.error({ err: error }, 'getActiveBets error')
    return []
  }
}

/**
 * Discover the on-chain betId for a bet we created.
 *
 * After issueBet, the SC assigns a sequential betId. We discover it by:
 * 1. Getting all active bet IDs from the SC
 * 2. Querying getBetInfo for each (starting from highest/newest)
 * 3. Matching by betDesc substring
 *
 * @param betDescPrefix - First 31 chars of the bet description (as used in issueBet)
 * @param maxCheckCount - Max number of bet IDs to check (default 10, newest first)
 * @returns The matching betId, or null if not found
 */
export async function discoverBetId(
  betDescPrefix: string,
  maxCheckCount: number = 10,
): Promise<number | null> {
  try {
    const activeIds = await getActiveBets()
    if (activeIds.length === 0) {
      rpcLog.info('discoverBetId: no active bets found')
      return null
    }

    // Sort descending (newest first) and check up to maxCheckCount
    const sortedIds = [...activeIds].sort((a, b) => b - a)
    const toCheck = sortedIds.slice(0, maxCheckCount)

    const normalizedPrefix = betDescPrefix.toLowerCase().trim()

    for (const id of toCheck) {
      const info = await getBetInfo(id)
      if (!info) continue

      // Match by betDesc (case-insensitive, trimmed)
      if (info.betDesc.toLowerCase().trim() === normalizedPrefix) {
        rpcLog.info({ betId: id, betDesc: info.betDesc }, 'discoverBetId: found match')
        return id
      }
    }

    rpcLog.info({ prefix: normalizedPrefix, checked: toCheck.length }, 'discoverBetId: no match')
    return null
  } catch (error) {
    rpcLog.error({ err: error }, 'discoverBetId error')
    return null
  }
}

/**
 * Get SC node info (fees, limits, counters).
 */
export async function getNodeInfo(): Promise<{
  feePerSlotPerHour: number
  nIssuedBet: number
  nActiveBet: number
} | null> {
  try {
    const result = await rpcCall<{
      responseData?: string
    }>('/querySmartContract', {
      method: 'POST',
      body: JSON.stringify({
        contractIndex: QUOTTERY_CONTRACT_INDEX,
        inputType: FUNCTIONS.getNodeInfo,
        inputSize: 0,
        requestData: '',
      }),
    })

    if (!result.responseData) return null

    const raw = Uint8Array.from(atob(result.responseData), (c) => c.charCodeAt(0))
    if (raw.length < 12) return null

    const view = new DataView(raw.buffer, raw.byteOffset, raw.byteLength)

    return {
      feePerSlotPerHour: view.getUint32(0, true),
      nIssuedBet: view.getUint32(4, true),
      nActiveBet: view.getUint32(8, true),
    }
  } catch (error) {
    rpcLog.error({ err: error }, 'getNodeInfo error')
    return null
  }
}

/**
 * Get current tick and epoch from Qubic network.
 * Convenience export for external callers.
 */
export { getCurrentTick }

/**
 * Expose RPC call function for external use (e.g., escrow sweep).
 */
export { rpcCall }

/**
 * Expose address-to-public-key converter for external use.
 */
export { addressToPublicKey }

/**
 * Get balance for a Qubic address.
 */
export async function getBalance(address: string): Promise<bigint> {
  try {
    const result = await rpcCall<{
      balance: {
        id: string
        balance: string | number
      }
    }>(`/balances/${address}`)

    if (result.balance && typeof result.balance === 'object') {
      return BigInt(result.balance.balance)
    }
    return 0n
  } catch {
    return 0n
  }
}

// ---------------------------------------------------------------------------
// Response Parsers
// ---------------------------------------------------------------------------

/**
 * Parse getBetInfo SC response.
 *
 * Output struct layout (verified against official Quottery frontend fetchBetDetailFromCoreNode):
 *   [0..3]     bet_id (uint32, 4B)
 *   [4..7]     nOption (uint32, 4B)
 *   [8..39]    creator (32B public key)
 *   [40..71]   bet_desc (32B, null-terminated ASCII)
 *   [72..327]  option_desc[8] (8×32B = 256B)
 *   [328..583] oracle_id[8] (8×32B = 256B, raw public keys)
 *   [584..615] oracle_fee[8] (8×uint32 = 32B)
 *   [616..619] open_date (packed uint32, 4B)
 *   [620..623] close_date (packed uint32, 4B)
 *   [624..627] end_date (packed uint32, 4B)
 *   [628..631] reserved (4B)
 *   [632..639] amount_per_bet_slot (uint64, 8B)
 *   [640..643] maxBetSlotPerOption (uint32, 4B)
 *   [644..675] current_num_selection[8] (8×uint32 = 32B)
 *   [676..683] betResultWonOption[8] (8×int8 = 8B)
 *   [684..691] betResultOPId[8] (8×int8 = 8B)
 *
 * Total: ~692 bytes
 */
function parseBetInfoResponse(base64Data: string): BetInfo | null {
  try {
    const raw = Uint8Array.from(atob(base64Data), (c) => c.charCodeAt(0))
    if (raw.length < 640) return null

    const view = new DataView(raw.buffer, raw.byteOffset, raw.byteLength)

    // [0..3] bet_id (uint32)
    const betId = view.getUint32(0, true)

    // [4..7] nOption (uint32)
    const numberOfOption = view.getUint32(4, true)

    // [8..39] creator (32B public key → hex)
    const creatorBytes = raw.slice(8, 40)
    const creator = Array.from(creatorBytes)
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('')

    // [40..71] bet_desc (32B string)
    const betDesc = decodeId(raw.slice(40, 72))

    // [72..327] option_desc[8] (256B)
    const options: string[] = []
    for (let i = 0; i < 8; i++) {
      const off = 72 + i * 32
      const opt = decodeId(raw.slice(off, off + 32))
      if (opt) options.push(opt)
    }

    // [328..583] oracle_id[8] (256B, raw public keys)
    const oracleProviderIds: string[] = []
    for (let i = 0; i < 8; i++) {
      const off = 328 + i * 32
      const keyBytes = raw.slice(off, off + 32)
      const isNonZero = keyBytes.some((b) => b !== 0)
      if (isNonZero) {
        oracleProviderIds.push(
          Array.from(keyBytes)
            .map((b) => b.toString(16).padStart(2, '0'))
            .join(''),
        )
      }
    }

    // [584..615] oracle_fee[8] (32B)
    const oracleFees: number[] = []
    for (let i = 0; i < 8; i++) {
      oracleFees.push(view.getUint32(584 + i * 4, true))
    }

    // [616..619] open_date (packed uint32)
    const openPacked = view.getUint32(616, true)
    const openDate = openPacked > 0 ? unpackQuotteryDate(openPacked) : null

    // [620..623] close_date (packed uint32)
    const closePacked = view.getUint32(620, true)
    const closeDate = closePacked > 0 ? unpackQuotteryDate(closePacked) : null

    // [624..627] end_date (packed uint32)
    const endPacked = view.getUint32(624, true)
    const endDate = endPacked > 0 ? unpackQuotteryDate(endPacked) : null

    // [628..631] reserved — skip

    // [632..639] amount_per_bet_slot (uint64)
    const amountPerSlot = view.getBigUint64(632, true)

    // [640..643] maxBetSlotPerOption (uint32)
    const maxBetSlotPerOption = view.getUint32(640, true)

    // [644..675] current_num_selection[8] (8×uint32)
    const currentNumSelection: number[] = []
    for (let i = 0; i < 8; i++) {
      currentNumSelection.push(view.getUint32(644 + i * 4, true))
    }

    // [676..683] betResultWonOption[8] (8×int8)
    const betResultWonOption: number[] = []
    for (let i = 0; i < 8; i++) {
      if (676 + i < raw.length) {
        betResultWonOption.push(view.getInt8(676 + i))
      }
    }

    // [684..691] betResultOPId[8] (8×int8)
    const betResultOPId: number[] = []
    for (let i = 0; i < 8; i++) {
      if (684 + i < raw.length) {
        betResultOPId.push(view.getInt8(684 + i))
      }
    }

    return {
      betId,
      numberOfOption,
      creator,
      betDesc,
      options: options.slice(0, numberOfOption),
      oracleProviderIds,
      oracleFees,
      openDate,
      closeDate,
      endDate,
      amountPerSlot: BigInt(amountPerSlot),
      maxBetSlotPerOption,
      currentNumSelection,
      betResultWonOption,
      betResultOPId,
    }
  } catch (error) {
    rpcLog.error({ err: error }, 'failed to parse getBetInfo response')
    return null
  }
}

/**
 * Parse getActiveBet SC response.
 *
 * Format (verified against official Quottery frontend fetchActiveBets):
 *   First 4 bytes: uint32 count (number of active bets)
 *   Then count × 4 bytes: uint32 bet IDs
 */
function parseActiveBetsResponse(base64Data: string): number[] {
  try {
    const raw = Uint8Array.from(atob(base64Data), (c) => c.charCodeAt(0))
    if (raw.length < 4) return []

    const view = new DataView(raw.buffer, raw.byteOffset, raw.byteLength)

    // First 4 bytes = count
    const count = view.getUint32(0, true)
    if (count === 0) return []

    const ids: number[] = []
    for (let i = 0; i < count; i++) {
      const offset = 4 + i * 4
      if (offset + 4 > raw.length) break
      const id = view.getUint32(offset, true)
      if (id > 0) ids.push(id)
    }

    return ids
  } catch {
    return []
  }
}

// ---------------------------------------------------------------------------
// Utility Exports
// ---------------------------------------------------------------------------

/**
 * Estimate the total cost for a user to join a bet.
 */
export function estimateJoinCost(
  amountPerSlot: bigint,
  numberOfSlot: number,
): bigint {
  return amountPerSlot * BigInt(numberOfSlot)
}

/**
 * Estimate payout for a bet, matching the Quottery SC fee model.
 *
 * CRITICAL: The Quottery SC takes fees from the LOSER pool only.
 * Winners get their full stake back + (loser pool minus fees).
 *
 * Fee structure (from Quottery.h, applied to loser pool):
 *   - 2% burned
 *   - 10% to shareholders
 *   - 0.5% to game operator (bet creator)
 *   - oracleFee split among oracle providers
 *   - remainder distributed to winners proportionally
 *
 * Verified on-chain: 90k pool (2 YES + 7 NO × 10k), SC paid 81,250 QU
 *   = 20k (winner stake) + 70k × 87.5% (loser pool minus 12.5% fees)
 *
 * @param totalPool     Total QU in the pool (all options combined)
 * @param winnerSlots   Slots held by the user being estimated
 * @param totalWinnerSlots Total slots on the winning option
 * @param oracleFeeBps  Oracle fee in basis points (default 0)
 * @param totalSlots    Total slots across ALL options (needed to compute loser pool)
 */
export function estimatePayout(
  totalPool: bigint,
  winnerSlots: number,
  totalWinnerSlots: number,
  oracleFeeBps: number = 0,
  totalSlots?: number,
): {
  burn: bigint
  shareholderFee: bigint
  gameOperatorFee: bigint
  oracleFee: bigint
  winnerStake: bigint
  loserPool: bigint
  totalFees: bigint
  winnerPool: bigint
  perSlotPayout: bigint
  userPayout: bigint
} {
  // Decompose pool into winner stake + loser pool
  const allSlots = totalSlots ?? totalWinnerSlots
  const winnerStake = allSlots > 0
    ? (totalPool * BigInt(totalWinnerSlots)) / BigInt(allSlots)
    : 0n
  const loserPool = totalPool - winnerStake

  // Fees are taken from the LOSER pool only (not total pool)
  const burn = (loserPool * 2n) / 100n
  const shareholderFee = (loserPool * 10n) / 100n
  const gameOperatorFee = (loserPool * 5n) / 1000n // 0.5%
  const oracleFee = (loserPool * BigInt(oracleFeeBps)) / 10000n
  const totalFees = burn + shareholderFee + gameOperatorFee + oracleFee

  // Winners get their stake back + loser pool minus fees
  const winnerPool = winnerStake + loserPool - totalFees
  const perSlotPayout =
    totalWinnerSlots > 0 ? winnerPool / BigInt(totalWinnerSlots) : 0n
  const userPayout = perSlotPayout * BigInt(winnerSlots)

  return {
    burn,
    shareholderFee,
    gameOperatorFee,
    oracleFee,
    winnerStake,
    loserPool,
    totalFees,
    winnerPool,
    perSlotPayout,
    userPayout,
  }
}
