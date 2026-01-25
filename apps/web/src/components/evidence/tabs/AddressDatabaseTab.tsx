'use client'

import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Database, Binary, Coins } from 'lucide-react'
import dynamic from 'next/dynamic'

// Lazy load table components for better performance
const QubicSeedsTable = dynamic(
  () => import('../tables/QubicSeedsTable'),
  {
    loading: () => (
      <div className="flex items-center justify-center h-[500px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="text-muted-foreground">Loading Qubic Seeds...</span>
        </div>
      </div>
    ),
  }
)

const MatrixAddressesTable = dynamic(
  () => import('../tables/MatrixAddressesTable'),
  {
    loading: () => (
      <div className="flex items-center justify-center h-[500px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="text-muted-foreground">Loading Matrix Addresses...</span>
        </div>
      </div>
    ),
  }
)

/**
 * Address Database Tab
 *
 * Displays searchable tables for:
 * - Qubic Seeds (55-char private seeds → 60-char public identities)
 * - Bitcoin Matrix Addresses (derived from Anna Matrix, public addresses only)
 */
export default function AddressDatabaseTab() {
  const [activeTab, setActiveTab] = useState('qubic')

  return (
    <div className="w-full min-h-[600px] bg-gradient-to-b from-background to-muted/10 rounded-lg border border-border p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30 flex items-center justify-center">
            <Database className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              Address Database
            </h3>
            <p className="text-sm text-muted-foreground">
              Cryptographic research data from the Bitcoin-Qubic bridge analysis
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-2 w-full max-w-md mb-6">
          <TabsTrigger value="qubic" className="flex items-center gap-2">
            <Binary className="w-4 h-4" />
            Qubic Seeds
          </TabsTrigger>
          <TabsTrigger value="bitcoin" className="flex items-center gap-2">
            <Coins className="w-4 h-4" />
            Matrix Addresses
          </TabsTrigger>
        </TabsList>

        <TabsContent value="qubic" className="mt-0">
          <QubicSeedsTable />
        </TabsContent>

        <TabsContent value="bitcoin" className="mt-0">
          <MatrixAddressesTable />
        </TabsContent>
      </Tabs>
    </div>
  )
}
