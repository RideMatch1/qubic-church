'use client'

import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { Loader2 } from 'lucide-react'

const ContactCubeScene = dynamic(
  () => import('../contact-cube/ContactCubeScene').then((mod) => mod.ContactCubeScene),
  {
    ssr: false,
    loading: () => <ContactCubeLoading />,
  }
)

function ContactCubeLoading() {
  return (
    <div className="w-full h-[700px] bg-black rounded-lg border border-neutral-800 flex items-center justify-center">
      <div className="flex items-center gap-3 text-neutral-500">
        <Loader2 className="w-5 h-5 animate-spin" />
        <span className="text-sm">Loading 3D scene...</span>
      </div>
    </div>
  )
}

export default function ContactCubeTab() {
  return (
    <div className="w-full space-y-4">
      {/* Minimal Header */}
      <div className="flex items-baseline justify-between">
        <div>
          <h3 className="text-lg font-medium text-foreground">
            Contact Cube
          </h3>
          <p className="text-sm text-muted-foreground">
            Fold the 128×128 matrix into 3D to reveal point symmetry patterns
          </p>
        </div>
        <div className="text-xs text-muted-foreground/60">
          99.59% symmetric · 68 anomalies
        </div>
      </div>

      {/* Controls - simple inline */}
      <div className="flex items-center gap-6 text-xs text-muted-foreground border-b border-border pb-3">
        <span>
          <kbd className="px-1.5 py-0.5 bg-muted rounded text-[10px] font-mono mr-1">Click</kbd>
          Fold/Unfold
        </span>
        <span>
          <kbd className="px-1.5 py-0.5 bg-muted rounded text-[10px] font-mono mr-1">Drag</kbd>
          Rotate
        </span>
        <span>
          <kbd className="px-1.5 py-0.5 bg-muted rounded text-[10px] font-mono mr-1">Scroll</kbd>
          Zoom
        </span>
        <span className="ml-auto flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 bg-amber-500 rounded-full" />
            Center [22,22]
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 bg-red-500 rounded-full" />
            Anomalies
          </span>
        </span>
      </div>

      {/* 3D Scene */}
      <Suspense fallback={<ContactCubeLoading />}>
        <ContactCubeScene
          className="rounded-lg border border-neutral-800"
          showControls={true}
          showInfoPanel={true}
        />
      </Suspense>

      {/* Minimal formula */}
      <div className="text-center py-4 border-t border-border">
        <code className="text-sm text-muted-foreground font-mono">
          M[r][c] + M[127-r][127-c] = 0
        </code>
        <p className="text-xs text-muted-foreground/60 mt-1">
          Point symmetry formula — cells sum to zero with their mirror
        </p>
      </div>
    </div>
  )
}
