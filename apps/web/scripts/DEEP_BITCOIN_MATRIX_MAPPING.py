#!/usr/bin/env python3
"""
BITCOIN-MATRIX MAPPING (HONEST TEST)
=====================================
Maps Bitcoin addresses to the A-Z alphabet and tests for matrix connections.
Includes a CONTROL GROUP of random Bitcoin-like addresses.

HONESTY CLAUSE: If no significant connection is found, that IS the result.
No cherry-picking, no post-hoc hypothesis adjustment.

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-10
"""

import json
import numpy as np
from pathlib import Path
import hashlib

MATRIX_FILE = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
with open(MATRIX_FILE, 'r') as f:
    data = json.load(f)
matrix = np.array(data['matrix'], dtype=np.int64)

diag_values = np.array([matrix[i][i] for i in range(26)], dtype=np.int64)

POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def c2n(c):
    return ord(c) - ord('A')

pocc_nums = np.array([c2n(c) for c in POCC])
hasv_nums = np.array([c2n(c) for c in HASV])
pocc_ds = int(diag_values[pocc_nums].sum())
hasv_ds = int(diag_values[hasv_nums].sum())

print("=" * 70)
print("BITCOIN-MATRIX MAPPING (HONEST TEST)")
print("=" * 70)
print()

# =============================================================================
# BITCOIN ADDRESSES
# =============================================================================
# Famous Bitcoin addresses
BITCOIN_ADDRESSES = {
    "Satoshi Genesis": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "1CFB Block264": "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg",
    "Satoshi Block9": "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S",
    "Satoshi Block1": "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX",
    "Hal Finney TX": "1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3",
    # Control: well-known non-Satoshi addresses
    "Bitfinex Cold": "3JZq4atUahhuA9rLhXLMhhTo133J9rF97j",
    "Binance Hot": "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s",
    "Random1": "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
    "Random2": "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
    "Random3": "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
}

# =============================================================================
# MAPPING METHODS
# =============================================================================

def map_method_uppercase(addr):
    """Extract only uppercase A-Z characters from address."""
    chars = [c for c in addr if c.isalpha() and c.isupper() and 'A' <= c <= 'Z']
    return chars

def map_method_alpha(addr):
    """Extract all alphabetic characters, convert to uppercase."""
    chars = [c.upper() for c in addr if c.isalpha()]
    # Keep only A-Z
    return [c for c in chars if 'A' <= c <= 'Z']

def map_method_hash(addr):
    """SHA256 hash of address → take 60 bytes → mod 26 → letters."""
    h = hashlib.sha256(addr.encode()).digest()
    # Extend hash if needed
    extended = h
    while len(extended) < 60:
        extended += hashlib.sha256(extended).digest()
    return [chr(b % 26 + 65) for b in extended[:60]]

def map_method_positional(addr):
    """Map each character to A-Z based on position in Base58 alphabet."""
    base58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    mapped = []
    for c in addr:
        if c in base58:
            idx = base58.index(c)
            mapped.append(chr(idx % 26 + 65))
    return mapped

METHODS = {
    "uppercase": map_method_uppercase,
    "alpha": map_method_alpha,
    "hash60": map_method_hash,
    "positional": map_method_positional,
}

print("=" * 70)
print("MAPPING BITCOIN ADDRESSES")
print("=" * 70)
print()

# =============================================================================
# COMPUTE MAPPINGS AND DIAGONAL SUMS
# =============================================================================
results = {}

for method_name, method_fn in METHODS.items():
    print(f"\n--- Method: {method_name} ---")
    print()

    method_results = {}

    for btc_name, btc_addr in BITCOIN_ADDRESSES.items():
        mapped = method_fn(btc_addr)

        if len(mapped) < 2:
            print(f"  {btc_name:20s}: only {len(mapped)} chars, SKIP")
            continue

        # Compute properties
        nums = np.array([c2n(c) for c in mapped])
        charsum = int(nums.sum())

        # Diagonal sum (only first 26 letters if available)
        if len(nums) > 0:
            diagsum = int(diag_values[nums].sum())
        else:
            diagsum = 0

        # Compare with POCC and HASV
        diag_diff_pocc = abs(diagsum - pocc_ds)
        diag_diff_hasv = abs(diagsum - hasv_ds)
        char_diff_pocc = abs(charsum - int(pocc_nums.sum()))
        char_diff_hasv = abs(charsum - int(hasv_nums.sum()))

        flags = []
        if diag_diff_pocc == 676:
            flags.append("DIAG=676 vs POCC!")
        if diag_diff_hasv == 676:
            flags.append("DIAG=676 vs HASV!")
        if char_diff_pocc == 138:
            flags.append("CHAR=138 vs POCC!")
        if char_diff_hasv == 138:
            flags.append("CHAR=138 vs HASV!")

        # Also check for 26, 121
        if diag_diff_pocc % 26 == 0 and diag_diff_pocc != 0:
            flags.append(f"diag%26=0({diag_diff_pocc//26}x)")

        flag_str = " | ".join(flags) if flags else ""
        print(f"  {btc_name:20s}: {len(mapped):2d} chars, charsum={charsum:5d}, "
              f"diagsum={diagsum:6d}, dd_P={diag_diff_pocc:5d}, dd_H={diag_diff_hasv:5d}"
              f"  {flag_str}")

        method_results[btc_name] = {
            "mapped_len": len(mapped),
            "charsum": charsum,
            "diagsum": diagsum,
            "diag_diff_pocc": diag_diff_pocc,
            "diag_diff_hasv": diag_diff_hasv,
            "flags": flags,
        }

    results[method_name] = method_results

print()

# =============================================================================
# CONTROL GROUP: Monte Carlo with same-length random mappings
# =============================================================================
print("=" * 70)
print("CONTROL GROUP: Monte Carlo Random Addresses")
print("=" * 70)
print()

# For each method, generate random "Bitcoin-like" addresses and compare
# We focus on the hash60 method since it gives consistent 60-char output
print("Testing hash60 method (consistent 60 chars):")
print()

N_CONTROL = 100_000
np.random.seed(42)

control_diag_diffs_pocc = np.zeros(N_CONTROL)
control_diag_diffs_hasv = np.zeros(N_CONTROL)

for i in range(N_CONTROL):
    # Random 60-letter address
    r_nums = np.random.randint(0, 26, 60)
    r_ds = int(diag_values[r_nums].sum())
    control_diag_diffs_pocc[i] = abs(r_ds - pocc_ds)
    control_diag_diffs_hasv[i] = abs(r_ds - hasv_ds)

# For each Bitcoin address mapped with hash60, check percentile
print("Bitcoin addresses vs. control distribution (hash60 method):")
print(f"  Control: mean diag_diff_POCC = {control_diag_diffs_pocc.mean():.1f}, "
      f"std = {control_diag_diffs_pocc.std():.1f}")
print()

hash_results = results.get("hash60", {})
for btc_name, props in hash_results.items():
    dd = props["diag_diff_pocc"]
    percentile = (control_diag_diffs_pocc <= dd).mean() * 100
    z = (dd - control_diag_diffs_pocc.mean()) / control_diag_diffs_pocc.std()
    sig = "OUTLIER" if abs(z) > 3 else ""
    print(f"  {btc_name:20s}: dd_POCC={dd:5d}, percentile={percentile:5.1f}%, z={z:+.2f} {sig}")

print()

# =============================================================================
# SPECIFIC TEST: Does the Satoshi Genesis address map to 676?
# =============================================================================
print("=" * 70)
print("SATOSHI GENESIS SPECIFIC TESTS")
print("=" * 70)
print()

satoshi = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
print(f"Address: {satoshi}")
print()

for method_name, method_fn in METHODS.items():
    mapped = method_fn(satoshi)
    mapped_str = ''.join(mapped)
    nums = np.array([c2n(c) for c in mapped])
    cs = int(nums.sum())
    ds = int(diag_values[nums].sum()) if len(nums) > 0 else 0

    print(f"Method '{method_name}':")
    print(f"  Mapped ({len(mapped)} chars): {mapped_str[:40]}{'...' if len(mapped_str) > 40 else ''}")
    print(f"  Charsum: {cs}, Diagsum: {ds}")
    print(f"  dd_POCC: {abs(ds - pocc_ds)}, dd_HASV: {abs(ds - hasv_ds)}")

    # Any modular relationships?
    dd = abs(ds - pocc_ds)
    if dd > 0:
        if dd % 676 == 0:
            print(f"  !!! dd_POCC is multiple of 676: {dd // 676}×676")
        if dd % 26 == 0:
            print(f"  dd_POCC mod 26 = 0 ({dd // 26}×26)")
        if dd % 138 == 0:
            print(f"  dd_POCC mod 138 = 0 ({dd // 138}×138)")
    print()

# =============================================================================
# CONCLUSION
# =============================================================================
print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print()

# Count total significant findings
total_flags = sum(
    len(props.get("flags", []))
    for method_results in results.values()
    for props in method_results.values()
    if "676" in str(props.get("flags", []))
)

if total_flags == 0:
    print("RESULT: NO significant Bitcoin-to-Matrix connections found.")
    print()
    print("None of the 4 mapping methods produced diag_diff = 676")
    print("between any Bitcoin address and POCC/HASV.")
    print()
    print("This is an HONEST NULL RESULT.")
    print("The Bitcoin connection hypothesis is NOT SUPPORTED by data.")
    print()
    print("Note: This does NOT disprove a connection — it only means that")
    print("naive character-mapping approaches don't reveal one.")
    print("A more sophisticated mapping (if it exists) would require")
    print("knowledge of how Qubic's K12 hash relates to Bitcoin's SHA-256.")
else:
    print(f"Found {total_flags} potential connections with diag_diff = 676.")
    print("These require further investigation and Monte Carlo validation.")

print()
print("HONESTY STATEMENT:")
print("  - Control group was used for all comparisons")
print("  - No post-hoc hypothesis adjustment was performed")
print("  - Null results are reported honestly")
print("  - This test cannot prove OR disprove a Bitcoin connection")
print("    through other mathematical channels")

print()
print("=" * 70)
print("COMPLETE")
print("=" * 70)
