import { setRequestLocale } from 'next-intl/server'
import type { LocaleOptions } from '@/lib/opendocs/types/i18n'
import { defaultLocale, locales } from '@/config/i18n'
import { CHURCH_CONFIG } from '@/config/church'
import { NFT_COLLECTION } from '@/config/nfts'

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
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted">
      {/* Hero Section - Placeholder */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center space-y-6">
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
            ✨ {CHURCH_CONFIG.mission.title} ✨
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto">
            {CHURCH_CONFIG.mission.subtitle}
          </p>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            {CHURCH_CONFIG.mission.description}
          </p>

          {/* Countdown Placeholder */}
          <div className="mt-8 p-6 bg-card rounded-lg border inline-block">
            <p className="text-sm text-muted-foreground mb-2">
              {CHURCH_CONFIG.countdown.label}
            </p>
            <p className="text-3xl font-mono font-bold">
              {new Date(CHURCH_CONFIG.countdown.targetDate).toLocaleDateString()}
            </p>
          </div>
        </div>
      </section>

      {/* NFT Collection Preview */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center space-y-4 mb-12">
          <h2 className="text-3xl md:text-4xl font-bold">
            {CHURCH_CONFIG.collection.name}
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            {CHURCH_CONFIG.collection.description}
          </p>
          <p className="text-2xl font-bold">
            {NFT_COLLECTION.length} Unique NFTs
          </p>
        </div>

        {/* Placeholder for Star Map */}
        <div className="bg-card border rounded-lg p-12 text-center">
          <div className="space-y-4">
            <div className="text-6xl">🌟</div>
            <p className="text-xl font-semibold">Interactive 3D Star Map</p>
            <p className="text-muted-foreground">
              Coming soon: Explore 200 Anna NFTs in an immersive star field
            </p>
            <p className="text-sm text-muted-foreground mt-8">
              Phase 5 Implementation in Progress
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="space-y-6 max-w-2xl mx-auto">
          <h3 className="text-2xl font-bold">Support Open Research</h3>
          <p className="text-muted-foreground">
            All our research is 100% free and open source. By purchasing an Anna
            NFT, you support independent research and join the community
            discovering the Bitcoin-Qubic connection.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <a
              href={CHURCH_CONFIG.links.qubicBay}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center rounded-md bg-primary px-8 py-3 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90"
            >
              View Collection on QubicBay
            </a>
            <a
              href="/timeline"
              className="inline-flex items-center justify-center rounded-md border border-input bg-background px-8 py-3 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground"
            >
              Explore the Journey
            </a>
          </div>
        </div>
      </section>

      {/* Footer Notice */}
      <section className="container mx-auto px-4 py-8 text-center border-t">
        <p className="text-sm text-muted-foreground">
          🚧 Phase 5 Implementation in Progress: Star Map, Live Metrics, Holy
          Circle, and Intelligence Challenges coming soon
        </p>
      </section>
    </div>
  )
}
