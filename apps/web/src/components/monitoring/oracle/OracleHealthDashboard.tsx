'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'

interface NodeDetail {
  ip: string
  status: string
  latencyMs: number
  tick: number
  epoch: number
  error: string | null
}

interface OracleStats {
  pendingCount: number
  pendingOracleMachineCount: number
  pendingCommitCount: number
  pendingRevealCount: number
  successfulCount: number
  revealTxCount: number
  unresolvableCount: number
  timeoutCount: number
  timeoutNoReplyCount: number
  timeoutNoCommitCount: number
  timeoutNoRevealCount: number
  oracleMachineRepliesDisagreeCount: number
  oracleMachineReplyAvgMilliTicksPerQuery: number
  commitAvgMilliTicksPerQuery: number
  successAvgMilliTicksPerQuery: number
  timeoutAvgMilliTicksPerQuery: number
  wrongKnowledgeProofCount: number
}

interface Anomaly {
  severity: 'CRITICAL' | 'WARNING' | 'INFO'
  type: string
  message: string
}

interface HeartbeatSnapshot {
  timestamp: string
  healthScore: number
  scanDurationMs: number
  network: {
    nodesTotal: number
    nodesConnected: number
    consensusTick: number
    currentEpoch: number
    tickDrift: number
    tickRange: { firstTick: number; currentTick: number } | null
  }
  oracle: {
    successRate: number
    stats: OracleStats | null
    pendingCount: number
    pendingIds: number[]
    revenue: { totalRevenue: number; activeComputors: number } | null
  }
  anomalies: Anomaly[]
  nodes: NodeDetail[]
}

interface HeartbeatData {
  snapshot: HeartbeatSnapshot | null
  history: Array<{
    timestamp: string
    healthScore: number
    nodesConnected: number
    consensusTick: number
    successRate: number
    pendingCount: number
    anomalyCount: number
  }>
  lastUpdated: string | null
}

const ease = [0.22, 1, 0.36, 1] as const

export function OracleHealthDashboard() {
  const [data, setData] = useState<HeartbeatData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchHeartbeat = useCallback(async () => {
    try {
      const res = await fetch('/api/oracle/heartbeat')
      const json = await res.json()
      if (json.data) {
        setData(json.data)
        setError(null)
      } else {
        setError(json.message ?? 'No data')
      }
    } catch {
      setError('Failed to load heartbeat data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchHeartbeat()
    const interval = setInterval(fetchHeartbeat, 15000)
    return () => clearInterval(interval)
  }, [fetchHeartbeat])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-5 h-5 border-2 border-emerald-400/30 border-t-emerald-400 rounded-full animate-spin" />
      </div>
    )
  }

  if (error || !data?.snapshot) {
    return (
      <div className="text-center py-12">
        <p className="text-zinc-500 text-sm">{error ?? 'No heartbeat data'}</p>
        <p className="text-zinc-600 text-xs mt-2 font-mono">
          Run: node scripts/ORACLE_HEARTBEAT.mjs --json
        </p>
      </div>
    )
  }

  const s = data.snapshot

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease }}
    >
      {/* Health Score + Key Metrics */}
      <div className="flex items-start gap-6 mb-5">
        {/* Health Score */}
        <HealthScoreRing score={s.healthScore} />

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-x-6 gap-y-2 flex-1">
          <MetricCard
            label="SUCCESS RATE"
            value={`${s.oracle.successRate}%`}
            color={s.oracle.successRate >= 90 ? 'emerald' : s.oracle.successRate >= 50 ? 'amber' : 'red'}
          />
          <MetricCard
            label="PENDING"
            value={String(s.oracle.pendingCount)}
            color={s.oracle.pendingCount > 10 ? 'amber' : 'zinc'}
          />
          <MetricCard
            label="SUCCESSFUL"
            value={String(s.oracle.stats?.successfulCount ?? 0)}
            color="emerald"
          />
          <MetricCard
            label="TIMEOUTS"
            value={String(s.oracle.stats?.timeoutCount ?? 0)}
            color="red"
          />
        </div>
      </div>

      {/* Node Status Grid */}
      <div className="mb-4">
        <h4 className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 mb-2">Node Status</h4>
        <div className="space-y-1">
          {s.nodes.map((node) => (
            <div key={node.ip} className="flex items-center gap-3 text-xs font-mono">
              <span className={`w-1.5 h-1.5 rounded-full ${
                node.status === 'connected' ? 'bg-emerald-400' : 'bg-zinc-600'
              }`} />
              <span className="text-zinc-400 w-36">{node.ip}</span>
              <span className="text-zinc-500 w-24">
                {node.tick ? node.tick.toLocaleString() : '--'}
              </span>
              <span className="text-zinc-600 w-16">
                {node.latencyMs ? `${node.latencyMs}ms` : '--'}
              </span>
              <span className={`text-xs ${node.status === 'connected' ? 'text-emerald-400/60' : 'text-zinc-600'}`}>
                {node.status === 'connected' ? 'Connected' : node.error ?? 'Offline'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Anomalies */}
      {s.anomalies.length > 0 && (
        <div className="mb-4">
          <h4 className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 mb-2">Anomalies</h4>
          <div className="space-y-1">
            {s.anomalies.map((a, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <SeverityBadge severity={a.severity} />
                <span className="text-zinc-400">{a.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer: Scan info */}
      <div className="flex items-center gap-4 text-[10px] text-zinc-600 font-mono pt-2 border-t border-white/[0.04]">
        <span>Epoch {s.network.currentEpoch}</span>
        <span>Tick {s.network.consensusTick?.toLocaleString()}</span>
        <span>Drift: {s.network.tickDrift}</span>
        <span>Scan: {s.scanDurationMs}ms</span>
        {s.oracle.revenue && (
          <span>{s.oracle.revenue.activeComputors}/676 computors</span>
        )}
      </div>
    </motion.div>
  )
}

function HealthScoreRing({ score }: { score: number }) {
  const color = score >= 80 ? '#34d399' : score >= 50 ? '#f59e0b' : '#ef4444'
  return (
    <div className="flex-shrink-0 relative w-20 h-20">
      <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
        <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="4" />
        <circle
          cx="40" cy="40" r="34"
          fill="none"
          stroke={color}
          strokeWidth="4"
          strokeDasharray={`${score * 2.136} 213.6`}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-lg text-zinc-200">{score}</span>
        <span className="text-[8px] uppercase tracking-[0.15em] text-zinc-600">health</span>
      </div>
    </div>
  )
}

function MetricCard({ label, value, color }: { label: string; value: string; color: string }) {
  const colorClasses: Record<string, string> = {
    emerald: 'text-emerald-400',
    amber: 'text-amber-400',
    red: 'text-red-400',
    cyan: 'text-cyan-400',
    zinc: 'text-zinc-300',
  }
  return (
    <div>
      <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">{label}</div>
      <div className={`font-mono text-sm ${colorClasses[color] ?? 'text-zinc-300'}`}>{value}</div>
    </div>
  )
}

function SeverityBadge({ severity }: { severity: string }) {
  const config: Record<string, { bg: string; text: string }> = {
    CRITICAL: { bg: 'bg-red-400/10', text: 'text-red-400' },
    WARNING: { bg: 'bg-amber-400/10', text: 'text-amber-400' },
    INFO: { bg: 'bg-cyan-400/10', text: 'text-cyan-400' },
  }
  const c = config[severity] ?? { bg: 'bg-cyan-400/10', text: 'text-cyan-400' }
  return (
    <span className={`text-[9px] px-1.5 py-0.5 rounded font-medium ${c.bg} ${c.text}`}>
      {severity}
    </span>
  )
}
