'use client'

import { useState, useRef, useEffect } from 'react'
import { Link, usePathname } from '@/navigation'
import { Icons } from '@/components/icons'
import { siteConfig } from '@/config/site'
import { cn } from '@/lib/utils'
import { ChevronDown, BookOpen, Grid3X3, Clock, Activity } from 'lucide-react'

interface MainNavProps {
  messages: {
    docs: string
    blog: string
  }
}

const researchItems = [
  { href: '/docs', label: 'Research Archive', icon: BookOpen, description: '75+ open-source documents' },
  { href: '/evidence', label: 'Anna Matrix', icon: Grid3X3, description: 'Interactive 128x128 visualization' },
  { href: '/timeline', label: 'Evidence Timeline', icon: Clock, description: '12-phase discovery journey' },
  { href: '/monitoring', label: 'Live Monitoring', icon: Activity, description: 'Real-time Qubic metrics' },
]

export function MainNav({ messages }: MainNavProps) {
  const pathname = usePathname()
  const [researchOpen, setResearchOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setResearchOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Close dropdown on route change
  useEffect(() => {
    setResearchOpen(false)
  }, [pathname])

  const isResearchActive = pathname.includes('/docs') || pathname.includes('/evidence') || pathname.includes('/timeline') || pathname.includes('/monitoring')

  return (
    <div className="mr-4 hidden md:flex">
      <Link className="mr-6 flex items-center space-x-2" href="/">
        <Icons.logo className="size-4" />
        <span className="hidden font-bold sm:inline-block">
          {siteConfig.name}
        </span>
      </Link>

      <nav className="flex items-center gap-4 text-sm lg:gap-6">
        {/* Research Dropdown */}
        <div ref={dropdownRef} className="relative">
          <button
            onClick={() => setResearchOpen(!researchOpen)}
            className={cn(
              'flex items-center gap-1 hover:text-foreground/80 transition-colors',
              isResearchActive ? 'dark:text-primary-active' : 'text-foreground/60'
            )}
          >
            Research
            <ChevronDown className={cn('w-3.5 h-3.5 transition-transform', researchOpen && 'rotate-180')} />
          </button>

          {researchOpen && (
            <div className="absolute top-full left-0 mt-2 w-72 rounded-xl bg-background/95 backdrop-blur-lg border border-border/50 shadow-xl shadow-black/20 p-2 z-50">
              {researchItems.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      'flex items-start gap-3 px-3 py-2.5 rounded-lg hover:bg-accent/50 transition-colors group',
                      pathname.includes(item.href) && 'bg-accent/30'
                    )}
                  >
                    <Icon className="w-4 h-4 mt-0.5 text-muted-foreground group-hover:text-foreground transition-colors shrink-0" />
                    <div>
                      <div className="font-medium text-sm text-foreground">{item.label}</div>
                      <div className="text-xs text-muted-foreground">{item.description}</div>
                    </div>
                  </Link>
                )
              })}
            </div>
          )}
        </div>

        {/* NFT Collection */}
        <Link
          className={cn(
            'hover:text-foreground/80 transition-colors',
            pathname.includes('/nft') ? 'dark:text-primary-active' : 'text-foreground/60'
          )}
          href="/nfts"
        >
          NFT Collection
        </Link>

        {/* Giveaway */}
        <Link
          className={cn(
            'hover:text-foreground/80 transition-colors',
            pathname === '/#giveaway' ? 'dark:text-primary-active' : 'text-foreground/60'
          )}
          href="/#giveaway"
        >
          <span className="flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-yellow-500" />
            </span>
            Giveaway
          </span>
        </Link>

        {/* Get Qubic */}
        <Link
          className={cn(
            'hover:text-foreground/80 transition-colors',
            pathname.includes('/get-qubic') ? 'dark:text-primary-active' : 'text-foreground/60'
          )}
          href="/get-qubic"
        >
          Get Qubic
        </Link>

        {/* Mine Qubic */}
        <Link
          className={cn(
            'hover:text-foreground/80 transition-colors',
            pathname.includes('/mine-qubic') ? 'dark:text-primary-active' : 'text-foreground/60'
          )}
          href="/mine-qubic"
        >
          Mine Qubic
        </Link>
      </nav>
    </div>
  )
}
