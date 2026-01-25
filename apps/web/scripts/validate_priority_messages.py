#!/usr/bin/env python3
"""
DEEP MESSAGE VALIDATION - PHASE 1
=================================
Rigorose statistische Validierung aller behaupteten versteckten Nachrichten.
Verwendet Monte-Carlo Simulation für p-Wert Berechnung.

KEINE HALLUZINATIONEN - nur verifizierte Fakten!

Author: Claude Code Research Agent
Date: 2026-01-17
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
import random
import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================
MONTE_CARLO_ITERATIONS = 10000
SIGNIFICANCE_THRESHOLD = 0.001  # p < 0.001 für signifikant

# =============================================================================
# LOAD MATRIX
# =============================================================================
script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

print("=" * 70)
print("DEEP MESSAGE VALIDATION - PHASE 1")
print("=" * 70)
print(f"Loading matrix from: {matrix_path}")

with open(matrix_path) as f:
    data = json.load(f)

raw_matrix = data["matrix"]

# Helper function to safely convert to integer
def safe_int(v):
    """Convert value to integer, treating strings as 0"""
    if isinstance(v, str):
        return 0
    return int(v)

# Create integer matrix
matrix = np.zeros((128, 128), dtype=int)
string_cells = []
for r in range(128):
    for c in range(128):
        val = raw_matrix[r][c]
        if isinstance(val, str):
            string_cells.append((r, c, val))
            matrix[r][c] = 0
        else:
            matrix[r][c] = int(val)

print(f"Matrix dimensions: {matrix.shape}")
print(f"String cells found: {len(string_cells)}")
print(f"Value range: [{matrix.min()}, {matrix.max()}]")

results = {
    "validation_timestamp": datetime.datetime.now().isoformat(),
    "monte_carlo_iterations": MONTE_CARLO_ITERATIONS,
    "significance_threshold": SIGNIFICANCE_THRESHOLD,
    "matrix_info": {
        "dimensions": "128x128",
        "total_cells": 16384,
        "string_cells": len(string_cells),
        "min_value": int(matrix.min()),
        "max_value": int(matrix.max())
    },
    "validations": {}
}

# =============================================================================
# VALIDATION 1: CFB in Letter Stream
# =============================================================================
print("\n" + "=" * 70)
print("VALIDATION 1: 'CFB' in Letter Stream")
print("=" * 70)

def validate_cfb():
    """
    Claim: 'cfb' appears at position 854 in the letter stream

    Method:
    1. Extract all letters from matrix (lower 7 bits → ASCII letters)
    2. Search for 'cfb'
    3. Monte-Carlo: How often does 'cfb' appear in random stream of same length?
    """
    # Extract letter stream
    letters = []
    for r in range(128):
        for c in range(128):
            val = matrix[r][c]
            # Get lower 7 bits
            ascii_val = val & 0x7F
            if 65 <= ascii_val <= 90 or 97 <= ascii_val <= 122:  # A-Z or a-z
                letters.append(chr(ascii_val).lower())

    letter_stream = ''.join(letters)
    stream_len = len(letter_stream)

    print(f"Letter stream length: {stream_len}")

    # Find 'cfb'
    cfb_positions = []
    pos = 0
    while True:
        pos = letter_stream.find('cfb', pos)
        if pos == -1:
            break
        cfb_positions.append(pos)
        pos += 1

    cfb_count = len(cfb_positions)
    print(f"'cfb' found at positions: {cfb_positions}")
    print(f"Total occurrences: {cfb_count}")

    # Also check reversed stream
    reversed_stream = letter_stream[::-1]
    cfb_reversed_positions = []
    pos = 0
    while True:
        pos = reversed_stream.find('cfb', pos)
        if pos == -1:
            break
        cfb_reversed_positions.append(pos)
        pos += 1

    print(f"'cfb' in reversed stream: {len(cfb_reversed_positions)} times")

    # Monte-Carlo Simulation
    print(f"\nRunning Monte-Carlo simulation ({MONTE_CARLO_ITERATIONS} iterations)...")

    # First, get the letter frequency distribution from actual stream
    letter_freq = Counter(letter_stream)
    total_letters = sum(letter_freq.values())
    letter_probs = {k: v/total_letters for k, v in letter_freq.items()}
    letters_list = list(letter_probs.keys())
    probs_list = list(letter_probs.values())

    random_hits = 0
    random_counts = []

    for i in range(MONTE_CARLO_ITERATIONS):
        # Generate random stream with same letter distribution
        random_stream = ''.join(random.choices(letters_list, weights=probs_list, k=stream_len))
        count = random_stream.count('cfb')
        random_counts.append(count)
        if count >= cfb_count:
            random_hits += 1

        if (i + 1) % 2000 == 0:
            print(f"  Progress: {i+1}/{MONTE_CARLO_ITERATIONS}")

    p_value = random_hits / MONTE_CARLO_ITERATIONS

    print(f"\nResults:")
    print(f"  Observed 'cfb' count: {cfb_count}")
    print(f"  Random streams with >= {cfb_count} 'cfb': {random_hits}/{MONTE_CARLO_ITERATIONS}")
    print(f"  p-value: {p_value}")
    print(f"  Significant (p < {SIGNIFICANCE_THRESHOLD}): {p_value < SIGNIFICANCE_THRESHOLD}")

    # Additional statistics
    print(f"\nRandom stream 'cfb' statistics:")
    print(f"  Mean: {np.mean(random_counts):.2f}")
    print(f"  Max: {max(random_counts)}")
    print(f"  Streams with 0 'cfb': {random_counts.count(0)}")
    print(f"  Streams with 1+ 'cfb': {sum(1 for c in random_counts if c >= 1)}")

    return {
        "claim": "CFB appears in letter stream",
        "stream_length": stream_len,
        "observed_positions": cfb_positions,
        "observed_count": cfb_count,
        "reversed_count": len(cfb_reversed_positions),
        "monte_carlo_hits": random_hits,
        "monte_carlo_mean": float(np.mean(random_counts)),
        "monte_carlo_max": max(random_counts),
        "p_value": p_value,
        "significant": p_value < SIGNIFICANCE_THRESHOLD,
        "verdict": "VALIDATED" if p_value < SIGNIFICANCE_THRESHOLD else "NOT SIGNIFICANT - likely random"
    }

results["validations"]["cfb"] = validate_cfb()

# =============================================================================
# VALIDATION 2: Point Symmetry 99.59%
# =============================================================================
print("\n" + "=" * 70)
print("VALIDATION 2: 99.59% Point Symmetry")
print("=" * 70)

def validate_symmetry():
    """
    Claim: Matrix has 99.59% point symmetry around center (63.5, 63.5)

    Property: matrix[r][c] + matrix[127-r][127-c] = -1

    Method:
    1. Count how many cell pairs satisfy the symmetry property
    2. Compare against random matrices
    """
    symmetric_count = 0
    asymmetric_positions = []

    for r in range(128):
        for c in range(128):
            val1 = matrix[r][c]
            val2 = matrix[127-r][127-c]
            if val1 + val2 == -1:
                symmetric_count += 1
            else:
                asymmetric_positions.append({
                    "pos1": (r, c),
                    "pos2": (127-r, 127-c),
                    "val1": int(val1),
                    "val2": int(val2),
                    "sum": int(val1 + val2)
                })

    total = 128 * 128
    symmetry_pct = symmetric_count / total * 100

    print(f"Symmetric pairs: {symmetric_count}/{total}")
    print(f"Symmetry percentage: {symmetry_pct:.4f}%")
    print(f"Asymmetric positions: {len(asymmetric_positions)}")

    # Show first few asymmetric positions
    print("\nFirst 10 asymmetric positions:")
    for ap in asymmetric_positions[:10]:
        print(f"  {ap['pos1']} <-> {ap['pos2']}: {ap['val1']} + {ap['val2']} = {ap['sum']}")

    # Monte-Carlo: Random matrices
    print(f"\nRunning Monte-Carlo simulation ({MONTE_CARLO_ITERATIONS} iterations)...")

    random_symmetry_rates = []

    for i in range(min(1000, MONTE_CARLO_ITERATIONS)):  # Use 1000 for speed
        rand_matrix = np.random.randint(-128, 128, (128, 128))
        sym_count = 0
        for r in range(128):
            for c in range(128):
                if rand_matrix[r][c] + rand_matrix[127-r][127-c] == -1:
                    sym_count += 1
        random_symmetry_rates.append(sym_count / total * 100)

        if (i + 1) % 200 == 0:
            print(f"  Progress: {i+1}/1000")

    # p-value: How often does random matrix achieve >= observed symmetry?
    p_value = sum(1 for r in random_symmetry_rates if r >= symmetry_pct) / len(random_symmetry_rates)

    print(f"\nResults:")
    print(f"  Observed symmetry: {symmetry_pct:.4f}%")
    print(f"  Random mean: {np.mean(random_symmetry_rates):.4f}%")
    print(f"  Random max: {max(random_symmetry_rates):.4f}%")
    print(f"  Random min: {min(random_symmetry_rates):.4f}%")
    print(f"  p-value: {p_value}")
    print(f"  Significant (p < {SIGNIFICANCE_THRESHOLD}): {p_value < SIGNIFICANCE_THRESHOLD}")

    # This should be EXTREMELY significant - random matrices have ~0.39% symmetry
    expected_random = 100 / 256  # 1/256 chance of val1 + val2 = -1 for random
    print(f"\n  Expected random symmetry: ~{expected_random:.2f}%")
    print(f"  Observed is {symmetry_pct / expected_random:.0f}x higher than random!")

    return {
        "claim": "99.59% point symmetry",
        "observed_symmetry_pct": symmetry_pct,
        "symmetric_pairs": symmetric_count,
        "asymmetric_pairs": len(asymmetric_positions),
        "asymmetric_positions_sample": asymmetric_positions[:20],
        "random_mean": float(np.mean(random_symmetry_rates)),
        "random_max": float(max(random_symmetry_rates)),
        "random_min": float(min(random_symmetry_rates)),
        "expected_random": expected_random,
        "observed_vs_random_ratio": symmetry_pct / expected_random,
        "p_value": p_value,
        "significant": p_value < SIGNIFICANCE_THRESHOLD,
        "verdict": "VALIDATED - This is NOT random" if p_value < SIGNIFICANCE_THRESHOLD else "UNEXPECTED"
    }

results["validations"]["symmetry"] = validate_symmetry()

# =============================================================================
# VALIDATION 3: AI MEG in Pair 30↔97
# =============================================================================
print("\n" + "=" * 70)
print("VALIDATION 3: 'AI MEG' in Column Pair 30↔97")
print("=" * 70)

def validate_ai_meg():
    """
    Claim: XOR of columns 30 and 97 contains 'AI', 'MEG', 'GOU'

    Method:
    1. Calculate XOR for all 128 rows
    2. Convert to ASCII
    3. Search for claimed words
    4. Monte-Carlo: How often do these words appear in random XOR pairs?
    """
    # Calculate XOR for pair 30↔97
    xor_values = []
    xor_chars = []

    for r in range(128):
        val_30 = matrix[r][30]
        val_97 = matrix[r][97]
        xor_val = (val_30 & 0xFF) ^ (val_97 & 0xFF)
        xor_values.append(xor_val)

        # Convert to printable ASCII
        if 32 <= xor_val <= 126:
            xor_chars.append(chr(xor_val))
        else:
            xor_chars.append('.')

    xor_text = ''.join(xor_chars)
    xor_text_upper = xor_text.upper()

    print(f"XOR text (pair 30↔97):")
    print(f"  {xor_text}")

    # Search for patterns
    patterns = ['AI', 'MEG', 'GOU', 'KC', 'IO', 'OI']
    found_patterns = {}

    for pattern in patterns:
        positions = []
        pos = 0
        while True:
            pos = xor_text_upper.find(pattern, pos)
            if pos == -1:
                break
            positions.append(pos)
            pos += 1
        found_patterns[pattern] = positions
        if positions:
            print(f"  '{pattern}' found at positions: {positions}")

    # Monte-Carlo: Check random column pairs
    print(f"\nRunning Monte-Carlo simulation for random column pairs...")

    pattern_hits = {p: 0 for p in patterns}

    for i in range(min(5000, MONTE_CARLO_ITERATIONS)):
        # Pick two random columns
        col1, col2 = random.sample(range(128), 2)

        # Calculate XOR
        random_xor_text = ''
        for r in range(128):
            xor_val = (matrix[r][col1] & 0xFF) ^ (matrix[r][col2] & 0xFF)
            if 32 <= xor_val <= 126:
                random_xor_text += chr(xor_val)
            else:
                random_xor_text += '.'

        random_text_upper = random_xor_text.upper()

        for pattern in patterns:
            if pattern in random_text_upper:
                pattern_hits[pattern] += 1

        if (i + 1) % 1000 == 0:
            print(f"  Progress: {i+1}/5000")

    print(f"\nPattern frequency in random column pairs:")
    for pattern, hits in pattern_hits.items():
        p_val = hits / 5000
        print(f"  '{pattern}': {hits}/5000 = {p_val:.4f}")

    # Calculate combined p-value for finding AI AND MEG in same pair
    ai_and_meg_count = 0
    for i in range(5000):
        col1, col2 = random.sample(range(128), 2)
        random_xor_text = ''
        for r in range(128):
            xor_val = (matrix[r][col1] & 0xFF) ^ (matrix[r][col2] & 0xFF)
            if 32 <= xor_val <= 126:
                random_xor_text += chr(xor_val)
            else:
                random_xor_text += '.'
        if 'AI' in random_xor_text.upper() and 'MEG' in random_xor_text.upper():
            ai_and_meg_count += 1

    combined_p_value = ai_and_meg_count / 5000
    print(f"\n  'AI' AND 'MEG' together: {ai_and_meg_count}/5000 = {combined_p_value:.4f}")

    # Verdict
    ai_found = len(found_patterns.get('AI', [])) > 0
    meg_found = len(found_patterns.get('MEG', [])) > 0

    return {
        "claim": "AI MEG in column pair 30-97",
        "xor_text": xor_text,
        "xor_text_printable": ''.join(c for c in xor_text if c != '.'),
        "patterns_found": {k: v for k, v in found_patterns.items() if v},
        "ai_found": ai_found,
        "meg_found": meg_found,
        "gou_found": len(found_patterns.get('GOU', [])) > 0,
        "pattern_random_frequencies": {p: h/5000 for p, h in pattern_hits.items()},
        "combined_p_value": combined_p_value,
        "significant": combined_p_value < SIGNIFICANCE_THRESHOLD,
        "verdict": "NEEDS DEEPER ANALYSIS - Short words have higher random probability"
    }

results["validations"]["ai_meg"] = validate_ai_meg()

# =============================================================================
# VALIDATION 4: XOR Triangle {100, 27, 127}
# =============================================================================
print("\n" + "=" * 70)
print("VALIDATION 4: XOR Triangle {100, 27, 127}")
print("=" * 70)

def validate_xor_triangle():
    """
    Claim: Values 100, 27, 127 form a closed XOR triangle
           AND position [22,22] contains value 100

    Method:
    1. Verify XOR properties (mathematically trivial)
    2. Check if position [22,22] really contains 100
    3. Check how special position [22,22] is
    """
    # Verify XOR properties
    xor_checks = {
        "100 XOR 27 = 127": (100 ^ 27) == 127,
        "100 XOR 127 = 27": (100 ^ 127) == 27,
        "27 XOR 127 = 100": (27 ^ 127) == 100
    }

    print("XOR Triangle verification:")
    for desc, result in xor_checks.items():
        print(f"  {desc}: {result}")

    all_xor_valid = all(xor_checks.values())

    # Check position [22,22]
    value_at_22_22 = matrix[22][22]
    print(f"\nValue at position [22,22]: {value_at_22_22}")
    print(f"Is 100: {value_at_22_22 == 100}")

    # Count how many cells contain 100
    cells_with_100 = []
    for r in range(128):
        for c in range(128):
            if matrix[r][c] == 100:
                cells_with_100.append((r, c))

    print(f"\nTotal cells with value 100: {len(cells_with_100)}")
    print(f"First 10 positions: {cells_with_100[:10]}")

    # Is [22,22] on the main diagonal?
    is_diagonal = True  # 22 == 22
    print(f"\n[22,22] is on main diagonal: {is_diagonal}")

    # Check diagonal positions
    diagonal_values = [matrix[i][i] for i in range(128)]
    diagonal_100_positions = [i for i, v in enumerate(diagonal_values) if v == 100]
    print(f"Diagonal positions with 100: {diagonal_100_positions}")

    # Significance: Is having 100 at [22,22] special?
    # 22 = 2 * 11, and 11 is a Qubic-related number
    print(f"\nPosition significance:")
    print(f"  22 = 2 × 11 (Qubic number)")
    print(f"  22 + 22 = 44 = 4 × 11")
    print(f"  Value 100 = 10² (perfect square)")
    print(f"  100 = ASCII 'd' (decode?)")

    return {
        "claim": "XOR Triangle {100, 27, 127} at position [22,22]",
        "xor_properties_valid": all_xor_valid,
        "xor_checks": xor_checks,
        "value_at_22_22": int(value_at_22_22),
        "is_100": value_at_22_22 == 100,
        "total_cells_with_100": len(cells_with_100),
        "cells_with_100_sample": cells_with_100[:20],
        "diagonal_positions_with_100": diagonal_100_positions,
        "on_main_diagonal": is_diagonal,
        "significant": value_at_22_22 == 100 and all_xor_valid,
        "verdict": "VALIDATED - Mathematical property confirmed" if value_at_22_22 == 100 else "NOT VALIDATED - Position [22,22] does not contain 100"
    }

results["validations"]["xor_triangle"] = validate_xor_triangle()

# =============================================================================
# VALIDATION 5: 127 Formula (Col1 + Col2 = 127)
# =============================================================================
print("\n" + "=" * 70)
print("VALIDATION 5: 127 Formula (Column Pairs Sum to 127)")
print("=" * 70)

def validate_127_formula():
    """
    Claim: All 64 column pairs satisfy Col1 + Col2 = 127

    Method:
    1. Enumerate all pairs where col1 + col2 = 127
    2. Verify there are exactly 64 such pairs
    """
    pairs = []
    for col1 in range(64):
        col2 = 127 - col1
        pairs.append((col1, col2))

    print(f"Total column pairs where Col1 + Col2 = 127: {len(pairs)}")
    print(f"First 10 pairs: {pairs[:10]}")
    print(f"Last 10 pairs: {pairs[-10:]}")

    # This is mathematically guaranteed
    is_valid = len(pairs) == 64 and all(c1 + c2 == 127 for c1, c2 in pairs)

    print(f"\nAll pairs satisfy Col1 + Col2 = 127: {is_valid}")

    # Note: This is a STRUCTURAL property, not a statistical one
    # It's a consequence of 128-column matrix and choosing pairs that sum to 127

    return {
        "claim": "All 64 column pairs sum to 127",
        "total_pairs": len(pairs),
        "all_valid": is_valid,
        "pairs_sample": pairs[:10] + pairs[-10:],
        "verdict": "VALIDATED - Structural property (not statistical)",
        "note": "This is a mathematical definition, not a discovery"
    }

results["validations"]["127_formula"] = validate_127_formula()

# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("FINAL VALIDATION SUMMARY")
print("=" * 70)

summary = {
    "total_validations": len(results["validations"]),
    "validated": [],
    "not_validated": [],
    "needs_more_analysis": []
}

for name, validation in results["validations"].items():
    verdict = validation.get("verdict", "UNKNOWN")
    if "VALIDATED" in verdict:
        summary["validated"].append(name)
    elif "NOT SIGNIFICANT" in verdict or "NOT VALIDATED" in verdict:
        summary["not_validated"].append(name)
    else:
        summary["needs_more_analysis"].append(name)

print(f"\n✓ VALIDATED ({len(summary['validated'])}):")
for name in summary["validated"]:
    print(f"    - {name}: {results['validations'][name]['verdict']}")

print(f"\n✗ NOT VALIDATED ({len(summary['not_validated'])}):")
for name in summary["not_validated"]:
    print(f"    - {name}: {results['validations'][name]['verdict']}")

print(f"\n? NEEDS MORE ANALYSIS ({len(summary['needs_more_analysis'])}):")
for name in summary["needs_more_analysis"]:
    print(f"    - {name}: {results['validations'][name]['verdict']}")

results["summary"] = summary

# =============================================================================
# SAVE RESULTS
# =============================================================================
output_path = script_dir / "PRIORITY_VALIDATION_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n✓ Results saved to: {output_path}")
print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)
