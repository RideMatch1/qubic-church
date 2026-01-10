/**
 * Holy Circle Lottery Configuration
 * Prize pool, draw date, and lottery system settings
 */

export const LOTTERY_CONFIG = {
  drawDate: new Date('2027-03-03T00:00:00Z'), // Anna's arrival month
  totalTickets: 200,
  prizePool: {
    qubic: 675_000_000n, // 675M QUBIC
    genesis: 2_000_000n, // 2M Genesis
  },
  description:
    'Support open research and enter to win up to 300M QUBIC + 1M Genesis',
} as const

export interface Prize {
  place: number
  qubic: bigint
  genesis: bigint
  percentage: number
}

export const PRIZE_STRUCTURE: Prize[] = [
  {
    place: 1,
    qubic: 300_000_000n,
    genesis: 1_000_000n,
    percentage: 44.4,
  },
  {
    place: 2,
    qubic: 150_000_000n,
    genesis: 500_000n,
    percentage: 22.2,
  },
  {
    place: 3,
    qubic: 100_000_000n,
    genesis: 250_000n,
    percentage: 14.8,
  },
  {
    place: 4,
    qubic: 75_000_000n,
    genesis: 150_000n,
    percentage: 11.1,
  },
  {
    place: 5,
    qubic: 50_000_000n,
    genesis: 100_000n,
    percentage: 7.4,
  },
] as const

export const BONUS_PRIZES = {
  intelligenceChampions: {
    description: 'Top 10 puzzle solvers',
    amount: 1_000_000n, // 1M QUBIC each
    count: 10,
  },
  earlySupport: {
    description: 'First 20 buyers',
    amount: 500_000n, // 500K QUBIC each
    count: 20,
  },
  communityChoice: {
    description: 'Voted by holders',
    amount: 5_000_000n, // 5M QUBIC
    count: 1,
  },
} as const

export type LotteryStatus = 'pending' | 'entered' | 'winner'

export interface LotteryTicket {
  nftId: number // 1-200
  qubicAddress: string // Buyer's wallet
  genesisAmount: number // = nftId (unique identifier)
  purchaseDate: Date // When NFT was bought
  entryDate: Date | null // When user entered Holy Circle
  status: LotteryStatus
  intelligenceScore?: number // Optional: puzzle score
  place?: number // 1-5 if winner
  prizeQubic?: bigint
  prizeGenesis?: bigint
}
