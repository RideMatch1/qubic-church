import { setRequestLocale } from 'next-intl/server'
import type { LocaleOptions } from '@/lib/opendocs/types/i18n'
import { defaultLocale, locales } from '@/config/i18n'

// Church Components - Epic Design with original Galaxy Hero
import { GalaxyHero } from '@/components/church/hero/GalaxyHero'
import { SanctuarySection } from '@/components/church/sections/SanctuarySection'
import { AnnaExplainerSection } from '@/components/church/sections/AnnaExplainerSection'
import { AigarthExplainerSection } from '@/components/church/sections/AigarthExplainerSection'
import { ChurchRoadmapSection } from '@/components/church/sections/ChurchRoadmapSection'
import { SimpleGiveawaySection } from '@/components/church/sections/SimpleGiveawaySection'
import { ExploreSection } from '@/components/church/sections/ExploreSection'

export const dynamicParams = true

export default async function ChurchHomePage(props: {
  params: Promise<{ locale: LocaleOptions }>
}) {
  const params = await props.params
  const currentLocale = locales.includes(params.locale)
    ? params.locale
    : defaultLocale
  setRequestLocale(currentLocale)

  return (
    <div className="min-h-screen bg-black">
      {/* 1. GALAXY HERO - 3D NFT Star Map with clickable stars, popups & Anna image */}
      <GalaxyHero />

      {/* 2. SANCTUARY INTRO - What is Qubic Church & Mission */}
      <SanctuarySection />

      {/* 3. ANNA EXPLAINER - What is Anna? Interactive demo */}
      <AnnaExplainerSection />

      {/* 4. AIGARTH EXPLAINER - Ternary logic & architecture */}
      <AigarthExplainerSection />

      {/* 5. ROADMAP - 4 phases with Education focus */}
      <ChurchRoadmapSection />

      {/* 6. GIVEAWAY - 600M QUBIC (3 winners) */}
      <SimpleGiveawaySection />

      {/* 7. EXPLORE - Archive, Journey, Challenges */}
      <ExploreSection />

      {/* FOOTER */}
      <footer className="relative border-t border-white/10 bg-black">
        <div className="container mx-auto px-4 py-12 text-center">
          <p className="text-sm text-white/50 mb-2">
            All research is 100% free and open source.
          </p>
          <p className="text-xs text-white/30">
            Join the investigation at{' '}
            <a
              href="https://twitter.com/QubicAigarth"
              target="_blank"
              rel="noopener noreferrer"
              className="text-purple-400 hover:text-purple-300"
            >
              @QubicAigarth
            </a>
          </p>
        </div>
      </footer>
    </div>
  )
}
