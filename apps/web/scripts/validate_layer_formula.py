#!/usr/bin/env python3
"""
Validate Layer Formula
======================

Tests the hypothesis that Anna Matrix maps to Patoshi blocks via:
    block_height = (layer × 16,384) + (row × 128) + column

Where:
    - Layer 0: Blocks 0-16,383
    - Layer 1: Blocks 16,384-32,767
    - Layer 2: Blocks 32,768-49,151

Author: qubic-academic-docs
Date: 2026-01-23
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


def load_patoshi_blocks() -> Set[int]:
    """Load all Patoshi block heights."""
    script_dir = Path(__file__).parent
    data_path = script_dir.parent / "public" / "data" / "patoshi-addresses.json"

    with open(data_path, 'r') as f:
        data = json.load(f)

    records = data.get('records', data)
    return {r['blockHeight'] for r in records if 'blockHeight' in r}


def generate_layer_blocks(layers: int = 3) -> Dict[int, List[Tuple[int, int, int]]]:
    """
    Generate all block heights from the layer formula.

    Returns dict mapping block_height -> list of (layer, row, col) tuples
    """
    blocks = defaultdict(list)

    for layer in range(layers):
        for row in range(128):
            for col in range(128):
                block = (layer * 16384) + (row * 128) + col
                blocks[block].append((layer, row, col))

    return dict(blocks)


def analyze_coverage(patoshi_blocks: Set[int], formula_blocks: Dict[int, List]) -> Dict:
    """Analyze how well the layer formula covers Patoshi blocks."""

    # Get block ranges
    patoshi_min = min(patoshi_blocks)
    patoshi_max = max(patoshi_blocks)
    formula_min = min(formula_blocks.keys())
    formula_max = max(formula_blocks.keys())

    # Calculate overlaps
    formula_set = set(formula_blocks.keys())
    overlap = patoshi_blocks & formula_set
    patoshi_only = patoshi_blocks - formula_set
    formula_only = formula_set - patoshi_blocks

    # Layer-by-layer analysis
    layer_stats = {}
    for layer in range(3):
        layer_start = layer * 16384
        layer_end = layer_start + 16383

        patoshi_in_layer = {b for b in patoshi_blocks if layer_start <= b <= layer_end}
        formula_in_layer = {b for b in formula_set if layer_start <= b <= layer_end}
        layer_overlap = patoshi_in_layer & formula_in_layer

        layer_stats[f"layer_{layer}"] = {
            "range": f"{layer_start}-{layer_end}",
            "patoshi_count": len(patoshi_in_layer),
            "formula_count": len(formula_in_layer),
            "overlap_count": len(layer_overlap),
            "patoshi_coverage": len(layer_overlap) / len(patoshi_in_layer) if patoshi_in_layer else 0
        }

    return {
        "patoshi_range": {"min": patoshi_min, "max": patoshi_max, "total": len(patoshi_blocks)},
        "formula_range": {"min": formula_min, "max": formula_max, "total": len(formula_set)},
        "overlap": {
            "count": len(overlap),
            "patoshi_coverage_percent": len(overlap) / len(patoshi_blocks) * 100,
            "formula_coverage_percent": len(overlap) / len(formula_set) * 100
        },
        "patoshi_outside_formula": {
            "count": len(patoshi_only),
            "min": min(patoshi_only) if patoshi_only else None,
            "max": max(patoshi_only) if patoshi_only else None,
            "examples": sorted(list(patoshi_only))[:20]
        },
        "layer_analysis": layer_stats
    }


def find_anomaly_blocks(anomalies_path: Path, layers: int = 3) -> List[Dict]:
    """Map anomaly cell positions to block heights."""
    with open(anomalies_path, 'r') as f:
        anomalies = json.load(f)

    results = []
    for anomaly in anomalies.get('anomalies', []):
        pos = anomaly['pos']
        row, col = pos[0], pos[1]
        value = anomaly['value']

        # Calculate blocks for each layer
        layer_blocks = []
        for layer in range(layers):
            block = (layer * 16384) + (row * 128) + col
            layer_blocks.append({
                "layer": layer,
                "block": block
            })

        results.append({
            "matrix_position": pos,
            "matrix_value": value,
            "derived_blocks": layer_blocks,
            "is_special": anomaly.get('special', False)
        })

    return results


def main():
    print("=" * 70)
    print("LAYER FORMULA VALIDATION")
    print("block_height = (layer × 16,384) + (row × 128) + column")
    print("=" * 70)

    # Load data
    print("\nLoading Patoshi blocks...")
    patoshi_blocks = load_patoshi_blocks()
    print(f"Loaded {len(patoshi_blocks)} unique Patoshi block heights")

    # Generate formula blocks
    print("\nGenerating formula blocks (3 layers)...")
    formula_blocks = generate_layer_blocks(3)
    print(f"Generated {len(formula_blocks)} unique block heights")

    # Analyze coverage
    print("\nAnalyzing coverage...")
    analysis = analyze_coverage(patoshi_blocks, formula_blocks)

    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    print(f"\nPatoshi Blocks:")
    print(f"  Range: {analysis['patoshi_range']['min']} - {analysis['patoshi_range']['max']}")
    print(f"  Total: {analysis['patoshi_range']['total']}")

    print(f"\nFormula Blocks (3 layers):")
    print(f"  Range: {analysis['formula_range']['min']} - {analysis['formula_range']['max']}")
    print(f"  Total: {analysis['formula_range']['total']}")

    print(f"\nOverlap Analysis:")
    print(f"  Blocks in both: {analysis['overlap']['count']}")
    print(f"  Patoshi coverage: {analysis['overlap']['patoshi_coverage_percent']:.2f}%")
    print(f"  Formula coverage: {analysis['overlap']['formula_coverage_percent']:.2f}%")

    print(f"\nPatoshi blocks OUTSIDE formula range:")
    print(f"  Count: {analysis['patoshi_outside_formula']['count']}")
    if analysis['patoshi_outside_formula']['min']:
        print(f"  Range: {analysis['patoshi_outside_formula']['min']} - {analysis['patoshi_outside_formula']['max']}")
        print(f"  Examples: {analysis['patoshi_outside_formula']['examples'][:10]}...")

    print("\nLayer-by-Layer Analysis:")
    for layer_name, stats in analysis['layer_analysis'].items():
        print(f"\n  {layer_name.upper()} (Blocks {stats['range']}):")
        print(f"    Patoshi blocks in range: {stats['patoshi_count']}")
        print(f"    Formula blocks: {stats['formula_count']}")
        print(f"    Overlap: {stats['overlap_count']}")
        print(f"    Coverage: {stats['patoshi_coverage']*100:.2f}%")

    # Anomaly blocks analysis
    print("\n" + "=" * 70)
    print("ANOMALY CELLS → BLOCKS MAPPING")
    print("=" * 70)

    script_dir = Path(__file__).parent
    anomalies_path = script_dir.parent / "public" / "data" / "anna-matrix-anomalies.json"

    if anomalies_path.exists():
        anomaly_blocks = find_anomaly_blocks(anomalies_path)
        print(f"\nMapped {len(anomaly_blocks)} anomaly cells to blocks")

        # Check which anomaly blocks are Patoshi blocks
        patoshi_anomalies = []
        for ab in anomaly_blocks:
            for lb in ab['derived_blocks']:
                if lb['block'] in patoshi_blocks:
                    patoshi_anomalies.append({
                        "position": ab['matrix_position'],
                        "value": ab['matrix_value'],
                        "layer": lb['layer'],
                        "block": lb['block'],
                        "is_special": ab['is_special']
                    })

        print(f"Anomaly cells mapping to Patoshi blocks: {len(patoshi_anomalies)}")

        if patoshi_anomalies:
            print("\nExamples:")
            for pa in patoshi_anomalies[:10]:
                special = " [SPECIAL]" if pa['is_special'] else ""
                print(f"  Position {pa['position']} (value={pa['value']}) → Layer {pa['layer']}, Block {pa['block']}{special}")

        analysis['anomaly_mapping'] = {
            "total_anomalies": len(anomaly_blocks),
            "patoshi_matches": len(patoshi_anomalies),
            "matches": patoshi_anomalies
        }

    # Save results
    output_path = script_dir / "LAYER_FORMULA_VALIDATION.json"
    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    # Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    coverage = analysis['overlap']['patoshi_coverage_percent']
    if coverage >= 90:
        print(f"\n✅ HIGH COVERAGE ({coverage:.2f}%)")
        print("The layer formula strongly correlates with Patoshi blocks!")
    elif coverage >= 50:
        print(f"\n⚠️ PARTIAL COVERAGE ({coverage:.2f}%)")
        print("The layer formula partially explains Patoshi block mapping.")
    else:
        print(f"\n❌ LOW COVERAGE ({coverage:.2f}%)")
        print("The layer formula does not fully explain Patoshi blocks.")
        print("Additional layers or different formula may be needed.")


if __name__ == "__main__":
    main()
