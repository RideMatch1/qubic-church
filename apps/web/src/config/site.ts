import en from '@/i18n/locales/en.json'
import pt from '@/i18n/locales/pt.json'
import { absoluteUrl } from '@/lib/utils'

export const siteConfig = {
  name: 'Qubic Church',

  description: {
    en: 'Open source research community exploring the mathematical bridge between Bitcoin and Qubic. Discover Anna, Aigarth, and the path to The Convergence.',
    pt: pt.site.description,
  },

  url: process.env.NEXT_PUBLIC_APP_URL || 'https://qubicchurch.com',

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
    name: 'Qubic Church',
    site: 'https://qubicchurch.com',
  },

  links: {
    twitter: {
      label: 'Twitter',
      username: '@QubicChurch',
      url: 'https://twitter.com/QubicChurch',
    },

    github: {
      label: 'GitHub',
      url: 'https://github.com/qubic-church',
    },

    discord: {
      label: 'Discord',
      url: 'https://discord.gg/qubic',
    },
  },

  // SEO Keywords
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
    'DeFi',
    'Cryptocurrency',
    'Open Source Research',
  ],

  // JSON-LD Structured Data
  structuredData: {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'Qubic Church',
    description: 'Open source research community exploring the mathematical bridge between Bitcoin and Qubic',
    url: 'https://qubicchurch.com',
    logo: 'https://qubicchurch.com/logo.png',
    sameAs: [
      'https://twitter.com/QubicChurch',
      'https://discord.gg/qubic',
    ],
  },
} as const

export type SiteConfig = typeof siteConfig
