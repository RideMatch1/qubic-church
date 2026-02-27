'use client'

/**
 * MetricsCard Component
 * Reusable card for displaying live metrics
 * Church HUD Design System: no rounded corners, gold accents, angular aesthetic
 */

import { TrendingUp, TrendingDown, Activity, AlertCircle } from 'lucide-react'
import type { ReactNode } from 'react'

export interface MetricsCardProps {
  title: string
  value: string | number | ReactNode
  subtitle?: string
  icon?: ReactNode
  trend?: 'up' | 'down' | 'neutral'
  status?: 'excellent' | 'good' | 'fair' | 'slow' | 'error'
  loading?: boolean
  error?: boolean
}

/**
 * Get status color classes - gold-based hierarchy for non-error states
 */
function getStatusClasses(status?: MetricsCardProps['status']): string {
  switch (status) {
    case 'excellent':
      return 'text-[#D4AF37] border-[#D4AF37]/30 bg-[#D4AF37]/5'
    case 'good':
      return 'text-[#D4AF37]/80 border-[#D4AF37]/20 bg-[#D4AF37]/[0.03]'
    case 'fair':
      return 'text-[#D4AF37]/60 border-[#D4AF37]/15 bg-[#D4AF37]/[0.02]'
    case 'slow':
      return 'text-white/50 border-white/10 bg-white/[0.02]'
    case 'error':
      return 'text-red-500 border-red-500/30 bg-red-500/5'
    default:
      return 'text-foreground border-white/[0.04] bg-[#050505]'
  }
}

export function MetricsCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  status,
  loading,
  error,
}: MetricsCardProps) {
  const statusClasses = getStatusClasses(error ? 'error' : status)

  return (
    <div
      className={`relative overflow-hidden border p-6 transition-all duration-200 hover:shadow-[0_0_30px_rgba(212,175,55,0.03)] ${statusClasses}`}
    >
      {/* Background gradient effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-[#D4AF37]/[0.02] opacity-50" />

      {/* Content */}
      <div className="relative space-y-3">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-[#D4AF37]/50 text-[11px] uppercase tracking-[0.4em] font-mono">
            {title}
          </h3>
          {icon && (
            <div className="text-muted-foreground opacity-60">{icon}</div>
          )}
        </div>

        {/* Value */}
        <div className="space-y-1">
          {loading ? (
            <div className="flex items-center gap-2">
              <div className="animate-spin h-6 w-6 border-2 border-[#D4AF37] border-t-transparent" />
              <span className="text-sm text-muted-foreground">Loading...</span>
            </div>
          ) : error ? (
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <span className="text-sm text-red-500">Error loading data</span>
            </div>
          ) : (
            <>
              <div className="text-3xl font-bold tracking-tight">{value}</div>
              {subtitle && (
                <p className="text-sm text-muted-foreground">{subtitle}</p>
              )}
            </>
          )}
        </div>

        {/* Trend indicator */}
        {trend && !loading && !error && (
          <div className="flex items-center gap-1 text-sm">
            {trend === 'up' && (
              <>
                <TrendingUp className="w-4 h-4 text-[#D4AF37]" />
                <span className="text-[#D4AF37]">Trending up</span>
              </>
            )}
            {trend === 'down' && (
              <>
                <TrendingDown className="w-4 h-4 text-red-500" />
                <span className="text-red-500">Trending down</span>
              </>
            )}
            {trend === 'neutral' && (
              <>
                <Activity className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">Stable</span>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
