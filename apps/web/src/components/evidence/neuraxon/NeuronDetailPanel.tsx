'use client'

import { Button } from '@/components/ui/button'
import { Copy, Check, ExternalLink, X, ArrowRight, ArrowLeft, Zap, Activity, Box } from 'lucide-react'
import { useState } from 'react'
import type { NeuraxonNode, NeuraxonEdge } from './types'

interface NeuronDetailPanelProps {
  node: NeuraxonNode
  connections: { incoming: NeuraxonEdge[]; outgoing: NeuraxonEdge[] }
  getNodeById: (id: number) => NeuraxonNode | undefined
  onClose: () => void
  onNodeClick: (node: NeuraxonNode) => void
}

// State display helpers
const STATE_CONFIG = {
  '-1': {
    label: 'Negative',
    color: 'bg-blue-500',
    textColor: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    glowColor: 'shadow-blue-500/20',
  },
  '0': {
    label: 'Neutral',
    color: 'bg-gray-500',
    textColor: 'text-gray-400',
    bgColor: 'bg-gray-500/10',
    borderColor: 'border-gray-500/30',
    glowColor: 'shadow-gray-500/20',
  },
  '1': {
    label: 'Positive',
    color: 'bg-orange-500',
    textColor: 'text-orange-400',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30',
    glowColor: 'shadow-orange-500/20',
  },
}

const TYPE_CONFIG = {
  input: { label: 'Input Layer', icon: ArrowRight, color: 'text-green-400' },
  hidden: { label: 'Hidden Layer', icon: Activity, color: 'text-purple-400' },
  output: { label: 'Output Layer', icon: ArrowLeft, color: 'text-red-400' },
}

const SYNAPSE_COLORS = {
  fast: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/30' },
  slow: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/30' },
  meta: { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500/30' },
}

export function NeuronDetailPanel({
  node,
  connections,
  getNodeById,
  onClose,
  onNodeClick,
}: NeuronDetailPanelProps) {
  const [copiedField, setCopiedField] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'info' | 'connections'>('info')

  const handleCopy = async (text: string, field: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  const stateConfig = STATE_CONFIG[String(node.state) as keyof typeof STATE_CONFIG]
  const typeConfig = TYPE_CONFIG[node.type]
  const TypeIcon = typeConfig.icon

  // Sort connections by weight
  const sortedOutgoing = [...connections.outgoing].sort((a, b) => b.weight - a.weight).slice(0, 8)
  const sortedIncoming = [...connections.incoming].sort((a, b) => b.weight - a.weight).slice(0, 8)

  return (
    <div className="absolute top-4 right-4 w-[340px] bg-black/95 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden pointer-events-auto">
      {/* Header with gradient */}
      <div className={`relative p-4 ${stateConfig.bgColor} border-b ${stateConfig.borderColor}`}>
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '16px 16px'
          }} />
        </div>

        <div className="relative flex items-start justify-between">
          <div className="flex items-center gap-3">
            {/* State indicator with glow */}
            <div className={`w-12 h-12 rounded-xl ${stateConfig.color} flex items-center justify-center shadow-lg ${stateConfig.glowColor}`}>
              <span className="text-white font-bold text-lg">
                {node.state > 0 ? '+1' : node.state < 0 ? '-1' : '0'}
              </span>
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-white text-lg">Neuron #{node.id}</h3>
              </div>
              <div className="flex items-center gap-2 mt-0.5">
                <TypeIcon className={`w-3 h-3 ${typeConfig.color}`} />
                <span className={`text-xs ${typeConfig.color}`}>{typeConfig.label}</span>
              </div>
            </div>
          </div>

          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8 text-white/50 hover:text-white hover:bg-white/10 rounded-lg"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* State badge */}
        <div className={`inline-flex items-center gap-1.5 mt-3 px-3 py-1.5 rounded-full ${stateConfig.bgColor} border ${stateConfig.borderColor}`}>
          <Zap className={`w-3 h-3 ${stateConfig.textColor}`} />
          <span className={`text-xs font-medium ${stateConfig.textColor}`}>
            {stateConfig.label} State
          </span>
        </div>
      </div>

      {/* Tab navigation */}
      <div className="flex border-b border-white/10">
        <button
          onClick={() => setActiveTab('info')}
          className={`flex-1 px-4 py-2.5 text-xs font-medium transition-colors ${
            activeTab === 'info'
              ? 'text-white bg-white/5 border-b-2 border-white'
              : 'text-white/50 hover:text-white hover:bg-white/5'
          }`}
        >
          Identity
        </button>
        <button
          onClick={() => setActiveTab('connections')}
          className={`flex-1 px-4 py-2.5 text-xs font-medium transition-colors ${
            activeTab === 'connections'
              ? 'text-white bg-white/5 border-b-2 border-white'
              : 'text-white/50 hover:text-white hover:bg-white/5'
          }`}
        >
          Connections ({connections.outgoing.length + connections.incoming.length})
        </button>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4 max-h-[400px] overflow-y-auto custom-scrollbar">
        {activeTab === 'info' ? (
          <>
            {/* Seed */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-[10px] text-white/40 uppercase tracking-wider font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-orange-500" />
                Private Seed (55 chars)
              </label>
              <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-lg p-2.5 group hover:border-white/20 transition-colors">
                <code className="flex-1 text-xs font-mono text-white/80 truncate">
                  {node.seed}
                </code>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 shrink-0 text-white/40 hover:text-white hover:bg-white/10"
                  onClick={() => handleCopy(node.seed, 'seed')}
                >
                  {copiedField === 'seed' ? (
                    <Check className="w-3.5 h-3.5 text-green-500" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </Button>
              </div>
            </div>

            {/* Real ID */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-[10px] text-white/40 uppercase tracking-wider font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                Public Identity (60 chars)
              </label>
              <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-lg p-2.5 group hover:border-white/20 transition-colors">
                <code className="flex-1 text-xs font-mono text-white/80 truncate">
                  {node.realId}
                </code>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 shrink-0 text-white/40 hover:text-white hover:bg-white/10"
                  onClick={() => handleCopy(node.realId, 'realId')}
                >
                  {copiedField === 'realId' ? (
                    <Check className="w-3.5 h-3.5 text-green-500" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </Button>
                <a
                  href={`https://explorer.qubic.org/network/address/${node.realId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-white/40 hover:text-blue-400 hover:bg-blue-500/10"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Button>
                </a>
              </div>
            </div>

            {/* Stats grid */}
            <div className="grid grid-cols-2 gap-3">
              {/* Position */}
              <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <Box className="w-3 h-3 text-white/40" />
                  <span className="text-[10px] text-white/40 uppercase tracking-wider">Position</span>
                </div>
                <div className="text-xs font-mono text-white/80">
                  [{node.position.map((v) => v.toFixed(1)).join(', ')}]
                </div>
              </div>

              {/* Frame */}
              <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <Activity className="w-3 h-3 text-white/40" />
                  <span className="text-[10px] text-white/40 uppercase tracking-wider">Frame</span>
                </div>
                <div className="text-xs text-white/80">
                  <span className="font-semibold">{node.frame + 1}</span>
                  <span className="text-white/40"> / 47</span>
                </div>
              </div>
            </div>

            {/* Quick view button */}
            <a
              href={`https://explorer.qubic.org/network/address/${node.realId}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white text-sm font-medium rounded-lg transition-all hover:shadow-lg hover:shadow-blue-500/20"
            >
              <ExternalLink className="w-4 h-4" />
              View on Qubic Explorer
            </a>
          </>
        ) : (
          <>
            {/* Connection summary */}
            <div className="flex items-center justify-center gap-6 py-2">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">{connections.outgoing.length}</div>
                <div className="text-[10px] text-white/40 uppercase tracking-wider">Outgoing</div>
              </div>
              <div className="w-px h-8 bg-white/10" />
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">{connections.incoming.length}</div>
                <div className="text-[10px] text-white/40 uppercase tracking-wider">Incoming</div>
              </div>
            </div>

            {/* Outgoing connections */}
            {sortedOutgoing.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <ArrowRight className="w-3 h-3 text-green-400" />
                  <span className="text-xs font-medium text-white/60">
                    Outgoing Synapses
                  </span>
                </div>
                <div className="space-y-1.5">
                  {sortedOutgoing.map((edge, i) => {
                    const targetNode = getNodeById(edge.target)
                    const synapseColor = SYNAPSE_COLORS[edge.type]
                    return (
                      <button
                        key={i}
                        className="flex items-center gap-2 w-full text-left text-xs bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/10 rounded-lg p-2 transition-all group"
                        onClick={() => targetNode && onNodeClick(targetNode)}
                      >
                        <ArrowRight className="w-3 h-3 text-green-400/50 group-hover:text-green-400" />
                        <span className="font-mono text-white/70 group-hover:text-white flex-1">
                          #{edge.target}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${synapseColor.bg} ${synapseColor.text} border ${synapseColor.border}`}
                        >
                          {(edge.weight * 100).toFixed(0)}%
                        </span>
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Incoming connections */}
            {sortedIncoming.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <ArrowLeft className="w-3 h-3 text-purple-400" />
                  <span className="text-xs font-medium text-white/60">
                    Incoming Synapses
                  </span>
                </div>
                <div className="space-y-1.5">
                  {sortedIncoming.map((edge, i) => {
                    const sourceNode = getNodeById(edge.source)
                    const synapseColor = SYNAPSE_COLORS[edge.type]
                    return (
                      <button
                        key={i}
                        className="flex items-center gap-2 w-full text-left text-xs bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/10 rounded-lg p-2 transition-all group"
                        onClick={() => sourceNode && onNodeClick(sourceNode)}
                      >
                        <ArrowLeft className="w-3 h-3 text-purple-400/50 group-hover:text-purple-400" />
                        <span className="font-mono text-white/70 group-hover:text-white flex-1">
                          #{edge.source}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${synapseColor.bg} ${synapseColor.text} border ${synapseColor.border}`}
                        >
                          {(edge.weight * 100).toFixed(0)}%
                        </span>
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Synapse legend */}
            <div className="pt-2 border-t border-white/10">
              <div className="text-[10px] text-white/30 uppercase tracking-wider mb-2">Synapse Types</div>
              <div className="flex items-center gap-3 text-[10px]">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-white/50">Fast &gt;70%</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-yellow-500" />
                  <span className="text-white/50">Slow 40-70%</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-purple-500" />
                  <span className="text-white/50">Meta &lt;40%</span>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-white/10 bg-white/5">
        <div className="flex items-center justify-between text-[10px] text-white/30">
          <span>Frame {node.frame + 1} of 47</span>
          <span>Node {node.id + 1} of 512</span>
        </div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 2px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      `}</style>
    </div>
  )
}
