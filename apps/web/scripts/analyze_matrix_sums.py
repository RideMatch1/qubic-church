#!/usr/bin/env python3
"""
Anna Matrix Sum Analysis - Searching for Hidden Messages

This script analyzes the Anna Matrix by computing row and column sums,
applying various modulo operations and transformations to decode
potential hidden messages.
"""

import json
import numpy as np
from pathlib import Path

# Paths
MATRIX_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json")
OUTPUT_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/SUM_MESSAGES.json")


def load_matrix():
    """Load the Anna Matrix from JSON file."""
    with open(MATRIX_PATH, 'r') as f:
        data = json.load(f)

    # Handle different possible formats
    if isinstance(data, list):
        if isinstance(data[0], list):
            # Direct 2D array - convert to integers
            return np.array(data, dtype=np.int64)
        elif isinstance(data[0], dict):
            # Array of objects with row data
            rows = []
            for item in data:
                if 'values' in item:
                    rows.append([int(v) for v in item['values']])
                elif 'row' in item:
                    rows.append([int(v) for v in item['row']])
                else:
                    # Try to extract numeric values
                    row_vals = [int(v) for v in item.values() if isinstance(v, (int, float, str)) and str(v).lstrip('-').isdigit()]
                    if row_vals:
                        rows.append(row_vals)
            return np.array(rows, dtype=np.int64)
    elif isinstance(data, dict):
        if 'matrix' in data:
            return np.array(data['matrix'], dtype=np.int64)
        elif 'data' in data:
            return np.array(data['data'], dtype=np.int64)
        elif 'rows' in data:
            return np.array(data['rows'], dtype=np.int64)

    raise ValueError(f"Unknown matrix format: {type(data)}")


def bytes_to_ascii(byte_values, filter_printable=False):
    """Convert byte values to ASCII string."""
    result = ""
    for b in byte_values:
        b_int = int(b) % 256
        if filter_printable:
            if 32 <= b_int <= 126:
                result += chr(b_int)
            else:
                result += "."
        else:
            try:
                result += chr(b_int) if 0 <= b_int < 256 else "?"
            except:
                result += "?"
    return result


def find_readable_segments(text, min_length=3):
    """Find readable ASCII segments in text."""
    segments = []
    current = ""
    start_idx = 0

    for i, c in enumerate(text):
        if c.isalnum() or c in " .,!?-_:;'\"":
            if not current:
                start_idx = i
            current += c
        else:
            if len(current) >= min_length:
                segments.append({
                    "text": current,
                    "start": start_idx,
                    "end": i - 1,
                    "length": len(current)
                })
            current = ""

    if len(current) >= min_length:
        segments.append({
            "text": current,
            "start": start_idx,
            "end": len(text) - 1,
            "length": len(current)
        })

    return segments


def analyze_matrix(matrix):
    """Perform comprehensive sum analysis on the matrix."""
    results = {
        "matrix_shape": list(matrix.shape),
        "matrix_stats": {
            "min": float(np.min(matrix)),
            "max": float(np.max(matrix)),
            "mean": float(np.mean(matrix)),
            "sum": float(np.sum(matrix))
        },
        "row_sums": {},
        "column_sums": {},
        "partial_sums": {},
        "xor_reduction": {},
        "modulo_operations": {},
        "cumulative_patterns": {},
        "interesting_findings": []
    }

    num_rows, num_cols = matrix.shape

    # =====================
    # 1. ROW SUMS ANALYSIS
    # =====================
    print("\n=== ROW SUMS ANALYSIS ===")

    row_sums = np.sum(matrix, axis=1)
    results["row_sums"]["raw"] = [int(s) for s in row_sums]

    # Mod 256 -> ASCII
    row_mod256 = row_sums % 256
    row_ascii = bytes_to_ascii(row_mod256)
    row_ascii_printable = bytes_to_ascii(row_mod256, filter_printable=True)
    results["row_sums"]["mod256"] = [int(m) for m in row_mod256]
    results["row_sums"]["mod256_ascii"] = row_ascii_printable
    results["row_sums"]["mod256_hex"] = row_mod256.astype(int).tobytes().hex()

    print(f"Row sums mod 256 (printable): {row_ascii_printable}")

    readable_row = find_readable_segments(row_ascii_printable, 4)
    if readable_row:
        results["interesting_findings"].append({
            "type": "row_sums_mod256",
            "segments": readable_row
        })
        print(f"  Readable segments: {readable_row}")

    # =====================
    # 2. COLUMN SUMS ANALYSIS
    # =====================
    print("\n=== COLUMN SUMS ANALYSIS ===")

    col_sums = np.sum(matrix, axis=0)
    results["column_sums"]["raw"] = [int(s) for s in col_sums]

    # Mod 256 -> ASCII
    col_mod256 = col_sums % 256
    col_ascii = bytes_to_ascii(col_mod256)
    col_ascii_printable = bytes_to_ascii(col_mod256, filter_printable=True)
    results["column_sums"]["mod256"] = [int(m) for m in col_mod256]
    results["column_sums"]["mod256_ascii"] = col_ascii_printable
    results["column_sums"]["mod256_hex"] = col_mod256.astype(int).tobytes().hex()

    print(f"Column sums mod 256 (printable): {col_ascii_printable}")

    readable_col = find_readable_segments(col_ascii_printable, 4)
    if readable_col:
        results["interesting_findings"].append({
            "type": "column_sums_mod256",
            "segments": readable_col
        })
        print(f"  Readable segments: {readable_col}")

    # =====================
    # 3. PARTIAL SUMS
    # =====================
    print("\n=== PARTIAL SUMS ANALYSIS ===")

    # Sum only positive values in each row
    positive_row_sums = np.sum(np.maximum(matrix, 0), axis=1)
    pos_mod256 = positive_row_sums % 256
    pos_ascii = bytes_to_ascii(pos_mod256, filter_printable=True)
    results["partial_sums"]["positive_row_sums_mod256"] = [int(p) for p in pos_mod256]
    results["partial_sums"]["positive_row_sums_ascii"] = pos_ascii
    print(f"Positive row sums mod 256: {pos_ascii}")

    readable_pos = find_readable_segments(pos_ascii, 4)
    if readable_pos:
        results["interesting_findings"].append({
            "type": "positive_row_sums",
            "segments": readable_pos
        })

    # Sum only negative values in each row
    negative_row_sums = np.sum(np.minimum(matrix, 0), axis=1)
    neg_mod256 = np.abs(negative_row_sums) % 256
    neg_ascii = bytes_to_ascii(neg_mod256, filter_printable=True)
    results["partial_sums"]["negative_row_sums_mod256"] = [int(n) for n in neg_mod256]
    results["partial_sums"]["negative_row_sums_ascii"] = neg_ascii
    print(f"Negative row sums mod 256: {neg_ascii}")

    readable_neg = find_readable_segments(neg_ascii, 4)
    if readable_neg:
        results["interesting_findings"].append({
            "type": "negative_row_sums",
            "segments": readable_neg
        })

    # Sum alternating values (even indices)
    even_col_sums = np.sum(matrix[:, 0::2], axis=1)
    even_mod256 = even_col_sums % 256
    even_ascii = bytes_to_ascii(even_mod256, filter_printable=True)
    results["partial_sums"]["even_col_sums_mod256"] = [int(e) for e in even_mod256]
    results["partial_sums"]["even_col_sums_ascii"] = even_ascii
    print(f"Even column sums mod 256: {even_ascii}")

    # Sum alternating values (odd indices)
    odd_col_sums = np.sum(matrix[:, 1::2], axis=1)
    odd_mod256 = odd_col_sums % 256
    odd_ascii = bytes_to_ascii(odd_mod256, filter_printable=True)
    results["partial_sums"]["odd_col_sums_mod256"] = [int(o) for o in odd_mod256]
    results["partial_sums"]["odd_col_sums_ascii"] = odd_ascii
    print(f"Odd column sums mod 256: {odd_ascii}")

    # =====================
    # 4. XOR REDUCTION
    # =====================
    print("\n=== XOR REDUCTION ANALYSIS ===")

    # XOR all values in each row
    row_xor = []
    for row in matrix:
        xor_result = 0
        for val in row:
            xor_result ^= int(val) & 0xFF
        row_xor.append(xor_result)
    row_xor = np.array(row_xor)
    row_xor_ascii = bytes_to_ascii(row_xor, filter_printable=True)
    results["xor_reduction"]["row_xor"] = [int(x) for x in row_xor]
    results["xor_reduction"]["row_xor_ascii"] = row_xor_ascii
    print(f"Row XOR reduction: {row_xor_ascii}")

    readable_xor_row = find_readable_segments(row_xor_ascii, 4)
    if readable_xor_row:
        results["interesting_findings"].append({
            "type": "row_xor",
            "segments": readable_xor_row
        })

    # XOR all values in each column
    col_xor = []
    for col_idx in range(num_cols):
        xor_result = 0
        for row_idx in range(num_rows):
            xor_result ^= int(matrix[row_idx, col_idx]) & 0xFF
        col_xor.append(xor_result)
    col_xor = np.array(col_xor)
    col_xor_ascii = bytes_to_ascii(col_xor, filter_printable=True)
    results["xor_reduction"]["col_xor"] = [int(x) for x in col_xor]
    results["xor_reduction"]["col_xor_ascii"] = col_xor_ascii
    print(f"Column XOR reduction: {col_xor_ascii}")

    readable_xor_col = find_readable_segments(col_xor_ascii, 4)
    if readable_xor_col:
        results["interesting_findings"].append({
            "type": "col_xor",
            "segments": readable_xor_col
        })

    # =====================
    # 5. MODULO OPERATIONS
    # =====================
    print("\n=== MODULO OPERATIONS ===")

    # Row sum mod 127
    row_mod127 = row_sums % 127
    row_mod127_ascii = bytes_to_ascii(row_mod127, filter_printable=True)
    results["modulo_operations"]["row_mod127"] = [int(m) for m in row_mod127]
    results["modulo_operations"]["row_mod127_ascii"] = row_mod127_ascii
    print(f"Row sums mod 127: {row_mod127_ascii}")

    readable_mod127 = find_readable_segments(row_mod127_ascii, 4)
    if readable_mod127:
        results["interesting_findings"].append({
            "type": "row_mod127",
            "segments": readable_mod127
        })

    # Row sum mod 27 (alphabet + space)
    row_mod27 = row_sums % 27
    # Map: 0=space, 1-26=A-Z
    row_mod27_text = ""
    for m in row_mod27:
        m_int = int(m)
        if m_int == 0:
            row_mod27_text += " "
        elif 1 <= m_int <= 26:
            row_mod27_text += chr(ord('A') + m_int - 1)
        else:
            row_mod27_text += "?"
    results["modulo_operations"]["row_mod27"] = [int(m) for m in row_mod27]
    results["modulo_operations"]["row_mod27_text"] = row_mod27_text
    print(f"Row sums mod 27 (alphabet): {row_mod27_text}")

    readable_mod27 = find_readable_segments(row_mod27_text.replace(" ", "_"), 4)
    if readable_mod27:
        results["interesting_findings"].append({
            "type": "row_mod27",
            "segments": readable_mod27
        })

    # Row sum mod 13
    row_mod13 = row_sums % 13
    results["modulo_operations"]["row_mod13"] = [int(m) for m in row_mod13]
    # Map to hex: 0-12 -> 0-9, A-C
    row_mod13_hex = "".join([hex(int(m))[2:].upper() for m in row_mod13])
    results["modulo_operations"]["row_mod13_hex"] = row_mod13_hex
    print(f"Row sums mod 13 (hex-like): {row_mod13_hex}")

    # Column sums with same modulos
    col_mod127 = col_sums % 127
    col_mod127_ascii = bytes_to_ascii(col_mod127, filter_printable=True)
    results["modulo_operations"]["col_mod127"] = [int(m) for m in col_mod127]
    results["modulo_operations"]["col_mod127_ascii"] = col_mod127_ascii
    print(f"Column sums mod 127: {col_mod127_ascii}")

    col_mod27 = col_sums % 27
    col_mod27_text = ""
    for m in col_mod27:
        m_int = int(m)
        if m_int == 0:
            col_mod27_text += " "
        elif 1 <= m_int <= 26:
            col_mod27_text += chr(ord('A') + m_int - 1)
        else:
            col_mod27_text += "?"
    results["modulo_operations"]["col_mod27"] = [int(m) for m in col_mod27]
    results["modulo_operations"]["col_mod27_text"] = col_mod27_text
    print(f"Column sums mod 27 (alphabet): {col_mod27_text}")

    # =====================
    # 6. CUMULATIVE PATTERNS
    # =====================
    print("\n=== CUMULATIVE PATTERNS ===")

    # Running sum across rows
    running_row_sum = np.cumsum(row_sums)
    running_mod256 = running_row_sum % 256
    running_ascii = bytes_to_ascii(running_mod256, filter_printable=True)
    results["cumulative_patterns"]["running_row_sum_mod256"] = [int(r) for r in running_mod256]
    results["cumulative_patterns"]["running_row_sum_ascii"] = running_ascii
    print(f"Running row sum mod 256: {running_ascii}")

    # Running XOR across rows
    running_xor = []
    xor_acc = 0
    for s in row_sums:
        xor_acc ^= int(s) & 0xFF
        running_xor.append(xor_acc)
    running_xor = np.array(running_xor)
    running_xor_ascii = bytes_to_ascii(running_xor, filter_printable=True)
    results["cumulative_patterns"]["running_row_xor"] = [int(r) for r in running_xor]
    results["cumulative_patterns"]["running_row_xor_ascii"] = running_xor_ascii
    print(f"Running row XOR: {running_xor_ascii}")

    # Running sum across columns
    running_col_sum = np.cumsum(col_sums)
    running_col_mod256 = running_col_sum % 256
    running_col_ascii = bytes_to_ascii(running_col_mod256, filter_printable=True)
    results["cumulative_patterns"]["running_col_sum_mod256"] = [int(r) for r in running_col_mod256]
    results["cumulative_patterns"]["running_col_sum_ascii"] = running_col_ascii
    print(f"Running column sum mod 256: {running_col_ascii}")

    # =====================
    # ADDITIONAL ANALYSES
    # =====================
    print("\n=== ADDITIONAL ANALYSES ===")

    # Diagonal sums
    main_diag_sum = np.trace(matrix)
    anti_diag_sum = np.trace(np.fliplr(matrix))
    results["diagonal_sums"] = {
        "main_diagonal": int(main_diag_sum),
        "anti_diagonal": int(anti_diag_sum),
        "main_mod256": int(main_diag_sum % 256),
        "anti_mod256": int(anti_diag_sum % 256),
        "main_char": chr(int(main_diag_sum % 256)) if 32 <= main_diag_sum % 256 <= 126 else ".",
        "anti_char": chr(int(anti_diag_sum % 256)) if 32 <= anti_diag_sum % 256 <= 126 else "."
    }
    print(f"Main diagonal sum: {main_diag_sum} (mod 256: {main_diag_sum % 256})")
    print(f"Anti-diagonal sum: {anti_diag_sum} (mod 256: {anti_diag_sum % 256})")

    # Row/Column index weighted sums
    weighted_row_sums = []
    for i, row in enumerate(matrix):
        weighted_sum = sum(int(v) * (j + 1) for j, v in enumerate(row))
        weighted_row_sums.append(weighted_sum)
    weighted_mod256 = [w % 256 for w in weighted_row_sums]
    weighted_ascii = bytes_to_ascii(weighted_mod256, filter_printable=True)
    results["weighted_sums"] = {
        "position_weighted_row_sums": weighted_row_sums[:20],  # First 20
        "position_weighted_mod256_ascii": weighted_ascii
    }
    print(f"Position-weighted row sums mod 256: {weighted_ascii}")

    # Absolute value sums
    abs_row_sums = np.sum(np.abs(matrix), axis=1)
    abs_mod256 = abs_row_sums % 256
    abs_ascii = bytes_to_ascii(abs_mod256, filter_printable=True)
    results["absolute_sums"] = {
        "row_abs_sums_mod256": [int(a) for a in abs_mod256],
        "row_abs_sums_ascii": abs_ascii
    }
    print(f"Absolute row sums mod 256: {abs_ascii}")

    # Check for specific patterns
    print("\n=== PATTERN SEARCH ===")

    # Look for "ANNA", "CFB", "SATOSHI", "QUBIC" in any output
    patterns_to_find = ["ANNA", "CFB", "SATOSHI", "QUBIC", "BRIDGE", "BITCOIN", "BTC", "KEY"]
    found_patterns = []

    all_outputs = [
        ("row_mod256", row_ascii_printable.upper()),
        ("col_mod256", col_ascii_printable.upper()),
        ("row_mod27", row_mod27_text),
        ("col_mod27", col_mod27_text),
        ("row_xor", row_xor_ascii.upper()),
        ("col_xor", col_xor_ascii.upper()),
        ("row_mod127", row_mod127_ascii.upper()),
        ("col_mod127", col_mod127_ascii.upper()),
    ]

    for pattern in patterns_to_find:
        for output_name, output_text in all_outputs:
            if pattern in output_text:
                found_patterns.append({
                    "pattern": pattern,
                    "found_in": output_name,
                    "position": output_text.find(pattern)
                })
                print(f"  Found '{pattern}' in {output_name} at position {output_text.find(pattern)}")

    results["pattern_search"] = found_patterns

    # =====================
    # 7. ADVANCED PATTERNS
    # =====================
    print("\n=== ADVANCED PATTERNS ===")

    # Difference between adjacent row sums
    row_diffs = np.diff(row_sums)
    row_diffs_mod256 = row_diffs % 256
    row_diffs_ascii = bytes_to_ascii(row_diffs_mod256, filter_printable=True)
    results["advanced_patterns"] = {
        "row_diff_mod256": [int(d) for d in row_diffs_mod256],
        "row_diff_ascii": row_diffs_ascii
    }
    print(f"Row sum differences mod 256: {row_diffs_ascii}")

    # Sum of first half vs second half of each row
    half_diff = []
    for row in matrix:
        first_half = np.sum(row[:64])
        second_half = np.sum(row[64:])
        half_diff.append(int(first_half - second_half))
    half_diff_mod256 = [h % 256 for h in half_diff]
    half_diff_ascii = bytes_to_ascii(half_diff_mod256, filter_printable=True)
    results["advanced_patterns"]["half_diff_mod256"] = half_diff_mod256
    results["advanced_patterns"]["half_diff_ascii"] = half_diff_ascii
    print(f"Half difference mod 256: {half_diff_ascii}")

    # Product of signs in each row
    sign_product = []
    for row in matrix:
        pos_count = np.sum(row > 0)
        neg_count = np.sum(row < 0)
        sign_product.append((pos_count - neg_count) % 256)
    sign_ascii = bytes_to_ascii(sign_product, filter_printable=True)
    results["advanced_patterns"]["sign_balance_ascii"] = sign_ascii
    print(f"Sign balance (pos-neg) mod 256: {sign_ascii}")

    # Row sum XOR with row index
    row_xor_idx = [(int(s) ^ i) % 256 for i, s in enumerate(row_sums)]
    row_xor_idx_ascii = bytes_to_ascii(row_xor_idx, filter_printable=True)
    results["advanced_patterns"]["row_sum_xor_index"] = row_xor_idx
    results["advanced_patterns"]["row_sum_xor_index_ascii"] = row_xor_idx_ascii
    print(f"Row sum XOR index mod 256: {row_xor_idx_ascii}")

    # Every Nth row sum
    for n in [2, 3, 4, 8]:
        nth_sums = row_sums[::n]
        nth_mod256 = nth_sums % 256
        nth_ascii = bytes_to_ascii(nth_mod256, filter_printable=True)
        results["advanced_patterns"][f"every_{n}th_row_mod256"] = [int(m) for m in nth_mod256]
        results["advanced_patterns"][f"every_{n}th_row_ascii"] = nth_ascii
        print(f"Every {n}th row sum mod 256: {nth_ascii}")

    # Absolute row sum difference from mean
    mean_row_sum = np.mean(row_sums)
    dev_from_mean = [abs(int(s) - mean_row_sum) % 256 for s in row_sums]
    dev_ascii = bytes_to_ascii(dev_from_mean, filter_printable=True)
    results["advanced_patterns"]["deviation_from_mean_ascii"] = dev_ascii
    print(f"Deviation from mean mod 256: {dev_ascii}")

    # Bit patterns - count of set bits in each row sum
    bit_counts = [bin(abs(int(s))).count('1') for s in row_sums]
    bit_count_ascii = bytes_to_ascii(bit_counts, filter_printable=True)
    results["advanced_patterns"]["bit_counts"] = bit_counts
    results["advanced_patterns"]["bit_counts_ascii"] = bit_count_ascii
    print(f"Bit counts: {bit_counts[:32]}...")

    # Quadrant sums
    q1 = np.sum(matrix[:64, :64])
    q2 = np.sum(matrix[:64, 64:])
    q3 = np.sum(matrix[64:, :64])
    q4 = np.sum(matrix[64:, 64:])
    results["advanced_patterns"]["quadrant_sums"] = {
        "q1": int(q1), "q2": int(q2), "q3": int(q3), "q4": int(q4),
        "q1_mod256": int(q1 % 256), "q2_mod256": int(q2 % 256),
        "q3_mod256": int(q3 % 256), "q4_mod256": int(q4 % 256),
        "q1_char": chr(int(q1 % 256)) if 32 <= q1 % 256 <= 126 else ".",
        "q2_char": chr(int(q2 % 256)) if 32 <= q2 % 256 <= 126 else ".",
        "q3_char": chr(int(q3 % 256)) if 32 <= q3 % 256 <= 126 else ".",
        "q4_char": chr(int(q4 % 256)) if 32 <= q4 % 256 <= 126 else "."
    }
    print(f"Quadrant sums: Q1={q1}, Q2={q2}, Q3={q3}, Q4={q4}")
    print(f"Quadrant chars: {results['advanced_patterns']['quadrant_sums']['q1_char']}{results['advanced_patterns']['quadrant_sums']['q2_char']}{results['advanced_patterns']['quadrant_sums']['q3_char']}{results['advanced_patterns']['quadrant_sums']['q4_char']}")

    # =====================
    # 8. BLOCK PATTERNS (8x8, 16x16)
    # =====================
    print("\n=== BLOCK PATTERNS ===")

    # 8x8 block sums (16 blocks)
    block8_sums = []
    for i in range(0, 128, 8):
        for j in range(0, 128, 8):
            block_sum = np.sum(matrix[i:i+8, j:j+8])
            block8_sums.append(int(block_sum))
    block8_mod256 = [b % 256 for b in block8_sums]
    block8_ascii = bytes_to_ascii(block8_mod256, filter_printable=True)
    results["block_patterns"] = {
        "block8_sums": block8_sums,
        "block8_mod256": block8_mod256,
        "block8_ascii": block8_ascii
    }
    print(f"8x8 block sums mod 256: {block8_ascii}")

    # 16x16 block sums (64 blocks)
    block16_sums = []
    for i in range(0, 128, 16):
        for j in range(0, 128, 16):
            block_sum = np.sum(matrix[i:i+16, j:j+16])
            block16_sums.append(int(block_sum))
    block16_mod256 = [b % 256 for b in block16_sums]
    block16_ascii = bytes_to_ascii(block16_mod256, filter_printable=True)
    results["block_patterns"]["block16_sums"] = block16_sums
    results["block_patterns"]["block16_mod256"] = block16_mod256
    results["block_patterns"]["block16_ascii"] = block16_ascii
    print(f"16x16 block sums mod 256: {block16_ascii}")

    # =====================
    # 9. CAESAR CIPHER DECODES
    # =====================
    print("\n=== CAESAR CIPHER ATTEMPTS ===")

    results["caesar_attempts"] = {}
    # Try different Caesar shifts on the mod 27 text
    base_text = row_mod27_text
    for shift in range(1, 27):
        shifted = ""
        for c in base_text:
            if c == ' ':
                shifted += ' '
            elif 'A' <= c <= 'Z':
                shifted += chr((ord(c) - ord('A') + shift) % 26 + ord('A'))
            else:
                shifted += c
        results["caesar_attempts"][f"shift_{shift}"] = shifted
        # Check for interesting words
        if any(word in shifted for word in ["ANNA", "CFB", "BITCOIN", "QUBIC", "SATOSHI", "BRIDGE", "KEY"]):
            print(f"Shift {shift}: {shifted}")

    # =====================
    # 10. REVERSE AND MIRROR PATTERNS
    # =====================
    print("\n=== REVERSE AND MIRROR PATTERNS ===")

    # Reverse row sums
    rev_row_sums = row_sums[::-1]
    rev_mod256 = rev_row_sums % 256
    rev_ascii = bytes_to_ascii(rev_mod256, filter_printable=True)
    results["reverse_patterns"] = {
        "reversed_row_sums_ascii": rev_ascii
    }
    print(f"Reversed row sums mod 256: {rev_ascii}")

    # XOR row sums with reversed row sums
    xor_with_rev = [(int(a) ^ int(b)) % 256 for a, b in zip(row_sums, rev_row_sums)]
    xor_rev_ascii = bytes_to_ascii(xor_with_rev, filter_printable=True)
    results["reverse_patterns"]["xor_with_reversed_ascii"] = xor_rev_ascii
    print(f"XOR with reversed mod 256: {xor_rev_ascii}")

    # =====================
    # SUMMARY
    # =====================
    print("\n" + "="*60)
    print("SUMMARY OF INTERESTING FINDINGS")
    print("="*60)

    if results["interesting_findings"]:
        for finding in results["interesting_findings"]:
            print(f"\nType: {finding['type']}")
            for seg in finding['segments']:
                print(f"  '{seg['text']}' at positions {seg['start']}-{seg['end']}")
    else:
        print("No significant readable segments found.")

    if found_patterns:
        print("\nKnown patterns found:")
        for p in found_patterns:
            print(f"  {p['pattern']} in {p['found_in']}")

    return results


def main():
    print("="*60)
    print("ANNA MATRIX SUM ANALYSIS")
    print("="*60)

    try:
        matrix = load_matrix()
        print(f"\nMatrix loaded successfully!")
        print(f"Shape: {matrix.shape}")
        print(f"Data type: {matrix.dtype}")
        print(f"Sample values (first row): {matrix[0][:10]}...")

        results = analyze_matrix(matrix)

        # Save results
        with open(OUTPUT_PATH, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n\nResults saved to: {OUTPUT_PATH}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
