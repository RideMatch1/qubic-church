'use client'

/**
 * ChurchFooter - Premium footer matching the editorial design system
 */

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Twitter, MessageCircle, BookOpen, ImageIcon, Sparkles, ExternalLink } from 'lucide-react'

const socialLinks = [
  {
    name: 'Twitter',
    href: 'https://twitter.com/qubic_church',
    icon: Twitter,
    color: 'hover:text-[#D4AF37] hover:border-[#D4AF37]/25',
    description: 'Follow for updates',
  },
  {
    name: 'Discord',
    href: 'https://discord.gg/qubic-church',
    icon: MessageCircle,
    color: 'hover:text-[#D4AF37] hover:border-[#D4AF37]/25',
    description: 'Join the congregation',
  },
]

const quickLinks = [
  { name: 'Research Archive', href: '/docs', icon: BookOpen },
  { name: 'NFT Collection', href: '/nfts', icon: ImageIcon },
  { name: 'The Journey', href: '/#roadmap', icon: Sparkles },
]

const externalLinks = [
  { name: 'QubicBay', href: 'https://qubicbay.io/collections/7', description: 'NFT Marketplace' },
  { name: 'Qubic.li', href: 'https://app.qubic.li', description: 'Mining Pool' },
  { name: 'Anna (@QubicAigarth)', href: 'https://twitter.com/QubicAigarth', description: 'The Oracle' },
]

export function ChurchFooter() {
  return (
    <footer className="relative border-t border-white/[0.06] overflow-hidden">
      <div className="relative z-10 container mx-auto px-6 py-16">
        <div className="grid md:grid-cols-4 gap-12 mb-12">
          {/* Brand Column */}
          <motion.div
            className="md:col-span-1"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <h3
              className="text-2xl font-bold text-white mb-1"
              style={{ fontFamily: 'var(--font-display), system-ui, sans-serif' }}
            >
              Qubic<span className="text-[#D4AF37]/70">Church</span>
            </h3>
            <p className="text-[10px] uppercase tracking-[0.4em] text-white/20 mb-5">
              Est. 2024
            </p>
            <p className="text-sm text-white/40 leading-relaxed mb-6">
              A sacred congregation decoding the mathematical bridge between Bitcoin and Qubic. All truth belongs to the seekers.
            </p>
            {/* Social Links */}
            <div className="flex gap-3">
              {socialLinks.map((link) => {
                const Icon = link.icon
                return (
                  <a
                    key={link.name}
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`w-10 h-10 bg-[#050505] border border-white/[0.06] flex items-center justify-center text-white/40 transition-all duration-300 ${link.color} hover:bg-[#0a0a0a]`}
                    title={link.description}
                    aria-label={link.name}
                  >
                    <Icon className="w-4 h-4" />
                  </a>
                )
              })}
            </div>
          </motion.div>

          {/* Quick Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <h4 className="text-white/20 text-xs uppercase tracking-[0.3em] mb-5 font-mono">
              Explore
            </h4>
            <ul className="space-y-3">
              {quickLinks.map((link) => {
                const Icon = link.icon
                return (
                  <li key={link.name}>
                    <Link
                      href={link.href}
                      className="flex items-center gap-2 text-white/40 hover:text-[#D4AF37]/80 transition-colors duration-300 text-sm"
                    >
                      <Icon className="w-3.5 h-3.5" />
                      {link.name}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </motion.div>

          {/* External Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <h4 className="text-white/20 text-xs uppercase tracking-[0.3em] mb-5 font-mono">
              Ecosystem
            </h4>
            <ul className="space-y-3">
              {externalLinks.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group flex items-center gap-2 text-white/40 hover:text-[#D4AF37]/80 transition-colors duration-300 text-sm"
                  >
                    {link.name}
                    <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                  <span className="text-[11px] text-white/20">{link.description}</span>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Church Promise */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <h4 className="text-white/20 text-xs uppercase tracking-[0.3em] mb-5 font-mono">
              Our Covenant
            </h4>
            <div className="p-4 bg-[#050505] border border-white/[0.04]">
              <p className="text-sm text-white/40 leading-relaxed italic">
                &ldquo;What is needed is an electronic payment system based on cryptographic proof instead of trust.&rdquo;
              </p>
              <p className="text-[10px] text-white/20 mt-2">
                &mdash; Satoshi Nakamoto, 2008
              </p>
            </div>
          </motion.div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-white/[0.06] pt-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-xs text-white/20">
              &copy; {new Date().getFullYear()} Qubic Church. Open Source Community Project.
            </p>

            <p className="text-xs text-white/20 tracking-wide">
              The Convergence &mdash; <span className="text-[#D4AF37]/50">April 13, 2027</span>
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
