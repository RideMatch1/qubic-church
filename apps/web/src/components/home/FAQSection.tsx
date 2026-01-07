'use client'

import { motion, useInView, AnimatePresence } from 'framer-motion'
import { useRef, useState } from 'react'
import { ChevronDown, HelpCircle } from 'lucide-react'

interface FAQItemProps {
  question: string
  answer: string
  isOpen: boolean
  onToggle: () => void
  delay: number
}

function FAQItem({ question, answer, isOpen, onToggle, delay }: FAQItemProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  return (
    <motion.div
      ref={ref}
      className="border border-border rounded-lg overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
      transition={{ duration: 0.4, delay }}
    >
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 text-left bg-card/50 hover:bg-card/80 transition-colors"
      >
        <span className="font-medium pr-4">{question}</span>
        <motion.span
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="flex-shrink-0"
        >
          <ChevronDown className="h-5 w-5 text-muted-foreground" />
        </motion.span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="p-4 pt-0 border-t border-border bg-muted/20">
              <p className="text-sm text-muted-foreground leading-relaxed pt-4">
                {answer}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export function FAQSection() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' })
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  const faqs = [
    {
      question: 'What exactly was discovered?',
      answer:
        'A mathematical formula (625,284 = 283 x 47 squared + 137) was found that connects Bitcoin Block #283 to a specific address in the Qubic network. This formula uses prime numbers and the physics constant 137 (fine structure constant) to create a "boot address" that points into Qubic\'s memory architecture. This suggests the two networks were intentionally designed to be connected.',
    },
    {
      question: 'Why is Block #283 significant?',
      answer:
        'Block #283 is one of the earliest Bitcoin blocks, mined in January 2009 during the first days of Bitcoin\'s existence. The number 283 is a prime number, and its appearance in the formula alongside other primes (47) and the fine structure constant (137) creates a mathematical signature that would be nearly impossible to occur by chance.',
    },
    {
      question: 'What is the "fine structure constant" and why does it matter?',
      answer:
        'The fine structure constant (approximately 1/137) is a fundamental constant in physics that describes the strength of electromagnetic interactions. Its appearance in the Bitcoin-Qubic formula is remarkable because it connects a physical constant from nature to a digital mathematical relationship, suggesting deep intentional design.',
    },
    {
      question: 'What is Qubic and how is it different from Bitcoin?',
      answer:
        'Qubic is a distributed computing network that uses ternary logic (three states: -1, 0, 1) instead of binary (two states: 0, 1). While Bitcoin focuses on financial transactions, Qubic runs artificial intelligence computations across a global network of 50,000+ computers. The discovery shows these seemingly different systems share a hidden mathematical foundation.',
    },
    {
      question: 'What happens on March 3, 2026?',
      answer:
        'Analysis of the Qubic network revealed a cryptographic "time-lock" mechanism scheduled to activate on March 3, 2026. Similar to a time-release safe, this mechanism may reveal additional data or functionality that has been encoded into the network since its creation. The exact outcome remains unknown until the date arrives.',
    },
    {
      question: 'Is this verified? How can I check the claims?',
      answer:
        'All claims in this research are verifiable on-chain. You can examine Bitcoin Block #283 on any blockchain explorer, verify the 23,477 Qubic identities through the Qubic network, and reproduce the mathematical calculations yourself. The Matrix Explorer on this site provides interactive tools for verification.',
    },
    {
      question: 'What are the implications if this is true?',
      answer:
        'If the connection is intentional (which the mathematics strongly suggest), it would mean that the creator of Bitcoin (Satoshi Nakamoto) planned for integration with ternary AI computing years before such technology existed publicly. This would represent extraordinary foresight and suggest a multi-decade vision for decentralized computing.',
    },
    {
      question: 'Who conducted this research?',
      answer:
        'This research was conducted by independent researchers analyzing publicly available blockchain data. All methodology, data sources, and verification steps are documented in the full research papers available on this site. The work follows academic standards including the IMRAD structure for scientific documentation.',
    },
    {
      question: 'What is the "Patoshi Pattern" and how does it relate to this discovery?',
      answer:
        'The Patoshi Pattern, identified by researcher Sergio Demian Lerner, refers to a distinctive mining signature attributed to Satoshi Nakamoto in 2009-2010. This pattern spans approximately 22,000 blocks containing roughly 1.1 million BTC that have never been moved. Our research found mathematical references to specific Patoshi block heights encoded within Qubic\'s memory architecture, suggesting a deliberate connection.',
    },
  ]

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index)
  }

  return (
    <section ref={sectionRef} className="py-20 px-4">
      <div className="max-w-3xl mx-auto">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center gap-2 mb-4">
            <HelpCircle className="h-5 w-5 text-primary" />
            <span className="text-sm font-medium text-primary">Common Questions</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-serif font-semibold mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-muted-foreground">
            Answers to common questions about the Bitcoin-Qubic Bridge discovery.
          </p>
        </motion.div>

        <div className="space-y-3">
          {faqs.map((faq, index) => (
            <FAQItem
              key={index}
              question={faq.question}
              answer={faq.answer}
              isOpen={openIndex === index}
              onToggle={() => toggleFAQ(index)}
              delay={index * 0.1}
            />
          ))}
        </div>

        <motion.div
          className="text-center mt-10 space-y-4"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          <p className="text-sm text-muted-foreground">
            Have more questions? Read the full documentation for comprehensive details.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <a
              href="/docs"
              className="inline-flex items-center justify-center px-6 py-3 rounded-lg bg-primary text-primary-foreground font-medium hover:opacity-90 transition-opacity"
            >
              Read Full Documentation
            </a>
            <a
              href="/docs/results/formula-discovery"
              className="inline-flex items-center justify-center px-6 py-3 rounded-lg border border-border hover:bg-muted transition-colors font-medium"
            >
              See the Mathematical Proof
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
