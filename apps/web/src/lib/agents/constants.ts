/**
 * AGENT CONSTANTS
 *
 * Known addresses, patterns, and research data for the Discovery Engine
 */

// Extended Patoshi addresses (first 50 blocks mined by Satoshi)
export const PATOSHI_ADDRESSES = [
  { address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', block: 0, btc: 50, note: 'Genesis Block' },
  { address: '12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX', block: 1, btc: 50, note: 'Block 1' },
  { address: '1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1', block: 2, btc: 50, note: 'Block 2' },
  { address: '1FvzCLoTPGANNjWoUo6jUGuAG3wg1w4YjR', block: 3, btc: 50, note: 'Block 3' },
  { address: '15ubicBBWFnvoZLT7GiU2qxjRaKJPdkDMG', block: 4, btc: 50, note: 'Block 4' },
  { address: '1JfbZRwdDHKZmuiZgYArJZhcuuzuw2HuMu', block: 5, btc: 50, note: 'Block 5' },
  { address: '1GkQmKAmHtNfnD3LHhTkewJxKHVSta4m2a', block: 6, btc: 50, note: 'Block 6' },
  { address: '16LoW7y83wtawMg5XmT4M3Q7EdjjUmenjM', block: 7, btc: 50, note: 'Block 7' },
  { address: '1J6PYEzr4CUoGbnXrELyHszoTSz3wCsCaj', block: 8, btc: 50, note: 'Block 8' },
  { address: '12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S', block: 9, btc: 50, note: 'Block 9' },
]

// CFB-related known data
export const CFB_SIGNATURES = {
  nxtAccount: 'NXT-NYJW-6M4F-6LG2-B6SCK',
  qubicGenesis: 'CFBMEMNONUNLOSICLRUEGDIKSECGDSEJDXDBMFPLEOIUDKQWBLFTEVNPTDPCVKDLPLCVH',
  firstMention: 1397818193, // Unix timestamp
  knownPatterns: [
    '1CFB', // Address prefix pattern
    'ANNA', // Matrix reference
    '0x7B', // Hex signature
  ],
}

// Matrix semantic regions
export const MATRIX_REGIONS = {
  bitcoin: { start: 0, end: 31, name: 'Bitcoin Genesis Zone', description: 'Contains Bitcoin-related patterns' },
  qubic: { start: 32, end: 63, name: 'Qubic Protocol Zone', description: 'Qubic consensus patterns' },
  bridge: { start: 64, end: 95, name: 'Bridge Connection Zone', description: 'Cross-chain correlation area' },
  temporal: { start: 96, end: 127, name: 'Temporal Pattern Zone', description: 'Time-based encodings' },
}

// Significant numbers in Bitcoin/Qubic
export const SIGNIFICANT_NUMBERS = {
  bitcoinMaxSupply: 21_000_000,
  satoshisPerBtc: 100_000_000,
  halvingInterval: 210_000,
  genesisTimestamp: 1231006505,
  genesisBlockHash: '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f',
  qubicTickInterval: 1000, // ms
  matrixSize: 128,
  matrixCells: 16384,
}

// Base58 alphabet for Bitcoin
export const BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

// Fibonacci sequence (used for pattern detection)
export const FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

// Prime numbers under 128 (for matrix analysis)
export const PRIMES_UNDER_128 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127]
