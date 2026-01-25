#!/usr/bin/env python3
"""
===============================================================================
        PRIORITY 4: COMPLETE XOR HEATMAP ANALYSIS
===============================================================================
Systematically analyze ALL 64 symmetric column pairs and row pairs.
Generate data for interactive visualization.
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter
import re

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   ██╗  ██╗ ██████╗ ██████╗     ██╗  ██╗███████╗ █████╗ ████████╗███╗   ███╗ █████╗ ██████╗
   ╚██╗██╔╝██╔═══██╗██╔══██╗    ██║  ██║██╔════╝██╔══██╗╚══██╔══╝████╗ ████║██╔══██╗██╔══██╗
    ╚███╔╝ ██║   ██║██████╔╝    ███████║█████╗  ███████║   ██║   ██╔████╔██║███████║██████╔╝
    ██╔██╗ ██║   ██║██╔══██╗    ██╔══██║██╔══╝  ██╔══██║   ██║   ██║╚██╔╝██║██╔══██║██╔═══╝
   ██╔╝ ██╗╚██████╔╝██║  ██║    ██║  ██║███████╗██║  ██║   ██║   ██║ ╚═╝ ██║██║  ██║██║
   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝
                          PRIORITY 4: XOR HEATMAP
""")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# Common English words for detection
ENGLISH_WORDS = set([
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
    'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
    'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
    'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
    'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
    'ai', 'meg', 'gou', 'ice', 'key', 'code', 'data', 'bit', 'byte', 'hash',
    'seed', 'tree', 'root', 'node', 'link', 'path', 'file', 'name', 'type', 'value',
    'matrix', 'anna', 'cfb', 'qubic', 'coin', 'block', 'chain', 'mine', 'satoshi',
    'message', 'secret', 'hidden', 'encode', 'decode', 'cipher', 'crypt', 'mirror'
])

def find_words(text, min_length=3):
    """Find English words in text"""
    text = text.lower()
    found = []
    for word in ENGLISH_WORDS:
        if len(word) >= min_length and word in text:
            # Find all occurrences
            start = 0
            while True:
                pos = text.find(word, start)
                if pos == -1:
                    break
                found.append((word, pos))
                start = pos + 1
    return found

def find_longest_palindrome(s):
    """Find longest palindrome in string"""
    if len(s) == 0:
        return ""
    longest = s[0]
    for i in range(len(s)):
        # Odd length
        l, r = i, i
        while l >= 0 and r < len(s) and s[l] == s[r]:
            if r - l + 1 > len(longest):
                longest = s[l:r+1]
            l -= 1
            r += 1
        # Even length
        l, r = i, i + 1
        while l >= 0 and r < len(s) and s[l] == s[r]:
            if r - l + 1 > len(longest):
                longest = s[l:r+1]
            l -= 1
            r += 1
    return longest

# ==============================================================================
# PHASE 1: COLUMN PAIR XOR ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 1: COLUMN PAIR XOR ANALYSIS (64 pairs)")
print("=" * 80)

column_results = []

for c in range(64):  # 0-63 pairs with 127-63 down to 64
    c2 = 127 - c

    # XOR the two columns
    xor_col = []
    for r in range(128):
        val = int(matrix[r, c]) ^ int(matrix[r, c2])
        xor_col.append(val)

    # Convert to ASCII string (printable chars only)
    ascii_str = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in xor_col)

    # Find words
    words = find_words(ascii_str)
    unique_words = list(set([w for w, p in words]))

    # Find palindromes
    palindrome = find_longest_palindrome(ascii_str)

    # Count asymmetric cells (where XOR != 0)
    asymmetric = sum(1 for v in xor_col if v != 0)

    result = {
        "column_pair": [c, c2],
        "asymmetric_cells": asymmetric,
        "ascii_length": len(ascii_str),
        "words_found": unique_words,
        "word_count": len(unique_words),
        "longest_palindrome": palindrome if len(palindrome) > 3 else "",
        "palindrome_length": len(palindrome) if len(palindrome) > 3 else 0,
        "raw_xor": xor_col,
        "ascii_string": ascii_str[:100]  # First 100 chars
    }

    column_results.append(result)

    if unique_words or len(palindrome) > 10:
        print(f"\n  Column {c} ⊕ {c2}:")
        print(f"    Asymmetric cells: {asymmetric}")
        print(f"    Words: {unique_words[:5]}")
        if len(palindrome) > 10:
            print(f"    Palindrome ({len(palindrome)}): {palindrome[:50]}...")

# Sort by significance
column_results_sorted = sorted(column_results, key=lambda x: (x["word_count"], x["palindrome_length"]), reverse=True)

print(f"\n  Top 10 Column Pairs by Word Count:")
for i, res in enumerate(column_results_sorted[:10], 1):
    c, c2 = res["column_pair"]
    print(f"    {i}. Col {c}⊕{c2}: {res['word_count']} words, {res['asymmetric_cells']} asymmetric")

# ==============================================================================
# PHASE 2: ROW PAIR XOR ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 2: ROW PAIR XOR ANALYSIS (64 pairs)")
print("=" * 80)

row_results = []

for r in range(64):
    r2 = 127 - r

    # XOR the two rows
    xor_row = []
    for c in range(128):
        val = int(matrix[r, c]) ^ int(matrix[r2, c])
        xor_row.append(val)

    # Convert to ASCII string
    ascii_str = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in xor_row)

    # Find words
    words = find_words(ascii_str)
    unique_words = list(set([w for w, p in words]))

    # Find palindromes
    palindrome = find_longest_palindrome(ascii_str)

    # Count asymmetric cells
    asymmetric = sum(1 for v in xor_row if v != 0)

    result = {
        "row_pair": [r, r2],
        "asymmetric_cells": asymmetric,
        "ascii_length": len(ascii_str),
        "words_found": unique_words,
        "word_count": len(unique_words),
        "longest_palindrome": palindrome if len(palindrome) > 3 else "",
        "palindrome_length": len(palindrome) if len(palindrome) > 3 else 0,
        "raw_xor": xor_row,
        "ascii_string": ascii_str[:100]
    }

    row_results.append(result)

    if len(palindrome) > 40:
        print(f"\n  Row {r} ⊕ {r2}:")
        print(f"    Palindrome ({len(palindrome)}): {palindrome[:60]}...")

# Sort by palindrome length
row_results_sorted = sorted(row_results, key=lambda x: x["palindrome_length"], reverse=True)

print(f"\n  Top 10 Row Pairs by Palindrome Length:")
for i, res in enumerate(row_results_sorted[:10], 1):
    r, r2 = res["row_pair"]
    print(f"    {i}. Row {r}⊕{r2}: {res['palindrome_length']} char palindrome, {res['word_count']} words")

# ==============================================================================
# PHASE 3: HEATMAP DATA GENERATION
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3: GENERATING HEATMAP DATA")
print("=" * 80)

# Create heatmap matrices
word_heatmap = np.zeros((64, 64))  # Rows x Columns
palindrome_heatmap = np.zeros((64, 64))
asymmetric_heatmap = np.zeros((64, 64))

# For each row pair, compute metrics against each column pair
print("\n  Computing cross-correlations...")

for ri, r_res in enumerate(row_results):
    r, r2 = r_res["row_pair"]

    for ci, c_res in enumerate(column_results):
        c, c2 = c_res["column_pair"]

        # Get XOR value at intersection
        xor_val = int(matrix[r, c]) ^ int(matrix[r2, c2])

        # Store metrics
        word_heatmap[ri, ci] = r_res["word_count"] + c_res["word_count"]
        palindrome_heatmap[ri, ci] = r_res["palindrome_length"] + c_res["palindrome_length"]
        asymmetric_heatmap[ri, ci] = r_res["asymmetric_cells"] + c_res["asymmetric_cells"]

# Find hotspots
print("\n  Word Count Hotspots:")
hotspots = np.where(word_heatmap == word_heatmap.max())
for ri, ci in zip(hotspots[0], hotspots[1]):
    r_pair = row_results[ri]["row_pair"]
    c_pair = column_results[ci]["column_pair"]
    print(f"    Row {r_pair[0]}↔{r_pair[1]} × Col {c_pair[0]}↔{c_pair[1]}: {word_heatmap[ri, ci]} words")

print("\n  Palindrome Length Hotspots:")
hotspots = np.where(palindrome_heatmap == palindrome_heatmap.max())
for ri, ci in zip(hotspots[0], hotspots[1]):
    r_pair = row_results[ri]["row_pair"]
    c_pair = column_results[ci]["column_pair"]
    print(f"    Row {r_pair[0]}↔{r_pair[1]} × Col {c_pair[0]}↔{c_pair[1]}: {palindrome_heatmap[ri, ci]} chars")

# ==============================================================================
# PHASE 4: STATISTICS
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 4: STATISTICAL SUMMARY")
print("=" * 80)

total_words_cols = sum(r["word_count"] for r in column_results)
total_words_rows = sum(r["word_count"] for r in row_results)
total_palindromes = sum(1 for r in row_results if r["palindrome_length"] > 10)

print(f"""
  Column Pair Statistics:
    Total word occurrences: {total_words_cols}
    Pairs with words: {sum(1 for r in column_results if r['word_count'] > 0)}
    Max words in single pair: {max(r['word_count'] for r in column_results)}

  Row Pair Statistics:
    Total word occurrences: {total_words_rows}
    Pairs with palindromes > 10 chars: {total_palindromes}
    Max palindrome length: {max(r['palindrome_length'] for r in row_results)}

  Combined Heatmap:
    Word hotspot max: {word_heatmap.max()}
    Palindrome hotspot max: {palindrome_heatmap.max()}
""")

# ==============================================================================
# PHASE 5: EXPORT DATA FOR VISUALIZATION
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 5: EXPORTING DATA FOR VISUALIZATION")
print("=" * 80)

# Prepare export data
export_data = {
    "timestamp": datetime.now().isoformat(),
    "column_pairs": [
        {
            "pair": r["column_pair"],
            "words": r["words_found"],
            "word_count": r["word_count"],
            "palindrome_length": r["palindrome_length"],
            "asymmetric": r["asymmetric_cells"],
            "preview": r["ascii_string"][:50]
        }
        for r in column_results
    ],
    "row_pairs": [
        {
            "pair": r["row_pair"],
            "words": r["words_found"],
            "word_count": r["word_count"],
            "palindrome": r["longest_palindrome"][:100] if r["longest_palindrome"] else "",
            "palindrome_length": r["palindrome_length"],
            "asymmetric": r["asymmetric_cells"],
            "preview": r["ascii_string"][:50]
        }
        for r in row_results
    ],
    "heatmaps": {
        "word_counts": word_heatmap.tolist(),
        "palindrome_lengths": palindrome_heatmap.tolist(),
        "asymmetric_counts": asymmetric_heatmap.tolist()
    },
    "statistics": {
        "total_words_cols": total_words_cols,
        "total_words_rows": total_words_rows,
        "max_palindrome": max(r['palindrome_length'] for r in row_results),
        "pairs_with_words": sum(1 for r in column_results if r['word_count'] > 0)
    },
    "top_findings": {
        "best_column_pairs": [
            {"pair": r["column_pair"], "words": r["words_found"][:10]}
            for r in column_results_sorted[:5]
        ],
        "best_row_pairs": [
            {"pair": r["row_pair"], "palindrome_length": r["palindrome_length"]}
            for r in row_results_sorted[:5]
        ]
    }
}

# Save main results
output_path = script_dir / "PRIORITY4_XOR_HEATMAP_DATA.json"
with open(output_path, "w") as f:
    json.dump(export_data, f, indent=2)

print(f"  ✓ Heatmap data saved to: {output_path.name}")

# Save compact version for web visualization
web_data = {
    "wordHeatmap": word_heatmap.tolist(),
    "palindromeHeatmap": palindrome_heatmap.tolist(),
    "columnLabels": [f"{r['column_pair'][0]}↔{r['column_pair'][1]}" for r in column_results],
    "rowLabels": [f"{r['row_pair'][0]}↔{r['row_pair'][1]}" for r in row_results],
    "topColumnPairs": [
        {
            "pair": r["column_pair"],
            "words": r["words_found"][:5],
            "wordCount": r["word_count"]
        }
        for r in column_results_sorted[:10]
    ],
    "topRowPairs": [
        {
            "pair": r["row_pair"],
            "palindrome": r["longest_palindrome"][:50] if r["longest_palindrome"] else "",
            "length": r["palindrome_length"]
        }
        for r in row_results_sorted[:10]
    ]
}

web_path = script_dir.parent / "public" / "data" / "xor-heatmap-data.json"
with open(web_path, "w") as f:
    json.dump(web_data, f, indent=2)

print(f"  ✓ Web visualization data saved to: public/data/xor-heatmap-data.json")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("XOR HEATMAP ANALYSIS COMPLETE")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         XOR HEATMAP SUMMARY                                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  COLUMN PAIR XOR (64 pairs):                                                  ║
║    • Total words found: {total_words_cols:4d}                                              ║
║    • Pairs with words: {sum(1 for r in column_results if r['word_count'] > 0):4d}                                               ║
║    • Best pair: Col {column_results_sorted[0]['column_pair'][0]}↔{column_results_sorted[0]['column_pair'][1]} ({column_results_sorted[0]['word_count']} words)                               ║
║                                                                               ║
║  ROW PAIR XOR (64 pairs):                                                     ║
║    • Pairs with palindromes: {total_palindromes:3d}                                           ║
║    • Max palindrome: {max(r['palindrome_length'] for r in row_results):3d} characters                                        ║
║    • Best pair: Row {row_results_sorted[0]['row_pair'][0]}↔{row_results_sorted[0]['row_pair'][1]}                                               ║
║                                                                               ║
║  FILES GENERATED:                                                             ║
║    • PRIORITY4_XOR_HEATMAP_DATA.json (full analysis)                          ║
║    • public/data/xor-heatmap-data.json (web visualization)                    ║
║                                                                               ║
║  NEXT: Create React component to visualize heatmap                            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")
