'use client'

/**
 * NFTModal Component
 * Displays detailed NFT information when a star is clicked
 */

import { useEffect } from 'react'
import type { NFT } from '@/config/nfts'
import { X, ExternalLink, Award } from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'

interface NFTModalProps {
  nft: NFT | null
  isOpen: boolean
  onClose: () => void
}

/**
 * Get rarity badge styling
 */
function getRarityBadgeClass(rarity: string): string {
  switch (rarity) {
    case 'legendary':
      return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/50'
    case 'epic':
      return 'bg-purple-500/20 text-purple-500 border-purple-500/50'
    case 'rare':
      return 'bg-blue-500/20 text-blue-500 border-blue-500/50'
    case 'common':
      return 'bg-gray-500/20 text-gray-400 border-gray-500/50'
    default:
      return 'bg-gray-500/20 text-gray-400 border-gray-500/50'
  }
}

/**
 * Get role info based on NFT ID
 */
function getRoleInfo(id: number) {
  if (id <= 50) {
    return {
      role: 'Researcher',
      specialty: 'Deep Research Analysis',
      bonus: '+20% on Research Challenges',
    }
  }
  if (id <= 100) {
    return {
      role: 'Detective',
      specialty: 'Blockchain Forensics',
      bonus: '+20% on Forensic Challenges',
    }
  }
  if (id <= 150) {
    return {
      role: 'Mathematician',
      specialty: 'Cryptographic Patterns',
      bonus: '+20% on Mathematical Challenges',
    }
  }
  return {
    role: 'Visionary',
    specialty: 'Future Predictions',
    bonus: '+20% on Visionary Challenges',
  }
}

export function NFTModal({ nft, isOpen, onClose }: NFTModalProps) {
  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  if (!isOpen || !nft) return null

  const roleInfo = getRoleInfo(nft.id)

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 animate-in fade-in duration-200"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div
          className="bg-background border border-border rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto pointer-events-auto animate-in zoom-in-95 duration-200"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="sticky top-0 bg-background/95 backdrop-blur-sm border-b border-border p-4 flex items-center justify-between z-10">
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold">{nft.name}</h2>
              <span
                className={`px-2 py-1 rounded-md text-xs font-medium border uppercase ${getRarityBadgeClass(nft.rarity)}`}
              >
                {nft.rarity}
              </span>
            </div>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground transition-colors p-2 hover:bg-muted rounded-lg"
              aria-label="Close modal"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* NFT Image */}
            <div className="relative aspect-square w-full max-w-md mx-auto rounded-lg overflow-hidden border border-border bg-muted">
              <Image
                src={nft.image}
                alt={nft.name}
                fill
                className="object-cover"
                sizes="(max-width: 768px) 100vw, 448px"
                priority
              />
            </div>

            {/* Title */}
            <div>
              <h3 className="text-xl font-semibold text-foreground">
                {nft.title}
              </h3>
              <p className="text-muted-foreground mt-2">{nft.description}</p>
            </div>

            {/* Owner Status */}
            {nft.owner ? (
              <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
                <div className="flex items-center gap-2 text-green-500 font-medium">
                  <Award className="w-5 h-5" />
                  <span>Owned</span>
                </div>
                <p className="text-sm text-muted-foreground mt-1 font-mono">
                  {nft.owner}
                </p>
              </div>
            ) : (
              <div className="bg-muted/50 border border-border rounded-lg p-4">
                <p className="text-sm text-muted-foreground">
                  This NFT is available for purchase on QubicBay
                </p>
              </div>
            )}

            {/* Role & Specialty */}
            <div className="bg-primary/5 border border-primary/20 rounded-lg p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Role</span>
                <span className="font-semibold text-foreground">
                  {roleInfo.role}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  Specialty
                </span>
                <span className="text-sm text-foreground">
                  {roleInfo.specialty}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  Challenge Bonus
                </span>
                <span className="text-sm font-medium text-primary">
                  {roleInfo.bonus}
                </span>
              </div>
            </div>

            {/* Research Connection */}
            {nft.researchConnection && (
              <div className="bg-purple-500/5 border border-purple-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 text-purple-400 font-medium mb-2">
                  <Award className="w-4 h-4" />
                  <span className="text-sm uppercase tracking-wide">
                    Research Connection
                  </span>
                </div>
                <Link
                  href={nft.researchConnection.slug}
                  className="block group"
                >
                  <h4 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                    {nft.researchConnection.title}
                  </h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    {nft.researchConnection.teaser}
                  </p>
                  <span className="text-xs text-primary mt-2 inline-flex items-center gap-1 group-hover:underline">
                    Explore Research
                    <ExternalLink className="w-3 h-3" />
                  </span>
                </Link>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <a
                href={nft.qubicBayLink}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg px-4 py-3 font-medium text-center transition-colors inline-flex items-center justify-center gap-2"
              >
                View on QubicBay
                <ExternalLink className="w-4 h-4" />
              </a>
              <button
                onClick={onClose}
                className="px-6 py-3 bg-muted hover:bg-muted/80 rounded-lg font-medium transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
