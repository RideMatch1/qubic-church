'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import {
  Shield, CheckCircle, XCircle, Hash, ArrowLeft,
  Download, Loader2, Eye, Database, Coins
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { formatQu } from '@/components/predict/helpers'

interface MarketVerification {
  market: {
    id: string
    pair: string
    question: string
    resolutionType: string
    resolutionTarget: number
    resolutionTargetHigh: number | null
    status: string
    commitmentHash: string | null
    resolutionPrice: number | null
    winningOption: number | null
    resolvedAt: string | null
  }
  oracleAttestations: Array<{
    source: string
    price: number
    timestamp: string
    attestationHash: string
  }>
  chainEntries: number
  bets: Array<{
    betId: string
    userAddress: string
    option: number
    slots: number
    amountQu: number
    commitmentHash: string | null
    hasNonce: boolean
    status: string
    payoutQu: number | null
    chainEntries: number
  }>
  proofAvailable: boolean
}

interface ProofVerification {
  package: Record<string, unknown>
  verification: {
    valid: boolean
    checks: Array<{
      name: string
      passed: boolean
      detail?: string
    }>
  }
}

export default function MarketVerifyPage() {
  const params = useParams()
  const locale = (params?.locale as string) ?? 'en'
  const marketId = params.id as string

  const [data, setData] = useState<MarketVerification | null>(null)
  const [proofResult, setProofResult] = useState<ProofVerification | null>(null)
  const [loading, setLoading] = useState(true)
  const [verifying, setVerifying] = useState(false)

  useEffect(() => {
    loadData()
  }, [marketId])

  async function loadData() {
    setLoading(true)
    try {
      const res = await fetch(`/api/predict/verify?type=market&id=${marketId}`)
      if (res.ok) setData(await res.json())
    } finally {
      setLoading(false)
    }
  }

  async function verifyProof() {
    setVerifying(true)
    try {
      const res = await fetch(
        `/api/predict/verify?type=proof&id=${marketId}&verify=true`,
      )
      if (res.ok) setProofResult(await res.json())
    } finally {
      setVerifying(false)
    }
  }

  async function downloadProof() {
    const res = await fetch(`/api/predict/verify?type=proof&id=${marketId}`)
    if (!res.ok) return
    const pkg = await res.json()
    const blob = new Blob([JSON.stringify(pkg, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `qpredict-proof-${marketId}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!data) {
    return (
      <div className="container max-w-4xl py-8">
        <p className="text-muted-foreground">Market not found.</p>
      </div>
    )
  }

  const m = data.market

  return (
    <div className="container max-w-4xl py-8 space-y-6">
      {/* Back Link */}
      <Link
        href={`/${locale}/predict/verify`}
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Verification Dashboard
      </Link>

      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-7 h-7 text-emerald-500" />
          <h1 className="text-2xl font-bold">Market Verification</h1>
        </div>
        <p className="text-lg">{m.question}</p>
        <p className="text-sm text-muted-foreground mt-1">
          {m.pair.toUpperCase()} | {m.resolutionType} | Target: ${m.resolutionTarget.toLocaleString()}
          {m.resolutionTargetHigh && ` - $${m.resolutionTargetHigh.toLocaleString()}`}
        </p>
      </div>

      {/* Market Commitment */}
      <section className="rounded-xl border border-border/50 bg-card p-5 space-y-3">
        <h2 className="font-semibold flex items-center gap-2">
          <Hash className="w-4 h-4 text-blue-500" /> Market Commitment
        </h2>
        {m.commitmentHash ? (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-500" />
              <span className="text-sm">Market parameters cryptographically bound at creation</span>
            </div>
            <p className="text-xs font-mono bg-accent/30 p-2 rounded break-all">
              {m.commitmentHash}
            </p>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            No commitment hash (market created before provably fair system)
          </p>
        )}
      </section>

      {/* Oracle Attestations */}
      <section className="rounded-xl border border-border/50 bg-card p-5 space-y-3">
        <h2 className="font-semibold flex items-center gap-2">
          <Eye className="w-4 h-4 text-amber-500" /> Oracle Attestations
        </h2>
        {data.oracleAttestations.length > 0 ? (
          <div className="space-y-2">
            {data.oracleAttestations.map((att, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 rounded-lg bg-accent/20"
              >
                <div>
                  <span className="font-medium text-sm capitalize">{att.source}</span>
                  <span className="text-xs text-muted-foreground ml-2">
                    {new Date(att.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="text-right">
                  <p className="font-mono font-semibold">${att.price.toLocaleString()}</p>
                  <p className="text-[10px] font-mono text-muted-foreground">
                    {att.attestationHash.slice(0, 16)}...
                  </p>
                </div>
              </div>
            ))}
            {m.resolutionPrice !== null && (
              <p className="text-sm text-muted-foreground">
                Median resolution price: <strong>${m.resolutionPrice.toLocaleString()}</strong>
                {' | '}
                Winner: <strong>{m.winningOption === 0 ? 'YES' : 'NO'}</strong>
              </p>
            )}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            No oracle attestations recorded for this market.
          </p>
        )}
      </section>

      {/* Bet Commitments */}
      <section className="rounded-xl border border-border/50 bg-card p-5 space-y-3">
        <h2 className="font-semibold flex items-center gap-2">
          <Database className="w-4 h-4 text-purple-500" /> Bet Commitments ({data.bets.length})
        </h2>
        {data.bets.length > 0 ? (
          <div className="space-y-2">
            {data.bets.map((bet) => (
              <div
                key={bet.betId}
                className="flex items-center justify-between p-3 rounded-lg bg-accent/20"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        bet.option === 0
                          ? 'bg-emerald-500/10 text-emerald-500'
                          : 'bg-red-500/10 text-red-500'
                      }`}
                    >
                      {bet.option === 0 ? 'YES' : 'NO'}
                    </span>
                    <span className="text-sm">{bet.slots} slots</span>
                    <span className="text-xs text-muted-foreground">
                      {bet.userAddress.slice(0, 8)}...
                    </span>
                  </div>
                  {bet.commitmentHash && (
                    <p className="text-[10px] font-mono text-muted-foreground mt-1">
                      {bet.commitmentHash.slice(0, 24)}...
                    </p>
                  )}
                </div>
                <div className="text-right shrink-0">
                  <p className="text-sm font-medium">{formatQu(bet.amountQu)}</p>
                  <div className="flex items-center gap-1 justify-end">
                    {bet.commitmentHash ? (
                      <CheckCircle className="w-3 h-3 text-emerald-500" />
                    ) : (
                      <XCircle className="w-3 h-3 text-muted-foreground" />
                    )}
                    <span
                      className={`text-xs ${
                        bet.status === 'won'
                          ? 'text-emerald-500'
                          : bet.status === 'lost'
                            ? 'text-red-500'
                            : 'text-muted-foreground'
                      }`}
                    >
                      {bet.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">No bets placed on this market.</p>
        )}
      </section>

      {/* Chain Entries */}
      <section className="rounded-xl border border-border/50 bg-card p-5 space-y-3">
        <h2 className="font-semibold flex items-center gap-2">
          <Coins className="w-4 h-4 text-cyan-500" /> Audit Trail
        </h2>
        <p className="text-sm text-muted-foreground">
          {data.chainEntries} chain entries recorded for this market
        </p>
      </section>

      {/* Proof Package */}
      {data.proofAvailable && (
        <section className="rounded-xl border border-border/50 bg-card p-5 space-y-4">
          <h2 className="font-semibold flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-500" /> Resolution Proof Package
          </h2>

          <div className="flex gap-3">
            <Button variant="outline" size="sm" onClick={downloadProof}>
              <Download className="w-4 h-4 mr-2" />
              Download Proof (JSON)
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={verifyProof}
              disabled={verifying}
            >
              {verifying ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Shield className="w-4 h-4 mr-2" />
              )}
              Verify All Checks
            </Button>
          </div>

          {proofResult && (
            <div className="space-y-2">
              <div
                className={`flex items-center gap-2 p-3 rounded-lg ${
                  proofResult.verification.valid
                    ? 'bg-emerald-500/10 border border-emerald-500/30'
                    : 'bg-red-500/10 border border-red-500/30'
                }`}
              >
                {proofResult.verification.valid ? (
                  <CheckCircle className="w-5 h-5 text-emerald-500" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500" />
                )}
                <p className="font-medium">
                  {proofResult.verification.valid
                    ? 'All verification checks passed!'
                    : 'Some verification checks failed'}
                </p>
              </div>

              {proofResult.verification.checks.map((check, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-2 rounded text-sm"
                >
                  {check.passed ? (
                    <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-500 shrink-0" />
                  )}
                  <span className="font-mono text-xs text-muted-foreground w-40 shrink-0">
                    {check.name}
                  </span>
                  <span className="text-xs">{check.detail}</span>
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  )
}
