export interface NeuraxonNode {
  id: number
  type: 'input' | 'hidden' | 'output'
  seed: string
  realId: string
  documentedId: string
  state: -1 | 0 | 1
  position: [number, number, number]
  frame: number
}

export interface NeuraxonEdge {
  source: number
  target: number
  weight: number
  type: 'fast' | 'slow' | 'meta'
}

export interface NeuraxonFrame {
  id: number
  label: string
  nodeIds: number[]
  startId: number
  endId: number
}

export interface NeuraxonMetadata {
  totalNodes: number
  totalEdges: number
  totalFrames: number
  nodesPerFrame: number
  stateDistribution: {
    negative: number
    zero: number
    positive: number
  }
  typeDistribution: {
    input: number
    hidden: number
    output: number
  }
}

export interface NeuraxonData {
  metadata: NeuraxonMetadata
  nodes: NeuraxonNode[]
  edges: NeuraxonEdge[]
  frames: NeuraxonFrame[]
}
