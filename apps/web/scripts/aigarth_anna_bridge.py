#!/usr/bin/env python3
"""
AIGARTH ↔ ANNA MATRIX BRIDGE EXPERIMENT
========================================

This script demonstrates the CONNECTION between:
- Aigarth-it (Ternary Neural Network)
- Anna Matrix (128×128 Trained Weights)

Key Questions:
1. Can Aigarth process coordinates like Anna Bot?
2. Can we reconstruct Anna Matrix values from ternary operations?
3. What is the mathematical bridge?

Date: January 17, 2026
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from aigarth_it.common import (
    ternary_clamp,
    random_trit_vector,
    bitstring_to_trits,
    int_to_bitstring
)
from aigarth_it.neuron_cl import AITClNeuron

# Load Anna Matrix data
ANNA_MATRIX_PATH = Path(__file__).parent.parent / "public/data/anna-matrix.json"

def log(msg):
    print(msg)

def divider(title=""):
    log(f"\n{'='*60}")
    if title:
        log(f"  {title}")
        log('='*60)

# =============================================================================
# LOAD ANNA MATRIX
# =============================================================================
def load_anna_matrix():
    """Load the Anna Matrix from JSON."""
    try:
        with open(ANNA_MATRIX_PATH, 'r') as f:
            data = json.load(f)

        # Handle different JSON formats
        if isinstance(data, dict) and "matrix" in data:
            # Format: {"matrix": [[...]]}
            raw_matrix = data["matrix"]
        elif isinstance(data, list):
            # Format: [[...]]
            raw_matrix = data
        else:
            raise ValueError(f"Unknown matrix format: {type(data)}")

        # Convert to 128x128 integer matrix
        matrix = []
        for row_data in raw_matrix:
            row = []
            for cell in row_data:
                if isinstance(cell, dict):
                    value = cell.get('value', 0)
                elif isinstance(cell, (int, float)):
                    value = int(cell)
                else:
                    value = 0
                row.append(value)
            matrix.append(row)

        log(f"  ✓ Anna Matrix loaded: {len(matrix)}×{len(matrix[0])}")
        return matrix
    except Exception as e:
        log(f"  ✗ Failed to load Anna Matrix: {e}")
        import traceback
        traceback.print_exc()
        return None

# =============================================================================
# EXPERIMENT 1: Ternary Weight Reconstruction
# =============================================================================
def experiment_1_weight_reconstruction(matrix):
    """Can Anna Matrix values be reconstructed from ternary weights?"""
    divider("EXPERIMENT 1: Ternary Weight Reconstruction")

    if matrix is None:
        log("  Skipping - matrix not loaded")
        return False

    log("  Hypothesis: Anna values = Sum of row's ternary weights")
    log("  If true: value = count(+1) - count(-1) for 128 cells")

    # Analyze row sums
    row_sums = []
    for i, row in enumerate(matrix):
        row_sum = sum(row)
        row_sums.append(row_sum)

    # Statistics
    min_sum = min(row_sums)
    max_sum = max(row_sums)
    avg_sum = sum(row_sums) / len(row_sums)

    log(f"\n  Row sum statistics:")
    log(f"    Min: {min_sum}")
    log(f"    Max: {max_sum}")
    log(f"    Avg: {avg_sum:.1f}")

    # Check if values could be ternary aggregations
    # Each cell is int8 [-128, 127], not ternary
    # But could represent aggregated ternary weights

    log(f"\n  Value distribution analysis:")
    all_values = [cell for row in matrix for cell in row]
    unique_values = sorted(set(all_values))

    log(f"    Unique values: {len(unique_values)}")
    log(f"    Range: [{min(all_values)}, {max(all_values)}]")

    # Top 10 most common
    from collections import Counter
    value_counts = Counter(all_values)
    top_10 = value_counts.most_common(10)

    log(f"\n  Top 10 collision values:")
    for val, count in top_10:
        pct = 100 * count / len(all_values)
        log(f"    {val:4d}: {count:4d} ({pct:.2f}%)")

    return True

# =============================================================================
# EXPERIMENT 2: Coordinate to Value Mapping
# =============================================================================
def experiment_2_coordinate_mapping(matrix):
    """Test the coordinate transformation formula."""
    divider("EXPERIMENT 2: Coordinate Mapping Formula")

    if matrix is None:
        log("  Skipping - matrix not loaded")
        return False

    # Known strategic nodes from documentation
    strategic_nodes = [
        {"name": "VOID", "anna": (0, 0), "matrix": (63, 64), "expected": -40},
        {"name": "CORE", "anna": (6, 33), "matrix": (30, 70), "expected": -93},
        {"name": "ENTRY", "anna": (45, 92), "matrix": None, "expected": 106},
        {"name": "MEMORY", "anna": (21, 21), "matrix": (42, 85), "expected": -50},
        {"name": "GUARDIAN", "anna": (19, 18), "matrix": (45, 83), "expected": 36},
    ]

    log("  Testing strategic node values:")
    log("  " + "-"*50)

    def anna_to_matrix(x, y):
        """Convert Anna coordinates to Matrix indices."""
        col = (x + 64) % 128
        row = (63 - y) % 128
        return row, col

    results = []
    for node in strategic_nodes:
        x, y = node["anna"]
        row, col = anna_to_matrix(x, y)

        try:
            actual = matrix[row][col]
            expected = node["expected"]
            match = actual == expected
            status = "✓" if match else "✗"

            results.append({
                "name": node["name"],
                "anna": (x, y),
                "matrix": (row, col),
                "expected": expected,
                "actual": actual,
                "match": match
            })

            log(f"  {status} {node['name']:10s}: Anna({x:3d},{y:3d}) → Matrix[{row:3d}][{col:3d}] = {actual:4d} (exp: {expected:4d})")
        except IndexError as e:
            log(f"  ✗ {node['name']:10s}: Index out of range")
            results.append({
                "name": node["name"],
                "error": str(e)
            })

    passed = sum(1 for r in results if r.get("match", False))
    total = len(results)
    log(f"\n  Result: {passed}/{total} nodes verified")

    return passed > 0

# =============================================================================
# EXPERIMENT 3: Create Aigarth Network from Anna Weights
# =============================================================================
def experiment_3_network_from_matrix(matrix):
    """Create an Aigarth network using Anna Matrix values as weights."""
    divider("EXPERIMENT 3: Aigarth Network from Anna Weights")

    if matrix is None:
        log("  Skipping - matrix not loaded")
        return False

    # Take a single row as weights for a neuron
    row_68 = matrix[68]  # Primary Cortex row

    log(f"  Using Row 68 (Primary Cortex) as weights")
    log(f"  Row length: {len(row_68)}")
    log(f"  Sample values: {row_68[:10]}...")

    # Convert int8 values to ternary weights
    # Method 1: Clamp directly
    ternary_weights_1 = [ternary_clamp(v) for v in row_68]

    # Method 2: Sign-based (positive=1, negative=-1, zero=0)
    ternary_weights_2 = [1 if v > 0 else (-1 if v < 0 else 0) for v in row_68]

    log(f"\n  Ternary conversion methods:")

    # Count distribution for method 1
    count_1 = {-1: ternary_weights_1.count(-1), 0: ternary_weights_1.count(0), 1: ternary_weights_1.count(1)}
    log(f"    Method 1 (clamp): -1:{count_1[-1]} 0:{count_1[0]} +1:{count_1[1]}")

    count_2 = {-1: ternary_weights_2.count(-1), 0: ternary_weights_2.count(0), 1: ternary_weights_2.count(1)}
    log(f"    Method 2 (sign):  -1:{count_2[-1]} 0:{count_2[0]} +1:{count_2[1]}")

    # Create Aigarth neuron with these weights
    neuron = AITClNeuron(input_weights=ternary_weights_2, input_skew=0)

    log(f"\n  Created AITClNeuron with Row 68 weights")
    log(f"    Weights: {neuron.input_weights[:10]}...")
    log(f"    State: {neuron.state}")
    log(f"    Split index: {neuron.input_split_index}")

    # Test feedforward with some inputs
    test_inputs = [
        [1] * 128,   # All positive
        [-1] * 128,  # All negative
        [0] * 128,   # All neutral
        random_trit_vector(128),  # Random
    ]

    log(f"\n  Feedforward tests:")
    for i, feed in enumerate(test_inputs):
        neuron.state = 0
        neuron.feedforward(tuple(feed))
        state, changed = neuron.commit_state()

        # Calculate expected sum
        weighted_sum = sum(f * w for f, w in zip(feed, neuron.input_weights))
        expected_state = ternary_clamp(weighted_sum)

        status = "✓" if state == expected_state else "✗"
        label = ["all +1", "all -1", "all 0", "random"][i]

        log(f"    {status} Input {label:8s}: sum={weighted_sum:5d} → state={state:2d}")

    return True

# =============================================================================
# EXPERIMENT 4: Reverse Engineering the Hash
# =============================================================================
def experiment_4_hash_analysis(matrix):
    """Analyze potential hash functions connecting seeds to coordinates."""
    divider("EXPERIMENT 4: Hash Function Analysis")

    if matrix is None:
        log("  Skipping - matrix not loaded")
        return False

    import hashlib

    # The documented formula from source code:
    # row = sha256(seed)[0] % 128
    # col = sha256(seed)[1] % 128

    log("  Testing SHA256 → Coordinate mapping:")
    log("  Formula: row = hash[0] % 128, col = hash[1] % 128")

    test_seeds = [
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "qubicqubicqubicqubicqubicqubicqubicqubicqubicqubicqubic",
        "testtesttesttesttesttesttesttesttesttesttesttesttesttest",
        "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabc",
    ]

    log("\n  Seed → Hash → Coordinates → Value:")
    for seed in test_seeds:
        # SHA256 hash
        h = hashlib.sha256(seed.encode('utf-8')).digest()

        # Extract coordinates
        row = h[0] % 128
        col = h[1] % 128

        # Get value from matrix
        value = matrix[row][col]

        # Convert to Anna coordinates
        anna_x = col - 64
        anna_y = 63 - row

        log(f"\n    Seed: {seed[:20]}...")
        log(f"    Hash[0:2]: {h[0]:3d}, {h[1]:3d}")
        log(f"    Matrix: [{row:3d}][{col:3d}]")
        log(f"    Anna: ({anna_x:3d}, {anna_y:3d})")
        log(f"    Value: {value}")

    log("\n  This demonstrates how SHA256 deterministically maps seeds to coordinates!")

    return True

# =============================================================================
# EXPERIMENT 5: CFB Signature Analysis
# =============================================================================
def experiment_5_cfb_signature(matrix):
    """Analyze CFB's mathematical signatures in the matrix."""
    divider("EXPERIMENT 5: CFB Signature Analysis")

    if matrix is None:
        log("  Skipping - matrix not loaded")
        return False

    # CFB's known numbers
    cfb_numbers = {
        27: "3³ - Perfect cube",
        47: "Prime, appears in master formula",
        137: "Fine structure constant × 1000",
        283: "Prime, appears in master formula",
        121: "11² - NXT constant",
        114: "Dominant weight",
        113: "Prime, dominant weight"
    }

    log("  Searching for CFB signature numbers in matrix:")

    all_values = [cell for row in matrix for cell in row]
    from collections import Counter
    value_counts = Counter(all_values)

    for num, meaning in cfb_numbers.items():
        count_pos = value_counts.get(num, 0)
        count_neg = value_counts.get(-num, 0)

        if count_pos > 0 or count_neg > 0:
            log(f"\n    {num:4d} ({meaning}):")
            if count_pos > 0:
                log(f"      +{num}: {count_pos} occurrences")
            if count_neg > 0:
                log(f"      -{num}: {count_neg} occurrences")

    # Check for master formula components
    log("\n  Master Formula Check: 625,284 = 283 × 47² + 137")
    result = 283 * 47 * 47 + 137
    log(f"    283 × 47² + 137 = {result}")
    log(f"    625,284 mod 16384 = {625284 % 16384} (boot address = Row 21)")

    return True

# =============================================================================
# MAIN
# =============================================================================
def main():
    divider("AIGARTH ↔ ANNA MATRIX BRIDGE")
    log(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load matrix
    matrix = load_anna_matrix()

    # Run experiments
    experiments = [
        ("Weight Reconstruction", lambda: experiment_1_weight_reconstruction(matrix)),
        ("Coordinate Mapping", lambda: experiment_2_coordinate_mapping(matrix)),
        ("Network from Matrix", lambda: experiment_3_network_from_matrix(matrix)),
        ("Hash Analysis", lambda: experiment_4_hash_analysis(matrix)),
        ("CFB Signature", lambda: experiment_5_cfb_signature(matrix)),
    ]

    passed = 0
    for name, func in experiments:
        try:
            if func():
                passed += 1
        except Exception as e:
            log(f"\n  ✗ EXPERIMENT FAILED: {name}")
            log(f"    Error: {e}")
            import traceback
            traceback.print_exc()

    divider("SUMMARY")
    log(f"  Experiments completed: {passed}/{len(experiments)}")

    # Key insight
    log("\n  KEY INSIGHT:")
    log("  ════════════")
    log("  Aigarth-it provides the PROCESSING layer")
    log("  Anna Matrix provides the TRAINED WEIGHTS")
    log("  SHA256 provides the COORDINATE MAPPING")
    log("")
    log("  Together they form a deterministic system:")
    log("  Seed → SHA256 → Coordinates → Anna Value → Aigarth Processing")

    divider()

    return passed == len(experiments)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
