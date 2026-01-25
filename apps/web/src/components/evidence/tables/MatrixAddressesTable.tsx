'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import { VirtualizedTable, ExplorerButton, type Column } from './VirtualizedTable'
import { Copy, Check, Info } from 'lucide-react'
import type { FilterConfig } from './TableFilters'

interface MatrixAddress {
  id: number
  address: string
}

interface MatrixData {
  total: number
  generated: number
  uniqueCount: number
  records: MatrixAddress[]
}

export default function MatrixAddressesTable() {
  const [data, setData] = useState<MatrixAddress[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [stats, setStats] = useState({ total: 0, unique: 0 })

  useEffect(() => {
    fetch('/data/matrix-addresses.json')
      .then((res) => res.json())
      .then((json: MatrixData) => {
        setData(json.records)
        setStats({
          total: json.total,
          unique: json.uniqueCount,
        })
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const handleCopy = async (text: string, id: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const columns: Column<MatrixAddress>[] = [
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
            onClick={() => handleCopy(String(value), `addr-${row.id}`)}
            className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
          >
            {copiedId === `addr-${row.id}` ? (
              <Check className="w-3 h-3 text-green-500" />
            ) : (
              <Copy className="w-3 h-3 text-muted-foreground hover:text-foreground" />
            )}
          </button>
          <ExplorerButton type="bitcoin" value={String(value)} />
        </div>
      ),
    },
    {
      id: 'prefix',
      header: 'Type',
      accessor: (row) => {
        if (row.address.startsWith('bc1')) return 'Bech32'
        if (row.address.startsWith('3')) return 'P2SH'
        if (row.address.startsWith('1')) return 'P2PKH'
        return 'Unknown'
      },
      width: '100px',
      render: (value) => (
        <span
          className={`px-2 py-0.5 rounded text-xs font-medium ${
            value === 'Bech32'
              ? 'bg-blue-500/20 text-blue-400'
              : value === 'P2SH'
                ? 'bg-purple-500/20 text-purple-400'
                : 'bg-orange-500/20 text-orange-400'
          }`}
        >
          {String(value)}
        </span>
      ),
    },
  ]

  // Filter configuration
  const filters: FilterConfig[] = useMemo(
    () => [
      {
        id: 'addressPrefix',
        label: 'Address Type',
        type: 'prefix',
        field: 'address',
        options: ['1', '3', 'bc1'],
      },
    ],
    []
  )

  // Get field value for filtering
  const getFilterFieldValue = useCallback(
    (item: MatrixAddress, field: string): string => {
      if (field === 'address') {
        return item.address
      }
      return ''
    },
    []
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[600px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="text-muted-foreground">Loading matrix addresses...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[600px] text-destructive">
        Error: {error}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Info Banner */}
      <div className="flex items-start gap-3 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
        <Info className="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
        <div>
          <h4 className="font-medium text-blue-400">Matrix-Derived Addresses</h4>
          <p className="text-sm text-muted-foreground mt-1">
            These Bitcoin addresses were mathematically derived from the 128×128 Anna Matrix
            using K12 hash functions. Public addresses only — no private keys are stored or displayed.
          </p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold">Anna Matrix Bitcoin Addresses</h3>
          <p className="text-sm text-muted-foreground">
            {stats.unique.toLocaleString()} unique addresses derived from matrix coordinates
          </p>
        </div>

        <div className="flex items-center gap-6">
          <div className="text-right">
            <div className="text-2xl font-bold text-orange-500">
              {stats.total.toLocaleString()}
            </div>
            <div className="text-xs text-muted-foreground">Total Addresses</div>
          </div>
        </div>
      </div>

      <VirtualizedTable
        data={data}
        columns={columns}
        searchFields={['address']}
        filters={filters}
        getFilterFieldValue={getFilterFieldValue}
        exportable
        onExport={() => {
          const csv = data.map((r) => r.address).join('\n')
          const blob = new Blob([`Address\n${csv}`], { type: 'text/csv' })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = 'matrix-bitcoin-addresses.csv'
          a.click()
        }}
      />
    </div>
  )
}
