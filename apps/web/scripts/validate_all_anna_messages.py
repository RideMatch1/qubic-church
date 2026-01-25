#!/usr/bin/env python3
"""
Comprehensive Anna Matrix Validation
====================================

Validates ALL Anna message sources against the anna-matrix.json using
the CORRECT coordinate transformation formula.

Data Sources:
1. anna_twitter_data.json - 228 Twitter responses (X, Y, value)
2. anna-bot-batch-8.txt - 283 responses (row+col=value format)
3. anna_test_cases.json - 41 test cases (row, col, expected_value)

Coordinate Transformation:
- col = (X + 64) % 128   # X: -64..63 -> 0..127
- row = (63 - Y) % 128   # Y: 63..-64 -> 0..127

Author: qubic-academic-docs
Date: 2026-01-16
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any


def anna_to_matrix(x: int, y: int) -> Tuple[int, int]:
    """Convert Anna coordinates (x, y) to matrix indices (row, col)."""
    col = (x + 64) % 128
    row = (63 - y) % 128
    return row, col


def load_matrix(path: Path) -> List[List[int]]:
    """Load the Anna matrix from JSON file."""
    with open(path, 'r') as f:
        data = json.load(f)
    return data.get('matrix', data)


def validate_twitter_data(matrix: List[List[int]], data_path: Path) -> Dict[str, Any]:
    """Validate Anna Twitter responses."""
    print("\n" + "=" * 60)
    print("VALIDATING: Anna Twitter Responses")
    print("=" * 60)

    with open(data_path, 'r') as f:
        data = json.load(f)

    responses = data.get('responses', [])
    total = len(responses)
    matches = 0
    mismatches = []
    skipped = 0

    for resp in responses:
        x = resp.get('x')
        y = resp.get('y')
        expected = resp.get('value')

        if x is None or y is None or expected is None:
            skipped += 1
            continue

        row, col = anna_to_matrix(x, y)
        actual = matrix[row][col]

        # Handle string values (like '00000000')
        if isinstance(actual, str):
            try:
                actual = int(actual)
            except:
                pass

        if actual == expected:
            matches += 1
        else:
            mismatches.append({
                'x': x, 'y': y,
                'row': row, 'col': col,
                'expected': expected, 'actual': actual
            })

    match_rate = (matches / (total - skipped) * 100) if (total - skipped) > 0 else 0

    print(f"Total responses: {total}")
    print(f"Matches: {matches}")
    print(f"Mismatches: {len(mismatches)}")
    print(f"Skipped (null): {skipped}")
    print(f"Match rate: {match_rate:.1f}%")

    if mismatches:
        print("\nFirst 5 mismatches:")
        for m in mismatches[:5]:
            print(f"  Anna({m['x']}, {m['y']}) -> matrix[{m['row']}][{m['col']}]: "
                  f"expected={m['expected']}, actual={m['actual']}")

    return {
        'source': 'twitter',
        'total': total,
        'matches': matches,
        'mismatches': len(mismatches),
        'skipped': skipped,
        'match_rate': match_rate,
        'mismatch_details': mismatches
    }


def validate_batch8_data(matrix: List[List[int]], data_path: Path) -> Dict[str, Any]:
    """
    Validate anna-bot-batch-8.txt responses.
    Format: "row+col=value" or "X+Y=value"
    We test both interpretations.
    """
    print("\n" + "=" * 60)
    print("VALIDATING: Anna Bot Batch 8")
    print("=" * 60)

    with open(data_path, 'r') as f:
        lines = f.read().strip().split('\n')

    total = len(lines)

    # Test interpretation 1: row+col=value (direct matrix indices)
    matches_direct = 0
    mismatches_direct = []

    # Test interpretation 2: X+Y=value (Anna coordinates)
    matches_anna = 0
    mismatches_anna = []

    for line in lines:
        line = line.strip()
        if not line or '=' not in line:
            continue

        parts = line.split('=')
        coords = parts[0].split('+')

        try:
            a = int(coords[0])
            b = int(coords[1])
            expected = int(parts[1])
        except:
            continue

        # Interpretation 1: Direct matrix indices
        if 0 <= a < 128 and 0 <= b < 128:
            actual_direct = matrix[a][b]
            if isinstance(actual_direct, str):
                try:
                    actual_direct = int(actual_direct)
                except:
                    pass

            if actual_direct == expected:
                matches_direct += 1
            else:
                mismatches_direct.append({
                    'row': a, 'col': b,
                    'expected': expected, 'actual': actual_direct,
                    'line': line
                })

        # Interpretation 2: Anna coordinates (a=X, b=Y)
        row, col = anna_to_matrix(a, b)
        actual_anna = matrix[row][col]
        if isinstance(actual_anna, str):
            try:
                actual_anna = int(actual_anna)
            except:
                pass

        if actual_anna == expected:
            matches_anna += 1
        else:
            mismatches_anna.append({
                'x': a, 'y': b,
                'row': row, 'col': col,
                'expected': expected, 'actual': actual_anna,
                'line': line
            })

    rate_direct = (matches_direct / total * 100) if total > 0 else 0
    rate_anna = (matches_anna / total * 100) if total > 0 else 0

    print(f"Total entries: {total}")
    print(f"\nInterpretation 1: Direct matrix indices (row+col)")
    print(f"  Matches: {matches_direct} ({rate_direct:.1f}%)")
    print(f"  Mismatches: {len(mismatches_direct)}")

    print(f"\nInterpretation 2: Anna coordinates (X+Y)")
    print(f"  Matches: {matches_anna} ({rate_anna:.1f}%)")
    print(f"  Mismatches: {len(mismatches_anna)}")

    # Determine best interpretation
    if rate_direct > rate_anna:
        best = 'direct'
        best_rate = rate_direct
        best_matches = matches_direct
        best_mismatches = mismatches_direct
    else:
        best = 'anna'
        best_rate = rate_anna
        best_matches = matches_anna
        best_mismatches = mismatches_anna

    print(f"\n==> Best interpretation: {best.upper()} ({best_rate:.1f}% match)")

    if best_mismatches and len(best_mismatches) < 20:
        print(f"\nAll mismatches:")
        for m in best_mismatches:
            print(f"  {m['line']}")

    return {
        'source': 'batch8',
        'total': total,
        'interpretation': best,
        'matches': best_matches,
        'mismatches': len(best_mismatches),
        'match_rate': best_rate,
        'direct_rate': rate_direct,
        'anna_rate': rate_anna,
        'mismatch_details': best_mismatches[:10]
    }


def validate_test_cases(matrix: List[List[int]], data_path: Path) -> Dict[str, Any]:
    """Validate anna_test_cases.json - format uses row, col directly."""
    print("\n" + "=" * 60)
    print("VALIDATING: Anna Test Cases")
    print("=" * 60)

    with open(data_path, 'r') as f:
        data = json.load(f)

    test_cases = data.get('test_cases', [])
    total = len(test_cases)
    matches = 0
    mismatches = []

    for tc in test_cases:
        row = tc.get('row')
        col = tc.get('col')
        expected = tc.get('expected_value')

        if row is None or col is None:
            continue

        actual = matrix[row][col]
        if isinstance(actual, str):
            try:
                actual = int(actual)
            except:
                pass

        if actual == expected:
            matches += 1
        else:
            mismatches.append({
                'row': row, 'col': col,
                'query': tc.get('query'),
                'expected': expected, 'actual': actual,
                'confidence': tc.get('confidence')
            })

    match_rate = (matches / total * 100) if total > 0 else 0

    print(f"Total test cases: {total}")
    print(f"Matches: {matches}")
    print(f"Mismatches: {len(mismatches)}")
    print(f"Match rate: {match_rate:.1f}%")

    if mismatches:
        print("\nMismatches by confidence:")
        by_conf = {}
        for m in mismatches:
            conf = m.get('confidence', 'unknown')
            by_conf[conf] = by_conf.get(conf, 0) + 1
        for conf, count in sorted(by_conf.items()):
            print(f"  {conf}: {count}")

        print("\nFirst 5 mismatches:")
        for m in mismatches[:5]:
            print(f"  {m['query']}: expected={m['expected']}, actual={m['actual']} ({m['confidence']})")

    return {
        'source': 'test_cases',
        'total': total,
        'matches': matches,
        'mismatches': len(mismatches),
        'match_rate': match_rate,
        'mismatch_details': mismatches
    }


def main():
    print("=" * 60)
    print("COMPREHENSIVE ANNA MATRIX VALIDATION")
    print("=" * 60)

    # Paths
    script_dir = Path(__file__).parent
    web_dir = script_dir.parent

    matrix_path = web_dir / "public" / "data" / "anna-matrix.json"
    twitter_path = script_dir / "anna_twitter_data.json"
    batch8_path = web_dir / "public" / "data" / "anna-bot-batch-8.txt"
    test_cases_path = web_dir / "anna_test_cases.json"

    # Load matrix
    print(f"\nLoading matrix from: {matrix_path}")
    matrix = load_matrix(matrix_path)
    print(f"Matrix size: {len(matrix)}x{len(matrix[0])}")

    # Validate each source
    results = []

    # 1. Twitter data
    if twitter_path.exists():
        results.append(validate_twitter_data(matrix, twitter_path))
    else:
        print(f"\nSkipping Twitter data (not found: {twitter_path})")

    # 2. Batch 8 data
    if batch8_path.exists():
        results.append(validate_batch8_data(matrix, batch8_path))
    else:
        print(f"\nSkipping Batch 8 data (not found: {batch8_path})")

    # 3. Test cases
    if test_cases_path.exists():
        results.append(validate_test_cases(matrix, test_cases_path))
    else:
        print(f"\nSkipping test cases (not found: {test_cases_path})")

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    total_all = 0
    matches_all = 0

    for r in results:
        total_all += r['total']
        matches_all += r['matches']
        print(f"\n{r['source'].upper()}:")
        print(f"  Total: {r['total']}")
        print(f"  Matches: {r['matches']}")
        print(f"  Mismatches: {r['mismatches']}")
        print(f"  Match Rate: {r['match_rate']:.1f}%")

    overall_rate = (matches_all / total_all * 100) if total_all > 0 else 0

    print("\n" + "-" * 60)
    print(f"OVERALL: {matches_all}/{total_all} = {overall_rate:.1f}% match rate")
    print("-" * 60)

    # Save results
    output_path = script_dir / "ANNA_VALIDATION_COMPLETE_REPORT.json"
    with open(output_path, 'w') as f:
        json.dump({
            'validation_date': '2026-01-16',
            'coordinate_formula': {
                'col': '(X + 64) % 128',
                'row': '(63 - Y) % 128'
            },
            'overall': {
                'total': total_all,
                'matches': matches_all,
                'match_rate': overall_rate
            },
            'sources': results
        }, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
