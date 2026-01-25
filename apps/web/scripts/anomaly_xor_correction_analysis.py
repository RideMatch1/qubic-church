#!/usr/bin/env python3
"""
Anna Matrix Anomaly XOR Correction Analysis

Investigates whether there's an XOR value that can "fix" the 68 anomaly cells
by restoring the point-symmetry property: value + mirror_value = -1

Author: Research Analysis
Date: 2026-01-17
"""

import json
import os
from typing import List, Dict, Tuple, Any

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MATRIX_PATH = os.path.join(SCRIPT_DIR, '..', 'public', 'data', 'anna-matrix.json')
ANOMALIES_PATH = os.path.join(SCRIPT_DIR, '..', 'public', 'data', 'anna-matrix-anomalies.json')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'ANOMALY_XOR_CORRECTION.json')


def load_data():
    """Load the Anna Matrix and anomaly data."""
    with open(MATRIX_PATH, 'r') as f:
        matrix = json.load(f)

    with open(ANOMALIES_PATH, 'r') as f:
        anomalies = json.load(f)

    return matrix, anomalies


def calculate_required_xor(value: int, mirror_value: int) -> Dict[str, Any]:
    """
    Calculate what XOR value would make value + mirror_value = -1

    If we XOR the value with X: (value XOR X) + mirror_value = -1
    => value XOR X = -1 - mirror_value
    => X = value XOR (-1 - mirror_value)

    Similarly if we XOR the mirror: value + (mirror_value XOR X) = -1
    => mirror_value XOR X = -1 - value
    => X = mirror_value XOR (-1 - value)
    """
    # What we need the value to become for symmetry
    needed_value = -1 - mirror_value
    needed_mirror = -1 - value

    # XOR to fix value side (treating as signed 8-bit)
    def signed_to_unsigned(v):
        return v & 0xFF

    def unsigned_to_signed(v):
        if v > 127:
            return v - 256
        return v

    # Calculate XOR values in unsigned space
    xor_for_value = signed_to_unsigned(value) ^ signed_to_unsigned(needed_value)
    xor_for_mirror = signed_to_unsigned(mirror_value) ^ signed_to_unsigned(needed_mirror)

    return {
        'current_sum': value + mirror_value,
        'needed_sum': -1,
        'value': value,
        'mirror_value': mirror_value,
        'needed_value': needed_value,
        'needed_mirror': needed_mirror,
        'xor_to_fix_value': xor_for_value,
        'xor_to_fix_mirror': xor_for_mirror,
        'xor_values_match': xor_for_value == xor_for_mirror
    }


def test_xor_value(anomalies: List[Dict], xor_val: int) -> Dict[str, Any]:
    """
    Test a specific XOR value against all anomalies.
    Count how many pairs become "fixed" (sum to -1 after XOR).
    """

    def signed_to_unsigned(v):
        return v & 0xFF

    def unsigned_to_signed(v):
        if v > 127:
            return v - 256
        return v

    fixed_pairs = []
    unfixed_pairs = []

    for anomaly in anomalies:
        value = anomaly['value']
        mirror_value = anomaly['mirrorValue']
        pos = anomaly['pos']
        mirror_pos = anomaly['mirrorPos']

        # Apply XOR to value (in unsigned space, then back to signed)
        xored_value = unsigned_to_signed(signed_to_unsigned(value) ^ xor_val)
        new_sum_v = xored_value + mirror_value

        # Apply XOR to mirror
        xored_mirror = unsigned_to_signed(signed_to_unsigned(mirror_value) ^ xor_val)
        new_sum_m = value + xored_mirror

        # Apply XOR to both
        new_sum_both = xored_value + xored_mirror

        pair_info = {
            'pos': pos,
            'mirror_pos': mirror_pos,
            'original_value': value,
            'original_mirror': mirror_value,
            'original_sum': value + mirror_value,
            'xored_value': xored_value,
            'xored_mirror': xored_mirror,
            'sum_after_xor_value': new_sum_v,
            'sum_after_xor_mirror': new_sum_m,
            'sum_after_xor_both': new_sum_both
        }

        # Check if any XOR application fixes this pair
        fixed_by_value = new_sum_v == -1
        fixed_by_mirror = new_sum_m == -1
        fixed_by_both = new_sum_both == -1

        pair_info['fixed_by_value'] = fixed_by_value
        pair_info['fixed_by_mirror'] = fixed_by_mirror
        pair_info['fixed_by_both'] = fixed_by_both

        if fixed_by_value or fixed_by_mirror or fixed_by_both:
            fixed_pairs.append(pair_info)
        else:
            unfixed_pairs.append(pair_info)

    return {
        'xor_value': xor_val,
        'xor_value_hex': hex(xor_val),
        'xor_value_binary': bin(xor_val),
        'total_anomalies': len(anomalies),
        'fixed_count': len(fixed_pairs),
        'unfixed_count': len(unfixed_pairs),
        'fix_percentage': round(len(fixed_pairs) / len(anomalies) * 100, 2) if anomalies else 0,
        'fixed_by_value_xor': sum(1 for p in fixed_pairs if p['fixed_by_value']),
        'fixed_by_mirror_xor': sum(1 for p in fixed_pairs if p['fixed_by_mirror']),
        'fixed_by_both_xor': sum(1 for p in fixed_pairs if p['fixed_by_both']),
        'fixed_pairs': fixed_pairs[:5],  # Sample
        'unfixed_pairs': unfixed_pairs[:5]  # Sample
    }


def find_common_xor_patterns(anomalies: List[Dict]) -> Dict[str, Any]:
    """
    Analyze all anomalies to find if there's a common XOR pattern.
    """
    xor_counts = {}
    xor_details = {}

    for anomaly in anomalies:
        result = calculate_required_xor(anomaly['value'], anomaly['mirrorValue'])

        xor_v = result['xor_to_fix_value']
        xor_m = result['xor_to_fix_mirror']

        # Count occurrences
        xor_counts[xor_v] = xor_counts.get(xor_v, 0) + 1
        xor_counts[xor_m] = xor_counts.get(xor_m, 0) + 1

        # Store details
        key = f"{anomaly['pos']}"
        xor_details[key] = {
            'pos': anomaly['pos'],
            'mirror_pos': anomaly['mirrorPos'],
            'value': anomaly['value'],
            'mirror_value': anomaly['mirrorValue'],
            'current_sum': result['current_sum'],
            'xor_to_fix_value': xor_v,
            'xor_to_fix_mirror': xor_m,
            'xor_match': result['xor_values_match']
        }

    # Sort by frequency
    sorted_xors = sorted(xor_counts.items(), key=lambda x: -x[1])

    return {
        'xor_frequency': dict(sorted_xors[:20]),
        'most_common_xor': sorted_xors[0] if sorted_xors else None,
        'unique_xor_values': len(xor_counts),
        'anomaly_details': xor_details
    }


def analyze_sum_patterns(anomalies: List[Dict]) -> Dict[str, Any]:
    """
    Analyze the sum patterns of anomalies to find regularities.
    """
    sums = [a['sum'] for a in anomalies]
    sum_counts = {}
    for s in sums:
        sum_counts[s] = sum_counts.get(s, 0) + 1

    # Check for patterns with +1 (since symmetric should be -1)
    deviation_from_neg1 = [s - (-1) for s in sums]

    return {
        'unique_sums': len(set(sums)),
        'sum_frequency': dict(sorted(sum_counts.items(), key=lambda x: -x[1])),
        'sum_range': [min(sums), max(sums)],
        'sums_with_127': [a for a in anomalies if a['sum'] == 127],
        'sums_with_neg127': [a for a in anomalies if a['sum'] == -127],
        'deviations': deviation_from_neg1
    }


def brute_force_xor_search(anomalies: List[Dict]) -> Dict[str, Any]:
    """
    Brute force search for XOR values 0-255 to find best corrections.
    """
    best_results = []

    for xor_val in range(256):
        result = test_xor_value(anomalies, xor_val)
        best_results.append({
            'xor': xor_val,
            'xor_hex': hex(xor_val),
            'fixed': result['fixed_count'],
            'by_value': result['fixed_by_value_xor'],
            'by_mirror': result['fixed_by_mirror_xor'],
            'by_both': result['fixed_by_both_xor']
        })

    # Sort by most fixes
    best_results.sort(key=lambda x: -x['fixed'])

    return {
        'best_10': best_results[:10],
        'perfect_fix_found': any(r['fixed'] == len(anomalies) for r in best_results),
        'max_fixes': best_results[0]['fixed'] if best_results else 0
    }


def main():
    print("=" * 60)
    print("Anna Matrix Anomaly XOR Correction Analysis")
    print("=" * 60)

    # Load data
    matrix, anomalies_data = load_data()
    anomalies = anomalies_data['anomalies']

    print(f"\nLoaded {len(anomalies)} anomalies (34 pairs expected)")

    results = {
        'metadata': {
            'title': 'Anna Matrix Anomaly XOR Correction Analysis',
            'date': '2026-01-17',
            'purpose': 'Find XOR value(s) that restore point-symmetry to anomalous cells',
            'total_anomalies': len(anomalies),
            'expected_symmetry': 'value + mirror_value = -1'
        }
    }

    # 1. Analyze required XOR patterns
    print("\n[1] Analyzing required XOR patterns...")
    xor_patterns = find_common_xor_patterns(anomalies)
    results['xor_pattern_analysis'] = xor_patterns

    print(f"  - Unique XOR values needed: {xor_patterns['unique_xor_values']}")
    if xor_patterns['most_common_xor']:
        mc = xor_patterns['most_common_xor']
        print(f"  - Most common XOR: {mc[0]} (hex: {hex(mc[0])}) appears {mc[1]} times")

    # 2. Test specific XOR values
    print("\n[2] Testing specific XOR values...")
    test_values = [0, 7, 13, 27, 33, 100, 121, 127, 255, 128, 1, 64, 32, 16, 8, 4, 2]
    specific_tests = {}

    for xor_val in test_values:
        result = test_xor_value(anomalies, xor_val)
        specific_tests[str(xor_val)] = result
        print(f"  - XOR {xor_val:3d} ({hex(xor_val):>4s}): fixes {result['fixed_count']:2d}/{len(anomalies)} anomalies")

    results['specific_xor_tests'] = specific_tests

    # 3. Brute force search
    print("\n[3] Brute force search (0-255)...")
    brute_force = brute_force_xor_search(anomalies)
    results['brute_force_search'] = brute_force

    print(f"  - Best XOR value: {brute_force['best_10'][0]['xor']} fixes {brute_force['best_10'][0]['fixed']} anomalies")
    print(f"  - Perfect fix found: {brute_force['perfect_fix_found']}")

    # 4. Analyze sum patterns
    print("\n[4] Analyzing sum patterns...")
    sum_patterns = analyze_sum_patterns(anomalies)
    results['sum_pattern_analysis'] = sum_patterns

    print(f"  - Unique sums: {sum_patterns['unique_sums']}")
    print(f"  - Sum range: {sum_patterns['sum_range']}")
    print(f"  - Anomalies with sum=127: {len(sum_patterns['sums_with_127'])}")
    print(f"  - Anomalies with sum=-127: {len(sum_patterns['sums_with_neg127'])}")

    # 5. Special analysis: Check if XOR works differently per column
    print("\n[5] Per-column XOR analysis...")
    column_22_anomalies = [a for a in anomalies if a['pos'][1] == 22]
    column_97_anomalies = [a for a in anomalies if a['pos'][1] == 97]
    column_30_anomalies = [a for a in anomalies if a['pos'][1] == 30]

    column_analysis = {}

    for col, col_anomalies, name in [
        (22, column_22_anomalies, 'column_22'),
        (97, column_97_anomalies, 'column_97'),
        (30, column_30_anomalies, 'column_30')
    ]:
        if col_anomalies:
            col_brute = brute_force_xor_search(col_anomalies)
            column_analysis[name] = {
                'anomaly_count': len(col_anomalies),
                'best_xor': col_brute['best_10'][0] if col_brute['best_10'] else None,
                'perfect_fix': col_brute['perfect_fix_found']
            }
            print(f"  - Column {col}: {len(col_anomalies)} anomalies, best XOR fixes {column_analysis[name]['best_xor']['fixed'] if column_analysis[name]['best_xor'] else 0}")

    results['per_column_analysis'] = column_analysis

    # 6. Check for position-dependent XOR
    print("\n[6] Checking position-dependent XOR patterns...")
    position_xor = []
    for anomaly in anomalies:
        row, col = anomaly['pos']
        xor_info = calculate_required_xor(anomaly['value'], anomaly['mirrorValue'])

        # Check if XOR value relates to position
        xor_v = xor_info['xor_to_fix_value']
        position_xor.append({
            'pos': [row, col],
            'xor_needed': xor_v,
            'xor_equals_row': xor_v == row,
            'xor_equals_col': xor_v == col,
            'xor_equals_row_xor_col': xor_v == (row ^ col),
            'xor_equals_row_plus_col': xor_v == ((row + col) & 0xFF),
            'xor_mod_128': xor_v % 128,
            'row_mod_128': row % 128,
            'col_mod_128': col % 128
        })

    position_correlations = {
        'xor_equals_row': sum(1 for p in position_xor if p['xor_equals_row']),
        'xor_equals_col': sum(1 for p in position_xor if p['xor_equals_col']),
        'xor_equals_row_xor_col': sum(1 for p in position_xor if p['xor_equals_row_xor_col']),
        'xor_equals_row_plus_col': sum(1 for p in position_xor if p['xor_equals_row_plus_col']),
        'samples': position_xor[:10]
    }
    results['position_xor_analysis'] = position_correlations

    print(f"  - XOR = row: {position_correlations['xor_equals_row']}")
    print(f"  - XOR = col: {position_correlations['xor_equals_col']}")
    print(f"  - XOR = row XOR col: {position_correlations['xor_equals_row_xor_col']}")
    print(f"  - XOR = (row + col) mod 256: {position_correlations['xor_equals_row_plus_col']}")

    # 7. Summary and conclusions
    print("\n" + "=" * 60)
    print("CONCLUSIONS")
    print("=" * 60)

    conclusions = []

    if brute_force['perfect_fix_found']:
        conclusions.append("MAJOR DISCOVERY: A single XOR value fixes ALL anomalies!")
        conclusions.append(f"The universal XOR correction value is: {brute_force['best_10'][0]['xor']}")
    else:
        conclusions.append(f"No single XOR value fixes all anomalies")
        conclusions.append(f"Best XOR value {brute_force['best_10'][0]['xor']} fixes only {brute_force['best_10'][0]['fixed']}/{len(anomalies)}")

        # Check if different columns need different XOR values
        if column_analysis:
            col_fixes = [
                (name, data['best_xor']['xor'])
                for name, data in column_analysis.items()
                if data.get('best_xor') and data.get('perfect_fix')
            ]
            if col_fixes:
                conclusions.append("Different columns may need different XOR values:")
                for name, xor_val in col_fixes:
                    conclusions.append(f"  - {name}: XOR {xor_val}")

    # Check for 127-related patterns
    if sum_patterns['sums_with_127']:
        conclusions.append(f"Interesting: {len(sum_patterns['sums_with_127'])} anomalies sum to 127 (complement of -128)")

    if sum_patterns['sums_with_neg127']:
        conclusions.append(f"Interesting: {len(sum_patterns['sums_with_neg127'])} anomalies sum to -127 (complement of 126)")

    results['conclusions'] = conclusions

    for c in conclusions:
        print(f"  {c}")

    # Save results
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[SAVED] Results written to: {OUTPUT_PATH}")

    return results


if __name__ == '__main__':
    main()
