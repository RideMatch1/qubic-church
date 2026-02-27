#!/usr/bin/env python3
"""
01_WORD_ENCODING_AUDIT.py - Rigorous statistical audit of "word encoding" claims
about the Anna Matrix.

The "word encoding" method uses only the 26 diagonal values matrix[i][i] for
i=0..25, mapping A=position 0, B=position 1, ..., Z=position 25. A word's
"encoding" is the sum of diagonal values at each letter's position.

This script tests whether the observed word-value coincidences are statistically
meaningful or whether any random diagonal produces equally "interesting" results.

Seed: 42 for all random generation.
"""

import sys
import os
import json
import re
from collections import defaultdict, Counter
from pathlib import Path
from itertools import combinations

import numpy as np

# Ensure the analysis lib is importable
sys.path.insert(0, str(Path(__file__).parent))

from lib.matrix_loader import load_matrix, get_diagonal
from lib.statistical_tests import TestReport, empirical_p_value, format_p_value
from lib.control_generator import generate_uniform

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SEED = 42
N_CONTROLS = 1000
DICT_PATH = "/usr/share/dict/words"
OUTPUT_DIR = Path(__file__).parent
OUTPUT_JSON = OUTPUT_DIR / "01_WORD_ENCODING_AUDIT_RESULTS.json"

# The claimed "special" word-value mappings from prior research
SPECIAL_CLAIMS = {
    0: ["zero-sum target"],
    96: ["ANNA"],
    -96: ["AI", "SOUL"],
    33: ["THE"],
    26: ["MOON"],
    -416: ["CHRIST"],
    145: ["LIFE"],
    -145: ["GOD"],
    -105: ["CODE", "DEATH"],
}

# Words considered "theologically/scientifically interesting" for the control test
INTERESTING_WORDS = {
    "GOD", "JESUS", "CHRIST", "SOUL", "SPIRIT", "ANGEL", "HEAVEN", "HELL",
    "SATAN", "DEVIL", "FAITH", "HOPE", "LOVE", "LIFE", "DEATH", "TRUTH",
    "LIGHT", "DARK", "SIN", "HOLY", "DIVINE", "SACRED", "BIBLE", "CROSS",
    "ANNA", "AI", "CODE", "DATA", "MIND", "BRAIN", "THINK", "KNOW",
    "ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN",
    "EIGHT", "NINE", "TEN", "PI", "PHI", "PRIME", "MOON", "SUN",
    "STAR", "EARTH", "FIRE", "WATER", "ATOM", "QUBIT", "QUANTUM",
    "MATRIX", "KEY", "SEED", "GENESIS", "EXODUS", "BITCOIN", "BLOCK",
    "HASH", "MINE", "COIN", "GOLD", "SILVER", "THE", "QUBIC",
}

# "Special" target values: powers of 2, multiples of 13, and small round numbers
def is_special_value(v):
    """Return True if a value would be considered 'interesting' in numerology."""
    v = int(v)
    if v == 0:
        return True
    abs_v = abs(v)
    # Powers of 2
    if abs_v > 0 and (abs_v & (abs_v - 1)) == 0 and abs_v <= 1024:
        return True
    # Multiples of 13
    if abs_v % 13 == 0 and abs_v <= 500:
        return True
    # Multiples of 33
    if abs_v % 33 == 0 and abs_v <= 500:
        return True
    # Fibonacci numbers
    fibs = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377}
    if abs_v in fibs:
        return True
    # Round multiples of 10
    if abs_v % 10 == 0 and abs_v <= 500:
        return True
    return False


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def load_dictionary():
    """Load all English words from /usr/share/dict/words.

    Filters to uppercase A-Z only, length 2-15.
    """
    words = []
    try:
        with open(DICT_PATH, "r") as f:
            for line in f:
                word = line.strip().upper()
                if len(word) < 2 or len(word) > 15:
                    continue
                if not re.match(r'^[A-Z]+$', word):
                    continue
                words.append(word)
    except FileNotFoundError:
        print(f"ERROR: Dictionary not found at {DICT_PATH}")
        print("This script requires a Unix dictionary file.")
        sys.exit(1)

    # Deduplicate (some dictionaries have case variants)
    words = sorted(set(words))
    return words


def encode_word(word, diagonal):
    """Compute word encoding: sum of diagonal values at each letter position."""
    return sum(int(diagonal[ord(c) - ord('A')]) for c in word)


def compute_all_encodings(words, diagonal):
    """Compute encodings for all words. Returns dict: word -> sum."""
    return {w: encode_word(w, diagonal) for w in words}


def build_sum_histogram(encodings):
    """Build histogram: sum_value -> list of words."""
    hist = defaultdict(list)
    for word, val in encodings.items():
        hist[val].append(word)
    return hist


def count_zero_sum_pairs(histogram):
    """Count the number of (w1, w2) pairs where encode(w1) + encode(w2) = 0.

    For value v with count_v words, and value -v with count_neg_v words,
    the number of cross-pairs is count_v * count_neg_v.
    For value 0, it is C(count_0, 2) = count_0*(count_0-1)/2.
    """
    total_pairs = 0
    seen = set()

    for val, word_list in histogram.items():
        if val in seen:
            continue
        neg_val = -val
        if val == 0:
            n = len(word_list)
            total_pairs += n * (n - 1) // 2
            seen.add(0)
        elif neg_val in histogram:
            total_pairs += len(word_list) * len(histogram[neg_val])
            seen.add(val)
            seen.add(neg_val)

    return total_pairs


def count_interesting_coincidences(histogram, interesting_words_set):
    """Count how many 'interesting' words map to 'special' values.

    An interesting coincidence = a word from the interesting set whose
    encoding is a 'special' number (power of 2, multiple of 13, etc.).
    """
    count = 0
    hits = []
    for val, word_list in histogram.items():
        if is_special_value(val):
            for w in word_list:
                if w in interesting_words_set:
                    count += 1
                    hits.append((w, val))
    return count, hits


# ---------------------------------------------------------------------------
# Main audit
# ---------------------------------------------------------------------------

def main():
    print("=" * 80)
    print("  WORD ENCODING AUDIT - Anna Matrix Diagonal")
    print("  Rigorous statistical analysis of word-sum coincidences")
    print("=" * 80)
    print()

    # ------------------------------------------------------------------
    # Load matrix and extract diagonal
    # ------------------------------------------------------------------
    print("[SETUP] Loading Anna Matrix...")
    matrix = load_matrix(verify_hash=True)
    diagonal = get_diagonal(matrix, start=0, end=26)
    print(f"  Matrix shape: {matrix.shape}")
    print(f"  Diagonal (26 values): {diagonal.tolist()}")
    print()

    # Verify the diagonal matches the known values
    expected_diag = [-68, 60, -118, -70, 120, 120, -38, 26, -28, -76,
                     -79, -67, -16, 116, -37, -40, -91, -70, -113, -113,
                     121, 28, 100, 67, -75, -75]
    if list(diagonal) == expected_diag:
        print("  Diagonal verified: matches expected values.")
    else:
        print("  WARNING: Diagonal does NOT match expected values!")
        print(f"  Expected: {expected_diag}")
        print(f"  Got:      {list(diagonal)}")
    print()

    # ------------------------------------------------------------------
    # Load dictionary
    # ------------------------------------------------------------------
    print("[SETUP] Loading dictionary...")
    words = load_dictionary()
    print(f"  Total words loaded: {len(words)}")
    print(f"  Length range: {min(len(w) for w in words)}-{max(len(w) for w in words)}")
    print()

    # ------------------------------------------------------------------
    # SECTION 1: Full word encoding analysis
    # ------------------------------------------------------------------
    print("=" * 80)
    print("  SECTION 1: Word Encoding Overview")
    print("=" * 80)
    print()

    encodings = compute_all_encodings(words, diagonal)
    histogram = build_sum_histogram(encodings)

    all_sums = list(encodings.values())
    min_sum = min(all_sums)
    max_sum = max(all_sums)
    distinct_sums = len(histogram)
    avg_words_per_sum = len(words) / distinct_sums

    print(f"  Total words tested:    {len(words)}")
    print(f"  Sum range:             [{min_sum}, {max_sum}]")
    print(f"  Distinct sum values:   {distinct_sums}")
    print(f"  Avg words per sum:     {avg_words_per_sum:.2f}")
    print()

    # Distribution of words-per-sum
    counts_per_sum = [len(wl) for wl in histogram.values()]
    print(f"  Words-per-sum stats:")
    print(f"    Min:    {min(counts_per_sum)}")
    print(f"    Max:    {max(counts_per_sum)}")
    print(f"    Median: {int(np.median(counts_per_sum))}")
    print(f"    Mean:   {np.mean(counts_per_sum):.2f}")
    print(f"    Std:    {np.std(counts_per_sum):.2f}")
    print()

    # Top 10 most crowded sum values
    top_sums = sorted(histogram.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    print("  Top 10 most populated sum values:")
    for val, wl in top_sums:
        print(f"    Sum {val:>6d}: {len(wl):>4d} words")
    print()

    # ------------------------------------------------------------------
    # SECTION 2: Check specific claimed values
    # ------------------------------------------------------------------
    print("=" * 80)
    print("  SECTION 2: Verification of Specific Claims")
    print("=" * 80)
    print()

    section2_results = {}

    for target_val, claimed_words in sorted(SPECIAL_CLAIMS.items()):
        actual_words = histogram.get(target_val, [])
        # Verify claimed words are actually present
        verified = []
        missing = []
        for cw in claimed_words:
            if cw.startswith("["):
                # Not a real word, it's a label
                continue
            actual_encoding = encode_word(cw, diagonal) if re.match(r'^[A-Z]+$', cw) else None
            if actual_encoding == target_val:
                verified.append(cw)
            elif actual_encoding is not None:
                missing.append((cw, actual_encoding))

        print(f"  Value {target_val}: {len(actual_words)} total words in dictionary")
        if verified:
            print(f"    Claimed words VERIFIED at this value: {', '.join(verified)}")
        if missing:
            for mw, mv in missing:
                print(f"    CLAIM ERROR: '{mw}' actually encodes to {mv}, NOT {target_val}")

        # Show all words at this value (capped at 30 for readability)
        if actual_words:
            display_words = sorted(actual_words)
            if len(display_words) > 30:
                print(f"    All words (showing 30 of {len(display_words)}): "
                      f"{', '.join(display_words[:30])}...")
            else:
                print(f"    All words: {', '.join(display_words)}")
        else:
            print(f"    No dictionary words encode to this value.")

        section2_results[str(target_val)] = {
            "total_words": len(actual_words),
            "claimed_words": claimed_words,
            "verified": verified,
            "all_words_sample": sorted(actual_words)[:50],
        }
        print()

    # ------------------------------------------------------------------
    # SECTION 3: Zero-sum pair analysis
    # ------------------------------------------------------------------
    print("=" * 80)
    print("  SECTION 3: Zero-Sum Pair Analysis")
    print("=" * 80)
    print()

    zero_sum_pairs = count_zero_sum_pairs(histogram)
    words_at_zero = len(histogram.get(0, []))

    print(f"  Total zero-sum word pairs (w1+w2=0): {zero_sum_pairs:,}")
    print(f"  Words encoding to exactly 0:         {words_at_zero}")
    print()

    # Show some example zero-sum pairs
    print("  Example zero-sum pairs:")
    examples_shown = 0
    for val in sorted(histogram.keys()):
        if val >= 0 and (-val) in histogram and val != 0:
            pos_words = histogram[val][:3]
            neg_words = histogram[-val][:3]
            for pw in pos_words:
                for nw in neg_words:
                    if examples_shown < 10:
                        print(f"    {pw} ({val}) + {nw} ({-val}) = 0")
                        examples_shown += 1
            if examples_shown >= 10:
                break
    if words_at_zero >= 2:
        zero_words = histogram[0][:5]
        for i in range(min(3, len(zero_words))):
            for j in range(i + 1, min(4, len(zero_words))):
                print(f"    {zero_words[i]} (0) + {zero_words[j]} (0) = 0")
    print()

    # ------------------------------------------------------------------
    # SECTION 4: Anagram analysis
    # ------------------------------------------------------------------
    print("=" * 80)
    print("  SECTION 4: Anagram Analysis (Commutativity of Sums)")
    print("=" * 80)
    print()

    print("  KEY INSIGHT: Since encoding = sum of letter values, it is commutative.")
    print("  Any permutation of the same letters gives the same encoding.")
    print("  Therefore ALL anagrams trivially share an encoding.")
    print()

    # Group words by sorted-letter signature
    anagram_groups = defaultdict(list)
    for w in words:
        sig = ''.join(sorted(w))
        anagram_groups[sig].append(w)

    multi_anagram_groups = {k: v for k, v in anagram_groups.items() if len(v) > 1}
    words_in_anagram_groups = sum(len(v) for v in multi_anagram_groups.values())

    print(f"  Total anagram groups (>1 word):  {len(multi_anagram_groups)}")
    print(f"  Words that have an anagram:      {words_in_anagram_groups}")
    print(f"  Fraction with anagram partner:   "
          f"{words_in_anagram_groups / len(words) * 100:.1f}%")
    print()

    # Show some anagram groups
    big_groups = sorted(multi_anagram_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    print("  Largest anagram groups:")
    for sig, group in big_groups:
        encoding = encode_word(group[0], diagonal)
        print(f"    Encoding={encoding:>5d}: {', '.join(sorted(group)[:8])}"
              f"{'...' if len(group) > 8 else ''} ({len(group)} words)")
    print()

    # Beyond anagrams: words with the same sum but different letter compositions
    # (These are the non-trivial collisions)
    print("  NON-ANAGRAM COLLISIONS (same sum, different letters):")
    # Group by sum, then within each sum, check for distinct letter signatures
    non_trivial_collision_count = 0
    for val, word_list in histogram.items():
        sigs = set()
        for w in word_list:
            sigs.add(''.join(sorted(w)))
        if len(sigs) > 1:
            non_trivial_collision_count += 1

    print(f"  Sum values with non-anagram collisions: {non_trivial_collision_count} "
          f"out of {distinct_sums} distinct sums "
          f"({non_trivial_collision_count / distinct_sums * 100:.1f}%)")
    print()

    # ------------------------------------------------------------------
    # SECTION 5: CONTROL DIAGONAL TEST
    # ------------------------------------------------------------------
    print("=" * 80)
    print("  SECTION 5: Control Diagonal Test (N=1000)")
    print("=" * 80)
    print()
    print(f"  Generating {N_CONTROLS} random diagonals (26 values in [-128, 127])...")
    print(f"  Seed: {SEED}")
    print()

    rng = np.random.default_rng(SEED)

    # Anna's metrics
    anna_zero_pairs = zero_sum_pairs
    anna_words_at_zero = words_at_zero
    anna_interesting_count, anna_interesting_hits = count_interesting_coincidences(
        histogram, INTERESTING_WORDS
    )

    print(f"  Anna diagonal metrics:")
    print(f"    Zero-sum pairs:          {anna_zero_pairs:,}")
    print(f"    Words at sum=0:          {anna_words_at_zero}")
    print(f"    Interesting coincidences: {anna_interesting_count}")
    if anna_interesting_hits:
        for w, v in sorted(anna_interesting_hits, key=lambda x: x[0]):
            print(f"      {w} -> {v}")
    print()

    # Run control diagonals
    control_zero_pairs = []
    control_words_at_zero = []
    control_interesting_counts = []
    control_distinct_sums = []
    control_max_words_per_sum = []

    for i in range(N_CONTROLS):
        if (i + 1) % 100 == 0:
            print(f"  Processing control {i + 1}/{N_CONTROLS}...", flush=True)

        ctrl_diag = rng.integers(-128, 128, size=26)
        ctrl_encodings = compute_all_encodings(words, ctrl_diag)
        ctrl_histogram = build_sum_histogram(ctrl_encodings)

        ctrl_zp = count_zero_sum_pairs(ctrl_histogram)
        ctrl_wz = len(ctrl_histogram.get(0, []))
        ctrl_ic, _ = count_interesting_coincidences(ctrl_histogram, INTERESTING_WORDS)
        ctrl_ds = len(ctrl_histogram)
        ctrl_max = max(len(wl) for wl in ctrl_histogram.values())

        control_zero_pairs.append(ctrl_zp)
        control_words_at_zero.append(ctrl_wz)
        control_interesting_counts.append(ctrl_ic)
        control_distinct_sums.append(ctrl_ds)
        control_max_words_per_sum.append(ctrl_max)

    control_zero_pairs = np.array(control_zero_pairs)
    control_words_at_zero = np.array(control_words_at_zero)
    control_interesting_counts = np.array(control_interesting_counts)
    control_distinct_sums = np.array(control_distinct_sums)
    control_max_words_per_sum = np.array(control_max_words_per_sum)

    print()

    # ------------------------------------------------------------------
    # Build TestReport
    # ------------------------------------------------------------------
    report = TestReport(
        title="Word Encoding Audit - Anna Diagonal vs Random Diagonals",
        n_controls=N_CONTROLS,
        seed=SEED,
        alpha=0.05,  # Use 0.05 as the family-wise alpha
    )

    report.add_test(
        name="zero_sum_pairs",
        null_hypothesis="Anna's zero-sum pair count is typical for random diagonals",
        observed=anna_zero_pairs,
        control_values=control_zero_pairs,
        alternative="greater",
        unit="pairs",
    )

    report.add_test(
        name="words_at_zero",
        null_hypothesis="Anna's count of words encoding to 0 is typical",
        observed=anna_words_at_zero,
        control_values=control_words_at_zero,
        alternative="greater",
        unit="words",
    )

    report.add_test(
        name="interesting_coincidences",
        null_hypothesis="Anna's 'interesting word -> special value' count is typical",
        observed=anna_interesting_count,
        control_values=control_interesting_counts,
        alternative="greater",
        unit="coincidences",
    )

    report.add_test(
        name="distinct_sums",
        null_hypothesis="Anna's number of distinct sum values is typical",
        observed=distinct_sums,
        control_values=control_distinct_sums,
        alternative="two-sided",
        unit="distinct values",
    )

    anna_max_words = max(len(wl) for wl in histogram.values())
    report.add_test(
        name="max_words_per_sum",
        null_hypothesis="Anna's maximum collision count per sum is typical",
        observed=anna_max_words,
        control_values=control_max_words_per_sum,
        alternative="greater",
        unit="words",
    )

    print()
    report.print_report()
    print()

    # ------------------------------------------------------------------
    # Print control distribution summaries
    # ------------------------------------------------------------------
    print("-" * 80)
    print("  Detailed Control Distribution Comparisons")
    print("-" * 80)
    print()

    for label, anna_val, ctrl_vals in [
        ("Zero-sum pairs", anna_zero_pairs, control_zero_pairs),
        ("Words at sum=0", anna_words_at_zero, control_words_at_zero),
        ("Interesting coincidences", anna_interesting_count, control_interesting_counts),
        ("Distinct sums", distinct_sums, control_distinct_sums),
        ("Max words per sum", anna_max_words, control_max_words_per_sum),
    ]:
        pct = np.sum(ctrl_vals >= anna_val) / len(ctrl_vals) * 100
        print(f"  {label}:")
        print(f"    Anna:    {anna_val:>10,}")
        print(f"    Control: mean={np.mean(ctrl_vals):>10,.1f}  "
              f"std={np.std(ctrl_vals):>10,.1f}  "
              f"range=[{np.min(ctrl_vals):,}, {np.max(ctrl_vals):,}]")
        print(f"    Percentile of Anna in controls: "
              f"{pct:.1f}% of controls >= Anna's value")
        print()

    # ------------------------------------------------------------------
    # SECTION 6: Summary and Conclusion
    # ------------------------------------------------------------------
    print("=" * 80)
    print("  SECTION 6: Summary and Conclusion")
    print("=" * 80)
    print()

    report.finalize()
    sig_tests = [t for t in report.tests if t["significant"]]
    nonsig_tests = [t for t in report.tests if not t["significant"]]

    if len(sig_tests) == 0:
        print("  CONCLUSION: No statistically significant differences found.")
        print()
        print("  The Anna matrix diagonal produces word-encoding patterns that are")
        print("  entirely consistent with random diagonals. Specifically:")
        print()
        print("  - The number of zero-sum word pairs is typical for any random diagonal.")
        print("  - The number of words encoding to zero is typical.")
        print("  - The number of 'interesting' word-value coincidences is typical.")
        print("  - The overall sum distribution is typical.")
        print()
        print("  The word-encoding scheme is a simple linear function over a commutative")
        print("  operation (addition). Given ~25,000+ English words mapped to ~2,000")
        print("  possible sum values, dense collisions and 'meaningful' word pairs are")
        print("  statistically inevitable for ANY diagonal, not special to Anna's.")
        conclusion = "NOT_SIGNIFICANT"
    elif len(sig_tests) < len(report.tests):
        print(f"  MIXED RESULTS: {len(sig_tests)} of {len(report.tests)} tests "
              f"are significant after Bonferroni correction.")
        print()
        print("  Significant tests:")
        for t in sig_tests:
            print(f"    - {t['name']}: p={format_p_value(t['p_value'])}")
        print()
        print("  Non-significant tests:")
        for t in nonsig_tests:
            print(f"    - {t['name']}: p={format_p_value(t['p_value'])}")
        print()
        print("  Some properties of Anna's diagonal are unusual, but this should be")
        print("  interpreted cautiously. With thousands of possible metrics to test,")
        print("  some will appear significant by chance.")
        conclusion = "MIXED"
    else:
        print(f"  ALL {len(report.tests)} TESTS SIGNIFICANT after Bonferroni correction.")
        print()
        for t in sig_tests:
            print(f"    - {t['name']}: p={format_p_value(t['p_value'])}")
        print()
        print("  Anna's diagonal appears genuinely unusual in its word-encoding properties.")
        print("  However, note that the diagonal was likely selected or designed to have")
        print("  specific properties, so this does not prove any metaphysical significance.")
        conclusion = "SIGNIFICANT"

    print()
    print("  METHODOLOGICAL NOTES:")
    print("  1. The word encoding is commutative (order-independent), so all anagrams")
    print("     trivially share the same encoding. This is not a meaningful coincidence.")
    print("  2. Cherry-picking a few 'special' words from thousands of collisions is")
    print("     a textbook example of the Texas Sharpshooter fallacy unless the words")
    print("     were predicted BEFORE examining the data.")
    print("  3. Any 26-element vector will produce dense word collisions when applied")
    print("     to a dictionary of >20,000 words over a sum range of ~2,000 values.")
    print("  4. The 'interesting coincidence' metric is generous - it counts any word")
    print("     from a curated list hitting any 'special' number. Both the word list")
    print("     and the number definitions are subjective.")
    print()

    # ------------------------------------------------------------------
    # Save JSON results
    # ------------------------------------------------------------------
    results = {
        "title": "Word Encoding Audit - Anna Matrix Diagonal",
        "seed": SEED,
        "n_controls": N_CONTROLS,
        "conclusion": conclusion,
        "dictionary": {
            "path": DICT_PATH,
            "total_words": len(words),
            "length_range": [min(len(w) for w in words), max(len(w) for w in words)],
        },
        "anna_diagonal": diagonal.tolist(),
        "section1_overview": {
            "total_words": len(words),
            "sum_range": [min_sum, max_sum],
            "distinct_sums": distinct_sums,
            "avg_words_per_sum": round(avg_words_per_sum, 2),
            "top_10_sums": [
                {"value": int(val), "count": len(wl)}
                for val, wl in top_sums
            ],
        },
        "section2_claims": section2_results,
        "section3_zero_sum": {
            "total_zero_sum_pairs": int(anna_zero_pairs),
            "words_at_zero": int(anna_words_at_zero),
            "words_at_zero_list": sorted(histogram.get(0, []))[:50],
        },
        "section4_anagrams": {
            "anagram_groups_gt1": len(multi_anagram_groups),
            "words_with_anagram": words_in_anagram_groups,
            "fraction_with_anagram": round(words_in_anagram_groups / len(words), 4),
            "non_trivial_collision_sums": non_trivial_collision_count,
        },
        "section5_control_test": {
            "anna_metrics": {
                "zero_sum_pairs": int(anna_zero_pairs),
                "words_at_zero": int(anna_words_at_zero),
                "interesting_coincidences": anna_interesting_count,
                "interesting_hits": [
                    {"word": w, "value": int(v)}
                    for w, v in sorted(anna_interesting_hits, key=lambda x: x[0])
                ],
                "distinct_sums": distinct_sums,
                "max_words_per_sum": int(anna_max_words),
            },
            "control_stats": {
                "zero_sum_pairs": {
                    "mean": float(np.mean(control_zero_pairs)),
                    "std": float(np.std(control_zero_pairs)),
                    "min": int(np.min(control_zero_pairs)),
                    "max": int(np.max(control_zero_pairs)),
                    "p5": float(np.percentile(control_zero_pairs, 5)),
                    "p95": float(np.percentile(control_zero_pairs, 95)),
                },
                "words_at_zero": {
                    "mean": float(np.mean(control_words_at_zero)),
                    "std": float(np.std(control_words_at_zero)),
                    "min": int(np.min(control_words_at_zero)),
                    "max": int(np.max(control_words_at_zero)),
                },
                "interesting_coincidences": {
                    "mean": float(np.mean(control_interesting_counts)),
                    "std": float(np.std(control_interesting_counts)),
                    "min": int(np.min(control_interesting_counts)),
                    "max": int(np.max(control_interesting_counts)),
                },
                "distinct_sums": {
                    "mean": float(np.mean(control_distinct_sums)),
                    "std": float(np.std(control_distinct_sums)),
                    "min": int(np.min(control_distinct_sums)),
                    "max": int(np.max(control_distinct_sums)),
                },
                "max_words_per_sum": {
                    "mean": float(np.mean(control_max_words_per_sum)),
                    "std": float(np.std(control_max_words_per_sum)),
                    "min": int(np.min(control_max_words_per_sum)),
                    "max": int(np.max(control_max_words_per_sum)),
                },
            },
            "test_results": {t["name"]: {
                "observed": t["observed"],
                "control_mean": t["control_mean"],
                "control_std": t["control_std"],
                "p_value": t["p_value"],
                "significant": t["significant"],
                "result": t["result"],
            } for t in report.tests},
        },
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Results saved to {OUTPUT_JSON}")
    print()
    print("  Audit complete.")
    print("=" * 80)


if __name__ == "__main__":
    main()
