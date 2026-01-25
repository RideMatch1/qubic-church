#!/usr/bin/env python3
"""
TERNARY ANALYSIS SCRIPT
=======================

Analyzes bridges using ternary (three-state) logic:
- +1 (TRUE/ACTIVE): value > 42
-  0 (NEUTRAL): -42 <= value <= 42
- -1 (FALSE/INHIBITED): value < -42

Author: qubic-academic-docs
Date: 2026-01-23
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from anna_matrix_utils import load_anna_matrix
from typing import Any


def safe_value(v: Any) -> int:
    """Convert matrix value to int, handling strings like '00000000'."""
    if isinstance(v, str):
        try:
            return int(v, 16) if len(v) == 8 else int(v)
        except:
            return 0
    return v


def to_ternary(value: Any) -> int:
    """Convert matrix value to ternary state (-1, 0, +1)."""
    v = safe_value(value)
    if v > 42:
        return 1
    elif v < -42:
        return -1
    else:
        return 0


def analyze_column_ternary(matrix: List[List[int]], column: int) -> Dict[str, Any]:
    """
    Perform comprehensive ternary analysis of a column.

    Returns:
        Dict with full ternary analysis
    """
    ternary_values = [to_ternary(safe_value(matrix[row][column])) for row in range(128)]

    positive = sum(1 for t in ternary_values if t == 1)
    negative = sum(1 for t in ternary_values if t == -1)
    neutral = sum(1 for t in ternary_values if t == 0)

    ternary_sum = sum(ternary_values)

    # Determine category
    if ternary_sum > 32:
        category = "POSITIVE"
    elif ternary_sum < -32:
        category = "NEGATIVE"
    else:
        category = "NEUTRAL"

    # Calculate ternary entropy (measure of balance)
    # Perfect balance would have equal distribution
    total = 128
    p_pos = positive / total
    p_neg = negative / total
    p_neu = neutral / total

    # Normalized entropy (0 = all same, 1 = perfectly balanced)
    import math
    entropy = 0
    for p in [p_pos, p_neg, p_neu]:
        if p > 0:
            entropy -= p * math.log2(p)
    max_entropy = math.log2(3)  # ~1.585
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

    # Find dominant regions (consecutive same-state neurons)
    regions = []
    current_region = {"state": ternary_values[0], "start": 0, "length": 1}
    for i in range(1, 128):
        if ternary_values[i] == current_region["state"]:
            current_region["length"] += 1
        else:
            if current_region["length"] >= 3:
                regions.append(current_region.copy())
            current_region = {"state": ternary_values[i], "start": i, "length": 1}
    if current_region["length"] >= 3:
        regions.append(current_region)

    return {
        "column": column,
        "ternary_sum": ternary_sum,
        "category": category,
        "positive_count": positive,
        "negative_count": negative,
        "neutral_count": neutral,
        "positive_ratio": round(p_pos, 4),
        "negative_ratio": round(p_neg, 4),
        "neutral_ratio": round(p_neu, 4),
        "normalized_entropy": round(normalized_entropy, 4),
        "balance_score": round(1 - abs(positive - negative) / 128, 4),
        "significant_regions": regions[:5],  # Top 5 longest regions
        "ternary_pattern": ''.join(['+' if t == 1 else '-' if t == -1 else '0'
                                    for t in ternary_values[:32]])  # First 32 chars
    }


def analyze_row_ternary(matrix: List[List[int]], row: int) -> Dict[str, Any]:
    """
    Perform ternary analysis of a row.
    """
    ternary_values = [to_ternary(safe_value(matrix[row][col])) for col in range(128)]

    positive = sum(1 for t in ternary_values if t == 1)
    negative = sum(1 for t in ternary_values if t == -1)
    neutral = sum(1 for t in ternary_values if t == 0)

    ternary_sum = sum(ternary_values)

    if ternary_sum > 32:
        category = "POSITIVE"
    elif ternary_sum < -32:
        category = "NEGATIVE"
    else:
        category = "NEUTRAL"

    return {
        "row": row,
        "ternary_sum": ternary_sum,
        "category": category,
        "positive_count": positive,
        "negative_count": negative,
        "neutral_count": neutral
    }


def helix_gate(a: Any, b: Any, c: Any) -> int:
    """
    Helix Gate: 3-input ternary operation.

    The fundamental operation in ternary neural networks.
    Takes three ternary values and produces a rotation (-3 to +3).

    Args:
        a, b, c: Raw matrix values

    Returns:
        Rotation value from -3 to +3
    """
    ta = to_ternary(safe_value(a))
    tb = to_ternary(safe_value(b))
    tc = to_ternary(safe_value(c))
    return ta + tb + tc


def analyze_helix_gates(matrix: List[List[int]], column: int) -> Dict[str, Any]:
    """
    Analyze Helix Gate activations for a column.

    Uses neighboring columns to compute helix rotations.
    """
    left_col = (column - 1) % 128
    right_col = (column + 1) % 128

    rotations = []
    for row in range(128):
        a = matrix[row][left_col]
        b = matrix[row][column]
        c = matrix[row][right_col]
        rotations.append(helix_gate(a, b, c))

    # Rotation distribution
    distribution = {i: rotations.count(i) for i in range(-3, 4)}

    # Average rotation (indicates overall bias)
    avg_rotation = sum(rotations) / len(rotations)

    # Rotation pattern
    pattern = ''.join([str(r + 3) for r in rotations[:32]])  # Map -3..3 to 0..6

    return {
        "column": column,
        "left_column": left_col,
        "right_column": right_col,
        "rotation_distribution": distribution,
        "average_rotation": round(avg_rotation, 4),
        "max_rotation_count": max(distribution.values()),
        "dominant_rotation": max(distribution, key=distribution.get),
        "rotation_pattern_32": pattern
    }


def main():
    """Main function."""
    print("=" * 60)
    print("TERNARY ANALYSIS")
    print("=" * 60)

    # Load matrix
    print("\nLoading Anna Matrix...")
    matrix = load_anna_matrix()
    print(f"Matrix loaded: {len(matrix)}x{len(matrix[0])}")

    # Load bridges if available
    bridges_path = Path(__file__).parent / "COMPLETE_BRIDGE_DATASET.json"
    if bridges_path.exists():
        print(f"Loading bridges from: {bridges_path}")
        with open(bridges_path, 'r') as f:
            data = json.load(f)
        bridges = data.get("bridges", [])
        print(f"Loaded {len(bridges)} bridges")
    else:
        bridges = []
        print("No bridge dataset found. Analyzing all columns.")

    # Perform ternary analysis
    print("\nPerforming ternary analysis...")

    column_analyses = {}
    row_analyses = {}
    helix_analyses = {}

    # Analyze columns
    for col in range(128):
        column_analyses[col] = analyze_column_ternary(matrix, col)

    # Analyze rows
    for row in range(128):
        row_analyses[row] = analyze_row_ternary(matrix, row)

    # Analyze helix gates for key columns
    key_columns = [5, 13, 23, 26, 30, 58, 74, 87, 92, 97, 106, 114, 115, 127]
    for col in key_columns:
        helix_analyses[col] = analyze_helix_gates(matrix, col)

    # If we have bridges, enhance them with ternary data
    enhanced_bridges = []
    if bridges:
        for bridge in bridges:
            enhanced = bridge.copy()
            col = bridge.get("column")
            if col is not None and col in column_analyses:
                enhanced["ternary_detailed"] = column_analyses[col]
                if col in helix_analyses:
                    enhanced["helix_analysis"] = helix_analyses[col]
            enhanced_bridges.append(enhanced)

    # Calculate global statistics
    all_ternary_sums = [column_analyses[c]["ternary_sum"] for c in range(128)]
    positive_columns = sum(1 for s in all_ternary_sums if s > 32)
    negative_columns = sum(1 for s in all_ternary_sums if s < -32)
    neutral_columns = sum(1 for s in all_ternary_sums if -32 <= s <= 32)

    global_stats = {
        "total_columns": 128,
        "positive_columns": positive_columns,
        "negative_columns": negative_columns,
        "neutral_columns": neutral_columns,
        "average_ternary_sum": round(sum(all_ternary_sums) / 128, 4),
        "max_ternary_sum": max(all_ternary_sums),
        "min_ternary_sum": min(all_ternary_sums),
        "most_positive_column": all_ternary_sums.index(max(all_ternary_sums)),
        "most_negative_column": all_ternary_sums.index(min(all_ternary_sums))
    }

    # Create output
    output = {
        "metadata": {
            "analyzed_at": datetime.now().isoformat(),
            "matrix_size": "128x128",
            "ternary_threshold": 42
        },
        "global_statistics": global_stats,
        "column_analyses": column_analyses,
        "row_analyses": row_analyses,
        "helix_analyses": helix_analyses,
        "enhanced_bridges": enhanced_bridges if enhanced_bridges else None
    }

    # Save output
    output_path = Path(__file__).parent / "TERNARY_ANALYSIS_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary
    print(f"\n{'=' * 60}")
    print("TERNARY ANALYSIS COMPLETE")
    print(f"{'=' * 60}")
    print(f"Global Statistics:")
    print(f"  Positive columns (sum > 32): {positive_columns}")
    print(f"  Negative columns (sum < -32): {negative_columns}")
    print(f"  Neutral columns: {neutral_columns}")
    print(f"  Average ternary sum: {global_stats['average_ternary_sum']}")
    print(f"  Most positive: Column {global_stats['most_positive_column']} (sum={max(all_ternary_sums)})")
    print(f"  Most negative: Column {global_stats['most_negative_column']} (sum={min(all_ternary_sums)})")
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
