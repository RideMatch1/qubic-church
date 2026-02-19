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

  // Use official Qubic library for Schnorr signatures — no fallback.
  // If the SDK is unavailable, operations MUST fail rather than silently
  // degrading to HMAC which provides no cryptographic identity proof.
  try {
    const { createRequire } = await import('module');
    const require = createRequire(import.meta.url);
    const lib = require('@qubic-lib/qubic-ts-library').default;
    const helper = new lib.QubicHelper();
    const idPackage = await helper.createIdPackage(seed.value);

    const sig = await helper.signMessage(
      seed.value,
      Buffer.from(messageHash, 'hex')
    );

    signature = Buffer.from(sig).toString('hex');
    publicId = idPackage.publicId;
  } catch (err) {
    throw new Error(
      `Qubic SDK required for signing — cannot operate without @qubic-lib/qubic-ts-library: ${err instanceof Error ? err.message : String(err)}`
    );
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

  // Use official Qubic library for signature verification — no fallback.
  // Format-only checks are NOT cryptographic verification and must never
  // be used as a substitute for real signature verification.
  try {
    const { createRequire: createReq } = await import('module');
    const req = createReq(import.meta.url);
    const qLib = req('@qubic-lib/qubic-ts-library').default;
    const verifyHelper = new qLib.QubicHelper();

    const isValid = await verifyHelper.verifySignature(
      signedAction.publicId,
      Buffer.from(messageHash, 'hex'),
      Buffer.from(signedAction.signature, 'hex')
    );

    return isValid;
  } catch (err) {
    throw new Error(
      `Qubic SDK required for signature verification — cannot verify without @qubic-lib/qubic-ts-library: ${err instanceof Error ? err.message : String(err)}`
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
