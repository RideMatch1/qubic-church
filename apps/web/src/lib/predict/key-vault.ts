/**
 * Key Vault — AES-256-GCM Encrypted Seed Storage
 *
 * Every escrow address has a corresponding Qubic seed (private key).
 * Seeds are encrypted at rest using AES-256-GCM with a master key
 * from the ESCROW_MASTER_KEY environment variable.
 *
 * After a successful payout sweep, keys are marked as 'swept'
 * and can be archived or deleted.
 */

import crypto from 'crypto'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface EncryptedSeed {
  ciphertext: string // hex-encoded AES-256-GCM ciphertext
  iv: string // hex-encoded 12-byte initialization vector
  authTag: string // hex-encoded 16-byte GCM authentication tag
}

export interface KeyVaultEntry extends EncryptedSeed {
  escrowId: string
  status: 'active' | 'swept' | 'archived'
  createdAt: string
  archivedAt: string | null
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ALGORITHM = 'aes-256-gcm'
const IV_BYTES = 12 // GCM recommended IV length
const TAG_BYTES = 16 // GCM authentication tag length
const KEY_BYTES = 32 // AES-256 key length

// ---------------------------------------------------------------------------
// Master Key
// ---------------------------------------------------------------------------

/**
 * Derive a 32-byte AES key from the master key string.
 * Uses SHA-256 to normalize any master key format to exactly 32 bytes.
 */
export function deriveMasterKey(masterKeyHex?: string): Buffer {
  const raw = masterKeyHex || process.env.ESCROW_MASTER_KEY
  if (!raw) {
    throw new Error(
      'ESCROW_MASTER_KEY environment variable is required for key vault operations',
    )
  }

  // If it's a valid 64-char hex string (32 bytes), use directly
  if (/^[0-9a-fA-F]{64}$/.test(raw)) {
    return Buffer.from(raw, 'hex')
  }

  // Otherwise, derive a 32-byte key via SHA-256
  return crypto.createHash('sha256').update(raw).digest()
}

// ---------------------------------------------------------------------------
// Encrypt / Decrypt
// ---------------------------------------------------------------------------

/**
 * Encrypt a Qubic seed (55 lowercase letters) using AES-256-GCM.
 *
 * @param seed - The 55-char Qubic seed to encrypt
 * @param masterKey - 32-byte AES key (from deriveMasterKey())
 * @returns EncryptedSeed with ciphertext, IV, and auth tag (all hex)
 */
export function encryptSeed(seed: string, masterKey: Buffer): EncryptedSeed {
  if (masterKey.length !== KEY_BYTES) {
    throw new Error(`Master key must be ${KEY_BYTES} bytes, got ${masterKey.length}`)
  }

  if (!/^[a-z]{55}$/.test(seed)) {
    throw new Error('Invalid Qubic seed: must be exactly 55 lowercase letters')
  }

  // Generate a random 12-byte IV for each encryption
  const iv = crypto.randomBytes(IV_BYTES)

  const cipher = crypto.createCipheriv(ALGORITHM, masterKey, iv, {
    authTagLength: TAG_BYTES,
  })

  const encrypted = Buffer.concat([
    cipher.update(seed, 'utf8'),
    cipher.final(),
  ])

  const authTag = cipher.getAuthTag()

  return {
    ciphertext: encrypted.toString('hex'),
    iv: iv.toString('hex'),
    authTag: authTag.toString('hex'),
  }
}

/**
 * Decrypt an encrypted Qubic seed using AES-256-GCM.
 *
 * @param encrypted - The encrypted seed data
 * @param masterKey - 32-byte AES key (same key used for encryption)
 * @returns The original 55-char Qubic seed
 * @throws If decryption fails (wrong key, tampered data, etc.)
 */
export function decryptSeed(encrypted: EncryptedSeed, masterKey: Buffer): string {
  if (masterKey.length !== KEY_BYTES) {
    throw new Error(`Master key must be ${KEY_BYTES} bytes, got ${masterKey.length}`)
  }

  const iv = Buffer.from(encrypted.iv, 'hex')
  const authTag = Buffer.from(encrypted.authTag, 'hex')
  const ciphertext = Buffer.from(encrypted.ciphertext, 'hex')

  if (iv.length !== IV_BYTES) {
    throw new Error(`Invalid IV length: expected ${IV_BYTES}, got ${iv.length}`)
  }

  if (authTag.length !== TAG_BYTES) {
    throw new Error(`Invalid auth tag length: expected ${TAG_BYTES}, got ${authTag.length}`)
  }

  const decipher = crypto.createDecipheriv(ALGORITHM, masterKey, iv, {
    authTagLength: TAG_BYTES,
  })
  decipher.setAuthTag(authTag)

  const decrypted = Buffer.concat([
    decipher.update(ciphertext),
    decipher.final(),
  ])

  const seed = decrypted.toString('utf8')

  // Validate the decrypted seed
  if (!/^[a-z]{55}$/.test(seed)) {
    throw new Error('Decryption produced invalid seed — possible key mismatch or data corruption')
  }

  return seed
}

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------

/**
 * Generate a new random master key (for initial setup).
 * Returns a 64-character hex string (32 bytes).
 */
export function generateMasterKey(): string {
  return crypto.randomBytes(KEY_BYTES).toString('hex')
}

/**
 * Verify that a master key can correctly decrypt an encrypted seed.
 * Useful for health checks and key rotation validation.
 */
export function verifyKeyPair(
  encrypted: EncryptedSeed,
  masterKey: Buffer,
  expectedSeed?: string,
): boolean {
  try {
    const decrypted = decryptSeed(encrypted, masterKey)
    if (expectedSeed) {
      return decrypted === expectedSeed
    }
    // If no expected seed, just check that decryption succeeds
    // and produces a valid seed format
    return /^[a-z]{55}$/.test(decrypted)
  } catch {
    return false
  }
}
