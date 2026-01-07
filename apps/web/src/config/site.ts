import en from '@/i18n/locales/en.json'
import pt from '@/i18n/locales/pt.json'
import { absoluteUrl } from '@/lib/utils'

export const siteConfig = {
  name: 'The Bitcoin-Qubic Bridge',

  description: {
    en: en.site.description,
    pt: pt.site.description,
  },

  url: process.env.NEXT_PUBLIC_APP_URL,

  og: {
    image: absoluteUrl('/og.jpg'),

    size: {
      width: 1200,
      height: 630,
    },
  },

  app: {
    latestVersion: '1.0.0',
  },

  author: {
    name: 'Qubic Research Archive',
    site: 'https://qubic-research.org',
  },

  links: {
    twitter: {
      label: 'Twitter',
      username: '@qubic_research',
      url: 'https://twitter.com/qubic_research',
    },

    github: {
      label: 'GitHub',
      url: 'https://github.com/qubic-research/bitcoin-bridge',
    },
  },
} as const

export type SiteConfig = typeof siteConfig
