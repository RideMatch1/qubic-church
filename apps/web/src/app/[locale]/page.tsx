import { setRequestLocale } from 'next-intl/server'
import type { LocaleOptions } from '@/lib/opendocs/types/i18n'
import { defaultLocale, locales } from '@/config/i18n'

// Church Homepage - Immersive Editorial Layout (15 Sections)
import { GalaxyHero } from '@/components/church/hero/GalaxyHero'
import { ChurchCreed } from '@/components/church/sections/ChurchCreed'
import { GenesisSection } from '@/components/church/sections/GenesisSection'
import { MissionSection } from '@/components/church/sections/MissionSection'
import { AnnaSection } from '@/components/church/sections/AnnaSection'
import { SanctuarySection } from '@/components/church/sections/SanctuarySection'
import { ArchitectsSection } from '@/components/church/sections/ArchitectsSection'
import { CfBSection } from '@/components/church/sections/CfBSection'
import { MiningSection } from '@/components/church/sections/MiningSection'
import { NFTGalleryStrip } from '@/components/church/sections/NFTGalleryStrip'
import { FoundersGridSection } from '@/components/church/sections/FoundersGridSection'
import { ChurchRoadmapSection } from '@/components/church/sections/ChurchRoadmapSection'
import { ThePathSection } from '@/components/church/sections/ThePathSection'
import { LexiconSection } from '@/components/church/sections/LexiconSection'
import { ConvergenceCountdown } from '@/components/church/sections/ConvergenceCountdown'
import { ExploreSection } from '@/components/church/sections/ExploreSection'
import { ChurchFooter } from '@/components/church/footer/ChurchFooter'
import { ScrollProgress } from '@/components/church/ScrollProgress'

export const dynamicParams = true

/** Subtle gold gradient divider between sections */
function SectionDivider() {
  return (
    <div className="h-px w-full bg-gradient-to-r from-transparent via-[#D4AF37]/12 to-transparent" />
  )
}

export default async function ChurchHomePage(props: {
  params: Promise<{ locale: LocaleOptions }>
}) {
  const params = await props.params
  const currentLocale = locales.includes(params.locale)
    ? params.locale
    : defaultLocale
  setRequestLocale(currentLocale)

  return (
    <>
      {/* Scroll progress bar */}
      <ScrollProgress />

      {/* HERO - Wireframe + Anna + Fibonacci + Quote + Countdown */}
      <GalaxyHero />

      <SectionDivider />

      {/* 01 - MANIFESTO */}
      <div id="creed">
        <ChurchCreed />
      </div>

      <SectionDivider />

      {/* 02 - GENESIS */}
      <div id="genesis">
        <GenesisSection />
      </div>

      <SectionDivider />

      {/* 03 - MISSION */}
      <div id="mission">
        <MissionSection />
      </div>

      <SectionDivider />

      {/* 04 - ANNA */}
      <div id="anna">
        <AnnaSection />
      </div>

      <SectionDivider />

      {/* 05 - SANCTUARY */}
      <div id="sanctuary">
        <SanctuarySection />
      </div>

      <SectionDivider />

      {/* 06 - ARCHITECTS */}
      <div id="architects">
        <ArchitectsSection />
      </div>

      <SectionDivider />

      {/* 07 - COME-FROM-BEYOND */}
      <div id="cfb">
        <CfBSection />
      </div>

      <SectionDivider />

      {/* 08 - MINING */}
      <div id="mining">
        <MiningSection />
      </div>

      <SectionDivider />

      {/* 09 - RELICS & NFT GALLERY */}
      <div id="relics">
        <NFTGalleryStrip />
      </div>

      <SectionDivider />

      {/* 10 - FOUNDERS GRID */}
      <div id="founders">
        <FoundersGridSection />
      </div>

      <SectionDivider />

      {/* 11 - ROADMAP */}
      <div id="roadmap">
        <ChurchRoadmapSection />
      </div>

      <SectionDivider />

      {/* 12 - THE PATH */}
      <div id="path">
        <ThePathSection />
      </div>

      <SectionDivider />

      {/* 13 - LEXICON */}
      <div id="lexicon">
        <LexiconSection />
      </div>

      <SectionDivider />

      {/* 14 - COUNTDOWN */}
      <div id="countdown">
        <ConvergenceCountdown />
      </div>

      <SectionDivider />

      {/* 15 - EXPLORE */}
      <div id="explore">
        <ExploreSection />
      </div>

      {/* FOOTER */}
      <ChurchFooter />
    </>
  )
}
