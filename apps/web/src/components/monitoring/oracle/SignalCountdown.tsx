'use client'

import { useState, useEffect } from 'react'
import { ORACLE_CONFIG } from '@/config/api'

const BITCOIN_GENESIS = new Date('2009-01-03T18:15:05Z')
const SIGNAL_DATE = ORACLE_CONFIG.signalDate
const TOTAL_SPAN_MS = SIGNAL_DATE.getTime() - BITCOIN_GENESIS.getTime()

function useCountdown(target: Date) {
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const diff = target.getTime() - now.getTime()
  if (diff <= 0) return { days: 0, hours: 0, minutes: 0, seconds: 0, passed: true, progress: 100 }

  const elapsed = now.getTime() - BITCOIN_GENESIS.getTime()
  const progress = Math.min((elapsed / TOTAL_SPAN_MS) * 100, 100)

  return {
    days: Math.floor(diff / 86400000),
    hours: Math.floor((diff % 86400000) / 3600000),
    minutes: Math.floor((diff % 3600000) / 60000),
    seconds: Math.floor((diff % 60000) / 1000),
    passed: false,
    progress,
  }
}

export function SignalCountdown() {
  const { days, hours, minutes, seconds, passed, progress } = useCountdown(SIGNAL_DATE)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-xs text-zinc-500 uppercase tracking-wider">Signal Countdown</span>
        <span className="text-xs text-amber-400/70 font-mono">
          6268 days from Bitcoin Genesis
        </span>
      </div>

      {passed ? (
        <div className="text-center py-3">
          <div className="text-lg font-bold text-amber-400 animate-pulse">
            SIGNAL WINDOW ACTIVE
          </div>
          <div className="text-xs text-amber-400/60 mt-1">March 3, 2026</div>
        </div>
      ) : (
        <>
          {/* Countdown digits */}
          <div className="grid grid-cols-4 gap-2">
            {[
              { value: days, label: 'Days' },
              { value: hours, label: 'Hours' },
              { value: minutes, label: 'Min' },
              { value: seconds, label: 'Sec' },
            ].map((item) => (
              <div key={item.label} className="text-center">
                <div className="text-2xl font-mono font-bold text-amber-400 tabular-nums">
                  {String(item.value).padStart(2, '0')}
                </div>
                <div className="text-[10px] text-zinc-600 uppercase">{item.label}</div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Target date */}
      <div className="text-center">
        <div className="text-xs text-zinc-500">
          March 3, 2026 &middot; Total Lunar Eclipse
        </div>
      </div>

      {/* Progress bar: Bitcoin Genesis -> Signal Date */}
      <div className="space-y-1.5">
        <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-amber-600 to-amber-400 transition-all duration-1000"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="flex justify-between text-[10px] text-zinc-600">
          <span>Jan 3, 2009</span>
          <span>{progress.toFixed(4)}%</span>
          <span>Mar 3, 2026</span>
        </div>
      </div>
    </div>
  )
}
