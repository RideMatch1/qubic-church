'use client'

import { JourneyContainer } from './JourneyContainer'
import { JourneyProgress } from './JourneyProgress'
import {
  VoidSection,
  GenesisSection,
  FormulaSection,
  PatoshiSection,
  BridgeSection,
  MatrixSection,
  NetworkSection,
  CountdownSection,
  EvidenceSection,
  CallSection,
} from './sections'

export function JourneyPage() {
  return (
    <JourneyContainer>
      {/* Progress indicator - hidden on mobile, visible on larger screens */}
      <div className="hidden md:block">
        <JourneyProgress position="right" />
      </div>

      {/* All journey sections */}
      <VoidSection />
      <GenesisSection />
      <FormulaSection />
      <PatoshiSection />
      <BridgeSection />
      <MatrixSection />
      <NetworkSection />
      <CountdownSection />
      <EvidenceSection />
      <CallSection />
    </JourneyContainer>
  )
}
