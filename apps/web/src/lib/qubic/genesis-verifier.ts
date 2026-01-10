/**
 * Genesis Token Verifier
 * Verifies Genesis token balance for lottery entry
 */

import { qubicRPC } from './rpc-client'
import { qubicBay } from './qubicbay-api'

export interface VerificationResult {
  success: boolean
  nftId?: number
  genesisBalance?: bigint
  error?: string
}

/**
 * Genesis Verifier
 * Verifies both NFT ownership and Genesis token balance for lottery entry
 */
export class GenesisVerifier {
  private static instance: GenesisVerifier

  private constructor() {}

  static getInstance(): GenesisVerifier {
    if (!GenesisVerifier.instance) {
      GenesisVerifier.instance = new GenesisVerifier()
    }
    return GenesisVerifier.instance
  }

  /**
   * Verify lottery entry requirements
   * 1. User owns the specified NFT
   * 2. User has Genesis tokens equal to NFT ID
   */
  async verifyEntry(
    qubicAddress: string,
    nftId: number,
    expectedGenesisAmount: number
  ): Promise<VerificationResult> {
    try {
      // Step 1: Verify NFT ownership
      const ownsNFT = await qubicBay.verifyOwnership(qubicAddress, nftId)
      if (!ownsNFT) {
        return {
          success: false,
          error: 'NFT ownership not found. Please ensure you own this NFT.',
        }
      }

      // Step 2: Get Genesis balance
      let genesisBalance: bigint
      try {
        genesisBalance = await qubicRPC.getBalance(qubicAddress)
      } catch (error) {
        return {
          success: false,
          error:
            'Failed to verify Genesis balance. RPC connection issue. Please try again.',
        }
      }

      // Step 3: Verify Genesis amount matches NFT ID
      const genesisAmountNum = Number(genesisBalance)
      if (genesisAmountNum !== expectedGenesisAmount) {
        return {
          success: false,
          nftId,
          genesisBalance,
          error: `Genesis balance mismatch. Expected ${expectedGenesisAmount}, found ${genesisAmountNum}. Your lottery number should equal your NFT ID.`,
        }
      }

      // All checks passed!
      return {
        success: true,
        nftId,
        genesisBalance,
      }
    } catch (error) {
      return {
        success: false,
        error:
          error instanceof Error
            ? error.message
            : 'Verification failed due to an unknown error',
      }
    }
  }

  /**
   * Quick check if an address owns any Anna NFTs
   */
  async hasAnyNFT(qubicAddress: string): Promise<boolean> {
    try {
      const ownerData = await qubicBay.getOwnerNFTs(qubicAddress)
      return ownerData.count > 0
    } catch (error) {
      return false
    }
  }

  /**
   * Get all NFTs owned by an address (for multi-NFT holders)
   */
  async getOwnedNFTs(qubicAddress: string): Promise<number[]> {
    try {
      const ownerData = await qubicBay.getOwnerNFTs(qubicAddress)
      return ownerData.nfts.map((nft) => nft.nftId)
    } catch (error) {
      return []
    }
  }

  /**
   * Verify Genesis balance only (without NFT check)
   * Useful for displaying balance in UI
   */
  async getGenesisBalance(qubicAddress: string): Promise<bigint | null> {
    try {
      return await qubicRPC.getBalance(qubicAddress)
    } catch (error) {
      console.error('Failed to get Genesis balance:', error)
      return null
    }
  }
}

/**
 * Singleton instance export
 */
export const genesisVerifier = GenesisVerifier.getInstance()
