#!/usr/bin/env python3
"""
ANNA MATRIX VISUALIZER
======================

Visualizes the 128×128 Anna Matrix as various representations:
- Terminal heatmap (ASCII)
- Statistics summary
- Strategic node highlighting
- Weight distribution chart

Usage:
    python3 matrix_visualizer.py [--mode MODE]

Modes:
    heatmap   - ASCII heatmap in terminal
    stats     - Statistical summary
    nodes     - Strategic nodes highlighted
    weights   - Weight distribution
    all       - All visualizations

Author: Research Team
Date: 2026-01-16
"""

import json
import argparse
from collections import Counter
from typing import List, Dict

# =============================================================================
# STRATEGIC NODES
# =============================================================================

STRATEGIC_NODES = {
    "VOID": {"anna": (0, 0), "matrix": (63, 64), "value": -40, "symbol": "V"},
    "CORE": {"anna": (6, 33), "matrix": (30, 70), "value": -93, "symbol": "C"},
    "ENTRY": {"anna": (45, 92), "matrix": (99, 109), "value": 106, "symbol": "E"},
    "EXIT": {"anna": (82, 39), "matrix": (24, 18), "value": -75, "symbol": "X"},
    "MEMORY": {"anna": (21, 21), "matrix": (42, 85), "value": -50, "symbol": "M"},
    "GUARDIAN": {"anna": (19, 18), "matrix": (45, 83), "value": 36, "symbol": "G"},
    "DATE": {"anna": (3, 3), "matrix": (60, 67), "value": -122, "symbol": "D"},
    "ORACLE": {"anna": (11, 110), "matrix": (81, 75), "value": -83, "symbol": "O"},
    "VISION": {"anna": (64, 64), "matrix": (127, 0), "value": -92, "symbol": "W"},
}

# =============================================================================
# DATA LOADING
# =============================================================================

def load_matrix(path: str = "apps/web/public/data/anna-matrix.json") -> List[List[int]]:
    """Load the Anna Matrix from JSON."""
    with open(path) as f:
        data = json.load(f)
    return data.get("matrix", data)

# =============================================================================
# ASCII HEATMAP
# =============================================================================

def value_to_char(value: int) -> str:
    """Convert matrix value to ASCII character for heatmap."""
    # Normalize to 0-9 range
    normalized = (value + 128) / 256  # 0.0 to 1.0
    chars = " ░▒▓█"
    idx = min(len(chars) - 1, int(normalized * len(chars)))
    return chars[idx]

def print_heatmap(matrix: List[List[int]], scale: int = 4):
    """Print ASCII heatmap of matrix."""
    print("\n" + "=" * 70)
    print("ANNA MATRIX HEATMAP (128×128)")
    print("=" * 70)
    print("Legend: ░ = low | ▒ = medium | ▓ = high | █ = max")
    print()

    # Downsample for terminal display
    height = 128 // scale
    width = 128 // scale

    # Build node position lookup
    node_positions = {}
    for name, info in STRATEGIC_NODES.items():
        row, col = info["matrix"]
        scaled_row = row // scale
        scaled_col = col // scale
        node_positions[(scaled_row, scaled_col)] = info["symbol"]

    # Print header
    print("    ", end="")
    for col in range(0, width, 8):
        print(f"{col * scale:3d}     ", end="")
    print()

    # Print rows
    for row in range(height):
        if row % 4 == 0:
            print(f"{row * scale:3d} ", end="")
        else:
            print("    ", end="")

        for col in range(width):
            # Check if this is a strategic node
            if (row, col) in node_positions:
                print(f"\033[91m{node_positions[(row, col)]}\033[0m", end="")
            else:
                # Average values in this cell
                values = []
                for dr in range(scale):
                    for dc in range(scale):
                        r, c = row * scale + dr, col * scale + dc
                        if 0 <= r < 128 and 0 <= c < 128:
                            values.append(matrix[r][c])
                if values:
                    avg = sum(values) // len(values)
                    print(value_to_char(avg), end="")
                else:
                    print(" ", end="")
        print()

    print()
    print("Strategic Nodes (red): ", end="")
    for name, info in STRATEGIC_NODES.items():
        print(f"{info['symbol']}={name} ", end="")
    print()

# =============================================================================
# STATISTICS
# =============================================================================

def print_statistics(matrix: List[List[int]]):
    """Print statistical summary of matrix."""
    print("\n" + "=" * 70)
    print("MATRIX STATISTICS")
    print("=" * 70)

    # Flatten and filter
    all_values = []
    for row in matrix:
        for val in row:
            if isinstance(val, int):
                all_values.append(val)

    if not all_values:
        print("No numeric values found!")
        return

    # Basic stats
    print(f"\nBasic Statistics:")
    print(f"  Total cells:    {len(all_values):,}")
    print(f"  Mean:           {sum(all_values) / len(all_values):.2f}")
    print(f"  Min:            {min(all_values)}")
    print(f"  Max:            {max(all_values)}")

    # Distribution
    positive = sum(1 for v in all_values if v > 0)
    negative = sum(1 for v in all_values if v < 0)
    zero = sum(1 for v in all_values if v == 0)

    print(f"\nValue Distribution:")
    print(f"  Positive:       {positive:,} ({positive/len(all_values)*100:.1f}%)")
    print(f"  Zero:           {zero:,} ({zero/len(all_values)*100:.1f}%)")
    print(f"  Negative:       {negative:,} ({negative/len(all_values)*100:.1f}%)")

    # Top values
    counter = Counter(all_values)
    print(f"\nTop 10 Most Common Values:")
    for value, count in counter.most_common(10):
        pct = count / len(all_values) * 100
        bar = "█" * int(pct * 2)
        print(f"  {value:5d}: {count:4d} ({pct:4.1f}%) {bar}")

    # CFB signature values
    print(f"\nCFB Signature Values:")
    cfb_values = [-114, -113, 14, -121, 27, -27, 121, 137]
    for val in cfb_values:
        count = counter.get(val, 0)
        pct = count / len(all_values) * 100
        print(f"  {val:5d}: {count:4d} ({pct:4.1f}%)")

    # Modulo-8 analysis
    print(f"\nModulo-8 Row Analysis:")
    for mod in range(8):
        mod_values = []
        for row_idx in range(128):
            if row_idx % 8 == mod:
                for val in matrix[row_idx]:
                    if isinstance(val, int):
                        mod_values.append(val)
        if mod_values:
            mod_counter = Counter(mod_values)
            top_val, top_count = mod_counter.most_common(1)[0]
            print(f"  Row % 8 = {mod}: Dominant = {top_val:4d} ({top_count} times)")

# =============================================================================
# STRATEGIC NODES
# =============================================================================

def print_strategic_nodes(matrix: List[List[int]]):
    """Print strategic node information."""
    print("\n" + "=" * 70)
    print("STRATEGIC NODES")
    print("=" * 70)

    print(f"\n{'Node':<10} {'Anna Coords':<12} {'Matrix':<12} {'Expected':<10} {'Actual':<10} {'Status'}")
    print("-" * 70)

    all_match = True
    for name, info in STRATEGIC_NODES.items():
        row, col = info["matrix"]
        expected = info["value"]

        try:
            actual = matrix[row][col]
            if expected is not None:
                match = actual == expected
                status = "✅" if match else "❌"
                if not match:
                    all_match = False
            else:
                status = "?"
        except (IndexError, TypeError):
            actual = "ERROR"
            status = "❌"
            all_match = False

        anna = f"({info['anna'][0]}, {info['anna'][1]})"
        matrix_pos = f"[{row}, {col}]"

        print(f"{name:<10} {anna:<12} {matrix_pos:<12} {expected:<10} {actual:<10} {status}")

    print("-" * 70)
    if all_match:
        print("✅ ALL NODES VERIFIED")
    else:
        print("⚠️  SOME NODES MISMATCH")

    # Node connectivity
    print(f"\nNode Connectivity:")
    print(f"  ENTRY(45) + EXIT(82) = 127 (Anti-diagonal!)")
    print(f"  VOID(0,0) = Origin point")
    print(f"  CORE(6,33) = Central processor")

# =============================================================================
# WEIGHT DISTRIBUTION
# =============================================================================

def print_weight_distribution(matrix: List[List[int]]):
    """Print weight distribution chart."""
    print("\n" + "=" * 70)
    print("WEIGHT DISTRIBUTION")
    print("=" * 70)

    # Collect values
    all_values = []
    for row in matrix:
        for val in row:
            if isinstance(val, int):
                all_values.append(val)

    counter = Counter(all_values)

    # Histogram buckets
    buckets = {}
    bucket_size = 16
    for val in all_values:
        bucket = (val // bucket_size) * bucket_size
        buckets[bucket] = buckets.get(bucket, 0) + 1

    # Find max for scaling
    max_count = max(buckets.values()) if buckets else 1

    print(f"\nHistogram (bucket size = {bucket_size}):")
    print()

    for bucket in sorted(buckets.keys()):
        count = buckets[bucket]
        bar_len = int(count / max_count * 40)
        bar = "█" * bar_len
        label = f"{bucket:4d} to {bucket + bucket_size - 1:4d}"
        print(f"  {label}: {bar} ({count:,})")

    # Power-law check
    print(f"\nPower-Law Distribution Check:")
    sorted_counts = sorted(counter.values(), reverse=True)
    if len(sorted_counts) >= 10:
        top_10_sum = sum(sorted_counts[:10])
        total = sum(sorted_counts)
        top_10_pct = top_10_sum / total * 100
        print(f"  Top 10 values account for: {top_10_pct:.1f}% of occurrences")
        if top_10_pct > 15:
            print(f"  → Indicates POWER-LAW distribution (evolved system)")
        else:
            print(f"  → Indicates more UNIFORM distribution")

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Anna Matrix Visualizer")
    parser.add_argument("--mode", choices=["heatmap", "stats", "nodes", "weights", "all"],
                        default="all", help="Visualization mode")
    parser.add_argument("--matrix", default="apps/web/public/data/anna-matrix.json",
                        help="Path to matrix JSON file")
    args = parser.parse_args()

    # Load matrix
    print("Loading matrix...")
    matrix = load_matrix(args.matrix)
    print(f"Matrix size: {len(matrix)} × {len(matrix[0]) if matrix else 0}")

    # Run visualizations
    if args.mode in ["heatmap", "all"]:
        print_heatmap(matrix)

    if args.mode in ["stats", "all"]:
        print_statistics(matrix)

    if args.mode in ["nodes", "all"]:
        print_strategic_nodes(matrix)

    if args.mode in ["weights", "all"]:
        print_weight_distribution(matrix)

    print("\n" + "=" * 70)
    print("VISUALIZATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
