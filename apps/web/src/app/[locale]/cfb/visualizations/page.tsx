'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { BarChart3, Activity, Grid3X3, TrendingUp, Zap } from 'lucide-react'
import { StylemetryRadar, ConfidenceHeatmap, TimelineChart } from '@/components/cfb'
import { GamificationProvider, AchievementUnlock } from '@/components/gamification'

type VisualizationType = 'overview' | 'stylometry' | 'heatmap' | 'timeline'

export default function CFBVisualizationsPage() {
  const [activeView, setActiveView] = useState<VisualizationType>('overview')

  const views = [
    { id: 'overview' as const, label: 'Overview', icon: BarChart3 },
    { id: 'stylometry' as const, label: 'Stylometry Radar', icon: Activity },
    { id: 'heatmap' as const, label: 'Confidence Matrix', icon: Grid3X3 },
    { id: 'timeline' as const, label: 'Activity Timeline', icon: TrendingUp },
  ]

  return (
    <GamificationProvider>
      <div className="flex flex-col min-h-screen">
        <AchievementUnlock />

        <main className="flex-1 py-20 px-4">
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <motion.div
              className="mb-8 text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="flex items-center justify-center gap-3 mb-3">
                <Zap className="h-10 w-10 text-cyan-400" />
                <h1 className="text-4xl font-bold">Data Visualizations</h1>
              </div>
              <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                Interactive visual analysis of the CFB = Satoshi hypothesis with 26,000+ data points
              </p>
            </motion.div>

            {/* Navigation Tabs */}
            <motion.div
              className="mb-8 flex flex-wrap gap-2 justify-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              {views.map((view) => {
                const Icon = view.icon
                const isActive = activeView === view.id
                return (
                  <button
                    key={view.id}
                    onClick={() => setActiveView(view.id)}
                    className={`flex items-center gap-2 px-5 py-3 rounded-lg transition-all whitespace-nowrap font-medium ${
                      isActive
                        ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/20'
                        : 'bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {view.label}
                  </button>
                )
              })}
            </motion.div>

            {/* Content */}
            <div className="space-y-8">
              {activeView === 'overview' && (
                <>
                  {/* Stats Overview */}
                  <motion.div
                    className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                  >
                    <div className="p-6 rounded-xl bg-gradient-to-br from-emerald-900/30 to-emerald-950/30 border border-emerald-800">
                      <div className="text-xs text-emerald-400 mb-1">STYLOMETRY MATCH</div>
                      <div className="text-3xl font-bold text-emerald-300">
                        99.8%
                      </div>
                      <div className="text-xs text-emerald-500 mt-2">847 Satoshi posts analyzed</div>
                    </div>
                    <div className="p-6 rounded-xl bg-gradient-to-br from-blue-900/30 to-blue-950/30 border border-blue-800">
                      <div className="text-xs text-blue-400 mb-1">OVERALL CONFIDENCE</div>
                      <div className="text-3xl font-bold text-blue-300">
                        91.4%
                      </div>
                      <div className="text-xs text-blue-500 mt-2">20 evidence categories</div>
                    </div>
                    <div className="p-6 rounded-xl bg-gradient-to-br from-amber-900/30 to-amber-950/30 border border-amber-800">
                      <div className="text-xs text-amber-400 mb-1">DATA POINTS</div>
                      <div className="text-3xl font-bold text-amber-300">
                        26,049+
                      </div>
                      <div className="text-xs text-amber-500 mt-2">Discord, BitcoinTalk, Emails</div>
                    </div>
                    <div className="p-6 rounded-xl bg-gradient-to-br from-purple-900/30 to-purple-950/30 border border-purple-800">
                      <div className="text-xs text-purple-400 mb-1">TIME SPAN</div>
                      <div className="text-3xl font-bold text-purple-300">17 Years</div>
                      <div className="text-xs text-purple-500 mt-2">2007 - 2024</div>
                    </div>
                  </motion.div>

                  {/* All Visualizations */}
                  <StylemetryRadar />
                  <ConfidenceHeatmap />
                  <TimelineChart />
                </>
              )}

              {activeView === 'stylometry' && <StylemetryRadar />}
              {activeView === 'heatmap' && <ConfidenceHeatmap />}
              {activeView === 'timeline' && <TimelineChart />}
            </div>

            {/* Methodology Footer */}
            <motion.div
              className="mt-12 p-6 rounded-xl bg-muted/30 border border-border"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <h3 className="text-lg font-bold mb-4">Visualization Methodology</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
                <div>
                  <h4 className="font-medium text-cyan-400 mb-2">Stylometry Radar</h4>
                  <p className="text-muted-foreground leading-relaxed">
                    Uses statistical linguistic analysis comparing 8 key metrics between Satoshi's
                    writings (847 posts/emails) and CFB's public communications (15,000+ messages).
                  </p>
                </div>
                <div>
                  <h4 className="font-medium text-cyan-400 mb-2">Confidence Matrix</h4>
                  <p className="text-muted-foreground leading-relaxed">
                    Multi-dimensional evidence scoring across 5 categories with 4 metrics each.
                    Each cell represents a specific evidentiary element with individual confidence level.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium text-cyan-400 mb-2">Activity Timeline</h4>
                  <p className="text-muted-foreground leading-relaxed">
                    Tracks public activity levels of Satoshi, CFB, and Qubic project from 2007-2026.
                    Highlights correlation patterns and key transition events.
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </main>

        <footer className="py-8 border-t border-border bg-muted/10">
          <div className="container">
            <div className="flex flex-col items-center text-center">
              <p className="text-sm text-muted-foreground">
                CFB Forensics - Data Visualizations
              </p>
              <p className="mt-2 font-mono text-xs text-muted-foreground/80">
                Interactive Charts | Real-time Analysis | 26,000+ Data Points
              </p>
            </div>
          </div>
        </footer>
      </div>
    </GamificationProvider>
  )
}
