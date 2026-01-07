'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'
import { Database, Cpu, Grid3X3, Coins, Binary, Loader2, Info, Sparkles, TrendingUp } from 'lucide-react'

// Tab components will be lazy loaded
import dynamic from 'next/dynamic'

// Quick Win 13: Enhanced loading skeleton with progress
function TableSkeleton({ label }: { label?: string }) {
  return (
    <div className="w-full h-[600px] bg-card/50 rounded-lg border border-border flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <div className="w-12 h-12 border-2 border-primary/30 rounded-full" />
          <div className="absolute inset-0 w-12 h-12 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
        <div className="text-center">
          <span className="text-muted-foreground text-sm block">Loading {label || 'data'}...</span>
          <span className="text-muted-foreground/50 text-xs">This may take a moment</span>
        </div>
      </div>
    </div>
  )
}

const PatoshiTable = dynamic(() => import('./tables/PatoshiTable'), {
  loading: () => <TableSkeleton label="Patoshi addresses" />,
  ssr: false,
})

const QubicSeedsTable = dynamic(() => import('./tables/QubicSeedsTable'), {
  loading: () => <TableSkeleton label="Qubic seeds" />,
  ssr: false,
})

const BitcoinAddressesTable = dynamic(() => import('./tables/BitcoinAddressesTable'), {
  loading: () => <TableSkeleton label="Bitcoin addresses" />,
  ssr: false,
})

const VisualizationsTab = dynamic(() => import('./tabs/VisualizationsTab'), {
  loading: () => <TableSkeleton label="visualizations" />,
  ssr: false,
})

const AnnaMatrixTab = dynamic(() => import('./tabs/AnnaMatrixTab'), {
  loading: () => <TableSkeleton label="Anna Matrix" />,
  ssr: false,
})

interface TabConfig {
  id: string
  label: string
  icon: React.ReactNode
  description: string
  count?: string
  badge?: string
  badgeColor?: string
  gradient?: string
}

// Quick Win 14: Enhanced tab config with badges and gradients
const TABS: TabConfig[] = [
  {
    id: 'visualizations',
    label: '3D Viz',
    icon: <Cpu className="w-4 h-4" />,
    description: 'Neuraxon neural network & Address Graph visualizations',
    badge: 'Interactive',
    badgeColor: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    gradient: 'from-purple-500/20 to-blue-500/20',
  },
  {
    id: 'matrix',
    label: 'Anna Grid',
    icon: <Grid3X3 className="w-4 h-4" />,
    description: '128×128 cryptographic matrix with 16,384 cells',
    badge: 'Enhanced',
    badgeColor: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    gradient: 'from-orange-500/20 to-amber-500/20',
  },
  {
    id: 'qubic',
    label: 'Qubic Seeds',
    icon: <Binary className="w-4 h-4" />,
    description: 'Complete private & public seed pairs with derivations',
    count: '23,765',
    gradient: 'from-blue-500/20 to-cyan-500/20',
  },
  {
    id: 'bitcoin',
    label: 'Bitcoin',
    icon: <Database className="w-4 h-4" />,
    description: 'Derived Bitcoin addresses with public keys',
    count: '1M+',
    badge: 'Verified',
    badgeColor: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    gradient: 'from-orange-500/20 to-yellow-500/20',
  },
  {
    id: 'patoshi',
    label: 'Patoshi',
    icon: <Coins className="w-4 h-4" />,
    description: 'Early Bitcoin mining addresses (blocks 1-36,288)',
    count: '21,953',
    gradient: 'from-amber-500/20 to-orange-500/20',
  },
]

// Quick Win 15: Tab info tooltip component
function TabTooltip({ tab, visible }: { tab: TabConfig; visible: boolean }) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 5, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 5, scale: 0.95 }}
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-popover border border-border rounded-lg shadow-lg z-50 min-w-[200px] pointer-events-none"
        >
          <div className="text-sm font-medium text-foreground mb-1">{tab.label}</div>
          <div className="text-xs text-muted-foreground">{tab.description}</div>
          {tab.count && (
            <div className="text-xs text-primary mt-1 font-mono">{tab.count} records</div>
          )}
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 rotate-45 w-2 h-2 bg-popover border-r border-b border-border" />
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export function EvidenceTabs() {
  const [activeTab, setActiveTab] = useState('visualizations')
  const [hoveredTab, setHoveredTab] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Quick Win 16: Smooth loading transition
  const handleTabChange = (value: string) => {
    if (value !== activeTab) {
      setIsLoading(true)
      setActiveTab(value)
      // Simulate loading delay for smooth transition
      setTimeout(() => setIsLoading(false), 100)
    }
  }

  // Quick Win 17: Keyboard navigation between tabs
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement) return

      const currentIndex = TABS.findIndex(t => t.id === activeTab)

      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault()
        const nextIndex = (currentIndex + 1) % TABS.length
        setActiveTab(TABS[nextIndex]?.id || 'visualizations')
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault()
        const prevIndex = (currentIndex - 1 + TABS.length) % TABS.length
        setActiveTab(TABS[prevIndex]?.id || 'visualizations')
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [activeTab])

  return (
      <section id="data-tables" className="py-16 px-4">
        <div className="container max-w-7xl mx-auto">
          {/* Quick Win 18: Section header with total stats */}
          <motion.div
            className="text-center mb-8"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 rounded-full text-sm text-primary mb-4">
              <TrendingUp className="w-4 h-4" />
              <span className="font-mono">1,050,515 Total Records</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-bold mb-2">Evidence Database</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Explore cryptographically verified data connecting Bitcoin&apos;s genesis to Qubic
            </p>
          </motion.div>

          <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
            <TabsList className="w-full flex flex-wrap justify-center gap-2 bg-transparent h-auto p-2 mb-8">
              {TABS.map((tab) => (
                <div
                  key={tab.id}
                  className="relative"
                  onMouseEnter={() => setHoveredTab(tab.id)}
                  onMouseLeave={() => setHoveredTab(null)}
                >
                  <TabTooltip tab={tab} visible={hoveredTab === tab.id} />
                  <TabsTrigger
                    value={tab.id}
                    className={cn(
                      'relative flex items-center gap-2 px-4 py-3 rounded-lg border transition-all duration-200',
                      'data-[state=active]:text-primary-foreground',
                      'data-[state=active]:border-primary data-[state=active]:shadow-lg',
                      'data-[state=inactive]:bg-card data-[state=inactive]:border-border',
                      'data-[state=inactive]:hover:bg-muted',
                      'overflow-hidden'
                    )}
                  >
                    {/* Quick Win 19: Active tab gradient background */}
                    <div
                      className={cn(
                        'absolute inset-0 opacity-0 transition-opacity bg-gradient-to-r',
                        tab.gradient,
                        'data-[state=active]:opacity-100'
                      )}
                      data-state={activeTab === tab.id ? 'active' : 'inactive'}
                    />
                    <div
                      className={cn(
                        'absolute inset-0 bg-primary opacity-0 transition-opacity',
                        activeTab === tab.id && 'opacity-100'
                      )}
                    />
                    <span className="relative z-10 flex items-center gap-2">
                      {tab.icon}
                      <span className="font-medium">{tab.label}</span>
                      {tab.count && (
                        <span className="text-xs bg-background/20 px-2 py-0.5 rounded-full">
                          {tab.count}
                        </span>
                      )}
                      {tab.badge && (
                        <span className={cn(
                          'text-[10px] px-1.5 py-0.5 rounded border uppercase font-medium',
                          tab.badgeColor || 'bg-primary/20 text-primary border-primary/30'
                        )}>
                          {tab.badge}
                        </span>
                      )}
                    </span>
                  </TabsTrigger>
                </div>
              ))}
            </TabsList>

            {/* Quick Win 20: Enhanced content container with subtle animation */}
            <motion.div
              className="bg-card/30 backdrop-blur-sm rounded-xl border border-border p-4 md:p-6 relative overflow-hidden"
              initial={false}
              animate={{ opacity: isLoading ? 0.7 : 1 }}
              transition={{ duration: 0.15 }}
            >
              {/* Decorative corner elements */}
              <div className="absolute top-0 left-0 w-20 h-20 bg-gradient-to-br from-primary/5 to-transparent rounded-br-full pointer-events-none" />
              <div className="absolute bottom-0 right-0 w-20 h-20 bg-gradient-to-tl from-primary/5 to-transparent rounded-tl-full pointer-events-none" />

              <TabsContent value="patoshi" className="mt-0 focus-visible:outline-none">
                <PatoshiTable />
              </TabsContent>

              <TabsContent value="qubic" className="mt-0 focus-visible:outline-none">
                <QubicSeedsTable />
              </TabsContent>

              <TabsContent value="bitcoin" className="mt-0 focus-visible:outline-none">
                <BitcoinAddressesTable />
              </TabsContent>

              <TabsContent value="visualizations" className="mt-0 focus-visible:outline-none">
                <VisualizationsTab />
              </TabsContent>

              <TabsContent value="matrix" className="mt-0 focus-visible:outline-none">
                <AnnaMatrixTab />
              </TabsContent>
            </motion.div>
          </Tabs>

          {/* Quick Win: Navigation hint */}
          <motion.div
            className="mt-4 flex items-center justify-center gap-4 text-xs text-muted-foreground/50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-muted/50 border border-border rounded text-[10px] font-mono">←</kbd>
              <kbd className="px-1.5 py-0.5 bg-muted/50 border border-border rounded text-[10px] font-mono">→</kbd>
              <span className="ml-1">Switch tabs</span>
            </span>
            <span className="text-muted-foreground/30">|</span>
            <span className="flex items-center gap-1">
              <Info className="w-3 h-3" />
              <span>Hover tabs for details</span>
            </span>
          </motion.div>
        </div>
      </section>
  )
}
