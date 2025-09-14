import { createContentlayerPlugin } from 'next-contentlayer2'
import createNextIntlPlugin from 'next-intl/plugin'

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

const withContentlayer = createContentlayerPlugin({})

const withNextIntl = createNextIntlPlugin('./src/i18n')

export default withNextIntl(withContentlayer(nextConfig))
