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
    cfb?: string
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
            pathname.includes('/cfb')
              ? 'dark:text-primary-active'
              : 'text-foreground/60'
          )}
          href="/cfb"
        >
          {messages.cfb || 'CFB Forensics'}
        </Link>
      </nav>
    </div>
  )
}
