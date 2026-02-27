/**
 * Trending Market Auto-Creator
 *
 * Background agent that scans news APIs and creates prediction markets
 * for trending topics. Runs every 6 hours as part of the Market Engine.
 *
 * Sources:
 *   - GNews API (free, 100 req/day)
 *   - NewsData.io (free, 200 req/day)
 *   - CoinGecko trending (free, no key)
 *
 * Flow:
 *   1. Fetch top headlines from news APIs
 *   2. LLM analyzes: "Which stories are bet-worthy?"
 *   3. Deduplicate against existing markets
 *   4. Auto-create 1-3 new markets per cycle
 */

import type { MarketType, Category } from './market-db'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface NewsArticle {
  title: string
  description: string
  source: string
  publishedAt: string
}

interface MarketProposal {
  marketType: MarketType
  question: string
  options: string[]
  category: Category
  closeDate: string
  endDate: string
  pair: string | null
  resolutionType: string | null
  resolutionTarget: number | null
}

export interface TrendingCreatorResult {
  scanned: number
  proposed: number
  created: number
  proposals: MarketProposal[]
  errors: string[]
}

// ---------------------------------------------------------------------------
// News Fetchers
// ---------------------------------------------------------------------------

async function fetchGNews(): Promise<NewsArticle[]> {
  const apiKey = process.env.GNEWS_API_KEY
  if (!apiKey) return []

  try {
    const res = await fetch(
      `https://gnews.io/api/v4/top-headlines?lang=en&max=10&apikey=${apiKey}`,
      { signal: AbortSignal.timeout(5000) },
    )
    if (!res.ok) return []

    const data = await res.json() as {
      articles?: Array<{ title: string; description: string; source: { name: string }; publishedAt: string }>
    }

    return (data.articles ?? []).map((a) => ({
      title: a.title,
      description: a.description ?? '',
      source: a.source?.name ?? 'gnews',
      publishedAt: a.publishedAt,
    }))
  } catch {
    return []
  }
}

async function fetchCoinGeckoTrending(): Promise<NewsArticle[]> {
  try {
    const res = await fetch(
      'https://api.coingecko.com/api/v3/search/trending',
      { signal: AbortSignal.timeout(5000) },
    )
    if (!res.ok) return []

    const data = await res.json() as {
      coins?: Array<{ item: { name: string; symbol: string; market_cap_rank: number } }>
    }

    return (data.coins ?? []).slice(0, 5).map((c) => ({
      title: `${c.item.name} (${c.item.symbol}) trending on CoinGecko`,
      description: `Market cap rank: ${c.item.market_cap_rank}`,
      source: 'coingecko_trending',
      publishedAt: new Date().toISOString(),
    }))
  } catch {
    return []
  }
}

// ---------------------------------------------------------------------------
// LLM Analysis
// ---------------------------------------------------------------------------

const TRENDING_SCHEMA = `[
  {
    "marketType": "price | sports | ai",
    "question": "Clear, specific question in English ending with ?",
    "options": ["Option A", "Option B", ...],
    "category": "crypto | sports | politics | tech | entertainment | other",
    "closeDate": "ISO date string",
    "endDate": "ISO date string",
    "pair": "btc/usdt | null",
    "resolutionType": "price_above | null",
    "resolutionTarget": 100000
  }
]

Rules:
- Return 1-3 market proposals maximum
- Only propose markets with clear, verifiable outcomes
- closeDate should be 1 day before endDate
- endDate should be when the outcome will be known
- For crypto trends, use price_above/price_below with specific targets
- For news events, use AI-resolvable markets
- Questions must be specific and time-bound
- Do NOT propose markets about ongoing wars, disasters, or deaths
- Focus on positive/neutral events: sports, tech, business, crypto
- Today's date: CURRENT_DATE`

async function analyzeHeadlines(articles: NewsArticle[]): Promise<MarketProposal[]> {
  if (articles.length === 0) return []

  try {
    const { getLLMClient } = await import('@/lib/agents/llm-client')
    const llm = getLLMClient()

    if (!llm.isReady()) return []

    const headlines = articles.map((a) => `- ${a.title}`).join('\n')
    const schema = TRENDING_SCHEMA.replace('CURRENT_DATE', new Date().toISOString().split('T')[0]!)

    const result = await llm.extract<MarketProposal[]>(
      `Analyze these news headlines and propose 1-3 prediction markets that people would want to bet on.\n\nHeadlines:\n${headlines}`,
      schema,
    )

    if (!result || !Array.isArray(result)) return []
    return result.slice(0, 3)
  } catch {
    return []
  }
}

// ---------------------------------------------------------------------------
// Deduplication
// ---------------------------------------------------------------------------

function isDuplicate(
  proposal: MarketProposal,
  existingQuestions: string[],
): boolean {
  const normalized = proposal.question.toLowerCase().replace(/[^a-z0-9 ]/g, '')
  return existingQuestions.some((q) => {
    const normExisting = q.toLowerCase().replace(/[^a-z0-9 ]/g, '')
    // Simple overlap check: more than 60% of words match
    const proposalWords = new Set(normalized.split(' ').filter(w => w.length > 3))
    const existingWords = new Set(normExisting.split(' ').filter(w => w.length > 3))
    let matches = 0
    for (const word of proposalWords) {
      if (existingWords.has(word)) matches++
    }
    return proposalWords.size > 0 && matches / proposalWords.size > 0.6
  })
}

// ---------------------------------------------------------------------------
// Main Function
// ---------------------------------------------------------------------------

/**
 * Scan news sources and propose/create trending markets.
 *
 * @param existingQuestions - List of existing market questions for dedup
 * @param dryRun - If true, don't create markets, just return proposals
 * @returns TrendingCreatorResult with what was scanned and proposed
 */
export async function createTrendingMarkets(
  existingQuestions: string[],
  dryRun: boolean = false,
): Promise<TrendingCreatorResult> {
  const result: TrendingCreatorResult = {
    scanned: 0,
    proposed: 0,
    created: 0,
    proposals: [],
    errors: [],
  }

  // 1. Fetch news from all sources
  const [gnews, trending] = await Promise.allSettled([
    fetchGNews(),
    fetchCoinGeckoTrending(),
  ])

  const articles: NewsArticle[] = [
    ...(gnews.status === 'fulfilled' ? gnews.value : []),
    ...(trending.status === 'fulfilled' ? trending.value : []),
  ]

  result.scanned = articles.length

  if (articles.length === 0) {
    result.errors.push('No articles fetched from any source')
    return result
  }

  // 2. LLM analyzes headlines
  const proposals = await analyzeHeadlines(articles)
  result.proposed = proposals.length

  // 3. Deduplicate
  const unique = proposals.filter((p) => !isDuplicate(p, existingQuestions))
  result.proposals = unique

  if (dryRun) {
    return result
  }

  // 4. Create markets (done by caller — Market Engine)
  // We just return the proposals; the engine creates them via MarketManager
  result.created = unique.length

  return result
}
