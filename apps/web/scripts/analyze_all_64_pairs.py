#!/usr/bin/env python3
"""
CRITICAL RESEARCH: Analyze ALL 64 Column Pairs Where Col_A + Col_B = 127

The 127 Formula Discovery: All known anomaly column pairs sum to 127.
Only 3 of 64 possible pairs have been tested - 95% of encoding space unexplored!

This script performs comprehensive analysis of all 64 column pairs.
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

# Paths
MATRIX_PATH = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json"
OUTPUT_PATH = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/ALL_64_PAIRS_ANALYSIS.json"

# Pattern keywords to search for
KEYWORDS = ['FIB', 'TX', 'CFB', 'BTC', 'KEY', 'SEED', 'HASH', 'BLOCK', 'GENESIS',
            'ANNA', 'BRIDGE', 'QUBIC', 'SATOSHI', 'COIN', 'WALLET', 'SIGN',
            'NONCE', 'MERKLE', 'SCRIPT', 'OP_', 'P2PKH', 'P2SH', 'ADDRESS']

# Row windows to analyze
ROW_WINDOWS = [
    ("all", 0, 128),
    ("first_quarter", 0, 32),
    ("second_quarter", 32, 64),
    ("third_quarter", 64, 96),
    ("fourth_quarter", 96, 128),
    ("first_half", 0, 64),
    ("second_half", 64, 128),
    ("middle", 32, 96),
]


def load_matrix() -> List[List[int]]:
    """Load the Anna Matrix from JSON file."""
    print(f"Loading matrix from: {MATRIX_PATH}")
    with open(MATRIX_PATH, 'r') as f:
        data = json.load(f)
    matrix = data.get('matrix', data)
    print(f"Matrix dimensions: {len(matrix)} rows x {len(matrix[0])} columns")
    return matrix


def is_printable_ascii(value: int) -> bool:
    """Check if value is in printable ASCII range (32-126)."""
    return 32 <= value <= 126


def safe_int_value(val: Any) -> int:
    """Safely convert a value to int, handling strings and other types."""
    if isinstance(val, int):
        return val
    elif isinstance(val, str):
        # Try to parse as integer
        try:
            return int(val)
        except ValueError:
            # If it looks like binary string "00000000", treat as 0
            if val.replace('0', '').replace('1', '') == '':
                return int(val, 2) if val else 0
            return 0
    elif isinstance(val, float):
        return int(val)
    else:
        return 0


def compute_xor_column_pair(matrix: List[List[int]], col_a: int, col_b: int) -> List[int]:
    """Compute XOR values between two columns for all rows."""
    xor_values = []
    for row in matrix:
        val_a = safe_int_value(row[col_a]) if col_a < len(row) else 0
        val_b = safe_int_value(row[col_b]) if col_b < len(row) else 0
        # Handle negative values by taking modulo 256
        val_a = val_a % 256
        val_b = val_b % 256
        xor_values.append(val_a ^ val_b)
    return xor_values


def analyze_printability(xor_values: List[int]) -> Dict[str, Any]:
    """Analyze the printability of XOR values."""
    total = len(xor_values)
    printable_count = sum(1 for v in xor_values if is_printable_ascii(v))
    printable_ratio = printable_count / total if total > 0 else 0

    # Find printable sequences
    sequences = []
    current_seq = []
    current_start = 0

    for i, v in enumerate(xor_values):
        if is_printable_ascii(v):
            if not current_seq:
                current_start = i
            current_seq.append(chr(v))
        else:
            if len(current_seq) >= 3:
                sequences.append({
                    "start_row": current_start,
                    "end_row": i - 1,
                    "length": len(current_seq),
                    "text": "".join(current_seq)
                })
            current_seq = []

    # Handle sequence at end
    if len(current_seq) >= 3:
        sequences.append({
            "start_row": current_start,
            "end_row": len(xor_values) - 1,
            "length": len(current_seq),
            "text": "".join(current_seq)
        })

    return {
        "printable_count": printable_count,
        "total_count": total,
        "printable_ratio": printable_ratio,
        "printable_percentage": round(printable_ratio * 100, 2),
        "sequences": sequences,
        "longest_sequence": max([s["length"] for s in sequences], default=0)
    }


def find_keyword_matches(text: str) -> List[Dict[str, Any]]:
    """Find keyword pattern matches in text."""
    matches = []
    text_upper = text.upper()

    for keyword in KEYWORDS:
        # Find all occurrences
        start = 0
        while True:
            idx = text_upper.find(keyword, start)
            if idx == -1:
                break
            matches.append({
                "keyword": keyword,
                "position": idx,
                "context": text[max(0, idx-5):min(len(text), idx+len(keyword)+5)]
            })
            start = idx + 1

    return matches


def extract_readable_words(text: str) -> List[str]:
    """Extract potential readable words (3+ alpha characters)."""
    # Find sequences of 3+ letters
    words = re.findall(r'[a-zA-Z]{3,}', text)
    return words


def analyze_row_window(matrix: List[List[int]], col_a: int, col_b: int,
                       start_row: int, end_row: int) -> Dict[str, Any]:
    """Analyze a specific row window for a column pair."""
    xor_values = []
    for row_idx in range(start_row, min(end_row, len(matrix))):
        row = matrix[row_idx]
        val_a = safe_int_value(row[col_a]) % 256 if col_a < len(row) else 0
        val_b = safe_int_value(row[col_b]) % 256 if col_b < len(row) else 0
        xor_values.append(val_a ^ val_b)

    # Convert to text
    text = ""
    for v in xor_values:
        if is_printable_ascii(v):
            text += chr(v)
        else:
            text += "."

    printability = analyze_printability(xor_values)
    keywords = find_keyword_matches(text)
    words = extract_readable_words(text)

    return {
        "row_range": f"{start_row}-{end_row}",
        "xor_values": xor_values,
        "text_representation": text,
        "printability": printability,
        "keyword_matches": keywords,
        "readable_words": words,
        "word_count": len(words)
    }


def compute_pair_score(analysis: Dict[str, Any]) -> float:
    """Compute an overall interest score for a column pair."""
    score = 0.0

    # Printability contributes most
    full_analysis = analysis.get("full_analysis", {})
    printability = full_analysis.get("printability", {})
    score += printability.get("printable_percentage", 0) * 2

    # Long sequences are very interesting
    score += printability.get("longest_sequence", 0) * 5

    # Keyword matches are extremely interesting
    keywords = full_analysis.get("keyword_matches", [])
    score += len(keywords) * 20

    # Readable words add to score
    words = full_analysis.get("readable_words", [])
    score += len(words) * 3

    # Bonus for specific important keywords
    important_keywords = {'CFB', 'BTC', 'KEY', 'SEED', 'GENESIS', 'SATOSHI', 'BRIDGE'}
    for kw in keywords:
        if kw.get("keyword", "").upper() in important_keywords:
            score += 50

    return score


def analyze_column_pair(matrix: List[List[int]], col_a: int, col_b: int) -> Dict[str, Any]:
    """Perform comprehensive analysis of a column pair."""
    print(f"  Analyzing pair {col_a} <-> {col_b}...")

    # Full XOR analysis
    xor_values = compute_xor_column_pair(matrix, col_a, col_b)

    # Convert to text representation
    full_text = ""
    for v in xor_values:
        if is_printable_ascii(v):
            full_text += chr(v)
        else:
            full_text += "."

    # Analyze full matrix
    full_printability = analyze_printability(xor_values)
    full_keywords = find_keyword_matches(full_text)
    full_words = extract_readable_words(full_text)

    full_analysis = {
        "xor_values": xor_values,
        "text_representation": full_text,
        "printability": full_printability,
        "keyword_matches": full_keywords,
        "readable_words": full_words,
        "word_count": len(full_words)
    }

    # Analyze each row window
    window_analyses = {}
    for window_name, start, end in ROW_WINDOWS:
        if window_name != "all":
            window_analyses[window_name] = analyze_row_window(matrix, col_a, col_b, start, end)

    result = {
        "column_a": col_a,
        "column_b": col_b,
        "sum": col_a + col_b,
        "full_analysis": full_analysis,
        "window_analyses": window_analyses
    }

    # Compute interest score
    result["interest_score"] = compute_pair_score(result)

    return result


def generate_executive_summary(all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate executive summary of the analysis."""
    # Sort by interest score
    sorted_results = sorted(all_results, key=lambda x: x["interest_score"], reverse=True)

    # Top 10 most interesting pairs
    top_10 = []
    for r in sorted_results[:10]:
        full = r.get("full_analysis", {})
        printability = full.get("printability", {})
        top_10.append({
            "rank": len(top_10) + 1,
            "columns": f"{r['column_a']} <-> {r['column_b']}",
            "score": r["interest_score"],
            "printable_pct": printability.get("printable_percentage", 0),
            "longest_sequence": printability.get("longest_sequence", 0),
            "keyword_count": len(full.get("keyword_matches", [])),
            "word_count": len(full.get("readable_words", [])),
            "sample_text": full.get("text_representation", "")[:100]
        })

    # Statistics
    all_scores = [r["interest_score"] for r in all_results]
    all_printable = [r.get("full_analysis", {}).get("printability", {}).get("printable_percentage", 0)
                    for r in all_results]

    # Pairs with keyword matches
    pairs_with_keywords = [r for r in all_results
                          if len(r.get("full_analysis", {}).get("keyword_matches", [])) > 0]

    # Pairs with high printability (>50%)
    high_printability_pairs = [r for r in all_results
                               if r.get("full_analysis", {}).get("printability", {}).get("printable_percentage", 0) > 50]

    return {
        "analysis_timestamp": datetime.now().isoformat(),
        "total_pairs_analyzed": len(all_results),
        "formula_verified": "All pairs sum to 127",
        "statistics": {
            "average_score": sum(all_scores) / len(all_scores) if all_scores else 0,
            "max_score": max(all_scores) if all_scores else 0,
            "min_score": min(all_scores) if all_scores else 0,
            "average_printability": sum(all_printable) / len(all_printable) if all_printable else 0,
            "pairs_with_keywords": len(pairs_with_keywords),
            "high_printability_pairs": len(high_printability_pairs)
        },
        "top_10_pairs": top_10,
        "pairs_with_keywords": [
            {
                "columns": f"{r['column_a']} <-> {r['column_b']}",
                "keywords_found": [k["keyword"] for k in r.get("full_analysis", {}).get("keyword_matches", [])]
            }
            for r in pairs_with_keywords
        ]
    }


def deep_analyze_top_pairs(matrix: List[List[int]], top_results: List[Dict[str, Any]], n: int = 5) -> List[Dict[str, Any]]:
    """Perform deep analysis on the top N pairs."""
    deep_analyses = []

    print(f"\n{'='*60}")
    print(f"DEEP ANALYSIS: Top {n} Pairs")
    print(f"{'='*60}")

    for i, result in enumerate(top_results[:n]):
        col_a = result["column_a"]
        col_b = result["column_b"]
        print(f"\n--- Deep Analysis: Pair {col_a} <-> {col_b} (Rank #{i+1}) ---")

        full = result.get("full_analysis", {})

        # Extract all complete ASCII sequences
        sequences = full.get("printability", {}).get("sequences", [])

        # Analyze different interpretations
        xor_values = full.get("xor_values", [])

        # Try different byte orderings
        interpretations = {}

        # Standard order
        standard_text = "".join(chr(v) if is_printable_ascii(v) else "." for v in xor_values)
        interpretations["standard"] = standard_text

        # Reverse order
        reverse_text = "".join(chr(v) if is_printable_ascii(v) else "." for v in reversed(xor_values))
        interpretations["reverse"] = reverse_text

        # Every other byte (even positions)
        even_text = "".join(chr(xor_values[i]) if is_printable_ascii(xor_values[i]) else "."
                           for i in range(0, len(xor_values), 2))
        interpretations["even_positions"] = even_text

        # Every other byte (odd positions)
        odd_text = "".join(chr(xor_values[i]) if is_printable_ascii(xor_values[i]) else "."
                          for i in range(1, len(xor_values), 2))
        interpretations["odd_positions"] = odd_text

        # Interleaved (zigzag)
        zigzag = []
        for i in range(min(len(xor_values)//2, 64)):
            zigzag.append(xor_values[i])
            zigzag.append(xor_values[-(i+1)])
        zigzag_text = "".join(chr(v) if is_printable_ascii(v) else "." for v in zigzag)
        interpretations["zigzag"] = zigzag_text

        # Window-specific coherent messages
        window_messages = {}
        for window_name, window_data in result.get("window_analyses", {}).items():
            text = window_data.get("text_representation", "")
            seqs = window_data.get("printability", {}).get("sequences", [])
            if seqs:
                best_seq = max(seqs, key=lambda x: x["length"])
                if best_seq["length"] >= 5:
                    window_messages[window_name] = {
                        "best_sequence": best_seq["text"],
                        "row_range": f"{best_seq['start_row']}-{best_seq['end_row']}",
                        "length": best_seq["length"]
                    }

        deep_analysis = {
            "rank": i + 1,
            "columns": f"{col_a} <-> {col_b}",
            "interest_score": result["interest_score"],
            "ascii_sequences": sequences,
            "interpretations": interpretations,
            "window_messages": window_messages,
            "readable_words_found": full.get("readable_words", []),
            "keyword_matches_detail": full.get("keyword_matches", [])
        }

        deep_analyses.append(deep_analysis)

        # Print summary
        print(f"  Score: {result['interest_score']:.1f}")
        print(f"  Sequences found: {len(sequences)}")
        print(f"  Longest sequence: {max([s['length'] for s in sequences], default=0)} chars")
        if full.get("keyword_matches"):
            print(f"  Keywords: {[k['keyword'] for k in full['keyword_matches']]}")
        if full.get("readable_words"):
            print(f"  Words: {full['readable_words'][:10]}")

    return deep_analyses


def main():
    """Main execution function."""
    print("="*70)
    print("CRITICAL RESEARCH: ALL 64 COLUMN PAIRS ANALYSIS")
    print("The 127 Formula - Testing Complete Encoding Space")
    print("="*70)
    print()

    # Load matrix
    matrix = load_matrix()

    if len(matrix) < 128 or len(matrix[0]) < 128:
        print(f"WARNING: Matrix dimensions ({len(matrix)}x{len(matrix[0])}) may be smaller than expected (128x128)")

    # Generate all 64 column pairs where col_a + col_b = 127
    pairs = [(i, 127 - i) for i in range(64)]

    print(f"\nAnalyzing {len(pairs)} column pairs where Col_A + Col_B = 127...")
    print("-" * 60)

    all_results = []

    for col_a, col_b in pairs:
        result = analyze_column_pair(matrix, col_a, col_b)
        all_results.append(result)

        # Quick status
        full = result.get("full_analysis", {})
        printability = full.get("printability", {})
        print(f"    Printability: {printability.get('printable_percentage', 0):.1f}% | "
              f"Longest seq: {printability.get('longest_sequence', 0)} | "
              f"Score: {result['interest_score']:.1f}")

    # Sort by interest score
    all_results_sorted = sorted(all_results, key=lambda x: x["interest_score"], reverse=True)

    # Generate executive summary
    print("\n" + "="*60)
    print("GENERATING EXECUTIVE SUMMARY")
    print("="*60)

    executive_summary = generate_executive_summary(all_results)

    # Deep analysis of top 5 pairs
    deep_analyses = deep_analyze_top_pairs(matrix, all_results_sorted, n=5)

    # Compile final output
    output = {
        "executive_summary": executive_summary,
        "deep_analysis_top_5": deep_analyses,
        "all_pair_results": [
            {
                "column_a": r["column_a"],
                "column_b": r["column_b"],
                "interest_score": r["interest_score"],
                "printable_percentage": r.get("full_analysis", {}).get("printability", {}).get("printable_percentage", 0),
                "longest_sequence": r.get("full_analysis", {}).get("printability", {}).get("longest_sequence", 0),
                "keyword_count": len(r.get("full_analysis", {}).get("keyword_matches", [])),
                "word_count": len(r.get("full_analysis", {}).get("readable_words", [])),
                "full_text": r.get("full_analysis", {}).get("text_representation", ""),
                "sequences": r.get("full_analysis", {}).get("printability", {}).get("sequences", []),
                "keywords": r.get("full_analysis", {}).get("keyword_matches", []),
                "words": r.get("full_analysis", {}).get("readable_words", [])
            }
            for r in all_results_sorted
        ]
    }

    # Save results
    print(f"\nSaving results to: {OUTPUT_PATH}")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)

    # Print final summary
    print("\n" + "="*70)
    print("EXECUTIVE SUMMARY")
    print("="*70)

    print(f"\nTotal pairs analyzed: {executive_summary['total_pairs_analyzed']}")
    print(f"Formula verified: {executive_summary['formula_verified']}")
    print(f"\nStatistics:")
    stats = executive_summary['statistics']
    print(f"  - Average interest score: {stats['average_score']:.1f}")
    print(f"  - Max interest score: {stats['max_score']:.1f}")
    print(f"  - Average printability: {stats['average_printability']:.1f}%")
    print(f"  - Pairs with keyword matches: {stats['pairs_with_keywords']}")
    print(f"  - High printability pairs (>50%): {stats['high_printability_pairs']}")

    print(f"\n{'='*70}")
    print("TOP 10 MOST INTERESTING PAIRS")
    print("="*70)

    for entry in executive_summary['top_10_pairs']:
        print(f"\n#{entry['rank']}: Columns {entry['columns']}")
        print(f"   Score: {entry['score']:.1f} | Printable: {entry['printable_pct']:.1f}% | "
              f"Longest seq: {entry['longest_sequence']} | Keywords: {entry['keyword_count']} | Words: {entry['word_count']}")
        print(f"   Sample: {entry['sample_text'][:80]}...")

    if executive_summary['pairs_with_keywords']:
        print(f"\n{'='*70}")
        print("PAIRS WITH KEYWORD MATCHES")
        print("="*70)
        for pk in executive_summary['pairs_with_keywords']:
            print(f"  {pk['columns']}: {pk['keywords_found']}")

    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print(f"Results saved to: {OUTPUT_PATH}")
    print("="*70)

    return output


if __name__ == "__main__":
    main()
