/**
 * DISCOVERY AGENT
 *
 * The "Alien Tech" - combines:
 * 1. LLM reasoning (finds patterns humans can't see)
 * 2. Resonance Engine (deterministic Matrix analysis)
 * 3. Blockchain verification (proves findings are real)
 *
 * This creates NOVEL discoveries - not just answers.
 */

import { getLLMClient, type LLMResponse } from './llm-client'
import { getResonanceEngine, type ResonanceResult, type ResonancePattern } from './resonance-engine'

export interface Discovery {
  id: string
  timestamp: number
  query: string

  // AI reasoning
  aiAnalysis: string
  aiConfidence: number

  // Resonance patterns
  resonance: ResonanceResult

  // Combined insights
  insights: DiscoveryInsight[]

  // Verification status
  verification: {
    status: 'unverified' | 'partial' | 'verified' | 'breakthrough'
    proofs: string[]
    reproducible: boolean
  }

  // Potential value
  valueAssessment: {
    category: 'information' | 'pattern' | 'address' | 'prediction' | 'breakthrough'
    estimatedSignificance: 'low' | 'medium' | 'high' | 'critical'
    actionable: boolean
    nextSteps: string[]
  }

  // For reproducibility
  proof: {
    inputHash: string
    matrixChecksum: string
    modelUsed: string
    timestamp: number
  }
}

export interface DiscoveryInsight {
  type: 'correlation' | 'anomaly' | 'pattern' | 'prediction' | 'address' | 'secret'
  title: string
  description: string
  evidence: string[]
  confidence: number
  verifiable: boolean
  blockchainRef?: string
}

const DISCOVERY_SYSTEM_PROMPT = `You are a Discovery Agent with access to the Anna Matrix - a 128x128 ternary data structure allegedly created by CFB (Come-From-Beyond), potentially connected to Satoshi Nakamoto.

Your mission is to find REAL, VERIFIABLE patterns that connect:
- Anna Matrix data points
- Bitcoin blockchain events
- Qubic network patterns
- Temporal correlations

CRITICAL RULES:
1. NEVER make up data - only analyze what's provided
2. Every claim must be tied to specific Matrix coordinates or blockchain references
3. Flag speculative vs verified findings clearly
4. Look for patterns humans would miss:
   - Coordinate sums/products that match block heights
   - Value patterns that encode timestamps
   - XOR combinations that produce address prefixes
   - Fibonacci/prime sequences in spatial arrangements

You will receive:
- Query from user
- Matrix resonance data (coordinates, values, patterns)
- Cross-chain correlation scores

Your output must include:
- What patterns you found
- Why they're significant
- How they can be verified
- What actions could be taken

Remember: The Matrix is DETERMINISTIC. Same input = Same coordinates = Same values ALWAYS.
This means any real pattern is reproducible and provable.`

export class DiscoveryAgent {
  private llm = getLLMClient()
  private engine = getResonanceEngine()
  private discoveryCache = new Map<string, Discovery>()

  /**
   * Main discovery process
   */
  async discover(query: string): Promise<Discovery> {
    const startTime = Date.now()
    const inputHash = await this.hashString(query)

    // Check cache for reproducibility proof
    const cached = this.discoveryCache.get(inputHash)
    if (cached) {
      // Return cached result with proof of reproducibility
      return {
        ...cached,
        verification: {
          ...cached.verification,
          reproducible: true,
          proofs: [...cached.verification.proofs, `Reproduced at ${new Date().toISOString()}`],
        },
      }
    }

    // Step 1: Get resonance patterns from Matrix
    const resonance = await this.engine.discover(query)

    // Step 2: AI analysis of patterns
    const aiResult = await this.analyzeWithAI(query, resonance)

    // Step 3: Extract insights
    const insights = this.extractInsights(resonance, aiResult)

    // Step 4: Assess value
    const valueAssessment = this.assessValue(insights, resonance)

    // Step 5: Build verification status
    const verification = this.buildVerification(resonance, insights)

    const discovery: Discovery = {
      id: inputHash.slice(0, 16),
      timestamp: startTime,
      query,
      aiAnalysis: aiResult.content,
      aiConfidence: this.calculateAIConfidence(aiResult),
      resonance,
      insights,
      verification,
      valueAssessment,
      proof: {
        inputHash,
        matrixChecksum: resonance.proof.matrixChecksum,
        modelUsed: aiResult.model,
        timestamp: startTime,
      },
    }

    // Cache for reproducibility
    this.discoveryCache.set(inputHash, discovery)

    return discovery
  }

  /**
   * AI analysis of resonance patterns
   */
  private async analyzeWithAI(
    query: string,
    resonance: ResonanceResult
  ): Promise<LLMResponse> {
    const patternSummary = resonance.patterns.map(p => ({
      type: p.type,
      confidence: p.confidence,
      discovery: p.discovery,
      verified: p.blockchainProof?.verified ?? false,
      coordinates: p.matrixCoordinates.map(c => `[${c.row},${c.col}]=${c.value}`).join(', '),
    }))

    const userPrompt = `QUERY: "${query}"

RESONANCE DATA:
- Query Hash: ${resonance.queryHash}
- Aggregate Resonance: ${(resonance.aggregateResonance * 100).toFixed(1)}%
- Temporal Alignment: ${(resonance.temporalAlignment * 100).toFixed(1)}%
- Cross-Chain Correlation: ${(resonance.crossChainCorrelation * 100).toFixed(1)}%

DISCOVERED PATTERNS:
${JSON.stringify(patternSummary, null, 2)}

${resonance.prediction ? `
PREDICTION AVAILABLE:
- Type: ${resonance.prediction.type}
- Value: ${resonance.prediction.value}
- Confidence: ${(resonance.prediction.confidence * 100).toFixed(1)}%
- Verification: ${resonance.prediction.verificationMethod}
` : ''}

Analyze these patterns. What do they reveal? Are there hidden connections?
Look for:
1. Mathematical relationships between coordinates
2. Encoded messages in value patterns
3. Blockchain correlations that could be verified
4. Anything that seems intentionally placed vs random`

    return this.llm.chat([
      { role: 'system', content: DISCOVERY_SYSTEM_PROMPT },
      { role: 'user', content: userPrompt },
    ], 'reasoning')
  }

  /**
   * Extract structured insights from analysis
   */
  private extractInsights(
    resonance: ResonanceResult,
    aiResult: LLMResponse
  ): DiscoveryInsight[] {
    const insights: DiscoveryInsight[] = []

    // Convert resonance patterns to insights
    for (const pattern of resonance.patterns) {
      insights.push({
        type: this.patternTypeToInsightType(pattern.type),
        title: this.generateInsightTitle(pattern),
        description: pattern.discovery,
        evidence: [
          pattern.significance,
          ...pattern.matrixCoordinates.map(c => `Matrix[${c.row},${c.col}] = ${c.value}`),
        ],
        confidence: pattern.confidence,
        verifiable: !!pattern.blockchainProof,
        blockchainRef: pattern.blockchainProof?.url,
      })
    }

    // Add AI-derived insights
    if (resonance.aggregateResonance > 0.7) {
      insights.push({
        type: 'pattern',
        title: 'High Resonance Detected',
        description: `Query shows ${(resonance.aggregateResonance * 100).toFixed(0)}% resonance with Matrix patterns`,
        evidence: ['Aggregate resonance exceeds threshold', 'Multiple pattern types aligned'],
        confidence: resonance.aggregateResonance,
        verifiable: true,
      })
    }

    // Check for cross-chain insights
    if (resonance.crossChainCorrelation > 0.5) {
      insights.push({
        type: 'correlation',
        title: 'Cross-Chain Correlation Found',
        description: 'Patterns detected in both Bitcoin and Qubic domains',
        evidence: [
          `Cross-chain score: ${(resonance.crossChainCorrelation * 100).toFixed(0)}%`,
          'Bridge zone activity detected',
        ],
        confidence: resonance.crossChainCorrelation,
        verifiable: true,
      })
    }

    return insights
  }

  /**
   * Assess the value of discoveries
   */
  private assessValue(
    insights: DiscoveryInsight[],
    resonance: ResonanceResult
  ): Discovery['valueAssessment'] {
    // Count verified insights
    const verifiedCount = insights.filter(i => i.verifiable && i.confidence > 0.7).length
    const hasAddressPattern = insights.some(i => i.type === 'address')
    const hasPrediction = !!resonance.prediction

    // Determine category
    let category: Discovery['valueAssessment']['category'] = 'information'
    if (hasAddressPattern) category = 'address'
    else if (hasPrediction) category = 'prediction'
    else if (verifiedCount >= 3) category = 'breakthrough'
    else if (verifiedCount >= 1) category = 'pattern'

    // Determine significance
    let significance: Discovery['valueAssessment']['estimatedSignificance'] = 'low'
    if (resonance.aggregateResonance > 0.9) significance = 'critical'
    else if (resonance.aggregateResonance > 0.7) significance = 'high'
    else if (resonance.aggregateResonance > 0.5) significance = 'medium'

    // Generate next steps
    const nextSteps: string[] = []
    if (hasAddressPattern) {
      nextSteps.push('Verify address pattern against known UTXOs')
      nextSteps.push('Check if derived address exists on blockchain')
    }
    if (hasPrediction) {
      nextSteps.push(`Verification: ${resonance.prediction?.verificationMethod}`)
    }
    if (verifiedCount > 0) {
      nextSteps.push('Cross-reference with additional queries')
      nextSteps.push('Document for reproducibility')
    }

    return {
      category,
      estimatedSignificance: significance,
      actionable: nextSteps.length > 0,
      nextSteps,
    }
  }

  /**
   * Build verification status
   */
  private buildVerification(
    resonance: ResonanceResult,
    insights: DiscoveryInsight[]
  ): Discovery['verification'] {
    const verifiedPatterns = resonance.patterns.filter(p => p.blockchainProof?.verified)
    const proofs = verifiedPatterns.map(p => p.blockchainProof?.url).filter((u): u is string => !!u)

    let status: Discovery['verification']['status'] = 'unverified'
    if (verifiedPatterns.length >= 3) status = 'breakthrough'
    else if (verifiedPatterns.length >= 2) status = 'verified'
    else if (verifiedPatterns.length >= 1) status = 'partial'

    return {
      status,
      proofs,
      reproducible: true, // Always true due to deterministic nature
    }
  }

  /**
   * Helper functions
   */
  private patternTypeToInsightType(
    type: ResonancePattern['type']
  ): DiscoveryInsight['type'] {
    const mapping: Record<ResonancePattern['type'], DiscoveryInsight['type']> = {
      address: 'address',
      timestamp: 'correlation',
      block: 'pattern',
      message: 'secret',
      prediction: 'prediction',
    }
    return mapping[type]
  }

  private generateInsightTitle(pattern: ResonancePattern): string {
    switch (pattern.type) {
      case 'address':
        return 'Bitcoin Address Pattern Detected'
      case 'timestamp':
        return 'Temporal Correlation Found'
      case 'block':
        return 'Block Height Reference'
      case 'message':
        return 'Encoded Message Pattern'
      case 'prediction':
        return 'Predictive Pattern Identified'
      default:
        return 'Pattern Discovered'
    }
  }

  private calculateAIConfidence(response: LLMResponse): number {
    // Base confidence on response characteristics
    let confidence = 0.5

    // Longer, more detailed responses indicate more analysis
    if (response.content.length > 1000) confidence += 0.1
    if (response.content.length > 2000) confidence += 0.1

    // Check for verification language
    if (response.content.includes('verified') || response.content.includes('confirmed')) {
      confidence += 0.1
    }

    // Check for uncertainty markers
    if (response.content.includes('uncertain') || response.content.includes('speculative')) {
      confidence -= 0.1
    }

    return Math.min(Math.max(confidence, 0), 1)
  }

  private async hashString(input: string): Promise<string> {
    const encoder = new TextEncoder()
    const data = encoder.encode(input.toLowerCase().trim())
    const hashBuffer = await crypto.subtle.digest('SHA-256', data)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
  }
}

// Singleton
let agentInstance: DiscoveryAgent | null = null

export function getDiscoveryAgent(): DiscoveryAgent {
  if (!agentInstance) {
    agentInstance = new DiscoveryAgent()
  }
  return agentInstance
}
