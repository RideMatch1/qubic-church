// =============================================================================
// ADDRESS GRAPH - CONSTANTS & CONFIGURATION
// =============================================================================

import type { AddressType, DerivationMethod, EdgeType, AddressGraphErrorType } from './types'
import {
  WifiOff,
  FileWarning,
  AlertTriangle,
  Clock,
  HardDrive,
  Monitor,
} from 'lucide-react'

// -----------------------------------------------------------------------------
// COLOR PALETTE
// -----------------------------------------------------------------------------

export const COLORS = {
  // Node type colors
  patoshiGenesis: '#FFD700',  // Gold
  patoshi: '#F59E0B',         // Orange
  cfbVanity: '#8B5CF6',       // Purple
  patoshiVanity: '#EC4899',   // Pink
  matrixDerived: '#3B82F6',   // Blue
  seedValidated: '#10B981',   // Emerald
  seedMismatch: '#EF4444',    // Red
  unknown: '#6B7280',         // Gray

  // Derivation method colors
  step13: '#F59E0B',    // Gold
  diagonal: '#8B5CF6',  // Purple
  col: '#3B82F6',       // Blue
  row: '#EC4899',       // Pink
  step7: '#10B981',     // Emerald
  step27: '#06B6D4',    // Cyan

  // Edge colors
  transaction: '#FFFFFF',
  sameSeed: '#F59E0B',
  matrixAdjacent: '#3B82F6',
  temporal: '#8B5CF6',
  derivation: '#10B981',

  // UI colors
  background: '#000000',
  surface: '#18181B',
  border: '#27272A',
  text: '#FAFAFA',
  textMuted: '#A1A1AA',
} as const

// -----------------------------------------------------------------------------
// NODE TYPE CONFIGURATION
// -----------------------------------------------------------------------------

export const NODE_TYPE_CONFIG: Record<AddressType, {
  color: string
  shape: 'sphere' | 'cube' | 'octahedron' | 'dodecahedron'
  size: 'xs' | 'small' | 'medium' | 'large' | 'xl'
  glow: number
  label: string
}> = {
  'patoshi-genesis': {
    color: COLORS.patoshiGenesis,
    shape: 'dodecahedron',
    size: 'xl',
    glow: 1,
    label: 'Genesis Block',
  },
  'patoshi': {
    color: COLORS.patoshi,
    shape: 'sphere',
    size: 'large',
    glow: 0.5,
    label: 'Patoshi Era',
  },
  'cfb-vanity': {
    color: COLORS.cfbVanity,
    shape: 'octahedron',
    size: 'large',
    glow: 0.8,
    label: 'CFB Vanity (1CFB)',
  },
  'patoshi-vanity': {
    color: COLORS.patoshiVanity,
    shape: 'octahedron',
    size: 'large',
    glow: 0.8,
    label: 'Patoshi Vanity (1Pat)',
  },
  'matrix-derived': {
    color: COLORS.matrixDerived,
    shape: 'cube',
    size: 'medium',
    glow: 0.3,
    label: 'Matrix-Derived',
  },
  'seed-validated': {
    color: COLORS.seedValidated,
    shape: 'sphere',
    size: 'medium',
    glow: 0.6,
    label: 'Seed Validated',
  },
  'seed-mismatch': {
    color: COLORS.seedMismatch,
    shape: 'sphere',
    size: 'medium',
    glow: 0.8,
    label: 'Seed Mismatch',
  },
  'unknown': {
    color: COLORS.unknown,
    shape: 'sphere',
    size: 'xs',
    glow: 0,
    label: 'Unknown',
  },
}

// -----------------------------------------------------------------------------
// DERIVATION METHOD CONFIGURATION
// -----------------------------------------------------------------------------

export const METHOD_CONFIG: Record<DerivationMethod, {
  color: string
  rings: number
  label: string
}> = {
  'step13': { color: COLORS.step13, rings: 1, label: '13-Step Pattern' },
  'diagonal': { color: COLORS.diagonal, rings: 2, label: 'Diagonal Traversal' },
  'col': { color: COLORS.col, rings: 0, label: 'Column-Based' },
  'row': { color: COLORS.row, rings: 0, label: 'Row-Based' },
  'step7': { color: COLORS.step7, rings: 1, label: '7-Step Pattern' },
  'step27': { color: COLORS.step27, rings: 3, label: '27-Step Pattern' },
}

// -----------------------------------------------------------------------------
// XOR RING CONFIGURATION
// -----------------------------------------------------------------------------

export const XOR_RING_CONFIG: Record<number, {
  rings: number
  color: string
  label: string
}> = {
  0: { rings: 0, color: '#FFFFFF', label: 'No XOR' },
  7: { rings: 1, color: '#F59E0B', label: 'XOR 7' },
  13: { rings: 2, color: '#8B5CF6', label: 'XOR 13' },
  27: { rings: 3, color: '#3B82F6', label: 'XOR 27' },
  33: { rings: 4, color: '#EC4899', label: 'XOR 33' },
}

// -----------------------------------------------------------------------------
// EDGE TYPE CONFIGURATION
// -----------------------------------------------------------------------------

export const EDGE_TYPE_CONFIG: Record<EdgeType, {
  color: string
  style: 'solid' | 'dashed' | 'dotted'
  animated: boolean
  label: string
}> = {
  'transaction': {
    color: COLORS.transaction,
    style: 'solid',
    animated: false,
    label: 'On-chain Transaction',
  },
  'same-seed': {
    color: COLORS.sameSeed,
    style: 'dashed',
    animated: true,
    label: 'Same Qubic Seed',
  },
  'matrix-adjacent': {
    color: COLORS.matrixAdjacent,
    style: 'dotted',
    animated: true,
    label: 'Matrix Position',
  },
  'temporal': {
    color: COLORS.temporal,
    style: 'solid',
    animated: true,
    label: 'Same Block Range',
  },
  'derivation': {
    color: COLORS.derivation,
    style: 'solid',
    animated: false,
    label: 'Derivation Path',
  },
}

// -----------------------------------------------------------------------------
// ERROR CONFIGURATION
// -----------------------------------------------------------------------------

export const ERROR_CONFIG: Record<AddressGraphErrorType, {
  icon: typeof WifiOff
  color: string
  bgColor: string
  retryable: boolean
  message: string
}> = {
  NETWORK_ERROR: {
    icon: WifiOff,
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/10',
    retryable: true,
    message: 'Network Connection Failed',
  },
  PARSE_ERROR: {
    icon: FileWarning,
    color: 'text-red-400',
    bgColor: 'bg-red-500/10',
    retryable: false,
    message: 'Data Format Error',
  },
  VALIDATION_ERROR: {
    icon: AlertTriangle,
    color: 'text-red-400',
    bgColor: 'bg-red-500/10',
    retryable: false,
    message: 'Data Validation Failed',
  },
  TIMEOUT_ERROR: {
    icon: Clock,
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/10',
    retryable: true,
    message: 'Request Timed Out',
  },
  MEMORY_ERROR: {
    icon: HardDrive,
    color: 'text-red-400',
    bgColor: 'bg-red-500/10',
    retryable: false,
    message: 'Memory Limit Exceeded',
  },
  WEBGL_ERROR: {
    icon: Monitor,
    color: 'text-red-400',
    bgColor: 'bg-red-500/10',
    retryable: false,
    message: 'WebGL Not Supported',
  },
  UNKNOWN_ERROR: {
    icon: AlertTriangle,
    color: 'text-gray-400',
    bgColor: 'bg-gray-500/10',
    retryable: true,
    message: 'An Error Occurred',
  },
}

// -----------------------------------------------------------------------------
// CAMERA PRESETS
// -----------------------------------------------------------------------------

export const CAMERA_PRESETS = {
  overview: {
    position: [0, 50, 50] as [number, number, number],
    target: [0, 0, 0] as [number, number, number],
    name: 'Overview',
  },
  patoshi: {
    position: [30, 20, 10] as [number, number, number],
    target: [20, 0, 0] as [number, number, number],
    name: 'Patoshi Cluster',
  },
  cfb: {
    position: [-30, 20, 10] as [number, number, number],
    target: [-20, 0, 0] as [number, number, number],
    name: 'CFB Cluster',
  },
  genesis: {
    position: [0, 5, 15] as [number, number, number],
    target: [0, 0, 0] as [number, number, number],
    name: 'Genesis Focus',
  },
  timeline: {
    position: [0, 30, 80] as [number, number, number],
    target: [0, 0, 40] as [number, number, number],
    name: 'Timeline View',
  },
}

// -----------------------------------------------------------------------------
// PLAYBACK SPEEDS
// -----------------------------------------------------------------------------

export const SPEED_OPTIONS = [0.25, 0.5, 1, 1.5, 2, 3, 5] as const

// -----------------------------------------------------------------------------
// KEYBOARD SHORTCUTS
// -----------------------------------------------------------------------------

export const KEYBOARD_SHORTCUTS = [
  {
    category: 'Playback',
    items: [
      { key: 'Space', action: 'Play / Pause timeline' },
      { key: '←', action: 'Previous block' },
      { key: '→', action: 'Next block' },
      { key: 'Home', action: 'Genesis block (0)' },
      { key: 'End', action: 'Latest block' },
      { key: '[ / ]', action: 'Decrease / Increase speed' },
    ],
  },
  {
    category: 'Navigation',
    items: [
      { key: 'R', action: 'Reset camera' },
      { key: 'C', action: 'Center on selected' },
      { key: 'F', action: 'Fly to node' },
      { key: '1-5', action: 'Camera presets' },
    ],
  },
  {
    category: 'Visibility',
    items: [
      { key: 'E', action: 'Toggle edges' },
      { key: 'P', action: 'Toggle Patoshi nodes' },
      { key: 'M', action: 'Toggle Matrix nodes' },
      { key: 'V', action: 'Toggle validated only' },
    ],
  },
  {
    category: 'Interface',
    items: [
      { key: 'F11', action: 'Toggle fullscreen' },
      { key: 'I', action: 'Toggle info panel' },
      { key: '/', action: 'Focus search' },
      { key: 'S', action: 'Screenshot' },
      { key: '?', action: 'Show shortcuts' },
      { key: 'Esc', action: 'Close / Deselect' },
    ],
  },
]

// -----------------------------------------------------------------------------
// PERFORMANCE LIMITS
// -----------------------------------------------------------------------------

export const PERFORMANCE = {
  MAX_VISIBLE_NODES: 35000, // Increased for full dataset
  MAX_VISIBLE_EDGES: 50000,
  LOD_DISTANCE: 100,
  CHUNK_SIZE: 1000,
  SIMULATION_ITERATIONS: 300,
  TARGET_FPS: 60,
} as const

// -----------------------------------------------------------------------------
// DATA URLS
// -----------------------------------------------------------------------------

export const DATA_URLS = {
  summary: '/data/summary.json',
  patoshi: '/data/patoshi-addresses.json',
  interesting: '/data/interesting-addresses.json',
  derived: '/data/bitcoin-derived-addresses.json',
  privateKeys: '/data/bitcoin-private-keys.json',
  qubicSeeds: '/data/qubic-seeds.json',
  matrix: '/data/matrix-addresses.json',
  annaMatrix: '/data/anna-matrix.json',
} as const
