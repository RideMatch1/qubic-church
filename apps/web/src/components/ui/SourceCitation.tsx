'use client'

import { ExternalLink, FileText, Link2, Database, Clock } from 'lucide-react'
import { motion } from 'framer-motion'

export type SourceType = 'blockchain' | 'paper' | 'website' | 'archive' | 'database'

interface SourceCitationProps {
  title: string
  url?: string
  type?: SourceType
  author?: string
  date?: string
  description?: string
  verified?: boolean
  className?: string
}

const sourceIcons = {
  blockchain: Database,
  paper: FileText,
  website: Link2,
  archive: Clock,
  database: Database,
}

const sourceLabels = {
  blockchain: 'Blockchain',
  paper: 'Paper',
  website: 'Website',
  archive: 'Archive',
  database: 'Database',
}

export function SourceCitation({
  title,
  url,
  type = 'website',
  author,
  date,
  description,
  verified = false,
  className = '',
}: SourceCitationProps) {
  const Icon = sourceIcons[type]

  const content = (
    <motion.div
      className={`
        group flex items-start gap-3 p-3 rounded-lg
        bg-muted/30 border border-border/50
        ${url ? 'hover:bg-muted/50 hover:border-border cursor-pointer' : ''}
        transition-all ${className}
      `}
      whileHover={url ? { scale: 1.01 } : undefined}
      whileTap={url ? { scale: 0.99 } : undefined}
    >
      {/* Icon */}
      <div className="flex-shrink-0 p-2 rounded-md bg-muted">
        <Icon className="h-4 w-4 text-muted-foreground" />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm truncate">{title}</span>
          {verified && (
            <span className="flex-shrink-0 px-1.5 py-0.5 text-[10px] font-medium rounded bg-verified-bg text-verified">
              Verified
            </span>
          )}
        </div>

        {(author || date) && (
          <div className="flex items-center gap-2 mt-0.5 text-xs text-muted-foreground">
            {author && <span>{author}</span>}
            {author && date && <span>·</span>}
            {date && <span>{date}</span>}
          </div>
        )}

        {description && (
          <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
            {description}
          </p>
        )}

        <div className="flex items-center gap-2 mt-1">
          <span className="text-[10px] uppercase tracking-wider text-muted-foreground/70">
            {sourceLabels[type]}
          </span>
          {url && (
            <ExternalLink className="h-3 w-3 text-muted-foreground/50 group-hover:text-muted-foreground transition-colors" />
          )}
        </div>
      </div>
    </motion.div>
  )

  if (url) {
    return (
      <a href={url} target="_blank" rel="noopener noreferrer" className="block">
        {content}
      </a>
    )
  }

  return content
}

// Compact inline citation
export function InlineCitation({
  number,
  url,
  tooltip,
}: {
  number: number
  url?: string
  tooltip?: string
}) {
  const content = (
    <span
      className="inline-flex items-center justify-center w-4 h-4 text-[10px] font-mono
                 rounded bg-muted text-muted-foreground hover:bg-primary hover:text-primary-foreground
                 cursor-pointer transition-colors align-super"
      title={tooltip}
    >
      {number}
    </span>
  )

  if (url) {
    return (
      <a href={url} target="_blank" rel="noopener noreferrer">
        {content}
      </a>
    )
  }

  return content
}

// Source list component
export function SourceList({
  sources,
  title = 'Sources',
  className = '',
}: {
  sources: SourceCitationProps[]
  title?: string
  className?: string
}) {
  return (
    <div className={`space-y-3 ${className}`}>
      {title && (
        <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <FileText className="h-4 w-4" />
          {title}
        </h4>
      )}
      <div className="space-y-2">
        {sources.map((source, idx) => (
          <SourceCitation key={idx} {...source} />
        ))}
      </div>
    </div>
  )
}
