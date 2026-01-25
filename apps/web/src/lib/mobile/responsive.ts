/**
 * Responsive Utilities & Breakpoint Management
 */

export const breakpoints = {
  xs: 320,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const

export type Breakpoint = keyof typeof breakpoints

/**
 * Check if current viewport matches breakpoint
 */
export function isBreakpoint(breakpoint: Breakpoint): boolean {
  if (typeof window === 'undefined') return false
  return window.innerWidth >= breakpoints[breakpoint]
}

/**
 * Get current breakpoint
 */
export function getCurrentBreakpoint(): Breakpoint {
  if (typeof window === 'undefined') return 'lg'

  const width = window.innerWidth

  if (width >= breakpoints['2xl']) return '2xl'
  if (width >= breakpoints.xl) return 'xl'
  if (width >= breakpoints.lg) return 'lg'
  if (width >= breakpoints.md) return 'md'
  if (width >= breakpoints.sm) return 'sm'
  return 'xs'
}

/**
 * Check if device is mobile
 */
export function isMobile(): boolean {
  if (typeof window === 'undefined') return false

  return (
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    ) || window.innerWidth < breakpoints.md
  )
}

/**
 * Check if device is tablet
 */
export function isTablet(): boolean {
  if (typeof window === 'undefined') return false

  return (
    /iPad|Android/i.test(navigator.userAgent) &&
    window.innerWidth >= breakpoints.md &&
    window.innerWidth < breakpoints.lg
  )
}

/**
 * Check if device is desktop
 */
export function isDesktop(): boolean {
  return !isMobile() && !isTablet()
}

/**
 * Check if device supports touch
 */
export function isTouchDevice(): boolean {
  if (typeof window === 'undefined') return false

  return (
    'ontouchstart' in window ||
    navigator.maxTouchPoints > 0 ||
    (navigator as any).msMaxTouchPoints > 0
  )
}

/**
 * Get optimal column count based on viewport
 */
export function getOptimalColumns(maxColumns: number = 4): number {
  const breakpoint = getCurrentBreakpoint()

  switch (breakpoint) {
    case 'xs':
      return 1
    case 'sm':
      return Math.min(2, maxColumns)
    case 'md':
      return Math.min(2, maxColumns)
    case 'lg':
      return Math.min(3, maxColumns)
    case 'xl':
    case '2xl':
      return maxColumns
    default:
      return maxColumns
  }
}

/**
 * Get optimal font size scale
 */
export function getFontScale(): number {
  if (!isMobile()) return 1

  const width = typeof window !== 'undefined' ? window.innerWidth : 375
  const baseWidth = 375 // iPhone width
  return Math.min(1, width / baseWidth)
}

/**
 * Debounce function for resize handlers
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }

    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Throttle function for scroll handlers
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

/**
 * React Hook for responsive breakpoints
 */
import { useState, useEffect } from 'react'

export function useBreakpoint(): Breakpoint {
  const [breakpoint, setBreakpoint] = useState<Breakpoint>('lg')

  useEffect(() => {
    const handleResize = debounce(() => {
      setBreakpoint(getCurrentBreakpoint())
    }, 150)

    // Initial set
    setBreakpoint(getCurrentBreakpoint())

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return breakpoint
}

/**
 * React Hook for mobile detection
 */
export function useIsMobile(): boolean {
  const [mobile, setMobile] = useState(false)

  useEffect(() => {
    const handleResize = debounce(() => {
      setMobile(isMobile())
    }, 150)

    setMobile(isMobile())

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return mobile
}

/**
 * React Hook for touch device detection
 */
export function useIsTouchDevice(): boolean {
  const [touch, setTouch] = useState(false)

  useEffect(() => {
    setTouch(isTouchDevice())
  }, [])

  return touch
}

/**
 * Viewport utilities
 */
export function getViewportSize(): { width: number; height: number } {
  if (typeof window === 'undefined') {
    return { width: 1024, height: 768 }
  }

  return {
    width: window.innerWidth,
    height: window.innerHeight,
  }
}

/**
 * Safe area insets for mobile devices (notch, home indicator)
 */
export function getSafeAreaInsets(): {
  top: number
  right: number
  bottom: number
  left: number
} {
  if (typeof window === 'undefined' || typeof getComputedStyle === 'undefined') {
    return { top: 0, right: 0, bottom: 0, left: 0 }
  }

  const style = getComputedStyle(document.documentElement)

  return {
    top: parseInt(style.getPropertyValue('--safe-area-inset-top') || '0'),
    right: parseInt(style.getPropertyValue('--safe-area-inset-right') || '0'),
    bottom: parseInt(style.getPropertyValue('--safe-area-inset-bottom') || '0'),
    left: parseInt(style.getPropertyValue('--safe-area-inset-left') || '0'),
  }
}
