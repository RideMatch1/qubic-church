#!/usr/bin/env python3
"""
===============================================================================
        CONTROL MATRIX BASELINE - Random Matrix Comparison
===============================================================================
Generates random 128x128 signed byte matrices and runs ALL key metrics
against them to establish baselines. This answers the fundamental question:

  "Is the Anna Matrix special, or would ANY matrix show these patterns?"

For each metric, we compare the Anna Matrix value against the distribution
of values from 10,000 random matrices.

PRE-REGISTERED HYPOTHESES (stated before running):
  H1: Anna Matrix point symmetry (99.58%) is higher than any random matrix
  H2: Anna Matrix Row 6 value-26 bias (24/128) is higher than expected
  H3: POCC/HASV diagonal difference (676) is unusual for random address pairs
  H4: Anna Matrix has lower entropy per row than random matrices
  H5: Anna Matrix tick-loop convergence differs from random matrices

SIGNIFICANCE THRESHOLD: p < 0.001 (with Bonferroni correction: p < 0.0002)
"""

import json
import numpy as np
import hashlib
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

script_dir = Path(__file__).parent
SIMULATIONS = 10000
SIGNIFICANCE = 0.001
BONFERRONI_TESTS = 5
CORRECTED_SIGNIFICANCE = SIGNIFICANCE / BONFERRONI_TESTS

print("=" * 80)
print("         CONTROL MATRIX BASELINE")
print("         Random Matrix Comparison")
print("=" * 80)
print(f"\nSimulations: {SIMULATIONS:,}")
print(f"Significance: p < {SIGNIFICANCE} (Bonferroni-corrected: p < {CORRECTED_SIGNIFICANCE})")
print(f"Date: {datetime.now().isoformat()}")
print()

# ============================================================================
# LOAD ANNA MATRIX
# ============================================================================
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

anna_matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]], dtype=np.int16)
print(f"Anna Matrix loaded: {anna_matrix.shape}")
print(f"Value range: [{anna_matrix.min()}, {anna_matrix.max()}]")

# Get value distribution of Anna Matrix for generating similar random matrices
anna_values = anna_matrix.flatten()
anna_value_counts = Counter(anna_values)
anna_unique_values = sorted(anna_value_counts.keys())
anna_value_probs = np.array([anna_value_counts[v] for v in anna_unique_values], dtype=float)
anna_value_probs /= anna_value_probs.sum()

print(f"Unique values: {len(anna_unique_values)}")
print(f"Mean: {anna_values.mean():.2f}, Std: {anna_values.std():.2f}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_random_matrix(match_distribution=False):
    """Generate a random 128x128 matrix.
    If match_distribution=True, uses same value distribution as Anna Matrix.
    Otherwise uses uniform random signed bytes [-128, 127].
    """
    if match_distribution:
        values = np.random.choice(anna_unique_values, size=(128, 128), p=anna_value_probs)
        return values.astype(np.int16)
    else:
        return np.random.randint(-128, 128, size=(128, 128), dtype=np.int16)


def compute_point_symmetry(m):
    """Compute percentage of cells where m[r,c] + m[127-r, 127-c] = -1"""
    count = 0
    total = 0
    for r in range(128):
        for c in range(128):
            if r == 127 - r and c == 127 - c:
                continue  # Skip center point
            total += 1
            if m[r, c] + m[127 - r, 127 - c] == -1:
                count += 1
    return count / total * 100 if total > 0 else 0


def compute_row_max_frequency(m, row_idx):
    """For a given row, find the most common value and its frequency."""
    row = m[row_idx, :]
    counter = Counter(row)
    most_common_val, most_common_count = counter.most_common(1)[0]
    return most_common_val, most_common_count


def compute_row_entropy(m, row_idx):
    """Shannon entropy of a row's value distribution."""
    row = m[row_idx, :]
    counter = Counter(row)
    total = len(row)
    entropy = 0
    for count in counter.values():
        p = count / total
        if p > 0:
            entropy -= p * np.log2(p)
    return entropy


def compute_diagonal_sum(m, address_str):
    """Sum matrix[c][c] for each character c in address (A=0, B=1, ..., Z=25)"""
    total = 0
    for ch in address_str.upper():
        idx = ord(ch) - ord('A')
        if 0 <= idx < 128:
            total += int(m[idx, idx])
    return total


def compute_address_char_sum(address_str):
    """Sum character values (A=0, B=1, ..., Z=25)"""
    return sum(ord(ch) - ord('A') for ch in address_str.upper())


def generate_random_qubic_address(length=60):
    """Generate a random Qubic-like address (uppercase A-Z only, 60 chars)."""
    return ''.join(chr(np.random.randint(0, 26) + ord('A')) for _ in range(length))


def simple_tick_loop(m, input_states, max_ticks=100):
    """Simplified tick-loop: 64 input neurons, 64 output neurons.
    Each output neuron takes weighted sum of 8 nearest input neighbors.
    Returns (energy, ticks_to_converge, converged).
    """
    n_inputs = 64
    n_outputs = 64
    states = list(input_states[:n_inputs]) + [0] * n_outputs

    for tick in range(max_ticks):
        changed = False
        for i in range(n_outputs):
            neuron_idx = n_inputs + i
            # 8 neighbors from input layer
            neighbors = [(i * 8 + j) % n_inputs for j in range(8)]
            weighted_sum = sum(states[n] * int(m[neuron_idx % 128, n % 128]) for n in neighbors)

            # Ternary clamp
            if weighted_sum > 0:
                new_state = 1
            elif weighted_sum < 0:
                new_state = -1
            else:
                new_state = 0

            if states[neuron_idx] != new_state:
                states[neuron_idx] = new_state
                changed = True

        if not changed:
            return sum(states), tick + 1, True

    return sum(states), max_ticks, False


# ============================================================================
# TEST 1: POINT SYMMETRY (H1)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: Point Symmetry")
print("  H1: Anna Matrix (99.58%) is higher than any random matrix")
print("=" * 80)

anna_symmetry = compute_point_symmetry(anna_matrix)
print(f"\n  Anna Matrix symmetry: {anna_symmetry:.4f}%")

random_symmetries = []
print(f"  Running {SIMULATIONS:,} random matrices (matching distribution)...", end="", flush=True)
for i in range(SIMULATIONS):
    rm = generate_random_matrix(match_distribution=True)
    sym = compute_point_symmetry(rm)
    random_symmetries.append(sym)
    if (i + 1) % 1000 == 0:
        print(f" {i+1}", end="", flush=True)
print()

random_symmetries = np.array(random_symmetries)
p_value_1 = np.mean(random_symmetries >= anna_symmetry)
print(f"\n  Random matrix symmetry:")
print(f"    Mean:   {random_symmetries.mean():.4f}%")
print(f"    Std:    {random_symmetries.std():.4f}%")
print(f"    Max:    {random_symmetries.max():.4f}%")
print(f"    Min:    {random_symmetries.min():.4f}%")
print(f"\n  p-value: {p_value_1}")
print(f"  Significant (p < {CORRECTED_SIGNIFICANCE})? {'YES' if p_value_1 < CORRECTED_SIGNIFICANCE else 'NO'}")
test1_result = "SIGNIFICANT" if p_value_1 < CORRECTED_SIGNIFICANCE else "NOT SIGNIFICANT"
print(f"\n  RESULT: {test1_result}")

# ============================================================================
# TEST 2: ROW 6 VALUE-26 BIAS (H2)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: Row 6 Value-26 Bias")
print("  H2: Row 6 has 24/128 cells with value 26 (18.8%), expected ~0.78%")
print("=" * 80)

anna_row6_val, anna_row6_count = compute_row_max_frequency(anna_matrix, 6)
print(f"\n  Anna Matrix Row 6: value {anna_row6_val} appears {anna_row6_count}/128 times ({anna_row6_count/128*100:.1f}%)")
print(f"  Specifically value 26: {np.sum(anna_matrix[6, :] == 26)}/128 times")

anna_row6_26_count = int(np.sum(anna_matrix[6, :] == 26))

# Test: How often does ANY value appear >= anna_row6_26_count times in a random row?
random_max_freqs = []
random_26_freqs = []
print(f"  Running {SIMULATIONS:,} random matrices...", end="", flush=True)
for i in range(SIMULATIONS):
    rm = generate_random_matrix(match_distribution=True)
    _, max_freq = compute_row_max_frequency(rm, 6)
    random_max_freqs.append(max_freq)
    random_26_freqs.append(int(np.sum(rm[6, :] == 26)))
    if (i + 1) % 2000 == 0:
        print(f" {i+1}", end="", flush=True)
print()

random_max_freqs = np.array(random_max_freqs)
random_26_freqs = np.array(random_26_freqs)

# p-value: How often does value 26 appear >= 24 times in Row 6 of random matrix?
p_value_2a = np.mean(random_26_freqs >= anna_row6_26_count)
# Also: How often does ANY value appear >= 24 times in Row 6?
p_value_2b = np.mean(random_max_freqs >= anna_row6_26_count)

print(f"\n  Random Row 6 (value 26 frequency):")
print(f"    Mean:   {random_26_freqs.mean():.2f}/128")
print(f"    Max:    {random_26_freqs.max()}/128")
print(f"    p(26 appears >= {anna_row6_26_count} times): {p_value_2a}")
print(f"\n  Random Row 6 (ANY value max frequency):")
print(f"    Mean max:  {random_max_freqs.mean():.2f}/128")
print(f"    Max max:   {random_max_freqs.max()}/128")
print(f"    p(any value >= {anna_row6_26_count}): {p_value_2b}")

p_value_2 = p_value_2a  # Use the specific test
print(f"\n  p-value (specific): {p_value_2}")
print(f"  Significant (p < {CORRECTED_SIGNIFICANCE})? {'YES' if p_value_2 < CORRECTED_SIGNIFICANCE else 'NO'}")
test2_result = "SIGNIFICANT" if p_value_2 < CORRECTED_SIGNIFICANCE else "NOT SIGNIFICANT"
print(f"\n  RESULT: {test2_result}")

# ============================================================================
# TEST 3: POCC/HASV DIAGONAL DIFFERENCE (H3)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: POCC/HASV Diagonal Difference = 676")
print("  H3: Random address pairs rarely have diagonal diff = 676")
print("=" * 80)

POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

anna_pocc_diag = compute_diagonal_sum(anna_matrix, POCC)
anna_hasv_diag = compute_diagonal_sum(anna_matrix, HASV)
anna_diag_diff = anna_hasv_diag - anna_pocc_diag
print(f"\n  POCC diagonal: {anna_pocc_diag}")
print(f"  HASV diagonal: {anna_hasv_diag}")
print(f"  Difference: {anna_diag_diff}")

# Test with random address pairs on Anna Matrix
random_diag_diffs = []
print(f"  Running {SIMULATIONS:,} random address pairs on Anna Matrix...", end="", flush=True)
for i in range(SIMULATIONS):
    addr1 = generate_random_qubic_address()
    addr2 = generate_random_qubic_address()
    d1 = compute_diagonal_sum(anna_matrix, addr1)
    d2 = compute_diagonal_sum(anna_matrix, addr2)
    random_diag_diffs.append(abs(d2 - d1))
    if (i + 1) % 2000 == 0:
        print(f" {i+1}", end="", flush=True)
print()

random_diag_diffs = np.array(random_diag_diffs)
p_value_3 = np.mean(random_diag_diffs >= abs(anna_diag_diff))

print(f"\n  Random address pair diagonal differences:")
print(f"    Mean:   {random_diag_diffs.mean():.2f}")
print(f"    Std:    {random_diag_diffs.std():.2f}")
print(f"    Max:    {random_diag_diffs.max()}")
print(f"    Median: {np.median(random_diag_diffs):.0f}")
print(f"    p(diff >= {abs(anna_diag_diff)}): {p_value_3}")
print(f"\n  p-value: {p_value_3}")
print(f"  Significant (p < {CORRECTED_SIGNIFICANCE})? {'YES' if p_value_3 < CORRECTED_SIGNIFICANCE else 'NO'}")
test3_result = "SIGNIFICANT" if p_value_3 < CORRECTED_SIGNIFICANCE else "NOT SIGNIFICANT"
print(f"\n  RESULT: {test3_result}")

# ============================================================================
# TEST 4: ROW ENTROPY (H4)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: Row Entropy Distribution")
print("  H4: Anna Matrix has different entropy per row than random matrices")
print("=" * 80)

anna_entropies = [compute_row_entropy(anna_matrix, r) for r in range(128)]
anna_mean_entropy = np.mean(anna_entropies)
anna_min_entropy = np.min(anna_entropies)
anna_min_entropy_row = np.argmin(anna_entropies)
print(f"\n  Anna Matrix:")
print(f"    Mean row entropy: {anna_mean_entropy:.4f} bits")
print(f"    Min row entropy:  {anna_min_entropy:.4f} bits (Row {anna_min_entropy_row})")
print(f"    Max row entropy:  {np.max(anna_entropies):.4f} bits (Row {np.argmax(anna_entropies)})")
print(f"    Row 6 entropy:    {anna_entropies[6]:.4f} bits")

random_mean_entropies = []
random_min_entropies = []
print(f"  Running {SIMULATIONS:,} random matrices...", end="", flush=True)
for i in range(SIMULATIONS):
    rm = generate_random_matrix(match_distribution=True)
    entropies = [compute_row_entropy(rm, r) for r in range(128)]
    random_mean_entropies.append(np.mean(entropies))
    random_min_entropies.append(np.min(entropies))
    if (i + 1) % 1000 == 0:
        print(f" {i+1}", end="", flush=True)
print()

random_mean_entropies = np.array(random_mean_entropies)
random_min_entropies = np.array(random_min_entropies)

# p-value: Is Anna's mean entropy lower than random?
p_value_4a = np.mean(random_mean_entropies <= anna_mean_entropy)
# p-value: Is Anna's minimum row entropy lower than random?
p_value_4b = np.mean(random_min_entropies <= anna_min_entropy)

print(f"\n  Random matrices:")
print(f"    Mean entropy: {random_mean_entropies.mean():.4f} +/- {random_mean_entropies.std():.4f}")
print(f"    Min entropy (per matrix): {random_min_entropies.mean():.4f} +/- {random_min_entropies.std():.4f}")
print(f"\n  p(mean entropy <= {anna_mean_entropy:.4f}): {p_value_4a}")
print(f"  p(min entropy <= {anna_min_entropy:.4f}): {p_value_4b}")

p_value_4 = p_value_4b  # Use min entropy as primary test
print(f"\n  p-value (min entropy): {p_value_4}")
print(f"  Significant (p < {CORRECTED_SIGNIFICANCE})? {'YES' if p_value_4 < CORRECTED_SIGNIFICANCE else 'NO'}")
test4_result = "SIGNIFICANT" if p_value_4 < CORRECTED_SIGNIFICANCE else "NOT SIGNIFICANT"
print(f"\n  RESULT: {test4_result}")

# ============================================================================
# TEST 5: TICK-LOOP CONVERGENCE (H5)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: Tick-Loop Convergence")
print("  H5: Anna Matrix tick-loop behaves differently from random matrices")
print("=" * 80)

# Generate 100 random inputs
n_test_inputs = 100
test_inputs = []
for _ in range(n_test_inputs):
    inp = [np.random.choice([-1, 0, 1]) for _ in range(64)]
    test_inputs.append(inp)

# Run on Anna Matrix
print(f"\n  Running {n_test_inputs} inputs on Anna Matrix...", end="", flush=True)
anna_energies = []
anna_ticks = []
anna_converged = []
for inp in test_inputs:
    energy, ticks, converged = simple_tick_loop(anna_matrix, inp)
    anna_energies.append(energy)
    anna_ticks.append(ticks)
    anna_converged.append(converged)
print(" done")

anna_convergence_rate = sum(anna_converged) / len(anna_converged)
anna_mean_energy = np.mean(anna_energies)
anna_mean_ticks = np.mean(anna_ticks)
print(f"  Anna Matrix results:")
print(f"    Convergence rate: {anna_convergence_rate:.2%}")
print(f"    Mean energy: {anna_mean_energy:.2f}")
print(f"    Mean ticks: {anna_mean_ticks:.1f}")

# Run on random matrices (fewer due to computational cost)
n_random_matrices = 100
print(f"  Running {n_test_inputs} inputs on {n_random_matrices} random matrices...", end="", flush=True)
random_convergence_rates = []
random_mean_energies = []
random_mean_ticks_list = []
for i in range(n_random_matrices):
    rm = generate_random_matrix(match_distribution=True)
    energies = []
    ticks_list = []
    converged_list = []
    for inp in test_inputs:
        energy, ticks, converged = simple_tick_loop(rm, inp)
        energies.append(energy)
        ticks_list.append(ticks)
        converged_list.append(converged)
    random_convergence_rates.append(sum(converged_list) / len(converged_list))
    random_mean_energies.append(np.mean(energies))
    random_mean_ticks_list.append(np.mean(ticks_list))
    if (i + 1) % 20 == 0:
        print(f" {i+1}", end="", flush=True)
print()

random_convergence_rates = np.array(random_convergence_rates)
random_mean_energies = np.array(random_mean_energies)

# p-value for convergence rate
p_conv = np.mean(random_convergence_rates >= anna_convergence_rate) if anna_convergence_rate > np.mean(random_convergence_rates) else np.mean(random_convergence_rates <= anna_convergence_rate)
# p-value for energy magnitude
anna_abs_energy = abs(anna_mean_energy)
random_abs_energies = np.abs(random_mean_energies)
p_energy = np.mean(random_abs_energies >= anna_abs_energy)

print(f"\n  Random matrices (n={n_random_matrices}):")
print(f"    Convergence rate: {random_convergence_rates.mean():.2%} +/- {random_convergence_rates.std():.2%}")
print(f"    Mean energy: {random_mean_energies.mean():.2f} +/- {random_mean_energies.std():.2f}")
print(f"    Mean ticks: {np.mean(random_mean_ticks_list):.1f}")
print(f"\n  p(convergence rate): {p_conv}")
print(f"  p(|energy| >= {anna_abs_energy:.2f}): {p_energy}")

p_value_5 = min(p_conv, p_energy)
print(f"\n  p-value (min): {p_value_5}")
print(f"  Significant (p < {CORRECTED_SIGNIFICANCE})? {'YES' if p_value_5 < CORRECTED_SIGNIFICANCE else 'NO'}")
test5_result = "SIGNIFICANT" if p_value_5 < CORRECTED_SIGNIFICANCE else "NOT SIGNIFICANT"
print(f"\n  RESULT: {test5_result}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY - CONTROL MATRIX BASELINE")
print("=" * 80)

results = {
    "date": datetime.now().isoformat(),
    "simulations": SIMULATIONS,
    "significance_threshold": SIGNIFICANCE,
    "bonferroni_corrected": CORRECTED_SIGNIFICANCE,
    "tests": {
        "H1_point_symmetry": {
            "anna_value": anna_symmetry,
            "random_mean": float(random_symmetries.mean()),
            "random_max": float(random_symmetries.max()),
            "p_value": float(p_value_1),
            "significant": bool(p_value_1 < CORRECTED_SIGNIFICANCE),
            "result": test1_result
        },
        "H2_row6_bias": {
            "anna_value": anna_row6_26_count,
            "random_mean": float(random_26_freqs.mean()),
            "random_max": int(random_26_freqs.max()),
            "p_value": float(p_value_2),
            "significant": bool(p_value_2 < CORRECTED_SIGNIFICANCE),
            "result": test2_result
        },
        "H3_diagonal_difference": {
            "anna_value": int(anna_diag_diff),
            "random_mean": float(random_diag_diffs.mean()),
            "random_max": int(random_diag_diffs.max()),
            "p_value": float(p_value_3),
            "significant": bool(p_value_3 < CORRECTED_SIGNIFICANCE),
            "result": test3_result
        },
        "H4_row_entropy": {
            "anna_mean_entropy": float(anna_mean_entropy),
            "anna_min_entropy": float(anna_min_entropy),
            "anna_min_entropy_row": int(anna_min_entropy_row),
            "random_mean_entropy": float(random_mean_entropies.mean()),
            "random_min_entropy_mean": float(random_min_entropies.mean()),
            "p_value": float(p_value_4),
            "significant": bool(p_value_4 < CORRECTED_SIGNIFICANCE),
            "result": test4_result
        },
        "H5_tick_loop": {
            "anna_convergence_rate": float(anna_convergence_rate),
            "anna_mean_energy": float(anna_mean_energy),
            "random_convergence_mean": float(random_convergence_rates.mean()),
            "random_energy_mean": float(random_mean_energies.mean()),
            "p_value": float(p_value_5),
            "significant": bool(p_value_5 < CORRECTED_SIGNIFICANCE),
            "result": test5_result
        }
    }
}

print(f"\n{'Test':<40} {'Anna':<15} {'Random Mean':<15} {'p-value':<12} {'Result':<15}")
print("-" * 97)
print(f"{'H1: Point Symmetry':<40} {anna_symmetry:.2f}%{'':<8} {random_symmetries.mean():.2f}%{'':<8} {p_value_1:<12.6f} {test1_result}")
print(f"{'H2: Row 6 Value-26 Count':<40} {anna_row6_26_count}/128{'':<8} {random_26_freqs.mean():.1f}/128{'':<5} {p_value_2:<12.6f} {test2_result}")
print(f"{'H3: Diagonal Diff (POCC/HASV)':<40} {anna_diag_diff:<15} {random_diag_diffs.mean():<15.1f} {p_value_3:<12.6f} {test3_result}")
print(f"{'H4: Min Row Entropy':<40} {anna_min_entropy:<15.4f} {random_min_entropies.mean():<15.4f} {p_value_4:<12.6f} {test4_result}")
print(f"{'H5: Tick-Loop Convergence':<40} {anna_convergence_rate:<15.2%} {random_convergence_rates.mean():<15.2%} {p_value_5:<12.6f} {test5_result}")

significant_count = sum(1 for t in results["tests"].values() if t["significant"])
print(f"\n  Significant results: {significant_count}/5")
print(f"  Non-significant: {5 - significant_count}/5")

# Save results
output_path = script_dir / "CONTROL_MATRIX_BASELINE_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n  Results saved to: {output_path}")

print("\n" + "=" * 80)
print("  INTERPRETATION GUIDE:")
print("  - SIGNIFICANT = Anna Matrix is genuinely special for this metric")
print("  - NOT SIGNIFICANT = Random matrices show similar values")
print("  - This does NOT prove intentional design, only statistical unusualness")
print("=" * 80)
