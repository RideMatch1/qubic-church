#!/usr/bin/env python3
"""
===============================================================================
            🔥 COLUMN 22↔105 ANALYSIS 🔥
===============================================================================
The SECOND biggest hotspot: 13 asymmetric cells.
22 + 105 = 127 (symmetric partner)

Special: Position [22,22] = 100 (on main diagonal, asymmetric!)
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import re

script_dir = Path(__file__).parent

print("=" * 80)
print("           🔥 COLUMN 22↔105 ANALYSIS 🔥")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# EXTRACT COLUMNS 22 AND 105
# ==============================================================================
print("\n" + "=" * 80)
print("COLUMN EXTRACTION")
print("=" * 80)

col_22 = [int(matrix[r, 22]) for r in range(128)]
col_105 = [int(matrix[r, 105]) for r in range(128)]

# XOR
xor_22_105 = [col_22[r] ^ col_105[r] for r in range(128)]
xor_string = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_22_105)

print(f"\n  Col22 ⊕ Col105 as ASCII:")
for i in range(0, 128, 32):
    print(f"    [{i:3d}-{i+31:3d}]: {xor_string[i:i+32]}")

# ==============================================================================
# FIND WORDS
# ==============================================================================
print("\n" + "=" * 80)
print("WORDS IN XOR STRING")
print("=" * 80)

words = re.findall(r'[a-zA-Z]{3,}', xor_string)
print(f"\n  3+ letter words found: {len(words)}")
for word in words:
    pos = xor_string.find(word)
    print(f"    Position {pos:3d}: '{word}'")

# 2-letter words
words_2 = re.findall(r'[a-zA-Z]{2}', xor_string)
print(f"\n  2-letter sequences: {len(words_2)}")
unique_2 = list(set(words_2))
print(f"    Unique: {unique_2[:20]}...")

# ==============================================================================
# ASYMMETRIC ROWS IN 22↔105
# ==============================================================================
print("\n" + "=" * 80)
print("ASYMMETRIC ROWS IN COLUMNS 22↔105")
print("=" * 80)

asymmetric_rows = []
for r in range(128):
    val_22 = col_22[r]
    val_105_partner = col_105[127 - r]

    if val_22 + val_105_partner != -1:
        asymmetric_rows.append({
            "row": r,
            "col22_val": val_22,
            "col105_partner_val": val_105_partner,
            "sum": val_22 + val_105_partner,
            "xor": val_22 ^ val_105_partner,
        })

print(f"\n  Found {len(asymmetric_rows)} asymmetric rows:")
print("  " + "-" * 60)
for ar in asymmetric_rows:
    ch22 = chr(abs(ar["col22_val"])) if 32 <= abs(ar["col22_val"]) <= 126 else '.'
    ch105 = chr(abs(ar["col105_partner_val"])) if 32 <= abs(ar["col105_partner_val"]) <= 126 else '.'
    print(f"  Row {ar['row']:3d}: Col22={ar['col22_val']:4d} '{ch22}', Col105*={ar['col105_partner_val']:4d} '{ch105}', Sum={ar['sum']:4d}")

# ==============================================================================
# POSITION [22,22] SPECIAL ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("POSITION [22,22] - THE DIAGONAL ANOMALY")
print("=" * 80)

val_22_22 = int(matrix[22, 22])
val_105_105 = int(matrix[105, 105])  # Symmetric partner

print(f"\n  Value at [22,22]: {val_22_22}")
print(f"  Value at [105,105]: {val_105_105}")
print(f"  Sum: {val_22_22 + val_105_105}")
print(f"  Expected for symmetry: -1")
print(f"  Symmetric: {'YES' if val_22_22 + val_105_105 == -1 else 'NO'}")

# XOR Triangle analysis
print(f"\n  XOR Triangle Analysis:")
print(f"    100 XOR 27 = {100 ^ 27}")
print(f"    100 XOR 127 = {100 ^ 127}")
print(f"    27 XOR 127 = {27 ^ 127}")

if val_22_22 == 100:
    print(f"\n  🎯 [22,22] = 100 is part of the XOR triangle!")
    print(f"     The values 100, 27, 127 are XOR-related:")
    print(f"     100 ⊕ 27 = 127, 100 ⊕ 127 = 27, 27 ⊕ 127 = 100")

# ==============================================================================
# COMPARE WITH COL30⊕COL97
# ==============================================================================
print("\n" + "=" * 80)
print("COMPARISON: COL22⊕COL105 vs COL30⊕COL97")
print("=" * 80)

col_30 = [int(matrix[r, 30]) for r in range(128)]
col_97 = [int(matrix[r, 97]) for r in range(128)]
xor_30_97 = [col_30[r] ^ col_97[r] for r in range(128)]
xor_30_97_string = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_30_97)

# Similarity
matching = sum(1 for i in range(128) if xor_22_105[i] == xor_30_97[i])
print(f"\n  Matching values: {matching}/128 ({matching/128*100:.1f}%)")

# Find common words
words_30_97 = set(re.findall(r'[a-zA-Z]{3,}', xor_30_97_string))
words_22_105 = set(re.findall(r'[a-zA-Z]{3,}', xor_string))

common_words = words_30_97 & words_22_105
print(f"\n  Common 3+ letter words: {common_words if common_words else 'None'}")

# ==============================================================================
# LOOK FOR PATTERNS
# ==============================================================================
print("\n" + "=" * 80)
print("PATTERN SEARCH")
print("=" * 80)

# Check for AI, MEG, GOU in this column pair too
patterns = ["AI", "MEG", "GOU", "CFB", "BTC", "KEY", "FIB"]
print("\n  Searching for known patterns:")
for pattern in patterns:
    pos = xor_string.upper().find(pattern)
    if pos >= 0:
        print(f"    '{pattern}' found at position {pos}")
    else:
        print(f"    '{pattern}' NOT found")

# ==============================================================================
# ROW OVERLAP ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("ROW OVERLAP WITH COL30⊕COL97")
print("=" * 80)

# Get asymmetric rows from 30/97
asym_30_97 = []
for r in range(128):
    val_30 = col_30[r]
    val_97_partner = col_97[127 - r]
    if val_30 + val_97_partner != -1:
        asym_30_97.append(r)

asym_22_105_rows = [ar["row"] for ar in asymmetric_rows]

overlap = set(asym_22_105_rows) & set(asym_30_97)
print(f"\n  Asymmetric rows in Col22↔105: {sorted(asym_22_105_rows)}")
print(f"  Asymmetric rows in Col30↔97: {sorted(asym_30_97)}")
print(f"  Overlap: {sorted(overlap) if overlap else 'None'}")

# ==============================================================================
# EXTRACT MESSAGE FROM ASYMMETRIC ROWS
# ==============================================================================
print("\n" + "=" * 80)
print("MESSAGE FROM ASYMMETRIC ROWS")
print("=" * 80)

# Method 1: Direct values
chars_direct = []
for ar in asymmetric_rows:
    ch = chr(abs(ar["col22_val"])) if 32 <= abs(ar["col22_val"]) <= 126 else '.'
    chars_direct.append(ch)

print(f"\n  Method 1 (Col22 values): {''.join(chars_direct)}")

# Method 2: XOR values
chars_xor = []
for ar in asymmetric_rows:
    ch = chr(abs(ar["xor"])) if 32 <= abs(ar["xor"]) <= 126 else '.'
    chars_xor.append(ch)

print(f"  Method 2 (XOR values): {''.join(chars_xor)}")

# Method 3: Sum as message
chars_sum = []
for ar in asymmetric_rows:
    ch = chr(abs(ar["sum"])) if 32 <= abs(ar["sum"]) <= 126 else '.'
    chars_sum.append(ch)

print(f"  Method 3 (Sum values): {''.join(chars_sum)}")

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("🔥 COLUMN 22↔105 ANALYSIS COMPLETE 🔥")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         COLUMN 22↔105 FINDINGS                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  STRUCTURE:                                                                   ║
║  • 13 asymmetric rows (second largest hotspot)                               ║
║  • Asymmetric rows: {str(sorted(asym_22_105_rows))[:50]:50}║
║                                                                               ║
║  SPECIAL POSITION [22,22]:                                                   ║
║  • Value = {val_22_22} (on main diagonal)                                          ║
║  • Part of XOR Triangle: 100 ⊕ 27 = 127                                      ║
║                                                                               ║
║  WORDS FOUND:                                                                 ║
║  • 3+ letter words: {len(words)} words                                              ║
║  • Notable: {str(words[:5])[:50]:50}║
║                                                                               ║
║  COMPARISON WITH COL30⊕97:                                                   ║
║  • Matching XOR values: {matching}/128 ({matching/128*100:.1f}%)                                  ║
║  • Common words: {str(common_words)[:40]:40}     ║
║  • Row overlap: {str(sorted(overlap))[:40] if overlap else 'None':40}     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "xor_string": xor_string,
    "asymmetric_rows": asymmetric_rows,
    "words_found": words,
    "position_22_22": {
        "value": val_22_22,
        "partner_value": val_105_105,
        "is_symmetric": val_22_22 + val_105_105 == -1,
        "xor_triangle_member": val_22_22 == 100,
    },
    "comparison_with_30_97": {
        "matching_values": matching,
        "common_words": list(common_words),
        "row_overlap": list(overlap),
    },
}

output_path = script_dir / "COLUMN_22_105_ANALYSIS_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"✓ Results saved: {output_path}")
