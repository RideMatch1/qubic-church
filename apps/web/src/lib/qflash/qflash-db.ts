/**
 * QFlash Database
 *
 * SQLite data layer for ultra-fast binary predictions.
 * Separate DB file (qflash.sqlite3) to isolate from QPredict.
 * Uses better-sqlite3 with WAL mode for concurrent reads.
 */

import Database from 'better-sqlite3'
import crypto from 'crypto'
import path from 'path'

import type {
  Round,
  RoundStatus,
  RoundDuration,
  Side,
  Outcome,
  Entry,
  EntryStatus,
  QFlashAccount,
  QFlashTransaction,
  QFlashTxType,
  QFlashTxStatus,
  PriceSnapshot,
  SnapshotType,
  QFlashLeaderboardEntry,
  QFlashStats,
  HouseLedgerEntry,
  HouseLedgerType,
  HouseStats,
} from './types'

// ---------------------------------------------------------------------------
// Database Class
// ---------------------------------------------------------------------------

const DEFAULT_DB_PATH = path.join(process.cwd(), 'qflash.sqlite3')

export class QFlashDatabase {
  private db: Database.Database
  private stmts: ReturnType<typeof this.prepareStatements> | null = null

  constructor(dbPath?: string) {
    this.db = new Database(dbPath || DEFAULT_DB_PATH)
    this.db.pragma('journal_mode = WAL')
    this.db.pragma('busy_timeout = 5000')
    this.db.pragma('foreign_keys = ON')
    this.initSchema()
  }

  // -------------------------------------------------------------------------
  // Schema
  // -------------------------------------------------------------------------

  private initSchema(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS rounds (
        id              TEXT PRIMARY KEY,
        pair            TEXT NOT NULL,
        duration_secs   INTEGER NOT NULL,
        status          TEXT NOT NULL DEFAULT 'upcoming',
        open_at         TEXT NOT NULL,
        lock_at         TEXT NOT NULL,
        close_at        TEXT NOT NULL,
        opening_price   REAL,
        closing_price   REAL,
        outcome         TEXT,
        up_pool_qu      INTEGER NOT NULL DEFAULT 0,
        down_pool_qu    INTEGER NOT NULL DEFAULT 0,
        entry_count     INTEGER NOT NULL DEFAULT 0,
        platform_fee_qu INTEGER NOT NULL DEFAULT 0,
        commitment_hash TEXT,
        resolved_at     TEXT,
        created_at      TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE INDEX IF NOT EXISTS idx_rounds_status ON rounds(status);
      CREATE INDEX IF NOT EXISTS idx_rounds_pair_status ON rounds(pair, status);
      CREATE INDEX IF NOT EXISTS idx_rounds_close_at ON rounds(close_at);

      CREATE TABLE IF NOT EXISTS entries (
        id           TEXT PRIMARY KEY,
        round_id     TEXT NOT NULL REFERENCES rounds(id),
        user_address TEXT NOT NULL,
        side         TEXT NOT NULL,
        amount_qu    INTEGER NOT NULL,
        payout_qu    INTEGER,
        status       TEXT NOT NULL DEFAULT 'active',
        is_house     INTEGER NOT NULL DEFAULT 0,
        created_at   TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE INDEX IF NOT EXISTS idx_entries_round ON entries(round_id);
      CREATE INDEX IF NOT EXISTS idx_entries_user ON entries(user_address);
      CREATE INDEX IF NOT EXISTS idx_entries_round_user ON entries(round_id, user_address);

      CREATE TABLE IF NOT EXISTS house_ledger (
        id              TEXT PRIMARY KEY,
        round_id        TEXT NOT NULL,
        entry_id        TEXT NOT NULL,
        type            TEXT NOT NULL,
        amount_qu       INTEGER NOT NULL,
        balance_after_qu INTEGER NOT NULL,
        created_at      TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE INDEX IF NOT EXISTS idx_house_ledger_round ON house_ledger(round_id);
      CREATE INDEX IF NOT EXISTS idx_house_ledger_type ON house_ledger(type);

      CREATE TABLE IF NOT EXISTS accounts (
        address          TEXT PRIMARY KEY,
        balance_qu       INTEGER NOT NULL DEFAULT 0,
        total_deposited  INTEGER NOT NULL DEFAULT 0,
        total_withdrawn  INTEGER NOT NULL DEFAULT 0,
        total_wagered    INTEGER NOT NULL DEFAULT 0,
        total_won        INTEGER NOT NULL DEFAULT 0,
        total_refunded   INTEGER NOT NULL DEFAULT 0,
        total_lost       INTEGER NOT NULL DEFAULT 0,
        win_count        INTEGER NOT NULL DEFAULT 0,
        loss_count       INTEGER NOT NULL DEFAULT 0,
        push_count       INTEGER NOT NULL DEFAULT 0,
        streak           INTEGER NOT NULL DEFAULT 0,
        best_streak      INTEGER NOT NULL DEFAULT 0,
        api_token        TEXT,
        created_at       TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS transactions (
        id         TEXT PRIMARY KEY,
        address    TEXT NOT NULL,
        type       TEXT NOT NULL,
        amount_qu  INTEGER NOT NULL,
        round_id   TEXT,
        tx_hash    TEXT,
        status     TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE INDEX IF NOT EXISTS idx_tx_address ON transactions(address);
      CREATE INDEX IF NOT EXISTS idx_tx_type ON transactions(type);

      CREATE TABLE IF NOT EXISTS price_snapshots (
        id               TEXT PRIMARY KEY,
        round_id         TEXT NOT NULL REFERENCES rounds(id),
        snapshot_type    TEXT NOT NULL,
        pair             TEXT NOT NULL,
        median_price     REAL NOT NULL,
        sources_json     TEXT NOT NULL,
        attestation_hash TEXT NOT NULL,
        created_at       TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE INDEX IF NOT EXISTS idx_snapshots_round ON price_snapshots(round_id);

      CREATE TABLE IF NOT EXISTS cron_locks (
        lock_name  TEXT PRIMARY KEY,
        owner_id   TEXT NOT NULL,
        acquired_at TEXT NOT NULL DEFAULT (datetime('now')),
        expires_at  TEXT NOT NULL
      );
    `)
  }

  // -------------------------------------------------------------------------
  // Prepared Statements (lazy-init singleton)
  // -------------------------------------------------------------------------

  private getStmts() {
    if (!this.stmts) {
      this.stmts = this.prepareStatements()
    }
    return this.stmts
  }

  private prepareStatements() {
    return {
      // Rounds
      insertRound: this.db.prepare(`
        INSERT INTO rounds (id, pair, duration_secs, status, open_at, lock_at, close_at, created_at)
        VALUES (?, ?, ?, 'upcoming', ?, ?, ?, datetime('now'))
      `),
      getRound: this.db.prepare(`SELECT * FROM rounds WHERE id = ?`),
      getRoundsByStatus: this.db.prepare(`SELECT * FROM rounds WHERE status = ? ORDER BY open_at ASC`),
      getRoundsByPairAndStatus: this.db.prepare(`SELECT * FROM rounds WHERE pair = ? AND status = ? ORDER BY open_at ASC`),
      getActiveRounds: this.db.prepare(`
        SELECT * FROM rounds WHERE status IN ('upcoming', 'open', 'locked', 'resolving')
        ORDER BY open_at ASC
      `),
      getActiveRoundsByPair: this.db.prepare(`
        SELECT * FROM rounds WHERE pair = ? AND status IN ('upcoming', 'open', 'locked', 'resolving')
        ORDER BY open_at ASC
      `),
      getActiveRoundsByPairAndDuration: this.db.prepare(`
        SELECT * FROM rounds WHERE pair = ? AND duration_secs = ? AND status IN ('upcoming', 'open', 'locked', 'resolving')
        ORDER BY open_at ASC
      `),
      getRecentResolved: this.db.prepare(`
        SELECT * FROM rounds WHERE status = 'resolved'
        ORDER BY resolved_at DESC LIMIT ?
      `),
      updateRoundStatus: this.db.prepare(`UPDATE rounds SET status = ? WHERE id = ?`),
      casUpdateRoundStatus: this.db.prepare(`UPDATE rounds SET status = ? WHERE id = ? AND status = ?`),
      updateRoundOpen: this.db.prepare(`
        UPDATE rounds SET status = 'open', opening_price = ?, commitment_hash = ? WHERE id = ?
      `),
      updateRoundLock: this.db.prepare(`UPDATE rounds SET status = 'locked' WHERE id = ?`),
      updateRoundResolve: this.db.prepare(`
        UPDATE rounds SET status = 'resolved', closing_price = ?, outcome = ?,
        platform_fee_qu = ?, resolved_at = datetime('now') WHERE id = ?
      `),
      updateRoundCancel: this.db.prepare(`
        UPDATE rounds SET status = 'cancelled', resolved_at = datetime('now') WHERE id = ?
      `),
      updateRoundPool: this.db.prepare(`
        UPDATE rounds SET up_pool_qu = up_pool_qu + ?, down_pool_qu = down_pool_qu + ?,
        entry_count = entry_count + 1 WHERE id = ?
      `),
      getUpcomingByPairDuration: this.db.prepare(`
        SELECT COUNT(*) as cnt FROM rounds
        WHERE pair = ? AND duration_secs = ? AND status IN ('upcoming', 'open')
      `),
      getRoundsToOpen: this.db.prepare(`
        SELECT * FROM rounds WHERE status = 'upcoming' AND open_at <= datetime('now')
      `),
      getRoundsToLock: this.db.prepare(`
        SELECT * FROM rounds WHERE status = 'open' AND lock_at <= datetime('now')
      `),
      getRoundsToResolve: this.db.prepare(`
        SELECT * FROM rounds WHERE status = 'locked' AND close_at <= datetime('now')
      `),
      getStaleResolvingRounds: this.db.prepare(`
        SELECT * FROM rounds WHERE status = 'resolving'
        AND close_at <= datetime('now', '-120 seconds')
      `),

      // Entries
      insertEntry: this.db.prepare(`
        INSERT INTO entries (id, round_id, user_address, side, amount_qu, status, is_house, created_at)
        VALUES (?, ?, ?, ?, ?, 'active', 0, datetime('now'))
      `),
      getEntriesByRound: this.db.prepare(`SELECT * FROM entries WHERE round_id = ?`),
      getEntriesByUser: this.db.prepare(`
        SELECT e.*, r.pair, r.duration_secs, r.outcome, r.opening_price, r.closing_price, r.status as round_status
        FROM entries e JOIN rounds r ON e.round_id = r.id
        WHERE e.user_address = ? ORDER BY e.created_at DESC LIMIT ?
      `),
      getUserEntryForRound: this.db.prepare(`
        SELECT * FROM entries WHERE round_id = ? AND user_address = ?
      `),
      updateEntryPayout: this.db.prepare(`
        UPDATE entries SET status = ?, payout_qu = ? WHERE id = ?
      `),
      updateEntriesRefund: this.db.prepare(`
        UPDATE entries SET status = 'refunded', payout_qu = amount_qu WHERE round_id = ?
      `),
      countUserRecentBets: this.db.prepare(`
        SELECT COUNT(*) as cnt FROM entries
        WHERE user_address = ? AND created_at >= datetime('now', '-1 minute')
      `),

      // Accounts
      getAccount: this.db.prepare(`SELECT * FROM accounts WHERE address = ?`),
      upsertAccount: this.db.prepare(`
        INSERT INTO accounts (address, balance_qu, created_at)
        VALUES (?, 0, datetime('now'))
        ON CONFLICT(address) DO NOTHING
      `),
      creditBalance: this.db.prepare(`
        UPDATE accounts SET balance_qu = balance_qu + ? WHERE address = ?
      `),
      debitBalance: this.db.prepare(`
        UPDATE accounts SET balance_qu = balance_qu - ? WHERE address = ?
      `),
      updateAccountDeposit: this.db.prepare(`
        UPDATE accounts SET balance_qu = balance_qu + ?, total_deposited = total_deposited + ?
        WHERE address = ?
      `),
      updateAccountWithdraw: this.db.prepare(`
        UPDATE accounts SET balance_qu = balance_qu - ?, total_withdrawn = total_withdrawn + ?
        WHERE address = ?
      `),
      updateAccountWager: this.db.prepare(`
        UPDATE accounts SET balance_qu = balance_qu - ?, total_wagered = total_wagered + ?
        WHERE address = ?
      `),
      updateAccountWin: this.db.prepare(`
        UPDATE accounts SET balance_qu = balance_qu + ?, total_won = total_won + ?,
        win_count = win_count + 1,
        streak = CASE WHEN streak >= 0 THEN streak + 1 ELSE 1 END,
        best_streak = MAX(best_streak, CASE WHEN streak >= 0 THEN streak + 1 ELSE 1 END)
        WHERE address = ?
      `),
      updateAccountLoss: this.db.prepare(`
        UPDATE accounts SET total_lost = total_lost + ?,
        loss_count = loss_count + 1,
        streak = CASE WHEN streak <= 0 THEN streak - 1 ELSE -1 END
        WHERE address = ?
      `),
      updateAccountPush: this.db.prepare(`
        UPDATE accounts SET balance_qu = balance_qu + ?,
        push_count = push_count + 1, streak = 0
        WHERE address = ?
      `),
      updateAccountRefund: this.db.prepare(`
        UPDATE accounts SET balance_qu = balance_qu + ?, total_refunded = total_refunded + ? WHERE address = ?
      `),

      // Transactions
      insertTransaction: this.db.prepare(`
        INSERT INTO transactions (id, address, type, amount_qu, round_id, tx_hash, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
      `),
      getTransactionsByAddress: this.db.prepare(`
        SELECT * FROM transactions WHERE address = ? ORDER BY created_at DESC LIMIT ?
      `),
      updateTransactionStatus: this.db.prepare(`
        UPDATE transactions SET status = ? WHERE id = ?
      `),
      getPendingWithdrawals: this.db.prepare(`
        SELECT * FROM transactions WHERE type = 'withdrawal' AND status = 'pending'
        ORDER BY created_at ASC
      `),
      getPendingDeposits: this.db.prepare(`
        SELECT * FROM transactions WHERE type = 'deposit' AND status = 'pending'
        ORDER BY created_at ASC
      `),

      // Price Snapshots
      insertSnapshot: this.db.prepare(`
        INSERT INTO price_snapshots (id, round_id, snapshot_type, pair, median_price, sources_json, attestation_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
      `),
      getSnapshotsByRound: this.db.prepare(`
        SELECT * FROM price_snapshots WHERE round_id = ? ORDER BY created_at ASC
      `),

      // Cron Locks — atomic acquire via single statement
      acquireLock: this.db.prepare(`
        INSERT INTO cron_locks (lock_name, owner_id, acquired_at, expires_at)
        VALUES (?, ?, datetime('now'), datetime('now', '+30 seconds'))
        ON CONFLICT(lock_name) DO UPDATE SET
          owner_id = excluded.owner_id,
          acquired_at = excluded.acquired_at,
          expires_at = excluded.expires_at
        WHERE expires_at <= datetime('now') OR owner_id = excluded.owner_id
      `),
      releaseLock: this.db.prepare(`
        DELETE FROM cron_locks WHERE lock_name = ? AND owner_id = ?
      `),

      // Stats
      statsQuery: this.db.prepare(`
        SELECT
          (SELECT COUNT(*) FROM rounds) as total_rounds,
          (SELECT COUNT(*) FROM rounds WHERE status IN ('upcoming','open','locked','resolving')) as active_rounds,
          (SELECT COUNT(*) FROM rounds WHERE status = 'resolved') as resolved_rounds,
          (SELECT COALESCE(SUM(up_pool_qu + down_pool_qu), 0) FROM rounds) as total_volume,
          (SELECT COUNT(*) FROM entries) as total_entries,
          (SELECT COUNT(*) FROM accounts) as total_accounts,
          (SELECT COALESCE(SUM(payout_qu), 0) FROM entries WHERE status = 'won') as total_paid_out,
          (SELECT COALESCE(SUM(platform_fee_qu), 0) FROM rounds WHERE status = 'resolved') as total_platform_fees
      `),

      // Leaderboard
      leaderboard: this.db.prepare(`
        SELECT
          a.address,
          (a.win_count + a.loss_count + a.push_count) as total_rounds,
          a.win_count as wins,
          a.loss_count as losses,
          a.push_count as pushes,
          CASE WHEN (a.win_count + a.loss_count) > 0
            THEN CAST(a.win_count AS REAL) / (a.win_count + a.loss_count) ELSE 0 END as win_rate,
          a.total_wagered,
          a.total_won,
          (a.total_won - a.total_lost) as profit_qu,
          a.best_streak
        FROM accounts a
        WHERE (a.win_count + a.loss_count + a.push_count) > 0
          AND a.address != 'HOUSE_INTERNAL'
        ORDER BY profit_qu DESC
        LIMIT ?
      `),

      // Auth tokens
      setApiToken: this.db.prepare(`UPDATE accounts SET api_token = ? WHERE address = ?`),
      getAccountByToken: this.db.prepare(`SELECT * FROM accounts WHERE api_token = ?`),

      // House Bank
      insertHouseEntry: this.db.prepare(`
        INSERT INTO entries (id, round_id, user_address, side, amount_qu, status, is_house, created_at)
        VALUES (?, ?, 'HOUSE_INTERNAL', ?, ?, 'active', 1, datetime('now'))
      `),
      insertHouseLedger: this.db.prepare(`
        INSERT INTO house_ledger (id, round_id, entry_id, type, amount_qu, balance_after_qu, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
      `),
      getHouseExposureForRound: this.db.prepare(`
        SELECT COALESCE(SUM(amount_qu), 0) as exposure
        FROM entries WHERE round_id = ? AND is_house = 1 AND status = 'active'
      `),
      getHouseTotalExposure: this.db.prepare(`
        SELECT COALESCE(SUM(e.amount_qu), 0) as exposure
        FROM entries e JOIN rounds r ON e.round_id = r.id
        WHERE e.is_house = 1 AND e.status = 'active'
        AND r.status IN ('open', 'locked', 'resolving')
      `),
      getHouseRecentLedger: this.db.prepare(`
        SELECT * FROM house_ledger ORDER BY created_at DESC LIMIT ?
      `),
      getHouseStats: this.db.prepare(`
        SELECT
          (SELECT COALESCE(SUM(amount_qu), 0) FROM house_ledger WHERE type = 'win') as total_won,
          (SELECT COALESCE(SUM(amount_qu), 0) FROM house_ledger WHERE type = 'loss') as total_lost,
          (SELECT COALESCE(SUM(amount_qu), 0) FROM house_ledger WHERE type = 'fee_income') as fee_income,
          (SELECT COUNT(*) FROM house_ledger WHERE type = 'match_bet') as rounds_played,
          (SELECT COUNT(*) FROM house_ledger WHERE type = 'win') as wins,
          (SELECT COUNT(*) FROM house_ledger WHERE type = 'loss') as losses
      `),
    }
  }

  // -------------------------------------------------------------------------
  // Round Operations
  // -------------------------------------------------------------------------

  createRound(
    pair: string,
    durationSecs: RoundDuration,
    openAt: string,
    lockAt: string,
    closeAt: string,
  ): Round {
    const id = `r_${crypto.randomBytes(12).toString('hex')}`
    this.getStmts().insertRound.run(id, pair, durationSecs, openAt, lockAt, closeAt)
    return this.getRound(id)!
  }

  getRound(id: string): Round | null {
    const row = this.getStmts().getRound.get(id) as Record<string, unknown> | undefined
    return row ? this.mapRound(row) : null
  }

  getRoundsByStatus(status: RoundStatus): Round[] {
    const rows = this.getStmts().getRoundsByStatus.all(status) as Record<string, unknown>[]
    return rows.map((r) => this.mapRound(r))
  }

  getActiveRounds(pair?: string, duration?: RoundDuration): Round[] {
    let rows: Record<string, unknown>[]
    if (pair && duration) {
      rows = this.getStmts().getActiveRoundsByPairAndDuration.all(pair, duration) as Record<string, unknown>[]
    } else if (pair) {
      rows = this.getStmts().getActiveRoundsByPair.all(pair) as Record<string, unknown>[]
    } else {
      rows = this.getStmts().getActiveRounds.all() as Record<string, unknown>[]
    }
    return rows.map((r) => this.mapRound(r))
  }

  getRecentResolved(limit: number = 20): Round[] {
    const rows = this.getStmts().getRecentResolved.all(limit) as Record<string, unknown>[]
    return rows.map((r) => this.mapRound(r))
  }

  getUpcomingCountForPairDuration(pair: string, duration: RoundDuration): number {
    const row = this.getStmts().getUpcomingByPairDuration.get(pair, duration) as { cnt: number }
    return row.cnt
  }

  getRoundsToOpen(): Round[] {
    const rows = this.getStmts().getRoundsToOpen.all() as Record<string, unknown>[]
    return rows.map((r) => this.mapRound(r))
  }

  getRoundsToLock(): Round[] {
    const rows = this.getStmts().getRoundsToLock.all() as Record<string, unknown>[]
    return rows.map((r) => this.mapRound(r))
  }

  getRoundsToResolve(): Round[] {
    const rows = this.getStmts().getRoundsToResolve.all() as Record<string, unknown>[]
    return rows.map((r) => this.mapRound(r))
  }

  getStaleResolvingRounds(): Round[] {
    const rows = this.getStmts().getStaleResolvingRounds.all() as Record<string, unknown>[]
    return rows.map((r) => this.mapRound(r))
  }

  updateRoundStatus(id: string, status: RoundStatus): void {
    this.getStmts().updateRoundStatus.run(status, id)
  }

  /**
   * Compare-and-swap status update. Returns true if the update was applied
   * (i.e., the round was in the expected state).
   */
  casUpdateRoundStatus(id: string, newStatus: RoundStatus, expectedStatus: RoundStatus): boolean {
    const result = this.getStmts().casUpdateRoundStatus.run(newStatus, id, expectedStatus)
    return result.changes > 0
  }

  openRound(id: string, openingPrice: number, commitmentHash: string): void {
    this.getStmts().updateRoundOpen.run(openingPrice, commitmentHash, id)
  }

  lockRound(id: string): void {
    this.getStmts().updateRoundLock.run(id)
  }

  resolveRound(id: string, closingPrice: number, outcome: Outcome, platformFeeQu: number): void {
    this.getStmts().updateRoundResolve.run(closingPrice, outcome, platformFeeQu, id)
  }

  cancelRound(id: string): void {
    this.getStmts().updateRoundCancel.run(id)
  }

  addToPool(id: string, side: Side, amountQu: number): void {
    const upAdd = side === 'up' ? amountQu : 0
    const downAdd = side === 'down' ? amountQu : 0
    this.getStmts().updateRoundPool.run(upAdd, downAdd, id)
  }

  // -------------------------------------------------------------------------
  // Entry Operations
  // -------------------------------------------------------------------------

  createEntry(roundId: string, userAddress: string, side: Side, amountQu: number): Entry {
    const id = `e_${crypto.randomBytes(12).toString('hex')}`
    this.getStmts().insertEntry.run(id, roundId, userAddress, side, amountQu)
    return this.mapEntry(this.getStmts().getEntriesByRound.all(roundId).find((e: unknown) => (e as Record<string, unknown>).id === id) as Record<string, unknown>)
  }

  getEntriesByRound(roundId: string): Entry[] {
    const rows = this.getStmts().getEntriesByRound.all(roundId) as Record<string, unknown>[]
    return rows.map((r) => this.mapEntry(r))
  }

  getUserEntryForRound(roundId: string, userAddress: string): Entry | null {
    const row = this.getStmts().getUserEntryForRound.get(roundId, userAddress) as Record<string, unknown> | undefined
    return row ? this.mapEntry(row) : null
  }

  getUserEntries(userAddress: string, limit: number = 50): (Entry & { pair: string; durationSecs: number; outcome: string | null; openingPrice: number | null; closingPrice: number | null; roundStatus: string })[] {
    const rows = this.getStmts().getEntriesByUser.all(userAddress, limit) as Record<string, unknown>[]
    return rows.map((r) => ({
      ...this.mapEntry(r),
      pair: r.pair as string,
      durationSecs: r.duration_secs as number,
      outcome: r.outcome as string | null,
      openingPrice: r.opening_price as number | null,
      closingPrice: r.closing_price as number | null,
      roundStatus: r.round_status as string,
    }))
  }

  updateEntryPayout(id: string, status: EntryStatus, payoutQu: number): void {
    this.getStmts().updateEntryPayout.run(status, payoutQu, id)
  }

  refundAllEntries(roundId: string): void {
    this.getStmts().updateEntriesRefund.run(roundId)
  }

  countUserRecentBets(userAddress: string): number {
    const row = this.getStmts().countUserRecentBets.get(userAddress) as { cnt: number }
    return row.cnt
  }

  // -------------------------------------------------------------------------
  // Account Operations
  // -------------------------------------------------------------------------

  getAccount(address: string): QFlashAccount | null {
    const row = this.getStmts().getAccount.get(address) as Record<string, unknown> | undefined
    return row ? this.mapAccount(row) : null
  }

  ensureAccount(address: string): QFlashAccount {
    this.getStmts().upsertAccount.run(address)
    return this.getAccount(address)!
  }

  creditDeposit(address: string, amountQu: number): void {
    this.ensureAccount(address)
    this.getStmts().updateAccountDeposit.run(amountQu, amountQu, address)
  }

  debitWithdrawal(address: string, amountQu: number): void {
    this.getStmts().updateAccountWithdraw.run(amountQu, amountQu, address)
  }

  debitWager(address: string, amountQu: number): void {
    this.getStmts().updateAccountWager.run(amountQu, amountQu, address)
  }

  creditWin(address: string, amountQu: number): void {
    this.getStmts().updateAccountWin.run(amountQu, amountQu, address)
  }

  recordLoss(address: string, amountQu: number): void {
    this.getStmts().updateAccountLoss.run(amountQu, address)
  }

  creditPush(address: string, amountQu: number): void {
    this.getStmts().updateAccountPush.run(amountQu, address)
  }

  creditRefund(address: string, amountQu: number): void {
    this.getStmts().updateAccountRefund.run(amountQu, amountQu, address)
  }

  // -------------------------------------------------------------------------
  // Auth Token Operations
  // -------------------------------------------------------------------------

  setApiToken(address: string, token: string): void {
    this.getStmts().setApiToken.run(token, address)
  }

  getAccountByToken(token: string): QFlashAccount | null {
    const row = this.getStmts().getAccountByToken.get(token) as Record<string, unknown> | undefined
    return row ? this.mapAccount(row) : null
  }

  // -------------------------------------------------------------------------
  // Transaction Operations
  // -------------------------------------------------------------------------

  createTransaction(
    address: string,
    type: QFlashTxType,
    amountQu: number,
    roundId?: string,
    txHash?: string,
    status: QFlashTxStatus = 'pending',
  ): QFlashTransaction {
    const id = `tx_${crypto.randomBytes(12).toString('hex')}`
    this.getStmts().insertTransaction.run(id, address, type, amountQu, roundId ?? null, txHash ?? null, status)
    return {
      id,
      address,
      type,
      amountQu,
      roundId: roundId ?? null,
      txHash: txHash ?? null,
      status,
      createdAt: new Date().toISOString(),
    }
  }

  getTransactionsByAddress(address: string, limit: number = 50): QFlashTransaction[] {
    const rows = this.getStmts().getTransactionsByAddress.all(address, limit) as Record<string, unknown>[]
    return rows.map((r) => this.mapTransaction(r))
  }

  updateTransactionStatus(id: string, status: QFlashTxStatus): void {
    this.getStmts().updateTransactionStatus.run(status, id)
  }

  getPendingWithdrawals(): QFlashTransaction[] {
    const rows = this.getStmts().getPendingWithdrawals.all() as Record<string, unknown>[]
    return rows.map((r) => this.mapTransaction(r))
  }

  // -------------------------------------------------------------------------
  // Price Snapshots
  // -------------------------------------------------------------------------

  createSnapshot(
    roundId: string,
    snapshotType: SnapshotType,
    pair: string,
    medianPrice: number,
    sourcesJson: string,
    attestationHash: string,
  ): void {
    const id = `snap_${crypto.randomBytes(12).toString('hex')}`
    this.getStmts().insertSnapshot.run(id, roundId, snapshotType, pair, medianPrice, sourcesJson, attestationHash)
  }

  getSnapshotsByRound(roundId: string): PriceSnapshot[] {
    const rows = this.getStmts().getSnapshotsByRound.all(roundId) as Record<string, unknown>[]
    return rows.map((r) => ({
      id: r.id as string,
      roundId: r.round_id as string,
      snapshotType: r.snapshot_type as SnapshotType,
      pair: r.pair as string,
      medianPrice: r.median_price as number,
      sourcesJson: r.sources_json as string,
      attestationHash: r.attestation_hash as string,
      createdAt: r.created_at as string,
    }))
  }

  // -------------------------------------------------------------------------
  // Cron Lock
  // -------------------------------------------------------------------------

  acquireCronLock(lockName: string, ownerId: string): boolean {
    // Atomic CAS: only acquires if lock is expired or owned by us
    const result = this.getStmts().acquireLock.run(lockName, ownerId)
    return result.changes > 0
  }

  releaseCronLock(lockName: string, ownerId: string): void {
    this.getStmts().releaseLock.run(lockName, ownerId)
  }

  // -------------------------------------------------------------------------
  // Stats & Leaderboard
  // -------------------------------------------------------------------------

  getStats(): QFlashStats {
    const row = this.getStmts().statsQuery.get() as Record<string, unknown>
    const totalRounds = (row.total_rounds as number) || 0
    const resolvedRounds = (row.resolved_rounds as number) || 0
    const totalVolume = (row.total_volume as number) || 0
    return {
      totalRounds,
      activeRounds: (row.active_rounds as number) || 0,
      resolvedRounds,
      totalVolume,
      totalEntries: (row.total_entries as number) || 0,
      totalAccounts: (row.total_accounts as number) || 0,
      totalPaidOut: (row.total_paid_out as number) || 0,
      totalPlatformFees: (row.total_platform_fees as number) || 0,
      avgRoundPool: resolvedRounds > 0 ? Math.round(totalVolume / totalRounds) : 0,
    }
  }

  getLeaderboard(limit: number = 50): QFlashLeaderboardEntry[] {
    const rows = this.getStmts().leaderboard.all(limit) as Record<string, unknown>[]
    return rows.map((r) => ({
      address: r.address as string,
      totalRounds: r.total_rounds as number,
      wins: r.wins as number,
      losses: r.losses as number,
      pushes: r.pushes as number,
      winRate: r.win_rate as number,
      totalWagered: r.total_wagered as number,
      totalWon: r.total_won as number,
      profitQu: r.profit_qu as number,
      bestStreak: r.best_streak as number,
    }))
  }

  // -------------------------------------------------------------------------
  // Atomic wager: debit balance + create entry + update pool in one TX
  // -------------------------------------------------------------------------

  placeWager(
    roundId: string,
    userAddress: string,
    side: Side,
    amountQu: number,
  ): { entry: Entry; newBalance: number } {
    const txn = this.db.transaction(() => {
      // Check balance
      const account = this.getAccount(userAddress)
      if (!account) throw new Error('Account not found')
      if (account.balanceQu < amountQu) throw new Error('Insufficient balance')

      // Check round is open
      const round = this.getRound(roundId)
      if (!round) throw new Error('Round not found')
      if (round.status !== 'open') throw new Error(`Round is not open (status: ${round.status})`)

      // Check existing entry
      const existing = this.getUserEntryForRound(roundId, userAddress)
      if (existing) throw new Error('Already placed a bet in this round')

      // Debit balance
      this.debitWager(userAddress, amountQu)

      // Create entry
      const entry = this.createEntry(roundId, userAddress, side, amountQu)

      // Update pool
      this.addToPool(roundId, side, amountQu)

      // Create transaction record
      this.createTransaction(userAddress, 'wager', amountQu, roundId, undefined, 'confirmed')

      const updatedAccount = this.getAccount(userAddress)!
      return { entry, newBalance: updatedAccount.balanceQu }
    })

    return txn()
  }

  // -------------------------------------------------------------------------
  // Atomic settlement: credit winners, debit fees, update entries
  // -------------------------------------------------------------------------

  settleRound(roundId: string, outcome: Outcome, platformFeeQu: number): {
    winnersCount: number
    losersCount: number
    totalPayout: number
  } {
    const txn = this.db.transaction(() => {
      const allEntries = this.getEntriesByRound(roundId)
      const round = this.getRound(roundId)
      if (!round) throw new Error('Round not found')

      // IDEMPOTENCY: only settle entries still in 'active' status
      const entries = allEntries.filter((e) => e.status === 'active')
      if (entries.length === 0) {
        return { winnersCount: 0, losersCount: 0, totalPayout: 0 }
      }

      // Push = refund everyone (including house entries)
      if (outcome === 'push') {
        for (const entry of entries) {
          if (entry.isHouse) {
            // Refund house balance
            this.creditRefund('HOUSE_INTERNAL', entry.amountQu)
            this.updateEntryPayout(entry.id, 'push', entry.amountQu)
            const houseAccount = this.getAccount('HOUSE_INTERNAL')
            this.recordHouseLedger(roundId, entry.id, 'refund', entry.amountQu, houseAccount?.balanceQu ?? 0)
          } else {
            this.creditPush(entry.userAddress, entry.amountQu)
            this.updateEntryPayout(entry.id, 'push', entry.amountQu)
            this.createTransaction(entry.userAddress, 'refund', entry.amountQu, roundId, undefined, 'confirmed')
          }
        }
        return { winnersCount: 0, losersCount: 0, totalPayout: entries.reduce((s, e) => s + e.amountQu, 0) }
      }

      const winningSide: Side = outcome
      const winners = entries.filter((e) => e.side === winningSide)
      const losers = entries.filter((e) => e.side !== winningSide)

      // One-sided round with NO house entries: refund all (legacy behavior)
      const hasHouseEntries = entries.some((e) => e.isHouse)
      if ((winners.length === 0 || losers.length === 0) && !hasHouseEntries) {
        for (const entry of entries) {
          this.creditRefund(entry.userAddress, entry.amountQu)
          this.updateEntryPayout(entry.id, 'refunded', entry.amountQu)
          this.createTransaction(entry.userAddress, 'refund', entry.amountQu, roundId, undefined, 'confirmed')
        }
        return { winnersCount: 0, losersCount: 0, totalPayout: entries.reduce((s, e) => s + e.amountQu, 0) }
      }

      // If one side is empty but has house entries, that shouldn't happen (house always takes opposite)
      // Safety: if still one-sided, refund all including house
      if (winners.length === 0 || losers.length === 0) {
        for (const entry of entries) {
          if (entry.isHouse) {
            this.creditRefund('HOUSE_INTERNAL', entry.amountQu)
            this.updateEntryPayout(entry.id, 'refunded', entry.amountQu)
            const houseAccount = this.getAccount('HOUSE_INTERNAL')
            this.recordHouseLedger(roundId, entry.id, 'refund', entry.amountQu, houseAccount?.balanceQu ?? 0)
          } else {
            this.creditRefund(entry.userAddress, entry.amountQu)
            this.updateEntryPayout(entry.id, 'refunded', entry.amountQu)
            this.createTransaction(entry.userAddress, 'refund', entry.amountQu, roundId, undefined, 'confirmed')
          }
        }
        return { winnersCount: 0, losersCount: 0, totalPayout: entries.reduce((s, e) => s + e.amountQu, 0) }
      }

      const winnerPool = winners.reduce((s, e) => s + e.amountQu, 0)
      const loserPool = losers.reduce((s, e) => s + e.amountQu, 0)
      const netLoserPool = loserPool - platformFeeQu
      let totalPayout = 0

      // Credit winners proportionally (both user and house)
      for (const entry of winners) {
        const share = entry.amountQu / winnerPool
        const payout = entry.amountQu + Math.floor(netLoserPool * share)

        if (entry.isHouse) {
          // House wins: credit house account
          this.creditWin('HOUSE_INTERNAL', payout)
          this.updateEntryPayout(entry.id, 'won', payout)
          const houseAccount = this.getAccount('HOUSE_INTERNAL')
          this.recordHouseLedger(roundId, entry.id, 'win', payout, houseAccount?.balanceQu ?? 0)
        } else {
          this.creditWin(entry.userAddress, payout)
          this.updateEntryPayout(entry.id, 'won', payout)
          this.createTransaction(entry.userAddress, 'payout', payout, roundId, undefined, 'confirmed')
        }
        totalPayout += payout
      }

      // Record losses (both user and house)
      for (const entry of losers) {
        if (entry.isHouse) {
          this.recordLoss('HOUSE_INTERNAL', entry.amountQu)
          this.updateEntryPayout(entry.id, 'lost', 0)
          const houseAccount = this.getAccount('HOUSE_INTERNAL')
          this.recordHouseLedger(roundId, entry.id, 'loss', entry.amountQu, houseAccount?.balanceQu ?? 0)
        } else {
          this.recordLoss(entry.userAddress, entry.amountQu)
          this.updateEntryPayout(entry.id, 'lost', 0)
        }
      }

      // Platform fee transaction
      if (platformFeeQu > 0) {
        this.createTransaction('PLATFORM', 'platform_fee', platformFeeQu, roundId, undefined, 'confirmed')
      }

      return { winnersCount: winners.length, losersCount: losers.length, totalPayout }
    })

    return txn()
  }

  // -------------------------------------------------------------------------
  // Row Mappers
  // -------------------------------------------------------------------------

  private mapRound(row: Record<string, unknown>): Round {
    return {
      id: row.id as string,
      pair: row.pair as string,
      durationSecs: row.duration_secs as RoundDuration,
      status: row.status as RoundStatus,
      openAt: row.open_at as string,
      lockAt: row.lock_at as string,
      closeAt: row.close_at as string,
      openingPrice: row.opening_price as number | null,
      closingPrice: row.closing_price as number | null,
      outcome: row.outcome as Outcome | null,
      upPoolQu: row.up_pool_qu as number,
      downPoolQu: row.down_pool_qu as number,
      entryCount: row.entry_count as number,
      platformFeeQu: row.platform_fee_qu as number,
      commitmentHash: row.commitment_hash as string | null,
      resolvedAt: row.resolved_at as string | null,
      createdAt: row.created_at as string,
    }
  }

  private mapEntry(row: Record<string, unknown>): Entry {
    return {
      id: row.id as string,
      roundId: row.round_id as string,
      userAddress: row.user_address as string,
      side: row.side as Side,
      amountQu: row.amount_qu as number,
      payoutQu: row.payout_qu as number | null,
      status: row.status as EntryStatus,
      isHouse: (row.is_house as number) === 1,
      createdAt: row.created_at as string,
    }
  }

  private mapAccount(row: Record<string, unknown>): QFlashAccount {
    return {
      address: row.address as string,
      balanceQu: row.balance_qu as number,
      totalDeposited: row.total_deposited as number,
      totalWithdrawn: row.total_withdrawn as number,
      totalWagered: row.total_wagered as number,
      totalWon: row.total_won as number,
      totalRefunded: (row.total_refunded as number) || 0,
      totalLost: row.total_lost as number,
      winCount: row.win_count as number,
      lossCount: row.loss_count as number,
      pushCount: row.push_count as number,
      streak: row.streak as number,
      bestStreak: row.best_streak as number,
      apiToken: (row.api_token as string) || null,
      createdAt: row.created_at as string,
    }
  }

  private mapTransaction(row: Record<string, unknown>): QFlashTransaction {
    return {
      id: row.id as string,
      address: row.address as string,
      type: row.type as QFlashTxType,
      amountQu: row.amount_qu as number,
      roundId: row.round_id as string | null,
      txHash: row.tx_hash as string | null,
      status: row.status as QFlashTxStatus,
      createdAt: row.created_at as string,
    }
  }

  // -------------------------------------------------------------------------
  // House Bank Operations
  // -------------------------------------------------------------------------

  createHouseEntry(roundId: string, side: Side, amountQu: number): Entry {
    const id = `e_h_${crypto.randomBytes(12).toString('hex')}`
    this.getStmts().insertHouseEntry.run(id, roundId, side, amountQu)
    // Update round pool
    this.addToPool(roundId, side, amountQu)
    // Return mapped entry
    const rows = this.getStmts().getEntriesByRound.all(roundId) as Record<string, unknown>[]
    const row = rows.find((r) => (r as Record<string, unknown>).id === id)
    return this.mapEntry(row as Record<string, unknown>)
  }

  recordHouseLedger(
    roundId: string,
    entryId: string,
    type: HouseLedgerType,
    amountQu: number,
    balanceAfterQu: number,
  ): void {
    const id = `hl_${crypto.randomBytes(12).toString('hex')}`
    this.getStmts().insertHouseLedger.run(id, roundId, entryId, type, amountQu, balanceAfterQu)
  }

  getHouseExposureForRound(roundId: string): number {
    const row = this.getStmts().getHouseExposureForRound.get(roundId) as { exposure: number }
    return row.exposure
  }

  getHouseTotalExposure(): number {
    const row = this.getStmts().getHouseTotalExposure.get() as { exposure: number }
    return row.exposure
  }

  getHouseRecentLedger(limit: number = 50): HouseLedgerEntry[] {
    const rows = this.getStmts().getHouseRecentLedger.all(limit) as Record<string, unknown>[]
    return rows.map((r) => ({
      id: r.id as string,
      roundId: r.round_id as string,
      entryId: r.entry_id as string,
      type: r.type as HouseLedgerType,
      amountQu: r.amount_qu as number,
      balanceAfterQu: r.balance_after_qu as number,
      createdAt: r.created_at as string,
    }))
  }

  getHouseStats(): HouseStats {
    const account = this.getAccount('HOUSE_INTERNAL')
    const balanceQu = account?.balanceQu ?? 0
    const totalExposureQu = this.getHouseTotalExposure()
    const row = this.getStmts().getHouseStats.get() as Record<string, unknown>
    const recentLedger = this.getHouseRecentLedger(50)

    return {
      balanceQu,
      totalExposureQu,
      roundsPlayed: (row.rounds_played as number) || 0,
      wins: (row.wins as number) || 0,
      losses: (row.losses as number) || 0,
      totalWonQu: (row.total_won as number) || 0,
      totalLostQu: (row.total_lost as number) || 0,
      netPnlQu: ((row.total_won as number) || 0) - ((row.total_lost as number) || 0),
      feeIncomeQu: (row.fee_income as number) || 0,
      recentLedger,
    }
  }

  // -------------------------------------------------------------------------
  // Cleanup
  // -------------------------------------------------------------------------

  close(): void {
    this.db.close()
  }
}

// ---------------------------------------------------------------------------
// Singleton
// ---------------------------------------------------------------------------

let _instance: QFlashDatabase | null = null

export function getQFlashDB(): QFlashDatabase {
  if (!_instance) {
    _instance = new QFlashDatabase()
  }
  return _instance
}
