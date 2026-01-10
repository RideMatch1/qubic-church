'use client'

/**
 * ChallengesPreview Component
 * Preview of Intelligence Challenges system
 */

import { Brain, Search, Calculator, Eye, Award, Zap } from 'lucide-react'
import { INTELLIGENCE_CHALLENGES, NFT_ROLES } from '@/config/challenges'

const CATEGORY_ICONS = {
  research: Search,
  forensic: Eye,
  mathematical: Calculator,
  vision: Brain,
}

const CATEGORY_COLORS = {
  research: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  forensic: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
  mathematical: 'text-green-500 bg-green-500/10 border-green-500/20',
  vision: 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20',
}

const DIFFICULTY_COLORS = {
  easy: 'bg-green-500/20 text-green-500',
  medium: 'bg-yellow-500/20 text-yellow-500',
  hard: 'bg-red-500/20 text-red-500',
  expert: 'bg-purple-500/20 text-purple-500',
}

export function ChallengesPreview() {
  // Get first challenge from each category for preview
  const previewChallenges = [
    INTELLIGENCE_CHALLENGES.find((c) => c.category === 'research'),
    INTELLIGENCE_CHALLENGES.find((c) => c.category === 'forensic'),
    INTELLIGENCE_CHALLENGES.find((c) => c.category === 'mathematical'),
    INTELLIGENCE_CHALLENGES.find((c) => c.category === 'vision'),
  ].filter(Boolean)

  return (
    <section className="w-full py-16 bg-gradient-to-b from-background via-background to-muted">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-12 space-y-4">
          <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-full px-4 py-2 mb-4">
            <Brain className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-primary uppercase tracking-wide">
              Intelligence Challenges
            </span>
          </div>
          <h2 className="text-3xl md:text-5xl font-bold">
            Test Your Knowledge
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            20 challenges across 4 categories. NFT holders get role-based bonuses.
          </p>
        </div>

        {/* Role Bonuses */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12 max-w-5xl mx-auto">
          {NFT_ROLES.map((role) => {
            const category = role.challenges[0] as keyof typeof CATEGORY_ICONS
            const Icon = CATEGORY_ICONS[category]
            return (
              <div
                key={role.role}
                className={`p-4 rounded-lg border ${CATEGORY_COLORS[category]}`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Icon className="w-5 h-5" />
                  <h3 className="font-semibold">{role.role}</h3>
                </div>
                <p className="text-sm opacity-80 mb-2">{role.specialty}</p>
                <div className="text-xs font-medium">{role.bonus}</div>
                <div className="text-xs opacity-60 mt-1">
                  NFTs #{role.range[0]}-{role.range[1]}
                </div>
              </div>
            )
          })}
        </div>

        {/* Preview Challenges */}
        <div className="grid md:grid-cols-2 gap-6 max-w-6xl mx-auto mb-12">
          {previewChallenges.map((challenge) => {
            if (!challenge) return null
            const Icon = CATEGORY_ICONS[challenge.category]
            return (
              <div
                key={challenge.id}
                className="bg-card border border-border rounded-xl p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className={`p-2 rounded-lg ${CATEGORY_COLORS[challenge.category]}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{challenge.title}</h3>
                      <p className="text-xs text-muted-foreground capitalize">
                        {challenge.category}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-1 rounded-md ${DIFFICULTY_COLORS[challenge.difficulty]}`}>
                      {challenge.difficulty}
                    </span>
                    <span className="text-sm font-semibold text-primary">
                      {challenge.points} pts
                    </span>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  {challenge.question}
                </p>
                {challenge.hint && (
                  <div className="bg-muted/50 rounded-lg p-3 text-xs text-muted-foreground">
                    <span className="font-medium">Hint:</span> {challenge.hint}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Stats & CTA */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-primary/10 to-purple-500/10 border border-primary/20 rounded-xl p-8">
            <div className="grid md:grid-cols-3 gap-6 mb-6">
              <div className="text-center">
                <div className="text-4xl font-bold text-primary mb-2">
                  {INTELLIGENCE_CHALLENGES.length}
                </div>
                <div className="text-sm text-muted-foreground">Total Challenges</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-primary mb-2">
                  {INTELLIGENCE_CHALLENGES.reduce((sum, c) => sum + c.points, 0)}
                </div>
                <div className="text-sm text-muted-foreground">Total Points</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-primary mb-2">+20%</div>
                <div className="text-sm text-muted-foreground">Role Bonus</div>
              </div>
            </div>

            <div className="text-center space-y-4">
              <p className="text-muted-foreground">
                Each NFT gives you a unique role with bonuses for specific challenge categories.
                Compete on the leaderboard and prove your expertise.
              </p>
              <div className="inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/20 rounded-lg px-4 py-2">
                <Zap className="w-4 h-4 text-yellow-500" />
                <span className="text-sm text-yellow-500 font-medium">
                  Full challenge system launching soon
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
