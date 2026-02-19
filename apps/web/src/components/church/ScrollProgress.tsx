'use client'

/**
 * ScrollProgress - Subtle scroll progress indicator at the top of the page
 * Thin amber line that fills as user scrolls down
 */

import { motion, useScroll, useSpring } from 'framer-motion'

export function ScrollProgress() {
  const { scrollYProgress } = useScroll()
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  })

  return (
    <motion.div
      className="fixed top-0 left-0 right-0 h-[2px] bg-[#D4AF37]/60 z-[9999] origin-left"
      style={{ scaleX }}
    />
  )
}
