#!/usr/bin/env python3
"""
XOR 127 TOTAL EXTRACTION
========================
Since CFB was found with XOR 127, let's extract ALL readable content
from the entire matrix using this encoding.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
import random
import re

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

print("=" * 70)
print("XOR 127 TOTAL EXTRACTION")
print("=" * 70)

# Extended word list
target_words = [
    # Short (3 chars)
    'cfb', 'key', 'god', 'meg', 'gou', 'fib', 'end', 'all', 'you', 'are', 'the', 'and',
    'one', 'two', 'now', 'way', 'see', 'use', 'can', 'has', 'get', 'new', 'old',
    # Medium (4 chars)
    'code', 'hash', 'seed', 'node', 'sign', 'time', 'find', 'look', 'come', 'here',
    'mega', 'anna', 'jinn', 'game', 'call', 'send', 'wake', 'rise', 'boot', 'init',
    'true', 'zero', 'ones', 'gate', 'open', 'loop', 'next', 'coin', 'mine', 'from',
    # Long (5+ chars) - most significant
    'beyond', 'bridge', 'oracle', 'qubic', 'bitcoin', 'satoshi', 'genesis', 'merkle',
    'aigarth', 'hidden', 'secret', 'cipher', 'decode', 'encode', 'unlock', 'reveal',
    'proof', 'truth', 'begin', 'start', 'ternary', 'binary', 'trinity',
    'creator', 'author', 'master', 'system', 'network', 'neural', 'brain',
    # Names
    'sergey', 'ivancheglo', 'nakamoto',
]

discoveries = []

# =============================================================================
# 1. FULL MATRIX XOR 127
# =============================================================================
print("\n--- Full Matrix XOR 127 ---")

xor127_matrix = (matrix ^ 127) & 0x7F
full_text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in xor127_matrix.flatten()])

print(f"Total printable characters: {sum(1 for c in full_text if c != '.')}")
print(f"First 200 chars: {full_text[:200]}")

# Search for words
for word in target_words:
    pos = 0
    while True:
        pos = full_text.lower().find(word, pos)
        if pos == -1:
            break
        row = pos // 128
        col = pos % 128
        context = full_text[max(0, pos-10):pos+len(word)+10]
        discoveries.append({
            "word": word,
            "position": pos,
            "row": row,
            "col": col,
            "context": context,
            "method": "full_xor127"
        })
        print(f"  '{word}' at pos {pos} (row {row}, col {col}): ...{context}...")
        pos += 1

# =============================================================================
# 2. ROW BY ROW XOR 127
# =============================================================================
print("\n--- Row by Row XOR 127 ---")

for r in range(128):
    row_xor = (matrix[r] ^ 127) & 0x7F
    text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in row_xor])

    # Only report rows with 4+ letter words
    for word in [w for w in target_words if len(w) >= 4]:
        if word in text.lower():
            pos = text.lower().find(word)
            discoveries.append({
                "word": word,
                "position": pos,
                "row": r,
                "col": pos,
                "context": text[max(0, pos-10):pos+len(word)+10],
                "method": f"row_{r}_xor127"
            })
            print(f"  Row {r}: '{word}' at col {pos}")

# =============================================================================
# 3. COLUMN BY COLUMN XOR 127
# =============================================================================
print("\n--- Column by Column XOR 127 ---")

for c in range(128):
    col_xor = (matrix[:, c] ^ 127) & 0x7F
    text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in col_xor])

    for word in [w for w in target_words if len(w) >= 4]:
        if word in text.lower():
            pos = text.lower().find(word)
            discoveries.append({
                "word": word,
                "position": pos,
                "row": pos,
                "col": c,
                "context": text[max(0, pos-10):pos+len(word)+10],
                "method": f"col_{c}_xor127"
            })
            print(f"  Col {c}: '{word}' at row {pos}")

# =============================================================================
# 4. DIAGONAL XOR 127
# =============================================================================
print("\n--- Diagonal XOR 127 ---")

# Main diagonal
main_diag = [(matrix[i][i] ^ 127) & 0x7F for i in range(128)]
text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in main_diag])

for word in target_words:
    if word in text.lower():
        pos = text.lower().find(word)
        print(f"  Main diagonal: '{word}' at pos {pos}")
        discoveries.append({
            "word": word,
            "position": pos,
            "method": "main_diag_xor127",
            "context": text[max(0, pos-10):pos+len(word)+10]
        })

# Anti-diagonal
anti_diag = [(matrix[i][127-i] ^ 127) & 0x7F for i in range(128)]
text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in anti_diag])

for word in target_words:
    if word in text.lower():
        pos = text.lower().find(word)
        print(f"  Anti-diagonal: '{word}' at pos {pos}")
        discoveries.append({
            "word": word,
            "position": pos,
            "method": "anti_diag_xor127",
            "context": text[max(0, pos-10):pos+len(word)+10]
        })

# =============================================================================
# 5. EXTRACT LONG READABLE SEQUENCES
# =============================================================================
print("\n--- Extracting Long Readable Sequences ---")

# Find sequences of 5+ consecutive printable letters
long_sequences = []
current_seq = ""
current_start = 0

for i, c in enumerate(full_text):
    if c.isalpha():
        if not current_seq:
            current_start = i
        current_seq += c
    else:
        if len(current_seq) >= 5:
            row = current_start // 128
            col = current_start % 128
            long_sequences.append({
                "sequence": current_seq,
                "start": current_start,
                "row": row,
                "col": col,
                "length": len(current_seq)
            })
        current_seq = ""

# Sort by length
long_sequences.sort(key=lambda x: -x["length"])

print(f"\nTop 20 longest sequences:")
for seq in long_sequences[:20]:
    print(f"  [{seq['row']:3d},{seq['col']:3d}] len={seq['length']:2d}: {seq['sequence']}")

# =============================================================================
# 6. VALIDATE SIGNIFICANT FINDINGS
# =============================================================================
print("\n--- Validating Significant Findings (4+ chars) ---")

# Group discoveries by word
word_counts = Counter([d["word"] for d in discoveries if len(d["word"]) >= 4])

print("\nWord frequency (4+ chars):")
for word, count in word_counts.most_common(20):
    print(f"  '{word}': {count} occurrences")

# Monte-Carlo validation for words appearing multiple times
print("\nMonte-Carlo validation for frequent words:")
for word, count in word_counts.most_common(5):
    if count >= 2:
        hits = 0
        for _ in range(1000):
            rand_matrix = np.random.choice(matrix.flatten(), size=(128, 128), replace=True)
            rand_xor = (rand_matrix ^ 127) & 0x7F
            rand_text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in rand_xor.flatten()])
            if rand_text.lower().count(word) >= count:
                hits += 1

        p_value = hits / 1000
        sig = "*" if p_value < 0.05 else ""
        print(f"  '{word}' ({count}x): p={p_value:.4f}{sig}")

# =============================================================================
# 7. SEARCH FOR SENTENCE PATTERNS
# =============================================================================
print("\n--- Searching for Sentence Patterns ---")

# Look for patterns like "WORD.WORD" or "WORDWORD"
sentence_patterns = [
    r'[a-z]{4,}\.[a-z]{4,}',  # word.word
    r'[a-z]{4,}[a-z]{4,}',    # wordword
]

for pattern in sentence_patterns:
    matches = re.findall(pattern, full_text.lower())
    if matches:
        print(f"Pattern '{pattern}':")
        for m in matches[:10]:
            print(f"    {m}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("XOR 127 EXTRACTION SUMMARY")
print("=" * 70)

# Unique words found
unique_words = set(d["word"] for d in discoveries)
print(f"\nTotal unique words found: {len(unique_words)}")
print(f"Words (4+ chars): {[w for w in unique_words if len(w) >= 4]}")

print(f"\nTop discoveries:")
for d in sorted(discoveries, key=lambda x: -len(x["word"]))[:10]:
    print(f"  '{d['word']}' at row {d.get('row', '?')}, col {d.get('col', '?')} via {d['method']}")

# Save results
output = {
    "encoding": "XOR 127",
    "total_discoveries": len(discoveries),
    "unique_words": list(unique_words),
    "discoveries": discoveries,
    "long_sequences": long_sequences[:50]
}

output_path = script_dir / "XOR127_EXTRACTION_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Results saved to {output_path}")
