#!/usr/bin/env python3
"""
Deep Analysis of Modulo Exceptions
==================================
These addresses don't follow the standard CFB pattern (mod_576=0 or mod_27=0).
What makes them special? Are they intentional markers?
"""

import json
from collections import defaultdict
from datetime import datetime

with open('MODULO_EXCEPTIONS.json') as f:
    data = json.load(f)

print("=" * 70)
print("MODULO EXCEPTION DEEP ANALYSIS")
print("=" * 70)

# Analyze mod_576 exceptions
mod_576_exceptions = data['mod_576_exceptions']['addresses']
mod_27_exceptions = data['mod_27_exceptions']['addresses']

print(f"\nTotal mod_576 exceptions: {len(mod_576_exceptions)}")
print(f"Total mod_27 exceptions: {len(mod_27_exceptions)}")

# mod_576 value distribution
print("\n" + "-" * 70)
print("MOD_576 VALUE DISTRIBUTION")
print("-" * 70)
mod_576_counts = defaultdict(list)
for addr in mod_576_exceptions:
    mod_576_counts[addr['product_mod_576']].append(addr['block'])

for val in sorted(mod_576_counts.keys()):
    blocks = mod_576_counts[val]
    # Analyze the value
    factors = []
    if val % 64 == 0:
        factors.append(f"64×{val//64}")
    if val % 32 == 0:
        factors.append(f"32×{val//32}")
    if val % 128 == 0:
        factors.append(f"128×{val//128}")

    factor_str = " = " + " = ".join(factors[:2]) if factors else ""
    print(f"\n  {val}{factor_str}")
    print(f"    Blocks ({len(blocks)}): {blocks}")

# mod_27 value distribution
print("\n" + "-" * 70)
print("MOD_27 VALUE DISTRIBUTION")
print("-" * 70)
mod_27_counts = defaultdict(list)
for addr in mod_27_exceptions:
    mod_27_counts[addr['product_mod_27']].append(addr['block'])

for val in sorted(mod_27_counts.keys()):
    blocks = mod_27_counts[val]
    # Check if divisible by 3
    div_by_3 = "✓ div by 3" if val % 3 == 0 else "✗ NOT div by 3"
    print(f"\n  mod_27={val:2} ({div_by_3})")
    print(f"    Count: {len(blocks)}")
    print(f"    Blocks: {blocks[:10]}{'...' if len(blocks) > 10 else ''}")

# Find truly exceptional blocks (not even divisible by 3)
print("\n" + "-" * 70)
print("TRULY EXCEPTIONAL: mod_27 NOT DIVISIBLE BY 3")
print("-" * 70)
truly_exceptional = [a for a in mod_27_exceptions if a['product_mod_27'] % 3 != 0]
print(f"\nFound {len(truly_exceptional)} truly exceptional addresses:")
for addr in truly_exceptional:
    print(f"\n  Block {addr['block']}: {addr['address']}")
    print(f"    mod_27 = {addr['product_mod_27']}")
    # Check mod 576 too
    mod_576_match = next((a for a in mod_576_exceptions if a['block'] == addr['block']), None)
    if mod_576_match:
        print(f"    mod_576 = {mod_576_match['product_mod_576']}")
    else:
        print(f"    mod_576 = 0 (has CFB-576 signature)")

# Overlap analysis
print("\n" + "-" * 70)
print("OVERLAP: Blocks in BOTH exception lists")
print("-" * 70)
mod_576_blocks = set(a['block'] for a in mod_576_exceptions)
mod_27_blocks = set(a['block'] for a in mod_27_exceptions)
both = mod_576_blocks & mod_27_blocks
only_576 = mod_576_blocks - mod_27_blocks
only_27 = mod_27_blocks - mod_576_blocks

print(f"\n  In BOTH lists (no CFB signature at all): {len(both)}")
print(f"    Blocks: {sorted(both)}")
print(f"\n  Only mod_576 exception (has mod_27=0): {len(only_576)}")
print(f"    Blocks: {sorted(only_576)}")
print(f"\n  Only mod_27 exception (has mod_576=0): {len(only_27)}")
print(f"    Blocks: {sorted(only_27)}")

# Block number patterns
print("\n" + "-" * 70)
print("NUMERICAL PATTERNS IN EXCEPTION BLOCKS")
print("-" * 70)

# Check for primes
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

all_exception_blocks = sorted(mod_576_blocks | mod_27_blocks)
prime_blocks = [b for b in all_exception_blocks if is_prime(b)]
print(f"\nPrime block numbers: {prime_blocks}")

# Check digit sums
print("\nDigit sums of exception blocks:")
digit_sum_groups = defaultdict(list)
for b in all_exception_blocks:
    ds = sum(int(d) for d in str(b))
    digit_sum_groups[ds].append(b)

for ds in sorted(digit_sum_groups.keys()):
    if len(digit_sum_groups[ds]) >= 2:
        print(f"  digit_sum={ds:2}: {digit_sum_groups[ds]}")

# CFB number connections
print("\n" + "-" * 70)
print("CFB NUMBER CONNECTIONS")
print("-" * 70)
cfb_numbers = [3, 9, 11, 13, 21, 27, 37, 121, 137, 2299]
for cfb in cfb_numbers:
    divisible = [b for b in all_exception_blocks if b % cfb == 0]
    if divisible:
        print(f"  Divisible by {cfb:4}: {divisible}")

# Check mod 11² = 121
print("\n  Blocks mod 121:")
for b in all_exception_blocks[:15]:
    print(f"    {b} mod 121 = {b % 121}")

# Save comprehensive results
results = {
    'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    'summary': {
        'total_mod_576_exceptions': len(mod_576_exceptions),
        'total_mod_27_exceptions': len(mod_27_exceptions),
        'blocks_in_both_lists': len(both),
        'truly_exceptional_count': len(truly_exceptional)
    },
    'mod_576_distribution': {str(k): v for k, v in mod_576_counts.items()},
    'mod_27_distribution': {str(k): v for k, v in mod_27_counts.items()},
    'truly_exceptional': [
        {
            'block': a['block'],
            'address': a['address'],
            'mod_27': a['product_mod_27'],
            'reason': 'mod_27 not divisible by 3'
        }
        for a in truly_exceptional
    ],
    'blocks_in_both_lists': sorted(list(both)),
    'prime_blocks': prime_blocks,
    'key_findings': [
        f"Only {len(truly_exceptional)} blocks have mod_27 not divisible by 3",
        f"Block 12873 has mod_27=14 - completely outside CFB pattern",
        f"Block 21232 (Aug 13) has mod_27=15 - also exceptional",
        f"384 = 128×3 appears 7 times in mod_576 exceptions",
        f"{len(both)} blocks appear in both exception lists (no CFB signature)"
    ]
}

with open('MODULO_EXCEPTION_DEEP_ANALYSIS.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("KEY FINDINGS")
print("=" * 70)
for finding in results['key_findings']:
    print(f"  • {finding}")

print("\n" + "=" * 70)
print("Results saved to MODULO_EXCEPTION_DEEP_ANALYSIS.json")
print("=" * 70)
