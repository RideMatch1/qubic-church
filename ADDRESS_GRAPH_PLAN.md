# Address Graph - Ultra Premium Visualization Plan v2.0

## Vision Statement
Create a **$10 Billion Research Lab Grade** 3D Address Network Graph that visualizes Bitcoin-Qubic address relationships with the same institutional quality as Neuraxon and Matrix Terrain. This is not just a visualization - it's a **forensic analysis instrument**.

---

## CRITICAL: 10 QUICK WINS I ORIGINALLY MISSED

### QW1: PATOSHI BLOCK HEIGHT POSITIONING
**Source:** `patoshi-addresses.json` has `blockHeight` field (21,953 records)
```typescript
// Use blockHeight for Z-axis positioning = temporal 3D space
interface PatoshiAddress {
  blockHeight: number      // 3, 4, 5, ... 36,000+
  outputIndex: number
  pubkey: string           // 130-char uncompressed pubkey
  amount: number           // Always 50.0 BTC
  scriptType: 'p2pk'       // All Patoshi are P2PK
}
// Z-position = blockHeight / 1000 (normalized)
```

### QW2: INTERESTING ADDRESSES VIP LAYER
**Source:** `interesting-addresses.json` (30 special addresses)
- `1CFB...` addresses - CFB vanity addresses
- `1Pat...` addresses - Patoshi pattern addresses
- Each has matrix position, derivation method, XOR value
```typescript
interface InterestingAddress {
  address: string          // "1CFBtCo6zDgmXAD9NJTZ7dw7Yvoq6ZPGGQ"
  position: [number, number] // [96, 17] - Anna Matrix coords
  method: string           // "step13" | "diagonal" | "col" | "step7" | "step27"
  xor: number              // 0, 7, 13, 27, 33
  compressed: boolean
  hash160: string
}
```
**Implementation:** Render as GOLD nodes with special glow, always visible, never filtered out.

### QW3: DERIVATION METHOD COLORING
**Source:** `interesting-addresses.json` `method` field
| Method | Color | Description |
|--------|-------|-------------|
| `step13` | `#F59E0B` Gold | 13-step diagonal pattern |
| `diagonal` | `#8B5CF6` Purple | Pure diagonal traversal |
| `col` | `#3B82F6` Blue | Column-based derivation |
| `step7` | `#10B981` Emerald | 7-step pattern |
| `step27` | `#06B6D4` Cyan | 27-step pattern |
| `row` | `#EC4899` Pink | Row-based derivation |

### QW4: XOR VALUE ENCODING (RING/HALO EFFECT)
**Source:** `interesting-addresses.json` `xor` field (0, 7, 13, 27, 33)
```typescript
const XOR_RING_CONFIG = {
  0:  { rings: 0, color: '#FFFFFF' },  // No XOR - solid white
  7:  { rings: 1, color: '#F59E0B' },  // Single orange ring
  13: { rings: 2, color: '#8B5CF6' },  // Double purple rings
  27: { rings: 3, color: '#3B82F6' },  // Triple blue rings
  33: { rings: 4, color: '#EC4899' },  // Quad pink rings
}
// Higher XOR = more complex derivation = more rings
```

### QW5: QUBIC SEED VALIDATION OVERLAY
**Source:** `qubic-seeds.json` (23,765 records with match validation)
```typescript
interface QubicSeed {
  id: number
  seed: string                    // 55-char seed
  documentedIdentity: string      // 60-char documented
  realIdentity: string            // 60-char computed
  match: boolean                  // TRUE = validated identity
  source: string                  // batch file origin
}
```
**Implementation:**
- GREEN glow = match: true (identity validated)
- RED glow = match: false (checksum mismatch - SUSPICIOUS!)
- This reveals potentially compromised/fake seeds

### QW6: KEYBOARD SHORTCUTS MODAL
**Pattern from:** `NeuraxonScene.tsx` `KeyboardShortcutsPanel`
```typescript
const KEYBOARD_SHORTCUTS = [
  { key: 'Space', action: 'Play / Pause timeline' },
  { key: '←/→', action: 'Navigate timeline blocks' },
  { key: 'Home', action: 'Jump to Genesis Block' },
  { key: 'End', action: 'Jump to latest block' },
  { key: 'F', action: 'Toggle fullscreen' },
  { key: 'E', action: 'Toggle edges/connections' },
  { key: 'R', action: 'Reset camera to default' },
  { key: 'C', action: 'Center on selected node' },
  { key: 'P', action: 'Toggle Patoshi cluster' },
  { key: 'M', action: 'Toggle Matrix-derived nodes' },
  { key: 'I', action: 'Toggle info panel' },
  { key: 'S', action: 'Take screenshot' },
  { key: '/', action: 'Focus search input' },
  { key: '?', action: 'Show this help' },
  { key: 'Esc', action: 'Close panels / Deselect' },
]
```

### QW7: SHARE URL WITH STATE
**Pattern from:** `NeuraxonScene.tsx` `handleShare`
```typescript
const handleShare = async () => {
  const params = new URLSearchParams({
    block: String(currentBlock),
    node: selectedNode?.address || '',
    camera: JSON.stringify(cameraState),
    filters: JSON.stringify(activeFilters),
    view: viewMode,
  })
  const url = `${window.location.origin}/evidence?viz=graph&${params}`

  if (navigator.share) {
    await navigator.share({
      title: 'Bitcoin Address Graph - CFB Forensics',
      text: `Exploring ${selectedNode?.address || 'network'} with ${visibleNodes} addresses`,
      url,
    })
  } else {
    await navigator.clipboard.writeText(url)
    // Show "Link copied!" toast
  }
}
```

### QW8: ERROR TYPE HANDLING
**Pattern from:** `NeuraxonScene.tsx` error system
```typescript
type AddressGraphErrorType =
  | 'NETWORK_ERROR'     // Failed to fetch JSON
  | 'PARSE_ERROR'       // Invalid JSON format
  | 'VALIDATION_ERROR'  // Data schema mismatch
  | 'TIMEOUT_ERROR'     // Load took > 30s
  | 'MEMORY_ERROR'      // Too many nodes for browser
  | 'WEBGL_ERROR'       // WebGL not supported
  | 'UNKNOWN_ERROR'

interface AddressGraphError {
  type: AddressGraphErrorType
  message: string
  details?: string
  retryable: boolean
}

const ERROR_CONFIG = {
  NETWORK_ERROR: { icon: WifiOff, color: 'text-orange-400', retryable: true },
  PARSE_ERROR: { icon: FileWarning, color: 'text-red-400', retryable: false },
  VALIDATION_ERROR: { icon: AlertTriangle, color: 'text-red-400', retryable: false },
  TIMEOUT_ERROR: { icon: Clock, color: 'text-yellow-400', retryable: true },
  MEMORY_ERROR: { icon: MemoryStick, color: 'text-red-400', retryable: false },
  WEBGL_ERROR: { icon: Monitor, color: 'text-red-400', retryable: false },
  UNKNOWN_ERROR: { icon: AlertTriangle, color: 'text-gray-400', retryable: true },
}
```

### QW9: PLAYBACK SPEED CONTROL
**Pattern from:** `NeuraxonControls.tsx`
```typescript
const SPEED_OPTIONS = [0.25, 0.5, 1, 1.5, 2, 3, 5]

// Timeline playback with speed control
const [playbackSpeed, setPlaybackSpeed] = useState(1)
const [isPlaying, setIsPlaying] = useState(false)

useEffect(() => {
  if (!isPlaying) return
  const interval = setInterval(() => {
    setCurrentBlock((b) => (b + 1) % totalBlocks)
  }, 1000 / playbackSpeed)
  return () => clearInterval(interval)
}, [isPlaying, playbackSpeed, totalBlocks])
```

### QW10: COLLAPSIBLE MOBILE CONTROLS
**Pattern from:** `NeuraxonControls.tsx` `isCollapsed` state
```typescript
const [isCollapsed, setIsCollapsed] = useState(false)

// Collapsed view on mobile
if (isCollapsed) {
  return (
    <button
      onClick={() => setIsCollapsed(false)}
      className="fixed bottom-4 left-4 right-4 flex items-center justify-center gap-2
                 bg-black/80 backdrop-blur-md border border-white/10 rounded-lg p-3"
    >
      <ChevronUp className="w-4 h-4" />
      <span>Show Controls</span>
      <span className="text-xs text-white/50">Block {currentBlock.toLocaleString()}</span>
    </button>
  )
}
```

---

## CRITICAL DATA SOURCES (COMPLETE INVENTORY)

| File | Size | Records | Key Fields |
|------|------|---------|------------|
| `patoshi-addresses.json` | 4.9MB | 21,953 | blockHeight, pubkey, amount, scriptType |
| `qubic-seeds.json` | 7.3MB | 23,765 | seed, documentedIdentity, realIdentity, match |
| `bitcoin-derived-addresses.json` | 4.2MB | 16,384+ | address, privateKey, sequence, method |
| `bitcoin-private-keys.json` | 312KB | ~1,000 | address, privateKeyWIF, position, method, xorVariant |
| `interesting-addresses.json` | 5.6KB | 30 | address, position, method, xor, compressed, hash160 |
| `matrix-addresses.json` | 63.7MB | 900,000+ | id, address (HUGE - needs streaming!) |
| `anna-matrix.json` | 78KB | 128×128 | 2D integer array |

### CRITICAL: matrix-addresses.json Handling
```typescript
// 900k+ addresses cannot load at once! Use progressive streaming:
async function* streamMatrixAddresses() {
  const response = await fetch('/data/matrix-addresses.json')
  const reader = response.body?.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    // Parse and yield chunks of 1000 addresses
    const addresses = parseChunk(buffer)
    for (const addr of addresses) yield addr
  }
}

// Or use Web Worker for background parsing
const worker = new Worker('/workers/matrix-parser.js')
worker.postMessage({ file: '/data/matrix-addresses.json' })
worker.onmessage = (e) => {
  const { type, data } = e.data
  if (type === 'CHUNK') appendNodes(data)
  if (type === 'COMPLETE') finalizeGraph()
}
```

---

## 1. CORE ARCHITECTURE (UPDATED)

### 1.1 Component Structure (EXPANDED)
```
components/evidence/address-graph/
├── AddressGraphScene.tsx           # 2000+ LOC - Main orchestrator
├── useAddressGraphData.ts          # 500+ LOC - Data hook with streaming
├── AddressNode.tsx                 # 300+ LOC - Instanced node rendering
├── AddressConnection.tsx           # 200+ LOC - Edge rendering with particles
├── AddressDetailPanel.tsx          # 500+ LOC - With Identity/Connections tabs
├── AddressGraphControls.tsx        # 400+ LOC - Bottom controls bar
├── AddressGraphToolbar.tsx         # 150+ LOC - Top-right action buttons
├── AddressGraphFilters.tsx         # 300+ LOC - Left filter panel
├── AddressTimeline.tsx             # 300+ LOC - Block height scrubber
├── AddressClusterRenderer.tsx      # 200+ LOC - Cluster visualization
├── KeyboardShortcutsPanel.tsx      # 100+ LOC - Help modal
├── LoadingScreen.tsx               # 150+ LOC - With progress + stats preview
├── ErrorScreen.tsx                 # 150+ LOC - With retry + troubleshooting
├── forceSimulation.worker.ts       # 200+ LOC - Web Worker for physics
├── matrixParser.worker.ts          # 100+ LOC - Web Worker for 900k parsing
├── shaders/
│   ├── nodeVertex.glsl             # Instanced node shader
│   ├── nodeFragment.glsl           # With fresnel + glow
│   ├── edgeVertex.glsl             # Bezier curve shader
│   ├── edgeFragment.glsl           # With particle flow
│   └── ringVertex.glsl             # XOR ring halos
├── types.ts                        # 200+ LOC - Complete type definitions
├── constants.ts                    # 100+ LOC - Colors, presets, config
└── index.ts
```

---

## 2. NODE TYPES & VISUAL ENCODING (EXPANDED)

### 2.1 Complete Address Categories
| Category | Color | Shape | Size | Glow | Ring Pattern | Data Source |
|----------|-------|-------|------|------|--------------|-------------|
| **Patoshi Genesis** | `#FFD700` Gold | Dodecahedron | XL | Pulse | Crown | patoshi block 0-100 |
| **Patoshi Era** | `#F59E0B` Orange | Sphere | Large | Soft | None | patoshi 101-36000 |
| **CFB Vanity (1CFB)** | `#8B5CF6` Purple | Octahedron | Large | Strong | XOR-based | interesting-addresses |
| **Patoshi Vanity (1Pat)** | `#EC4899` Pink | Octahedron | Large | Strong | XOR-based | interesting-addresses |
| **Matrix step13** | `#F59E0B` Gold | Cube | Medium | Subtle | 1 ring | method=step13 |
| **Matrix diagonal** | `#8B5CF6` Purple | Cube | Medium | Subtle | 2 rings | method=diagonal |
| **Matrix step7** | `#10B981` Emerald | Cube | Medium | Subtle | 1 ring | method=step7 |
| **Matrix step27** | `#06B6D4` Cyan | Cube | Medium | Subtle | 3 rings | method=step27 |
| **Matrix col/row** | `#3B82F6` Blue | Cube | Small | None | None | method=col/row |
| **Seed Validated** | Green border | Any | Any | Pulse | Check | match=true |
| **Seed Mismatch** | Red border | Any | Any | Warning | X | match=false |
| **Unknown** | `#6B7280` Gray | Sphere | XS | None | None | fallback |

### 2.2 Node State Machine
```typescript
type NodeState =
  | 'default'           // Normal rendering
  | 'hovered'           // Mouse over - show tooltip
  | 'selected'          // Clicked - open detail panel
  | 'connected'         // Neighbor of selected node
  | 'path-highlight'    // Part of shortest path
  | 'filtered-out'      // Ghost mode (0.1 opacity)
  | 'loading'           // Placeholder during stream
  | 'error'             // Failed to load details
```

---

## 3. DETAIL PANEL (NEURAXON PATTERN)

### 3.1 Tabbed Interface
```
┌────────────────────────────────────────────────┐
│ [X Close]                                      │
│ ═══════════════════════════════════════════    │
│ 1CFBtCo6zDgmXAD9NJTZ7dw7Yvoq6ZPGGQ  [Copy]    │
│ ═══════════════════════════════════════════    │
│                                                │
│ ┌──────────────────┐ ┌──────────────────┐     │
│ │     Identity     │ │   Connections    │     │
│ │    [selected]    │ │      (47)        │     │
│ └──────────────────┘ └──────────────────┘     │
├────────────────────────────────────────────────┤
│ (Tab Content Here)                             │
└────────────────────────────────────────────────┘
```

### 3.2 Identity Tab
```
TYPE:        🟡 CFB Vanity Address
STATUS:      🟢 Never Spent
BALANCE:     ₿ 0.00000000

─────────────────────────────────────
DERIVATION:
├─ Method:       step13
├─ Matrix Pos:   [96, 17]
├─ XOR Variant:  7
├─ Compressed:   false
└─ Hash160:      7b584aa6957a...

─────────────────────────────────────
BLOCK INFO:
├─ First Seen:   Block 156,743
├─ Date:         2011-09-13 14:23:07 UTC
├─ Tx Count:     0
└─ Last Active:  Never

─────────────────────────────────────
QUBIC SEED:
├─ Seed:         cfbtco6zdgmx... (55 chars)
├─ Identity:     CFBTCO6ZDGMX... (60 chars)
├─ Validation:   ✅ MATCH
└─ [View on Qubic Explorer]

─────────────────────────────────────
EXTERNAL:
[Blockchain.com] [Blockchair] [Mempool.space]
```

### 3.3 Connections Tab
```
CONNECTIONS: 47
├─ Outgoing:  23  [→ View all]
├─ Incoming:  18  [← View all]
└─ Temporal:  6   [⟷ Same block range]

─────────────────────────────────────
OUTGOING (Top 5):
→ 1A1zP1eP5QGefi2DMPTfTL5SLmv...   [Temporal]
→ 12c6DSiU4Rq3P4ZxziKxzrL5LmM...   [Matrix]
→ 1HLoD9E4SDFFPDiYfNYnkBLQ85Y...   [Seed]
→ 1FvzCLoTPGANNjWoUo6jUGuAG3w...   [Derivation]
→ 16ftSEQ4ctQFDtVZiUBusQUjRrG...   [Transaction]

─────────────────────────────────────
CONNECTION LEGEND:
● Direct Transaction (on-chain)
● Same Seed (Qubic relation)
● Matrix Position (adjacent cells)
● Temporal (same block range)
● Derivation (key path)
```

---

## 4. LOADING SCREEN (NEURAXON PATTERN)

### 4.1 Stats Preview During Load
```tsx
function LoadingScreen({ progress, stats }: { progress: number; stats: LoadStats }) {
  return (
    <div className="flex flex-col items-center justify-center h-full bg-gradient-to-b from-black via-gray-900 to-black">
      {/* Animated network icon */}
      <div className="relative w-32 h-32 mb-8">
        <div className="absolute inset-0 rounded-full border-2 border-orange-500/30 animate-ping" />
        <div className="absolute inset-4 rounded-full border-2 border-blue-500/30 animate-ping delay-200" />
        <div className="absolute inset-0 flex items-center justify-center">
          <Network className="w-16 h-16 text-orange-500 animate-pulse" />
        </div>
      </div>

      {/* Title */}
      <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-400 to-blue-400 bg-clip-text text-transparent mb-2">
        Address Graph
      </h2>
      <p className="text-sm text-gray-500 mb-6">Loading Bitcoin-Qubic network...</p>

      {/* Progress bar */}
      <div className="w-64 h-2 bg-gray-800 rounded-full overflow-hidden mb-4">
        <div
          className="h-full bg-gradient-to-r from-orange-500 to-blue-500 transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="text-xs text-gray-600 mb-8">{progress.toFixed(0)}% complete</div>

      {/* Stats preview */}
      <div className="grid grid-cols-4 gap-6 text-center">
        <div>
          <div className="text-xl font-bold text-orange-400">{stats.patoshi.toLocaleString()}</div>
          <div className="text-[10px] text-gray-600">Patoshi</div>
        </div>
        <div>
          <div className="text-xl font-bold text-purple-400">{stats.cfbLinked.toLocaleString()}</div>
          <div className="text-[10px] text-gray-600">CFB-Linked</div>
        </div>
        <div>
          <div className="text-xl font-bold text-blue-400">{stats.matrixDerived.toLocaleString()}</div>
          <div className="text-[10px] text-gray-600">Matrix</div>
        </div>
        <div>
          <div className="text-xl font-bold text-white/80">{stats.totalEdges.toLocaleString()}</div>
          <div className="text-[10px] text-gray-600">Edges</div>
        </div>
      </div>
    </div>
  )
}
```

---

## 5. ERROR SCREEN (NEURAXON PATTERN)

### 5.1 With Troubleshooting Tips
```tsx
function ErrorScreen({ error, onRetry, retryCount }: ErrorScreenProps) {
  const config = ERROR_CONFIG[error.type]
  const Icon = config.icon
  const canRetry = error.retryable && retryCount < 3

  return (
    <div className="flex flex-col items-center justify-center h-full bg-gradient-to-b from-black to-gray-900 p-8">
      {/* Error icon with ring */}
      <div className="relative mb-6">
        <div className={`absolute inset-0 rounded-full border-2 ${config.color} opacity-20 animate-ping`} />
        <div className={`w-24 h-24 rounded-full bg-gray-900 border-2 flex items-center justify-center ${config.color}`}>
          <Icon className="w-12 h-12" />
        </div>
      </div>

      {/* Error message */}
      <h2 className={`text-xl font-bold ${config.color} mb-2`}>{error.message}</h2>
      {error.details && <p className="text-sm text-gray-500 max-w-sm text-center mb-4">{error.details}</p>}

      {/* Error type badge */}
      <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-full mb-6">
        <span className="text-xs text-gray-500 uppercase">{error.type.replace('_', ' ')}</span>
      </div>

      {/* Retry button */}
      {canRetry && (
        <Button onClick={onRetry} className="gap-2 bg-orange-600 hover:bg-orange-500 mb-2">
          <RefreshCw className="w-4 h-4" />
          Try Again
        </Button>
      )}
      {canRetry && <p className="text-xs text-gray-600">Attempt {retryCount + 1} of 3</p>}

      {/* Troubleshooting tips */}
      <div className="mt-8 pt-6 border-t border-white/10 w-full max-w-sm">
        <p className="text-[10px] text-gray-600 uppercase mb-3">Troubleshooting</p>
        <ul className="text-xs text-gray-500 space-y-2">
          <li>• Check your internet connection</li>
          <li>• Try refreshing the page</li>
          <li>• Disable ad blockers that may block JSON files</li>
          <li>• Try a different browser (Chrome recommended)</li>
          <li>• Clear browser cache if issue persists</li>
        </ul>
      </div>
    </div>
  )
}
```

---

## 6. COMPLETE CONTROLS LAYOUT

### 6.1 Top-Right Toolbar
```
┌─────────────────────────────────────────────────────────────────────────┐
│ [⛶ Fullscreen] [↻ Reset] [3D/2D] [📷 Screenshot] [Share] [⚙️] [?] [ℹ️] │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Bottom Controls Bar (NeuraxonControls Pattern)
```
┌─────────────────────────────────────────────────────────────────────────┐
│ [🔍 Search..._______________] [Find]  ║  [⏮][◀][▶ Play][▶][⏭]  ║     │
│                                       ║                          ║     │
│ Block 156,743 / 800,000  [━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] 1x ▼ │
│                                                                   │     │
│ [👁 Edges: ON]  [🎯 Patoshi: 21,953]  [📊 Matrix: 16,384]        │     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Left Filter Panel
```
┌────────────────────────────┐
│ 🎚️ FILTERS                 │
├────────────────────────────┤
│ ADDRESS TYPE:              │
│ [✓] 🟠 Patoshi  (21,953)  │
│ [✓] 🟣 CFB      (30)      │
│ [✓] 🔵 Matrix   (16,384)  │
│ [✓] 🟢 Validated (23,765) │
│ [ ] ⚪ Unknown             │
├────────────────────────────┤
│ DERIVATION METHOD:         │
│ [✓] step13                │
│ [✓] diagonal              │
│ [✓] step7 / step27        │
│ [✓] col / row             │
├────────────────────────────┤
│ XOR VARIANT:               │
│ [ ] 0  [ ] 7  [ ] 13      │
│ [ ] 27 [ ] 33             │
├────────────────────────────┤
│ SEED VALIDATION:           │
│ [●] All                   │
│ [ ] Validated only        │
│ [ ] Mismatch only         │
├────────────────────────────┤
│ BLOCK RANGE:               │
│ [0 ────●──── 800,000]     │
├────────────────────────────┤
│ CONNECTIONS:               │
│ Min: [1] ───●              │
├────────────────────────────┤
│ [Reset Filters]            │
└────────────────────────────┘
```

### 6.4 Left Legend
```
┌────────────────────────────┐
│ 🔵 ADDRESS GRAPH           │
│ Bitcoin-Qubic Network      │
├────────────────────────────┤
│ NODES:                     │
│ 🟡 ◆ Genesis               │
│ 🟠 ● Patoshi               │
│ 🟣 ◆ CFB Vanity (1CFB)    │
│ 💗 ◆ Patoshi Vanity (1Pat)│
│ 🔵 ■ Matrix-Derived        │
│ 🟢 ● Seed Validated        │
│ 🔴 ○ Seed Mismatch         │
│ ⚪ · Unknown               │
├────────────────────────────┤
│ EDGES:                     │
│ ─── On-chain Transaction  │
│ ─·─ Same Qubic Seed       │
│ ··· Matrix Position       │
│ ≋≋≋ Same Block Range      │
│ →→→ Derivation Path       │
├────────────────────────────┤
│ XOR RINGS:                 │
│ ○    XOR 0  (no ring)     │
│ ◎    XOR 7  (1 ring)      │
│ ⊚    XOR 13 (2 rings)     │
│ ⊛    XOR 27 (3 rings)     │
│ ⊜    XOR 33 (4 rings)     │
├────────────────────────────┤
│ Visible: 12,341 / 62,132  │
│ Selected: 1CFBtCo6z...    │
│ Connections: 47            │
└────────────────────────────┘
```

---

## 7. KEYBOARD SHORTCUTS MODAL

```tsx
const SHORTCUTS = [
  { category: 'Playback', items: [
    { key: 'Space', action: 'Play / Pause timeline' },
    { key: '←', action: 'Previous block' },
    { key: '→', action: 'Next block' },
    { key: 'Home', action: 'Genesis block (0)' },
    { key: 'End', action: 'Latest block' },
    { key: '[/]', action: 'Decrease / Increase speed' },
  ]},
  { category: 'Navigation', items: [
    { key: 'R', action: 'Reset camera' },
    { key: 'C', action: 'Center on selected' },
    { key: 'F', action: 'Fly to node (double-click)' },
    { key: '1-5', action: 'Camera presets' },
  ]},
  { category: 'Visibility', items: [
    { key: 'E', action: 'Toggle edges' },
    { key: 'P', action: 'Toggle Patoshi nodes' },
    { key: 'M', action: 'Toggle Matrix nodes' },
    { key: 'V', action: 'Toggle validated only' },
  ]},
  { category: 'Interface', items: [
    { key: 'F11', action: 'Toggle fullscreen' },
    { key: 'I', action: 'Toggle info panel' },
    { key: '/', action: 'Focus search' },
    { key: 'S', action: 'Screenshot' },
    { key: '?', action: 'Show shortcuts' },
    { key: 'Esc', action: 'Close / Deselect' },
  ]},
]
```

---

## 8. DATA TYPES (COMPLETE)

```typescript
// ─────────────────────────────────────────────────────────────────────────
// NODE TYPES
// ─────────────────────────────────────────────────────────────────────────

interface AddressNode {
  id: string                              // Unique ID
  address: string                         // Bitcoin address
  type: AddressType
  position: [number, number, number]      // 3D position from force sim

  // Visual encoding
  color: string                           // Hex color
  shape: 'sphere' | 'cube' | 'octahedron' | 'dodecahedron'
  size: 'xs' | 'small' | 'medium' | 'large' | 'xl'
  glowIntensity: number                   // 0-1
  xorRings: number                        // 0-4 rings

  // Blockchain data
  blockHeight?: number                    // First seen (from Patoshi)
  amount?: number                         // BTC amount
  scriptType?: 'p2pk' | 'p2pkh' | 'p2sh' | 'p2wpkh'
  pubkey?: string                         // Uncompressed pubkey

  // Derivation data (from interesting-addresses)
  matrixPosition?: [number, number]       // [row, col] in Anna Matrix
  derivationMethod?: 'step13' | 'diagonal' | 'col' | 'row' | 'step7' | 'step27'
  xorVariant?: number                     // 0, 7, 13, 27, 33
  compressed?: boolean
  hash160?: string

  // Qubic data (from qubic-seeds)
  seed?: string                           // 55-char Qubic seed
  documentedIdentity?: string             // 60-char documented
  realIdentity?: string                   // 60-char computed
  seedValidated?: boolean                 // match field

  // Private key data (optional, sensitive)
  privateKeyAvailable?: boolean
  privateKeyWIF?: string                  // Only if revealed

  // State
  state: NodeState
  isVIP: boolean                          // Never filter out
  cluster?: string                        // Cluster assignment
}

type AddressType =
  | 'patoshi-genesis'     // Block 0-100
  | 'patoshi'             // Block 101+
  | 'cfb-vanity'          // 1CFB...
  | 'patoshi-vanity'      // 1Pat...
  | 'matrix-derived'      // From anna-matrix XOR
  | 'seed-validated'      // Qubic seed match=true
  | 'seed-mismatch'       // Qubic seed match=false
  | 'unknown'

// ─────────────────────────────────────────────────────────────────────────
// EDGE TYPES
// ─────────────────────────────────────────────────────────────────────────

interface AddressEdge {
  id: string
  source: string                          // Source address ID
  target: string                          // Target address ID
  type: EdgeType
  weight: number                          // 0-1 for visual thickness

  // Type-specific metadata
  txHash?: string                         // For transaction edges
  blockHeight?: number                    // For temporal edges
  matrixDistance?: number                 // For matrix position edges
  derivationSteps?: number                // For derivation edges

  // Visual
  color: string
  style: 'solid' | 'dashed' | 'dotted'
  animated: boolean
  particleCount: number
}

type EdgeType =
  | 'transaction'         // On-chain transaction
  | 'same-seed'           // Same Qubic seed
  | 'matrix-adjacent'     // Adjacent Anna Matrix cells
  | 'temporal'            // Same block range (±10)
  | 'derivation'          // Key derivation path

// ─────────────────────────────────────────────────────────────────────────
// STATS & METADATA
// ─────────────────────────────────────────────────────────────────────────

interface NetworkStats {
  totalNodes: number
  totalEdges: number
  clusters: number
  avgConnections: number

  byType: Record<AddressType, number>
  byMethod: Record<string, number>
  byXor: Record<number, number>

  patoshiBlocks: { min: number; max: number }
  totalBTC: number

  validatedSeeds: number
  mismatchedSeeds: number
}

interface FilterState {
  types: Set<AddressType>
  methods: Set<string>
  xorVariants: Set<number>
  seedValidation: 'all' | 'validated' | 'mismatch'
  blockRange: [number, number]
  minConnections: number
  searchQuery: string
}

interface ViewState {
  mode: 'force' | 'cluster' | 'timeline' | 'radial' | 'hierarchical'
  cameraPreset: 'overview' | 'patoshi' | 'cfb' | 'genesis' | 'custom'
  cameraPosition: [number, number, number]
  showEdges: boolean
  selectedNodeId: string | null
  highlightedPath: string[]
  playbackSpeed: number
  isPlaying: boolean
  currentBlock: number
}
```

---

## 9. PERFORMANCE STRATEGY

### 9.1 Progressive Loading Pipeline
```
1. Show LoadingScreen with stats preview
2. Fetch summary.json (1KB) → show total counts
3. Fetch interesting-addresses.json (5.6KB) → render 30 VIP nodes immediately
4. Fetch patoshi-addresses.json (4.9MB) → stream 21,953 nodes
5. Fetch bitcoin-derived-addresses.json (4.2MB) → stream 16,384 nodes
6. Fetch qubic-seeds.json (7.3MB) → add validation overlays
7. Run force simulation in Web Worker
8. Stream matrix-addresses.json (63.7MB) → background add 900k nodes
   - Only render visible 10k nodes (LOD)
   - Use spatial index for quick lookup
```

### 9.2 Rendering Optimization
```typescript
// InstancedMesh for 60 FPS with 100k+ nodes
const nodeInstances = new THREE.InstancedMesh(
  new THREE.SphereGeometry(0.1, 16, 16),
  nodeMaterial,
  MAX_VISIBLE_NODES // 10,000
)

// LOD: Only show nearby nodes in detail
function updateVisibleNodes(cameraPosition: Vector3) {
  const visible = spatialIndex.query(cameraPosition, MAX_DISTANCE)
  visible.slice(0, MAX_VISIBLE_NODES).forEach((node, i) => {
    matrix.setPosition(node.position)
    nodeInstances.setMatrixAt(i, matrix)
    nodeInstances.setColorAt(i, new Color(node.color))
  })
  nodeInstances.instanceMatrix.needsUpdate = true
}

// Edge culling: Only show edges for visible nodes
function updateVisibleEdges(visibleNodes: Set<string>) {
  const visibleEdges = edges.filter(e =>
    visibleNodes.has(e.source) || visibleNodes.has(e.target)
  )
  // Render max 50k edges
}
```

---

## 10. FILE DELIVERABLES (FINAL)

```
components/evidence/address-graph/
├── AddressGraphScene.tsx           # 2000+ LOC
├── useAddressGraphData.ts          # 500+ LOC
├── AddressNode.tsx                 # 300+ LOC
├── AddressConnection.tsx           # 200+ LOC
├── AddressDetailPanel.tsx          # 500+ LOC
├── AddressGraphControls.tsx        # 400+ LOC
├── AddressGraphToolbar.tsx         # 150+ LOC
├── AddressGraphFilters.tsx         # 300+ LOC
├── AddressTimeline.tsx             # 300+ LOC
├── AddressClusterRenderer.tsx      # 200+ LOC
├── KeyboardShortcutsPanel.tsx      # 100+ LOC
├── LoadingScreen.tsx               # 150+ LOC
├── ErrorScreen.tsx                 # 150+ LOC
├── workers/
│   ├── forceSimulation.worker.ts   # 200+ LOC
│   └── matrixParser.worker.ts      # 100+ LOC
├── shaders/
│   ├── node.vert.glsl
│   ├── node.frag.glsl
│   ├── edge.vert.glsl
│   ├── edge.frag.glsl
│   └── ring.vert.glsl
├── types.ts                        # 200+ LOC
├── constants.ts                    # 100+ LOC
└── index.ts

Total: ~5,500+ LOC
```

---

## 11. EXECUTION CHECKLIST

### Phase 1: Foundation
- [ ] Create folder structure
- [ ] Define all TypeScript interfaces
- [ ] Create constants file with colors/config
- [ ] Implement useAddressGraphData hook
- [ ] Create LoadingScreen component
- [ ] Create ErrorScreen component

### Phase 2: 3D Scene
- [ ] Basic Three.js canvas setup
- [ ] InstancedMesh node rendering
- [ ] Camera controls (OrbitControls)
- [ ] Camera presets
- [ ] Basic force simulation

### Phase 3: Data Integration
- [ ] Load interesting-addresses.json (VIP nodes)
- [ ] Load patoshi-addresses.json (block height)
- [ ] Load bitcoin-derived-addresses.json
- [ ] Load qubic-seeds.json (validation)
- [ ] Compute edges from relationships
- [ ] Web Worker for force simulation

### Phase 4: UI
- [ ] Top toolbar (fullscreen, reset, share)
- [ ] Bottom controls bar (Neuraxon pattern)
- [ ] Left filter panel
- [ ] Left legend panel
- [ ] Keyboard shortcuts modal
- [ ] Mobile collapsible controls

### Phase 5: Detail Panel
- [ ] Identity tab
- [ ] Connections tab
- [ ] External links
- [ ] Copy functionality
- [ ] Navigate to connected nodes

### Phase 6: Advanced
- [ ] Timeline scrubber with playback
- [ ] Speed control (0.25x - 5x)
- [ ] Share URL with state
- [ ] XOR ring halos
- [ ] Seed validation overlay
- [ ] Path finding mode
- [ ] Cluster zoom

### Phase 7: Polish
- [ ] Fresnel shaders
- [ ] Particle flow edges
- [ ] Loading animations
- [ ] Error retry logic
- [ ] Performance profiling
- [ ] Mobile testing

---

## SUMMARY

This plan is now **10000% wasserdicht** with:

1. **Complete data inventory** - All 7 JSON files analyzed with field-level detail
2. **10 Quick Wins** - Critical features from Neuraxon/MatrixTerrain patterns
3. **Streaming strategy** - Handle 900k+ matrix addresses without crashing
4. **VIP node layer** - 30 special addresses always visible
5. **XOR encoding** - Visual rings showing derivation complexity
6. **Seed validation** - Green/red overlay for identity verification
7. **Full keyboard shortcuts** - Modal with all controls
8. **Share URL** - Deep linking with filters/selection/camera
9. **Error handling** - 6 error types with troubleshooting
10. **Collapsible mobile** - Touch-friendly controls

This is a **$10 Billion Research Lab Grade** forensic visualization tool.
