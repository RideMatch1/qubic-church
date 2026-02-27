'use client'

import { ExternalLink } from 'lucide-react'

interface OracleInfoProps {
  tick: number
  epoch: number
}

export function OracleInfo({ tick, epoch }: OracleInfoProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-xs text-zinc-500 uppercase tracking-wider">Oracle Machine</span>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-medium">
          v1.278.0
        </span>
      </div>

      {/* Status */}
      <div className="grid grid-cols-2 gap-2">
        <div className="p-2 bg-zinc-800/30 rounded">
          <div className="text-[10px] text-zinc-600">Launched</div>
          <div className="text-xs font-mono text-zinc-300">Feb 11, 2026</div>
        </div>
        <div className="p-2 bg-zinc-800/30 rounded">
          <div className="text-[10px] text-zinc-600">Computors</div>
          <div className="text-xs font-mono text-zinc-300">676 required</div>
        </div>
        <div className="p-2 bg-zinc-800/30 rounded">
          <div className="text-[10px] text-zinc-600">Quorum</div>
          <div className="text-xs font-mono text-zinc-300">451 of 676</div>
        </div>
        <div className="p-2 bg-zinc-800/30 rounded">
          <div className="text-[10px] text-zinc-600">Query Cost</div>
          <div className="text-xs font-mono text-zinc-300">10 QU (burned)</div>
        </div>
      </div>

      {/* Price Feeds */}
      <div>
        <div className="text-[10px] text-zinc-600 mb-1.5">Supported Price Feeds</div>
        <div className="flex gap-1.5 flex-wrap">
          {['Binance', 'MEXC', 'Gate.io'].map((feed) => (
            <span
              key={feed}
              className="text-[10px] px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 border border-zinc-700/50"
            >
              {feed}
            </span>
          ))}
        </div>
      </div>

      {/* Consensus */}
      <div>
        <div className="text-[10px] text-zinc-600 mb-1.5">Consensus Pattern</div>
        <div className="flex items-center gap-2 text-[10px]">
          <span className="px-2 py-1 bg-cyan-500/10 text-cyan-400 rounded font-mono">Commit</span>
          <span className="text-zinc-600">&rarr;</span>
          <span className="px-2 py-1 bg-cyan-500/10 text-cyan-400 rounded font-mono">Reveal</span>
          <span className="text-zinc-600">&rarr;</span>
          <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded font-mono">Finalize</span>
        </div>
      </div>

      {/* Live Network */}
      {tick > 0 && (
        <div className="p-2 bg-zinc-800/30 rounded border border-zinc-700/30">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-zinc-600">Current Tick</span>
            <span className="text-xs font-mono text-zinc-300">{tick.toLocaleString()}</span>
          </div>
          <div className="flex items-center justify-between mt-1">
            <span className="text-[10px] text-zinc-600">Epoch</span>
            <span className="text-xs font-mono text-zinc-300">{epoch}</span>
          </div>
        </div>
      )}

      {/* CLI Info */}
      <div className="p-2 bg-zinc-800/30 rounded">
        <div className="text-[10px] text-zinc-600 mb-1">CLI Commands</div>
        <div className="space-y-0.5">
          <code className="text-[10px] text-cyan-400/70 font-mono block">-queryoracle [IF] [QUERY] [TIMEOUT]</code>
          <code className="text-[10px] text-cyan-400/70 font-mono block">-getoraclequery</code>
        </div>
      </div>

      {/* Links */}
      <div className="flex gap-2">
        <a
          href="https://github.com/qubic/oracle-machine"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-[10px] text-zinc-500 hover:text-cyan-400 transition-colors"
        >
          Oracle Machine <ExternalLink className="w-2.5 h-2.5" />
        </a>
        <a
          href="https://github.com/qubic/qubic-cli"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-[10px] text-zinc-500 hover:text-cyan-400 transition-colors"
        >
          qubic-cli <ExternalLink className="w-2.5 h-2.5" />
        </a>
      </div>
    </div>
  )
}
