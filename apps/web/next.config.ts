import { createContentlayerPlugin } from 'next-contentlayer2'
import createNextIntlPlugin from 'next-intl/plugin'
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  reactStrictMode: true,
}

const withContentlayer = createContentlayerPlugin({})

const withNextIntl = createNextIntlPlugin('./src/i18n')

export default withNextIntl(withContentlayer(nextConfig))
