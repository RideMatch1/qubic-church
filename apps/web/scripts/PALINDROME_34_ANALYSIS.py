"""
PALINDROME_34_ANALYSIS.py
=========================
Extracts and analyzes the 68 asymmetric cells from the 128x128 Anna Matrix.

The matrix has near-perfect point symmetry: M[r,c] + M[127-r,127-c] = -1 for most cells.
The 68 exceptions (asymmetric cells) are found in 4 column pairs: {0,127}, {22,105}, {30,97}, {41,86}.
Due to palindromic symmetry, these 68 cells yield 34 independent values.

This script:
1. Loads the matrix and identifies all asymmetric cells
2. Extracts the 34 independent values
3. Performs multiple analyses: ASCII, constants, patterns, coordinates, statistics
4. Saves all results to PALINDROME_34_RESULTS.json
"""

import json
import os
import math
import statistics
from collections import Counter

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
MATRIX_PATH = os.path.join(PROJECT_ROOT, 'apps', 'web', 'public', 'data', 'anna-matrix.json')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'PALINDROME_34_RESULTS.json')

EXPECTED_COL_PAIRS = [{0, 127}, {22, 105}, {30, 97}, {41, 86}]


def load_matrix():
    with open(MATRIX_PATH, 'r') as f:
        data = json.load(f)
    matrix = data['matrix']
    assert len(matrix) == 128
    for i, row in enumerate(matrix):
        assert len(row) == 128
    # Fix string values (some cells are "00000000" instead of 0)
    for r in range(128):
        for c in range(128):
            if isinstance(matrix[r][c], str):
                matrix[r][c] = int(matrix[r][c])
    return matrix


def find_asymmetric_pairs(matrix):
    pairs = []
    checked = set()
    for r in range(128):
        for c in range(128):
            mr, mc = 127 - r, 127 - c
            pair_key = tuple(sorted([(r, c), (mr, mc)]))
            if pair_key in checked:
                continue
            checked.add(pair_key)
            val = matrix[r][c]
            mirror_val = matrix[mr][mc]
            s = val + mirror_val
            if s != -1:
                if r < mr or (r == mr and c < mc):
                    pairs.append({
                        'primary': {'row': r, 'col': c, 'value': val},
                        'mirror': {'row': mr, 'col': mc, 'value': mirror_val},
                        'sum': s,
                    })
                else:
                    pairs.append({
                        'primary': {'row': mr, 'col': mc, 'value': mirror_val},
                        'mirror': {'row': r, 'col': c, 'value': val},
                        'sum': s,
                    })
    pairs.sort(key=lambda x: (x['primary']['row'], x['primary']['col']))
    return pairs


def find_all_asymmetric_cells(matrix):
    asymmetric = []
    checked = set()
    for r in range(128):
        for c in range(128):
            mr, mc = 127 - r, 127 - c
            pair_key = tuple(sorted([(r, c), (mr, mc)]))
            if pair_key in checked:
                continue
            checked.add(pair_key)
            val = matrix[r][c]
            mirror_val = matrix[mr][mc]
            s = val + mirror_val
            if s != -1:
                asymmetric.append({'row': r, 'col': c, 'value': val,
                    'mirror_row': mr, 'mirror_col': mc, 'mirror_value': mirror_val, 'sum': s})
                asymmetric.append({'row': mr, 'col': mc, 'value': mirror_val,
                    'mirror_row': r, 'mirror_col': c, 'mirror_value': val, 'sum': s})
    asymmetric.sort(key=lambda x: (x['row'], x['col']))
    return asymmetric


def ascii_analysis(values):
    results = {'direct': '', 'direct_printable': '', 'offset_plus_128': '', 'absolute': '', 'mod_128': ''}
    for v in values:
        if 32 <= v <= 126: results['direct'] += chr(v); results['direct_printable'] += chr(v)
        elif 0 <= v <= 127: results['direct'] += chr(v); results['direct_printable'] += '.'
        else: results['direct'] += '?'; results['direct_printable'] += '?'
        shifted = v + 128
        results['offset_plus_128'] += chr(shifted) if 32 <= shifted <= 126 else '?'
        av = abs(v)
        results['absolute'] += chr(av) if 32 <= av <= 126 else '?'
        mv = v % 128
        results['mod_128'] += chr(mv) if 32 <= mv <= 126 else '?'
    return results


def check_known_sequences(values):
    results = {}
    fib = [0, 1]
    for _ in range(50): fib.append(fib[-1] + fib[-2])
    fib_set = set(fib[:50])
    fib_matches = [(i, v) for i, v in enumerate(values) if v in fib_set]
    results['fibonacci_matches'] = {'count': len(fib_matches),
        'matches': [{'index': i, 'value': v} for i, v in fib_matches]}

    def is_prime(n):
        if n < 2: return False
        if n < 4: return True
        if n % 2 == 0 or n % 3 == 0: return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0: return False
            i += 6
        return True

    prime_matches = [(i, v) for i, v in enumerate(values) if is_prime(abs(v))]
    results['prime_matches'] = {'count': len(prime_matches),
        'matches': [{'index': i, 'value': v} for i, v in prime_matches]}

    pow2 = {2**i for i in range(20)}
    pow2_matches = [(i, v) for i, v in enumerate(values) if abs(v) in pow2]
    results['power_of_2_matches'] = {'count': len(pow2_matches),
        'matches': [{'index': i, 'value': v} for i, v in pow2_matches]}

    # Multiples of key numbers (7, 11, 13, 27)
    key_multiples = {}
    for key in [7, 11, 13, 27]:
        matches = [(i, v) for i, v in enumerate(values) if v != 0 and v % key == 0]
        key_multiples[str(key)] = {'count': len(matches),
            'matches': [{'index': i, 'value': v} for i, v in matches]}
    results['key_number_multiples'] = key_multiples

    return results


def arithmetic_patterns(values):
    results = {}
    diffs = [values[i+1] - values[i] for i in range(len(values) - 1)]
    results['first_differences'] = diffs
    second_diffs = [diffs[i+1] - diffs[i] for i in range(len(diffs) - 1)]
    results['second_differences'] = second_diffs

    cumsum = []
    s = 0
    for v in values: s += v; cumsum.append(s)
    results['cumulative_sum'] = cumsum
    results['total_sum'] = s

    xor_result = 0
    xor_seq = []
    for v in values: xor_result ^= (v & 0xFF); xor_seq.append(xor_result)
    results['running_xor'] = xor_seq
    results['final_xor'] = xor_result

    # XOR 127 decode
    xor127 = [v ^ 127 for v in values]
    xor127_ascii = ''.join(chr(x) if 32 <= x <= 126 else '.' for x in xor127)
    results['xor_127_values'] = xor127
    results['xor_127_ascii'] = xor127_ascii

    # Product of non-zero values
    product = 1
    for v in values:
        if v != 0: product *= v
    results['product_nonzero'] = product

    return results


def coordinate_analysis(values):
    coords = []
    for i in range(0, len(values) - 1, 2):
        coords.append({'x': values[i], 'y': values[i + 1]})

    collinear_triples = []
    n = len(coords)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                x1, y1 = coords[i]['x'], coords[i]['y']
                x2, y2 = coords[j]['x'], coords[j]['y']
                x3, y3 = coords[k]['x'], coords[k]['y']
                cross = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
                if cross == 0:
                    collinear_triples.append({'points': [i, j, k],
                        'coordinates': [coords[i], coords[j], coords[k]]})

    distances = []
    for i in range(len(coords) - 1):
        dx = coords[i+1]['x'] - coords[i]['x']
        dy = coords[i+1]['y'] - coords[i]['y']
        distances.append(round(math.sqrt(dx*dx + dy*dy), 4))

    xs = [c['x'] for c in coords]
    ys = [c['y'] for c in coords]

    return {
        'coordinates': coords, 'num_points': len(coords),
        'collinear_triples': collinear_triples[:20],
        'collinear_count': len(collinear_triples),
        'consecutive_distances': distances,
        'bounding_box': {'x_min': min(xs), 'x_max': max(xs), 'y_min': min(ys), 'y_max': max(ys)},
    }


def basic_statistics(values):
    n = len(values)
    sorted_vals = sorted(values)
    val_counts = Counter(values)
    return {
        'count': n, 'values_sorted': sorted_vals,
        'min': min(values), 'max': max(values), 'range': max(values) - min(values),
        'sum': sum(values), 'mean': round(statistics.mean(values), 4),
        'median': statistics.median(values),
        'stdev': round(statistics.stdev(values), 4) if n > 1 else 0,
        'value_frequency': dict(sorted(val_counts.items())),
        'unique_values': len(val_counts),
        'positive_count': sum(1 for v in values if v > 0),
        'negative_count': sum(1 for v in values if v < 0),
        'zero_count': sum(1 for v in values if v == 0),
    }


def group_by_column_pair(pairs):
    groups = {}
    for p in pairs:
        c1, c2 = p['primary']['col'], p['mirror']['col']
        key = f"{min(c1,c2)},{max(c1,c2)}"
        if key not in groups: groups[key] = []
        groups[key].append(p)
    result = {}
    for key, group in sorted(groups.items()):
        result[key] = {
            'count': len(group),
            'rows': [p['primary']['row'] for p in group],
            'primary_values': [p['primary']['value'] for p in group],
            'mirror_values': [p['mirror']['value'] for p in group],
            'sums': [p['sum'] for p in group],
        }
    return result


def hex_analysis(values):
    hex_str = ''.join(format(v & 0xFF, '02x') for v in values)
    byte_vals = bytes([v & 0xFF for v in values])
    return {
        'hex_values': [hex(v & 0xFF) for v in values],
        'hex_string': hex_str,
        'latin1_decode': byte_vals.decode('latin-1', errors='replace'),
        'utf8_decode': byte_vals.decode('utf-8', errors='replace'),
    }


def factorization_analysis(values):
    """Factor each value and look for patterns."""
    def factorize(n):
        if n == 0: return {0: 1}
        factors = {}
        n_abs = abs(n)
        d = 2
        while d * d <= n_abs:
            while n_abs % d == 0:
                factors[d] = factors.get(d, 0) + 1
                n_abs //= d
            d += 1
        if n_abs > 1: factors[n_abs] = 1
        if n < 0: factors[-1] = 1
        return factors

    factorizations = []
    all_prime_factors = Counter()
    for v in values:
        f = factorize(v)
        factorizations.append({'value': v, 'factors': f})
        for p, e in f.items():
            if p > 0: all_prime_factors[p] += e

    return {
        'factorizations': factorizations,
        'prime_factor_totals': dict(sorted(all_prime_factors.items())),
        'most_common_factors': all_prime_factors.most_common(10),
    }


def main():
    print("=" * 70)
    print("PALINDROME 34 ANALYSIS")
    print("=" * 70)

    print("\n[1/9] Loading matrix...")
    matrix = load_matrix()

    print("\n[2/9] Finding asymmetric cells...")
    all_asymmetric = find_all_asymmetric_cells(matrix)
    pairs = find_asymmetric_pairs(matrix)
    print(f"  Found {len(all_asymmetric)} asymmetric cells ({len(pairs)} unique pairs)")

    print("\n[3/9] Column distribution...")
    col_groups = group_by_column_pair(pairs)
    for key, group in col_groups.items():
        print(f"\n  Column pair ({key}): {group['count']} pairs")
        print(f"    Rows: {group['rows']}")
        print(f"    Primary values: {group['primary_values']}")
        print(f"    Mirror values:  {group['mirror_values']}")
        print(f"    Sums:           {group['sums']}")

    values_34 = [p['primary']['value'] for p in pairs]
    mirror_34 = [p['mirror']['value'] for p in pairs]
    print(f"\n  34 independent values: {values_34}")
    print(f"  34 mirror values:     {mirror_34}")

    print("\n[4/9] ASCII analysis...")
    ascii_res = ascii_analysis(values_34)
    for method, text in ascii_res.items():
        print(f"  {method:20s}: '{text}'")
    print("\n  Mirror ASCII:")
    mirror_ascii = ascii_analysis(mirror_34)
    for method, text in mirror_ascii.items():
        print(f"  {method:20s}: '{text}'")

    print("\n[5/9] Known sequences...")
    seq_res = check_known_sequences(values_34)
    print(f"  Fibonacci matches: {seq_res['fibonacci_matches']['count']}")
    for m in seq_res['fibonacci_matches']['matches']:
        print(f"    idx {m['index']}: value {m['value']}")
    print(f"  Prime matches: {seq_res['prime_matches']['count']}")
    for m in seq_res['prime_matches']['matches']:
        print(f"    idx {m['index']}: value {m['value']}")
    print(f"  Power-of-2 matches: {seq_res['power_of_2_matches']['count']}")
    for k, v in seq_res['key_number_multiples'].items():
        print(f"  Multiples of {k}: {v['count']}")

    print("\n[6/9] Arithmetic patterns...")
    arith = arithmetic_patterns(values_34)
    print(f"  Total sum: {arith['total_sum']}")
    print(f"  Final XOR: {arith['final_xor']} (0x{arith['final_xor']:02x})")
    print(f"  XOR 127 ASCII: '{arith['xor_127_ascii']}'")
    print(f"  Cumulative sum: {arith['cumulative_sum']}")

    print("\n[7/9] Coordinate analysis (17 points)...")
    coord_res = coordinate_analysis(values_34)
    for i, c in enumerate(coord_res['coordinates']):
        print(f"    P{i:2d}: ({c['x']:4d}, {c['y']:4d})")
    print(f"  Collinear triples: {coord_res['collinear_count']}")
    if coord_res['collinear_triples']:
        for ct in coord_res['collinear_triples'][:5]:
            print(f"    Points {ct['points']}: {ct['coordinates']}")

    print("\n[8/9] Statistics...")
    stats = basic_statistics(values_34)
    print(f"  Count: {stats['count']}, Unique: {stats['unique_values']}")
    print(f"  Min: {stats['min']}, Max: {stats['max']}, Range: {stats['range']}")
    print(f"  Sum: {stats['sum']}, Mean: {stats['mean']}, Median: {stats['median']}")
    print(f"  StdDev: {stats['stdev']}")
    print(f"  Positive: {stats['positive_count']}, Negative: {stats['negative_count']}, Zero: {stats['zero_count']}")
    print(f"  Sorted: {stats['values_sorted']}")
    print(f"  Frequency: {stats['value_frequency']}")

    print("\n[9/9] Factorization analysis...")
    factor_res = factorization_analysis(values_34)
    print(f"  Prime factor totals: {factor_res['prime_factor_totals']}")
    for f in factor_res['factorizations']:
        print(f"    {f['value']:5d} = {f['factors']}")

    # Hex analysis
    hex_res = hex_analysis(values_34)
    print(f"\n  Hex string: {hex_res['hex_string']}")
    print(f"  Latin-1: '{hex_res['latin1_decode']}'")

    # Sums analysis
    sums = [p['sum'] for p in pairs]
    sum_counts = Counter(sums)
    print(f"\n  Exception sums (M[r,c]+M[mr,mc]): {sorted(set(sums))}")
    print(f"  Sum frequency: {dict(sorted(sum_counts.items()))}")

    # Save results
    results = {
        'metadata': {
            'total_asymmetric_cells': len(all_asymmetric),
            'unique_pairs': len(pairs),
            'column_pairs': list(col_groups.keys()),
        },
        'the_34_values': values_34,
        'the_34_mirror_values': mirror_34,
        'all_34_pairs': [
            {'idx': i, 'row': p['primary']['row'], 'col': p['primary']['col'],
             'value': p['primary']['value'], 'mirror_row': p['mirror']['row'],
             'mirror_col': p['mirror']['col'], 'mirror_value': p['mirror']['value'],
             'sum': p['sum']}
            for i, p in enumerate(pairs)
        ],
        'column_pair_groups': col_groups,
        'ascii_analysis': ascii_res,
        'mirror_ascii': mirror_ascii,
        'known_sequences': seq_res,
        'arithmetic_patterns': arith,
        'coordinate_analysis': coord_res,
        'statistics': stats,
        'hex_analysis': hex_res,
        'factorization': factor_res,
        'sum_analysis': {'sums': sums, 'frequency': dict(sorted(sum_counts.items()))},
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
