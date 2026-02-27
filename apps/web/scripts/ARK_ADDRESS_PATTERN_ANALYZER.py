#!/usr/bin/env python3
"""
ARK ADDRESS PATTERN ANALYZER
Looking for hidden patterns in the address itself
"""

import json
from pathlib import Path
from collections import Counter
import numpy as np

ARK = "ARKMGCWFYEHJFAVSGKEXVWBGGXZAVLZNBDNBZEXTQBKLKRPEYPEIEKFHUPNG"

print("="*80)
print("ARK ADDRESS - DEEP PATTERN ANALYSIS")
print("="*80)

print(f"\nAddress: {ARK}")
print(f"Length: {len(ARK)}")

# Character frequency
print(f"\n{'='*80}")
print("CHARACTER FREQUENCY ANALYSIS")
print(f"{'='*80}")

counter = Counter(ARK)
print(f"\nMost common characters:")
for char, count in counter.most_common(10):
    percentage = count / len(ARK) * 100
    print(f"   {char}: {count} times ({percentage:.1f}%)")

# Check for repeated sequences
print(f"\n{'='*80}")
print("REPEATED SEQUENCES")
print(f"{'='*80}")

print(f"\n2-character sequences:")
for i in range(len(ARK)-1):
    seq = ARK[i:i+2]
    count = ARK.count(seq)
    if count > 2:
        print(f"   '{seq}' appears {count} times")

print(f"\n3-character sequences:")
for i in range(len(ARK)-2):
    seq = ARK[i:i+3]
    count = ARK.count(seq)
    if count > 1:
        positions = [j for j in range(len(ARK)-2) if ARK[j:j+3] == seq]
        print(f"   '{seq}' appears {count} times at positions {positions}")

# Chunk analysis
print(f"\n{'='*80}")
print("CHUNKING ANALYSIS")
print(f"{'='*80}")

# Split into meaningful chunks
chunks_4 = [ARK[i:i+4] for i in range(0, len(ARK), 4)]
print(f"\n4-character chunks (15 chunks):")
for i, chunk in enumerate(chunks_4):
    print(f"   {i:2d}. {chunk}")

# Check for palindromes
print(f"\n{'='*80}")
print("PALINDROME SEARCH")
print(f"{'='*80}")

palindromes = []
for length in range(3, 8):
    for i in range(len(ARK) - length + 1):
        substring = ARK[i:i+length]
        if substring == substring[::-1]:
            palindromes.append((i, substring))

if palindromes:
    print(f"\nFound {len(palindromes)} palindromes:")
    for pos, pal in palindromes:
        print(f"   Position {pos}: '{pal}'")
else:
    print(f"\nNo palindromes found")

# Check for arithmetic patterns in character values
print(f"\n{'='*80}")
print("ARITHMETIC PATTERNS")
print(f"{'='*80}")

def char_to_num(c):
    return ord(c.upper()) - ord('A') if c.isalpha() else 0

char_values = [char_to_num(c) for c in ARK]

print(f"\nFirst 20 character values:")
print(f"   {char_values[:20]}")

# Check for arithmetic sequences
print(f"\nLooking for arithmetic sequences (consecutive increases):")
for start in range(len(char_values) - 3):
    window = char_values[start:start+4]
    diffs = [window[i+1] - window[i] for i in range(3)]
    if len(set(diffs)) == 1 and diffs[0] != 0:  # All diffs are same
        print(f"   Position {start}: {ARK[start:start+4]} → {window} (diff={diffs[0]})")

# Check prefix/suffix patterns
print(f"\n{'='*80}")
print("PREFIX/SUFFIX ANALYSIS")
print(f"{'='*80}")

print(f"\nPrefix (first 10): {ARK[:10]}")
print(f"   Sum: {sum(char_to_num(c) for c in ARK[:10])}")

print(f"\nSuffix (last 10): {ARK[-10:]}")
print(f"   Sum: {sum(char_to_num(c) for c in ARK[-10:])}")

middle_start = (len(ARK) - 10) // 2
print(f"\nMiddle (chars {middle_start}-{middle_start+10}): {ARK[middle_start:middle_start+10]}")
print(f"   Sum: {sum(char_to_num(c) for c in ARK[middle_start:middle_start+10])}")

# Check if it encodes something specific
print(f"\n{'='*80}")
print("SPECIAL ENCODINGS")
print(f"{'='*80}")

# Check if prefix spells something
prefixes = ["ARK", "ANNA", "CFB", "GENESIS", "EXODUS", "POCC", "HASV"]
print(f"\nChecking for word prefixes:")
for prefix in prefixes:
    if ARK.startswith(prefix):
        print(f"   ✓ Starts with '{prefix}'")

# Check for "ANNA" anywhere
if "ANNA" in ARK:
    pos = ARK.find("ANNA")
    print(f"\n⭐ 'ANNA' found at position {pos}!")
else:
    print(f"\n   'ANNA' not found in address")

# Check for numbers if we interpret as Base26
print(f"\n{'='*80}")
print("SYMMETRY ANALYSIS")
print(f"{'='*80}")

# Check for mirror symmetry
half = len(ARK) // 2
first_half = ARK[:half]
second_half = ARK[half:]

print(f"\nFirst half:  {first_half}")
print(f"Second half: {second_half}")
print(f"Reversed 2nd: {second_half[::-1]}")

# Check character overlap
common = set(first_half) & set(second_half)
print(f"\nCommon characters in both halves: {sorted(common)}")
print(f"   Count: {len(common)}/26 letters")

# Load matrix for deeper check
print(f"\n{'='*80}")
print("MATRIX VALUE PATTERNS")
print(f"{'='*80}")

try:
    matrix_path = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
    with open(matrix_path, 'r') as f:
        data = json.load(f)
        matrix = np.array(data['matrix'], dtype=np.float64)

    # Check if address encodes a path through matrix
    print(f"\nChecking if address is a MATRIX PATH...")

    # Pairs as coordinates
    path_values = []
    for i in range(0, len(char_values)-1, 2):
        row = char_values[i]
        col = char_values[i+1]
        if row < 128 and col < 128:
            val = matrix[row][col]
            path_values.append(val)
            if i < 20:  # Show first 10 pairs
                print(f"   [{row:2d},{col:2d}] = {val:6.0f}")

    print(f"\n   Path sum: {sum(path_values):.0f}")
    print(f"   Path average: {np.mean(path_values):.2f}")

    # Check if path sum is special
    if abs(sum(path_values)) % 676 == 0:
        print(f"   ⭐ Path sum is multiple of 676!")

except Exception as e:
    print(f"   Could not load matrix: {e}")

print(f"\n{'='*80}")
print("NOTABLE FINDINGS")
print(f"{'='*80}")

findings = []

# Check what we found
if ARK.startswith("ARK"):
    findings.append("✓ Starts with 'ARK' (obviously)")

if len([c for c in counter if counter[c] > 4]) > 0:
    findings.append(f"✓ Has {len([c for c in counter if counter[c] > 4])} frequently repeated characters")

if len(palindromes) > 0:
    findings.append(f"✓ Contains {len(palindromes)} palindromic sequences")

if findings:
    print("\n" + "\n".join(findings))
else:
    print("\nNo special patterns found")

print(f"\n{'='*80}")
print("ANALYSIS COMPLETE")
print(f"{'='*80}")
