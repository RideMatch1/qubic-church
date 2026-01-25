'use client'

/**
 * SimpleGiveawaySection - 600M QUBIC Giveaway
 * Simple rules: Hold 1 Anna NFT = 1 entry
 */

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Gift, Trophy, Medal, Award, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react'

const prizes = [
  { place: 1, amount: '300,000,000', icon: Trophy, color: 'yellow' },
  { place: 2, amount: '200,000,000', icon: Medal, color: 'gray' },
  { place: 3, amount: '100,000,000', icon: Award, color: 'orange' },
]

export function SimpleGiveawaySection() {
  const [walletAddress, setWalletAddress] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setResult(null)

    // Simulate submission
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // Mock result (in production, this would verify NFT ownership)
    const success = walletAddress.length > 20
    setResult({
      success,
      message: success
        ? 'Entry registered! Good luck!'
        : 'Please enter a valid Qubic wallet address.',
    })
    setIsSubmitting(false)

    if (success) {
      setWalletAddress('')
    }
  }

  return (
    <section className="relative w-full py-24 md:py-32 bg-black overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-yellow-950/5 to-black" />

      {/* Decorative glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-yellow-500/10 rounded-full blur-[150px] pointer-events-none" />

      <div className="relative z-10 container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-yellow-500/10 border border-yellow-500/20 mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Gift className="w-4 h-4 text-yellow-400" />
            <span className="text-sm text-yellow-300 uppercase tracking-wider">
              Community Giveaway
            </span>
          </motion.div>

          {/* Big number */}
          <motion.div
            className="mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <span className="text-5xl md:text-7xl lg:text-8xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-yellow-300 to-orange-400">
              600M
            </span>
            <span className="block text-2xl md:text-3xl text-white/80 font-semibold mt-2">
              QUBIC Prize Pool
            </span>
          </motion.div>

          <p className="text-lg text-white/60 max-w-xl mx-auto">
            <span className="text-white font-semibold">3 Winners</span> -{' '}
            <span className="text-yellow-400">1 Simple Rule</span>
          </p>
        </motion.div>

        {/* Prize Podium */}
        <motion.div
          className="flex justify-center items-end gap-4 mb-12"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          {/* 2nd place */}
          <div className="flex flex-col items-center">
            <Medal className="w-8 h-8 text-gray-400 mb-2" />
            <div className="w-24 md:w-32 h-24 md:h-28 rounded-t-xl bg-gradient-to-b from-gray-500/20 to-gray-500/5 border border-gray-500/20 flex flex-col items-center justify-center">
              <span className="text-2xl font-bold text-gray-300">2nd</span>
              <span className="text-xs text-gray-400">200M</span>
            </div>
          </div>

          {/* 1st place */}
          <div className="flex flex-col items-center">
            <Trophy className="w-10 h-10 text-yellow-400 mb-2 animate-pulse" />
            <div className="w-28 md:w-36 h-32 md:h-40 rounded-t-xl bg-gradient-to-b from-yellow-500/30 to-yellow-500/5 border border-yellow-500/30 flex flex-col items-center justify-center shadow-lg shadow-yellow-500/20">
              <Sparkles className="w-6 h-6 text-yellow-400 mb-1" />
              <span className="text-3xl font-bold text-yellow-300">1st</span>
              <span className="text-sm text-yellow-400 font-semibold">300M QUBIC</span>
            </div>
          </div>

          {/* 3rd place */}
          <div className="flex flex-col items-center">
            <Award className="w-8 h-8 text-orange-400 mb-2" />
            <div className="w-24 md:w-32 h-20 md:h-24 rounded-t-xl bg-gradient-to-b from-orange-500/20 to-orange-500/5 border border-orange-500/20 flex flex-col items-center justify-center">
              <span className="text-2xl font-bold text-orange-300">3rd</span>
              <span className="text-xs text-orange-400">100M</span>
            </div>
          </div>
        </motion.div>

        {/* Entry Section */}
        <motion.div
          className="max-w-lg mx-auto"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          {/* Rule card */}
          <div className="p-6 rounded-xl bg-gradient-to-b from-white/5 to-transparent border border-white/10 mb-6">
            <h3 className="text-lg font-semibold text-white mb-4 text-center">
              How to Enter
            </h3>

            <div className="flex items-center justify-center gap-4 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
              <CheckCircle2 className="w-6 h-6 text-yellow-400" />
              <span className="text-white">
                Hold at least <span className="text-yellow-400 font-bold">1 Anna NFT</span>
              </span>
            </div>

            <p className="text-center text-sm text-white/40 mt-4">
              That's it! No complicated rules. No token matching.
            </p>
          </div>

          {/* Entry form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="wallet" className="block text-sm text-white/60 mb-2">
                Your Qubic Wallet Address
              </label>
              <input
                id="wallet"
                type="text"
                value={walletAddress}
                onChange={(e) => setWalletAddress(e.target.value)}
                placeholder="Enter your Qubic address..."
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:outline-none focus:border-yellow-500/50 transition-colors"
                required
                disabled={isSubmitting}
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting || !walletAddress}
              className="w-full py-4 rounded-xl bg-gradient-to-r from-yellow-500 to-orange-500 text-black font-bold text-lg hover:from-yellow-400 hover:to-orange-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                  Verifying NFT Ownership...
                </span>
              ) : (
                'Enter Giveaway'
              )}
            </button>

            {/* Result message */}
            {result && (
              <div
                className={`flex items-center gap-3 p-4 rounded-xl ${
                  result.success
                    ? 'bg-green-500/10 border border-green-500/20'
                    : 'bg-red-500/10 border border-red-500/20'
                }`}
              >
                {result.success ? (
                  <CheckCircle2 className="w-5 h-5 text-green-400" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-400" />
                )}
                <span className={result.success ? 'text-green-400' : 'text-red-400'}>
                  {result.message}
                </span>
              </div>
            )}
          </form>

          {/* Stats */}
          <div className="mt-8 flex items-center justify-center gap-8 text-center">
            <div>
              <span className="text-2xl font-bold text-white">47</span>
              <span className="block text-xs text-white/40">Entries</span>
            </div>
            <div className="w-px h-8 bg-white/10" />
            <div>
              <span className="text-2xl font-bold text-white">153</span>
              <span className="block text-xs text-white/40">Days Left</span>
            </div>
          </div>

          {/* Draw info */}
          <p className="text-center text-xs text-white/30 mt-6">
            Draw when all 200 NFTs sold OR March 3, 2027
            <br />
            Transparent blockchain randomness
          </p>
        </motion.div>
      </div>
    </section>
  )
}
