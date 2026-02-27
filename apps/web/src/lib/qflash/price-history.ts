/**
 * QFlash Price History
 *
 * In-memory ring buffer storing recent price ticks for live charts.
 * Server-side storage so new page loads get history immediately.
 * The cron pushes a new tick every 5 seconds from the price feed.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface PriceTick {
  timestamp: number  // unix ms
  price: number
  pair: string
}

// ---------------------------------------------------------------------------
// Ring Buffer
// ---------------------------------------------------------------------------

const MAX_TICKS = 300 // 5 minutes at 1-tick-per-second, or 25 minutes at 5s intervals

class PriceHistory {
  private buffer: Map<string, PriceTick[]> = new Map()

  addTick(pair: string, price: number): void {
    let ticks = this.buffer.get(pair)
    if (!ticks) {
      ticks = []
      this.buffer.set(pair, ticks)
    }

    ticks.push({
      timestamp: Date.now(),
      price,
      pair,
    })

    // Ring buffer: trim to max
    if (ticks.length > MAX_TICKS) {
      ticks.splice(0, ticks.length - MAX_TICKS)
    }
  }

  getHistory(pair: string, lastN?: number): PriceTick[] {
    const ticks = this.buffer.get(pair) ?? []
    if (lastN && lastN < ticks.length) {
      return ticks.slice(-lastN)
    }
    return [...ticks]
  }

  getLatest(pair: string): PriceTick | null {
    const ticks = this.buffer.get(pair)
    if (!ticks || ticks.length === 0) return null
    return ticks[ticks.length - 1]!
  }

  clear(pair?: string): void {
    if (pair) {
      this.buffer.delete(pair)
    } else {
      this.buffer.clear()
    }
  }
}

// ---------------------------------------------------------------------------
// Singleton
// ---------------------------------------------------------------------------

let _instance: PriceHistory | null = null

export function getPriceHistory(): PriceHistory {
  if (!_instance) {
    _instance = new PriceHistory()
  }
  return _instance
}
