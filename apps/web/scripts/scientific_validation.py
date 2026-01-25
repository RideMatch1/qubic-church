#!/usr/bin/env python3
"""
SCIENTIFIC VALIDATION - Which addresses are mathematically provable?
====================================================================
Separates addresses with mathematical Anna Matrix connection from those without
"""

import json
import os
from collections import defaultdict

script_dir = os.path.dirname(os.path.abspath(__file__))

# Load results
with open(os.path.join(script_dir, 'ULTIMATE_ADDRESS_SEARCH_RESULTS.json'), 'r') as f:
    ultimate = json.load(f)

with open(os.path.join(script_dir, 'EXTENDED_NEW_ADDRESSES.json'), 'r') as f:
    extended = json.load(f)

# Categorize strategies by mathematical rigor
STRONG_MATH = {
    'diagonal',           # matrix[i,i] = ±27 (ORIGINAL CFB criterion)
    'cell_mapping',       # matrix[row,col] ∈ CFB_VALUES
    'anti_diagonal',      # matrix[i, 127-i] ∈ CFB_VALUES
    'anomaly_position',   # Symmetry-breaking positions
    'xor_pattern',        # row XOR col = CFB value
}

MODERATE_MATH = {
    'row_cfb_count',      # Row has 5+ CFB values
    'column_cfb_count',   # Column has 5+ CFB values
    'special_value',      # Position has special value (0, 100, 127, -128)
    'sum_pattern',        # row + col = CFB number
    'self_reference',     # Value equals position
}

WEAK_MATH = {
    'fibonacci',          # Fibonacci position (math, but not matrix-derived)
    'prime_block',        # Prime number block (math, but not matrix-derived)
    'triangular',         # Triangular number block
    'perfect_square',     # Perfect square block
    'power_of_2',         # Power of 2 block
    'palindrome',         # Palindrome block number
    'digit_7',            # Block contains digit 7
}

NO_MATH = {
    'remaining_patoshi',  # Just "all other addresses" - NO mathematical criterion
}

# Count addresses by category
results = {
    'strong_math': {'count': 0, 'addresses': [], 'strategies': defaultdict(int)},
    'moderate_math': {'count': 0, 'addresses': [], 'strategies': defaultdict(int)},
    'weak_math': {'count': 0, 'addresses': [], 'strategies': defaultdict(int)},
    'no_math': {'count': 0, 'addresses': [], 'strategies': defaultdict(int)},
}

# Process ultimate results
for addr, info in ultimate.get('address_details', {}).items():
    strategy = info.get('strategy', 'unknown')
    if strategy in STRONG_MATH:
        results['strong_math']['count'] += 1
        results['strong_math']['addresses'].append(addr)
        results['strong_math']['strategies'][strategy] += 1
    elif strategy in MODERATE_MATH:
        results['moderate_math']['count'] += 1
        results['moderate_math']['addresses'].append(addr)
        results['moderate_math']['strategies'][strategy] += 1
    elif strategy in WEAK_MATH:
        results['weak_math']['count'] += 1
        results['weak_math']['addresses'].append(addr)
        results['weak_math']['strategies'][strategy] += 1
    elif strategy in NO_MATH:
        results['no_math']['count'] += 1
        results['no_math']['addresses'].append(addr)
        results['no_math']['strategies'][strategy] += 1

# Process extended results
for addr, info in extended.get('addresses', {}).items():
    strategy = info.get('strategy', 'unknown')
    if strategy in STRONG_MATH:
        results['strong_math']['count'] += 1
        results['strong_math']['addresses'].append(addr)
        results['strong_math']['strategies'][strategy] += 1
    elif strategy in MODERATE_MATH:
        results['moderate_math']['count'] += 1
        results['moderate_math']['addresses'].append(addr)
        results['moderate_math']['strategies'][strategy] += 1
    elif strategy in WEAK_MATH:
        results['weak_math']['count'] += 1
        results['weak_math']['addresses'].append(addr)
        results['weak_math']['strategies'][strategy] += 1
    elif strategy in NO_MATH:
        results['no_math']['count'] += 1
        results['no_math']['addresses'].append(addr)
        results['no_math']['strategies'][strategy] += 1

# Summary
print("=" * 70)
print("SCIENTIFIC VALIDATION REPORT")
print("=" * 70)
print()

total = sum(r['count'] for r in results.values())

print("MATHEMATICAL RIGOR LEVELS:")
print("-" * 70)
print()

print("1. STRONG MATH (Direct Anna Matrix Value Criterion):")
print(f"   Count: {results['strong_math']['count']:,} ({results['strong_math']['count']/total*100:.1f}%)")
print("   Strategies:")
for s, c in sorted(results['strong_math']['strategies'].items(), key=lambda x: -x[1]):
    print(f"      - {s}: {c:,}")
print()

print("2. MODERATE MATH (Row/Column Patterns):")
print(f"   Count: {results['moderate_math']['count']:,} ({results['moderate_math']['count']/total*100:.1f}%)")
print("   Strategies:")
for s, c in sorted(results['moderate_math']['strategies'].items(), key=lambda x: -x[1]):
    print(f"      - {s}: {c:,}")
print()

print("3. WEAK MATH (Number Theory, Not Matrix-Derived):")
print(f"   Count: {results['weak_math']['count']:,} ({results['weak_math']['count']/total*100:.1f}%)")
print("   Strategies:")
for s, c in sorted(results['weak_math']['strategies'].items(), key=lambda x: -x[1]):
    print(f"      - {s}: {c:,}")
print()

print("4. NO MATH (Just Remaining Addresses):")
print(f"   Count: {results['no_math']['count']:,} ({results['no_math']['count']/total*100:.1f}%)")
print("   Strategies:")
for s, c in sorted(results['no_math']['strategies'].items(), key=lambda x: -x[1]):
    print(f"      - {s}: {c:,}")
print()

print("=" * 70)
print("SUMMARY")
print("=" * 70)

strong_moderate = results['strong_math']['count'] + results['moderate_math']['count']
print(f"\nMATHEMATICALLY PROVABLE (Strong + Moderate):")
print(f"   {strong_moderate:,} addresses ({strong_moderate/total*100:.1f}%)")
print(f"   = {strong_moderate * 50:,} potential BTC")

all_math = strong_moderate + results['weak_math']['count']
print(f"\nALL MATHEMATICAL CRITERIA (incl. Weak):")
print(f"   {all_math:,} addresses ({all_math/total*100:.1f}%)")
print(f"   = {all_math * 50:,} potential BTC")

print(f"\nNOT MATHEMATICALLY DERIVED:")
print(f"   {results['no_math']['count']:,} addresses ({results['no_math']['count']/total*100:.1f}%)")

# Save scientifically validated addresses only
validated_strong = results['strong_math']['addresses']
validated_moderate = results['moderate_math']['addresses']

with open(os.path.join(script_dir, 'VALIDATED_STRONG_MATH_ADDRESSES.txt'), 'w') as f:
    for addr in sorted(validated_strong):
        f.write(f"{addr}\n")

with open(os.path.join(script_dir, 'VALIDATED_MODERATE_MATH_ADDRESSES.txt'), 'w') as f:
    for addr in sorted(validated_moderate):
        f.write(f"{addr}\n")

combined_validated = set(validated_strong + validated_moderate)
with open(os.path.join(script_dir, 'VALIDATED_ALL_MATH_ADDRESSES.txt'), 'w') as f:
    for addr in sorted(combined_validated):
        f.write(f"{addr}\n")

print(f"\nFiles saved:")
print(f"  - VALIDATED_STRONG_MATH_ADDRESSES.txt ({len(validated_strong):,} addresses)")
print(f"  - VALIDATED_MODERATE_MATH_ADDRESSES.txt ({len(validated_moderate):,} addresses)")
print(f"  - VALIDATED_ALL_MATH_ADDRESSES.txt ({len(combined_validated):,} addresses)")

# Save full validation report
report = {
    'total_addresses': total,
    'strong_math': {
        'count': results['strong_math']['count'],
        'percentage': results['strong_math']['count']/total*100,
        'strategies': dict(results['strong_math']['strategies'])
    },
    'moderate_math': {
        'count': results['moderate_math']['count'],
        'percentage': results['moderate_math']['count']/total*100,
        'strategies': dict(results['moderate_math']['strategies'])
    },
    'weak_math': {
        'count': results['weak_math']['count'],
        'percentage': results['weak_math']['count']/total*100,
        'strategies': dict(results['weak_math']['strategies'])
    },
    'no_math': {
        'count': results['no_math']['count'],
        'percentage': results['no_math']['count']/total*100,
        'strategies': dict(results['no_math']['strategies'])
    },
    'summary': {
        'mathematically_provable': strong_moderate,
        'mathematically_provable_pct': strong_moderate/total*100,
        'all_math_criteria': all_math,
        'all_math_criteria_pct': all_math/total*100,
        'not_math_derived': results['no_math']['count'],
        'not_math_derived_pct': results['no_math']['count']/total*100
    }
}

with open(os.path.join(script_dir, 'SCIENTIFIC_VALIDATION_REPORT.json'), 'w') as f:
    json.dump(report, f, indent=2)

print(f"  - SCIENTIFIC_VALIDATION_REPORT.json")
