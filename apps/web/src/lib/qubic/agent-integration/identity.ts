/**
 * Qubic Agent Identity Management
 * Handles seed generation, identity creation, and validation
 */

import crypto from 'crypto';
import { QubicSeed, QubicIdentity } from './types';

// Qubic uses only lowercase letters for seeds
const SEED_ALPHABET = 'abcdefghijklmnopqrstuvwxyz';
const SEED_LENGTH = 55;
const PUBLIC_ID_LENGTH = 60;

/**
 * Generate a cryptographically secure Qubic seed
 * @returns QubicSeed with 55 lowercase letters
 */
export function generateSeed(): QubicSeed {
  let seed = '';

  for (let i = 0; i < SEED_LENGTH; i++) {
    const randomIndex = crypto.randomInt(0, SEED_ALPHABET.length);
    seed += SEED_ALPHABET[randomIndex];
  }

  return { value: seed };
}

/**
 * Validate seed format
 * @param seed - String to validate
 * @returns true if valid Qubic seed format
 */
export function validateSeed(seed: string): boolean {
  if (seed.length !== SEED_LENGTH) return false;
  return /^[a-z]+$/.test(seed);
}

/**
 * Validate public ID format
 * @param id - String to validate
 * @returns true if valid Qubic public ID format
 */
export function validatePublicId(id: string): boolean {
  if (id.length !== PUBLIC_ID_LENGTH) return false;
  return /^[A-Z]+$/.test(id);
}

/**
 * Create identity from seed
 * NOTE: This is a simplified version. For production, use @qubic-lib/qubic-ts-library
 *
 * @param name - Agent name
 * @param seed - Qubic seed
 * @returns QubicIdentity
 */
export async function createIdentity(
  name: string,
  seed: QubicSeed
): Promise<QubicIdentity> {
  if (!validateSeed(seed.value)) {
    throw new Error('Invalid seed format');
  }

  // Use official Qubic library to derive real on-chain address
  // The library exports as CJS with .default, so we use createRequire
  try {
    const { createRequire } = await import('module');
    const require = createRequire(import.meta.url);
    const lib = require('@qubic-lib/qubic-ts-library').default;
    const helper = new lib.QubicHelper();
    const idPackage = await helper.createIdPackage(seed.value);

    return {
      name,
      publicId: idPackage.publicId,
      createdAt: Date.now(),
    };
  } catch (err) {
    throw new Error(
      `Failed to derive Qubic identity: @qubic-lib/qubic-ts-library is required. ` +
      `Install with: pnpm add @qubic-lib/qubic-ts-library. ` +
      `Original error: ${err instanceof Error ? err.message : String(err)}`
    );
  }
}

/**
 * Get agent identity from environment variable
 * @param agentName - Name of agent (jim, otto, anna)
 * @returns QubicIdentity
 */
export async function getAgentIdentity(
  agentName: 'jim' | 'otto' | 'anna'
): Promise<QubicIdentity> {
  const seedEnvVar = `QUBIC_SEED_${agentName.toUpperCase()}`;
  const seed = process.env[seedEnvVar];

  if (!seed) {
    throw new Error(`Missing environment variable: ${seedEnvVar}`);
  }

  if (!validateSeed(seed)) {
    throw new Error(`Invalid seed format for ${agentName}`);
  }

  return createIdentity(agentName, { value: seed });
}

/**
 * Generate seeds for all agents (run once during setup)
 * Outputs to console - copy to .env file
 */
export function generateAllAgentSeeds(): void {
  const agents = ['jim', 'otto', 'anna'];

  console.log('\n=== QUBIC AGENT SEEDS ===');
  console.log('Copy these to your .env file:\n');

  for (const agent of agents) {
    const seed = generateSeed();
    console.log(`QUBIC_SEED_${agent.toUpperCase()}=${seed.value}`);
  }

  console.log('\n=== IMPORTANT ===');
  console.log('Never share these seeds!');
  console.log('Never commit them to git!');
  console.log('Store securely in .env or secrets manager.\n');
}

// CLI support: Run with `npx ts-node identity.ts generate`
if (require.main === module) {
  const command = process.argv[2];

  if (command === 'generate') {
    generateAllAgentSeeds();
  } else {
    console.log('Usage: npx ts-node identity.ts generate');
  }
}
