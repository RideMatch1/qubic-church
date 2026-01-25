#!/usr/bin/env python3
"""
===============================================================================
   KRITISCHE VALIDIERUNG DER PATOSHI-BRIDGE HYPOTHESE
===============================================================================
Wissenschaftliche Rigorosität: Wir müssen ALLE alternativen Erklärungen prüfen
bevor wir irgendwelche Schlussfolgerungen ziehen!

HYPOTHESEN ZU TESTEN:
H0 (Null): Die Übereinstimmung ist ZUFALL
H1 (Alt):  Die Übereinstimmung ist ABSICHTLICH kodiert

TESTS:
1. Monte-Carlo Simulation mit 10000+ zufälligen Koordinaten
2. Sensitivitätsanalyse: Verschiedene Interpretationen
3. Multiple Testing Korrektur (Bonferroni)
4. Effektstärke berechnen
5. Alternative Erklärungen prüfen
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
import random
import math

random.seed(42)  # Reproduzierbarkeit
np.random.seed(42)

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   KRITISCHE WISSENSCHAFTLICHE VALIDIERUNG
   ========================================
""")
print("=" * 80)

# Load Patoshi data
patoshi_path = script_dir.parent / "public" / "data" / "patoshi-addresses.json"
with open(patoshi_path) as f:
    patoshi_data = json.load(f)

patoshi_blocks = set(r['blockHeight'] for r in patoshi_data['records'])
min_block = min(patoshi_blocks)
max_block = max(patoshi_blocks)
total_blocks_in_range = max_block - min_block + 1
patoshi_ratio = len(patoshi_blocks) / total_blocks_in_range

print(f"\n📊 PATOSHI DATASET STATISTIKEN:")
print(f"   Patoshi Blocks: {len(patoshi_blocks)}")
print(f"   Block Range: {min_block} - {max_block}")
print(f"   Total Blocks in Range: {total_blocks_in_range}")
print(f"   Patoshi Ratio: {patoshi_ratio:.4f} ({patoshi_ratio*100:.2f}%)")

# Actual bridge cells
bridge_cells = [
    (17, 76), (20, 78), (20, 120), (21, 15),
    (42, 63), (51, 51), (57, 124), (81, 108),
]

# ==============================================================================
# TEST 1: KOMBINIERTE BLOCK-NUMMERN (row || col)
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 1: KOMBINIERTE BLOCK-NUMMERN (row*100+col oder row||col)")
print("=" * 80)

def coords_to_combined_block(r, c):
    """Konvertiert (r,c) zu kombinierter Blocknummer"""
    if c < 100:
        return r * 100 + c
    else:
        return int(f"{r}{c}")

actual_combined = [coords_to_combined_block(r, c) for r, c in bridge_cells]
print(f"\n   Aktuelle Bridge-Blocks: {actual_combined}")

# Count how many are Patoshi AND in range
in_range = [b for b in actual_combined if min_block <= b <= max_block]
patoshi_matches = [b for b in in_range if b in patoshi_blocks]

print(f"   In Patoshi Range: {len(in_range)}/{len(actual_combined)}")
print(f"   Davon Patoshi: {len(patoshi_matches)}/{len(in_range)}")
print(f"   Patoshi Blocks: {patoshi_matches}")

# ==============================================================================
# TEST 2: MONTE-CARLO SIMULATION
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 2: MONTE-CARLO SIMULATION (10000 Durchläufe)")
print("=" * 80)

N_SIMULATIONS = 10000
matches_distribution = []

for _ in range(N_SIMULATIONS):
    # Generate 8 random coordinates in 128x128 matrix
    random_cells = [(random.randint(0, 127), random.randint(0, 127)) for _ in range(8)]
    random_blocks = [coords_to_combined_block(r, c) for r, c in random_cells]

    # Count Patoshi matches
    random_in_range = [b for b in random_blocks if min_block <= b <= max_block]
    random_patoshi = sum(1 for b in random_in_range if b in patoshi_blocks)
    matches_distribution.append((len(random_in_range), random_patoshi))

# Analyze results
print(f"\n   Simulationen: {N_SIMULATIONS}")

# For cells where we had 6 in range:
similar_cases = [m for ir, m in matches_distribution if ir == len(in_range)]
p_value = None
if similar_cases:
    avg_matches = np.mean(similar_cases)
    std_matches = np.std(similar_cases)

    # How often do we get >= our actual matches?
    at_least_as_good = sum(1 for m in similar_cases if m >= len(patoshi_matches))
    p_value = at_least_as_good / len(similar_cases)

    print(f"\n   Bei {len(in_range)} Blocks in Range:")
    print(f"   Erwartete Patoshi-Matches: {avg_matches:.2f} ± {std_matches:.2f}")
    print(f"   Tatsächliche Matches: {len(patoshi_matches)}")
    print(f"   Fälle mit >={len(patoshi_matches)} Matches: {at_least_as_good}/{len(similar_cases)}")
    print(f"   p-Wert: {p_value:.6f}")

    if p_value < 0.05:
        print(f"   ✅ SIGNIFIKANT bei α=0.05")
    else:
        print(f"   ❌ NICHT signifikant bei α=0.05")

# ==============================================================================
# TEST 3: VERSCHIEDENE INTERPRETATIONEN
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 3: SENSITIVITÄTSANALYSE - VERSCHIEDENE INTERPRETATIONEN")
print("=" * 80)

interpretations = {
    "Combined (r||c)": lambda r, c: coords_to_combined_block(r, c),
    "Sum (r+c)": lambda r, c: r + c,
    "Product (r*c)": lambda r, c: r * c,
    "XOR (r^c)": lambda r, c: r ^ c,
    "Diff |r-c|": lambda r, c: abs(r - c),
    "r*128+c": lambda r, c: r * 128 + c,
    "Row only": lambda r, c: r,
    "Col only": lambda r, c: c,
}

results = {}

for name, func in interpretations.items():
    blocks = [func(r, c) for r, c in bridge_cells]
    ir = [b for b in blocks if min_block <= b <= max_block]
    patoshi = sum(1 for b in ir if b in patoshi_blocks)

    # Monte Carlo for this interpretation
    mc_matches = []
    for _ in range(1000):
        rand_cells = [(random.randint(0, 127), random.randint(0, 127)) for _ in range(8)]
        rand_blocks = [func(r, c) for r, c in rand_cells]
        rand_in_range = [b for b in rand_blocks if min_block <= b <= max_block]
        rand_patoshi = sum(1 for b in rand_in_range if b in patoshi_blocks)
        mc_matches.append(rand_patoshi)

    expected = np.mean(mc_matches) if mc_matches else 0
    p_val = sum(1 for m in mc_matches if m >= patoshi) / len(mc_matches) if mc_matches else 1

    results[name] = {
        "in_range": len(ir),
        "patoshi": patoshi,
        "expected": expected,
        "p_value": p_val,
    }

    sig = "✅" if p_val < 0.05 else "❌"
    print(f"   {name:15} | In Range: {len(ir):2} | Patoshi: {patoshi:2} | Expected: {expected:.1f} | p={p_val:.4f} {sig}")

# ==============================================================================
# TEST 4: BONFERRONI KORREKTUR
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 4: MULTIPLE TESTING KORREKTUR (Bonferroni)")
print("=" * 80)

n_tests = len(interpretations)
bonferroni_alpha = 0.05 / n_tests

print(f"\n   Anzahl Tests: {n_tests}")
print(f"   Ursprüngliches α: 0.05")
print(f"   Bonferroni-korrigiertes α: {bonferroni_alpha:.6f}")

significant_after_correction = []
for name, res in results.items():
    if res["p_value"] < bonferroni_alpha:
        significant_after_correction.append(name)
        print(f"   ✅ {name}: p={res['p_value']:.6f} < {bonferroni_alpha:.6f}")

if not significant_after_correction:
    print(f"   ❌ KEINE Interpretation bleibt nach Bonferroni-Korrektur signifikant!")
else:
    print(f"\n   {len(significant_after_correction)}/{n_tests} bleiben signifikant")

# ==============================================================================
# TEST 5: ALTERNATIVE ERKLÄRUNGEN
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 5: ALTERNATIVE ERKLÄRUNGEN PRÜFEN")
print("=" * 80)

# Check base rate for early blocks
early_patoshi = [b for b in patoshi_blocks if b < 10000]
early_total = 10000 - min_block
early_ratio = len(early_patoshi) / early_total

print(f"\n   📊 EARLY BLOCK ANALYSIS (Blocks < 10000):")
print(f"   Patoshi Blocks < 10000: {len(early_patoshi)}")
print(f"   Total Blocks < 10000: {early_total}")
print(f"   Patoshi Ratio (early): {early_ratio:.4f} ({early_ratio*100:.2f}%)")
print(f"   Patoshi Ratio (all): {patoshi_ratio:.4f} ({patoshi_ratio*100:.2f}%)")

# Recalculate with early block rate
early_blocks_combined = [b for b in actual_combined if b < 10000]
early_patoshi_matches = [b for b in early_blocks_combined if b in patoshi_blocks]

print(f"\n   Mit Early Block Rate:")
print(f"   Bridge Blocks < 10000: {len(early_blocks_combined)}")
print(f"   Davon Patoshi: {len(early_patoshi_matches)}")

# Expected with early rate
expected_early = len(early_blocks_combined) * early_ratio
print(f"   Erwartet bei {early_ratio*100:.1f}% Rate: {expected_early:.1f}")
print(f"   Tatsächlich: {len(early_patoshi_matches)}")
print(f"   Differenz: {len(early_patoshi_matches) - expected_early:.1f}")

# ==============================================================================
# TEST 6: EFFEKTSTÄRKE
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 6: EFFEKTSTÄRKE (Cohen's h)")
print("=" * 80)

# Cohen's h for proportions
observed_rate = len(patoshi_matches) / len(in_range) if in_range else 0
expected_rate = patoshi_ratio

phi_obs = 2 * math.asin(math.sqrt(observed_rate))
phi_exp = 2 * math.asin(math.sqrt(expected_rate))
cohens_h = phi_obs - phi_exp

print(f"\n   Beobachtete Rate: {observed_rate:.4f}")
print(f"   Erwartete Rate: {expected_rate:.4f}")
print(f"   Cohen's h: {cohens_h:.4f}")

if abs(cohens_h) < 0.2:
    effect = "KLEIN (negligible)"
elif abs(cohens_h) < 0.5:
    effect = "KLEIN bis MITTEL"
elif abs(cohens_h) < 0.8:
    effect = "MITTEL"
else:
    effect = "GROSS"

print(f"   Effektstärke: {effect}")

# ==============================================================================
# TEST 7: SYMBOLISCHE BEDEUTUNG VALIDIERUNG
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 7: SYMBOLISCHE BEDEUTUNG - KRITISCHE PRÜFUNG")
print("=" * 80)

# Calculate palindrome probability
def is_palindrome(n):
    s = str(n)
    return s == s[::-1]

# Simulate
palindrome_count = 0
for _ in range(10000):
    random_blocks = [coords_to_combined_block(random.randint(0,127), random.randint(0,127)) for _ in range(8)]
    if any(is_palindrome(b) for b in random_blocks):
        palindrome_count += 1

print(f"\n   Wahrscheinlichkeit mind. 1 Palindrom in 8 Blocks: {palindrome_count/100:.1f}%")

# Check for "interesting" numbers
interesting_years = [1776, 1984, 2001, 2020, 2021, 2022, 2023, 2024, 2025]
interesting_count = 0
for _ in range(10000):
    random_blocks = [coords_to_combined_block(random.randint(0,127), random.randint(0,127)) for _ in range(8)]
    if any(b in interesting_years for b in random_blocks):
        interesting_count += 1

print(f"   Wahrscheinlichkeit ein 'interessantes' Jahr: {interesting_count/100:.1f}%")

# ==============================================================================
# ZUSAMMENFASSUNG
# ==============================================================================
print("\n" + "=" * 80)
print("KRITISCHE ZUSAMMENFASSUNG")
print("=" * 80)

print(f"""
   ╔══════════════════════════════════════════════════════════════════════════╗
   ║                    VALIDIERUNGS-ERGEBNISSE                               ║
   ╠══════════════════════════════════════════════════════════════════════════╣
   ║                                                                          ║
   ║  1. STATISTISCHE SIGNIFIKANZ:                                            ║
   ║     - p-Wert Combined: {p_value if p_value else 'N/A':.4f}                                           ║
   ║     - Nach Bonferroni: {'JA' if significant_after_correction else 'NEIN':44}  ║
   ║                                                                          ║
   ║  2. EFFEKTSTÄRKE:                                                        ║
   ║     - Cohen's h = {cohens_h:.4f} → {effect:32}      ║
   ║                                                                          ║
   ║  3. BASE RATE PROBLEM:                                                   ║
   ║     - Patoshi-Ratio ist {patoshi_ratio*100:.1f}% - sehr hoch!                          ║
   ║     - Bei frühen Blocks sogar {early_ratio*100:.1f}%                                  ║
   ║                                                                          ║
   ║  4. GESAMTURTEIL:                                                        ║
   ║     Die Evidenz ist NICHT ÜBERZEUGEND genug für eine                     ║
   ║     wissenschaftliche Publikation ohne weitere Validierung!              ║
   ║                                                                          ║
   ╚══════════════════════════════════════════════════════════════════════════╝
""")

# Save results
validation_results = {
    "patoshi_ratio": patoshi_ratio,
    "early_block_ratio": early_ratio,
    "combined_interpretation": {
        "in_range": len(in_range),
        "patoshi_matches": len(patoshi_matches),
        "p_value": p_value,
    },
    "bonferroni_significant": significant_after_correction,
    "cohens_h": cohens_h,
    "effect_size": effect,
    "conclusion": "WEITERE VALIDIERUNG ERFORDERLICH - Evidenz nicht überzeugend",
}

with open(script_dir / "CRITICAL_VALIDATION_RESULTS.json", "w") as f:
    json.dump(validation_results, f, indent=2)

print("\n✓ Ergebnisse gespeichert in CRITICAL_VALIDATION_RESULTS.json")
