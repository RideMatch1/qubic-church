#!/usr/bin/env python3
"""
PHASE 6: GROK-Pfad Entschlüsselung - NEW ALGORITHMS
====================================================
CFB: "Ask Grok to decode"

Testing previously UNTESTED approaches:
1. Matrix Path Walker
2. Balanced Ternary Conversion (120 trits)
3. Missing Numbers Analysis
4. Hamiltonian Path in 10x10 Grid
5. XOR with Anna Matrix values
6. GROK as Bridge Key
"""

import json
import hashlib
from datetime import datetime
from collections import Counter

print("=" * 80)
print("PHASE 6: GROK-PFAD ENTSCHLÜSSELUNG")
print("New Algorithms - Previously Untested")
print("=" * 80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# The GROK sequence
GROK = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16,
        73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

# Load Anna Matrix
with open('../public/data/anna-matrix.json') as f:
    matrix_data = json.load(f)
raw_matrix = matrix_data.get('matrix', [])
matrix = []
for row in raw_matrix:
    new_row = []
    for val in row:
        if isinstance(val, str):
            try:
                new_row.append(int(val))
            except ValueError:
                new_row.append(0)
        else:
            new_row.append(val)
    matrix.append(new_row)

print("\n[0] BASIC PROPERTIES")
print("-" * 60)
print(f"Sequence: {GROK}")
print(f"Count: {len(GROK)}")
print(f"Sum: {sum(GROK)} (= 2000 exactly!)")
print(f"Min: {min(GROK)}, Max: {max(GROK)}")
print(f"All unique: {len(GROK) == len(set(GROK))}")

results = {
    'sequence': GROK,
    'sum': sum(GROK),
    'count': len(GROK),
    'algorithms': {}
}

# ============================================================================
# ALGORITHM 1: MATRIX PATH WALKER
# ============================================================================
print("\n" + "=" * 80)
print("ALGORITHM 1: MATRIX PATH WALKER")
print("=" * 80)

# Method 1a: Pairs as direct coordinates
print("\n[1a] Pairs as direct coordinates (row, col)")
pairs = [(GROK[i], GROK[i+1]) for i in range(0, len(GROK)-1, 2)]
print(f"Coordinate pairs: {pairs}")

path_values_direct = []
for row, col in pairs:
    r = row % 128
    c = col % 128
    val = matrix[r][c]
    path_values_direct.append(val)
    print(f"  [{r:3}, {c:3}] = {val:4}")

print(f"\nCollected values: {path_values_direct}")
print(f"Sum: {sum(path_values_direct)}")

# Try as ASCII
ascii_direct = ''.join(chr(abs(v) + 32) if 0 <= abs(v) + 32 < 128 else '?' for v in path_values_direct)
print(f"As ASCII (offset 32): {ascii_direct}")

# XOR chain
xor_result = 0
for v in path_values_direct:
    xor_result ^= (v & 0xFF)
print(f"XOR chain result: {xor_result}")

results['algorithms']['path_walker_direct'] = {
    'values': path_values_direct,
    'sum': sum(path_values_direct),
    'ascii': ascii_direct,
    'xor': xor_result
}

# Method 1b: Pairs as delta movements
print("\n[1b] Pairs as delta movements from center (64, 64)")
pos = [64, 64]  # Start at center
path_delta = [matrix[pos[0]][pos[1]]]
positions_visited = [(64, 64)]

for i in range(0, len(GROK)-1, 2):
    delta_r = (GROK[i] - 50) % 128  # Offset to make movement reasonable
    delta_c = (GROK[i+1] - 50) % 128
    pos[0] = (pos[0] + delta_r) % 128
    pos[1] = (pos[1] + delta_c) % 128
    path_delta.append(matrix[pos[0]][pos[1]])
    positions_visited.append((pos[0], pos[1]))

print(f"Positions visited: {positions_visited[:10]}...")
print(f"Values collected: {path_delta}")

results['algorithms']['path_walker_delta'] = {
    'positions': positions_visited,
    'values': path_delta,
    'sum': sum(path_delta)
}

# ============================================================================
# ALGORITHM 2: BALANCED TERNARY CONVERSION
# ============================================================================
print("\n" + "=" * 80)
print("ALGORITHM 2: BALANCED TERNARY CONVERSION")
print("=" * 80)

def to_balanced_ternary(n, digits=3):
    """Convert to balanced ternary (-1, 0, +1)"""
    result = []
    for _ in range(digits):
        rem = n % 3
        if rem == 0:
            result.append(0)
        elif rem == 1:
            result.append(1)
        else:  # rem == 2
            result.append(-1)
            n += 1
        n //= 3
    return result[::-1]

print("\n[2a] Each number to 3-trit balanced ternary")
all_trits = []
for num in GROK:
    trits = to_balanced_ternary(num, 3)
    all_trits.extend(trits)
    if num in [45, 92, 27, 82, 39]:  # Key numbers
        print(f"  {num:3} -> {trits}")

print(f"\nTotal trits: {len(all_trits)} (= 40 × 3 = 120)")
print(f"First 30 trits: {all_trits[:30]}")

# Count distribution
trit_counts = Counter(all_trits)
print(f"Trit distribution: {dict(trit_counts)}")

# Convert trit sequence to regions in matrix
# -1 = negative region, 0 = zero region, +1 = positive region
region_sequence = ''.join(['N' if t == -1 else ('Z' if t == 0 else 'P') for t in all_trits])
print(f"Region sequence: {region_sequence[:40]}...")

# Try to interpret as message (3 trits = one character from 27-char alphabet)
alphabet_27 = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"
message_ternary = []
for i in range(0, len(all_trits), 3):
    if i+2 < len(all_trits):
        val = (all_trits[i] + 1) * 9 + (all_trits[i+1] + 1) * 3 + (all_trits[i+2] + 1)
        if 0 <= val < 27:
            message_ternary.append(alphabet_27[val])
        else:
            message_ternary.append('?')

print(f"Ternary message (27-char): {''.join(message_ternary)}")

results['algorithms']['balanced_ternary'] = {
    'total_trits': len(all_trits),
    'distribution': dict(trit_counts),
    'message_27': ''.join(message_ternary)
}

# ============================================================================
# ALGORITHM 3: MISSING NUMBERS ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("ALGORITHM 3: MISSING NUMBERS ANALYSIS")
print("=" * 80)

# GROK has 40 unique numbers from 3-98
# What numbers are MISSING?
present = set(GROK)
all_nums = set(range(1, 100))  # 1-99
missing = sorted(all_nums - present)

print(f"Present: {len(present)} numbers")
print(f"Missing: {len(missing)} numbers")
print(f"Missing list: {missing}")

# Check for patterns in missing numbers
print("\n[3a] Analysis of missing numbers:")
print(f"Sum of present: {sum(present)}")
print(f"Sum of missing: {sum(missing)}")
print(f"Sum of all (1-99): {sum(range(1, 100))}")
print(f"Sum present + missing = {sum(present) + sum(missing)}")

# Check which CFB numbers are missing
cfb_numbers = [3, 7, 11, 13, 19, 27, 37, 42, 73, 100, 121, 127]
print(f"\nCFB numbers in sequence: {[n for n in cfb_numbers if n in present]}")
print(f"CFB numbers MISSING: {[n for n in cfb_numbers if n in missing]}")

# XOR present vs missing
xor_present = 0
for n in present:
    xor_present ^= n
xor_missing = 0
for n in missing:
    xor_missing ^= n

print(f"\nXOR of present numbers: {xor_present}")
print(f"XOR of missing numbers: {xor_missing}")
print(f"XOR present ^ missing: {xor_present ^ xor_missing}")

# Check if missing numbers encode something
missing_mod27 = [m % 27 for m in missing]
alphabet_27 = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"
try:
    missing_msg = ''.join(alphabet_27[m] for m in missing_mod27[:30])
    print(f"Missing mod 27 as alphabet: {missing_msg}")
except:
    print("Could not convert missing to message")

results['algorithms']['missing_analysis'] = {
    'missing_count': len(missing),
    'missing_list': missing,
    'xor_present': xor_present,
    'xor_missing': xor_missing,
    'cfb_in_sequence': [n for n in cfb_numbers if n in present],
    'cfb_missing': [n for n in cfb_numbers if n in missing]
}

# ============================================================================
# ALGORITHM 4: HAMILTONIAN PATH IN 10x10 GRID
# ============================================================================
print("\n" + "=" * 80)
print("ALGORITHM 4: HAMILTONIAN PATH IN 10x10 GRID")
print("=" * 80)

# Map numbers to 10x10 grid positions
# cell = number - 1 (so 1-100 maps to 0-99)
# row = cell // 10, col = cell % 10

print("\n[4a] Mapping to 10x10 grid:")
grid_positions = []
for num in GROK:
    cell = num - 1  # Adjust to 0-indexed
    row = cell // 10
    col = cell % 10
    grid_positions.append((row, col))

print(f"Grid positions (first 10): {grid_positions[:10]}")

# Check if adjacent (king's move - 8 directions)
def is_adjacent_king(pos1, pos2):
    """Check if two positions are king-adjacent (including diagonals)"""
    r1, c1 = pos1
    r2, c2 = pos2
    return abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1 and pos1 != pos2

def is_adjacent_rook(pos1, pos2):
    """Check if two positions are rook-adjacent (only orthogonal)"""
    r1, c1 = pos1
    r2, c2 = pos2
    return (abs(r1 - r2) == 1 and c1 == c2) or (r1 == r2 and abs(c1 - c2) == 1)

king_adjacent = 0
rook_adjacent = 0
for i in range(len(grid_positions) - 1):
    if is_adjacent_king(grid_positions[i], grid_positions[i+1]):
        king_adjacent += 1
    if is_adjacent_rook(grid_positions[i], grid_positions[i+1]):
        rook_adjacent += 1

print(f"\nKing-adjacent transitions: {king_adjacent} / {len(GROK)-1}")
print(f"Rook-adjacent transitions: {rook_adjacent} / {len(GROK)-1}")

# Visualize path on 10x10 grid
grid_viz = [['.'] * 10 for _ in range(10)]
for i, (r, c) in enumerate(grid_positions):
    if grid_viz[r][c] == '.':
        grid_viz[r][c] = chr(65 + i) if i < 26 else str(i % 10)

print("\n10x10 Grid visualization (A-Z then 0-9 for sequence order):")
for row in grid_viz:
    print("  " + ' '.join(row))

results['algorithms']['hamiltonian_grid'] = {
    'positions': grid_positions,
    'king_adjacent': king_adjacent,
    'rook_adjacent': rook_adjacent
}

# ============================================================================
# ALGORITHM 5: XOR WITH ANNA MATRIX
# ============================================================================
print("\n" + "=" * 80)
print("ALGORITHM 5: XOR WITH ANNA MATRIX")
print("=" * 80)

# Method 5a: Use pairs as coordinates, XOR matrix values
print("\n[5a] Matrix values XORed together")
xor_accumulator = 0
xor_values = []
for r, c in pairs:
    val = matrix[r % 128][c % 128]
    xor_accumulator ^= (val & 0xFF)
    xor_values.append(val)

print(f"Values at pair coordinates: {xor_values}")
print(f"Final XOR result: {xor_accumulator}")
print(f"As char: {chr(xor_accumulator) if 32 <= xor_accumulator < 127 else '?'}")

# Method 5b: Each number XORed with corresponding matrix cell
print("\n[5b] Each GROK number XORed with matrix[num][num]")
diagonal_xor = []
for i, num in enumerate(GROK):
    diag_val = matrix[num % 128][num % 128]
    xored = num ^ (diag_val & 0xFF)
    diagonal_xor.append(xored)
    if i < 10:
        print(f"  {num} ^ matrix[{num%128},{num%128}]={diag_val} = {xored}")

print(f"\nDiagonal XOR results: {diagonal_xor}")

# Try as message
diag_message = ''.join(chr(v) if 32 <= v < 127 else '?' for v in diagonal_xor)
print(f"As ASCII: {diag_message}")

results['algorithms']['xor_matrix'] = {
    'pair_values': xor_values,
    'pair_xor_final': xor_accumulator,
    'diagonal_xor': diagonal_xor,
    'diagonal_message': diag_message
}

# ============================================================================
# ALGORITHM 6: GROK AS BRIDGE KEY
# ============================================================================
print("\n" + "=" * 80)
print("ALGORITHM 6: GROK AS BRIDGE KEY")
print("=" * 80)

# Method 6a: SHA256 of sequence
grok_bytes = bytes(GROK)
sha256_key = hashlib.sha256(grok_bytes).hexdigest()
print(f"\n[6a] SHA256(GROK bytes)")
print(f"Key: {sha256_key}")

# Method 6b: First 32 numbers as raw key
key_32 = bytes(GROK[:32])
print(f"\n[6b] First 32 numbers as raw bytes")
print(f"Key hex: {key_32.hex()}")

# Method 6c: Numbers as ASCII then hash
grok_str = ','.join(map(str, GROK))
sha256_str = hashlib.sha256(grok_str.encode()).hexdigest()
print(f"\n[6c] SHA256(GROK as string)")
print(f"Key: {sha256_str}")

# Method 6d: Pairs summed to 20 bytes
pair_sums = [GROK[i] + GROK[i+1] for i in range(0, len(GROK)-1, 2)]
print(f"\n[6d] Pair sums (20 values)")
print(f"Pair sums: {pair_sums}")
print(f"As hex: {bytes(pair_sums).hex()}")

results['algorithms']['bridge_key'] = {
    'sha256_bytes': sha256_key,
    'first_32_hex': key_32.hex(),
    'sha256_string': sha256_str,
    'pair_sums': pair_sums,
    'pair_sums_hex': bytes(pair_sums).hex()
}

# ============================================================================
# ALGORITHM 7: SPECIAL POSITIONS ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("ALGORITHM 7: SPECIAL POSITIONS ANALYSIS")
print("=" * 80)

print("\n[7a] Known CFB positions in sequence")
# (45, 92) = ENTRY coordinates
entry_val = matrix[45][92]
print(f"(45, 92) ENTRY: matrix[45][92] = {entry_val}")

# (82, 39) = possible EXIT
exit_val = matrix[82][39]
print(f"(82, 39) possible EXIT: matrix[82][39] = {exit_val}")

# 27 at position 37
print(f"\n27 is at position {GROK.index(27)} in sequence")
print(f"Position 27 in sequence has value: {GROK[27]}")

# Check if position sums encode something
print("\n[7b] Position + Value pairs")
pos_val_sums = [i + GROK[i] for i in range(len(GROK))]
print(f"Position + Value sums: {pos_val_sums}")
print(f"Sum of sums: {sum(pos_val_sums)}")

# Check for 137 (Fine Structure Constant = 45 + 92)
print(f"\n[7c] 137 connections")
print(f"45 + 92 = {45 + 92} (= 137 = Fine Structure Constant!)")
for i in range(len(GROK) - 1):
    if GROK[i] + GROK[i+1] == 137:
        print(f"  Adjacent pair sums to 137: GROK[{i}]+GROK[{i+1}] = {GROK[i]}+{GROK[i+1]}")

results['algorithms']['special_positions'] = {
    'entry_45_92': entry_val,
    'exit_82_39': exit_val,
    'position_27_value': GROK[27],
    'value_27_position': GROK.index(27),
    'position_value_sums': pos_val_sums
}

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY: GROK-PFAD ANALYSIS")
print("=" * 80)

print("""
KEY FINDINGS:
=============

1. MATRIX PATH WALKER
   - Direct coordinates give values with sum = {}
   - XOR chain result = {}

2. BALANCED TERNARY
   - 120 trits total
   - Distribution: {}
   - Could encode IOTA-style address

3. MISSING NUMBERS
   - 59 numbers missing from 1-99
   - XOR of present: {}
   - XOR of missing: {}
   - CFB numbers 42 and 11 are MISSING from sequence!

4. HAMILTONIAN PATH
   - King-adjacent: {}/39 transitions
   - Not a valid king's tour path

5. XOR WITH MATRIX
   - Diagonal XOR produces: {}

6. BRIDGE KEY CANDIDATES
   - SHA256(bytes): {}
   - Pair sums: {}

7. SPECIAL POSITIONS
   - (45, 92) = ENTRY → matrix value {}
   - 45 + 92 = 137 (Fine Structure Constant!)
""".format(
    sum(path_values_direct),
    xor_result,
    dict(trit_counts),
    xor_present,
    xor_missing,
    king_adjacent,
    diag_message[:20] + "...",
    sha256_key[:32] + "...",
    pair_sums[:5],
    entry_val
))

# Save results
output_path = "GROK_PATH_DECODED.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")

print("\n" + "=" * 80)
print("Phase 6 Complete: GROK-Pfad Analysis")
print("=" * 80)
