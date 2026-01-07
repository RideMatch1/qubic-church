import type { Variants, Transition } from 'framer-motion'

// ============================================
// BASIC ENTRANCE ANIMATIONS
// ============================================

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
}

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

export const fadeInDown: Variants = {
  hidden: { opacity: 0, y: -20 },
  visible: { opacity: 1, y: 0 },
}

export const fadeInLeft: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 },
}

export const fadeInRight: Variants = {
  hidden: { opacity: 0, x: 20 },
  visible: { opacity: 1, x: 0 },
}

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { opacity: 1, scale: 1 },
}

// ============================================
// CARD INTERACTIONS
// ============================================

export const cardHover: Variants = {
  rest: {
    y: 0,
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
  },
  hover: {
    y: -4,
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -6px rgba(0, 0, 0, 0.1)',
  },
}

export const cardTap: Variants = {
  rest: { scale: 1 },
  tap: { scale: 0.97 },
}

// ============================================
// CELEBRATION ANIMATIONS
// ============================================

export const celebrationBurst: Variants = {
  hidden: { scale: 0, opacity: 0 },
  visible: {
    scale: [0, 1.2, 1],
    opacity: [0, 1, 1],
    transition: {
      duration: 0.5,
      ease: 'easeOut',
    },
  },
}

export const celebrationPulse: Variants = {
  hidden: { scale: 1 },
  visible: {
    scale: [1, 1.05, 1],
    transition: {
      duration: 0.3,
      repeat: 2,
    },
  },
}

export const confettiBurst: Variants = {
  hidden: { scale: 0, rotate: 0 },
  visible: (i: number) => ({
    scale: [0, 1, 0],
    rotate: [0, 360 * (i % 2 === 0 ? 1 : -1)],
    x: [0, (i - 5) * 30],
    y: [0, -100, 200],
    transition: {
      duration: 1.5,
      delay: i * 0.05,
      ease: 'easeOut',
    },
  }),
}

// ============================================
// STAGGER CONTAINERS
// ============================================

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
}

export const staggerContainerFast: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
}

// ============================================
// PROGRESS ANIMATIONS
// ============================================

export const progressFill: Variants = {
  hidden: { scaleX: 0, originX: 0 },
  visible: (progress: number) => ({
    scaleX: progress,
    transition: {
      duration: 1,
      ease: 'easeOut',
    },
  }),
}

export const progressRing: Variants = {
  hidden: { pathLength: 0 },
  visible: (progress: number) => ({
    pathLength: progress,
    transition: {
      duration: 1.5,
      ease: 'easeOut',
    },
  }),
}

// ============================================
// NUMBER ANIMATIONS
// ============================================

export const numberPop: Variants = {
  hidden: { scale: 1 },
  visible: {
    scale: [1, 1.2, 1],
    transition: {
      duration: 0.3,
    },
  },
}

// ============================================
// BADGE ANIMATIONS
// ============================================

export const badgeAppear: Variants = {
  hidden: { scale: 0, opacity: 0 },
  visible: {
    scale: 1,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 15,
    },
  },
}

export const badgeGlow: Variants = {
  rest: {
    boxShadow: '0 0 0px rgba(34, 197, 94, 0)',
  },
  glow: {
    boxShadow: [
      '0 0 0px rgba(34, 197, 94, 0)',
      '0 0 20px rgba(34, 197, 94, 0.5)',
      '0 0 0px rgba(34, 197, 94, 0)',
    ],
    transition: {
      duration: 2,
      repeat: Infinity,
    },
  },
}

// ============================================
// TOOLTIP ANIMATIONS
// ============================================

export const tooltipEnter: Variants = {
  hidden: { opacity: 0, y: 5, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.15,
      ease: 'easeOut',
    },
  },
  exit: {
    opacity: 0,
    y: 5,
    scale: 0.95,
    transition: {
      duration: 0.1,
    },
  },
}

// ============================================
// MODAL ANIMATIONS
// ============================================

export const modalOverlay: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.2 },
  },
  exit: {
    opacity: 0,
    transition: { duration: 0.15 },
  },
}

export const modalContent: Variants = {
  hidden: { opacity: 0, scale: 0.95, y: 10 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 25,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 10,
    transition: { duration: 0.15 },
  },
}

// ============================================
// DEFAULT TRANSITIONS
// ============================================

export const defaultTransition: Transition = {
  duration: 0.3,
  ease: 'easeOut',
}

export const springTransition: Transition = {
  type: 'spring',
  stiffness: 300,
  damping: 25,
}

export const smoothTransition: Transition = {
  duration: 0.5,
  ease: [0.25, 0.1, 0.25, 1],
}

// ============================================
// REDUCED MOTION FALLBACKS
// ============================================

export const reducedMotionFade: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.01 },
  },
}

/**
 * Helper to get motion-safe variants
 */
export function getMotionSafeVariants(
  variants: Variants,
  prefersReducedMotion: boolean
): Variants {
  if (prefersReducedMotion) {
    return reducedMotionFade
  }
  return variants
}
