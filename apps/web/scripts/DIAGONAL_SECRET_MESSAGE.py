#!/usr/bin/env python3
"""
===============================================================================
        DIAGONAL SECRET MESSAGE EXTRACTION
===============================================================================
The positions (0,0)='D', (127,127)='C', (63,63)='E' suggest a diagonal message!
Let's extract the FULL diagonal and anti-diagonal messages.
===============================================================================
"""

import json
import numpy as np
from pathlib import Path

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   ██████╗ ██╗ █████╗  ██████╗  ██████╗ ███╗   ██╗ █████╗ ██╗
   ██╔══██╗██║██╔══██╗██╔════╝ ██╔═══██╗████╗  ██║██╔══██╗██║
   ██║  ██║██║███████║██║  ███╗██║   ██║██╔██╗ ██║███████║██║
   ██║  ██║██║██╔══██║██║   ██║██║   ██║██║╚██╗██║██╔══██║██║
   ██████╔╝██║██║  ██║╚██████╔╝╚██████╔╝██║ ╚████║██║  ██║███████╗
   ╚═════╝ ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
                    DIAGONAL SECRET MESSAGE
""")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# MAIN DIAGONAL (r = c)
# ==============================================================================
print("\n" + "=" * 80)
print("MAIN DIAGONAL (r = c): from (0,0) to (127,127)")
print("=" * 80)

main_diag = [int(matrix[i, i]) for i in range(128)]
main_diag_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in main_diag)

print(f"\n  Raw values (first 20): {main_diag[:20]}")
print(f"\n  As ASCII: {main_diag_ascii}")

# Find printable sequences
print("\n  Printable sequences (3+ chars):")
current = ""
sequences = []
for i, v in enumerate(main_diag):
    if 32 <= abs(v) <= 126:
        current += chr(abs(v))
    else:
        if len(current) >= 3:
            sequences.append((i - len(current), current))
        current = ""
if len(current) >= 3:
    sequences.append((128 - len(current), current))

for pos, seq in sequences:
    print(f"    Position {pos}: '{seq}'")

# ==============================================================================
# ANTI-DIAGONAL (r + c = 127)
# ==============================================================================
print("\n" + "=" * 80)
print("ANTI-DIAGONAL (r + c = 127): from (0,127) to (127,0)")
print("=" * 80)

anti_diag = [int(matrix[i, 127-i]) for i in range(128)]
anti_diag_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in anti_diag)

print(f"\n  Raw values (first 20): {anti_diag[:20]}")
print(f"\n  As ASCII: {anti_diag_ascii}")

# Find printable sequences
print("\n  Printable sequences (3+ chars):")
current = ""
sequences = []
for i, v in enumerate(anti_diag):
    if 32 <= abs(v) <= 126:
        current += chr(abs(v))
    else:
        if len(current) >= 3:
            sequences.append((i - len(current), current))
        current = ""
if len(current) >= 3:
    sequences.append((128 - len(current), current))

for pos, seq in sequences:
    print(f"    Position {pos}: '{seq}'")

# ==============================================================================
# XOR DIAGONALS
# ==============================================================================
print("\n" + "=" * 80)
print("XOR OF DIAGONALS")
print("=" * 80)

xor_diag = [main_diag[i] ^ anti_diag[i] for i in range(128)]
xor_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in xor_diag)

print(f"\n  Main ⊕ Anti diagonal:")
print(f"  {xor_ascii}")

# ==============================================================================
# CORNER VALUES
# ==============================================================================
print("\n" + "=" * 80)
print("CORNER VALUES - THE FRAME OF THE MATRIX")
print("=" * 80)

corners = [
    ((0, 0), "Top-Left"),
    ((0, 127), "Top-Right"),
    ((127, 0), "Bottom-Left"),
    ((127, 127), "Bottom-Right"),
]

print("\n  The 4 corners:")
corner_message = ""
for (r, c), name in corners:
    val = int(matrix[r, c])
    char = chr(abs(val)) if 32 <= abs(val) <= 126 else '?'
    corner_message += char
    print(f"    {name} ({r},{c}): {val} = '{char}'")

print(f"\n  Corner message: '{corner_message}'")

# ==============================================================================
# EDGES - TOP ROW, BOTTOM ROW, LEFT COL, RIGHT COL
# ==============================================================================
print("\n" + "=" * 80)
print("EDGE MESSAGES")
print("=" * 80)

# Top row
top_row = [int(matrix[0, c]) for c in range(128)]
top_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in top_row)
print(f"\n  Top row (row 0):")
print(f"    {top_ascii}")

# Bottom row
bottom_row = [int(matrix[127, c]) for c in range(128)]
bottom_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in bottom_row)
print(f"\n  Bottom row (row 127):")
print(f"    {bottom_ascii}")

# Left column
left_col = [int(matrix[r, 0]) for r in range(128)]
left_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in left_col)
print(f"\n  Left column (col 0):")
print(f"    {left_ascii}")

# Right column
right_col = [int(matrix[r, 127]) for r in range(128)]
right_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in right_col)
print(f"\n  Right column (col 127):")
print(f"    {right_ascii}")

# ==============================================================================
# CENTER CROSS
# ==============================================================================
print("\n" + "=" * 80)
print("CENTER CROSS (Row 63 and Column 63)")
print("=" * 80)

row63 = [int(matrix[63, c]) for c in range(128)]
row63_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in row63)
print(f"\n  Row 63 (horizontal center):")
print(f"    {row63_ascii}")

col63 = [int(matrix[r, 63]) for r in range(128)]
col63_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in col63)
print(f"\n  Column 63 (vertical center):")
print(f"    {col63_ascii}")

# ==============================================================================
# SPECIAL: EXTRACT ONLY THE 127-VALUES DIAGONAL NEIGHBORS
# ==============================================================================
print("\n" + "=" * 80)
print("DIAGONAL NEIGHBORS OF 127-CELLS")
print("=" * 80)

bridge_cells = [
    (17, 76), (20, 78), (20, 120), (21, 15),
    (42, 63), (51, 51), (57, 124), (81, 108),
]

print("\n  Diagonal neighbors of each 127-cell:")
for r, c in bridge_cells:
    neighbors = []
    # Diagonal positions
    for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 128 and 0 <= nc < 128:
            val = int(matrix[nr, nc])
            char = chr(abs(val)) if 32 <= abs(val) <= 126 else '?'
            neighbors.append(f"{val}({char})")
    print(f"    ({r},{c}): {neighbors}")

# ==============================================================================
# THE 42 ROW (ANSWER TO EVERYTHING)
# ==============================================================================
print("\n" + "=" * 80)
print("ROW 42 - THE ANSWER TO LIFE, UNIVERSE, AND EVERYTHING")
print("=" * 80)

row42 = [int(matrix[42, c]) for c in range(128)]
row42_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in row42)
print(f"\n  Row 42 as ASCII:")
print(f"    {row42_ascii}")

# XOR with partner row 85
row85 = [int(matrix[85, c]) for c in range(128)]
xor_42_85 = [row42[i] ^ row85[i] for i in range(128)]
xor_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in xor_42_85)
print(f"\n  Row 42 ⊕ Row 85:")
print(f"    {xor_ascii}")

# ==============================================================================
# COLUMN 42 (FOR GOOD MEASURE)
# ==============================================================================
print("\n" + "=" * 80)
print("COLUMN 42")
print("=" * 80)

col42 = [int(matrix[r, 42]) for r in range(128)]
col42_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in col42)
print(f"\n  Column 42 as ASCII:")
print(f"    {col42_ascii}")

# ==============================================================================
# SPIRAL READ FROM CENTER
# ==============================================================================
print("\n" + "=" * 80)
print("SPIRAL READ FROM CENTER (63,63)")
print("=" * 80)

def spiral_from_center(matrix, cx, cy, steps=50):
    """Read values in a spiral pattern from center"""
    values = []
    x, y = cx, cy
    dx, dy = 0, -1  # Start going up
    steps_in_direction = 1
    steps_taken = 0
    direction_changes = 0

    for _ in range(steps):
        if 0 <= x < 128 and 0 <= y < 128:
            values.append(int(matrix[y, x]))

        # Move
        x += dx
        y += dy
        steps_taken += 1

        # Check if we need to turn
        if steps_taken == steps_in_direction:
            steps_taken = 0
            direction_changes += 1

            # Turn right (clockwise)
            dx, dy = -dy, dx

            # Increase steps every 2 turns
            if direction_changes % 2 == 0:
                steps_in_direction += 1

    return values

spiral = spiral_from_center(matrix, 63, 63, 100)
spiral_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in spiral)
print(f"\n  First 100 values in spiral from center:")
print(f"    {spiral_ascii}")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("DIAGONAL ANALYSIS SUMMARY")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    DIAGONAL MESSAGE FINDINGS                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  CORNERS: '{corner_message}'                                                  ║
║    (0,0)='D', (0,127)='<', (127,0)='=', (127,127)='C'                         ║
║                                                                               ║
║  MAIN DIAGONAL: Contains scattered letters                                    ║
║    Key characters at specific positions                                       ║
║                                                                               ║
║  ROW 42: The "Answer" row                                                     ║
║    Contains potential message when XORed                                      ║
║                                                                               ║
║  CENTER (63,63) = 'E'                                                         ║
║    Energy? Entry? The key position                                            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")
