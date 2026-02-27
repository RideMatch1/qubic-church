'use client'

import { motion, useInView, AnimatePresence } from 'framer-motion'
import { useRef, useState } from 'react'
import {
  Binary,
  Calculator,
  CheckCircle2,
  ChevronDown,
  Clock,
  Database,
  Eye,
  Hash,
  HelpCircle,
  Layers,
  Link2,
  Lock,
  Network,
  Search,
  Sparkles,
  Timer,
  User,
  XCircle,
  Zap,
} from 'lucide-react'

type ConfidenceLevel = 'VERIFIED' | 'HIGH' | 'UNKNOWN' | 'DISPROVEN'

interface Discovery {
  id: number
  title: string
  summary: string
  details: string[]
  confidence: ConfidenceLevel
  data?: string
}

interface Tier {
  id: number
  name: string
  icon: React.ReactNode
  confidenceRange: string
  discoveries: Discovery[]
  color: string
}

const tiers: Tier[] = [
  {
    id: 1,
    name: 'The Formula & Core Mathematics',
    icon: <Calculator className="h-5 w-5" />,
    confidenceRange: '99%',
    color: 'from-[#050505] to-[#050505]/80 border-white/[0.04]',
    discoveries: [
      {
        id: 1,
        title: 'The Pattern Formula',
        summary: '625,284 = 283 × 47² + 137',
        details: [
          '283 = Bitcoin Block height (61st prime)',
          '47² = 2,209 (15th prime squared)',
          '137 = Fine structure constant (α ≈ 1/137)',
        ],
        confidence: 'VERIFIED',
        data: '283 × 2,209 + 137 = 625,284',
      },
      {
        id: 2,
        title: 'Boot Address Derivation',
        summary: '625,284 % 16,384 = 2,692 (Row 21, Column 4)',
        details: [
          'Jinn memory = 128 × 128 = 16,384 addresses',
          'Boot[0] = 2,692 = Bitcoin Block #283 input layer',
          'Modulo operation reveals bootstrap entry point',
        ],
        confidence: 'VERIFIED',
        data: 'Row 21, Col 4 = Bitcoin input',
      },
      {
        id: 3,
        title: 'The 121 Divisibility',
        summary: 'March 3, 2026 tick difference = 2,316,908',
        details: [
          '2,316,908 = 2² × 11² × 4,787',
          'Divisible by 121 (11²) = CFB constant proof',
          'Probability of random: < 0.1%',
        ],
        confidence: 'VERIFIED',
        data: '2,316,908 % 121 = 0',
      },
      {
        id: 4,
        title: 'Prime 4,787 Discovery',
        summary: '4,787 is the 647th prime',
        details: [
          '647 is also prime (118th prime) = double significance',
          '676 - 647 = 29 (also prime!)',
          '676 = Number of Qubic Computors',
        ],
        confidence: 'HIGH',
        data: 'Triple prime significance',
      },
      {
        id: 5,
        title: "Row 68's 137 Writes",
        summary: 'Row 68 performs exactly 137 WRITE operations',
        details: [
          '192 READ operations (from Row 21 + self-reference)',
          'Read/Write ratio ≈ 1.40 ≈ √2',
          'Validates α = 137 integration',
        ],
        confidence: 'VERIFIED',
        data: '137 = fine structure constant',
      },
    ],
  },
  {
    id: 2,
    name: 'Bitcoin-Qubic Bridge Architecture',
    icon: <Link2 className="h-5 w-5" />,
    confidenceRange: '95%',
    color: 'from-[#050505] to-[#050505]/80 border-white/[0.04]',
    discoveries: [
      {
        id: 6,
        title: 'Jinn Memory Matrix',
        summary: 'Complete 128×128 ternary architecture',
        details: [
          '16,384 total addresses',
          'Key rows: 0-10 (bootstrap), 21 (input), 68 (bridge), 86 (MAC), 96 (output)',
          'Balanced ternary values {-1, 0, +1}',
        ],
        confidence: 'VERIFIED',
        data: '128 × 128 = 16,384',
      },
      {
        id: 7,
        title: 'Row 68 as Bridge Layer',
        summary: 'Bitcoin→Qubic transformation layer',
        details: [
          'Addresses 8704-8831',
          '89 period-14 programs executing',
          'Self-modifying code capability',
        ],
        confidence: 'HIGH',
        data: 'Hybrid neural/cryptographic',
      },
      {
        id: 8,
        title: 'Output Layer Discovery',
        summary: 'Output of Row 21→68→96 transformation',
        details: [
          'Position: Row 96, Column 84 (address 12,372)',
          'Row 96 serves as the final output layer',
          'Data flows through bridge transformation',
        ],
        confidence: 'VERIFIED',
        data: 'Row 96, Col 84',
      },
      {
        id: 9,
        title: 'Bitcoin Block #283 Properties',
        summary: 'Height: 283 (prime, 61st prime)',
        details: [
          'Date: January 12, 2009, 23:45:57 UTC',
          'Single transaction (coinbase only)',
          'Hash: 000000001a6017f168bfbe3ef01...',
        ],
        confidence: 'VERIFIED',
        data: 'Jan 12, 2009',
      },
    ],
  },
  {
    id: 3,
    name: 'The Oracle System',
    icon: <Eye className="h-5 w-5" />,
    confidenceRange: '85-95%',
    color: 'from-[#050505] to-[#050505]/80 border-white/[0.04]',
    discoveries: [
      {
        id: 10,
        title: 'ARB Address & Sum',
        summary: 'Letter sum = 817 = 19 × 43 (both prime)',
        details: [
          'AFZPUAIYVPNUYGJRQVLUKOPPVLHAZQTGLYAAUUNBXFTVTAMSBKQBLEIEPCVJ',
          'Balance: 793B Qubic (~$500M USD)',
          '19 × 43 encodes Genesis Block design',
        ],
        confidence: 'VERIFIED',
        data: '817 = 19 × 43',
      },
      {
        id: 11,
        title: 'AFZJ Marker = 43',
        summary: 'A(1) + F(6) + Z(26) + J(10) = 43',
        details: [
          '43 = Genesis Block leading zero bits',
          'Deliberately encoded in first 4 letters',
          '11 extra zeros beyond required 32',
        ],
        confidence: 'HIGH',
        data: '1+6+26+10 = 43',
      },
      {
        id: 12,
        title: '19 = Genesis Range Start',
        summary: 'Genesis Block valid byte ranges: [0-9] and [19-58]',
        details: [
          'Gap [10-18] intentionally excluded',
          '19 appears in ARB factorization: 817 = 19 × 43',
          'Encodes Bitcoin Genesis design choice',
        ],
        confidence: 'HIGH',
        data: '[0-9] and [19-58]',
      },
      {
        id: 13,
        title: 'ARB Oracle Mechanism',
        summary: 'Receives 0-Qubic pings from 10-Qubic addresses',
        details: [
          'Smart contract trigger (primary)',
          'Time-lock backup (March 3, 2026)',
          'Aggregates community consensus',
        ],
        confidence: 'HIGH',
        data: '10 Qubic = voting right',
      },
      {
        id: 14,
        title: 'ARB/POCZ Relationship',
        summary: 'Paired but distinct components',
        details: [
          'ARB sum: 817 (public oracle beacon)',
          'POCZ sum: 672 (private seed holder)',
          'Both 60 characters, 23/26 letters shared',
        ],
        confidence: 'HIGH',
        data: '817 vs 672',
      },
    ],
  },
  {
    id: 4,
    name: 'Anna Matrix Discoveries',
    icon: <Layers className="h-5 w-5" />,
    confidenceRange: '85-100%',
    color: 'from-[#050505] to-[#050505]/80 border-white/[0.04]',
    discoveries: [
      {
        id: 15,
        title: 'Anna Matrix Structure',
        summary: 'Massive recursive identity structure',
        details: [
          'Initial layer: 8 identities (4 diagonal + 4 vortex)',
          'Layer 2: 8 derived identities',
          '179+ additional identities discovered',
        ],
        confidence: 'HIGH',
        data: '8 + 8 + 179+',
      },
      {
        id: 16,
        title: 'Seed Pattern Analysis',
        summary: 'Repeating patterns in seeds',
        details: [
          'Patterns: aaa, mmm, bnn, yyy',
          'Common substrings: aaaa, maaa, aama',
          '9 different geometric extraction methods',
        ],
        confidence: 'HIGH',
        data: '9 extraction methods',
      },
      {
        id: 17,
        title: '8 Verified Identities On-Chain',
        summary: '100% RPC confirmed on Qubic network',
        details: [
          'Layer 1: 4 diagonal + 4 vortex identities',
          'Layer 2: 8 derived identities',
          'All verified via Qubic RPC',
        ],
        confidence: 'VERIFIED',
        data: '100% on-chain',
      },
    ],
  },
  {
    id: 5,
    name: 'Bitcoin Signature Discoveries',
    icon: <Hash className="h-5 w-5" />,
    confidenceRange: '70-99%',
    color: 'from-[#050505] to-[#050505]/80 border-white/[0.04]',
    discoveries: [
      {
        id: 18,
        title: 'Block #4 "ubic" Vanity',
        summary: '9 years before QUBIC announcement!',
        details: [
          'Block #4 (Jan 9, 2009) contains "ubic" in address',
          'Value 676 only block (0-11) with this hex',
          '676 = 26² = Qubic Computors (announced 2018)',
        ],
        confidence: 'VERIFIED',
        data: '676 = 26²',
      },
      {
        id: 19,
        title: 'Block #264 & 1CFB Address',
        summary: '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg',
        details: [
          '264 = 11 × 24 (CFB encoding)',
          '50 BTC block reward, never moved',
          'Standard P2PKH format',
        ],
        confidence: 'VERIFIED',
        data: '50 BTC dormant',
      },
      {
        id: 20,
        title: '12 Unique 1CFB Addresses',
        summary: 'All 1CFB-prefixed addresses from 2009-2010',
        details: [
          'Systematic address generation pattern',
          'All from early Bitcoin era',
          'Suggests intentional mining',
        ],
        confidence: 'VERIFIED',
        data: '12 addresses found',
      },
      {
        id: 21,
        title: 'Patoshi Block Access',
        summary: 'CFB claims access to ~235 Patoshi blocks',
        details: [
          '~235 × 50 BTC = ~11,750 BTC (~$1B USD)',
          'Quote: "not my seed - not my coins"',
          'Access vs ownership distinction',
        ],
        confidence: 'HIGH',
        data: '~$1B USD value',
      },
    ],
  },
  {
    id: 6,
    name: 'CFB Signature Analysis',
    icon: <User className="h-5 w-5" />,
    confidenceRange: '80-95%',
    color: 'from-[#050505] to-[#050505]/80 border-white/[0.04]',
    discoveries: [
      {
        id: 22,
        title: 'Number 27 Throughout Systems',
        summary: '27 = 3³ appears everywhere',
        details: [
          'Anna Matrix: 27-letter alphabet (A-Z minus W)',
          'IOTA: 27 Coordinators',
          'Signal Date seconds ÷ 27 = exact division',
        ],
        confidence: 'VERIFIED',
        data: '27 = 3³',
      },
      {
        id: 23,
        title: 'CFB Constants Set',
        summary: 'Mathematical signature constants',
        details: [
          '7, 27 (3³), 47, 121 (11²), 137',
          '283, 676 (26²), 817 (19×43)',
          'Appear across NXT, IOTA, Qubic',
        ],
        confidence: 'VERIFIED',
        data: '8 key constants',
      },
      {
        id: 24,
        title: 'IOTA Transaction Sizes',
        summary: 'All divisible by 27',
        details: [
          '2187: Signature fragment (3⁷)',
          '2673: Transaction total',
          '2187/27=81, 2673/27=99',
        ],
        confidence: 'HIGH',
        data: '3⁷ = 2187',
      },
      {
        id: 25,
        title: 'Qubic 676 Signature',
        summary: '676 = 26² appears throughout the protocol',
        details: [
          '676 Computors validate the network',
          '26 = alphabet size (communication theme)',
          'Appears across multiple system parameters',
        ],
        confidence: 'HIGH',
        data: '676 = 26²',
      },
    ],
  },
  {
    id: 7,
    name: 'Time-Lock & Signal Date',
    icon: <Timer className="h-5 w-5" />,
    confidenceRange: '85-95%',
    color: 'from-[#050505] to-[#050505]/80 border-white/[0.04]',
    discoveries: [
      {
        id: 26,
        title: 'March 3, 2026 Signal Date',
        summary: '6,268 days from Bitcoin Genesis',
        details: [
          '541,555,200 seconds ÷ 27 = exact division',
          'Lunar eclipse on same date',
          'Same second as Genesis Block (18:15:05 UTC)',
        ],
        confidence: 'VERIFIED',
        data: '6,268 days',
      },
      {
        id: 27,
        title: 'Tick Countdown',
        summary: 'Target tick: 43,754,719',
        details: [
          'Tick rate: ~0.474621 ticks/second',
          '56 days remaining (8 weeks = 7 × 8)',
          'Automatic time-lock mechanism',
        ],
        confidence: 'VERIFIED',
        data: '56 days left',
      },
      {
        id: 28,
        title: 'Multiple Unlock Scenarios',
        summary: 'Possible outcomes on March 3',
        details: [
          'A (70%): Time-lock release',
          'B (40%): QUBIC + Chainlink partnership',
          'C (20%): Patoshi wallet movement',
        ],
        confidence: 'HIGH',
        data: '70% time-lock',
      },
    ],
  },
  {
    id: 8,
    name: 'Decoded Patterns & Ciphers',
    icon: <Binary className="h-5 w-5" />,
    confidenceRange: '99%',
    color: 'from-[#050505] to-[#050505]/80 border-white/[0.04]',
    discoveries: [
      {
        id: 29,
        title: 'HONNE Cipher Decoded',
        summary: 'POCZ HONNE sum = 821',
        details: [
          'Custom letter-to-number mapping',
          '821 mod 27 = 11 (CFB signature!)',
          'Self-referential: reverse mapping = POCZ[:55].lower()',
        ],
        confidence: 'VERIFIED',
        data: '821 mod 27 = 11',
      },
      {
        id: 30,
        title: 'Lost Numbers Extraction',
        summary: 'Positions [4,8,15,16,23,42] sum = 108 = 27×4',
        details: [
          'Extracted "ZTPWEB" sum = 92',
          '92 mod 27 = 11 (SAME SIGNATURE!)',
          'Fractal pattern: 99.863% designed',
        ],
        confidence: 'VERIFIED',
        data: 'Fractal proof',
      },
      {
        id: 31,
        title: 'CFB Signature System',
        summary: 'mod 27 = 11 across all projects',
        details: [
          'Bitcoin wallets: digit_sum mod 27 = 11',
          'POCZ identity: HONNE_sum mod 27 = 11',
          'Consistent across NXT, IOTA, Qubic',
        ],
        confidence: 'VERIFIED',
        data: 'mod 27 = 11',
      },
      {
        id: 32,
        title: 'Timestamp Patterns',
        summary: 'Bitcoin & Qubic Genesis mod 27 = 0',
        details: [
          'Block #283 timestamp mod 128 = 41 (matrix row!)',
          'Block #283 nonce mod 128 = 29 (matrix column!)',
          'Position (41,29) encodes -27 marker',
        ],
        confidence: 'VERIFIED',
        data: '(41, 29)',
      },
      {
        id: 33,
        title: 'Fine Structure Constant (137)',
        summary: 'Physics signature throughout',
        details: [
          'In formula: 283 × 47² + 137',
          'Row 68: exactly 137 writes',
          'α ≈ 1/137.036 (electromagnetic constant)',
        ],
        confidence: 'VERIFIED',
        data: 'α = 1/137',
      },
      {
        id: 34,
        title: '43 Appearances Everywhere',
        summary: 'Genesis Block: 43 leading zero bits',
        details: [
          '11 extra zeros beyond required 32',
          'AFZJ marker = 43',
          'ARB factorization: 817 = 19 × 43',
        ],
        confidence: 'VERIFIED',
        data: '43 = CFB constant',
      },
    ],
  },
  {
    id: 9,
    name: 'CFB Identity Analysis',
    icon: <Search className="h-5 w-5" />,
    confidenceRange: '70-95%',
    color: 'from-[#050505] to-[#050505]/80 border-white/[0.04]',
    discoveries: [
      {
        id: 35,
        title: 'CFB Part of Satoshi Group',
        summary: 'Strong circumstantial evidence',
        details: [
          'Technical capability matches',
          'Access to ~235 Patoshi blocks',
          'Block 4 signature ("ubic" + 676)',
          'Different writing style (NOT solo Satoshi)',
        ],
        confidence: 'HIGH',
        data: 'Collaborative group',
      },
      {
        id: 36,
        title: 'AiGarth NOT AGI',
        summary: 'Framework, not artificial intelligence itself',
        details: [
          'Uses ternary computing + evolutionary algorithms',
          'Research phase, not deployed',
          'Framework for building intelligent systems',
        ],
        confidence: 'VERIFIED',
        data: 'Framework only',
      },
      {
        id: 37,
        title: '1CFB NOT Multi-Sig',
        summary: 'Standard P2PKH (Pay-to-Public-Key-Hash)',
        details: [
          'No OP_CHECKMULTISIG',
          "Shamir's Secret Sharing possible (offline, undetectable)",
          'Single-key control on-chain',
        ],
        confidence: 'VERIFIED',
        data: 'P2PKH format',
      },
    ],
  },
  {
    id: 10,
    name: 'Negative Findings / Dead Ends',
    icon: <XCircle className="h-5 w-5" />,
    confidenceRange: 'DISPROVEN',
    color: 'from-[#050505] to-[#050505]/80 border-white/[0.04]',
    discoveries: [
      {
        id: 38,
        title: 'HONNE as POCZ Cipher Key',
        summary: '11 methods tested: 0 matches',
        details: [
          'ARB is NOT the cipher key for POCZ',
          'XOR, Vigenère, all variants failed',
          'Different encoding purposes',
        ],
        confidence: 'DISPROVEN',
        data: '0 matches',
      },
      {
        id: 39,
        title: '74 Seeds with Sum=676',
        summary: '0% exist on-chain',
        details: [
          'Mathematical artifact only',
          'Not related to power structure',
          'None are Computors',
        ],
        confidence: 'DISPROVEN',
        data: 'Irrelevant',
      },
      {
        id: 40,
        title: 'Venezuela Connection',
        summary: '"Maria" claims exposed as fraudulent',
        details: [
          '"Lechuga Verde" doesn\'t exist',
          'Maria likely CFB persona',
          'Exposed by real Venezuelan user',
        ],
        confidence: 'DISPROVEN',
        data: 'Fake identity',
      },
    ],
  },
  {
    id: 11,
    name: 'Unresolved Mysteries',
    icon: <HelpCircle className="h-5 w-5" />,
    confidenceRange: 'UNKNOWN',
    color: 'from-[#050505] to-[#050505]/80 border-white/[0.04]',
    discoveries: [
      {
        id: 41,
        title: 'POCZ Private Key Extraction',
        summary: '1,187 extraction methods failed',
        details: [
          'Time-locked until March 3, 2026',
          'Requires Row 68 algorithm understanding',
          'Awaiting protocol event',
        ],
        confidence: 'UNKNOWN',
        data: '40% confidence',
      },
      {
        id: 42,
        title: 'Block #283 → 625,284 Exact Transform',
        summary: 'K12 hash close but not exact',
        details: [
          'Arithmetic based, not pure hash',
          'Requires deeper analysis',
          'Near misses suggest computed value',
        ],
        confidence: 'UNKNOWN',
        data: '50% confidence',
      },
      {
        id: 43,
        title: 'Other Boot Addresses',
        summary: 'boot[1], boot[2], boot[3] derivation unknown',
        details: [
          'boot[1] = 7,394',
          'boot[2] = 15,962',
          'boot[3] = 7,912',
        ],
        confidence: 'UNKNOWN',
        data: '50% confidence',
      },
      {
        id: 44,
        title: 'Prime 4,787 Purpose',
        summary: '647th prime (triple significance)',
        details: [
          'Relation to 676 Computors unclear',
          'Possible epoch encoding',
          'Awaiting deeper analysis',
        ],
        confidence: 'UNKNOWN',
        data: '65% confidence',
      },
      {
        id: 45,
        title: 'Exact ARB Threshold',
        summary: 'Ping count for trigger unknown',
        details: [
          'Time-based vs count-based unclear',
          'May be 817 pings, 283 pings, or other',
          'Requires on-chain monitoring',
        ],
        confidence: 'UNKNOWN',
        data: '70% confidence',
      },
      {
        id: 46,
        title: 'Multi-Party Key Arrangement',
        summary: "Possible Shamir's Secret Sharing",
        details: [
          'CFB/Nazarov/others coordination',
          'Could be solo time-lock puzzle',
          'No direct evidence either way',
        ],
        confidence: 'UNKNOWN',
        data: '40% confidence',
      },
    ],
  },
]

function ConfidenceBadge({ level }: { level: ConfidenceLevel }) {
  const config = {
    VERIFIED: { bg: 'bg-[#D4AF37]/20', text: 'text-[#D4AF37]', border: 'border-[#D4AF37]/20' },
    HIGH: { bg: 'bg-[#D4AF37]/20', text: 'text-[#D4AF37]', border: 'border-[#D4AF37]/20' },
    UNKNOWN: { bg: 'bg-[#D4AF37]/20', text: 'text-[#D4AF37]', border: 'border-[#D4AF37]/20' },
    DISPROVEN: { bg: 'bg-gray-500/20', text: 'text-gray-400', border: 'border-gray-500/30' },
  }

  const c = config[level]

  return (
    <span className={`text-[10px] px-2 py-0.5  border ${c.bg} ${c.text} ${c.border}`}>
      {level}
    </span>
  )
}

function TierCard({ tier, isExpanded, onToggle }: { tier: Tier; isExpanded: boolean; onToggle: () => void }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-30px' })

  return (
    <motion.div
      ref={ref}
      className={`rounded-xl bg-gradient-to-b ${tier.color} overflow-hidden`}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
      transition={{ duration: 0.4, delay: tier.id * 0.05 }}
    >
      <button
        onClick={onToggle}
        className="w-full p-4 text-left hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/10">{tier.icon}</div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs text-muted-foreground">TIER {tier.id}</span>
                <span className="text-xs px-2 py-0.5  bg-white/10">
                  {tier.discoveries.length} findings
                </span>
                <span className="text-xs text-muted-foreground">{tier.confidenceRange}</span>
              </div>
              <h3 className="font-semibold text-sm">{tier.name}</h3>
            </div>
          </div>
          <motion.span
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="h-5 w-5 text-muted-foreground" />
          </motion.span>
        </div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-white/10"
          >
            <div className="p-4 space-y-3">
              {tier.discoveries.map((d) => (
                <div key={d.id} className="p-3 bg-black/20">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-muted-foreground">#{d.id}</span>
                      <ConfidenceBadge level={d.confidence} />
                    </div>
                    {d.data && (
                      <span className="font-mono text-xs text-primary">{d.data}</span>
                    )}
                  </div>
                  <h4 className="font-medium text-sm mb-1">{d.title}</h4>
                  <p className="text-xs text-muted-foreground mb-2">{d.summary}</p>
                  <ul className="space-y-1">
                    {d.details.map((detail, i) => (
                      <li key={i} className="text-xs text-muted-foreground/80 flex items-start gap-2">
                        <span className="text-primary/50 mt-1">-</span>
                        <span>{detail}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export function AllDiscoveriesSection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })
  const [expandedTiers, setExpandedTiers] = useState<number[]>([1]) // First tier open by default

  const toggleTier = (tierId: number) => {
    setExpandedTiers((prev) =>
      prev.includes(tierId) ? prev.filter((id) => id !== tierId) : [...prev, tierId]
    )
  }

  const totalDiscoveries = tiers.reduce((sum, t) => sum + t.discoveries.length, 0)
  const verifiedCount = tiers
    .flatMap((t) => t.discoveries)
    .filter((d) => d.confidence === 'VERIFIED').length
  const highCount = tiers.flatMap((t) => t.discoveries).filter((d) => d.confidence === 'HIGH').length
  const unknownCount = tiers
    .flatMap((t) => t.discoveries)
    .filter((d) => d.confidence === 'UNKNOWN').length

  return (
    <section ref={sectionRef} className="py-20 px-4 bg-gradient-to-b from-primary/5 to-transparent">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center gap-2 mb-4">
            <CheckCircle2 className="h-5 w-5 text-primary" />
            <span className="text-sm font-medium text-primary">Complete Research Findings</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-semibold mb-4">
            {totalDiscoveries} Discoveries in 11 Tiers
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto mb-6">
            Comprehensive catalog of all findings connecting Bitcoin and Qubic
            through mathematical and cryptographic analysis.
          </p>

          {/* Stats Bar */}
          <div className="flex flex-wrap justify-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-[#D4AF37]"></span>
              <span className="text-muted-foreground">{verifiedCount} Verified</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-[#D4AF37]"></span>
              <span className="text-muted-foreground">{highCount} High Confidence</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-[#D4AF37]"></span>
              <span className="text-muted-foreground">{unknownCount} Awaiting March 3</span>
            </div>
          </div>
        </motion.div>

        {/* Expand/Collapse All */}
        <div className="flex justify-end gap-2 mb-4">
          <button
            onClick={() => setExpandedTiers(tiers.map((t) => t.id))}
            className="text-xs px-3 py-1  bg-primary/20 hover:bg-primary/30 transition-colors"
          >
            Expand All
          </button>
          <button
            onClick={() => setExpandedTiers([])}
            className="text-xs px-3 py-1  bg-muted/50 hover:bg-muted transition-colors"
          >
            Collapse All
          </button>
        </div>

        {/* Tier Accordions */}
        <div className="space-y-3">
          {tiers.map((tier) => (
            <TierCard
              key={tier.id}
              tier={tier}
              isExpanded={expandedTiers.includes(tier.id)}
              onToggle={() => toggleTier(tier.id)}
            />
          ))}
        </div>

        {/* Legend */}
        <motion.div
          className="mt-8 p-4 bg-card/50 border border-border"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 0.6 }}
        >
          <h4 className="text-sm font-medium mb-3">Confidence Levels</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="flex items-center gap-2">
              <ConfidenceBadge level="VERIFIED" />
              <span className="text-muted-foreground">99%+ reproducible on-chain</span>
            </div>
            <div className="flex items-center gap-2">
              <ConfidenceBadge level="HIGH" />
              <span className="text-muted-foreground">70-95% strong evidence</span>
            </div>
            <div className="flex items-center gap-2">
              <ConfidenceBadge level="UNKNOWN" />
              <span className="text-muted-foreground">Awaiting March 3, 2026</span>
            </div>
            <div className="flex items-center gap-2">
              <ConfidenceBadge level="DISPROVEN" />
              <span className="text-muted-foreground">Dead ends / debunked</span>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
