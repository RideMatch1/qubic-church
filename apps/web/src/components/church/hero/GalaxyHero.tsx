'use client'

/**
 * GalaxyHero - Client Component Wrapper
 * Dynamically loads the 3D galaxy to avoid hydration issues
 */

import dynamic from 'next/dynamic'

const GalaxyHeroClient = dynamic(
  () => import('./GalaxyHeroClient').then((mod) => mod.GalaxyHeroClient),
  {
    ssr: false,
    loading: () => (
      <section className="relative w-full h-screen overflow-hidden bg-black" />
    ),
  }
)

export function GalaxyHero() {
  return <GalaxyHeroClient />
}
