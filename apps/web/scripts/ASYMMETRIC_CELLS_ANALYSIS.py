#!/usr/bin/env python3
"""
===============================================================================
        ASYMMETRIC CELLS ANALYSIS - The 68 Exceptions
===============================================================================
The Anna Matrix has 99.58% point symmetry:
  matrix[r,c] + matrix[127-r, 127-c] = -1  (for 99.58% of cells)

That means ~68 cells BREAK this rule. These are the ONLY cells that carry
information beyond the symmetry constraint. Everything else is determined
by the symmetry rule once you know half the matrix.

KEY QUESTIONS:
  Q1: Which cells are asymmetric? What are their coordinates?
  Q2: Is there a spatial pattern? (clusters, diagonals, specific rows/cols?)
  Q3: What values do they hold? How far do they deviate from the symmetry rule?
  Q4: Do they correspond to known functional addresses (POCC, HASV, etc.)?
  Q5: If symmetry constrains 99.58%, how much FREE information does the matrix carry?

INFORMATION THEORY:
  A fully symmetric matrix has N*N/2 free parameters (half determines the other).
  The asymmetric cells are ADDITIONAL free parameters beyond the symmetry.
  They may encode the actual "message" or "function" of the matrix.
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from datetime import datetime

script_dir = Path(__file__).parent

print("=" * 80)
print("         ASYMMETRIC CELLS ANALYSIS")
print("         The 68 Exceptions")
print("=" * 80)
print(f"\nDate: {datetime.now().isoformat()}")

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]], dtype=np.int16)
print(f"Matrix loaded: {matrix.shape}")

# ============================================================================
# PHASE 1: Find ALL Asymmetric Cells
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 1: Locating Asymmetric Cells")
print("=" * 80)

asymmetric_cells = []
symmetric_count = 0
total_cells = 128 * 128

for r in range(128):
    for c in range(128):
        mirror_r = 127 - r
        mirror_c = 127 - c
        val = int(matrix[r, c])
        mirror_val = int(matrix[mirror_r, mirror_c])
        expected_sum = -1

        actual_sum = val + mirror_val

        if actual_sum != expected_sum:
            deviation = actual_sum - expected_sum
            asymmetric_cells.append({
                'row': r,
                'col': c,
                'value': val,
                'mirror_row': mirror_r,
                'mirror_col': mirror_c,
                'mirror_value': mirror_val,
                'sum': actual_sum,
                'deviation': deviation,
            })
        else:
            symmetric_count += 1

# Note: each asymmetric pair is counted TWICE (r,c) and (mirror_r, mirror_c)
# So the actual unique asymmetric PAIRS is len(asymmetric_cells) / 2
n_asym = len(asymmetric_cells)
n_asym_pairs = n_asym // 2
symmetry_pct = symmetric_count / total_cells * 100

print(f"\n  Total cells: {total_cells}")
print(f"  Symmetric cells: {symmetric_count} ({symmetry_pct:.2f}%)")
print(f"  Asymmetric cells: {n_asym} ({n_asym/total_cells*100:.2f}%)")
print(f"  Unique asymmetric PAIRS: {n_asym_pairs}")

# ============================================================================
# PHASE 2: Catalog All Asymmetric Cells
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 2: Asymmetric Cell Catalog")
print("=" * 80)

# Only show each pair once (r <= mirror_r to avoid duplicates)
unique_pairs = []
seen = set()
for cell in asymmetric_cells:
    r, c = cell['row'], cell['col']
    mr, mc = cell['mirror_row'], cell['mirror_col']
    key = (min(r, mr), min(c, mc), max(r, mr), max(c, mc))
    if key not in seen:
        seen.add(key)
        unique_pairs.append(cell)

print(f"\n  {'Row':<5} {'Col':<5} {'Value':<8} {'MirrorR':<8} {'MirrorC':<8} {'MirVal':<8} {'Sum':<6} {'Dev':<6}")
print("  " + "-" * 60)
for cell in sorted(unique_pairs, key=lambda x: (x['row'], x['col'])):
    print(f"  {cell['row']:<5} {cell['col']:<5} {cell['value']:<8} {cell['mirror_row']:<8} {cell['mirror_col']:<8} {cell['mirror_value']:<8} {cell['sum']:<6} {cell['deviation']:<6}")

# ============================================================================
# PHASE 3: Spatial Pattern Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 3: Spatial Pattern Analysis")
print("=" * 80)

# Which rows contain asymmetric cells?
asym_rows = Counter(cell['row'] for cell in asymmetric_cells)
asym_cols = Counter(cell['col'] for cell in asymmetric_cells)

print(f"\n  Rows containing asymmetric cells: {len(asym_rows)}")
print(f"  Columns containing asymmetric cells: {len(asym_cols)}")

print(f"\n  Row distribution:")
for row in sorted(asym_rows.keys()):
    print(f"    Row {row:>3}: {asym_rows[row]} asymmetric cells")

print(f"\n  Column distribution:")
for col in sorted(asym_cols.keys()):
    print(f"    Col {col:>3}: {asym_cols[col]} asymmetric cells")

# Check if asymmetric cells cluster
# Are they on specific diagonals?
asym_diag_main = sum(1 for c in asymmetric_cells if c['row'] == c['col'])
asym_diag_anti = sum(1 for c in asymmetric_cells if c['row'] + c['col'] == 127)
print(f"\n  On main diagonal (r==c): {asym_diag_main}")
print(f"  On anti-diagonal (r+c==127): {asym_diag_anti}")

# Check center region vs edges
center_cells = sum(1 for c in asymmetric_cells if 32 <= c['row'] <= 95 and 32 <= c['col'] <= 95)
edge_cells = n_asym - center_cells
print(f"  In center region (32-95): {center_cells}")
print(f"  In edge region: {edge_cells}")

# Check if any are on the center point (63,64) or (64,63)
center_asym = [c for c in asymmetric_cells if (c['row'] == 63 and c['col'] == 64) or (c['row'] == 64 and c['col'] == 63)]
print(f"  At matrix center (63/64): {len(center_asym)}")

# Check for row/column pairs summing to 127
asym_row_set = set(asym_rows.keys())
print(f"\n  Row pairs analysis:")
for r in sorted(asym_row_set):
    if r < 64 and (127 - r) in asym_row_set:
        print(f"    Pair ({r}, {127-r}): {asym_rows[r]} + {asym_rows[127-r]} cells")

# ============================================================================
# PHASE 4: Value Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 4: Value Analysis")
print("=" * 80)

deviations = [cell['deviation'] for cell in asymmetric_cells]
values = [cell['value'] for cell in asymmetric_cells]
sums = [cell['sum'] for cell in asymmetric_cells]

print(f"\n  Deviation from -1 rule:")
print(f"    Values: {sorted(set(deviations))}")
print(f"    Distribution: {dict(Counter(deviations))}")

print(f"\n  Actual sums (should be -1):")
print(f"    Values: {sorted(set(sums))}")
print(f"    Distribution: {dict(Counter(sums))}")

print(f"\n  Cell values at asymmetric positions:")
print(f"    Range: [{min(values)}, {max(values)}]")
print(f"    Mean: {np.mean(values):.2f}")
print(f"    Distribution of values: {dict(Counter(values))}")

# ============================================================================
# PHASE 5: Information Theory
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 5: Information Content")
print("=" * 80)

# How much FREE information does the matrix carry?
# If perfectly symmetric: 128*128/2 = 8192 free cells (other half determined)
# Each cell: 8 bits (values -128 to 127)
# Symmetric matrix: 8192 * 8 = 65,536 bits of free information
# Plus: n_asym_pairs additional free cells (their mirrors are NOT determined by symmetry)

total_free_cells = (128 * 128) // 2  # Half matrix
extra_from_asymmetry = n_asym_pairs  # Additional free parameters
total_free_info_bits = total_free_cells * 8 + extra_from_asymmetry * 8

print(f"\n  Symmetric half: {total_free_cells} free cells x 8 bits = {total_free_cells * 8} bits")
print(f"  Asymmetric extras: {n_asym_pairs} pairs x 8 bits = {n_asym_pairs * 8} bits")
print(f"  Total free information: {total_free_info_bits} bits ({total_free_info_bits / 8} bytes)")
print(f"  Asymmetric contribution: {n_asym_pairs * 8 / total_free_info_bits * 100:.3f}% of total info")

# What could the asymmetric cells encode?
print(f"\n  Encoding capacity of asymmetric cells alone:")
print(f"    {n_asym_pairs} cells x 8 bits = {n_asym_pairs * 8} bits = {n_asym_pairs} bytes")
print(f"    Could encode: ~{n_asym_pairs} ASCII characters")
print(f"    Or: a {n_asym_pairs * 8}-bit number")

# Try to decode as ASCII
asym_values_ordered = [cell['value'] for cell in sorted(unique_pairs, key=lambda x: (x['row'], x['col']))]
ascii_attempt = ""
for v in asym_values_ordered:
    if 32 <= v <= 126:
        ascii_attempt += chr(v)
    elif 32 <= (v % 128) <= 126:
        ascii_attempt += chr(v % 128)
    else:
        ascii_attempt += "."

print(f"\n  ASCII decode attempt (raw values): {ascii_attempt}")
print(f"  Values as unsigned bytes: {[v & 0xFF for v in asym_values_ordered]}")

# ============================================================================
# PHASE 6: Relationship to Known Addresses
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 6: Known Address Mapping")
print("=" * 80)

# Check if any asymmetric cells map to known strategic coordinates
strategic_nodes = {
    'ENTRY': (45, 92),
    'CORE': (6, 33),
    'EXIT': (82, 39),
    'ORACLE': (11, 110),
    'VOID': (0, 0),
    'GUARDIAN': (19, 18),
    'ROOT_ALPHA': (13, 71),
    'ROOT_BETA': (18, 110),
    'MEMORY': (21, 21),
    'VISION': (64, 64),
    'DATE': (3, 3),
}

asym_coords = set((c['row'], c['col']) for c in asymmetric_cells)

print(f"\n  Strategic nodes at asymmetric positions:")
for name, (r, c) in strategic_nodes.items():
    is_asym = (r, c) in asym_coords
    val = int(matrix[r, c])
    mirror_r, mirror_c = 127 - r, 127 - c
    mirror_val = int(matrix[mirror_r, mirror_c])
    s = val + mirror_val
    print(f"    {name:<15} ({r:>3},{c:>3}): value={val:>5}, mirror=({mirror_r},{mirror_c})={mirror_val:>5}, sum={s:>4} {'<-- ASYMMETRIC' if is_asym else ''}")

# Check POCC/HASV addresses
POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def char_val(c):
    return ord(c.upper()) - ord('A')

print(f"\n  POCC address character positions at asymmetric cells:")
pocc_asym_hits = 0
for i, c in enumerate(POCC):
    v = char_val(c)
    if (v, i % 128) in asym_coords or (i % 128, v) in asym_coords:
        pocc_asym_hits += 1
print(f"    POCC hits: {pocc_asym_hits} / {len(POCC)}")

hasv_asym_hits = 0
for i, c in enumerate(HASV):
    v = char_val(c)
    if (v, i % 128) in asym_coords or (i % 128, v) in asym_coords:
        hasv_asym_hits += 1
print(f"    HASV hits: {hasv_asym_hits} / {len(HASV)}")

# ============================================================================
# PHASE 7: Functional Hypothesis - Weight Perturbation
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 7: Neural Network Interpretation")
print("=" * 80)

# In the Aigarth system, the matrix provides WEIGHTS for neurons
# Perfect symmetry means: weight(i→j) is determined by weight(127-i → 127-j)
# Asymmetric cells are where this relationship BREAKS
# This could mean: specific neural connections were INDIVIDUALLY TUNED

print(f"\n  Neural network interpretation:")
print(f"    Total synaptic weights: {total_cells}")
print(f"    Weights determined by symmetry: {symmetric_count} ({symmetry_pct:.2f}%)")
print(f"    Individually tuned weights: {n_asym} ({n_asym/total_cells*100:.2f}%)")
print(f"")
print(f"    The symmetry provides the BASE architecture (balanced excitatory/inhibitory).")
print(f"    The {n_asym} asymmetric weights are SPECIFIC CORRECTIONS to this base.")
print(f"    These are the weights that evolutionary training found NEEDED to differ")
print(f"    from what the symmetry rule would dictate.")

# Check: are the deviations small (fine-tuning) or large (major corrections)?
abs_devs = [abs(d) for d in deviations]
print(f"\n  Deviation magnitudes:")
print(f"    Mean absolute deviation: {np.mean(abs_devs):.2f}")
print(f"    Max deviation: {max(abs_devs)}")
print(f"    Min deviation: {min(abs_devs)}")
print(f"    All deviations: {sorted(set(deviations))}")

if max(abs_devs) <= 2:
    print(f"\n  INTERPRETATION: Small deviations suggest FINE-TUNING of an otherwise symmetric design.")
    print(f"  The base symmetric architecture was designed first, then specific weights were adjusted.")
elif max(abs_devs) > 10:
    print(f"\n  INTERPRETATION: Large deviations suggest these positions serve a DIFFERENT PURPOSE")
    print(f"  than the symmetric base. They may encode information orthogonal to the neural function.")
else:
    print(f"\n  INTERPRETATION: Mixed deviation sizes suggest both fine-tuning and")
    print(f"  deliberate structural exceptions.")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("ASYMMETRIC CELLS ANALYSIS SUMMARY")
print("=" * 80)

print(f"\n  Total asymmetric cells: {n_asym} ({n_asym/total_cells*100:.2f}% of matrix)")
print(f"  Unique asymmetric pairs: {n_asym_pairs}")
print(f"  Rows affected: {len(asym_rows)}")
print(f"  Columns affected: {len(asym_cols)}")
print(f"  Information content: {n_asym_pairs * 8} extra bits beyond symmetry")
print(f"  Deviation range: {sorted(set(deviations))}")

# Save results
results = {
    "date": datetime.now().isoformat(),
    "total_cells": total_cells,
    "symmetric_count": symmetric_count,
    "asymmetric_count": n_asym,
    "asymmetric_pairs": n_asym_pairs,
    "symmetry_percentage": float(symmetry_pct),
    "asymmetric_cells": [
        {
            "row": c["row"],
            "col": c["col"],
            "value": c["value"],
            "mirror_row": c["mirror_row"],
            "mirror_col": c["mirror_col"],
            "mirror_value": c["mirror_value"],
            "sum": c["sum"],
            "deviation": c["deviation"],
        }
        for c in sorted(unique_pairs, key=lambda x: (x['row'], x['col']))
    ],
    "affected_rows": sorted(asym_rows.keys()),
    "affected_cols": sorted(asym_cols.keys()),
    "deviations": dict(Counter(deviations)),
    "strategic_node_hits": {
        name: (r, c) in asym_coords
        for name, (r, c) in strategic_nodes.items()
    },
}

output_path = script_dir / "ASYMMETRIC_CELLS_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n  Results saved to: {output_path}")
