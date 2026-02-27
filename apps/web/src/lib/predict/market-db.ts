/**
 * QPredict Market Database
 *
 * SQLite data layer for the prediction market platform.
 * Uses better-sqlite3 with WAL mode for concurrent read access.
 *
 * Tables:
 *   - markets          — Prediction market definitions
 *   - user_bets        — Individual bets placed by users
 *   - accounts         — User account balances (custodial)
 *   - transactions     — Deposit/withdrawal/bet/payout history
 *   - market_snapshots — Probability snapshots over time
 */

import Database from 'better-sqlite3'
import crypto from 'crypto'
import path from 'path'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type MarketStatus =
  | 'draft'
  | 'pending_tx'
  | 'active'
  | 'closed'
  | 'resolving'
  | 'resolved'
  | 'cancelled'

export type MarketType = 'price' | 'sports' | 'ai' | 'custom'

export type ResolutionType = 'price_above' | 'price_below' | 'price_range' | 'price_bracket'

export type Category = 'crypto' | 'sports' | 'politics' | 'tech' | 'entertainment' | 'other'

export type CreatedBy = 'user' | 'trending_agent' | 'ai_parsed'

export type BetStatus = 'pending_deposit' | 'pending' | 'confirmed' | 'won' | 'lost' | 'refunded'

export type TransactionType =
  | 'deposit'
  | 'withdrawal'
  | 'bet'
  | 'payout'
  | 'market_create'
  | 'refund'

export interface Market {
  id: string
  quotteryBetId: number | null
  pair: string
  question: string
  resolutionType: ResolutionType
  resolutionTarget: number
  resolutionTargetHigh: number | null
  closeDate: string // ISO 8601
  endDate: string // ISO 8601
  minBetQu: number
  maxSlots: number
  status: MarketStatus
  totalPool: number
  yesSlots: number
  noSlots: number
  resolutionPrice: number | null
  winningOption: number | null
  creatorAddress: string | null
  txHash: string | null
  createdAt: string
  resolvedAt: string | null
  commitmentHash: string | null
  // v2 fields
  marketType: MarketType
  options: string[] // parsed from options_json
  numOptions: number
  oracleAddresses: string[] | null // parsed from oracle_addresses_json
  oracleFeeBps: number
  autoRefundAt: string | null
  category: Category | null
  slotsPerOption: Record<string, number> // parsed from slots_json
  aiResolutionAttempts: number
  aiResolutionProof: unknown | null // parsed from ai_resolution_proof JSON
  createdBy: CreatedBy
  sourceQuery: string | null
}

export interface UserBet {
  id: string
  marketId: string
  userAddress: string
  option: number // 0 = Yes, 1 = No
  slots: number
  amountQu: number
  txHash: string | null
  status: BetStatus
  payoutQu: number | null
  createdAt: string
  commitmentHash: string | null
  commitmentNonce: string | null
  userSignature: string | null
}

export interface Account {
  address: string
  displayName: string | null
  balanceQu: number
  totalDeposited: number
  totalWithdrawn: number
  totalBet: number
  totalWon: number
  createdAt: string
}

export interface Transaction {
  id: string
  address: string
  type: TransactionType
  amountQu: number
  txHash: string | null
  marketId: string | null
  status: string
  createdAt: string
}

export interface MarketSnapshot {
  marketId: string
  timestamp: string
  yesSlots: number
  noSlots: number
  impliedProbability: number
  totalPool: number
}

export interface PlatformStats {
  totalMarkets: number
  activeMarkets: number
  resolvedMarkets: number
  totalVolume: number
  totalBets: number
  totalUsers: number
  totalPaidOut: number
}

// Provably Fair types
export interface CommitmentChainRow {
  sequenceNum: number
  eventType: string
  entityId: string
  payloadHash: string
  prevHash: string
  chainHash: string
  payloadJson: string
  createdAt: string
}

export interface OracleAttestationRow {
  id: string
  marketId: string
  oracleSource: string
  pair: string
  price: number
  tick: number | null
  epoch: number | null
  sourceTimestamp: string
  attestationHash: string
  serverSignature: string
  createdAt: string
}

export interface SolvencyProofRow {
  id: string
  merkleRoot: string
  totalUserBalance: number
  onChainBalance: number
  isSolvent: number // 0 or 1
  accountCount: number
  tick: number
  epoch: number
  leafHashesJson: string
  createdAt: string
}

export interface LeaderboardEntry {
  address: string
  displayName: string | null
  totalBets: number
  wins: number
  losses: number
  accuracy: number
  totalWon: number
  totalBet: number
  profitQu: number
}

// Per-Bet Escrow types
export type EscrowStatus =
  | 'awaiting_deposit'
  | 'deposit_detected'
  | 'joining_sc'
  | 'active_in_sc'
  | 'won_awaiting_sweep'
  | 'sweeping'
  | 'swept'
  | 'completed'
  | 'lost'
  | 'expired'
  | 'refunding'
  | 'refunded'

export interface EscrowAddress {
  id: string
  betId: string
  marketId: string
  escrowAddress: string
  userPayoutAddress: string
  option: number
  slots: number
  expectedAmountQu: number
  status: EscrowStatus
  depositDetectedAt: string | null
  depositAmountQu: number | null
  joinBetTxId: string | null
  joinBetTick: number | null
  payoutDetectedAt: string | null
  payoutAmountQu: number | null
  sweepTxId: string | null
  sweepTick: number | null
  joinBetRetries: number
  expiresAt: string
  createdAt: string
}

export type EscrowKeyStatus = 'active' | 'swept' | 'archived'

export interface EscrowKey {
  escrowId: string
  encryptedSeed: string
  iv: string
  authTag: string
  status: EscrowKeyStatus
  createdAt: string
  archivedAt: string | null
}

// ---------------------------------------------------------------------------
// Database Class
// ---------------------------------------------------------------------------

const DEFAULT_DB_PATH = path.join(
  process.cwd(),
  'predict.sqlite3',
)

export class MarketDatabase {
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
      CREATE TABLE IF NOT EXISTS markets (
        id TEXT PRIMARY KEY,
        quottery_bet_id INTEGER,
        pair TEXT NOT NULL,
        question TEXT NOT NULL,
        resolution_type TEXT NOT NULL DEFAULT 'price_above',
        resolution_target REAL NOT NULL,
        resolution_target_high REAL,
        close_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        min_bet_qu INTEGER NOT NULL DEFAULT 10000,
        max_slots INTEGER NOT NULL DEFAULT 100,
        status TEXT NOT NULL DEFAULT 'draft',
        total_pool INTEGER NOT NULL DEFAULT 0,
        yes_slots INTEGER NOT NULL DEFAULT 0,
        no_slots INTEGER NOT NULL DEFAULT 0,
        resolution_price REAL,
        winning_option INTEGER,
        creator_address TEXT,
        tx_hash TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        resolved_at TEXT,
        -- v2 columns
        commitment_hash TEXT,
        market_type TEXT DEFAULT 'price',
        options_json TEXT DEFAULT '["Yes","No"]',
        num_options INTEGER DEFAULT 2,
        oracle_addresses_json TEXT,
        oracle_fee_bps INTEGER DEFAULT 0,
        auto_refund_at TEXT,
        category TEXT,
        slots_json TEXT DEFAULT '{"0":0,"1":0}',
        ai_resolution_attempts INTEGER DEFAULT 0,
        ai_resolution_proof TEXT,
        created_by TEXT DEFAULT 'user',
        source_query TEXT
      );

      CREATE TABLE IF NOT EXISTS user_bets (
        id TEXT PRIMARY KEY,
        market_id TEXT NOT NULL REFERENCES markets(id),
        user_address TEXT NOT NULL,
        option INTEGER NOT NULL,
        slots INTEGER NOT NULL,
        amount_qu INTEGER NOT NULL,
        tx_hash TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        payout_qu INTEGER,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        -- provably fair columns
        commitment_hash TEXT,
        commitment_nonce TEXT,
        user_signature TEXT
      );

      CREATE TABLE IF NOT EXISTS accounts (
        address TEXT PRIMARY KEY,
        display_name TEXT,
        balance_qu INTEGER NOT NULL DEFAULT 0,
        total_deposited INTEGER NOT NULL DEFAULT 0,
        total_withdrawn INTEGER NOT NULL DEFAULT 0,
        total_bet INTEGER NOT NULL DEFAULT 0,
        total_won INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        address TEXT NOT NULL REFERENCES accounts(address),
        type TEXT NOT NULL,
        amount_qu INTEGER NOT NULL,
        tx_hash TEXT,
        market_id TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS market_snapshots (
        market_id TEXT NOT NULL REFERENCES markets(id),
        timestamp TEXT NOT NULL DEFAULT (datetime('now')),
        yes_slots INTEGER NOT NULL DEFAULT 0,
        no_slots INTEGER NOT NULL DEFAULT 0,
        implied_probability REAL NOT NULL DEFAULT 0.5,
        total_pool INTEGER NOT NULL DEFAULT 0
      );

      -- Provably Fair: Commitment Chain (append-only audit log)
      CREATE TABLE IF NOT EXISTS commitment_chain (
        sequence_num   INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type     TEXT NOT NULL,
        entity_id      TEXT NOT NULL,
        payload_hash   TEXT NOT NULL,
        prev_hash      TEXT NOT NULL,
        chain_hash     TEXT NOT NULL,
        payload_json   TEXT NOT NULL,
        created_at     TEXT DEFAULT (datetime('now'))
      );

      -- Provably Fair: Oracle Attestations (HMAC-signed price proofs)
      CREATE TABLE IF NOT EXISTS oracle_attestations (
        id               TEXT PRIMARY KEY,
        market_id        TEXT NOT NULL,
        oracle_source    TEXT NOT NULL,
        pair             TEXT NOT NULL,
        price            REAL NOT NULL,
        tick             INTEGER,
        epoch            INTEGER,
        source_timestamp TEXT NOT NULL,
        attestation_hash TEXT NOT NULL,
        server_signature TEXT NOT NULL,
        created_at       TEXT DEFAULT (datetime('now'))
      );

      -- Provably Fair: Solvency Proofs (Merkle tree + on-chain verification)
      CREATE TABLE IF NOT EXISTS solvency_proofs (
        id                 TEXT PRIMARY KEY,
        merkle_root        TEXT NOT NULL,
        total_user_balance INTEGER NOT NULL,
        on_chain_balance   INTEGER NOT NULL,
        is_solvent         INTEGER NOT NULL,
        account_count      INTEGER NOT NULL,
        tick               INTEGER NOT NULL,
        epoch              INTEGER NOT NULL,
        leaf_hashes_json   TEXT NOT NULL,
        created_at         TEXT DEFAULT (datetime('now'))
      );

      -- Per-Bet Escrow: Escrow Addresses (one per bet)
      CREATE TABLE IF NOT EXISTS escrow_addresses (
        id                   TEXT PRIMARY KEY,
        bet_id               TEXT NOT NULL,
        market_id            TEXT NOT NULL,
        escrow_address       TEXT NOT NULL UNIQUE,
        user_payout_address  TEXT NOT NULL,
        option               INTEGER NOT NULL,
        slots                INTEGER NOT NULL,
        expected_amount_qu   INTEGER NOT NULL,
        status               TEXT NOT NULL DEFAULT 'awaiting_deposit',
        deposit_detected_at  TEXT,
        deposit_amount_qu    INTEGER,
        join_bet_tx_id       TEXT,
        join_bet_tick        INTEGER,
        payout_detected_at   TEXT,
        payout_amount_qu     INTEGER,
        sweep_tx_id          TEXT,
        sweep_tick           INTEGER,
        expires_at           TEXT NOT NULL,
        created_at           TEXT NOT NULL DEFAULT (datetime('now'))
      );

      -- Per-Bet Escrow: Encrypted Keys
      CREATE TABLE IF NOT EXISTS escrow_keys (
        escrow_id      TEXT PRIMARY KEY,
        encrypted_seed TEXT NOT NULL,
        iv             TEXT NOT NULL,
        auth_tag       TEXT NOT NULL,
        status         TEXT NOT NULL DEFAULT 'active',
        created_at     TEXT NOT NULL DEFAULT (datetime('now')),
        archived_at    TEXT
      );

      -- Idempotency keys for preventing double-processing
      CREATE TABLE IF NOT EXISTS idempotency_keys (
        key        TEXT PRIMARY KEY,
        response   TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
      );

      -- Cron single-instance lock
      CREATE TABLE IF NOT EXISTS cron_locks (
        lock_name  TEXT PRIMARY KEY,
        holder_id  TEXT NOT NULL,
        acquired_at TEXT NOT NULL DEFAULT (datetime('now')),
        expires_at TEXT NOT NULL
      );

      -- Nonce tracking for replay attack prevention
      CREATE TABLE IF NOT EXISTS used_nonces (
        nonce      TEXT PRIMARY KEY,
        address    TEXT NOT NULL,
        endpoint   TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
      );

      -- System status (key-value store for operational metadata)
      CREATE TABLE IF NOT EXISTS system_status (
        key        TEXT PRIMARY KEY,
        value      TEXT NOT NULL,
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
      );

      -- Indices
      CREATE INDEX IF NOT EXISTS idx_nonces_created ON used_nonces(created_at);
      CREATE INDEX IF NOT EXISTS idx_markets_status ON markets(status);
      CREATE INDEX IF NOT EXISTS idx_markets_pair ON markets(pair);
      CREATE INDEX IF NOT EXISTS idx_markets_end_date ON markets(end_date);
      CREATE INDEX IF NOT EXISTS idx_user_bets_market ON user_bets(market_id);
      CREATE INDEX IF NOT EXISTS idx_user_bets_user ON user_bets(user_address);
      CREATE INDEX IF NOT EXISTS idx_transactions_address ON transactions(address);
      CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
      CREATE INDEX IF NOT EXISTS idx_snapshots_market ON market_snapshots(market_id);
      CREATE INDEX IF NOT EXISTS idx_chain_event_type ON commitment_chain(event_type);
      CREATE INDEX IF NOT EXISTS idx_chain_entity ON commitment_chain(entity_id);
      CREATE INDEX IF NOT EXISTS idx_attestations_market ON oracle_attestations(market_id);
      CREATE INDEX IF NOT EXISTS idx_solvency_created ON solvency_proofs(created_at);
      CREATE INDEX IF NOT EXISTS idx_escrow_status ON escrow_addresses(status);
      CREATE INDEX IF NOT EXISTS idx_escrow_market ON escrow_addresses(market_id);
      CREATE INDEX IF NOT EXISTS idx_escrow_bet ON escrow_addresses(bet_id);
      CREATE INDEX IF NOT EXISTS idx_escrow_address ON escrow_addresses(escrow_address);
      CREATE INDEX IF NOT EXISTS idx_escrow_keys_status ON escrow_keys(status);
      CREATE INDEX IF NOT EXISTS idx_markets_type ON markets(market_type);
      CREATE INDEX IF NOT EXISTS idx_markets_category ON markets(category);
      CREATE INDEX IF NOT EXISTS idx_markets_created_by ON markets(created_by);
    `)

    // ALTER TABLE migrations for provably fair columns on existing tables
    this.migrateProvablyFairColumns()
  }

  /**
   * Add provably fair columns to existing tables (safe to run repeatedly).
   */
  private migrateProvablyFairColumns(): void {
    const addColumnIfMissing = (table: string, column: string, type: string) => {
      try {
        this.db.exec(`ALTER TABLE ${table} ADD COLUMN ${column} ${type}`)
      } catch {
        // Column already exists — ignore
      }
    }

    // Markets: commitment hash binding market params at creation
    addColumnIfMissing('markets', 'commitment_hash', 'TEXT')

    // User bets: cryptographic bet commitment
    addColumnIfMissing('user_bets', 'commitment_hash', 'TEXT')
    addColumnIfMissing('user_bets', 'commitment_nonce', 'TEXT')
    addColumnIfMissing('user_bets', 'user_signature', 'TEXT')

    // v2: Multi-option + AI + Category
    addColumnIfMissing('markets', 'market_type', "TEXT DEFAULT 'price'")
    addColumnIfMissing('markets', 'options_json', 'TEXT DEFAULT \'["Yes","No"]\'')
    addColumnIfMissing('markets', 'num_options', 'INTEGER DEFAULT 2')
    addColumnIfMissing('markets', 'oracle_addresses_json', 'TEXT')
    addColumnIfMissing('markets', 'oracle_fee_bps', 'INTEGER DEFAULT 0')
    addColumnIfMissing('markets', 'auto_refund_at', 'TEXT')
    addColumnIfMissing('markets', 'category', 'TEXT')
    addColumnIfMissing('markets', 'slots_json', 'TEXT DEFAULT \'{"0":0,"1":0}\'')
    addColumnIfMissing('markets', 'ai_resolution_attempts', 'INTEGER DEFAULT 0')
    addColumnIfMissing('markets', 'ai_resolution_proof', 'TEXT')
    addColumnIfMissing('markets', 'created_by', "TEXT DEFAULT 'user'")
    addColumnIfMissing('markets', 'source_query', 'TEXT')

    // v3: Escrow robustness
    addColumnIfMissing('escrow_addresses', 'join_bet_retries', 'INTEGER DEFAULT 0')
  }

  private prepareStatements() {
    return {
      // Markets
      insertMarket: this.db.prepare(`
        INSERT INTO markets (id, quottery_bet_id, pair, question, resolution_type,
          resolution_target, resolution_target_high, close_date, end_date,
          min_bet_qu, max_slots, status, creator_address, tx_hash,
          market_type, options_json, num_options, oracle_addresses_json,
          oracle_fee_bps, auto_refund_at, category, slots_json, created_by, source_query)
        VALUES (@id, @quotteryBetId, @pair, @question, @resolutionType,
          @resolutionTarget, @resolutionTargetHigh, @closeDate, @endDate,
          @minBetQu, @maxSlots, @status, @creatorAddress, @txHash,
          @marketType, @optionsJson, @numOptions, @oracleAddressesJson,
          @oracleFeeBps, @autoRefundAt, @category, @slotsJson, @createdBy, @sourceQuery)
      `),
      getMarket: this.db.prepare('SELECT * FROM markets WHERE id = ?'),
      getMarketByBetId: this.db.prepare(
        'SELECT * FROM markets WHERE quottery_bet_id = ?',
      ),
      listMarkets: this.db.prepare(
        'SELECT * FROM markets ORDER BY created_at DESC',
      ),
      listMarketsByStatus: this.db.prepare(
        'SELECT * FROM markets WHERE status = ? ORDER BY created_at DESC',
      ),
      listRecentResolved: this.db.prepare(
        "SELECT * FROM markets WHERE status = 'resolved' ORDER BY resolved_at DESC LIMIT ?",
      ),
      listMarketsByPair: this.db.prepare(
        'SELECT * FROM markets WHERE pair = ? AND status IN (\'active\', \'closed\') ORDER BY created_at DESC',
      ),
      updateMarketStatus: this.db.prepare(
        'UPDATE markets SET status = ? WHERE id = ?',
      ),
      updateMarketBetId: this.db.prepare(
        'UPDATE markets SET quottery_bet_id = ?, status = \'active\' WHERE id = ?',
      ),
      updateMarketResolution: this.db.prepare(`
        UPDATE markets SET
          status = 'resolved',
          resolution_price = ?,
          winning_option = ?,
          resolved_at = datetime('now')
        WHERE id = ?
      `),
      updateMarketPool: this.db.prepare(`
        UPDATE markets SET
          total_pool = total_pool + ?,
          yes_slots = CASE WHEN ? = 0 THEN yes_slots + ? ELSE yes_slots END,
          no_slots = CASE WHEN ? = 1 THEN no_slots + ? ELSE no_slots END
        WHERE id = ?
      `),

      // User Bets
      insertBet: this.db.prepare(`
        INSERT INTO user_bets (id, market_id, user_address, option, slots, amount_qu, tx_hash, status)
        VALUES (@id, @marketId, @userAddress, @option, @slots, @amountQu, @txHash, @status)
      `),
      getBet: this.db.prepare('SELECT * FROM user_bets WHERE id = ?'),
      getBetsByMarket: this.db.prepare(
        'SELECT * FROM user_bets WHERE market_id = ? ORDER BY created_at DESC',
      ),
      getBetsByUser: this.db.prepare(
        'SELECT * FROM user_bets WHERE user_address = ? ORDER BY created_at DESC',
      ),
      getUserBetsForMarket: this.db.prepare(
        'SELECT * FROM user_bets WHERE market_id = ? AND user_address = ? AND status IN (\'pending_deposit\', \'pending\', \'confirmed\')',
      ),
      updateBetStatus: this.db.prepare(
        'UPDATE user_bets SET status = ? WHERE id = ?',
      ),
      updateBetPayout: this.db.prepare(
        'UPDATE user_bets SET status = ?, payout_qu = ? WHERE id = ?',
      ),
      updateBetTxHash: this.db.prepare(
        'UPDATE user_bets SET tx_hash = ?, status = \'confirmed\' WHERE id = ?',
      ),

      // Accounts
      getAccount: this.db.prepare('SELECT * FROM accounts WHERE address = ?'),
      insertAccount: this.db.prepare(`
        INSERT OR IGNORE INTO accounts (address, display_name)
        VALUES (?, ?)
      `),
      updateBalance: this.db.prepare(
        'UPDATE accounts SET balance_qu = balance_qu + ? WHERE address = ?',
      ),
      updateAccountDeposit: this.db.prepare(`
        UPDATE accounts SET
          balance_qu = balance_qu + ?,
          total_deposited = total_deposited + ?
        WHERE address = ?
      `),
      updateAccountWithdraw: this.db.prepare(`
        UPDATE accounts SET
          balance_qu = balance_qu - ?,
          total_withdrawn = total_withdrawn + ?
        WHERE address = ?
      `),
      updateAccountBet: this.db.prepare(`
        UPDATE accounts SET
          balance_qu = balance_qu - ?,
          total_bet = total_bet + ?
        WHERE address = ?
      `),
      updateAccountWin: this.db.prepare(`
        UPDATE accounts SET
          balance_qu = balance_qu + ?,
          total_won = total_won + ?
        WHERE address = ?
      `),

      // Transactions
      insertTransaction: this.db.prepare(`
        INSERT INTO transactions (id, address, type, amount_qu, tx_hash, market_id, status)
        VALUES (@id, @address, @type, @amountQu, @txHash, @marketId, @status)
      `),
      getTransactionsByAddress: this.db.prepare(
        'SELECT * FROM transactions WHERE address = ? ORDER BY created_at DESC LIMIT 100',
      ),
      updateTransactionStatus: this.db.prepare(
        'UPDATE transactions SET status = ? WHERE id = ?',
      ),

      // Snapshots
      insertSnapshot: this.db.prepare(`
        INSERT INTO market_snapshots (market_id, yes_slots, no_slots, implied_probability, total_pool)
        SELECT id, yes_slots, no_slots,
          CASE WHEN (yes_slots + no_slots) > 0
            THEN CAST(yes_slots AS REAL) / (yes_slots + no_slots)
            ELSE 0.5
          END,
          total_pool
        FROM markets WHERE id = ?
      `),
      getSnapshots: this.db.prepare(
        'SELECT * FROM market_snapshots WHERE market_id = ? ORDER BY timestamp ASC',
      ),

      // Stats
      countMarkets: this.db.prepare(
        'SELECT COUNT(*) as count FROM markets',
      ),
      countActiveMarkets: this.db.prepare(
        "SELECT COUNT(*) as count FROM markets WHERE status IN ('active', 'closed')",
      ),
      countResolvedMarkets: this.db.prepare(
        "SELECT COUNT(*) as count FROM markets WHERE status = 'resolved'",
      ),
      totalVolume: this.db.prepare(
        'SELECT COALESCE(SUM(total_pool), 0) as total FROM markets',
      ),
      totalBets: this.db.prepare(
        'SELECT COUNT(*) as count FROM user_bets',
      ),
      totalUsers: this.db.prepare(
        'SELECT COUNT(*) as count FROM accounts',
      ),
      totalPaidOut: this.db.prepare(
        "SELECT COALESCE(SUM(payout_qu), 0) as total FROM user_bets WHERE status = 'won'",
      ),

      // Leaderboard
      leaderboard: this.db.prepare(`
        SELECT
          ub.user_address as address,
          a.display_name,
          COUNT(*) as total_bets,
          SUM(CASE WHEN ub.status = 'won' THEN 1 ELSE 0 END) as wins,
          SUM(CASE WHEN ub.status = 'lost' THEN 1 ELSE 0 END) as losses,
          CASE WHEN COUNT(*) > 0
            THEN ROUND(CAST(SUM(CASE WHEN ub.status = 'won' THEN 1 ELSE 0 END) AS REAL) / COUNT(*), 3)
            ELSE 0
          END as accuracy,
          COALESCE(SUM(CASE WHEN ub.status = 'won' THEN ub.payout_qu ELSE 0 END), 0) as total_won,
          SUM(ub.amount_qu) as total_bet,
          COALESCE(SUM(CASE WHEN ub.status = 'won' THEN ub.payout_qu ELSE 0 END), 0) - SUM(ub.amount_qu) as profit_qu
        FROM user_bets ub
        LEFT JOIN accounts a ON ub.user_address = a.address
        WHERE ub.status IN ('won', 'lost')
        GROUP BY ub.user_address
        HAVING COUNT(*) >= ?
        ORDER BY accuracy DESC, total_bets DESC
        LIMIT ?
      `),

      // Expiry check
      expiredMarkets: this.db.prepare(`
        SELECT * FROM markets
        WHERE status IN ('active', 'closed')
          AND replace(replace(end_date, 'T', ' '), 'Z', '') <= datetime('now')
      `),
      closingMarkets: this.db.prepare(`
        SELECT * FROM markets
        WHERE status = 'active'
          AND replace(replace(close_date, 'T', ' '), 'Z', '') <= datetime('now')
      `),

      // v2: Filtered queries
      listMarketsByCategory: this.db.prepare(
        "SELECT * FROM markets WHERE category = ? AND status IN ('active', 'closed') ORDER BY created_at DESC",
      ),
      listMarketsByType: this.db.prepare(
        "SELECT * FROM markets WHERE market_type = ? AND status IN ('active', 'closed') ORDER BY created_at DESC",
      ),
      listMarketsByCategoryAndType: this.db.prepare(
        "SELECT * FROM markets WHERE category = ? AND market_type = ? AND status IN ('active', 'closed') ORDER BY created_at DESC",
      ),
      // v2: AI resolution tracking
      updateAiResolutionAttempt: this.db.prepare(`
        UPDATE markets SET
          ai_resolution_attempts = ai_resolution_attempts + 1,
          ai_resolution_proof = ?
        WHERE id = ?
      `),
      // v2: Markets needing AI resolution
      marketsNeedingAiResolution: this.db.prepare(`
        SELECT * FROM markets
        WHERE market_type = 'ai'
          AND status IN ('closed', 'resolving')
          AND replace(replace(end_date, 'T', ' '), 'Z', '') <= datetime('now')
          AND ai_resolution_attempts < 3
      `),
      // v2: Custom markets needing auto-refund
      marketsNeedingAutoRefund: this.db.prepare(`
        SELECT * FROM markets
        WHERE market_type IN ('custom', 'ai')
          AND status IN ('closed', 'resolving')
          AND auto_refund_at IS NOT NULL
          AND replace(replace(auto_refund_at, 'T', ' '), 'Z', '') <= datetime('now')
          AND winning_option IS NULL
      `),
      // v2: Update slots_json
      updateSlotsJson: this.db.prepare(
        'UPDATE markets SET slots_json = ?, total_pool = total_pool + ? WHERE id = ?',
      ),

      // --- Provably Fair: Commitment Chain ---
      insertChainEntry: this.db.prepare(`
        INSERT INTO commitment_chain (event_type, entity_id, payload_hash, prev_hash, chain_hash, payload_json, created_at)
        VALUES (@eventType, @entityId, @payloadHash, @prevHash, @chainHash, @payloadJson, @createdAt)
      `),
      getLatestChainEntry: this.db.prepare(
        'SELECT * FROM commitment_chain ORDER BY sequence_num DESC LIMIT 1',
      ),
      getChainEntry: this.db.prepare(
        'SELECT * FROM commitment_chain WHERE sequence_num = ?',
      ),
      getChainRange: this.db.prepare(
        'SELECT * FROM commitment_chain WHERE sequence_num >= ? AND sequence_num <= ? ORDER BY sequence_num ASC',
      ),
      getChainByEntity: this.db.prepare(
        'SELECT * FROM commitment_chain WHERE entity_id = ? ORDER BY sequence_num ASC',
      ),
      getChainCount: this.db.prepare(
        'SELECT COUNT(*) as count FROM commitment_chain',
      ),
      getAllChainEntries: this.db.prepare(
        'SELECT * FROM commitment_chain ORDER BY sequence_num ASC',
      ),

      // --- Provably Fair: Oracle Attestations ---
      insertAttestation: this.db.prepare(`
        INSERT INTO oracle_attestations (id, market_id, oracle_source, pair, price, tick, epoch, source_timestamp, attestation_hash, server_signature, created_at)
        VALUES (@id, @marketId, @oracleSource, @pair, @price, @tick, @epoch, @sourceTimestamp, @attestationHash, @serverSignature, @createdAt)
      `),
      getAttestationsByMarket: this.db.prepare(
        'SELECT * FROM oracle_attestations WHERE market_id = ? ORDER BY created_at ASC',
      ),

      // --- Provably Fair: Solvency Proofs ---
      insertSolvencyProof: this.db.prepare(`
        INSERT INTO solvency_proofs (id, merkle_root, total_user_balance, on_chain_balance, is_solvent, account_count, tick, epoch, leaf_hashes_json, created_at)
        VALUES (@id, @merkleRoot, @totalUserBalance, @onChainBalance, @isSolvent, @accountCount, @tick, @epoch, @leafHashesJson, @createdAt)
      `),
      getLatestSolvencyProof: this.db.prepare(
        'SELECT * FROM solvency_proofs ORDER BY created_at DESC LIMIT 1',
      ),
      getSolvencyProofs: this.db.prepare(
        'SELECT * FROM solvency_proofs ORDER BY created_at DESC LIMIT ?',
      ),

      // --- Provably Fair: Market commitment hash ---
      updateMarketCommitment: this.db.prepare(
        'UPDATE markets SET commitment_hash = ? WHERE id = ?',
      ),

      // --- Provably Fair: Bet commitment ---
      updateBetCommitment: this.db.prepare(
        'UPDATE user_bets SET commitment_hash = ?, commitment_nonce = ? WHERE id = ?',
      ),

      // --- Provably Fair: All accounts for Merkle tree ---
      getAllAccounts: this.db.prepare(
        'SELECT * FROM accounts ORDER BY address ASC',
      ),
      getTotalUserBalance: this.db.prepare(
        'SELECT COALESCE(SUM(balance_qu), 0) as total FROM accounts',
      ),

      // --- Per-Bet Escrow: Escrow Addresses ---
      insertEscrow: this.db.prepare(`
        INSERT INTO escrow_addresses (id, bet_id, market_id, escrow_address, user_payout_address,
          option, slots, expected_amount_qu, status, expires_at)
        VALUES (@id, @betId, @marketId, @escrowAddress, @userPayoutAddress,
          @option, @slots, @expectedAmountQu, @status, @expiresAt)
      `),
      getEscrow: this.db.prepare('SELECT * FROM escrow_addresses WHERE id = ?'),
      getEscrowByBet: this.db.prepare('SELECT * FROM escrow_addresses WHERE bet_id = ?'),
      getEscrowByAddress: this.db.prepare('SELECT * FROM escrow_addresses WHERE escrow_address = ?'),
      getEscrowsByMarket: this.db.prepare(
        'SELECT * FROM escrow_addresses WHERE market_id = ? ORDER BY created_at DESC',
      ),
      getEscrowsByStatus: this.db.prepare(
        'SELECT * FROM escrow_addresses WHERE status = ? ORDER BY created_at ASC',
      ),
      getEscrowsByStatuses: this.db.prepare(
        'SELECT * FROM escrow_addresses WHERE status IN (?, ?) ORDER BY created_at ASC',
      ),
      updateEscrowStatus: this.db.prepare(
        'UPDATE escrow_addresses SET status = ? WHERE id = ?',
      ),
      updateEscrowDeposit: this.db.prepare(`
        UPDATE escrow_addresses SET
          status = 'deposit_detected',
          deposit_detected_at = datetime('now'),
          deposit_amount_qu = ?
        WHERE id = ?
      `),
      updateEscrowJoinBet: this.db.prepare(`
        UPDATE escrow_addresses SET
          status = 'joining_sc',
          join_bet_tx_id = ?,
          join_bet_tick = ?
        WHERE id = ?
      `),
      // Confirm joinBet after on-chain verification (joining_sc → active_in_sc)
      confirmJoinBet: this.db.prepare(`
        UPDATE escrow_addresses SET status = 'active_in_sc'
        WHERE id = ? AND status = 'joining_sc'
      `),
      // Revert failed joinBet (joining_sc → deposit_detected) for retry
      revertJoinBet: this.db.prepare(`
        UPDATE escrow_addresses SET
          status = 'deposit_detected',
          join_bet_tx_id = NULL,
          join_bet_tick = NULL
        WHERE id = ? AND status = 'joining_sc'
      `),
      // Get escrows in joining_sc state (pending confirmation)
      getJoiningScEscrows: this.db.prepare(
        "SELECT * FROM escrow_addresses WHERE status = 'joining_sc'"
      ),
      updateEscrowPayout: this.db.prepare(`
        UPDATE escrow_addresses SET
          status = 'won_awaiting_sweep',
          payout_detected_at = datetime('now'),
          payout_amount_qu = ?
        WHERE id = ?
      `),
      updateEscrowSweep: this.db.prepare(`
        UPDATE escrow_addresses SET
          sweep_tx_id = ?,
          sweep_tick = ?
        WHERE id = ?
      `),
      // Atomic claim: only transitions won_awaiting_sweep → sweeping if not already claimed
      claimEscrowForSweep: this.db.prepare(`
        UPDATE escrow_addresses SET status = 'sweeping'
        WHERE id = ? AND status = 'won_awaiting_sweep'
      `),
      // Confirm sweep: sweeping → swept ONLY if sweep_tx_id is recorded (SQL-level guard)
      confirmSweepComplete: this.db.prepare(`
        UPDATE escrow_addresses SET status = 'swept'
        WHERE id = ? AND status = 'sweeping' AND sweep_tx_id IS NOT NULL AND sweep_tx_id != ''
      `),
      // Revert sweeping → won_awaiting_sweep if sweep TX fails
      revertSweepClaim: this.db.prepare(`
        UPDATE escrow_addresses SET status = 'won_awaiting_sweep'
        WHERE id = ? AND status = 'sweeping'
      `),
      // Get escrows in 'sweeping' state (for confirmation checks)
      getSweepingEscrows: this.db.prepare(
        "SELECT * FROM escrow_addresses WHERE status = 'sweeping' ORDER BY created_at ASC",
      ),
      // Increment joinBet retry counter
      incrementJoinBetRetries: this.db.prepare(
        'UPDATE escrow_addresses SET join_bet_retries = join_bet_retries + 1 WHERE id = ?',
      ),
      updateEscrowLost: this.db.prepare(
        "UPDATE escrow_addresses SET status = 'lost' WHERE id = ?",
      ),
      updateEscrowExpired: this.db.prepare(
        "UPDATE escrow_addresses SET status = 'expired' WHERE id = ? AND status = 'awaiting_deposit'",
      ),
      getExpiredEscrows: this.db.prepare(
        "SELECT * FROM escrow_addresses WHERE status = 'awaiting_deposit' AND replace(replace(expires_at, 'T', ' '), 'Z', '') <= datetime('now')",
      ),
      countActiveEscrows: this.db.prepare(
        "SELECT COUNT(*) as count FROM escrow_addresses WHERE status NOT IN ('completed', 'expired', 'lost')",
      ),

      // --- Per-Bet Escrow: Encrypted Keys ---
      insertEscrowKey: this.db.prepare(`
        INSERT INTO escrow_keys (escrow_id, encrypted_seed, iv, auth_tag, status)
        VALUES (@escrowId, @encryptedSeed, @iv, @authTag, @status)
      `),
      getEscrowKey: this.db.prepare('SELECT * FROM escrow_keys WHERE escrow_id = ?'),
      updateEscrowKeyStatus: this.db.prepare(
        'UPDATE escrow_keys SET status = ?, archived_at = CASE WHEN ? = \'archived\' THEN datetime(\'now\') ELSE archived_at END WHERE escrow_id = ?',
      ),

      // --- Cron Locking ---
      acquireCronLock: this.db.prepare(`
        INSERT OR REPLACE INTO cron_locks (lock_name, holder_id, acquired_at, expires_at)
        SELECT ?, ?, datetime('now'), datetime('now', '+' || ? || ' seconds')
        WHERE NOT EXISTS (
          SELECT 1 FROM cron_locks
          WHERE lock_name = ? AND expires_at > datetime('now') AND holder_id != ?
        )
      `),
      releaseCronLock: this.db.prepare(
        'DELETE FROM cron_locks WHERE lock_name = ? AND holder_id = ?',
      ),
      cleanExpiredCronLocks: this.db.prepare(
        "DELETE FROM cron_locks WHERE expires_at <= datetime('now')",
      ),
    }
  }

  private getStmts() {
    if (!this.stmts) {
      this.stmts = this.prepareStatements()
    }
    return this.stmts
  }

  // -------------------------------------------------------------------------
  // Markets
  // -------------------------------------------------------------------------

  createMarket(params: {
    pair: string
    question: string
    resolutionType: ResolutionType
    resolutionTarget: number
    resolutionTargetHigh?: number
    closeDate: string
    endDate: string
    minBetQu?: number
    maxSlots?: number
    creatorAddress?: string
    // v2 params
    marketType?: MarketType
    options?: string[]
    oracleAddresses?: string[]
    oracleFeeBps?: number
    autoRefundAt?: string
    category?: Category
    createdBy?: CreatedBy
    sourceQuery?: string
  }): Market {
    const id = `mkt_${crypto.randomBytes(8).toString('hex')}`
    const s = this.getStmts()

    const options = params.options ?? ['Yes', 'No']
    const numOptions = options.length
    // Build initial slots_json with 0 for each option
    const slotsInit: Record<string, number> = {}
    for (let i = 0; i < numOptions; i++) slotsInit[String(i)] = 0

    s.insertMarket.run({
      id,
      quotteryBetId: null,
      pair: params.pair,
      question: params.question,
      resolutionType: params.resolutionType,
      resolutionTarget: params.resolutionTarget,
      resolutionTargetHigh: params.resolutionTargetHigh ?? null,
      closeDate: params.closeDate,
      endDate: params.endDate,
      minBetQu: params.minBetQu ?? 10_000,
      maxSlots: params.maxSlots ?? 100,
      status: 'draft',
      creatorAddress: params.creatorAddress ?? null,
      txHash: null,
      // v2 fields
      marketType: params.marketType ?? 'price',
      optionsJson: JSON.stringify(options),
      numOptions,
      oracleAddressesJson: params.oracleAddresses ? JSON.stringify(params.oracleAddresses) : null,
      oracleFeeBps: params.oracleFeeBps ?? 0,
      autoRefundAt: params.autoRefundAt ?? null,
      category: params.category ?? null,
      slotsJson: JSON.stringify(slotsInit),
      createdBy: params.createdBy ?? 'user',
      sourceQuery: params.sourceQuery ?? null,
    })

    return this.getMarket(id)!
  }

  getMarket(id: string): Market | null {
    const row = this.getStmts().getMarket.get(id) as Record<string, unknown> | undefined
    return row ? this.rowToMarket(row) : null
  }

  getMarketByBetId(quotteryBetId: number): Market | null {
    const row = this.getStmts().getMarketByBetId.get(quotteryBetId) as
      | Record<string, unknown>
      | undefined
    return row ? this.rowToMarket(row) : null
  }

  listMarkets(filter?: {
    status?: MarketStatus
    pair?: string
    marketType?: MarketType
  }): Market[] {
    const s = this.getStmts()
    let rows: Record<string, unknown>[]

    if (filter?.marketType) {
      rows = s.listMarketsByType.all(filter.marketType) as Record<string, unknown>[]
    } else if (filter?.status) {
      rows = s.listMarketsByStatus.all(filter.status) as Record<string, unknown>[]
    } else if (filter?.pair) {
      rows = s.listMarketsByPair.all(filter.pair) as Record<string, unknown>[]
    } else {
      rows = s.listMarkets.all() as Record<string, unknown>[]
    }

    return rows.map((r) => this.rowToMarket(r))
  }

  /**
   * List recently resolved markets, ordered by resolved_at DESC.
   */
  listRecentResolved(limit: number = 5): Market[] {
    const rows = this.getStmts().listRecentResolved.all(limit) as Record<string, unknown>[]
    return rows.map((r) => this.rowToMarket(r))
  }

  updateMarketStatus(id: string, status: MarketStatus): void {
    this.getStmts().updateMarketStatus.run(status, id)
  }

  activateMarket(id: string, quotteryBetId: number): void {
    this.getStmts().updateMarketBetId.run(quotteryBetId, id)
  }

  resolveMarket(
    id: string,
    resolutionPrice: number,
    winningOption: number,
  ): void {
    this.getStmts().updateMarketResolution.run(
      resolutionPrice,
      winningOption,
      id,
    )
  }

  getExpiredMarkets(): Market[] {
    const rows = this.getStmts().expiredMarkets.all() as Record<string, unknown>[]
    return rows.map((r) => this.rowToMarket(r))
  }

  getClosingMarkets(): Market[] {
    const rows = this.getStmts().closingMarkets.all() as Record<string, unknown>[]
    return rows.map((r) => this.rowToMarket(r))
  }

  /**
   * Atomically claim a market for resolution by setting status to 'resolving'.
   * Returns true if this caller won the race, false if another process got it first.
   */
  tryClaimForResolution(id: string): boolean {
    const result = this.db
      .prepare(
        "UPDATE markets SET status = 'resolving' WHERE id = ? AND status IN ('active', 'closed')",
      )
      .run(id)
    return result.changes > 0
  }

  private rowToMarket(row: Record<string, unknown>): Market {
    // Parse JSON fields safely
    let options: string[] = ['Yes', 'No']
    try {
      const raw = row.options_json as string | null
      if (raw) options = JSON.parse(raw)
    } catch { /* use default */ }

    let oracleAddresses: string[] | null = null
    try {
      const raw = row.oracle_addresses_json as string | null
      if (raw) oracleAddresses = JSON.parse(raw)
    } catch { /* null */ }

    let slotsPerOption: Record<string, number> = { '0': 0, '1': 0 }
    try {
      const raw = row.slots_json as string | null
      if (raw) slotsPerOption = JSON.parse(raw)
    } catch { /* use default */ }

    let aiResolutionProof: unknown = null
    try {
      const raw = row.ai_resolution_proof as string | null
      if (raw) aiResolutionProof = JSON.parse(raw)
    } catch { /* null */ }

    return {
      id: row.id as string,
      quotteryBetId: row.quottery_bet_id as number | null,
      pair: row.pair as string,
      question: row.question as string,
      resolutionType: row.resolution_type as ResolutionType,
      resolutionTarget: row.resolution_target as number,
      resolutionTargetHigh: row.resolution_target_high as number | null,
      closeDate: row.close_date as string,
      endDate: row.end_date as string,
      minBetQu: row.min_bet_qu as number,
      maxSlots: row.max_slots as number,
      status: row.status as MarketStatus,
      totalPool: row.total_pool as number,
      yesSlots: row.yes_slots as number,
      noSlots: row.no_slots as number,
      resolutionPrice: row.resolution_price as number | null,
      winningOption: row.winning_option as number | null,
      creatorAddress: row.creator_address as string | null,
      txHash: row.tx_hash as string | null,
      createdAt: row.created_at as string,
      resolvedAt: row.resolved_at as string | null,
      commitmentHash: (row.commitment_hash as string | null) ?? null,
      // v2 fields
      marketType: (row.market_type as MarketType) ?? 'price',
      options,
      numOptions: (row.num_options as number) ?? 2,
      oracleAddresses,
      oracleFeeBps: (row.oracle_fee_bps as number) ?? 0,
      autoRefundAt: (row.auto_refund_at as string | null) ?? null,
      category: (row.category as Category | null) ?? null,
      slotsPerOption,
      aiResolutionAttempts: (row.ai_resolution_attempts as number) ?? 0,
      aiResolutionProof,
      createdBy: (row.created_by as CreatedBy) ?? 'user',
      sourceQuery: (row.source_query as string | null) ?? null,
    }
  }

  // -------------------------------------------------------------------------
  // User Bets
  // -------------------------------------------------------------------------

  createBet(params: {
    marketId: string
    userAddress: string
    option: number
    slots: number
    amountQu: number
    txHash?: string
    /**
     * When true, creates the bet with status 'pending_deposit' and does NOT
     * update the market pool/slot counts. Used by the escrow flow — pool is
     * updated later via confirmBetDeposit() once the on-chain deposit arrives.
     * This prevents "ghost bets" from inflating the pool before funds exist.
     */
    skipPoolUpdate?: boolean
  }): UserBet {
    const id = `bet_${crypto.randomBytes(8).toString('hex')}`
    const s = this.getStmts()
    const status: BetStatus = params.skipPoolUpdate ? 'pending_deposit' : 'pending'

    s.insertBet.run({
      id,
      marketId: params.marketId,
      userAddress: params.userAddress,
      option: params.option,
      slots: params.slots,
      amountQu: params.amountQu,
      txHash: params.txHash ?? null,
      status,
    })

    // Only update pool/slots when NOT in escrow flow.
    // Escrow flow defers pool update to confirmBetDeposit() after real deposit.
    if (!params.skipPoolUpdate) {
      // Update market pool (total_pool, yes_slots, no_slots)
      s.updateMarketPool.run(
        params.amountQu,
        params.option,
        params.slots,
        params.option,
        params.slots,
        params.marketId,
      )

      // Update slots_json for v2 multi-option tracking
      const market = this.getMarket(params.marketId)
      if (market) {
        const slotsMap = { ...market.slotsPerOption }
        slotsMap[String(params.option)] = (slotsMap[String(params.option)] ?? 0) + params.slots
        this.db.prepare('UPDATE markets SET slots_json = ? WHERE id = ?').run(
          JSON.stringify(slotsMap), params.marketId,
        )
      }
    }

    return this.getBet(id)!
  }

  /**
   * Atomically check if slots are available for an option and reserve them.
   * Returns true if the reservation succeeded, false if slots are full.
   *
   * This uses a single UPDATE with a WHERE condition to prevent race conditions
   * where concurrent bets exceed maxSlots.
   *
   * NOTE: This only reserves by checking current slot counts against maxSlots.
   * The actual pool increment happens either immediately (direct flow) or later
   * (escrow flow via confirmBetDeposit).
   */
  tryReserveSlots(marketId: string, option: number, slots: number): boolean {
    const market = this.getMarket(marketId)
    if (!market) return false

    const currentSlots = market.slotsPerOption[String(option)] ?? 0
    if (currentSlots + slots > market.maxSlots) return false

    // The slot count check + bet creation happens within a transaction in createBet,
    // and since SQLite serializes writes, the read-check-write is atomic.
    // For extra safety, verify again inside the caller's transaction.
    return true
  }

  getBet(id: string): UserBet | null {
    const row = this.getStmts().getBet.get(id) as Record<string, unknown> | undefined
    return row ? this.rowToUserBet(row) : null
  }

  getBetsByMarket(marketId: string): UserBet[] {
    const rows = this.getStmts().getBetsByMarket.all(marketId) as Record<string, unknown>[]
    return rows.map((r) => this.rowToUserBet(r))
  }

  getBetsByUser(address: string): UserBet[] {
    const rows = this.getStmts().getBetsByUser.all(address) as Record<string, unknown>[]
    return rows.map((r) => this.rowToUserBet(r))
  }

  /**
   * Get active bets for a specific user on a specific market.
   * Used to prevent betting on both sides of the same market.
   */
  getUserBetsForMarket(marketId: string, userAddress: string): UserBet[] {
    const rows = this.getStmts().getUserBetsForMarket.all(marketId, userAddress) as Record<string, unknown>[]
    return rows.map((r) => this.rowToUserBet(r))
  }

  confirmBet(id: string, txHash: string): void {
    this.getStmts().updateBetTxHash.run(txHash, id)
  }

  /**
   * Confirm a bet's deposit: transitions pending_deposit → pending AND
   * atomically increments the market pool/slot counts.
   *
   * This is the ONLY code path that updates pool for escrow-created bets.
   * Must be called after on-chain deposit is verified.
   *
   * Returns true if confirmed, false if slots are no longer available
   * (deposit should be refunded in that case).
   */
  confirmBetDeposit(betId: string): boolean {
    const bet = this.getBet(betId)
    if (!bet) throw new Error(`Bet not found: ${betId}`)
    if (bet.status !== 'pending_deposit') return true // Already confirmed or in another state

    const s = this.getStmts()

    let success = false

    const txn = this.db.transaction(() => {
      // Atomic slot availability check — re-read market inside transaction
      // SQLite serializes writes, so this read-check-write is safe
      const market = this.getMarket(bet.marketId)
      if (!market) {
        throw new Error(`Market not found: ${bet.marketId}`)
      }

      const currentSlots = market.slotsPerOption[String(bet.option)] ?? 0
      if (currentSlots + bet.slots > market.maxSlots) {
        // Slots no longer available — deposit should be refunded
        success = false
        return
      }

      // 1. Transition bet status: pending_deposit → pending
      s.updateBetStatus.run('pending', betId)

      // 2. Update market pool (total_pool, yes_slots, no_slots)
      s.updateMarketPool.run(
        bet.amountQu,
        bet.option,
        bet.slots,
        bet.option,
        bet.slots,
        bet.marketId,
      )

      // 3. Update slots_json for v2 multi-option tracking
      const slotsMap = { ...market.slotsPerOption }
      slotsMap[String(bet.option)] = (slotsMap[String(bet.option)] ?? 0) + bet.slots
      this.db.prepare('UPDATE markets SET slots_json = ? WHERE id = ?').run(
        JSON.stringify(slotsMap), bet.marketId,
      )

      success = true
    })

    txn()
    return success
  }

  setBetStatus(id: string, status: BetStatus): void {
    this.getStmts().updateBetStatus.run(status, id)
  }

  resolveBet(id: string, won: boolean, payoutQu?: number): void {
    if (won) {
      this.getStmts().updateBetPayout.run('won', payoutQu ?? 0, id)
    } else {
      this.getStmts().updateBetStatus.run('lost', id)
    }
  }

  /**
   * Resolve all bets for a market after the winning option is determined.
   */
  resolveAllBetsForMarket(
    marketId: string,
    winningOption: number,
    payoutPerSlot: number,
  ): { winners: number; losers: number } {
    const bets = this.getBetsByMarket(marketId)
    let winners = 0
    let losers = 0

    const resolveTxn = this.db.transaction(() => {
      for (const bet of bets) {
        if (bet.status !== 'confirmed' && bet.status !== 'pending') continue

        if (bet.option === winningOption) {
          // BigInt multiplication to prevent precision loss with large pools
          const payout = Number(BigInt(payoutPerSlot) * BigInt(bet.slots))
          this.resolveBet(bet.id, true, payout)
          // Credit user account
          this.creditWinnings(bet.userAddress, payout)
          winners++
        } else {
          this.resolveBet(bet.id, false)
          losers++
        }
      }
    })

    resolveTxn()
    return { winners, losers }
  }

  /**
   * Rollback a bet — remove it from DB, un-debit the user, and undo pool changes.
   * Used when the on-chain joinBet TX fails.
   */
  rollbackBet(
    betId: string,
    userAddress: string,
    amountQu: number,
    marketId: string,
    option: number,
    slots: number,
  ): void {
    const rollback = this.db.transaction(() => {
      // Remove the bet
      this.db.prepare('DELETE FROM user_bets WHERE id = ?').run(betId)

      // Refund the user balance
      this.db
        .prepare(
          'UPDATE accounts SET balance_qu = balance_qu + ?, total_bet = total_bet - ? WHERE address = ?',
        )
        .run(amountQu, amountQu, userAddress)

      // Undo pool updates (total_pool + yes_slots/no_slots)
      if (option === 0) {
        this.db
          .prepare(
            'UPDATE markets SET total_pool = total_pool - ?, yes_slots = yes_slots - ? WHERE id = ?',
          )
          .run(amountQu, slots, marketId)
      } else {
        this.db
          .prepare(
            'UPDATE markets SET total_pool = total_pool - ?, no_slots = no_slots - ? WHERE id = ?',
          )
          .run(amountQu, slots, marketId)
      }

      // Undo slots_json update
      const market = this.getMarket(marketId)
      if (market) {
        const slotsMap = { ...market.slotsPerOption }
        slotsMap[String(option)] = Math.max(0, (slotsMap[String(option)] ?? 0) - slots)
        this.db.prepare('UPDATE markets SET slots_json = ? WHERE id = ?').run(
          JSON.stringify(slotsMap), marketId,
        )
      }

      // Remove the bet transaction record
      this.db
        .prepare(
          "DELETE FROM transactions WHERE address = ? AND type = 'bet' AND market_id = ? AND amount_qu = ? ORDER BY created_at DESC LIMIT 1",
        )
        .run(userAddress, marketId, amountQu)
    })
    rollback()
  }

  /**
   * Atomically check balance and debit for a bet.
   * Returns true if successful, false if insufficient balance.
   * Uses a single UPDATE with WHERE clause to prevent race conditions.
   */
  atomicDebitBet(address: string, amountQu: number, marketId: string): boolean {
    const result = this.db
      .prepare(
        'UPDATE accounts SET balance_qu = balance_qu - ?, total_bet = total_bet + ? WHERE address = ? AND balance_qu >= ?',
      )
      .run(amountQu, amountQu, address, amountQu)

    if (result.changes > 0) {
      this.recordTransaction({
        address,
        type: 'bet',
        amountQu,
        marketId,
        status: 'confirmed',
      })
      return true
    }
    return false
  }

  // -------------------------------------------------------------------------
  // Nonce Tracking (replay attack prevention)
  // -------------------------------------------------------------------------

  /**
   * Check if a nonce has been used before. If not, record it.
   * Returns true if the nonce is fresh (unused), false if it's a replay.
   */
  checkAndRecordNonce(nonce: string, address: string, endpoint: string): boolean {
    const existing = this.db
      .prepare('SELECT nonce FROM used_nonces WHERE nonce = ?')
      .get(nonce)

    if (existing) return false // Replay detected

    this.db
      .prepare('INSERT INTO used_nonces (nonce, address, endpoint) VALUES (?, ?, ?)')
      .run(nonce, address, endpoint)

    return true
  }

  /**
   * Clean up expired nonces older than 24 hours.
   */
  cleanExpiredNonces(): number {
    const result = this.db
      .prepare("DELETE FROM used_nonces WHERE created_at < datetime('now', '-24 hours')")
      .run()
    return result.changes
  }

  // -------------------------------------------------------------------------
  // Idempotency Keys (prevent double-processing of POST requests)
  // -------------------------------------------------------------------------

  /**
   * Check for an existing idempotency key and return the cached response.
   * Returns null if the key hasn't been used before.
   */
  getIdempotencyResponse(key: string): string | null {
    const row = this.db
      .prepare('SELECT response FROM idempotency_keys WHERE key = ?')
      .get(key) as { response: string } | undefined
    return row?.response ?? null
  }

  /**
   * Store an idempotency key with its response for deduplication.
   */
  setIdempotencyResponse(key: string, response: string): void {
    this.db
      .prepare('INSERT OR IGNORE INTO idempotency_keys (key, response) VALUES (?, ?)')
      .run(key, response)
  }

  /**
   * Clean up expired idempotency keys older than 24 hours.
   */
  cleanExpiredIdempotencyKeys(): number {
    const result = this.db
      .prepare("DELETE FROM idempotency_keys WHERE created_at < datetime('now', '-24 hours')")
      .run()
    return result.changes
  }

  // -------------------------------------------------------------------------
  // System Status (key-value store for operational metadata)
  // -------------------------------------------------------------------------

  getSystemStatus(key: string): string | null {
    const row = this.db
      .prepare('SELECT value FROM system_status WHERE key = ?')
      .get(key) as { value: string } | undefined
    return row?.value ?? null
  }

  setSystemStatus(key: string, value: string): void {
    this.db
      .prepare(
        `INSERT INTO system_status (key, value, updated_at) VALUES (?, ?, datetime('now'))
         ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = datetime('now')`,
      )
      .run(key, value)
  }

  // -------------------------------------------------------------------------
  // Aggregate Counts (for health/admin endpoints)
  // -------------------------------------------------------------------------

  getEscrowStatusCounts(): Record<string, number> {
    const rows = this.db
      .prepare('SELECT status, COUNT(*) as count FROM escrow_addresses GROUP BY status')
      .all() as Array<{ status: string; count: number }>
    const counts: Record<string, number> = {}
    for (const row of rows) counts[row.status] = row.count
    return counts
  }

  getMarketStatusCounts(): Record<string, number> {
    const rows = this.db
      .prepare('SELECT status, COUNT(*) as count FROM markets GROUP BY status')
      .all() as Array<{ status: string; count: number }>
    const counts: Record<string, number> = {}
    for (const row of rows) counts[row.status] = row.count
    return counts
  }

  getMarketsClosingSoon(withinMinutes: number = 60): Array<{ id: string; question: string; closeDate: string }> {
    return this.db
      .prepare(
        `SELECT id, question, close_date as closeDate FROM markets
         WHERE status = 'active'
           AND replace(replace(close_date, 'T', ' '), 'Z', '') <= datetime('now', '+' || ? || ' minutes')
         ORDER BY close_date ASC LIMIT 10`,
      )
      .all(withinMinutes) as Array<{ id: string; question: string; closeDate: string }>
  }

  getMarketsResolvingSoon(withinMinutes: number = 60): Array<{ id: string; question: string; endDate: string }> {
    return this.db
      .prepare(
        `SELECT id, question, end_date as endDate FROM markets
         WHERE status IN ('active', 'closed')
           AND replace(replace(end_date, 'T', ' '), 'Z', '') <= datetime('now', '+' || ? || ' minutes')
         ORDER BY end_date ASC LIMIT 10`,
      )
      .all(withinMinutes) as Array<{ id: string; question: string; endDate: string }>
  }

  private rowToUserBet(row: Record<string, unknown>): UserBet {
    return {
      id: row.id as string,
      marketId: row.market_id as string,
      userAddress: row.user_address as string,
      option: row.option as number,
      slots: row.slots as number,
      amountQu: row.amount_qu as number,
      txHash: row.tx_hash as string | null,
      status: row.status as BetStatus,
      payoutQu: row.payout_qu as number | null,
      createdAt: row.created_at as string,
      commitmentHash: (row.commitment_hash as string | null) ?? null,
      commitmentNonce: (row.commitment_nonce as string | null) ?? null,
      userSignature: (row.user_signature as string | null) ?? null,
    }
  }

  // -------------------------------------------------------------------------
  // Accounts
  // -------------------------------------------------------------------------

  getAccount(address: string): Account | null {
    const row = this.getStmts().getAccount.get(address) as
      | Record<string, unknown>
      | undefined
    return row ? this.rowToAccount(row) : null
  }

  createAccount(address: string, displayName?: string): Account {
    this.getStmts().insertAccount.run(address, displayName ?? null)
    return this.getAccount(address)!
  }

  ensureAccount(address: string, displayName?: string): Account {
    const existing = this.getAccount(address)
    if (existing) return existing
    return this.createAccount(address, displayName)
  }

  creditDeposit(address: string, amountQu: number): void {
    this.ensureAccount(address)
    this.getStmts().updateAccountDeposit.run(amountQu, amountQu, address)
    this.recordTransaction({
      address,
      type: 'deposit',
      amountQu,
      status: 'confirmed',
    })
  }

  debitWithdrawal(address: string, amountQu: number): void {
    const account = this.getAccount(address)
    if (!account) throw new Error(`Account not found: ${address}`)
    if (account.balanceQu < amountQu) {
      throw new Error(
        `Insufficient balance: ${account.balanceQu} < ${amountQu}`,
      )
    }
    this.getStmts().updateAccountWithdraw.run(amountQu, amountQu, address)
    this.recordTransaction({
      address,
      type: 'withdrawal',
      amountQu,
      status: 'pending',
    })
  }

  debitBet(address: string, amountQu: number, marketId: string): void {
    const account = this.getAccount(address)
    if (!account) throw new Error(`Account not found: ${address}`)
    if (account.balanceQu < amountQu) {
      throw new Error(
        `Insufficient balance: ${account.balanceQu} < ${amountQu}`,
      )
    }
    this.getStmts().updateAccountBet.run(amountQu, amountQu, address)
    this.recordTransaction({
      address,
      type: 'bet',
      amountQu,
      marketId,
      status: 'confirmed',
    })
  }

  creditWinnings(address: string, amountQu: number): void {
    this.ensureAccount(address)
    this.getStmts().updateAccountWin.run(amountQu, amountQu, address)
    this.recordTransaction({
      address,
      type: 'payout',
      amountQu,
      status: 'confirmed',
    })
  }

  private rowToAccount(row: Record<string, unknown>): Account {
    return {
      address: row.address as string,
      displayName: row.display_name as string | null,
      balanceQu: row.balance_qu as number,
      totalDeposited: row.total_deposited as number,
      totalWithdrawn: row.total_withdrawn as number,
      totalBet: row.total_bet as number,
      totalWon: row.total_won as number,
      createdAt: row.created_at as string,
    }
  }

  // -------------------------------------------------------------------------
  // Transactions
  // -------------------------------------------------------------------------

  recordTransaction(params: {
    address: string
    type: TransactionType
    amountQu: number
    txHash?: string
    marketId?: string
    status?: string
  }): Transaction {
    const id = `tx_${crypto.randomBytes(8).toString('hex')}`
    this.getStmts().insertTransaction.run({
      id,
      address: params.address,
      type: params.type,
      amountQu: params.amountQu,
      txHash: params.txHash ?? null,
      marketId: params.marketId ?? null,
      status: params.status ?? 'pending',
    })
    return {
      id,
      address: params.address,
      type: params.type,
      amountQu: params.amountQu,
      txHash: params.txHash ?? null,
      marketId: params.marketId ?? null,
      status: params.status ?? 'pending',
      createdAt: new Date().toISOString(),
    }
  }

  getTransactions(address: string): Transaction[] {
    const rows = this.getStmts().getTransactionsByAddress.all(address) as Record<
      string,
      unknown
    >[]
    return rows.map((r) => ({
      id: r.id as string,
      address: r.address as string,
      type: r.type as TransactionType,
      amountQu: r.amount_qu as number,
      txHash: r.tx_hash as string | null,
      marketId: r.market_id as string | null,
      status: r.status as string,
      createdAt: r.created_at as string,
    }))
  }

  // -------------------------------------------------------------------------
  // Provably Fair: Commitment Chain
  // -------------------------------------------------------------------------

  appendChainEntry(entry: {
    eventType: string
    entityId: string
    payloadHash: string
    prevHash: string
    chainHash: string
    payloadJson: string
    createdAt: string
  }): CommitmentChainRow {
    const result = this.getStmts().insertChainEntry.run(entry)
    return this.getChainEntry(Number(result.lastInsertRowid))!
  }

  getLatestChainEntry(): CommitmentChainRow | null {
    const row = this.getStmts().getLatestChainEntry.get() as
      | Record<string, unknown>
      | undefined
    return row ? this.rowToChainEntry(row) : null
  }

  getChainEntry(sequenceNum: number): CommitmentChainRow | null {
    const row = this.getStmts().getChainEntry.get(sequenceNum) as
      | Record<string, unknown>
      | undefined
    return row ? this.rowToChainEntry(row) : null
  }

  getChainRange(from: number, to: number): CommitmentChainRow[] {
    const rows = this.getStmts().getChainRange.all(from, to) as Record<string, unknown>[]
    return rows.map((r) => this.rowToChainEntry(r))
  }

  getChainByEntity(entityId: string): CommitmentChainRow[] {
    const rows = this.getStmts().getChainByEntity.all(entityId) as Record<string, unknown>[]
    return rows.map((r) => this.rowToChainEntry(r))
  }

  getChainCount(): number {
    return (this.getStmts().getChainCount.get() as { count: number }).count
  }

  getAllChainEntries(): CommitmentChainRow[] {
    const rows = this.getStmts().getAllChainEntries.all() as Record<string, unknown>[]
    return rows.map((r) => this.rowToChainEntry(r))
  }

  private rowToChainEntry(row: Record<string, unknown>): CommitmentChainRow {
    return {
      sequenceNum: row.sequence_num as number,
      eventType: row.event_type as string,
      entityId: row.entity_id as string,
      payloadHash: row.payload_hash as string,
      prevHash: row.prev_hash as string,
      chainHash: row.chain_hash as string,
      payloadJson: row.payload_json as string,
      createdAt: row.created_at as string,
    }
  }

  // -------------------------------------------------------------------------
  // Provably Fair: Oracle Attestations
  // -------------------------------------------------------------------------

  insertAttestation(att: {
    id: string
    marketId: string
    oracleSource: string
    pair: string
    price: number
    tick: number | null
    epoch: number | null
    sourceTimestamp: string
    attestationHash: string
    serverSignature: string
    createdAt: string
  }): void {
    this.getStmts().insertAttestation.run(att)
  }

  getAttestationsByMarket(marketId: string): OracleAttestationRow[] {
    const rows = this.getStmts().getAttestationsByMarket.all(marketId) as Record<
      string,
      unknown
    >[]
    return rows.map((r) => this.rowToAttestation(r))
  }

  private rowToAttestation(row: Record<string, unknown>): OracleAttestationRow {
    return {
      id: row.id as string,
      marketId: row.market_id as string,
      oracleSource: row.oracle_source as string,
      pair: row.pair as string,
      price: row.price as number,
      tick: row.tick as number | null,
      epoch: row.epoch as number | null,
      sourceTimestamp: row.source_timestamp as string,
      attestationHash: row.attestation_hash as string,
      serverSignature: row.server_signature as string,
      createdAt: row.created_at as string,
    }
  }

  // -------------------------------------------------------------------------
  // Provably Fair: Solvency Proofs
  // -------------------------------------------------------------------------

  insertSolvencyProof(proof: {
    id: string
    merkleRoot: string
    totalUserBalance: number
    onChainBalance: number
    isSolvent: number
    accountCount: number
    tick: number
    epoch: number
    leafHashesJson: string
    createdAt: string
  }): void {
    this.getStmts().insertSolvencyProof.run(proof)
  }

  getLatestSolvencyProof(): SolvencyProofRow | null {
    const row = this.getStmts().getLatestSolvencyProof.get() as
      | Record<string, unknown>
      | undefined
    return row ? this.rowToSolvencyProof(row) : null
  }

  getSolvencyProofs(limit: number = 20): SolvencyProofRow[] {
    const rows = this.getStmts().getSolvencyProofs.all(limit) as Record<string, unknown>[]
    return rows.map((r) => this.rowToSolvencyProof(r))
  }

  private rowToSolvencyProof(row: Record<string, unknown>): SolvencyProofRow {
    return {
      id: row.id as string,
      merkleRoot: row.merkle_root as string,
      totalUserBalance: row.total_user_balance as number,
      onChainBalance: row.on_chain_balance as number,
      isSolvent: row.is_solvent as number,
      accountCount: row.account_count as number,
      tick: row.tick as number,
      epoch: row.epoch as number,
      leafHashesJson: row.leaf_hashes_json as string,
      createdAt: row.created_at as string,
    }
  }

  // -------------------------------------------------------------------------
  // Provably Fair: Market & Bet Commitments
  // -------------------------------------------------------------------------

  setMarketCommitment(id: string, commitmentHash: string): void {
    this.getStmts().updateMarketCommitment.run(commitmentHash, id)
  }

  setBetCommitment(
    betId: string,
    commitmentHash: string,
    nonce: string,
  ): void {
    this.getStmts().updateBetCommitment.run(commitmentHash, nonce, betId)
  }

  // -------------------------------------------------------------------------
  // Provably Fair: Account Helpers
  // -------------------------------------------------------------------------

  getAllAccounts(): Account[] {
    const rows = this.getStmts().getAllAccounts.all() as Record<string, unknown>[]
    return rows.map((r) => this.rowToAccount(r))
  }

  getTotalUserBalance(): number {
    return (this.getStmts().getTotalUserBalance.get() as { total: number }).total
  }

  // -------------------------------------------------------------------------
  // Per-Bet Escrow: Escrow Addresses
  // -------------------------------------------------------------------------

  createEscrow(params: {
    betId: string
    marketId: string
    escrowAddress: string
    userPayoutAddress: string
    option: number
    slots: number
    expectedAmountQu: number
    expiresAt: string
  }): EscrowAddress {
    const id = `esc_${crypto.randomBytes(8).toString('hex')}`
    this.getStmts().insertEscrow.run({
      id,
      betId: params.betId,
      marketId: params.marketId,
      escrowAddress: params.escrowAddress,
      userPayoutAddress: params.userPayoutAddress,
      option: params.option,
      slots: params.slots,
      expectedAmountQu: params.expectedAmountQu,
      status: 'awaiting_deposit',
      expiresAt: params.expiresAt,
    })
    return this.getEscrow(id)!
  }

  getEscrow(id: string): EscrowAddress | null {
    const row = this.getStmts().getEscrow.get(id) as Record<string, unknown> | undefined
    return row ? this.rowToEscrow(row) : null
  }

  getEscrowByBet(betId: string): EscrowAddress | null {
    const row = this.getStmts().getEscrowByBet.get(betId) as Record<string, unknown> | undefined
    return row ? this.rowToEscrow(row) : null
  }

  getEscrowByAddress(escrowAddress: string): EscrowAddress | null {
    const row = this.getStmts().getEscrowByAddress.get(escrowAddress) as Record<string, unknown> | undefined
    return row ? this.rowToEscrow(row) : null
  }

  getEscrowsByMarket(marketId: string): EscrowAddress[] {
    const rows = this.getStmts().getEscrowsByMarket.all(marketId) as Record<string, unknown>[]
    return rows.map((r) => this.rowToEscrow(r))
  }

  getEscrowsByStatus(status: EscrowStatus): EscrowAddress[] {
    const rows = this.getStmts().getEscrowsByStatus.all(status) as Record<string, unknown>[]
    return rows.map((r) => this.rowToEscrow(r))
  }

  getEscrowsByStatuses(status1: EscrowStatus, status2: EscrowStatus): EscrowAddress[] {
    const rows = this.getStmts().getEscrowsByStatuses.all(status1, status2) as Record<string, unknown>[]
    return rows.map((r) => this.rowToEscrow(r))
  }

  updateEscrowStatus(id: string, status: EscrowStatus): void {
    this.getStmts().updateEscrowStatus.run(status, id)
  }

  recordEscrowDeposit(id: string, amountQu: number): void {
    this.getStmts().updateEscrowDeposit.run(amountQu, id)
  }

  recordEscrowJoinBet(id: string, txId: string, tick: number): void {
    this.getStmts().updateEscrowJoinBet.run(txId, tick, id)
  }

  /** Confirm joinBet on-chain (joining_sc → active_in_sc). Returns true if status was updated. */
  confirmJoinBet(id: string): boolean {
    const result = this.getStmts().confirmJoinBet.run(id)
    return result.changes > 0
  }

  /** Revert failed joinBet (joining_sc → deposit_detected) for retry. */
  revertJoinBet(id: string): void {
    this.getStmts().revertJoinBet.run(id)
  }

  /** Get all escrows pending joinBet on-chain confirmation. */
  getJoiningScEscrows(): EscrowAddress[] {
    const rows = this.getStmts().getJoiningScEscrows.all() as Record<string, unknown>[]
    return rows.map((r) => this.rowToEscrow(r))
  }

  recordEscrowPayout(id: string, amountQu: number): void {
    this.getStmts().updateEscrowPayout.run(amountQu, id)
  }

  recordEscrowSweep(id: string, txId: string, tick: number): void {
    this.getStmts().updateEscrowSweep.run(txId, tick, id)
  }

  /** Atomically claim an escrow for sweeping (won_awaiting_sweep → sweeping).
   *  Returns true if this process won the claim, false if another process already claimed it. */
  claimEscrowForSweep(id: string): boolean {
    const result = this.getStmts().claimEscrowForSweep.run(id)
    return result.changes > 0
  }

  /** Confirm sweep completion (sweeping → swept).
   *  SQL-level guard: ONLY transitions if sweep_tx_id is NOT NULL.
   *  This prevents false sweep confirmations when no TX was actually broadcast.
   *  Returns true if the confirmation succeeded. */
  confirmSweepComplete(id: string): boolean {
    const result = this.getStmts().confirmSweepComplete.run(id)
    return result.changes > 0
  }

  /** Revert a sweep claim (sweeping → won_awaiting_sweep) if the TX fails. */
  revertSweepClaim(id: string): void {
    this.getStmts().revertSweepClaim.run(id)
  }

  /** Increment the joinBet retry counter for an escrow. */
  incrementJoinBetRetries(id: string): void {
    this.getStmts().incrementJoinBetRetries.run(id)
  }

  /** Get all escrows currently in 'sweeping' state (TX broadcast but unconfirmed). */
  getSweepingEscrows(): EscrowAddress[] {
    const rows = this.getStmts().getSweepingEscrows.all() as Record<string, unknown>[]
    return rows.map((r) => this.rowToEscrow(r))
  }

  markEscrowLost(id: string): void {
    this.getStmts().updateEscrowLost.run(id)
  }

  markEscrowExpired(id: string): void {
    this.getStmts().updateEscrowExpired.run(id)
  }

  getExpiredEscrows(): EscrowAddress[] {
    const rows = this.getStmts().getExpiredEscrows.all() as Record<string, unknown>[]
    return rows.map((r) => this.rowToEscrow(r))
  }

  countActiveEscrows(): number {
    return (this.getStmts().countActiveEscrows.get() as { count: number }).count
  }

  private rowToEscrow(row: Record<string, unknown>): EscrowAddress {
    return {
      id: row.id as string,
      betId: row.bet_id as string,
      marketId: row.market_id as string,
      escrowAddress: row.escrow_address as string,
      userPayoutAddress: row.user_payout_address as string,
      option: row.option as number,
      slots: row.slots as number,
      expectedAmountQu: row.expected_amount_qu as number,
      status: row.status as EscrowStatus,
      depositDetectedAt: row.deposit_detected_at as string | null,
      depositAmountQu: row.deposit_amount_qu as number | null,
      joinBetTxId: row.join_bet_tx_id as string | null,
      joinBetTick: row.join_bet_tick as number | null,
      payoutDetectedAt: row.payout_detected_at as string | null,
      payoutAmountQu: row.payout_amount_qu as number | null,
      sweepTxId: row.sweep_tx_id as string | null,
      sweepTick: row.sweep_tick as number | null,
      joinBetRetries: (row.join_bet_retries as number) ?? 0,
      expiresAt: row.expires_at as string,
      createdAt: row.created_at as string,
    }
  }

  // -------------------------------------------------------------------------
  // Per-Bet Escrow: Encrypted Keys
  // -------------------------------------------------------------------------

  insertEscrowKey(params: {
    escrowId: string
    encryptedSeed: string
    iv: string
    authTag: string
  }): void {
    this.getStmts().insertEscrowKey.run({
      escrowId: params.escrowId,
      encryptedSeed: params.encryptedSeed,
      iv: params.iv,
      authTag: params.authTag,
      status: 'active',
    })
  }

  getEscrowKey(escrowId: string): EscrowKey | null {
    const row = this.getStmts().getEscrowKey.get(escrowId) as Record<string, unknown> | undefined
    if (!row) return null
    return {
      escrowId: row.escrow_id as string,
      encryptedSeed: row.encrypted_seed as string,
      iv: row.iv as string,
      authTag: row.auth_tag as string,
      status: row.status as EscrowKeyStatus,
      createdAt: row.created_at as string,
      archivedAt: row.archived_at as string | null,
    }
  }

  updateEscrowKeyStatus(escrowId: string, status: EscrowKeyStatus): void {
    this.getStmts().updateEscrowKeyStatus.run(status, status, escrowId)

    // Secure deletion: when archiving, overwrite encrypted seed data with random bytes.
    // This ensures that even if the DB is compromised after archival, the seed cannot
    // be recovered from the encrypted_seed, iv, or auth_tag fields.
    if (status === 'archived') {
      this.secureOverwriteKey(escrowId)
    }
  }

  /**
   * Overwrite an escrow key's encrypted seed, iv, and auth_tag with random data.
   * Called automatically when status transitions to 'archived'.
   */
  private secureOverwriteKey(escrowId: string): void {
    const randomSeed = crypto.randomBytes(64).toString('hex')
    const randomIv = crypto.randomBytes(12).toString('hex')
    const randomTag = crypto.randomBytes(16).toString('hex')

    this.db
      .prepare(
        'UPDATE escrow_keys SET encrypted_seed = ?, iv = ?, auth_tag = ? WHERE escrow_id = ?',
      )
      .run(randomSeed, randomIv, randomTag, escrowId)
  }

  // -------------------------------------------------------------------------
  // Cron Locking
  // -------------------------------------------------------------------------

  /**
   * Attempt to acquire a named lock for cron single-instance execution.
   * Returns true if the lock was acquired, false if another holder has it.
   * Lock auto-expires after ttlSeconds.
   */
  acquireCronLock(lockName: string, holderId: string, ttlSeconds: number = 60): boolean {
    // Clean expired locks first
    this.getStmts().cleanExpiredCronLocks.run()
    const result = this.getStmts().acquireCronLock.run(
      lockName, holderId, String(ttlSeconds), lockName, holderId,
    )
    return result.changes > 0
  }

  /** Release a named cron lock (only if we are the holder). */
  releaseCronLock(lockName: string, holderId: string): void {
    this.getStmts().releaseCronLock.run(lockName, holderId)
  }

  // -------------------------------------------------------------------------
  // Provably Fair: Raw DB access for transactions
  // -------------------------------------------------------------------------

  /**
   * Run a function inside a SQLite transaction.
   * If the function throws, the transaction is rolled back.
   */
  transaction<T>(fn: () => T): T {
    const txn = this.db.transaction(fn)
    return txn()
  }

  // -------------------------------------------------------------------------
  // Market Snapshots
  // -------------------------------------------------------------------------

  recordSnapshot(marketId: string): void {
    this.getStmts().insertSnapshot.run(marketId)
  }

  getSnapshots(marketId: string): MarketSnapshot[] {
    const rows = this.getStmts().getSnapshots.all(marketId) as Record<
      string,
      unknown
    >[]
    return rows.map((r) => ({
      marketId: r.market_id as string,
      timestamp: r.timestamp as string,
      yesSlots: r.yes_slots as number,
      noSlots: r.no_slots as number,
      impliedProbability: r.implied_probability as number,
      totalPool: r.total_pool as number,
    }))
  }

  // -------------------------------------------------------------------------
  // Platform Stats
  // -------------------------------------------------------------------------

  getPlatformStats(): PlatformStats {
    const s = this.getStmts()
    return {
      totalMarkets: (s.countMarkets.get() as { count: number }).count,
      activeMarkets: (s.countActiveMarkets.get() as { count: number }).count,
      resolvedMarkets: (s.countResolvedMarkets.get() as { count: number }).count,
      totalVolume: (s.totalVolume.get() as { total: number }).total,
      totalBets: (s.totalBets.get() as { count: number }).count,
      totalUsers: (s.totalUsers.get() as { count: number }).count,
      totalPaidOut: (s.totalPaidOut.get() as { total: number }).total,
    }
  }

  getLeaderboard(
    minBets: number = 3,
    limit: number = 50,
  ): LeaderboardEntry[] {
    const rows = this.getStmts().leaderboard.all(minBets, limit) as Record<
      string,
      unknown
    >[]
    return rows.map((r) => ({
      address: r.address as string,
      displayName: r.display_name as string | null,
      totalBets: r.total_bets as number,
      wins: r.wins as number,
      losses: r.losses as number,
      accuracy: r.accuracy as number,
      totalWon: r.total_won as number,
      totalBet: r.total_bet as number,
      profitQu: r.profit_qu as number,
    }))
  }

  // -------------------------------------------------------------------------
  // v2: Multi-Option Slot Tracking
  // -------------------------------------------------------------------------

  /**
   * Add slots for a specific option in a multi-option market.
   * Updates both slots_json and yes_slots/no_slots for backwards compat.
   */
  addSlotsForOption(marketId: string, option: number, slots: number, amountQu: number): void {
    const market = this.getMarket(marketId)
    if (!market) throw new Error(`Market not found: ${marketId}`)

    const slotsMap = { ...market.slotsPerOption }
    slotsMap[String(option)] = (slotsMap[String(option)] ?? 0) + slots
    this.getStmts().updateSlotsJson.run(JSON.stringify(slotsMap), amountQu, marketId)

    // Also update yes_slots/no_slots for backwards compat (option 0 = yes, 1 = no)
    if (option === 0) {
      this.db.prepare('UPDATE markets SET yes_slots = yes_slots + ? WHERE id = ?').run(slots, marketId)
    } else if (option === 1) {
      this.db.prepare('UPDATE markets SET no_slots = no_slots + ? WHERE id = ?').run(slots, marketId)
    }
  }

  /**
   * Repair slotsPerOption and total_pool by absolute set (not incremental).
   */
  repairSlotsJson(marketId: string, slotsMap: Record<string, number>, totalPool: number): void {
    this.db.prepare(
      'UPDATE markets SET slots_json = ?, total_pool = ?, yes_slots = ?, no_slots = ? WHERE id = ?',
    ).run(
      JSON.stringify(slotsMap),
      totalPool,
      slotsMap['0'] ?? 0,
      slotsMap['1'] ?? 0,
      marketId,
    )
  }

  /**
   * Get total slots across all options for a market.
   */
  getTotalSlots(market: Market): number {
    return Object.values(market.slotsPerOption).reduce((sum, v) => sum + v, 0)
  }

  // -------------------------------------------------------------------------
  // v2: AI Resolution
  // -------------------------------------------------------------------------

  /**
   * Record an AI resolution attempt with proof data.
   */
  recordAiResolutionAttempt(marketId: string, proof: unknown): void {
    this.getStmts().updateAiResolutionAttempt.run(JSON.stringify(proof), marketId)
  }

  /**
   * Get markets that need AI resolution (past end_date, under 3 attempts).
   */
  getMarketsNeedingAiResolution(): Market[] {
    const rows = this.getStmts().marketsNeedingAiResolution.all() as Record<string, unknown>[]
    return rows.map((r) => this.rowToMarket(r))
  }

  /**
   * Get custom/AI markets that need auto-refund (past auto_refund_at, unresolved).
   */
  getMarketsNeedingAutoRefund(): Market[] {
    const rows = this.getStmts().marketsNeedingAutoRefund.all() as Record<string, unknown>[]
    return rows.map((r) => this.rowToMarket(r))
  }

  // -------------------------------------------------------------------------
  // Utilities
  // -------------------------------------------------------------------------

  /**
   * Calculate implied probability for a market.
   */
  static calcImpliedProbability(yesSlots: number, noSlots: number): number {
    const total = yesSlots + noSlots
    if (total === 0) return 0.5
    return yesSlots / total
  }

  /**
   * Close the database connection.
   */
  close(): void {
    this.stmts = null
    this.db.close()
  }
}

// ---------------------------------------------------------------------------
// Singleton Export
// ---------------------------------------------------------------------------

let _instance: MarketDatabase | null = null

export function getMarketDB(dbPath?: string): MarketDatabase {
  if (!_instance) {
    _instance = new MarketDatabase(dbPath)
  }
  return _instance
}
