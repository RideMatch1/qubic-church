import { setRequestLocale } from 'next-intl/server'

import { StylemetryRadar } from '@/components/cfb'
import { GamificationProvider, AchievementUnlock } from '@/components/gamification'
import type { LocaleOptions } from '@/lib/opendocs/types/i18n'
import { defaultLocale, locales } from '@/config/i18n'

export const dynamicParams = true

export default async function CFBStylometryPage(props: {
  params: Promise<{ locale: LocaleOptions }>
}) {
  const params = await props.params
  const currentLocale = locales.includes(params.locale)
    ? params.locale
    : defaultLocale
  setRequestLocale(currentLocale)

  return (
    <GamificationProvider>
      <div className="flex flex-col min-h-screen">
        <AchievementUnlock />

        <main className="flex-1">
          <StylemetryRadar />
        </main>

        <footer className="py-8 border-t border-border bg-muted/10">
          <div className="container">
            <div className="flex flex-col items-center text-center">
              <p className="font-mono text-lg text-emerald-400 mb-4">
                99.8% Match Score
              </p>
              <p className="text-sm text-muted-foreground">
                CFB Forensics - Stylometry Analysis
              </p>
              <p className="mt-2 font-mono text-xs text-muted-foreground/80">
                847 Satoshi Posts | 15,000+ CFB Writings | 8 Linguistic Metrics
              </p>
            </div>
          </div>
        </footer>
      </div>
    </GamificationProvider>
  )
}
