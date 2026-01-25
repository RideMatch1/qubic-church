#!/usr/bin/env python3
"""
Anna Matrix Diagonal Message Analysis
=====================================
Searches for hidden messages along diagonals of the Anna Matrix.
"""

import json
import os
from pathlib import Path

# Load the matrix
MATRIX_PATH = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
OUTPUT_PATH = Path(__file__).parent / "DIAGONAL_MESSAGES.json"

def load_matrix():
    """Load the Anna Matrix from JSON file."""
    with open(MATRIX_PATH, 'r') as f:
        data = json.load(f)

    # The matrix could be stored in different formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        if 'matrix' in data:
            return data['matrix']
        elif 'data' in data:
            return data['data']

    return data

def values_to_ascii(values):
    """Convert list of values to ASCII string, handling non-printable chars."""
    result = []
    printable_count = 0

    for v in values:
        if isinstance(v, (int, float)):
            v = int(v)
            if 32 <= v <= 126:  # Printable ASCII
                result.append(chr(v))
                printable_count += 1
            elif v == 0:
                result.append('.')  # Null
            elif v == 10 or v == 13:
                result.append('\\n')  # Newline
                printable_count += 1
            else:
                result.append(f'[{v}]')
        else:
            result.append(str(v))

    return ''.join(result), printable_count

def find_readable_sequences(values, min_length=3):
    """Find sequences of printable ASCII characters."""
    sequences = []
    current_seq = []
    current_start = 0

    for i, v in enumerate(values):
        if isinstance(v, (int, float)):
            v = int(v)
            if 32 <= v <= 126:  # Printable ASCII
                if not current_seq:
                    current_start = i
                current_seq.append(chr(v))
            else:
                if len(current_seq) >= min_length:
                    sequences.append({
                        'text': ''.join(current_seq),
                        'start': current_start,
                        'end': i - 1,
                        'length': len(current_seq)
                    })
                current_seq = []

    # Check last sequence
    if len(current_seq) >= min_length:
        sequences.append({
            'text': ''.join(current_seq),
            'start': current_start,
            'end': len(values) - 1,
            'length': len(current_seq)
        })

    return sequences

def extract_main_diagonal(matrix):
    """Extract main diagonal where row == col."""
    size = len(matrix)
    values = []

    for i in range(min(size, len(matrix[0]) if matrix else 0)):
        if i < len(matrix) and i < len(matrix[i]):
            values.append(matrix[i][i])

    return values

def extract_anti_diagonal(matrix):
    """Extract anti-diagonal where row + col = size - 1."""
    size = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    values = []

    # For a 128x128 matrix, row + col = 127
    target_sum = min(size, cols) - 1

    for i in range(size):
        j = target_sum - i
        if 0 <= j < cols and i < len(matrix) and j < len(matrix[i]):
            values.append(matrix[i][j])

    return values

def extract_parallel_diagonal(matrix, offset):
    """Extract diagonal parallel to main diagonal with given offset."""
    size = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    values = []

    for i in range(size):
        j = i + offset
        if 0 <= j < cols and i < len(matrix) and j < len(matrix[i]):
            values.append(matrix[i][j])

    return values

def extract_parallel_anti_diagonal(matrix, offset):
    """Extract diagonal parallel to anti-diagonal with given offset."""
    size = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    values = []

    # For a 128x128 matrix, base is row + col = 127
    target_sum = min(size, cols) - 1 + offset

    for i in range(size):
        j = target_sum - i
        if 0 <= j < cols and i < len(matrix) and j < len(matrix[i]):
            values.append(matrix[i][j])

    return values

def xor_lists(list1, list2):
    """XOR two lists element by element."""
    result = []
    for i in range(min(len(list1), len(list2))):
        v1 = int(list1[i]) if isinstance(list1[i], (int, float)) else 0
        v2 = int(list2[i]) if isinstance(list2[i], (int, float)) else 0
        result.append(v1 ^ v2)
    return result

def get_fibonacci_positions(max_pos):
    """Generate Fibonacci positions up to max_pos."""
    fibs = [0, 1]
    while fibs[-1] < max_pos:
        fibs.append(fibs[-1] + fibs[-2])
    return [f for f in fibs if f < max_pos]

def get_mersenne_positions():
    """Get Mersenne number positions: 2^n - 1."""
    return [1, 3, 7, 15, 31, 63, 127]

def analyze_special_positions(values, positions, name):
    """Analyze values at special positions."""
    result = {
        'name': name,
        'positions_checked': [],
        'values': [],
        'ascii_chars': [],
        'combined_text': ''
    }

    for pos in positions:
        if pos < len(values):
            val = values[pos]
            result['positions_checked'].append(pos)
            result['values'].append(val)

            if isinstance(val, (int, float)):
                v = int(val)
                if 32 <= v <= 126:
                    result['ascii_chars'].append(chr(v))
                else:
                    result['ascii_chars'].append(f'[{v}]')
            else:
                result['ascii_chars'].append(str(val))

    result['combined_text'] = ''.join(result['ascii_chars'])
    return result

def main():
    print("Loading Anna Matrix...")
    matrix = load_matrix()

    if not matrix:
        print("ERROR: Could not load matrix")
        return

    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    print(f"Matrix size: {rows} x {cols}")

    results = {
        'matrix_info': {
            'rows': rows,
            'cols': cols,
            'source': str(MATRIX_PATH)
        },
        'main_diagonal': {},
        'anti_diagonal': {},
        'parallel_diagonals': [],
        'xor_analysis': {},
        'special_positions': {},
        'notable_findings': []
    }

    # 1. Main diagonal (row = col)
    print("\n=== Main Diagonal (row == col) ===")
    main_diag = extract_main_diagonal(matrix)
    results['main_diagonal']['values'] = main_diag[:128]  # First 128
    results['main_diagonal']['length'] = len(main_diag)

    ascii_str, printable = values_to_ascii(main_diag)
    results['main_diagonal']['ascii_string'] = ascii_str
    results['main_diagonal']['printable_count'] = printable

    sequences = find_readable_sequences(main_diag)
    results['main_diagonal']['readable_sequences'] = sequences

    print(f"  Length: {len(main_diag)}")
    print(f"  Printable chars: {printable}/{len(main_diag)}")
    if sequences:
        print(f"  Readable sequences found: {len(sequences)}")
        for seq in sequences:
            print(f"    [{seq['start']}-{seq['end']}]: \"{seq['text']}\"")
            results['notable_findings'].append({
                'location': 'main_diagonal',
                'position': f"{seq['start']}-{seq['end']}",
                'text': seq['text'],
                'type': 'readable_sequence'
            })

    # Check special position [22,22]
    if 22 < len(main_diag):
        val_22 = main_diag[22]
        print(f"  Position [22,22] value: {val_22}")
        results['main_diagonal']['position_22'] = val_22

    # Check special position [51,51]
    if 51 < len(main_diag):
        val_51 = main_diag[51]
        print(f"  Position [51,51] value: {val_51}")
        results['main_diagonal']['position_51'] = val_51

    # 2. Anti-diagonal (row + col = 127)
    print("\n=== Anti-Diagonal (row + col = 127) ===")
    anti_diag = extract_anti_diagonal(matrix)
    results['anti_diagonal']['values'] = anti_diag[:128]
    results['anti_diagonal']['length'] = len(anti_diag)

    ascii_str, printable = values_to_ascii(anti_diag)
    results['anti_diagonal']['ascii_string'] = ascii_str
    results['anti_diagonal']['printable_count'] = printable

    sequences = find_readable_sequences(anti_diag)
    results['anti_diagonal']['readable_sequences'] = sequences

    print(f"  Length: {len(anti_diag)}")
    print(f"  Printable chars: {printable}/{len(anti_diag)}")
    if sequences:
        print(f"  Readable sequences found: {len(sequences)}")
        for seq in sequences:
            print(f"    [{seq['start']}-{seq['end']}]: \"{seq['text']}\"")
            results['notable_findings'].append({
                'location': 'anti_diagonal',
                'position': f"{seq['start']}-{seq['end']}",
                'text': seq['text'],
                'type': 'readable_sequence'
            })

    # 3. Parallel diagonals (±1, ±2, ±3 from main)
    print("\n=== Parallel Diagonals ===")
    for offset in [-3, -2, -1, 1, 2, 3]:
        diag = extract_parallel_diagonal(matrix, offset)
        ascii_str, printable = values_to_ascii(diag)
        sequences = find_readable_sequences(diag)

        diag_result = {
            'offset': offset,
            'type': 'main_parallel',
            'length': len(diag),
            'values': diag[:128] if len(diag) > 128 else diag,
            'ascii_string': ascii_str,
            'printable_count': printable,
            'readable_sequences': sequences
        }
        results['parallel_diagonals'].append(diag_result)

        print(f"  Main+{offset}: length={len(diag)}, printable={printable}")
        if sequences:
            for seq in sequences:
                print(f"    [{seq['start']}-{seq['end']}]: \"{seq['text']}\"")
                results['notable_findings'].append({
                    'location': f'main_diagonal_offset_{offset}',
                    'position': f"{seq['start']}-{seq['end']}",
                    'text': seq['text'],
                    'type': 'readable_sequence'
                })

    # Parallel anti-diagonals
    for offset in [-3, -2, -1, 1, 2, 3]:
        diag = extract_parallel_anti_diagonal(matrix, offset)
        ascii_str, printable = values_to_ascii(diag)
        sequences = find_readable_sequences(diag)

        diag_result = {
            'offset': offset,
            'type': 'anti_parallel',
            'length': len(diag),
            'values': diag[:128] if len(diag) > 128 else diag,
            'ascii_string': ascii_str,
            'printable_count': printable,
            'readable_sequences': sequences
        }
        results['parallel_diagonals'].append(diag_result)

        print(f"  Anti+{offset}: length={len(diag)}, printable={printable}")
        if sequences:
            for seq in sequences:
                print(f"    [{seq['start']}-{seq['end']}]: \"{seq['text']}\"")
                results['notable_findings'].append({
                    'location': f'anti_diagonal_offset_{offset}',
                    'position': f"{seq['start']}-{seq['end']}",
                    'text': seq['text'],
                    'type': 'readable_sequence'
                })

    # 4. XOR diagonals
    print("\n=== XOR Analysis ===")
    xor_result = xor_lists(main_diag, anti_diag)
    ascii_str, printable = values_to_ascii(xor_result)
    sequences = find_readable_sequences(xor_result)

    results['xor_analysis']['main_xor_anti'] = {
        'values': xor_result[:128],
        'ascii_string': ascii_str,
        'printable_count': printable,
        'readable_sequences': sequences
    }

    print(f"  Main XOR Anti: printable={printable}")
    if sequences:
        print(f"  Readable sequences found: {len(sequences)}")
        for seq in sequences:
            print(f"    [{seq['start']}-{seq['end']}]: \"{seq['text']}\"")
            results['notable_findings'].append({
                'location': 'xor_main_anti',
                'position': f"{seq['start']}-{seq['end']}",
                'text': seq['text'],
                'type': 'readable_sequence'
            })

    # XOR with key 22 (value at [22,22])
    if 22 < len(main_diag):
        key = int(main_diag[22])
        xor_with_key = [int(v) ^ key if isinstance(v, (int, float)) else 0 for v in main_diag]
        ascii_str, printable = values_to_ascii(xor_with_key)
        sequences = find_readable_sequences(xor_with_key)

        results['xor_analysis']['main_xor_key22'] = {
            'key': key,
            'values': xor_with_key[:128],
            'ascii_string': ascii_str,
            'printable_count': printable,
            'readable_sequences': sequences
        }

        print(f"  Main XOR key(22): printable={printable}")
        if sequences:
            for seq in sequences:
                print(f"    [{seq['start']}-{seq['end']}]: \"{seq['text']}\"")
                results['notable_findings'].append({
                    'location': 'xor_with_key_22',
                    'position': f"{seq['start']}-{seq['end']}",
                    'text': seq['text'],
                    'type': 'readable_sequence'
                })

    # 5. Special positions on diagonals
    print("\n=== Special Positions ===")

    # Fibonacci positions
    fib_positions = get_fibonacci_positions(len(main_diag))
    print(f"  Fibonacci positions: {fib_positions}")

    fib_main = analyze_special_positions(main_diag, fib_positions, 'fibonacci_main_diagonal')
    results['special_positions']['fibonacci_main'] = fib_main
    print(f"    Main diagonal Fibonacci: {fib_main['combined_text']}")

    fib_anti = analyze_special_positions(anti_diag, fib_positions, 'fibonacci_anti_diagonal')
    results['special_positions']['fibonacci_anti'] = fib_anti
    print(f"    Anti diagonal Fibonacci: {fib_anti['combined_text']}")

    # Mersenne positions
    mersenne_positions = get_mersenne_positions()
    print(f"  Mersenne positions: {mersenne_positions}")

    mersenne_main = analyze_special_positions(main_diag, mersenne_positions, 'mersenne_main_diagonal')
    results['special_positions']['mersenne_main'] = mersenne_main
    print(f"    Main diagonal Mersenne: {mersenne_main['combined_text']}")

    mersenne_anti = analyze_special_positions(anti_diag, mersenne_positions, 'mersenne_anti_diagonal')
    results['special_positions']['mersenne_anti'] = mersenne_anti
    print(f"    Anti diagonal Mersenne: {mersenne_anti['combined_text']}")

    # Powers of 2 positions
    pow2_positions = [1, 2, 4, 8, 16, 32, 64]
    print(f"  Power of 2 positions: {pow2_positions}")

    pow2_main = analyze_special_positions(main_diag, pow2_positions, 'power2_main_diagonal')
    results['special_positions']['power2_main'] = pow2_main
    print(f"    Main diagonal Powers of 2: {pow2_main['combined_text']}")

    pow2_anti = analyze_special_positions(anti_diag, pow2_positions, 'power2_anti_diagonal')
    results['special_positions']['power2_anti'] = pow2_anti
    print(f"    Anti diagonal Powers of 2: {pow2_anti['combined_text']}")

    # Prime positions
    prime_positions = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]
    prime_positions = [p for p in prime_positions if p < len(main_diag)]

    prime_main = analyze_special_positions(main_diag, prime_positions, 'prime_main_diagonal')
    results['special_positions']['prime_main'] = prime_main
    print(f"    Main diagonal Primes: {prime_main['combined_text'][:50]}...")

    prime_anti = analyze_special_positions(anti_diag, prime_positions, 'prime_anti_diagonal')
    results['special_positions']['prime_anti'] = prime_anti
    print(f"    Anti diagonal Primes: {prime_anti['combined_text'][:50]}...")

    # Look for specific patterns
    print("\n=== Pattern Analysis ===")

    # Check if diagonal values form a pattern
    unique_main = list(set(int(v) for v in main_diag if isinstance(v, (int, float))))
    unique_main.sort()
    results['pattern_analysis'] = {
        'unique_main_diagonal_values': unique_main,
        'unique_main_count': len(unique_main)
    }
    print(f"  Unique values in main diagonal: {len(unique_main)}")
    print(f"  Value range: {min(unique_main) if unique_main else 0} - {max(unique_main) if unique_main else 0}")

    # Check for value = position patterns
    position_matches = []
    for i, v in enumerate(main_diag):
        if isinstance(v, (int, float)) and int(v) == i:
            position_matches.append(i)
    results['pattern_analysis']['position_equals_value'] = position_matches
    if position_matches:
        print(f"  Positions where value == position: {position_matches}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY OF NOTABLE FINDINGS")
    print("="*60)

    if results['notable_findings']:
        for finding in results['notable_findings']:
            print(f"  Location: {finding['location']}")
            print(f"  Text: \"{finding['text']}\"")
            print()
    else:
        print("  No readable text sequences found in diagonals.")

    # Save results
    print(f"\nSaving results to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print("Done!")
    return results

if __name__ == "__main__":
    main()
