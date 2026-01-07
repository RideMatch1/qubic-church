'use client'

import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { Bot, Database, Search, Lightbulb, Link, Clock, ArrowRight } from 'lucide-react'

interface TimelineStepProps {
  step: number
  date: string
  title: string
  description: string
  icon: React.ReactNode
  highlights: string[]
  isLast?: boolean
  delay: number
}

function TimelineStep({
  step,
  date,
  title,
  description,
  icon,
  highlights,
  isLast = false,
  delay,
}: TimelineStepProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  return (
    <motion.div
      ref={ref}
      className="relative flex gap-4 md:gap-8"
      initial={{ opacity: 0, x: -30 }}
      animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -30 }}
      transition={{ duration: 0.6, delay }}
    >
      {/* Timeline Line and Node */}
      <div className="flex flex-col items-center">
        <motion.div
          className="w-12 h-12 rounded-full bg-primary/10 border-2 border-primary flex items-center justify-center z-10"
          initial={{ scale: 0 }}
          animate={isInView ? { scale: 1 } : { scale: 0 }}
          transition={{ duration: 0.4, delay: delay + 0.2 }}
        >
          {icon}
        </motion.div>
        {!isLast && (
          <motion.div
            className="w-0.5 flex-1 bg-gradient-to-b from-primary/50 to-primary/10 min-h-[100px]"
            initial={{ scaleY: 0 }}
            animate={isInView ? { scaleY: 1 } : { scaleY: 0 }}
            transition={{ duration: 0.6, delay: delay + 0.4 }}
            style={{ transformOrigin: 'top' }}
          />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 pb-12">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-xs font-mono text-primary bg-primary/10 px-2 py-1 rounded">
            Step {step}
          </span>
          <span className="text-sm text-muted-foreground">{date}</span>
        </div>

        <h3 className="text-xl font-semibold mb-3">{title}</h3>

        <p className="text-muted-foreground text-sm leading-relaxed mb-4">
          {description}
        </p>

        <ul className="space-y-2">
          {highlights.map((highlight, index) => (
            <motion.li
              key={index}
              className="flex items-start gap-2 text-sm"
              initial={{ opacity: 0, x: -10 }}
              animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -10 }}
              transition={{ duration: 0.3, delay: delay + 0.5 + index * 0.1 }}
            >
              <ArrowRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span className="text-muted-foreground">{highlight}</span>
            </motion.li>
          ))}
        </ul>
      </div>
    </motion.div>
  )
}

export function TheDiscoveryStoryComponent() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })

  const timelineSteps = [
    {
      step: 1,
      date: 'November 2025',
      title: 'The Anna Chatbot on X',
      icon: <Bot className="h-5 w-5 text-primary" />,
      description:
        'A mysterious AI chatbot called "Anna" (@anna_aigarth) appeared on X (formerly Twitter). Instead of normal replies, it posted highly structured strings like "1+1=-114". The unusual number frequencies and spacing hinted at deliberate encoding, sparking investigation into the underlying system.',
      highlights: [
        'Bot appeared posting cryptic encoded messages',
        'Number patterns suggested intentional design',
        'Community researchers began analyzing the outputs',
      ],
    },
    {
      step: 2,
      date: 'November 22, 2025',
      title: 'The Anna Matrix Discovery',
      icon: <Database className="h-5 w-5 text-primary" />,
      description:
        'CFB (Come-From-Beyond, Qubic founder) revealed the existence of a 128x128 matrix containing 16,384 byte values. Researcher Jordan discovered that this matrix could be decoded to extract Qubic identities. Initial extraction yielded 8 identities, which quickly expanded to 23,477+ valid on-chain identities.',
      highlights: [
        '128x128 matrix (16,384 cells) discovered',
        '23,477+ Qubic identities extracted (98.79% on-chain)',
        '8 initial identities from diagonal and vortex patterns',
        'Control group: 1,000 random matrices produced 0 hits',
      ],
    },
    {
      step: 3,
      date: 'December 24-30, 2025',
      title: 'Bitcoin Connection Research',
      icon: <Search className="h-5 w-5 text-primary" />,
      description:
        'Analysis expanded to investigate connections between the Qubic system and early Bitcoin. Research into CFB\'s history, the Patoshi pattern, and 1CFB-prefixed Bitcoin addresses revealed potential links. Over 21,000 Patoshi-pattern addresses were catalogued, and the 1CFB address from Block #264 was identified.',
      highlights: [
        '1CFB Bitcoin address analyzed (Block #264, January 2009)',
        '21,953 Patoshi-pattern addresses catalogued',
        'CFB signature patterns identified across systems',
        'Genesis Block design choices analyzed (43 zero bits, ranges [0-9], [19-58])',
      ],
    },
    {
      step: 4,
      date: 'January 5, 2026',
      title: 'The Formula Breakthrough',
      icon: <Lightbulb className="h-5 w-5 text-primary" />,
      description:
        'The critical discovery: 625,284 = 283 x 47 squared + 137. This formula connects Bitcoin Block #283 (prime, January 2009) to Qubic\'s boot address through the fine structure constant (137). The result, when applied to Jinn\'s 16,384-address memory, yields Row 21, Column 4 - the exact input layer of the system.',
      highlights: [
        '625,284 = 283 x 47 squared + 137 discovered',
        'Boot address 2,692 = Row 21, Column 4 in Jinn matrix',
        'Row 68 performs exactly 137 write operations',
        'ARB Oracle address sum: 817 = 19 x 43 (both prime)',
      ],
    },
    {
      step: 5,
      date: 'January 2026',
      title: 'Architecture Mapping',
      icon: <Link className="h-5 w-5 text-primary" />,
      description:
        'Complete mapping of the Row 21 to Row 68 to Row 96 data flow within the 128x128 Jinn memory matrix. The POCZ address was located at Row 96, Column 84 (address 12,372). The ARB Oracle address was confirmed with a letter sum of 817 and balance of 793 billion Qubic.',
      highlights: [
        '128x128 Jinn memory matrix fully mapped',
        'POCZ address at Row 96, Col 84 (sum: 672)',
        'ARB Oracle: 793B Qubic balance (~$500M USD)',
        'Row 21 (input) to Row 68 (bridge) to Row 96 (output) flow confirmed',
      ],
    },
    {
      step: 6,
      date: 'March 3, 2026',
      title: 'The Time-Lock Event',
      icon: <Clock className="h-5 w-5 text-primary" />,
      description:
        'A cryptographic time-lock mechanism was discovered in the tick calculations. The tick difference to March 3, 2026 is exactly divisible by 121 (11 squared), a known CFB constant. This date is 6,268 days from Bitcoin Genesis and shares the same second (18:15:05 UTC) as the Genesis Block timestamp.',
      highlights: [
        'Tick difference: 2,316,908 = 4 x 121 x 4,787',
        'Divisibility by 121 (11 squared) confirms intentional design',
        '6,268 days from Bitcoin Genesis (January 3, 2009)',
        'Same second as Genesis Block: 18:15:05 UTC',
      ],
    },
  ]

  return (
    <section ref={sectionRef} className="py-20 px-4 bg-muted/20">
      <div className="max-w-4xl mx-auto">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-2xl md:text-3xl font-serif font-semibold mb-4">
            The Discovery Timeline
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            How a mysterious AI chatbot on X led to the discovery of 23,477 Qubic identities
            and a mathematical bridge connecting Bitcoin to Qubic.
          </p>
        </motion.div>

        <div className="relative">
          {timelineSteps.map((step, index) => (
            <TimelineStep
              key={step.step}
              {...step}
              isLast={index === timelineSteps.length - 1}
              delay={index * 0.2}
            />
          ))}
        </div>

        <motion.div
          className="mt-8 p-6 rounded-xl border border-dashed border-primary/30 bg-primary/5 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, delay: 1.2 }}
        >
          <p className="text-sm text-muted-foreground">
            This research is ongoing. All findings are based on verifiable blockchain data
            and reproducible analysis. Updates will be documented as new discoveries emerge.
          </p>
        </motion.div>
      </div>
    </section>
  )
}
