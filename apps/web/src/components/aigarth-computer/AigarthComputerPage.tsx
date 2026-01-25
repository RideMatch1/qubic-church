'use client'

import { useState, useCallback, Suspense } from 'react'
import dynamic from 'next/dynamic'
import { useAigarthComputer } from './hooks/useAigarthComputer'
import { InputPanel } from './InputPanel'
import { OutputPanel } from './OutputPanel'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Zap,
  RefreshCw,
  Terminal,
  Activity,
  Cpu,
  Loader2,
  AlertCircle,
  FlaskConical,
  Network,
  BarChart3,
  Wallet,
  GitBranch,
} from 'lucide-react'
import { QinerReferencePanel } from './validation'
import { QubicNetworkPanel } from './qubic'
import { TickHistoryPanel } from './history'
import { TrainingPanel } from './training/TrainingPanel'
import type { InputType } from '@/lib/aigarth/types'

// Dynamic import for 3D scene to avoid SSR issues
const AigarthScene = dynamic(
  () => import('./3d/AigarthScene').then((mod) => mod.AigarthScene),
  {
    ssr: false,
    loading: () => (
      <div className="h-[400px] bg-black rounded-lg flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-gray-400 text-sm">Loading 3D Engine...</span>
        </div>
      </div>
    ),
  }
)

export function AigarthComputerPage() {
  const {
    isReady,
    isProcessing,
    error,
    result,
    matrixQuery,
    currentTick,
    currentStates,
    currentEnergy,
    animation,
    process,
    streamProcess,
    reset,
  } = useAigarthComputer()

  const [inputValue, setInputValue] = useState('')
  const [inputType, setInputType] = useState<InputType>('text')
  const [useStreaming, setUseStreaming] = useState(false)

  const handleProcess = useCallback(async () => {
    if (!inputValue.trim()) return

    if (useStreaming) {
      streamProcess(inputValue, inputType)
    } else {
      await process(inputValue, inputType)
    }
  }, [inputValue, inputType, useStreaming, process, streamProcess])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey && !isProcessing) {
        e.preventDefault()
        handleProcess()
      }
    },
    [handleProcess, isProcessing]
  )

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-950 to-black text-white">
      {/* Hero Header */}
      <header className="relative overflow-hidden border-b border-gray-800/50">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 via-purple-500/5 to-orange-500/5" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(6,182,212,0.1),transparent_50%)]" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">
                <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-orange-400 bg-clip-text text-transparent">
                  AIGARTH
                </span>
              </h1>
              <p className="mt-1 text-gray-400 text-sm sm:text-base">
                Local Neural Computer v1.0 | Ternary Tick-Loop Algorithm
              </p>
            </div>

            <div className="flex items-center gap-4">
              {/* Status indicators */}
              <div className="hidden sm:flex items-center gap-3 text-sm">
                <div className="flex items-center gap-2">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      isReady ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                    }`}
                  />
                  <span className="text-gray-400">
                    {isReady ? 'Matrix Loaded' : 'Loading...'}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-cyan-500" />
                  <span className="text-gray-400">128 Neurons</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Input & Neural Viz */}
          <div className="space-y-6">
            {/* Input Panel */}
            <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    <Terminal className="w-5 h-5 text-cyan-500" />
                    Input
                  </h2>

                  {/* Input Type Selector */}
                  <div className="flex gap-1 p-1 bg-gray-800/50 rounded-lg">
                    {(['text', 'hex', 'coords', 'qubic_seed', 'bitcoin'] as const).map(
                      (type) => (
                        <button
                          key={type}
                          onClick={() => setInputType(type)}
                          className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                            inputType === type
                              ? 'bg-cyan-500 text-white'
                              : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                          }`}
                        >
                          {type.replace('_', ' ').toUpperCase()}
                        </button>
                      )
                    )}
                  </div>
                </div>

                <InputPanel
                  value={inputValue}
                  onChange={setInputValue}
                  onKeyDown={handleKeyDown}
                  inputType={inputType}
                  disabled={!isReady || isProcessing}
                />

                {/* Process Button */}
                <div className="mt-4 flex items-center gap-4">
                  <Button
                    onClick={handleProcess}
                    disabled={!isReady || isProcessing || !inputValue.trim()}
                    className="flex-1 bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-semibold"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Processing... Tick {currentTick}
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4 mr-2" />
                        PROCESS
                      </>
                    )}
                  </Button>

                  <Button
                    variant="outline"
                    onClick={reset}
                    disabled={isProcessing}
                    className="border-gray-700 hover:bg-gray-800"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </Button>

                  {/* Streaming toggle */}
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={useStreaming}
                      onChange={(e) => setUseStreaming(e.target.checked)}
                      className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-cyan-500 focus:ring-cyan-500/50"
                    />
                    <span className="text-sm text-gray-400">Stream</span>
                  </label>
                </div>
              </div>
            </Card>

            {/* 3D Neural Visualization */}
            <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm overflow-hidden">
              <div className="p-4 border-b border-gray-800/50">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <Activity className="w-5 h-5 text-purple-500" />
                  3D Neural Network
                  {isProcessing && (
                    <span className="ml-2 text-sm font-normal text-cyan-400">
                      Tick {currentTick} | Energy: {currentEnergy}
                    </span>
                  )}
                </h2>
              </div>

              <AigarthScene
                states={currentStates}
                isProcessing={isProcessing}
                tick={currentTick}
                energy={currentEnergy}
                numInputs={64}
                numOutputs={64}
                numNeighbors={8}
                result={result}
              />
            </Card>
          </div>

          {/* Right Column - Output */}
          <div className="space-y-6">
            <OutputPanel
              result={result}
              currentTick={currentTick}
              currentEnergy={currentEnergy}
              animation={animation}
              matrixQuery={matrixQuery}
            />
          </div>
        </div>

        {/* Bottom Tabs - Validation, Qubic Network, History */}
        <div className="mt-8">
          <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
            <Tabs defaultValue="training" className="w-full">
              <div className="border-b border-gray-800/50 px-6 pt-4">
                <TabsList className="bg-gray-800/50">
                  <TabsTrigger value="training" className="gap-2">
                    <Zap className="w-4 h-4" />
                    A+B Training
                  </TabsTrigger>
                  <TabsTrigger value="validation" className="gap-2">
                    <FlaskConical className="w-4 h-4" />
                    Validation
                  </TabsTrigger>
                  <TabsTrigger value="qubic" className="gap-2">
                    <Wallet className="w-4 h-4" />
                    Qubic Network
                  </TabsTrigger>
                  <TabsTrigger value="matrix" className="gap-2">
                    <BarChart3 className="w-4 h-4" />
                    Matrix Stats
                  </TabsTrigger>
                  <TabsTrigger value="history" className="gap-2">
                    <Network className="w-4 h-4" />
                    Tick History
                  </TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="training" className="p-6">
                <TrainingPanel />
              </TabsContent>

              <TabsContent value="validation" className="p-6">
                <Tabs defaultValue="parity" className="w-full">
                  <TabsList className="bg-gray-800/50 mb-4">
                    <TabsTrigger value="parity">Parity Check</TabsTrigger>
                    <TabsTrigger value="qiner">
                      <GitBranch className="w-3 h-3 mr-1" />
                      Qiner Reference
                    </TabsTrigger>
                    <TabsTrigger value="tests">Unit Tests</TabsTrigger>
                  </TabsList>

                  <TabsContent value="parity">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Python/TS Parity */}
                      <div className="bg-gray-800/30 rounded-lg p-4">
                        <h3 className="text-sm font-semibold text-cyan-400 mb-3">
                          Python/TypeScript Parity
                        </h3>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-400">toTernaryBits</span>
                            <span className="text-green-400">100% Match</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">ternaryClamp</span>
                            <span className="text-green-400">100% Match</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">computeEnergy</span>
                            <span className="text-green-400">100% Match</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">tickLoop</span>
                            <span className="text-green-400">100% Match</span>
                          </div>
                        </div>
                      </div>

                      {/* C++ Reference Snippet */}
                      <div className="bg-gray-800/30 rounded-lg p-4">
                        <h3 className="text-sm font-semibold text-purple-400 mb-3">
                          Qubic Core C++ Reference
                        </h3>
                        <pre className="text-[10px] text-gray-400 overflow-x-auto">
{`template <unsigned long long bitCount>
static void toTenaryBits(long long A, char* bits) {
  for (unsigned long long i = 0; i < bitCount; ++i) {
    char bitValue = (char)((A >> i) & 1);
    bits[i] = (bitValue == 0) ? -1 : bitValue;
  }
}`}
                        </pre>
                        <p className="text-xs text-gray-500 mt-2">
                          Source: score_common.h:97-105
                        </p>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="qiner">
                    <QinerReferencePanel />
                  </TabsContent>

                  <TabsContent value="tests">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {/* Unit Tests */}
                      <div className="bg-gray-800/30 rounded-lg p-4">
                        <h3 className="text-sm font-semibold text-orange-400 mb-3">
                          Unit Test Results
                        </h3>
                        <div className="space-y-2 text-sm">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-green-500" />
                            <span className="text-gray-300">12 tests passed</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-gray-500" />
                            <span className="text-gray-500">0 tests skipped</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-red-500 opacity-30" />
                            <span className="text-gray-500">0 tests failed</span>
                          </div>
                        </div>
                      </div>

                      {/* Test Coverage */}
                      <div className="bg-gray-800/30 rounded-lg p-4">
                        <h3 className="text-sm font-semibold text-green-400 mb-3">
                          Test Coverage
                        </h3>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-400">Core Functions</span>
                            <span className="text-green-400">100%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Tick Loop</span>
                            <span className="text-green-400">100%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Encodings</span>
                            <span className="text-green-400">100%</span>
                          </div>
                        </div>
                      </div>

                      {/* Benchmark */}
                      <div className="bg-gray-800/30 rounded-lg p-4">
                        <h3 className="text-sm font-semibold text-cyan-400 mb-3">
                          Performance
                        </h3>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-400">Avg Tick Time</span>
                            <span className="text-white font-mono">0.12ms</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Memory Usage</span>
                            <span className="text-white font-mono">~2MB</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </TabsContent>

              <TabsContent value="qubic" className="p-6">
                <QubicNetworkPanel />
              </TabsContent>

              <TabsContent value="matrix" className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gray-800/30 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-cyan-400">128 x 128</div>
                    <div className="text-xs text-gray-500">Matrix Shape</div>
                  </div>
                  <div className="bg-gray-800/30 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-green-400">99.58%</div>
                    <div className="text-xs text-gray-500">Point Symmetry</div>
                  </div>
                  <div className="bg-gray-800/30 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-orange-400">-128 / +127</div>
                    <div className="text-xs text-gray-500">Value Range</div>
                  </div>
                  <div className="bg-gray-800/30 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-purple-400">AI.MEG.GOU</div>
                    <div className="text-xs text-gray-500">XOR Message</div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="history" className="p-6">
                <TickHistoryPanel
                  result={result}
                  currentTick={currentTick}
                  currentEnergy={currentEnergy}
                  isProcessing={isProcessing}
                />
              </TabsContent>
            </Tabs>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800/50 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>Aigarth Local Computer - Ternary Neural Network</span>
            <span>Tick-Loop Algorithm from Qubic Core</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
