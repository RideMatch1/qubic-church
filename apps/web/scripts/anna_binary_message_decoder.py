#!/usr/bin/env python3
"""
Anna Matrix Binary Pattern Decoder
Searches for hidden messages in binary patterns of the Anna Matrix
"""

import json
import os
from typing import List, Dict, Any, Tuple

def load_matrix(filepath: str) -> Tuple[List[List[int]], List[Tuple[int, int, str]]]:
    """Load the Anna Matrix from JSON file.
    Returns: (matrix with strings converted to int, list of original string cells)
    """
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
                # Try to interpret string as binary or convert to 0
                if cell.isdigit() and all(c in '01' for c in cell):
                    clean_row.append(int(cell, 2))  # Interpret as binary
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

def bytes_to_ascii(data: bytes, filter_printable: bool = True) -> str:
    """Convert bytes to ASCII string, optionally filtering printable chars."""
    if filter_printable:
        return ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
    return data.decode('ascii', errors='replace')

def extract_readable_sequences(text: str, min_length: int = 4) -> List[str]:
    """Extract sequences of readable characters."""
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
    """Flatten matrix in row-major order."""
    return [val for row in matrix for val in row]

def flatten_column_major(matrix: List[List[int]]) -> List[int]:
    """Flatten matrix in column-major order."""
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
# ENCODING METHODS
# ============================================================================

def sign_bit_encoding(values: List[int]) -> List[int]:
    """Extract sign bits: 1 if positive, 0 if negative."""
    return [1 if v >= 0 else 0 for v in values]

def threshold_encoding(values: List[int], threshold: int) -> List[int]:
    """1 if value > threshold, 0 otherwise."""
    return [1 if v > threshold else 0 for v in values]

def parity_encoding(values: List[int]) -> List[int]:
    """1 if value is odd, 0 if even."""
    return [abs(v) % 2 for v in values]

def high_bit_extraction(values: List[int], bit_position: int) -> List[int]:
    """Extract specific bit from each value."""
    return [(abs(v) >> bit_position) & 1 for v in values]

def comparison_encoding(values: List[int]) -> List[int]:
    """1 if cell[i] > cell[i+1], 0 otherwise."""
    return [1 if values[i] > values[i+1] else 0 for i in range(len(values) - 1)]

def modulo_encoding(values: List[int], mod: int) -> List[int]:
    """Return value mod n for each value."""
    return [abs(v) % mod for v in values]

def trits_to_bits(trits: List[int]) -> List[int]:
    """Convert ternary (base-3) to binary."""
    # Pack trits into groups of 5, convert to byte
    bits = []
    for trit in trits:
        # Simple conversion: 0->00, 1->01, 2->10
        bits.extend([trit >> 1, trit & 1])
    return bits

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_encoding(name: str, bits: List[int], results: Dict[str, Any]) -> None:
    """Analyze a bit sequence for messages."""
    data = bits_to_bytes(bits)
    ascii_text = bytes_to_ascii(data)
    readable = extract_readable_sequences(ascii_text, min_length=3)

    # Calculate statistics
    ones = sum(bits)
    zeros = len(bits) - ones

    results[name] = {
        "total_bits": len(bits),
        "ones": ones,
        "zeros": zeros,
        "ratio": round(ones / len(bits), 4) if bits else 0,
        "bytes_count": len(data),
        "ascii_preview": ascii_text[:200] if len(ascii_text) > 200 else ascii_text,
        "readable_sequences": readable[:20],  # Limit to 20 sequences
        "raw_bytes_hex": data[:50].hex() if len(data) > 50 else data.hex()
    }

def find_repeating_patterns(bits: List[int], pattern_length: int) -> Dict[str, int]:
    """Find repeating bit patterns of specified length."""
    patterns = {}
    for i in range(len(bits) - pattern_length + 1):
        pattern = tuple(bits[i:i + pattern_length])
        pattern_str = ''.join(map(str, pattern))
        patterns[pattern_str] = patterns.get(pattern_str, 0) + 1
    # Return top 10 most common
    return dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10])

def search_known_strings(data: bytes) -> List[Dict[str, Any]]:
    """Search for known strings in the data."""
    known_strings = [
        b"bitcoin", b"satoshi", b"nakamoto", b"qubic", b"cfb",
        b"genesis", b"bridge", b"key", b"secret", b"password",
        b"anna", b"matrix", b"iota", b"hello", b"world",
        b"21e8", b"hash", b"block", b"chain", b"crypto"
    ]
    found = []
    data_lower = data.lower()
    for s in known_strings:
        idx = data_lower.find(s)
        if idx >= 0:
            found.append({
                "string": s.decode('ascii'),
                "position": idx,
                "context": data[max(0, idx-5):idx+len(s)+5].hex()
            })
    return found

def analyze_diagonal(matrix: List[List[int]], direction: str = "main") -> List[int]:
    """Extract values along diagonals."""
    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    values = []

    if direction == "main":
        for i in range(min(rows, cols)):
            values.append(matrix[i][i])
    elif direction == "anti":
        for i in range(min(rows, cols)):
            values.append(matrix[i][cols - 1 - i])

    return values

def analyze_snake_pattern(matrix: List[List[int]]) -> List[int]:
    """Read matrix in snake/zigzag pattern."""
    result = []
    for i, row in enumerate(matrix):
        if i % 2 == 0:
            result.extend(row)
        else:
            result.extend(reversed(row))
    return result

def xor_adjacent_rows(matrix: List[List[int]]) -> List[int]:
    """XOR adjacent rows and extract bits."""
    result = []
    for i in range(len(matrix) - 1):
        for j in range(len(matrix[i])):
            if j < len(matrix[i+1]):
                result.append(matrix[i][j] ^ matrix[i+1][j])
    return result

def analyze_byte_boundaries(values: List[int]) -> Dict[str, Any]:
    """Analyze values at byte boundaries (every 8th position)."""
    byte_boundary_values = values[::8]
    return {
        "count": len(byte_boundary_values),
        "values": byte_boundary_values[:50],
        "ascii": ''.join(chr(v & 0x7F) if 32 <= (v & 0x7F) < 127 else '.' for v in byte_boundary_values[:100])
    }

def main():
    # Load the matrix
    matrix_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json"
    matrix, string_cells = load_matrix(matrix_path)

    print(f"Matrix loaded: {len(matrix)} rows x {len(matrix[0])} columns")
    print(f"String cells found: {len(string_cells)}")
    print(f"Total cells: {len(matrix) * len(matrix[0])}")

    results = {
        "metadata": {
            "rows": len(matrix),
            "cols": len(matrix[0]) if matrix else 0,
            "total_cells": len(matrix) * (len(matrix[0]) if matrix else 0),
            "string_cells": [{"row": r, "col": c, "value": v} for r, c, v in string_cells]
        },
        "encodings": {},
        "special_patterns": {},
        "known_strings_found": [],
        "interesting_findings": []
    }

    # Flatten in different orders
    row_major = flatten_row_major(matrix)
    col_major = flatten_column_major(matrix)
    snake = analyze_snake_pattern(matrix)

    print("\n=== SIGN BIT EXTRACTION ===")
    for name, values in [("row_major", row_major), ("col_major", col_major), ("snake", snake)]:
        bits = sign_bit_encoding(values)
        analyze_encoding(f"sign_bit_{name}", bits, results["encodings"])
        print(f"  {name}: {results['encodings'][f'sign_bit_{name}']['readable_sequences'][:5]}")

    print("\n=== THRESHOLD ENCODING ===")
    for threshold in [0, 50, 100, -50]:
        bits = threshold_encoding(row_major, threshold)
        analyze_encoding(f"threshold_{threshold}_row", bits, results["encodings"])
        bits = threshold_encoding(col_major, threshold)
        analyze_encoding(f"threshold_{threshold}_col", bits, results["encodings"])
        print(f"  threshold {threshold}: {results['encodings'][f'threshold_{threshold}_row']['readable_sequences'][:5]}")

    print("\n=== PARITY ENCODING ===")
    for name, values in [("row_major", row_major), ("col_major", col_major)]:
        bits = parity_encoding(values)
        analyze_encoding(f"parity_{name}", bits, results["encodings"])
        print(f"  parity {name}: {results['encodings'][f'parity_{name}']['readable_sequences'][:5]}")

    print("\n=== HIGH BIT EXTRACTION ===")
    for bit_pos in [7, 6, 5, 4]:
        bits = high_bit_extraction(row_major, bit_pos)
        analyze_encoding(f"bit{bit_pos}_row", bits, results["encodings"])
        bits = high_bit_extraction(col_major, bit_pos)
        analyze_encoding(f"bit{bit_pos}_col", bits, results["encodings"])
        print(f"  bit {bit_pos}: {results['encodings'][f'bit{bit_pos}_row']['readable_sequences'][:5]}")

    print("\n=== VALUE COMPARISON ENCODING ===")
    bits = comparison_encoding(row_major)
    analyze_encoding("comparison_row", bits, results["encodings"])
    bits = comparison_encoding(col_major)
    analyze_encoding("comparison_col", bits, results["encodings"])
    print(f"  comparison row: {results['encodings']['comparison_row']['readable_sequences'][:5]}")
    print(f"  comparison col: {results['encodings']['comparison_col']['readable_sequences'][:5]}")

    print("\n=== MODULO ENCODING ===")
    for mod in [2, 3, 5, 7]:
        bits = modulo_encoding(row_major, mod)
        if mod == 2:
            analyze_encoding(f"mod{mod}_row", bits, results["encodings"])
            print(f"  mod {mod}: {results['encodings'][f'mod{mod}_row']['readable_sequences'][:5]}")
        elif mod == 3:
            # Convert trits to bits
            binary_bits = trits_to_bits(bits)
            analyze_encoding(f"mod{mod}_as_trits_row", binary_bits, results["encodings"])
            print(f"  mod {mod} (trits): {results['encodings'][f'mod{mod}_as_trits_row']['readable_sequences'][:5]}")

    print("\n=== DIAGONAL ANALYSIS ===")
    main_diag = analyze_diagonal(matrix, "main")
    anti_diag = analyze_diagonal(matrix, "anti")

    main_bits = sign_bit_encoding(main_diag)
    analyze_encoding("diagonal_main_sign", main_bits, results["encodings"])
    anti_bits = sign_bit_encoding(anti_diag)
    analyze_encoding("diagonal_anti_sign", anti_bits, results["encodings"])
    print(f"  main diagonal: {results['encodings']['diagonal_main_sign']['readable_sequences'][:5]}")
    print(f"  anti diagonal: {results['encodings']['diagonal_anti_sign']['readable_sequences'][:5]}")

    print("\n=== XOR ADJACENT ROWS ===")
    xor_values = xor_adjacent_rows(matrix)
    xor_bits = sign_bit_encoding(xor_values)
    analyze_encoding("xor_adjacent_sign", xor_bits, results["encodings"])
    xor_parity = parity_encoding(xor_values)
    analyze_encoding("xor_adjacent_parity", xor_parity, results["encodings"])
    print(f"  xor sign: {results['encodings']['xor_adjacent_sign']['readable_sequences'][:5]}")
    print(f"  xor parity: {results['encodings']['xor_adjacent_parity']['readable_sequences'][:5]}")

    print("\n=== BYTE BOUNDARY ANALYSIS ===")
    byte_analysis = analyze_byte_boundaries(row_major)
    results["special_patterns"]["byte_boundaries"] = byte_analysis
    print(f"  ASCII at byte boundaries: {byte_analysis['ascii'][:80]}")

    print("\n=== REPEATING PATTERN SEARCH ===")
    sign_bits = sign_bit_encoding(row_major)
    for pattern_len in [8, 16, 32]:
        patterns = find_repeating_patterns(sign_bits, pattern_len)
        results["special_patterns"][f"repeating_{pattern_len}bit"] = patterns
        print(f"  Most common {pattern_len}-bit patterns: {list(patterns.items())[:3]}")

    print("\n=== KNOWN STRING SEARCH ===")
    # Search in all major encodings
    for enc_name in ["sign_bit_row_major", "parity_row_major", "threshold_0_row"]:
        if enc_name in results["encodings"]:
            hex_data = results["encodings"][enc_name]["raw_bytes_hex"]
            data = bytes.fromhex(hex_data)
            found = search_known_strings(data)
            if found:
                results["known_strings_found"].extend([{**f, "encoding": enc_name} for f in found])
                print(f"  Found in {enc_name}: {found}")

    # Extended search - try direct value interpretation
    print("\n=== DIRECT VALUE INTERPRETATION ===")
    # Maybe values are direct ASCII codes?
    direct_ascii = ''.join(chr(abs(v) % 128) if 32 <= abs(v) % 128 < 127 else '.' for v in row_major[:256])
    direct_sequences = extract_readable_sequences(direct_ascii, 3)
    results["special_patterns"]["direct_ascii_mod128"] = {
        "preview": direct_ascii,
        "sequences": direct_sequences[:20]
    }
    print(f"  Direct ASCII (mod 128): {direct_ascii[:80]}")

    # Values as 7-bit ASCII
    direct_7bit = ''.join(chr(v & 0x7F) if 32 <= (v & 0x7F) < 127 else '.' for v in row_major[:256])
    results["special_patterns"]["direct_7bit_ascii"] = {
        "preview": direct_7bit,
        "sequences": extract_readable_sequences(direct_7bit, 3)[:20]
    }
    print(f"  Direct 7-bit ASCII: {direct_7bit[:80]}")

    # Look for interesting findings
    print("\n=== ANALYZING FOR INTERESTING FINDINGS ===")

    # Count all readable sequences across encodings
    all_sequences = []
    for enc_name, enc_data in results["encodings"].items():
        for seq in enc_data.get("readable_sequences", []):
            if len(seq) >= 4:  # Only sequences of 4+ chars
                all_sequences.append({
                    "sequence": seq,
                    "encoding": enc_name,
                    "length": len(seq)
                })

    # Sort by length (longer = more interesting)
    all_sequences.sort(key=lambda x: x["length"], reverse=True)
    results["interesting_findings"] = all_sequences[:50]

    print(f"  Top 10 longest readable sequences:")
    for item in all_sequences[:10]:
        print(f"    [{item['encoding']}] '{item['sequence']}' (len={item['length']})")

    # Analyze specific row patterns
    print("\n=== ROW-BY-ROW ANALYSIS ===")
    row_messages = []
    for i, row in enumerate(matrix[:20]):  # First 20 rows
        row_sign = sign_bit_encoding(row)
        row_parity = parity_encoding(row)

        sign_data = bits_to_bytes(row_sign)
        parity_data = bits_to_bytes(row_parity)

        sign_ascii = bytes_to_ascii(sign_data)
        parity_ascii = bytes_to_ascii(parity_data)

        sign_readable = extract_readable_sequences(sign_ascii, 3)
        parity_readable = extract_readable_sequences(parity_ascii, 3)

        if sign_readable or parity_readable:
            row_messages.append({
                "row": i,
                "sign_sequences": sign_readable,
                "parity_sequences": parity_readable
            })
            print(f"  Row {i}: sign={sign_readable[:3]}, parity={parity_readable[:3]}")

    results["special_patterns"]["row_by_row"] = row_messages

    # Save results
    output_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/BINARY_MESSAGES.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n=== RESULTS SAVED TO {output_path} ===")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total encodings analyzed: {len(results['encodings'])}")
    print(f"Interesting sequences found: {len(results['interesting_findings'])}")
    print(f"Known strings found: {len(results['known_strings_found'])}")

    if results['known_strings_found']:
        print("\nKNOWN STRINGS DETECTED:")
        for item in results['known_strings_found']:
            print(f"  '{item['string']}' at position {item['position']} in {item['encoding']}")

    return results

if __name__ == "__main__":
    main()
