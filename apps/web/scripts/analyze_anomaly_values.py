#!/usr/bin/env python3
"""
Anna Matrix Anomaly Value Decoder
Analyzes the 68 anomaly cells for hidden patterns or messages.
"""

import json
import os
from collections import Counter
from itertools import combinations

# Load the anomaly data
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'public', 'data', 'anna-matrix-anomalies.json')

with open(data_path, 'r') as f:
    data = json.load(f)

anomalies = data['anomalies']

# Extract all 68 values: primary positions + mirror positions
primary_values = []
mirror_values = []
all_positions = []
all_values = []

for a in anomalies:
    primary_values.append(a['value'])
    mirror_values.append(a['mirrorValue'])
    all_positions.append(tuple(a['pos']))
    all_positions.append(tuple(a['mirrorPos']))
    all_values.append(a['value'])
    all_values.append(a['mirrorValue'])

# Sort by row, then column
anomaly_list = []
for a in anomalies:
    anomaly_list.append({'pos': tuple(a['pos']), 'value': a['value']})
    anomaly_list.append({'pos': tuple(a['mirrorPos']), 'value': a['mirrorValue']})

# Sort by row, then column
anomaly_list.sort(key=lambda x: (x['pos'][0], x['pos'][1]))

# Extract ordered values
ordered_values = [a['value'] for a in anomaly_list]
ordered_positions = [a['pos'] for a in anomaly_list]

results = {
    "metadata": {
        "title": "Anna Matrix Anomaly Value Decode Analysis",
        "totalAnomalyCells": 68,
        "analysisDate": "2026-01-17"
    },
    "orderedValues": ordered_values,
    "orderedPositions": [list(p) for p in ordered_positions],
    "decodings": {}
}

print("=" * 70)
print("ANNA MATRIX ANOMALY VALUE DECODE ANALYSIS")
print("=" * 70)
print(f"\nTotal anomaly cells: {len(ordered_values)}")
print(f"\nOrdered values (by row, then column):")
print(ordered_values)

# 1. ASCII DECODE (mod 256 for negative values)
print("\n" + "=" * 70)
print("1. ASCII DECODE")
print("=" * 70)

ascii_values = [(v % 256) for v in ordered_values]
ascii_chars = ''.join([chr(v) if 32 <= v < 127 else '.' for v in ascii_values])
ascii_full = ''.join([chr(v % 256) for v in ordered_values])

print(f"\nMod 256 values: {ascii_values}")
print(f"\nPrintable ASCII (others as '.'): {ascii_chars}")
print(f"\nAll chars (raw): {repr(ascii_full)}")

results["decodings"]["ascii"] = {
    "mod256Values": ascii_values,
    "printableAscii": ascii_chars,
    "rawChars": ascii_full,
    "printableCount": sum(1 for v in ascii_values if 32 <= v < 127)
}

# 2. HEX DECODE
print("\n" + "=" * 70)
print("2. HEX REPRESENTATION")
print("=" * 70)

hex_values = [format(v & 0xFF, '02x') for v in ordered_values]
hex_string = ''.join(hex_values)
print(f"\nHex bytes: {hex_string}")

# Try to interpret as address or key
results["decodings"]["hex"] = {
    "hexString": hex_string,
    "byteCount": len(hex_values),
    "hexValues": hex_values
}

# 3. BINARY PATTERNS
print("\n" + "=" * 70)
print("3. BINARY PATTERNS")
print("=" * 70)

binary_values = [format(v & 0xFF, '08b') for v in ordered_values]
binary_string = ''.join(binary_values)
print(f"\nBinary string ({len(binary_string)} bits):")
print(binary_string[:128] + "...")

# Count 1s and 0s
ones = binary_string.count('1')
zeros = binary_string.count('0')
print(f"\n1s: {ones}, 0s: {zeros}, Ratio: {ones/zeros:.4f}")

# Check for repeated patterns
results["decodings"]["binary"] = {
    "totalBits": len(binary_string),
    "ones": ones,
    "zeros": zeros,
    "ratio": ones / zeros if zeros > 0 else float('inf'),
    "first128bits": binary_string[:128],
    "binaryValues": binary_values
}

# 4. SUM PATTERNS
print("\n" + "=" * 70)
print("4. SUM PATTERNS")
print("=" * 70)

total_sum = sum(ordered_values)
primary_sum = sum(primary_values)
mirror_sum = sum(mirror_values)

print(f"\nTotal sum of all 68 values: {total_sum}")
print(f"Sum of 34 primary values: {primary_sum}")
print(f"Sum of 34 mirror values: {mirror_sum}")
print(f"Primary + Mirror: {primary_sum + mirror_sum}")

# Check if sum relates to known constants
print(f"\nSum mod 127: {total_sum % 127}")
print(f"Sum mod 128: {total_sum % 128}")
print(f"Sum mod 256: {total_sum % 256}")

# Sum of absolute values
abs_sum = sum(abs(v) for v in ordered_values)
print(f"Sum of absolute values: {abs_sum}")

results["decodings"]["sums"] = {
    "totalSum": total_sum,
    "primarySum": primary_sum,
    "mirrorSum": mirror_sum,
    "absSum": abs_sum,
    "sumMod127": total_sum % 127,
    "sumMod128": total_sum % 128,
    "sumMod256": total_sum % 256
}

# 5. XOR PATTERNS
print("\n" + "=" * 70)
print("5. XOR PATTERNS")
print("=" * 70)

# XOR all values together
xor_all = 0
for v in ordered_values:
    xor_all ^= (v & 0xFF)
print(f"\nXOR of all 68 values: {xor_all} (0x{xor_all:02x}, char: {chr(xor_all) if 32 <= xor_all < 127 else '?'})")

# XOR primary vs mirror
xor_primary = 0
for v in primary_values:
    xor_primary ^= (v & 0xFF)
xor_mirror = 0
for v in mirror_values:
    xor_mirror ^= (v & 0xFF)
print(f"XOR of primary values: {xor_primary} (0x{xor_primary:02x})")
print(f"XOR of mirror values: {xor_mirror} (0x{xor_mirror:02x})")
print(f"Primary XOR Mirror: {xor_primary ^ xor_mirror}")

# Try XOR with various constants
print("\nXOR with constants:")
for const in [13, 27, 100, 127, 128, 255]:
    xored = [(v ^ const) & 0xFF for v in ordered_values]
    chars = ''.join([chr(c) if 32 <= c < 127 else '.' for c in xored])
    print(f"  XOR {const:3d}: {chars}")

results["decodings"]["xor"] = {
    "xorAll": xor_all,
    "xorPrimary": xor_primary,
    "xorMirror": xor_mirror,
    "primaryXorMirror": xor_primary ^ xor_mirror
}

# 6. MATHEMATICAL SEQUENCES
print("\n" + "=" * 70)
print("6. MATHEMATICAL SEQUENCE ANALYSIS")
print("=" * 70)

# Differences between consecutive values
diffs = [ordered_values[i+1] - ordered_values[i] for i in range(len(ordered_values)-1)]
print(f"\nDifferences: {diffs[:20]}...")

# Check for arithmetic progression
diff_counter = Counter(diffs)
print(f"\nMost common differences: {diff_counter.most_common(10)}")

# Check modular patterns
mod_patterns = {}
for m in [3, 5, 7, 8, 11, 13, 19, 27]:
    pattern = [v % m for v in ordered_values]
    mod_patterns[m] = pattern
    unique = len(set(pattern))
    print(f"Mod {m:2d}: unique values = {unique}, pattern = {pattern[:15]}...")

results["decodings"]["sequences"] = {
    "differences": diffs,
    "mostCommonDiffs": diff_counter.most_common(10),
    "modPatterns": {str(k): v for k, v in mod_patterns.items()}
}

# 7. VALUE FREQUENCY ANALYSIS
print("\n" + "=" * 70)
print("7. VALUE FREQUENCY ANALYSIS")
print("=" * 70)

value_counter = Counter(ordered_values)
print(f"\nValue frequencies:")
for val, count in value_counter.most_common(15):
    print(f"  {val:4d}: appears {count} times")

# Check for special values
special_values = [-121, 100, 127, -127, 0, 1, -1]
print(f"\nSpecial value occurrences:")
for sv in special_values:
    count = ordered_values.count(sv)
    if count > 0:
        print(f"  {sv}: {count} times")

results["decodings"]["frequency"] = {
    "valueCounts": dict(value_counter),
    "totalUnique": len(value_counter)
}

# 8. COLUMN 22 vs COLUMN 97 ANALYSIS
print("\n" + "=" * 70)
print("8. COLUMN-SPECIFIC ANALYSIS")
print("=" * 70)

col22_values = [a['value'] for a in anomalies if a['pos'][1] == 22]
col97_values = [a['value'] for a in anomalies if a['pos'][1] == 97]

print(f"\nColumn 22 values ({len(col22_values)}): {col22_values}")
print(f"Column 97 values ({len(col97_values)}): {col97_values}")

col22_ascii = ''.join([chr(v % 256) if 32 <= (v % 256) < 127 else '.' for v in col22_values])
col97_ascii = ''.join([chr(v % 256) if 32 <= (v % 256) < 127 else '.' for v in col97_values])

print(f"\nColumn 22 ASCII: {col22_ascii}")
print(f"Column 97 ASCII: {col97_ascii}")

print(f"\nColumn 22 sum: {sum(col22_values)}")
print(f"Column 97 sum: {sum(col97_values)}")

results["decodings"]["columnAnalysis"] = {
    "column22": {
        "values": col22_values,
        "ascii": col22_ascii,
        "sum": sum(col22_values)
    },
    "column97": {
        "values": col97_values,
        "ascii": col97_ascii,
        "sum": sum(col97_values)
    }
}

# 9. PAIR ANALYSIS (each anomaly with its mirror)
print("\n" + "=" * 70)
print("9. PAIR ANALYSIS")
print("=" * 70)

pair_sums = [a['value'] + a['mirrorValue'] for a in anomalies]
pair_xors = [(a['value'] ^ a['mirrorValue']) & 0xFF for a in anomalies]
pair_products = [a['value'] * a['mirrorValue'] for a in anomalies]

print(f"\nPair sums: {pair_sums}")
print(f"Pair XORs: {pair_xors}")

sum_counter = Counter(pair_sums)
print(f"\nMost common pair sums: {sum_counter.most_common(10)}")

# Check for patterns in pair sums
unique_sums = sorted(set(pair_sums))
print(f"\nUnique pair sums: {unique_sums}")

# Notable: sum = 127 or -127 (2^7 - 1)
sum127_count = pair_sums.count(127) + pair_sums.count(-127)
print(f"\nPairs summing to +/-127: {sum127_count}")

results["decodings"]["pairAnalysis"] = {
    "pairSums": pair_sums,
    "pairXors": pair_xors,
    "uniqueSums": unique_sums,
    "sumFrequency": dict(sum_counter)
}

# 10. HIDDEN MESSAGE SEARCH
print("\n" + "=" * 70)
print("10. HIDDEN MESSAGE SEARCH")
print("=" * 70)

# Try different orderings and transformations
messages_found = []

# A) Primary values only as ASCII
primary_ascii = ''.join([chr(v % 256) if 32 <= (v % 256) < 127 else '.' for v in primary_values])
print(f"\nPrimary values ASCII: {primary_ascii}")

# B) Mirror values only as ASCII
mirror_ascii = ''.join([chr(v % 256) if 32 <= (v % 256) < 127 else '.' for v in mirror_values])
print(f"Mirror values ASCII: {mirror_ascii}")

# C) Alternate primary/mirror
alternate = []
for p, m in zip(primary_values, mirror_values):
    alternate.extend([p, m])
alternate_ascii = ''.join([chr(v % 256) if 32 <= (v % 256) < 127 else '.' for v in alternate])
print(f"Alternating ASCII: {alternate_ascii}")

# D) Check if values encode base64 indices or similar
import string
base64_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
base64_decode = []
for v in ordered_values:
    idx = v % 64
    if 0 <= idx < 64:
        base64_decode.append(base64_chars[idx])
print(f"\nAs base64 indices: {''.join(base64_decode)}")

# E) ROT13 on ASCII values
def rot13(c):
    if 'a' <= c <= 'z':
        return chr((ord(c) - ord('a') + 13) % 26 + ord('a'))
    if 'A' <= c <= 'Z':
        return chr((ord(c) - ord('A') + 13) % 26 + ord('A'))
    return c

rot13_primary = ''.join([rot13(chr(v % 256)) if 32 <= (v % 256) < 127 else '.' for v in primary_values])
print(f"Primary ROT13: {rot13_primary}")

results["decodings"]["hiddenMessages"] = {
    "primaryAscii": primary_ascii,
    "mirrorAscii": mirror_ascii,
    "alternatingAscii": alternate_ascii,
    "base64Indices": ''.join(base64_decode),
    "primaryRot13": rot13_primary
}

# 11. BYTE GROUPINGS
print("\n" + "=" * 70)
print("11. BYTE GROUPINGS (2, 4, 8)")
print("=" * 70)

# Group into 16-bit, 32-bit, 64-bit values
def bytes_to_int(byte_list, big_endian=True):
    result = 0
    if big_endian:
        for b in byte_list:
            result = (result << 8) | (b & 0xFF)
    else:
        for i, b in enumerate(byte_list):
            result |= (b & 0xFF) << (8 * i)
    return result

byte_vals = [v & 0xFF for v in ordered_values]

# 16-bit values
int16_be = [bytes_to_int(byte_vals[i:i+2], True) for i in range(0, len(byte_vals)-1, 2)]
int16_le = [bytes_to_int(byte_vals[i:i+2], False) for i in range(0, len(byte_vals)-1, 2)]
print(f"\n16-bit BE: {int16_be[:10]}...")
print(f"16-bit LE: {int16_le[:10]}...")

# 32-bit values
int32_be = [bytes_to_int(byte_vals[i:i+4], True) for i in range(0, len(byte_vals)-3, 4)]
int32_le = [bytes_to_int(byte_vals[i:i+4], False) for i in range(0, len(byte_vals)-3, 4)]
print(f"\n32-bit BE: {[hex(x) for x in int32_be[:5]]}...")

results["decodings"]["byteGroupings"] = {
    "int16BE": int16_be,
    "int16LE": int16_le,
    "int32BE": int32_be,
    "int32LE": int32_le
}

# 12. POSITION-BASED ANALYSIS
print("\n" + "=" * 70)
print("12. POSITION-BASED PATTERNS")
print("=" * 70)

# Check if position relates to value
position_value_products = []
for pos, val in zip(ordered_positions, ordered_values):
    row, col = pos
    product = row * col
    xor_pos = row ^ col
    print(f"  ({row:3d}, {col:3d}): value={val:4d}, row*col={product:5d}, row^col={xor_pos:3d}, val%127={val%127:4d}")
    position_value_products.append({
        "pos": list(pos),
        "value": val,
        "rowTimesCol": product,
        "rowXorCol": xor_pos,
        "valueMod127": val % 127
    })

results["decodings"]["positionAnalysis"] = position_value_products[:20]

# 13. SPECIFIC MESSAGE SEARCHES
print("\n" + "=" * 70)
print("13. SPECIFIC PATTERN SEARCHES")
print("=" * 70)

# Search for known strings
known_patterns = ['ANNA', 'CFB', 'BTC', 'QUBIC', 'KEY', 'SEED', 'SATOSHI', 'GENESIS']
hex_upper = hex_string.upper()
for pattern in known_patterns:
    pattern_hex = pattern.encode().hex().upper()
    if pattern_hex in hex_upper:
        print(f"FOUND: '{pattern}' in hex at position {hex_upper.index(pattern_hex)//2}")

# Check if column 22 + column 97 encode something special
combined_cols = col22_values + col97_values
combined_ascii = ''.join([chr(v % 256) if 32 <= (v % 256) < 127 else '.' for v in combined_cols])
print(f"\nCombined columns 22+97 ASCII: {combined_ascii}")

# 14. SUMMARY OF KEY FINDINGS
print("\n" + "=" * 70)
print("14. KEY FINDINGS SUMMARY")
print("=" * 70)

key_findings = []

# Finding 1: Value -121 appears twice
if ordered_values.count(-121) > 0:
    key_findings.append({
        "finding": "Value -121 (= -11^2, Qubic constant) appears",
        "count": ordered_values.count(-121),
        "positions": [list(ordered_positions[i]) for i, v in enumerate(ordered_values) if v == -121]
    })
    print(f"- Value -121 appears {ordered_values.count(-121)} times (Qubic constant = -11^2)")

# Finding 2: Sum patterns
if total_sum % 127 == 0:
    key_findings.append({
        "finding": "Total sum divisible by 127",
        "sum": total_sum
    })
    print(f"- Total sum {total_sum} is divisible by 127")

# Finding 3: Pair sums = 127
count_127 = pair_sums.count(127)
if count_127 > 0:
    key_findings.append({
        "finding": "Pairs summing to 127",
        "count": count_127,
        "indices": [i for i, s in enumerate(pair_sums) if s == 127]
    })
    print(f"- {count_127} pairs sum to exactly 127 (2^7 - 1)")

# Finding 4: XOR result
key_findings.append({
    "finding": "XOR of all values",
    "xorAll": xor_all,
    "binary": format(xor_all, '08b'),
    "character": chr(xor_all) if 32 <= xor_all < 127 else None
})
print(f"- XOR of all 68 values = {xor_all} (0x{xor_all:02x})")

# Finding 5: Column 22 interpretation
if any(32 <= (v % 256) < 127 for v in col22_values):
    key_findings.append({
        "finding": "Column 22 has readable ASCII",
        "ascii": col22_ascii,
        "values": col22_values
    })
    print(f"- Column 22 partial ASCII: {col22_ascii}")

# Finding 6: Check for 68 = 4 * 17
key_findings.append({
    "finding": "68 = 4 * 17 cells",
    "significance": "4 quadrants, 17 per region potentially"
})
print(f"- 68 anomaly cells = 4 * 17")

# Finding 7: Position [22,22] has value 100
key_findings.append({
    "finding": "Position [22,22] = 100",
    "significance": "Diagonal self-match position, value 100 = 'd' in ASCII",
    "ascii": chr(100)
})
print(f"- Position [22,22] has value 100 (ASCII 'd'), only self-matching position")

results["keyFindings"] = key_findings

# 15. DEEP VALUE DECODE ATTEMPT
print("\n" + "=" * 70)
print("15. DEEP DECODE ATTEMPTS")
print("=" * 70)

# Try interpreting as UTF-8 bytes
try:
    utf8_bytes = bytes([v & 0xFF for v in ordered_values])
    utf8_decode = utf8_bytes.decode('utf-8', errors='replace')
    print(f"UTF-8 decode attempt: {utf8_decode}")
except:
    print("UTF-8 decode failed")

# Try Caesar cipher shifts
print("\nCaesar cipher attempts on ASCII:")
for shift in range(1, 26):
    shifted = []
    for v in ordered_values:
        c = v % 256
        if 65 <= c <= 90:  # Uppercase
            shifted.append(chr((c - 65 + shift) % 26 + 65))
        elif 97 <= c <= 122:  # Lowercase
            shifted.append(chr((c - 97 + shift) % 26 + 97))
        else:
            shifted.append('.')
    result = ''.join(shifted)
    if any(c.isalpha() for c in result):
        # Only print if there's meaningful content
        alpha_count = sum(1 for c in result if c.isalpha())
        if alpha_count > 10:
            print(f"  Shift {shift:2d}: {result}")

# 16. FINAL COMPREHENSIVE HEXDUMP
print("\n" + "=" * 70)
print("16. COMPREHENSIVE HEXDUMP")
print("=" * 70)

print("\nPos    Dec   Hex  Bin        ASCII  Mod127")
print("-" * 55)
for i, (pos, val) in enumerate(zip(ordered_positions, ordered_values)):
    byte_val = val & 0xFF
    char = chr(byte_val) if 32 <= byte_val < 127 else '.'
    mod127 = val % 127
    print(f"({pos[0]:3d},{pos[1]:3d}) {val:4d}  {byte_val:02x}   {byte_val:08b}  '{char}'    {mod127:4d}")

results["hexDump"] = [
    {
        "position": list(ordered_positions[i]),
        "decimal": ordered_values[i],
        "hex": format(ordered_values[i] & 0xFF, '02x'),
        "binary": format(ordered_values[i] & 0xFF, '08b'),
        "ascii": chr(ordered_values[i] & 0xFF) if 32 <= (ordered_values[i] & 0xFF) < 127 else None,
        "mod127": ordered_values[i] % 127
    }
    for i in range(len(ordered_values))
]

# Save results
output_path = os.path.join(script_dir, 'ANOMALY_VALUE_DECODE.json')
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n\nResults saved to: {output_path}")
print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
