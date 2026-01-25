#!/usr/bin/env python3
"""
ANALYZE THE SEEDS THAT GENERATE 0x7b + 2299 ADDRESSES

We have 4 seeds that generate addresses with first byte 0x7b:
- Seed ID 1928, 7655, 8462, 13495

Let's analyze them for patterns!
"""

import json
from collections import Counter

def analyze_seed(seed):
    """Analyze a single seed"""
    return {
        'seed': seed,
        'length': len(seed),
        'unique_chars': len(set(seed)),
        'char_freq': Counter(seed),
        'repeating_pattern': detect_repeating_pattern(seed),
        'char_positions': {c: [i for i, ch in enumerate(seed) if ch == c] for c in set(seed)}
    }

def detect_repeating_pattern(seed):
    """Detect if seed has a repeating pattern"""
    length = len(seed)

    # Try different pattern lengths
    for pattern_len in [13, 14, 15, 11, 12, 16]:
        if length % pattern_len == 0 or length % pattern_len < 5:
            # Extract potential pattern
            pattern = seed[:pattern_len]
            # Check if it repeats
            reconstructed = (pattern * (length // pattern_len + 1))[:length]
            if reconstructed == seed:
                return {
                    'has_pattern': True,
                    'pattern': pattern,
                    'pattern_length': pattern_len,
                    'repetitions': length // pattern_len
                }

    return {'has_pattern': False}

print("=" * 80)
print("ANALYZING SEEDS THAT GENERATE 0x7b + 2299 ADDRESSES")
print("=" * 80)
print()

# Load all seeds
with open('../public/data/qubic-seeds.json', 'r') as f:
    seeds_data = json.load(f)
    all_seeds = seeds_data['records']

# The 4 known seed IDs
seed_ids = [1928, 7655, 8462, 13495]

seed_analyses = []

for seed_id in seed_ids:
    seed_rec = all_seeds[seed_id]
    seed = seed_rec['seed']

    print(f"Seed ID: {seed_id}")
    print(f"Seed: {seed}")

    analysis = analyze_seed(seed)

    print(f"  Length: {analysis['length']}")
    print(f"  Unique chars: {analysis['unique_chars']}")
    print(f"  Char frequency: {dict(analysis['char_freq'].most_common())}")

    if analysis['repeating_pattern']['has_pattern']:
        print(f"  ✓ REPEATING PATTERN DETECTED!")
        print(f"    Pattern: {analysis['repeating_pattern']['pattern']}")
        print(f"    Length: {analysis['repeating_pattern']['pattern_length']}")
        print(f"    Repetitions: {analysis['repeating_pattern']['repetitions']}")
    else:
        print(f"  No obvious repeating pattern")

    print()

    seed_analyses.append({
        'seed_id': seed_id,
        'seed': seed,
        'analysis': analysis
    })

# Cross-analysis
print("=" * 80)
print("CROSS-SEED ANALYSIS")
print("=" * 80)
print()

all_chars = set()
for sa in seed_analyses:
    all_chars.update(sa['seed'])

print(f"Total unique characters across all seeds: {len(all_chars)}")
print(f"Characters: {sorted(all_chars)}")
print()

# Common patterns
print("COMMON CHARACTERISTICS:")
lengths = [sa['analysis']['length'] for sa in seed_analyses]
unique_counts = [sa['analysis']['unique_chars'] for sa in seed_analyses]

print(f"  Seed lengths: {lengths} (all same: {len(set(lengths)) == 1})")
print(f"  Unique char counts: {unique_counts}")
print()

# Check for common substrings
print("CHECKING FOR COMMON SUBSTRINGS:")
seed_strings = [sa['seed'] for sa in seed_analyses]

for length in [5, 6, 7, 8, 9, 10]:
    common_subs = set()
    for seed in seed_strings:
        for i in range(len(seed) - length + 1):
            substring = seed[i:i+length]
            # Check if this substring appears in ALL seeds
            if all(substring in s for s in seed_strings):
                common_subs.add(substring)

    if common_subs:
        print(f"  Length {length}: {len(common_subs)} common substrings")
        if len(common_subs) <= 5:
            for sub in sorted(common_subs):
                print(f"    - {sub}")
print()

# Save results
output = {
    'seed_count': len(seed_analyses),
    'seeds': seed_analyses,
    'cross_analysis': {
        'all_unique_chars': sorted(list(all_chars)),
        'total_unique_chars': len(all_chars),
        'seed_lengths': lengths,
        'unique_char_counts': unique_counts
    }
}

with open('0x7b_SEED_ANALYSIS.json', 'w') as f:
    json.dump(output, f, indent=2)

print("=" * 80)
print("Results saved to: 0x7b_SEED_ANALYSIS.json")
print("=" * 80)
