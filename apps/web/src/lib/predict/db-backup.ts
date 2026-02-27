/**
 * QPredict Database Backup Module
 *
 * Creates atomic SQLite backups using VACUUM INTO, with integrity
 * verification and automatic rotation of old backup files.
 *
 * Designed to be called periodically from the cron loop — use
 * `runBackupIfDue(cycleCount)` to trigger every N cycles.
 */

import Database from 'better-sqlite3'
import fs from 'fs'
import path from 'path'

import { dbLog as log } from './logger'
import { sendAlert } from './alerting'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Same path computation used by market-db.ts */
const DB_PATH = path.join(process.cwd(), 'predict.sqlite3')

/** Maximum number of backup files to keep */
const MAX_BACKUPS = 3

/** How often to run a backup (every N cron cycles) */
const BACKUP_EVERY_N_CYCLES = 100

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface BackupResult {
  success: boolean
  backupPath?: string
  error?: string
  sizeBytes?: number
}

// ---------------------------------------------------------------------------
// Core Backup
// ---------------------------------------------------------------------------

/**
 * Perform an atomic backup of the predict database.
 *
 * 1. Opens the DB in read-only mode (safe for concurrent WAL access).
 * 2. Runs `PRAGMA integrity_check` — if it fails, the backup is skipped.
 * 3. Uses `VACUUM INTO ?` to create a consistent, compacted snapshot.
 * 4. Rotates old backups, keeping only the last MAX_BACKUPS files.
 */
export function performBackup(): BackupResult {
  const dbDir = path.dirname(DB_PATH)

  // Verify the main database file exists
  if (!fs.existsSync(DB_PATH)) {
    const msg = `Database file not found: ${DB_PATH}`
    log.error(msg)
    return { success: false, error: msg }
  }

  // Open a separate read-only connection for the backup.
  // This avoids interfering with the singleton MarketDatabase instance and
  // is safe under WAL mode (concurrent readers are supported).
  let backupDb: Database.Database | null = null

  try {
    backupDb = new Database(DB_PATH, { readonly: true })

    // ---- Step 1: Integrity check ----
    const integrityRows = backupDb.pragma('integrity_check') as Array<{ integrity_check: string }>
    const integrityResult = integrityRows[0]?.integrity_check ?? ''

    if (integrityResult !== 'ok') {
      const msg = `Integrity check failed: ${integrityResult}`
      log.error(msg)
      backupDb.close()
      return { success: false, error: msg }
    }

    // ---- Step 2: Create backup via VACUUM INTO ----
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const backupFilename = `predict-backup-${timestamp}.sqlite3`
    const backupPath = path.join(dbDir, backupFilename)

    // VACUUM INTO requires a read-write connection because it creates
    // internal temporary structures. Close the read-only connection and
    // open a brief read-write one solely for the VACUUM INTO operation.
    backupDb.close()
    backupDb = null

    const rwDb = new Database(DB_PATH, { readonly: false })
    // Set busy timeout so we don't fail if the main connection is writing
    rwDb.pragma('busy_timeout = 10000')

    try {
      rwDb.exec(`VACUUM INTO '${backupPath.replace(/'/g, "''")}'`)
    } finally {
      rwDb.close()
    }

    // ---- Step 3: Verify the backup file was created ----
    if (!fs.existsSync(backupPath)) {
      const msg = 'VACUUM INTO completed but backup file was not found'
      log.error(msg)
      return { success: false, error: msg }
    }

    const stats = fs.statSync(backupPath)
    const sizeBytes = stats.size

    log.info(
      `Backup created: ${backupFilename} (${(sizeBytes / 1024).toFixed(1)} KB)`,
    )

    // ---- Step 4: Rotate old backups ----
    rotateBackups(dbDir)

    return { success: true, backupPath, sizeBytes }
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err)
    log.error(`Backup failed: ${msg}`)
    void sendAlert('backup_failure', 'error', `Database backup failed: ${msg}`)
    return { success: false, error: msg }
  } finally {
    // Defensive cleanup — close if we didn't already
    try {
      backupDb?.close()
    } catch {
      // Ignore close errors on cleanup
    }
  }
}

// ---------------------------------------------------------------------------
// Backup Rotation
// ---------------------------------------------------------------------------

/**
 * Scan the given directory for backup files matching the naming pattern
 * and delete all but the most recent MAX_BACKUPS files.
 */
function rotateBackups(directory: string): void {
  try {
    const allFiles = fs.readdirSync(directory)

    // Match files like: predict-backup-2026-02-13T12-00-00-000Z.sqlite3
    const backupFiles = allFiles
      .filter((f) => f.startsWith('predict-backup-') && f.endsWith('.sqlite3'))
      .sort() // ISO-based timestamps sort lexicographically

    if (backupFiles.length <= MAX_BACKUPS) {
      return
    }

    // Delete oldest files, keeping only the last MAX_BACKUPS
    const toDelete = backupFiles.slice(0, backupFiles.length - MAX_BACKUPS)

    for (const file of toDelete) {
      const filePath = path.join(directory, file)
      try {
        fs.unlinkSync(filePath)
        log.info(`Deleted old backup: ${file}`)
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err)
        log.warn(`Failed to delete old backup ${file}: ${msg}`)
      }
    }
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err)
    log.warn(`Backup rotation scan failed: ${msg}`)
  }
}

// ---------------------------------------------------------------------------
// Cron Integration
// ---------------------------------------------------------------------------

/**
 * Run a backup if the current cycle count is a multiple of BACKUP_EVERY_N_CYCLES.
 *
 * Call this from the cron loop:
 * ```ts
 * const backupResult = runBackupIfDue(cycleCount)
 * ```
 *
 * @param cycleCount - The current cron cycle number (0, 1, 2, ...)
 * @returns The backup result if a backup was performed, or null if not due.
 */
export function runBackupIfDue(cycleCount: number): BackupResult | null {
  if (cycleCount % BACKUP_EVERY_N_CYCLES !== 0) {
    return null
  }

  log.info(`Backup due at cycle ${cycleCount} — starting...`)
  return performBackup()
}
