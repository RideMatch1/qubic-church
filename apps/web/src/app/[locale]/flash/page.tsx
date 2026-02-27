'use client'

import { FlashArena } from '@/components/qflash/FlashArena'

export default function FlashPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex-1">
        <FlashArena />
      </main>
    </div>
  )
}
