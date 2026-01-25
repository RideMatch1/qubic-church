import { Link } from '@/navigation'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { Sparkles, Database } from 'lucide-react'

// Static hero - fixed background grid that stays visible while scrolling
export function EvidenceHero() {
  return (
    <>
      {/* Fixed background grid - stays visible on entire page */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div
          className="absolute inset-0 opacity-[0.12]"
          style={{
            backgroundImage: `
              linear-gradient(to right, #7c2d12 1px, transparent 1px),
              linear-gradient(to bottom, #7c2d12 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
          }}
        />
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-orange-500/5 rounded-full blur-3xl" />
      </div>

      {/* Hero content */}
      <section className="relative flex flex-col items-center justify-center py-20 md:py-28 text-center">
        <div className="relative z-10 max-w-4xl mx-auto px-4">
          {/* Badge */}
          <div className="flex items-center justify-center gap-2 mb-6">
            <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-orange-500/10 border border-orange-500/20 text-sm font-medium tracking-widest text-orange-500 uppercase">
              <span className="inline-flex rounded-full h-2 w-2 bg-orange-500" />
              Research Archive
            </span>
          </div>

          {/* Title */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-serif font-bold tracking-tight mb-6">
            <span className="bg-gradient-to-r from-orange-400 via-amber-500 to-orange-500 bg-clip-text text-transparent">
              Cryptographic
            </span>
            <br />
            <span className="text-foreground">
              Research Data
            </span>
          </h1>

          {/* Description */}
          <p className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-10 leading-relaxed">
            Research datasets including the <span className="font-mono text-purple-400">128×128</span> Anna Matrix,
            derived addresses, and interactive 3D analysis tools.
          </p>
        </div>
      </section>
    </>
  )
}
