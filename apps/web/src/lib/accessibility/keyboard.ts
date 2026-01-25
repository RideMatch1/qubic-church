/**
 * Keyboard Navigation & Shortcuts
 * WCAG 2.1 Keyboard Accessible
 */

export type KeyboardKey =
  | 'Enter'
  | 'Space'
  | 'Escape'
  | 'Tab'
  | 'ArrowUp'
  | 'ArrowDown'
  | 'ArrowLeft'
  | 'ArrowRight'
  | 'Home'
  | 'End'
  | 'PageUp'
  | 'PageDown'

export interface KeyboardShortcut {
  key: string
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
  meta?: boolean
  description: string
  action: () => void
}

/**
 * Keyboard Navigation Manager
 */
export class KeyboardNavigationManager {
  private shortcuts: KeyboardShortcut[] = []
  private enabled: boolean = true

  constructor() {
    this.init()
  }

  private init() {
    document.addEventListener('keydown', this.handleKeyDown.bind(this))
  }

  register(shortcut: KeyboardShortcut) {
    this.shortcuts.push(shortcut)
  }

  unregister(key: string) {
    this.shortcuts = this.shortcuts.filter((s) => s.key !== key)
  }

  enable() {
    this.enabled = true
  }

  disable() {
    this.enabled = false
  }

  private handleKeyDown(e: KeyboardEvent) {
    if (!this.enabled) return

    // Don't trigger shortcuts when typing in inputs
    if (
      e.target instanceof HTMLInputElement ||
      e.target instanceof HTMLTextAreaElement ||
      (e.target as HTMLElement).isContentEditable
    ) {
      return
    }

    const shortcut = this.shortcuts.find((s) => {
      return (
        s.key === e.key &&
        !!s.ctrl === e.ctrlKey &&
        !!s.shift === e.shiftKey &&
        !!s.alt === e.altKey &&
        !!s.meta === e.metaKey
      )
    })

    if (shortcut) {
      e.preventDefault()
      shortcut.action()
    }
  }

  getShortcuts(): KeyboardShortcut[] {
    return [...this.shortcuts]
  }
}

// Global instance
export const globalKeyboardManager = new KeyboardNavigationManager()

/**
 * Handle keyboard navigation in lists/menus
 */
export function handleListNavigation(
  e: KeyboardEvent,
  items: HTMLElement[],
  currentIndex: number,
  onSelect: (index: number) => void,
  options: {
    orientation?: 'vertical' | 'horizontal'
    loop?: boolean
  } = {}
): number | null {
  const { orientation = 'vertical', loop = true } = options

  let newIndex: number | null = null

  switch (e.key) {
    case 'ArrowDown':
      if (orientation === 'vertical') {
        e.preventDefault()
        newIndex = currentIndex + 1
        if (newIndex >= items.length) {
          newIndex = loop ? 0 : items.length - 1
        }
      }
      break

    case 'ArrowUp':
      if (orientation === 'vertical') {
        e.preventDefault()
        newIndex = currentIndex - 1
        if (newIndex < 0) {
          newIndex = loop ? items.length - 1 : 0
        }
      }
      break

    case 'ArrowRight':
      if (orientation === 'horizontal') {
        e.preventDefault()
        newIndex = currentIndex + 1
        if (newIndex >= items.length) {
          newIndex = loop ? 0 : items.length - 1
        }
      }
      break

    case 'ArrowLeft':
      if (orientation === 'horizontal') {
        e.preventDefault()
        newIndex = currentIndex - 1
        if (newIndex < 0) {
          newIndex = loop ? items.length - 1 : 0
        }
      }
      break

    case 'Home':
      e.preventDefault()
      newIndex = 0
      break

    case 'End':
      e.preventDefault()
      newIndex = items.length - 1
      break

    case 'Enter':
    case ' ':
      e.preventDefault()
      onSelect(currentIndex)
      return currentIndex
  }

  if (newIndex !== null && items[newIndex]) {
    items[newIndex]!.focus()
    return newIndex
  }

  return null
}

/**
 * Handle keyboard navigation in tabs
 */
export function handleTabNavigation(
  e: KeyboardEvent,
  tabs: HTMLElement[],
  currentIndex: number,
  onActivate: (index: number) => void
): number | null {
  let newIndex: number | null = null

  switch (e.key) {
    case 'ArrowRight':
    case 'ArrowDown':
      e.preventDefault()
      newIndex = (currentIndex + 1) % tabs.length
      break

    case 'ArrowLeft':
    case 'ArrowUp':
      e.preventDefault()
      newIndex = (currentIndex - 1 + tabs.length) % tabs.length
      break

    case 'Home':
      e.preventDefault()
      newIndex = 0
      break

    case 'End':
      e.preventDefault()
      newIndex = tabs.length - 1
      break
  }

  if (newIndex !== null) {
    tabs[newIndex]!.focus()
    onActivate(newIndex)
    return newIndex
  }

  return null
}

/**
 * Skip Links for keyboard navigation
 */
export function createSkipLinks(targets: Array<{ id: string; label: string }>): HTMLElement {
  const container = document.createElement('div')
  container.className = 'skip-links'
  container.setAttribute('role', 'navigation')
  container.setAttribute('aria-label', 'Skip links')

  targets.forEach((target) => {
    const link = document.createElement('a')
    link.href = `#${target.id}`
    link.textContent = target.label
    link.className = 'skip-link'

    link.addEventListener('click', (e) => {
      e.preventDefault()
      const targetElement = document.getElementById(target.id)
      if (targetElement) {
        targetElement.focus()
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    })

    container.appendChild(link)
  })

  return container
}

/**
 * Roving tabindex for keyboard navigation
 */
export class RovingTabIndex {
  private items: HTMLElement[]
  private currentIndex: number = 0

  constructor(items: HTMLElement[]) {
    this.items = items
    this.init()
  }

  private init() {
    this.items.forEach((item, index) => {
      item.setAttribute('tabindex', index === 0 ? '0' : '-1')
      item.addEventListener('keydown', this.handleKeyDown.bind(this))
      item.addEventListener('focus', () => this.setCurrentIndex(index))
    })
  }

  private handleKeyDown(e: KeyboardEvent) {
    const currentItem = e.currentTarget as HTMLElement
    const index = this.items.indexOf(currentItem)

    let newIndex: number | null = null

    switch (e.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        e.preventDefault()
        newIndex = (index + 1) % this.items.length
        break

      case 'ArrowUp':
      case 'ArrowLeft':
        e.preventDefault()
        newIndex = (index - 1 + this.items.length) % this.items.length
        break

      case 'Home':
        e.preventDefault()
        newIndex = 0
        break

      case 'End':
        e.preventDefault()
        newIndex = this.items.length - 1
        break
    }

    if (newIndex !== null) {
      this.moveFocus(newIndex)
    }
  }

  private moveFocus(newIndex: number) {
    this.items[this.currentIndex]!.setAttribute('tabindex', '-1')
    this.items[newIndex]!.setAttribute('tabindex', '0')
    this.items[newIndex]!.focus()
    this.currentIndex = newIndex
  }

  private setCurrentIndex(index: number) {
    this.currentIndex = index
  }

  destroy() {
    this.items.forEach((item) => {
      item.removeEventListener('keydown', this.handleKeyDown.bind(this))
    })
  }
}

/**
 * React Hook for keyboard shortcuts
 */
import { useEffect } from 'react'

export function useKeyboardShortcut(
  key: string,
  callback: () => void,
  options: {
    ctrl?: boolean
    shift?: boolean
    alt?: boolean
    meta?: boolean
  } = {}
) {
  useEffect(() => {
    const shortcut: KeyboardShortcut = {
      key,
      ...options,
      description: `Shortcut for ${key}`,
      action: callback,
    }

    globalKeyboardManager.register(shortcut)

    return () => {
      globalKeyboardManager.unregister(key)
    }
  }, [key, callback, options])
}

/**
 * React Hook for list navigation
 */
export function useListNavigation(
  items: HTMLElement[],
  initialIndex: number = 0,
  options: {
    orientation?: 'vertical' | 'horizontal'
    loop?: boolean
  } = {}
) {
  const [currentIndex, setCurrentIndex] = React.useState(initialIndex)

  const handleKeyDown = (e: KeyboardEvent) => {
    const newIndex = handleListNavigation(
      e,
      items,
      currentIndex,
      (index) => setCurrentIndex(index),
      options
    )

    if (newIndex !== null) {
      setCurrentIndex(newIndex)
    }
  }

  return { currentIndex, handleKeyDown }
}

import React from 'react'
