#!/usr/bin/env python3
"""
Anna Matrix Diagonal Message Analysis - Deep Investigation
============================================================
Extended analysis looking for hidden messages along diagonals.
"""

import json
from pathlib import Path

MATRIX_PATH = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
OUTPUT_PATH = Path(__file__).parent / "DIAGONAL_MESSAGES.json"

def load_matrix():
    """Load the Anna Matrix from JSON file."""
    with open(MATRIX_PATH, 'r') as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        if 'matrix' in data:
            return data['matrix']
        elif 'data' in data:
            return data['data']
    return data

def extract_main_diagonal(matrix):
    """Extract main diagonal where row == col."""
    return [matrix[i][i] for i in range(min(len(matrix), len(matrix[0])))]

def extract_anti_diagonal(matrix):
    """Extract anti-diagonal where row + col = 127."""
    size = len(matrix)
    target = size - 1
    return [matrix[i][target - i] for i in range(size)]

def try_decode_with_key(values, key, name):
    """Try decoding with a specific XOR key."""
    decoded = [int(v) ^ key for v in values]
    ascii_chars = []
    printable = 0
    for v in decoded:
        if 32 <= v <= 126:
            ascii_chars.append(chr(v))
            printable += 1
        else:
            ascii_chars.append('.')
    return {
        'key': key,
        'name': name,
        'text': ''.join(ascii_chars),
        'printable_ratio': printable / len(values) if values else 0,
        'printable_count': printable
    }

def look_for_symmetry(values):
    """Check for palindromic or symmetric patterns."""
    n = len(values)
    palindrome_chars = 0

    for i in range(n // 2):
        if values[i] == values[n - 1 - i]:
            palindrome_chars += 1

    return {
        'palindrome_positions': palindrome_chars,
        'palindrome_ratio': palindrome_chars / (n // 2) if n > 0 else 0
    }

def main():
    print("Loading Anna Matrix...")
    matrix = load_matrix()
    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    print(f"Matrix size: {rows} x {cols}")

    # Load existing results
    with open(OUTPUT_PATH, 'r') as f:
        results = json.load(f)

    main_diag = extract_main_diagonal(matrix)
    anti_diag = extract_anti_diagonal(matrix)

    # Deep analysis section
    results['deep_analysis'] = {}

    # 1. Check XOR patterns with interesting keys
    print("\n=== XOR with Various Keys ===")
    interesting_keys = [
        22,   # Position [22,22] is decode key
        100,  # Value at [22,22]
        127,  # Value at [51,51] and max 7-bit
        51,   # Position of 127
        65,   # ASCII 'A'
        97,   # ASCII 'a'
        48,   # ASCII '0'
        42,   # Answer to everything
        27,   # Qubic significance
        3,    # Ternary base
        9,    # 3^2
    ]

    results['deep_analysis']['xor_tests'] = []
    for key in interesting_keys:
        result = try_decode_with_key(main_diag, key, f'main_diag_xor_{key}')
        if result['printable_ratio'] > 0.4:
            print(f"  Key {key}: {result['printable_count']}/128 printable")
            print(f"    Text: {result['text']}")
        results['deep_analysis']['xor_tests'].append(result)

    # 2. Look for symmetry in main diagonal
    print("\n=== Symmetry Analysis ===")
    symmetry = look_for_symmetry(main_diag)
    results['deep_analysis']['main_diagonal_symmetry'] = symmetry
    print(f"  Main diagonal palindrome positions: {symmetry['palindrome_positions']}")

    anti_symmetry = look_for_symmetry(anti_diag)
    results['deep_analysis']['anti_diagonal_symmetry'] = anti_symmetry
    print(f"  Anti diagonal palindrome positions: {anti_symmetry['palindrome_positions']}")

    # 3. Extract all diagonals and look for complete messages
    print("\n=== All Diagonals Analysis ===")

    # Collect all diagonal values into one stream
    all_diag_stream = []
    for offset in range(-127, 128):
        for i in range(128):
            j = i + offset
            if 0 <= j < 128:
                all_diag_stream.append(matrix[i][j])

    # Try to find readable sequences in the stream
    results['deep_analysis']['diagonal_stream_length'] = len(all_diag_stream)

    # 4. Check specific interesting positions
    print("\n=== Specific Position Values ===")
    positions = {
        '[0,0]': matrix[0][0],
        '[22,22]': matrix[22][22],
        '[51,51]': matrix[51][51],
        '[63,63]': matrix[63][63],
        '[63,64]': matrix[63][64] if cols > 64 else None,
        '[64,63]': matrix[64][63] if rows > 64 else None,
        '[64,64]': matrix[64][64] if rows > 64 and cols > 64 else None,
        '[127,0]': matrix[127][0] if rows > 127 else None,
        '[0,127]': matrix[0][127] if cols > 127 else None,
        '[127,127]': matrix[127][127] if rows > 127 and cols > 127 else None,
    }

    results['deep_analysis']['specific_positions'] = positions
    for pos, val in positions.items():
        if val is not None:
            char = chr(val) if 32 <= val <= 126 else f'[{val}]'
            print(f"  {pos} = {val} ({char})")

    # 5. Check for diagonal messages with position-based XOR
    print("\n=== Position-Based XOR Decoding ===")
    # XOR each value with its position
    pos_xor_main = [int(main_diag[i]) ^ i for i in range(len(main_diag))]
    pos_xor_ascii = []
    printable = 0
    for v in pos_xor_main:
        if 32 <= v <= 126:
            pos_xor_ascii.append(chr(v))
            printable += 1
        else:
            pos_xor_ascii.append('.')

    results['deep_analysis']['position_xor_main'] = {
        'text': ''.join(pos_xor_ascii),
        'printable_count': printable,
        'values': pos_xor_main
    }
    print(f"  Main diagonal XOR position: {printable}/128 printable")
    print(f"    Text: {''.join(pos_xor_ascii)}")

    # 6. Look for "ZZZ" pattern significance
    print("\n=== ZZZ Pattern Analysis ===")
    # ZZZ appears at positions [36-38] on main diagonal
    # 'Z' = 90 in ASCII
    # Position 36, 37, 38 all have value 90

    zzz_analysis = {
        'positions': [36, 37, 38],
        'char': 'Z',
        'ascii_value': 90,
        'binary': bin(90),
        'observation': 'Three consecutive Z characters at positions 36-38'
    }

    # Check surrounding values
    zzz_context = []
    for i in range(max(0, 33), min(128, 42)):
        val = main_diag[i]
        char = chr(val) if 32 <= val <= 126 else f'[{val}]'
        zzz_context.append({'position': i, 'value': val, 'char': char})

    zzz_analysis['context'] = zzz_context
    results['deep_analysis']['zzz_pattern'] = zzz_analysis
    print(f"  ZZZ context: {zzz_context}")

    # 7. Diagonal cross-correlation
    print("\n=== Diagonal Cross-Correlation ===")
    correlation = 0
    for i in range(128):
        if main_diag[i] == anti_diag[i]:
            correlation += 1

    results['deep_analysis']['diagonal_correlation'] = {
        'matching_positions': correlation,
        'ratio': correlation / 128
    }
    print(f"  Matching positions main vs anti: {correlation}/128")

    # Find where they match
    matches = []
    for i in range(128):
        if main_diag[i] == anti_diag[i]:
            val = main_diag[i]
            char = chr(val) if 32 <= val <= 126 else f'[{val}]'
            matches.append({'position': i, 'value': val, 'char': char})

    results['deep_analysis']['diagonal_matches'] = matches
    if matches:
        print(f"  Match positions: {[m['position'] for m in matches]}")

    # 8. Check for hidden message patterns
    print("\n=== Hidden Message Search ===")

    # Check if first characters spell something
    first_chars_main = [main_diag[0], main_diag[1], main_diag[2], main_diag[3], main_diag[4]]
    first_chars_anti = [anti_diag[0], anti_diag[1], anti_diag[2], anti_diag[3], anti_diag[4]]

    results['deep_analysis']['first_five_main'] = {
        'values': first_chars_main,
        'ascii': ''.join(chr(v) if 32 <= v <= 126 else f'[{v}]' for v in first_chars_main)
    }

    results['deep_analysis']['first_five_anti'] = {
        'values': first_chars_anti,
        'ascii': ''.join(chr(v) if 32 <= v <= 126 else f'[{v}]' for v in first_chars_anti)
    }

    print(f"  First 5 main diagonal: {first_chars_main}")
    print(f"  First 5 anti diagonal: {first_chars_anti}")

    # 9. Check diagonal using different value interpretations
    print("\n=== Unsigned Byte Interpretation ===")
    # Convert signed to unsigned
    unsigned_main = [(v + 256) % 256 for v in main_diag]
    unsigned_ascii = ''.join(chr(v) if 32 <= v <= 126 else '.' for v in unsigned_main)
    printable = sum(1 for v in unsigned_main if 32 <= v <= 126)

    results['deep_analysis']['unsigned_main'] = {
        'values': unsigned_main,
        'ascii': unsigned_ascii,
        'printable': printable
    }
    print(f"  Unsigned main diagonal: {printable}/128 printable")
    print(f"    Text: {unsigned_ascii}")

    # 10. Look for the intersection point [63,64] or [64,63]
    print("\n=== Intersection Point Analysis ===")
    # The main and anti diagonals intersect at the center
    # For 128x128, intersection is around position 63-64

    center_region = {}
    for i in range(60, 68):
        for j in range(60, 68):
            key = f'[{i},{j}]'
            val = matrix[i][j]
            char = chr(val) if 32 <= val <= 126 else f'[{val}]'
            center_region[key] = {'value': val, 'char': char}
            # Check if on main diagonal
            if i == j:
                center_region[key]['on_main'] = True
            # Check if on anti diagonal
            if i + j == 127:
                center_region[key]['on_anti'] = True

    results['deep_analysis']['center_region'] = center_region
    print(f"  Center region (60-67, 60-67) extracted")

    # 11. Final summary: Most interesting findings
    print("\n" + "="*70)
    print("DEEP ANALYSIS SUMMARY")
    print("="*70)

    summary = []

    # Highlight significant findings
    summary.append({
        'finding': 'Position [22,22] contains value 100 (ASCII "d")',
        'significance': 'This position is identified as the decode key'
    })

    summary.append({
        'finding': 'Position [51,51] contains value 127 (DEL character)',
        'significance': 'Maximum 7-bit value at position 51'
    })

    summary.append({
        'finding': 'ZZZ pattern at positions 36-38',
        'significance': 'Three consecutive Z characters may indicate sleep/termination or padding'
    })

    summary.append({
        'finding': f'Main diagonal has {results["deep_analysis"]["main_diagonal_symmetry"]["palindrome_positions"]} palindromic positions',
        'significance': 'Some structural symmetry exists'
    })

    # Check for XOR patterns with high printable ratio
    best_xor = max(results['deep_analysis']['xor_tests'], key=lambda x: x['printable_ratio'])
    summary.append({
        'finding': f'Best XOR key: {best_xor["key"]} with {best_xor["printable_count"]} printable chars',
        'significance': 'Potential decode key'
    })

    results['deep_analysis']['summary'] = summary

    for item in summary:
        print(f"\n  Finding: {item['finding']}")
        print(f"  Significance: {item['significance']}")

    # Save updated results
    print(f"\n\nSaving updated results to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print("Deep analysis complete!")

if __name__ == "__main__":
    main()
