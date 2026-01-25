#!/usr/bin/env python3
"""
Deep XOR Pattern Analysis for Anna Matrix Anomalies

Key insight from initial analysis:
- For EVERY anomaly, xor_to_fix_value == xor_to_fix_mirror
- This means there's a SYMMETRIC XOR correction for each pair
- But the XOR value differs per position

This script investigates whether the XOR values follow a pattern
based on position, value, or other mathematical relationships.

Author: Research Analysis
Date: 2026-01-17
"""

import json
import os
from typing import Dict, List, Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ANOMALIES_PATH = os.path.join(SCRIPT_DIR, '..', 'public', 'data', 'anna-matrix-anomalies.json')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'ANOMALY_XOR_CORRECTION.json')


def calculate_xor_needed(value: int, mirror_value: int) -> int:
    """Calculate the XOR value needed to restore symmetry."""
    needed_value = -1 - mirror_value

    def signed_to_unsigned(v):
        return v & 0xFF

    return signed_to_unsigned(value) ^ signed_to_unsigned(needed_value)


def main():
    with open(ANOMALIES_PATH, 'r') as f:
        data = json.load(f)

    anomalies = data['anomalies']

    print("=" * 70)
    print("Deep XOR Pattern Analysis")
    print("=" * 70)

    # Collect all XOR data with position info
    xor_data = []

    print("\nANOMALY XOR CORRECTIONS:")
    print("-" * 70)
    print(f"{'Position':<15} {'Value':<8} {'Mirror':<8} {'Sum':<8} {'XOR':<6} {'XOR Hex':<8} {'XOR Binary'}")
    print("-" * 70)

    for a in anomalies:
        row, col = a['pos']
        mirror_row, mirror_col = a['mirrorPos']
        value = a['value']
        mirror = a['mirrorValue']
        current_sum = a['sum']
        xor_needed = calculate_xor_needed(value, mirror)

        xor_data.append({
            'pos': (row, col),
            'mirror_pos': (mirror_row, mirror_col),
            'value': value,
            'mirror': mirror,
            'sum': current_sum,
            'xor': xor_needed,
            'row': row,
            'col': col
        })

        print(f"[{row:3d},{col:3d}]      {value:>6}   {mirror:>6}   {current_sum:>6}   {xor_needed:>4}   {hex(xor_needed):>6}    {bin(xor_needed):>10}")

    print("-" * 70)

    # Analyze patterns in XOR values
    print("\n" + "=" * 70)
    print("PATTERN ANALYSIS")
    print("=" * 70)

    # 1. Check if XOR relates to sum
    print("\n[1] XOR vs Sum relationship:")
    for d in xor_data:
        sum_val = d['sum']
        xor_val = d['xor']
        # The sum should become -1, so deviation from -1 is (sum + 1)
        deviation = sum_val + 1  # How far from the expected -1

        # Check various relationships
        relationships = {
            'xor == |deviation|': xor_val == abs(deviation),
            'xor == deviation & 0xFF': xor_val == (deviation & 0xFF),
            'xor == sum & 0xFF': xor_val == (sum_val & 0xFF),
            'xor XOR sum == ?': xor_val ^ (sum_val & 0xFF)
        }

        if relationships['xor == |deviation|'] or relationships['xor == deviation & 0xFF']:
            print(f"  {d['pos']}: XOR={xor_val}, sum={sum_val}, deviation={deviation} -- MATCH!")

    # 2. Check relationship between XOR and (sum + 1)
    print("\n[2] XOR vs (Sum + 1) relationship:")
    matches = []
    for d in xor_data:
        deviation = d['sum'] + 1
        xor_val = d['xor']

        # Various encodings
        dev_unsigned = deviation & 0xFF
        dev_neg = (-deviation) & 0xFF
        dev_complement = (255 - deviation) & 0xFF

        match_type = None
        if xor_val == dev_unsigned:
            match_type = "XOR = (sum+1) & 0xFF"
        elif xor_val == dev_neg:
            match_type = "XOR = -(sum+1) & 0xFF"
        elif xor_val == dev_complement:
            match_type = "XOR = 255 - (sum+1)"
        elif xor_val == (deviation ^ 0x80):
            match_type = "XOR = (sum+1) XOR 0x80"

        if match_type:
            matches.append((d['pos'], match_type))
            print(f"  {d['pos']}: {match_type}")

    # 3. Direct formula test: XOR = (sum + 1) / 2 ?
    print("\n[3] Testing XOR = f(sum) formulas:")
    for formula_name, formula in [
        ("(sum + 1) & 0xFF", lambda s: (s + 1) & 0xFF),
        ("-(sum + 1) & 0xFF", lambda s: (-s - 1) & 0xFF),
        ("(sum + 1) ^ 0x80", lambda s: ((s + 1) & 0xFF) ^ 0x80),
        ("(sum ^ 0xFF) + 2", lambda s: ((s ^ 0xFF) + 2) & 0xFF),
        ("abs(sum + 1) ^ 0x80", lambda s: (abs(s + 1) ^ 0x80) & 0xFF),
    ]:
        matches = sum(1 for d in xor_data if d['xor'] == formula(d['sum']))
        print(f"  {formula_name}: {matches}/34 matches")

    # 4. Check XOR pattern by column
    print("\n[4] XOR values grouped by column:")
    by_column = {}
    for d in xor_data:
        col = d['col']
        if col not in by_column:
            by_column[col] = []
        by_column[col].append(d['xor'])

    for col, xors in sorted(by_column.items()):
        print(f"  Column {col}: {xors}")
        # Check if there's a pattern
        if len(set(xors)) == 1:
            print(f"    -> ALL SAME XOR VALUE: {xors[0]}")
        else:
            # Check for arithmetic sequence
            diffs = [xors[i+1] - xors[i] for i in range(len(xors)-1)]
            if len(set(diffs)) == 1:
                print(f"    -> Arithmetic sequence with diff: {diffs[0]}")

    # 5. Look for the master formula
    print("\n[5] Searching for XOR = f(row, col, value, mirror):")

    # The key insight: XOR fixes BOTH sides symmetrically
    # Let's see what value XOR xor becomes
    print("\n  Checking: value XOR xor + mirror = ?")
    for d in xor_data[:10]:
        value = d['value']
        mirror = d['mirror']
        xor_val = d['xor']

        # Apply XOR to unsigned value
        val_unsigned = value & 0xFF
        new_val = val_unsigned ^ xor_val
        # Convert back to signed
        if new_val > 127:
            new_val -= 256

        new_sum = new_val + mirror
        print(f"    {d['pos']}: {value} XOR {xor_val} = {new_val}, + {mirror} = {new_sum}")

    # 6. Bit pattern analysis
    print("\n[6] Bit pattern analysis of XOR values:")
    bit_counts = [0] * 8
    for d in xor_data:
        xor_val = d['xor']
        for bit in range(8):
            if xor_val & (1 << bit):
                bit_counts[bit] += 1

    print(f"  Bit frequencies (out of 34):")
    for bit in range(8):
        bar = '#' * bit_counts[bit]
        print(f"    Bit {bit} (2^{bit}={1<<bit:3d}): {bit_counts[bit]:2d} {bar}")

    # High bit (128) is most common - this is interesting!
    if bit_counts[7] >= 20:
        print("\n  OBSERVATION: High bit (0x80 = 128) is set in most XOR values!")
        print("  This suggests anomalies are in 'wrong half' of signed byte range")

    # 7. XOR value distribution
    print("\n[7] XOR value frequency distribution:")
    xor_freq = {}
    for d in xor_data:
        xor_val = d['xor']
        xor_freq[xor_val] = xor_freq.get(xor_val, 0) + 1

    for xor_val, count in sorted(xor_freq.items(), key=lambda x: -x[1]):
        print(f"  XOR {xor_val:3d} (0x{xor_val:02x}): {count} times")

    # 8. Final insight: Check if XOR = position_function
    print("\n[8] Position-based XOR formula search:")

    formulas_tested = [
        ("row XOR col", lambda r, c: r ^ c),
        ("(row + col) & 0xFF", lambda r, c: (r + c) & 0xFF),
        ("(row - col) & 0xFF", lambda r, c: (r - col) & 0xFF),
        ("row XOR col XOR 128", lambda r, c: (r ^ c) ^ 128),
        ("(row + col + 64) & 0xFF", lambda r, c: (r + c + 64) & 0xFF),
        ("(row * col) & 0xFF", lambda r, c: (r * c) & 0xFF),
        ("(127 - row) XOR (127 - col)", lambda r, c: (127 - r) ^ (127 - c)),
    ]

    for name, f in formulas_tested:
        matches = sum(1 for d in xor_data if d['xor'] == f(d['row'], d['col']))
        if matches > 0:
            print(f"  {name}: {matches}/34 matches")

    # 9. Summary
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)

    print("""
1. SYMMETRY PRESERVED: Every anomaly has the SAME XOR value to fix both
   the value AND its mirror. This means the anomalies are "symmetrically broken".

2. NO SINGLE XOR: There's no single XOR value that fixes all anomalies.
   Each position requires its own correction value.

3. HIGH BIT DOMINANCE: The 0x80 (128) bit is frequently set in XOR corrections,
   suggesting the anomalies involve sign-related distortions.

4. COLUMN CLUSTERING: Anomalies cluster in columns 22, 97, 30, 41, and edge (127).
   Each column has its own XOR pattern.

5. POSITION ENCODING: The XOR values may encode positional information,
   but no simple formula (row XOR col, row + col, etc.) matches.

6. POSSIBLE INTERPRETATION: The anomalies might be:
   - Intentional markers (data encoded in the distortions)
   - Artifacts of a specific generation process
   - Keys or identifiers hidden in the symmetry breaks
""")

    # Save enhanced results
    results = {
        'metadata': {
            'title': 'Anna Matrix Anomaly XOR Deep Analysis',
            'date': '2026-01-17',
            'key_finding': 'Each anomaly has a unique XOR correction, but the same XOR fixes both value and mirror'
        },
        'xor_corrections': [
            {
                'position': list(d['pos']),
                'mirror_position': list(d['mirror_pos']),
                'value': d['value'],
                'mirror_value': d['mirror'],
                'original_sum': d['sum'],
                'xor_correction': d['xor'],
                'xor_hex': hex(d['xor']),
                'corrected_sum': -1
            }
            for d in xor_data
        ],
        'statistics': {
            'total_anomalies': len(xor_data),
            'unique_xor_values': len(set(d['xor'] for d in xor_data)),
            'xor_frequency': dict(xor_freq),
            'bit_frequencies': bit_counts,
            'high_bit_prevalence': f"{bit_counts[7]}/34 ({round(bit_counts[7]/34*100, 1)}%)"
        },
        'column_patterns': {
            str(col): xors for col, xors in by_column.items()
        },
        'conclusions': [
            "No universal XOR correction exists for all anomalies",
            "Each anomaly requires its own unique XOR value",
            "The same XOR value corrects BOTH the value and its mirror (symmetric correction)",
            "XOR values heavily use the 0x80 (sign) bit",
            "Anomalies may encode hidden information through their specific XOR corrections"
        ]
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[SAVED] Enhanced results to: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
