'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import {
  Database, Download, Hash, Shield, Activity, Eye,
  ChevronRight, Search, FileJson, Clock,
  CheckCircle, XCircle, TrendingUp, Users, ArrowLeft
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { formatQu, formatDateTime, anonymizeAddress } from '@/components/predict/helpers'
import { Skeleton } from '@/components/ui/skeleton'
import { HistorySkeleton } from '@/components/predict/skeletons'
import { usePagination, PaginationControls } from '@/components/predict/PaginationControls'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ChainEntry {
  sequence: number
  eventType: string
  entityId: string
  payloadHash: string
  prevHash: string
  chainHash: string
  payload: Record<string, unknown>
  timestamp: string
}

interface BetEscrow {
  address: string
  status: string
  depositDetectedAt: string | null
  depositAmountQu: number | null
  joinBetTxId: string | null
  joinBetTick: number | null
  payoutDetectedAt: string | null
  payoutAmountQu: number | null
  sweepTxId: string | null
  sweepTick: number | null
  createdAt: string
  expiresAt: string
}

interface MarketHistory {
  id: string
  pair: string
  question: string
  status: string
  totalPool: number
  yesSlots: number
  noSlots: number
  resolutionPrice: number | null
  winningOption: number | null
  commitmentHash: string | null
  createdAt: string
  resolvedAt: string | null
  bets: Array<{
    id: string
    userAddress: string
    option: number
    optionLabel: string
    slots: number
    amountQu: number
    status: string
    payoutQu: number | null
    commitmentHash: string | null
    txHash: string | null
    createdAt: string
    escrow?: BetEscrow | null
  }>
  oracleAttestations: Array<{
    source: string
    price: number
    timestamp: string
    attestationHash: string
  }>
  chainEntries: number
}

interface PlatformStats {
  totalMarkets: number
  activeMarkets: number
  resolvedMarkets: number
  totalVolume: number
  totalBets: number
  totalUsers: number
  totalPaidOut: number
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function HistoryPage() {
  const routeParams = useParams()
  const locale = (routeParams?.locale as string) ?? 'en'
  const [tab, setTab] = useState<'overview' | 'chain' | 'markets'>('overview')
  const [stats, setStats] = useState<PlatformStats | null>(null)
  const [chainEntries, setChainEntries] = useState<ChainEntry[]>([])
  const [chainTotal, setChainTotal] = useState(0)
  const [markets, setMarkets] = useState<MarketHistory[]>([])
  const [loading, setLoading] = useState(true)
  const [searchAddress, setSearchAddress] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setLoading(true)
    try {
      const [statsRes, chainRes, marketsRes] = await Promise.all([
        fetch('/api/predict/stats'),
        fetch('/api/predict/history?type=chain'),
        fetch('/api/predict/history?type=markets'),
      ])

      if (statsRes.ok) setStats(await statsRes.json())
      if (chainRes.ok) {
        const data = await chainRes.json()
        setChainEntries(data.entries ?? [])
        setChainTotal(data.totalEntries ?? 0)
      }
      if (marketsRes.ok) {
        const data = await marketsRes.json()
        setMarkets(data.markets ?? [])
      }
    } catch (err) {
      console.error('Failed to load history data:', err)
    } finally {
      setLoading(false)
    }
  }

  function downloadJson(url: string, fallbackName: string) {
    const a = document.createElement('a')
    a.href = url + (url.includes('?') ? '&' : '?') + 'download=true'
    a.download = fallbackName
    a.click()
  }

  if (loading) {
    return (
      <div className="container max-w-6xl py-8 space-y-6">
        <Skeleton className="h-5 w-32" />
        <div>
          <Skeleton className="mb-2 h-8 w-48" />
          <Skeleton className="h-4 w-96" />
        </div>
        <HistorySkeleton />
      </div>
    )
  }

  return (
    <div className="container max-w-6xl py-8 space-y-6">
      {/* Back Link */}
      <Link
        href={`/${locale}/predict`}
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Markets
      </Link>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Database className="w-8 h-8 text-blue-500" />
            <h1 className="text-3xl font-bold">Public History</h1>
          </div>
          <p className="text-muted-foreground">
            Every action on QPredict is recorded, verifiable, and downloadable.
            100% transparency, zero trust required.
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => downloadJson('/api/predict/history?type=full', 'qpredict-full-export.json')}
        >
          <Download className="w-4 h-4 mr-2" />
          Export All
        </Button>
      </div>

      {/* Platform Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
          <StatCard icon={<Activity className="w-4 h-4 text-emerald-500" />} label="Markets" value={stats.totalMarkets.toString()} />
          <StatCard icon={<TrendingUp className="w-4 h-4 text-blue-500" />} label="Active" value={stats.activeMarkets.toString()} />
          <StatCard icon={<CheckCircle className="w-4 h-4 text-green-500" />} label="Resolved" value={stats.resolvedMarkets.toString()} />
          <StatCard icon={<Users className="w-4 h-4 text-purple-500" />} label="Users" value={stats.totalUsers.toString()} />
          <StatCard icon={<Hash className="w-4 h-4 text-amber-500" />} label="Bets" value={stats.totalBets.toString()} />
          <StatCard icon={<Database className="w-4 h-4 text-cyan-500" />} label="Volume" value={formatQu(stats.totalVolume) + ' QU'} />
          <StatCard icon={<Shield className="w-4 h-4 text-emerald-500" />} label="Chain" value={chainTotal.toString() + ' entries'} />
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border/50 pb-2">
        {(['overview', 'chain', 'markets'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              tab === t
                ? 'bg-accent text-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {t === 'overview' ? 'Overview' : t === 'chain' ? 'Commitment Chain' : 'Market History'}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === 'overview' && (
        <OverviewTab
          markets={markets}
          chainEntries={chainEntries}
          searchAddress={searchAddress}
          setSearchAddress={setSearchAddress}
          onDownload={downloadJson}
          locale={locale}
        />
      )}
      {tab === 'chain' && (
        <ChainTab
          entries={chainEntries}
          total={chainTotal}
          onDownload={downloadJson}
        />
      )}
      {tab === 'markets' && (
        <MarketsTab
          markets={markets}
          onDownload={downloadJson}
          locale={locale}
        />
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Overview Tab
// ---------------------------------------------------------------------------

function OverviewTab({
  markets,
  chainEntries,
  searchAddress,
  setSearchAddress,
  onDownload,
  locale,
}: {
  markets: MarketHistory[]
  chainEntries: ChainEntry[]
  searchAddress: string
  setSearchAddress: (s: string) => void
  onDownload: (url: string, name: string) => void
  locale: string
}) {
  const [marketSearch, setMarketSearch] = useState('')
  const filteredResolved = markets.filter((m) => m.status === 'resolved').filter((m) => {
    if (!marketSearch) return true
    const q = marketSearch.toLowerCase()
    return (
      m.question.toLowerCase().includes(q) ||
      m.pair.toLowerCase().includes(q) ||
      m.id.toLowerCase().includes(q)
    )
  })

  return (
    <div className="space-y-6">
      {/* User Lookup */}
      <section className="rounded-xl border border-border/50 bg-card p-5 space-y-3">
        <h2 className="font-semibold flex items-center gap-2">
          <Search className="w-4 h-4 text-blue-500" /> Look Up User History
        </h2>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Enter Qubic address (60 uppercase letters)..."
            value={searchAddress}
            onChange={(e) => setSearchAddress(e.target.value.toUpperCase())}
            className="flex-1 rounded-lg border border-border/50 bg-background px-3 py-2 text-sm font-mono placeholder:text-muted-foreground"
            maxLength={60}
          />
          <Button
            variant="outline"
            size="sm"
            disabled={searchAddress.length !== 60}
            onClick={() => onDownload(
              `/api/predict/history?type=bets&address=${searchAddress}`,
              `qpredict-bets-${searchAddress.slice(0, 8)}.json`,
            )}
          >
            <Download className="w-4 h-4 mr-2" /> Bets
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={searchAddress.length !== 60}
            onClick={() => onDownload(
              `/api/predict/history?type=transactions&address=${searchAddress}`,
              `qpredict-txs-${searchAddress.slice(0, 8)}.json`,
            )}
          >
            <Download className="w-4 h-4 mr-2" /> Transactions
          </Button>
        </div>
      </section>

      {/* Download Center */}
      <section className="rounded-xl border border-border/50 bg-card p-5 space-y-3">
        <h2 className="font-semibold flex items-center gap-2">
          <FileJson className="w-4 h-4 text-amber-500" /> Download Center
        </h2>
        <p className="text-sm text-muted-foreground">
          Download complete datasets as JSON for independent verification.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <DownloadButton
            label="Full Chain"
            desc="All commitment hashes"
            onClick={() => onDownload('/api/predict/history?type=chain', 'qpredict-chain.json')}
          />
          <DownloadButton
            label="All Markets"
            desc="Markets + bets + proofs"
            onClick={() => onDownload('/api/predict/history?type=markets', 'qpredict-markets.json')}
          />
          <DownloadButton
            label="Oracle Data"
            desc="All attestations"
            onClick={() => onDownload('/api/predict/history?type=attestations', 'qpredict-attestations.json')}
          />
          <DownloadButton
            label="Solvency Proofs"
            desc="Merkle tree proofs"
            onClick={() => onDownload('/api/predict/history?type=proofs', 'qpredict-proofs.json')}
          />
        </div>
      </section>

      {/* Recent Activity */}
      <section className="rounded-xl border border-border/50 bg-card p-5 space-y-3">
        <h2 className="font-semibold flex items-center gap-2">
          <Clock className="w-4 h-4 text-cyan-500" /> Recent Activity
        </h2>
        <div className="space-y-1">
          {chainEntries.slice(-10).reverse().map((entry) => (
            <div
              key={entry.sequence}
              className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-accent/30 text-sm"
            >
              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground w-8">#{entry.sequence}</span>
                <EventBadge type={entry.eventType} />
                <span className="font-mono text-xs text-muted-foreground">
                  {entry.entityId.slice(0, 16)}...
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-mono text-[10px] text-muted-foreground">
                  {entry.chainHash.slice(0, 12)}...
                </span>
                <span className="text-xs text-muted-foreground">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Resolved Markets */}
      <section className="rounded-xl border border-border/50 bg-card p-5 space-y-3">
        <h2 className="font-semibold flex items-center gap-2">
          <Shield className="w-4 h-4 text-emerald-500" /> Resolved Markets
        </h2>
        <input
          type="text"
          placeholder="Search markets by question, pair, or ID..."
          value={marketSearch}
          onChange={(e) => setMarketSearch(e.target.value)}
          className="w-full rounded-lg border border-border/50 bg-background px-3 py-2 text-sm placeholder:text-muted-foreground"
        />
        {filteredResolved.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            {marketSearch ? 'No markets match your search.' : 'No resolved markets yet.'}
          </p>
        ) : (
          <div className="space-y-2">
            {filteredResolved.map((m) => (
              <div
                key={m.id}
                className="flex items-center justify-between p-3 rounded-lg bg-accent/20"
              >
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-sm truncate">{m.question}</p>
                  <div className="flex flex-wrap items-center gap-3 mt-1 text-xs text-muted-foreground">
                    <span className="uppercase">{m.pair}</span>
                    <span>Pool: {formatQu(m.totalPool)} QU</span>
                    <span>
                      Winner: {m.winningOption === 0 ? 'YES' : 'NO'}
                      {m.resolutionPrice !== null && ` at $${m.resolutionPrice.toLocaleString()}`}
                    </span>
                    <span>{m.bets.length} bets</span>
                    {(() => {
                      const swept = m.bets.filter((b) => b.escrow?.status === 'swept' || b.escrow?.status === 'completed').length
                      const lost = m.bets.filter((b) => b.escrow?.status === 'lost').length
                      return (
                        <>
                          {swept > 0 && <span className="text-green-500">{swept} paid out</span>}
                          {lost > 0 && <span className="text-red-400">{lost} lost</span>}
                        </>
                      )
                    })()}
                    {m.resolvedAt && <span>{formatDateTime(m.resolvedAt)}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Link href={`/${locale}/predict/verify/${m.id}`}>
                    <Button variant="ghost" size="sm">
                      <Shield className="w-3 h-3 mr-1" /> Verify
                    </Button>
                  </Link>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDownload(
                      `/api/predict/history?type=market&id=${m.id}`,
                      `qpredict-market-${m.id}.json`,
                    )}
                  >
                    <Download className="w-3 h-3 mr-1" /> Export
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Chain Tab
// ---------------------------------------------------------------------------

function ChainTab({
  entries,
  total,
  onDownload,
}: {
  entries: ChainEntry[]
  total: number
  onDownload: (url: string, name: string) => void
}) {
  const [expanded, setExpanded] = useState<number | null>(null)
  const reversed = [...entries].reverse()
  const { page, setPage, totalPages, paged } = usePagination(reversed, 20)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {total} entries in commitment chain. Each entry is cryptographically linked to the previous.
        </p>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onDownload('/api/predict/history?type=chain', 'qpredict-chain.json')}
        >
          <Download className="w-4 h-4 mr-2" /> Download Full Chain
        </Button>
      </div>

      <div className="rounded-xl border border-border/50 bg-card overflow-hidden">
        {/* Header */}
        <div className="grid grid-cols-[60px_120px_1fr_120px_100px] gap-2 p-3 border-b border-border/30 text-xs font-medium text-muted-foreground">
          <span>#</span>
          <span>Event</span>
          <span>Entity / Hash</span>
          <span>Chain Hash</span>
          <span>Time</span>
        </div>

        {/* Entries (newest first, paginated) */}
        {paged.map((entry) => (
          <div key={entry.sequence}>
            <div
              className="grid grid-cols-[60px_120px_1fr_120px_100px] gap-2 p-3 hover:bg-accent/30 cursor-pointer text-sm items-center"
              onClick={() => setExpanded(expanded === entry.sequence ? null : entry.sequence)}
            >
              <span className="text-muted-foreground">#{entry.sequence}</span>
              <EventBadge type={entry.eventType} />
              <span className="font-mono text-xs truncate">{entry.entityId}</span>
              <span className="font-mono text-[10px] text-muted-foreground">
                {entry.chainHash.slice(0, 12)}...
              </span>
              <span className="text-xs text-muted-foreground">
                {new Date(entry.timestamp).toLocaleTimeString()}
              </span>
            </div>

            {expanded === entry.sequence && (
              <div className="px-4 pb-4 space-y-2 text-xs bg-accent/10">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-muted-foreground mb-1">Previous Hash</p>
                    <p className="font-mono break-all">{entry.prevHash}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground mb-1">Chain Hash</p>
                    <p className="font-mono break-all">{entry.chainHash}</p>
                  </div>
                </div>
                <div>
                  <p className="text-muted-foreground mb-1">Payload Hash</p>
                  <p className="font-mono break-all">{entry.payloadHash}</p>
                </div>
                <div>
                  <p className="text-muted-foreground mb-1">Payload</p>
                  <pre className="font-mono text-[10px] bg-background/50 p-2 rounded overflow-x-auto">
                    {JSON.stringify(entry.payload, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <PaginationControls
        page={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />

      {/* Verification Note */}
      <div className="rounded-lg border border-border/30 bg-accent/10 p-4 text-xs text-muted-foreground space-y-2">
        <p className="font-medium text-foreground flex items-center gap-2">
          <Eye className="w-4 h-4" /> How to Verify
        </p>
        <p>
          For each entry: <code className="bg-background px-1 rounded">chainHash = SHA-256(sequence | eventType | entityId | SHA-256(canonicalJSON(payload)) | prevHash)</code>
        </p>
        <p>
          Genesis entry has <code className="bg-background px-1 rounded">prevHash = 0000...0000</code> (64 zeros).
          If any entry is tampered with, all subsequent chain hashes break.
        </p>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Markets Tab
// ---------------------------------------------------------------------------

function MarketsTab({
  markets,
  onDownload,
  locale,
}: {
  markets: MarketHistory[]
  onDownload: (url: string, name: string) => void
  locale: string
}) {
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [marketSearch, setMarketSearch] = useState('')
  const filtered = markets.filter((m) => {
    if (!marketSearch) return true
    const q = marketSearch.toLowerCase()
    return (
      m.question.toLowerCase().includes(q) ||
      m.pair.toLowerCase().includes(q) ||
      m.id.toLowerCase().includes(q)
    )
  })
  const { page, setPage, totalPages, paged, resetPage } = usePagination(filtered, 10)

  // Reset page when search changes
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { resetPage() }, [marketSearch])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {filtered.length} of {markets.length} markets. Click to expand full details.
        </p>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onDownload('/api/predict/history?type=markets', 'qpredict-all-markets.json')}
        >
          <Download className="w-4 h-4 mr-2" /> Download All
        </Button>
      </div>

      <input
        type="text"
        placeholder="Search markets by question, pair, or ID..."
        value={marketSearch}
        onChange={(e) => setMarketSearch(e.target.value)}
        className="w-full rounded-lg border border-border/50 bg-background px-3 py-2 text-sm placeholder:text-muted-foreground"
      />

      {paged.map((m) => (
        <div
          key={m.id}
          className="rounded-xl border border-border/50 bg-card overflow-hidden"
        >
          {/* Market Header */}
          <div
            className="flex items-center justify-between p-4 cursor-pointer hover:bg-accent/30"
            onClick={() => setExpandedId(expandedId === m.id ? null : m.id)}
          >
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="uppercase text-xs font-medium text-muted-foreground">{m.pair}</span>
                <StatusBadge status={m.status} />
                {m.winningOption !== null && (
                  <span className={`text-xs font-medium ${m.winningOption === 0 ? 'text-emerald-500' : 'text-red-500'}`}>
                    {m.winningOption === 0 ? 'YES' : 'NO'} wins
                  </span>
                )}
              </div>
              <p className="font-medium">{m.question}</p>
              <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                <span>Pool: {formatQu(m.totalPool)} QU</span>
                <span>YES: {m.yesSlots} | NO: {m.noSlots}</span>
                <span>{m.bets.length} bets</span>
                <span>{m.chainEntries} chain entries</span>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  onDownload(
                    `/api/predict/history?type=market&id=${m.id}`,
                    `qpredict-market-${m.id}.json`,
                  )
                }}
              >
                <Download className="w-3 h-3" />
              </Button>
              <ChevronRight
                className={`w-4 h-4 transition-transform ${expandedId === m.id ? 'rotate-90' : ''}`}
              />
            </div>
          </div>

          {/* Expanded Details */}
          {expandedId === m.id && (
            <div className="border-t border-border/30 p-4 space-y-4">
              {/* Market Details */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div>
                  <p className="text-xs text-muted-foreground">Created</p>
                  <p>{formatDateTime(m.createdAt)}</p>
                </div>
                {m.resolvedAt && (
                  <div>
                    <p className="text-xs text-muted-foreground">Resolved</p>
                    <p>{formatDateTime(m.resolvedAt)}</p>
                  </div>
                )}
                {m.resolutionPrice !== null && (
                  <div>
                    <p className="text-xs text-muted-foreground">Resolution Price</p>
                    <p className="font-mono">${m.resolutionPrice.toLocaleString()}</p>
                  </div>
                )}
                <div>
                  <p className="text-xs text-muted-foreground">Commitment Hash</p>
                  <p className="font-mono text-[10px] break-all">
                    {m.commitmentHash ?? 'N/A'}
                  </p>
                </div>
              </div>

              {/* Bets with Escrow Lifecycle */}
              <div>
                <h3 className="text-sm font-semibold mb-2">Bets ({m.bets.length})</h3>
                <div className="space-y-2">
                  {m.bets.map((b) => (
                    <div
                      key={b.id}
                      className="rounded-lg bg-accent/20 overflow-hidden"
                    >
                      {/* Bet Header */}
                      <div className="flex items-center justify-between p-3 text-sm">
                        <div className="flex items-center gap-3">
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                              b.option === 0
                                ? 'bg-emerald-500/10 text-emerald-500'
                                : 'bg-red-500/10 text-red-500'
                            }`}
                          >
                            {b.optionLabel}
                          </span>
                          <span>{b.slots} slots</span>
                          <span className="text-muted-foreground">{anonymizeAddress(b.userAddress)}</span>
                          {b.commitmentHash && (
                            <CheckCircle className="w-3 h-3 text-emerald-500" />
                          )}
                        </div>
                        <div className="flex items-center gap-3">
                          <span>{formatQu(b.amountQu)} QU</span>
                          <span
                            className={`text-xs ${
                              b.status === 'won'
                                ? 'text-emerald-500'
                                : b.status === 'lost'
                                  ? 'text-red-500'
                                  : 'text-muted-foreground'
                            }`}
                          >
                            {b.status}
                            {b.payoutQu ? ` (+${formatQu(b.payoutQu)})` : ''}
                          </span>
                        </div>
                      </div>

                      {/* Escrow Lifecycle */}
                      {b.escrow && (
                        <div className="border-t border-border/20 px-3 py-2 bg-background/30">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                              Transaction Trail
                            </span>
                            <EscrowStatusBadge status={b.escrow.status} />
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-xs">
                            {/* Escrow Address */}
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Escrow</span>
                              <span className="font-mono">
                                {b.escrow.address.slice(0, 8)}...{b.escrow.address.slice(-4)}
                              </span>
                            </div>

                            {/* Deposit */}
                            {b.escrow.depositDetectedAt && (
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Deposit</span>
                                <span>
                                  {b.escrow.depositAmountQu != null && `${formatQu(b.escrow.depositAmountQu)} QU · `}
                                  {formatDateTime(b.escrow.depositDetectedAt)}
                                </span>
                              </div>
                            )}

                            {/* JoinBet TX */}
                            {b.escrow.joinBetTxId && (
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">JoinBet TX</span>
                                <span className="font-mono">
                                  {b.escrow.joinBetTxId.slice(0, 12)}...
                                  {b.escrow.joinBetTick != null && (
                                    <span className="text-muted-foreground ml-1">
                                      tick {b.escrow.joinBetTick}
                                    </span>
                                  )}
                                </span>
                              </div>
                            )}

                            {/* Payout */}
                            {b.escrow.payoutDetectedAt && (
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Payout</span>
                                <span>
                                  {b.escrow.payoutAmountQu != null && `${formatQu(b.escrow.payoutAmountQu)} QU · `}
                                  {formatDateTime(b.escrow.payoutDetectedAt)}
                                </span>
                              </div>
                            )}

                            {/* Sweep TX */}
                            {b.escrow.sweepTxId && (
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Sweep TX</span>
                                <span className="font-mono">
                                  {b.escrow.sweepTxId.slice(0, 12)}...
                                  {b.escrow.sweepTick != null && (
                                    <span className="text-muted-foreground ml-1">
                                      tick {b.escrow.sweepTick}
                                    </span>
                                  )}
                                </span>
                              </div>
                            )}

                            {/* Created */}
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Created</span>
                              <span>{formatDateTime(b.escrow.createdAt)}</span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Oracle Attestations */}
              {m.oracleAttestations.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold mb-2">Oracle Attestations</h3>
                  <div className="space-y-1">
                    {m.oracleAttestations.map((a, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between p-2 rounded bg-accent/20 text-sm"
                      >
                        <span className="capitalize">{a.source}</span>
                        <div className="text-right">
                          <span className="font-mono">${a.price.toLocaleString()}</span>
                          <span className="text-[10px] font-mono text-muted-foreground ml-2">
                            {a.attestationHash.slice(0, 12)}...
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-2 border-t border-border/30">
                <Link href={`/${locale}/predict/verify/${m.id}`}>
                  <Button variant="outline" size="sm">
                    <Shield className="w-3 h-3 mr-1" /> Verify Market
                  </Button>
                </Link>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onDownload(
                    `/api/predict/history?type=market&id=${m.id}`,
                    `qpredict-market-${m.id}.json`,
                  )}
                >
                  <Download className="w-3 h-3 mr-1" /> Download Full History
                </Button>
              </div>
            </div>
          )}
        </div>
      ))}

      <PaginationControls
        page={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />
    </div>
  )
}

// ---------------------------------------------------------------------------
// Shared Components
// ---------------------------------------------------------------------------

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="rounded-lg bg-accent/30 p-3">
      <div className="flex items-center gap-2 mb-1">
        {icon}
        <span className="text-xs text-muted-foreground">{label}</span>
      </div>
      <p className="text-sm font-semibold">{value}</p>
    </div>
  )
}

function EventBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    market_create: 'bg-blue-500/10 text-blue-500',
    bet_place: 'bg-purple-500/10 text-purple-500',
    bet_confirm: 'bg-emerald-500/10 text-emerald-500',
    market_resolve: 'bg-amber-500/10 text-amber-500',
    payout: 'bg-green-500/10 text-green-500',
    deposit: 'bg-cyan-500/10 text-cyan-500',
    withdrawal: 'bg-red-500/10 text-red-500',
    solvency_proof: 'bg-indigo-500/10 text-indigo-500',
  }

  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${colors[type] ?? 'bg-zinc-500/10 text-zinc-400'}`}>
      {type.replace('_', ' ')}
    </span>
  )
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    active: 'bg-emerald-500/10 text-emerald-500',
    closed: 'bg-amber-500/10 text-amber-500',
    resolved: 'bg-zinc-500/10 text-zinc-400',
    cancelled: 'bg-red-500/10 text-red-500',
    draft: 'bg-zinc-500/10 text-zinc-500',
  }

  return (
    <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${colors[status] ?? 'bg-zinc-500/10 text-zinc-400'}`}>
      {status}
    </span>
  )
}

function EscrowStatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    awaiting_deposit: 'bg-yellow-500/10 text-yellow-500',
    deposit_detected: 'bg-cyan-500/10 text-cyan-500',
    joining_sc: 'bg-blue-500/10 text-blue-500',
    active_in_sc: 'bg-emerald-500/10 text-emerald-500',
    won_awaiting_sweep: 'bg-green-500/10 text-green-500',
    swept: 'bg-green-500/10 text-green-400',
    completed: 'bg-green-500/10 text-green-400',
    lost: 'bg-red-500/10 text-red-500',
    expired: 'bg-zinc-500/10 text-zinc-400',
    refunded: 'bg-amber-500/10 text-amber-500',
  }

  const labels: Record<string, string> = {
    awaiting_deposit: 'Awaiting Deposit',
    deposit_detected: 'Deposit Detected',
    joining_sc: 'Joining SC',
    active_in_sc: 'Active in SC',
    won_awaiting_sweep: 'Won - Sweeping',
    swept: 'Swept',
    completed: 'Completed',
    lost: 'Lost',
    expired: 'Expired',
    refunded: 'Refunded',
  }

  return (
    <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${colors[status] ?? 'bg-zinc-500/10 text-zinc-400'}`}>
      {labels[status] ?? status}
    </span>
  )
}

function DownloadButton({
  label,
  desc,
  onClick,
}: {
  label: string
  desc: string
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-center gap-1 p-4 rounded-lg border border-border/30 hover:border-border hover:bg-accent/30 transition-colors"
    >
      <Download className="w-5 h-5 text-muted-foreground" />
      <span className="text-sm font-medium">{label}</span>
      <span className="text-[10px] text-muted-foreground">{desc}</span>
    </button>
  )
}
