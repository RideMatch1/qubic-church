'use client'

import { useRef, useState, useEffect } from 'react'
import { motion, useInView } from 'framer-motion'
import { PhaseWrapper } from '../shared/PhaseWrapper'
import { CollapsibleSection } from '../shared/CollapsibleSection'
import { SourceCitation, SourceCitationGroup } from '../shared/SourceCitation'
import { Clock, Calendar, AlertCircle, Zap } from 'lucide-react'

// Target dates - exact time from research: 18:15:05 UTC
const MARCH_2026 = new Date('2026-03-03T18:15:05Z')
const APRIL_2027 = new Date('2027-04-13T00:00:00Z')

interface CountdownValues {
  days: number
  hours: number
  minutes: number
  seconds: number
}

function calculateCountdown(targetDate: Date): CountdownValues {
  const now = new Date()
  const diff = targetDate.getTime() - now.getTime()

  if (diff <= 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0 }
  }

  return {
    days: Math.floor(diff / (1000 * 60 * 60 * 24)),
    hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
    minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
    seconds: Math.floor((diff % (1000 * 60)) / 1000),
  }
}

function CountdownDisplay({
  targetDate,
  label,
  variant,
}: {
  targetDate: Date
  label: string
  variant: 'primary' | 'secondary'
}) {
  const [countdown, setCountdown] = useState<CountdownValues>({ days: 0, hours: 0, minutes: 0, seconds: 0 })

  useEffect(() => {
    setCountdown(calculateCountdown(targetDate))

    const interval = setInterval(() => {
      setCountdown(calculateCountdown(targetDate))
    }, 1000)

    return () => clearInterval(interval)
  }, [targetDate])

  const isPrimary = variant === 'primary'

  return (
    <div
      className={`p-6 rounded-2xl ${
        isPrimary
          ? 'bg-gradient-to-b from-orange-950/30 to-purple-950/30 border-2 border-orange-500/30'
          : 'bg-white/5 border border-white/10'
      }`}
    >
      <div className="flex items-center gap-2 mb-4">
        <Calendar className={`w-5 h-5 ${isPrimary ? 'text-orange-400' : 'text-white/60'}`} />
        <span className={`font-medium ${isPrimary ? 'text-orange-400' : 'text-white/70'}`}>
          {label}
        </span>
      </div>

      <div className="grid grid-cols-4 gap-3">
        {[
          { value: countdown.days, label: 'Days' },
          { value: countdown.hours, label: 'Hours' },
          { value: countdown.minutes, label: 'Min' },
          { value: countdown.seconds, label: 'Sec' },
        ].map((item, index) => (
          <div key={index} className="text-center">
            <motion.div
              key={item.value}
              initial={{ scale: 1.1, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className={`text-2xl md:text-3xl font-mono font-bold ${
                isPrimary ? 'text-white' : 'text-white/80'
              }`}
            >
              {item.value.toString().padStart(2, '0')}
            </motion.div>
            <div className="text-xs text-white/40">{item.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function Phase11_TheCountdown() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: false, amount: 0.3 })

  return (
    <PhaseWrapper
      id="countdown"
      phaseNumber={11}
      title="The Countdown"
      subtitle="Key dates referenced in the research"
    >
      <div ref={ref} className="space-y-8">
        {/* Primary Countdown - March 2026 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.5 }}
        >
          <CountdownDisplay
            targetDate={MARCH_2026}
            label="March 3, 2026 - 576th Message Protocol Event"
            variant="primary"
          />
        </motion.div>

        {/* Event Details */}
        <motion.div
          className="p-6 rounded-2xl bg-white/5 border border-white/10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <h3 className="text-lg font-semibold text-white/90 mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-orange-400" />
            What happens on March 3, 2026?
          </h3>

          <div className="space-y-4 text-sm text-white/70">
            <p>According to the decoded GENESIS token binary messages:</p>

            <div className="p-4 rounded-lg bg-black/30 font-mono text-xs border-l-2 border-orange-500/50">
              <p className="text-white/80 italic">
                "The 576th message will be published. It will not be an announcement, but a stage
                of the protocol."
              </p>
              <p className="text-white/80 italic mt-2">
                "The signal will begin 6,268 time units counted from point zero."
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4 mt-4">
              <div className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
                <div className="text-xs text-orange-400 mb-1">576th Message</div>
                <div className="text-white/80">SWIFT MT576 = "Statement of Open Orders"</div>
              </div>
              <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/20">
                <div className="text-xs text-purple-400 mb-1">6,268 Days from Genesis</div>
                <div className="text-white/80">Jan 3, 2009 + 6,268 = March 3, 2026</div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Secondary Countdown - April 2027 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <CountdownDisplay
            targetDate={APRIL_2027}
            label="April 13, 2027 - Phase 6 Event"
            variant="secondary"
          />
        </motion.div>

        {/* Warning */}
        <motion.div
          className="p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/20 flex items-start gap-3"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <AlertCircle className="w-5 h-5 text-yellow-400 shrink-0 mt-0.5" />
          <div className="text-sm text-white/70">
            <strong className="text-yellow-400">Important:</strong> These dates are derived from our
            interpretation of encoded messages. They are{' '}
            <span className="text-yellow-400">Tier 3 hypotheses</span>, not verified facts. Nothing
            may happen. Do not make financial decisions based on these dates.
          </div>
        </motion.div>

        <CollapsibleSection
          title="The 676 Pattern"
          icon={<Clock className="w-4 h-4" />}
          badge="Technical"
        >
          <div className="space-y-3 text-sm text-white/70">
            <p>
              The number <span className="text-purple-400 font-bold">676</span> (26^2) appears
              throughout the protocol:
            </p>
            <ul className="space-y-1 ml-4 list-disc">
              <li>676 Qubic Computors validate the network</li>
              <li>GENESIS max supply = 676 billion</li>
              <li>Top 676 token holders referenced for distribution</li>
              <li>Bitcoin blocks 1-676 (early Satoshi era)</li>
              <li>676 = standard Qubic IPO share size</li>
            </ul>
            <p className="text-white/50 italic">26 = alphabet size (communication theme)</p>
          </div>
        </CollapsibleSection>

        <SourceCitationGroup>
          <SourceCitation
            href="/docs/03-results/05-time-lock"
            title="Time-Lock Analysis"
            tier={3}
          />
          <SourceCitation
            href="/docs/03-results/28-mt576-genesis-connection"
            title="MT576 Connection"
            tier={2}
          />
        </SourceCitationGroup>
      </div>
    </PhaseWrapper>
  )
}
