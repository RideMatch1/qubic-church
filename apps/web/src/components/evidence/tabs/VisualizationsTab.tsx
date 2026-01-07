'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Brain, Network, Maximize2, Info, Sparkles, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import dynamic from 'next/dynamic'

// Enhanced loading component
function VizLoadingScreen({ name, description }: { name: string; description: string }) {
  return (
    <div className="w-full h-[700px] bg-gradient-to-b from-black via-gray-900 to-black rounded-lg border border-border flex items-center justify-center">
      <div className="flex flex-col items-center gap-4 max-w-sm text-center">
        <div className="relative">
          <div className="w-16 h-16 border-2 border-primary/30 rounded-full" />
          <div className="absolute inset-0 w-16 h-16 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center">
            <Brain className="w-6 h-6 text-primary/50" />
          </div>
        </div>
        <div>
          <div className="text-white font-medium mb-1">Loading {name}...</div>
          <div className="text-muted-foreground text-xs">{description}</div>
        </div>
      </div>
    </div>
  )
}

// Dynamically import scenes to avoid SSR issues with Three.js
const NeuraxonScene = dynamic(
  () => import('@/components/evidence/neuraxon/NeuraxonScene'),
  {
    loading: () => (
      <VizLoadingScreen
        name="Neuraxon"
        description="Initializing neural network visualization"
      />
    ),
    ssr: false,
  }
)

const AddressGraphScene = dynamic(
  () => import('@/components/evidence/address-graph/AddressGraphScene').then(mod => ({ default: mod.AddressGraphScene })),
  {
    loading: () => (
      <VizLoadingScreen
        name="Address Graph"
        description="Loading Bitcoin address connections"
      />
    ),
    ssr: false,
  }
)

// Visualization configurations
const VISUALIZATIONS = [
  {
    id: 'neuraxon',
    label: 'Neuraxon',
    icon: Brain,
    description: 'Neural network visualization of the Bitcoin-Qubic bridge',
    stats: {
      neurons: '128',
      connections: '512+',
      layers: '4',
    },
    color: 'from-purple-500 to-blue-500',
  },
  {
    id: 'graph',
    label: 'Address Graph',
    icon: Network,
    description: 'Interactive 3D graph of connected Bitcoin addresses',
    stats: {
      nodes: '100+',
      edges: '200+',
      clusters: '5',
    },
    color: 'from-orange-500 to-amber-500',
  },
]

// =============================================================================
// MAIN COMPONENT
// =============================================================================
export default function VisualizationsTab() {
  const [activeViz, setActiveViz] = useState('neuraxon')
  const [isFullscreen, setIsFullscreen] = useState(false)

  const currentViz = VISUALIZATIONS.find(v => v.id === activeViz)

  const handleFullscreen = () => {
    const element = document.querySelector('[data-viz-container]')
    if (element) {
      if (!document.fullscreenElement) {
        element.requestFullscreen()
        setIsFullscreen(true)
      } else {
        document.exitFullscreen()
        setIsFullscreen(false)
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-blue-500/20 border border-purple-500/30">
              <Sparkles className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h3 className="text-xl font-semibold">3D Visualizations</h3>
              <p className="text-sm text-muted-foreground">Interactive Bitcoin-Qubic structures</p>
            </div>
          </div>
          <p className="text-sm text-muted-foreground max-w-2xl">
            Explore the mathematical connections between Bitcoin and Qubic through
            immersive 3D visualizations. Click and drag to rotate, scroll to zoom.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleFullscreen}
            className="gap-2"
          >
            <Maximize2 className="w-4 h-4" />
            Fullscreen
          </Button>
        </div>
      </motion.div>

      {/* Visualization Tabs */}
      <Tabs value={activeViz} onValueChange={setActiveViz}>
        <TabsList className="grid grid-cols-2 w-full max-w-md bg-muted/50">
          {VISUALIZATIONS.map((viz) => {
            const Icon = viz.icon
            return (
              <TabsTrigger
                key={viz.id}
                value={viz.id}
                className="flex items-center gap-2 data-[state=active]:bg-background"
              >
                <Icon className="w-4 h-4" />
                {viz.label}
              </TabsTrigger>
            )
          })}
        </TabsList>

        {/* Current Visualization Info Card */}
        {currentViz && (
          <motion.div
            key={currentViz.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 rounded-xl bg-gradient-to-r from-muted/30 to-muted/10 border border-border"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg bg-gradient-to-br ${currentViz.color} bg-opacity-20`}>
                  <currentViz.icon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <div className="font-medium">{currentViz.label}</div>
                  <div className="text-sm text-muted-foreground">{currentViz.description}</div>
                </div>
              </div>
              <div className="flex items-center gap-6">
                {Object.entries(currentViz.stats).map(([key, value]) => (
                  <div key={key} className="text-center">
                    <div className="text-lg font-bold text-primary">{value}</div>
                    <div className="text-xs text-muted-foreground capitalize">{key}</div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Visualization Container */}
        <div data-viz-container className="mt-4">
          {activeViz === 'neuraxon' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <NeuraxonScene />
            </motion.div>
          )}

          {activeViz === 'graph' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="h-[700px] bg-black rounded-lg border border-border overflow-hidden"
            >
              <AddressGraphScene />
            </motion.div>
          )}
        </div>
      </Tabs>

      {/* Footer hints */}
      <motion.div
        className="flex items-center justify-center gap-4 pt-4 text-xs text-muted-foreground/50"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <div className="flex items-center gap-1">
          <Zap className="w-3 h-3" />
          <span>WebGL powered</span>
        </div>
        <span className="text-muted-foreground/20">•</span>
        <div className="flex items-center gap-1">
          <Info className="w-3 h-3" />
          <span>Click + drag to rotate</span>
        </div>
        <span className="text-muted-foreground/20">•</span>
        <div className="flex items-center gap-1">
          <Network className="w-3 h-3" />
          <span>Scroll to zoom</span>
        </div>
      </motion.div>
    </div>
  )
}
