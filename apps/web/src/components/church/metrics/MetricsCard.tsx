'use client'

/**
 * MetricsCard Component
 * Reusable card for displaying live metrics
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
 * Get status color classes
 */
function getStatusClasses(status?: MetricsCardProps['status']): string {
  switch (status) {
    case 'excellent':
      return 'text-green-500 border-green-500/30 bg-green-500/5'
    case 'good':
      return 'text-blue-500 border-blue-500/30 bg-blue-500/5'
    case 'fair':
      return 'text-yellow-500 border-yellow-500/30 bg-yellow-500/5'
    case 'slow':
      return 'text-orange-500 border-orange-500/30 bg-orange-500/5'
    case 'error':
      return 'text-red-500 border-red-500/30 bg-red-500/5'
    default:
      return 'text-foreground border-border bg-card'
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
      className={`relative overflow-hidden rounded-lg border p-6 transition-all duration-200 hover:shadow-lg ${statusClasses}`}
    >
      {/* Background gradient effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-primary/5 opacity-50" />

      {/* Content */}
      <div className="relative space-y-3">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
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
              <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full" />
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
                <TrendingUp className="w-4 h-4 text-green-500" />
                <span className="text-green-500">Trending up</span>
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
