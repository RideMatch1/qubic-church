import { setRequestLocale } from 'next-intl/server'
import type { LocaleOptions } from '@/lib/opendocs/types/i18n'
import { defaultLocale, locales } from '@/config/i18n'
import { CHURCH_CONFIG } from '@/config/church'
import { ChurchHero } from '@/components/church/hero/ChurchHero'
import { MetricsDashboard } from '@/components/church/metrics/MetricsDashboard'

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
    <div className="min-h-screen">
      {/* Hero Section with 3D Star Map */}
      <ChurchHero />

      {/* Live Metrics Dashboard */}
      <MetricsDashboard />

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16 text-center bg-gradient-to-b from-background to-muted">
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
          🚧 Phase 5 Implementation in Progress: Live Metrics, Holy Circle, and
          Intelligence Challenges coming soon
        </p>
      </section>
    </div>
  )
}
