'use client'

/**
 * LotterySection Component
 * Holy Circle Lottery with Genesis verification
 * Updated for dark theme
 */

import { useState } from 'react'
import { motion } from 'framer-motion'
import { LOTTERY_CONFIG, PRIZE_STRUCTURE } from '@/config/lottery'
import { Trophy, Coins, AlertCircle, CheckCircle2, Sparkles, Crown, Medal, Award } from 'lucide-react'

/**
 * Format bigint with commas
 */
function formatBigInt(num: bigint): string {
  return num.toLocaleString('en-US')
}

const placeIcons = [Crown, Medal, Award, Trophy, Trophy]
const placeColors = ['text-yellow-400', 'text-gray-400', 'text-orange-400', 'text-purple-400', 'text-cyan-400']

export function LotterySection() {
  const [walletAddress, setWalletAddress] = useState('')
  const [nftId, setNftId] = useState('')
  const [isVerifying, setIsVerifying] = useState(false)
  const [verificationResult, setVerificationResult] = useState<{
    success: boolean
    message: string
  } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsVerifying(true)
    setVerificationResult(null)

    // Simulate verification (in production, this would call genesis-verifier API)
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Mock result
    const success = Math.random() > 0.5
    setVerificationResult({
      success,
      message: success
        ? `Entry confirmed! NFT #${nftId} with Genesis tokens verified.`
        : `Verification failed. Please ensure you own NFT #${nftId} and have the correct Genesis token amount.`,
    })
    setIsVerifying(false)

    if (success) {
      setWalletAddress('')
      setNftId('')
    }
  }

  return (
    <section className="relative w-full py-24 md:py-32 bg-black overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-purple-950/10 to-black" />

      {/* Decorative glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-purple-500/10 rounded-full blur-[200px] pointer-events-none" />

      <div className="relative z-10 container mx-auto px-4 max-w-6xl">
        {/* Section Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-4 py-2 mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-medium text-purple-300 uppercase tracking-wider">
              The Holy Circle
            </span>
          </motion.div>

          <motion.div
            className="mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <span className="text-4xl md:text-6xl lg:text-7xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400">
              76M QUBIC
            </span>
            <span className="block text-xl md:text-2xl text-white/60 font-semibold mt-2">
              + 7M Genesis Tokens
            </span>
          </motion.div>

          <p className="text-lg text-white/50 max-w-xl mx-auto mb-6">
            The ultimate community lottery for Anna NFT holders
          </p>

          <div className="inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/30 rounded-full px-6 py-2">
            <Sparkles className="w-4 h-4 text-yellow-400 animate-pulse" />
            <span className="text-sm font-medium text-yellow-400 uppercase tracking-wider">
              Coming Soon
            </span>
          </div>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Prize Pool */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/20">
              <div className="flex items-center gap-2 mb-6">
                <Trophy className="w-6 h-6 text-purple-400" />
                <h3 className="text-xl font-semibold text-white">Prize Structure</h3>
              </div>
              <div className="space-y-3">
                {PRIZE_STRUCTURE.map((prize, index) => {
                  const Icon = placeIcons[index] || Trophy
                  const color = placeColors[index] || 'text-white'
                  return (
                    <div
                      key={prize.place}
                      className="flex items-center justify-between p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10"
                    >
                      <div className="flex items-center gap-3">
                        <div className={`flex items-center justify-center w-10 h-10 rounded-full bg-white/5 ${color}`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="font-semibold text-white">
                            {formatBigInt(prize.qubic)} QUBIC
                          </div>
                          <div className="text-sm text-white/50">
                            + {formatBigInt(prize.genesis)} Genesis
                          </div>
                        </div>
                      </div>
                      <div className="text-sm text-white/40">
                        {prize.percentage}%
                      </div>
                    </div>
                  )
                })}
              </div>
              <div className="mt-6 pt-6 border-t border-white/10">
                <div className="flex items-center justify-between text-lg font-semibold">
                  <span className="text-white/70">Total Prize Pool</span>
                  <div className="text-right">
                    <div className="text-purple-400">
                      {formatBigInt(LOTTERY_CONFIG.prizePool.qubic)} QUBIC
                    </div>
                    <div className="text-sm text-white/50">
                      + {formatBigInt(LOTTERY_CONFIG.prizePool.genesis)} Genesis
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Right Column - Entry Form */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="space-y-6"
          >
            <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-b from-white/5 to-transparent border border-white/10">
              <div className="flex items-center gap-2 mb-6">
                <Coins className="w-6 h-6 text-cyan-400" />
                <h3 className="text-xl font-semibold text-white">Enter the Draw</h3>
              </div>

              <div className="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/20 mb-6">
                <p className="text-sm text-cyan-300">
                  <strong className="text-cyan-400">Requirements:</strong> Own an Anna NFT + matching Genesis tokens
                  (NFT #1 = 1 Genesis, #42 = 42 Genesis, etc.)
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Wallet Address */}
                <div>
                  <label
                    htmlFor="lottery-wallet"
                    className="block text-sm font-medium text-white/60 mb-2"
                  >
                    Qubic Wallet Address
                  </label>
                  <input
                    id="lottery-wallet"
                    type="text"
                    value={walletAddress}
                    onChange={(e) => setWalletAddress(e.target.value)}
                    placeholder="Enter your Qubic address..."
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:outline-none focus:border-purple-500/50 transition-all"
                    required
                    disabled={isVerifying}
                  />
                </div>

                {/* NFT ID */}
                <div>
                  <label htmlFor="lottery-nft-id" className="block text-sm font-medium text-white/60 mb-2">
                    Anna NFT ID
                  </label>
                  <input
                    id="lottery-nft-id"
                    type="number"
                    min="1"
                    max="200"
                    value={nftId}
                    onChange={(e) => setNftId(e.target.value)}
                    placeholder="1 - 200"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:outline-none focus:border-purple-500/50 transition-all"
                    required
                    disabled={isVerifying}
                  />
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isVerifying || !walletAddress || !nftId}
                  className="w-full py-4 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold text-lg hover:from-purple-400 hover:to-pink-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {isVerifying ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="animate-spin h-5 w-5 border-2 border-white/30 border-t-white rounded-full" />
                      Verifying...
                    </span>
                  ) : (
                    'Verify & Enter'
                  )}
                </button>

                {/* Verification Result */}
                {verificationResult && (
                  <div
                    className={`flex items-start gap-3 p-4 rounded-xl ${
                      verificationResult.success
                        ? 'bg-green-500/10 border border-green-500/20'
                        : 'bg-red-500/10 border border-red-500/20'
                    }`}
                  >
                    {verificationResult.success ? (
                      <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    )}
                    <p
                      className={`text-sm ${
                        verificationResult.success ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {verificationResult.message}
                    </p>
                  </div>
                )}
              </form>
            </div>

            {/* Additional Info */}
            <div className="p-5 rounded-xl bg-white/5 border border-white/10">
              <h4 className="font-semibold text-white mb-4">How it works:</h4>
              <ul className="space-y-3 text-sm text-white/50">
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-1">•</span>
                  <span>Each Anna NFT holder gets 1 lottery ticket</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-1">•</span>
                  <span>Must hold Genesis tokens matching your NFT ID (e.g., NFT #42 requires 42 Genesis)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-1">•</span>
                  <span>Winners drawn transparently using blockchain randomness</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-1">•</span>
                  <span>5 winners share 675M QUBIC + 2M Genesis tokens</span>
                </li>
              </ul>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
