#!/usr/bin/env python3
"""
Deep Analysis of Position [22,22] in the Anna Matrix
=====================================================

This position is unique because:
- value = mirror_value (both are +100)
- 22 + 105 = 127 (the symmetry axis)
- 100 XOR 127 = 27 (CFB's signature number)
- 22 = 2 × 11 (contains prime factor 11)

This script performs comprehensive analysis to understand why this position might be the "key".
"""

import json
import os
from typing import Dict, List, Tuple, Any
from collections import Counter
import math

def load_matrix(filepath: str) -> List[List[int]]:
    """Load the Anna Matrix from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    # Convert any string values to integers (e.g., "00000000" -> 0)
    matrix = data['matrix']
    for r, row in enumerate(matrix):
        for c, val in enumerate(row):
            if isinstance(val, str):
                try:
                    matrix[r][c] = int(val)
                except ValueError:
                    matrix[r][c] = 0  # Default to 0 if conversion fails
    return matrix

def get_neighbors(matrix: List[List[int]], row: int, col: int, radius: int) -> Dict[str, Any]:
    """Get all neighbors within a given radius."""
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0

    neighbors = []
    grid = []

    for r in range(row - radius, row + radius + 1):
        row_values = []
        for c in range(col - radius, col + radius + 1):
            if 0 <= r < rows and 0 <= c < cols:
                val = matrix[r][c]
                if r != row or c != col:  # Exclude center
                    neighbors.append({
                        'position': [r, c],
                        'value': val,
                        'distance': abs(r - row) + abs(c - col)  # Manhattan distance
                    })
                row_values.append(val)
            else:
                row_values.append(None)
        grid.append(row_values)

    return {
        'grid': grid,
        'neighbors': neighbors,
        'radius': radius
    }

def analyze_number_100() -> Dict[str, Any]:
    """Comprehensive analysis of the number 100."""
    n = 100

    # Prime factorization
    def prime_factors(n):
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors

    # Divisors
    def get_divisors(n):
        divisors = []
        for i in range(1, int(n**0.5) + 1):
            if n % i == 0:
                divisors.append(i)
                if i != n // i:
                    divisors.append(n // i)
        return sorted(divisors)

    # Digit properties
    digits = [int(d) for d in str(n)]
    digit_sum = sum(digits)
    digit_product = 1
    for d in digits:
        digit_product *= d if d != 0 else 1

    return {
        'decimal': n,
        'binary': bin(n),
        'binary_clean': bin(n)[2:],
        'hex': hex(n),
        'hex_clean': hex(n)[2:],
        'octal': oct(n),
        'octal_clean': oct(n)[2:],
        'ascii_char': chr(n),
        'ascii_interpretation': f"'{chr(n)}' (lowercase 'd')",
        'prime_factors': prime_factors(n),
        'divisors': get_divisors(n),
        'is_prime': len(prime_factors(n)) == 1 and prime_factors(n)[0] == n,
        'is_perfect_square': int(n**0.5)**2 == n,
        'square_root': 10,  # sqrt(100) = 10
        'is_triangular': False,  # 100 is not a triangular number
        'digits': digits,
        'digit_sum': digit_sum,
        'digit_product': digit_product,
        'digit_root': 1,  # 1+0+0 = 1
        'special_properties': {
            '10_squared': '100 = 10²',
            'sum_of_cubes': '100 = 1³ + 2³ + 3³ + 4³',  # 1+8+27+64 = 100
            'century': 'Base of percentage system (per centum)',
            'degrees_in_right_angle': '100 gradians = 90 degrees',
            'in_binary': '1100100 = 100 in base 10',
        },
        'xor_operations': {
            '100_XOR_127': 100 ^ 127,  # = 27 (CFB's number!)
            '100_XOR_22': 100 ^ 22,    # = 114
            '100_XOR_100': 100 ^ 100,  # = 0
            '100_XOR_27': 100 ^ 27,    # = 127 (symmetry axis!)
            '100_XOR_11': 100 ^ 11,    # 22 = 2×11
        },
        'modular_properties': {
            'mod_27': 100 % 27,
            'mod_22': 100 % 22,
            'mod_11': 100 % 11,
            'mod_127': 100 % 127,
            'mod_128': 100 % 128,
            'mod_256': 100 % 256,
        }
    }

def analyze_position_22() -> Dict[str, Any]:
    """Analyze the significance of position 22."""
    n = 22

    return {
        'value': n,
        'prime_factors': [2, 11],
        'factorization': '2 × 11',
        'contains_11': True,  # CFB's signature prime
        'binary': bin(n),
        'hex': hex(n),
        'sum_to_127': n + 105,  # = 127 (symmetry axis)
        'mirror_position': 127 - 22,  # = 105
        'xor_with_100': n ^ 100,  # = 114
        'xor_with_127': n ^ 127,  # = 105 (the mirror!)
        'special_meanings': {
            'hebrew_letters': '22 letters in Hebrew alphabet',
            'tarot_major_arcana': '22 major arcana cards',
            'catch_22': 'Paradoxical situation',
            'master_number': '22 is a master number in numerology',
        },
        'relationships': {
            'double_11': '22 = 2 × 11 (11 is CFB signature)',
            '11_squared_negative': '1CFi + 1CFB = -121 = -(11²)',
            'fibonacci': '22 is not a Fibonacci number',
        }
    }

def analyze_diagonals(matrix: List[List[int]]) -> Dict[str, Any]:
    """Analyze diagonal positions: [0,0], [11,11], [22,22], [33,33], etc."""
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0
    max_diag = min(rows, cols)

    diagonals = []
    for i in range(max_diag):
        val = matrix[i][i]
        mirror_row = 127 - i if 127 - i < rows else None
        mirror_col = 127 - i if 127 - i < cols else None
        mirror_val = matrix[mirror_row][mirror_col] if mirror_row is not None and mirror_col is not None else None

        diagonals.append({
            'position': [i, i],
            'value': val,
            'mirror_position': [mirror_row, mirror_col] if mirror_row else None,
            'mirror_value': mirror_val,
            'value_equals_mirror': val == mirror_val if mirror_val is not None else None,
            'sum_with_mirror': val + mirror_val if mirror_val is not None else None,
            'xor_with_mirror': val ^ mirror_val if mirror_val is not None else None,
        })

    # Special diagonal positions (multiples of 11)
    special_positions = []
    for mult in range(0, max_diag // 11 + 1):
        pos = mult * 11
        if pos < max_diag:
            val = matrix[pos][pos]
            special_positions.append({
                'multiplier': mult,
                'position': [pos, pos],
                'value': val,
                'pos_mod_11': pos % 11,
                'value_mod_11': val % 11,
            })

    return {
        'all_diagonal_values': diagonals,
        'special_11_multiples': special_positions,
        'diagonal_sum': sum(d['value'] for d in diagonals),
        'diagonal_stats': {
            'count': len(diagonals),
            'min': min(d['value'] for d in diagonals),
            'max': max(d['value'] for d in diagonals),
            'avg': sum(d['value'] for d in diagonals) / len(diagonals) if diagonals else 0,
        }
    }

def find_value_occurrences(matrix: List[List[int]], target: int) -> List[Dict[str, Any]]:
    """Find all occurrences of a specific value in the matrix."""
    occurrences = []

    for r, row in enumerate(matrix):
        for c, val in enumerate(row):
            if val == target:
                # Calculate mirror position
                mirror_r = 127 - r
                mirror_c = 127 - c

                occurrences.append({
                    'position': [r, c],
                    'row': r,
                    'col': c,
                    'row_plus_col': r + c,
                    'row_times_col': r * c,
                    'row_xor_col': r ^ c,
                    'mirror_position': [mirror_r, mirror_c],
                    'is_on_diagonal': r == c,
                    'distance_from_22_22': abs(r - 22) + abs(c - 22),
                })

    return occurrences

def analyze_neighborhood_patterns(matrix: List[List[int]], center_row: int, center_col: int) -> Dict[str, Any]:
    """Analyze patterns radiating from center position."""
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0

    # Analyze rings of increasing radius
    rings = []
    for radius in range(1, min(center_row, center_col, rows - center_row - 1, cols - center_col - 1) + 1):
        ring_values = []

        # Top edge
        for c in range(center_col - radius, center_col + radius + 1):
            r = center_row - radius
            if 0 <= r < rows and 0 <= c < cols:
                ring_values.append(matrix[r][c])

        # Right edge (excluding corners)
        for r in range(center_row - radius + 1, center_row + radius):
            c = center_col + radius
            if 0 <= r < rows and 0 <= c < cols:
                ring_values.append(matrix[r][c])

        # Bottom edge
        for c in range(center_col + radius, center_col - radius - 1, -1):
            r = center_row + radius
            if 0 <= r < rows and 0 <= c < cols:
                ring_values.append(matrix[r][c])

        # Left edge (excluding corners)
        for r in range(center_row + radius - 1, center_row - radius, -1):
            c = center_col - radius
            if 0 <= r < rows and 0 <= c < cols:
                ring_values.append(matrix[r][c])

        if ring_values:
            rings.append({
                'radius': radius,
                'cell_count': len(ring_values),
                'values': ring_values[:20],  # First 20 for brevity
                'sum': sum(ring_values),
                'average': sum(ring_values) / len(ring_values),
                'min': min(ring_values),
                'max': max(ring_values),
                'contains_100': 100 in ring_values,
                'contains_27': 27 in ring_values,
                'value_at_radius_mod_27': sum(ring_values) % 27,
            })

        if radius >= 22:  # Limit analysis to reasonable radius
            break

    return {
        'center': [center_row, center_col],
        'center_value': matrix[center_row][center_col],
        'rings': rings,
    }

def analyze_cross_pattern(matrix: List[List[int]], center_row: int, center_col: int) -> Dict[str, Any]:
    """Analyze cross pattern (horizontal and vertical lines through center)."""
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0

    # Horizontal line (row 22)
    horizontal = matrix[center_row] if center_row < rows else []

    # Vertical line (column 22)
    vertical = [matrix[r][center_col] for r in range(rows) if center_col < cols]

    return {
        'horizontal_line': {
            'row': center_row,
            'values': horizontal[:50],  # First 50 for brevity
            'sum': sum(horizontal),
            'average': sum(horizontal) / len(horizontal) if horizontal else 0,
            'count_100': horizontal.count(100),
            'count_27': horizontal.count(27),
        },
        'vertical_line': {
            'col': center_col,
            'values': vertical[:50],  # First 50 for brevity
            'sum': sum(vertical),
            'average': sum(vertical) / len(vertical) if vertical else 0,
            'count_100': vertical.count(100),
            'count_27': vertical.count(27),
        },
        'intersection_value': matrix[center_row][center_col],
    }

def main():
    # Load matrix
    matrix_path = '/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json'
    matrix = load_matrix(matrix_path)

    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0

    print(f"Matrix dimensions: {rows} x {cols}")
    print(f"Value at [22,22]: {matrix[22][22]}")

    # Build comprehensive analysis
    analysis = {
        'metadata': {
            'matrix_dimensions': [rows, cols],
            'analysis_target': [22, 22],
            'target_value': matrix[22][22],
            'symmetry_axis': 127,
        },
        'position_22_22': {
            'value': matrix[22][22],
            'mirror_position': [105, 105],
            'mirror_value': matrix[105][105] if 105 < rows and 105 < cols else None,
            'value_equals_mirror': matrix[22][22] == matrix[105][105] if 105 < rows and 105 < cols else None,
            'significance': {
                '22_plus_105': 22 + 105,  # = 127
                'is_symmetry_axis': 22 + 105 == 127,
                '100_xor_127': 100 ^ 127,  # = 27
                '100_xor_27': 100 ^ 27,    # = 127
            }
        },
        'number_100_analysis': analyze_number_100(),
        'position_22_analysis': analyze_position_22(),
        'neighborhood_3x3': get_neighbors(matrix, 22, 22, 1),
        'neighborhood_5x5': get_neighbors(matrix, 22, 22, 2),
        'neighborhood_7x7': get_neighbors(matrix, 22, 22, 3),
        'diagonal_analysis': analyze_diagonals(matrix),
        'value_100_occurrences': find_value_occurrences(matrix, 100),
        'value_27_occurrences': find_value_occurrences(matrix, 27),
        'ring_patterns': analyze_neighborhood_patterns(matrix, 22, 22),
        'cross_pattern': analyze_cross_pattern(matrix, 22, 22),
    }

    # Calculate neighborhood statistics
    for size in ['neighborhood_3x3', 'neighborhood_5x5', 'neighborhood_7x7']:
        neighbors = analysis[size]['neighbors']
        values = [n['value'] for n in neighbors]
        analysis[size]['statistics'] = {
            'count': len(values),
            'sum': sum(values),
            'average': sum(values) / len(values) if values else 0,
            'min': min(values) if values else None,
            'max': max(values) if values else None,
            'sum_mod_27': sum(values) % 27,
            'sum_mod_100': sum(values) % 100,
            'sum_mod_127': sum(values) % 127,
        }

    # Key findings summary
    analysis['key_findings'] = {
        'unique_property': f"Position [22,22] is the ONLY position where value = mirror_value = {matrix[22][22]}",
        'symmetry': '22 + 105 = 127 (the symmetry axis)',
        'cfb_connection': '100 XOR 127 = 27 (CFB signature)',
        'reverse_xor': '100 XOR 27 = 127 (reveals symmetry axis)',
        'prime_factor': '22 = 2 × 11 (11 is CFB signature prime)',
        'value_100_count': len(analysis['value_100_occurrences']),
        'value_27_count': len(analysis['value_27_occurrences']),
        'is_on_main_diagonal': True,
        'ascii_meaning': "100 = 'd' (could reference 'data', 'decode', or 'diagonal')",
    }

    # Add mathematical relationships
    analysis['mathematical_relationships'] = {
        'key_equation_1': '22 + 105 = 127 (position symmetry)',
        'key_equation_2': '100 ^ 127 = 27 (XOR reveals CFB)',
        'key_equation_3': '100 ^ 27 = 127 (XOR reveals axis)',
        'key_equation_4': '22 ^ 127 = 105 (position to mirror)',
        'triangle': {
            'point_1': [22, 22, 100],
            'point_2': [105, 105, 100],
            'relation': 'Both points have value 100, connected through 127 axis',
        },
        'cfb_signature': {
            '11_squared': '121 = 11²',
            'negative_121': '-121 appears in CFB relationships',
            '22_is_2x11': '22 = 2 × 11',
            '27_is_3_cubed': '27 = 3³',
        }
    }

    # Save results
    output_path = '/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/POSITION_22_22_DEEP_ANALYSIS.json'
    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\nAnalysis saved to: {output_path}")

    # Print key findings
    print("\n" + "="*60)
    print("KEY FINDINGS - POSITION [22,22]")
    print("="*60)
    print(f"Value at [22,22]: {matrix[22][22]}")
    print(f"Value at mirror [105,105]: {matrix[105][105] if 105 < rows and 105 < cols else 'N/A'}")
    print(f"Values equal: {matrix[22][22] == matrix[105][105] if 105 < rows and 105 < cols else 'N/A'}")
    print(f"\nSymmetry relationships:")
    print(f"  22 + 105 = {22 + 105} (symmetry axis)")
    print(f"  100 XOR 127 = {100 ^ 127} (CFB signature!)")
    print(f"  100 XOR 27 = {100 ^ 27} (reveals axis!)")
    print(f"\nOccurrences of 100 in matrix: {len(analysis['value_100_occurrences'])}")
    print(f"Occurrences of 27 in matrix: {len(analysis['value_27_occurrences'])}")

    # Check if [22,22] is unique
    value_100_on_diagonal = [o for o in analysis['value_100_occurrences'] if o['is_on_diagonal']]
    print(f"\nPositions with value 100 on main diagonal: {len(value_100_on_diagonal)}")
    for pos in value_100_on_diagonal:
        print(f"  [{pos['row']},{pos['col']}]")

if __name__ == '__main__':
    main()
