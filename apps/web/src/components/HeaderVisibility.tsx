'use client'

import { usePathname } from '@/navigation'

export function HeaderVisibility({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  // Hide header on homepage - navigation is handled by the immersion wheel
  const isHomepage = pathname === '/' || pathname === ''

  if (isHomepage) return null

  return <>{children}</>
}
