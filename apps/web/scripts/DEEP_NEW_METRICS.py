#!/usr/bin/env python3
"""
NEW POCC/HASV METRICS - QUICK WINS
====================================
Test 6 new metrics that have never been analyzed.
Each is validated by 100K Monte Carlo.
Only p < 0.01 (after Bonferroni for 6 tests = p < 0.0017) reported.

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-10
"""

import json
import numpy as np
from pathlib import Path
import time

MATRIX_FILE = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
with open(MATRIX_FILE, 'r') as f:
    data = json.load(f)
matrix = np.array(data['matrix'], dtype=np.int64)

POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def c2n(c):
    return ord(c) - ord('A')

pocc_nums = np.array([c2n(c) for c in POCC])
hasv_nums = np.array([c2n(c) for c in HASV])
diag_values = np.array([matrix[i][i] for i in range(26)], dtype=np.int64)

N_MC = 200_000
BONFERRONI = 12  # number of distinct tests
ALPHA = 0.01 / BONFERRONI  # corrected threshold

print("=" * 70)
print("NEW POCC/HASV METRICS")
print(f"Monte Carlo: {N_MC:,} trials per test")
print(f"Bonferroni correction: {BONFERRONI} tests → alpha = {ALPHA:.5f}")
print("=" * 70)
print()

results = []

# =============================================================================
# METRIC 1: Character Frequency Correlation with Diagonal Values
# =============================================================================
print("--- METRIC 1: Frequency-Diagonal Correlation ---")

def freq_diag_corr(nums):
    freq = np.bincount(nums, minlength=26)
    return float(np.corrcoef(freq, diag_values[:26])[0, 1])

obs_corr_p = freq_diag_corr(pocc_nums)
obs_corr_h = freq_diag_corr(hasv_nums)
obs_corr_diff = abs(obs_corr_p - obs_corr_h)

print(f"  POCC freq-diag correlation: {obs_corr_p:.4f}")
print(f"  HASV freq-diag correlation: {obs_corr_h:.4f}")
print(f"  |Difference|: {obs_corr_diff:.4f}")

np.random.seed(42)
mc_corr_diff = np.zeros(N_MC)
for i in range(N_MC):
    a1 = np.random.randint(0, 26, 60)
    a2 = np.random.randint(0, 26, 60)
    mc_corr_diff[i] = abs(freq_diag_corr(a1) - freq_diag_corr(a2))

p_corr = (mc_corr_diff >= obs_corr_diff).mean()
z_corr = (obs_corr_diff - mc_corr_diff.mean()) / mc_corr_diff.std()
sig = "SIGNIFICANT" if p_corr < ALPHA else "not significant"
print(f"  p = {p_corr:.5f}, z = {z_corr:.2f} [{sig}]")
results.append(("Freq-Diag Corr Diff", obs_corr_diff, p_corr, z_corr))
print()

# =============================================================================
# METRIC 2: Run-Length Analysis
# =============================================================================
print("--- METRIC 2: Run-Length Analysis ---")

def count_runs(addr):
    runs = 1
    for i in range(1, len(addr)):
        if addr[i] != addr[i-1]:
            runs += 1
    return runs

def count_doubles(addr):
    return sum(1 for i in range(len(addr)-1) if addr[i] == addr[i+1])

obs_runs_p = count_runs(POCC)
obs_runs_h = count_runs(HASV)
obs_doubles_p = count_doubles(POCC)
obs_doubles_h = count_doubles(HASV)
obs_run_diff = abs(obs_runs_p - obs_runs_h)
obs_double_diff = abs(obs_doubles_p - obs_doubles_h)

print(f"  POCC runs: {obs_runs_p}, doubles: {obs_doubles_p}")
print(f"  HASV runs: {obs_runs_h}, doubles: {obs_doubles_h}")
print(f"  |Run diff|: {obs_run_diff}, |Double diff|: {obs_double_diff}")

np.random.seed(42)
mc_run_diff = np.zeros(N_MC)
mc_double_diff = np.zeros(N_MC)
for i in range(N_MC):
    a1 = ''.join(chr(c + 65) for c in np.random.randint(0, 26, 60))
    a2 = ''.join(chr(c + 65) for c in np.random.randint(0, 26, 60))
    mc_run_diff[i] = abs(count_runs(a1) - count_runs(a2))
    mc_double_diff[i] = abs(count_doubles(a1) - count_doubles(a2))

p_runs = (mc_run_diff >= obs_run_diff).mean()
p_doubles = (mc_double_diff >= obs_double_diff).mean()
sig_r = "SIGNIFICANT" if p_runs < ALPHA else "not significant"
sig_d = "SIGNIFICANT" if p_doubles < ALPHA else "not significant"
print(f"  Runs: p = {p_runs:.5f} [{sig_r}]")
print(f"  Doubles: p = {p_doubles:.5f} [{sig_d}]")
results.append(("Run Diff", obs_run_diff, p_runs, 0))
results.append(("Double Diff", obs_double_diff, p_doubles, 0))
print()

# =============================================================================
# METRIC 3: Sliding Window Diagonal Sums
# =============================================================================
print("--- METRIC 3: Sliding Window Diagonal Sums ---")

for window in [4, 8, 12, 20]:
    diffs = []
    for start in range(60 - window + 1):
        d_p = sum(diag_values[pocc_nums[start:start+window]])
        d_h = sum(diag_values[hasv_nums[start:start+window]])
        diffs.append(int(d_h - d_p))

    diffs = np.array(diffs)
    n_26 = (diffs == 26).sum()
    n_121 = (diffs == 121).sum()
    n_neg26 = (diffs == -26).sum()
    n_0 = (diffs == 0).sum()

    # How many windows hit multiples of 26?
    n_mult26 = ((diffs != 0) & (diffs % 26 == 0)).sum()

    print(f"  Window {window}: {len(diffs)} windows")
    print(f"    diff=26: {n_26}, diff=-26: {n_neg26}, diff=121: {n_121}, diff=0: {n_0}")
    print(f"    Multiples of 26 (non-zero): {n_mult26} / {len(diffs)}")

    # Monte Carlo: how many multiples of 26 in random pairs?
    np.random.seed(42)
    mc_mult26 = np.zeros(N_MC // 10)  # fewer trials for speed
    for trial in range(len(mc_mult26)):
        a1 = np.random.randint(0, 26, 60)
        a2 = np.random.randint(0, 26, 60)
        trial_diffs = []
        for start in range(60 - window + 1):
            d1 = diag_values[a1[start:start+window]].sum()
            d2 = diag_values[a2[start:start+window]].sum()
            trial_diffs.append(int(d2 - d1))
        trial_diffs = np.array(trial_diffs)
        mc_mult26[trial] = ((trial_diffs != 0) & (trial_diffs % 26 == 0)).sum()

    p_mult = (mc_mult26 >= n_mult26).mean()
    sig = "SIGNIFICANT" if p_mult < ALPHA else "not significant"
    print(f"    MC p(mult26 >= {n_mult26}): {p_mult:.5f} [{sig}]")
    results.append((f"Window-{window} mult26", n_mult26, p_mult, 0))
    print()

# =============================================================================
# METRIC 4: Sorted Address Diagonal Sum
# =============================================================================
print("--- METRIC 4: Sorted Address Properties ---")

pocc_sorted = np.sort(pocc_nums)
hasv_sorted = np.sort(hasv_nums)
sorted_diag_p = int(diag_values[pocc_sorted].sum())
sorted_diag_h = int(diag_values[hasv_sorted].sum())
sorted_diff = sorted_diag_h - sorted_diag_p

print(f"  Sorted POCC diagonal: {sorted_diag_p}")
print(f"  Sorted HASV diagonal: {sorted_diag_h}")
print(f"  Sorted diff: {sorted_diff}")
print(f"  Original diff: 676")
print(f"  Match: {sorted_diff == 676}")
print(f"  (Sorting preserves frequencies, so diff MUST be 676)")
print()

# =============================================================================
# METRIC 5: Positional Entropy
# =============================================================================
print("--- METRIC 5: Positional Difference Pattern ---")

pos_diff = (hasv_nums - pocc_nums) % 26
print(f"  Position diffs (mod 26): {pos_diff.tolist()[:20]}...")
print(f"  Mean: {pos_diff.mean():.2f}")
print(f"  Std: {pos_diff.std():.2f}")

# Is the difference sequence periodic?
from collections import Counter
diff_freq = Counter(pos_diff.tolist())
print(f"  Most common diffs: {diff_freq.most_common(5)}")

# Autocorrelation
diff_centered = pos_diff - pos_diff.mean()
autocorr = np.correlate(diff_centered, diff_centered, 'full')
autocorr = autocorr[len(autocorr)//2:]  # positive lags only
autocorr = autocorr / autocorr[0]  # normalize
print(f"  Autocorrelation lag 1: {autocorr[1]:.4f}")
print(f"  Autocorrelation lag 2: {autocorr[2]:.4f}")
print(f"  Autocorrelation lag 3: {autocorr[3]:.4f}")

# MC test for autocorrelation
np.random.seed(42)
mc_ac1 = np.zeros(N_MC)
for i in range(N_MC):
    a1 = np.random.randint(0, 26, 60)
    a2 = np.random.randint(0, 26, 60)
    d = (a2 - a1) % 26
    dc = d - d.mean()
    ac = np.correlate(dc, dc, 'full')
    ac = ac[len(ac)//2:]
    if ac[0] > 0:
        mc_ac1[i] = ac[1] / ac[0]

obs_ac1 = autocorr[1]
p_ac1 = (np.abs(mc_ac1) >= abs(obs_ac1)).mean()
sig = "SIGNIFICANT" if p_ac1 < ALPHA else "not significant"
print(f"  Autocorrelation p = {p_ac1:.5f} [{sig}]")
results.append(("Autocorrelation lag-1", obs_ac1, p_ac1, 0))
print()

# =============================================================================
# METRIC 6: Character Position Sum Products
# =============================================================================
print("--- METRIC 6: Position-Weighted Sums ---")

# Sum of (character_value * position)
pos_weight_p = sum(pocc_nums[i] * i for i in range(60))
pos_weight_h = sum(hasv_nums[i] * i for i in range(60))
pos_weight_diff = abs(pos_weight_h - pos_weight_p)

print(f"  POCC position-weighted sum: {pos_weight_p}")
print(f"  HASV position-weighted sum: {pos_weight_h}")
print(f"  |Difference|: {pos_weight_diff}")
print(f"  Diff mod 676: {pos_weight_diff % 676}")
print(f"  Diff mod 26: {pos_weight_diff % 26}")

np.random.seed(42)
mc_pw_diff = np.zeros(N_MC)
for i in range(N_MC):
    a1 = np.random.randint(0, 26, 60)
    a2 = np.random.randint(0, 26, 60)
    pw1 = sum(a1[j] * j for j in range(60))
    pw2 = sum(a2[j] * j for j in range(60))
    mc_pw_diff[i] = abs(pw2 - pw1)

p_pw = (mc_pw_diff >= pos_weight_diff).mean()
z_pw = (pos_weight_diff - mc_pw_diff.mean()) / mc_pw_diff.std()
sig = "SIGNIFICANT" if p_pw < ALPHA else "not significant"
print(f"  p = {p_pw:.5f}, z = {z_pw:.2f} [{sig}]")
results.append(("Position-weighted diff", pos_weight_diff, p_pw, z_pw))
print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 70)
print("SUMMARY OF ALL METRICS")
print("=" * 70)
print()
print(f"Bonferroni threshold: p < {ALPHA:.5f}")
print()

significant = []
for name, val, p, z in results:
    status = "*** SIGNIFICANT ***" if p < ALPHA else ""
    print(f"  {name:30s}: value={val}, p={p:.5f} {status}")
    if p < ALPHA:
        significant.append((name, val, p, z))

print()
if significant:
    print(f"SIGNIFICANT FINDINGS ({len(significant)}):")
    for name, val, p, z in significant:
        print(f"  {name}: p = {p:.6f} (Bonferroni threshold: {ALPHA:.5f})")
else:
    print("NO significant new metrics found after Bonferroni correction.")
    print("The existing 3 properties (diagonal=676, charsum=138, identical>=6)")
    print("remain the only statistically significant connections.")

print()
print("=" * 70)
print("COMPLETE")
print("=" * 70)
