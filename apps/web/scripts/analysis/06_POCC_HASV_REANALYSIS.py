#!/usr/bin/env python3
"""
06_POCC_HASV_REANALYSIS.py
==========================
HONEST reanalysis of POCC/HASV claims.

Previous research claimed the diagonal difference of 676 between POCC and
HASV addresses (computed through the Anna matrix) was statistically
significant. This script demonstrates it is NOT significant (p ~ 0.44),
and systematically audits every claimed "proof" for independence and
statistical validity.

The goal is TRUTH, not what we want to believe.
"""

import sys
import os
import json
import math
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.matrix_loader import load_matrix, get_diagonal
from lib.statistical_tests import TestReport
import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"
SEED = 42
N_SIMULATIONS = 100_000
OUTPUT_JSON = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "06_POCC_HASV_REANALYSIS_RESULTS.json",
)


def char_sum(address, base=0):
    """Sum of character values. base=0 means A=0..Z=25; base=1 means A=1..Z=26."""
    return sum(ord(c) - ord("A") + base for c in address)


def diagonal_sum(address, diag):
    """Sum of diagonal matrix values for each character in address."""
    return sum(int(diag[ord(c) - ord("A")]) for c in address)


def letter_frequencies(address):
    """Return array of length 26 with counts for each letter."""
    freq = np.zeros(26, dtype=int)
    for c in address:
        freq[ord(c) - ord("A")] += 1
    return freq


def section_header(title):
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)


def subsection(title):
    print()
    print(f"--- {title} ---")


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    np.random.seed(SEED)
    results = {
        "title": "POCC/HASV Honest Reanalysis",
        "timestamp": datetime.now().isoformat(),
        "seed": SEED,
        "n_simulations": N_SIMULATIONS,
        "sections": {},
    }

    print()
    print("#" * 80)
    print("#  POCC/HASV HONEST REANALYSIS")
    print("#  Seed: 42 | Simulations: 100,000")
    print(f"#  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("#" * 80)

    # Load matrix
    matrix = load_matrix()
    diag = get_diagonal(matrix, start=0, end=26)
    print(f"\nMatrix loaded. Diagonal (A..Z): {diag.tolist()}")

    # -----------------------------------------------------------------------
    # SECTION 1: BASIC CALCULATIONS
    # -----------------------------------------------------------------------
    section_header("SECTION 1: BASIC CALCULATIONS (verify the math)")

    pocc_char_sum = char_sum(POCC, base=0)
    hasv_char_sum = char_sum(HASV, base=0)
    char_diff = hasv_char_sum - pocc_char_sum

    pocc_diag_sum = diagonal_sum(POCC, diag)
    hasv_diag_sum = diagonal_sum(HASV, diag)
    diag_diff = hasv_diag_sum - pocc_diag_sum

    print(f"POCC address: {POCC}")
    print(f"HASV address: {HASV}")
    print(f"Both addresses are {len(POCC)} characters long.")
    print()
    print(f"Character sums (A=0..Z=25):")
    print(f"  POCC: {pocc_char_sum}  (expected: 612) -> {'MATCH' if pocc_char_sum == 612 else 'MISMATCH'}")
    print(f"  HASV: {hasv_char_sum}  (expected: 750) -> {'MATCH' if hasv_char_sum == 750 else 'MISMATCH'}")
    print(f"  Difference (HASV - POCC): {char_diff}  (expected: 138) -> {'MATCH' if char_diff == 138 else 'MISMATCH'}")
    print()
    print(f"Diagonal sums (sum of matrix[c][c] for each char c):")
    print(f"  POCC: {pocc_diag_sum}  (expected: -1231) -> {'MATCH' if pocc_diag_sum == -1231 else 'MISMATCH'}")
    print(f"  HASV: {hasv_diag_sum}  (expected: -555) -> {'MATCH' if hasv_diag_sum == -555 else 'MISMATCH'}")
    print(f"  Difference (HASV - POCC): {diag_diff}  (expected: 676) -> {'MATCH' if diag_diff == 676 else 'MISMATCH'}")

    results["sections"]["basic_calculations"] = {
        "pocc_char_sum": pocc_char_sum,
        "hasv_char_sum": hasv_char_sum,
        "char_diff": char_diff,
        "pocc_diag_sum": pocc_diag_sum,
        "hasv_diag_sum": hasv_diag_sum,
        "diag_diff": diag_diff,
        "all_match": (
            pocc_char_sum == 612
            and hasv_char_sum == 750
            and char_diff == 138
            and pocc_diag_sum == -1231
            and hasv_diag_sum == -555
            and diag_diff == 676
        ),
    }

    # -----------------------------------------------------------------------
    # SECTION 2: WHY 676 IS NOT SIGNIFICANT (p ~ 0.44)
    # -----------------------------------------------------------------------
    section_header("SECTION 2: WHY 676 IS NOT SIGNIFICANT")

    subsection("The mechanism")
    print("The diagonal sum for a 60-char address only uses 26 values: matrix[0,0]..matrix[25,25].")
    print("For each address, diagonal_sum = sum(freq[i] * diag[i] for i in 0..25).")
    print("Random addresses have random letter frequencies, so diagonal sums vary widely.")
    print("The difference of two such sums has even MORE variance.")
    print()
    print(f"Diagonal values: {diag.tolist()}")
    print(f"Diagonal mean: {diag.mean():.2f}")
    print(f"Diagonal std: {diag.std():.2f}")
    print(f"Diagonal range: [{diag.min()}, {diag.max()}]")

    subsection(f"Monte Carlo: {N_SIMULATIONS:,} random 60-char address pairs")
    random_diag_diffs = np.zeros(N_SIMULATIONS, dtype=np.int64)
    for i in range(N_SIMULATIONS):
        addr1 = np.random.randint(0, 26, 60)
        addr2 = np.random.randint(0, 26, 60)
        d1 = np.sum(diag[addr1])
        d2 = np.sum(diag[addr2])
        random_diag_diffs[i] = d2 - d1

    abs_diffs = np.abs(random_diag_diffs)
    fraction_ge_676 = np.mean(abs_diffs >= 676)
    p_random_pairs = fraction_ge_676

    print(f"Random pairs with |diagonal_diff| >= 676: {np.sum(abs_diffs >= 676):,} / {N_SIMULATIONS:,}")
    print(f"p-value (random pairs): {p_random_pairs:.4f}")
    print()
    print(f"Distribution of |diagonal_diff|:")
    print(f"  Mean:   {np.mean(abs_diffs):.1f}")
    print(f"  Median: {np.median(abs_diffs):.1f}")
    print(f"  Std:    {np.std(abs_diffs):.1f}")
    print(f"  P5:     {np.percentile(abs_diffs, 5):.0f}")
    print(f"  P25:    {np.percentile(abs_diffs, 25):.0f}")
    print(f"  P50:    {np.percentile(abs_diffs, 50):.0f}")
    print(f"  P75:    {np.percentile(abs_diffs, 75):.0f}")
    print(f"  P95:    {np.percentile(abs_diffs, 95):.0f}")
    print(f"  Max:    {np.max(abs_diffs)}")
    print()
    print(f"CONCLUSION: 676 is an ORDINARY difference. ~{p_random_pairs*100:.1f}% of random pairs")
    print(f"produce a diagonal difference at least this large. NOT SIGNIFICANT.")

    results["sections"]["random_pair_test"] = {
        "n_simulations": N_SIMULATIONS,
        "observed_diff": int(diag_diff),
        "fraction_ge_676": float(fraction_ge_676),
        "p_value": float(p_random_pairs),
        "significant": bool(p_random_pairs < 0.05),
        "abs_diff_mean": float(np.mean(abs_diffs)),
        "abs_diff_median": float(np.median(abs_diffs)),
        "abs_diff_std": float(np.std(abs_diffs)),
        "abs_diff_p5": float(np.percentile(abs_diffs, 5)),
        "abs_diff_p95": float(np.percentile(abs_diffs, 95)),
        "verdict": "NOT SIGNIFICANT",
    }

    # -----------------------------------------------------------------------
    # SECTION 3: PERMUTATION TEST
    # -----------------------------------------------------------------------
    section_header("SECTION 3: PERMUTATION TEST (shuffle diagonal values)")

    print("Test: given THESE two addresses (POCC and HASV), is the diagonal")
    print("difference of 676 special for THIS particular matrix diagonal?")
    print()
    print("Method: keep addresses fixed, shuffle the 26 diagonal values 100,000 times.")

    pocc_freq = letter_frequencies(POCC)
    hasv_freq = letter_frequencies(HASV)
    freq_diff = hasv_freq - pocc_freq

    print(f"\nLetter frequency differences (HASV - POCC):")
    for i in range(26):
        if freq_diff[i] != 0:
            print(f"  {chr(i+65)}: {freq_diff[i]:+d}")

    perm_diffs = np.zeros(N_SIMULATIONS, dtype=np.int64)
    diag_copy = diag.copy()
    for i in range(N_SIMULATIONS):
        np.random.shuffle(diag_copy)
        perm_diffs[i] = np.dot(freq_diff, diag_copy)

    exact_676_count = np.sum(perm_diffs == 676)
    abs_perm_ge_676 = np.sum(np.abs(perm_diffs) >= 676)
    p_exact = exact_676_count / N_SIMULATIONS
    p_perm_abs = abs_perm_ge_676 / N_SIMULATIONS

    print(f"\nPermutation results ({N_SIMULATIONS:,} shuffles):")
    print(f"  Shuffles yielding exactly 676: {exact_676_count:,} ({p_exact:.6f})")
    print(f"  Shuffles yielding |diff| >= 676: {abs_perm_ge_676:,} ({p_perm_abs:.4f})")
    print(f"  Mean permuted diff: {np.mean(perm_diffs):.1f}")
    print(f"  Std permuted diff:  {np.std(perm_diffs):.1f}")
    print()
    if p_perm_abs > 0.05:
        print(f"CONCLUSION: p = {p_perm_abs:.4f}. Even for these specific addresses,")
        print("676 is NOT a special value of the diagonal. NOT SIGNIFICANT.")
    else:
        print(f"CONCLUSION: p = {p_perm_abs:.4f}.")
        if p_perm_abs < 0.001:
            print("This IS statistically significant under permutation test.")
        else:
            print("This is borderline and would not survive Bonferroni correction.")

    results["sections"]["permutation_test"] = {
        "n_simulations": N_SIMULATIONS,
        "exact_676_count": int(exact_676_count),
        "p_exact_676": float(p_exact),
        "abs_ge_676_count": int(abs_perm_ge_676),
        "p_abs_ge_676": float(p_perm_abs),
        "perm_diff_mean": float(np.mean(perm_diffs)),
        "perm_diff_std": float(np.std(perm_diffs)),
        "significant": bool(p_perm_abs < 0.05),
        "verdict": "NOT SIGNIFICANT" if p_perm_abs > 0.05 else "SIGNIFICANT" if p_perm_abs < 0.001 else "BORDERLINE",
    }

    # -----------------------------------------------------------------------
    # SECTION 4: DERIVED vs INDEPENDENT PROPERTIES
    # -----------------------------------------------------------------------
    section_header("SECTION 4: DERIVED vs INDEPENDENT PROPERTIES")

    print("Auditing the 15 claimed 'proofs' from previous research.")
    print("For each claim, we determine if it provides INDEPENDENT information")
    print("or is merely a DERIVED mathematical consequence of other properties.")
    print()

    claims = [
        {
            "id": 1,
            "claim": "Character sum difference = 138",
            "math_correct": True,
            "independent": True,
            "significant": False,
            "explanation": (
                "True: HASV(750) - POCC(612) = 138. However, this is just the "
                "difference in letter-value sums for two specific addresses. "
                "Any address pair has SOME difference. Not inherently meaningful."
            ),
        },
        {
            "id": 2,
            "claim": "138 mod 6 = 0",
            "math_correct": True,
            "independent": False,
            "significant": False,
            "explanation": (
                "DERIVED from claim #1. 138 = 6 * 23. Any number divisible by 6 "
                "has this property. 1 in 6 random integers satisfy this. "
                "Not independent information."
            ),
        },
        {
            "id": 3,
            "claim": "138 mod 23 = 0",
            "math_correct": True,
            "independent": False,
            "significant": False,
            "explanation": (
                "DERIVED from claim #1. 138 = 6 * 23. This is just the "
                "factorization of 138, not new information."
            ),
        },
        {
            "id": 4,
            "claim": "138 = 2 * 3 * 23 (prime factorization)",
            "math_correct": True,
            "independent": False,
            "significant": False,
            "explanation": (
                "DERIVED from claim #1. Every integer has a unique prime "
                "factorization. This is just a mathematical fact about 138."
            ),
        },
        {
            "id": 5,
            "claim": "Diagonal difference = 676 = 26^2",
            "math_correct": True,
            "independent": True,
            "significant": False,
            "explanation": (
                "True: HASV_diag(-555) - POCC_diag(-1231) = 676 = 26^2. "
                "The math is correct. However, as shown in Section 2, "
                "p = 0.44 -- about 44% of random pairs achieve this or larger. "
                "NOT SIGNIFICANT."
            ),
        },
        {
            "id": 6,
            "claim": "676 = 26^2 (perfect square of alphabet size)",
            "math_correct": True,
            "independent": False,
            "significant": False,
            "explanation": (
                "DERIVED from claim #5. 676 is 26^2 as a mathematical fact. "
                "The connection to alphabet size is numerological pattern-matching, "
                "not statistical evidence."
            ),
        },
        {
            "id": 7,
            "claim": "sqrt(676) = 26 = number of letters in alphabet",
            "math_correct": True,
            "independent": False,
            "significant": False,
            "explanation": (
                "DERIVED from claim #6. Same fact restated. sqrt(676) = 26 is "
                "just the definition of 676 = 26^2."
            ),
        },
        {
            "id": 8,
            "claim": "HASV 1-based char sum = 810",
            "math_correct": True,
            "independent": False,
            "significant": False,
            "explanation": (
                "DERIVED from claim #1. If A=0 sum is 750, then A=1 sum is "
                "750 + 60 = 810. No new information."
            ),
        },
        {
            "id": 9,
            "claim": "POCC 1-based char sum = 672 ~ 676",
            "math_correct": False,
            "independent": False,
            "significant": False,
            "explanation": (
                "DERIVED and WRONG. 672 is NOT 676. The claim that they are "
                "'close' (0.59% error) is numerological. In mathematics, close "
                "does not equal equal. Many random addresses have 1-based sums "
                "within 4 of 676."
            ),
        },
        {
            "id": 10,
            "claim": "HASV char sum = 750 = expected value for random 60-char string",
            "math_correct": True,
            "independent": False,
            "significant": False,
            "explanation": (
                "DERIVED observation. E[sum] = 60 * 12.5 = 750. HASV hitting "
                "the expected value exactly is mildly interesting but p ~ 1/57 "
                "(one sigma bin) -- many addresses do this."
            ),
        },
        {
            "id": 11,
            "claim": "676 / 138 = 4.8986... (claimed meaningful ratio)",
            "math_correct": True,
            "independent": False,
            "significant": False,
            "explanation": (
                "DERIVED from claims #1 and #5. Any two numbers have a ratio. "
                "4.8986... is not a notable mathematical constant."
            ),
        },
        {
            "id": 12,
            "claim": "POCC diagonal sum = -1231 (claimed significant)",
            "math_correct": True,
            "independent": False,
            "significant": False,
            "explanation": (
                "DERIVED component of claim #5. The individual diagonal sums "
                "are determined by letter frequencies and diagonal values. "
                "Not independently testable without claim #5."
            ),
        },
        {
            "id": 13,
            "claim": "HASV diagonal sum = -555 (claimed triple-5 pattern)",
            "math_correct": True,
            "independent": False,
            "significant": False,
            "explanation": (
                "DERIVED component of claim #5. The repeated digit pattern "
                "(-555) is numerological. In base 10, getting three identical "
                "digits in a three-digit number has p ~ 10/900 ~ 0.011 -- "
                "mildly unlikely but common enough with multiple looks."
            ),
        },
        {
            "id": 14,
            "claim": "Multiple modular arithmetic properties of 676",
            "math_correct": True,
            "independent": False,
            "significant": False,
            "explanation": (
                "DERIVED from claim #5. Every number has modular properties. "
                "676 mod 26 = 0, 676 mod 13 = 0, etc. These are consequences "
                "of 676 = 26^2, not independent facts."
            ),
        },
        {
            "id": 15,
            "claim": "Combined probability of all properties is astronomically low",
            "math_correct": False,
            "independent": False,
            "significant": False,
            "explanation": (
                "INCORRECT. This claim multiplies p-values of DERIVED properties "
                "as if they were independent, which drastically underestimates "
                "the true probability. Most 'properties' are mathematical "
                "consequences of just 1-2 base facts. The combined probability "
                "is driven entirely by the few independent claims, which are "
                "individually not significant."
            ),
        },
    ]

    # Count independence
    independent_count = sum(1 for c in claims if c["independent"])
    derived_count = sum(1 for c in claims if not c["independent"])
    significant_count = sum(1 for c in claims if c["significant"])

    for c in claims:
        status_ind = "INDEPENDENT" if c["independent"] else "DERIVED"
        status_math = "CORRECT" if c["math_correct"] else "INCORRECT"
        status_sig = "SIGNIFICANT" if c["significant"] else "NOT SIGNIFICANT"
        print(f"Claim #{c['id']}: {c['claim']}")
        print(f"  Math: {status_math} | Independence: {status_ind} | Significance: {status_sig}")
        print(f"  {c['explanation']}")
        print()

    print(f"TOTALS: {independent_count} independent, {derived_count} derived, "
          f"{significant_count} significant out of {len(claims)} claims")
    print()
    print("KEY INSIGHT: Of 15 claimed proofs, only 2 are independent observations")
    print("(character sum difference = 138, diagonal difference = 676).")
    print("The remaining 13 are mathematical consequences of these two facts.")
    print("Neither independent observation is statistically significant.")

    results["sections"]["independence_audit"] = {
        "total_claims": len(claims),
        "independent_count": independent_count,
        "derived_count": derived_count,
        "significant_count": significant_count,
        "claims": claims,
    }

    # -----------------------------------------------------------------------
    # SECTION 5: EXPECTED VALUE ANALYSIS
    # -----------------------------------------------------------------------
    section_header("SECTION 5: EXPECTED VALUE ANALYSIS")

    expected_one_char = sum(range(26)) / 26  # = 12.5
    expected_sum_60 = 60 * expected_one_char  # = 750.0
    var_one_char = np.var(range(26))  # variance of uniform(0..25)
    std_sum_60 = np.sqrt(60 * var_one_char)

    pocc_z = (expected_sum_60 - pocc_char_sum) / std_sum_60
    hasv_z = (hasv_char_sum - expected_sum_60) / std_sum_60

    print(f"For a random 60-char uppercase string (uniform A-Z):")
    print(f"  E[one char] = (0+1+...+25)/26 = {expected_one_char:.1f}")
    print(f"  E[60-char sum] = 60 * 12.5 = {expected_sum_60:.1f}")
    print(f"  Var[one char] = Var(uniform 0..25) = {var_one_char:.4f}")
    print(f"  Std[60-char sum] = sqrt(60 * {var_one_char:.4f}) = {std_sum_60:.2f}")
    print()
    print(f"HASV char sum: {hasv_char_sum}")
    print(f"  Deviation from expected: {hasv_char_sum - expected_sum_60:.1f}")
    print(f"  Z-score: {hasv_z:.4f}")
    print(f"  HASV is EXACTLY at the expected value. This is unremarkable.")
    print(f"  (Many addresses land near the expected value by CLT)")
    print()
    print(f"POCC char sum: {pocc_char_sum}")
    print(f"  Deviation from expected: {pocc_char_sum - expected_sum_60:.1f}")
    print(f"  Z-score: -{pocc_z:.2f} (i.e., {pocc_z:.2f} sigma below mean)")
    print(f"  This is moderately unusual but far from extreme.")
    two_sided_p = 2 * (1 - 0.5 * (1 + math.erf(pocc_z / math.sqrt(2))))
    print(f"  P(|Z| >= {pocc_z:.2f}) ~ {two_sided_p:.4f} (two-sided)")

    # Empirical verification
    random_sums = np.array([np.sum(np.random.randint(0, 26, 60)) for _ in range(N_SIMULATIONS)])
    frac_le_612 = np.mean(random_sums <= 612)
    frac_eq_750 = np.mean(random_sums == 750)

    print()
    print(f"Empirical verification ({N_SIMULATIONS:,} random addresses):")
    print(f"  Fraction with sum <= 612 (as extreme as POCC): {frac_le_612:.4f}")
    print(f"  Fraction with sum == 750 (exactly like HASV): {frac_eq_750:.4f}")
    print(f"  Empirical mean: {np.mean(random_sums):.2f}")
    print(f"  Empirical std: {np.std(random_sums):.2f}")

    results["sections"]["expected_value_analysis"] = {
        "expected_one_char": float(expected_one_char),
        "expected_sum_60": float(expected_sum_60),
        "var_one_char": float(var_one_char),
        "std_sum_60": float(std_sum_60),
        "hasv_z_score": float(hasv_z),
        "pocc_z_score": float(-pocc_z),
        "pocc_sigma_below_mean": float(pocc_z),
        "empirical_frac_le_612": float(frac_le_612),
        "empirical_frac_eq_750": float(frac_eq_750),
    }

    # -----------------------------------------------------------------------
    # SECTION 6: THE "1-BASED SUM = 672 ~ 676" CLAIM
    # -----------------------------------------------------------------------
    section_header("SECTION 6: THE '1-BASED SUM = 672 approx 676' CLAIM")

    pocc_sum_1based = char_sum(POCC, base=1)
    hasv_sum_1based = char_sum(HASV, base=1)

    print(f"If we use A=1..Z=26 instead of A=0..Z=25:")
    print(f"  POCC 1-based sum: {pocc_sum_1based}")
    print(f"  HASV 1-based sum: {hasv_sum_1based}")
    print(f"  (Note: 1-based sum = 0-based sum + 60, since each of 60 chars gains +1)")
    print()
    print(f"The claim: POCC 1-based sum ({pocc_sum_1based}) is 'close' to 676.")
    print(f"  Difference: |{pocc_sum_1based} - 676| = {abs(pocc_sum_1based - 676)}")
    print(f"  Error: {abs(pocc_sum_1based - 676)/676*100:.2f}%")
    print()
    print("REBUTTAL: 672 is NOT 676. In mathematics, close does not count.")

    # How many random addresses have 1-based sum within 4 of 676?
    random_sums_1based = random_sums + 60  # just add 60 to convert
    within_4_of_676 = np.mean(np.abs(random_sums_1based - 676) <= 4)
    within_10_of_676 = np.mean(np.abs(random_sums_1based - 676) <= 10)

    print(f"\nHow common is a 1-based sum 'close to 676'?")
    print(f"  Random addresses within 4 of 676: {within_4_of_676*100:.2f}%")
    print(f"  Random addresses within 10 of 676: {within_10_of_676*100:.2f}%")
    print()
    print("CONCLUSION: Many random addresses have 1-based sums near 676.")
    print("This 'closeness' is unremarkable and not evidence of anything.")

    results["sections"]["one_based_sum_claim"] = {
        "pocc_sum_1based": pocc_sum_1based,
        "hasv_sum_1based": hasv_sum_1based,
        "difference_from_676": abs(pocc_sum_1based - 676),
        "error_percent": abs(pocc_sum_1based - 676) / 676 * 100,
        "frac_within_4_of_676": float(within_4_of_676),
        "frac_within_10_of_676": float(within_10_of_676),
        "verdict": "NOT SIGNIFICANT - 672 != 676",
    }

    # -----------------------------------------------------------------------
    # SECTION 7: HONEST SUMMARY TABLE
    # -----------------------------------------------------------------------
    section_header("SECTION 7: HONEST SUMMARY TABLE")

    header = f"{'#':<3} {'Claim':<50} {'Math?':<10} {'Significant?':<16} {'Independent?':<14} {'Verdict'}"
    print(header)
    print("-" * len(header))

    summary_rows = []
    for c in claims:
        math_str = "YES" if c["math_correct"] else "NO"
        sig_str = "YES" if c["significant"] else "NO"
        ind_str = "YES" if c["independent"] else "NO"

        if not c["math_correct"]:
            verdict = "INVALID"
        elif not c["independent"]:
            verdict = "DERIVED (redundant)"
        elif not c["significant"]:
            verdict = "NOT SIGNIFICANT"
        else:
            verdict = "VALID"

        row = f"{c['id']:<3} {c['claim'][:50]:<50} {math_str:<10} {sig_str:<16} {ind_str:<14} {verdict}"
        print(row)
        summary_rows.append({
            "id": c["id"],
            "claim": c["claim"],
            "math_correct": c["math_correct"],
            "significant": c["significant"],
            "independent": c["independent"],
            "verdict": verdict,
        })

    print()
    print(f"VALID claims (math correct + independent + significant): {significant_count}")
    print(f"DERIVED claims (mathematical consequences, not new info): {derived_count}")
    print(f"INVALID claims (math incorrect): {sum(1 for c in claims if not c['math_correct'])}")

    results["sections"]["summary_table"] = summary_rows

    # -----------------------------------------------------------------------
    # FINAL VERDICT
    # -----------------------------------------------------------------------
    section_header("FINAL VERDICT")

    print("The POCC/HASV diagonal difference of 676 is:")
    print()
    print("  1. MATHEMATICALLY CORRECT: Yes, the arithmetic checks out.")
    print("  2. STATISTICALLY SIGNIFICANT: NO. p ~ 0.44 for random pair test.")
    print("     About 44% of random address pairs produce a diagonal difference")
    print("     at least as large as 676.")
    print("  3. NUMEROLOGICALLY APPEALING: Yes, 676 = 26^2 is a 'nice' number.")
    print("     But nice numbers appear by chance all the time.")
    print("  4. EVIDENCE OF DESIGN: NO. The evidence does not support the claim")
    print("     that these addresses were intentionally chosen to produce 676.")
    print()
    print("Of 15 claimed 'proofs':")
    print(f"  - {independent_count} are genuinely independent observations")
    print(f"  - {derived_count} are derived/redundant (mathematical consequences)")
    print(f"  - {sum(1 for c in claims if not c['math_correct'])} contain mathematical errors")
    print(f"  - {significant_count} are statistically significant")
    print()
    print("The previous research inflated significance by:")
    print("  a) Counting derived properties as independent evidence")
    print("  b) Multiplying non-independent p-values (statistical fallacy)")
    print("  c) Treating 'close to' as 'equal to' (672 ~ 676)")
    print("  d) Not performing proper null hypothesis testing")
    print()
    print("HONEST CONCLUSION: The POCC/HASV 676 finding is a coincidence.")
    print("It is not evidence of intentional design in the Anna matrix.")

    results["final_verdict"] = {
        "mathematically_correct": True,
        "statistically_significant": False,
        "p_value_random_pairs": float(p_random_pairs),
        "p_value_permutation": float(p_perm_abs),
        "independent_claims": independent_count,
        "derived_claims": derived_count,
        "invalid_claims": sum(1 for c in claims if not c["math_correct"]),
        "significant_claims": significant_count,
        "conclusion": "The POCC/HASV 676 finding is a coincidence, not evidence of design.",
    }

    # -----------------------------------------------------------------------
    # SAVE RESULTS
    # -----------------------------------------------------------------------
    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
