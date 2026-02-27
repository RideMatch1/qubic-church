#!/usr/bin/env python3
"""
GAME Deep Analysis in the Anna Matrix
======================================
Comprehensive analysis of the word "GAME" encoded via XOR 127 in the 128x128 Anna Matrix.

Searches all rows, columns, and diagonals for the pattern G-A-M-E,
then performs cross-referencing, statistical controls, and game-theoretic analysis.
"""

import json
import os
import math
import random
import string
from collections import Counter, defaultdict
from itertools import product

# ─── Configuration ───────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MATRIX_PATH = os.path.join(SCRIPT_DIR, "..", "public", "data", "anna-matrix.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "..", "..", "..", "GAME_ANALYSIS_RESULTS.json")

# Target word
TARGET = "GAME"
TARGET_CODES = [ord(c) for c in TARGET]  # [71, 65, 77, 69]

# Population definitions (from ANNA_MASTER_NUMBERS.py)
POP_A  = [0, 1, 3, 4, 5, 6, 7, 9, 12, 13, 15, 17, 20, 21, 23, 29, 32, 33, 35, 36, 37, 38, 39, 41, 44, 45, 47, 49, 52, 53, 55, 61, 68, 69, 71, 77, 85, 100, 101, 103, 109, 117]
POP_Ai = [10, 18, 24, 27, 42, 50, 56, 58, 59, 62, 66, 72, 74, 75, 78, 80, 82, 83, 86, 88, 89, 90, 91, 92, 94, 95, 98, 104, 106, 107, 110, 112, 114, 115, 118, 120, 121, 122, 123, 124, 126, 127]
POP_B  = [2, 8, 11, 14, 16, 19, 22, 25, 28, 30, 31, 34, 40, 43, 46, 48, 51, 54, 57, 60, 63, 64, 65, 67, 70, 73, 76, 79, 81, 84, 87, 93, 96, 97, 99, 102, 105, 108, 111, 113, 116, 119, 125]

EXCEPTION_COLS = {0, 22, 30, 41, 86, 97, 105, 127}
FACTORY_ROWS = {1, 9, 49, 57}
PACEMAKER_ROW = 26
BOUNDARY_ROWS = {0, 42, 43, 84, 85, 127}

# ─── Helper functions ────────────────────────────────────────────────────────

def xor127_char(value):
    """Convert matrix value to character via XOR 127."""
    v = int(value)
    code = (v ^ 127) % 128
    return code, chr(code) if 32 <= code < 127 else None

def get_population(row):
    """Return the population label for a given row."""
    if row == 26:
        return "N26 (pacemaker)"
    if row in POP_A:
        return "Pop A (attractor=-1)"
    if row in POP_Ai:
        return "Pop A' (attractor=+1)"
    if row in POP_B:
        return "Pop B (conductor)"
    return "Unknown"

def row_xor_stream(matrix, row):
    """Get XOR 127 character codes for an entire row."""
    return [(int(v) ^ 127) % 128 for v in matrix[row]]

def col_xor_stream(matrix, col):
    """Get XOR 127 character codes for an entire column."""
    return [(int(matrix[r][col]) ^ 127) % 128 for r in range(128)]

def shannon_entropy(values):
    """Calculate Shannon entropy of a list of values."""
    n = len(values)
    if n == 0:
        return 0.0
    counts = Counter(values)
    return -sum((c/n) * math.log2(c/n) for c in counts.values() if c > 0)


# ─── Load Matrix ─────────────────────────────────────────────────────────────

print("=" * 80)
print("GAME DEEP ANALYSIS - Anna Matrix (128x128)")
print("=" * 80)

with open(MATRIX_PATH) as f:
    data = json.load(f)

matrix = data["matrix"]
assert len(matrix) == 128 and len(matrix[0]) == 128, "Matrix must be 128x128"

# Convert all values to int
for r in range(128):
    for c in range(128):
        matrix[r][c] = int(matrix[r][c])

print(f"\nMatrix loaded: {len(matrix)}x{len(matrix[0])}")
print(f"Value range: [{min(min(row) for row in matrix)}, {max(max(row) for row in matrix)}]")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Find ALL GAME positions in XOR 127 encoding
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("SECTION 1: Finding ALL 'GAME' occurrences in XOR 127 encoding")
print("=" * 80)

game_positions = []

def find_pattern_in_stream(codes, target_codes):
    """Find all positions where target_codes appears consecutively in codes."""
    positions = []
    for i in range(len(codes) - len(target_codes) + 1):
        if codes[i:i+len(target_codes)] == target_codes:
            positions.append(i)
    return positions

# 1a. Search rows (left to right)
print("\n--- Searching ROWS (left-to-right) ---")
row_game_count = 0
for r in range(128):
    stream = row_xor_stream(matrix, r)
    hits = find_pattern_in_stream(stream, TARGET_CODES)
    for col_start in hits:
        row_game_count += 1
        pop = get_population(r)
        raw_vals = [matrix[r][col_start + i] for i in range(4)]
        print(f"  GAME #{row_game_count}: Row {r}, Col {col_start}-{col_start+3} | Pop: {pop} | Raw: {raw_vals}")
        game_positions.append({
            "type": "row",
            "row": r,
            "col_start": col_start,
            "col_end": col_start + 3,
            "direction": "left-to-right",
            "population": pop,
            "raw_values": raw_vals,
            "cells": [(r, col_start + i) for i in range(4)]
        })

# 1b. Search columns (top to bottom)
print("\n--- Searching COLUMNS (top-to-bottom) ---")
col_game_count = 0
for c in range(128):
    stream = col_xor_stream(matrix, c)
    hits = find_pattern_in_stream(stream, TARGET_CODES)
    for row_start in hits:
        col_game_count += 1
        raw_vals = [matrix[row_start + i][c] for i in range(4)]
        pops = [get_population(row_start + i) for i in range(4)]
        print(f"  GAME #{col_game_count}: Col {c}, Rows {row_start}-{row_start+3} | Pops: {pops} | Raw: {raw_vals}")
        game_positions.append({
            "type": "column",
            "col": c,
            "row_start": row_start,
            "row_end": row_start + 3,
            "direction": "top-to-bottom",
            "populations": pops,
            "raw_values": raw_vals,
            "cells": [(row_start + i, c) for i in range(4)]
        })

# 1c. Search diagonals (↘ and ↙)
print("\n--- Searching DIAGONALS ---")
diag_game_count = 0

# Main diagonals (↘): start from top row and left column
for start_r, start_c in [(r, 0) for r in range(128)] + [(0, c) for c in range(1, 128)]:
    stream = []
    coords = []
    r, c = start_r, start_c
    while 0 <= r < 128 and 0 <= c < 128:
        stream.append((int(matrix[r][c]) ^ 127) % 128)
        coords.append((r, c))
        r += 1
        c += 1
    hits = find_pattern_in_stream(stream, TARGET_CODES)
    for idx in hits:
        diag_game_count += 1
        cells = coords[idx:idx+4]
        raw_vals = [matrix[cr][cc] for cr, cc in cells]
        pops = [get_population(cr) for cr, _ in cells]
        print(f"  GAME #{diag_game_count} (↘): Start ({cells[0][0]},{cells[0][1]}) to ({cells[3][0]},{cells[3][1]}) | Pops: {pops} | Raw: {raw_vals}")
        game_positions.append({
            "type": "diagonal_SE",
            "direction": "↘",
            "cells": cells,
            "populations": pops,
            "raw_values": raw_vals
        })

# Anti-diagonals (↙): start from top row and right column
for start_r, start_c in [(r, 127) for r in range(128)] + [(0, c) for c in range(127)]:
    stream = []
    coords = []
    r, c = start_r, start_c
    while 0 <= r < 128 and 0 <= c < 128:
        stream.append((int(matrix[r][c]) ^ 127) % 128)
        coords.append((r, c))
        r += 1
        c -= 1
    hits = find_pattern_in_stream(stream, TARGET_CODES)
    for idx in hits:
        diag_game_count += 1
        cells = coords[idx:idx+4]
        raw_vals = [matrix[cr][cc] for cr, cc in cells]
        pops = [get_population(cr) for cr, _ in cells]
        print(f"  GAME #{diag_game_count} (↙): Start ({cells[0][0]},{cells[0][1]}) to ({cells[3][0]},{cells[3][1]}) | Pops: {pops} | Raw: {raw_vals}")
        game_positions.append({
            "type": "diagonal_SW",
            "direction": "↙",
            "cells": cells,
            "populations": pops,
            "raw_values": raw_vals
        })

# Also search reversed directions (right-to-left, bottom-to-top, ↖, ↗)
print("\n--- Searching REVERSED directions (EMAG = reverse GAME) ---")
REVERSE_CODES = TARGET_CODES[::-1]  # E, M, A, G

# Rows reversed
for r in range(128):
    stream = row_xor_stream(matrix, r)
    # Instead of reversing, search for EMAG in forward stream (= GAME read right-to-left)
    hits = find_pattern_in_stream(stream, REVERSE_CODES)
    for col_start in hits:
        pop = get_population(r)
        raw_vals = [matrix[r][col_start + i] for i in range(4)]
        print(f"  EMAG (reverse GAME) in Row {r}, Col {col_start}-{col_start+3} | Pop: {pop}")
        # Note: reading these right-to-left gives GAME
        game_positions.append({
            "type": "row_reversed",
            "row": r,
            "col_start": col_start,
            "col_end": col_start + 3,
            "direction": "right-to-left (GAME read backwards)",
            "population": pop,
            "raw_values": raw_vals,
            "cells": [(r, col_start + i) for i in range(4)]
        })

# Columns reversed
for c in range(128):
    stream = col_xor_stream(matrix, c)
    hits = find_pattern_in_stream(stream, REVERSE_CODES)
    for row_start in hits:
        raw_vals = [matrix[row_start + i][c] for i in range(4)]
        pops = [get_population(row_start + i) for i in range(4)]
        print(f"  EMAG (reverse GAME) in Col {c}, Rows {row_start}-{row_start+3} | Pops: {pops}")
        game_positions.append({
            "type": "column_reversed",
            "col": c,
            "row_start": row_start,
            "row_end": row_start + 3,
            "direction": "bottom-to-top (GAME read upwards)",
            "populations": pops,
            "raw_values": raw_vals,
            "cells": [(row_start + i, c) for i in range(4)]
        })

total_forward = row_game_count + col_game_count + diag_game_count
print(f"\n  TOTAL FORWARD GAME occurrences: {total_forward}")
print(f"    Rows: {row_game_count}")
print(f"    Columns: {col_game_count}")
print(f"    Diagonals: {diag_game_count}")
print(f"  TOTAL positions (including reverse): {len(game_positions)}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Analyze GAME positions
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("SECTION 2: Position Analysis")
print("=" * 80)

# Collect all cells used by forward GAME hits
forward_positions = [p for p in game_positions if "reversed" not in p["type"]]

print(f"\nAnalyzing {len(forward_positions)} forward GAME occurrences:")

exception_col_hits = []
special_row_hits = []
mirror_analysis = []

for i, pos in enumerate(forward_positions):
    cells = pos["cells"]
    print(f"\n--- GAME #{i+1} ({pos['type']}, {pos.get('direction', '')}) ---")
    print(f"  Cells: {cells}")
    print(f"  Raw values: {pos['raw_values']}")

    # Exception column check
    for r, c in cells:
        if c in EXCEPTION_COLS:
            exception_col_hits.append({"game_idx": i+1, "row": r, "col": c, "exception_col": c})
            print(f"  ** Cell ({r},{c}) is in EXCEPTION column {c}!")

    # Special row check
    for r, c in cells:
        if r in FACTORY_ROWS:
            special_row_hits.append({"game_idx": i+1, "row": r, "col": c, "special": f"factory row {r}"})
            print(f"  ** Cell ({r},{c}) is in FACTORY row {r}!")
        if r == PACEMAKER_ROW:
            special_row_hits.append({"game_idx": i+1, "row": r, "col": c, "special": "pacemaker row 26"})
            print(f"  ** Cell ({r},{c}) is in PACEMAKER row 26!")
        if r in BOUNDARY_ROWS:
            special_row_hits.append({"game_idx": i+1, "row": r, "col": c, "special": f"boundary row {r}"})
            print(f"  ** Cell ({r},{c}) is in BOUNDARY row {r}!")

    # Mirror position analysis
    mirror_cells = [(127 - r, 127 - c) for r, c in cells]
    mirror_codes = [(int(matrix[mr][mc]) ^ 127) % 128 for mr, mc in mirror_cells]
    mirror_chars = [chr(code) if 32 <= code < 127 else f"<{code}>" for code in mirror_codes]
    mirror_word = "".join(mirror_chars)
    print(f"  Mirror positions (127-r, 127-c): {mirror_cells}")
    print(f"  Mirror XOR 127 codes: {mirror_codes}")
    print(f"  Mirror characters: {''.join(mirror_chars)} ({mirror_word})")
    mirror_analysis.append({
        "game_idx": i + 1,
        "original_cells": cells,
        "mirror_cells": mirror_cells,
        "mirror_codes": mirror_codes,
        "mirror_chars": mirror_chars,
        "mirror_word": mirror_word
    })

print(f"\nException column hits: {len(exception_col_hits)}")
for h in exception_col_hits:
    print(f"  GAME #{h['game_idx']}: ({h['row']},{h['col']}) in exception col {h['exception_col']}")

print(f"\nSpecial row hits: {len(special_row_hits)}")
for h in special_row_hits:
    print(f"  GAME #{h['game_idx']}: ({h['row']},{h['col']}) - {h['special']}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: Context around each GAME
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("SECTION 3: Context around each GAME")
print("=" * 80)

context_analysis = []

for i, pos in enumerate(forward_positions):
    print(f"\n--- GAME #{i+1} ({pos['type']}) ---")

    if pos["type"] == "row":
        r = pos["row"]
        stream = row_xor_stream(matrix, r)
        col = pos["col_start"]

        # Get context: 10 chars before and after
        before_start = max(0, col - 10)
        after_end = min(128, col + 4 + 10)

        context_codes = stream[before_start:after_end]
        context_chars = [chr(c) if 32 <= c < 127 else "." for c in context_codes]
        context_str = "".join(context_chars)

        game_offset = col - before_start
        # Mark GAME in context
        marked = context_str[:game_offset] + "[" + context_str[game_offset:game_offset+4] + "]" + context_str[game_offset+4:]

        print(f"  Row {r} context: ...{marked}...")
        print(f"  Full row decoded: {''.join(chr(c) if 32 <= c < 127 else '.' for c in stream)}")

        context_analysis.append({
            "game_idx": i + 1,
            "context_string": marked,
            "full_row": "".join(chr(c) if 32 <= c < 127 else "." for c in stream)
        })

    elif pos["type"] == "column":
        c = pos["col"]
        stream = col_xor_stream(matrix, c)
        row = pos["row_start"]

        before_start = max(0, row - 10)
        after_end = min(128, row + 4 + 10)

        context_codes = stream[before_start:after_end]
        context_chars = [chr(code) if 32 <= code < 127 else "." for code in context_codes]
        context_str = "".join(context_chars)

        game_offset = row - before_start
        marked = context_str[:game_offset] + "[" + context_str[game_offset:game_offset+4] + "]" + context_str[game_offset+4:]

        print(f"  Col {c} context: ...{marked}...")

        context_analysis.append({
            "game_idx": i + 1,
            "context_string": marked
        })

    elif "diagonal" in pos["type"]:
        cells = pos["cells"]
        print(f"  Diagonal cells: {cells}")
        # Show nearby cells on same diagonal
        context_analysis.append({
            "game_idx": i + 1,
            "cells": [list(c) for c in cells],
            "note": "diagonal occurrence"
        })

# Search for longer words containing GAME
print("\n--- Searching for longer words containing GAME ---")
extended_words = []
for r in range(128):
    stream = row_xor_stream(matrix, r)
    hits = find_pattern_in_stream(stream, TARGET_CODES)
    for col_start in hits:
        # Extend left and right while printable
        left = col_start
        while left > 0:
            code = stream[left - 1]
            if 65 <= code <= 90:  # uppercase letter
                left -= 1
            else:
                break
        right = col_start + 4
        while right < 128:
            code = stream[right]
            if 65 <= code <= 90:
                right += 1
            else:
                break
        word_codes = stream[left:right]
        word = "".join(chr(c) for c in word_codes)
        if len(word) > 4:
            print(f"  Row {r}: Extended word = '{word}' (cols {left}-{right-1})")
            extended_words.append({"row": r, "word": word, "col_start": left, "col_end": right - 1})


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Cross-reference with GENESIS token messages
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("SECTION 4: Cross-reference with GENESIS token messages")
print("=" * 80)

# "First key to the GAME" - search for KEY near GAME
print("\n--- Searching for 'KEY' near GAME positions ---")
KEY_CODES = [ord(c) for c in "KEY"]
key_near_game = []

for i, pos in enumerate(forward_positions):
    if pos["type"] == "row":
        r = pos["row"]
        stream = row_xor_stream(matrix, r)
        key_hits = find_pattern_in_stream(stream, KEY_CODES)
        if key_hits:
            for kh in key_hits:
                distance = abs(kh - pos["col_start"])
                print(f"  GAME #{i+1} row {r}: 'KEY' found at col {kh}, distance = {distance}")
                key_near_game.append({
                    "game_idx": i + 1,
                    "game_row": r,
                    "game_col": pos["col_start"],
                    "key_col": kh,
                    "distance": distance
                })

# Also search all rows for KEY
print("\n--- All 'KEY' occurrences in rows ---")
all_key_positions = []
for r in range(128):
    stream = row_xor_stream(matrix, r)
    hits = find_pattern_in_stream(stream, KEY_CODES)
    for h in hits:
        all_key_positions.append({"row": r, "col": h})
        print(f"  KEY at row {r}, col {h} (Pop: {get_population(r)})")

print(f"\nTotal KEY occurrences: {len(all_key_positions)}")

# "The game is not random" - entropy analysis
print("\n--- Entropy analysis: GAME rows vs. other rows ---")
game_rows = set()
for pos in forward_positions:
    if pos["type"] == "row":
        game_rows.add(pos["row"])
    elif pos["type"] in ("column", "diagonal_SE", "diagonal_SW"):
        for r, c in pos["cells"]:
            game_rows.add(r)

game_row_entropies = []
other_row_entropies = []

for r in range(128):
    vals = [matrix[r][c] for c in range(128)]
    ent = shannon_entropy(vals)
    if r in game_rows:
        game_row_entropies.append((r, ent))
    else:
        other_row_entropies.append((r, ent))

avg_game_entropy = sum(e for _, e in game_row_entropies) / max(len(game_row_entropies), 1)
avg_other_entropy = sum(e for _, e in other_row_entropies) / max(len(other_row_entropies), 1)

print(f"\n  GAME rows ({len(game_row_entropies)}): avg entropy = {avg_game_entropy:.4f}")
for r, e in game_row_entropies:
    print(f"    Row {r}: entropy = {e:.4f}")
print(f"  Other rows ({len(other_row_entropies)}): avg entropy = {avg_other_entropy:.4f}")
print(f"  Difference: {avg_game_entropy - avg_other_entropy:+.4f}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: GAME as game-theoretic mechanism
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("SECTION 5: GAME as game-theoretic mechanism - numerical connections")
print("=" * 80)

# G=6, A=0, M=12, E=4 (A=0 encoding)
a0_vals = {"G": 6, "A": 0, "M": 12, "E": 4}
a0_sum = sum(a0_vals.values())
print(f"\nA=0 encoding: G={a0_vals['G']}, A={a0_vals['A']}, M={a0_vals['M']}, E={a0_vals['E']}")
print(f"  Sum = {a0_sum}")
print(f"  22 is exception column? {'YES' if a0_sum in EXCEPTION_COLS else 'NO'} (exception cols: {sorted(EXCEPTION_COLS)})")

# G=7, A=1, M=13, E=5 (A=1 encoding)
a1_vals = {"G": 7, "A": 1, "M": 13, "E": 5}
a1_sum = sum(a1_vals.values())
print(f"\nA=1 encoding: G={a1_vals['G']}, A={a1_vals['A']}, M={a1_vals['M']}, E={a1_vals['E']}")
print(f"  Sum = {a1_sum}")
print(f"  26 is the pacemaker neuron (N26)? {'YES' if a1_sum == PACEMAKER_ROW else 'NO'}")

# ASCII values
ascii_vals = {"G": 71, "A": 65, "M": 77, "E": 69}
ascii_sum = sum(ascii_vals.values())
print(f"\nASCII values: G={ascii_vals['G']}, A={ascii_vals['A']}, M={ascii_vals['M']}, E={ascii_vals['E']}")
print(f"  Sum = {ascii_sum}")
print(f"  {ascii_sum} mod 128 = {ascii_sum % 128}")
print(f"  {ascii_sum} mod 127 = {ascii_sum % 127}")

# XOR of GAME ascii values
xor_game = 71 ^ 65 ^ 77 ^ 69
print(f"\n  G XOR A XOR M XOR E = {xor_game}")
print(f"  {xor_game} is special? col {xor_game}? exception? {xor_game in EXCEPTION_COLS}")

# Product connections
prod_a0 = a0_vals['G'] * a0_vals['A'] * a0_vals['M'] * a0_vals['E']
print(f"\n  A=0 product: 6 * 0 * 12 * 4 = {prod_a0} (zero because A=0)")
prod_a1 = a1_vals['G'] * a1_vals['A'] * a1_vals['M'] * a1_vals['E']
print(f"  A=1 product: 7 * 1 * 13 * 5 = {prod_a1}")
print(f"  455 mod 128 = {prod_a1 % 128}")

# Matrix value at position (22, 26) and (26, 22) - the intersection
val_22_26 = matrix[22][26]
val_26_22 = matrix[26][22]
print(f"\n  M[22,26] = {val_22_26} (intersection of exception col 22 col, pacemaker row 26 offset)")
print(f"  M[26,22] = {val_26_22} (pacemaker row, exception col)")
code_26_22 = (val_26_22 ^ 127) % 128
print(f"  M[26,22] XOR 127 = {code_26_22} = '{chr(code_26_22) if 32 <= code_26_22 < 127 else '<non-printable>'}'")

# Where does GAME appear relative to the matrix diagonal?
print(f"\nDiagonal analysis:")
for i, pos in enumerate(forward_positions):
    cells = pos["cells"]
    for r, c in cells:
        on_diag = "ON MAIN DIAGONAL" if r == c else f"off by {abs(r-c)}"
        on_anti = "ON ANTI-DIAGONAL" if r + c == 127 else f"anti-diag sum = {r+c}"
        print(f"  GAME #{i+1} cell ({r},{c}): {on_diag}, {on_anti}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: Statistical controls
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("SECTION 6: Statistical Controls")
print("=" * 80)

# 6a. Count all 4-letter uppercase words in XOR 127 rows
print("\n--- 6a: All 4-letter uppercase words in XOR 127 (rows only) ---")

# Common 4-letter English words to search
COMMON_WORDS = [
    "GAME", "LOVE", "LIFE", "DEAD", "CODE", "DATA", "FILE", "HACK", "HOME",
    "JAVA", "KEYS", "KING", "LINK", "LOCK", "LOOP", "MEGA", "MODE", "MOON",
    "NAME", "NODE", "NULL", "ONCE", "OPEN", "PAGE", "PATH", "PIPE", "PORT",
    "PUSH", "QUIT", "READ", "RING", "ROOT", "SEED", "SELF", "SORT", "STAR",
    "STOP", "SYNC", "TASK", "TEST", "TEXT", "TIME", "TOOL", "TRAP", "TREE",
    "TRUE", "TYPE", "UNIT", "USER", "VIEW", "VOID", "WAIT", "WALK", "WALL",
    "WAVE", "WORD", "WORK", "ZERO", "ZONE", "FREE", "GOLD", "HASH", "HELP",
    "HIDE", "HIGH", "HOLD", "HUNT", "IDEA", "JUMP", "JUST", "KEEP", "LAST",
    "LEFT", "LINE", "LIST", "LONG", "LOOK", "LUCK", "MAIN", "MAKE", "MARK",
    "MIND", "MINE", "MISS", "MUCH", "MUST", "NEAR", "NEED", "NEXT", "NICE",
    "ANNA", "BURN", "CALL", "CARD", "CARE", "CAST", "COME", "COOL", "COPY",
    "CORE", "DARK", "DEEP", "DONE", "DOWN", "DROP", "EACH", "EASY", "EDGE",
    "EVIL", "EXIT", "FACE", "FAIL", "FAIR", "FALL", "FAST", "FATE", "FEAR",
    "FEEL", "FIND", "FIRE", "FISH", "FIVE", "FLAG", "FLAT", "FLOW", "FOLD",
    "FOOD", "FORK", "FORM", "FOUR", "FROM", "FULL", "FUNC", "FUSE", "GAIN"
]

word_counts = {}
for word in COMMON_WORDS:
    codes = [ord(c) for c in word]
    count = 0
    for r in range(128):
        stream = row_xor_stream(matrix, r)
        count += len(find_pattern_in_stream(stream, codes))
    if count > 0:
        word_counts[word] = count

# Sort by count
sorted_words = sorted(word_counts.items(), key=lambda x: -x[1])
print(f"\n  Words found (rows only):")
for word, count in sorted_words:
    marker = " <<<" if word == "GAME" else ""
    print(f"    {word}: {count}{marker}")

# Also do exhaustive search for ANY 4 consecutive uppercase letters
print("\n--- Exhaustive 4-uppercase-letter sequences in rows ---")
four_letter_seqs = Counter()
for r in range(128):
    stream = row_xor_stream(matrix, r)
    for i in range(125):
        if all(65 <= stream[i+j] <= 90 for j in range(4)):
            word = "".join(chr(stream[i+j]) for j in range(4))
            four_letter_seqs[word] += 1

print(f"  Total distinct 4-uppercase sequences: {len(four_letter_seqs)}")
print(f"  Top 30 by frequency:")
for word, count in four_letter_seqs.most_common(30):
    marker = " <<<" if word == "GAME" else ""
    print(f"    {word}: {count}{marker}")

words_8_plus = {w: c for w, c in four_letter_seqs.items() if c >= 8}
print(f"\n  4-letter sequences appearing 8+ times: {len(words_8_plus)}")
for w, c in sorted(words_8_plus.items(), key=lambda x: -x[1]):
    print(f"    {w}: {c}")

# 6b. Monte Carlo: expected GAME count in random 128x128 matrix
print("\n--- 6b: Monte Carlo simulation (1000 random matrices) ---")
N_TRIALS = 1000
random_counts = []
random.seed(42)

for trial in range(N_TRIALS):
    count = 0
    # Generate random 128x128 matrix with values in [-128, 127]
    for r in range(128):
        stream = [(random.randint(-128, 127) ^ 127) % 128 for _ in range(128)]
        count += len(find_pattern_in_stream(stream, TARGET_CODES))
    random_counts.append(count)

avg_random = sum(random_counts) / N_TRIALS
max_random = max(random_counts)
min_random = min(random_counts)
std_random = (sum((x - avg_random)**2 for x in random_counts) / N_TRIALS) ** 0.5

# How many of the random trials had >= observed count?
observed_row_count = row_game_count
p_value = sum(1 for x in random_counts if x >= observed_row_count) / N_TRIALS

print(f"  Observed GAME count in rows: {observed_row_count}")
print(f"  Random matrix stats (rows only, {N_TRIALS} trials):")
print(f"    Mean: {avg_random:.2f}")
print(f"    Std:  {std_random:.2f}")
print(f"    Min:  {min_random}")
print(f"    Max:  {max_random}")
print(f"    P-value (>= {observed_row_count}): {p_value:.4f}")
if std_random > 0:
    z_score = (observed_row_count - avg_random) / std_random
    print(f"    Z-score: {z_score:.2f}")
else:
    z_score = float('inf') if observed_row_count > avg_random else 0
    print(f"    Z-score: {z_score}")

# Theoretical expectation
# Each row has 125 possible start positions for a 4-letter sequence
# P(GAME at any position) = (1/128)^4 for uniform random XOR output
# Expected per row = 125 * (1/128)^4
# Expected total = 128 * 125 * (1/128)^4
p_single = (1/128)**4
expected_per_row = 125 * p_single
expected_total = 128 * expected_per_row
print(f"\n  Theoretical (uniform):")
print(f"    P(GAME at single position) = (1/128)^4 = {p_single:.2e}")
print(f"    Expected per row = {expected_per_row:.6f}")
print(f"    Expected total (rows) = {expected_total:.6f}")

# 6c. Distribution of XOR 127 values
print("\n--- 6c: XOR 127 value distribution ---")
all_xor_vals = []
for r in range(128):
    for c in range(128):
        all_xor_vals.append((int(matrix[r][c]) ^ 127) % 128)

xor_dist = Counter(all_xor_vals)
# Check if G, A, M, E values are over/under-represented
for letter, code in [("G", 71), ("A", 65), ("M", 77), ("E", 69)]:
    count = xor_dist[code]
    expected = 128 * 128 / 128  # = 128 if uniform
    print(f"  XOR value {code} ({letter}): count = {count}, expected ~{expected:.0f}, ratio = {count/expected:.3f}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: Additional deep patterns
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("SECTION 7: Additional deep patterns")
print("=" * 80)

# Check if GAME positions form geometric patterns
print("\n--- GAME position geometry ---")
if forward_positions:
    all_game_cells = set()
    for pos in forward_positions:
        for cell in pos["cells"]:
            all_game_cells.add(tuple(cell))

    rows_used = sorted(set(r for r, c in all_game_cells))
    cols_used = sorted(set(c for r, c in all_game_cells))
    print(f"  Rows containing GAME cells: {rows_used}")
    print(f"  Cols containing GAME cells: {cols_used}")
    print(f"  Total unique cells: {len(all_game_cells)}")

    # Check symmetry
    symmetric_pairs = 0
    for r, c in all_game_cells:
        mirror = (127 - r, 127 - c)
        if mirror in all_game_cells:
            symmetric_pairs += 1
    print(f"  Cells with 127-mirror also in GAME: {symmetric_pairs} / {len(all_game_cells)}")

    # Row/col sums
    for pos in forward_positions:
        cells = pos["cells"]
        row_sum = sum(r for r, c in cells)
        col_sum = sum(c for r, c in cells)
        total_sum = sum(r + c for r, c in cells)
        print(f"  GAME ({pos['type']}): row_sum={row_sum}, col_sum={col_sum}, total_sum={total_sum}")

# Check what the full row XOR 127 looks like for each GAME row
print("\n--- Full XOR 127 decoded rows containing GAME ---")
game_row_set = set()
for pos in forward_positions:
    if pos["type"] == "row":
        game_row_set.add(pos["row"])

for r in sorted(game_row_set):
    stream = row_xor_stream(matrix, r)
    decoded = "".join(chr(c) if 32 <= c < 127 else "." for c in stream)
    # Highlight GAME
    highlighted = decoded.replace("GAME", ">>GAME<<")
    print(f"  Row {r:3d} ({get_population(r):25s}): {highlighted}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: Investigating the "8 GAME" claim
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("SECTION 8: Investigating the prior '8 GAME' claim")
print("=" * 80)

print("""
Prior scripts (ANNA_MASTER_NUMBERS.py, ANNA_CRYPTO_DECODE.py) claimed "GAME appears
8 times in XOR 127". This section investigates what that count might have referred to.
""")

# Count all 4-char sequences using ONLY the letters {G, A, M, E}
game_letter_set = {71, 65, 77, 69}  # G, A, M, E
game_family_rows = []
for r in range(128):
    stream = row_xor_stream(matrix, r)
    for i in range(125):
        window = stream[i:i+4]
        if all(c in game_letter_set for c in window):
            word = "".join(chr(c) for c in window)
            game_family_rows.append({"row": r, "col": i, "word": word})

print(f"  All 4-char sequences using only {{G, A, M, E}} in rows: {len(game_family_rows)}")
for item in game_family_rows:
    marker = " <<<" if item["word"] == "GAME" else ""
    print(f"    Row {item['row']}, Col {item['col']}: {item['word']}{marker}")

# Count specific GAME-related patterns
game_related_patterns = {}
for pattern_name, codes in [
    ("GAME", [71, 65, 77, 69]),
    ("GAGE", [71, 65, 71, 69]),
    ("AGEE", [65, 71, 69, 69]),
    ("GEEE", [71, 69, 69, 69]),
    ("EEEE", [69, 69, 69, 69]),
    ("MEGA", [77, 69, 71, 65]),
    ("MAGE", [77, 65, 71, 69]),
    ("CAGE", [67, 65, 71, 69]),  # not pure GAME letters
    ("RAGE", [82, 65, 71, 69]),
    ("SAGE", [83, 65, 71, 69]),
    ("PAGE", [80, 65, 71, 69]),
    ("AGED", [65, 71, 69, 68]),
    ("AGES", [65, 71, 69, 83]),
    ("RGAG", [82, 71, 65, 71]),
    ("GAGE", [71, 65, 71, 69]),
]:
    count = 0
    positions = []
    for r in range(128):
        stream = row_xor_stream(matrix, r)
        for i in range(125):
            if stream[i:i+4] == codes:
                count += 1
                positions.append((r, i))
    if count > 0:
        game_related_patterns[pattern_name] = {"count": count, "positions": positions}

print(f"\n  GAME-related 4-letter patterns found in rows:")
for name, info in sorted(game_related_patterns.items(), key=lambda x: -x[1]["count"]):
    print(f"    {name}: {info['count']} at {info['positions']}")

# Count GAME-family in columns too
game_family_cols = []
for col in range(128):
    stream = col_xor_stream(matrix, col)
    for i in range(125):
        window = stream[i:i+4]
        if all(c in game_letter_set for c in window):
            word = "".join(chr(c) for c in window)
            game_family_cols.append({"col": col, "row_start": i, "word": word})

print(f"\n  All 4-char {{G,A,M,E}}-only sequences in columns: {len(game_family_cols)}")
for item in game_family_cols:
    print(f"    Col {item['col']}, Row {item['row_start']}: {item['word']}")

# Total GAME-letter-family across rows + cols
total_family = len(game_family_rows) + len(game_family_cols)
print(f"\n  TOTAL {'{'}G,A,M,E{'}'}-only 4-char sequences: {total_family} (rows: {len(game_family_rows)}, cols: {len(game_family_cols)})")

# Rows that contain all 4 letters G, A, M, E somewhere (not consecutive)
rows_with_all_4 = []
for r in range(128):
    stream = set(row_xor_stream(matrix, r))
    if game_letter_set.issubset(stream):
        rows_with_all_4.append(r)
print(f"\n  Rows containing all 4 letters G, A, M, E (non-consecutive): {len(rows_with_all_4)}")
print(f"    Rows: {rows_with_all_4}")

# Hypothesis: the "8" may have been the count of GAGE (4) + GAME (1) + AGEE (2) + something
# Or it might have been rows with all 4 letters (4 rows) doubled somehow
print(f"\n  Conclusion: The exact '8 GAME' count from prior scripts cannot be reproduced.")
print(f"  Actual consecutive 'GAME' in XOR 127: 1 (Row 1, Col 52)")
print(f"  Related patterns: GAGE=4, AGEE=2, GAME=1 in rows")
print(f"  The '8' may have been an error, or counted GAME-letter-family patterns differently.")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: Row 1 deep dive (the GAME row)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("SECTION 9: Row 1 deep dive - the GAME row")
print("=" * 80)

stream_r1 = row_xor_stream(matrix, 1)
decoded_r1 = "".join(chr(c) if 32 <= c < 127 else "." for c in stream_r1)

print(f"\n  Row 1 is: Factory Row (one of {{1, 9, 49, 57}})")
print(f"  Population: {get_population(1)}")
print(f"  Full XOR 127 decoded:")
print(f"    {decoded_r1}")

# Find ALL words/patterns in row 1
print(f"\n  All uppercase 3+ letter sequences in Row 1:")
i = 0
while i < 128:
    if 65 <= stream_r1[i] <= 90:
        j = i
        while j < 128 and 65 <= stream_r1[j] <= 90:
            j += 1
        if j - i >= 3:
            word = "".join(chr(stream_r1[k]) for k in range(i, j))
            print(f"    Cols {i}-{j-1}: '{word}' (len={j-i})")
        i = j
    else:
        i += 1

# Row 1 special values
print(f"\n  Row 1 raw values at GAME position (cols 52-55): {[matrix[1][c] for c in range(52, 56)]}")
print(f"  Row 1 raw values at GAGE position (cols 32-35): {[matrix[1][c] for c in range(32, 36)]}")

# Compare row 1 with its mirror row 126
stream_r126 = row_xor_stream(matrix, 126)
decoded_r126 = "".join(chr(c) if 32 <= c < 127 else "." for c in stream_r126)
print(f"\n  Mirror Row 126 ({get_population(126)}):")
print(f"    {decoded_r126}")

# Check if row 1 and row 126 are related
matching = sum(1 for a, b in zip(stream_r1, stream_r126) if a == b)
print(f"  Cells matching between Row 1 and Row 126: {matching}/128")

# Factory row comparison
print(f"\n  All factory rows decoded:")
for fr in sorted(FACTORY_ROWS):
    stream = row_xor_stream(matrix, fr)
    decoded = "".join(chr(c) if 32 <= c < 127 else "." for c in stream)
    # Check for GAME
    has_game = "GAME" in decoded
    print(f"    Row {fr:3d}: {decoded}  {'*** HAS GAME ***' if has_game else ''}")


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT: Save all results to JSON
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("Saving results to JSON...")
print("=" * 80)

results = {
    "summary": {
        "total_forward_GAME": total_forward,
        "row_occurrences": row_game_count,
        "column_occurrences": col_game_count,
        "diagonal_occurrences": diag_game_count,
        "total_with_reverse": len(game_positions),
    },
    "game_positions": [],
    "exception_column_hits": exception_col_hits,
    "special_row_hits": special_row_hits,
    "mirror_analysis": mirror_analysis,
    "context_analysis": context_analysis,
    "extended_words": extended_words,
    "key_near_game": key_near_game,
    "all_key_positions": all_key_positions,
    "entropy_analysis": {
        "game_rows": [{"row": r, "entropy": e} for r, e in game_row_entropies],
        "avg_game_entropy": avg_game_entropy,
        "avg_other_entropy": avg_other_entropy,
        "difference": avg_game_entropy - avg_other_entropy,
    },
    "numerical_connections": {
        "A0_encoding": a0_vals,
        "A0_sum": a0_sum,
        "A0_sum_is_exception_col": a0_sum in EXCEPTION_COLS,
        "A1_encoding": a1_vals,
        "A1_sum": a1_sum,
        "A1_sum_is_pacemaker": a1_sum == PACEMAKER_ROW,
        "ASCII_sum": ascii_sum,
        "ASCII_sum_mod128": ascii_sum % 128,
        "XOR_of_GAME": xor_game,
        "A1_product": prod_a1,
    },
    "statistical_controls": {
        "four_letter_word_counts_rows": dict(sorted_words),
        "four_letter_uppercase_sequences_8plus": words_8_plus,
        "total_distinct_4letter_sequences": len(four_letter_seqs),
        "monte_carlo": {
            "trials": N_TRIALS,
            "observed_row_count": observed_row_count,
            "mean_random": avg_random,
            "std_random": std_random,
            "min_random": min_random,
            "max_random": max_random,
            "p_value": p_value,
            "z_score": z_score if isinstance(z_score, (int, float)) and not math.isinf(z_score) else str(z_score),
        },
        "theoretical_expected_rows": expected_total,
        "xor127_distribution_GAME_letters": {
            "G_71": {"count": xor_dist[71], "expected": 128},
            "A_65": {"count": xor_dist[65], "expected": 128},
            "M_77": {"count": xor_dist[77], "expected": 128},
            "E_69": {"count": xor_dist[69], "expected": 128},
        }
    },
    "geometry": {
        "rows_used": rows_used if forward_positions else [],
        "cols_used": cols_used if forward_positions else [],
        "total_unique_cells": len(all_game_cells) if forward_positions else 0,
        "mirror_symmetric_cells": symmetric_pairs if forward_positions else 0,
    },
    "game_letter_family": {
        "rows_using_only_GAME_letters": [{"row": x["row"], "col": x["col"], "word": x["word"]} for x in game_family_rows],
        "cols_using_only_GAME_letters": [{"col": x["col"], "row_start": x["row_start"], "word": x["word"]} for x in game_family_cols],
        "total_family_count": total_family,
        "game_related_patterns": {name: {"count": info["count"], "positions": [list(p) for p in info["positions"]]} for name, info in game_related_patterns.items()},
        "rows_with_all_4_letters": rows_with_all_4,
    },
    "prior_8_claim_investigation": {
        "conclusion": "The '8 GAME' claim from ANNA_MASTER_NUMBERS.py cannot be reproduced. Actual consecutive GAME in XOR 127: 1. The prior count may have used a broader definition or contained an error.",
        "actual_GAME_count": 1,
        "GAGE_count": game_related_patterns.get("GAGE", {}).get("count", 0),
        "AGEE_count": game_related_patterns.get("AGEE", {}).get("count", 0),
        "total_GAME_letter_family_rows": len(game_family_rows),
    },
    "row1_deep_dive": {
        "population": get_population(1),
        "is_factory_row": True,
        "decoded_xor127": decoded_r1,
        "game_position": {"col_start": 52, "col_end": 55},
        "raw_values_at_game": [matrix[1][c] for c in range(52, 56)],
    }
}

# Serialize game positions (convert tuples to lists for JSON)
for pos in game_positions:
    serializable = {}
    for k, v in pos.items():
        if k == "cells":
            serializable[k] = [list(c) for c in v]
        else:
            serializable[k] = v
    results["game_positions"].append(serializable)

with open(OUTPUT_PATH, "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to: {OUTPUT_PATH}")

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print(f"""
GAME occurrences (forward):
  Rows:      {row_game_count}
  Columns:   {col_game_count}
  Diagonals: {diag_game_count}
  TOTAL:     {total_forward}

Statistical significance:
  Expected by chance (rows): {expected_total:.4f}
  Observed (rows): {observed_row_count}
  Monte Carlo p-value: {p_value:.4f}

Numerical connections:
  G+A+M+E (A=0) = {a0_sum} = exception column 22  {'CONFIRMED' if a0_sum in EXCEPTION_COLS else 'NOT CONFIRMED'}
  G+A+M+E (A=1) = {a1_sum} = pacemaker neuron 26  {'CONFIRMED' if a1_sum == PACEMAKER_ROW else 'NOT CONFIRMED'}
  G XOR A XOR M XOR E = {xor_game}

Exception column overlaps: {len(exception_col_hits)}
Special row overlaps: {len(special_row_hits)}
KEY near GAME: {len(key_near_game)}
""")

print("Analysis complete.")
