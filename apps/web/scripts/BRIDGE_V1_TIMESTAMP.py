#!/usr/bin/env python3
"""
===============================================================================
        BRIDGE V1: PRE-GENESIS TIMESTAMP VERIFICATION
===============================================================================
PRE-REGISTERED HYPOTHESES:
  H1.4: 1221069728 % 121 = 43 (trivial arithmetic verification)
  H1.5: Timestamp 1221069728 converts to 2008-09-10 (~115 days before Genesis)
  H1.6: p = 0.00826 (1/121) is honest, BUT must apply Bonferroni correction
        for testing multiple divisors (if 121 was chosen post-hoc)

CRITICAL TEST:
  Test ALL divisors from 2 to 200. For each divisor D, check if
  1221069728 % D produces a "meaningful" remainder (like 43 = Qubic epoch start).
  If many divisors produce "interesting" remainders, the 121 finding is not special.

SIGNIFICANCE THRESHOLD: p < 0.001 (after Bonferroni for 199 divisors)
===============================================================================
"""

import json
import numpy as np
from datetime import datetime, timezone
from pathlib import Path

script_dir = Path(__file__).parent
np.random.seed(42)

print("=" * 80)
print("         BRIDGE V1: PRE-GENESIS TIMESTAMP VERIFICATION")
print("=" * 80)
print(f"\nDate: {datetime.now().isoformat()}")

results = {}

TIMESTAMP = 1221069728
GENESIS_TIMESTAMP = 1231006505  # Bitcoin Genesis block (2009-01-03 18:15:05 UTC)
QUBIC_EPOCH = 43  # Claimed significant value

# ============================================================================
# H1.4: Arithmetic Verification
# ============================================================================
print("\n" + "=" * 80)
print("H1.4: Arithmetic Verification")
print("=" * 80)

remainder = TIMESTAMP % 121
h1_4_pass = remainder == 43

print(f"\n  1221069728 % 121 = {remainder}")
print(f"  Expected: 43")
print(f"  Result: {'CONFIRMED' if h1_4_pass else 'FAILED'}")

results["h1_4_remainder"] = remainder
results["h1_4_confirmed"] = h1_4_pass

# ============================================================================
# H1.5: Date Verification
# ============================================================================
print("\n" + "=" * 80)
print("H1.5: Date Verification")
print("=" * 80)

dt = datetime.fromtimestamp(TIMESTAMP, tz=timezone.utc)
genesis_dt = datetime.fromtimestamp(GENESIS_TIMESTAMP, tz=timezone.utc)
days_before = (genesis_dt - dt).days

print(f"\n  Timestamp: {TIMESTAMP}")
print(f"  UTC date: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"  Genesis block: {genesis_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"  Days before Genesis: {days_before}")
print(f"  Expected: ~115 days before Genesis")
print(f"  Result: {'CONFIRMED' if 110 <= days_before <= 120 else 'DIFFERENT'} ({days_before} days)")

results["h1_5_date"] = dt.isoformat()
results["h1_5_days_before_genesis"] = days_before
results["h1_5_confirmed"] = 110 <= days_before <= 120

# ============================================================================
# H1.6: Bonferroni Correction for Multiple Divisor Testing
# ============================================================================
print("\n" + "=" * 80)
print("H1.6: Multiple Divisor Testing (Bonferroni)")
print("=" * 80)

print(f"\n  CRITICAL QUESTION: Was 121 chosen post-hoc?")
print(f"  If yes, we must test whether OTHER divisors also produce 'interesting' results.")
print(f"")
print(f"  Testing divisors 2-200 against timestamp {TIMESTAMP}...")

# Define "interesting" remainders
INTERESTING_VALUES = {
    0: "zero (divisible)",
    1: "unity",
    7: "lucky number",
    13: "significant in numerology",
    27: "3^3 / Qubic connection",
    42: "answer to everything",
    43: "Qubic epoch",
    64: "2^6",
    121: "11^2",
    127: "2^7-1 (matrix size)",
    128: "2^7 (matrix dimension)",
}

print(f"\n  {'Divisor':<10} {'Remainder':<12} {'P(exact)':<12} {'Interesting?':<20}")
print("  " + "-" * 60)

interesting_hits = []
all_remainders = {}

for d in range(2, 201):
    r = TIMESTAMP % d
    all_remainders[d] = r
    p_exact = 1.0 / d  # probability of getting exactly this remainder

    is_interesting = r in INTERESTING_VALUES or r == d - 1 or r <= 1

    if r in INTERESTING_VALUES:
        label = INTERESTING_VALUES[r]
        interesting_hits.append((d, r, label))
        print(f"  {d:<10} {r:<12} {p_exact:<12.6f} {label}")

print(f"\n  Total divisors tested: 199")
print(f"  Divisors producing 'interesting' remainders: {len(interesting_hits)}")

# Bonferroni correction
p_single = 1.0 / 121
p_bonferroni = min(1.0, p_single * 199)

print(f"\n  Bonferroni analysis for divisor 121 → remainder 43:")
print(f"    Single-test p-value: {p_single:.6f} (1/121)")
print(f"    Number of divisors tested: 199 (2 through 200)")
print(f"    Bonferroni-corrected p: {p_bonferroni:.4f}")
print(f"    Significant at p < 0.05? {'YES' if p_bonferroni < 0.05 else 'NO'}")
print(f"    Significant at p < 0.001? {'YES' if p_bonferroni < 0.001 else 'NO'}")

results["h1_6_p_single"] = p_single
results["h1_6_p_bonferroni"] = p_bonferroni
results["h1_6_interesting_hits"] = len(interesting_hits)

# ============================================================================
# DEEPER: Why 121?
# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS: Why Divisor 121?")
print("=" * 80)

print(f"\n  121 = 11^2")
print(f"  11 is significant in Qubic: 11 quorum members")
print(f"  The connection chain: 121 → 11^2 → Qubic quorum")
print(f"")
print(f"  But this is POST-HOC reasoning. The divisor was chosen because")
print(f"  it produces remainder 43. We must evaluate what happens if we")
print(f"  search for ANY connection.")

# How many divisors < 200 produce remainder 43?
divs_with_43 = [d for d in range(44, 201) if TIMESTAMP % d == 43]
print(f"\n  Divisors in [44, 200] producing remainder 43: {len(divs_with_43)}")
print(f"  They are: {divs_with_43}")
print(f"  Expected count (random): {len(range(44, 201)) / 43:.1f}")  # rough

# For each, check if the divisor itself has a "story"
print(f"\n  Can we tell a story for each?")
for d in divs_with_43:
    # Check if d has mathematical properties
    props = []
    sqrt_d = d ** 0.5
    if sqrt_d == int(sqrt_d):
        props.append(f"perfect square ({int(sqrt_d)}^2)")
    if d % 11 == 0:
        props.append(f"divisible by 11 (= {d//11} × 11)")
    if all(d % i != 0 for i in range(2, int(d**0.5) + 1)):
        props.append("prime")
    # Check powers
    for base in range(2, 20):
        for exp in range(2, 10):
            if base ** exp == d:
                props.append(f"{base}^{exp}")

    props_str = ", ".join(props) if props else "no special properties"
    print(f"    {d}: {props_str}")

# ============================================================================
# ADDITIONAL: Relationship Between Timestamps
# ============================================================================
print("\n" + "=" * 80)
print("ADDITIONAL: Timestamp Relationships")
print("=" * 80)

diff = GENESIS_TIMESTAMP - TIMESTAMP
print(f"\n  Genesis - PreGenesis = {diff} seconds")
print(f"  = {diff / 3600:.1f} hours")
print(f"  = {diff / 86400:.1f} days")
print(f"  = {diff / (86400 * 7):.1f} weeks")
print(f"  {diff} mod 121 = {diff % 121}")
print(f"  {diff} mod 27 = {diff % 27}")
print(f"  {diff} mod 576 = {diff % 576}")
print(f"  {diff} mod 128 = {diff % 128}")

# Is the difference itself "interesting"?
print(f"\n  Factorization of {diff}:")
n = diff
factors = []
for p in range(2, min(10000, n)):
    while n % p == 0:
        factors.append(p)
        n //= p
if n > 1:
    factors.append(n)
print(f"    {diff} = {' × '.join(str(f) for f in factors)}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TIMESTAMP VERIFICATION SUMMARY")
print("=" * 80)

print(f"\n  H1.4 (1221069728 % 121 = 43): {'CONFIRMED' if h1_4_pass else 'FAILED'}")
print(f"  H1.5 (Date = ~115 days before Genesis): {'CONFIRMED' if results['h1_5_confirmed'] else 'DIFFERENT'} ({days_before} days)")
print(f"  H1.6 (Bonferroni-corrected significance): p = {p_bonferroni:.4f}")
print(f"")
print(f"  VERDICT:")
print(f"    The arithmetic is correct (trivially verifiable).")
print(f"    After Bonferroni correction for testing 199 divisors,")
print(f"    p = {p_bonferroni:.4f} — {'still significant at p<0.05' if p_bonferroni < 0.05 else 'NOT significant'}.")
print(f"    {len(divs_with_43)} other divisors also produce remainder 43.")
print(f"    The choice of 121 requires independent justification (11^2 = Qubic quorum).")

# Save results
results["summary"] = {
    "h1_4": "CONFIRMED" if h1_4_pass else "FAILED",
    "h1_5": f"CONFIRMED ({days_before} days before Genesis)",
    "h1_6": f"p_bonferroni = {p_bonferroni:.4f}",
    "divisors_producing_43": divs_with_43,
}

output_path = script_dir / "BRIDGE_V1_TIMESTAMP_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n  Results saved to: {output_path}")
