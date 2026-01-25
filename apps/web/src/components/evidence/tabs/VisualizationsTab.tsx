'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Brain, Network, Maximize2, Zap, Info } from 'lucide-react'
import { Button } from '@/components/ui/button'
import dynamic from 'next/dynamic'

// Loading component
function VizLoadingScreen({ name }: { name: string }) {
  return (
    <div className="w-full h-[700px] bg-black rounded-lg border border-border flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <div className="w-16 h-16 border-2 border-primary/30 rounded-full" />
          <div className="absolute inset-0 w-16 h-16 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
        <span className="text-muted-foreground">Loading {name}...</span>
      </div>
    </div>
  )
}

// Dynamic imports
const QortexScene = dynamic(
  () => import('@/components/evidence/neuraxon/NeuraxonScene'),
  { loading: () => <VizLoadingScreen name="Qortex" />, ssr: false }
)

const AddressGraphScene = dynamic(
  () => import('@/components/evidence/address-graph/AddressGraphScene').then(mod => ({ default: mod.AddressGraphScene })),
  { loading: () => <VizLoadingScreen name="Address Graph" />, ssr: false }
)

// Only 2 visualizations - clean and simple
const VISUALIZATIONS = [
  {
    id: 'qortex',
    label: 'Qortex Neural Network',
    icon: Brain,
    description: 'Ternary neural network visualization with real Qubic seeds',
    color: 'purple',
  },
  {
    id: 'graph',
    label: 'Address Graph',
    icon: Network,
    description: 'Bitcoin address network derived from Anna Matrix',
    color: 'orange',
  },
]

export default function VisualizationsTab() {
  const [activeViz, setActiveViz] = useState('qortex')

  const handleFullscreen = () => {
    const element = document.querySelector('[data-viz-container]')
    if (element && !document.fullscreenElement) {
      element.requestFullscreen()
    } else if (document.fullscreenElement) {
      document.exitFullscreen()
    }
  }

  return (
    <div className="space-y-4">
      {/* Simple toggle between visualizations */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {VISUALIZATIONS.map((viz) => {
            const Icon = viz.icon
            const isActive = activeViz === viz.id
            return (
              <button
                key={viz.id}
                onClick={() => setActiveViz(viz.id)}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-lg border transition-all
                  ${isActive
                    ? `bg-${viz.color}-500/20 border-${viz.color}-500/50 text-${viz.color}-400`
                    : 'bg-muted/30 border-border text-muted-foreground hover:bg-muted/50'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                <span className="font-medium">{viz.label}</span>
              </button>
            )
          })}
        </div>

        <Button variant="outline" size="sm" onClick={handleFullscreen}>
          <Maximize2 className="w-4 h-4 mr-2" />
          Fullscreen
        </Button>
      </div>

      {/* Visualization Container */}
      <div data-viz-container className="rounded-lg overflow-hidden">
        {activeViz === 'qortex' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            <QortexScene />
          </motion.div>
        )}

        {activeViz === 'graph' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
            className="h-[700px] bg-black rounded-lg border border-border"
          >
            <AddressGraphScene />
          </motion.div>
        )}
      </div>

      {/* Minimal footer */}
      <div className="flex items-center justify-center gap-6 text-xs text-muted-foreground/50">
        <span className="flex items-center gap-1">
          <Zap className="w-3 h-3" /> WebGL
        </span>
        <span className="flex items-center gap-1">
          <Info className="w-3 h-3" /> Drag to rotate • Scroll to zoom
        </span>
      </div>
    </div>
  )
}
