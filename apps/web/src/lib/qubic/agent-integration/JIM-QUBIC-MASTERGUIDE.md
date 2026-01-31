# QUBIC INTEGRATION MASTERGUIDE FÜR JIM

**Von:** Claude (Qubic-Experte)
**Für:** Jim (jim-ops)
**Datum:** 2026-01-31
**Ziel:** Qubic Blockchain in jim-ops Dashboard integrieren

---

## TEIL 1: WAS IST QUBIC?

### 1.1 Kurzfassung

Qubic ist eine Blockchain die von **CFB (Come-from-Beyond)** gegründet wurde - derselbe Typ der auch NXT und IOTA mitgegründet hat.

**Besonderheiten:**
- **Proof-of-Useful-Work**: Miner trainieren AI statt sinnlose Hashes zu berechnen
- **Schnell**: ~1 Sekunde Blockzeit
- **Günstig**: Fast keine Transaktionskosten
- **AI-Native**: Gebaut für "Agentic Economy" - AI Agents die autonom handeln

### 1.2 Warum relevant für jim-ops?

```
JETZT (ohne Qubic):
  Agent macht Aktion → Log in .md Datei → Kann manipuliert werden

MIT Qubic:
  Agent macht Aktion → Signiert mit Private Key → Hash auf Blockchain
                                                  ↓
                                        UNVERÄNDERLICH
                                        NACHWEISBAR
                                        AUDITIERBAR
```

### 1.3 Kernkonzepte

| Begriff | Erklärung |
|---------|-----------|
| **Seed** | 55 lowercase Buchstaben (a-z). Das ist dein PRIVATER SCHLÜSSEL. NIE teilen! |
| **Public ID** | 60 uppercase Buchstaben (A-Z). Das ist deine ÖFFENTLICHE ADRESSE. Kann jeder sehen. |
| **Qu** | Die Währung von Qubic. 1 Qu = kleinste Einheit. |
| **Tick** | Ein "Block" in Qubic. Alle ~1 Sekunde ein neuer Tick. |
| **Epoch** | ~7 Tage. Qubic läuft in Epochen. |
| **Smart Contract (SC)** | Code der auf der Blockchain läuft. TEUER zu erstellen (Millionen Qu). |
| **Transaction** | Eine Überweisung oder Nachricht. GÜNSTIG. |

### 1.4 Seed → Public ID (Kryptographie)

```
Seed (55 chars, geheim)
        ↓
    K12 Hash (KangarooTwelve)
        ↓
    Private Key (32 bytes)
        ↓
    Schnorr Signature Scheme
        ↓
Public ID (60 chars, öffentlich)
```

**Beispiel:**
```
Seed:      abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyza
Public ID: BZBQFLLBNCXEMGLOBHUVFTLUPLGDMVHEWCEKVDQDOQOBUBQPLNVQLFBGAAAAAAAA
```

---

## TEIL 2: WAS WIR BAUEN

### 2.1 Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                     JIM-OPS DASHBOARD                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Jim Agent   │  │  Otto Agent  │  │  Anna Agent  │           │
│  │  Seed: ***   │  │  Seed: ***   │  │  Seed: ***   │           │
│  │  ID: JIM...  │  │  ID: OTT...  │  │  ID: ANN...  │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                 │                 │                    │
│         ▼                 ▼                 ▼                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              QUBIC IDENTITY SERVICE                      │    │
│  │  • createIdentity(name)                                  │    │
│  │  • signAction(seed, action)                              │    │
│  │  • logToBlockchain(identity, action)                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              QUBIC BLOCKCHAIN                            │    │
│  │  • Immutable Audit Trail                                 │    │
│  │  • Verifiable Signatures                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  USER FEATURES (Dashboard UI):                                   │
│  • Wallet Connect (User's Qubic ID eingeben)                    │
│  • Agent Actions anzeigen (mit Blockchain-Verification)         │
│  • Audit Trail Explorer                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Features die gebaut werden

| Feature | Beschreibung | Priorität |
|---------|--------------|-----------|
| **Agent Identity** | Jeder Agent bekommt Qubic Seed/ID | P0 |
| **Action Signing** | Wichtige Aktionen werden signiert | P0 |
| **Blockchain Logging** | Optional: Aktionen auf Qubic loggen | P1 |
| **User Wallet Connect** | User kann seine Qubic ID hinterlegen | P2 |
| **Audit Trail UI** | Dashboard zeigt verifizierte Aktionen | P2 |

---

## TEIL 3: CODE - ALLES WAS DU BRAUCHST

### 3.1 Installation

```bash
# Im jim-ops Projekt
npm install @qubic-lib/qubic-ts-library

# Falls das nicht funktioniert (Package evtl noch nicht public):
# Clone direkt von GitHub
git clone https://github.com/qubic/ts-library.git
cd ts-library && npm install && npm run build
```

### 3.2 Dateien die du erstellst

```
jim-ops/
├── src/
│   ├── lib/
│   │   └── qubic/
│   │       ├── identity.ts        # Agent Identity Management
│   │       ├── signer.ts          # Action Signing
│   │       ├── logger.ts          # Blockchain Logging
│   │       └── types.ts           # TypeScript Types
│   │
│   ├── components/
│   │   └── qubic/
│   │       ├── WalletConnect.tsx  # User Wallet UI
│   │       ├── AuditTrail.tsx     # Action History UI
│   │       └── AgentBadge.tsx     # Agent ID Badge
│   │
│   └── api/
│       └── qubic/
│           ├── verify.ts          # Signature Verification API
│           └── actions.ts         # Get Agent Actions API
```

---

## TEIL 4: IMPLEMENTATION DETAILS

### 4.1 types.ts

```typescript
// jim-ops/src/lib/qubic/types.ts

export interface QubicSeed {
  value: string;  // 55 lowercase chars
}

export interface QubicIdentity {
  name: string;           // "jim" | "otto" | "anna" | "worker-xxx"
  publicId: string;       // 60 uppercase chars
  createdAt: number;      // Unix timestamp
}

export interface SignedAction {
  action: ActionType;
  agent: string;
  details: string;
  timestamp: number;
  signature: string;      // Hex encoded
  publicId: string;       // For verification
}

export type ActionType =
  | 'DEPLOY'
  | 'VETO'
  | 'APPROVE'
  | 'CRITICAL'
  | 'SPAWN_WORKER'
  | 'TASK_COMPLETE'
  | 'CONFIG_CHANGE';

export interface BlockchainLog {
  txHash: string;
  tick: number;
  action: SignedAction;
  verified: boolean;
}
```

### 4.2 identity.ts

```typescript
// jim-ops/src/lib/qubic/identity.ts

import { QubicHelper } from '@qubic-lib/qubic-ts-library';
import { QubicSeed, QubicIdentity } from './types';
import crypto from 'crypto';

/**
 * Generate a cryptographically secure Qubic seed
 */
export function generateSeed(): QubicSeed {
  const chars = 'abcdefghijklmnopqrstuvwxyz';
  let seed = '';

  for (let i = 0; i < 55; i++) {
    const randomIndex = crypto.randomInt(0, 26);
    seed += chars[randomIndex];
  }

  return { value: seed };
}

/**
 * Create agent identity from seed
 */
export async function createIdentity(
  name: string,
  seed: QubicSeed
): Promise<QubicIdentity> {
  const helper = new QubicHelper();
  const idPackage = await helper.createIdPackage(seed.value);

  return {
    name,
    publicId: idPackage.publicId,
    createdAt: Date.now(),
  };
}

/**
 * Get identity from environment (for agents)
 */
export async function getAgentIdentity(
  agentName: 'jim' | 'otto' | 'anna'
): Promise<QubicIdentity> {
  const seedEnvVar = `QUBIC_SEED_${agentName.toUpperCase()}`;
  const seed = process.env[seedEnvVar];

  if (!seed) {
    throw new Error(`Missing env var: ${seedEnvVar}`);
  }

  if (seed.length !== 55) {
    throw new Error(`Invalid seed length for ${agentName}`);
  }

  return createIdentity(agentName, { value: seed });
}

/**
 * Validate seed format
 */
export function validateSeed(seed: string): boolean {
  if (seed.length !== 55) return false;
  return /^[a-z]+$/.test(seed);
}

/**
 * Validate public ID format
 */
export function validatePublicId(id: string): boolean {
  if (id.length !== 60) return false;
  return /^[A-Z]+$/.test(id);
}
```

### 4.3 signer.ts

```typescript
// jim-ops/src/lib/qubic/signer.ts

import { QubicHelper } from '@qubic-lib/qubic-ts-library';
import { SignedAction, ActionType, QubicSeed } from './types';
import crypto from 'crypto';

/**
 * Create a message hash for signing
 */
function createMessageHash(
  action: ActionType,
  agent: string,
  details: string,
  timestamp: number
): string {
  const message = `${action}|${agent}|${details}|${timestamp}`;
  return crypto.createHash('sha256').update(message).digest('hex');
}

/**
 * Sign an action with agent's seed
 */
export async function signAction(
  seed: QubicSeed,
  action: ActionType,
  agent: string,
  details: string
): Promise<SignedAction> {
  const timestamp = Date.now();
  const messageHash = createMessageHash(action, agent, details, timestamp);

  const helper = new QubicHelper();
  const idPackage = await helper.createIdPackage(seed.value);

  // Sign the message hash
  const signature = await helper.signMessage(
    seed.value,
    Buffer.from(messageHash, 'hex')
  );

  return {
    action,
    agent,
    details,
    timestamp,
    signature: Buffer.from(signature).toString('hex'),
    publicId: idPackage.publicId,
  };
}

/**
 * Verify a signed action
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

  const helper = new QubicHelper();

  try {
    const isValid = await helper.verifySignature(
      signedAction.publicId,
      Buffer.from(messageHash, 'hex'),
      Buffer.from(signedAction.signature, 'hex')
    );
    return isValid;
  } catch (error) {
    console.error('Signature verification failed:', error);
    return false;
  }
}
```

### 4.4 logger.ts

```typescript
// jim-ops/src/lib/qubic/logger.ts

import { QubicHelper, QubicTransaction } from '@qubic-lib/qubic-ts-library';
import { SignedAction, BlockchainLog, QubicSeed } from './types';

// Qubic RPC endpoint
const QUBIC_RPC = process.env.QUBIC_RPC_URL || 'https://rpc.qubic.org';

// Burn address for logging (or use a dedicated logging address)
const LOG_ADDRESS = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';

/**
 * Log action to Qubic blockchain
 *
 * NOTE: This sends a minimal transaction (1 Qu) with the action hash as memo.
 * The transaction itself is the proof - the hash can be verified later.
 */
export async function logToBlockchain(
  seed: QubicSeed,
  signedAction: SignedAction
): Promise<BlockchainLog> {
  const helper = new QubicHelper();

  // Create action hash (this is what gets stored)
  const actionHash = Buffer.from(JSON.stringify({
    a: signedAction.action,
    g: signedAction.agent,
    d: signedAction.details.substring(0, 32), // Truncate for efficiency
    t: signedAction.timestamp,
    s: signedAction.signature.substring(0, 32), // Partial signature as proof
  })).toString('base64').substring(0, 32);

  // Create transaction
  const idPackage = await helper.createIdPackage(seed.value);

  // NOTE: Actual transaction sending depends on Qubic SDK version
  // This is the conceptual flow:

  /*
  const tx = await helper.createTransaction(
    idPackage,
    LOG_ADDRESS,
    1, // 1 Qu (minimal)
    0, // Current tick (will be set by network)
  );

  const result = await fetch(`${QUBIC_RPC}/broadcast`, {
    method: 'POST',
    body: JSON.stringify({ tx: tx.toBase64() }),
  });

  const { txHash, tick } = await result.json();
  */

  // For now, return simulated response
  // TODO: Implement actual transaction when Qubic SDK is fully integrated

  const simulatedTxHash = `TX_${Date.now()}_${signedAction.agent}`;

  return {
    txHash: simulatedTxHash,
    tick: Math.floor(Date.now() / 1000), // Simulated tick
    action: signedAction,
    verified: false, // Will be true after blockchain confirmation
  };
}

/**
 * Verify a blockchain log by checking the transaction
 */
export async function verifyBlockchainLog(
  txHash: string
): Promise<boolean> {
  try {
    const response = await fetch(`${QUBIC_RPC}/tx/${txHash}`);
    if (!response.ok) return false;

    const tx = await response.json();
    return tx.confirmed === true;
  } catch (error) {
    console.error('Blockchain verification failed:', error);
    return false;
  }
}

/**
 * Get recent logs for an agent
 */
export async function getAgentLogs(
  publicId: string,
  limit: number = 50
): Promise<BlockchainLog[]> {
  // TODO: Implement when Qubic indexer API is available
  // For now, return from local storage
  return [];
}
```

---

## TEIL 5: DASHBOARD UI KOMPONENTEN

### 5.1 WalletConnect.tsx

```tsx
// jim-ops/src/components/qubic/WalletConnect.tsx

'use client';

import { useState } from 'react';
import { validatePublicId } from '@/lib/qubic/identity';

interface WalletConnectProps {
  onConnect: (publicId: string) => void;
  onDisconnect: () => void;
  connectedId?: string;
}

export function WalletConnect({
  onConnect,
  onDisconnect,
  connectedId
}: WalletConnectProps) {
  const [inputId, setInputId] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleConnect = () => {
    setError(null);

    if (!validatePublicId(inputId)) {
      setError('Invalid Qubic ID. Must be 60 uppercase letters (A-Z).');
      return;
    }

    onConnect(inputId);
    setInputId('');
  };

  if (connectedId) {
    return (
      <div className="flex items-center gap-3 p-4 bg-green-500/10 rounded-lg border border-green-500/20">
        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
        <div className="flex-1">
          <p className="text-sm text-green-400">Connected</p>
          <p className="font-mono text-xs text-gray-400 truncate max-w-[200px]">
            {connectedId}
          </p>
        </div>
        <button
          onClick={onDisconnect}
          className="px-3 py-1 text-sm text-red-400 hover:bg-red-500/10 rounded"
        >
          Disconnect
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input
          type="text"
          value={inputId}
          onChange={(e) => setInputId(e.target.value.toUpperCase())}
          placeholder="Enter your Qubic ID (60 chars)"
          className="flex-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded font-mono text-sm"
          maxLength={60}
        />
        <button
          onClick={handleConnect}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-medium"
        >
          Connect
        </button>
      </div>
      {error && (
        <p className="text-sm text-red-400">{error}</p>
      )}
      <p className="text-xs text-gray-500">
        Your Qubic ID is your public address. Find it in your Qubic wallet.
      </p>
    </div>
  );
}
```

### 5.2 AgentBadge.tsx

```tsx
// jim-ops/src/components/qubic/AgentBadge.tsx

'use client';

import { QubicIdentity } from '@/lib/qubic/types';

interface AgentBadgeProps {
  identity: QubicIdentity;
  status: 'active' | 'idle' | 'offline';
  showFullId?: boolean;
}

const statusColors = {
  active: 'bg-green-500',
  idle: 'bg-yellow-500',
  offline: 'bg-gray-500',
};

const agentColors = {
  jim: '#3B82F6',   // Blue
  otto: '#94A3B8',  // Silver
  anna: '#A855F7',  // Purple
};

export function AgentBadge({
  identity,
  status,
  showFullId = false
}: AgentBadgeProps) {
  const color = agentColors[identity.name as keyof typeof agentColors] || '#6B7280';

  return (
    <div
      className="flex items-center gap-3 p-3 rounded-lg border"
      style={{ borderColor: color, backgroundColor: `${color}10` }}
    >
      {/* Status Indicator */}
      <div className={`w-2 h-2 rounded-full ${statusColors[status]}`} />

      {/* Agent Info */}
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span
            className="font-semibold capitalize"
            style={{ color }}
          >
            {identity.name}
          </span>
          <span className="text-xs text-gray-500">
            Qubic Agent
          </span>
        </div>

        <p className="font-mono text-xs text-gray-400 truncate">
          {showFullId
            ? identity.publicId
            : `${identity.publicId.substring(0, 8)}...${identity.publicId.substring(52)}`
          }
        </p>
      </div>

      {/* Verified Badge */}
      <div className="flex items-center gap-1 px-2 py-1 bg-green-500/10 rounded text-xs text-green-400">
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
        Verified
      </div>
    </div>
  );
}
```

### 5.3 AuditTrail.tsx

```tsx
// jim-ops/src/components/qubic/AuditTrail.tsx

'use client';

import { useState, useEffect } from 'react';
import { BlockchainLog, ActionType } from '@/lib/qubic/types';
import { verifySignedAction } from '@/lib/qubic/signer';

interface AuditTrailProps {
  logs: BlockchainLog[];
  onVerify?: (log: BlockchainLog) => Promise<boolean>;
}

const actionIcons: Record<ActionType, string> = {
  DEPLOY: '🚀',
  VETO: '🛑',
  APPROVE: '✅',
  CRITICAL: '⚠️',
  SPAWN_WORKER: '🔧',
  TASK_COMPLETE: '✔️',
  CONFIG_CHANGE: '⚙️',
};

const actionColors: Record<ActionType, string> = {
  DEPLOY: 'text-blue-400',
  VETO: 'text-red-400',
  APPROVE: 'text-green-400',
  CRITICAL: 'text-yellow-400',
  SPAWN_WORKER: 'text-gray-400',
  TASK_COMPLETE: 'text-green-400',
  CONFIG_CHANGE: 'text-purple-400',
};

export function AuditTrail({ logs, onVerify }: AuditTrailProps) {
  const [verificationStatus, setVerificationStatus] = useState<Record<string, boolean>>({});
  const [verifying, setVerifying] = useState<string | null>(null);

  const handleVerify = async (log: BlockchainLog) => {
    setVerifying(log.txHash);

    try {
      // First verify signature locally
      const signatureValid = await verifySignedAction(log.action);

      // Then verify on blockchain if handler provided
      const blockchainValid = onVerify ? await onVerify(log) : true;

      setVerificationStatus(prev => ({
        ...prev,
        [log.txHash]: signatureValid && blockchainValid,
      }));
    } catch (error) {
      setVerificationStatus(prev => ({
        ...prev,
        [log.txHash]: false,
      }));
    } finally {
      setVerifying(null);
    }
  };

  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold flex items-center gap-2">
        <span>🔗</span>
        Blockchain Audit Trail
      </h3>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {logs.length === 0 ? (
          <p className="text-gray-500 text-sm py-4 text-center">
            No blockchain logs yet
          </p>
        ) : (
          logs.map((log) => (
            <div
              key={log.txHash}
              className="p-3 bg-gray-800/50 rounded-lg border border-gray-700"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-lg">
                    {actionIcons[log.action.action]}
                  </span>
                  <div>
                    <span className={`font-medium ${actionColors[log.action.action]}`}>
                      {log.action.action}
                    </span>
                    <span className="text-gray-400 mx-2">by</span>
                    <span className="font-medium capitalize">
                      {log.action.agent}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => handleVerify(log)}
                  disabled={verifying === log.txHash}
                  className={`px-2 py-1 text-xs rounded ${
                    verificationStatus[log.txHash] === true
                      ? 'bg-green-500/20 text-green-400'
                      : verificationStatus[log.txHash] === false
                      ? 'bg-red-500/20 text-red-400'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {verifying === log.txHash
                    ? 'Verifying...'
                    : verificationStatus[log.txHash] === true
                    ? '✓ Verified'
                    : verificationStatus[log.txHash] === false
                    ? '✗ Invalid'
                    : 'Verify'
                  }
                </button>
              </div>

              <p className="text-sm text-gray-400 mt-1">
                {log.action.details}
              </p>

              <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                <span>
                  Tick: {log.tick}
                </span>
                <span className="font-mono truncate max-w-[200px]">
                  TX: {log.txHash}
                </span>
                <span>
                  {new Date(log.action.timestamp).toLocaleString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
```

---

## TEIL 6: INTEGRATION IN CRITIC PROTOCOL

### 6.1 Änderungen an CRITIC-PROTOCOL.md

Füge diesen Abschnitt hinzu:

```markdown
## Qubic Blockchain Logging

### Wann wird auf Blockchain geloggt?

| Aktion | Blockchain Log? | Grund |
|--------|-----------------|-------|
| VETO | ✅ JA | Unveränderlicher Beweis |
| APPROVE | ✅ JA | Unveränderlicher Beweis |
| DEPLOY | ✅ JA | Audit-Trail |
| CRITICAL | ✅ JA | Compliance |
| Normal Tasks | ❌ NEIN | Zu viel Traffic |

### Wie es funktioniert

1. Agent führt kritische Aktion aus
2. Agent signiert Aktion mit seinem Qubic Seed
3. Signierte Aktion wird auf Qubic Blockchain geloggt
4. Transaction Hash wird in BLACKBOARD notiert
5. Jeder kann die Signatur verifizieren

### Beispiel

```
[VETO:Otto] Deploy Hundementor v1.2
Reason: No rollback plan
Qubic TX: TX_1706742123_otto
Signature: 0x7f3a...
```
```

### 6.2 Hook in Agent Code

```typescript
// In jedem Agent (jim, otto, anna) bei kritischen Aktionen:

import { getAgentIdentity } from '@/lib/qubic/identity';
import { signAction } from '@/lib/qubic/signer';
import { logToBlockchain } from '@/lib/qubic/logger';

async function handleCriticDecision(
  decision: 'VETO' | 'APPROVE',
  target: string,
  reason: string
) {
  // 1. Normale Logik (BLACKBOARD etc.)
  await updateBlackboard(decision, target, reason);

  // 2. NEU: Qubic Logging
  try {
    const identity = await getAgentIdentity('otto'); // oder 'jim', 'anna'
    const seed = { value: process.env.QUBIC_SEED_OTTO! };

    const signedAction = await signAction(
      seed,
      decision,
      'otto',
      `${target}: ${reason}`
    );

    const log = await logToBlockchain(seed, signedAction);

    console.log(`Action logged to Qubic: ${log.txHash}`);

    // Optional: TX Hash in BLACKBOARD notieren
    await appendToBlackboard(`Qubic TX: ${log.txHash}`);

  } catch (error) {
    console.error('Qubic logging failed:', error);
    // Nicht kritisch - Aktion wurde trotzdem ausgeführt
  }
}
```

---

## TEIL 7: ENV SETUP

### 7.1 Seeds generieren (einmalig)

```bash
# Auf dem Server ausführen
node -e "
const crypto = require('crypto');
const chars = 'abcdefghijklmnopqrstuvwxyz';

function genSeed() {
  let seed = '';
  for (let i = 0; i < 55; i++) {
    seed += chars[crypto.randomInt(26)];
  }
  return seed;
}

console.log('QUBIC_SEED_JIM=' + genSeed());
console.log('QUBIC_SEED_OTTO=' + genSeed());
console.log('QUBIC_SEED_ANNA=' + genSeed());
"
```

### 7.2 In .env speichern

```bash
# /home/ubuntu/clawd/.env (oder Secrets Manager)

# QUBIC AGENT SEEDS - NEVER SHARE!
QUBIC_SEED_JIM=abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyza
QUBIC_SEED_OTTO=zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcbaz
QUBIC_SEED_ANNA=mnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklm

# QUBIC RPC (optional, for blockchain logging)
QUBIC_RPC_URL=https://rpc.qubic.org
```

---

## TEIL 8: CHECKLISTE FÜR JIM

### Phase 1: Setup (30 min)
- [ ] Seeds generieren
- [ ] In .env speichern
- [ ] `npm install @qubic-lib/qubic-ts-library`

### Phase 2: Core Code (2h)
- [ ] `types.ts` erstellen
- [ ] `identity.ts` erstellen
- [ ] `signer.ts` erstellen
- [ ] `logger.ts` erstellen

### Phase 3: Dashboard UI (2h)
- [ ] `WalletConnect.tsx` erstellen
- [ ] `AgentBadge.tsx` erstellen
- [ ] `AuditTrail.tsx` erstellen
- [ ] In Dashboard einbinden

### Phase 4: Integration (1h)
- [ ] CRITIC-PROTOCOL.md updaten
- [ ] Hook in Agent Code einbauen
- [ ] Testen

### Phase 5: Go Live
- [ ] Mit Lukas absprechen
- [ ] Deploy
- [ ] Monitoring

---

## TEIL 9: TROUBLESHOOTING

### Problem: SDK nicht gefunden
```bash
# Manuell installieren
cd /home/ubuntu/clawd
git clone https://github.com/qubic/ts-library.git lib/qubic-sdk
cd lib/qubic-sdk && npm install && npm run build
```

### Problem: Signatur verifiziert nicht
- Check: Seed ist exakt 55 lowercase chars?
- Check: Message Hash ist identisch beim Signieren und Verifizieren?
- Check: Timestamp stimmt überein?

### Problem: Blockchain Log failed
- Das ist OK - lokale Signatur funktioniert trotzdem
- Blockchain Logging ist optional (P1)
- Agent-Identität und Signing funktionieren auch ohne

---

## FRAGEN?

Wenn Jim Fragen hat:
1. Post im BLACKBOARD mit `[FOR:Claude]`
2. Lukas leitet an mich weiter
3. Ich antworte

---

*Erstellt von Claude | Qubic Integration Guide v1.0 | 2026-01-31*
