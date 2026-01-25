#!/usr/bin/env python3
"""
Search for Special Qubic Seeds
================================

Looks for seeds that might indicate a "finder's reward":
- Keywords: reward, finder, prize, genesis, satoshi
- Special patterns
- CFB signatures

Usage:
    python3 search_special_seeds.py
"""

import json
import hashlib

def search_special_seeds():
    """Search for special seeds in database"""

    print("="*80)
    print("SEARCHING FOR FINDER'S REWARD SEEDS")
    print("="*80)
    print()

    # Load seeds
    try:
        with open('public/data/qubic-seeds.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("⚠️  qubic-seeds.json not found")
        return

    seeds = data if isinstance(data, list) else data.get('records', [])

    print(f"Searching {len(seeds)} Qubic seeds...")
    print()

    # Keywords to search for
    reward_keywords = [
        'reward', 'finder', 'prize', 'bounty', 'treasure',
        'genesis', 'genesi', 'satoshi', 'cfb',
        'first', 'discoverer', 'winner', 'unlock',
        'secret', 'hidden', 'special'
    ]

    matches = []

    for i, seed_data in enumerate(seeds):
        if isinstance(seed_data, str):
            seed = seed_data
            identity = f"Seed_{i}"
        else:
            seed = seed_data.get('seed', '')
            identity = seed_data.get('documentedIdentity',
                                   seed_data.get('identity',
                                   seed_data.get('name', f"Seed_{i}")))

        # Search in identity
        identity_lower = identity.lower()

        for keyword in reward_keywords:
            if keyword in identity_lower:
                matches.append({
                    'type': 'keyword_match',
                    'keyword': keyword,
                    'seed': seed,
                    'identity': identity,
                    'index': i
                })
                break

    # Print results
    print("="*80)
    print("KEYWORD MATCHES")
    print("="*80)
    print()

    if matches:
        for match in matches:
            print(f"✓ FOUND: {match['keyword'].upper()}")
            print(f"  Identity: {match['identity']}")
            print(f"  Seed: {match['seed']}")
            print(f"  Index: {match['index']}")
            print()
    else:
        print("No keyword matches found")
        print()

    # Search for special patterns
    print("="*80)
    print("SPECIAL PATTERN SEARCH")
    print("="*80)
    print()

    special_patterns = []

    for i, seed_data in enumerate(seeds[:100]):  # Check first 100
        if isinstance(seed_data, str):
            seed = seed_data
        else:
            seed = seed_data.get('seed', '')

        if not seed:
            continue

        # Pattern 1: Repeating characters
        if any(char * 5 in seed for char in 'abcdefghijklmnopqrstuvwxyz'):
            special_patterns.append({
                'type': 'repeating',
                'seed': seed,
                'index': i
            })

        # Pattern 2: Alphabetical sequence
        if 'abcdef' in seed or 'zyxwvu' in seed:
            special_patterns.append({
                'type': 'alphabetical',
                'seed': seed,
                'index': i
            })

    if special_patterns:
        for pattern in special_patterns[:10]:
            print(f"✓ {pattern['type'].upper()} PATTERN")
            print(f"  Seed: {pattern['seed']}")
            print(f"  Index: {pattern['index']}")
            print()
    else:
        print("No special patterns found in first 100 seeds")
        print()

    # Search for CFB number seeds
    print("="*80)
    print("CFB NUMBER SEEDS")
    print("="*80)
    print()

    cfb_numbers = [27, 283, 47, 137, 121, 43, 19, 7, 14]

    for num in cfb_numbers:
        # Derive seed from CFB number
        num_hash = hashlib.sha256(str(num).encode()).digest()
        num_seed = ''.join(chr(ord('a') + (byte % 26)) for byte in num_hash[:28])

        # Check if this seed exists in our database
        for i, seed_data in enumerate(seeds):
            if isinstance(seed_data, str):
                seed = seed_data
                identity = f"Seed_{i}"
            else:
                seed = seed_data.get('seed', '')
                identity = seed_data.get('documentedIdentity', f"Seed_{i}")

            if seed == num_seed:
                print(f"✓ CFB NUMBER {num} SEED FOUND!")
                print(f"  Seed: {seed}")
                print(f"  Identity: {identity}")
                print(f"  Index: {i}")
                print()

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total seeds searched: {len(seeds)}")
    print(f"Keyword matches: {len(matches)}")
    print(f"Special patterns: {len(special_patterns)}")
    print()

    if matches or special_patterns:
        print("✓ POTENTIAL REWARD SEEDS FOUND!")
        print()
        print("Next steps:")
        print("1. Investigate each match manually")
        print("2. Try deriving Bitcoin addresses from these seeds")
        print("3. Check if addresses have balance or special properties")
    else:
        print("⚠️  No obvious reward seeds found")
        print()
        print("Reward might be hidden in:")
        print("- QubicTrade Genesi token")
        print("- Source code")
        print("- Mathematical puzzles")

    # Save results
    with open('special_seeds_results.json', 'w') as f:
        json.dump({
            'keyword_matches': matches,
            'special_patterns': special_patterns,
            'total_searched': len(seeds)
        }, f, indent=2)

    print()
    print("✓ Results saved to: special_seeds_results.json")

if __name__ == "__main__":
    search_special_seeds()
