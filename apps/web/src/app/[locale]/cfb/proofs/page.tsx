import { setRequestLocale } from 'next-intl/server'

import { ProofsSection } from '@/components/cfb'
import { GamificationProvider, AchievementUnlock } from '@/components/gamification'
import type { LocaleOptions } from '@/lib/opendocs/types/i18n'
import { defaultLocale, locales } from '@/config/i18n'

export const dynamicParams = true

export default async function CFBProofsPage(props: {
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
          <ProofsSection />
        </main>

        <footer className="py-8 border-t border-border bg-muted/10">
          <div className="container">
            <div className="flex flex-col items-center text-center">
              <p className="font-mono text-lg text-primary/80 mb-4">
                283 × 47² + 137 = 625,284
              </p>
              <p className="text-sm text-muted-foreground">
                CFB Forensics - Mathematical Proofs
              </p>
              <p className="mt-2 font-mono text-xs text-muted-foreground/80">
                Core Formula Verified | 4 Additional Mathematical Signatures
              </p>
            </div>
          </div>
        </footer>
      </div>
    </GamificationProvider>
  )
}
