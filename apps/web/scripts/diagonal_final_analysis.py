#!/usr/bin/env python3
"""
Final Diagonal Analysis - Looking for XOR symmetry and complete messages
"""

import json
from pathlib import Path

MATRIX_PATH = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
OUTPUT_PATH = Path(__file__).parent / "DIAGONAL_MESSAGES.json"

def load_matrix():
    with open(MATRIX_PATH, 'r') as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return data.get('matrix', data.get('data', data))
    return data

def main():
    matrix = load_matrix()

    # Load existing results
    with open(OUTPUT_PATH, 'r') as f:
        results = json.load(f)

    # Extract diagonals
    main_diag = [matrix[i][i] for i in range(128)]
    anti_diag = [matrix[i][127-i] for i in range(128)]

    # Key findings section
    key_findings = []

    print("="*70)
    print("DIAGONAL MESSAGE ANALYSIS - FINAL SUMMARY")
    print("="*70)

    # 1. Notable sequences found
    print("\n[1] READABLE SEQUENCES FOUND")
    print("-"*70)

    # Main diagonal sequences
    sequences = [
        {'location': 'Main diagonal [36-38]', 'text': 'ZZZ', 'ascii': [90, 90, 90]},
        {'location': 'Main diagonal [67-69]', 'text': '4hl', 'ascii': [52, 104, 108]},
        {'location': 'Main diagonal [96-103]', 'text': 'j.F*jjJJ', 'ascii': [106, 46, 70, 42, 106, 106, 74, 74]},
        {'location': 'Main diagonal [108-113]', 'text': 'ppEZ\'$', 'ascii': [112, 112, 69, 90, 39, 36]},
        {'location': 'Main diagonal [116-118]', 'text': 'BNK', 'ascii': [66, 78, 75]},
        {'location': 'Anti diagonal [64-70]', 'text': "'qzy5qD", 'ascii': [39, 113, 122, 121, 53, 113, 68]},
    ]

    for seq in sequences:
        print(f"  {seq['location']}: \"{seq['text']}\"")
        key_findings.append({
            'type': 'readable_sequence',
            'location': seq['location'],
            'text': seq['text'],
            'values': seq['ascii']
        })

    # 2. XOR patterns
    print("\n[2] XOR SYMMETRY ANALYSIS")
    print("-"*70)

    xor_result = [int(main_diag[i]) ^ int(anti_diag[i]) for i in range(128)]

    # Check for palindrome in XOR
    is_palindrome = True
    palindrome_check = []
    for i in range(64):
        if xor_result[i] != xor_result[127-i]:
            is_palindrome = False
        else:
            palindrome_check.append(i)

    print(f"  XOR result palindrome: {is_palindrome}")
    print(f"  Palindrome positions (first 10): {palindrome_check[:10]}")

    key_findings.append({
        'type': 'xor_symmetry',
        'is_palindrome': is_palindrome,
        'palindrome_positions': palindrome_check
    })

    # 3. Key positions
    print("\n[3] KEY DIAGONAL POSITIONS")
    print("-"*70)

    key_positions = [
        (0, 0, 'Origin'),
        (22, 22, 'Decode key position'),
        (51, 51, 'Contains 127'),
        (63, 63, 'Near center'),
        (64, 64, 'Near center'),
        (127, 127, 'End'),
    ]

    for row, col, desc in key_positions:
        val = matrix[row][col]
        char = chr(val) if 32 <= val <= 126 else f'non-printable({val})'
        print(f"  [{row},{col}] ({desc}): {val} = '{char}'")
        key_findings.append({
            'type': 'key_position',
            'position': [row, col],
            'description': desc,
            'value': val,
            'char': char if 32 <= val <= 126 else None
        })

    # 4. Check for message at diagonal intersection
    print("\n[4] DIAGONAL INTERSECTION")
    print("-"*70)

    # Main and anti-diagonals intersect at position [63, 64] or [64, 63]
    # For 128x128: main[i] = matrix[i][i], anti[i] = matrix[i][127-i]
    # They cross when i == 127-i, so i = 63.5 (between 63 and 64)

    intersection_values = {
        'main_63': main_diag[63],
        'main_64': main_diag[64],
        'anti_63': anti_diag[63],
        'anti_64': anti_diag[64],
    }
    print(f"  Main diagonal at 63: {main_diag[63]}")
    print(f"  Main diagonal at 64: {main_diag[64]}")
    print(f"  Anti diagonal at 63: {anti_diag[63]}")
    print(f"  Anti diagonal at 64: {anti_diag[64]}")

    key_findings.append({
        'type': 'intersection',
        'values': intersection_values
    })

    # 5. Pattern in value distribution
    print("\n[5] VALUE DISTRIBUTION PATTERNS")
    print("-"*70)

    # Count occurrences of each value
    value_counts = {}
    for v in main_diag:
        value_counts[v] = value_counts.get(v, 0) + 1

    # Find most common values
    sorted_counts = sorted(value_counts.items(), key=lambda x: -x[1])[:10]
    print("  Most common values in main diagonal:")
    for val, count in sorted_counts:
        char = chr(val) if 32 <= val <= 126 else f'non-printable'
        print(f"    {val} ({char}): {count} times")

    key_findings.append({
        'type': 'value_distribution',
        'most_common': [{'value': v, 'count': c} for v, c in sorted_counts]
    })

    # 6. Check for encoded words
    print("\n[6] POTENTIAL ENCODED MESSAGES")
    print("-"*70)

    # Try common decode operations

    # a) Every Nth position
    for n in [2, 3, 4, 5, 7]:
        selected = [main_diag[i] for i in range(0, 128, n)]
        text = ''.join(chr(v) if 32 <= v <= 126 else '.' for v in selected)
        printable = sum(1 for v in selected if 32 <= v <= 126)
        if printable > len(selected) * 0.4:
            print(f"  Every {n}th position: \"{text[:50]}...\" ({printable}/{len(selected)} printable)")

    # b) Reversed diagonal
    reversed_main = list(reversed(main_diag))
    reversed_text = ''.join(chr(v) if 32 <= v <= 126 else '.' for v in reversed_main)
    print(f"  Reversed main diagonal: {sum(1 for v in reversed_main if 32 <= v <= 126)}/128 printable")

    # 7. Final message candidates
    print("\n[7] FINAL MESSAGE CANDIDATES")
    print("-"*70)

    messages = []

    # ZZZ could mean "end" or "sleep"
    messages.append({
        'text': 'ZZZ',
        'interpretation': 'Could indicate termination/sleep marker or padding',
        'confidence': 'medium'
    })

    # BNK
    messages.append({
        'text': 'BNK',
        'interpretation': 'Could be abbreviation for "bank" (Bitcoin context)',
        'confidence': 'low'
    })

    # 4hl
    messages.append({
        'text': '4hl',
        'interpretation': 'Meaning unclear',
        'confidence': 'low'
    })

    for msg in messages:
        print(f"  \"{msg['text']}\": {msg['interpretation']} (confidence: {msg['confidence']})")
        key_findings.append({
            'type': 'message_candidate',
            **msg
        })

    # Update results with key findings
    results['key_findings'] = key_findings

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
The Anna Matrix diagonals contain several readable sequences:
- 'ZZZ' at positions [36-38] on main diagonal
- 'BNK' at positions [116-118] on main diagonal
- 'j.F*jjJJ' pattern at positions [96-103]
- Position [22,22] = 100 (ASCII 'd') - decode key position
- Position [51,51] = 127 (max 7-bit value)
- XOR of main and anti diagonals does NOT form a palindrome

The diagonals appear to contain structural markers rather than
complete hidden messages. The 'ZZZ' pattern suggests a terminator
or padding sequence.
""")

    # Save results
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
