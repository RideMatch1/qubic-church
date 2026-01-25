/**
 * Touch & Gesture Handler for Mobile Optimization
 * Provides smooth touch interactions and swipe gestures
 */

export interface TouchGesture {
  type: 'swipe' | 'tap' | 'long-press' | 'pinch'
  direction?: 'left' | 'right' | 'up' | 'down'
  distance?: number
  velocity?: number
  scale?: number
  target: HTMLElement
}

export interface TouchConfig {
  swipeThreshold?: number
  velocityThreshold?: number
  longPressDelay?: number
  enablePinch?: boolean
  enableRotate?: boolean
}

/**
 * Touch Handler Class
 * Manages touch events and gesture recognition
 */
export class TouchHandler {
  private element: HTMLElement
  private config: Required<TouchConfig>
  private touchStart: { x: number; y: number; time: number } | null = null
  private longPressTimer: NodeJS.Timeout | null = null
  private initialPinchDistance: number = 0

  constructor(element: HTMLElement, config: TouchConfig = {}) {
    this.element = element
    this.config = {
      swipeThreshold: config.swipeThreshold || 50,
      velocityThreshold: config.velocityThreshold || 0.5,
      longPressDelay: config.longPressDelay || 500,
      enablePinch: config.enablePinch ?? true,
      enableRotate: config.enableRotate ?? false,
    }

    this.init()
  }

  private init() {
    this.element.addEventListener('touchstart', this.handleTouchStart.bind(this), {
      passive: false,
    })
    this.element.addEventListener('touchmove', this.handleTouchMove.bind(this), {
      passive: false,
    })
    this.element.addEventListener('touchend', this.handleTouchEnd.bind(this), {
      passive: false,
    })
  }

  private handleTouchStart(e: TouchEvent) {
    if (e.touches.length === 1) {
      const touch = e.touches[0]!
      this.touchStart = {
        x: touch.clientX,
        y: touch.clientY,
        time: Date.now(),
      }

      // Start long press timer
      this.longPressTimer = setTimeout(() => {
        this.dispatchGesture({
          type: 'long-press',
          target: this.element,
        })
      }, this.config.longPressDelay)
    } else if (e.touches.length === 2 && this.config.enablePinch) {
      // Pinch gesture start
      this.initialPinchDistance = this.getPinchDistance(e.touches[0]!, e.touches[1]!)
    }
  }

  private handleTouchMove(e: TouchEvent) {
    // Cancel long press on move
    if (this.longPressTimer) {
      clearTimeout(this.longPressTimer)
      this.longPressTimer = null
    }

    if (e.touches.length === 2 && this.config.enablePinch) {
      e.preventDefault()
      const currentDistance = this.getPinchDistance(e.touches[0]!, e.touches[1]!)
      const scale = currentDistance / this.initialPinchDistance

      this.dispatchGesture({
        type: 'pinch',
        scale,
        target: this.element,
      })
    }
  }

  private handleTouchEnd(e: TouchEvent) {
    if (this.longPressTimer) {
      clearTimeout(this.longPressTimer)
      this.longPressTimer = null
    }

    if (!this.touchStart) return

    const touch = e.changedTouches[0]!
    const deltaX = touch.clientX - this.touchStart.x
    const deltaY = touch.clientY - this.touchStart.y
    const deltaTime = Date.now() - this.touchStart.time
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
    const velocity = distance / deltaTime

    // Tap detection
    if (distance < 10 && deltaTime < 200) {
      this.dispatchGesture({
        type: 'tap',
        target: this.element,
      })
    }

    // Swipe detection
    if (distance > this.config.swipeThreshold || velocity > this.config.velocityThreshold) {
      const direction = this.getSwipeDirection(deltaX, deltaY)

      this.dispatchGesture({
        type: 'swipe',
        direction,
        distance,
        velocity,
        target: this.element,
      })
    }

    this.touchStart = null
  }

  private getSwipeDirection(deltaX: number, deltaY: number): TouchGesture['direction'] {
    if (Math.abs(deltaX) > Math.abs(deltaY)) {
      return deltaX > 0 ? 'right' : 'left'
    } else {
      return deltaY > 0 ? 'down' : 'up'
    }
  }

  private getPinchDistance(touch1: Touch, touch2: Touch): number {
    const dx = touch1.clientX - touch2.clientX
    const dy = touch1.clientY - touch2.clientY
    return Math.sqrt(dx * dx + dy * dy)
  }

  private dispatchGesture(gesture: TouchGesture) {
    const event = new CustomEvent('gesture', { detail: gesture })
    this.element.dispatchEvent(event)
  }

  destroy() {
    if (this.longPressTimer) {
      clearTimeout(this.longPressTimer)
    }
    // Remove event listeners would go here
  }
}

/**
 * React Hook for Touch Gestures
 */
export function useTouchGestures(
  ref: React.RefObject<HTMLElement>,
  config: TouchConfig = {}
): {
  onGesture: (callback: (gesture: TouchGesture) => void) => void
} {
  const [handler, setHandler] = React.useState<TouchHandler | null>(null)

  React.useEffect(() => {
    if (ref.current) {
      const touchHandler = new TouchHandler(ref.current, config)
      setHandler(touchHandler)

      return () => touchHandler.destroy()
    }
  }, [ref, config])

  const onGesture = React.useCallback(
    (callback: (gesture: TouchGesture) => void) => {
      if (ref.current) {
        ref.current.addEventListener('gesture', ((e: CustomEvent<TouchGesture>) => {
          callback(e.detail)
        }) as EventListener)
      }
    },
    [ref]
  )

  return { onGesture }
}

// For non-React usage
import React from 'react'
