'use client'

import { Link, usePathname } from '@/navigation'
import { Icons } from '@/components/icons'
import { siteConfig } from '@/config/site'
import { cn } from '@/lib/utils'

interface MainNavProps {
  messages: {
    docs: string
    blog: string
    evidence?: string
    monitoring?: string
    aigarth?: string
    nft?: string
    timeline?: string
    agents?: string
  }
}

export function MainNav({ messages }: MainNavProps) {
  const pathname = usePathname()

  return (
    <div className="mr-4 hidden md:flex">
      <Link className="mr-6 flex items-center space-x-2" href="/">
        <Icons.logo className="size-4" />

        <span className="hidden font-bold sm:inline-block">
          {siteConfig.name}
        </span>
      </Link>

      <nav className="flex items-center gap-4 text-sm lg:gap-6">
        <Link
          className={cn(
            'hover:text-foreground/80 transition-colors',
            pathname.includes('/docs')
              ? 'dark:text-primary-active'
              : 'text-foreground/60'
          )}
          href="/docs"
        >
          {messages.docs}
        </Link>

        <Link
          className={cn(
            'hover:text-foreground/80 transition-colors',
            pathname.includes('/timeline')
              ? 'dark:text-primary-active'
              : 'text-foreground/60'
          )}
          href="/timeline"
        >
          {messages.timeline || 'Journey'}
        </Link>

        <Link
          className={cn(
            'hover:text-foreground/80 transition-colors',
            pathname.includes('/evidence')
              ? 'dark:text-primary-active'
              : 'text-foreground/60'
          )}
          href="/evidence"
        >
          {messages.evidence || 'Evidence'}
        </Link>

        <Link
          className={cn(
            'hover:text-foreground/80 transition-colors',
            pathname.includes('/monitoring')
              ? 'dark:text-primary-active'
              : 'text-foreground/60'
          )}
          href="/monitoring"
        >
          <span className="flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
            </span>
            {messages.monitoring || 'Live'}
          </span>
        </Link>

        <Link
          className={cn(
            'hover:text-foreground/80 transition-colors',
            pathname.includes('/aigarth-computer')
              ? 'dark:text-primary-active'
              : 'text-foreground/60'
          )}
          href="/aigarth-computer"
        >
          {messages.aigarth || 'Aigarth'}
        </Link>

        <Link
          className={cn(
            'hover:text-foreground/80 transition-colors',
            pathname.includes('/nft')
              ? 'dark:text-primary-active'
              : 'text-foreground/60'
          )}
          href="/nft"
        >
          {messages.nft || 'NFT'}
        </Link>

        <Link
          className={cn(
            'hover:text-foreground/80 transition-colors',
            pathname.includes('/agents')
              ? 'dark:text-primary-active'
              : 'text-foreground/60'
          )}
          href="/agents"
        >
          {messages.agents || 'Agents'}
        </Link>
      </nav>
    </div>
  )
}
