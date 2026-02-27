#!/usr/bin/env python3
"""
===============================================================================
        TICK-LOOP BEHAVIOR STUDY - Neural Network Analysis
===============================================================================
Studies the Anna Matrix's behavior AS A NEURAL NETWORK.

The tick-loop implements a Hopfield-like recurrent ternary network:
- 128 neurons total (64 input, 64 output)
- Each output neuron takes weighted sum of 8 input neighbors
- Weights from Anna Matrix
- Ternary activation: clamp(sum) -> {-1, 0, +1}
- Iterates until convergence or max ticks

KEY QUESTIONS:
  Q1: Does the Anna Matrix produce more convergence than random matrices?
  Q2: Are there attractor states? (Fixed outputs for many different inputs)
  Q3: What is the energy distribution for random inputs?
  Q4: Is the Anna Matrix's convergence behavior statistically unusual?

CONTROL: 100 random matrices (same value distribution)
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from datetime import datetime

script_dir = Path(__file__).parent

print("=" * 80)
print("         TICK-LOOP BEHAVIOR STUDY")
print("         Neural Network Analysis")
print("=" * 80)
print(f"\nDate: {datetime.now().isoformat()}")

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

anna_matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]], dtype=np.int16)
print(f"Anna Matrix loaded: {anna_matrix.shape}")

# Parameters
N_INPUTS = 1000  # Random inputs to test
N_RANDOM_MATRICES = 100  # Control matrices
MAX_TICKS = 200

# ============================================================================
# TICK-LOOP IMPLEMENTATION
# ============================================================================

def tick_loop(matrix, input_states, max_ticks=MAX_TICKS):
    """Simplified tick-loop matching resonance-core.ts behavior.
    64 input neurons (fixed), 64 output neurons (computed).
    Each output neuron i has 8 neighbors from input layer.
    """
    n_in = 64
    n_out = 64
    states = list(input_states[:n_in]) + [0] * n_out

    ticks_to_converge = max_ticks
    converged = False
    energy_history = []

    for tick in range(max_ticks):
        changed = False
        for i in range(n_out):
            neuron_idx = n_in + i
            # 8 neighbors from input layer (circular)
            neighbors = [(i * 8 + j) % n_in for j in range(8)]
            weighted_sum = sum(
                states[n] * int(matrix[neuron_idx % 128, n % 128])
                for n in neighbors
            )

            # Ternary clamp
            new_state = 1 if weighted_sum > 0 else (-1 if weighted_sum < 0 else 0)

            if states[neuron_idx] != new_state:
                states[neuron_idx] = new_state
                changed = True

        energy = sum(states)
        energy_history.append(energy)

        # Check all outputs non-zero
        all_nonzero = all(states[n_in + j] != 0 for j in range(n_out))

        if not changed:
            ticks_to_converge = tick + 1
            converged = True
            break

        if all_nonzero and tick > 0:
            ticks_to_converge = tick + 1
            converged = True
            break

    output_pattern = tuple(states[n_in:])
    return {
        'energy': sum(states),
        'ticks': ticks_to_converge,
        'converged': converged,
        'output_pattern': output_pattern,
        'output_states': states[n_in:],
        'energy_history': energy_history,
    }


def generate_random_input():
    """Generate random ternary input (64 values of -1, 0, or +1)."""
    return [int(np.random.choice([-1, 0, 1])) for _ in range(64)]


def generate_random_matrix():
    """Generate random matrix with same distribution as Anna Matrix."""
    anna_vals = anna_matrix.flatten()
    vals = np.random.choice(anna_vals, size=(128, 128))
    return vals.astype(np.int16)


# ============================================================================
# PHASE 1: Anna Matrix Behavior
# ============================================================================
print("\n" + "=" * 80)
print(f"PHASE 1: Anna Matrix with {N_INPUTS} Random Inputs")
print("=" * 80)

# Generate test inputs (same for Anna and random matrices)
test_inputs = [generate_random_input() for _ in range(N_INPUTS)]

print(f"\n  Running {N_INPUTS} inputs through Anna Matrix tick-loop...", end="", flush=True)
anna_results = []
for i, inp in enumerate(test_inputs):
    result = tick_loop(anna_matrix, inp)
    anna_results.append(result)
    if (i + 1) % 200 == 0:
        print(f" {i+1}", end="", flush=True)
print(" done")

anna_energies = [r['energy'] for r in anna_results]
anna_ticks = [r['ticks'] for r in anna_results]
anna_converged = [r['converged'] for r in anna_results]
anna_patterns = [r['output_pattern'] for r in anna_results]

anna_convergence_rate = sum(anna_converged) / len(anna_converged)
anna_mean_energy = np.mean(anna_energies)
anna_mean_ticks = np.mean(anna_ticks)

# Count unique output patterns (attractors)
anna_pattern_counter = Counter(anna_patterns)
anna_unique_patterns = len(anna_pattern_counter)
anna_top_patterns = anna_pattern_counter.most_common(10)

print(f"\n  Anna Matrix Results:")
print(f"    Convergence rate: {anna_convergence_rate:.2%}")
print(f"    Mean energy: {anna_mean_energy:.2f} (range: [{min(anna_energies)}, {max(anna_energies)}])")
print(f"    Mean ticks to converge: {anna_mean_ticks:.1f}")
print(f"    Unique output patterns: {anna_unique_patterns} / {N_INPUTS}")
print(f"    Top pattern frequency: {anna_top_patterns[0][1]} inputs -> same output")

# Energy distribution
energy_counter = Counter(anna_energies)
print(f"\n  Energy Distribution (top 10):")
for energy, count in sorted(energy_counter.items(), key=lambda x: -x[1])[:10]:
    pct = count / N_INPUTS * 100
    print(f"    Energy {energy:>4}: {count:>4} ({pct:.1f}%)")

# ============================================================================
# PHASE 2: Attractor Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 2: Attractor Analysis")
print("=" * 80)

print(f"\n  Total unique output patterns (attractors): {anna_unique_patterns}")
print(f"\n  Top 10 Attractors:")
for i, (pattern, count) in enumerate(anna_top_patterns):
    energy = sum(pattern)
    nonzero = sum(1 for s in pattern if s != 0)
    positive = sum(1 for s in pattern if s > 0)
    negative = sum(1 for s in pattern if s < 0)
    print(f"    #{i+1}: {count} inputs converge here | energy={energy}, +1s={positive}, -1s={negative}, 0s={64-nonzero}")

# Are most inputs converging to a few attractors or many unique states?
cumulative = 0
for i, (_, count) in enumerate(anna_pattern_counter.most_common()):
    cumulative += count
    if cumulative >= N_INPUTS * 0.5:
        print(f"\n  50% of inputs converge to {i+1} attractors")
        break

cumulative = 0
for i, (_, count) in enumerate(anna_pattern_counter.most_common()):
    cumulative += count
    if cumulative >= N_INPUTS * 0.9:
        print(f"  90% of inputs converge to {i+1} attractors")
        break

# ============================================================================
# PHASE 3: Random Matrix Comparison
# ============================================================================
print("\n" + "=" * 80)
print(f"PHASE 3: Random Matrix Comparison ({N_RANDOM_MATRICES} matrices)")
print("=" * 80)

random_convergence_rates = []
random_mean_energies = []
random_mean_ticks_list = []
random_unique_patterns_list = []
random_top_pattern_freqs = []

print(f"\n  Running {N_INPUTS} inputs on {N_RANDOM_MATRICES} random matrices...", end="", flush=True)
# Use subset for random matrices (computational cost)
test_inputs_subset = test_inputs[:200]

for m_idx in range(N_RANDOM_MATRICES):
    rm = generate_random_matrix()
    rm_results = []
    for inp in test_inputs_subset:
        result = tick_loop(rm, inp, max_ticks=100)  # Shorter for speed
        rm_results.append(result)

    rm_energies = [r['energy'] for r in rm_results]
    rm_converged = [r['converged'] for r in rm_results]
    rm_ticks = [r['ticks'] for r in rm_results]
    rm_patterns = [r['output_pattern'] for r in rm_results]

    random_convergence_rates.append(sum(rm_converged) / len(rm_converged))
    random_mean_energies.append(np.mean(rm_energies))
    random_mean_ticks_list.append(np.mean(rm_ticks))

    rm_pattern_counter = Counter(rm_patterns)
    random_unique_patterns_list.append(len(rm_pattern_counter))
    random_top_pattern_freqs.append(rm_pattern_counter.most_common(1)[0][1])

    if (m_idx + 1) % 20 == 0:
        print(f" {m_idx+1}", end="", flush=True)
print(" done")

random_convergence_rates = np.array(random_convergence_rates)
random_mean_energies = np.array(random_mean_energies)
random_mean_ticks = np.array(random_mean_ticks_list)
random_unique_patterns_arr = np.array(random_unique_patterns_list)
random_top_pattern_freqs = np.array(random_top_pattern_freqs)

print(f"\n  Random Matrix Results (n={N_RANDOM_MATRICES}, {len(test_inputs_subset)} inputs each):")
print(f"    Convergence rate: {random_convergence_rates.mean():.2%} +/- {random_convergence_rates.std():.2%}")
print(f"    Mean energy: {random_mean_energies.mean():.2f} +/- {random_mean_energies.std():.2f}")
print(f"    Mean ticks: {random_mean_ticks.mean():.1f} +/- {random_mean_ticks.std():.1f}")
print(f"    Unique patterns: {random_unique_patterns_arr.mean():.0f} +/- {random_unique_patterns_arr.std():.0f}")
print(f"    Top pattern freq: {random_top_pattern_freqs.mean():.1f} +/- {random_top_pattern_freqs.std():.1f}")

# ============================================================================
# PHASE 4: Statistical Comparison
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 4: Statistical Comparison")
print("=" * 80)

# Use Anna results on same subset for fair comparison
anna_subset_results = anna_results[:200]
anna_sub_conv = sum(r['converged'] for r in anna_subset_results) / len(anna_subset_results)
anna_sub_energy = np.mean([r['energy'] for r in anna_subset_results])
anna_sub_patterns = len(Counter([r['output_pattern'] for r in anna_subset_results]))
anna_sub_top = Counter([r['output_pattern'] for r in anna_subset_results]).most_common(1)[0][1]

# p-values
p_conv = np.mean(random_convergence_rates >= anna_sub_conv) if anna_sub_conv > random_convergence_rates.mean() else np.mean(random_convergence_rates <= anna_sub_conv)
p_energy = 2 * min(np.mean(random_mean_energies <= anna_sub_energy), np.mean(random_mean_energies >= anna_sub_energy))
p_patterns = np.mean(random_unique_patterns_arr <= anna_sub_patterns) if anna_sub_patterns < random_unique_patterns_arr.mean() else np.mean(random_unique_patterns_arr >= anna_sub_patterns)
p_top_freq = np.mean(random_top_pattern_freqs >= anna_sub_top)

print(f"\n  {'Metric':<30} {'Anna':<15} {'Random Mean':<15} {'p-value':<12}")
print("  " + "-" * 72)
print(f"  {'Convergence Rate':<30} {anna_sub_conv:<15.2%} {random_convergence_rates.mean():<15.2%} {p_conv:<12.6f}")
print(f"  {'Mean Energy':<30} {anna_sub_energy:<15.2f} {random_mean_energies.mean():<15.2f} {p_energy:<12.6f}")
print(f"  {'Unique Patterns':<30} {anna_sub_patterns:<15} {random_unique_patterns_arr.mean():<15.0f} {p_patterns:<12.6f}")
print(f"  {'Top Pattern Freq':<30} {anna_sub_top:<15} {random_top_pattern_freqs.mean():<15.1f} {p_top_freq:<12.6f}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TICK-LOOP BEHAVIOR STUDY SUMMARY")
print("=" * 80)

print(f"\n  KEY FINDINGS:")
print(f"    1. Anna Matrix convergence: {anna_convergence_rate:.2%}")
print(f"    2. Unique attractors: {anna_unique_patterns} / {N_INPUTS} inputs")
print(f"    3. Strongest attractor: {anna_top_patterns[0][1]} inputs converge to same state")
print(f"    4. Most common energy: {energy_counter.most_common(1)[0]}")

any_significant = any(p < 0.001 for p in [p_conv, p_energy, p_patterns, p_top_freq])
if any_significant:
    print(f"\n  CONCLUSION: Anna Matrix tick-loop IS statistically different from random matrices")
else:
    print(f"\n  CONCLUSION: Anna Matrix tick-loop is NOT statistically different from random matrices")
    print(f"  The neural network behavior appears to be a property of ANY matrix, not specific to Anna.")

# Save results
results = {
    "date": datetime.now().isoformat(),
    "n_inputs": N_INPUTS,
    "n_random_matrices": N_RANDOM_MATRICES,
    "max_ticks": MAX_TICKS,
    "anna_matrix": {
        "convergence_rate": float(anna_convergence_rate),
        "mean_energy": float(anna_mean_energy),
        "mean_ticks": float(anna_mean_ticks),
        "unique_patterns": anna_unique_patterns,
        "top_pattern_frequency": anna_top_patterns[0][1],
        "energy_distribution": dict(energy_counter),
    },
    "random_matrices": {
        "convergence_rate_mean": float(random_convergence_rates.mean()),
        "convergence_rate_std": float(random_convergence_rates.std()),
        "mean_energy_mean": float(random_mean_energies.mean()),
        "mean_energy_std": float(random_mean_energies.std()),
        "unique_patterns_mean": float(random_unique_patterns_arr.mean()),
        "top_pattern_freq_mean": float(random_top_pattern_freqs.mean()),
    },
    "p_values": {
        "convergence": float(p_conv),
        "energy": float(p_energy),
        "unique_patterns": float(p_patterns),
        "top_pattern_freq": float(p_top_freq),
    },
    "any_significant": any_significant,
}

output_path = script_dir / "TICK_LOOP_BEHAVIOR_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n  Results saved to: {output_path}")
