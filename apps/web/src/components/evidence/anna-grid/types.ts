// =============================================================================
// ANNA GRID TYPES
// =============================================================================

export type ViewMode = 'heatmap' | 'terrain' | 'wireframe' | 'scientific' | 'flat'

export type ColorTheme = 'default' | 'fire' | 'ice' | 'matrix' | 'scientific'

export type SpecialRowType = 'bitcoin-input' | 'transformation' | 'output' | 'boot' | 'pocz'

// =============================================================================
// CELL TYPES
// =============================================================================

export interface AnnaCell {
  address: number        // 0-16383 (linear address)
  row: number            // 0-127
  col: number            // 0-127
  value: number          // -128 to 127

  // Computed properties
  hex: string            // "0x7F" etc
  binary: string         // "01111111"
  normalized: number     // 0-1 for visualization

  // Special classifications
  isSpecialRow: boolean
  specialRowType?: SpecialRowType
  specialRowName?: string

  // VIP status
  isVIP: boolean
  vipData?: VIPCellData
}

export interface VIPCellData {
  bitcoinAddress: string
  xorVariant: number
  method: string
  compressed: boolean
  hash160: string
}

export interface CellNeighbors {
  top?: number
  topRight?: number
  right?: number
  bottomRight?: number
  bottom?: number
  bottomLeft?: number
  left?: number
  topLeft?: number
}

// =============================================================================
// MATRIX DATA TYPES
// =============================================================================

export interface RawAnnaMatrix {
  matrix: number[][]
  dimensions: string
  note: string
}

export interface RawInterestingAddress {
  address: string
  position: [number, number]  // [row, col]
  xor: number
  method: string
  compressed: boolean
  hash160: string
}

export interface MatrixStats {
  totalCells: number
  min: number
  max: number
  mean: number
  median: number
  stdDev: number
  positiveCount: number
  negativeCount: number
  zeroCount: number
  uniqueValues: number

  // Row statistics
  specialRows: {
    row21: RowStats
    row68: RowStats
    row96: RowStats
  }

  // VIP stats
  vipCount: number
  vipPositions: Array<{ row: number; col: number; address: string }>
}

export interface RowStats {
  min: number
  max: number
  mean: number
  sum: number
  positiveCount: number
  negativeCount: number
}

// =============================================================================
// VISUALIZATION STATE
// =============================================================================

export interface AnnaGridState {
  viewMode: ViewMode
  colorTheme: ColorTheme
  showGrid: boolean
  showLabels: boolean
  showVIPMarkers: boolean
  showSpecialRows: boolean
  highlightValue: number | null
  zoomLevel: number
  panOffset: { x: number; y: number }
}

export interface CameraPreset {
  name: string
  position: [number, number, number]
  target: [number, number, number]
}

// =============================================================================
// HOOK RETURN TYPES
// =============================================================================

export interface UseAnnaGridDataReturn {
  loading: boolean
  progress: number
  error: AnnaGridError | null
  matrix: number[][] | null
  stats: MatrixStats | null
  vipCells: Map<string, VIPCellData>

  // Helpers
  getCell: (row: number, col: number) => AnnaCell | null
  getCellByAddress: (address: number) => AnnaCell | null
  getCellNeighbors: (row: number, col: number) => CellNeighbors
  searchByValue: (value: number) => AnnaCell[]
  searchByRange: (min: number, max: number) => AnnaCell[]

  // Actions
  retry: () => void
  retryCount: number
}

export type AnnaGridErrorType =
  | 'NETWORK_ERROR'
  | 'PARSE_ERROR'
  | 'VALIDATION_ERROR'
  | 'UNKNOWN_ERROR'

export interface AnnaGridError {
  type: AnnaGridErrorType
  message: string
  details?: string
  retryable: boolean
}

// =============================================================================
// COMPONENT PROPS
// =============================================================================

export interface AnnaGridSceneProps {
  onCellSelect?: (cell: AnnaCell) => void
  initialViewMode?: ViewMode
  initialColorTheme?: ColorTheme
}

export interface CellDetailPanelProps {
  cell: AnnaCell
  neighbors: CellNeighbors
  onClose: () => void
  onNavigate: (row: number, col: number) => void
}

export interface AnnaGridControlsProps {
  viewMode: ViewMode
  colorTheme: ColorTheme
  showVIPMarkers: boolean
  showSpecialRows: boolean
  stats: MatrixStats | null
  selectedCell: AnnaCell | null

  onViewModeChange: (mode: ViewMode) => void
  onColorThemeChange: (theme: ColorTheme) => void
  onToggleVIP: () => void
  onToggleSpecialRows: () => void
  onSearch: (query: string) => AnnaCell | null
  onCellFound: (cell: AnnaCell) => void
  onJumpToPreset: (preset: 'boot' | 'pocz' | 'row21' | 'row68' | 'row96') => void
  onExport: () => void
}

export interface StatsPanelProps {
  stats: MatrixStats
  selectedCell: AnnaCell | null
  isExpanded: boolean
  onToggle: () => void
}

// =============================================================================
// EXPORT TYPES
// =============================================================================

export interface ExportData {
  timestamp: string
  source: 'anna-matrix'
  dimensions: { rows: number; cols: number }
  selection?: {
    type: 'cell' | 'row' | 'region'
    data: AnnaCell | AnnaCell[]
  }
  stats: MatrixStats
  matrix?: number[][]
}
