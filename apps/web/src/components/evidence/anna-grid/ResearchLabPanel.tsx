'use client'

import { useState, useCallback, useEffect } from 'react'
import {
  X,
  Play,
  Code,
  BarChart3,
  FileJson,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Beaker,
  Sparkles,
  Hash,
  Binary,
  RefreshCw,
  Download,
  ExternalLink,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { executeSandboxedCode, CODE_SNIPPETS } from '@/lib/research/sandbox'
import { createMatrixAPI, type MatrixStats } from '@/lib/research/matrix-api'

// =============================================================================
// TYPES
// =============================================================================

interface ResearchLabPanelProps {
  isOpen: boolean
  onClose: () => void
  matrix: number[][]
  stats: {
    min: number
    max: number
    mean: number
    stdDev: number
    zeroCount: number
    positiveCount: number
    negativeCount: number
    totalCells: number
  }
  selectedCell: { row: number; col: number; value: number } | null
  onCellSelect: (row: number, col: number) => void
}

// =============================================================================
// CODE EDITOR COMPONENT
// =============================================================================

function SimpleCodeEditor({
  code,
  onChange,
}: {
  code: string
  onChange: (code: string) => void
}) {
  return (
    <div className="relative">
      <textarea
        value={code}
        onChange={(e) => onChange(e.target.value)}
        className="w-full h-48 bg-black/50 border border-white/10 rounded-lg p-3 font-mono text-sm text-green-400 resize-none focus:outline-none focus:border-green-500/50"
        spellCheck={false}
        placeholder="// Write your analysis code here
// Available: matrix.getCell(row, col), matrix.rowSum(row), etc.

const cell = matrix.getCell(21, 68)
console.log(cell)
return cell.value"
      />
      <div className="absolute bottom-2 right-2 text-[10px] text-white/30">
        JavaScript
      </div>
    </div>
  )
}

// =============================================================================
// QUICK ANALYSIS TOOLS
// =============================================================================

function QuickAnalysis({
  matrix,
  stats,
  selectedCell,
  onResult,
}: {
  matrix: number[][]
  stats: ResearchLabPanelProps['stats']
  selectedCell: ResearchLabPanelProps['selectedCell']
  onResult: (result: string) => void
}) {
  const matrixAPI = createMatrixAPI(matrix)

  const tools = [
    {
      name: 'Row Sums',
      icon: Hash,
      action: () => {
        const sums = []
        for (let i = 0; i < 128; i++) {
          const sum = matrixAPI.rowSum(i)
          if (sum !== 0) sums.push({ row: i, sum })
        }
        const nonZero = sums.filter((s) => s.sum !== 0)
        onResult(
          `Row Sums Analysis:\n` +
            `- Total rows: 128\n` +
            `- Non-zero sums: ${nonZero.length}\n` +
            `- Zero sums: ${128 - nonZero.length}\n\n` +
            `Notable rows:\n` +
            nonZero
              .slice(0, 10)
              .map((s) => `  Row ${s.row}: ${s.sum}`)
              .join('\n')
        )
      },
    },
    {
      name: 'Find Zeros',
      icon: Binary,
      action: () => {
        const zeros = matrixAPI.findValue(0)
        onResult(
          `Zero Values:\n` +
            `- Count: ${zeros.length}\n` +
            `- Percentage: ${((zeros.length / 16384) * 100).toFixed(2)}%\n\n` +
            `Positions:\n` +
            zeros
              .slice(0, 20)
              .map((p) => `  [${p.row}, ${p.col}]`)
              .join('\n') +
            (zeros.length > 20 ? `\n  ... and ${zeros.length - 20} more` : '')
        )
      },
    },
    {
      name: 'Symmetry',
      icon: RefreshCw,
      action: () => {
        const rotational = matrixAPI.findSymmetry('rotational')
        const horizontal = matrixAPI.findSymmetry('horizontal')
        const vertical = matrixAPI.findSymmetry('vertical')
        onResult(
          `Symmetry Analysis:\n\n` +
            `Rotational (180°):\n` +
            `  Matches: ${rotational.matches}/${rotational.total}\n` +
            `  Percentage: ${rotational.percentage.toFixed(1)}%\n\n` +
            `Horizontal (flip):\n` +
            `  Matches: ${horizontal.matches}/${horizontal.total}\n` +
            `  Percentage: ${horizontal.percentage.toFixed(1)}%\n\n` +
            `Vertical (flip):\n` +
            `  Matches: ${vertical.matches}/${vertical.total}\n` +
            `  Percentage: ${vertical.percentage.toFixed(1)}%`
        )
      },
    },
    {
      name: 'Word: THE',
      icon: Sparkles,
      action: () => {
        const result = matrixAPI.wordEncodingSum('THE')
        onResult(
          `Word Encoding: "THE"\n\n` +
            `Using A=0, B=1, ... Z=25 diagonal positions:\n` +
            `  T (19): matrix[19][19] = ${matrix[19]?.[19]}\n` +
            `  H (7):  matrix[7][7] = ${matrix[7]?.[7]}\n` +
            `  E (4):  matrix[4][4] = ${matrix[4]?.[4]}\n\n` +
            `Sum: ${result}\n\n` +
            `Note: 33 = Blood Moon to Easter days in 2015`
        )
      },
    },
    {
      name: 'Selected Cell',
      icon: BarChart3,
      action: () => {
        if (!selectedCell) {
          onResult('No cell selected. Click on a cell in the matrix first.')
          return
        }
        const cell = matrixAPI.getCell(selectedCell.row, selectedCell.col)
        onResult(
          `Cell [${cell.row}, ${cell.col}]:\n\n` +
            `Value: ${cell.value}\n` +
            `Address: ${cell.address}\n` +
            `Hex: ${cell.hex}\n` +
            `Binary: ${cell.binary}\n\n` +
            `Neighbors:\n` +
            `  North: ${cell.neighbors.north ?? 'N/A'}\n` +
            `  South: ${cell.neighbors.south ?? 'N/A'}\n` +
            `  East: ${cell.neighbors.east ?? 'N/A'}\n` +
            `  West: ${cell.neighbors.west ?? 'N/A'}\n\n` +
            (cell.isSpecial ? `Special: ${cell.specialInfo}` : '')
        )
      },
    },
  ]

  return (
    <div className="grid grid-cols-2 gap-2">
      {tools.map((tool) => {
        const Icon = tool.icon
        return (
          <button
            key={tool.name}
            onClick={tool.action}
            className="flex items-center gap-2 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-white/80 hover:text-white transition-colors"
          >
            <Icon className="w-4 h-4 text-cyan-400" />
            {tool.name}
          </button>
        )
      })}
    </div>
  )
}

// =============================================================================
// API INFO SECTION
// =============================================================================

function APIInfo() {
  const [copied, setCopied] = useState<string | null>(null)

  const endpoints = [
    { method: 'GET', path: '/api/research/anna-matrix', desc: 'Statistics' },
    { method: 'GET', path: '/api/research/anna-matrix?format=full', desc: 'Full matrix' },
    { method: 'GET', path: '/api/research/anna-matrix?format=cell&row=21&col=68', desc: 'Single cell' },
    { method: 'GET', path: '/api/research/anna-matrix?format=row&row=21', desc: 'Entire row' },
  ]

  const copyToClipboard = async (text: string) => {
    await navigator.clipboard.writeText(text)
    setCopied(text)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs text-white/50 uppercase">REST API</span>
        <a
          href="/api/research/anna-matrix?format=info"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
        >
          Full Docs <ExternalLink className="w-3 h-3" />
        </a>
      </div>
      <div className="space-y-1">
        {endpoints.map((ep) => (
          <div
            key={ep.path}
            className="flex items-center gap-2 bg-black/30 rounded px-2 py-1.5 group"
          >
            <span className="text-[10px] font-mono text-green-400 w-8">{ep.method}</span>
            <code className="flex-1 text-[10px] font-mono text-white/60 truncate">{ep.path}</code>
            <button
              onClick={() => copyToClipboard(ep.path)}
              className="opacity-0 group-hover:opacity-100 transition-opacity"
            >
              {copied === ep.path ? (
                <Check className="w-3 h-3 text-green-400" />
              ) : (
                <Copy className="w-3 h-3 text-white/40 hover:text-white" />
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

// =============================================================================
// MAIN RESEARCH LAB PANEL
// =============================================================================

export function ResearchLabPanel({
  isOpen,
  onClose,
  matrix,
  stats,
  selectedCell,
  onCellSelect,
}: ResearchLabPanelProps) {
  const [code, setCode] = useState(CODE_SNIPPETS[0]?.code || '')
  const [output, setOutput] = useState('')
  const [isRunning, setIsRunning] = useState(false)
  const [activeTab, setActiveTab] = useState<'code' | 'analysis' | 'api'>('code')
  const [expandedSnippets, setExpandedSnippets] = useState(false)

  // Create matrix API for code execution
  const matrixAPI = createMatrixAPI(matrix)

  // Run user code
  const runCode = useCallback(async () => {
    if (!code.trim()) return
    setIsRunning(true)
    setOutput('Running...')

    try {
      const result = await executeSandboxedCode(code, matrixAPI)
      let outputText = ''

      if (result.logs.length > 0) {
        outputText += result.logs.join('\n')
      }

      if (result.result !== undefined) {
        if (outputText) outputText += '\n\n'
        outputText += '→ ' + JSON.stringify(result.result, null, 2)
      }

      if (result.error) {
        outputText = `Error: ${result.error}`
      }

      setOutput(outputText || 'No output')
    } catch (err) {
      setOutput(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setIsRunning(false)
    }
  }, [code, matrixAPI])

  // Keyboard shortcut to run code
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && isOpen) {
        e.preventDefault()
        runCode()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [runCode, isOpen])

  if (!isOpen) return null

  return (
    <div className="absolute top-0 right-0 bottom-0 w-[400px] bg-zinc-950/98 backdrop-blur-xl border-l border-white/10 z-50 flex flex-col pointer-events-auto overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-black/50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-green-500 to-cyan-500 flex items-center justify-center">
            <Beaker className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Research Lab</h3>
            <p className="text-[10px] text-white/40">Code • Analyze • Export</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 text-white/60 hover:text-white">
          <X className="w-4 h-4" />
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/10">
        {[
          { id: 'code', label: 'Code', icon: Code },
          { id: 'analysis', label: 'Analysis', icon: BarChart3 },
          { id: 'api', label: 'API', icon: FileJson },
        ].map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 text-sm transition-colors ${
                activeTab === tab.id
                  ? 'text-white bg-white/5 border-b-2 border-cyan-400'
                  : 'text-white/50 hover:text-white hover:bg-white/5'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activeTab === 'code' && (
          <>
            {/* Snippets */}
            <div className="space-y-2">
              <button
                onClick={() => setExpandedSnippets(!expandedSnippets)}
                className="flex items-center justify-between w-full text-xs text-white/50 hover:text-white"
              >
                <span className="uppercase">Snippets</span>
                {expandedSnippets ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              {expandedSnippets && (
                <div className="grid grid-cols-2 gap-1">
                  {CODE_SNIPPETS.map((snippet) => (
                    <button
                      key={snippet.name}
                      onClick={() => setCode(snippet.code)}
                      className="text-left px-2 py-1.5 bg-white/5 hover:bg-white/10 rounded text-xs text-white/70 hover:text-white truncate"
                      title={snippet.name}
                    >
                      {snippet.name}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Editor */}
            <SimpleCodeEditor code={code} onChange={setCode} />

            {/* Run Button */}
            <Button
              onClick={runCode}
              disabled={isRunning || !code.trim()}
              className="w-full gap-2 bg-gradient-to-r from-green-600 to-cyan-600 hover:from-green-500 hover:to-cyan-500"
            >
              <Play className="w-4 h-4" />
              {isRunning ? 'Running...' : 'Run Code'}
              <span className="text-[10px] text-white/50">(⌘+Enter)</span>
            </Button>

            {/* Output */}
            <div className="space-y-2">
              <div className="text-xs text-white/50 uppercase">Output</div>
              <pre className="bg-black/50 border border-white/10 rounded-lg p-3 text-xs font-mono text-white/80 max-h-48 overflow-auto whitespace-pre-wrap">
                {output || 'Click "Run Code" to execute your analysis.'}
              </pre>
            </div>
          </>
        )}

        {activeTab === 'analysis' && (
          <>
            {/* Quick Stats */}
            <div className="space-y-2">
              <div className="text-xs text-white/50 uppercase">Quick Stats</div>
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-[10px] text-white/40">Range</div>
                  <div className="text-sm font-mono text-white">[{stats.min}, {stats.max}]</div>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-[10px] text-white/40">Mean</div>
                  <div className="text-sm font-mono text-white">{stats.mean.toFixed(2)}</div>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-[10px] text-white/40">Std Dev</div>
                  <div className="text-sm font-mono text-white">{stats.stdDev.toFixed(2)}</div>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-[10px] text-white/40">Zeros</div>
                  <div className="text-sm font-mono text-white">{stats.zeroCount}</div>
                </div>
              </div>
            </div>

            {/* Quick Analysis Tools */}
            <div className="space-y-2">
              <div className="text-xs text-white/50 uppercase">Quick Analysis</div>
              <QuickAnalysis
                matrix={matrix}
                stats={stats}
                selectedCell={selectedCell}
                onResult={setOutput}
              />
            </div>

            {/* Output */}
            {output && (
              <div className="space-y-2">
                <div className="text-xs text-white/50 uppercase">Result</div>
                <pre className="bg-black/50 border border-white/10 rounded-lg p-3 text-xs font-mono text-white/80 max-h-64 overflow-auto whitespace-pre-wrap">
                  {output}
                </pre>
              </div>
            )}
          </>
        )}

        {activeTab === 'api' && (
          <>
            <APIInfo />

            {/* Export Options */}
            <div className="space-y-2 pt-4 border-t border-white/10">
              <div className="text-xs text-white/50 uppercase">Export</div>
              <div className="grid grid-cols-2 gap-2">
                <a
                  href="/data/anna-matrix.json"
                  download
                  className="flex items-center justify-center gap-2 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-white/80 hover:text-white"
                >
                  <Download className="w-4 h-4" />
                  JSON
                </a>
                <button
                  onClick={() => {
                    const csv = matrix.map((row) => row.join(',')).join('\n')
                    const blob = new Blob([csv], { type: 'text/csv' })
                    const url = URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = 'anna-matrix.csv'
                    a.click()
                    URL.revokeObjectURL(url)
                  }}
                  className="flex items-center justify-center gap-2 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-white/80 hover:text-white"
                >
                  <Download className="w-4 h-4" />
                  CSV
                </button>
              </div>
            </div>

            {/* Python Code Example */}
            <div className="space-y-2 pt-4 border-t border-white/10">
              <div className="text-xs text-white/50 uppercase">Python Example</div>
              <pre className="bg-black/50 border border-white/10 rounded-lg p-3 text-xs font-mono text-green-400 overflow-x-auto">
{`import requests
import numpy as np

# Fetch matrix
url = "https://qubicchurch.com/api/research/anna-matrix?format=full"
data = requests.get(url).json()
matrix = np.array(data['matrix'])

# Analyze
print(f"Shape: {matrix.shape}")
print(f"Mean: {matrix.mean():.2f}")
print(f"Row 21 sum: {matrix[21].sum()}")`}
              </pre>
            </div>
          </>
        )}
      </div>

      {/* Selected Cell Quick Info */}
      {selectedCell && (
        <div className="px-4 py-2 border-t border-white/10 bg-black/50">
          <div className="flex items-center justify-between text-xs">
            <span className="text-white/50">Selected:</span>
            <span className="font-mono text-white">
              [{selectedCell.row}, {selectedCell.col}] = {selectedCell.value}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
