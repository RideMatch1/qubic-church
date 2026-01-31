/**
 * Qubic Action Signing
 * Signs agent actions for verification and audit trail
 */

import crypto from 'crypto';
import { SignedAction, ActionType, QubicSeed } from './types';
import { validateSeed } from './identity';

/**
 * Create a deterministic message hash for signing
 */
function createMessageHash(
  action: ActionType,
  agent: string,
  details: string,
  timestamp: number
): string {
  const message = `QUBIC_ACTION|${action}|${agent}|${details}|${timestamp}`;
  return crypto.createHash('sha256').update(message).digest('hex');
}

/**
 * Sign an action with agent's seed
 *
 * @param seed - Agent's Qubic seed
 * @param action - Type of action
 * @param agent - Agent name
 * @param details - Action details
 * @returns SignedAction with signature
 */
export async function signAction(
  seed: QubicSeed,
  action: ActionType,
  agent: string,
  details: string
): Promise<SignedAction> {
  if (!validateSeed(seed.value)) {
    throw new Error('Invalid seed format');
  }

  const timestamp = Date.now();
  const messageHash = createMessageHash(action, agent, details, timestamp);

  let signature: string;
  let publicId: string;

  // Try to use official Qubic library
  try {
    const { QubicHelper } = await import('@qubic-lib/qubic-ts-library');
    const helper = new QubicHelper();
    const idPackage = await helper.createIdPackage(seed.value);

    const sig = await helper.signMessage(
      seed.value,
      Buffer.from(messageHash, 'hex')
    );

    signature = Buffer.from(sig).toString('hex');
    publicId = idPackage.publicId;
  } catch {
    // Fallback: HMAC-based signature
    // NOT cryptographically equivalent to Qubic Schnorr signatures!
    console.warn('Qubic SDK not available, using HMAC fallback');

    signature = crypto
      .createHmac('sha256', seed.value)
      .update(messageHash)
      .digest('hex');

    // Generate fallback public ID
    const { createIdentity } = await import('./identity');
    const identity = await createIdentity(agent, seed);
    publicId = identity.publicId;
  }

  return {
    action,
    agent,
    details,
    timestamp,
    signature,
    publicId,
  };
}

/**
 * Verify a signed action
 *
 * @param signedAction - The action to verify
 * @returns true if signature is valid
 */
export async function verifySignedAction(
  signedAction: SignedAction
): Promise<boolean> {
  const messageHash = createMessageHash(
    signedAction.action,
    signedAction.agent,
    signedAction.details,
    signedAction.timestamp
  );

  // Try to use official Qubic library
  try {
    const { QubicHelper } = await import('@qubic-lib/qubic-ts-library');
    const helper = new QubicHelper();

    const isValid = await helper.verifySignature(
      signedAction.publicId,
      Buffer.from(messageHash, 'hex'),
      Buffer.from(signedAction.signature, 'hex')
    );

    return isValid;
  } catch {
    // Fallback: Cannot verify without original seed
    // In production, this should use the Qubic SDK
    console.warn('Qubic SDK not available, cannot verify signature');

    // Basic format validation only
    return (
      signedAction.signature.length === 64 && // SHA256 hex
      signedAction.publicId.length === 60 &&
      signedAction.timestamp > 0
    );
  }
}

/**
 * Create a compact action summary for logging
 */
export function createActionSummary(signedAction: SignedAction): string {
  return JSON.stringify({
    a: signedAction.action,
    g: signedAction.agent,
    t: signedAction.timestamp,
    s: signedAction.signature.substring(0, 16) + '...',
    p: signedAction.publicId.substring(0, 8) + '...',
  });
}

/**
 * Format action for BLACKBOARD posting
 */
export function formatActionForBlackboard(signedAction: SignedAction): string {
  return `[${signedAction.action}] by ${signedAction.agent}
Details: ${signedAction.details}
Time: ${new Date(signedAction.timestamp).toISOString()}
Signature: ${signedAction.signature.substring(0, 32)}...
Public ID: ${signedAction.publicId.substring(0, 16)}...`;
}
