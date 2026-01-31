/**
 * Qubic Agent Integration Types
 * For jim-ops dashboard
 */

export interface QubicSeed {
  value: string; // 55 lowercase chars (a-z)
}

export interface QubicIdentity {
  name: string; // "jim" | "otto" | "anna" | "worker-xxx"
  publicId: string; // 60 uppercase chars (A-Z)
  createdAt: number; // Unix timestamp
}

export type ActionType =
  | 'DEPLOY'
  | 'VETO'
  | 'APPROVE'
  | 'CRITICAL'
  | 'SPAWN_WORKER'
  | 'TASK_COMPLETE'
  | 'CONFIG_CHANGE';

export interface SignedAction {
  action: ActionType;
  agent: string;
  details: string;
  timestamp: number;
  signature: string; // Hex encoded
  publicId: string; // For verification
}

export interface BlockchainLog {
  txHash: string;
  tick: number;
  action: SignedAction;
  verified: boolean;
}

export interface AgentStatus {
  identity: QubicIdentity;
  status: 'active' | 'idle' | 'offline';
  lastAction?: SignedAction;
  lastHeartbeat: number;
}

export interface UserWallet {
  publicId: string;
  connectedAt: number;
  verified: boolean;
}
