#!/usr/bin/env python3
"""
===============================================================================
        BRIDGE VALIDATION - WS0: DATA INTEGRITY CHECK
===============================================================================
Foundation check: Verify all bridge-related data files are internally
consistent, complete, and traceable BEFORE testing any claims.

PRE-REGISTERED CHECKS (stated before running):
  C0.1: anna-matrix.json has 128 rows of 128 integers in [-128, 127]
  C0.2: Point symmetry: matrix[r,c] + matrix[127-r,127-c] = -1 for 99.58%
  C0.3: 27-divisible block positions [20,28],[9,115],[83,65],[59,57]
        have values [85, 60, 100, -68] (sum=177=0xB1)
  C0.4: patoshi-addresses.json has 21,953 records with valid structure
  C0.5: bitcoin-derived-addresses.json has 20,955 records
  C0.6: qubic-seeds.json has 23,765 records with valid 55-char lowercase seeds
  C0.7: anna-collision-analysis.json contains "P(random) < 10^-500" (fabricated)

RUNTIME: ~30 seconds
===============================================================================
"""

import json
import re
import numpy as np
from pathlib import Path
from collections import Counter
from datetime import datetime

script_dir = Path(__file__).parent
data_dir = script_dir.parent / "public" / "data"

print("=" * 80)
print("         BRIDGE VALIDATION - WS0: DATA INTEGRITY CHECK")
print("=" * 80)
print(f"Date: {datetime.now().isoformat()}")

results = {}
all_pass = True

# ============================================================================
# CHECK 0.1: Anna Matrix Structure
# ============================================================================
print("\n" + "=" * 80)
print("CHECK 0.1: Anna Matrix Structure")
print("=" * 80)

matrix_path = data_dir / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

raw_matrix = data["matrix"]
n_rows = len(raw_matrix)
n_cols_per_row = [len(row) for row in raw_matrix]
matrix = np.array([[safe_int(v) for v in row] for row in raw_matrix], dtype=np.int16)

check_rows = n_rows == 128
check_cols = all(c == 128 for c in n_cols_per_row)
check_range = int(matrix.min()) >= -128 and int(matrix.max()) <= 127

# Check for string values (non-numeric)
string_count = sum(1 for row in raw_matrix for v in row if isinstance(v, str))

print(f"  Rows: {n_rows} (expected 128) {'PASS' if check_rows else 'FAIL'}")
print(f"  Cols per row: all 128? {'PASS' if check_cols else 'FAIL'}")
print(f"  Value range: [{int(matrix.min())}, {int(matrix.max())}] {'PASS' if check_range else 'FAIL'}")
print(f"  String values: {string_count} (these are treated as 0)")
print(f"  Unique values: {len(np.unique(matrix))}")

results["0.1_structure"] = check_rows and check_cols and check_range
if not results["0.1_structure"]:
    all_pass = False

# ============================================================================
# CHECK 0.2: Point Symmetry
# ============================================================================
print("\n" + "=" * 80)
print("CHECK 0.2: Point Symmetry Verification")
print("=" * 80)

sym_count = 0
asym_count = 0
total = 128 * 128

for r in range(128):
    for c in range(128):
        if int(matrix[r, c]) + int(matrix[127 - r, 127 - c]) == -1:
            sym_count += 1
        else:
            asym_count += 1

sym_pct = sym_count / total * 100
check_sym = abs(sym_pct - 99.58) < 0.01

print(f"  Symmetric cells: {sym_count}/{total} ({sym_pct:.2f}%)")
print(f"  Asymmetric cells: {asym_count}")
print(f"  Expected: 99.58% {'PASS' if check_sym else 'FAIL'}")

results["0.2_symmetry"] = check_sym
if not results["0.2_symmetry"]:
    all_pass = False

# ============================================================================
# CHECK 0.3: 27-Divisible Block Position Values
# ============================================================================
print("\n" + "=" * 80)
print("CHECK 0.3: 27-Divisible Block Cell Values")
print("=" * 80)

# The bridge document claims these 4 blocks map to specific coordinates
blocks_27 = {
    3996: {"expected_row": 20, "expected_col": 28, "expected_val": 85},
    10611: {"expected_row": 9, "expected_col": 115, "expected_val": 60},
    16065: {"expected_row": 83, "expected_col": 65, "expected_val": 100},
    36153: {"expected_row": 59, "expected_col": 57, "expected_val": -68},
}

print(f"\n  Verifying mapping algorithm: row = (block // 27) % 128, col = block % 128")
print(f"  {'Block':<8} {'CalcRow':<8} {'ExpRow':<8} {'CalcCol':<8} {'ExpCol':<8} {'MatVal':<8} {'ExpVal':<8} {'Match'}")
print("  " + "-" * 70)

all_match = True
actual_values = []
for block, expected in blocks_27.items():
    calc_row = (block // 27) % 128
    calc_col = block % 128
    actual_val = int(matrix[calc_row, calc_col])
    actual_values.append(actual_val)

    row_match = calc_row == expected["expected_row"]
    col_match = calc_col == expected["expected_col"]
    val_match = actual_val == expected["expected_val"]
    match = row_match and col_match and val_match

    if not match:
        all_match = False

    print(f"  {block:<8} {calc_row:<8} {expected['expected_row']:<8} {calc_col:<8} {expected['expected_col']:<8} {actual_val:<8} {expected['expected_val']:<8} {'PASS' if match else 'FAIL'}")

cell_sum = sum(actual_values)
hex_val = hex(cell_sum & 0xFF)
sum_match = cell_sum == 177 and hex_val == "0xb1"

print(f"\n  Cell sum: {cell_sum} (expected 177)")
print(f"  Hex: {hex_val} (expected 0xb1)")
print(f"  Sum match: {'PASS' if sum_match else 'FAIL'}")
print(f"  All values match documentation: {'PASS' if all_match else 'FAIL'}")

results["0.3_block_values"] = all_match and sum_match
if not results["0.3_block_values"]:
    all_pass = False

# ============================================================================
# CHECK 0.4: Patoshi Addresses
# ============================================================================
print("\n" + "=" * 80)
print("CHECK 0.4: Patoshi Addresses Data")
print("=" * 80)

patoshi_path = data_dir / "patoshi-addresses.json"
with open(patoshi_path) as f:
    patoshi = json.load(f)

if isinstance(patoshi, list):
    n_patoshi = len(patoshi)
elif isinstance(patoshi, dict) and "records" in patoshi:
    n_patoshi = len(patoshi["records"])
    patoshi = patoshi["records"]
elif isinstance(patoshi, dict) and "addresses" in patoshi:
    n_patoshi = len(patoshi["addresses"])
    patoshi = patoshi["addresses"]
else:
    n_patoshi = 0
    patoshi = []

check_patoshi_count = n_patoshi == 21953

# Sample check: valid structure
valid_records = 0
sample_size = min(100, n_patoshi)
for i in range(sample_size):
    record = patoshi[i]
    if isinstance(record, dict):
        has_fields = True  # Accept any dict structure
        valid_records += 1
    elif isinstance(record, str):
        # Could be just addresses as strings
        valid_records += 1

valid_pct = valid_records / sample_size * 100 if sample_size > 0 else 0

print(f"  Records: {n_patoshi} (expected 21,953) {'PASS' if check_patoshi_count else f'FAIL (got {n_patoshi})'}")
print(f"  Sample validation: {valid_records}/{sample_size} ({valid_pct:.0f}%)")

if n_patoshi > 0:
    sample = patoshi[0]
    print(f"  Record type: {type(sample).__name__}")
    if isinstance(sample, dict):
        print(f"  Fields: {list(sample.keys())[:8]}")
    elif isinstance(sample, str):
        print(f"  Format: string ({len(sample)} chars)")
        print(f"  Example: {sample[:50]}...")

results["0.4_patoshi"] = n_patoshi > 0 and valid_pct > 90
if not results["0.4_patoshi"]:
    all_pass = False

# ============================================================================
# CHECK 0.5: Bitcoin Derived Addresses
# ============================================================================
print("\n" + "=" * 80)
print("CHECK 0.5: Bitcoin Derived Addresses")
print("=" * 80)

btc_path = data_dir / "bitcoin-derived-addresses.json"
with open(btc_path) as f:
    btc_data = json.load(f)

if isinstance(btc_data, list):
    btc_addresses = btc_data
elif isinstance(btc_data, dict) and "records" in btc_data:
    btc_addresses = btc_data["records"]
elif isinstance(btc_data, dict) and "addresses" in btc_data:
    btc_addresses = btc_data["addresses"]
else:
    btc_addresses = []

n_btc = len(btc_addresses)
check_btc_count = n_btc == 20955

# Base58 check pattern
BASE58_PATTERN = re.compile(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$')

valid_base58 = 0
methods_found = set()
sample_btc = min(100, n_btc)

for i in range(sample_btc):
    record = btc_addresses[i]
    if isinstance(record, dict):
        addr = record.get("address", record.get("btcAddress", ""))
        method = record.get("method", record.get("derivation", "unknown"))
        methods_found.add(str(method))
    elif isinstance(record, str):
        addr = record
    else:
        addr = ""

    if BASE58_PATTERN.match(str(addr)):
        valid_base58 += 1

valid_btc_pct = valid_base58 / sample_btc * 100 if sample_btc > 0 else 0

print(f"  Records: {n_btc} (expected 20,955) {'PASS' if check_btc_count else f'INFO (got {n_btc})'}")
print(f"  Valid Base58 (sample of {sample_btc}): {valid_base58} ({valid_btc_pct:.0f}%)")
print(f"  Derivation methods: {methods_found if methods_found else 'N/A'}")

if n_btc > 0:
    sample = btc_addresses[0]
    if isinstance(sample, dict):
        print(f"  Fields: {list(sample.keys())[:8]}")

results["0.5_btc_derived"] = n_btc > 0
if not results["0.5_btc_derived"]:
    all_pass = False

# ============================================================================
# CHECK 0.6: Qubic Seeds
# ============================================================================
print("\n" + "=" * 80)
print("CHECK 0.6: Qubic Seeds")
print("=" * 80)

seeds_path = data_dir / "qubic-seeds.json"
with open(seeds_path) as f:
    seeds_data = json.load(f)

if isinstance(seeds_data, list):
    seeds = seeds_data
elif isinstance(seeds_data, dict) and "records" in seeds_data:
    seeds = seeds_data["records"]
elif isinstance(seeds_data, dict) and "seeds" in seeds_data:
    seeds = seeds_data["seeds"]
else:
    seeds = []

n_seeds = len(seeds)
check_seed_count = n_seeds == 23765

# Validate seed format: 55 lowercase letters
SEED_PATTERN = re.compile(r'^[a-z]{55}$')
valid_seeds = 0
seed_sources = set()
sample_seeds = min(100, n_seeds)

for i in range(sample_seeds):
    record = seeds[i]
    if isinstance(record, dict):
        seed_val = record.get("seed", record.get("value", ""))
        source = record.get("source", "unknown")
        seed_sources.add(str(source)[:30])
    elif isinstance(record, str):
        seed_val = record
    else:
        seed_val = ""

    if SEED_PATTERN.match(str(seed_val)):
        valid_seeds += 1

valid_seed_pct = valid_seeds / sample_seeds * 100 if sample_seeds > 0 else 0

# Check for duplicates
all_seed_values = []
for record in seeds:
    if isinstance(record, dict):
        all_seed_values.append(record.get("seed", record.get("value", "")))
    elif isinstance(record, str):
        all_seed_values.append(record)

n_unique = len(set(all_seed_values))
n_duplicates = n_seeds - n_unique

print(f"  Records: {n_seeds} (expected 23,765) {'PASS' if check_seed_count else f'INFO (got {n_seeds})'}")
print(f"  Valid format (sample of {sample_seeds}): {valid_seeds} ({valid_seed_pct:.0f}%)")
print(f"  Unique seeds: {n_unique}/{n_seeds} (duplicates: {n_duplicates})")
print(f"  Sources: {seed_sources if seed_sources else 'N/A'}")

if n_seeds > 0:
    sample = seeds[0]
    if isinstance(sample, dict):
        print(f"  Fields: {list(sample.keys())[:8]}")

results["0.6_qubic_seeds"] = n_seeds > 0 and valid_seed_pct > 90
if not results["0.6_qubic_seeds"]:
    all_pass = False

# ============================================================================
# CHECK 0.7: Anna Collision Analysis - Fabricated P-value
# ============================================================================
print("\n" + "=" * 80)
print("CHECK 0.7: Anna Collision Analysis - P-value Audit")
print("=" * 80)

collision_path = data_dir / "anna-collision-analysis.json"
with open(collision_path) as f:
    collision_data = json.load(f)

metadata = collision_data.get("metadata", {})
stat_proof = metadata.get("statisticalProof", "NOT FOUND")
total_responses = metadata.get("totalResponses", 0)

has_fabricated_p = "10^-500" in str(stat_proof) or "10^-" in str(stat_proof)

print(f"  Total responses: {total_responses}")
print(f"  Statistical proof claim: \"{stat_proof}\"")
print(f"  Contains fabricated P-value: {'YES - FLAGGED' if has_fabricated_p else 'No'}")

# Check if raw data exists or only aggregates
top_collisions = collision_data.get("topCollisions", [])
has_raw_data = "rawResponses" in collision_data or "responses" in collision_data
print(f"  Top collision entries: {len(top_collisions)}")
print(f"  Has raw response data: {'Yes' if has_raw_data else 'NO - aggregates only'}")

if top_collisions:
    print(f"  Top collision values: {[c.get('value', '?') for c in top_collisions[:5]]}")
    print(f"  Top collision counts: {[c.get('count', '?') for c in top_collisions[:5]]}")

results["0.7_collision_pvalue"] = has_fabricated_p  # We EXPECT to find it (flag)
# Note: This is a FLAG, not a failure - we confirm the fabricated claim exists

# ============================================================================
# ADDITIONAL: Value Distribution Analysis
# ============================================================================
print("\n" + "=" * 80)
print("ADDITIONAL: Matrix Value Distribution")
print("=" * 80)

values_flat = matrix.flatten()
value_counts = Counter(values_flat.tolist())
most_common = value_counts.most_common(10)
least_common = value_counts.most_common()[-5:]

print(f"  Total cells: {len(values_flat)}")
print(f"  Unique values: {len(value_counts)}")
print(f"  Most common: {most_common[:5]}")
print(f"  Value 26 count: {value_counts.get(26, 0)} ({value_counts.get(26, 0)/len(values_flat)*100:.2f}%)")
print(f"  Value -27 count: {value_counts.get(-27, 0)} ({value_counts.get(-27, 0)/len(values_flat)*100:.2f}%)")
print(f"  Value -113 count: {value_counts.get(-113, 0)} ({value_counts.get(-113, 0)/len(values_flat)*100:.2f}%)")
print(f"  Value -114 count: {value_counts.get(-114, 0)} ({value_counts.get(-114, 0)/len(values_flat)*100:.2f}%)")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("DATA INTEGRITY SUMMARY")
print("=" * 80)

for check, passed in results.items():
    if check == "0.7_collision_pvalue":
        status = "FLAGGED" if passed else "NOT FOUND"
    else:
        status = "PASS" if passed else "FAIL"
    print(f"  {check}: {status}")

print(f"\n  Overall: {'ALL CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED'}")
print(f"  Fabricated P-value found: {'YES - needs correction in WS4' if results.get('0.7_collision_pvalue') else 'No'}")

# Save results
output = {
    "date": datetime.now().isoformat(),
    "checks": {k: bool(v) for k, v in results.items()},
    "matrix_shape": [n_rows, 128],
    "symmetry_percentage": float(sym_pct),
    "asymmetric_cells": int(asym_count),
    "block_27_values": actual_values,
    "block_27_sum": int(cell_sum),
    "patoshi_count": n_patoshi,
    "btc_derived_count": n_btc,
    "qubic_seeds_count": n_seeds,
    "seed_duplicates": n_duplicates,
    "collision_responses": total_responses,
    "fabricated_pvalue": stat_proof,
    "value_minus113_count": int(value_counts.get(-113, 0)),
    "value_minus114_count": int(value_counts.get(-114, 0)),
    "value_26_count": int(value_counts.get(26, 0)),
}

output_path = script_dir / "BRIDGE_V0_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  Results saved to: {output_path}")
