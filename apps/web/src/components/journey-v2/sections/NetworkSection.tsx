'use client'

import { useRef, useState, useEffect } from 'react'
import { motion, useInView } from 'framer-motion'
import { JourneySection } from '../JourneySection'
import { Network, ArrowRight, Users, GitBranch, HelpCircle, Share2, Activity } from 'lucide-react'
import Link from 'next/link'

// Deterministic connection points
const CONNECTION_POINTS = Array.from({ length: 20 }, (_, i) => ({
  id: i,
  x: 10 + (i % 5) * 20,
  y: 15 + Math.floor(i / 5) * 20,
  size: 3 + (i % 3),
  delay: i * 0.05,
}))

export function NetworkSection() {
  const contentRef = useRef(null)
  const isInView = useInView(contentRef, { once: false, amount: 0.2 })
  const [animatedNodes, setAnimatedNodes] = useState(0)

  // Animate nodes appearing
  useEffect(() => {
    if (isInView) {
      const timer = setInterval(() => {
        setAnimatedNodes(prev => {
          if (prev >= 20) {
            clearInterval(timer)
            return 20
          }
          return prev + 1
        })
      }, 80)
      return () => clearInterval(timer)
    } else {
      setAnimatedNodes(0)
    }
  }, [isInView])

  return (
    <JourneySection id="network" background="transparent" className="flex items-center justify-center py-12 md:py-20">
      <div ref={contentRef} className="relative z-10 w-full max-w-5xl mx-auto px-4">
        {/* Chapter Header */}
        <motion.div
          className="text-center mb-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0.9 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/50 text-xs font-mono">
              CHAPTER 6
            </span>
          </motion.div>

          <motion.div
            className="inline-flex items-center gap-2 mb-4"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: isInView ? 1 : 0, scale: isInView ? 1 : 0.9 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Network className="h-8 w-8 text-white/60" />
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-bold text-white/90 mb-6">
            The Address Network
          </h2>

          {/* Story context */}
          <motion.div
            className="max-w-2xl mx-auto space-y-4 mb-8"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <p className="text-lg text-white/50 leading-relaxed">
              We analyzed over <span className="text-white/70 font-medium">1.1 million addresses</span> —
              mapping connections between Bitcoin's early network and Qubic.
            </p>
            <p className="text-base text-white/40 leading-relaxed">
              The patterns that emerged look like{' '}
              <span className="text-white/60">neural pathways</span>, connecting two systems
              separated by 15 years.
            </p>
          </motion.div>

          {/* What is an address network */}
          <motion.div
            className="inline-flex items-start gap-3 px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-left max-w-lg mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: isInView ? 1 : 0 }}
            transition={{ delay: 0.6 }}
          >
            <HelpCircle className="h-5 w-5 text-white/40 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-white/60 font-medium mb-1">What is an Address Network?</p>
              <p className="text-xs text-white/40 leading-relaxed">
                Every Bitcoin transaction creates a link between addresses. By mapping millions
                of these connections, we can visualize how money flows — and who might be
                connected to whom.
              </p>
            </div>
          </motion.div>
        </motion.div>

        {/* Network Preview Visualization */}
        <motion.div
          className="relative rounded-2xl overflow-hidden border border-white/10 bg-black/40 mb-8"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 30 }}
          transition={{ duration: 0.6, delay: 0.7 }}
        >
          {/* Simplified Network Visualization */}
          <div className="p-8 md:p-12 relative h-64">
            {/* Connection lines */}
            <svg className="absolute inset-0 w-full h-full" style={{ opacity: 0.3 }}>
              {CONNECTION_POINTS.slice(0, animatedNodes).map((point, i) =>
                CONNECTION_POINTS.slice(i + 1, Math.min(i + 4, animatedNodes)).map((target, j) => (
                  <motion.line
                    key={`${i}-${j}`}
                    x1={`${point.x}%`}
                    y1={`${point.y}%`}
                    x2={`${target.x}%`}
                    y2={`${target.y}%`}
                    stroke="rgba(255,255,255,0.2)"
                    strokeWidth="1"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 0.5 }}
                  />
                ))
              )}
            </svg>

            {/* Nodes */}
            {CONNECTION_POINTS.map((point, i) => (
              <motion.div
                key={point.id}
                className="absolute rounded-full bg-white/40"
                style={{
                  left: `${point.x}%`,
                  top: `${point.y}%`,
                  width: point.size,
                  height: point.size,
                  transform: 'translate(-50%, -50%)',
                }}
                initial={{ scale: 0, opacity: 0 }}
                animate={{
                  scale: i < animatedNodes ? 1 : 0,
                  opacity: i < animatedNodes ? 1 : 0,
                }}
                transition={{ duration: 0.3, delay: point.delay }}
              />
            ))}

            {/* Center pulse */}
            <motion.div
              className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
              initial={{ scale: 0 }}
              animate={{ scale: isInView ? 1 : 0 }}
              transition={{ delay: 1.5 }}
            >
              <motion.div
                className="w-8 h-8 rounded-full bg-white/20"
                animate={{ scale: [1, 1.3, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </motion.div>
          </div>

          {/* Stats */}
          <div className="px-8 pb-6 flex justify-center gap-8 text-center">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
              transition={{ delay: 1 }}
            >
              <div className="text-2xl font-mono font-bold text-white/80">1.14M</div>
              <div className="text-xs text-white/40">Addresses</div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
              transition={{ delay: 1.1 }}
            >
              <div className="text-2xl font-mono font-bold text-white/80">3.2M</div>
              <div className="text-xs text-white/40">Connections</div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 10 }}
              transition={{ delay: 1.2 }}
            >
              <div className="text-2xl font-mono font-bold text-white/80">47</div>
              <div className="text-xs text-white/40">Hub clusters</div>
            </motion.div>
          </div>

          {/* CTA to full experience */}
          <Link
            href="/evidence/address-network"
            className="block p-6 border-t border-white/10 bg-white/[0.02] hover:bg-white/[0.05] transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-white/5">
                  <Share2 className="h-6 w-6 text-white/50" />
                </div>
                <div>
                  <div className="font-medium text-white/80 group-hover:text-white transition-colors">
                    Explore Full 3D Network
                  </div>
                  <div className="text-sm text-white/40">
                    Interactive graph with timeline scrubber
                  </div>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-white/50 group-hover:text-white/60 group-hover:translate-x-1 transition-all" />
            </div>
          </Link>
        </motion.div>

        {/* Network Stats */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.6, delay: 1 }}
        >
          <motion.div
            className="p-4 rounded-xl bg-white/5 border border-white/10 text-center"
            whileHover={{ scale: 1.02, y: -2 }}
          >
            <Users className="h-5 w-5 text-white/40 mx-auto mb-2" />
            <div className="text-xl font-mono font-bold text-white/80">1.14M</div>
            <div className="text-xs text-white/40">Total addresses</div>
          </motion.div>

          <motion.div
            className="p-4 rounded-xl bg-white/5 border border-white/10 text-center"
            whileHover={{ scale: 1.02, y: -2 }}
          >
            <GitBranch className="h-5 w-5 text-white/40 mx-auto mb-2" />
            <div className="text-xl font-mono font-bold text-white/80">3.2M</div>
            <div className="text-xs text-white/40">Connections mapped</div>
          </motion.div>

          <motion.div
            className="p-4 rounded-xl bg-white/5 border border-white/10 text-center"
            whileHover={{ scale: 1.02, y: -2 }}
          >
            <Network className="h-5 w-5 text-white/40 mx-auto mb-2" />
            <div className="text-xl font-mono font-bold text-white/80">21,953</div>
            <div className="text-xs text-white/40">Patoshi nodes</div>
          </motion.div>

          <motion.div
            className="p-4 rounded-xl bg-white/5 border border-white/10 text-center"
            whileHover={{ scale: 1.02, y: -2 }}
          >
            <Activity className="h-5 w-5 text-white/40 mx-auto mb-2" />
            <div className="text-xl font-mono font-bold text-white/80">47</div>
            <div className="text-xs text-white/40">Hub clusters</div>
          </motion.div>
        </motion.div>

        {/* Connection Types */}
        <motion.div
          className="p-6 rounded-xl bg-white/[0.03] border border-white/10 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.6, delay: 1.2 }}
        >
          <h3 className="font-medium text-white/70 mb-4">What the Analysis Reveals</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5">
              <div className="w-3 h-3 rounded-full bg-white/40" />
              <div>
                <div className="text-sm text-white/60">Bitcoin Early (2009-2010)</div>
                <div className="text-xs text-white/40">Original Satoshi-era blocks</div>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5">
              <div className="w-3 h-3 rounded-full bg-white/30" />
              <div>
                <div className="text-sm text-white/60">Qubic References</div>
                <div className="text-xs text-white/40">Addresses in Anna Matrix</div>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5">
              <div className="w-3 h-3 rounded-full bg-white/20" />
              <div>
                <div className="text-sm text-white/60">Cross-Links</div>
                <div className="text-xs text-white/40">Pattern matches between both</div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Transition hint */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: 1.4 }}
        >
          <p className="text-sm text-white/50 italic">
            "All paths lead to a single date..."
          </p>
        </motion.div>
      </div>
    </JourneySection>
  )
}
