#!/usr/bin/env python3
"""
===============================================================================
            BLOCK PATTERN ANALYSIS - PURE DATA
===============================================================================
Divide matrix into blocks and analyze properties.
NO interpretation - only statistics and comparisons.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent

print("=" * 80)
print("           BLOCK PATTERN ANALYSIS")
print("           Analyzing 8x8 and 16x16 blocks")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# 8x8 BLOCK ANALYSIS (16x16 = 256 blocks)
# ==============================================================================
print("\n" + "=" * 80)
print("8x8 BLOCK ANALYSIS")
print("=" * 80)

blocks_8x8 = []

for br in range(16):
    for bc in range(16):
        block = matrix[br*8:(br+1)*8, bc*8:(bc+1)*8]

        # Statistics
        block_sum = int(np.sum(block))
        block_mean = float(np.mean(block))
        block_std = float(np.std(block))
        block_min = int(np.min(block))
        block_max = int(np.max(block))

        # Check symmetry within block
        symmetric_cells = 0
        for r in range(4):
            for c in range(8):
                if block[r, c] + block[7-r, 7-c] == -1:
                    symmetric_cells += 1

        blocks_8x8.append({
            "block_row": br,
            "block_col": bc,
            "sum": block_sum,
            "mean": block_mean,
            "std": block_std,
            "min": block_min,
            "max": block_max,
            "internal_symmetry": symmetric_cells,
        })

# Find outlier blocks
mean_sum = np.mean([b["sum"] for b in blocks_8x8])
std_sum = np.std([b["sum"] for b in blocks_8x8])

outlier_blocks = [b for b in blocks_8x8 if abs(b["sum"] - mean_sum) > 2 * std_sum]

print(f"\n  Total 8x8 blocks: {len(blocks_8x8)}")
print(f"  Sum statistics: mean={mean_sum:.1f}, std={std_sum:.1f}")
print(f"  Outlier blocks (|sum - mean| > 2σ): {len(outlier_blocks)}")

for b in outlier_blocks:
    z = (b["sum"] - mean_sum) / std_sum
    print(f"    Block [{b['block_row']},{b['block_col']}]: sum={b['sum']}, z={z:.2f}")

# ==============================================================================
# BLOCK SYMMETRY ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("BLOCK PAIR SYMMETRY")
print("=" * 80)

# Check if block[br,bc] is symmetric partner to block[15-br,15-bc]
block_pair_symmetry = []

for br in range(8):
    for bc in range(16):
        block1 = matrix[br*8:(br+1)*8, bc*8:(bc+1)*8]
        partner_br = 15 - br
        partner_bc = 15 - bc
        block2 = matrix[partner_br*8:(partner_br+1)*8, partner_bc*8:(partner_bc+1)*8]

        # Count symmetric cell pairs
        sym_count = 0
        for r in range(8):
            for c in range(8):
                if block1[r, c] + block2[7-r, 7-c] == -1:
                    sym_count += 1

        block_pair_symmetry.append({
            "block1": (br, bc),
            "block2": (partner_br, partner_bc),
            "symmetric_cells": sym_count,
            "symmetry_pct": sym_count / 64 * 100,
        })

# Statistics
sym_pcts = [b["symmetry_pct"] for b in block_pair_symmetry]
print(f"\n  Block pair symmetry statistics:")
print(f"    Mean: {np.mean(sym_pcts):.2f}%")
print(f"    Min: {np.min(sym_pcts):.2f}%")
print(f"    Max: {np.max(sym_pcts):.2f}%")

# Blocks with less than 100% symmetry
asymmetric_blocks = [b for b in block_pair_symmetry if b["symmetry_pct"] < 100]
print(f"\n  Block pairs with <100% symmetry: {len(asymmetric_blocks)}")

for b in sorted(asymmetric_blocks, key=lambda x: x["symmetry_pct"])[:10]:
    print(f"    Blocks {b['block1']}↔{b['block2']}: {b['symmetry_pct']:.1f}% symmetric")

# ==============================================================================
# 16x16 BLOCK ANALYSIS (8x8 = 64 blocks)
# ==============================================================================
print("\n" + "=" * 80)
print("16x16 BLOCK ANALYSIS")
print("=" * 80)

blocks_16x16 = []

for br in range(8):
    for bc in range(8):
        block = matrix[br*16:(br+1)*16, bc*16:(bc+1)*16]

        block_sum = int(np.sum(block))
        block_mean = float(np.mean(block))
        block_std = float(np.std(block))

        blocks_16x16.append({
            "block_row": br,
            "block_col": bc,
            "sum": block_sum,
            "mean": block_mean,
            "std": block_std,
        })

# Heatmap of sums
print(f"\n  16x16 Block Sums Heatmap:")
print("       " + "".join(f"{c:8}" for c in range(8)))
for br in range(8):
    row_sums = [b["sum"] for b in blocks_16x16 if b["block_row"] == br]
    print(f"  {br}:  " + "".join(f"{s:8}" for s in row_sums))

# ==============================================================================
# DIAGONAL BLOCK ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("DIAGONAL BLOCKS (8x8)")
print("=" * 80)

diagonal_blocks = [b for b in blocks_8x8 if b["block_row"] == b["block_col"]]
anti_diagonal_blocks = [b for b in blocks_8x8 if b["block_row"] + b["block_col"] == 15]

print(f"\n  Main diagonal blocks (br == bc):")
for b in diagonal_blocks:
    print(f"    Block [{b['block_row']},{b['block_col']}]: sum={b['sum']:5}, mean={b['mean']:6.1f}, std={b['std']:5.1f}")

print(f"\n  Anti-diagonal blocks (br + bc == 15):")
for b in anti_diagonal_blocks:
    print(f"    Block [{b['block_row']},{b['block_col']}]: sum={b['sum']:5}, mean={b['mean']:6.1f}, std={b['std']:5.1f}")

# ==============================================================================
# STRING CELL BLOCK DISTRIBUTION
# ==============================================================================
print("\n" + "=" * 80)
print("STRING CELLS BY BLOCK")
print("=" * 80)

# Load raw matrix to find string cells
raw_matrix = data["matrix"]
string_cells_by_block = {}

for r in range(128):
    for c in range(128):
        if isinstance(raw_matrix[r][c], str):
            br, bc = r // 8, c // 8
            key = (br, bc)
            if key not in string_cells_by_block:
                string_cells_by_block[key] = 0
            string_cells_by_block[key] += 1

print(f"\n  Blocks containing string cells:")
for (br, bc), count in sorted(string_cells_by_block.items()):
    print(f"    Block [{br},{bc}]: {count} string cells")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("BLOCK ANALYSIS COMPLETE")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         BLOCK ANALYSIS SUMMARY                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  8x8 BLOCKS:                                                                  ║
║  • Total: 256 blocks                                                          ║
║  • Outlier blocks (>2σ): {len(outlier_blocks):2}                                              ║
║  • Block pairs with <100% symmetry: {len(asymmetric_blocks):2}                               ║
║                                                                               ║
║  16x16 BLOCKS:                                                                ║
║  • Total: 64 blocks                                                           ║
║                                                                               ║
║  STRING CELLS:                                                                ║
║  • Blocks with strings: {len(string_cells_by_block):2}                                              ║
║  • Total string cells: {sum(string_cells_by_block.values()):2}                                              ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "blocks_8x8": {
        "total": len(blocks_8x8),
        "outliers": outlier_blocks,
        "asymmetric_block_pairs": asymmetric_blocks,
    },
    "blocks_16x16": blocks_16x16,
    "diagonal_blocks": diagonal_blocks,
    "string_cells_by_block": {f"{k[0]},{k[1]}": v for k, v in string_cells_by_block.items()},
}

output_path = script_dir / "BLOCK_ANALYSIS_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"✓ Results saved: {output_path}")
