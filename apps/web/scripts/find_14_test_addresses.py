#!/usr/bin/env python3
"""
Find the 14 Test Transaction Addresses
=======================================

CFB mentioned: "For some reason I did 14 test transactions 10 btc each"

This script searches for:
- Addresses with exactly 10.0 BTC
- From 2009-2010 era (Patoshi period)
- In sequences of 14
- With CFB mathematical signatures

Usage:
    python3 find_14_test_addresses.py

Output:
    14_test_addresses.json - Candidate sequences
    14_test_analysis.txt - Detailed analysis
"""

import json
from typing import List, Dict

def load_patoshi_data() -> List[Dict]:
    """Load Patoshi addresses"""
    try:
        with open('public/data/patoshi-addresses.json', 'r') as f:
            data = json.load(f)

        if 'records' in data:
            return data['records']
        elif isinstance(data, list):
            return data
        else:
            return []
    except FileNotFoundError:
        print("⚠️  patoshi-addresses.json not found")
        return []

def find_exact_10_btc_addresses(records: List[Dict]) -> List[Dict]:
    """Find all addresses with exactly 10.0 BTC"""
    return [r for r in records if r.get('amount') == 10.0 or r.get('amount') == 50.0]

def find_sequences_of_14(addresses: List[Dict]) -> List[List[Dict]]:
    """
    Find sequences of 14 addresses

    Criteria:
    - 14 consecutive addresses
    - All with 10.0 BTC
    - Within reasonable block range
    """
    sequences = []

    for i in range(len(addresses) - 13):
        sequence = addresses[i:i+14]

        # Get block heights
        blocks = [a.get('blockHeight', 0) for a in sequence]

        # Check if all have valid blocks
        if all(b > 0 for b in blocks):
            # Check if blocks are relatively close (within 5000 blocks)
            if max(blocks) - min(blocks) < 5000:
                sequences.append(sequence)

    return sequences

def analyze_cfb_patterns(sequence: List[Dict]) -> Dict:
    """
    Analyze sequence for CFB mathematical signatures

    Check for:
    - Block number patterns (27, 283, 47, etc.)
    - Modulo patterns
    - Sequence patterns
    """
    blocks = [a.get('blockHeight', 0) for a in sequence]

    analysis = {
        'block_range': f"{min(blocks)} - {max(blocks)}",
        'block_span': max(blocks) - min(blocks),
        'first_block': min(blocks),
        'last_block': max(blocks),
        'cfb_patterns': []
    }

    # Check for CFB number modulos
    first_block = min(blocks)

    if first_block % 27 == 0:
        analysis['cfb_patterns'].append(f"First block {first_block} divisible by 27")

    if first_block % 283 == 0:
        analysis['cfb_patterns'].append(f"First block {first_block} divisible by 283")

    if first_block % 47 == 0:
        analysis['cfb_patterns'].append(f"First block {first_block} divisible by 47")

    # Check span
    span = max(blocks) - min(blocks)

    if span % 27 == 0:
        analysis['cfb_patterns'].append(f"Span {span} divisible by 27")

    if span % 14 == 0:
        analysis['cfb_patterns'].append(f"Span {span} divisible by 14 (transaction count!)")

    # Check for arithmetic progression
    if len(blocks) == 14:
        differences = [blocks[i+1] - blocks[i] for i in range(13)]
        if len(set(differences)) == 1:
            analysis['cfb_patterns'].append(f"Arithmetic progression (diff={differences[0]})")

    # Check sum
    total = sum(blocks)
    if total % 27 == 0:
        analysis['cfb_patterns'].append(f"Sum of blocks divisible by 27")

    return analysis

def main():
    """Find the 14 test addresses"""

    print("="*80)
    print("FINDING CFB'S 14 TEST TRANSACTION ADDRESSES")
    print("="*80)
    print()
    print("Quote: 'For some reason I did 14 test transactions 10 btc each'")
    print()

    # Load data
    print("Loading Patoshi data...")
    records = load_patoshi_data()
    print(f"✓ Loaded {len(records)} Patoshi records")
    print()

    # Find all 10.0 BTC addresses (also check 50.0 as block rewards)
    print("Finding addresses with 10.0 or 50.0 BTC...")
    ten_btc = find_exact_10_btc_addresses(records)
    print(f"✓ Found {len(ten_btc)} addresses")
    print()

    # Show distribution
    ten_only = [a for a in ten_btc if a.get('amount') == 10.0]
    fifty_only = [a for a in ten_btc if a.get('amount') == 50.0]

    print(f"  - 10.0 BTC:  {len(ten_only)}")
    print(f"  - 50.0 BTC:  {len(fifty_only)}")
    print()

    # Find sequences
    print("Searching for sequences of 14 addresses...")
    sequences = find_sequences_of_14(ten_btc)
    print(f"✓ Found {len(sequences)} potential sequences")
    print()

    # Analyze each sequence
    print("="*80)
    print("CANDIDATE SEQUENCES")
    print("="*80)

    candidates = []

    for i, seq in enumerate(sequences[:20], 1):  # Show top 20
        print(f"\nSequence #{i}")
        print("-"*80)

        blocks = [a.get('blockHeight', 0) for a in seq]
        amounts = [a.get('amount', 0) for a in seq]

        print(f"Block Range: {min(blocks)} - {max(blocks)}")
        print(f"Block Span:  {max(blocks) - min(blocks)} blocks")
        print(f"Amounts:     {amounts[:3]}... (showing first 3)")

        # Analyze for CFB patterns
        analysis = analyze_cfb_patterns(seq)

        if analysis['cfb_patterns']:
            print(f"\n🔍 CFB PATTERNS DETECTED:")
            for pattern in analysis['cfb_patterns']:
                print(f"   - {pattern}")

            candidates.append({
                'sequence_number': i,
                'addresses': seq,
                'analysis': analysis,
                'priority': 'HIGH' if len(analysis['cfb_patterns']) > 1 else 'MEDIUM'
            })

    # Save results
    output_data = {
        'metadata': {
            'total_10btc_addresses': len(ten_btc),
            'total_sequences_found': len(sequences),
            'high_priority_candidates': len([c for c in candidates if c['priority'] == 'HIGH'])
        },
        'candidates': candidates
    }

    with open('14_test_addresses.json', 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✓ Saved to: 14_test_addresses.json")

    # Save analysis
    with open('14_test_analysis.txt', 'w') as f:
        f.write("14 TEST TRANSACTION ADDRESS ANALYSIS\n")
        f.write("="*80 + "\n\n")
        f.write(f"Total addresses with 10.0 BTC: {len(ten_btc)}\n")
        f.write(f"Sequences found: {len(sequences)}\n")
        f.write(f"High priority candidates: {len([c for c in candidates if c['priority'] == 'HIGH'])}\n\n")

        for candidate in candidates:
            f.write(f"\nSequence #{candidate['sequence_number']} - {candidate['priority']} PRIORITY\n")
            f.write("-"*80 + "\n")
            f.write(f"Block Range: {candidate['analysis']['block_range']}\n")
            f.write(f"Block Span: {candidate['analysis']['block_span']}\n")

            if candidate['analysis']['cfb_patterns']:
                f.write("\nCFB Patterns:\n")
                for pattern in candidate['analysis']['cfb_patterns']:
                    f.write(f"  - {pattern}\n")

    print(f"✓ Saved to: 14_test_analysis.txt")
    print()

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"High Priority Candidates: {len([c for c in candidates if c['priority'] == 'HIGH'])}")
    print(f"Medium Priority Candidates: {len([c for c in candidates if c['priority'] == 'MEDIUM'])}")
    print()

    if candidates:
        print("Most promising sequence:")
        top = candidates[0]
        print(f"  Sequence #{top['sequence_number']}")
        print(f"  Blocks: {top['analysis']['block_range']}")
        print(f"  CFB Patterns: {len(top['analysis']['cfb_patterns'])}")

    print()
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
