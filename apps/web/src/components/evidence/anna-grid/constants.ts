import type { ViewMode, ColorTheme, CameraPreset, SpecialRowType } from './types'

// =============================================================================
// MATRIX DIMENSIONS
// =============================================================================

export const MATRIX_SIZE = 128
export const TOTAL_CELLS = MATRIX_SIZE * MATRIX_SIZE // 16,384
export const VALUE_MIN = -128
export const VALUE_MAX = 127

// =============================================================================
// DATA URLS
// =============================================================================

export const DATA_URLS = {
  matrix: '/data/anna-matrix.json',
  interesting: '/data/interesting-addresses.json',
} as const

// =============================================================================
// SPECIAL ADDRESSES
// =============================================================================

export const SPECIAL_ADDRESSES = {
  boot: {
    address: 2692,
    row: 21,
    col: 4,
    name: 'Boot Address',
    description: 'Execution begins here (625,284 % 16,384 = 2,692)',
    formula: '625,284 mod 16,384',
  },
  pocz: {
    address: 12372,
    row: 96,
    col: 84,
    name: 'POCZ Address',
    description: 'Proof of Compute Zero - Final output',
  },
} as const

// =============================================================================
// SPECIAL ROWS
// =============================================================================

export const SPECIAL_ROWS: Record<number, {
  type: SpecialRowType
  name: string
  description: string
  color: string
  glowColor: string
  addressRange: [number, number]
}> = {
  21: {
    type: 'bitcoin-input',
    name: 'Bitcoin Input Layer',
    description: 'Receives Block #283 data from Bitcoin blockchain',
    color: '#F7931A',
    glowColor: 'rgba(247, 147, 26, 0.4)',
    addressRange: [2688, 2815],
  },
  68: {
    type: 'transformation',
    name: 'Transformation Bridge',
    description: 'Bitcoin → Qubic conversion (137 writes = α constant)',
    color: '#8B5CF6',
    glowColor: 'rgba(139, 92, 246, 0.4)',
    addressRange: [8704, 8831],
  },
  96: {
    type: 'output',
    name: 'Output Layer',
    description: 'Final computation output, contains POCZ address',
    color: '#22C55E',
    glowColor: 'rgba(34, 197, 94, 0.4)',
    addressRange: [12288, 12415],
  },
}

// =============================================================================
// COLOR THEMES
// =============================================================================

export const COLOR_THEMES: Record<ColorTheme, {
  name: string
  description: string
  negative: string
  neutral: string
  positive: string
  background: string
  grid: string
}> = {
  default: {
    name: 'Default',
    description: 'Blue to Orange gradient',
    negative: '#3B82F6',
    neutral: '#6B7280',
    positive: '#F59E0B',
    background: '#0A0A0A',
    grid: '#1F2937',
  },
  fire: {
    name: 'Fire',
    description: 'Deep blue to flame',
    negative: '#1E3A5F',
    neutral: '#DC2626',
    positive: '#FCD34D',
    background: '#0F0505',
    grid: '#3B1010',
  },
  ice: {
    name: 'Ice',
    description: 'Cold gradient',
    negative: '#1E40AF',
    neutral: '#06B6D4',
    positive: '#FFFFFF',
    background: '#050A14',
    grid: '#0E1B3D',
  },
  matrix: {
    name: 'Matrix',
    description: 'Classic green terminal',
    negative: '#000000',
    neutral: '#166534',
    positive: '#22C55E',
    background: '#000500',
    grid: '#0A1F0A',
  },
  scientific: {
    name: 'Scientific',
    description: 'High contrast for analysis',
    negative: '#7C3AED',
    neutral: '#FFFFFF',
    positive: '#EF4444',
    background: '#000000',
    grid: '#333333',
  },
}

// =============================================================================
// VIEW MODE CONFIG
// =============================================================================

export const VIEW_MODE_CONFIG: Record<ViewMode, {
  name: string
  description: string
  icon: string
  requires3D: boolean
}> = {
  heatmap: {
    name: 'Heatmap',
    description: 'Color-coded cell values',
    icon: 'Palette',
    requires3D: false,
  },
  terrain: {
    name: 'Terrain',
    description: '3D height map based on values',
    icon: 'Mountain',
    requires3D: true,
  },
  wireframe: {
    name: 'Wireframe',
    description: 'Structural mesh view',
    icon: 'Grid3X3',
    requires3D: true,
  },
  scientific: {
    name: 'Scientific',
    description: 'High contrast for analysis',
    icon: 'FlaskConical',
    requires3D: false,
  },
  flat: {
    name: 'Flat 2D',
    description: 'Fast 2D overview',
    icon: 'Square',
    requires3D: false,
  },
}

// =============================================================================
// CAMERA PRESETS
// =============================================================================

export const CAMERA_PRESETS: Record<string, CameraPreset> = {
  overview: {
    name: 'Overview',
    position: [0, 15, 15],
    target: [0, 0, 0],
  },
  top: {
    name: 'Top Down',
    position: [0, 20, 0],
    target: [0, 0, 0],
  },
  front: {
    name: 'Front',
    position: [0, 5, 15],
    target: [0, 0, 0],
  },
  row21: {
    name: 'Row 21',
    position: [0, 3, 8],
    target: [0, -1.5, 0], // Offset to focus on row 21
  },
  row68: {
    name: 'Row 68',
    position: [0, 3, 0],
    target: [0, 0.5, 0], // Center of matrix
  },
  row96: {
    name: 'Row 96',
    position: [0, 3, -8],
    target: [0, 1.5, 0], // Offset to focus on row 96
  },
  isometric: {
    name: 'Isometric',
    position: [12, 12, 12],
    target: [0, 0, 0],
  },
}

// =============================================================================
// VIP CELL COLORS
// =============================================================================

export const VIP_COLORS = {
  cfbVanity: {
    color: '#FF6B35',
    glow: 'rgba(255, 107, 53, 0.6)',
    label: 'CFB Vanity',
  },
  patoshiVanity: {
    color: '#9333EA',
    glow: 'rgba(147, 51, 234, 0.6)',
    label: 'Patoshi Vanity',
  },
  matrixDerived: {
    color: '#06B6D4',
    glow: 'rgba(6, 182, 212, 0.4)',
    label: 'Matrix Derived',
  },
}

// =============================================================================
// KEYBOARD SHORTCUTS
// =============================================================================

export const KEYBOARD_SHORTCUTS = [
  { key: 'W/A/S/D', action: 'Pan camera' },
  { key: 'Scroll', action: 'Zoom in/out' },
  { key: 'R', action: 'Reset camera' },
  { key: 'F', action: 'Toggle fullscreen' },
  { key: 'G', action: 'Toggle grid' },
  { key: 'V', action: 'Toggle VIP markers' },
  { key: '1-5', action: 'Switch view mode' },
  { key: 'Arrow Keys', action: 'Navigate cells' },
  { key: 'Enter', action: 'Select cell' },
  { key: 'Escape', action: 'Deselect / Close panel' },
  { key: '?', action: 'Show shortcuts' },
  { key: 'B', action: 'Jump to Boot address' },
  { key: 'P', action: 'Jump to POCZ address' },
] as const

// =============================================================================
// QUICK NAVIGATION PRESETS
// =============================================================================

export const QUICK_NAV_PRESETS = [
  {
    id: 'boot',
    label: 'Boot Address',
    address: 2692,
    row: 21,
    col: 4,
    color: '#FBBF24',
  },
  {
    id: 'pocz',
    label: 'POCZ Output',
    address: 12372,
    row: 96,
    col: 84,
    color: '#10B981',
  },
  {
    id: 'row21-start',
    label: 'Row 21 Start',
    address: 2688,
    row: 21,
    col: 0,
    color: '#F7931A',
  },
  {
    id: 'row68-start',
    label: 'Row 68 Start',
    address: 8704,
    row: 68,
    col: 0,
    color: '#8B5CF6',
  },
  {
    id: 'row96-start',
    label: 'Row 96 Start',
    address: 12288,
    row: 96,
    col: 0,
    color: '#22C55E',
  },
  {
    id: 'center',
    label: 'Matrix Center',
    address: 8256, // Row 64, Col 64
    row: 64,
    col: 64,
    color: '#6B7280',
  },
] as const

// =============================================================================
// STATISTICS LABELS
// =============================================================================

export const STAT_LABELS = {
  totalCells: 'Total Cells',
  uniqueValues: 'Unique Values',
  min: 'Minimum',
  max: 'Maximum',
  mean: 'Mean',
  median: 'Median',
  stdDev: 'Std Deviation',
  positiveCount: 'Positive (+)',
  negativeCount: 'Negative (-)',
  zeroCount: 'Zero (0)',
  vipCount: 'VIP Cells',
} as const

// =============================================================================
// FORMULA REFERENCES
// =============================================================================

export const FORMULA_REFERENCES = {
  coreFormula: {
    equation: '625,284 = 283 × 47² + 137',
    components: {
      block283: 'Bitcoin Block #283 (61st prime)',
      prime47: '47² = 2,209 (architectural constant)',
      alpha137: 'Fine structure constant α ≈ 1/137',
    },
  },
  bootDerivation: {
    equation: '625,284 mod 16,384 = 2,692',
    explanation: 'Maps universal constant to Anna Matrix boot address',
  },
  row68Operations: {
    reads: 192,
    writes: 137,
    ratio: 'Close to √2 (1.40)',
    significance: '137 writes matches α constant',
  },
} as const
