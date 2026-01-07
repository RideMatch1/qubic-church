import { setRequestLocale } from 'next-intl/server'

import { CFBHero, CFBOverview } from '@/components/cfb'
import { GamificationProvider, AchievementUnlock } from '@/components/gamification'
import type { LocaleOptions } from '@/lib/opendocs/types/i18n'
import { defaultLocale, locales } from '@/config/i18n'

export const dynamicParams = true

export default async function CFBPage(props: {
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
        {/* Achievement Unlock Overlay */}
        <AchievementUnlock />

        <main className="flex-1">
          {/* 1. Hero: CFB Introduction */}
          <CFBHero />

          {/* 2. Overview: Navigation to sub-sections */}
          <CFBOverview />
        </main>

        <footer className="py-8 border-t border-border bg-muted/10">
          <div className="container">
            <div className="flex flex-col items-center text-center">
              <p className="font-mono text-lg text-primary/80 mb-4">
                26,049+ Data Points Analyzed
              </p>
              <p className="text-sm text-muted-foreground">
                CFB Forensics - Come-from-Beyond Research Archive
              </p>
              <p className="mt-2 font-mono text-xs text-muted-foreground/80">
                99.8% Stylometry Match | 91% Overall Confidence | 17 Years of Data
              </p>
            </div>
          </div>
        </footer>
      </div>
    </GamificationProvider>
  )
}
