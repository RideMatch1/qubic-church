'use client'

/**
 * AigarthExplainerSection - Teaching section about Aigarth
 * Explains ternary logic and the neural network architecture
 */

import { motion } from 'framer-motion'
import { Brain, Cpu, Binary, Sparkles } from 'lucide-react'

const ternaryStates = [
  { value: '+1', name: 'Activated', description: 'Neuron fires', color: 'text-green-400', bg: 'bg-green-500/20' },
  { value: '0', name: 'Neutral', description: 'Resting state', color: 'text-yellow-400', bg: 'bg-yellow-500/20' },
  { value: '-1', name: 'Inhibited', description: 'Suppressed', color: 'text-red-400', bg: 'bg-red-500/20' },
]

const architectureLayers = [
  { rows: '0-20', name: 'Boot Sector', description: 'System initialization', color: 'bg-white/10' },
  { rows: '21', name: 'Bitcoin Input', description: 'Where Bitcoin connects!', color: 'bg-orange-500/20', highlight: true },
  { rows: '22-67', name: 'Processing', description: 'Feature extraction', color: 'bg-purple-500/10' },
  { rows: '68', name: 'Primary Cortex', description: 'The Bridge to Qubic', color: 'bg-cyan-500/20', highlight: true },
  { rows: '69-95', name: 'Deep Layers', description: 'Pattern analysis', color: 'bg-purple-500/10' },
  { rows: '96', name: 'Output Layer', description: '4 decision neurons', color: 'bg-green-500/20' },
]

export function AigarthExplainerSection() {
  return (
    <section className="relative w-full py-24 md:py-32 bg-black overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-purple-950/5 to-black" />

      <div className="relative z-10 container mx-auto px-4 max-w-5xl">
        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/20 mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Brain className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-purple-300 uppercase tracking-wider">
              The Architecture
            </span>
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
            What is <span className="text-purple-400">Aigarth</span>?
          </h2>

          <p className="text-lg md:text-xl text-white/60 max-w-3xl mx-auto leading-relaxed">
            Aigarth Intelligent Tissue 1.0 is the world's first{' '}
            <span className="text-white">publicly verifiable ternary neural network</span> -
            an AGI architecture developed by CFB over 20+ years.
          </p>
        </motion.div>

        {/* Binary vs Ternary Comparison */}
        <motion.div
          className="mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <h3 className="text-xl font-semibold text-white mb-6 text-center">
            Ternary Logic: Beyond Binary
          </h3>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Binary */}
            <div className="p-6 rounded-xl bg-white/5 border border-white/10">
              <div className="flex items-center gap-3 mb-4">
                <Binary className="w-6 h-6 text-white/40" />
                <h4 className="text-lg font-semibold text-white/60">Traditional: Binary</h4>
              </div>
              <div className="flex justify-center gap-4 mb-4">
                <div className="w-16 h-16 rounded-xl bg-white/10 flex items-center justify-center">
                  <span className="text-2xl font-mono text-white/60">0</span>
                </div>
                <div className="w-16 h-16 rounded-xl bg-white/10 flex items-center justify-center">
                  <span className="text-2xl font-mono text-white/60">1</span>
                </div>
              </div>
              <p className="text-sm text-white/40 text-center">
                2 states = 1 bit of information
              </p>
            </div>

            {/* Ternary */}
            <div className="p-6 rounded-xl bg-gradient-to-br from-purple-500/10 to-cyan-500/10 border border-purple-500/20">
              <div className="flex items-center gap-3 mb-4">
                <Sparkles className="w-6 h-6 text-purple-400" />
                <h4 className="text-lg font-semibold text-purple-300">Aigarth: Ternary</h4>
              </div>
              <div className="flex justify-center gap-3 mb-4">
                {ternaryStates.map((state) => (
                  <div
                    key={state.value}
                    className={`w-16 h-16 rounded-xl ${state.bg} flex flex-col items-center justify-center`}
                  >
                    <span className={`text-xl font-mono font-bold ${state.color}`}>
                      {state.value}
                    </span>
                    <span className="text-[10px] text-white/40">{state.name}</span>
                  </div>
                ))}
              </div>
              <p className="text-sm text-purple-300/70 text-center">
                3 states = <span className="text-white">1.585 bits</span> (58.5% more efficient!)
              </p>
            </div>
          </div>
        </motion.div>

        {/* Why Ternary Matters */}
        <motion.div
          className="mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <h3 className="text-xl font-semibold text-white mb-6 text-center">
            Why Ternary is Revolutionary
          </h3>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { title: 'More Dense', desc: '58.5% more information per unit' },
              { title: 'Uncertainty', desc: 'Can represent "unknown" naturally' },
              { title: 'Reversible', desc: 'All operations can be undone' },
              { title: 'Biological', desc: 'Matches real neuron behavior' },
            ].map((item, index) => (
              <div
                key={index}
                className="p-4 rounded-xl bg-white/5 border border-white/10 text-center"
              >
                <h4 className="font-semibold text-white mb-1">{item.title}</h4>
                <p className="text-xs text-white/50">{item.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Architecture Visualization */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h3 className="text-xl font-semibold text-white mb-6 text-center">
            The 128 x 128 Neural Matrix
          </h3>

          <div className="p-6 rounded-xl bg-white/5 border border-white/10">
            <div className="flex items-center justify-center gap-3 mb-6">
              <Cpu className="w-6 h-6 text-purple-400" />
              <span className="text-lg font-mono text-white">16,384 Neurons</span>
            </div>

            {/* Layer visualization */}
            <div className="space-y-2 max-w-md mx-auto">
              {architectureLayers.map((layer, index) => (
                <motion.div
                  key={index}
                  className={`flex items-center gap-4 p-3 rounded-lg ${layer.color} ${
                    layer.highlight ? 'border border-white/20' : ''
                  }`}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.3, delay: 0.5 + index * 0.05 }}
                >
                  <span className="w-16 text-xs font-mono text-white/60">
                    Row {layer.rows}
                  </span>
                  <div className="flex-1">
                    <span className={`text-sm font-semibold ${layer.highlight ? 'text-white' : 'text-white/80'}`}>
                      {layer.name}
                    </span>
                    {layer.highlight && (
                      <span className="ml-2 text-xs text-cyan-400">
                        {layer.description}
                      </span>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Key insight */}
            <div className="mt-6 p-4 rounded-xl bg-gradient-to-r from-orange-500/10 to-purple-500/10 border border-orange-500/20 text-center">
              <p className="text-sm text-white/70">
                <span className="text-orange-400 font-semibold">Key Discovery:</span>{' '}
                Row 21 is the Bitcoin Input Layer - this is where Bitcoin addresses connect to the Qubic neural network.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Footer note */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <p className="text-sm text-white/40">
            Want to learn more?{' '}
            <a href="/docs/03-results/17-aigarth-architecture" className="text-purple-400 hover:text-purple-300 underline">
              Read the full technical documentation
            </a>
          </p>
        </motion.div>
      </div>
    </section>
  )
}
