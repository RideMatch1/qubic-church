'use client'

import { ExternalLink, Copy, Check } from 'lucide-react'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { BitcoinLogoSVG } from '@/components/logos'

type Chain = 'bitcoin' | 'qubic'
type LinkType = 'address' | 'transaction' | 'block'

interface ExplorerLinkProps {
  chain: Chain
  type: LinkType
  value: string
  label?: string
  showCopy?: boolean
  showIcon?: boolean
  truncate?: boolean
  className?: string
}

// Explorer URLs
const explorers = {
  bitcoin: {
    address: (value: string) => `https://mempool.space/address/${value}`,
    transaction: (value: string) => `https://mempool.space/tx/${value}`,
    block: (value: string) => `https://mempool.space/block/${value}`,
  },
  qubic: {
    address: (value: string) => `https://explorer.qubic.org/network/address/${value}`,
    transaction: (value: string) => `https://explorer.qubic.org/network/tx/${value}`,
    block: (value: string) => `https://explorer.qubic.org/network/block/${value}`,
  },
}

const chainIcons = {
  bitcoin: BitcoinLogoSVG,
  qubic: null, // Will use img
}

const chainColors = {
  bitcoin: 'text-[#D4AF37] hover:text-[#D4AF37]/80',
  qubic: 'text-[#D4AF37]/80 hover:text-[#D4AF37]',
}

export function ExplorerLink({
  chain,
  type,
  value,
  label,
  showCopy = true,
  showIcon = true,
  truncate = true,
  className = '',
}: ExplorerLinkProps) {
  const [copied, setCopied] = useState(false)

  const url = explorers[chain][type](value)
  const displayValue = label || (truncate ? truncateValue(value) : value)
  const Icon = chainIcons[chain]

  const handleCopy = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    try {
      await navigator.clipboard.writeText(value)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea')
      textarea.value = value
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <span className={`inline-flex items-center gap-1.5 ${className}`}>
      {showIcon && (
        <span className="flex-shrink-0">
          {chain === 'bitcoin' && Icon && <Icon size={14} />}
          {chain === 'qubic' && (
            <img src="/logos/qubic.png" alt="Qubic" className="w-3.5 h-3.5" />
          )}
        </span>
      )}

      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className={`font-mono text-sm ${chainColors[chain]} hover:underline transition-colors`}
        title={`View on ${chain === 'bitcoin' ? 'Mempool.space' : 'Qubic Explorer'}`}
      >
        {displayValue}
      </a>

      <ExternalLink className="h-3 w-3 text-muted-foreground flex-shrink-0" />

      {showCopy && (
        <motion.button
          onClick={handleCopy}
          className="p-1 hover:bg-white/[0.06] transition-colors flex-shrink-0"
          whileTap={{ scale: 0.9 }}
          title={copied ? 'Copied!' : 'Copy to clipboard'}
        >
          {copied ? (
            <Check className="h-3 w-3 text-verified" />
          ) : (
            <Copy className="h-3 w-3 text-muted-foreground hover:text-foreground" />
          )}
        </motion.button>
      )}
    </span>
  )
}

// Full address display with copy
export function AddressDisplay({
  chain,
  address,
  label,
  showExplorer = true,
  className = '',
}: {
  chain: Chain
  address: string
  label?: string
  showExplorer?: boolean
  className?: string
}) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(address)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Ignore
    }
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <div className="flex items-center gap-2">
          {chain === 'bitcoin' && <BitcoinLogoSVG size={16} />}
          {chain === 'qubic' && (
            <img src="/logos/qubic.png" alt="Qubic" className="w-4 h-4" />
          )}
          <span className="text-sm font-medium">{label}</span>
        </div>
      )}

      <div className="flex items-center gap-2 p-3 bg-white/[0.02] border border-white/[0.04]">
        <code className="flex-1 font-mono text-xs break-all select-all">
          {address}
        </code>

        <div className="flex items-center gap-1 flex-shrink-0">
          <motion.button
            onClick={handleCopy}
            className="p-2 hover:bg-white/[0.06] transition-colors"
            whileTap={{ scale: 0.9 }}
            title={copied ? 'Copied!' : 'Copy address'}
          >
            {copied ? (
              <Check className="h-4 w-4 text-verified" />
            ) : (
              <Copy className="h-4 w-4 text-muted-foreground" />
            )}
          </motion.button>

          {showExplorer && (
            <a
              href={explorers[chain].address(address)}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 hover:bg-white/[0.06] transition-colors"
              title="View on explorer"
            >
              <ExternalLink className="h-4 w-4 text-muted-foreground" />
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

// Block link with height display
export function BlockLink({
  chain,
  height,
  hash,
  showHeight = true,
  className = '',
}: {
  chain: Chain
  height?: number
  hash?: string
  showHeight?: boolean
  className?: string
}) {
  const value = hash || (height !== undefined ? height.toString() : '')
  const displayValue = showHeight && height !== undefined ? `#${height.toLocaleString()}` : truncateValue(value)

  return (
    <ExplorerLink
      chain={chain}
      type="block"
      value={value}
      label={displayValue}
      truncate={false}
      className={className}
    />
  )
}

// Helper function
function truncateValue(value: string, startChars = 8, endChars = 6): string {
  if (value.length <= startChars + endChars + 3) return value
  return `${value.slice(0, startChars)}...${value.slice(-endChars)}`
}
