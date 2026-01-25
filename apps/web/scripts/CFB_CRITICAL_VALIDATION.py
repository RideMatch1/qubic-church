#!/usr/bin/env python3
"""
CRITICAL VALIDATION - No Bullshit, Just Math
"""

SEQ = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

print("="*70)
print("CRITICAL VALIDATION - ANTI-BULLSHIT CHECK")
print("="*70)

# CLAIM 1: First pair sums to 137
print("\n[CLAIM 1] First pair (45, 92) sums to 137")
result = SEQ[0] + SEQ[1]
print(f"  Calculation: {SEQ[0]} + {SEQ[1]} = {result}")
print(f"  VERDICT: {'✓ TRUE' if result == 137 else '✗ FALSE'}")

# CLAIM 2: Last pair sums to 121
print("\n[CLAIM 2] Last pair (82, 39) sums to 121")
result = SEQ[-2] + SEQ[-1]
print(f"  Calculation: {SEQ[-2]} + {SEQ[-1]} = {result}")
print(f"  VERDICT: {'✓ TRUE' if result == 121 else '✗ FALSE'}")

# CLAIM 3: Pair 9 sums to 121
print("\n[CLAIM 3] Pair 9 (84, 37) sums to 121")
pair9 = (SEQ[16], SEQ[17])  # 0-indexed: positions 17,18 = indices 16,17
print(f"  Pair 9 (indices 16,17): ({SEQ[16]}, {SEQ[17]})")
result = SEQ[16] + SEQ[17]
print(f"  Calculation: {SEQ[16]} + {SEQ[17]} = {result}")
print(f"  VERDICT: {'✓ TRUE' if result == 121 else '✗ FALSE'}")

# CLAIM 4: First 3 + Last 3 = 288
print("\n[CLAIM 4] First 3 + Last 3 = 288")
first3 = SEQ[:3]
last3 = SEQ[-3:]
sum_first3 = sum(first3)
sum_last3 = sum(last3)
total = sum_first3 + sum_last3
print(f"  First 3: {first3} = {sum_first3}")
print(f"  Last 3: {last3} = {sum_last3}")
print(f"  Total: {sum_first3} + {sum_last3} = {total}")
print(f"  VERDICT: {'✓ TRUE' if total == 288 else '✗ FALSE'}")

# CLAIM 5: XOR of all = 1
print("\n[CLAIM 5] XOR of all 40 numbers = 1")
xor_all = 0
for n in SEQ:
    xor_all ^= n
print(f"  Step by step XOR:")
running = 0
for i, n in enumerate(SEQ):
    running ^= n
    if i < 5 or i >= 35:
        print(f"    {i+1:2d}: {n:2d} -> cumulative XOR = {running}")
    elif i == 5:
        print(f"    ...")
print(f"  Final XOR: {xor_all}")
print(f"  VERDICT: {'✓ TRUE' if xor_all == 1 else '✗ FALSE'}")

# CLAIM 6: XOR first 20 = 56, second 20 = 57
print("\n[CLAIM 6] XOR of first 20 = 56, XOR of second 20 = 57")
first20 = SEQ[:20]
second20 = SEQ[20:]
print(f"  First 20: {first20}")
print(f"  Second 20: {second20}")

xor_first = 0
for n in first20:
    xor_first ^= n

xor_second = 0
for n in second20:
    xor_second ^= n

print(f"  XOR of first 20: {xor_first}")
print(f"  XOR of second 20: {xor_second}")
print(f"  {xor_first} XOR {xor_second} = {xor_first ^ xor_second}")
print(f"  VERDICT first=56: {'✓ TRUE' if xor_first == 56 else '✗ FALSE'}")
print(f"  VERDICT second=57: {'✓ TRUE' if xor_second == 57 else '✗ FALSE'}")
print(f"  VERDICT 56^57=1: {'✓ TRUE' if xor_first ^ xor_second == 1 else '✗ FALSE'}")

# CLAIM 7: Frame XOR = 28, Middle XOR = 29
print("\n[CLAIM 7] Frame XOR = 28, Middle XOR = 29")
frame = SEQ[:3] + SEQ[-3:]
middle = SEQ[3:37]
print(f"  Frame (first 3 + last 3): {frame}")
print(f"  Middle (positions 4-37, indices 3-36): {len(middle)} numbers")

xor_frame = 0
for n in frame:
    xor_frame ^= n

xor_middle = 0
for n in middle:
    xor_middle ^= n

print(f"  XOR of frame: {xor_frame}")
print(f"  XOR of middle: {xor_middle}")
print(f"  {xor_frame} XOR {xor_middle} = {xor_frame ^ xor_middle}")
print(f"  VERDICT frame=28: {'✓ TRUE' if xor_frame == 28 else '✗ FALSE'}")
print(f"  VERDICT middle=29: {'✓ TRUE' if xor_middle == 29 else '✗ FALSE'}")

# CLAIM 8: 6*121 + 7*137 = 1685 = sum of middle
print("\n[CLAIM 8] 6×121 + 7×137 = 1685 = sum of middle (positions 4-37)")
middle_sum = sum(middle)
formula = 6*121 + 7*137
print(f"  Sum of middle: {middle_sum}")
print(f"  6×121 + 7×137 = {6*121} + {7*137} = {formula}")
print(f"  VERDICT: {'✓ TRUE' if middle_sum == formula else '✗ FALSE'}")

# CRITICAL CHECK: Is 6 and 7 cherry-picked?
print("\n[CRITICAL CHECK] Is 6×121 + 7×137 = 1685 cherry-picked?")
print("  Searching ALL solutions for a×121 + b×137 = 1685 where a,b are integers 0-20:")
solutions = []
for a in range(0, 21):
    for b in range(0, 21):
        if a*121 + b*137 == 1685:
            solutions.append((a, b))
print(f"  Solutions found: {solutions}")
if len(solutions) == 1:
    print("  VERDICT: Only ONE solution exists → NOT arbitrary cherry-picking")
else:
    print(f"  VERDICT: {len(solutions)} solutions exist → COULD be cherry-picking")

# PROBABILITY CHECK: XOR = 1
print("\n[PROBABILITY CHECK] How likely is XOR of 40 random numbers = 1?")
import random
trials = 100000
count = 0
for _ in range(trials):
    test_seq = [random.randint(3, 98) for _ in range(40)]
    test_xor = 0
    for n in test_seq:
        test_xor ^= n
    if test_xor == 1:
        count += 1
prob = count / trials
print(f"  {trials} random trials, {count} had XOR=1")
print(f"  Probability: {prob:.4f} (~1 in {int(1/prob) if prob > 0 else 'inf'})")

# PROBABILITY CHECK: XOR = consecutive numbers
print("\n[PROBABILITY CHECK] How likely is first/second half XOR being consecutive?")
count_consecutive = 0
for _ in range(trials):
    test_seq = [random.randint(3, 98) for _ in range(40)]
    xor1 = 0
    for n in test_seq[:20]:
        xor1 ^= n
    xor2 = 0
    for n in test_seq[20:]:
        xor2 ^= n
    if abs(xor1 - xor2) == 1:
        count_consecutive += 1
prob_cons = count_consecutive / trials
print(f"  {trials} random trials, {count_consecutive} had consecutive XORs")
print(f"  Probability: {prob_cons:.4f} (~1 in {int(1/prob_cons) if prob_cons > 0 else 'inf'})")

# CRITICAL: What about the sums 137 and 121?
print("\n[PROBABILITY CHECK] First pair = 137 AND last pair = 121?")
count_both = 0
for _ in range(trials):
    test_seq = [random.randint(3, 98) for _ in range(40)]
    if test_seq[0] + test_seq[1] == 137 and test_seq[-2] + test_seq[-1] == 121:
        count_both += 1
prob_both = count_both / trials
print(f"  {trials} random trials, {count_both} had both conditions")
if count_both > 0:
    print(f"  Probability: {prob_both:.6f} (~1 in {int(1/prob_both)})")
else:
    print(f"  Probability: <{1/trials:.6f} (0 hits in {trials} trials)")

# FINAL SUMMARY
print("\n" + "="*70)
print("FINAL VALIDATION SUMMARY")
print("="*70)
print("""
VERIFIED FACTS (mathematically certain):
  ✓ First pair = 137
  ✓ Last pair = 121
  ✓ Pair 9 = 121
  ✓ First 3 + Last 3 = 288
  ✓ XOR of all = 1
  ✓ XOR first 20 = 56
  ✓ XOR second 20 = 57
  ✓ 56 and 57 are consecutive, XOR to 1

QUESTIONABLE CLAIMS:
  ? Frame XOR = 28, Middle XOR = 29
    → Need to verify the split is meaningful, not arbitrary
  ? 6×121 + 7×137 = 1685
    → Formula is TRUE, but why 6 and 7? Only one solution, but still...

STATISTICAL SIGNIFICANCE:
  - XOR = 1: ~1% chance (weak alone)
  - First=137 AND Last=121: very rare
  - Consecutive XOR halves: ~1-2% chance (weak alone)
  - ALL together: much more significant
""")

# The real question
print("\n" + "="*70)
print("THE REAL QUESTION")
print("="*70)
print("""
Is the COMBINATION of all these properties unlikely by chance?

Individual probabilities:
- P(first pair = 137) ≈ 1/95 (sums from 6 to 196)
- P(last pair = 121) ≈ 1/95
- P(XOR all = 1) ≈ 1/128 (values 0-127)
- P(XOR halves consecutive) ≈ 1/64

If independent: P(all) ≈ 1/(95 × 95 × 128 × 64) ≈ 1/73,000,000

But are they independent? That's the key question.
""")
