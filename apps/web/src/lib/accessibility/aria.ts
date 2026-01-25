/**
 * ARIA (Accessible Rich Internet Applications) Utilities
 * WCAG 2.1 Level AA Compliance
 */

export interface AriaAttributes {
  'aria-label'?: string
  'aria-labelledby'?: string
  'aria-describedby'?: string
  'aria-expanded'?: boolean
  'aria-hidden'?: boolean
  'aria-live'?: 'polite' | 'assertive' | 'off'
  'aria-busy'?: boolean
  'aria-checked'?: boolean | 'mixed'
  'aria-disabled'?: boolean
  'aria-invalid'?: boolean
  'aria-required'?: boolean
  'aria-selected'?: boolean
  'aria-controls'?: string
  'aria-haspopup'?: boolean | 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog'
  'aria-pressed'?: boolean | 'mixed'
  'aria-current'?: boolean | 'page' | 'step' | 'location' | 'date' | 'time'
  role?: string
}

/**
 * Generate ARIA attributes for common UI patterns
 */
export function generateAriaAttributes(
  type: 'button' | 'link' | 'tab' | 'modal' | 'tooltip' | 'menu' | 'table',
  options: Partial<AriaAttributes> = {}
): AriaAttributes {
  const base: AriaAttributes = {}

  switch (type) {
    case 'button':
      base.role = 'button'
      if (options['aria-pressed'] !== undefined) {
        base['aria-pressed'] = options['aria-pressed']
      }
      break

    case 'link':
      base.role = 'link'
      break

    case 'tab':
      base.role = 'tab'
      base['aria-selected'] = options['aria-selected'] ?? false
      base['aria-controls'] = options['aria-controls']
      break

    case 'modal':
      base.role = 'dialog'
      ;(base as any)['aria-modal'] = true
      base['aria-labelledby'] = options['aria-labelledby']
      base['aria-describedby'] = options['aria-describedby']
      break

    case 'tooltip':
      base.role = 'tooltip'
      base['aria-hidden'] = options['aria-hidden'] ?? false
      break

    case 'menu':
      base.role = 'menu'
      ;(base as any)['aria-orientation'] = 'vertical'
      break

    case 'table':
      base.role = 'table'
      base['aria-labelledby'] = options['aria-labelledby']
      break
  }

  return { ...base, ...options }
}

/**
 * Announce message to screen readers
 */
export function announceToScreenReader(
  message: string,
  priority: 'polite' | 'assertive' = 'polite',
  timeout: number = 5000
) {
  if (typeof document === 'undefined') return

  const announcement = document.createElement('div')
  announcement.setAttribute('role', 'status')
  announcement.setAttribute('aria-live', priority)
  announcement.setAttribute('aria-atomic', 'true')
  announcement.className = 'sr-only' // Visually hidden
  announcement.textContent = message

  document.body.appendChild(announcement)

  setTimeout(() => {
    document.body.removeChild(announcement)
  }, timeout)
}

/**
 * Create visually hidden but screen reader accessible element
 */
export function createSROnlyElement(text: string): HTMLElement {
  const element = document.createElement('span')
  element.className = 'sr-only'
  element.textContent = text

  // Inline styles for reliability
  element.style.position = 'absolute'
  element.style.width = '1px'
  element.style.height = '1px'
  element.style.padding = '0'
  element.style.margin = '-1px'
  element.style.overflow = 'hidden'
  element.style.clip = 'rect(0, 0, 0, 0)'
  element.style.whiteSpace = 'nowrap'
  element.style.border = '0'

  return element
}

/**
 * Manage focus trap for modals
 */
export class FocusTrap {
  private element: HTMLElement
  private firstFocusableElement: HTMLElement | null = null
  private lastFocusableElement: HTMLElement | null = null
  private previouslyFocusedElement: HTMLElement | null = null

  constructor(element: HTMLElement) {
    this.element = element
    this.updateFocusableElements()
  }

  activate() {
    this.previouslyFocusedElement = document.activeElement as HTMLElement
    this.updateFocusableElements()

    if (this.firstFocusableElement) {
      this.firstFocusableElement.focus()
    }

    this.element.addEventListener('keydown', this.handleKeyDown.bind(this))
  }

  deactivate() {
    this.element.removeEventListener('keydown', this.handleKeyDown.bind(this))

    if (this.previouslyFocusedElement) {
      this.previouslyFocusedElement.focus()
    }
  }

  private updateFocusableElements() {
    const focusableSelectors = [
      'a[href]',
      'button:not([disabled])',
      'textarea:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
    ]

    const focusableElements = this.element.querySelectorAll<HTMLElement>(
      focusableSelectors.join(', ')
    )

    this.firstFocusableElement = focusableElements[0] || null
    this.lastFocusableElement =
      focusableElements[focusableElements.length - 1] || null
  }

  private handleKeyDown(e: KeyboardEvent) {
    if (e.key !== 'Tab') return

    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === this.firstFocusableElement) {
        e.preventDefault()
        this.lastFocusableElement?.focus()
      }
    } else {
      // Tab
      if (document.activeElement === this.lastFocusableElement) {
        e.preventDefault()
        this.firstFocusableElement?.focus()
      }
    }
  }
}

/**
 * Check if element is focusable
 */
export function isFocusable(element: HTMLElement): boolean {
  if (element.hasAttribute('disabled')) return false
  if (element.hasAttribute('hidden')) return false
  if (element.getAttribute('tabindex') === '-1') return false

  const tagName = element.tagName.toLowerCase()
  if (['a', 'button', 'input', 'textarea', 'select'].includes(tagName)) {
    return true
  }

  return element.hasAttribute('tabindex')
}

/**
 * Get all focusable elements within a container
 */
export function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const selectors = [
    'a[href]',
    'button:not([disabled])',
    'textarea:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ]

  return Array.from(container.querySelectorAll<HTMLElement>(selectors.join(', '))).filter(
    isFocusable
  )
}

/**
 * React Hook for ARIA live regions
 */
import { useEffect, useRef } from 'react'

export function useAriaLive(message: string | null, priority: 'polite' | 'assertive' = 'polite') {
  const liveRegionRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (message && liveRegionRef.current) {
      liveRegionRef.current.textContent = message
    }
  }, [message])

  const liveRegionProps = {
    ref: liveRegionRef,
    role: 'status',
    'aria-live': priority,
    'aria-atomic': 'true',
    className: 'sr-only',
  }

  return liveRegionProps
}

/**
 * React Hook for focus trap
 */
export function useFocusTrap(active: boolean, containerRef: React.RefObject<HTMLElement>) {
  useEffect(() => {
    if (!active || !containerRef.current) return

    const trap = new FocusTrap(containerRef.current)
    trap.activate()

    return () => trap.deactivate()
  }, [active, containerRef])
}

/**
 * Generate unique ID for ARIA relationships
 */
let idCounter = 0

export function generateId(prefix: string = 'a11y'): string {
  return `${prefix}-${++idCounter}-${Date.now()}`
}
