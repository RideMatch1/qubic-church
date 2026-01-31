/**
 * Qubic Blockchain Logger
 * Logs agent actions to Qubic blockchain for immutable audit trail
 */

import { SignedAction, BlockchainLog, QubicSeed } from './types';

// Qubic RPC endpoint
const QUBIC_RPC_URL =
  process.env.QUBIC_RPC_URL || 'https://rpc.qubic.org';

// For logging without value transfer, we use a null/burn address
const NULL_ADDRESS =
  'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';

/**
 * Log a signed action to Qubic blockchain
 *
 * NOTE: Full blockchain integration requires Qu tokens for transaction fees.
 * This implementation provides the framework - actual transaction sending
 * depends on Qubic SDK availability and network access.
 *
 * @param seed - Agent's seed for signing transaction
 * @param signedAction - The action to log
 * @returns BlockchainLog with transaction details
 */
export async function logToBlockchain(
  seed: QubicSeed,
  signedAction: SignedAction
): Promise<BlockchainLog> {
  // Create compact payload for blockchain
  const payload = {
    a: signedAction.action,
    g: signedAction.agent,
    d: signedAction.details.substring(0, 32), // Truncate for efficiency
    t: signedAction.timestamp,
    s: signedAction.signature.substring(0, 32),
  };

  const payloadHash = Buffer.from(JSON.stringify(payload)).toString('base64');

  // Try to send actual transaction
  try {
    const { QubicHelper, QubicTransaction } = await import(
      '@qubic-lib/qubic-ts-library'
    );

    const helper = new QubicHelper();
    const idPackage = await helper.createIdPackage(seed.value);

    // Get current tick from network
    const tickResponse = await fetch(`${QUBIC_RPC_URL}/status`);
    const { tick: currentTick } = await tickResponse.json();

    // Create minimal transaction (0 Qu transfer, just for logging)
    // The transaction itself is the record - payload in input data
    const tx = new QubicTransaction();
    tx.setSourcePublicKey(idPackage.publicKey);
    tx.setDestinationPublicKey(NULL_ADDRESS);
    tx.setAmount(0);
    tx.setTick(currentTick + 5); // Execute in 5 ticks
    tx.setInputType(0);
    tx.setInputSize(payloadHash.length);
    // tx.setInput(Buffer.from(payloadHash));

    // Sign transaction
    const signedTx = await helper.signTransaction(seed.value, tx);

    // Broadcast to network
    const broadcastResponse = await fetch(`${QUBIC_RPC_URL}/broadcast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transaction: signedTx.toBase64(),
      }),
    });

    if (!broadcastResponse.ok) {
      throw new Error(`Broadcast failed: ${broadcastResponse.status}`);
    }

    const { txHash } = await broadcastResponse.json();

    return {
      txHash,
      tick: currentTick + 5,
      action: signedAction,
      verified: false, // Will be verified after confirmation
    };
  } catch (error) {
    // Fallback: Local logging only
    console.warn('Blockchain logging failed, using local fallback:', error);

    // Generate deterministic "transaction hash" for local tracking
    const localTxHash = `LOCAL_${signedAction.agent}_${signedAction.timestamp}_${signedAction.signature.substring(0, 8)}`;

    return {
      txHash: localTxHash,
      tick: 0, // Local only, no tick
      action: signedAction,
      verified: false,
    };
  }
}

/**
 * Verify a blockchain log by checking transaction status
 *
 * @param txHash - Transaction hash to verify
 * @returns true if transaction is confirmed on blockchain
 */
export async function verifyBlockchainLog(txHash: string): Promise<boolean> {
  // Local transactions cannot be verified on blockchain
  if (txHash.startsWith('LOCAL_')) {
    console.warn('Cannot verify local transaction on blockchain');
    return false;
  }

  try {
    const response = await fetch(`${QUBIC_RPC_URL}/tx/${txHash}`);

    if (!response.ok) {
      return false;
    }

    const txData = await response.json();
    return txData.confirmed === true;
  } catch (error) {
    console.error('Blockchain verification failed:', error);
    return false;
  }
}

/**
 * Get recent blockchain logs for an agent
 *
 * @param publicId - Agent's public ID
 * @param limit - Maximum number of logs to retrieve
 * @returns Array of BlockchainLog
 */
export async function getAgentBlockchainLogs(
  publicId: string,
  limit: number = 50
): Promise<BlockchainLog[]> {
  try {
    const response = await fetch(
      `${QUBIC_RPC_URL}/address/${publicId}/transactions?limit=${limit}`
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch logs: ${response.status}`);
    }

    const { transactions } = await response.json();

    // Parse transactions back to BlockchainLog format
    // This depends on how we encoded the payload
    return transactions.map((tx: any) => ({
      txHash: tx.hash,
      tick: tx.tick,
      action: parseActionFromTx(tx),
      verified: tx.confirmed,
    }));
  } catch (error) {
    console.error('Failed to fetch blockchain logs:', error);
    return [];
  }
}

/**
 * Parse action data from transaction
 */
function parseActionFromTx(tx: any): SignedAction {
  try {
    const payload = JSON.parse(
      Buffer.from(tx.input || '', 'base64').toString()
    );

    return {
      action: payload.a,
      agent: payload.g,
      details: payload.d,
      timestamp: payload.t,
      signature: payload.s,
      publicId: tx.source,
    };
  } catch {
    // Return minimal action if parsing fails
    return {
      action: 'CRITICAL',
      agent: 'unknown',
      details: 'Unparseable transaction',
      timestamp: Date.now(),
      signature: '',
      publicId: tx.source || '',
    };
  }
}

/**
 * Store log locally (for when blockchain is unavailable)
 */
export function storeLogLocally(log: BlockchainLog, storagePath: string): void {
  const fs = require('fs');
  const path = require('path');

  const logsDir = path.dirname(storagePath);
  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
  }

  // Append to log file
  const logLine = JSON.stringify(log) + '\n';
  fs.appendFileSync(storagePath, logLine);
}

/**
 * Read local logs
 */
export function readLocalLogs(storagePath: string): BlockchainLog[] {
  const fs = require('fs');

  try {
    const content = fs.readFileSync(storagePath, 'utf-8');
    return content
      .split('\n')
      .filter((line: string) => line.trim())
      .map((line: string) => JSON.parse(line));
  } catch {
    return [];
  }
}
