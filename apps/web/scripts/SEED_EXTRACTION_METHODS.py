#!/usr/bin/env python3
"""
===============================================================================
            SEED EXTRACTION METHODS
===============================================================================
Try multiple methods to extract potential 55-char Qubic seeds from the matrix.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import hashlib

script_dir = Path(__file__).parent

print("=" * 80)
print("           SEED EXTRACTION METHODS")
print("           Trying multiple extraction approaches")
print("=" * 80)

matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

def to_seed_char(val):
    """Convert value to lowercase a-z, or empty if not possible"""
    val = abs(int(val))
    # Method 1: Direct ASCII if in range
    if 97 <= val <= 122:
        return chr(val)
    # Method 2: Mod 26 + 'a'
    return chr((val % 26) + ord('a'))

def extract_55(values, method="direct"):
    """Extract 55 lowercase chars from values"""
    if method == "direct":
        # Only use values that are already lowercase ASCII
        chars = [chr(abs(v)) for v in values if 97 <= abs(v) <= 122]
    elif method == "mod26":
        # Use mod 26 for all values
        chars = [chr((abs(v) % 26) + ord('a')) for v in values]
    elif method == "abs_mod26":
        # Use absolute value mod 26
        chars = [chr((abs(v) % 26) + ord('a')) for v in values]

    return ''.join(chars[:55])

candidates = []

# ==============================================================================
# METHOD 1: Key rows with palindromes
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 1: KEY ROWS (palindrome locations)")
print("=" * 80)

key_rows = [15, 112, 7, 120, 6, 121, 12, 115]
for r in key_rows[:4]:
    row = [int(matrix[r, c]) for c in range(128)]
    seed_direct = extract_55(row, "direct")
    seed_mod = extract_55(row, "mod26")

    print(f"\n  Row {r}:")
    print(f"    Direct: '{seed_direct[:55]}' ({len(seed_direct)} chars)")
    print(f"    Mod26:  '{seed_mod}'")

    if len(seed_direct) >= 55:
        candidates.append(("Row " + str(r) + " direct", seed_direct[:55]))
    candidates.append(("Row " + str(r) + " mod26", seed_mod))

# ==============================================================================
# METHOD 2: Key columns
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 2: KEY COLUMNS (AI.MEG, Mirror)")
print("=" * 80)

key_cols = [30, 97, 19, 108, 22, 105]
for c in key_cols[:4]:
    col = [int(matrix[r, c]) for r in range(128)]
    seed_direct = extract_55(col, "direct")
    seed_mod = extract_55(col, "mod26")

    print(f"\n  Col {c}:")
    print(f"    Direct: '{seed_direct[:55]}' ({len(seed_direct)} chars)")
    print(f"    Mod26:  '{seed_mod}'")

    candidates.append(("Col " + str(c) + " mod26", seed_mod))

# ==============================================================================
# METHOD 3: XOR of key pairs
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 3: XOR OF KEY PAIRS")
print("=" * 80)

xor_pairs = [
    ("Row 15⊕112", 15, 112, "row"),
    ("Row 7⊕120", 7, 120, "row"),
    ("Col 30⊕97", 30, 97, "col"),
    ("Col 19⊕108", 19, 108, "col"),
]

for name, idx1, idx2, ptype in xor_pairs:
    if ptype == "row":
        v1 = [int(matrix[idx1, c]) for c in range(128)]
        v2 = [int(matrix[idx2, c]) for c in range(128)]
    else:
        v1 = [int(matrix[r, idx1]) for r in range(128)]
        v2 = [int(matrix[r, idx2]) for r in range(128)]

    xor = [v1[i] ^ v2[i] for i in range(128)]
    seed_direct = extract_55(xor, "direct")
    seed_mod = extract_55(xor, "mod26")

    print(f"\n  {name}:")
    print(f"    Direct: '{seed_direct[:55]}' ({len(seed_direct)} chars)")
    print(f"    Mod26:  '{seed_mod}'")

    candidates.append((name + " mod26", seed_mod))

# ==============================================================================
# METHOD 4: Asymmetric cells only
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 4: ASYMMETRIC CELLS")
print("=" * 80)

asym_values = []
for r in range(128):
    for c in range(128):
        if matrix[r, c] + matrix[127-r, 127-c] != -1:
            asym_values.append(int(matrix[r, c]))

seed_asym = extract_55(asym_values, "mod26")
print(f"\n  From {len(asym_values)} asymmetric cells:")
print(f"    Mod26: '{seed_asym}'")
candidates.append(("Asymmetric mod26", seed_asym))

# ==============================================================================
# METHOD 5: Specific positions (row 42, col 42 - "The Answer")
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 5: POSITION 42 (The Answer)")
print("=" * 80)

row42 = [int(matrix[42, c]) for c in range(128)]
col42 = [int(matrix[r, 42]) for r in range(128)]

seed_r42 = extract_55(row42, "mod26")
seed_c42 = extract_55(col42, "mod26")

print(f"\n  Row 42: '{seed_r42}'")
print(f"  Col 42: '{seed_c42}'")

candidates.append(("Row 42 mod26", seed_r42))
candidates.append(("Col 42 mod26", seed_c42))

# ==============================================================================
# METHOD 6: First 55 values of specific patterns
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 6: FIRST 55 VALUES")
print("=" * 80)

# First row
first_row = [int(matrix[0, c]) for c in range(55)]
seed_first = ''.join(chr((abs(v) % 26) + ord('a')) for v in first_row)
print(f"\n  First row (0-54): '{seed_first}'")
candidates.append(("First row mod26", seed_first))

# Diagonal 0-54
diag_55 = [int(matrix[i, i]) for i in range(55)]
seed_diag = ''.join(chr((abs(v) % 26) + ord('a')) for v in diag_55)
print(f"  Diagonal (0-54): '{seed_diag}'")
candidates.append(("Diagonal mod26", seed_diag))

# ==============================================================================
# METHOD 7: Center region
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 7: CENTER REGION")
print("=" * 80)

# Extract from center (around 63,63)
center_values = []
for r in range(55, 72):
    for c in range(55, 72):
        center_values.append(int(matrix[r, c]))

seed_center = extract_55(center_values[:55], "mod26")
print(f"\n  Center region: '{seed_center}'")
candidates.append(("Center mod26", seed_center))

# ==============================================================================
# METHOD 8: Reading order (spiral, zigzag)
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 8: SPIRAL READING")
print("=" * 80)

# Simple spiral from center
def spiral_coords(n):
    """Generate spiral coordinates from center"""
    coords = []
    x, y = n // 2, n // 2
    coords.append((x, y))
    for layer in range(1, n // 2 + 1):
        # Right
        for i in range(layer * 2):
            x += 1
            if 0 <= x < n and 0 <= y < n:
                coords.append((x, y))
        # Down
        for i in range(layer * 2):
            y += 1
            if 0 <= x < n and 0 <= y < n:
                coords.append((x, y))
        # Left
        for i in range(layer * 2 + 1):
            x -= 1
            if 0 <= x < n and 0 <= y < n:
                coords.append((x, y))
        # Up
        for i in range(layer * 2 + 1):
            y -= 1
            if 0 <= x < n and 0 <= y < n:
                coords.append((x, y))
    return coords[:55]

spiral = spiral_coords(128)
spiral_values = [int(matrix[r, c]) for r, c in spiral]
seed_spiral = ''.join(chr((abs(v) % 26) + ord('a')) for v in spiral_values)
print(f"\n  Spiral from center: '{seed_spiral}'")
candidates.append(("Spiral mod26", seed_spiral))

# ==============================================================================
# VALIDATE ALL CANDIDATES
# ==============================================================================
print("\n" + "=" * 80)
print("ALL CANDIDATES")
print("=" * 80)

print(f"\n  {'Method':<30} {'Seed':<60}")
print("  " + "-" * 90)

unique_seeds = set()
for name, seed in candidates:
    if len(seed) == 55 and seed.isalpha() and seed.islower():
        unique_seeds.add(seed)
        # Hash for comparison
        h = hashlib.sha256(seed.encode()).hexdigest()[:8]
        print(f"  {name:<30} {seed} [{h}]")

print(f"\n  Unique valid seeds: {len(unique_seeds)}")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("SEED EXTRACTION COMPLETE")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         EXTRACTION SUMMARY                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  METHODS TRIED: 8                                                             ║
║  CANDIDATES GENERATED: {len(candidates):2}                                                 ║
║  UNIQUE VALID SEEDS (55 lowercase): {len(unique_seeds):2}                                  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save
results = {
    "timestamp": datetime.now().isoformat(),
    "candidates": [(name, seed) for name, seed in candidates],
    "unique_seeds": list(unique_seeds),
    "unique_count": len(unique_seeds),
}

with open(script_dir / "SEED_EXTRACTION_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"✓ Results saved")
