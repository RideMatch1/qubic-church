/**
 * AI Market Creator
 *
 * Parses natural language input into structured market definitions.
 * Uses the existing LLMClient (Groq) with extract<T>() for structured output.
 *
 * Examples:
 *   "BTC over 200K by June" → price market, price_above, 200000
 *   "Wer gewinnt die EM 2028?" → ai market, 4 options, sports category
 *   "Will OpenAI release GPT-5?" → ai market, yes/no, tech category
 */

import type { MarketType, Category, ResolutionType } from './market-db'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ParsedMarket {
  marketType: MarketType
  question: string
  options: string[]
  pair: string | null
  resolutionType: ResolutionType | null
  resolutionTarget: number | null
  resolutionTargetHigh: number | null
  category: Category
  closeDate: string
  endDate: string
}

export interface ParseResult {
  success: boolean
  parsed: ParsedMarket | null
  confidence: number
  error?: string
}

// ---------------------------------------------------------------------------
// Market Schema for LLM extraction
// ---------------------------------------------------------------------------

const MARKET_SCHEMA = `{
  "marketType": "price | sports | ai | custom",
  "question": "Clear, specific question in English",
  "options": ["Option 0", "Option 1", ...],
  "pair": "btc/usdt | eth/usdt | sol/usdt | null",
  "resolutionType": "price_above | price_below | price_range | price_bracket | null",
  "resolutionTarget": 100000,
  "resolutionTargetHigh": null,
  "category": "crypto | sports | politics | tech | entertainment | other",
  "closeDate": "2026-03-30T00:00:00Z",
  "endDate": "2026-03-31T00:00:00Z"
}

Rules:
- marketType "price": crypto price predictions (requires pair, resolutionType, resolutionTarget)
- marketType "sports": sports events (options = team/player names)
- marketType "ai": anything that can be fact-checked (news, politics, tech)
- marketType "custom": extremely subjective questions
- For YES/NO questions, options should be ["Yes", "No"]
- For multi-option, provide 2-8 specific options
- closeDate = when betting closes (1 day before endDate)
- endDate = when the result should be known
- Always use English for the question, even if input is in another language
- Supported pairs: btc/usdt, eth/usdt, sol/usdt, xrp/usdt, bnb/usdt, doge/usdt, ada/usdt, avax/usdt, link/usdt, dot/usdt, ltc/usdt, sui/usdt, near/usdt, trx/usdt, atom/usdt, apt/usdt, qubic/usdt, eth/btc
- Today's date: ${new Date().toISOString().split('T')[0]}`

// ---------------------------------------------------------------------------
// Parser
// ---------------------------------------------------------------------------

/**
 * Parse a natural language market idea into structured market data.
 * Uses the existing LLMClient.extract<T>() for structured output.
 */
export async function parseNaturalLanguageMarket(
  userInput: string,
): Promise<ParseResult> {
  try {
    // Dynamic import to avoid circular deps
    const { getLLMClient } = await import('@/lib/agents/llm-client')
    const llm = getLLMClient()

    if (!llm.isReady()) {
      return {
        success: false,
        parsed: null,
        confidence: 0,
        error: 'LLM client not available (GROQ_API_KEY not set)',
      }
    }

    const result = await llm.extract<ParsedMarket>(
      `Parse this prediction market idea into structured data.\n\nUser input: "${userInput}"\n\nToday: ${new Date().toISOString().split('T')[0]}`,
      MARKET_SCHEMA,
    )

    if (!result) {
      return {
        success: false,
        parsed: null,
        confidence: 0,
        error: 'Failed to parse market from input',
      }
    }

    // Validate parsed result
    const validation = validateParsedMarket(result)
    if (!validation.valid) {
      return {
        success: false,
        parsed: null,
        confidence: 0.3,
        error: validation.error,
      }
    }

    return {
      success: true,
      parsed: result,
      confidence: 0.9,
    }
  } catch (err) {
    return {
      success: false,
      parsed: null,
      confidence: 0,
      error: err instanceof Error ? err.message : 'Unknown error',
    }
  }
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

function validateParsedMarket(m: ParsedMarket): { valid: boolean; error?: string } {
  if (!m.question || m.question.length < 10) {
    return { valid: false, error: 'Question too short' }
  }

  if (!m.options || m.options.length < 2 || m.options.length > 8) {
    return { valid: false, error: 'Options must be 2-8 items' }
  }

  if (!m.closeDate || !m.endDate) {
    return { valid: false, error: 'Missing dates' }
  }

  // Validate close date is in the future
  const closeDate = new Date(m.closeDate)
  if (closeDate <= new Date()) {
    return { valid: false, error: 'Close date must be in the future' }
  }

  // Price markets need pair and target
  if (m.marketType === 'price') {
    if (!m.pair) {
      return { valid: false, error: 'Price markets need a trading pair' }
    }
    if (m.resolutionTarget === null || m.resolutionTarget === undefined) {
      return { valid: false, error: 'Price markets need a resolution target' }
    }
  }

  return { valid: true }
}
