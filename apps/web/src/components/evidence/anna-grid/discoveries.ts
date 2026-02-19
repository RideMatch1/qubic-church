// =============================================================================
// ANNA MATRIX DISCOVERIES - All Easter Eggs and Patterns Found
// Analysis Date: January 26, 2026
// =============================================================================

export type DiscoveryCategory =
  | 'easter-egg'
  | 'mathematical'
  | 'symmetry'
  | 'word-encoding'
  | 'bitcoin-connection'
  | 'balance'
  | 'special-value'

export interface Discovery {
  id: string
  name: string
  category: DiscoveryCategory
  description: string
  formula?: string
  significance: string
  positions?: Array<{ row: number; col: number; label?: string }>
  rowPairs?: Array<{ row1: number; row2: number; sum: number; meaning: string }>
  value?: number | string
  color: string
  glowColor: string
  icon: string
}

// =============================================================================
// TOP 20 DISCOVERIES
// =============================================================================

export const DISCOVERIES: Discovery[] = [
  // 1. THE = 33
  {
    id: 'the-33',
    name: '"THE" = 33',
    category: 'word-encoding',
    description: 'The first word of the Genesis Block message encodes 33',
    formula: 'T(19) + H(7) + E(4) diagonal sum = 33',
    significance: '33 = Days from Blood Moon (03.03.2026) to Easter (05.04.2026)',
    positions: [
      { row: 19, col: 19, label: 'T = -113' },
      { row: 7, col: 7, label: 'H = 26' },
      { row: 4, col: 4, label: 'E = 120' },
    ],
    value: 33,
    color: '#FFD700',
    glowColor: 'rgba(255, 215, 0, 0.6)',
    icon: 'MessageCircle',
  },

  // 2. Key at Diagonal 66
  {
    id: 'key-diagonal-66',
    name: '"Key" at Diagonal 66',
    category: 'easter-egg',
    description: 'The word "Key" is spelled at diagonal offset 66',
    formula: '8 × 74 + 84 = 676 (Computors!)',
    significance: 'The formula reveals 676 = number of Qubic Computors',
    positions: [
      { row: 8, col: 74, label: 'K = -75' },
      { row: 9, col: 75, label: 'e = 101' },
      { row: 10, col: 76, label: 'y = -121' },
    ],
    color: '#FF6B35',
    glowColor: 'rgba(255, 107, 53, 0.6)',
    icon: 'Key',
  },

  // 3. Answer to Everything
  {
    id: 'answer-42',
    name: 'Matrix[99,99] = 42',
    category: 'easter-egg',
    description: 'The Answer to Life, the Universe, and Everything',
    formula: '99 = 100 - 1 = 9 × 11',
    significance: 'Douglas Adams reference at position (99, 99)',
    positions: [{ row: 99, col: 99, label: '42' }],
    value: 42,
    color: '#9333EA',
    glowColor: 'rgba(147, 51, 234, 0.6)',
    icon: 'Sparkles',
  },

  // 4. ZZZ Magic Square
  {
    id: 'zzz-magic',
    name: 'ZZZ Magic Square',
    category: 'easter-egg',
    description: '3×3 magic square where every element = 90 = "Z"',
    formula: 'Magic sum = 270 = 10 × 27',
    significance: 'ZZZ = Sleep? End? The matrix contains hidden art',
    positions: [
      { row: 36, col: 36, label: 'Z' },
      { row: 36, col: 37, label: 'Z' },
      { row: 36, col: 38, label: 'Z' },
      { row: 37, col: 36, label: 'Z' },
      { row: 37, col: 37, label: 'Z' },
      { row: 37, col: 38, label: 'Z' },
      { row: 38, col: 36, label: 'Z' },
      { row: 38, col: 37, label: 'Z' },
      { row: 38, col: 38, label: 'Z' },
    ],
    color: '#22C55E',
    glowColor: 'rgba(34, 197, 94, 0.6)',
    icon: 'Grid3X3',
  },

  // 5. Fibonacci Sum = 1
  {
    id: 'fibonacci-unity',
    name: 'Fibonacci = 1',
    category: 'mathematical',
    description: 'Fibonacci diagonal positions sum to exactly 1',
    formula: 'Σ Matrix[fib, fib] = 1 (Unity!)',
    significance: 'The Fibonacci sequence encodes the number ONE',
    positions: [
      { row: 1, col: 1, label: '60' },
      { row: 2, col: 2, label: '-118' },
      { row: 3, col: 3, label: '-70' },
      { row: 5, col: 5, label: '120' },
      { row: 8, col: 8, label: '-28' },
      { row: 13, col: 13, label: '116' },
      { row: 21, col: 21, label: '28' },
      { row: 34, col: 34, label: '-102' },
      { row: 55, col: 55, label: '26' },
      { row: 89, col: 89, label: '-91' },
    ],
    value: 1,
    color: '#F59E0B',
    glowColor: 'rgba(245, 158, 11, 0.6)',
    icon: 'Infinity',
  },

  // 6. Prime Diagonal = 121
  {
    id: 'prime-121',
    name: 'Prime Diagonal = 121',
    category: 'mathematical',
    description: 'Sum of values at prime diagonal positions = 121 = 11²',
    formula: 'Σ Matrix[prime, prime] = 121 = 11 × 11',
    significance: 'Another perfect square emerges from primes',
    positions: [
      { row: 2, col: 2, label: '2' },
      { row: 3, col: 3, label: '3' },
      { row: 5, col: 5, label: '5' },
      { row: 7, col: 7, label: '7' },
      { row: 11, col: 11, label: '11' },
      { row: 13, col: 13, label: '13' },
    ],
    value: 121,
    color: '#3B82F6',
    glowColor: 'rgba(59, 130, 246, 0.6)',
    icon: 'Hash',
  },

  // 7. XOR Corners = 0
  {
    id: 'xor-corners',
    name: 'XOR(Corners) = 0',
    category: 'symmetry',
    description: 'The four corner values XOR to exactly zero',
    formula: '-68 XOR 91 XOR -92 XOR 67 = 0',
    significance: 'Perfect balance across the matrix extremes',
    positions: [
      { row: 0, col: 0, label: 'α-α = -68' },
      { row: 0, col: 127, label: 'α-ω = 91' },
      { row: 127, col: 0, label: 'ω-α = -92' },
      { row: 127, col: 127, label: 'ω-ω = 67' },
    ],
    value: 0,
    color: '#06B6D4',
    glowColor: 'rgba(6, 182, 212, 0.6)',
    icon: 'Minimize2',
  },

  // 8. Row 7 = Row 36
  {
    id: 'row-7-36',
    name: 'Row 7 = Row 36',
    category: 'balance',
    description: 'Only two rows sum to 7436 = 11 × 676',
    formula: '7436 = 11 × 676 (Computors × 11)',
    significance: 'These are the ONLY rows with 676-multiple sums',
    rowPairs: [{ row1: 7, row2: 36, sum: 7436, meaning: '11 × 676' }],
    value: 7436,
    color: '#EC4899',
    glowColor: 'rgba(236, 72, 153, 0.6)',
    icon: 'Equal',
  },

  // 9. Bitcoin 50 BTC
  {
    id: 'btc-50',
    name: '√676 + √576 = 50',
    category: 'bitcoin-connection',
    description: 'Square roots of key numbers equal Bitcoin block reward',
    formula: '√676 + √576 = 26 + 24 = 50 BTC',
    significance: 'The matrix encodes Bitcoins original block reward',
    value: 50,
    color: '#F7931A',
    glowColor: 'rgba(247, 147, 26, 0.6)',
    icon: 'Bitcoin',
  },

  // 10. Matrix[33,33] = 26
  {
    id: 'easter-26',
    name: 'Matrix[33,33] = 26',
    category: 'special-value',
    description: '33 days to Easter, value is 26 (alphabet)',
    formula: '33 = Days from Blood Moon to Easter',
    significance: 'The timing and the alphabet are encoded together',
    positions: [{ row: 33, col: 33, label: '26' }],
    value: 26,
    color: '#8B5CF6',
    glowColor: 'rgba(139, 92, 246, 0.6)',
    icon: 'Calendar',
  },

  // 11. Column Mirror Symmetry
  {
    id: 'col-mirror',
    name: 'Col[i] + Col[127-i] = -128',
    category: 'symmetry',
    description: '60 out of 64 column pairs sum to -128',
    formula: 'Mirror symmetry with matrix dimension offset',
    significance: 'The matrix structure encodes its own dimension',
    value: -128,
    color: '#10B981',
    glowColor: 'rgba(16, 185, 129, 0.6)',
    icon: 'FlipHorizontal',
  },

  // 12. Row 0 + Row 127 = -128
  {
    id: 'row-first-last',
    name: 'Row 0 + Row 127 = -128',
    category: 'symmetry',
    description: 'First and last row sum to negative matrix dimension',
    formula: '4721 + (-4849) = -128',
    significance: 'Self-referential structure',
    rowPairs: [{ row1: 0, row2: 127, sum: -128, meaning: 'Matrix Dimension' }],
    value: -128,
    color: '#EF4444',
    glowColor: 'rgba(239, 68, 68, 0.6)',
    icon: 'ArrowDownUp',
  },

  // 13. Zero Balance Rows
  {
    id: 'zero-balance',
    name: 'Zero Balance Rows',
    category: 'balance',
    description: 'Specific row pairs sum to exactly zero',
    formula: 'Row 51 + Row 76 = 0, Row 73 + Row 102 = 0',
    significance: 'Perfect mathematical balance',
    rowPairs: [
      { row1: 51, row2: 76, sum: 0, meaning: 'Zero' },
      { row1: 73, row2: 102, sum: 0, meaning: 'Zero' },
    ],
    value: 0,
    color: '#6B7280',
    glowColor: 'rgba(107, 114, 128, 0.6)',
    icon: 'Scale',
  },

  // 14. Message 576 Rows
  {
    id: 'message-576',
    name: 'Message 576 Rows',
    category: 'special-value',
    description: 'Row pairs that sum to ±576',
    formula: 'Row 50 + Row 69 = +576, Row 21 + Row 56 = -576',
    significance: '576 = 24² = Message 576 encoded',
    rowPairs: [
      { row1: 50, row2: 69, sum: 576, meaning: 'Message 576' },
      { row1: 21, row2: 56, sum: -576, meaning: 'Neg Message' },
    ],
    value: 576,
    color: '#FBBF24',
    glowColor: 'rgba(251, 191, 36, 0.6)',
    icon: 'Mail',
  },

  // 15. Value 0 appears 26 times
  {
    id: 'zero-26-times',
    name: 'Zero × 26',
    category: 'special-value',
    description: 'The value 0 appears exactly 26 times',
    significance: '26 = Alphabet letters = √676',
    value: '0 × 26',
    color: '#14B8A6',
    glowColor: 'rgba(20, 184, 166, 0.6)',
    icon: 'Circle',
  },

  // 16. Value 90 appears 256 times
  {
    id: 'z-256-times',
    name: '"Z" × 256',
    category: 'special-value',
    description: 'Value 90 (Z) appears exactly 256 = 2^8 times',
    significance: 'Binary perfection: one byte of Zs',
    value: '90 × 256',
    color: '#A855F7',
    glowColor: 'rgba(168, 85, 247, 0.6)',
    icon: 'Binary',
  },

  // 17. BEDATZFAUR XOR EASTEREGG
  {
    id: 'hexvridgst',
    name: 'HEXVRIDGST',
    category: 'easter-egg',
    description: 'BEDATZFAUR XOR EASTEREGG = HEXVRIDGST',
    formula: 'HEX + DGST = Hex Digest hint',
    significance: 'Hints at how the key is encoded',
    positions: [
      { row: 36, col: 23, label: 'B' },
      { row: 36, col: 24, label: 'E' },
      { row: 36, col: 25, label: 'D' },
      { row: 36, col: 26, label: 'A' },
      { row: 36, col: 27, label: 'T' },
      { row: 36, col: 28, label: 'Z' },
      { row: 36, col: 29, label: 'F' },
      { row: 36, col: 30, label: 'A' },
      { row: 36, col: 31, label: 'U' },
      { row: 36, col: 32, label: 'R' },
    ],
    color: '#DC2626',
    glowColor: 'rgba(220, 38, 38, 0.6)',
    icon: 'Code',
  },

  // 18. 21M mod 676 = 60
  {
    id: 'btc-21m',
    name: '21M mod 676 = 60',
    category: 'bitcoin-connection',
    description: 'Bitcoin max supply mod Computors = Qubic address length',
    formula: '21,000,000 mod 676 = 60 = Matrix[21,0]',
    significance: 'Bitcoin supply encodes Qubic address length',
    positions: [{ row: 21, col: 0, label: '60' }],
    value: 60,
    color: '#F97316',
    glowColor: 'rgba(249, 115, 22, 0.6)',
    icon: 'Coins',
  },

  // 19. Rotational Antisymmetry
  {
    id: 'rot180-zero',
    name: 'Matrix - Rot180 = 0',
    category: 'symmetry',
    description: 'Matrix minus itself rotated 180° equals zero',
    significance: 'Perfect rotational antisymmetry',
    value: 0,
    color: '#0EA5E9',
    glowColor: 'rgba(14, 165, 233, 0.6)',
    icon: 'RotateCcw',
  },

  // 20. Value Pairs Symmetry
  {
    id: 'value-pairs',
    name: 'Value Pair Symmetry',
    category: 'symmetry',
    description: 'For value n, -(n+1) appears with similar frequency',
    formula: '26/-27: 476×, 90/-91: 256×, 120/-121: 278×',
    significance: 'Antisymmetric value distribution',
    color: '#84CC16',
    glowColor: 'rgba(132, 204, 22, 0.6)',
    icon: 'GitBranch',
  },
]

// =============================================================================
// SPECIAL POSITIONS FOR QUICK NAVIGATION
// =============================================================================

export const DISCOVERY_PRESETS = [
  { id: 'key', label: '"Key" Start', row: 8, col: 74, color: '#FF6B35' },
  { id: 'answer', label: '42 (Answer)', row: 99, col: 99, color: '#9333EA' },
  { id: 'zzz', label: 'ZZZ Magic', row: 36, col: 36, color: '#22C55E' },
  { id: 'easter', label: '33 Days', row: 33, col: 33, color: '#8B5CF6' },
  { id: 'the-t', label: '"THE" T', row: 19, col: 19, color: '#FFD700' },
  { id: 'the-h', label: '"THE" H', row: 7, col: 7, color: '#FFD700' },
  { id: 'the-e', label: '"THE" E', row: 4, col: 4, color: '#FFD700' },
  { id: 'corner-aa', label: 'Corner α-α', row: 0, col: 0, color: '#06B6D4' },
  { id: 'corner-oo', label: 'Corner ω-ω', row: 127, col: 127, color: '#06B6D4' },
  { id: 'bedatz', label: 'BEDATZFAUR', row: 36, col: 23, color: '#DC2626' },
  { id: 'fib-55', label: 'Fib 55', row: 55, col: 55, color: '#F59E0B' },
  { id: 'prime-7', label: 'Prime 7', row: 7, col: 7, color: '#3B82F6' },
]

// =============================================================================
// CAMERA PRESETS FOR DISCOVERIES
// =============================================================================

export const DISCOVERY_CAMERA_PRESETS = {
  key: {
    name: '"Key" Position',
    position: [2, 5, 2] as [number, number, number],
    target: [0.8, 0, -1.2] as [number, number, number],
  },
  answer42: {
    name: 'Answer 42',
    position: [-1, 5, -3] as [number, number, number],
    target: [-1, 0, -2.5] as [number, number, number],
  },
  zzzMagic: {
    name: 'ZZZ Magic Square',
    position: [0.5, 4, 1] as [number, number, number],
    target: [0.5, 0, 0.5] as [number, number, number],
  },
  corners: {
    name: 'Four Corners',
    position: [0, 20, 0] as [number, number, number],
    target: [0, 0, 0] as [number, number, number],
  },
  fibonacci: {
    name: 'Fibonacci Line',
    position: [5, 8, 5] as [number, number, number],
    target: [0, 0, 0] as [number, number, number],
  },
}

// =============================================================================
// KEYBOARD SHORTCUTS FOR DISCOVERIES
// =============================================================================

export const DISCOVERY_SHORTCUTS = [
  { key: 'K', action: 'Jump to "Key" position' },
  { key: '4', action: 'Jump to Answer 42' },
  { key: 'Z', action: 'Jump to ZZZ Magic Square' },
  { key: 'T', action: 'Jump to "THE" (T position)' },
  { key: 'E', action: 'Toggle Easter Eggs overlay' },
  { key: 'M', action: 'Toggle Mathematical patterns' },
  { key: 'Y', action: 'Toggle Symmetry lines' },
]

// =============================================================================
// PATTERN LINES FOR VISUALIZATION
// =============================================================================

export interface PatternLine {
  id: string
  name: string
  points: Array<{ row: number; col: number }>
  color: string
  type: 'diagonal' | 'horizontal' | 'vertical' | 'custom'
}

export const PATTERN_LINES: PatternLine[] = [
  {
    id: 'key-line',
    name: '"Key" Diagonal',
    points: [
      { row: 8, col: 74 },
      { row: 9, col: 75 },
      { row: 10, col: 76 },
    ],
    color: '#FF6B35',
    type: 'diagonal',
  },
  {
    id: 'fibonacci-line',
    name: 'Fibonacci Diagonal',
    points: [
      { row: 1, col: 1 },
      { row: 2, col: 2 },
      { row: 3, col: 3 },
      { row: 5, col: 5 },
      { row: 8, col: 8 },
      { row: 13, col: 13 },
      { row: 21, col: 21 },
      { row: 34, col: 34 },
      { row: 55, col: 55 },
      { row: 89, col: 89 },
    ],
    color: '#F59E0B',
    type: 'diagonal',
  },
  {
    id: 'the-line',
    name: '"THE" Positions',
    points: [
      { row: 19, col: 19 },
      { row: 7, col: 7 },
      { row: 4, col: 4 },
    ],
    color: '#FFD700',
    type: 'diagonal',
  },
  {
    id: 'row-7',
    name: 'Row 7 (= Row 36)',
    points: Array.from({ length: 128 }, (_, i) => ({ row: 7, col: i })),
    color: '#EC4899',
    type: 'horizontal',
  },
  {
    id: 'row-36',
    name: 'Row 36 (= Row 7)',
    points: Array.from({ length: 128 }, (_, i) => ({ row: 36, col: i })),
    color: '#EC4899',
    type: 'horizontal',
  },
]

// =============================================================================
// ROW STATISTICS FOR VISUALIZATION
// =============================================================================

export const SPECIAL_ROW_SUMS: Record<
  number,
  { sum: number; meaning: string; color: string }
> = {
  7: { sum: 7436, meaning: '11 × 676', color: '#EC4899' },
  36: { sum: 7436, meaning: '11 × 676', color: '#EC4899' },
  51: { sum: -1377, meaning: 'Zero pair with 76', color: '#6B7280' },
  76: { sum: 1377, meaning: 'Zero pair with 51', color: '#6B7280' },
  73: { sum: 429, meaning: 'Zero pair with 102', color: '#6B7280' },
  102: { sum: -429, meaning: 'Zero pair with 73', color: '#6B7280' },
  50: { sum: -7244, meaning: '576 pair with 69', color: '#FBBF24' },
  69: { sum: 7820, meaning: '576 pair with 50', color: '#FBBF24' },
  21: { sum: 7358, meaning: '-576 pair with 56', color: '#F7931A' },
  56: { sum: -7934, meaning: '-576 pair with 21', color: '#F7931A' },
}

// =============================================================================
// VALUE FREQUENCIES
// =============================================================================

export const SPECIAL_VALUE_FREQUENCIES = [
  { value: 26, count: 476, meaning: 'Alphabet signature' },
  { value: -27, count: 476, meaning: 'Antisymmetric pair' },
  { value: 90, count: 256, meaning: '"Z" = 2^8 times' },
  { value: -91, count: 256, meaning: 'Antisymmetric pair' },
  { value: 0, count: 26, meaning: 'Zeros = Alphabet' },
  { value: -1, count: 26, meaning: 'Near-zeros = Alphabet' },
  { value: 42, count: 48, meaning: 'Answer appearances' },
]

// =============================================================================
// TIMELINE DATA
// =============================================================================

export const TIMELINE = {
  today: '2026-01-26',
  bloodMoon: '2026-03-03',
  easter: '2026-04-05',
  daysToBloodMoon: 36,
  daysBloodMoonToEaster: 33,
  totalDays: 69,
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

export function getDiscoveryById(id: string): Discovery | undefined {
  return DISCOVERIES.find((d) => d.id === id)
}

export function getDiscoveriesByCategory(category: DiscoveryCategory): Discovery[] {
  return DISCOVERIES.filter((d) => d.category === category)
}

export function getDiscoveryAtPosition(
  row: number,
  col: number
): Discovery | undefined {
  return DISCOVERIES.find((d) =>
    d.positions?.some((p) => p.row === row && p.col === col)
  )
}

export function isDiscoveryPosition(row: number, col: number): boolean {
  return DISCOVERIES.some((d) =>
    d.positions?.some((p) => p.row === row && p.col === col)
  )
}

export function getPositionLabel(row: number, col: number): string | undefined {
  for (const discovery of DISCOVERIES) {
    const pos = discovery.positions?.find((p) => p.row === row && p.col === col)
    if (pos?.label) return pos.label
  }
  return undefined
}
