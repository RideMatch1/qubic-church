#!/usr/bin/env python3
"""
===============================================================================
        BRIDGE V2: ADDRESS PREFIX BASE RATE ANALYSIS
===============================================================================
PRE-REGISTERED HYPOTHESES:
  H2.1: Expected count of "1CFB" prefix in 983k addresses = 983040/58^3 ≈ 5.04
  H2.2: 15 occurrences is (or is not) significant under Poisson(λ=5.04)
  H2.3: Count ALL 4-char prefixes in the dataset. How many OTHER prefixes
        appear 15+ times? If many do, "1CFB" is not special.

ALSO TESTS (BRIDGE_V2_DERIVED_AUDIT combined):
  H2.4: Count "1CFB" prefix in bitcoin-derived-addresses.json (20,955 addresses)
  H2.5: Count ALL 4-char prefixes in derived addresses

METHODOLOGY:
  - Analytical: Calculate Poisson probability
  - Empirical: Count all prefixes in actual data files
  - Bonferroni: Correct for number of possible 4-char prefixes tested

SIGNIFICANCE: p < 0.001 after Bonferroni for 195,112 possible prefixes
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from math import factorial, exp, log
from datetime import datetime

script_dir = Path(__file__).parent
np.random.seed(42)

print("=" * 80)
print("         BRIDGE V2: ADDRESS PREFIX BASE RATE ANALYSIS")
print("=" * 80)
print(f"\nDate: {datetime.now().isoformat()}")

results = {}

# ============================================================================
# H2.1: Analytical Base Rate Calculation
# ============================================================================
print("\n" + "=" * 80)
print("H2.1: Analytical Base Rate for '1CFB' Prefix")
print("=" * 80)

# Bitcoin Base58Check address format:
# First character: "1" (P2PKH), "3" (P2SH), "bc1" (Bech32)
# Remaining chars: Base58 alphabet (123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz)
# Base58 has 58 characters

BASE58_SIZE = 58
N_ADDRESSES_CLAIMED = 983040
N_ADDRESSES_DERIVED = 20955

# P("1CFB") for a random address starting with "1":
# Position 0: must be "1" (already fixed for P2PKH)
# Position 1: "C" is one of 58 possible chars → P = 1/58
# Position 2: "F" is one of 58 possible chars → P = 1/58
# Position 3: "B" is one of 58 possible chars → P = 1/58
# P("1CFB") = 1/58^3 (given address starts with "1")

p_1cfb_given_1 = 1.0 / (BASE58_SIZE ** 3)
total_possible_3char_suffixes = BASE58_SIZE ** 3  # 195,112

print(f"\n  Base58 alphabet size: {BASE58_SIZE}")
print(f"  P('1CFB' | starts with '1') = 1/{BASE58_SIZE}^3 = 1/{total_possible_3char_suffixes}")
print(f"  P = {p_1cfb_given_1:.8f}")
print(f"")
print(f"  For N = {N_ADDRESSES_CLAIMED:,} addresses:")
expected_983k = N_ADDRESSES_CLAIMED * p_1cfb_given_1
print(f"    Expected '1CFB' count: {expected_983k:.2f}")
print(f"    Claimed count: 15")
print(f"    Ratio: {15 / expected_983k:.1f}x expected")

print(f"\n  For N = {N_ADDRESSES_DERIVED:,} derived addresses:")
expected_21k = N_ADDRESSES_DERIVED * p_1cfb_given_1
print(f"    Expected '1CFB' count: {expected_21k:.3f}")

results["h2_1"] = {
    "p_1cfb": p_1cfb_given_1,
    "total_possible_prefixes": total_possible_3char_suffixes,
    "expected_983k": expected_983k,
    "expected_21k": expected_21k,
}

# ============================================================================
# H2.2: Poisson Significance Test
# ============================================================================
print("\n" + "=" * 80)
print("H2.2: Poisson Test for 15 Occurrences")
print("=" * 80)

def poisson_pmf(k, lam):
    """Calculate P(X = k) for Poisson distribution."""
    return exp(-lam) * (lam ** k) / factorial(k)

def poisson_sf(k, lam):
    """Calculate P(X >= k) for Poisson distribution (survival function)."""
    # P(X >= k) = 1 - P(X < k) = 1 - sum(P(X=i) for i in range(k))
    cumul = sum(poisson_pmf(i, lam) for i in range(k))
    return 1.0 - cumul

lam = expected_983k
observed = 15

p_exact = poisson_pmf(observed, lam)
p_tail = poisson_sf(observed, lam)

print(f"\n  Poisson test: X ~ Poisson(λ = {lam:.2f})")
print(f"  Observed: k = {observed}")
print(f"  P(X = {observed}) = {p_exact:.6f}")
print(f"  P(X >= {observed}) = {p_tail:.6f}")
print(f"")
print(f"  Without correction:")
print(f"    Significant at p < 0.05? {'YES' if p_tail < 0.05 else 'NO'}")
print(f"    Significant at p < 0.001? {'YES' if p_tail < 0.001 else 'NO'}")

# Bonferroni: we could have been excited about ANY 4-char prefix
p_bonferroni = min(1.0, p_tail * total_possible_3char_suffixes)

print(f"\n  With Bonferroni correction (m = {total_possible_3char_suffixes:,} possible prefixes):")
print(f"    Corrected p = {p_bonferroni:.4f}")
print(f"    Significant at p < 0.05? {'YES' if p_bonferroni < 0.05 else 'NO'}")
print(f"    Significant at p < 0.001? {'YES' if p_bonferroni < 0.001 else 'NO'}")

results["h2_2"] = {
    "lambda": lam,
    "observed": observed,
    "p_exact": p_exact,
    "p_tail": p_tail,
    "p_bonferroni": p_bonferroni,
}

# ============================================================================
# H2.3: All 4-Char Prefix Analysis (Derived Addresses)
# ============================================================================
print("\n" + "=" * 80)
print("H2.3/H2.4/H2.5: Actual Prefix Counts in Data")
print("=" * 80)

# Load derived addresses
btc_path = script_dir.parent / "public" / "data" / "bitcoin-derived-addresses.json"
with open(btc_path) as f:
    btc_data = json.load(f)

if isinstance(btc_data, dict) and "records" in btc_data:
    btc_records = btc_data["records"]
elif isinstance(btc_data, list):
    btc_records = btc_data
else:
    btc_records = []

print(f"\n  Loaded {len(btc_records)} derived address records")

# Extract addresses
addresses = []
for r in btc_records:
    if isinstance(r, dict):
        addr = r.get("address", r.get("btcAddress", ""))
    else:
        addr = str(r)
    if addr and len(addr) >= 4:
        addresses.append(addr)

print(f"  Valid addresses: {len(addresses)}")

# Count all 4-char prefixes
prefix_counter = Counter(addr[:4] for addr in addresses if addr.startswith("1"))
total_1_addresses = sum(1 for a in addresses if a.startswith("1"))

print(f"  Addresses starting with '1': {total_1_addresses}")
print(f"  Unique 4-char prefixes: {len(prefix_counter)}")

# Count "1CFB" specifically
cfb_count = prefix_counter.get("1CFB", 0)
cfb_count_lower = prefix_counter.get("1Cfb", 0)
cfb_count_any_case = sum(v for k, v in prefix_counter.items() if k.upper() == "1CFB")

print(f"\n  '1CFB' prefix count: {cfb_count}")
print(f"  '1CFB' any case: {cfb_count_any_case}")

# How many prefixes appear as many or more times?
if cfb_count > 0:
    at_least_as_many = sum(1 for k, v in prefix_counter.items() if v >= cfb_count)
    print(f"  Prefixes with count >= {cfb_count}: {at_least_as_many}")
elif cfb_count_any_case > 0:
    at_least_as_many = sum(1 for k, v in prefix_counter.items() if v >= cfb_count_any_case)
    print(f"  Prefixes with count >= {cfb_count_any_case}: {at_least_as_many}")

# Top 20 most common prefixes
print(f"\n  Top 20 most common 4-char prefixes:")
print(f"  {'Prefix':<10} {'Count':<8} {'Expected':<10} {'Ratio'}")
print("  " + "-" * 40)

expected_per = total_1_addresses * p_1cfb_given_1
for prefix, count in prefix_counter.most_common(20):
    ratio = count / expected_per if expected_per > 0 else 0
    print(f"  {prefix:<10} {count:<8} {expected_per:.2f}{'':>5} {ratio:.1f}x")

# Expected number of addresses per prefix
expected_per_prefix_21k = len(addresses) / total_possible_3char_suffixes
print(f"\n  Expected addresses per prefix (uniform): {expected_per_prefix_21k:.4f}")

# How many prefixes appear 2+ times? (relevant for small datasets)
prefixes_2plus = sum(1 for v in prefix_counter.values() if v >= 2)
prefixes_5plus = sum(1 for v in prefix_counter.values() if v >= 5)
prefixes_10plus = sum(1 for v in prefix_counter.values() if v >= 10)
prefixes_15plus = sum(1 for v in prefix_counter.values() if v >= 15)

print(f"\n  Prefix frequency distribution:")
print(f"    Prefixes appearing 2+ times: {prefixes_2plus}")
print(f"    Prefixes appearing 5+ times: {prefixes_5plus}")
print(f"    Prefixes appearing 10+ times: {prefixes_10plus}")
print(f"    Prefixes appearing 15+ times: {prefixes_15plus}")

results["h2_3_4_5"] = {
    "total_addresses": len(addresses),
    "total_starting_with_1": total_1_addresses,
    "unique_prefixes": len(prefix_counter),
    "1CFB_count": cfb_count,
    "1CFB_any_case": cfb_count_any_case,
    "top_20": prefix_counter.most_common(20),
    "prefixes_2plus": prefixes_2plus,
    "prefixes_5plus": prefixes_5plus,
    "prefixes_10plus": prefixes_10plus,
    "prefixes_15plus": prefixes_15plus,
}

# ============================================================================
# METHOD-LEVEL ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("METHOD-LEVEL: Prefix by Derivation Method")
print("=" * 80)

# Group by derivation method
method_prefixes = {}
for r in btc_records:
    if isinstance(r, dict):
        method = r.get("method", "unknown")
        addr = r.get("address", "")
        if addr and len(addr) >= 4 and addr.startswith("1"):
            if method not in method_prefixes:
                method_prefixes[method] = Counter()
            method_prefixes[method][addr[:4]] += 1

for method, counter in method_prefixes.items():
    total_method = sum(counter.values())
    cfb_in_method = counter.get("1CFB", 0)
    top3 = counter.most_common(3)
    print(f"\n  Method: {method}")
    print(f"    Total addresses: {total_method}")
    print(f"    '1CFB' count: {cfb_in_method}")
    print(f"    Top 3 prefixes: {top3}")

results["method_analysis"] = {
    method: {
        "total": sum(counter.values()),
        "1CFB": counter.get("1CFB", 0),
        "top_5": counter.most_common(5),
    }
    for method, counter in method_prefixes.items()
}

# ============================================================================
# Check larger address files if they exist
# ============================================================================
print("\n" + "=" * 80)
print("EXTENDED: Checking Larger Address Files")
print("=" * 80)

larger_files = [
    "matrix-addresses.json",
    "matrix-addresses-1.json",
    "matrix-addresses-2.json",
    "matrix-addresses-3.json",
]

for fname in larger_files:
    fpath = script_dir.parent / "public" / "data" / fname
    if fpath.exists():
        try:
            # These files might be very large; just count 1CFB
            print(f"\n  File: {fname} ({fpath.stat().st_size / 1e6:.1f} MB)")

            # For very large files, stream-search for "1CFB" instead of full JSON parse
            if fpath.stat().st_size > 50_000_000:  # > 50MB
                with open(fpath) as f:
                    content = f.read()
                cfb_occurrences = content.count('"1CFB')
                print(f"    '1CFB' string occurrences (grep): {cfb_occurrences}")
                total_1_addrs = content.count('"1')  # rough count
                print(f"    Rough address count (\"1 starts): {total_1_addrs}")
            else:
                with open(fpath) as f:
                    file_data = json.load(f)

                if isinstance(file_data, dict) and "records" in file_data:
                    recs = file_data["records"]
                elif isinstance(file_data, list):
                    recs = file_data
                else:
                    recs = []

                print(f"    Records: {len(recs)}")

                # Count 1CFB
                cfb_count_file = 0
                total_in_file = 0
                for r in recs[:100000]:  # Cap at 100k for speed
                    if isinstance(r, dict):
                        addr = r.get("address", r.get("btcAddress", ""))
                    else:
                        addr = str(r)
                    if addr and len(addr) >= 4:
                        total_in_file += 1
                        if addr[:4] == "1CFB":
                            cfb_count_file += 1

                print(f"    Checked: {total_in_file} addresses")
                print(f"    '1CFB' count: {cfb_count_file}")
                print(f"    Expected: {total_in_file * p_1cfb_given_1:.2f}")
        except Exception as e:
            print(f"    ERROR: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("PREFIX BASE RATE SUMMARY")
print("=" * 80)

print(f"\n  Analytical:")
print(f"    P('1CFB' | starts with '1') = 1/{total_possible_3char_suffixes:,} = {p_1cfb_given_1:.8f}")
print(f"    Expected in 983k: {expected_983k:.2f}")
print(f"    Claimed: 15")
print(f"    Poisson p (uncorrected): {p_tail:.6f}")
print(f"    Poisson p (Bonferroni): {p_bonferroni:.4f}")
print(f"")
print(f"  Empirical (derived addresses, N={len(addresses)}):")
print(f"    '1CFB' count: {cfb_count}")
print(f"    Expected: {expected_per:.3f}")
print(f"    Prefixes with higher counts: {sum(1 for v in prefix_counter.values() if v > max(cfb_count, 1))}")
print(f"")
if p_bonferroni > 0.05:
    print(f"  VERDICT: After Bonferroni correction for {total_possible_3char_suffixes:,} possible")
    print(f"  prefixes, the '1CFB' finding is NOT statistically significant (p = {p_bonferroni:.4f}).")
    print(f"  This is a case of LOOK-ELSEWHERE EFFECT.")
elif p_bonferroni < 0.001:
    print(f"  VERDICT: '1CFB' count is significant even after Bonferroni correction.")
else:
    print(f"  VERDICT: Borderline significance (p = {p_bonferroni:.4f} after Bonferroni).")
    print(f"  This warrants further investigation but is not conclusive.")

# Save results
output_path = script_dir / "BRIDGE_V2_PREFIX_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n  Results saved to: {output_path}")
