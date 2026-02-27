'use client'

import { useState } from 'react'
import { NavigationWheel } from '@/components/church/navigation'

export function ImmersionButton() {
  const [wheelOpen, setWheelOpen] = useState(false)

  return (
    <>
      <button
        onClick={() => setWheelOpen(true)}
        className="px-4 py-1.5 border border-[#D4AF37]/40 text-[#D4AF37] text-[10px] md:text-xs
                   uppercase tracking-[0.2em] font-medium
                   hover:bg-[#D4AF37]/10 hover:border-[#D4AF37]/70
                   transition-all duration-300 backdrop-blur-sm mr-4"
      >
        Start Immersion &#9662;
      </button>

      <NavigationWheel
        isOpen={wheelOpen}
        onClose={() => setWheelOpen(false)}
      />
    </>
  )
}
