'use client'

import { useState, useEffect, useCallback } from 'react'
import { Loader2, Copy, Check } from 'lucide-react'
import { qubicOracle } from '@/lib/qubic/oracle-client'
import type { AddressActivity } from '@/lib/qubic/oracle-client'

const REFRESH_INTERVAL = 30_000 // 30s

interface AddressData {
  addresses: AddressActivity[]
  loading: boolean
  lastUpdate: Date | null
}

function useAddressWatch(watchAddresses: string[]): AddressData & { refresh: () => Promise<void> } {
  const [state, setState] = useState<AddressData>({
    addresses: [],
    loading: true,
    lastUpdate: null,
  })

  const refresh = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true }))
    try {
      const results = await Promise.all(
        watchAddresses.map((addr) =>
          qubicOracle.getAddressActivity(addr).catch(() => null)
        )
      )
      setState({
        addresses: results.filter((r): r is AddressActivity => r !== null),
        loading: false,
        lastUpdate: new Date(),
      })
    } catch {
      setState((prev) => ({ ...prev, loading: false }))
    }
  }, [watchAddresses])

  useEffect(() => {
    refresh()
    const interval = setInterval(refresh, REFRESH_INTERVAL)
    return () => clearInterval(interval)
  }, [refresh])

  return { ...state, refresh }
}

function AddressCard({
  label,
  tag,
  address,
  activity,
  loading,
  accentColor,
}: {
  label: string
  tag: string
  address: string
  activity: AddressActivity | null
  loading: boolean
  accentColor: string
}) {
  const [copied, setCopied] = useState(false)
  const isActive = activity && activity.lastActivityTick > 0
  const balance = activity ? Number(activity.balance) : 0

  const copyAddress = () => {
    navigator.clipboard.writeText(address)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="p-3 bg-zinc-800/30 rounded-lg border border-zinc-800/50">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className={`text-xs font-semibold ${accentColor}`}>{label}</span>
          <span className="text-[10px] text-zinc-600">{tag}</span>
        </div>
        <div className={`flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium ${
          isActive
            ? 'bg-emerald-500/10 text-emerald-400'
            : 'bg-zinc-700/50 text-zinc-500'
        }`}>
          <span className={`w-1 h-1 rounded-full ${isActive ? 'bg-emerald-400' : 'bg-zinc-600'}`} />
          {isActive ? 'Active' : 'Dormant'}
        </div>
      </div>

      {/* Address */}
      <button
        onClick={copyAddress}
        className="flex items-center gap-1 group mb-3 w-full"
      >
        <code className="text-[10px] text-zinc-500 font-mono truncate group-hover:text-zinc-300 transition-colors">
          {address.slice(0, 20)}...{address.slice(-8)}
        </code>
        {copied ? (
          <Check className="w-2.5 h-2.5 text-emerald-400 flex-shrink-0" />
        ) : (
          <Copy className="w-2.5 h-2.5 text-zinc-600 opacity-0 group-hover:opacity-100 flex-shrink-0 transition-opacity" />
        )}
      </button>

      {loading ? (
        <div className="flex items-center justify-center py-2">
          <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-600" />
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-2">
          <div>
            <div className="text-[10px] text-zinc-600">Balance</div>
            <div className="text-sm font-mono text-zinc-200">{balance.toLocaleString()} QU</div>
          </div>
          <div>
            <div className="text-[10px] text-zinc-600">Transactions</div>
            <div className="text-sm font-mono text-zinc-200">{activity?.txCount ?? 0}</div>
          </div>
          {activity && activity.lastActivityTick > 0 && (
            <div className="col-span-2">
              <div className="text-[10px] text-zinc-600">Last Activity</div>
              <div className="text-xs font-mono text-zinc-400">Tick {activity.lastActivityTick.toLocaleString()}</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export function AddressWatch({
  addresses = [],
}: {
  addresses?: { label: string; tag: string; address: string; accentColor: string }[]
}) {
  const watchAddrs = addresses.map((a) => a.address)
  const { addresses: activities, loading } = useAddressWatch(watchAddrs)

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs text-zinc-500 uppercase tracking-wider">Address Watch</span>
        <span className="text-[10px] text-zinc-600">Auto-refresh 30s</span>
      </div>

      {addresses.map((addr) => {
        const activity = activities.find((a) => a.address === addr.address) ?? null
        return (
          <AddressCard
            key={addr.address}
            label={addr.label}
            tag={addr.tag}
            address={addr.address}
            activity={activity}
            loading={loading}
            accentColor={addr.accentColor}
          />
        )
      })}

      {addresses.length === 0 && (
        <div className="p-3 text-center text-xs text-zinc-500">
          No addresses configured for monitoring.
        </div>
      )}
    </div>
  )
}
