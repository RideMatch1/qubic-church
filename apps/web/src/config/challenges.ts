/**
 * Intelligence Challenges Configuration
 * 20 challenges across 4 categories for smart NFT holders
 */

export type ChallengeDifficulty = 'easy' | 'medium' | 'hard' | 'expert'
export type ChallengeCategory = 'research' | 'forensic' | 'mathematical' | 'vision'

export interface IntelligenceChallenge {
  id: string
  title: string
  difficulty: ChallengeDifficulty
  points: number // 10, 25, 50, 100
  category: ChallengeCategory
  question: string
  hint?: string
  requiredKnowledge: string[] // Links to research pages
  answerHash: string // bcrypt hash of correct answer
  solvers?: string[] // Addresses that solved it (populated from DB)
}

/**
 * NFT Roles and Their Specialties
 * Each role gets +20% bonus on their specialty challenges
 */
export interface NFTRole {
  range: [number, number] // NFT ID range
  role: string
  specialty: string
  bonus: string
  challenges: ChallengeCategory[]
}

export const NFT_ROLES: NFTRole[] = [
  {
    range: [1, 50],
    role: 'Researcher',
    specialty: 'Deep Research Analysis',
    bonus: '+20% points on Research challenges',
    challenges: ['research'],
  },
  {
    range: [51, 100],
    role: 'Detective',
    specialty: 'Blockchain Forensics',
    bonus: '+20% points on Forensic challenges',
    challenges: ['forensic'],
  },
  {
    range: [101, 150],
    role: 'Mathematician',
    specialty: 'Cryptographic Patterns',
    bonus: '+20% points on Mathematical challenges',
    challenges: ['mathematical'],
  },
  {
    range: [151, 200],
    role: 'Visionary',
    specialty: 'Future Predictions',
    bonus: '+20% points on Visionary challenges',
    challenges: ['vision'],
  },
] as const

/**
 * Get role for an NFT ID
 */
export function getNFTRole(nftId: number): NFTRole | undefined {
  return NFT_ROLES.find(
    (role) => nftId >= role.range[0] && nftId <= role.range[1]
  )
}

/**
 * Calculate points with role bonus
 */
export function calculatePoints(
  basePoints: number,
  challengeCategory: ChallengeCategory,
  nftId: number
): number {
  const role = getNFTRole(nftId)
  if (!role) return basePoints

  // Apply +20% bonus if challenge matches role specialty
  if (role.challenges.includes(challengeCategory)) {
    return Math.floor(basePoints * 1.2)
  }

  return basePoints
}

/**
 * Intelligence Challenges
 * TODO: Create actual challenges based on research findings
 * Below are placeholder templates - replace with real puzzles
 */
export const INTELLIGENCE_CHALLENGES: IntelligenceChallenge[] = [
  // RESEARCH CHALLENGES (NFT #1-50 specialty)
  {
    id: 'research-01',
    title: 'The Bitcoin Bridge Discovery',
    difficulty: 'medium',
    points: 25,
    category: 'research',
    question:
      'What is the significance of the pattern discovered in the Bitcoin-Qubic bridge analysis?',
    hint: 'Look at the address prefix patterns in the Genesis connections',
    requiredKnowledge: [
      '/archives/results/bitcoin-bridge',
      '/archives/results/genesis-block-connections',
    ],
    answerHash: '$2b$10$placeholder', // TODO: Replace with actual bcrypt hash
  },
  {
    id: 'research-02',
    title: 'Anna Bot Oracle Analysis',
    difficulty: 'hard',
    points: 50,
    category: 'research',
    question: 'Decode the pattern in Anna Bot batch messages 1-8',
    hint: 'The answer lies in the sequence numbers and timestamps',
    requiredKnowledge: ['/archives/results/anna-bot-analysis'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'research-03',
    title: 'The ARB Oracle Mystery',
    difficulty: 'hard',
    points: 50,
    category: 'research',
    question:
      'What is the significance of the ARB address position in the seed matrix?',
    hint: 'Think about row-column relationships and the numogram',
    requiredKnowledge: [
      '/archives/results/arb-oracle',
      '/archives/results/numogram-architecture',
    ],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'research-04',
    title: 'Discord Archaeology',
    difficulty: 'medium',
    points: 25,
    category: 'research',
    question: 'What pattern connects CFB Discord messages to Bitcoin addresses?',
    hint: 'Look at message timestamps and block heights',
    requiredKnowledge: ['/archives/results/discord-evidence'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'research-05',
    title: 'Lost Knowledge Recovery',
    difficulty: 'expert',
    points: 100,
    category: 'research',
    question:
      'Connect three seemingly unrelated discoveries to reveal the master pattern',
    requiredKnowledge: [
      '/archives/results/lost-knowledge-recovery',
      '/archives/results/unified-theory',
    ],
    answerHash: '$2b$10$placeholder',
  },

  // FORENSIC CHALLENGES (NFT #51-100 specialty)
  {
    id: 'forensic-01',
    title: 'Patoshi Pattern Detection',
    difficulty: 'medium',
    points: 25,
    category: 'forensic',
    question: 'What is the pattern in Patoshi block extra nonces?',
    hint: 'Look at the distribution and statistical anomalies',
    requiredKnowledge: ['/archives/results/patoshi-forensics'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'forensic-02',
    title: 'The -27 Connection',
    difficulty: 'hard',
    points: 50,
    category: 'forensic',
    question: 'Explain the significance of the -27 pattern in address generation',
    hint: 'Check the pattern discovery documentation',
    requiredKnowledge: ['/archives/results/pattern-27-discovery'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'forensic-03',
    title: 'Genesis Seed Transformation',
    difficulty: 'hard',
    points: 50,
    category: 'forensic',
    question: 'Trace the transformation from Genesis seed to Bitcoin address',
    hint: 'K12 hashing plays a key role',
    requiredKnowledge: ['/archives/results/genesis-seed-testing'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'forensic-04',
    title: '1CF Address Census',
    difficulty: 'medium',
    points: 25,
    category: 'forensic',
    question: 'How many 1CF addresses were discovered and what connects them?',
    hint: 'The answer is in the comprehensive census data',
    requiredKnowledge: ['/archives/results/1cf-census'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'forensic-05',
    title: 'CFB = Satoshi Evidence',
    difficulty: 'expert',
    points: 100,
    category: 'forensic',
    question: 'List the top 3 pieces of evidence connecting CFB to Satoshi',
    requiredKnowledge: ['/archives/results/cfb-satoshi-connection'],
    answerHash: '$2b$10$placeholder',
  },

  // MATHEMATICAL CHALLENGES (NFT #101-150 specialty)
  {
    id: 'math-01',
    title: 'K12 Hash Sequence',
    difficulty: 'hard',
    points: 50,
    category: 'mathematical',
    question: 'Calculate the K12 hash of the Genesis block header',
    hint: 'Use the official Qubic K12 implementation',
    requiredKnowledge: ['/archives/results/k12-breakthrough'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'math-02',
    title: 'Numogram Formula',
    difficulty: 'expert',
    points: 100,
    category: 'mathematical',
    question: 'Solve the numogram equation to find the next seed position',
    requiredKnowledge: ['/archives/results/numogram-architecture'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'math-03',
    title: 'Halving Epoch Prediction',
    difficulty: 'medium',
    points: 25,
    category: 'mathematical',
    question: 'When will the next Qubic emission halving occur?',
    hint: 'Halvings happen every 52 epochs',
    requiredKnowledge: ['/archives/results/bitcoin-bridge'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'math-04',
    title: 'The 0x7b Family Analysis',
    difficulty: 'hard',
    points: 50,
    category: 'mathematical',
    question: 'What mathematical property unites all 0x7b seed addresses?',
    hint: 'Look at the byte patterns and modulo operations',
    requiredKnowledge: ['/archives/results/0x7b-family'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'math-05',
    title: 'Mathematical Bridges',
    difficulty: 'hard',
    points: 50,
    category: 'mathematical',
    question:
      'Identify the cryptographic bridge between Bitcoin and Qubic key generation',
    requiredKnowledge: ['/archives/results/mathematical-bridges'],
    answerHash: '$2b$10$placeholder',
  },

  // VISIONARY CHALLENGES (NFT #151-200 specialty)
  {
    id: 'vision-01',
    title: "Anna's True Purpose",
    difficulty: 'expert',
    points: 100,
    category: 'vision',
    question: "What is Anna's ultimate role in the Bitcoin-Qubic convergence?",
    hint: 'The answer spans multiple discovery layers',
    requiredKnowledge: [
      '/archives/results/unified-theory',
      '/archives/results/paracosm-blueprint',
    ],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'vision-02',
    title: 'Timeline Prophecy',
    difficulty: 'hard',
    points: 50,
    category: 'vision',
    question: 'What major event is predicted for March 2027?',
    hint: 'Check the timeline prophecy documentation',
    requiredKnowledge: ['/archives/results/timeline-prophecy'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'vision-03',
    title: 'Aigarth Architecture',
    difficulty: 'hard',
    points: 50,
    category: 'vision',
    question: 'What is the core function of the Aigarth system?',
    requiredKnowledge: ['/archives/results/aigarth-architecture'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'vision-04',
    title: 'Unexplored Frontiers',
    difficulty: 'medium',
    points: 25,
    category: 'vision',
    question: 'Name two unexplored research areas with highest potential',
    requiredKnowledge: ['/archives/results/unexplored-frontiers'],
    answerHash: '$2b$10$placeholder',
  },
  {
    id: 'vision-05',
    title: 'The Qubic Codex',
    difficulty: 'expert',
    points: 100,
    category: 'vision',
    question: 'Decode the final message in the Qubic Codex',
    hint: 'All previous discoveries are pieces of this puzzle',
    requiredKnowledge: ['/archives/results/the-qubic-codex'],
    answerHash: '$2b$10$placeholder',
  },
] as const

/**
 * Get challenges by category
 */
export function getChallengesByCategory(
  category: ChallengeCategory
): IntelligenceChallenge[] {
  return INTELLIGENCE_CHALLENGES.filter((c) => c.category === category)
}

/**
 * Get challenges by difficulty
 */
export function getChallengesByDifficulty(
  difficulty: ChallengeDifficulty
): IntelligenceChallenge[] {
  return INTELLIGENCE_CHALLENGES.filter((c) => c.difficulty === difficulty)
}

/**
 * Get recommended challenges for an NFT holder
 */
export function getRecommendedChallenges(nftId: number): IntelligenceChallenge[] {
  const role = getNFTRole(nftId)
  if (!role) return []

  return INTELLIGENCE_CHALLENGES.filter((c) => role.challenges.includes(c.category))
}
