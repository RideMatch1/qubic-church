/**
 * Lottery Entry Verifier
 * Verifies NFT ownership and balance for lottery entry
 */

import { qubicRPC } from './rpc-client'
import { qubicBay } from './qubicbay-api'

export interface VerificationResult {
  success: boolean
  nftId?: number
  balance?: bigint
  error?: string
}

/**
 * Lottery Entry Verifier
 * Verifies NFT ownership for lottery entry
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
   */
  async verifyEntry(
    qubicAddress: string,
    nftId: number
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

      // All checks passed!
      return {
        success: true,
        nftId,
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
   * Get Qubic balance for an address
   * Useful for displaying balance in UI
   */
  async getBalance(qubicAddress: string): Promise<bigint | null> {
    try {
      return await qubicRPC.getBalance(qubicAddress)
    } catch (error) {
      console.error('Failed to get balance:', error)
      return null
    }
  }
}

/**
 * Singleton instance export
 */
export const genesisVerifier = GenesisVerifier.getInstance()
