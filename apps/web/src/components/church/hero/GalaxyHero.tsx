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
      <section className="relative w-full h-screen overflow-hidden bg-black">
        <div className="absolute inset-0 bg-gradient-radial from-purple-900/20 via-blue-900/5 to-black" />
      </section>
    ),
  }
)

export function GalaxyHero() {
  return <GalaxyHeroClient />
}
