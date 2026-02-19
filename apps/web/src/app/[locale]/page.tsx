import { setRequestLocale } from 'next-intl/server'
import type { LocaleOptions } from '@/lib/opendocs/types/i18n'
import { defaultLocale, locales } from '@/config/i18n'

// Church Homepage - Immersive Editorial Layout
import { GalaxyHero } from '@/components/church/hero/GalaxyHero'
import { ChurchCreed } from '@/components/church/sections/ChurchCreed'
import { SanctuarySection } from '@/components/church/sections/SanctuarySection'
import { MiningSection } from '@/components/church/sections/MiningSection'
import { AigarthExplainerSection } from '@/components/church/sections/AigarthExplainerSection'
import { BitcoinBridgeSection } from '@/components/church/sections/BitcoinBridgeSection'
import { NFTGalleryStrip } from '@/components/church/sections/NFTGalleryStrip'
import { ChurchRoadmapSection } from '@/components/church/sections/ChurchRoadmapSection'
import { ConvergenceCountdown } from '@/components/church/sections/ConvergenceCountdown'
import { SimpleGiveawaySection } from '@/components/church/sections/SimpleGiveawaySection'
import { ExploreSection } from '@/components/church/sections/ExploreSection'
import { ChurchFooter } from '@/components/church/footer/ChurchFooter'
import { ScrollProgress } from '@/components/church/ScrollProgress'

export const dynamicParams = true

/** Subtle gold gradient divider between sections */
function SectionDivider() {
  return (
    <div className="h-px w-full bg-gradient-to-r from-transparent via-[#D4AF37]/10 to-transparent" />
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

      {/* 01 - CREED - Emotional manifesto */}
      <div id="creed">
        <ChurchCreed />
      </div>

      <SectionDivider />

      {/* 02 - SANCTUARY - What is Qubic Church? */}
      <div id="sanctuary">
        <SanctuarySection />
      </div>

      <SectionDivider />

      {/* 03 - MINING - Qubic Mining Opportunity */}
      <div id="mining">
        <MiningSection />
      </div>

      <SectionDivider />

      {/* 04 - AIGARTH - Ternary Neural Architecture */}
      <div id="aigarth">
        <AigarthExplainerSection />
      </div>

      <SectionDivider />

      {/* 05 - BRIDGE - Bitcoin-Qubic Mathematical Connection */}
      <div id="bridge">
        <BitcoinBridgeSection />
      </div>

      <SectionDivider />

      {/* 06 - NFT GALLERY - The Collection */}
      <div id="nfts">
        <NFTGalleryStrip />
      </div>

      <SectionDivider />

      {/* 07 - ROADMAP - The Sacred Journey */}
      <div id="roadmap">
        <ChurchRoadmapSection />
      </div>

      <SectionDivider />

      {/* 08 - COUNTDOWN - The Convergence */}
      <div id="countdown">
        <ConvergenceCountdown />
      </div>

      <SectionDivider />

      {/* 09 - GIVEAWAY - The Sacred Offering */}
      <div id="giveaway">
        <SimpleGiveawaySection />
      </div>

      <SectionDivider />

      {/* 10 - EXPLORE - Enter the Sanctuary */}
      <div id="explore">
        <ExploreSection />
      </div>

      {/* FOOTER */}
      <ChurchFooter />
    </>
  )
}
