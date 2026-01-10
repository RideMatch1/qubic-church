/**
 * Signal-Based Unlock System Configuration
 * Controls when the lottery/prize pool unlocks
 */

export type SignalType = 'date' | 'soldout' | 'hybrid' | 'manual'
export type SignalStatus = 'locked' | 'unlocked'

export interface UnlockSignal {
  type: SignalType
  status: SignalStatus
  condition: string
  currentProgress?: number
  targetProgress?: number
  unlockDate?: Date
}

export interface HybridCondition {
  type: 'date' | 'soldout'
  unlockDate?: string
  target?: number
}

export interface HybridSignal extends UnlockSignal {
  conditions: HybridCondition[]
}

/**
 * Default signal configuration
 * Can be overridden via environment variables or admin panel
 */
export const DEFAULT_SIGNAL: HybridSignal = {
  type: 'hybrid',
  status: 'locked',
  condition: 'Unlocks on 03.03.2027 OR when all 200 NFTs are sold',
  conditions: [
    {
      type: 'date',
      unlockDate: '2027-03-03T00:00:00Z',
    },
    {
      type: 'soldout',
      target: 200,
    },
  ],
} as const

/**
 * Check if unlock signal is met
 */
export async function checkUnlockSignal(
  signal: UnlockSignal,
  nftSoldCount?: number
): Promise<boolean> {
  switch (signal.type) {
    case 'date':
      if (!signal.unlockDate) return false
      return Date.now() >= signal.unlockDate.getTime()

    case 'soldout':
      if (!signal.targetProgress || nftSoldCount === undefined) return false
      return nftSoldCount >= signal.targetProgress

    case 'hybrid': {
      const hybridSignal = signal as HybridSignal
      const dateCondition = hybridSignal.conditions.find((c) => c.type === 'date')
      const soldoutCondition = hybridSignal.conditions.find(
        (c) => c.type === 'soldout'
      )

      let dateReached = false
      if (dateCondition?.unlockDate) {
        dateReached = Date.now() >= new Date(dateCondition.unlockDate).getTime()
      }

      let soldOut = false
      if (soldoutCondition?.target && nftSoldCount !== undefined) {
        soldOut = nftSoldCount >= soldoutCondition.target
      }

      return dateReached || soldOut
    }

    case 'manual':
      return signal.status === 'unlocked'

    default:
      return false
  }
}
