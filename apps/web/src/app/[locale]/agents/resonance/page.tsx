'use client'

import { useState, useCallback } from 'react'

type Mode = 'oracle' | 'single' | 'compare' | 'batch'

interface OracleResult {
  question: string
  answer: 'YES' | 'NO' | 'UNCERTAIN'
  confidence: number
  reasoning: {
    energy: number
    convergence: string
    pattern: string
  }
  hash: string
}

interface SingleResult {
  input: string
  inputType: string
  normalizedEnergy: number
  ticks: number
  endReason: string
  resonance: string
  convergenceQuality: string
  outputHash: string
  distribution: { positive: number; neutral: number; negative: number }
}

interface CompareResult {
  verdict: string
  outputSimilarity: number
  energyDifference: number
  matchingOutputs: number
  totalOutputs: number
  inputA: SingleResult
  inputB: SingleResult
}

interface BatchResult {
  statistics: {
    avgEnergy: number
    avgTicks: number
    strongPositive: number
    positive: number
    neutral: number
    negative: number
    strongNegative: number
  }
  ranked: Array<{ input: string; energy: number; rank: number }>
}

export default function ResonancePage() {
  const [mode, setMode] = useState<Mode>('oracle')
  const [input, setInput] = useState('')
  const [inputA, setInputA] = useState('')
  const [inputB, setInputB] = useState('')
  const [batchInput, setBatchInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<OracleResult | SingleResult | CompareResult | BatchResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [durationMs, setDurationMs] = useState<number>(0)

  const compute = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      let body: Record<string, unknown> = { mode }

      switch (mode) {
        case 'oracle':
          body.question = input
          break
        case 'single':
          body.input = input
          break
        case 'compare':
          body.inputA = inputA
          body.inputB = inputB
          break
        case 'batch':
          body.inputs = batchInput.split('\n').filter(s => s.trim())
          break
      }

      const response = await fetch('/api/agents/resonance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed')
      }

      setResult(data.data)
      setDurationMs(data.durationMs)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }, [mode, input, inputA, inputB, batchInput])

  return (
    <div className="min-h-screen bg-black text-zinc-100 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <header className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-4 py-1 bg-cyan-500/10 border border-cyan-500/30 rounded-full text-cyan-400 text-xs font-mono">
            <span className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
            TERNARY COMPUTING
          </div>
          <h1 className="text-3xl font-mono">
            <span className="text-cyan-400">Resonance</span> Engine
          </h1>
          <p className="text-zinc-500 text-sm font-mono">
            Echte Berechnung durch die 128×128 Anna Matrix
          </p>
        </header>

        {/* Mode Selection */}
        <div className="flex justify-center gap-2 flex-wrap">
          {(['oracle', 'single', 'compare', 'batch'] as Mode[]).map(m => (
            <button
              key={m}
              type="button"
              onClick={() => { setMode(m); setResult(null) }}
              className={`px-4 py-2 rounded-lg border text-sm font-mono transition-all ${
                mode === m
                  ? 'border-cyan-500 bg-cyan-500/20 text-cyan-400'
                  : 'border-zinc-800 text-zinc-500 hover:border-zinc-700'
              }`}
            >
              {m === 'oracle' && '🔮 Oracle'}
              {m === 'single' && '📊 Single'}
              {m === 'compare' && '⚖️ Compare'}
              {m === 'batch' && '📋 Batch'}
            </button>
          ))}
        </div>

        {/* Input Section */}
        <div className="space-y-4">
          {mode === 'oracle' && (
            <div>
              <label className="block text-xs font-mono text-zinc-500 mb-2">
                FRAGE (Ja/Nein)
              </label>
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Is CFB Satoshi Nakamoto?"
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 font-mono text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-cyan-500"
              />
            </div>
          )}

          {mode === 'single' && (
            <div>
              <label className="block text-xs font-mono text-zinc-500 mb-2">
                INPUT (Text, Bitcoin Address, oder Hex)
              </label>
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 font-mono text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-cyan-500"
              />
            </div>
          )}

          {mode === 'compare' && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono text-zinc-500 mb-2">INPUT A</label>
                <input
                  type="text"
                  value={inputA}
                  onChange={e => setInputA(e.target.value)}
                  placeholder="First input..."
                  className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 font-mono text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-xs font-mono text-zinc-500 mb-2">INPUT B</label>
                <input
                  type="text"
                  value={inputB}
                  onChange={e => setInputB(e.target.value)}
                  placeholder="Second input..."
                  className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 font-mono text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          )}

          {mode === 'batch' && (
            <div>
              <label className="block text-xs font-mono text-zinc-500 mb-2">
                INPUTS (einer pro Zeile, max 50)
              </label>
              <textarea
                value={batchInput}
                onChange={e => setBatchInput(e.target.value)}
                placeholder={"1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa\n12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX\n1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1"}
                rows={6}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 font-mono text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-cyan-500"
              />
            </div>
          )}

          <button
            type="button"
            onClick={compute}
            disabled={isLoading}
            className="w-full bg-cyan-500 hover:bg-cyan-400 disabled:bg-zinc-800 text-black font-mono font-bold py-3 rounded-lg transition-all"
          >
            {isLoading ? 'COMPUTING...' : 'COMPUTE RESONANCE'}
          </button>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 font-mono text-sm">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
              <span className="text-xs font-mono text-zinc-500">RESULT</span>
              <span className="text-xs font-mono text-zinc-600">{durationMs}ms</span>
            </div>

            {mode === 'oracle' && (
              <OracleResultView result={result as OracleResult} />
            )}

            {mode === 'single' && (
              <SingleResultView result={result as SingleResult} />
            )}

            {mode === 'compare' && (
              <CompareResultView result={result as CompareResult} />
            )}

            {mode === 'batch' && (
              <BatchResultView result={result as BatchResult} />
            )}
          </div>
        )}

        {/* How it works */}
        <div className="text-xs font-mono text-zinc-600 space-y-1">
          <p className="text-zinc-500 font-bold">WIE ES FUNKTIONIERT:</p>
          <p>1. Input → SHA256 → 64 Ternary-Werte (-1, 0, +1)</p>
          <p>2. Tick-Loop durch 128×128 Anna Matrix</p>
          <p>3. Neuronen berechnen gewichtete Summen</p>
          <p>4. Konvergenz oder max 500 Ticks</p>
          <p>5. Energy bestimmt Resonance</p>
          <p className="text-cyan-400 mt-2">100% deterministisch • Gleicher Input = Gleicher Output</p>
        </div>
      </div>
    </div>
  )
}

function OracleResultView({ result }: { result: OracleResult }) {
  const answerColors = {
    YES: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/50',
    NO: 'text-red-400 bg-red-500/20 border-red-500/50',
    UNCERTAIN: 'text-amber-400 bg-amber-500/20 border-amber-500/50',
  }

  return (
    <div className="p-6 space-y-6">
      <div className="text-center">
        <div className={`inline-block px-8 py-4 rounded-xl border-2 text-4xl font-mono font-bold ${answerColors[result.answer]}`}>
          {result.answer}
        </div>
        <div className="mt-4 text-zinc-500 font-mono">
          Confidence: {(result.confidence * 100).toFixed(0)}%
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 text-center">
        <div className="bg-black/30 rounded-lg p-3">
          <div className={`text-xl font-mono font-bold ${result.reasoning.energy > 0 ? 'text-emerald-400' : result.reasoning.energy < 0 ? 'text-red-400' : 'text-zinc-400'}`}>
            {result.reasoning.energy > 0 ? '+' : ''}{result.reasoning.energy.toFixed(3)}
          </div>
          <div className="text-xs font-mono text-zinc-500">Energy</div>
        </div>
        <div className="bg-black/30 rounded-lg p-3">
          <div className="text-xl font-mono font-bold text-zinc-300">
            {result.reasoning.convergence.split(' ')[0]}
          </div>
          <div className="text-xs font-mono text-zinc-500">Ticks</div>
        </div>
        <div className="bg-black/30 rounded-lg p-3">
          <div className="text-sm font-mono text-cyan-400 break-all">
            {result.hash}
          </div>
          <div className="text-xs font-mono text-zinc-500">Hash</div>
        </div>
      </div>

      <div className="text-xs font-mono text-zinc-600 text-center">
        Pattern: {result.reasoning.pattern}
      </div>
    </div>
  )
}

function SingleResultView({ result }: { result: SingleResult }) {
  const energyColor = result.normalizedEnergy > 0.15 ? 'text-emerald-400' :
                      result.normalizedEnergy < -0.15 ? 'text-red-400' : 'text-zinc-400'

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs font-mono text-zinc-500">TYPE</div>
          <div className="text-sm font-mono text-zinc-300">{result.inputType}</div>
        </div>
        <div className="text-right">
          <div className="text-xs font-mono text-zinc-500">RESONANCE</div>
          <div className={`text-lg font-mono font-bold ${
            result.resonance === 'strong_positive' ? 'text-emerald-400' :
            result.resonance === 'positive' ? 'text-emerald-300' :
            result.resonance === 'negative' ? 'text-red-300' :
            result.resonance === 'strong_negative' ? 'text-red-400' : 'text-zinc-400'
          }`}>
            {result.resonance.replace('_', ' ').toUpperCase()}
          </div>
        </div>
      </div>

      <div className="bg-black/30 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-mono text-zinc-500">ENERGY</span>
          <span className={`text-2xl font-mono font-bold ${energyColor}`}>
            {result.normalizedEnergy > 0 ? '+' : ''}{(result.normalizedEnergy * 100).toFixed(1)}%
          </span>
        </div>
        <div className="h-4 bg-zinc-800 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all ${result.normalizedEnergy > 0 ? 'bg-emerald-500' : 'bg-red-500'}`}
            style={{
              width: `${Math.abs(result.normalizedEnergy) * 100}%`,
              marginLeft: result.normalizedEnergy < 0 ? 'auto' : 0,
            }}
          />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 text-center text-xs font-mono">
        <div>
          <div className="text-zinc-300">{result.ticks}</div>
          <div className="text-zinc-500">Ticks</div>
        </div>
        <div>
          <div className="text-zinc-300">{result.endReason}</div>
          <div className="text-zinc-500">End</div>
        </div>
        <div>
          <div className="text-zinc-300">{result.convergenceQuality}</div>
          <div className="text-zinc-500">Quality</div>
        </div>
        <div>
          <div className="text-cyan-400">{result.outputHash}</div>
          <div className="text-zinc-500">Hash</div>
        </div>
      </div>

      <div className="flex justify-center gap-4 text-xs font-mono">
        <span className="text-emerald-400">+{result.distribution.positive}</span>
        <span className="text-zinc-500">0:{result.distribution.neutral}</span>
        <span className="text-red-400">-{result.distribution.negative}</span>
      </div>
    </div>
  )
}

function CompareResultView({ result }: { result: CompareResult }) {
  const verdictColors = {
    very_similar: 'text-emerald-400',
    similar: 'text-emerald-300',
    different: 'text-amber-400',
    opposite: 'text-red-400',
  }

  return (
    <div className="p-6 space-y-6">
      <div className="text-center">
        <div className={`text-2xl font-mono font-bold ${verdictColors[result.verdict as keyof typeof verdictColors]}`}>
          {result.verdict.replace('_', ' ').toUpperCase()}
        </div>
        <div className="text-zinc-500 font-mono text-sm mt-1">
          {(result.outputSimilarity * 100).toFixed(1)}% similarity ({result.matchingOutputs}/{result.totalOutputs} matching)
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-black/30 rounded-lg p-4">
          <div className="text-xs font-mono text-zinc-500 mb-2">INPUT A</div>
          <div className={`text-xl font-mono font-bold ${result.inputA.normalizedEnergy > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {result.inputA.normalizedEnergy > 0 ? '+' : ''}{(result.inputA.normalizedEnergy * 100).toFixed(1)}%
          </div>
          <div className="text-xs font-mono text-zinc-500 mt-1">{result.inputA.resonance}</div>
        </div>
        <div className="bg-black/30 rounded-lg p-4">
          <div className="text-xs font-mono text-zinc-500 mb-2">INPUT B</div>
          <div className={`text-xl font-mono font-bold ${result.inputB.normalizedEnergy > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {result.inputB.normalizedEnergy > 0 ? '+' : ''}{(result.inputB.normalizedEnergy * 100).toFixed(1)}%
          </div>
          <div className="text-xs font-mono text-zinc-500 mt-1">{result.inputB.resonance}</div>
        </div>
      </div>

      <div className="text-center text-xs font-mono text-zinc-600">
        Energy difference: {(result.energyDifference * 100).toFixed(1)}%
      </div>
    </div>
  )
}

function BatchResultView({ result }: { result: BatchResult }) {
  return (
    <div className="p-6 space-y-6">
      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4 text-center">
        <div className="bg-emerald-500/10 rounded-lg p-3">
          <div className="text-xl font-mono font-bold text-emerald-400">
            {result.statistics.strongPositive + result.statistics.positive}
          </div>
          <div className="text-xs font-mono text-zinc-500">Positive</div>
        </div>
        <div className="bg-zinc-500/10 rounded-lg p-3">
          <div className="text-xl font-mono font-bold text-zinc-400">
            {result.statistics.neutral}
          </div>
          <div className="text-xs font-mono text-zinc-500">Neutral</div>
        </div>
        <div className="bg-red-500/10 rounded-lg p-3">
          <div className="text-xl font-mono font-bold text-red-400">
            {result.statistics.negative + result.statistics.strongNegative}
          </div>
          <div className="text-xs font-mono text-zinc-500">Negative</div>
        </div>
        <div className="bg-cyan-500/10 rounded-lg p-3">
          <div className="text-xl font-mono font-bold text-cyan-400">
            {(result.statistics.avgEnergy * 100).toFixed(1)}%
          </div>
          <div className="text-xs font-mono text-zinc-500">Avg Energy</div>
        </div>
      </div>

      {/* Ranking */}
      <div>
        <div className="text-xs font-mono text-zinc-500 mb-2">RANKING BY ENERGY</div>
        <div className="space-y-1 max-h-80 overflow-y-auto">
          {result.ranked.map((item, i) => (
            <div
              key={i}
              className={`flex items-center justify-between p-2 rounded ${
                i < 3 ? 'bg-emerald-500/10' : i >= result.ranked.length - 3 ? 'bg-red-500/10' : 'bg-zinc-800/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className={`w-6 text-xs font-mono ${
                  i < 3 ? 'text-emerald-400' : 'text-zinc-500'
                }`}>
                  #{item.rank}
                </span>
                <span className="text-sm font-mono text-zinc-300 truncate max-w-[300px]">
                  {item.input}
                </span>
              </div>
              <span className={`text-sm font-mono font-bold ${
                item.energy > 0.1 ? 'text-emerald-400' :
                item.energy < -0.1 ? 'text-red-400' : 'text-zinc-400'
              }`}>
                {item.energy > 0 ? '+' : ''}{(item.energy * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
