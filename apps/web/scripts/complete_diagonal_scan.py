#!/usr/bin/env python3
"""
Complete Diagonal Scan for ±27 Values in Anna Matrix
=====================================================
Scans ALL 128 diagonal positions to find blocks with matrix[i,i] = ±27
"""

import json
import os

# Known blocks from previous research
KNOWN_BLOCKS = {73, 74, 75, 80, 89, 93, 95, 96, 120, 121}

def main():
    # Load Anna Matrix
    script_dir = os.path.dirname(os.path.abspath(__file__))
    matrix_path = os.path.join(script_dir, '../public/data/anna-matrix.json')

    print("Loading Anna Matrix...")
    with open(matrix_path, 'r') as f:
        data = json.load(f)

    # Matrix is stored as data['matrix']
    matrix = data['matrix']
    print(f"Matrix size: {len(matrix)}x{len(matrix[0])}")
    print()

    # Scan ALL diagonal positions
    print("=" * 60)
    print("SCANNING ALL 128 DIAGONAL POSITIONS FOR ±27")
    print("=" * 60)
    print()

    results = []
    all_diagonal_values = []

    for i in range(128):
        value = matrix[i][i]
        all_diagonal_values.append(value)

        if value == 27 or value == -27:
            status = 'KNOWN' if i in KNOWN_BLOCKS else '⭐ NEW!'
            results.append({
                'position': i,
                'value': value,
                'status': status
            })

    # Report results
    print(f"Total positions with ±27: {len(results)}")
    print()

    print("ALL ±27 POSITIONS:")
    print("-" * 40)
    for r in results:
        marker = "⭐" if r['status'] == '⭐ NEW!' else "  "
        print(f"{marker} Block {r['position']:3d}: diagonal = {r['value']:+4d} [{r['status']}]")

    print()

    # Count new vs known
    new_count = sum(1 for r in results if r['status'] == '⭐ NEW!')
    known_count = sum(1 for r in results if r['status'] == 'KNOWN')

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Known positions (73-121):  {known_count}")
    print(f"NEW positions found:       {new_count}")
    print(f"Total ±27 positions:       {len(results)}")
    print()

    if new_count > 0:
        print("🎉 NEW POSITIONS FOUND! 🎉")
        for r in results:
            if r['status'] == '⭐ NEW!':
                print(f"   Block {r['position']}: diagonal = {r['value']}")
    else:
        print("No new ±27 positions found beyond the known 10.")

    print()

    # Also show diagonal value distribution for context
    print("=" * 60)
    print("DIAGONAL VALUE DISTRIBUTION")
    print("=" * 60)
    from collections import Counter
    value_counts = Counter(all_diagonal_values)
    for value, count in sorted(value_counts.items()):
        marker = " ← ±27!" if value in [27, -27] else ""
        print(f"Value {value:+4d}: {count:3d} occurrences{marker}")

    # Save results
    output_path = os.path.join(script_dir, 'COMPLETE_DIAGONAL_SCAN_RESULTS.json')
    with open(output_path, 'w') as f:
        json.dump({
            'total_positions_with_27': len(results),
            'new_positions': [r for r in results if r['status'] == '⭐ NEW!'],
            'known_positions': [r for r in results if r['status'] == 'KNOWN'],
            'all_results': results,
            'diagonal_values': all_diagonal_values
        }, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")

    return results

if __name__ == '__main__':
    main()
