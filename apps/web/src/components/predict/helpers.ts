/**
 * QPredict UI Helpers
 *
 * Formatting and time utilities shared across predict components.
 */

/**
 * Format a QU amount with locale-aware thousands separators.
 */
export function formatQu(amount: number): string {
  return amount.toLocaleString('en-US')
}

/**
 * Format a probability value (0-1) as a percentage string.
 */
export function formatProbability(p: number): string {
  return `${Math.round(p * 100)}%`
}

/**
 * Format a price value with appropriate decimal places.
 */
export function formatPrice(price: number): string {
  if (price >= 1000) {
    return price.toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    })
  }
  if (price >= 1) {
    return price.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  }
  return price.toLocaleString('en-US', {
    minimumFractionDigits: 4,
    maximumFractionDigits: 6,
  })
}

/**
 * Get remaining time as a human-readable string.
 * Returns null if the date is in the past.
 */
export function timeRemaining(isoDate: string): string | null {
  const target = new Date(isoDate).getTime()
  const now = Date.now()
  const diff = target - now

  if (diff <= 0) return null

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  if (days > 0) {
    return `${days}d ${hours}h left`
  }
  if (hours > 0) {
    return `${hours}h ${minutes}m left`
  }
  return `${minutes}m left`
}

/**
 * Get a status display badge config.
 */
export function statusConfig(status: string): {
  label: string
  className: string
} {
  switch (status) {
    case 'active':
      return {
        label: 'Active',
        className: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
      }
    case 'closed':
      return {
        label: 'Closing Soon',
        className: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
      }
    case 'resolving':
      return {
        label: 'Resolving',
        className: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
      }
    case 'resolved':
      return {
        label: 'Resolved',
        className: 'bg-zinc-500/15 text-zinc-400 border-zinc-500/30',
      }
    case 'cancelled':
      return {
        label: 'Cancelled',
        className: 'bg-red-500/15 text-red-400 border-red-500/30',
      }
    case 'draft':
      return {
        label: 'Draft',
        className: 'bg-zinc-500/15 text-zinc-500 border-zinc-500/30',
      }
    default:
      return {
        label: status,
        className: 'bg-zinc-500/15 text-zinc-400 border-zinc-500/30',
      }
  }
}

/**
 * localStorage key for the user's payout address.
 */
const STORAGE_KEY = 'qpredict_payout_address'

/**
 * Retrieve the stored payout address from localStorage.
 * Returns empty string when unavailable or on the server.
 */
export function getStoredAddress(): string {
  if (typeof window === 'undefined') return ''
  try {
    return localStorage.getItem(STORAGE_KEY) ?? ''
  } catch {
    return ''
  }
}

/**
 * Persist a validated payout address to localStorage.
 * Only stores addresses that are exactly 60 uppercase letters.
 */
export function setStoredAddress(address: string): void {
  if (typeof window === 'undefined') return
  try {
    if (address.length === 60 && /^[A-Z]+$/.test(address)) {
      localStorage.setItem(STORAGE_KEY, address)
    }
  } catch {
    // localStorage unavailable (private browsing, quota exceeded, etc.)
  }
}

/**
 * Anonymize a Qubic address for display.
 * Shows first 6 and last 4 characters.
 */
export function anonymizeAddress(address: string): string {
  if (address.length <= 12) return address
  return `${address.slice(0, 6)}...${address.slice(-4)}`
}

/**
 * Format a datetime string to locale-friendly display.
 */
export function formatDateTime(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
