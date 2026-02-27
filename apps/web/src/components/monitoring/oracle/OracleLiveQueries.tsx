'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

// ─── Types ──────────────────────────────────────────────────────────

interface QueryReply {
  numerator: number
  denominator: number
  price: number
}

interface OnChainQuery {
  queryId: string
  tick: number
  type: string
  status: string
  statusFlags: string[]
  interfaceIndex: number
  interfaceName?: string
  subscriptionId?: number
  revealTick: number
  totalCommits: number
  agreeingCommits: number
  oracle?: string
  queryTimestamp?: string
  currency1?: string
  currency2?: string
  reply?: QueryReply
  isSeal: boolean
  sealName?: string
  senderPublicKey?: string
  senderIdentity?: string
  firstSeen?: string
  lastUpdated?: string
  // Interface 1 (Mock) specific
  mockValue?: number
  // Raw data for all interfaces
  queryDataHex?: string
  replyDataHex?: string
  // Unknown interfaces
  queryRaw?: { rawHex: string; rawLength: number }
}

const INTERFACE_LABELS: Record<number, { name: string; color: string; abbr: string }> = {
  0: { name: 'Price', color: 'emerald', abbr: 'PX' },
  1: { name: 'Mock', color: 'sky', abbr: 'MK' },
}

interface LiveQueryData {
  scanTimestamp: string
  scanDurationSeconds?: number
  monitorMode?: string
  monitorStarted?: string
  monitorUptime?: number
  newSinceMonitorStart?: number
  epoch: number
  currentTick: number
  tickRange: { first: number; current: number }
  stats: {
    successfulCount: number
    timeoutCount: number
    pendingCount: number
    unresolvableCount: number
  }
  totalOnChain: number
  sealsFound: number
  uniqueSenders?: number
  senderBreakdown?: Record<string, number>
  queries: OnChainQuery[]
}

type FilterMode = 'all' | 'seals' | 'prices' | 'experiments' | 'interface1'

// ─── Constants ──────────────────────────────────────────────────────

const ease = [0.22, 1, 0.36, 1] as const
const PAGE_SIZES = [10, 25, 50, 100] as const

const SEAL_ICONS: Record<string, string> = {
  'I. BERESHIT': '\u2721',
  'II. BABEL': '\u25B2',
  'III. SULLAM': '\u2191',
  'IV. EHYEH': '\u2609',
  'V. HOTAM': '\u2605',
  'VI. YOM ADONAI': '\u263D',
  'VII. HOTAM ACHARON': '\u03A9',
}

// ─── CSV Export ─────────────────────────────────────────────────────

const CSV_COLUMNS = [
  { key: 'queryId', label: 'Query ID' },
  { key: 'tick', label: 'Tick' },
  { key: 'type', label: 'Type' },
  { key: 'status', label: 'Status' },
  { key: 'statusFlags', label: 'Flags' },
  { key: 'interfaceIndex', label: 'Interface' },
  { key: 'oracle', label: 'Oracle' },
  { key: 'currency1', label: 'Currency 1' },
  { key: 'currency2', label: 'Currency 2' },
  { key: 'queryTimestamp', label: 'Query Timestamp' },
  { key: 'price', label: 'Price' },
  { key: 'numerator', label: 'Numerator' },
  { key: 'denominator', label: 'Denominator' },
  { key: 'senderIdentity', label: 'Sender' },
  { key: 'senderPublicKey', label: 'Sender PubKey' },
  { key: 'revealTick', label: 'Reveal Tick' },
  { key: 'totalCommits', label: 'Total Commits' },
  { key: 'agreeingCommits', label: 'Agreeing Commits' },
  { key: 'isSeal', label: 'Is Seal' },
  { key: 'sealName', label: 'Seal Name' },
  { key: 'interfaceName', label: 'Interface Name' },
  { key: 'mockValue', label: 'Mock Value' },
  { key: 'queryDataHex', label: 'Query Data (hex)' },
  { key: 'replyDataHex', label: 'Reply Data (hex)' },
  { key: 'subscriptionId', label: 'Subscription ID' },
  { key: 'firstSeen', label: 'First Seen' },
  { key: 'lastUpdated', label: 'Last Updated' },
] as const

function queriesToCSV(queries: OnChainQuery[], columns: string[]): string {
  const header = columns.join(',')
  const rows = queries.map(q => {
    return columns.map(col => {
      let val: string | number | boolean | undefined = ''
      switch (col) {
        case 'price': val = q.reply?.price; break
        case 'numerator': val = q.reply?.numerator; break
        case 'denominator': val = q.reply?.denominator; break
        case 'statusFlags': val = q.statusFlags?.join('; '); break
        case 'mockValue': val = q.mockValue; break
        default: val = (q as unknown as Record<string, unknown>)[col] as string | number | boolean | undefined
      }
      const str = val == null ? '' : String(val)
      return str.includes(',') || str.includes('"') || str.includes('\n')
        ? `"${str.replace(/"/g, '""')}"`
        : str
    }).join(',')
  })
  return [header, ...rows].join('\n')
}

function downloadCSV(csv: string, filename: string) {
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

// ─── Copy Helper ────────────────────────────────────────────────────

function queryToClipboardText(q: OnChainQuery): string {
  const ifName = q.interfaceName ?? INTERFACE_LABELS[q.interfaceIndex]?.name ?? `Unknown(${q.interfaceIndex})`
  const lines = [
    `Query ID: ${q.queryId}`,
    `Tick: ${q.tick}`,
    `Status: ${q.status}`,
    `Interface: ${q.interfaceIndex} (${ifName})`,
  ]
  if (q.oracle) lines.push(`Oracle: ${q.oracle}`)
  if (q.currency1) lines.push(`Currency1: ${q.currency1}`)
  if (q.currency2) lines.push(`Currency2: ${q.currency2}`)
  if (q.mockValue !== undefined) lines.push(`Mock Value: ${q.mockValue}`)
  if (q.reply) lines.push(`Price: ${q.reply.price} (${q.reply.numerator}/${q.reply.denominator})`)
  if (q.senderIdentity) lines.push(`Sender: ${q.senderIdentity}`)
  if (q.senderPublicKey) lines.push(`PubKey: ${q.senderPublicKey}`)
  if (q.statusFlags?.length) lines.push(`Flags: ${q.statusFlags.join(', ')}`)
  if (q.queryTimestamp) lines.push(`Timestamp: ${q.queryTimestamp}`)
  if (q.revealTick) lines.push(`Reveal Tick: ${q.revealTick}`)
  if (q.totalCommits > 0) lines.push(`Commits: ${q.agreeingCommits}/${q.totalCommits}`)
  if (q.isSeal) lines.push(`Seal: ${q.sealName}`)
  if (q.queryDataHex) lines.push(`Query Data (hex): ${q.queryDataHex}`)
  if (q.replyDataHex) lines.push(`Reply Data (hex): ${q.replyDataHex}`)
  return lines.join('\n')
}

// ─── Main Component ─────────────────────────────────────────────────

export function OracleLiveQueries() {
  const [data, setData] = useState<LiveQueryData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<FilterMode>('all')
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState<number>(25)
  const [showExport, setShowExport] = useState(false)
  const [exportCols, setExportCols] = useState<Set<string>>(
    new Set(['queryId', 'tick', 'status', 'oracle', 'currency1', 'currency2', 'price', 'senderIdentity', 'interfaceIndex', 'statusFlags'])
  )
  const [copiedRow, setCopiedRow] = useState<string | null>(null)

  const fetchLive = useCallback(async () => {
    try {
      const res = await fetch('/api/oracle/live')
      const json = await res.json()
      if (json.data) {
        setData(json.data)
        setError(null)
      } else {
        setError(json.message ?? 'No data')
      }
    } catch {
      setError('Failed to load live query data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchLive()
    const interval = setInterval(fetchLive, 10000)
    return () => clearInterval(interval)
  }, [fetchLive])

  const filtered = useMemo(() => {
    if (!data) return []
    return data.queries.filter(q => {
      if (filter === 'seals') return q.isSeal
      if (filter === 'prices') return q.status === 'success' && !q.isSeal
      if (filter === 'experiments') return !q.isSeal && q.status !== 'success'
      if (filter === 'interface1') return q.interfaceIndex === 1
      return true
    })
  }, [data, filter])

  const totalPages = Math.ceil(filtered.length / pageSize)
  const paged = filtered.slice(page * pageSize, (page + 1) * pageSize)

  // Reset page when filter changes
  useEffect(() => { setPage(0) }, [filter, pageSize])

  const copyRow = useCallback((q: OnChainQuery, e: React.MouseEvent) => {
    e.stopPropagation()
    navigator.clipboard.writeText(queryToClipboardText(q)).then(() => {
      setCopiedRow(q.queryId)
      setTimeout(() => setCopiedRow(null), 1500)
    })
  }, [])

  const handleExport = useCallback(() => {
    const cols = Array.from(exportCols)
    const csv = queriesToCSV(filtered, cols)
    const ts = new Date().toISOString().slice(0, 19).replace(/[T:]/g, '-')
    downloadCSV(csv, `oracle-queries-${filter}-${ts}.csv`)
  }, [filtered, filter, exportCols])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-5 h-5 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-zinc-500 text-sm">{error ?? 'No live query data'}</p>
        <p className="text-zinc-600 text-xs mt-2 font-mono">Run: node scripts/ORACLE_MONITOR.mjs</p>
      </div>
    )
  }

  const sealCount = data.queries.filter(q => q.isSeal).length
  const successCount = data.queries.filter(q => q.status === 'success').length
  const timeoutCount = data.queries.filter(q => q.status === 'timeout').length
  const pendingCount = data.queries.filter(q => q.status === 'pending' || q.status === 'committed').length
  const if1Count = data.queries.filter(q => q.interfaceIndex === 1).length

  const dataAge = data.scanTimestamp ? (Date.now() - new Date(data.scanTimestamp).getTime()) / 1000 : Infinity
  const isMonitorLive = data.monitorMode === 'live' && dataAge < 30
  const isLiveMode = data.monitorMode === 'live'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease }}
    >
      {/* Monitor Status Bar */}
      {isLiveMode && (
        <div className={`flex items-center gap-2 mb-3 px-3 py-1.5 rounded-lg border text-[11px] ${
          isMonitorLive
            ? 'bg-emerald-500/[0.05] border-emerald-500/20'
            : 'bg-amber-500/[0.05] border-amber-500/20'
        }`}>
          <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
            isMonitorLive ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
          }`} />
          <span className={isMonitorLive ? 'text-emerald-400' : 'text-amber-400'}>
            {isMonitorLive ? 'MONITOR LIVE' : 'MONITOR STALE'}
          </span>
          <span className="text-zinc-600 ml-1">
            Updated {formatTime(data.scanTimestamp)}
            {data.monitorUptime != null && ` | Uptime: ${formatUptime(data.monitorUptime)}`}
            {data.newSinceMonitorStart != null && data.newSinceMonitorStart > 0 && (
              <span className="text-cyan-400 ml-2">+{data.newSinceMonitorStart} new</span>
            )}
          </span>
        </div>
      )}

      {/* Overview Stats */}
      <div className="flex items-center gap-4 mb-4 flex-wrap">
        <StatBadge label="ON-CHAIN" value={String(data.totalOnChain)} color="cyan" />
        <StatBadge label="SEALS" value={`${sealCount}/7`} color="purple" />
        <StatBadge label="SUCCESS" value={String(successCount)} color="emerald" />
        <StatBadge label="TIMEOUT" value={String(timeoutCount)} color="amber" />
        {pendingCount > 0 && <StatBadge label="PENDING" value={String(pendingCount)} color="cyan" />}
        {if1Count > 0 && <StatBadge label="MOCK" value={String(if1Count)} color="sky" />}
        <StatBadge label="SENDERS" value={String(data.uniqueSenders ?? '?')} color="zinc" />
        <StatBadge label="EPOCH" value={String(data.epoch)} color="zinc" />
      </div>

      {/* Sender Breakdown (top 10) */}
      {data.senderBreakdown && Object.keys(data.senderBreakdown).length > 0 && (
        <div className="mb-4 space-y-1">
          <div className="text-[9px] uppercase tracking-[0.2em] text-zinc-600 mb-1.5">
            SENDER ADDRESSES ({data.uniqueSenders ?? Object.keys(data.senderBreakdown).length})
          </div>
          {Object.entries(data.senderBreakdown)
            .sort(([, a], [, b]) => (b as number) - (a as number))
            .slice(0, 10)
            .map(([address, count]) => (
              <SenderRow key={address} address={address} count={count as number} total={data.totalOnChain} />
            ))}
          {Object.keys(data.senderBreakdown).length > 10 && (
            <div className="text-[10px] text-zinc-600 px-3">
              +{Object.keys(data.senderBreakdown).length - 10} more senders
            </div>
          )}
        </div>
      )}

      {/* Filter Chips + Export */}
      <div className="flex items-center gap-1.5 mb-4 flex-wrap">
        {(['all', 'seals', 'prices', 'experiments', 'interface1'] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`text-[10px] px-2.5 py-1 rounded-full uppercase tracking-[0.15em] font-medium transition-colors ${
              filter === f
                ? 'bg-white/[0.08] text-zinc-200 border border-white/[0.12]'
                : 'text-zinc-500 hover:text-zinc-400 border border-transparent'
            }`}
          >
            {f === 'all' ? `All (${data.totalOnChain})` :
             f === 'seals' ? `Seals (${sealCount})` :
             f === 'prices' ? `Prices (${successCount})` :
             f === 'interface1' ? `Mock/IF1 (${if1Count})` :
             `Experiments (${data.totalOnChain - sealCount - successCount})`}
          </button>
        ))}

        <div className="flex-1" />

        {/* Export Button */}
        <button
          onClick={() => setShowExport(!showExport)}
          className="text-[10px] px-2.5 py-1 rounded-full uppercase tracking-[0.15em] font-medium text-zinc-500 hover:text-zinc-300 border border-white/[0.06] hover:border-white/[0.12] transition-colors"
        >
          CSV Export
        </button>
      </div>

      {/* Export Panel */}
      <AnimatePresence>
        {showExport && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease }}
            className="overflow-hidden"
          >
            <div className="mb-4 p-3 rounded-lg border border-white/[0.06] bg-white/[0.02] space-y-2">
              <div className="text-[9px] uppercase tracking-[0.2em] text-zinc-600">SELECT COLUMNS</div>
              <div className="flex flex-wrap gap-1.5">
                {CSV_COLUMNS.map(col => (
                  <button
                    key={col.key}
                    onClick={() => {
                      const next = new Set(exportCols)
                      if (next.has(col.key)) next.delete(col.key)
                      else next.add(col.key)
                      setExportCols(next)
                    }}
                    className={`text-[9px] px-2 py-0.5 rounded border transition-colors ${
                      exportCols.has(col.key)
                        ? 'bg-cyan-400/10 border-cyan-400/30 text-cyan-400'
                        : 'border-white/[0.06] text-zinc-600 hover:text-zinc-400'
                    }`}
                  >
                    {col.label}
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setExportCols(new Set(CSV_COLUMNS.map(c => c.key)))}
                  className="text-[9px] text-zinc-500 hover:text-zinc-300 underline"
                >All</button>
                <button
                  onClick={() => setExportCols(new Set())}
                  className="text-[9px] text-zinc-500 hover:text-zinc-300 underline"
                >None</button>
                <div className="flex-1" />
                <span className="text-[10px] text-zinc-600">
                  {filtered.length} rows, {exportCols.size} columns, filter: {filter}
                </span>
                <button
                  onClick={handleExport}
                  disabled={exportCols.size === 0}
                  className="text-[10px] px-3 py-1 rounded bg-cyan-400/10 border border-cyan-400/30 text-cyan-400 hover:bg-cyan-400/20 transition-colors disabled:opacity-30"
                >
                  Download CSV
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Pagination Controls */}
      {filtered.length > PAGE_SIZES[0] && (
        <div className="flex items-center gap-3 mb-3 text-[10px]">
          <span className="text-zinc-600">Show:</span>
          {PAGE_SIZES.map(s => (
            <button
              key={s}
              onClick={() => setPageSize(s)}
              className={`px-1.5 py-0.5 rounded ${
                pageSize === s ? 'bg-white/[0.08] text-zinc-300' : 'text-zinc-600 hover:text-zinc-400'
              }`}
            >{s}</button>
          ))}
          <div className="flex-1" />
          {totalPages > 1 && (
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0}
                className="px-1.5 py-0.5 text-zinc-500 hover:text-zinc-300 disabled:opacity-30"
              >Prev</button>
              <span className="text-zinc-500 font-mono">{page + 1}/{totalPages}</span>
              <button
                onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                disabled={page >= totalPages - 1}
                className="px-1.5 py-0.5 text-zinc-500 hover:text-zinc-300 disabled:opacity-30"
              >Next</button>
            </div>
          )}
          <span className="text-zinc-600 font-mono">{filtered.length} total</span>
        </div>
      )}

      {/* Query List */}
      <div className="space-y-1.5">
        <AnimatePresence mode="popLayout">
          {paged.map((q, i) => (
            <motion.div
              key={q.queryId}
              layout
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.3, delay: i * 0.02, ease }}
            >
              <QueryRow
                query={q}
                expanded={expandedId === q.queryId}
                onToggle={() => setExpandedId(expandedId === q.queryId ? null : q.queryId)}
                onCopy={copyRow}
                isCopied={copiedRow === q.queryId}
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <div className="flex items-center gap-4 text-[10px] text-zinc-600 font-mono pt-3 mt-3 border-t border-white/[0.04]">
        <span>Tick: {data.tickRange.first.toLocaleString()} - {data.tickRange.current.toLocaleString()}</span>
        <span>Epoch: {data.epoch}</span>
        {data.scanDurationSeconds != null && <span>Scan: {data.scanDurationSeconds}s</span>}
      </div>
    </motion.div>
  )
}

// ─── Query Row ──────────────────────────────────────────────────────

function QueryRow({ query: q, expanded, onToggle, onCopy, isCopied }: {
  query: OnChainQuery
  expanded: boolean
  onToggle: () => void
  onCopy: (q: OnChainQuery, e: React.MouseEvent) => void
  isCopied: boolean
}) {
  const isSeal = q.isSeal
  const isSuccess = q.status === 'success'
  const isIF1 = q.interfaceIndex === 1

  const borderColor = isSeal
    ? 'border-purple-500/20 hover:border-purple-500/40'
    : isIF1
      ? 'border-sky-500/20 hover:border-sky-500/40'
      : isSuccess
        ? 'border-emerald-500/10 hover:border-emerald-500/30'
        : 'border-white/[0.04] hover:border-white/[0.08]'

  const bgColor = isSeal
    ? 'bg-purple-500/[0.03]'
    : isIF1
      ? 'bg-sky-500/[0.03]'
      : isSuccess
        ? 'bg-emerald-500/[0.02]'
        : 'bg-white/[0.01]'

  return (
    <div className={`border rounded-lg ${borderColor} ${bgColor} transition-colors cursor-pointer group/row relative`}>
      {/* Copy indicator */}
      {isCopied && (
        <div className="absolute top-1 right-12 text-[9px] text-cyan-400 bg-cyan-400/10 px-2 py-0.5 rounded z-10">
          COPIED
        </div>
      )}

      {/* Main Row */}
      <div className="flex items-center gap-3 px-3 py-2" onClick={onToggle}>
        {/* Status Dot */}
        <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
          isSuccess ? 'bg-emerald-400' :
          q.status === 'timeout' ? 'bg-amber-400/60' :
          q.status === 'pending' ? 'bg-cyan-400 animate-pulse' :
          'bg-zinc-600'
        }`} />

        {/* Seal Icon, Interface Badge, or Type */}
        {isSeal ? (
          <span className="text-purple-400 text-sm w-5 text-center flex-shrink-0" title={q.sealName}>
            {SEAL_ICONS[q.sealName!] ?? '\u2726'}
          </span>
        ) : isIF1 ? (
          <span className="text-sky-400 text-[9px] w-5 text-center flex-shrink-0 font-mono" title="Interface 1">
            I1
          </span>
        ) : (
          <span className="text-zinc-600 text-[10px] w-5 text-center flex-shrink-0 uppercase">
            {isSuccess ? 'PX' : '#'}
          </span>
        )}

        {/* Oracle Name / Interface Info */}
        <span className={`font-mono text-xs truncate ${
          isSeal ? 'text-purple-300' : isIF1 ? 'text-sky-300' : 'text-zinc-300'
        }`} style={{ minWidth: '120px', maxWidth: '160px' }}>
          {isIF1 ? (
            q.mockValue !== undefined ? `mock(${q.mockValue})` : 'mock(?)'
          ) : (
            q.oracle ?? q.interfaceName ?? `IF:${q.interfaceIndex}`
          )}
        </span>

        {/* Pair / Interface Label */}
        <span className="font-mono text-[11px] text-zinc-500 truncate" style={{ minWidth: '100px' }}>
          {isIF1 ? (
            <span className="text-sky-500/70">Mock Interface</span>
          ) : q.currency1 && q.currency2 ? (
            `${q.currency1}/${q.currency2}`
          ) : q.interfaceIndex > 1 ? (
            <span className="text-zinc-600">IF:{q.interfaceIndex}</span>
          ) : (
            '--'
          )}
        </span>

        {/* Price or Seal Name */}
        <span className="font-mono text-xs text-right flex-1">
          {isSeal ? (
            <span className="text-purple-400/80 text-[10px] uppercase tracking-[0.1em]">{q.sealName}</span>
          ) : q.reply?.price != null ? (
            <span className={isIF1 ? 'text-sky-400' : 'text-emerald-400'}>{formatPrice(q.reply.price)}</span>
          ) : (
            <span className="text-zinc-600 text-[10px]">no reply</span>
          )}
        </span>

        {/* Status Badge */}
        <StatusBadge status={q.status} />

        {/* Tick */}
        <span className="font-mono text-[10px] text-zinc-600 w-24 text-right flex-shrink-0">
          tick {q.tick.toLocaleString()}
        </span>

        {/* Copy Button */}
        <button
          onClick={(e) => onCopy(q, e)}
          className="text-[9px] text-zinc-700 hover:text-cyan-400 transition-colors flex-shrink-0 opacity-0 group-hover/row:opacity-100"
          title="Copy query data"
        >
          CPY
        </button>

        {/* Expand arrow */}
        <span className={`text-zinc-600 text-[10px] transition-transform ${expanded ? 'rotate-180' : ''}`}>
          {'\u25BC'}
        </span>
      </div>

      {/* Sender Address Row — always visible */}
      {q.senderIdentity && (
        <div className="flex items-center gap-2 px-3 pb-1.5 -mt-0.5" onClick={onToggle}>
          <span className="text-[8px] uppercase tracking-[0.15em] text-zinc-700 flex-shrink-0">from</span>
          <span className="font-mono text-[10px] text-zinc-500 truncate">{q.senderIdentity}</span>
        </div>
      )}

      {/* Expanded Details */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 pt-1 border-t border-white/[0.04] space-y-2 text-[11px]">
              {/* Sender Address — full width */}
              {q.senderIdentity && (
                <div className="rounded bg-white/[0.02] px-2 py-1.5 border border-white/[0.04]">
                  <span className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">SENDER</span>
                  <CopyableText value={q.senderIdentity} className="font-mono text-[11px] text-cyan-400/80" />
                </div>
              )}

              {/* Detail Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-x-6 gap-y-1.5">
                <Detail label="Query ID" value={q.queryId} mono copyable />
                <Detail label="Tick" value={q.tick.toLocaleString()} mono copyable />
                <Detail label="Type" value={q.type} />
                <Detail label="Status" value={q.status} />
                <Detail label="Flags" value={q.statusFlags.length > 0 ? q.statusFlags.join(', ') : 'none'} />
                <Detail label="Interface" value={`${q.interfaceIndex} (${q.interfaceName ?? INTERFACE_LABELS[q.interfaceIndex]?.name ?? 'Unknown'})`} />
                {q.subscriptionId != null && q.subscriptionId !== 0 && (
                  <Detail label="Subscription ID" value={String(q.subscriptionId)} mono />
                )}
                {q.queryTimestamp && <Detail label="Timestamp" value={q.queryTimestamp} mono />}
                {q.revealTick > 0 && <Detail label="Reveal Tick" value={q.revealTick.toLocaleString()} mono />}
                {q.totalCommits > 0 && <Detail label="Commits" value={`${q.agreeingCommits}/${q.totalCommits} agreeing`} />}

                {/* Interface 1 (Mock) specific */}
                {q.mockValue !== undefined && (
                  <Detail label="Mock Input" value={String(q.mockValue)} mono />
                )}

                {/* Reply data */}
                {q.reply && (
                  <>
                    <Detail label="Numerator" value={q.reply.numerator.toLocaleString()} mono />
                    <Detail label="Denominator" value={q.reply.denominator.toLocaleString()} mono />
                    <Detail label="Price" value={formatPrice(q.reply.price)} mono />
                  </>
                )}
                {q.senderPublicKey && (
                  <Detail label="Public Key (hex)" value={q.senderPublicKey} mono copyable />
                )}
                {isSeal && q.currency1 && (
                  <Detail label="Encrypted Seed" value={q.currency1} mono copyable />
                )}
                {isSeal && q.currency2 && (
                  <Detail label="Scripture" value={q.currency2.replace(/_/g, ' ')} />
                )}
                {q.firstSeen && <Detail label="First Seen" value={q.firstSeen} mono />}
                {q.lastUpdated && <Detail label="Last Updated" value={q.lastUpdated} mono />}
              </div>

              {/* Raw Hex Data — always show for transparency */}
              {(q.queryDataHex || q.replyDataHex) && (
                <div className="space-y-1 rounded bg-black/20 px-2 py-1.5 border border-white/[0.04]">
                  <span className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">RAW DATA</span>
                  {q.queryDataHex && (
                    <CopyableText
                      value={q.queryDataHex}
                      className="font-mono text-[10px] text-zinc-500 break-all"
                    />
                  )}
                  {q.replyDataHex && (
                    <CopyableText
                      value={q.replyDataHex}
                      className="font-mono text-[10px] text-amber-400/60 break-all"
                    />
                  )}
                </div>
              )}

              {/* Copy Full Query */}
              <div className="pt-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    navigator.clipboard.writeText(queryToClipboardText(q))
                  }}
                  className="text-[9px] px-2 py-1 rounded border border-white/[0.06] text-zinc-500 hover:text-zinc-300 hover:border-white/[0.12] transition-colors"
                >
                  Copy All Fields
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ─── Sub-Components ─────────────────────────────────────────────────

function SenderRow({ address, count, total }: { address: string; count: number; total: number }) {
  const [copied, setCopied] = useState(false)
  const pct = total > 0 ? ((count / total) * 100).toFixed(0) : '0'

  return (
    <div
      className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.02] border border-white/[0.04] group cursor-pointer"
      onClick={() => {
        navigator.clipboard.writeText(address).then(() => {
          setCopied(true)
          setTimeout(() => setCopied(false), 2000)
        })
      }}
    >
      <span className="font-mono text-[11px] text-zinc-400 truncate flex-1">{address}</span>
      <span className="text-[10px] text-zinc-500 flex-shrink-0">{count} queries ({pct}%)</span>
      <div className="w-20 h-1 rounded-full bg-white/[0.05] overflow-hidden flex-shrink-0">
        <div className="h-full rounded-full bg-cyan-400/40" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[9px] text-zinc-600 group-hover:text-zinc-400 transition-colors flex-shrink-0">
        {copied ? 'COPIED' : 'COPY'}
      </span>
    </div>
  )
}

function CopyableText({ value, className }: { value: string; className?: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <div
      className={`truncate cursor-pointer group ${className ?? ''}`}
      onClick={(e) => {
        e.stopPropagation()
        navigator.clipboard.writeText(value).then(() => {
          setCopied(true)
          setTimeout(() => setCopied(false), 2000)
        })
      }}
    >
      {value}
      <span className="ml-1 text-[8px] text-zinc-600 opacity-0 group-hover:opacity-100 transition-opacity">
        {copied ? 'COPIED' : 'COPY'}
      </span>
    </div>
  )
}

function Detail({ label, value, mono, copyable }: { label: string; value: string; mono?: boolean; copyable?: boolean }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = (e: React.MouseEvent) => {
    if (!copyable) return
    e.stopPropagation()
    navigator.clipboard.writeText(value).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className={copyable ? 'cursor-pointer group' : ''} onClick={handleCopy}>
      <span className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">{label}</span>
      <div className={`text-zinc-400 truncate ${mono ? 'font-mono' : ''}`}>
        {value}
        {copyable && (
          <span className="ml-1 text-[8px] text-zinc-600 opacity-0 group-hover:opacity-100 transition-opacity">
            {copied ? 'COPIED' : 'COPY'}
          </span>
        )}
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { bg: string; text: string }> = {
    success: { bg: 'bg-emerald-400/10', text: 'text-emerald-400' },
    timeout: { bg: 'bg-amber-400/10', text: 'text-amber-400' },
    pending: { bg: 'bg-cyan-400/10', text: 'text-cyan-400' },
    committed: { bg: 'bg-purple-400/10', text: 'text-purple-400' },
    unresolvable: { bg: 'bg-red-400/10', text: 'text-red-400' },
    unknown: { bg: 'bg-zinc-400/10', text: 'text-zinc-500' },
  }
  const fallback = { bg: 'bg-zinc-400/10', text: 'text-zinc-500' }
  const c = config[status] ?? fallback
  return (
    <span className={`text-[9px] px-1.5 py-0.5 rounded font-medium uppercase tracking-[0.1em] flex-shrink-0 ${c.bg} ${c.text}`}>
      {status}
    </span>
  )
}

function StatBadge({ label, value, color }: { label: string; value: string; color: string }) {
  const colorClasses: Record<string, string> = {
    cyan: 'text-cyan-400',
    amber: 'text-amber-400',
    purple: 'text-purple-400',
    emerald: 'text-emerald-400',
    sky: 'text-sky-400',
    zinc: 'text-zinc-400',
  }
  return (
    <div className="flex items-center gap-1.5">
      <span className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">{label}</span>
      <span className={`font-mono text-sm ${colorClasses[color] ?? 'text-zinc-400'}`}>{value}</span>
    </div>
  )
}

// ─── Formatters ─────────────────────────────────────────────────────

function formatPrice(price: number): string {
  if (price >= 1000) return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  if (price >= 1) return price.toFixed(4)
  return price.toFixed(8)
}

function formatTime(ts: string | null) {
  if (!ts) return '--'
  const diff = Date.now() - new Date(ts).getTime()
  if (diff < 60000) return `${Math.round(diff / 1000)}s ago`
  if (diff < 3600000) return `${Math.round(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.round(diff / 3600000)}h ago`
  return new Date(ts).toLocaleDateString()
}

function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  if (h > 0) return `${h}h ${m}m`
  if (m > 0) return `${m}m`
  return `${seconds}s`
}
