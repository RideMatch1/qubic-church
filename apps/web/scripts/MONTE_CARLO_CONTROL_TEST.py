#!/usr/bin/env python3
"""
MONTE CARLO CONTROL TEST
=========================
The HARDEST possible test for our findings.

Question: If we apply the SAME analysis pipeline to 100,000 random
BTC transactions, how often do we find equally "interesting" patterns?

If the answer is "frequently" → our findings are WORTHLESS
If the answer is "almost never" → our findings are SIGNIFICANT

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-09
Methodology: Null hypothesis testing via simulation
"""

import json
import numpy as np
from pathlib import Path
import random
import math
from collections import Counter

np.random.seed(42)  # Reproducibility
random.seed(42)

# Load Anna Matrix
MATRIX_PATH = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
with open(MATRIX_PATH, 'r') as f:
    data = json.load(f)
matrix = np.array(data['matrix'], dtype=np.int8)

# Our key numbers (the ones we checked against)
KEY_NUMBERS = [26, 41, 67, 97, 121, 576, 676]
EXCEPTION_COLS = {0, 22, 30, 41, 86, 97, 105, 127}
PERFECT_SQUARES = {i*i for i in range(1, 50)}  # up to 2401

# ============================================================
# TEST 1: BTC Amount Factorization
# ============================================================
# Our finding: 536737 = 67 × 8011
#   67 = 19th prime
#   8011 mod 676 = 575 (= 576-1)
#   8011 mod 121 = 25  (= 26-1)

def get_primes(n):
    """Sieve of Eratosthenes up to n"""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = False
    return [i for i in range(n + 1) if sieve[i]]

PRIMES = get_primes(100000)
PRIME_SET = set(PRIMES)
PRIME_INDEX = {p: i+1 for i, p in enumerate(PRIMES)}  # 1-indexed

def factorize(n):
    """Return prime factorization"""
    if n <= 1:
        return []
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def analyze_amount(amount_satoshis):
    """Apply our EXACT analysis pipeline to a BTC amount.
    Returns a score: how many 'interesting' properties it has."""
    score = 0
    details = []

    # Remove the "2." prefix to get the message part (like we did with 536737)
    amount_str = str(amount_satoshis)

    # Check: does the number factor into exactly 2 primes?
    factors = factorize(amount_satoshis)
    if len(factors) == 2 and factors[0] != factors[1]:
        p1, p2 = factors[0], factors[1]

        # Is either factor the Nth prime where N is in our key set?
        for p in [p1, p2]:
            if p in PRIME_INDEX:
                idx = PRIME_INDEX[p]
                if idx in KEY_NUMBERS or idx in EXCEPTION_COLS:
                    score += 1
                    details.append(f"{p} is {idx}th prime (key number)")

        # Do the factors have special mod properties?
        for p in [p1, p2]:
            for key in [676, 121]:
                mod_val = p % key
                # Check if mod result is "one less" than a key number
                if mod_val + 1 in KEY_NUMBERS or mod_val + 1 in {576, 676}:
                    score += 1
                    details.append(f"{p} mod {key} = {mod_val} (= {mod_val+1}-1)")
                # Check if mod result IS a key number
                if mod_val in KEY_NUMBERS or mod_val in EXCEPTION_COLS:
                    score += 1
                    details.append(f"{p} mod {key} = {mod_val} (key number)")

    # Check mod 6268 (Signal day)
    mod_6268 = amount_satoshis % 6268
    if mod_6268 == 33 or mod_6268 == 46:  # POCC or HASV prefix sum
        score += 1
        details.append(f"mod 6268 = {mod_6268}")

    # Check if amount contains "256" (SHA-256 reference)
    if "256" in amount_str:
        score += 1
        details.append("contains '256'")

    return score, details


# ============================================================
# TEST 2: Timeline Gap Analysis
# ============================================================
# Our finding: 97 + 24 = 121
#   97 = Exception Column
#   24 = √576
#   121 = 11²

def analyze_timeline_gap(total_gap, split_day):
    """Split a total gap at split_day. Check if both parts are 'special'."""
    gap1 = split_day
    gap2 = total_gap - split_day
    score = 0

    if gap1 <= 0 or gap2 <= 0:
        return 0

    # Is gap1 an Exception Column number?
    if gap1 in EXCEPTION_COLS:
        score += 1

    # Is gap2 a perfect square root result?
    if gap2 * gap2 in KEY_NUMBERS or gap2 * gap2 in {576, 676, 121}:
        score += 1

    # Does gap1 + gap2 equal a perfect square?
    total = gap1 + gap2
    if total in PERFECT_SQUARES:
        score += 1

    return score


# ============================================================
# TEST 3: Diagonal Self-Reference
# ============================================================
# Our finding: matrix[41,41]=22, matrix[97,97]=46, matrix[33,33]=26

def analyze_diagonal(positions):
    """Check if diagonal values at given positions are 'special'."""
    score = 0
    for pos in positions:
        if 0 <= pos < 128:
            diag_val = int(matrix[pos, pos])
            if diag_val in EXCEPTION_COLS:
                score += 1
            if diag_val == 26 or diag_val == 46 or diag_val == 33:
                score += 1
    return score


# ============================================================
# TEST 4: Row 6 Oracle
# ============================================================
# Our finding: matrix[6,22]=26, matrix[6,33]=26, matrix[6,97]=26

def analyze_row6(positions):
    """Check if Row 6 values at positions are special."""
    score = 0
    for pos in positions:
        if 0 <= pos < 128:
            val = int(matrix[6, pos])
            if val == 26:
                score += 1
    return score


# ============================================================
# TEST 5: Address Prefix Match
# ============================================================
# Our finding: 1CEq prefix match (4 chars) → p ≈ 1/195,112
# This is independently testable - we just calculate the probability


# ============================================================
# SIMULATION
# ============================================================

N_SIMULATIONS = 100_000
print("=" * 80)
print(f"MONTE CARLO CONTROL TEST ({N_SIMULATIONS:,} simulations)")
print("=" * 80)
print()

# --- TEST 1: BTC Amount Analysis ---
print("TEST 1: BTC Amount Factorization & Modular Properties")
print("-" * 60)

our_amount = 536737  # The "message" part of 2.56536737
our_score, our_details = analyze_amount(our_amount)
print(f"OUR amount ({our_amount}):")
print(f"  Score: {our_score}")
for d in our_details:
    print(f"  - {d}")
print()

# Also check the full satoshi amount
our_full = 256536737
our_full_score, our_full_details = analyze_amount(our_full)
print(f"OUR full amount ({our_full}):")
print(f"  Score: {our_full_score}")
for d in our_full_details:
    print(f"  - {d}")
print()

# Generate random amounts and test
random_scores = []
for _ in range(N_SIMULATIONS):
    # Random 6-digit number (like 536737)
    rand_amount = random.randint(100000, 999999)
    score, _ = analyze_amount(rand_amount)
    random_scores.append(score)

score_counts = Counter(random_scores)
print("Random amount score distribution:")
for s in sorted(score_counts.keys()):
    pct = score_counts[s] / N_SIMULATIONS * 100
    print(f"  Score {s}: {score_counts[s]:6d} ({pct:5.2f}%)")

p_value_amount = sum(1 for s in random_scores if s >= our_score) / N_SIMULATIONS
print(f"\nP(random score >= {our_score}): {p_value_amount:.6f} ({p_value_amount*100:.4f}%)")
if p_value_amount < 0.01:
    print("  >>> SIGNIFICANT (p < 0.01) <<<")
elif p_value_amount < 0.05:
    print("  >>> MARGINALLY SIGNIFICANT (p < 0.05) <<<")
else:
    print("  >>> NOT SIGNIFICANT <<<")
print()


# --- TEST 2: Timeline Gap ---
print("TEST 2: Timeline Gap Analysis (97 + 24 = 121)")
print("-" * 60)

our_total_gap = 121  # GENESIS to Signal
our_split = 97  # BTC TX splits at day 97
our_timeline_score = analyze_timeline_gap(our_total_gap, our_split)
print(f"OUR gap: {our_split} + {our_total_gap - our_split} = {our_total_gap}")
print(f"  Score: {our_timeline_score}")
print()

# For each possible split of 121 days, how many give score >= ours?
all_splits_scores = []
for split in range(1, 121):
    s = analyze_timeline_gap(121, split)
    all_splits_scores.append((split, 121-split, s))

high_scores = [(a, b, s) for a, b, s in all_splits_scores if s >= our_timeline_score]
p_value_timeline = len(high_scores) / len(all_splits_scores)
print(f"Splits of 121 with score >= {our_timeline_score}: {len(high_scores)} / {len(all_splits_scores)}")
print(f"P(random split equally special): {p_value_timeline:.4f} ({p_value_timeline*100:.2f}%)")
print()
print("All equally-scoring splits:")
for a, b, s in high_scores:
    labels_a = []
    labels_b = []
    if a in EXCEPTION_COLS: labels_a.append("ExcCol")
    if b*b in {576, 676, 121}: labels_b.append(f"√{b*b}")
    print(f"  {a:3d} ({','.join(labels_a) or '-':>8s}) + {b:3d} ({','.join(labels_b) or '-':>6s}) = 121")

# Now test: what if the total gap was NOT 121?
# Generate random total gaps (50-200 days) and random splits
print()
print("Control: Random total gaps (50-200 days):")
random_timeline_scores = []
for _ in range(N_SIMULATIONS):
    total = random.randint(50, 200)
    split = random.randint(1, total - 1)
    s = analyze_timeline_gap(total, split)
    random_timeline_scores.append(s)

timeline_counts = Counter(random_timeline_scores)
for s in sorted(timeline_counts.keys()):
    pct = timeline_counts[s] / N_SIMULATIONS * 100
    print(f"  Score {s}: {timeline_counts[s]:6d} ({pct:5.2f}%)")

p_random_timeline = sum(1 for s in random_timeline_scores if s >= our_timeline_score) / N_SIMULATIONS
print(f"P(random gap+split score >= {our_timeline_score}): {p_random_timeline:.6f}")
print()


# --- TEST 3: Diagonal Self-Reference ---
print("TEST 3: Matrix Diagonal Self-Reference")
print("-" * 60)

our_positions = [33, 41, 97]
our_diag_score = analyze_diagonal(our_positions)
print(f"OUR positions {our_positions}: diagonal score = {our_diag_score}")
print(f"  matrix[33,33]={int(matrix[33,33])}, matrix[41,41]={int(matrix[41,41])}, matrix[97,97]={int(matrix[97,97])}")
print()

# Random 3 positions
random_diag_scores = []
for _ in range(N_SIMULATIONS):
    positions = random.sample(range(128), 3)
    s = analyze_diagonal(positions)
    random_diag_scores.append(s)

diag_counts = Counter(random_diag_scores)
for s in sorted(diag_counts.keys()):
    pct = diag_counts[s] / N_SIMULATIONS * 100
    print(f"  Score {s}: {diag_counts[s]:6d} ({pct:5.2f}%)")

p_diag = sum(1 for s in random_diag_scores if s >= our_diag_score) / N_SIMULATIONS
print(f"P(random 3 positions score >= {our_diag_score}): {p_diag:.6f}")
if our_diag_score == 0:
    print("  (Our score is 0 - nothing to test)")
print()


# --- TEST 4: Row 6 Oracle ---
print("TEST 4: Row 6 Oracle Values")
print("-" * 60)

our_row6_positions = [22, 33, 97]
our_row6_score = analyze_row6(our_row6_positions)
print(f"OUR positions {our_row6_positions}: Row 6 score = {our_row6_score}")
print(f"  matrix[6,22]={int(matrix[6,22])}, matrix[6,33]={int(matrix[6,33])}, matrix[6,97]={int(matrix[6,97])}")
print()

# How many cells in Row 6 equal 26?
row6_26_count = int(np.sum(matrix[6, :] == 26))
print(f"Row 6 cells with value 26: {row6_26_count} / 128 = {row6_26_count/128*100:.1f}%")
print()

# Random 3 positions in Row 6
random_row6_scores = []
for _ in range(N_SIMULATIONS):
    positions = random.sample(range(128), 3)
    s = analyze_row6(positions)
    random_row6_scores.append(s)

row6_counts = Counter(random_row6_scores)
for s in sorted(row6_counts.keys()):
    pct = row6_counts[s] / N_SIMULATIONS * 100
    print(f"  Score {s}: {row6_counts[s]:6d} ({pct:5.2f}%)")

p_row6 = sum(1 for s in random_row6_scores if s >= our_row6_score) / N_SIMULATIONS
print(f"P(random 3 positions score >= {our_row6_score}): {p_row6:.6f}")
print()


# --- TEST 5: Mod 6268 = POCC prefix (33) ---
print("TEST 5: Amount mod 6268 = POCC prefix sum (33)")
print("-" * 60)

our_mod = 256536737 % 6268
print(f"OUR: 256536737 mod 6268 = {our_mod}")
print(f"  Matches POCC prefix sum (33): {our_mod == 33}")
print()

# What's the probability?
# We checked mod 6268 specifically because it's the Signal day.
# Target values: 33 (POCC) or 46 (HASV)
# P(hitting 33 or 46 from mod 6268) = 2/6268
p_mod = 2 / 6268
print(f"P(random mod 6268 = 33 or 46): {p_mod:.6f} ({p_mod*100:.4f}%)")
print()

# BUT: How many different mod operations did we try?
# We need to count this for Bonferroni
print("CRITICAL: This test was ONE of many mod operations we performed.")
print("Must apply Bonferroni correction (see TEST 6).")
print()


# --- TEST 6: COMBINED P-VALUE ---
print("=" * 80)
print("TEST 6: COMBINED ASSESSMENT")
print("=" * 80)
print()

# Count our tests
print("Total modular operations performed in our analysis:")
mods_performed = [
    "amount mod 676", "amount mod 121", "amount mod 97", "amount mod 576",
    "amount mod 6268",
    "8011 mod 676", "8011 mod 121", "8011 mod 127", "8011 mod 128",
    "6268 mod 121", "6268 mod 97", "6268 mod 676", "6268 mod 576",
    "6268 mod 26", "6268 mod 24", "6268 mod 50",
    "6244 mod 676", "6244 mod 121", "6244 mod 576", "6244 mod 26",
    "6244 mod 24", "6244 mod 97", "6244 mod 41", "6244 mod 50",
    "6147 mod 676", "6147 mod 121",
    "22144 mod 121", "22144 mod 676", "22144 mod 127", "22144 mod 128",
    "22144 mod 26", "22144 mod 46",
    "536737 factorization check",
    "256536737 factorization check",
    "2050 mod 676",
    "41-19 difference check",
    "779 mod 121", "779 mod 676", "779 mod 26",
    "3526 mod 676", "3526 mod 121",
    "1009 mod 121",  # 8011's prime index
    "173 mod 26", "173 mod 11", "173 mod 6",
]
n_tests = len(mods_performed)
print(f"  Counted: {n_tests} distinct tests/operations")
print()

# Bonferroni correction
alpha = 0.05
corrected_alpha = alpha / n_tests
print(f"Bonferroni-corrected significance level:")
print(f"  α = {alpha} / {n_tests} = {corrected_alpha:.6f}")
print()

# Which findings survive?
print("FINDINGS VS. BONFERRONI THRESHOLD:")
print("-" * 60)

findings = [
    ("POCC+HASV combined (pre-existing)", 2.05e-8, "KNOWN"),
    ("Point Symmetry 99.58%", 1e-4, "KNOWN"),
    ("1CEq prefix match (4 chars)", 1/195112, "NEW"),
    ("Row 6 at positions 22,33,97 all =26", p_row6, "NEW"),
    ("536737 = 67×8011 properties", p_value_amount, "NEW"),
    ("97+24=121 timeline split", p_value_timeline, "NEW"),
    ("256536737 mod 6268 = 33", p_mod, "NEW"),
    ("Diagonal self-references", p_diag, "NEW"),
]

survivors = 0
for name, p, category in findings:
    survives = p < corrected_alpha
    status = "✅ SURVIVES" if survives else "❌ FAILS"
    if survives:
        survivors += 1
    print(f"  {status}: {name}")
    print(f"           p = {p:.2e}, threshold = {corrected_alpha:.2e} [{category}]")
    print()

print(f"SURVIVORS: {survivors} / {len(findings)}")
print()

# Final summary
print("=" * 80)
print("FINAL VERDICT")
print("=" * 80)
print()
print("TIER 1 - MATHEMATICALLY CERTAIN (survive all corrections):")
print("  These are the findings we can CONFIDENTLY claim.")
print()
print("TIER 2 - INTERESTING BUT NOT PROVEN:")
print("  These may be real patterns but don't survive Bonferroni.")
print("  Could be confirmation bias or lucky coincidence.")
print()
print("TIER 3 - LIKELY CHERRY-PICKED:")
print("  These probably exist because we looked at enough numbers.")
print()
