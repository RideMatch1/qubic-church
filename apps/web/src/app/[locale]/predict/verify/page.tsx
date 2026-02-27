'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { Shield, CheckCircle, XCircle, Hash, Link2, Activity, Loader2, ChevronRight, Download, ArrowLeft } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { formatQu } from '@/components/predict/helpers'
import { Skeleton } from '@/components/ui/skeleton'
import { VerifySkeleton } from '@/components/predict/skeletons'
import { usePagination, PaginationControls } from '@/components/predict/PaginationControls'

interface ChainStatus {
  totalEntries: number
  latestSequence: number
  latestHash: string | null
  latestEvent: string | null
  latestEntity: string | null
  latestTimestamp: string | null
  validation?: {
    valid: boolean
    brokenAt: number
    totalEntries: number
  }
}

interface SolvencyData {
  hasSolvencyProof: boolean
  proof?: {
    id: string
    merkleRoot: string
    totalUserBalance: number
    onChainBalance: number
    isSolvent: boolean
    accountCount: number
    tick: number
    epoch: number
    createdAt: string
  }
}

interface MarketSummary {
  id: string
  question: string
  pair: string
  status: string
  commitmentHash: string | null
  resolutionPrice: number | null
  winningOption: number | null
}

export default function VerifyPage() {
  const routeParams = useParams()
  const locale = (routeParams?.locale as string) ?? 'en'
  const [chainStatus, setChainStatus] = useState<ChainStatus | null>(null)
  const [solvency, setSolvency] = useState<SolvencyData | null>(null)
  const [markets, setMarkets] = useState<MarketSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [validating, setValidating] = useState(false)
  const marketPagination = usePagination(markets, 20)

  useEffect(() => {
    load()
  }, [])

  async function load() {
    setLoading(true)
    try {
      const [chainRes, solvencyRes, marketsRes] = await Promise.all([
        fetch('/api/predict/verify?type=chain'),
        fetch('/api/predict/verify?type=solvency'),
        fetch('/api/predict/markets'),
      ])

      if (chainRes.ok) setChainStatus(await chainRes.json())
      if (solvencyRes.ok) setSolvency(await solvencyRes.json())
      if (marketsRes.ok) {
        const data = await marketsRes.json()
        setMarkets(data.markets ?? [])
      }
    } catch (err) {
      console.error('Failed to load verification data:', err)
    } finally {
      setLoading(false)
    }
  }

  async function validateChain() {
    setValidating(true)
    try {
      const res = await fetch('/api/predict/verify?type=chain&validate=true')
      if (res.ok) setChainStatus(await res.json())
    } finally {
      setValidating(false)
    }
  }

  if (loading) {
    return (
      <div className="container max-w-5xl py-8 space-y-8">
        <Skeleton className="h-5 w-32" />
        <div>
          <Skeleton className="mb-2 h-8 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <VerifySkeleton />
      </div>
    )
  }

  return (
    <div className="container max-w-5xl py-8 space-y-8">
      {/* Back Link */}
      <Link
        href={`/${locale}/predict`}
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Markets
      </Link>

      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-8 h-8 text-emerald-500" />
          <h1 className="text-3xl font-bold">Provably Fair Verification</h1>
        </div>
        <p className="text-muted-foreground">
          Every action on QPredict is cryptographically tracked. Verify the integrity
          of the commitment chain, oracle attestations, and platform solvency.
        </p>
      </div>

      {/* Commitment Chain */}
      <section className="rounded-xl border border-border/50 bg-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Hash className="w-5 h-5 text-blue-500" />
            <h2 className="text-xl font-semibold">Commitment Chain</h2>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={validateChain}
            disabled={validating}
          >
            {validating ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <Shield className="w-4 h-4 mr-2" />
            )}
            Validate Integrity
          </Button>
        </div>

        {chainStatus && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Total Entries" value={chainStatus.totalEntries.toString()} />
            <StatCard label="Latest Sequence" value={`#${chainStatus.latestSequence}`} />
            <StatCard
              label="Latest Event"
              value={chainStatus.latestEvent?.replace('_', ' ') ?? 'None'}
            />
            <StatCard
              label="Latest Hash"
              value={chainStatus.latestHash ? chainStatus.latestHash.slice(0, 12) + '...' : 'None'}
              mono
            />
          </div>
        )}

        {chainStatus?.validation && (
          <div
            className={`flex items-center gap-3 p-4 rounded-lg ${
              chainStatus.validation.valid
                ? 'bg-emerald-500/10 border border-emerald-500/30'
                : 'bg-red-500/10 border border-red-500/30'
            }`}
          >
            {chainStatus.validation.valid ? (
              <>
                <CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" />
                <div>
                  <p className="font-medium text-emerald-500">Chain Integrity Verified</p>
                  <p className="text-sm text-muted-foreground">
                    All {chainStatus.validation.totalEntries} entries are correctly linked
                    and hash-verified.
                  </p>
                </div>
              </>
            ) : (
              <>
                <XCircle className="w-5 h-5 text-red-500 shrink-0" />
                <div>
                  <p className="font-medium text-red-500">Chain Integrity Broken!</p>
                  <p className="text-sm text-muted-foreground">
                    Break detected at sequence #{chainStatus.validation.brokenAt}
                  </p>
                </div>
              </>
            )}
          </div>
        )}
      </section>

      {/* Solvency Proof */}
      <section className="rounded-xl border border-border/50 bg-card p-6 space-y-4">
        <div className="flex items-center gap-3">
          <Activity className="w-5 h-5 text-amber-500" />
          <h2 className="text-xl font-semibold">Solvency Proof</h2>
        </div>

        {solvency?.hasSolvencyProof && solvency.proof ? (
          <>
            <div
              className={`flex items-center gap-3 p-4 rounded-lg ${
                solvency.proof.isSolvent
                  ? 'bg-emerald-500/10 border border-emerald-500/30'
                  : 'bg-red-500/10 border border-red-500/30'
              }`}
            >
              {solvency.proof.isSolvent ? (
                <CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" />
              ) : (
                <XCircle className="w-5 h-5 text-red-500 shrink-0" />
              )}
              <p className="font-medium">
                {solvency.proof.isSolvent
                  ? 'Platform is solvent — on-chain balance covers all user funds'
                  : 'WARNING: Platform may be insolvent'}
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                label="On-Chain Balance"
                value={formatQu(solvency.proof.onChainBalance)}
              />
              <StatCard
                label="User Balances"
                value={formatQu(solvency.proof.totalUserBalance)}
              />
              <StatCard label="Accounts" value={solvency.proof.accountCount.toString()} />
              <StatCard
                label="Merkle Root"
                value={solvency.proof.merkleRoot.slice(0, 12) + '...'}
                mono
              />
            </div>

            <p className="text-xs text-muted-foreground">
              Proof at tick {solvency.proof.tick} (epoch {solvency.proof.epoch}) —{' '}
              {new Date(solvency.proof.createdAt).toLocaleString()}
            </p>
          </>
        ) : (
          <p className="text-muted-foreground">
            No solvency proofs generated yet. Proofs are created periodically.
          </p>
        )}
      </section>

      {/* Market Verification */}
      <section className="rounded-xl border border-border/50 bg-card p-6 space-y-4">
        <div className="flex items-center gap-3">
          <Link2 className="w-5 h-5 text-purple-500" />
          <h2 className="text-xl font-semibold">Market Verification</h2>
        </div>

        {markets.length === 0 ? (
          <p className="text-muted-foreground">No markets found.</p>
        ) : (
          <>
            <div className="space-y-2">
              {marketPagination.paged.map((m) => (
                <Link
                  key={m.id}
                  href={`/${locale}/predict/verify/${m.id}`}
                  className="flex items-center justify-between p-4 rounded-lg hover:bg-accent/50 transition-colors border border-transparent hover:border-border/50"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{m.question}</p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                      <span className="uppercase">{m.pair}</span>
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                          m.status === 'resolved'
                            ? 'bg-emerald-500/10 text-emerald-500'
                            : m.status === 'active'
                              ? 'bg-blue-500/10 text-blue-500'
                              : 'bg-muted text-muted-foreground'
                        }`}
                      >
                        {m.status}
                      </span>
                      {m.commitmentHash && (
                        <span className="font-mono opacity-70">
                          {m.commitmentHash.slice(0, 8)}...
                        </span>
                      )}
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />
                </Link>
              ))}
            </div>
            <PaginationControls
              page={marketPagination.page}
              totalPages={marketPagination.totalPages}
              onPageChange={marketPagination.setPage}
              className="mt-4"
            />
          </>
        )}
      </section>
    </div>
  )
}

function StatCard({
  label,
  value,
  mono,
}: {
  label: string
  value: string
  mono?: boolean
}) {
  return (
    <div className="rounded-lg bg-accent/30 p-3">
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      <p className={`text-sm font-semibold ${mono ? 'font-mono' : ''}`}>{value}</p>
    </div>
  )
}
