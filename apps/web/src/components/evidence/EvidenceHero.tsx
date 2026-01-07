import { Link } from '@/navigation'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { Sparkles, Shield, Zap, Database } from 'lucide-react'

const HERO_STATS = [
  {
    label: 'Bitcoin Addresses',
    value: '1,004,767',
    icon: Database,
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30'
  },
  {
    label: 'Matrix Cells',
    value: '16,384',
    icon: Sparkles,
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30'
  },
  {
    label: 'Qubic Seeds',
    value: '23,765',
    icon: Zap,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30'
  },
  {
    label: 'Verification',
    value: '99%',
    icon: Shield,
    color: 'text-emerald-500',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/30'
  },
]

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
              Evidence Vault
            </span>
          </div>

          {/* Title */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-serif font-bold tracking-tight mb-6">
            <span className="bg-gradient-to-r from-orange-400 via-amber-500 to-orange-500 bg-clip-text text-transparent">
              The Mathematical
            </span>
            <br />
            <span className="text-foreground">
              Evidence Archive
            </span>
          </h1>

          {/* Description */}
          <p className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-4 leading-relaxed">
            Explore the <span className="text-orange-500 font-medium">cryptographically verified</span> connections between Bitcoin and Qubic
          </p>

          <p className="text-sm sm:text-base text-muted-foreground/80 max-w-2xl mx-auto mb-10 leading-relaxed">
            Over <span className="font-mono text-orange-400">1 million</span> Bitcoin addresses, the <span className="font-mono text-purple-400">128x128</span> Anna Matrix,
            K12 hash derivations, and complete mathematical validation.
          </p>

          {/* Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link
              href="#data-tables"
              className={cn(
                buttonVariants({ size: 'lg' }),
                'font-medium px-8 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600'
              )}
            >
              <Database className="w-4 h-4 mr-2" />
              Explore Data
            </Link>

            <Link
              href="#data-tables"
              className={cn(
                buttonVariants({ variant: 'outline', size: 'lg' }),
                'font-medium px-8'
              )}
            >
              <Sparkles className="w-4 h-4 mr-2" />
              View Anna Grid
            </Link>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {HERO_STATS.map((stat) => {
              const Icon = stat.icon
              return (
                <div
                  key={stat.label}
                  className={cn(
                    "relative p-4 rounded-xl border overflow-hidden",
                    stat.bgColor,
                    stat.borderColor
                  )}
                >
                  <div className="absolute -right-4 -top-4 opacity-10">
                    <Icon className="w-20 h-20" />
                  </div>
                  <div className="relative">
                    <div className="flex items-center gap-2 mb-1">
                      <Icon className={cn("w-4 h-4", stat.color)} />
                      <span className={cn("text-2xl font-bold", stat.color)}>
                        {stat.value}
                      </span>
                    </div>
                    <div className="text-sm font-medium text-foreground">{stat.label}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>
    </>
  )
}
