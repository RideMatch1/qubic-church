#!/usr/bin/env python3
"""
HIDDEN MESSAGE EXTRACTION: Focus on Anomalous Pairs and Message Decoding

Key Discovery: 60/64 pairs are PERFECTLY symmetric (palindromes).
The 4 NON-SYMMETRIC pairs may contain intentional messages!

Non-symmetric pairs:
- Pair 0 <-> 127: 98.4% symmetry
- Pair 22 <-> 105: 79.7% symmetry
- Pair 30 <-> 97: 78.1% symmetry
- Pair 41 <-> 86: 96.9% symmetry

This script extracts and analyzes the ASYMMETRIC portions.
"""

import json
from typing import Dict, List, Any
from datetime import datetime

MATRIX_PATH = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json"
OUTPUT_PATH = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/HIDDEN_MESSAGES_EXTRACTED.json"


def safe_int_value(val) -> int:
    """Safely convert a value to int."""
    if isinstance(val, int):
        return val
    elif isinstance(val, str):
        try:
            return int(val)
        except ValueError:
            return 0
    elif isinstance(val, float):
        return int(val)
    return 0


def load_matrix() -> List[List[int]]:
    """Load the Anna Matrix."""
    with open(MATRIX_PATH, 'r') as f:
        data = json.load(f)
    return data.get('matrix', data)


def compute_xor_pair(matrix: List[List[int]], col_a: int, col_b: int) -> List[int]:
    """Compute XOR values for a column pair."""
    xor_values = []
    for row in matrix:
        val_a = safe_int_value(row[col_a]) % 256 if col_a < len(row) else 0
        val_b = safe_int_value(row[col_b]) % 256 if col_b < len(row) else 0
        xor_values.append(val_a ^ val_b)
    return xor_values


def is_printable(v: int) -> bool:
    return 32 <= v <= 126


def xor_to_text(xor_values: List[int]) -> str:
    return "".join(chr(v) if is_printable(v) else "." for v in xor_values)


def find_asymmetric_positions(xor_values: List[int]) -> List[Dict[str, Any]]:
    """Find positions where the palindrome breaks."""
    n = len(xor_values)
    asymmetric = []

    for i in range(n // 2):
        mirror_idx = n - 1 - i
        if xor_values[i] != xor_values[mirror_idx]:
            left_char = chr(xor_values[i]) if is_printable(xor_values[i]) else f"[{xor_values[i]}]"
            right_char = chr(xor_values[mirror_idx]) if is_printable(xor_values[mirror_idx]) else f"[{xor_values[mirror_idx]}]"
            asymmetric.append({
                "left_pos": i,
                "right_pos": mirror_idx,
                "left_value": xor_values[i],
                "right_value": xor_values[mirror_idx],
                "left_char": left_char,
                "right_char": right_char
            })

    return asymmetric


def extract_message_from_asymmetry(asymmetric_positions: List[Dict]) -> str:
    """Try to extract a message from the asymmetric chars."""
    # Collect just the left-side asymmetric chars
    left_chars = []
    for pos in sorted(asymmetric_positions, key=lambda x: x["left_pos"]):
        if is_printable(pos["left_value"]):
            left_chars.append(chr(pos["left_value"]))
        else:
            left_chars.append('.')

    # And the right-side chars (reversed positions)
    right_chars = []
    for pos in sorted(asymmetric_positions, key=lambda x: x["right_pos"]):
        if is_printable(pos["right_value"]):
            right_chars.append(chr(pos["right_value"]))
        else:
            right_chars.append('.')

    return "".join(left_chars), "".join(right_chars)


def analyze_first_half_vs_second_half(xor_values: List[int]) -> Dict[str, Any]:
    """Compare first half to reversed second half in detail."""
    n = len(xor_values)
    half = n // 2

    first_half = xor_values[:half]
    second_half = xor_values[half:]
    second_half_reversed = second_half[::-1]

    first_text = xor_to_text(first_half)
    second_text = xor_to_text(second_half_reversed)

    # Find differences
    differences = []
    for i in range(half):
        if first_half[i] != second_half_reversed[i]:
            differences.append({
                "position": i,
                "first_half": first_half[i],
                "second_half_rev": second_half_reversed[i],
                "first_char": chr(first_half[i]) if is_printable(first_half[i]) else f"[{first_half[i]}]",
                "second_char": chr(second_half_reversed[i]) if is_printable(second_half_reversed[i]) else f"[{second_half_reversed[i]}]"
            })

    return {
        "first_half_text": first_text,
        "second_half_reversed_text": second_text,
        "difference_count": len(differences),
        "differences": differences
    }


def try_decode_schemes(xor_values: List[int]) -> Dict[str, str]:
    """Try various decoding schemes on the XOR values."""
    n = len(xor_values)
    half = n // 2

    decodings = {}

    # 1. Simple ASCII
    decodings["ascii"] = xor_to_text(xor_values)

    # 2. Only first half
    decodings["first_half"] = xor_to_text(xor_values[:half])

    # 3. Only asymmetric positions (XOR of differences)
    first_half = xor_values[:half]
    second_half_rev = xor_values[half:][::-1]

    diff_xor = []
    for i in range(half):
        diff_xor.append(first_half[i] ^ second_half_rev[i])
    decodings["diff_xor"] = xor_to_text(diff_xor)

    # 4. Average of symmetric positions
    avg_vals = []
    for i in range(half):
        avg_vals.append((first_half[i] + second_half_rev[i]) // 2)
    decodings["symmetric_average"] = xor_to_text(avg_vals)

    # 5. Every Nth character
    for step in [2, 3, 4]:
        decodings[f"every_{step}th"] = xor_to_text(xor_values[::step])

    # 6. Extract only printable chars
    printable = [v for v in xor_values if is_printable(v)]
    decodings["printable_only"] = "".join(chr(v) for v in printable)

    # 7. Subtract 32 (shift)
    shifted = [(v - 32) % 256 for v in xor_values]
    decodings["shifted_minus_32"] = xor_to_text(shifted)

    return decodings


def analyze_anomalous_pair(matrix: List[List[int]], col_a: int, col_b: int) -> Dict[str, Any]:
    """Deep analysis of an anomalous (non-symmetric) pair."""
    xor_values = compute_xor_pair(matrix, col_a, col_b)
    text = xor_to_text(xor_values)

    asymmetric = find_asymmetric_positions(xor_values)
    left_msg, right_msg = extract_message_from_asymmetry(asymmetric)

    half_comparison = analyze_first_half_vs_second_half(xor_values)
    decodings = try_decode_schemes(xor_values)

    # Symmetry percentage
    symmetric_count = len(xor_values) // 2 - len(asymmetric)
    symmetry_pct = symmetric_count / (len(xor_values) // 2) * 100

    return {
        "pair": f"{col_a} <-> {col_b}",
        "col_a": col_a,
        "col_b": col_b,
        "symmetry_percentage": round(symmetry_pct, 2),
        "asymmetric_position_count": len(asymmetric),
        "full_text": text,
        "asymmetric_positions": asymmetric,
        "left_message_from_asymmetry": left_msg,
        "right_message_from_asymmetry": right_msg,
        "half_comparison": half_comparison,
        "decoding_attempts": decodings
    }


def main():
    print("="*70)
    print("HIDDEN MESSAGE EXTRACTION")
    print("Analyzing Non-Symmetric Column Pairs for Intentional Messages")
    print("="*70)
    print()

    matrix = load_matrix()
    print(f"Matrix loaded: {len(matrix)} x {len(matrix[0])}")

    # The 4 anomalous pairs identified
    anomalous_pairs = [
        (0, 127),   # 98.4% symmetry
        (22, 105),  # 79.7% symmetry
        (30, 97),   # 78.1% symmetry
        (41, 86)    # 96.9% symmetry
    ]

    results = []

    for col_a, col_b in anomalous_pairs:
        print(f"\n{'='*60}")
        print(f"ANALYZING PAIR {col_a} <-> {col_b}")
        print(f"{'='*60}")

        analysis = analyze_anomalous_pair(matrix, col_a, col_b)
        results.append(analysis)

        print(f"\nSymmetry: {analysis['symmetry_percentage']}%")
        print(f"Asymmetric positions: {analysis['asymmetric_position_count']}")

        print(f"\n--- Full Text (128 chars) ---")
        print(analysis['full_text'])

        print(f"\n--- First Half ---")
        print(analysis['half_comparison']['first_half_text'])

        print(f"\n--- Second Half (Reversed) ---")
        print(analysis['half_comparison']['second_half_reversed_text'])

        print(f"\n--- Message from Left Asymmetric Chars ---")
        print(analysis['left_message_from_asymmetry'])

        print(f"\n--- Message from Right Asymmetric Chars ---")
        print(analysis['right_message_from_asymmetry'])

        print(f"\n--- Difference XOR ---")
        print(analysis['decoding_attempts']['diff_xor'])

        print(f"\n--- Asymmetric Positions Detail ---")
        for pos in analysis['asymmetric_positions'][:10]:
            print(f"  Row {pos['left_pos']:3d} vs Row {pos['right_pos']:3d}: "
                  f"'{pos['left_char']}' ({pos['left_value']}) vs "
                  f"'{pos['right_char']}' ({pos['right_value']})")
        if len(analysis['asymmetric_positions']) > 10:
            print(f"  ... and {len(analysis['asymmetric_positions']) - 10} more positions")

    # Now analyze ALL pairs for any hidden patterns in the printable sequences
    print(f"\n\n{'='*70}")
    print("ANALYZING ALL 64 PAIRS FOR HIDDEN MESSAGES")
    print("='*70")

    all_pairs_printable = []
    for col_a in range(64):
        col_b = 127 - col_a
        xor_values = compute_xor_pair(matrix, col_a, col_b)
        text = xor_to_text(xor_values)

        # Extract only printable chars
        printable = "".join(c for c in text if c != '.')

        if len(printable) >= 10:
            all_pairs_printable.append({
                "pair": f"{col_a} <-> {col_b}",
                "printable_length": len(printable),
                "printable_text": printable,
                # Look for message in first half only (since it's palindrome)
                "first_half_printable": "".join(c for c in text[:64] if c != '.')
            })

    # Sort by printable length
    all_pairs_printable.sort(key=lambda x: x["printable_length"], reverse=True)

    print("\nTop 15 Pairs by Printable Content:\n")
    for item in all_pairs_printable[:15]:
        print(f"{item['pair']}: ({item['printable_length']} chars)")
        print(f"  First half: {item['first_half_printable'][:80]}")
        print()

    # Look for common words/patterns across all pairs
    print("\n" + "="*70)
    print("SEARCHING FOR COMMON WORDS ACROSS ALL PAIRS")
    print("="*70)

    common_words = {}
    import re

    for item in all_pairs_printable:
        words = re.findall(r'[a-zA-Z]{3,}', item['printable_text'])
        for word in words:
            word_lower = word.lower()
            if word_lower not in common_words:
                common_words[word_lower] = []
            common_words[word_lower].append(item['pair'])

    # Find words appearing in multiple pairs
    multi_pair_words = {w: pairs for w, pairs in common_words.items() if len(pairs) > 1}
    print("\nWords appearing in multiple pairs:")
    for word, pairs in sorted(multi_pair_words.items(), key=lambda x: -len(x[1])):
        print(f"  '{word}': {pairs}")

    # Save output
    output = {
        "analysis_timestamp": datetime.now().isoformat(),
        "key_finding": "4 pairs break the palindrome symmetry - may contain messages",
        "anomalous_pairs_analysis": results,
        "all_pairs_printable_content": all_pairs_printable,
        "multi_pair_words": multi_pair_words
    }

    print(f"\nSaving to: {OUTPUT_PATH}")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

    return output


if __name__ == "__main__":
    main()
