#!/usr/bin/env python3
"""
Deep Analysis of Anna Matrix Anomaly Values
Following up on initial findings with targeted decoding attempts.
"""

import json
import os

# Load the previous results
script_dir = os.path.dirname(os.path.abspath(__file__))

# Key findings from initial analysis that warrant deeper investigation:
# 1. Column 22 ASCII: \qd.*.jx(.,xe - contains readable letters
# 2. XOR all = 61 = '=' (ASCII equals sign)
# 3. Three pairs sum to 127
# 4. Value 100 at [22,22] - 'd' in ASCII
# 5. Values at mirrored col 105: fn.nFdBJ - interesting pattern

# Let's reconstruct the key data
anomalies_raw = [
    {"pos": [19, 127], "value": 15, "mirrorPos": [108, 0], "mirrorValue": -48},
    {"pos": [20, 22], "value": 92, "mirrorPos": [107, 105], "mirrorValue": -18},
    {"pos": [21, 22], "value": 113, "mirrorPos": [106, 105], "mirrorValue": -58},
    {"pos": [22, 22], "value": 100, "mirrorPos": [105, 105], "mirrorValue": 100},
    {"pos": [23, 22], "value": -121, "mirrorPos": [104, 105], "mirrorValue": -26},
    {"pos": [24, 22], "value": 42, "mirrorPos": [103, 105], "mirrorValue": 74},
    {"pos": [25, 22], "value": 23, "mirrorPos": [102, 105], "mirrorValue": 66},
    {"pos": [26, 22], "value": 106, "mirrorPos": [101, 105], "mirrorValue": 100},
    {"pos": [27, 22], "value": 120, "mirrorPos": [100, 105], "mirrorValue": 70},
    {"pos": [28, 22], "value": 40, "mirrorPos": [99, 105], "mirrorValue": 110},
    {"pos": [29, 22], "value": -121, "mirrorPos": [98, 105], "mirrorValue": -50},
    {"pos": [30, 22], "value": 44, "mirrorPos": [97, 105], "mirrorValue": 110},
    {"pos": [31, 22], "value": 120, "mirrorPos": [96, 105], "mirrorValue": 102},
    {"pos": [32, 22], "value": 101, "mirrorPos": [95, 105], "mirrorValue": -108},
    {"pos": [48, 97], "value": 14, "mirrorPos": [79, 30], "mirrorValue": -16},
    {"pos": [50, 97], "value": -114, "mirrorPos": [77, 30], "mirrorValue": -15},
    {"pos": [51, 97], "value": 14, "mirrorPos": [76, 30], "mirrorValue": 113},
    {"pos": [53, 97], "value": 30, "mirrorPos": [74, 30], "mirrorValue": -15},
    {"pos": [54, 97], "value": 10, "mirrorPos": [73, 30], "mirrorValue": -31},
    {"pos": [55, 97], "value": 26, "mirrorPos": [72, 30], "mirrorValue": -11},
    {"pos": [56, 97], "value": -114, "mirrorPos": [71, 30], "mirrorValue": -27},
    {"pos": [57, 97], "value": 30, "mirrorPos": [70, 30], "mirrorValue": 113},
    {"pos": [58, 97], "value": -114, "mirrorPos": [69, 30], "mirrorValue": -31},
    {"pos": [59, 97], "value": -98, "mirrorPos": [68, 30], "mirrorValue": 113},
    {"pos": [60, 30], "value": 81, "mirrorPos": [67, 97], "mirrorValue": 46},
    {"pos": [60, 97], "value": 22, "mirrorPos": [67, 30], "mirrorValue": 97},
    {"pos": [61, 30], "value": -45, "mirrorPos": [66, 97], "mirrorValue": -82},
    {"pos": [61, 97], "value": 30, "mirrorPos": [66, 30], "mirrorValue": -23},
    {"pos": [62, 30], "value": -47, "mirrorPos": [65, 97], "mirrorValue": 44},
    {"pos": [62, 41], "value": -101, "mirrorPos": [65, 86], "mirrorValue": 109},
    {"pos": [62, 97], "value": -102, "mirrorPos": [65, 30], "mirrorValue": -31},
    {"pos": [63, 30], "value": -27, "mirrorPos": [64, 97], "mirrorValue": 46},
    {"pos": [63, 41], "value": -101, "mirrorPos": [64, 86], "mirrorValue": 109},
    {"pos": [63, 97], "value": 26, "mirrorPos": [64, 30], "mirrorValue": 101}
]

print("=" * 70)
print("DEEP DECODE ANALYSIS - ANNA MATRIX ANOMALIES")
print("=" * 70)

# ANALYSIS 1: Focus on column 22 values (the primary anomaly stripe)
print("\n" + "=" * 70)
print("ANALYSIS 1: Column 22 Primary Stripe (rows 20-32)")
print("=" * 70)

col22_anomalies = [a for a in anomalies_raw if a['pos'][1] == 22]
col22_values = [a['value'] for a in col22_anomalies]
col22_rows = [a['pos'][0] for a in col22_anomalies]

print(f"\nColumn 22 values by row:")
for a in col22_anomalies:
    v = a['value']
    byte_val = v & 0xFF
    char = chr(byte_val) if 32 <= byte_val < 127 else '.'
    print(f"  Row {a['pos'][0]:2d}: {v:4d} -> 0x{byte_val:02x} = '{char}'")

# Interesting: Let's look at just the printable characters from col 22
col22_printable = []
for v in col22_values:
    b = v & 0xFF
    if 32 <= b < 127:
        col22_printable.append(chr(b))
col22_message = ''.join(col22_printable)
print(f"\nColumn 22 printable message: '{col22_message}'")

# ANALYSIS 2: Mirror column 105 values
print("\n" + "=" * 70)
print("ANALYSIS 2: Mirror Column 105 (mirrors of col 22)")
print("=" * 70)

col105_values = [a['mirrorValue'] for a in col22_anomalies]
print(f"\nColumn 105 values:")
for a in col22_anomalies:
    v = a['mirrorValue']
    byte_val = v & 0xFF
    char = chr(byte_val) if 32 <= byte_val < 127 else '.'
    print(f"  Row {a['mirrorPos'][0]:3d}: {v:4d} -> 0x{byte_val:02x} = '{char}'")

col105_printable = []
for v in col105_values:
    b = v & 0xFF
    if 32 <= b < 127:
        col105_printable.append(chr(b))
col105_message = ''.join(col105_printable)
print(f"\nColumn 105 printable message: '{col105_message}'")

# ANALYSIS 3: Interleave col22 and col105 for combined message
print("\n" + "=" * 70)
print("ANALYSIS 3: Combined Interleaved Messages")
print("=" * 70)

# Interleave: 22, 105, 22, 105...
interleaved = []
for a in col22_anomalies:
    interleaved.append(a['value'])
    interleaved.append(a['mirrorValue'])

interleaved_chars = []
for v in interleaved:
    b = v & 0xFF
    if 32 <= b < 127:
        interleaved_chars.append(chr(b))
    else:
        interleaved_chars.append('.')
print(f"Interleaved (col22+col105): {''.join(interleaved_chars)}")

# ANALYSIS 4: Look at mod127 values for hidden patterns
print("\n" + "=" * 70)
print("ANALYSIS 4: Mod 127 Values (signed to 0-126 range)")
print("=" * 70)

all_values = []
for a in anomalies_raw:
    all_values.append((a['pos'], a['value']))
    all_values.append((a['mirrorPos'], a['mirrorValue']))

# Sort by row then column
all_values.sort(key=lambda x: (x[0][0], x[0][1]))

mod127_chars = []
for pos, val in all_values:
    m = val % 127
    if 32 <= m < 127:
        mod127_chars.append(chr(m))
    else:
        mod127_chars.append('.')

print(f"Mod 127 as ASCII: {''.join(mod127_chars)}")

# Check if mod127 values spell anything
mod127_printable = [chr(val % 127) for pos, val in all_values if 32 <= (val % 127) < 127]
print(f"Mod 127 printable only: {''.join(mod127_printable)}")

# ANALYSIS 5: Key numbers in the data
print("\n" + "=" * 70)
print("ANALYSIS 5: Significant Number Patterns")
print("=" * 70)

# The number 22 and 105 are interesting
print(f"\n22 + 105 = {22 + 105}")  # 127
print(f"22 ^ 105 = {22 ^ 105}")  # 127
print(f"22 * 105 = {22 * 105}")  # 2310

# Column 97 + column 30
print(f"\n97 + 30 = {97 + 30}")  # 127
print(f"97 ^ 30 = {97 ^ 30}")  # 127

# All key columns seem to relate to 127!
print("\nKey finding: All anomaly column pairs sum/XOR to 127!")
print("  Col 22 + Col 105 = 127")
print("  Col 97 + Col 30 = 127")
print("  Col 41 + Col 86 = 127")

# ANALYSIS 6: Row-based message extraction
print("\n" + "=" * 70)
print("ANALYSIS 6: Row Ranges Analysis")
print("=" * 70)

# Rows 20-32 in column 22
rows_20_32 = [92, 113, 100, -121, 42, 23, 106, 120, 40, -121, 44, 120, 101]
print(f"\nRows 20-32 col 22 values: {rows_20_32}")

# Map to ASCII
ascii_20_32 = ''.join([chr(v & 0xFF) if 32 <= (v & 0xFF) < 127 else '_' for v in rows_20_32])
print(f"ASCII: {ascii_20_32}")

# Check if it encodes as hex pairs
hex_pairs = ''.join([format(v & 0xFF, '02x') for v in rows_20_32])
print(f"Hex: {hex_pairs}")

# ANALYSIS 7: XOR between primary and mirror
print("\n" + "=" * 70)
print("ANALYSIS 7: Primary XOR Mirror for Each Pair")
print("=" * 70)

xor_results = []
for a in anomalies_raw:
    p = a['value'] & 0xFF
    m = a['mirrorValue'] & 0xFF
    x = p ^ m
    xor_results.append(x)
    char = chr(x) if 32 <= x < 127 else '.'
    print(f"  [{a['pos'][0]:2d},{a['pos'][1]:3d}] {a['value']:4d} XOR {a['mirrorValue']:4d} = {x:3d} ('{char}')")

xor_message = ''.join([chr(x) if 32 <= x < 127 else '.' for x in xor_results])
print(f"\nXOR message: {xor_message}")

# ANALYSIS 8: Sum patterns for pairs
print("\n" + "=" * 70)
print("ANALYSIS 8: Pair Sums as Potential Message")
print("=" * 70)

sums = []
for a in anomalies_raw:
    s = a['value'] + a['mirrorValue']
    sums.append(s)
    char = chr(s & 0xFF) if 32 <= (s & 0xFF) < 127 else '.'
    print(f"  Sum {s:4d} -> '{char}'")

sum_message = ''.join([chr(s & 0xFF) if 32 <= (s & 0xFF) < 127 else '.' for s in sums])
print(f"\nSum message: {sum_message}")

# ANALYSIS 9: Check special position [22,22] = 100 = 'd'
print("\n" + "=" * 70)
print("ANALYSIS 9: The Special Position [22,22]")
print("=" * 70)

print(f"\nPosition [22, 22]:")
print(f"  Value = 100 (ASCII 'd')")
print(f"  22 + 22 = 44 (ASCII ',')")
print(f"  22 * 22 = 484")
print(f"  22 XOR 22 = 0")
print(f"  Mirror position [105, 105] also has value 100 (UNIQUE!)")
print(f"  This is the ONLY position where value = mirrorValue")
print(f"\n  Significance: 'd' could stand for:")
print(f"    - diagonal")
print(f"    - deterministic")
print(f"    - 'd' in hexadecimal (13)")
print(f"    - day/date marker")

# ANALYSIS 10: Reverse the column 22 sequence
print("\n" + "=" * 70)
print("ANALYSIS 10: Reversed Sequences")
print("=" * 70)

col22_reversed = col22_values[::-1]
col22_rev_ascii = ''.join([chr(v & 0xFF) if 32 <= (v & 0xFF) < 127 else '.' for v in col22_reversed])
print(f"Column 22 reversed ASCII: {col22_rev_ascii}")

# ANALYSIS 11: Specific value investigation
print("\n" + "=" * 70)
print("ANALYSIS 11: Value 113 Investigation")
print("=" * 70)

# 113 appears 4 times - is it significant?
print(f"\nValue 113 = 'q' appears at:")
for pos, val in all_values:
    if val == 113:
        print(f"  Position {pos}")

# 113 in binary
print(f"\n113 in binary: {bin(113)} = 01110001")
print(f"113 is prime: {all(113 % i != 0 for i in range(2, int(113**0.5)+1))}")

# ANALYSIS 12: Column 97 (secondary stripe) analysis
print("\n" + "=" * 70)
print("ANALYSIS 12: Column 97 Secondary Stripe")
print("=" * 70)

col97_anomalies = [a for a in anomalies_raw if a['pos'][1] == 97]
print(f"\nColumn 97 values:")
for a in col97_anomalies:
    v = a['value']
    byte_val = v & 0xFF
    char = chr(byte_val) if 32 <= byte_val < 127 else '.'
    print(f"  Row {a['pos'][0]:2d}: {v:4d} -> 0x{byte_val:02x} = '{char}'")

# All column 97 values seem to be control characters or high bytes
# Let's check their mod 127 interpretations
print(f"\nColumn 97 as mod 127:")
for a in col97_anomalies:
    v = a['value']
    m = v % 127
    char = chr(m) if 32 <= m < 127 else '.'
    print(f"  Row {a['pos'][0]:2d}: {v:4d} mod 127 = {m:3d} = '{char}'")

# ANALYSIS 13: Binary bit patterns
print("\n" + "=" * 70)
print("ANALYSIS 13: Binary Bit Pattern Analysis")
print("=" * 70)

# Check if high bits form a pattern
all_vals_sorted = [v for _, v in all_values]
high_bits = ''.join(['1' if (v & 0x80) else '0' for v in all_vals_sorted])
print(f"\nHigh bit pattern (68 bits): {high_bits}")
print(f"Number of 1s: {high_bits.count('1')}")
print(f"Number of 0s: {high_bits.count('0')}")

# Check low nibbles
low_nibbles = [v & 0x0F for v in all_vals_sorted]
print(f"\nLow nibbles: {low_nibbles}")

# ANALYSIS 14: The final encoded message hypothesis
print("\n" + "=" * 70)
print("ANALYSIS 14: Final Message Reconstruction Attempts")
print("=" * 70)

# Hypothesis 1: Column 22 contains the primary message
col22_msg = ''.join([chr(v & 0xFF) for v in col22_values])
print(f"\nColumn 22 raw: {repr(col22_msg)}")

# Hypothesis 2: Read only positive values
positive_vals = [(pos, val) for pos, val in all_values if val > 0]
pos_message = ''.join([chr(val) if 32 <= val < 127 else '.' for _, val in positive_vals])
print(f"Positive values ASCII: {pos_message}")

# Hypothesis 3: The message is in the mod127 of negative values
neg_vals = [(pos, val) for pos, val in all_values if val < 0]
neg_mod127 = ''.join([chr(val % 127) if 32 <= (val % 127) < 127 else '.' for _, val in neg_vals])
print(f"Negative values mod 127: {neg_mod127}")

# Hypothesis 4: Concatenate readable parts
# From column 22 we get: \, q, d, *, j, x, (, ,, x, e
# From column 105 we get: m, n, F, d, B, J, d
readable_col22 = ['\\', 'q', 'd', '*', 'j', 'x', '(', ',', 'x', 'e']
readable_col105 = ['m', 'n', 'F', 'd', 'B', 'J', 'd']
print(f"\nReadable from col 22: {''.join(readable_col22)}")
print(f"Readable from col 105: {''.join(readable_col105)}")

# ANALYSIS 15: Key value sequences
print("\n" + "=" * 70)
print("ANALYSIS 15: Key Value Sequences")
print("=" * 70)

# Look at the mirror column 105 more closely - it spells something!
# Row 95-108: -108, 102, 110, -50, 110, 70, 100, 66, 74, -26, 100, -58, -18, -48
mirror_105_only = [-18, -58, 100, -26, 74, 66, 100, 70, 110, -50, 110, 102, -108]  # From row 107 down
mirror_105_chars = ''.join([chr(v & 0xFF) if 32 <= (v & 0xFF) < 127 else '.' for v in mirror_105_only])
print(f"Mirror col 105 (bottom to top): {mirror_105_chars}")

# The readable portion 'fn.nFdBJ' is interesting
# F = 70, d = 100, B = 66, J = 74
# Together: FdBJ could be an acronym or identifier

print("\n" + "=" * 70)
print("SUMMARY OF DISCOVERIES")
print("=" * 70)

summary = {
    "key_findings": [
        {
            "finding": "All anomaly column pairs sum to 127",
            "details": "22+105=127, 97+30=127, 41+86=127",
            "significance": "127 = 2^7 - 1, maximum signed byte value"
        },
        {
            "finding": "Column 22 contains partially readable ASCII",
            "message": "\\qd*jx(,xe",
            "significance": "May encode a key or seed fragment"
        },
        {
            "finding": "Column 105 contains 'FdBJd'",
            "details": "Letters F, d, B, J appear in sequence",
            "significance": "Could be acronym: 'Foundation' + dBJ?"
        },
        {
            "finding": "XOR of all 68 values = 61 = '='",
            "details": "The equals sign may indicate equivalence/balance",
            "significance": "Point symmetry theme"
        },
        {
            "finding": "Position [22,22] = [105,105] = 100 = 'd'",
            "details": "Only position with identical mirror value",
            "significance": "Diagonal self-match, 'd' for diagonal?"
        },
        {
            "finding": "Value -121 appears twice",
            "details": "-121 = -(11^2) = negative Qubic constant",
            "positions": [[23,22], [29,22]]
        },
        {
            "finding": "68 anomalies = 4 * 17",
            "details": "17 is a significant prime in cryptography",
            "significance": "May relate to 17-byte keys or 17-word seeds"
        },
        {
            "finding": "Three pairs sum exactly to 127",
            "indices": [16, 24, 33],
            "significance": "Maximum positive signed byte value"
        }
    ],
    "potential_messages": {
        "column22_ascii": "\\qd*jx(,xe",
        "column105_ascii": "FdBJd",
        "xor_all": "= (equals sign)",
        "special_position": "d at [22,22]"
    },
    "column_arithmetic": {
        "col22_col105": "22 + 105 = 22 XOR 105 = 127",
        "col97_col30": "97 + 30 = 97 XOR 30 = 127",
        "col41_col86": "41 + 86 = 127"
    }
}

print(json.dumps(summary, indent=2))

# Save results
output_path = os.path.join(script_dir, 'ANOMALY_DEEP_DECODE.json')
with open(output_path, 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\n\nDeep analysis saved to: {output_path}")
