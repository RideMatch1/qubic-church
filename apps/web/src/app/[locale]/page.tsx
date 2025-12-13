import { setRequestLocale, getTranslations } from 'next-intl/server'

import {
  PageHeader,
  PageActions,
  PageHeaderHeading,
  PageHeaderDescription,
} from '@/components/page-header'

import { TextGenerateEffect } from '@/components/ui/text-generate-effect'
import { InstallationBox } from '@/components/installation-box'
import type { LocaleOptions } from '@/lib/opendocs/types/i18n'
import { FeaturedCard } from '@/components/featured-card'
import { Announcement } from '@/components/announcement'
import { buttonVariants } from '@/components/ui/button'
import { FlipWords } from '@/components/ui/flip-words'
import { Vortex } from '@/components/vortex'
import { Icons } from '@/components/icons'
import { siteConfig } from '@/config/site'
import { Link } from '@/navigation'
import { cn } from '@/lib/utils'
import { defaultLocale, locales } from '@/config/i18n'

export const dynamicParams = true

export default async function IndexPage(props: {
  params: Promise<{ locale: LocaleOptions }>
}) {
  const params = await props.params
  const currentLocale = locales.includes(params.locale)
    ? params.locale
    : defaultLocale
  setRequestLocale(currentLocale)

  const t = await getTranslations('site')

  return (
    <div className="container relative">
      <PageHeader>
        <Announcement href="/docs" title={t('announcement')} />

        <PageHeaderHeading>
          <FlipWords
            className="text-9xl -z-10"
            words={['site', 'blog', 'docs']}
          />

          <TextGenerateEffect words={t('heading')} />
        </PageHeaderHeading>

        <PageHeaderDescription>{t('description')}</PageHeaderDescription>

        <PageActions className="flex-wrap gap-3 sm:gap-0">
          <Link className={cn(buttonVariants())} href="/docs">
            {t('buttons.get_started')}
          </Link>

          <Link
            className={cn(buttonVariants({ variant: 'outline' }))}
            href={siteConfig.links.github.url}
            rel="noreferrer"
            target="_blank"
            title={siteConfig.links.github.label}
          >
            <Icons.gitHub className="mr-2 size-4" />
            {siteConfig.links.github.label}
          </Link>

          <Link
            className={cn(
              buttonVariants({ variant: 'outline' }),
              'flex gap-2 group'
            )}
            href="https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fdaltonmenezes%2Fopendocs&project-name=my-opendocs&repository-name=my-opendocs&demo-title=OpenDocs&demo-description=Next.js%20beautifully%20designed%20template%20that%20you%20can%20use%20for%20your%20projects%20for%20free%20with%20site%2C%20blog%20and%20docs%20support.%20Accessible.%20Customizable.%20Open%20Source%20with%20i18n%20support.&demo-url=https%3A%2F%2Fopendocs.daltonmenezes.com%2F&root-directory=apps%2Fweb"
            target="_blank"
          >
            <span className="pr-3 mr-1 border border-transparent border-r-border group-hover:border-r-black/50">
              ▲
            </span>
            {t('buttons.deploy_vercel')}
          </Link>
        </PageActions>

        <InstallationBox
          __rawString__="npx degit daltonmenezes/opendocs project_name"
          className="w-full relative max-w-140 flex flex-wrap items-center pl-4! pr-12!"
        />

        <div className="fixed left-0 -top-40 size-full -z-10 overflow-hidden">
          <Vortex
            backgroundColor="transparent"
            baseRadius={2}
            className="flex size-full"
            particleCount={20}
            rangeSpeed={1.5}
            rangeY={300}
          />
        </div>
      </PageHeader>

      <section className="flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-2 2xl:grid-cols-4">
          <FeaturedCard
            description={t('featured_cards.nextjs.description')}
            icon="🧬"
            title="Next.js"
          />

          <FeaturedCard
            description={t('featured_cards.shadcn.description')}
            icon="⚡️"
            title="Shadcn"
          />

          <FeaturedCard
            description={t('featured_cards.tailwind.description')}
            icon="🚀"
            title="Tailwind"
          />

          <FeaturedCard
            description={t('featured_cards.i18n.description')}
            icon="🌍"
            title="i18n"
          />
        </div>

        <FeaturedCard
          description={t('featured_cards.more.description')}
          icon="+"
          orientation="horizontal"
          title={t('featured_cards.more.title')}
        />
      </section>
    </div>
  )
}
