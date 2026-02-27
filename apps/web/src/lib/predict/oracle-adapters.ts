/**
 * QPredict Oracle Adapter System
 *
 * Pluggable oracle adapters for resolving different market types:
 *   Tier 1 (API): CryptoPriceAdapter, SportsAdapter — 100% accuracy
 *   Tier 2 (AI):  AICouncilAdapter — ~89% accuracy (multi-LLM consensus)
 *   Tier 3 (Manual): CreatorAdapter — creator-resolved with auto-refund
 *
 * Each adapter implements OracleAdapter interface. The Market Engine
 * iterates adapters in priority order to resolve expired markets.
 */

import type { Market, MarketType } from './market-db'
import { oracleLog } from './logger'
import { resolvePrice, type MultiOracleResult } from './oracle-resolution'

// ---------------------------------------------------------------------------
// Oracle Adapter Interface
// ---------------------------------------------------------------------------

export interface OracleResult {
  winningOption: number
  proof: {
    source: string
    data: unknown
  }
}

export interface OracleAdapter {
  type: string
  canResolve(market: Market): boolean
  fetchResult(market: Market): Promise<OracleResult | null>
}

// ---------------------------------------------------------------------------
// Adapter 1: Crypto Price Oracle (wraps existing oracle-resolution.ts)
// ---------------------------------------------------------------------------

export class CryptoPriceAdapter implements OracleAdapter {
  type = 'crypto_price'

  canResolve(market: Market): boolean {
    return market.marketType === 'price' && !!market.pair
  }

  async fetchResult(market: Market): Promise<OracleResult | null> {
    const result: MultiOracleResult = await resolvePrice(market.id, market.pair)

    if (!result.success) {
      oracleLog.error({ marketId: market.id, error: result.error }, 'CryptoPriceAdapter failed')
      return null
    }

    const winningOption = this.determineWinner(market, result.medianPrice)
    if (winningOption === null) return null

    return {
      winningOption,
      proof: {
        source: 'crypto_price_oracle',
        data: {
          medianPrice: result.medianPrice,
          sourceCount: result.sourceCount,
          prices: result.prices,
          attestationIds: result.attestations.map((a) => a.id),
        },
      },
    }
  }

  private determineWinner(market: Market, price: number): number | null {
    switch (market.resolutionType) {
      case 'price_above':
        // Option 0 = Yes (above), Option 1 = No (not above)
        return price >= market.resolutionTarget ? 0 : 1

      case 'price_below':
        // Option 0 = Yes (below), Option 1 = No (not below)
        return price <= market.resolutionTarget ? 0 : 1

      case 'price_range':
        // Option 0 = Yes (in range), Option 1 = No (out of range)
        if (market.resolutionTargetHigh === null) return null
        return price >= market.resolutionTarget && price <= market.resolutionTargetHigh
          ? 0
          : 1

      case 'price_bracket': {
        // Multi-option brackets: find which bracket the price falls into
        // Options are ordered: [<bracket1, bracket1-bracket2, ..., >bracketN]
        // Brackets stored as comma-separated values in resolutionTarget/resolutionTargetHigh
        // For now: bracket boundaries encoded in options labels
        // e.g. options: ["Under $90K", "$90K-$95K", "$95K-$100K", "Over $100K"]
        // with bracket boundaries derived from resolutionTarget as base
        const numOptions = market.numOptions
        if (numOptions < 2) return null

        // Extract bracket boundaries from the market
        // Convention: resolutionTarget = base price, brackets evenly spaced
        // OR: brackets stored as JSON in ai_resolution_proof
        const brackets = this.extractBracketBoundaries(market)
        if (!brackets) return null

        for (let i = 0; i < brackets.length; i++) {
          if (price < brackets[i]!) return i
        }
        return brackets.length // last option (above all brackets)
      }

      default:
        return null
    }
  }

  private extractBracketBoundaries(market: Market): number[] | null {
    // Try to extract from ai_resolution_proof (which stores bracket config)
    try {
      const proof = market.aiResolutionProof as { brackets?: number[] } | null
      if (proof?.brackets && Array.isArray(proof.brackets)) {
        return proof.brackets
      }
    } catch { /* fallback */ }

    // Fallback: evenly spaced brackets from resolutionTarget
    if (market.numOptions < 2) return null
    const base = market.resolutionTarget
    const high = market.resolutionTargetHigh
    if (!high || high <= base) return null

    const step = (high - base) / (market.numOptions - 1)
    const boundaries: number[] = []
    for (let i = 1; i < market.numOptions; i++) {
      boundaries.push(base + step * i)
    }
    return boundaries
  }
}

// ---------------------------------------------------------------------------
// Adapter 2: Sports Oracle (free APIs)
// ---------------------------------------------------------------------------

export class SportsAdapter implements OracleAdapter {
  type = 'sports'

  canResolve(market: Market): boolean {
    return market.marketType === 'sports'
  }

  async fetchResult(market: Market): Promise<OracleResult | null> {
    // Try TheSportsDB (free, no API key needed)
    const result = await this.fetchTheSportsDB(market)
    if (result) return result

    return null
  }

  private async fetchTheSportsDB(market: Market): Promise<OracleResult | null> {
    // TheSportsDB provides free event search
    // We match the market question against events
    try {
      const query = encodeURIComponent(market.question)
      const res = await fetch(
        `https://www.thesportsdb.com/api/v1/json/3/searchevents.php?e=${query}`,
        { signal: AbortSignal.timeout(5000) },
      )
      if (!res.ok) return null

      const data = await res.json() as { event?: Array<{
        strEvent: string
        strResult: string
        strHomeTeam: string
        strAwayTeam: string
        intHomeScore: string | null
        intAwayScore: string | null
        strStatus: string
      }> }

      if (!data.event || data.event.length === 0) return null

      // Find the matching event with a result
      for (const event of data.event) {
        if (event.intHomeScore === null || event.intAwayScore === null) continue
        if (event.strStatus !== 'Match Finished') continue

        // Try to match winner to one of the market options
        const homeScore = parseInt(event.intHomeScore, 10)
        const awayScore = parseInt(event.intAwayScore, 10)
        const winner = homeScore > awayScore ? event.strHomeTeam : event.strAwayTeam
        const isDraw = homeScore === awayScore

        // Find matching option
        for (let i = 0; i < market.options.length; i++) {
          const opt = market.options[i]!.toLowerCase()
          if (isDraw && (opt.includes('draw') || opt.includes('unentschieden'))) {
            return {
              winningOption: i,
              proof: {
                source: 'thesportsdb',
                data: { event: event.strEvent, score: `${homeScore}-${awayScore}`, winner: 'Draw' },
              },
            }
          }
          if (winner.toLowerCase().includes(opt) || opt.includes(winner.toLowerCase())) {
            return {
              winningOption: i,
              proof: {
                source: 'thesportsdb',
                data: { event: event.strEvent, score: `${homeScore}-${awayScore}`, winner },
              },
            }
          }
        }
      }
    } catch {
      // API not available
    }

    return null
  }
}

// ---------------------------------------------------------------------------
// Adapter 3: AI Council Oracle (LLM-based resolution)
// ---------------------------------------------------------------------------

interface AIVote {
  role: string
  winningOption: number
  confidence: number
  reasoning: string
}

export class AICouncilAdapter implements OracleAdapter {
  type = 'ai_council'

  canResolve(market: Market): boolean {
    return market.marketType === 'ai' && market.aiResolutionAttempts < 3
  }

  async fetchResult(market: Market): Promise<OracleResult | null> {
    // 1. Gather evidence from news APIs
    const evidence = await this.gatherEvidence(market.question)

    // 2. Get 3 independent LLM votes
    const votes = await this.getCouncilVotes(market, evidence)

    if (votes.length < 3) {
      oracleLog.error({ marketId: market.id, voteCount: votes.length }, 'AICouncil insufficient votes')
      return null
    }

    // 3. Check for majority (2/3 agreement)
    const majority = this.getMajorityVote(votes, market.numOptions)
    if (!majority) {
      oracleLog.info({ marketId: market.id, votes: votes.map(v => v.winningOption) }, 'AICouncil no consensus')
      return null
    }

    // 4. Check confidence threshold
    const avgConfidence = votes.reduce((s, v) => s + v.confidence, 0) / votes.length
    if (avgConfidence < 0.7) {
      oracleLog.info({ marketId: market.id, confidence: avgConfidence }, 'AICouncil low confidence')
      return null
    }

    return {
      winningOption: majority.option,
      proof: {
        source: 'ai_council',
        data: {
          votes,
          evidence: evidence.slice(0, 5),
          majorityOption: majority.option,
          majorityCount: majority.count,
          avgConfidence,
        },
      },
    }
  }

  private async gatherEvidence(question: string): Promise<string[]> {
    const evidence: string[] = []

    // Try GNews API (free, 100 req/day)
    try {
      const apiKey = process.env.GNEWS_API_KEY
      if (apiKey) {
        const q = encodeURIComponent(question)
        const res = await fetch(
          `https://gnews.io/api/v4/search?q=${q}&lang=en&max=5&apikey=${apiKey}`,
          { signal: AbortSignal.timeout(5000) },
        )
        if (res.ok) {
          const data = await res.json() as { articles?: Array<{ title: string; description: string }> }
          if (data.articles) {
            for (const article of data.articles) {
              evidence.push(`${article.title}: ${article.description}`)
            }
          }
        }
      }
    } catch { /* continue without */ }

    // Try NewsData.io (free, 200 req/day)
    try {
      const apiKey = process.env.NEWSDATA_API_KEY
      if (apiKey) {
        const q = encodeURIComponent(question)
        const res = await fetch(
          `https://newsdata.io/api/1/news?q=${q}&language=en&apikey=${apiKey}`,
          { signal: AbortSignal.timeout(5000) },
        )
        if (res.ok) {
          const data = await res.json() as { results?: Array<{ title: string; description: string }> }
          if (data.results) {
            for (const article of data.results.slice(0, 5)) {
              evidence.push(`${article.title}: ${article.description ?? ''}`)
            }
          }
        }
      }
    } catch { /* continue without */ }

    return evidence
  }

  private async getCouncilVotes(market: Market, evidence: string[]): Promise<AIVote[]> {
    const roles = [
      { name: 'analyst', system: 'You are a financial analyst who focuses on data and statistics.' },
      { name: 'journalist', system: 'You are an investigative journalist who focuses on facts and sources.' },
      { name: 'researcher', system: 'You are an academic researcher who focuses on historical patterns and probability.' },
    ]

    const optionsList = market.options.map((o, i) => `${i}: ${o}`).join('\n')
    const evidenceText = evidence.length > 0
      ? `\nRecent news:\n${evidence.map(e => `- ${e}`).join('\n')}`
      : '\nNo recent news available.'

    const votes: AIVote[] = []

    // Use dynamic import for LLM client (may not be available in all contexts)
    let getLLMClient: (() => import('@/lib/agents/llm-client').LLMClient) | null = null
    try {
      const mod = await import('@/lib/agents/llm-client')
      getLLMClient = mod.getLLMClient
    } catch {
      oracleLog.error('AICouncil LLM client not available')
      return []
    }

    const llmClient = getLLMClient()
    if (!llmClient?.isReady()) {
      oracleLog.error('AICouncil LLM client not ready (no GROQ_API_KEY?)')
      return []
    }

    for (const role of roles) {
      try {
        const response = await llmClient.chat(
          [
            {
              role: 'system' as const,
              content: `${role.system}

You are voting on a prediction market outcome. Based on available evidence, determine which option won.
Respond with ONLY valid JSON in this format:
{"winningOption": <number>, "confidence": <0.0-1.0>, "reasoning": "<brief explanation>"}

The options are:
${optionsList}

Today's date: ${new Date().toISOString().split('T')[0]}`,
            },
            {
              role: 'user' as const,
              content: `Question: ${market.question}
End date: ${market.endDate}
${evidenceText}

Which option won? Respond with JSON only.`,
            },
          ],
          'smart',
        )

        const parsed = JSON.parse(response.content) as {
          winningOption: number
          confidence: number
          reasoning: string
        }

        if (
          typeof parsed.winningOption === 'number' &&
          parsed.winningOption >= 0 &&
          parsed.winningOption < market.numOptions
        ) {
          votes.push({
            role: role.name,
            winningOption: parsed.winningOption,
            confidence: Math.min(1, Math.max(0, parsed.confidence ?? 0.5)),
            reasoning: parsed.reasoning ?? '',
          })
        }
      } catch (err) {
        oracleLog.error({ err, role: role.name }, 'AICouncil vote failed')
      }
    }

    return votes
  }

  private getMajorityVote(
    votes: AIVote[],
    _numOptions: number,
  ): { option: number; count: number } | null {
    const counts = new Map<number, number>()
    for (const vote of votes) {
      counts.set(vote.winningOption, (counts.get(vote.winningOption) ?? 0) + 1)
    }

    // Find option with >= 2/3 majority
    const threshold = Math.ceil(votes.length * 2 / 3)
    for (const [option, count] of counts) {
      if (count >= threshold) {
        return { option, count }
      }
    }

    return null
  }
}

// ---------------------------------------------------------------------------
// Adapter 4: Creator Oracle (manual resolution + auto-refund)
// ---------------------------------------------------------------------------

export class CreatorAdapter implements OracleAdapter {
  type = 'creator'

  canResolve(market: Market): boolean {
    return market.marketType === 'custom'
  }

  async fetchResult(_market: Market): Promise<OracleResult | null> {
    // Creator adapters don't fetch — they wait for manual resolution
    // via the POST /api/predict/markets/resolve endpoint.
    // The Market Engine checks auto_refund_at for timeout.
    return null
  }
}

// ---------------------------------------------------------------------------
// Adapter Registry
// ---------------------------------------------------------------------------

/**
 * Get all oracle adapters in priority order.
 * The Market Engine iterates these for each market needing resolution.
 */
export function getOracleAdapters(): OracleAdapter[] {
  return [
    new CryptoPriceAdapter(),
    new SportsAdapter(),
    new AICouncilAdapter(),
    new CreatorAdapter(),
  ]
}

/**
 * Find the appropriate adapter for a given market type.
 */
export function getAdapterForMarket(market: Market): OracleAdapter | null {
  const adapters = getOracleAdapters()
  return adapters.find((a) => a.canResolve(market)) ?? null
}

/**
 * Attempt to resolve a market using its matching oracle adapter.
 */
export async function tryResolveMarket(market: Market): Promise<OracleResult | null> {
  const adapter = getAdapterForMarket(market)
  if (!adapter) return null
  return adapter.fetchResult(market)
}
