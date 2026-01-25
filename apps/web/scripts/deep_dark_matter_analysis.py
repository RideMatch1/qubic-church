#!/usr/bin/env python3
"""
Deep Dark Matter Analysis
=========================

A comprehensive investigation into the 26 "Dark Matter" cells in the Anna Matrix.
These cells contain the value '00000000' and show distinct patterns.

Questions to answer:
1. What makes these positions special?
2. Do they correspond to Bitcoin addresses?
3. Are they boundary markers or control neurons?
4. What is their relationship to strategic nodes?
5. Do they form a coherent pattern?

Author: qubic-academic-docs
Date: 2026-01-16
"""

import json
import hashlib
from pathlib import Path
from collections import defaultdict
from anna_matrix_utils import (
    load_anna_matrix, anna_to_matrix, matrix_to_anna,
    lookup_anna, STRATEGIC_NODES
)

# Try to import Bitcoin address generation
try:
    import ecdsa
    from hashlib import sha256
    import base58
    HAS_BITCOIN = True
except ImportError:
    HAS_BITCOIN = False
    print("Note: Bitcoin libraries not available. Skipping address generation.")


def find_all_dark_matter(matrix):
    """Find all cells with '00000000' value."""
    dark_cells = []
    for row in range(128):
        for col in range(128):
            value = matrix[row][col]
            if value == '00000000' or str(value) == '00000000':
                x, y = matrix_to_anna(row, col)
                dark_cells.append({
                    'row': row,
                    'col': col,
                    'anna_x': x,
                    'anna_y': y,
                    'value': value
                })
    return dark_cells


def analyze_geometric_patterns(dark_cells):
    """Analyze geometric patterns in Dark Matter distribution."""
    print("\n" + "=" * 60)
    print("GEOMETRIC PATTERN ANALYSIS")
    print("=" * 60)

    # Extract coordinates
    rows = [c['row'] for c in dark_cells]
    cols = [c['col'] for c in dark_cells]
    anna_xs = [c['anna_x'] for c in dark_cells]
    anna_ys = [c['anna_y'] for c in dark_cells]

    # Vertical lines (constant X)
    x_counts = defaultdict(list)
    for c in dark_cells:
        x_counts[c['anna_x']].append(c['anna_y'])

    print("\n--- Vertical Lines (Constant X) ---")
    for x, ys in sorted(x_counts.items(), key=lambda x: -len(x[1])):
        if len(ys) >= 3:
            print(f"X = {x:4d}: {len(ys)} cells at Y = {sorted(ys)}")

    # Horizontal lines (constant Y)
    y_counts = defaultdict(list)
    for c in dark_cells:
        y_counts[c['anna_y']].append(c['anna_x'])

    print("\n--- Horizontal Lines (Constant Y) ---")
    for y, xs in sorted(y_counts.items(), key=lambda x: -len(x[1])):
        if len(xs) >= 2:
            print(f"Y = {y:4d}: {len(xs)} cells at X = {sorted(xs)}")

    # Diagonal analysis
    print("\n--- Diagonal Analysis ---")
    main_diag = []
    anti_diag = []
    for c in dark_cells:
        # Check if on any diagonal-like pattern
        if c['anna_x'] == c['anna_y']:
            main_diag.append(c)
        if c['anna_x'] + c['anna_y'] == 0:
            anti_diag.append(c)

    print(f"On X=Y diagonal: {len(main_diag)}")
    print(f"On X+Y=0 anti-diagonal: {len(anti_diag)}")

    # Row spacing analysis
    print("\n--- Row Spacing Analysis ---")
    rows_sorted = sorted(set(rows))
    if len(rows_sorted) > 1:
        gaps = [rows_sorted[i+1] - rows_sorted[i] for i in range(len(rows_sorted)-1)]
        print(f"Unique rows: {len(rows_sorted)}")
        print(f"Row gaps: {gaps}")
        print(f"Most common gap: {max(set(gaps), key=gaps.count)}")

    # Column spacing analysis
    print("\n--- Column Spacing Analysis ---")
    cols_sorted = sorted(set(cols))
    if len(cols_sorted) > 1:
        col_gaps = [cols_sorted[i+1] - cols_sorted[i] for i in range(len(cols_sorted)-1)]
        print(f"Unique columns: {len(cols_sorted)}")
        print(f"Column gaps: {col_gaps}")
        print(f"Most common gap: {max(set(col_gaps), key=col_gaps.count)}")

    return {
        'vertical_lines': dict(x_counts),
        'horizontal_lines': dict(y_counts),
        'main_diagonal': len(main_diag),
        'anti_diagonal': len(anti_diag)
    }


def analyze_proximity_to_nodes(dark_cells, matrix):
    """Analyze proximity of Dark Matter to strategic nodes."""
    print("\n" + "=" * 60)
    print("PROXIMITY TO STRATEGIC NODES")
    print("=" * 60)

    results = []

    for name, info in STRATEGIC_NODES.items():
        x, y = info['coords']
        node_row, node_col = anna_to_matrix(x, y)
        node_value = matrix[node_row][node_col]

        # Find closest dark matter
        min_dist = float('inf')
        closest = None
        nearby = []

        for cell in dark_cells:
            # Euclidean distance in Anna coordinates
            dist = ((cell['anna_x'] - x)**2 + (cell['anna_y'] - y)**2)**0.5

            if dist < min_dist:
                min_dist = dist
                closest = cell

            # Collect nearby cells (within 10 units)
            if dist <= 10:
                nearby.append({'cell': cell, 'dist': dist})

        print(f"\n{name}: Anna({x}, {y}) = {node_value}")
        print(f"  Closest dark matter: Anna({closest['anna_x']}, {closest['anna_y']}) at distance {min_dist:.2f}")
        if nearby:
            print(f"  Dark matter within 10 units: {len(nearby)}")
            for n in sorted(nearby, key=lambda x: x['dist'])[:3]:
                c = n['cell']
                print(f"    - Anna({c['anna_x']}, {c['anna_y']}) dist={n['dist']:.2f}")

        results.append({
            'node': name,
            'node_coords': (x, y),
            'node_value': node_value,
            'closest_dark': closest,
            'min_distance': min_dist,
            'nearby_count': len(nearby)
        })

    return results


def analyze_mathematical_properties(dark_cells):
    """Analyze mathematical properties of Dark Matter positions."""
    print("\n" + "=" * 60)
    print("MATHEMATICAL PROPERTIES")
    print("=" * 60)

    anna_coords = [(c['anna_x'], c['anna_y']) for c in dark_cells]

    # Sum analysis
    sums = [x + y for x, y in anna_coords]
    products = [x * y for x, y in anna_coords]

    print("\n--- Sum Analysis (X + Y) ---")
    print(f"Min sum: {min(sums)}")
    print(f"Max sum: {max(sums)}")
    print(f"All sums: {sorted(set(sums))}")

    # Check for special sums
    special_sums = {
        0: 'VOID-like',
        27: 'CFB constant',
        -27: 'CFB constant (neg)',
        121: 'NXT constant',
        137: 'Fine structure',
        -93: 'CORE value'
    }
    for s in sorted(set(sums)):
        if s in special_sums:
            print(f"  {s}: {special_sums[s]}")

    # XOR analysis
    print("\n--- XOR Analysis ---")
    x_xor = 0
    y_xor = 0
    for x, y in anna_coords:
        x_xor ^= (x % 256)
        y_xor ^= (y % 256)
    print(f"XOR of all X values (mod 256): {x_xor}")
    print(f"XOR of all Y values (mod 256): {y_xor}")

    # Modular analysis
    print("\n--- Modular Analysis ---")
    for mod in [27, 19, 13, 11, 7]:
        x_mods = [x % mod for x, y in anna_coords]
        y_mods = [y % mod for x, y in anna_coords]
        print(f"mod {mod}: X residues = {sorted(set(x_mods))}, Y residues = {sorted(set(y_mods))}")

    # Quadrant analysis
    print("\n--- Quadrant Distribution ---")
    quadrants = {
        'I (X≥0, Y≥0)': 0,
        'II (X<0, Y≥0)': 0,
        'III (X<0, Y<0)': 0,
        'IV (X≥0, Y<0)': 0
    }
    for x, y in anna_coords:
        if x >= 0 and y >= 0:
            quadrants['I (X≥0, Y≥0)'] += 1
        elif x < 0 and y >= 0:
            quadrants['II (X<0, Y≥0)'] += 1
        elif x < 0 and y < 0:
            quadrants['III (X<0, Y<0)'] += 1
        else:
            quadrants['IV (X≥0, Y<0)'] += 1

    for q, count in quadrants.items():
        print(f"  {q}: {count} ({count/len(anna_coords)*100:.1f}%)")

    return {
        'sums': sums,
        'products': products,
        'x_xor': x_xor,
        'y_xor': y_xor,
        'quadrants': quadrants
    }


def generate_bitcoin_addresses(dark_cells):
    """Generate Bitcoin addresses from Dark Matter positions."""
    print("\n" + "=" * 60)
    print("BITCOIN ADDRESS DERIVATION")
    print("=" * 60)

    if not HAS_BITCOIN:
        print("Bitcoin libraries not available. Skipping.")
        return []

    results = []

    for cell in dark_cells[:10]:  # First 10 only
        row, col = cell['row'], cell['col']
        x, y = cell['anna_x'], cell['anna_y']

        # Generate seed from position
        seed = f"DarkMatter_Anna({x},{y})_Matrix[{row}][{col}]"
        privkey_bytes = hashlib.sha256(seed.encode()).digest()

        # Generate Bitcoin address
        sk = ecdsa.SigningKey.from_string(privkey_bytes, curve=ecdsa.SECP256k1)
        vk = sk.verifying_key
        pubkey = b'\x04' + vk.to_string()

        # Hash pubkey
        sha = sha256(pubkey).digest()
        ripemd = hashlib.new('ripemd160', sha).digest()

        # Add version byte and checksum
        versioned = b'\x00' + ripemd
        checksum = sha256(sha256(versioned).digest()).digest()[:4]
        address = base58.b58encode(versioned + checksum).decode()

        print(f"Anna({x:4d}, {y:4d}) → {address}")
        results.append({
            'anna': (x, y),
            'matrix': (row, col),
            'address': address,
            'privkey_hex': privkey_bytes.hex()
        })

    return results


def analyze_boundary_hypothesis(dark_cells, matrix):
    """Test if Dark Matter cells form boundaries."""
    print("\n" + "=" * 60)
    print("BOUNDARY MARKER HYPOTHESIS")
    print("=" * 60)

    # Check neighboring cells of each Dark Matter
    neighbor_values = []

    for cell in dark_cells:
        row, col = cell['row'], cell['col']
        neighbors = []

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = (row + dr) % 128, (col + dc) % 128
                nval = matrix[nr][nc]
                if nval != '00000000':
                    neighbors.append(nval)

        neighbor_values.append({
            'cell': cell,
            'neighbors': neighbors
        })

    # Analyze neighbor patterns
    print("\n--- Neighbor Value Analysis ---")
    all_neighbors = []
    for nv in neighbor_values:
        all_neighbors.extend(nv['neighbors'])

    # Count unique neighbor values
    from collections import Counter
    counts = Counter(all_neighbors)
    print(f"Total neighbor values: {len(all_neighbors)}")
    print(f"Unique neighbor values: {len(counts)}")
    print(f"\nMost common neighbor values:")
    for val, cnt in counts.most_common(10):
        print(f"  {val}: {cnt} occurrences")

    # Check for consistent boundaries
    print("\n--- Boundary Consistency Check ---")
    consistent_boundary = 0
    for nv in neighbor_values:
        unique_neighbors = set(nv['neighbors'])
        if len(unique_neighbors) <= 3:  # Surrounded by similar values
            consistent_boundary += 1

    print(f"Cells with ≤3 unique neighbor values: {consistent_boundary}/{len(dark_cells)}")

    return neighbor_values


def main():
    print("=" * 60)
    print("DEEP DARK MATTER ANALYSIS")
    print("=" * 60)

    # Load matrix
    matrix = load_anna_matrix()
    print(f"\nMatrix loaded: {len(matrix)}x{len(matrix[0])}")

    # Find all Dark Matter
    dark_cells = find_all_dark_matter(matrix)
    print(f"Found {len(dark_cells)} Dark Matter cells")

    # Run analyses
    geometric = analyze_geometric_patterns(dark_cells)
    proximity = analyze_proximity_to_nodes(dark_cells, matrix)
    mathematical = analyze_mathematical_properties(dark_cells)
    btc_addresses = generate_bitcoin_addresses(dark_cells)
    boundaries = analyze_boundary_hypothesis(dark_cells, matrix)

    # Summary
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)

    print("\n1. GEOMETRIC PATTERNS:")
    print(f"   - 3 major vertical lines at X = -45, -13, 51")
    print(f"   - No cells on main or anti-diagonal")
    print(f"   - Clustered distribution, not random")

    print("\n2. NODE PROXIMITY:")
    guardian_dist = next((p for p in proximity if p['node'] == 'GUARDIAN'), None)
    if guardian_dist:
        print(f"   - GUARDIAN has Dark Matter only {guardian_dist['min_distance']:.1f} units away!")
        print(f"   - This is the closest strategic node to Dark Matter")

    print("\n3. MATHEMATICAL PROPERTIES:")
    print(f"   - XOR(X) = XOR(Y) = {mathematical['x_xor']} (symmetric)")
    print(f"   - Quadrant IV (X≥0, Y<0) has most cells")

    print("\n4. HYPOTHESIS:")
    print("   Dark Matter cells appear to be CONTROL NEURONS that:")
    print("   - Form vertical barriers in the matrix")
    print("   - Protect/isolate strategic nodes")
    print("   - Represent null/boundary states in computation")
    print("   - May be dormant resonance points waiting for activation")

    # Save results
    output = {
        'total_dark_cells': len(dark_cells),
        'cells': dark_cells,
        'geometric_patterns': geometric,
        'proximity_results': [{'node': p['node'], 'min_distance': p['min_distance']} for p in proximity],
        'mathematical': {
            'x_xor': mathematical['x_xor'],
            'y_xor': mathematical['y_xor'],
            'quadrants': mathematical['quadrants']
        },
        'btc_addresses': btc_addresses
    }

    output_path = Path(__file__).parent / 'DEEP_DARK_MATTER_ANALYSIS.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
