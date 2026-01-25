'use client'

/**
 * CTASection Component
 * Call to action section for joining the community
 */

import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  Users,
  BookOpen,
  ExternalLink,
  ChevronRight,
  Compass,
  Image as ImageIcon,
} from 'lucide-react'

const ctaLinks = [
  {
    href: '/docs',
    title: 'Research Archive',
    desc: 'All research documents and data',
    icon: BookOpen,
    primary: true,
  },
  {
    href: '/evidence',
    title: 'Interactive Evidence',
    desc: 'Visualize the discoveries',
    icon: Compass,
    primary: false,
  },
  {
    href: '/nft',
    title: 'Anna NFT Collection',
    desc: '200 unique digital artifacts',
    icon: ImageIcon,
    primary: false,
  },
]

const externalLinks = [
  { href: 'https://qubic.org', title: 'Qubic Official', desc: 'The Qubic network' },
  { href: 'https://discord.gg/qubic', title: 'Discord', desc: 'Join the discussion' },
  {
    href: 'https://qubicbay.com',
    title: 'QubicBay',
    desc: 'NFT Marketplace',
  },
]

export function CTASection() {
  return (
    <section className="w-full py-20 bg-gradient-to-b from-background via-purple-950/10 to-background">
      <div className="container mx-auto px-4 max-w-5xl">
        {/* Section Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Join the Investigation
          </h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            The research continues - and you can be part of it
          </p>
        </motion.div>

        {/* Primary CTAs */}
        <motion.div
          className="grid md:grid-cols-3 gap-4 mb-8"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          {ctaLinks.map((link, index) => {
            const Icon = link.icon
            return (
              <Link
                key={index}
                href={link.href}
                className={`p-6 rounded-2xl transition-all group ${
                  link.primary
                    ? 'bg-gradient-to-br from-primary/20 to-purple-500/20 border-2 border-primary/30 hover:border-primary/50'
                    : 'bg-card border border-border hover:bg-muted/50'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2 rounded-lg ${link.primary ? 'bg-primary/20' : 'bg-muted'}`}>
                    <Icon className={`w-5 h-5 ${link.primary ? 'text-primary' : 'text-muted-foreground'}`} />
                  </div>
                  <ChevronRight
                    className={`w-5 h-5 transition-transform group-hover:translate-x-1 ${
                      link.primary ? 'text-primary' : 'text-muted-foreground'
                    }`}
                  />
                </div>
                <h4 className={`font-semibold mb-1 ${link.primary ? 'text-foreground' : 'text-foreground/90'}`}>
                  {link.title}
                </h4>
                <p className="text-sm text-muted-foreground">{link.desc}</p>
              </Link>
            )
          })}
        </motion.div>

        {/* External Links */}
        <motion.div
          className="p-6 rounded-2xl bg-card border border-border mb-8"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-muted-foreground" />
            Join the Community
          </h3>

          <div className="grid md:grid-cols-3 gap-3">
            {externalLinks.map((link, index) => (
              <a
                key={index}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="p-4 rounded-xl bg-muted/50 hover:bg-muted transition-colors group"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium">{link.title}</span>
                  <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                </div>
                <p className="text-xs text-muted-foreground">{link.desc}</p>
              </a>
            ))}
          </div>
        </motion.div>

        {/* NFT Support Section */}
        <motion.div
          className="p-8 rounded-2xl bg-gradient-to-b from-purple-950/30 to-background border border-purple-500/20 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <h3 className="text-xl font-bold mb-3">Support Open Research</h3>
          <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
            All our research is 100% free and open source. By purchasing an Anna NFT,
            you support independent research and join the Holy Circle community.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="https://qubicbay.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-orange-600 to-purple-600 hover:from-orange-500 hover:to-purple-500 px-8 py-4 text-base font-semibold text-white shadow-lg transition-all duration-300 hover:scale-105"
            >
              View Anna NFT Collection
              <ExternalLink className="w-4 h-4 ml-2" />
            </a>
          </div>
        </motion.div>

        {/* Final Quote */}
        <motion.div
          className="text-center py-8"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <p className="text-lg text-muted-foreground italic">
            "The truth is not hidden. It was always there, waiting for someone to look."
          </p>
          <p className="text-sm text-muted-foreground/70 mt-2">
            - The Qubic Church Research Collective
          </p>
        </motion.div>
      </div>
    </section>
  )
}
