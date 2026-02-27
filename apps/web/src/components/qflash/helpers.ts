/**
 * QFlash UI Helpers
 */

export function formatQu(amount: number): string {
  return amount.toLocaleString('en-US')
}

export function formatPrice(price: number): string {
  if (price >= 1000) {
    return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }
  if (price >= 1) {
    return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })
  }
  return price.toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 6 })
}

export function durationLabel(secs: number): string {
  if (secs < 60) return `${secs}s`
  return `${secs / 60}m`
}

export function pairLabel(pair: string): string {
  return pair.toUpperCase().replace('/', '/')
}

export function pairIcon(pair: string): string {
  const base = pair.split('/')[0]
  switch (base) {
    case 'btc': return 'BTC'
    case 'eth': return 'ETH'
    case 'sol': return 'SOL'
    default: return base?.toUpperCase() ?? '?'
  }
}

export function anonymizeAddress(address: string): string {
  if (address.length <= 12) return address
  return `${address.slice(0, 6)}...${address.slice(-4)}`
}

const QFLASH_ADDRESS_KEY = 'qflash_address'

export function getStoredAddress(): string {
  if (typeof window === 'undefined') return ''
  try {
    return localStorage.getItem(QFLASH_ADDRESS_KEY) ?? ''
  } catch {
    return ''
  }
}

export function setStoredAddress(address: string): void {
  if (typeof window === 'undefined') return
  try {
    if (address.length === 60 && /^[A-Z]+$/.test(address)) {
      localStorage.setItem(QFLASH_ADDRESS_KEY, address)
    }
  } catch {
    // localStorage unavailable
  }
}
