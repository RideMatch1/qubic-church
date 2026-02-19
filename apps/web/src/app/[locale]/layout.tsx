import { setRequestLocale } from 'next-intl/server'
import { NextIntlClientProvider } from 'next-intl'
import type { Metadata, Viewport } from 'next'

import '@/styles/globals.css'

import { getObjectValueByLocale } from '@/lib/opendocs/utils/locale'
import type { LocaleOptions } from '@/lib/opendocs/types/i18n'
import { ThemeProvider } from '@/components/theme-provider'
import { SiteFooter } from '@/components/site-footer'
import { SiteHeader } from '@/components/site-header'
import { EasterEggProvider } from '@/components/church/easter-eggs/EasterEggProvider'
import { TreasureHuntProvider } from '@/components/church/easter-eggs/TreasureHuntProvider'
import { CosmicWrapper } from '@/components/church/backgrounds/CosmicWrapper'
import { defaultLocale } from '@/config/i18n'
import { siteConfig } from '@/config/site'
import { HeaderVisibility } from '@/components/HeaderVisibility'
import { getSansFont, fontHeading, fontChalk, fontHandodle, fontDisplay } from '@/lib/fonts'
import { cn } from '@/lib/utils'

export async function generateMetadata(props: {
  params: Promise<{ locale: string }>
}): Promise<Metadata> {
  const params = await props.params

  const locale = (params.locale as LocaleOptions) || defaultLocale
  setRequestLocale(locale)

  return {
    title: {
      default: siteConfig.name,
      template: `%s - ${siteConfig.name}`,
    },

    description: getObjectValueByLocale(siteConfig.description, locale),

    keywords: [
      'Qubic',
      'Qubic Church',
      'Anna AI',
      'Aigarth',
      'Bitcoin Bridge',
      'Qubic NFT',
      'Anna NFT',
      'Crypto Research',
      'Blockchain Research',
      'CFB',
      'Ternary Computing',
      'Neural Network',
      'Qubic Mining',
      'Genesis Token',
      'Web3',
      'Cryptocurrency',
      'Open Source Research',
    ],

    authors: [
      {
        name: siteConfig.author.name,
        url: siteConfig.author.site,
      },
    ],

    creator: siteConfig.author.name,

    openGraph: {
      type: 'website',
      locale: 'en_US',
      url: siteConfig.url,
      title: siteConfig.name,
      siteName: siteConfig.name,

      description: getObjectValueByLocale(siteConfig.description, locale),

      images: [
        {
          ...siteConfig.og.size,
          alt: siteConfig.name,
          url: siteConfig.og.image,
        },
      ],
    },

    twitter: {
      creator: siteConfig.links.twitter.username,
      title: siteConfig.name,
      card: 'summary_large_image',
      images: [siteConfig.og.image],

      description: getObjectValueByLocale(siteConfig.description, locale),
    },

    icons: {
      icon: '/favicon.ico',
      apple: '/apple-touch-icon.png',
      shortcut: '/favicon-16x16.png',
    },

    manifest: '/manifest.webmanifest',
  }
}

export const dynamicParams = true

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
}

export default async function RootLayout(props: {
  params: Promise<{ locale: string }>
  children: React.ReactNode
}) {
  const params = await props.params

  const locale = (params.locale as LocaleOptions) || defaultLocale

  const { children } = props

  setRequestLocale(locale)

  const fontSans = await getSansFont()
  return (
    <html lang={locale} suppressHydrationWarning className="dark bg-black" style={{ backgroundColor: '#000' }}>
      <head>
        <meta content="#000000" name="theme-color" />
        <style dangerouslySetInnerHTML={{ __html: `
          html, body { background: #000 !important; }
          canvas { background: transparent !important; }
        `}} />
      </head>

      <body
        className={cn(
          'bg-black min-h-screen font-sans antialiased',
          fontSans.variable,
          fontHeading.variable,
          fontChalk.variable,
          fontHandodle.variable,
          fontDisplay.variable
        )}
      >
        <NextIntlClientProvider
          locale={params.locale || defaultLocale}
          messages={{}}
        >
          <ThemeProvider
            attribute="class"
            defaultTheme="dark"
            forcedTheme="dark"
            disableTransitionOnChange
          >
            <EasterEggProvider>
              <TreasureHuntProvider>
                <CosmicWrapper>
                  {/* Subtle noise texture - very low opacity to avoid color contamination */}
                  <div
                    className="fixed inset-0 z-[1] pointer-events-none opacity-[0.015] mix-blend-overlay"
                    style={{
                      backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
                      backgroundRepeat: 'repeat',
                      backgroundSize: '128px 128px',
                    }}
                  />
                  <div className="relative z-10 flex min-h-screen flex-col">
                    <HeaderVisibility>
                      <SiteHeader />
                    </HeaderVisibility>

                    <main className="flex-1">{children}</main>

                    <SiteFooter />
                  </div>
                </CosmicWrapper>
              </TreasureHuntProvider>
            </EasterEggProvider>
          </ThemeProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  )
}
