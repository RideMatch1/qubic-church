#!/usr/bin/env python3
"""
Anna Matrix Binary Pattern Decoder V2
Enhanced analysis with more encoding methods and pattern searches
"""

import json
import os
import string
from typing import List, Dict, Any, Tuple
from collections import Counter
import hashlib

def load_matrix(filepath: str) -> Tuple[List[List[int]], List[Tuple[int, int, str]]]:
    """Load the Anna Matrix from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    raw_matrix = data['matrix']
    string_cells = []
    clean_matrix = []

    for i, row in enumerate(raw_matrix):
        clean_row = []
        for j, cell in enumerate(row):
            if isinstance(cell, str):
                string_cells.append((i, j, cell))
                if cell.isdigit() and all(c in '01' for c in cell):
                    clean_row.append(int(cell, 2))
                else:
                    clean_row.append(0)
            else:
                clean_row.append(int(cell))
        clean_matrix.append(clean_row)

    return clean_matrix, string_cells

def bits_to_bytes(bits: List[int]) -> bytes:
    """Convert list of bits to bytes."""
    result = []
    for i in range(0, len(bits) - 7, 8):
        byte_val = 0
        for j in range(8):
            byte_val = (byte_val << 1) | bits[i + j]
        result.append(byte_val)
    return bytes(result)

def bits_to_bytes_lsb(bits: List[int]) -> bytes:
    """Convert list of bits to bytes (LSB first)."""
    result = []
    for i in range(0, len(bits) - 7, 8):
        byte_val = 0
        for j in range(8):
            byte_val |= bits[i + j] << j
        result.append(byte_val)
    return bytes(result)

def is_printable_ascii(b: int) -> bool:
    return 32 <= b < 127

def bytes_to_ascii(data: bytes) -> str:
    return ''.join(chr(b) if is_printable_ascii(b) else '.' for b in data)

def extract_readable_sequences(text: str, min_length: int = 4) -> List[str]:
    sequences = []
    current = ""
    for char in text:
        if char != '.':
            current += char
        else:
            if len(current) >= min_length:
                sequences.append(current)
            current = ""
    if len(current) >= min_length:
        sequences.append(current)
    return sequences

def flatten_row_major(matrix: List[List[int]]) -> List[int]:
    return [val for row in matrix for val in row]

def flatten_column_major(matrix: List[List[int]]) -> List[int]:
    if not matrix:
        return []
    rows = len(matrix)
    cols = len(matrix[0])
    result = []
    for col in range(cols):
        for row in range(rows):
            if col < len(matrix[row]):
                result.append(matrix[row][col])
    return result

# ============================================================================
# ADVANCED ENCODING METHODS
# ============================================================================

def extract_bit_plane(matrix: List[List[int]], bit_pos: int) -> List[List[int]]:
    """Extract a specific bit plane from the matrix."""
    result = []
    for row in matrix:
        result.append([(abs(v) >> bit_pos) & 1 for v in row])
    return result

def sign_magnitude_split(values: List[int]) -> Tuple[List[int], List[int]]:
    """Split values into sign bits and magnitude."""
    signs = [0 if v >= 0 else 1 for v in values]
    magnitudes = [abs(v) for v in values]
    return signs, magnitudes

def nibble_encoding(values: List[int]) -> Tuple[List[int], List[int]]:
    """Split each byte value into high and low nibbles."""
    high_nibbles = [(abs(v) >> 4) & 0xF for v in values]
    low_nibbles = [abs(v) & 0xF for v in values]
    return high_nibbles, low_nibbles

def delta_encoding(values: List[int]) -> List[int]:
    """Return differences between consecutive values."""
    return [values[i+1] - values[i] for i in range(len(values) - 1)]

def run_length_encoding(bits: List[int]) -> List[Tuple[int, int]]:
    """Run-length encode a bit sequence."""
    if not bits:
        return []
    runs = []
    current_bit = bits[0]
    count = 1
    for bit in bits[1:]:
        if bit == current_bit:
            count += 1
        else:
            runs.append((current_bit, count))
            current_bit = bit
            count = 1
    runs.append((current_bit, count))
    return runs

def interleave_bits(matrix: List[List[int]], n: int = 2) -> List[List[int]]:
    """Interleave every n-th bit."""
    flat = flatten_row_major(matrix)
    bits = []
    for v in flat:
        for i in range(8):
            bits.append((abs(v) >> (7 - i)) & 1)

    interleaved = [[] for _ in range(n)]
    for i, bit in enumerate(bits):
        interleaved[i % n].append(bit)

    return interleaved

def block_xor(matrix: List[List[int]], block_size: int = 8) -> List[List[int]]:
    """XOR blocks of values together."""
    result = []
    for row in matrix:
        new_row = []
        for i in range(0, len(row), block_size):
            block = row[i:i+block_size]
            xor_val = 0
            for v in block:
                xor_val ^= abs(v)
            new_row.append(xor_val)
        result.append(new_row)
    return result

def analyze_utf8_patterns(data: bytes) -> List[Dict[str, Any]]:
    """Look for UTF-8 encoded strings."""
    findings = []
    try:
        text = data.decode('utf-8', errors='replace')
        sequences = extract_readable_sequences(text, 3)
        if sequences:
            findings.append({
                "encoding": "utf-8",
                "sequences": sequences[:10]
            })
    except:
        pass
    return findings

def search_hidden_words(data: bytes) -> List[Dict[str, Any]]:
    """Search for specific words that might be hidden."""
    words = [
        b"bitcoin", b"satoshi", b"nakamoto", b"genesis", b"block",
        b"qubic", b"cfb", b"iota", b"anna", b"matrix", b"bridge",
        b"key", b"secret", b"password", b"hash", b"chain",
        b"21e8", b"come", b"forth", b"sergey", b"ivancheglo",
        b"hello", b"world", b"the", b"begin", b"end", b"start",
        b"message", b"hidden", b"treasure", b"find", b"truth",
        b"btc", b"eth", b"nxt", b"proof", b"work", b"stake"
    ]
    found = []
    data_lower = data.lower()
    for word in words:
        idx = 0
        while True:
            idx = data_lower.find(word, idx)
            if idx == -1:
                break
            context_start = max(0, idx - 10)
            context_end = min(len(data), idx + len(word) + 10)
            found.append({
                "word": word.decode('ascii'),
                "position": idx,
                "context_hex": data[context_start:context_end].hex(),
                "context_ascii": bytes_to_ascii(data[context_start:context_end])
            })
            idx += 1
    return found

def analyze_bit_alignments(bits: List[int]) -> Dict[str, Any]:
    """Try different bit alignments for byte extraction."""
    results = {}
    for offset in range(8):
        shifted_bits = bits[offset:]
        data_msb = bits_to_bytes(shifted_bits)
        data_lsb = bits_to_bytes_lsb(shifted_bits)

        ascii_msb = bytes_to_ascii(data_msb)
        ascii_lsb = bytes_to_ascii(data_lsb)

        seq_msb = extract_readable_sequences(ascii_msb, 4)
        seq_lsb = extract_readable_sequences(ascii_lsb, 4)

        if seq_msb or seq_lsb:
            results[f"offset_{offset}"] = {
                "msb_sequences": seq_msb[:10],
                "lsb_sequences": seq_lsb[:10],
                "msb_preview": ascii_msb[:100],
                "lsb_preview": ascii_lsb[:100]
            }
    return results

def analyze_specific_rows(matrix: List[List[int]], rows: List[int]) -> Dict[str, Any]:
    """Analyze specific rows for patterns."""
    results = {}
    for row_idx in rows:
        if row_idx < len(matrix):
            row = matrix[row_idx]
            # Sign bits
            sign_bits = [0 if v >= 0 else 1 for v in row]
            sign_data = bits_to_bytes(sign_bits)

            # Parity
            parity_bits = [abs(v) % 2 for v in row]
            parity_data = bits_to_bytes(parity_bits)

            # Direct ASCII (values as chars)
            direct_ascii = ''.join(chr(v & 0x7F) if is_printable_ascii(v & 0x7F) else '.' for v in row)

            # Values mod 256 as bytes
            mod_bytes = bytes([v % 256 for v in row])
            mod_ascii = bytes_to_ascii(mod_bytes)

            results[f"row_{row_idx}"] = {
                "sign_ascii": bytes_to_ascii(sign_data),
                "parity_ascii": bytes_to_ascii(parity_data),
                "direct_ascii": direct_ascii,
                "mod256_ascii": mod_ascii,
                "raw_values": row[:32]
            }
    return results

def analyze_fibonacci_positions(values: List[int]) -> Dict[str, Any]:
    """Extract values at Fibonacci positions."""
    fib = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946]
    fib_values = []
    for pos in fib:
        if pos < len(values):
            fib_values.append(values[pos])

    # Try as ASCII
    ascii_direct = ''.join(chr(v & 0x7F) if is_printable_ascii(v & 0x7F) else '.' for v in fib_values)

    return {
        "fibonacci_positions": fib[:len(fib_values)],
        "values": fib_values,
        "ascii_interpretation": ascii_direct
    }

def analyze_prime_positions(values: List[int]) -> Dict[str, Any]:
    """Extract values at prime positions."""
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173]
    prime_values = []
    for pos in primes:
        if pos < len(values):
            prime_values.append(values[pos])

    ascii_direct = ''.join(chr(v & 0x7F) if is_printable_ascii(v & 0x7F) else '.' for v in prime_values)

    return {
        "prime_positions": primes[:len(prime_values)],
        "values": prime_values,
        "ascii_interpretation": ascii_direct
    }

def analyze_diagonal_patterns(matrix: List[List[int]]) -> Dict[str, Any]:
    """Analyze all diagonals for patterns."""
    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    results = {}

    # Main diagonals (top-left to bottom-right)
    main_diags = []
    for start in range(-(rows-1), cols):
        diag = []
        for i in range(max(rows, cols)):
            r, c = i, start + i
            if 0 <= r < rows and 0 <= c < cols:
                diag.append(matrix[r][c])
        if len(diag) >= 8:
            main_diags.append(diag)

    # Anti-diagonals (top-right to bottom-left)
    anti_diags = []
    for start in range(rows + cols - 1):
        diag = []
        for i in range(max(rows, cols)):
            r, c = i, start - i
            if 0 <= r < rows and 0 <= c < cols:
                diag.append(matrix[r][c])
        if len(diag) >= 8:
            anti_diags.append(diag)

    # Analyze longest diagonals
    results["main_diagonal_count"] = len(main_diags)
    results["anti_diagonal_count"] = len(anti_diags)

    # Process main diagonals
    main_findings = []
    for i, diag in enumerate(sorted(main_diags, key=len, reverse=True)[:10]):
        sign_bits = [0 if v >= 0 else 1 for v in diag]
        data = bits_to_bytes(sign_bits)
        ascii_text = bytes_to_ascii(data)
        sequences = extract_readable_sequences(ascii_text, 3)
        if sequences:
            main_findings.append({
                "diagonal_index": i,
                "length": len(diag),
                "sequences": sequences[:5],
                "ascii_preview": ascii_text[:50]
            })
    results["main_diagonal_findings"] = main_findings

    # Process anti-diagonals
    anti_findings = []
    for i, diag in enumerate(sorted(anti_diags, key=len, reverse=True)[:10]):
        sign_bits = [0 if v >= 0 else 1 for v in diag]
        data = bits_to_bytes(sign_bits)
        ascii_text = bytes_to_ascii(data)
        sequences = extract_readable_sequences(ascii_text, 3)
        if sequences:
            anti_findings.append({
                "diagonal_index": i,
                "length": len(diag),
                "sequences": sequences[:5],
                "ascii_preview": ascii_text[:50]
            })
    results["anti_diagonal_findings"] = anti_findings

    return results

def analyze_block_patterns(matrix: List[List[int]], block_size: int = 8) -> Dict[str, Any]:
    """Analyze matrix in blocks."""
    results = {"block_size": block_size, "blocks": []}

    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0

    for br in range(0, rows, block_size):
        for bc in range(0, cols, block_size):
            block_values = []
            for r in range(br, min(br + block_size, rows)):
                for c in range(bc, min(bc + block_size, cols)):
                    block_values.append(matrix[r][c])

            # Sign bits
            sign_bits = [0 if v >= 0 else 1 for v in block_values]
            if len(sign_bits) >= 8:
                data = bits_to_bytes(sign_bits)
                ascii_text = bytes_to_ascii(data)
                sequences = extract_readable_sequences(ascii_text, 3)
                if sequences:
                    results["blocks"].append({
                        "block_row": br // block_size,
                        "block_col": bc // block_size,
                        "sequences": sequences[:3],
                        "ascii": ascii_text
                    })

    return results

def analyze_spiral_pattern(matrix: List[List[int]]) -> Dict[str, Any]:
    """Read matrix in spiral pattern from outside to inside."""
    if not matrix:
        return {}

    rows = len(matrix)
    cols = len(matrix[0])
    result = []

    top, bottom, left, right = 0, rows - 1, 0, cols - 1

    while top <= bottom and left <= right:
        # Top row
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1

        # Right column
        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right -= 1

        if top <= bottom:
            # Bottom row
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1

        if left <= right:
            # Left column
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1

    # Analyze spiral
    sign_bits = [0 if v >= 0 else 1 for v in result]
    data = bits_to_bytes(sign_bits)
    ascii_text = bytes_to_ascii(data)
    sequences = extract_readable_sequences(ascii_text, 3)

    return {
        "spiral_length": len(result),
        "sequences": sequences[:20],
        "ascii_preview": ascii_text[:200]
    }

def analyze_quadrants(matrix: List[List[int]]) -> Dict[str, Any]:
    """Analyze each quadrant separately."""
    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    mid_row = rows // 2
    mid_col = cols // 2

    quadrants = {
        "top_left": [],
        "top_right": [],
        "bottom_left": [],
        "bottom_right": []
    }

    for r in range(rows):
        for c in range(cols):
            if r < mid_row and c < mid_col:
                quadrants["top_left"].append(matrix[r][c])
            elif r < mid_row and c >= mid_col:
                quadrants["top_right"].append(matrix[r][c])
            elif r >= mid_row and c < mid_col:
                quadrants["bottom_left"].append(matrix[r][c])
            else:
                quadrants["bottom_right"].append(matrix[r][c])

    results = {}
    for name, values in quadrants.items():
        sign_bits = [0 if v >= 0 else 1 for v in values]
        data = bits_to_bytes(sign_bits)
        ascii_text = bytes_to_ascii(data)
        sequences = extract_readable_sequences(ascii_text, 3)

        parity_bits = [abs(v) % 2 for v in values]
        parity_data = bits_to_bytes(parity_bits)
        parity_ascii = bytes_to_ascii(parity_data)
        parity_seq = extract_readable_sequences(parity_ascii, 3)

        results[name] = {
            "sign_sequences": sequences[:10],
            "parity_sequences": parity_seq[:10],
            "sign_ascii_preview": ascii_text[:100],
            "parity_ascii_preview": parity_ascii[:100]
        }

    return results

def analyze_value_mapping(matrix: List[List[int]]) -> Dict[str, Any]:
    """Map values to characters using different schemes."""
    flat = flatten_row_major(matrix)

    results = {}

    # Direct mapping (value % 256 as byte)
    direct = bytes([v % 256 for v in flat])
    results["direct_mod256"] = {
        "preview": bytes_to_ascii(direct[:200]),
        "sequences": extract_readable_sequences(bytes_to_ascii(direct), 4)[:20]
    }

    # Shift to printable range (map -128..127 to 32..159)
    shifted = bytes([(v + 128) % 128 + 32 for v in flat])
    results["shifted_to_printable"] = {
        "preview": bytes_to_ascii(shifted[:200]),
        "sequences": extract_readable_sequences(bytes_to_ascii(shifted), 4)[:20]
    }

    # XOR with 0x55 (common mask)
    xor_55 = bytes([(v ^ 0x55) % 256 for v in flat])
    results["xor_0x55"] = {
        "preview": bytes_to_ascii(xor_55[:200]),
        "sequences": extract_readable_sequences(bytes_to_ascii(xor_55), 4)[:20]
    }

    # XOR with 0xAA
    xor_aa = bytes([(v ^ 0xAA) % 256 for v in flat])
    results["xor_0xAA"] = {
        "preview": bytes_to_ascii(xor_aa[:200]),
        "sequences": extract_readable_sequences(bytes_to_ascii(xor_aa), 4)[:20]
    }

    return results

def main():
    matrix_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json"
    matrix, string_cells = load_matrix(matrix_path)

    print(f"Matrix loaded: {len(matrix)} rows x {len(matrix[0])} columns")
    print(f"String cells found: {len(string_cells)}")

    results = {
        "metadata": {
            "rows": len(matrix),
            "cols": len(matrix[0]) if matrix else 0,
            "total_cells": len(matrix) * (len(matrix[0]) if matrix else 0),
            "string_cells": [{"row": r, "col": c, "value": v} for r, c, v in string_cells]
        },
        "basic_encodings": {},
        "advanced_analysis": {},
        "pattern_findings": {},
        "hidden_words": [],
        "interesting_sequences": []
    }

    flat_row = flatten_row_major(matrix)
    flat_col = flatten_column_major(matrix)

    print("\n=== BASIC ENCODINGS ===")

    # Sign bit encoding
    for name, values in [("row_major", flat_row), ("col_major", flat_col)]:
        sign_bits = [0 if v >= 0 else 1 for v in values]
        data = bits_to_bytes(sign_bits)
        ascii_text = bytes_to_ascii(data)
        sequences = extract_readable_sequences(ascii_text, 3)
        results["basic_encodings"][f"sign_{name}"] = {
            "sequences": sequences[:20],
            "ascii_preview": ascii_text[:200]
        }
        print(f"  Sign bit {name}: {sequences[:5]}")

    # Parity encoding
    for name, values in [("row_major", flat_row), ("col_major", flat_col)]:
        parity_bits = [abs(v) % 2 for v in values]
        data = bits_to_bytes(parity_bits)
        ascii_text = bytes_to_ascii(data)
        sequences = extract_readable_sequences(ascii_text, 3)
        results["basic_encodings"][f"parity_{name}"] = {
            "sequences": sequences[:20],
            "ascii_preview": ascii_text[:200]
        }
        print(f"  Parity {name}: {sequences[:5]}")

    print("\n=== BIT ALIGNMENT ANALYSIS ===")
    sign_bits_row = [0 if v >= 0 else 1 for v in flat_row]
    alignments = analyze_bit_alignments(sign_bits_row)
    results["advanced_analysis"]["bit_alignments"] = alignments
    for offset, data in alignments.items():
        print(f"  {offset}: MSB={data['msb_sequences'][:3]}, LSB={data['lsb_sequences'][:3]}")

    print("\n=== SPECIAL POSITIONS ===")
    fib_analysis = analyze_fibonacci_positions(flat_row)
    prime_analysis = analyze_prime_positions(flat_row)
    results["advanced_analysis"]["fibonacci_positions"] = fib_analysis
    results["advanced_analysis"]["prime_positions"] = prime_analysis
    print(f"  Fibonacci: {fib_analysis['ascii_interpretation']}")
    print(f"  Prime: {prime_analysis['ascii_interpretation']}")

    print("\n=== DIAGONAL PATTERNS ===")
    diag_analysis = analyze_diagonal_patterns(matrix)
    results["pattern_findings"]["diagonals"] = diag_analysis
    print(f"  Main diagonals with findings: {len(diag_analysis.get('main_diagonal_findings', []))}")
    print(f"  Anti diagonals with findings: {len(diag_analysis.get('anti_diagonal_findings', []))}")

    print("\n=== SPIRAL PATTERN ===")
    spiral = analyze_spiral_pattern(matrix)
    results["pattern_findings"]["spiral"] = spiral
    print(f"  Spiral sequences: {spiral['sequences'][:5]}")

    print("\n=== QUADRANT ANALYSIS ===")
    quadrants = analyze_quadrants(matrix)
    results["pattern_findings"]["quadrants"] = quadrants
    for name, data in quadrants.items():
        print(f"  {name}: sign={data['sign_sequences'][:3]}, parity={data['parity_sequences'][:3]}")

    print("\n=== BLOCK PATTERNS (8x8) ===")
    blocks = analyze_block_patterns(matrix, 8)
    results["pattern_findings"]["blocks_8x8"] = blocks
    print(f"  Blocks with sequences: {len(blocks['blocks'])}")

    print("\n=== VALUE MAPPING ===")
    value_map = analyze_value_mapping(matrix)
    results["advanced_analysis"]["value_mapping"] = value_map
    for name, data in value_map.items():
        print(f"  {name}: {data['sequences'][:3]}")

    print("\n=== SPECIFIC ROWS ANALYSIS ===")
    interesting_rows = [0, 1, 2, 3, 7, 13, 21, 27, 42, 64, 100, 127]
    specific_rows = analyze_specific_rows(matrix, interesting_rows)
    results["advanced_analysis"]["specific_rows"] = specific_rows
    for row_name, data in specific_rows.items():
        print(f"  {row_name}: direct_ascii={data['direct_ascii'][:40]}")

    print("\n=== HIDDEN WORD SEARCH ===")
    # Search in all major encodings
    all_data = []
    for encoding in ["sign", "parity"]:
        for order in ["row_major", "col_major"]:
            key = f"{encoding}_{order}"
            if key in results["basic_encodings"]:
                bits = None
                if encoding == "sign":
                    values = flat_row if order == "row_major" else flat_col
                    bits = [0 if v >= 0 else 1 for v in values]
                else:
                    values = flat_row if order == "row_major" else flat_col
                    bits = [abs(v) % 2 for v in values]
                if bits:
                    data = bits_to_bytes(bits)
                    words = search_hidden_words(data)
                    for word in words:
                        word["encoding"] = key
                    results["hidden_words"].extend(words)

    if results["hidden_words"]:
        print(f"  Found {len(results['hidden_words'])} hidden word occurrences!")
        for word in results["hidden_words"][:10]:
            print(f"    '{word['word']}' at pos {word['position']} in {word['encoding']}")
    else:
        print("  No predefined words found")

    print("\n=== COLLECTING ALL INTERESTING SEQUENCES ===")
    all_sequences = []

    for enc_name, enc_data in results["basic_encodings"].items():
        for seq in enc_data.get("sequences", []):
            if len(seq) >= 4:
                all_sequences.append({
                    "sequence": seq,
                    "source": enc_name,
                    "length": len(seq),
                    "category": "basic_encoding"
                })

    for pattern_name, pattern_data in results["pattern_findings"].items():
        if isinstance(pattern_data, dict):
            for key, val in pattern_data.items():
                if isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict) and "sequences" in item:
                            for seq in item["sequences"]:
                                if len(seq) >= 4:
                                    all_sequences.append({
                                        "sequence": seq,
                                        "source": f"{pattern_name}/{key}",
                                        "length": len(seq),
                                        "category": "pattern"
                                    })
                if isinstance(val, dict) and "sequences" in val:
                    for seq in val["sequences"]:
                        if len(seq) >= 4:
                            all_sequences.append({
                                "sequence": seq,
                                "source": f"{pattern_name}/{key}",
                                "length": len(seq),
                                "category": "pattern"
                            })

    # Deduplicate and sort
    seen = set()
    unique_sequences = []
    for item in all_sequences:
        if item["sequence"] not in seen:
            seen.add(item["sequence"])
            unique_sequences.append(item)

    unique_sequences.sort(key=lambda x: x["length"], reverse=True)
    results["interesting_sequences"] = unique_sequences[:100]

    print(f"  Unique sequences (len >= 4): {len(unique_sequences)}")
    print("  Top 15 longest:")
    for item in unique_sequences[:15]:
        print(f"    [{item['source']}] '{item['sequence']}' (len={item['length']})")

    # Deeper analysis of direct ASCII values from all rows
    print("\n=== DIRECT ASCII ROW-BY-ROW ANALYSIS ===")
    all_row_ascii = []
    for i, row in enumerate(matrix):
        # Direct ASCII (values as chars)
        direct_ascii = ''.join(chr(v & 0x7F) if is_printable_ascii(v & 0x7F) else '' for v in row)
        # Extract readable sequences
        sequences = extract_readable_sequences(direct_ascii, 4)
        if sequences:
            all_row_ascii.append({
                "row": i,
                "sequences": sequences,
                "full_text": direct_ascii
            })
            print(f"  Row {i}: {sequences[:3]}")
    results["advanced_analysis"]["direct_ascii_rows"] = all_row_ascii

    # Look for letter-only sequences (potential words)
    print("\n=== LETTER-ONLY SEQUENCES FROM DIRECT ASCII ===")
    letter_sequences = []
    for row_data in all_row_ascii:
        for seq in row_data["sequences"]:
            # Extract only alphabetic characters
            letters_only = ''.join(c for c in seq if c.isalpha())
            if len(letters_only) >= 4:
                letter_sequences.append({
                    "row": row_data["row"],
                    "sequence": letters_only,
                    "original": seq
                })
    letter_sequences.sort(key=lambda x: len(x["sequence"]), reverse=True)
    results["advanced_analysis"]["letter_sequences"] = letter_sequences[:50]
    print(f"  Found {len(letter_sequences)} letter-only sequences")
    for item in letter_sequences[:20]:
        print(f"    Row {item['row']}: '{item['sequence']}' (from '{item['original']}')")

    # Look for patterns that might be words with l33t speak or spacing
    print("\n=== LOOKING FOR WORD-LIKE PATTERNS ===")
    all_text = ''.join(row_data["full_text"] for row_data in all_row_ascii)
    # Common word patterns
    word_patterns = []
    for i in range(len(all_text) - 3):
        substr = all_text[i:i+20]
        letters = ''.join(c.lower() for c in substr if c.isalpha())
        if len(letters) >= 4:
            # Check for common English words
            common_words = ["the", "and", "for", "are", "but", "not", "you", "all",
                          "can", "had", "her", "was", "one", "our", "out", "day",
                          "get", "has", "him", "his", "how", "its", "may", "new",
                          "now", "old", "see", "two", "way", "who", "boy", "did",
                          "come", "from", "have", "here", "into", "just", "know",
                          "like", "made", "make", "more", "must", "over", "said",
                          "some", "than", "them", "then", "they", "this", "time",
                          "very", "want", "well", "were", "what", "when", "will",
                          "with", "word", "work", "your", "bitcoin", "satoshi",
                          "genesis", "block", "hash", "chain", "qubic", "anna",
                          "bridge", "matrix", "key", "secret", "code", "message",
                          "hidden", "truth", "find", "seek"]
            for word in common_words:
                if word in letters:
                    word_patterns.append({
                        "word": word,
                        "context": substr,
                        "position": i
                    })
    # Deduplicate
    seen_words = set()
    unique_word_patterns = []
    for wp in word_patterns:
        key = (wp["word"], wp["position"] // 100)
        if key not in seen_words:
            seen_words.add(key)
            unique_word_patterns.append(wp)
    results["advanced_analysis"]["word_patterns"] = unique_word_patterns[:50]
    if unique_word_patterns:
        print(f"  Found {len(unique_word_patterns)} word-like patterns!")
        for wp in unique_word_patterns[:15]:
            print(f"    '{wp['word']}' in context: '{wp['context']}'")

    # Save results
    output_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/BINARY_MESSAGES.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n=== RESULTS SAVED TO {output_path} ===")

    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Matrix dimensions: {results['metadata']['rows']} x {results['metadata']['cols']}")
    print(f"String cells (special markers): {len(string_cells)}")
    print(f"Unique readable sequences found: {len(unique_sequences)}")
    print(f"Hidden words found: {len(results['hidden_words'])}")

    # Look for potential meaningful sequences
    meaningful = []
    for seq in unique_sequences:
        # seq is a dict with 'sequence' key
        seq_text = seq['sequence'] if isinstance(seq, dict) else seq
        # Check if sequence looks like a word (has vowels and consonants)
        vowels = sum(1 for c in seq_text.lower() if c in 'aeiou')
        consonants = sum(1 for c in seq_text.lower() if c.isalpha() and c not in 'aeiou')
        if len(seq_text) >= 5 and vowels > 0 and consonants > 0:
            meaningful.append(seq)

    if meaningful:
        print("\nPOTENTIALLY MEANINGFUL SEQUENCES:")
        for item in meaningful[:20]:
            if isinstance(item, dict):
                print(f"  '{item['sequence']}'")
            else:
                print(f"  '{item}'")

    return results

if __name__ == "__main__":
    main()
