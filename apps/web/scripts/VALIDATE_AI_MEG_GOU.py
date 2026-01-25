#!/usr/bin/env python3
"""
===============================================================================
            🔬 VALIDATE AI.MEG.GOU PATTERN 🔬
===============================================================================
Is the "AI.MEG.GOU" pattern in Col30⊕Col97 statistically significant?

Monte Carlo approach:
1. Generate 10,000 random column pairs
2. XOR them together
3. Check how often "AI", "MEG", "GOU" appear
4. Calculate p-value
"""

import json
import numpy as np
import random
import re
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent

print("=" * 80)
print("           🔬 VALIDATE AI.MEG.GOU PATTERN 🔬")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# OBSERVED PATTERN
# ==============================================================================
print("\n" + "=" * 80)
print("OBSERVED PATTERN IN COL30⊕COL97")
print("=" * 80)

col_30 = [int(matrix[r, 30]) for r in range(128)]
col_97 = [int(matrix[r, 97]) for r in range(128)]
xor_30_97 = [col_30[r] ^ col_97[r] for r in range(128)]

observed_string = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_30_97)
observed_upper = observed_string.upper()

print(f"\n  XOR String: {observed_string}")

# Check for patterns
patterns_to_check = ["AI", "MEG", "GOU", "AIMEG", "AI.MEG", "AI MEG"]
observed_patterns = {}

for pattern in patterns_to_check:
    count = observed_upper.count(pattern.upper())
    pos = observed_upper.find(pattern.upper())
    observed_patterns[pattern] = {"count": count, "position": pos}
    print(f"  '{pattern}': Found {count} times, first at position {pos}")

# ==============================================================================
# MONTE CARLO SIMULATION
# ==============================================================================
print("\n" + "=" * 80)
print("MONTE CARLO SIMULATION")
print("=" * 80)

n_simulations = 10000

# Method 1: XOR of random column pairs from the SAME matrix
print("\n  Method 1: Random column pairs from same matrix")

hits_ai = 0
hits_meg = 0
hits_gou = 0
hits_all_three = 0

for i in range(n_simulations):
    # Pick two random columns
    c1 = random.randint(0, 127)
    c2 = random.randint(0, 127)

    col1 = [int(matrix[r, c1]) for r in range(128)]
    col2 = [int(matrix[r, c2]) for r in range(128)]
    xor_cols = [col1[r] ^ col2[r] for r in range(128)]

    xor_str = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_cols).upper()

    has_ai = "AI" in xor_str
    has_meg = "MEG" in xor_str
    has_gou = "GOU" in xor_str

    if has_ai:
        hits_ai += 1
    if has_meg:
        hits_meg += 1
    if has_gou:
        hits_gou += 1
    if has_ai and has_meg and has_gou:
        hits_all_three += 1

print(f"\n  Results ({n_simulations} random column pairs):")
print(f"    'AI' appears: {hits_ai} times ({hits_ai/n_simulations*100:.2f}%)")
print(f"    'MEG' appears: {hits_meg} times ({hits_meg/n_simulations*100:.2f}%)")
print(f"    'GOU' appears: {hits_gou} times ({hits_gou/n_simulations*100:.2f}%)")
print(f"    ALL THREE appear: {hits_all_three} times ({hits_all_three/n_simulations*100:.2f}%)")

p_value_all_three = hits_all_three / n_simulations

# Method 2: XOR of completely random byte arrays
print("\n  Method 2: Random 128-byte arrays")

hits_ai_random = 0
hits_meg_random = 0
hits_gou_random = 0
hits_all_three_random = 0

for i in range(n_simulations):
    random_xor = [random.randint(-128, 127) for _ in range(128)]
    xor_str = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in random_xor).upper()

    has_ai = "AI" in xor_str
    has_meg = "MEG" in xor_str
    has_gou = "GOU" in xor_str

    if has_ai:
        hits_ai_random += 1
    if has_meg:
        hits_meg_random += 1
    if has_gou:
        hits_gou_random += 1
    if has_ai and has_meg and has_gou:
        hits_all_three_random += 1

print(f"\n  Results ({n_simulations} random byte arrays):")
print(f"    'AI' appears: {hits_ai_random} times ({hits_ai_random/n_simulations*100:.2f}%)")
print(f"    'MEG' appears: {hits_meg_random} times ({hits_meg_random/n_simulations*100:.2f}%)")
print(f"    'GOU' appears: {hits_gou_random} times ({hits_gou_random/n_simulations*100:.2f}%)")
print(f"    ALL THREE appear: {hits_all_three_random} times ({hits_all_three_random/n_simulations*100:.2f}%)")

p_value_random = hits_all_three_random / n_simulations

# ==============================================================================
# SPECIFIC PATTERN TEST
# ==============================================================================
print("\n" + "=" * 80)
print("SPECIFIC PATTERN: 'AI.MEG' within 5 positions")
print("=" * 80)

# In our observed string, "AI" is at position 55, "MEG" is at 58
# That's only 3 positions apart!

def find_ai_meg_close(s, max_gap=5):
    """Check if AI and MEG appear within max_gap positions."""
    ai_pos = s.upper().find("AI")
    meg_pos = s.upper().find("MEG")

    if ai_pos >= 0 and meg_pos >= 0:
        gap = abs(meg_pos - ai_pos - 2)  # -2 because "AI" is 2 chars
        return gap <= max_gap
    return False

# Check observed
observed_has_close_ai_meg = find_ai_meg_close(observed_string)
print(f"\n  Observed has AI and MEG within 5 positions: {observed_has_close_ai_meg}")

# Monte Carlo for close AI.MEG
close_hits = 0
for i in range(n_simulations):
    c1 = random.randint(0, 127)
    c2 = random.randint(0, 127)

    col1 = [int(matrix[r, c1]) for r in range(128)]
    col2 = [int(matrix[r, c2]) for r in range(128)]
    xor_cols = [col1[r] ^ col2[r] for r in range(128)]

    xor_str = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_cols)

    if find_ai_meg_close(xor_str):
        close_hits += 1

print(f"  Random column pairs with close AI.MEG: {close_hits} ({close_hits/n_simulations*100:.2f}%)")
p_value_close = close_hits / n_simulations

# ==============================================================================
# STATISTICAL VERDICT
# ==============================================================================
print("\n" + "=" * 80)
print("🔬 STATISTICAL VERDICT 🔬")
print("=" * 80)

significance_threshold = 0.001

is_significant_all = p_value_all_three < significance_threshold
is_significant_close = p_value_close < significance_threshold

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PATTERN VALIDATION RESULTS                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  OBSERVED in Col30⊕Col97:                                                    ║
║  • "AI" at position 55                                                       ║
║  • "MEG" at position 58 (3 chars after AI)                                   ║
║  • "GOU" at position 66                                                      ║
║                                                                               ║
║  MONTE CARLO RESULTS (n={n_simulations}):                                          ║
║                                                                               ║
║  Test 1: All three patterns (AI + MEG + GOU) in same XOR                     ║
║    • Random column pairs: {p_value_all_three*100:.2f}%                                         ║
║    • p-value: {p_value_all_three:.4f}                                                        ║
║    • Significant (p<0.001): {'YES ✓' if is_significant_all else 'NO ✗':44}║
║                                                                               ║
║  Test 2: AI and MEG within 5 positions                                       ║
║    • Random column pairs: {p_value_close*100:.2f}%                                          ║
║    • p-value: {p_value_close:.4f}                                                        ║
║    • Significant (p<0.001): {'YES ✓' if is_significant_close else 'NO ✗':44}║
║                                                                               ║
║  CONCLUSION:                                                                  ║
""")

if is_significant_all or is_significant_close:
    print("""║  The "AI.MEG" pattern is STATISTICALLY SIGNIFICANT!                        ║
║  This is unlikely to be random chance.                                      ║""")
else:
    print("""║  The pattern is NOT statistically significant.                              ║
║  It could easily occur by chance in random column XORs.                     ║
║  This is likely PAREIDOLIA.                                                 ║""")

print("""║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "observed_string": observed_string,
    "patterns_found": observed_patterns,
    "monte_carlo": {
        "n_simulations": n_simulations,
        "all_three_patterns": {
            "random_column_pairs": p_value_all_three,
            "random_bytes": p_value_random,
        },
        "close_ai_meg": p_value_close,
    },
    "is_significant_all_three": is_significant_all,
    "is_significant_close": is_significant_close,
    "conclusion": "SIGNIFICANT" if (is_significant_all or is_significant_close) else "NOT SIGNIFICANT - LIKELY PAREIDOLIA",
}

output_path = script_dir / "AI_MEG_GOU_VALIDATION.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"✓ Results saved: {output_path}")
