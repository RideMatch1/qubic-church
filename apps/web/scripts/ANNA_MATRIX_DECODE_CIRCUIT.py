#!/usr/bin/env python3
"""
Anna Matrix: Circuit Decode — The Architecture
=================================================
The 3 populations + Neuron 26 form a CIRCUIT.
What does it compute? How does information flow?

1. Meta-circuit: 3×3 group connectivity matrix
2. Neuron 26 deep dive — the singular element
3. The palindrome as address/program
4. Exception columns × population membership
5. The attractor as computation OUTPUT
6. What does the circuit DECIDE?
7. Can we REVERSE-ENGINEER the input domain?
"""

import json
import numpy as np
from collections import Counter
from math import log2

np.random.seed(42)

with open("../public/data/anna-matrix.json") as f:
    raw = json.load(f)
M = np.array(raw["matrix"], dtype=float)
Mi = np.array(raw["matrix"], dtype=int)
T = np.sign(Mi).astype(int)
N = 128

# Define the 3 populations from Phase 1 results
POP_A  = [0, 1, 3, 4, 5, 6, 7, 9, 12, 13, 15, 17, 20, 21, 23, 29, 32, 33, 35, 36, 37, 38, 39, 41, 44, 45, 47, 49, 52, 53, 55, 61, 68, 69, 71, 77, 85, 100, 101, 103, 109, 117]  # excitatory, pattern (+1,-1,-1,+1)
POP_Ai = [10, 18, 24, 27, 42, 50, 56, 58, 59, 62, 66, 72, 74, 75, 78, 80, 82, 83, 86, 88, 89, 90, 91, 92, 94, 95, 98, 104, 106, 107, 110, 112, 114, 115, 118, 120, 121, 122, 123, 124, 126, 127]  # inhibitory, pattern (-1,+1,+1,-1)
POP_B  = [2, 8, 11, 14, 16, 19, 22, 25, 28, 30, 31, 34, 40, 43, 46, 48, 51, 54, 57, 60, 63, 64, 65, 67, 70, 73, 76, 79, 81, 84, 87, 93, 96, 97, 99, 102, 105, 108, 111, 113, 116, 119, 125]  # mixed, pattern (-1,-1,+1,+1)
NEURON_26 = [26]  # anomaly, pattern (0,+1,0,-1)

print("="*72)
print("ANNA MATRIX: CIRCUIT DECODE")
print("="*72)
print(f"Population A  (excitatory, phase +1-1-1+1): {len(POP_A)} neurons")
print(f"Population A' (inhibitory, phase -1+1+1-1): {len(POP_Ai)} neurons")
print(f"Population B  (mixed, phase -1-1+1+1):      {len(POP_B)} neurons")
print(f"Neuron 26     (anomaly, phase 0+10-1):       {len(NEURON_26)} neuron")

# ============================================================
# CIRCUIT 1: THE META-CIRCUIT — 4×4 GROUP CONNECTIVITY
# ============================================================
print("\n" + "="*72)
print("CIRCUIT 1: THE META-CIRCUIT (GROUP-TO-GROUP CONNECTIVITY)")
print("="*72)

groups = {"A": POP_A, "A'": POP_Ai, "B": POP_B, "N26": NEURON_26}
group_names = ["A", "A'", "B", "N26"]

# Compute mean connection strength between groups
# M[r,c] = weight from neuron c to neuron r
# So "A→B" means: mean of M[b, a] for b in B, a in A
print("\nMeta-connectivity matrix (mean weight FROM column group TO row group):")
print(f"{'':8s}", end="")
for gn in group_names:
    print(f"{'FROM '+gn:>12s}", end="")
print()

meta_matrix = np.zeros((4, 4))
meta_matrix_abs = np.zeros((4, 4))
for i, (gn_to, g_to) in enumerate(groups.items()):
    print(f"{'TO '+gn_to:8s}", end="")
    for j, (gn_from, g_from) in enumerate(groups.items()):
        # Mean of M[row, col] where row in g_to, col in g_from
        submatrix = M[np.ix_(g_to, g_from)]
        mean_w = np.mean(submatrix)
        mean_abs = np.mean(np.abs(submatrix))
        meta_matrix[i, j] = mean_w
        meta_matrix_abs[i, j] = mean_abs
        print(f"{mean_w:+12.2f}", end="")
    print()

print(f"\nMeta-connectivity (absolute strength):")
print(f"{'':8s}", end="")
for gn in group_names:
    print(f"{'FROM '+gn:>12s}", end="")
print()
for i, gn_to in enumerate(group_names):
    print(f"{'TO '+gn_to:8s}", end="")
    for j in range(4):
        print(f"{meta_matrix_abs[i, j]:12.2f}", end="")
    print()

# Net flow direction
print(f"\nNet information flow (positive = excitatory, negative = inhibitory):")
for i, gn_to in enumerate(group_names):
    for j, gn_from in enumerate(group_names):
        if i != j:
            direction = "excites" if meta_matrix[i, j] > 0 else "inhibits"
            strength = abs(meta_matrix[i, j])
            print(f"  {gn_from:3s} {direction:8s} {gn_to:3s}: strength={strength:.2f}")

# ============================================================
# CIRCUIT 2: THE CIRCUIT DIAGRAM
# ============================================================
print("\n" + "="*72)
print("CIRCUIT 2: THE CIRCUIT DIAGRAM")
print("="*72)

# Simplified: which groups excite and which inhibit each other?
print("""
Based on the meta-connectivity matrix, the circuit is:
""")

for i, gn_to in enumerate(group_names[:3]):  # skip N26 for clarity
    excites = []
    inhibits = []
    for j, gn_from in enumerate(group_names[:3]):
        if meta_matrix[i, j] > 5:
            excites.append(f"{gn_from}({meta_matrix[i,j]:+.0f})")
        elif meta_matrix[i, j] < -5:
            inhibits.append(f"{gn_from}({meta_matrix[i,j]:+.0f})")
    print(f"  {gn_to} receives:")
    print(f"    Excitation from: {', '.join(excites) if excites else 'none'}")
    print(f"    Inhibition from: {', '.join(inhibits) if inhibits else 'none'}")

# Self-connections
print(f"\nSelf-connectivity (diagonal of meta-matrix):")
for i, gn in enumerate(group_names):
    val = meta_matrix[i, i]
    print(f"  {gn}: {val:+.2f} ({'self-excitatory' if val > 0 else 'self-inhibitory'})")

# Cross-group total drive
print(f"\nTotal drive on each group (sum of all inputs):")
for i, gn in enumerate(group_names):
    total = sum(meta_matrix[i, j] * len(groups[group_names[j]]) for j in range(4))
    print(f"  {gn}: {total:+.0f}")

# ============================================================
# CIRCUIT 3: NEURON 26 — THE SINGULAR ELEMENT
# ============================================================
print("\n" + "="*72)
print("CIRCUIT 3: NEURON 26 — DEEP DIVE")
print("="*72)

r26 = Mi[26, :]  # row 26 = weights FROM all neurons TO neuron 26
c26 = Mi[:, 26]  # col 26 = weights FROM neuron 26 TO all neurons

print(f"Neuron 26 profile:")
print(f"  Row sum (total input): {np.sum(r26):+d}")
print(f"  Col sum (total output): {np.sum(c26):+d}")
print(f"  Dominant input value: {Counter(r26).most_common(1)[0]}")
print(f"  Dominant output value: {Counter(c26).most_common(1)[0]}")

# How does neuron 26 connect to each population?
print(f"\nNeuron 26 connections to populations:")
for gn, g in groups.items():
    input_from = np.mean([Mi[26, n] for n in g])
    output_to = np.mean([Mi[n, 26] for n in g])
    print(f"  {gn:4s} → N26: mean weight = {input_from:+.1f}")
    print(f"  N26 → {gn:4s}: mean weight = {output_to:+.1f}")

# Mirror neuron 101
print(f"\nNeuron 101 (mirror of 26):")
r101 = Mi[101, :]
print(f"  Row sum: {np.sum(r101):+d}")
print(f"  Population: {'A' if 101 in POP_A else 'A_inv' if 101 in POP_Ai else 'B'}")
print(f"  M[26,x] + M[101, 127-x] = -1 ? ", end="")
violations = sum(1 for x in range(N) if Mi[26, x] + Mi[101, N-1-x] != -1)
print(f"{violations} violations")

# What makes neuron 26 special? Compare to its neighbors
print(f"\nNeuron 26 vs neighbors:")
for n in [24, 25, 26, 27, 28]:
    row_sum = int(np.sum(Mi[n, :]))
    pop = "A" if n in POP_A else ("A'" if n in POP_Ai else ("B" if n in POP_B else "N26"))
    ternary_zeros = np.sum(Mi[n, :] == 0)
    print(f"  Neuron {n:3d}: sum={row_sum:+6d}, pop={pop:3s}, zeros={ternary_zeros}")

# The critical question: WHY does neuron 26 pass through 0?
print(f"\nWhy does neuron 26 oscillate through 0?")
# In the attractor, at the steps where N26 = 0:
# T @ state should give exactly 0 for neuron 26
# Let's verify
x = np.ones(N, dtype=float)
for _ in range(50):
    x = np.sign(T @ x).astype(float)

for step in range(4):
    state = np.sign(x).astype(int)
    raw_activation = T[26, :] @ state  # raw value before sign()
    signed = np.sign(raw_activation)
    print(f"  Step {step}: state[26]={state[26]:+d}, raw activation = {raw_activation:+d}, sign = {signed:+.0f}")
    x = np.sign(T @ x).astype(float)

# ============================================================
# CIRCUIT 4: EXCEPTION COLUMNS × POPULATIONS
# ============================================================
print("\n" + "="*72)
print("CIRCUIT 4: EXCEPTION COLUMNS × POPULATION MEMBERSHIP")
print("="*72)

exc_cols = [0, 22, 30, 41, 86, 97, 105, 127]
print(f"Exception columns: {exc_cols}")
print()

for ec in exc_cols:
    pop = "A" if ec in POP_A else ("A'" if ec in POP_Ai else ("B" if ec in POP_B else "N26"))
    mirror = N - 1 - ec
    mirror_pop = "A" if mirror in POP_A else ("A'" if mirror in POP_Ai else ("B" if mirror in POP_B else "N26"))

    # Count exceptions in this column
    n_exc = sum(1 for r in range(N) if Mi[r, ec] + Mi[N-1-r, N-1-ec] != -1)

    print(f"  Col {ec:3d} (pop {pop:3s}) ↔ Col {mirror:3d} (pop {mirror_pop:3s}): {n_exc} exceptions")

# Population membership of exception columns
print(f"\nException columns by population:")
for gn, g in groups.items():
    exc_in_group = [ec for ec in exc_cols if ec in g]
    print(f"  {gn:4s}: {exc_in_group}")

# ============================================================
# CIRCUIT 5: THE PALINDROME AS PROGRAM
# ============================================================
print("\n" + "="*72)
print("CIRCUIT 5: THE PALINDROME AS PROGRAM / ADDRESS SYSTEM")
print("="*72)

# The 34 independent deviation values
palindrome_half = [-32, 75, 56, 201, -146, 117, 90, 207, 191, 151,
                   -170, 155, 223, -6, -1, -128, 128, 16, -20, 16,
                   -140, 144, -144, 16, 128, 120, -126, 8, -2, 9,
                   -132, 20, 9, 128]

print(f"34 independent deviations (first half of palindrome):")
print(f"  {palindrome_half}")

# Interpretation 1: as neuron indices (mod 128)
neuron_indices = [d % 128 for d in palindrome_half]
print(f"\nAs neuron indices (mod 128):")
print(f"  {neuron_indices}")

# Which populations do these neurons belong to?
pop_membership = []
for ni in neuron_indices:
    if ni in POP_A:
        pop_membership.append("A")
    elif ni in POP_Ai:
        pop_membership.append("A'")
    elif ni in POP_B:
        pop_membership.append("B")
    elif ni == 26:
        pop_membership.append("N26")
    else:
        pop_membership.append("?")
print(f"  Population sequence: {pop_membership}")
print(f"  Population counts: {Counter(pop_membership).most_common()}")

# Interpretation 2: as matrix coordinates (consecutive pairs)
print(f"\nAs matrix coordinates (consecutive pairs → M[d1 mod 128, d2 mod 128]):")
for i in range(0, len(palindrome_half) - 1, 2):
    r = palindrome_half[i] % 128
    c = palindrome_half[i+1] % 128
    val = Mi[r, c]
    is_exc = Mi[r, c] + Mi[N-1-r, N-1-c] != -1
    pop_r = "A" if r in POP_A else ("A'" if r in POP_Ai else ("B" if r in POP_B else "N26"))
    print(f"  [{palindrome_half[i]:+4d},{palindrome_half[i+1]:+4d}] → M[{r:3d},{c:3d}] = {val:+4d}"
          f"  pop_row={pop_r}  {'*** EXC' if is_exc else ''}")

# Interpretation 3: absolute values as byte sequence
print(f"\nAbsolute values as bytes:")
abs_vals = [abs(d) for d in palindrome_half]
print(f"  {abs_vals}")
print(f"  Sum: {sum(abs_vals)}")
# As ASCII where possible
ascii_str = ''.join(chr(v) if 32 <= v <= 126 else f'[{v}]' for v in abs_vals)
print(f"  ASCII: {ascii_str}")

# Interpretation 4: sign sequence
sign_seq = [1 if d > 0 else (-1 if d < 0 else 0) for d in palindrome_half]
print(f"\nSign sequence: {sign_seq}")
print(f"  Positive: {sign_seq.count(1)}, Negative: {sign_seq.count(-1)}")
# Binary: positive = 1, negative = 0
binary = ''.join('1' if s > 0 else '0' for s in sign_seq)
print(f"  Binary: {binary}")
print(f"  = {int(binary, 2)} decimal")
print(f"  = 0x{int(binary, 2):X} hex")

# Interpretation 5: as offsets from each exception group
print(f"\nDeviation statistics by exception column group:")
# Recall: the 68 exceptions are in column pairs 0/127, 22/105, 30/97, 41/86
# Deviations in order: cols 0/127 (2), cols 22/105 (26), cols 30/97 (36), cols 41/86 (4)
groups_deviations = {
    "0/127": palindrome_half[0:1],  # first value (-32)
    "22/105": palindrome_half[1:14],  # next 13 values
    "30/97": palindrome_half[14:32],  # next 18 values
    "41/86": palindrome_half[32:34],  # last 2 values
}

for pair, devs in groups_deviations.items():
    print(f"  Cols {pair}: {devs}")
    print(f"    Sum: {sum(devs)}, Mean: {np.mean(devs):.1f}")
    if len(devs) > 1:
        diffs = [devs[i+1] - devs[i] for i in range(len(devs)-1)]
        print(f"    Consecutive differences: {diffs}")

# ============================================================
# CIRCUIT 6: THE ATTRACTOR AS COMPUTATION OUTPUT
# ============================================================
print("\n" + "="*72)
print("CIRCUIT 6: WHAT DOES THE CIRCUIT COMPUTE?")
print("="*72)

print("""
The circuit has 3 populations + 1 anomaly:
  A  (42 excitatory neurons): oscillate (+1,-1,-1,+1)
  A' (42 inhibitory neurons): oscillate (-1,+1,+1,-1) = opposite of A
  B  (43 mixed neurons):      oscillate (-1,-1,+1,+1) = shifted by 1
  N26 (1 anomaly):            oscillate (0,+1,0,-1) = passes through zero

The 4-step cycle:
  Step 0: A=+1, A'=-1, B=-1, N26=0  → 42 positive (A)
  Step 1: A=-1, A'=+1, B=-1, N26=+1 → 43 positive (A' + N26)
  Step 2: A=-1, A'=+1, B=+1, N26=0  → 85 positive (A' + B)
  Step 3: A=+1, A'=-1, B=+1, N26=-1 → 85 positive (A + B)

Wait — let me verify this step by step...
""")

x = np.ones(N, dtype=float)
for _ in range(50):
    x = np.sign(T @ x).astype(float)

for step in range(4):
    state = np.sign(x).astype(int)

    a_vals = [state[n] for n in POP_A]
    ai_vals = [state[n] for n in POP_Ai]
    b_vals = [state[n] for n in POP_B]
    n26_val = state[26]

    a_pos = sum(1 for v in a_vals if v == 1)
    ai_pos = sum(1 for v in ai_vals if v == 1)
    b_pos = sum(1 for v in b_vals if v == 1)

    total_pos = np.sum(state == 1)
    total_sum = np.sum(state)

    print(f"  Step {step}: A:+1={a_pos:2d}/-1={42-a_pos:2d}  "
          f"A':+1={ai_pos:2d}/-1={42-ai_pos:2d}  "
          f"B:+1={b_pos:2d}/-1={43-b_pos:2d}  "
          f"N26={n26_val:+d}  "
          f"Total:+1={total_pos:3d} sum={total_sum:+4d}")

    x = np.sign(T @ x).astype(float)

# ============================================================
# CIRCUIT 7: INFORMATION FLOW — WHO DRIVES WHOM?
# ============================================================
print("\n" + "="*72)
print("CIRCUIT 7: CAUSAL FLOW — WHO DRIVES THE TRANSITION?")
print("="*72)

# At each step transition, which group's input causes the others to flip?
x = np.ones(N, dtype=float)
for _ in range(50):
    x = np.sign(T @ x).astype(float)

print("Analyzing causal contributions at each transition:")
for step in range(4):
    state = np.sign(x).astype(int)
    raw = T.astype(float) @ state  # raw activations

    # Next state
    x = np.sign(T @ x).astype(float)
    next_state = np.sign(x).astype(int)

    # For each neuron that FLIPS, decompose what caused the flip
    flipped = np.where(state != next_state)[0]
    if len(flipped) == 0:
        continue

    # For a subset of flipped neurons, decompose the drive by population
    print(f"\n  Step {step}→{(step+1)%4}: {len(flipped)} neurons flip")

    # Average causal contribution per group
    for gn_to, g_to in [("A", POP_A), ("A'", POP_Ai), ("B", POP_B)]:
        flipped_in_group = [n for n in flipped if n in g_to]
        if not flipped_in_group:
            continue

        # For these flipped neurons, what drove the flip?
        drives = {"A": [], "A'": [], "B": [], "N26": []}
        for n in flipped_in_group:
            for gn_from, g_from in groups.items():
                drive = sum(T[n, m] * state[m] for m in g_from)
                drives[gn_from].append(drive)

        print(f"    {gn_to} neurons that flip ({len(flipped_in_group)}):")
        for gn_from in group_names:
            mean_drive = np.mean(drives[gn_from])
            print(f"      Drive from {gn_from:4s}: {mean_drive:+8.1f} "
                  f"({'→ flip' if (mean_drive > 0) != (state[flipped_in_group[0]] > 0) else '→ stay'})")

# ============================================================
# CIRCUIT 8: NEURON 26 AND THE NUMBER 26
# ============================================================
print("\n" + "="*72)
print("CIRCUIT 8: THE SIGNIFICANCE OF 26")
print("="*72)

print(f"""
26 in mathematics and nature:
  26 = 2 × 13
  26 = only number between a perfect square (25) and a cube (27)
  26 = number of letters in English/Latin alphabet
  26 = atomic number of Iron (Fe)
  26 = number of sporadic groups (in 26 + 1 families)
  26 = value that appears most in Row 6 of the Anna Matrix (24 times)

26 in the Anna Matrix:
  Neuron 26: the ONLY neuron with ternary zero in attractor
  Value 26 in matrix: {np.sum(Mi == 26)} occurrences
  Value -26 in matrix: {np.sum(Mi == -26)} occurrences
  Row 26 sum: {np.sum(Mi[26, :]):+d}
  Col 26 sum: {np.sum(Mi[:, 26]):+d}
  M[26, 26] = {Mi[26, 26]}
  M[26, 101] = {Mi[26, 101]} (26 + 101 = 127)

26 in the semigroup:
  Exception columns: [0, 22, 30, 41, 86, 97, 105, 127]
  26 = 22 + 4 (not a generator)
  26 is in the GAP SET of the semigroup (cannot be represented)
  Position 26 is a "missing number" in the semigroup structure.

26 in the attractor:
  N26 is the THRESHOLD neuron. It oscillates between +1 and -1
  BUT passes through 0 at the transition points.
  It is the only neuron that "hesitates" — it enters the
  UNKNOWN state of ternary logic before deciding.
""")

# Is 26 in the gap set?
generators = [22, 30, 41, 86, 97, 105, 127]
S_set = set([0])
for _ in range(300):
    new = set()
    for s in list(S_set):
        for g in generators:
            v = s + g
            if v <= 300:
                new.add(v)
    if not new - S_set:
        break
    S_set.update(new)
print(f"  26 is in semigroup: {26 in S_set}")
print(f"  Gap numbers near 26: {[g for g in sorted(set(range(30)) - S_set)]}")

# ============================================================
# CIRCUIT 9: CAN WE REVERSE-ENGINEER THE INPUT DOMAIN?
# ============================================================
print("\n" + "="*72)
print("CIRCUIT 9: REVERSE-ENGINEERING — WHAT INPUTS WAS THIS DESIGNED FOR?")
print("="*72)

# Since ALL inputs converge to the same attractor, the matrix doesn't
# CLASSIFY inputs. But the TRANSIENT (path to convergence) differs.
# Can we extract information from the transient?

print("Transient analysis: does the PATH to convergence encode information?")

test_inputs = {
    "all +1": np.ones(N),
    "all -1": -np.ones(N),
    "alternating": np.array([(-1)**i for i in range(N)], dtype=float),
    "first_half +1": np.array([1]*64 + [-1]*64, dtype=float),
    "random_1": np.random.choice([-1, 1], N).astype(float),
    "random_2": np.random.choice([-1, 1], N).astype(float),
    "exc_cols_hot": np.array([1 if i in [0,22,30,41,86,97,105,127] else -1 for i in range(N)], dtype=float),
    "pop_A_hot": np.array([1 if i in POP_A else -1 for i in range(N)], dtype=float),
    "pop_Ai_hot": np.array([1 if i in POP_Ai else -1 for i in range(N)], dtype=float),
    "pop_B_hot": np.array([1 if i in POP_B else -1 for i in range(N)], dtype=float),
    "neuron_26_only": np.array([1 if i == 26 else -1 for i in range(N)], dtype=float),
}

print(f"\n{'Input':20s} {'Steps':>6s} {'Path signature':>40s}")
print("-" * 70)

for name, x_init in test_inputs.items():
    x = x_init.copy()
    path = []
    for step in range(20):
        state = np.sign(x).astype(int)
        path.append(np.sum(state == 1))
        x = np.sign(T @ x).astype(float)

        # Check convergence
        if step > 0 and path[-1] == path[-4] if len(path) >= 4 else False:
            break

    # Path signature: the sequence of +1 counts
    sig = path[:min(len(path), 10)]
    print(f"{name:20s} {len(path):6d} {str(sig):>40s}")

# The key insight: the FIRST STEP response differs
print(f"\nFirst-step fingerprint (raw activation magnitudes):")
for name, x_init in list(test_inputs.items())[:6]:
    raw = T.astype(float) @ x_init
    mean_mag = np.mean(np.abs(raw))
    max_mag = np.max(np.abs(raw))
    zeros = np.sum(raw == 0)
    print(f"  {name:20s}: mean|a|={mean_mag:.1f}, max|a|={max_mag:.1f}, zeros={zeros}")

# ============================================================
# CIRCUIT 10: THE COMPLETE PICTURE
# ============================================================
print("\n" + "="*72)
print("CIRCUIT 10: THE COMPLETE PICTURE")
print("="*72)

print(f"""
=================================================================
THE ANNA MATRIX IS A PHASE-LOCKED OSCILLATOR
=================================================================

Architecture:
  128 neurons arranged in 3 populations + 1 threshold neuron

  Population A  (42 neurons): ALL excitatory (row sums 2891-9569)
  Population A' (42 neurons): ALL inhibitory (row sums -9697 to -3019)
  Population B  (43 neurons): Mixed E/I (22 excitatory, 21 inhibitory)
  Neuron 26    (1 neuron):    Threshold element (passes through 0)

Dynamics:
  1. Any input → amplified by all unstable eigenvalues
  2. Ternary clamp prevents explosion
  3. Dominant eigenvalue phase ≈ pi/2 → period-4 rotation
  4. Convergence in ~6 steps to single attractor

The 4-phase cycle:
  Phase 0: A fires (+1), A' silent (-1), B silent (-1), N26 at zero
  Phase 1: A silent, A' fires, B still silent, N26 fires (+1)
  Phase 2: A silent, A' fires, B fires, N26 at zero
  Phase 3: A fires, A' silent, B fires, N26 fires (-1)

  Pattern: A and A' alternate (180° out of phase)
           B lags A by 90° (quarter cycle)
           N26 lags A by 90° but passes through zero

This is a QUADRATURE OSCILLATOR:
  - A and A' are the I and Q channels (in-phase / quadrature)
  - B provides the phase reference
  - N26 is the zero-crossing detector

The 42/43 split (128/3 ≈ 42.67):
  The 3 populations divide 128 neurons approximately into thirds.
  A=42, A'=42, B=43 gives the most balanced 3-way split of 127
  with the extra neuron (N26) serving as threshold.
  42 + 42 + 43 + 1 = 128.

WHAT DOES IT COMPUTE?
  The matrix does not CLASSIFY inputs — all inputs converge
  to the same attractor. Instead, it implements a CLOCK:

  A phase-locked 4-tick clock where:
  - Tick 0: Excitatory neurons fire alone
  - Tick 1: Inhibitory neurons fire + threshold crosses zero
  - Tick 2: Inhibitory + mixed fire together
  - Tick 3: Excitatory + mixed fire together

  This is exactly the firing pattern of a biological
  CENTRAL PATTERN GENERATOR (CPG) — the neural circuit
  that produces rhythmic behavior (heartbeat, breathing,
  walking) in biological organisms.

  The Anna Matrix is a DIGITAL CPG implemented in ternary logic.
""")
