import { setRequestLocale } from 'next-intl/server'

import { JourneyPage } from '@/components/journey-v2'
import { GamificationProvider, AchievementUnlock } from '@/components/gamification'
import type { LocaleOptions } from '@/lib/opendocs/types/i18n'
import { defaultLocale, locales } from '@/config/i18n'

export const dynamicParams = true

export default async function TimelinePage(props: {
  params: Promise<{ locale: LocaleOptions }>
}) {
  const params = await props.params
  const currentLocale = locales.includes(params.locale)
    ? params.locale
    : defaultLocale
  setRequestLocale(currentLocale)

  return (
    <GamificationProvider>
      {/* Achievement Unlock Overlay */}
      <AchievementUnlock />

      {/* Epic Scroll-Based Journey */}
      <JourneyPage />
    </GamificationProvider>
  )
}
