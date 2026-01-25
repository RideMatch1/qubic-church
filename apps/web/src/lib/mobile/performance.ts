/**
 * Mobile Performance Optimization Utilities
 */

/**
 * Lazy load images with Intersection Observer
 */
export function lazyLoadImages(selector: string = 'img[data-src]') {
  if (typeof window === 'undefined' || !('IntersectionObserver' in window)) {
    return
  }

  const images = document.querySelectorAll(selector)

  const imageObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement
          const src = img.dataset.src

          if (src) {
            img.src = src
            img.removeAttribute('data-src')
            observer.unobserve(img)
          }
        }
      })
    },
    {
      rootMargin: '50px 0px',
      threshold: 0.01,
    }
  )

  images.forEach((img) => imageObserver.observe(img))
}

/**
 * Virtualization helper for long lists
 */
export interface VirtualListConfig {
  itemHeight: number
  containerHeight: number
  overscan?: number
}

export function calculateVirtualList(
  scrollTop: number,
  totalItems: number,
  config: VirtualListConfig
): {
  startIndex: number
  endIndex: number
  offsetY: number
} {
  const { itemHeight, containerHeight, overscan = 3 } = config

  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan)
  const visibleItems = Math.ceil(containerHeight / itemHeight)
  const endIndex = Math.min(totalItems - 1, startIndex + visibleItems + overscan * 2)

  return {
    startIndex,
    endIndex,
    offsetY: startIndex * itemHeight,
  }
}

/**
 * Reduce motion for users who prefer it
 */
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false

  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * Battery optimization - check battery status
 */
export async function getBatteryStatus(): Promise<{
  charging: boolean
  level: number
  lowBattery: boolean
} | null> {
  if (typeof navigator === 'undefined' || !('getBattery' in navigator)) {
    return null
  }

  try {
    const battery = await (navigator as any).getBattery()

    return {
      charging: battery.charging,
      level: battery.level,
      lowBattery: battery.level < 0.2 && !battery.charging,
    }
  } catch (error) {
    return null
  }
}

/**
 * Network information - adapt quality based on connection
 */
export function getNetworkInfo(): {
  effectiveType: string
  downlink: number
  rtt: number
  saveData: boolean
  slowConnection: boolean
} | null {
  if (typeof navigator === 'undefined' || !('connection' in navigator)) {
    return null
  }

  const connection = (navigator as any).connection

  return {
    effectiveType: connection.effectiveType || 'unknown',
    downlink: connection.downlink || 0,
    rtt: connection.rtt || 0,
    saveData: connection.saveData || false,
    slowConnection: connection.effectiveType === '2g' || connection.effectiveType === 'slow-2g',
  }
}

/**
 * Adaptive loading based on device capabilities
 */
export function shouldLoadHighQuality(): boolean {
  // Check network
  const network = getNetworkInfo()
  if (network?.slowConnection || network?.saveData) {
    return false
  }

  // Check memory (if available)
  if ('deviceMemory' in navigator) {
    const memory = (navigator as any).deviceMemory
    if (memory < 4) {
      return false
    }
  }

  // Check hardware concurrency
  if (navigator.hardwareConcurrency < 4) {
    return false
  }

  return true
}

/**
 * Request Idle Callback wrapper
 */
export function requestIdleCallback(
  callback: () => void,
  options?: { timeout?: number }
): number | NodeJS.Timeout {
  if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
    return (window as any).requestIdleCallback(callback, options)
  }

  // Fallback to setTimeout
  return setTimeout(callback, 1)
}

/**
 * Cancel Idle Callback wrapper
 */
export function cancelIdleCallback(id: number | NodeJS.Timeout) {
  if (typeof window !== 'undefined' && 'cancelIdleCallback' in window) {
    ;(window as any).cancelIdleCallback(id)
  } else if (typeof id === 'number') {
    clearTimeout(id)
  }
}

/**
 * Measure performance
 */
export function measurePerformance(name: string, callback: () => void) {
  if (typeof performance === 'undefined') {
    callback()
    return
  }

  const startMark = `${name}-start`
  const endMark = `${name}-end`

  performance.mark(startMark)
  callback()
  performance.mark(endMark)

  try {
    performance.measure(name, startMark, endMark)
    const measure = performance.getEntriesByName(name)[0]!
    console.log(`[Performance] ${name}: ${measure.duration.toFixed(2)}ms`)
  } catch (error) {
    // Silently fail
  }
}

/**
 * React Hook for performance monitoring
 */
import { useEffect, useRef } from 'react'

export function usePerformanceMonitor(componentName: string) {
  const renderCount = useRef(0)
  const mountTime = useRef<number>(0)

  useEffect(() => {
    mountTime.current = performance.now()

    return () => {
      const unmountTime = performance.now()
      const lifetime = unmountTime - mountTime.current
      console.log(
        `[${componentName}] Lifetime: ${lifetime.toFixed(2)}ms, Renders: ${renderCount.current}`
      )
    }
  }, [componentName])

  useEffect(() => {
    renderCount.current++
  })
}

/**
 * Optimize scroll performance
 */
export function optimizeScroll(
  element: HTMLElement,
  callback: () => void,
  delay: number = 100
) {
  let ticking = false
  let lastScrollTime = 0

  const handleScroll = () => {
    const now = Date.now()
    if (now - lastScrollTime < delay) return

    lastScrollTime = now

    if (!ticking) {
      requestAnimationFrame(() => {
        callback()
        ticking = false
      })
      ticking = true
    }
  }

  element.addEventListener('scroll', handleScroll, { passive: true })

  return () => element.removeEventListener('scroll', handleScroll)
}

/**
 * Preload critical resources
 */
export function preloadResource(url: string, type: 'script' | 'style' | 'image' | 'font') {
  if (typeof document === 'undefined') return

  const link = document.createElement('link')
  link.rel = 'preload'
  link.href = url

  switch (type) {
    case 'script':
      link.as = 'script'
      break
    case 'style':
      link.as = 'style'
      break
    case 'image':
      link.as = 'image'
      break
    case 'font':
      link.as = 'font'
      link.crossOrigin = 'anonymous'
      break
  }

  document.head.appendChild(link)
}
