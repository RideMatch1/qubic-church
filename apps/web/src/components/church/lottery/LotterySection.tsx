'use client'

/**
 * LotterySection Component
 * Holy Circle Lottery with Genesis verification
 */

import { useState } from 'react'
import { LOTTERY_CONFIG, PRIZE_STRUCTURE } from '@/config/lottery'
import { Trophy, Coins, AlertCircle, CheckCircle2, Sparkles } from 'lucide-react'

/**
 * Format bigint with commas
 */
function formatBigInt(num: bigint): string {
  return num.toLocaleString('en-US')
}

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
    <section className="w-full py-16 bg-gradient-to-b from-background via-purple-500/5 to-background">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-12 space-y-4">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-4 py-2 mb-4">
            <Sparkles className="w-4 h-4 text-purple-500" />
            <span className="text-sm font-medium text-purple-500 uppercase tracking-wide">
              The Holy Circle
            </span>
          </div>
          <h2 className="text-3xl md:text-5xl font-bold">
            675M QUBIC + 2M Genesis
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Community lottery for Anna NFT holders
          </p>
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/30 rounded-full px-6 py-2 mt-4">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-medium text-purple-400 uppercase tracking-wide">
              Coming Soon
            </span>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {/* Left Column - Prize Pool */}
          <div className="space-y-6">
            {/* Prize Pool */}
            <div className="bg-gradient-to-br from-primary/10 to-purple-500/10 border border-primary/20 rounded-xl p-8">
              <div className="flex items-center gap-2 mb-6">
                <Trophy className="w-6 h-6 text-primary" />
                <h3 className="text-xl font-semibold">Prize Structure</h3>
              </div>
              <div className="space-y-4">
                {PRIZE_STRUCTURE.map((prize) => (
                  <div
                    key={prize.place}
                    className="flex items-center justify-between p-4 bg-background/80 backdrop-blur-sm rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold ${
                        prize.place === 1 ? 'bg-yellow-500/20 text-yellow-500' :
                        prize.place === 2 ? 'bg-gray-400/20 text-gray-400' :
                        prize.place === 3 ? 'bg-orange-500/20 text-orange-500' :
                        'bg-muted text-muted-foreground'
                      }`}>
                        {prize.place}
                      </div>
                      <div>
                        <div className="font-medium">
                          {formatBigInt(prize.qubic)} QUBIC
                        </div>
                        <div className="text-sm text-muted-foreground">
                          + {formatBigInt(prize.genesis)} Genesis
                        </div>
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {prize.percentage}%
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-6 pt-6 border-t border-border">
                <div className="flex items-center justify-between text-lg font-semibold">
                  <span>Total Prize Pool</span>
                  <div className="text-right">
                    <div className="text-primary">
                      {formatBigInt(LOTTERY_CONFIG.prizePool.qubic)} QUBIC
                    </div>
                    <div className="text-sm text-muted-foreground">
                      + {formatBigInt(LOTTERY_CONFIG.prizePool.genesis)} Genesis
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Entry Form */}
          <div className="space-y-6">
            <div className="bg-card border border-border rounded-xl p-8">
              <div className="flex items-center gap-2 mb-6">
                <Coins className="w-6 h-6 text-primary" />
                <h3 className="text-xl font-semibold">Enter the Draw</h3>
              </div>

              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 mb-6">
                <p className="text-sm text-blue-400">
                  <strong>Requirements:</strong> Own an Anna NFT + matching Genesis tokens
                  (NFT #1 = 1 Genesis, #42 = 42 Genesis, etc.)
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Wallet Address */}
                <div>
                  <label
                    htmlFor="wallet"
                    className="block text-sm font-medium mb-2"
                  >
                    Qubic Wallet Address
                  </label>
                  <input
                    id="wallet"
                    type="text"
                    value={walletAddress}
                    onChange={(e) => setWalletAddress(e.target.value)}
                    placeholder="QUBIC..."
                    className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                    required
                    disabled={isVerifying}
                  />
                </div>

                {/* NFT ID */}
                <div>
                  <label htmlFor="nft-id" className="block text-sm font-medium mb-2">
                    Anna NFT ID
                  </label>
                  <input
                    id="nft-id"
                    type="number"
                    min="1"
                    max="200"
                    value={nftId}
                    onChange={(e) => setNftId(e.target.value)}
                    placeholder="1 - 200"
                    className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                    required
                    disabled={isVerifying}
                  />
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isVerifying || !walletAddress || !nftId}
                  className="w-full bg-primary text-primary-foreground py-4 rounded-lg font-semibold hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {isVerifying ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="animate-spin h-5 w-5 border-2 border-primary-foreground border-t-transparent rounded-full" />
                      Verifying...
                    </span>
                  ) : (
                    'Verify & Enter'
                  )}
                </button>

                {/* Verification Result */}
                {verificationResult && (
                  <div
                    className={`flex items-start gap-3 p-4 rounded-lg ${
                      verificationResult.success
                        ? 'bg-green-500/10 border border-green-500/20'
                        : 'bg-red-500/10 border border-red-500/20'
                    }`}
                  >
                    {verificationResult.success ? (
                      <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
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
            <div className="bg-muted/50 border border-border rounded-xl p-6 space-y-3">
              <h4 className="font-semibold">How it works:</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>Each Anna NFT holder gets 1 lottery ticket</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>Must hold Genesis tokens matching your NFT ID (e.g., NFT #42 requires 42 Genesis)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>Winners drawn transparently using blockchain randomness</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>5 winners share 675M QUBIC + 2M Genesis tokens</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
