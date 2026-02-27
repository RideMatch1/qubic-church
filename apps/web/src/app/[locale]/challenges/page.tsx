'use client'

/**
 * Intelligence Challenges Page
 * Interactive challenge system with role-based bonuses
 */

import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import {
  Brain,
  Search,
  Calculator,
  Eye,
  Trophy,
  Zap,
  ChevronRight,
  ArrowLeft,
  Lock,
  Unlock,
  CheckCircle2,
  XCircle,
  Info,
  Sparkles
} from 'lucide-react'
import { INTELLIGENCE_CHALLENGES, NFT_ROLES, type IntelligenceChallenge } from '@/config/challenges'

const CATEGORY_CONFIG = {
  research: {
    icon: Search,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/20',
    borderColor: 'border-blue-500/30',
    label: 'Research',
  },
  forensic: {
    icon: Eye,
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/20',
    borderColor: 'border-purple-500/30',
    label: 'Forensic',
  },
  mathematical: {
    icon: Calculator,
    color: 'text-green-400',
    bgColor: 'bg-green-500/20',
    borderColor: 'border-green-500/30',
    label: 'Mathematical',
  },
  vision: {
    icon: Brain,
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/20',
    borderColor: 'border-yellow-500/30',
    label: 'Vision',
  },
}

const DIFFICULTY_CONFIG = {
  easy: { color: 'text-green-400', bgColor: 'bg-green-500/20', label: 'Easy', multiplier: 1 },
  medium: { color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', label: 'Medium', multiplier: 1.5 },
  hard: { color: 'text-orange-400', bgColor: 'bg-orange-500/20', label: 'Hard', multiplier: 2 },
  expert: { color: 'text-red-400', bgColor: 'bg-red-500/20', label: 'Expert', multiplier: 3 },
}

type CategoryFilter = 'all' | 'research' | 'forensic' | 'mathematical' | 'vision'
type DifficultyFilter = 'all' | 'easy' | 'medium' | 'hard' | 'expert'

export default function ChallengesPage() {
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>('all')
  const [difficultyFilter, setDifficultyFilter] = useState<DifficultyFilter>('all')
  const [selectedChallenge, setSelectedChallenge] = useState<IntelligenceChallenge | null>(null)
  const [userAnswer, setUserAnswer] = useState('')
  const [showHint, setShowHint] = useState(false)
  const [answerResult, setAnswerResult] = useState<'correct' | 'incorrect' | null>(null)
  const [completedChallenges, setCompletedChallenges] = useState<Set<string>>(new Set())

  const filteredChallenges = useMemo(() => {
    return INTELLIGENCE_CHALLENGES.filter((challenge) => {
      const matchesCategory = categoryFilter === 'all' || challenge.category === categoryFilter
      const matchesDifficulty = difficultyFilter === 'all' || challenge.difficulty === difficultyFilter
      return matchesCategory && matchesDifficulty
    })
  }, [categoryFilter, difficultyFilter])

  const totalPoints = useMemo(() => {
    return INTELLIGENCE_CHALLENGES.reduce((sum, c) => sum + c.points, 0)
  }, [])

  const earnedPoints = useMemo(() => {
    return INTELLIGENCE_CHALLENGES
      .filter((c) => completedChallenges.has(c.id))
      .reduce((sum, c) => sum + c.points, 0)
  }, [completedChallenges])

  const handleSubmitAnswer = () => {
    if (!selectedChallenge || !userAnswer.trim()) return

    // In production, this would verify against the server
    // For now, we'll simulate with a simple hash check
    const isCorrect = userAnswer.toLowerCase().trim().length > 3 // Placeholder logic

    setAnswerResult(isCorrect ? 'correct' : 'incorrect')

    if (isCorrect) {
      setCompletedChallenges((prev) => new Set([...prev, selectedChallenge.id]))
      setTimeout(() => {
        setSelectedChallenge(null)
        setUserAnswer('')
        setAnswerResult(null)
        setShowHint(false)
      }, 2000)
    }
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <div className="relative border-b border-white/10">
        <div className="absolute inset-0 bg-gradient-to-b from-cyan-950/20 via-black to-black" />
        <div className="relative z-10 container mx-auto px-4 py-12">
          {/* Back link */}
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-white/50 hover:text-white transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center gap-3 mb-4">
              <Brain className="w-8 h-8 text-cyan-400" />
              <h1 className="text-4xl md:text-5xl font-bold text-white">
                Intelligence Challenges
              </h1>
            </div>
            <p className="text-lg text-white/60 max-w-2xl mb-6">
              Test your knowledge of Qubic, Aigarth, and the Bitcoin Bridge.
              NFT holders get role-based bonuses for specific challenge categories.
            </p>

            {/* Stats Bar */}
            <div className="flex flex-wrap gap-6">
              <div className="flex items-center gap-2">
                <Trophy className="w-5 h-5 text-yellow-400" />
                <span className="text-white">
                  <span className="font-bold">{earnedPoints}</span>
                  <span className="text-white/50">/{totalPoints} Points</span>
                </span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span className="text-white">
                  <span className="font-bold">{completedChallenges.size}</span>
                  <span className="text-white/50">/{INTELLIGENCE_CHALLENGES.length} Completed</span>
                </span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Sidebar - Role Bonuses */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-6">
              {/* Role Info */}
              <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-400" />
                  NFT Role Bonuses
                </h3>
                <div className="space-y-3">
                  {NFT_ROLES.map((role) => {
                    const category = role.challenges[0] as keyof typeof CATEGORY_CONFIG
                    const config = CATEGORY_CONFIG[category]
                    const Icon = config.icon
                    return (
                      <div
                        key={role.role}
                        className={`p-3 rounded-lg ${config.bgColor} border ${config.borderColor}`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <Icon className={`w-4 h-4 ${config.color}`} />
                          <span className={`text-sm font-medium ${config.color}`}>{role.role}</span>
                        </div>
                        <p className="text-xs text-white/50">{role.bonus}</p>
                        <p className="text-xs text-white/30 mt-1">NFTs #{role.range[0]}-{role.range[1]}</p>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Category Filter */}
              <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                <h3 className="text-white font-semibold mb-4">Category</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => setCategoryFilter('all')}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
                      categoryFilter === 'all'
                        ? 'bg-white/10 text-white'
                        : 'text-white/50 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    All Categories
                  </button>
                  {(Object.keys(CATEGORY_CONFIG) as Array<keyof typeof CATEGORY_CONFIG>).map((cat) => {
                    const config = CATEGORY_CONFIG[cat]
                    const Icon = config.icon
                    return (
                      <button
                        key={cat}
                        onClick={() => setCategoryFilter(cat)}
                        className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${
                          categoryFilter === cat
                            ? `${config.bgColor} ${config.color}`
                            : 'text-white/50 hover:text-white hover:bg-white/5'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        {config.label}
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Difficulty Filter */}
              <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                <h3 className="text-white font-semibold mb-4">Difficulty</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => setDifficultyFilter('all')}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
                      difficultyFilter === 'all'
                        ? 'bg-white/10 text-white'
                        : 'text-white/50 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    All Difficulties
                  </button>
                  {(Object.keys(DIFFICULTY_CONFIG) as Array<keyof typeof DIFFICULTY_CONFIG>).map((diff) => {
                    const config = DIFFICULTY_CONFIG[diff]
                    return (
                      <button
                        key={diff}
                        onClick={() => setDifficultyFilter(diff)}
                        className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
                          difficultyFilter === diff
                            ? `${config.bgColor} ${config.color}`
                            : 'text-white/50 hover:text-white hover:bg-white/5'
                        }`}
                      >
                        {config.label}
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Challenge Grid */}
          <div className="lg:col-span-3">
            <div className="mb-4 text-sm text-white/40">
              Showing {filteredChallenges.length} of {INTELLIGENCE_CHALLENGES.length} challenges
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <AnimatePresence mode="popLayout">
                {filteredChallenges.map((challenge, index) => {
                  const categoryConfig = CATEGORY_CONFIG[challenge.category]
                  const difficultyConfig = DIFFICULTY_CONFIG[challenge.difficulty]
                  const Icon = categoryConfig.icon
                  const isCompleted = completedChallenges.has(challenge.id)

                  return (
                    <motion.div
                      key={challenge.id}
                      layout
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.2, delay: index * 0.02 }}
                      className={`group p-5 rounded-xl border transition-all cursor-pointer ${
                        isCompleted
                          ? 'bg-green-500/10 border-green-500/30'
                          : `${categoryConfig.bgColor} ${categoryConfig.borderColor} hover:scale-[1.02]`
                      }`}
                      onClick={() => !isCompleted && setSelectedChallenge(challenge)}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className={`p-2 rounded-lg ${categoryConfig.bgColor} border ${categoryConfig.borderColor}`}>
                            {isCompleted ? (
                              <CheckCircle2 className="w-5 h-5 text-green-400" />
                            ) : (
                              <Icon className={`w-5 h-5 ${categoryConfig.color}`} />
                            )}
                          </div>
                          <div>
                            <h3 className={`font-semibold ${isCompleted ? 'text-green-400' : 'text-white'}`}>
                              {challenge.title}
                            </h3>
                            <p className={`text-xs ${categoryConfig.color} capitalize`}>
                              {challenge.category}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`text-xs px-2 py-1 rounded-md ${difficultyConfig.bgColor} ${difficultyConfig.color}`}>
                            {difficultyConfig.label}
                          </span>
                        </div>
                      </div>

                      <p className="text-sm text-white/60 mb-4 line-clamp-2">
                        {challenge.question}
                      </p>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1">
                          <Zap className="w-4 h-4 text-yellow-400" />
                          <span className="text-sm font-semibold text-yellow-400">{challenge.points} pts</span>
                        </div>
                        {!isCompleted && (
                          <div className="flex items-center gap-1 text-white/40 group-hover:text-white transition-colors">
                            <span className="text-sm">Solve</span>
                            <ChevronRight className="w-4 h-4" />
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )
                })}
              </AnimatePresence>
            </div>

            {filteredChallenges.length === 0 && (
              <div className="text-center py-20">
                <p className="text-white/40 text-lg">No challenges found matching your criteria</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Challenge Modal */}
      <AnimatePresence>
        {selectedChallenge && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
            onClick={() => {
              setSelectedChallenge(null)
              setUserAnswer('')
              setAnswerResult(null)
              setShowHint(false)
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="relative w-full max-w-xl bg-gradient-to-b from-white/10 to-white/5 border border-white/20 rounded-2xl p-6"
              onClick={(e) => e.stopPropagation()}
            >
              {(() => {
                const catConfig = CATEGORY_CONFIG[selectedChallenge.category]
                const diffConfig = DIFFICULTY_CONFIG[selectedChallenge.difficulty]
                const CatIcon = catConfig.icon

                return (
                  <>
                    {/* Header */}
                    <div className="flex items-start justify-between mb-6">
                      <div className="flex items-center gap-3">
                        <div className={`p-3 rounded-xl ${catConfig.bgColor} border ${catConfig.borderColor}`}>
                          <CatIcon className={`w-6 h-6 ${catConfig.color}`} />
                        </div>
                        <div>
                          <h2 className="text-xl font-bold text-white">{selectedChallenge.title}</h2>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={`text-xs px-2 py-0.5 rounded ${catConfig.bgColor} ${catConfig.color}`}>
                              {catConfig.label}
                            </span>
                            <span className={`text-xs px-2 py-0.5 rounded ${diffConfig.bgColor} ${diffConfig.color}`}>
                              {diffConfig.label}
                            </span>
                            <span className="text-xs text-yellow-400 font-semibold">
                              {selectedChallenge.points} pts
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Question */}
                    <div className="p-4 rounded-xl bg-white/5 border border-white/10 mb-6">
                      <p className="text-white leading-relaxed">{selectedChallenge.question}</p>
                    </div>

                    {/* Required Knowledge */}
                    {selectedChallenge.requiredKnowledge && selectedChallenge.requiredKnowledge.length > 0 && (
                      <div className="mb-6">
                        <p className="text-xs text-white/40 uppercase tracking-wider mb-2">Required Knowledge</p>
                        <div className="flex flex-wrap gap-2">
                          {selectedChallenge.requiredKnowledge.map((topic, i) => (
                            <span key={i} className="text-xs px-2 py-1 rounded-full bg-white/10 text-white/60">
                              {topic}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Hint */}
                    {selectedChallenge.hint && (
                      <div className="mb-6">
                        <button
                          onClick={() => setShowHint(!showHint)}
                          className="flex items-center gap-2 text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
                        >
                          {showHint ? <Unlock className="w-4 h-4" /> : <Lock className="w-4 h-4" />}
                          {showHint ? 'Hide Hint' : 'Show Hint'}
                        </button>
                        <AnimatePresence>
                          {showHint && (
                            <motion.div
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: 'auto' }}
                              exit={{ opacity: 0, height: 0 }}
                              className="mt-2 p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/20"
                            >
                              <div className="flex items-start gap-2">
                                <Info className="w-4 h-4 text-cyan-400 mt-0.5" />
                                <p className="text-sm text-cyan-300">{selectedChallenge.hint}</p>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    )}

                    {/* Answer Input */}
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm text-white/60 mb-2">Your Answer</label>
                        <input
                          type="text"
                          value={userAnswer}
                          onChange={(e) => {
                            setUserAnswer(e.target.value)
                            setAnswerResult(null)
                          }}
                          placeholder="Enter your answer..."
                          className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:outline-none focus:border-cyan-500/50 transition-colors"
                          disabled={answerResult === 'correct'}
                        />
                      </div>

                      {/* Result Message */}
                      {answerResult && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className={`flex items-center gap-2 p-3 rounded-lg ${
                            answerResult === 'correct'
                              ? 'bg-green-500/10 border border-green-500/20'
                              : 'bg-red-500/10 border border-red-500/20'
                          }`}
                        >
                          {answerResult === 'correct' ? (
                            <>
                              <CheckCircle2 className="w-5 h-5 text-green-400" />
                              <span className="text-green-400">Correct! +{selectedChallenge.points} points</span>
                            </>
                          ) : (
                            <>
                              <XCircle className="w-5 h-5 text-red-400" />
                              <span className="text-red-400">Incorrect. Try again!</span>
                            </>
                          )}
                        </motion.div>
                      )}

                      {/* Submit Button */}
                      <button
                        onClick={handleSubmitAnswer}
                        disabled={!userAnswer.trim() || answerResult === 'correct'}
                        className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-semibold hover:from-cyan-400 hover:to-purple-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                      >
                        Submit Answer
                      </button>
                    </div>
                  </>
                )
              })()}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
