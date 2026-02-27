#!/usr/bin/env python3
"""
ULTRA-KRITISCHE VALIDIERUNG - JEDE EINZELNE BEHAUPTUNG
========================================================
Prüft JEDE ZEILE des Pastebin-Dokuments auf:
- Faktische Korrektheit
- Keine Interpretationen
- Keine Übertreibungen
- Alle Zahlen belegt
- Keine "Spinnerei"
"""

import json
import numpy as np
from scipy import stats

# Load Anna Matrix
MATRIX_FILE = "../public/data/anna-matrix.json"
with open(MATRIX_FILE, 'r') as f:
    data = json.load(f)
    matrix = np.array(data['matrix'], dtype=np.int8)

POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def char_to_num(c):
    return ord(c.upper()) - ord('A')

print("=" * 80)
print("ULTRA-KRITISCHE LINE-BY-LINE VALIDIERUNG")
print("=" * 80)
print()
print("REGEL: Jede Behauptung muss 100% BEWEISBAR sein")
print("       Keine Interpretationen, keine Übertreibungen")
print()

errors = []
warnings = []

# =============================================================================
# CLAIM: "Statistical Confidence: 99.9%+ (p < 0.00001)"
# =============================================================================
print("[CLAIM] Statistical Confidence: 99.9%+ (p < 0.00001)")
print("-" * 60)

# Berechne die tatsächliche Wahrscheinlichkeit
pocc_chars = [char_to_num(c) for c in POCC]
hasv_chars = [char_to_num(c) for c in HASV]

pocc_diag = sum(matrix[c][c] for c in pocc_chars)
hasv_diag = sum(matrix[c][c] for c in hasv_chars)
diag_diff = hasv_diag - pocc_diag

# Monte Carlo für Diagonal-Differenz
np.random.seed(42)
random_diffs = []
for _ in range(10000):
    rand1 = np.random.randint(-128, 128, 60)
    rand2 = np.random.randint(-128, 128, 60)
    diff = sum(rand2) - sum(rand1)
    random_diffs.append(abs(diff))

# Wie viele sind >= 676?
extreme_count = sum(1 for d in random_diffs if d >= 676)
p_value_diagonal = extreme_count / len(random_diffs)

print(f"Monte Carlo (10,000 trials):")
print(f"  Diagonal differences >= 676: {extreme_count}/{len(random_diffs)}")
print(f"  p-value: {p_value_diagonal}")
print(f"  Claimed: p < 0.00001")

if p_value_diagonal > 0.00001:
    warnings.append(f"p-value ({p_value_diagonal}) ist HÖHER als claimed (0.00001)")
    print(f"  ⚠️  WARNING: Actual p-value is {p_value_diagonal}, not < 0.00001")
else:
    print(f"  ✓ VERIFIED: p-value < 0.00001")

print()

# =============================================================================
# CLAIM: "Chance Probability: < 0.00001%"
# =============================================================================
print("[CLAIM] Chance Probability: < 0.00001%")
print("-" * 60)

claimed_prob = 0.00001 / 100  # Als Dezimalzahl
actual_prob = p_value_diagonal

print(f"Claimed: < 0.00001% = {claimed_prob}")
print(f"Actual:  {actual_prob * 100:.6f}%")

if actual_prob > claimed_prob:
    warnings.append(f"Actual probability ({actual_prob*100}%) higher than claimed")
    print(f"  ⚠️  WARNING: Übertreibung detected")
else:
    print(f"  ✓ VERIFIED")

print()

# =============================================================================
# CLAIM: Diagonal sums exact values
# =============================================================================
print("[CLAIM] POCC diagonal = -1,231, HASV diagonal = -555")
print("-" * 60)

print(f"POCC diagonal: {pocc_diag}")
print(f"HASV diagonal: {hasv_diag}")

if pocc_diag != -1231:
    errors.append(f"POCC diagonal is {pocc_diag}, NOT -1231")
    print(f"  ❌ ERROR: Wrong value!")

if hasv_diag != -555:
    errors.append(f"HASV diagonal is {hasv_diag}, NOT -555")
    print(f"  ❌ ERROR: Wrong value!")

if pocc_diag == -1231 and hasv_diag == -555:
    print(f"  ✓ VERIFIED: Both values exact")

print()

# =============================================================================
# CLAIM: Character sum difference = 138
# =============================================================================
print("[CLAIM] Character sum difference = 138")
print("-" * 60)

pocc_sum = sum(char_to_num(c) for c in POCC)
hasv_sum = sum(char_to_num(c) for c in HASV)
char_diff = hasv_sum - pocc_sum

print(f"POCC sum: {pocc_sum}")
print(f"HASV sum: {hasv_sum}")
print(f"Difference: {char_diff}")

if char_diff != 138:
    errors.append(f"Character diff is {char_diff}, NOT 138")
    print(f"  ❌ ERROR: Wrong value!")
else:
    print(f"  ✓ VERIFIED: Exactly 138")

print()

# =============================================================================
# CLAIM: "138 = 6 × 23"
# =============================================================================
print("[CLAIM] 138 = 6 × 23")
print("-" * 60)

if 6 * 23 != 138:
    errors.append("6 × 23 ≠ 138")
    print(f"  ❌ ERROR: Math is wrong!")
else:
    print(f"  6 × 23 = {6*23}")
    print(f"  ✓ VERIFIED: Faktisch korrekt")

print()

# =============================================================================
# CLAIM: "Row 6 bias toward 26 (18.8%)"
# =============================================================================
print("[CLAIM] Row 6 has value 26 appearing 18.8% of the time")
print("-" * 60)

row6 = matrix[6]
count_26 = np.sum(row6 == 26)
percentage_26 = (count_26 / 128) * 100

print(f"Value 26 appears: {count_26} times out of 128")
print(f"Percentage: {percentage_26:.1f}%")
print(f"Claimed: 18.8%")

if abs(percentage_26 - 18.8) > 0.1:
    errors.append(f"Row 6: 26 appears {percentage_26}%, NOT 18.8%")
    print(f"  ❌ ERROR: Wrong percentage!")
else:
    print(f"  ✓ VERIFIED: Correct percentage")

# Ist das statistisch signifikant biased?
expected = 1 / 128  # Bei random distribution
observed = count_26 / 128

# Chi-square test
from scipy.stats import chisquare
expected_counts = np.ones(128) * (128 / 128)  # Uniform
observed_counts = np.bincount(row6 + 128, minlength=256)[-128:]  # Shift für negative Werte

# Simplified: Ist 26 überrepräsentiert?
if count_26 > 3:  # Mehr als 3× expected (1/128 * 128 = 1)
    print(f"  ✓ VERIFIED: 26 is overrepresented ({count_26}× vs expected ~1)")
else:
    warnings.append("26 is NOT significantly overrepresented")
    print(f"  ⚠️  WARNING: Not as biased as claimed")

print()

# =============================================================================
# CLAIM: "matrix[6, 33] = 26"
# =============================================================================
print("[CLAIM] matrix[6, 33] = 26")
print("-" * 60)

val_6_33 = matrix[6][33]
print(f"matrix[6, 33] = {val_6_33}")

if val_6_33 != 26:
    errors.append(f"matrix[6,33] is {val_6_33}, NOT 26")
    print(f"  ❌ ERROR: Wrong value!")
else:
    print(f"  ✓ VERIFIED")

print()

# =============================================================================
# CLAIM: "matrix[6, 46] = 90"
# =============================================================================
print("[CLAIM] matrix[6, 46] = 90")
print("-" * 60)

val_6_46 = matrix[6][46]
print(f"matrix[6, 46] = {val_6_46}")

if val_6_46 != 90:
    errors.append(f"matrix[6,46] is {val_6_46}, NOT 90")
    print(f"  ❌ ERROR: Wrong value!")
else:
    print(f"  ✓ VERIFIED")

print()

# =============================================================================
# CLAIM: "matrix[6, 37] = 26"
# =============================================================================
print("[CLAIM] matrix[6, 37] = 26 (Smart Contract)")
print("-" * 60)

val_6_37 = matrix[6][37]
print(f"matrix[6, 37] = {val_6_37}")

if val_6_37 != 26:
    errors.append(f"matrix[6,37] is {val_6_37}, NOT 26")
    print(f"  ❌ ERROR: Wrong value!")
else:
    print(f"  ✓ VERIFIED")

print()

# =============================================================================
# CLAIM: "POCC (1-based) = 672"
# =============================================================================
print("[CLAIM] POCC 1-based sum = 672")
print("-" * 60)

pocc_1based = sum(char_to_num(c) + 1 for c in POCC)
print(f"POCC 1-based sum: {pocc_1based}")

if pocc_1based != 672:
    errors.append(f"POCC 1-based is {pocc_1based}, NOT 672")
    print(f"  ❌ ERROR: Wrong value!")
else:
    print(f"  ✓ VERIFIED")

print()

# =============================================================================
# CLAIM: "6 identical positions"
# =============================================================================
print("[CLAIM] 6 identical positions")
print("-" * 60)

identical = [i for i in range(60) if POCC[i] == HASV[i]]
print(f"Identical positions: {len(identical)}")
print(f"Positions: {identical}")

if len(identical) != 6:
    errors.append(f"Found {len(identical)} identical positions, NOT 6")
    print(f"  ❌ ERROR: Wrong count!")
else:
    print(f"  ✓ VERIFIED")

print()

# =============================================================================
# CLAIM: "Position 34 = 'H', matrix[7,7] = 26"
# =============================================================================
print("[CLAIM] Position 34: both 'H', matrix[7,7] = 26")
print("-" * 60)

if 34 not in identical:
    errors.append("Position 34 is NOT identical")
    print(f"  ❌ ERROR: Position 34 is not the same!")
    print(f"  POCC[34] = '{POCC[34]}', HASV[34] = '{HASV[34]}'")
else:
    char_34 = POCC[34]
    print(f"Position 34: '{char_34}'")

    if char_34 != 'H':
        errors.append(f"Position 34 is '{char_34}', NOT 'H'")
        print(f"  ❌ ERROR: Not 'H'!")
    else:
        val_7_7 = matrix[7][7]
        print(f"matrix[7, 7] = {val_7_7}")

        if val_7_7 != 26:
            errors.append(f"matrix[7,7] is {val_7_7}, NOT 26")
            print(f"  ❌ ERROR: Wrong value!")
        else:
            print(f"  ✓ VERIFIED")

print()

# =============================================================================
# CLAIM: "Row 79 difference = 26"
# =============================================================================
print("[CLAIM] Row 79 difference = 26")
print("-" * 60)

row79_pocc = sum(matrix[79][c] for c in pocc_chars if c < 128)
row79_hasv = sum(matrix[79][c] for c in hasv_chars if c < 128)
row79_diff = row79_hasv - row79_pocc

print(f"Row 79 POCC: {row79_pocc}")
print(f"Row 79 HASV: {row79_hasv}")
print(f"Difference: {row79_diff}")

if row79_diff != 26:
    errors.append(f"Row 79 diff is {row79_diff}, NOT 26")
    print(f"  ❌ ERROR: Wrong value!")
else:
    print(f"  ✓ VERIFIED")

print()

# =============================================================================
# CLAIM: "mod 23 identical"
# =============================================================================
print("[CLAIM] Both character sums mod 23 = 14")
print("-" * 60)

pocc_mod23 = pocc_sum % 23
hasv_mod23 = hasv_sum % 23

print(f"POCC mod 23: {pocc_mod23}")
print(f"HASV mod 23: {hasv_mod23}")

if pocc_mod23 != 14 or hasv_mod23 != 14:
    errors.append(f"mod 23: POCC={pocc_mod23}, HASV={hasv_mod23}, NOT both 14")
    print(f"  ❌ ERROR: Not both 14!")
elif pocc_mod23 != hasv_mod23:
    errors.append("mod 23: Not identical")
    print(f"  ❌ ERROR: Not identical!")
else:
    print(f"  ✓ VERIFIED: Both = 14")

print()

# =============================================================================
# CLAIM: "Diagonal mod 676 = 121"
# =============================================================================
print("[CLAIM] Both diagonal sums mod 676 = 121")
print("-" * 60)

pocc_diag_mod676 = pocc_diag % 676
hasv_diag_mod676 = hasv_diag % 676

print(f"POCC diagonal mod 676: {pocc_diag_mod676}")
print(f"HASV diagonal mod 676: {hasv_diag_mod676}")

if pocc_diag_mod676 != 121 or hasv_diag_mod676 != 121:
    errors.append(f"diag mod 676: POCC={pocc_diag_mod676}, HASV={hasv_diag_mod676}, NOT both 121")
    print(f"  ❌ ERROR: Not both 121!")
elif pocc_diag_mod676 != hasv_diag_mod676:
    errors.append("diag mod 676: Not identical")
    print(f"  ❌ ERROR: Not identical!")
else:
    print(f"  ✓ VERIFIED: Both = 121")

print()

# =============================================================================
# CLAIM: "GENESIS supply = 676,000,000,000"
# =============================================================================
print("[CLAIM] GENESIS token supply = 676,000,000,000")
print("-" * 60)

# Wir können die Supply nicht direkt verifizieren ohne Blockchain-Zugriff
print("⚠️  CANNOT VERIFY: Requires blockchain data")
print("   This claim should be marked as 'Reported' not 'Verified'")
warnings.append("Token supplies cannot be verified without blockchain access")

print()

# =============================================================================
# CLAIM: "EXODUS supply = 676"
# =============================================================================
print("[CLAIM] EXODUS token supply = 676")
print("-" * 60)

print("⚠️  CANNOT VERIFY: Requires blockchain data")
print("   This claim should be marked as 'Reported' not 'Verified'")

print()

# =============================================================================
# INTERPRETATIONEN PRÜFEN
# =============================================================================
print("\n" + "=" * 80)
print("PRÜFUNG: INTERPRETATIONEN vs FAKTEN")
print("=" * 80 + "\n")

interpretations = [
    ("POCC & HASV are a designed pair", "INTERPRETATION - nicht 100% beweisbar"),
    ("Deliberate mathematical design", "INTERPRETATION - hochwahrscheinlich aber nicht 100%"),
    ("Whoever created POCC/HASV designed the Anna Matrix", "SPEKULATION"),
    ("CFB = Satoshi", "SPEKULATION - CFB hat es sogar dementiert"),
    ("26 = YHVH was chosen deliberately", "INTERPRETATION"),
]

for claim, status in interpretations:
    print(f"'{claim}'")
    print(f"  → {status}")
    print()

# =============================================================================
# FINAL REPORT
# =============================================================================
print("=" * 80)
print("VALIDIERUNGS-REPORT")
print("=" * 80)
print()

print(f"ERRORS (faktisch falsch): {len(errors)}")
for error in errors:
    print(f"  ❌ {error}")

print()
print(f"WARNINGS (Übertreibungen/nicht verifizierbar): {len(warnings)}")
for warning in warnings:
    print(f"  ⚠️  {warning}")

print()

if len(errors) == 0:
    print("✅ ALLE ZAHLEN SIND KORREKT")
else:
    print(f"❌ {len(errors)} FEHLER GEFUNDEN - DOKUMENT MUSS KORRIGIERT WERDEN")

print()
print("EMPFEHLUNGEN:")
print("  1. Alle 'PROVEN' → 'VERIFIED' (wenn Zahlen stimmen)")
print("  2. Alle 'PROVEN' → 'HIGHLY LIKELY' (wenn Interpretation)")
print("  3. Token supplies: 'Reported' nicht 'Verified'")
print("  4. p-values: Nur angeben wenn exakt berechnet")
print("  5. Alle Spekulationen klar markieren")
print()
