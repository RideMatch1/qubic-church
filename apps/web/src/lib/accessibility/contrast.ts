/**
 * Color Contrast & Visual Accessibility
 * WCAG 2.1 Contrast Requirements
 */

export interface ContrastRatio {
  ratio: number
  passesAA: boolean
  passesAAA: boolean
  level: 'AA' | 'AAA' | 'FAIL'
}

/**
 * Calculate relative luminance of a color
 */
function getRelativeLuminance(rgb: { r: number; g: number; b: number }): number {
  const sRGB = [rgb.r / 255, rgb.g / 255, rgb.b / 255]

  const linearRGB = sRGB.map((val) => {
    if (val <= 0.03928) {
      return val / 12.92
    }
    return Math.pow((val + 0.055) / 1.055, 2.4)
  })

  return 0.2126 * linearRGB[0]! + 0.7152 * linearRGB[1]! + 0.0722 * linearRGB[2]!
}

/**
 * Parse hex color to RGB
 */
function hexToRGB(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)

  return result
    ? {
        r: parseInt(result[1]!, 16),
        g: parseInt(result[2]!, 16),
        b: parseInt(result[3]!, 16),
      }
    : null
}

/**
 * Calculate contrast ratio between two colors
 */
export function calculateContrastRatio(color1: string, color2: string): number {
  const rgb1 = hexToRGB(color1)
  const rgb2 = hexToRGB(color2)

  if (!rgb1 || !rgb2) return 0

  const l1 = getRelativeLuminance(rgb1)
  const l2 = getRelativeLuminance(rgb2)

  const lighter = Math.max(l1, l2)
  const darker = Math.min(l1, l2)

  return (lighter + 0.05) / (darker + 0.05)
}

/**
 * Check if contrast ratio meets WCAG standards
 */
export function checkContrast(
  foreground: string,
  background: string,
  textSize: 'normal' | 'large' = 'normal'
): ContrastRatio {
  const ratio = calculateContrastRatio(foreground, background)

  // WCAG 2.1 Level AA: 4.5:1 for normal text, 3:1 for large text
  // WCAG 2.1 Level AAA: 7:1 for normal text, 4.5:1 for large text
  const aaThreshold = textSize === 'large' ? 3 : 4.5
  const aaaThreshold = textSize === 'large' ? 4.5 : 7

  return {
    ratio,
    passesAA: ratio >= aaThreshold,
    passesAAA: ratio >= aaaThreshold,
    level: ratio >= aaaThreshold ? 'AAA' : ratio >= aaThreshold ? 'AA' : 'FAIL',
  }
}

/**
 * Suggest accessible color based on contrast requirements
 */
export function suggestAccessibleColor(
  background: string,
  targetRatio: number = 4.5
): string {
  const bgRGB = hexToRGB(background)
  if (!bgRGB) return '#000000'

  const bgLuminance = getRelativeLuminance(bgRGB)

  // Try white first
  const whiteRatio = (1 + 0.05) / (bgLuminance + 0.05)
  if (whiteRatio >= targetRatio) {
    return '#FFFFFF'
  }

  // Try black
  const blackRatio = (bgLuminance + 0.05) / (0 + 0.05)
  if (blackRatio >= targetRatio) {
    return '#000000'
  }

  // If neither works, return the better option
  return whiteRatio > blackRatio ? '#FFFFFF' : '#000000'
}

/**
 * Check if color scheme is high contrast
 */
export function detectHighContrastMode(): boolean {
  if (typeof window === 'undefined') return false

  return (
    window.matchMedia('(prefers-contrast: high)').matches ||
    window.matchMedia('(-ms-high-contrast: active)').matches
  )
}

/**
 * Check color blindness simulation
 */
export function simulateColorBlindness(
  hex: string,
  type: 'protanopia' | 'deuteranopia' | 'tritanopia'
): string {
  const rgb = hexToRGB(hex)
  if (!rgb) return hex

  let r = rgb.r
  let g = rgb.g
  let b = rgb.b

  // Simplified color blindness simulation matrices
  switch (type) {
    case 'protanopia': // Red-blind
      r = 0.567 * r + 0.433 * g
      g = 0.558 * r + 0.442 * g
      b = 0.242 * g + 0.758 * b
      break

    case 'deuteranopia': // Green-blind
      r = 0.625 * r + 0.375 * g
      g = 0.7 * r + 0.3 * g
      b = 0.3 * g + 0.7 * b
      break

    case 'tritanopia': // Blue-blind
      r = 0.95 * r + 0.05 * g
      g = 0.433 * g + 0.567 * b
      b = 0.475 * g + 0.525 * b
      break
  }

  // Clamp values
  r = Math.round(Math.max(0, Math.min(255, r)))
  g = Math.round(Math.max(0, Math.min(255, g)))
  b = Math.round(Math.max(0, Math.min(255, b)))

  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

/**
 * Generate accessible color palette
 */
export function generateAccessiblePalette(
  baseColor: string,
  background: string = '#FFFFFF'
): string[] {
  const palette: string[] = []
  const baseRGB = hexToRGB(baseColor)

  if (!baseRGB) return [baseColor]

  // Generate shades that meet contrast requirements
  for (let i = 0; i < 5; i++) {
    const factor = 0.2 + i * 0.2 // 0.2, 0.4, 0.6, 0.8, 1.0

    const r = Math.round(baseRGB.r * factor)
    const g = Math.round(baseRGB.g * factor)
    const b = Math.round(baseRGB.b * factor)

    const color = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`

    const contrast = checkContrast(color, background)
    if (contrast.passesAA) {
      palette.push(color)
    }
  }

  return palette
}

/**
 * React Hook for contrast checking
 */
import { useState, useEffect } from 'react'

export function useContrastChecker(foreground: string, background: string) {
  const [contrast, setContrast] = useState<ContrastRatio>({
    ratio: 0,
    passesAA: false,
    passesAAA: false,
    level: 'FAIL',
  })

  useEffect(() => {
    const result = checkContrast(foreground, background)
    setContrast(result)
  }, [foreground, background])

  return contrast
}

/**
 * React Hook for high contrast mode detection
 */
export function useHighContrastMode(): boolean {
  const [highContrast, setHighContrast] = useState(false)

  useEffect(() => {
    const checkContrast = () => setHighContrast(detectHighContrastMode())

    checkContrast()

    const mediaQuery = window.matchMedia('(prefers-contrast: high)')
    mediaQuery.addEventListener('change', checkContrast)

    return () => mediaQuery.removeEventListener('change', checkContrast)
  }, [])

  return highContrast
}
