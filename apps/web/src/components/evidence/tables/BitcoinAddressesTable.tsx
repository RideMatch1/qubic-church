'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import { VirtualizedTable, ExplorerButton, type Column } from './VirtualizedTable'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Copy, Check, Eye, EyeOff, AlertTriangle, Key, Database, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import type { FilterConfig } from './TableFilters'

// Types for different Bitcoin data
interface DerivedAddress {
  id: number
  address: string
  privateKey: string
  sequence: string
  method: string
}

interface PrivateKeyRecord {
  id: number
  address: string
  privateKeyHex: string
  privateKeyWIF: string
  position: number[]
  method: string
  xorVariant: number
  compressed: boolean
  hash160: string
  cfVariant: string
  validationStatus: string
}

interface MatrixAddress {
  id: number
  address: string
}

export default function BitcoinAddressesTable() {
  const [activeSubTab, setActiveSubTab] = useState('private-keys')
  const [showPrivateKeys, setShowPrivateKeys] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  // Data states
  const [derivedData, setDerivedData] = useState<DerivedAddress[]>([])
  const [privateKeysData, setPrivateKeysData] = useState<PrivateKeyRecord[]>([])
  const [matrixData, setMatrixData] = useState<MatrixAddress[]>([])
  const [loading, setLoading] = useState({ derived: true, privateKeys: true, matrix: true })
  const [counts, setCounts] = useState({ derived: 0, privateKeys: 0, matrix: 0 })

  // Load all data
  useEffect(() => {
    // Load derived addresses
    fetch('/data/bitcoin-derived-addresses.json')
      .then((res) => res.json())
      .then((json) => {
        setDerivedData(json.records)
        setCounts((c) => ({ ...c, derived: json.total }))
        setLoading((l) => ({ ...l, derived: false }))
      })

    // Load private keys
    fetch('/data/bitcoin-private-keys.json')
      .then((res) => res.json())
      .then((json) => {
        setPrivateKeysData(json.records)
        setCounts((c) => ({ ...c, privateKeys: json.total }))
        setLoading((l) => ({ ...l, privateKeys: false }))
      })

    // Load matrix addresses
    fetch('/data/matrix-addresses.json')
      .then((res) => res.json())
      .then((json) => {
        setMatrixData(json.records)
        setCounts((c) => ({ ...c, matrix: json.total }))
        setLoading((l) => ({ ...l, matrix: false }))
      })
  }, [])

  const handleCopy = async (text: string, id: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  // Column definitions for private keys table
  const privateKeysColumns: Column<PrivateKeyRecord>[] = [
    {
      id: 'address',
      header: 'Address',
      accessor: (row) => row.address,
      width: '280px',
      render: (value, row) => (
        <div className="flex items-center gap-2 group">
          <span className="font-mono text-xs truncate">{String(value)}</span>
          <button
            onClick={() => handleCopy(String(value), `addr-${row.id}`)}
            className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
          >
            {copiedId === `addr-${row.id}` ? (
              <Check className="w-3 h-3 text-green-500" />
            ) : (
              <Copy className="w-3 h-3 text-muted-foreground" />
            )}
          </button>
          <ExplorerButton type="bitcoin" value={String(value)} />
        </div>
      ),
    },
    {
      id: 'privateKeyWIF',
      header: 'Private Key (WIF)',
      accessor: (row) => row.privateKeyWIF,
      width: '400px',
      render: (value, row) => (
        <div className="flex items-center gap-2 group">
          <span className="font-mono text-xs">
            {showPrivateKeys ? String(value) : '•'.repeat(30) + '...'}
          </span>
          {showPrivateKeys && (
            <>
              <button
                onClick={() => handleCopy(String(value), `wif-${row.id}`)}
                className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
              >
                {copiedId === `wif-${row.id}` ? (
                  <Check className="w-3 h-3 text-green-500" />
                ) : (
                  <Copy className="w-3 h-3 text-muted-foreground" />
                )}
              </button>
              <ExplorerButton type="bitcoin" value={row.address} />
            </>
          )}
        </div>
      ),
    },
    {
      id: 'method',
      header: 'Method',
      accessor: (row) => row.method,
      width: '100px',
      render: (value) => (
        <span className="px-2 py-0.5 bg-primary/20 rounded text-xs">{String(value)}</span>
      ),
    },
    {
      id: 'position',
      header: 'Matrix Pos',
      accessor: (row) => `[${row.position.join(',')}]`,
      width: '100px',
    },
    {
      id: 'validationStatus',
      header: 'Status',
      accessor: (row) => row.validationStatus,
      width: '100px',
      render: (value) => (
        <span
          className={`px-2 py-0.5 rounded text-xs ${
            value === 'SUCCESS' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}
        >
          {String(value)}
        </span>
      ),
    },
  ]

  // Column definitions for derived addresses
  const derivedColumns: Column<DerivedAddress>[] = [
    {
      id: 'address',
      header: 'Address',
      accessor: (row) => row.address,
      width: '300px',
      render: (value, row) => (
        <div className="flex items-center gap-2 group">
          <span className="font-mono text-xs truncate">{String(value)}</span>
          <ExplorerButton type="bitcoin" value={String(value)} />
        </div>
      ),
      copyable: true,
    },
    {
      id: 'privateKey',
      header: 'Private Key (Hex)',
      accessor: (row) => row.privateKey,
      width: '450px',
      render: (value, row) => (
        <div className="flex items-center gap-2 group">
          <span className="font-mono text-xs">
            {showPrivateKeys ? String(value) : '•'.repeat(40) + '...'}
          </span>
          {showPrivateKeys && (
            <button
              onClick={() => handleCopy(String(value), `derived-${row.id}`)}
              className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
            >
              {copiedId === `derived-${row.id}` ? (
                <Check className="w-3 h-3 text-green-500" />
              ) : (
                <Copy className="w-3 h-3 text-muted-foreground" />
              )}
            </button>
          )}
        </div>
      ),
    },
    {
      id: 'method',
      header: 'Method',
      accessor: (row) => row.method,
      width: '100px',
      render: (value) => (
        <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded text-xs">
          {String(value)}
        </span>
      ),
    },
  ]

  // Column definitions for matrix addresses (no private keys)
  const matrixColumns: Column<MatrixAddress>[] = [
    {
      id: 'id',
      header: '#',
      accessor: (row) => row.id + 1,
      width: '100px',
      sortable: true,
    },
    {
      id: 'address',
      header: 'Bitcoin Address',
      accessor: (row) => row.address,
      width: '400px',
      render: (value, row) => (
        <div className="flex items-center gap-2 group">
          <span className="font-mono text-sm">{String(value)}</span>
          <button
            onClick={() => handleCopy(String(value), `matrix-${row.id}`)}
            className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
          >
            {copiedId === `matrix-${row.id}` ? (
              <Check className="w-3 h-3 text-green-500" />
            ) : (
              <Copy className="w-3 h-3 text-muted-foreground" />
            )}
          </button>
          <ExplorerButton type="bitcoin" value={String(value)} />
        </div>
      ),
    },
  ]

  // Filter configurations
  const privateKeysFilters: FilterConfig[] = useMemo(
    () => [
      {
        id: 'addressPrefix',
        label: 'Address Starts With',
        type: 'prefix',
        field: 'address',
        options: ['1', '3', 'b'],
      },
      {
        id: 'method',
        label: 'Method',
        type: 'category',
        field: 'method',
        options: ['sha256', 'k12', 'qubic'],
      },
      {
        id: 'status',
        label: 'Status',
        type: 'category',
        field: 'validationStatus',
        options: ['SUCCESS', 'FAILED'],
      },
    ],
    []
  )

  const derivedFilters: FilterConfig[] = useMemo(
    () => [
      {
        id: 'addressPrefix',
        label: 'Address Starts With',
        type: 'prefix',
        field: 'address',
        options: ['1', '3', 'b'],
      },
      {
        id: 'method',
        label: 'Method',
        type: 'category',
        field: 'method',
      },
    ],
    []
  )

  const matrixFilters: FilterConfig[] = useMemo(
    () => [
      {
        id: 'addressPrefix',
        label: 'Address Starts With',
        type: 'prefix',
        field: 'address',
        options: ['1', '3', 'b'],
      },
    ],
    []
  )

  // Filter field value getters
  const getPrivateKeysFilterValue = useCallback(
    (item: PrivateKeyRecord, field: string): string => {
      if (field === 'address') return item.address
      if (field === 'method') return item.method
      if (field === 'validationStatus') return item.validationStatus
      return ''
    },
    []
  )

  const getDerivedFilterValue = useCallback(
    (item: DerivedAddress, field: string): string => {
      if (field === 'address') return item.address
      if (field === 'method') return item.method
      return ''
    },
    []
  )

  const getMatrixFilterValue = useCallback(
    (item: MatrixAddress, field: string): string => {
      if (field === 'address') return item.address
      return ''
    },
    []
  )

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold">Bitcoin Address Database</h3>
          <p className="text-sm text-muted-foreground">
            Derived addresses, validated private keys, and matrix-generated addresses
          </p>
        </div>

        <div className="flex items-center gap-4">
          {(activeSubTab === 'private-keys' || activeSubTab === 'derived') && (
            <Button
              variant={showPrivateKeys ? 'destructive' : 'outline'}
              size="sm"
              onClick={() => setShowPrivateKeys(!showPrivateKeys)}
            >
              {showPrivateKeys ? (
                <>
                  <EyeOff className="w-4 h-4 mr-2" />
                  Hide Keys
                </>
              ) : (
                <>
                  <Eye className="w-4 h-4 mr-2" />
                  Show Keys
                </>
              )}
            </Button>
          )}

          <div className="text-right">
            <div className="text-2xl font-bold text-orange-500">
              {(counts.derived + counts.privateKeys + counts.matrix).toLocaleString()}
            </div>
            <div className="text-xs text-muted-foreground">Total Records</div>
          </div>
        </div>
      </div>

      {/* Warning Banner */}
      {showPrivateKeys && (activeSubTab === 'private-keys' || activeSubTab === 'derived') && (
        <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
          <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-medium text-red-400">Private Keys Visible</h4>
            <p className="text-sm text-muted-foreground mt-1">
              These are real Bitcoin private keys. Anyone with access can control these
              addresses. This data is provided for cryptographic research purposes only.
            </p>
          </div>
        </div>
      )}

      {/* Sub-tabs */}
      <Tabs value={activeSubTab} onValueChange={setActiveSubTab}>
        <TabsList className="grid grid-cols-3 w-full max-w-lg">
          <TabsTrigger value="private-keys" className="flex items-center gap-2">
            <Key className="w-4 h-4" />
            WIF Keys ({counts.privateKeys})
          </TabsTrigger>
          <TabsTrigger value="derived" className="flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            Derived ({counts.derived.toLocaleString()})
          </TabsTrigger>
          <TabsTrigger value="matrix" className="flex items-center gap-2">
            <Database className="w-4 h-4" />
            Matrix ({counts.matrix.toLocaleString()})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="private-keys" className="mt-4">
          {loading.privateKeys ? (
            <div className="flex items-center justify-center h-[500px]">
              <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <VirtualizedTable
              data={privateKeysData}
              columns={privateKeysColumns}
              searchFields={['address', 'privateKeyWIF', 'method', 'cfVariant']}
              filters={privateKeysFilters}
              getFilterFieldValue={getPrivateKeysFilterValue}
              height={500}
            />
          )}
        </TabsContent>

        <TabsContent value="derived" className="mt-4">
          {loading.derived ? (
            <div className="flex items-center justify-center h-[500px]">
              <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <VirtualizedTable
              data={derivedData}
              columns={derivedColumns}
              searchFields={['address', 'method']}
              filters={derivedFilters}
              getFilterFieldValue={getDerivedFilterValue}
              height={500}
            />
          )}
        </TabsContent>

        <TabsContent value="matrix" className="mt-4">
          {loading.matrix ? (
            <div className="flex items-center justify-center h-[500px]">
              <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <VirtualizedTable
              data={matrixData}
              columns={matrixColumns}
              searchFields={['address']}
              filters={matrixFilters}
              getFilterFieldValue={getMatrixFilterValue}
              height={500}
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
