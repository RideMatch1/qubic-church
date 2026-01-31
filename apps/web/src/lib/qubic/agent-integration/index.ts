/**
 * Qubic Agent Integration
 *
 * This module provides everything needed to integrate Qubic blockchain
 * identity and action logging into the jim-ops agent system.
 *
 * Usage:
 *
 * ```typescript
 * import {
 *   generateSeed,
 *   getAgentIdentity,
 *   signAction,
 *   verifySignedAction,
 *   logToBlockchain
 * } from '@/lib/qubic/agent-integration';
 *
 * // Get agent identity
 * const jimIdentity = await getAgentIdentity('jim');
 *
 * // Sign an action
 * const signedAction = await signAction(
 *   { value: process.env.QUBIC_SEED_JIM! },
 *   'APPROVE',
 *   'jim',
 *   'Approved deployment of Hundementor v1.2'
 * );
 *
 * // Optionally log to blockchain
 * const log = await logToBlockchain(
 *   { value: process.env.QUBIC_SEED_JIM! },
 *   signedAction
 * );
 *
 * console.log('Action logged:', log.txHash);
 * ```
 *
 * @module qubic/agent-integration
 */

// Types
export type {
  QubicSeed,
  QubicIdentity,
  ActionType,
  SignedAction,
  BlockchainLog,
  AgentStatus,
  UserWallet,
} from './types';

// Identity Management
export {
  generateSeed,
  validateSeed,
  validatePublicId,
  createIdentity,
  getAgentIdentity,
  generateAllAgentSeeds,
} from './identity';

// Action Signing
export {
  signAction,
  verifySignedAction,
  createActionSummary,
  formatActionForBlackboard,
} from './signer';

// Blockchain Logging
export {
  logToBlockchain,
  verifyBlockchainLog,
  getAgentBlockchainLogs,
  storeLogLocally,
  readLocalLogs,
} from './logger';
