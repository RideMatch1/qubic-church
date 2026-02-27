'use client'

import Link from 'next/link'
import { useParams } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'

import { CreateMarketForm } from '@/components/predict/CreateMarketForm'

export default function CreateMarketPage() {
  const { locale } = useParams() as { locale: string }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <Link
        href={`/${locale}/predict`}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Markets
      </Link>

      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          Create Market
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Deploy a new prediction market on the Qubic blockchain via the
          Quottery smart contract. Set the trading pair, target price, and
          resolution timeline.
        </p>
      </div>

      <div className="rounded-lg border bg-card p-6">
        <CreateMarketForm />
      </div>
    </div>
  )
}
