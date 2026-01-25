#!/usr/bin/env python3
"""
Analyze Anti-Pattern Blocks
============================

These 12 blocks have NEITHER mod_576=0 NOR mod_27=0.
They are completely outside the CFB mathematical pattern.
Are they intentional markers? Errors? Or something else?
"""

import json
import requests
from pathlib import Path
from datetime import datetime

# The 12 anti-pattern addresses (both mod_576≠0 AND mod_27≠0)
ANTI_PATTERN_BLOCKS = [
    {"address": "16V6Emoj1w2uHVnx58urHk7Sr2w4wH1GGG", "block": 1115, "mod_576": 384, "mod_27": 6},
    {"address": "1AhLXbqriGBG39YU7EqXeEuKGGA72QUG2w", "block": 2720, "mod_576": 384, "mod_27": 24},
    {"address": "17LnUaS2doAoXXXVSPoMLaBqPwkRb3Lt76", "block": 5057, "mod_576": 384, "mod_27": 24},
    {"address": "1LBNt5kaH4aobYdu1DNSxf5Xrujdi67ESE", "block": 5279, "mod_576": 384, "mod_27": 24},
    {"address": "1Gr1kH2y3Vn1jHk6N7oDqH9hXa3wrhwetP", "block": 11221, "mod_576": 384, "mod_27": 24},
    {"address": "13rXzet49NogKrVGUizGqa3e1PYUBk5jLQ", "block": 12778, "mod_576": 384, "mod_27": 24},
    {"address": "1Loo8Lw74rtdRA6PqRho8nq86SrNSDg99L", "block": 12873, "mod_576": 320, "mod_27": 14},
    {"address": "1LhioiU3KXdowARGt1rjwA1ryx8bE6r6xi", "block": 13752, "mod_576": 192, "mod_27": 3},
    {"address": "1LueD1Viqkc1xDx7HV46Xj3nxUDDXXDA6q", "block": 19214, "mod_576": 192, "mod_27": 3},
    {"address": "1HhahkS9KhYMwbgrqq8BPUzrqXnHuAh4n5", "block": 21232, "mod_576": 384, "mod_27": 15},
    {"address": "1Nqjoktnuw23o2PKqWrzBdNUUGGk1L8qY", "block": 22574, "mod_576": 192, "mod_27": 12},
    {"address": "161b3V8XUaiRYYibidnHEGP5S3dP7RZGjb", "block": 40252, "mod_576": 192, "mod_27": 12},
]

def get_block_info(block_height):
    """Get block info from blockchain.info API."""
    try:
        url = f"https://blockchain.info/block-height/{block_height}?format=json"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('blocks') and len(data['blocks']) > 0:
                block = data['blocks'][0]
                return {
                    "hash": block.get('hash', ''),
                    "time": block.get('time', 0),
                    "date": datetime.utcfromtimestamp(block.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S') if block.get('time') else 'Unknown',
                    "n_tx": block.get('n_tx', 0),
                    "size": block.get('size', 0)
                }
    except Exception as e:
        print(f"  Error fetching block {block_height}: {e}")
    return None

def get_address_info(address):
    """Get address info from blockchain.info API."""
    try:
        url = f"https://blockchain.info/rawaddr/{address}?limit=0"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return {
                "n_tx": data.get('n_tx', 0),
                "total_received": data.get('total_received', 0) / 100000000,
                "total_sent": data.get('total_sent', 0) / 100000000,
                "final_balance": data.get('final_balance', 0) / 100000000
            }
    except Exception as e:
        print(f"  Error fetching address {address}: {e}")
    return None

def analyze_matrix_position(block_height):
    """Calculate matrix position from block height."""
    layer = block_height // 16384
    remainder = block_height % 16384
    row = remainder // 128
    col = remainder % 128
    return {"layer": layer, "row": row, "col": col}

def analyze_block_number(block):
    """Analyze mathematical properties of block number."""
    properties = []

    # Check for special numbers
    if block % 11 == 0:
        properties.append(f"divisible by 11 ({block//11})")
    if block % 27 == 0:
        properties.append(f"divisible by 27 ({block//27})")
    if block % 121 == 0:
        properties.append(f"divisible by 121 ({block//121})")
    if block % 137 == 0:
        properties.append(f"divisible by 137 ({block//137})")

    # Check digit patterns
    digits = str(block)
    if len(set(digits)) == 1:
        properties.append(f"repdigit ({digits})")
    if digits == digits[::-1]:
        properties.append(f"palindrome")

    # Prime factors
    n = block
    factors = []
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        while n % p == 0:
            factors.append(p)
            n //= p
    if n > 1:
        factors.append(n)

    return {
        "properties": properties,
        "factors": factors,
        "digit_sum": sum(int(d) for d in digits),
        "digit_product": eval('*'.join(digits)) if '0' not in digits else 0
    }

def main():
    print("=" * 70)
    print("ANTI-PATTERN BLOCKS ANALYSIS")
    print("These 12 blocks have NEITHER mod_576=0 NOR mod_27=0")
    print("=" * 70)

    results = {
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_anti_pattern_blocks": len(ANTI_PATTERN_BLOCKS),
        "significance": "These blocks are completely outside CFB mathematical patterns",
        "blocks": []
    }

    for i, entry in enumerate(ANTI_PATTERN_BLOCKS, 1):
        print(f"\n[{i}/12] Block {entry['block']}: {entry['address']}")
        print("-" * 60)

        block_data = {
            "address": entry['address'],
            "block": entry['block'],
            "mod_576": entry['mod_576'],
            "mod_27": entry['mod_27']
        }

        # Matrix position
        pos = analyze_matrix_position(entry['block'])
        block_data["matrix_position"] = pos
        print(f"  Matrix: Layer {pos['layer']}, Row {pos['row']}, Col {pos['col']}")

        # Block number analysis
        num_analysis = analyze_block_number(entry['block'])
        block_data["number_analysis"] = num_analysis
        print(f"  Factors: {num_analysis['factors']}")
        print(f"  Digit sum: {num_analysis['digit_sum']}, Product: {num_analysis['digit_product']}")
        if num_analysis['properties']:
            print(f"  Special: {', '.join(num_analysis['properties'])}")

        # Fetch blockchain data
        block_info = get_block_info(entry['block'])
        if block_info:
            block_data["block_info"] = block_info
            print(f"  Date: {block_info['date']}")

        addr_info = get_address_info(entry['address'])
        if addr_info:
            block_data["address_info"] = addr_info
            print(f"  Balance: {addr_info['final_balance']:.8f} BTC")
            print(f"  Status: {'UNSPENT' if addr_info['final_balance'] > 0 else 'SPENT'}")

        results["blocks"].append(block_data)

    # Pattern analysis
    print("\n" + "=" * 70)
    print("PATTERN ANALYSIS")
    print("=" * 70)

    # Check mod_576 values
    mod_576_values = [b["mod_576"] for b in ANTI_PATTERN_BLOCKS]
    print(f"\nmod_576 values: {set(mod_576_values)}")
    print(f"  192 appears: {mod_576_values.count(192)}x")
    print(f"  320 appears: {mod_576_values.count(320)}x")
    print(f"  384 appears: {mod_576_values.count(384)}x")

    # Check mod_27 values
    mod_27_values = [b["mod_27"] for b in ANTI_PATTERN_BLOCKS]
    print(f"\nmod_27 values: {set(mod_27_values)}")
    for v in sorted(set(mod_27_values)):
        print(f"  {v} appears: {mod_27_values.count(v)}x")

    # Interesting observations
    observations = []

    # 192 = 64 × 3 = 2^6 × 3
    observations.append("192 = 64 × 3 = 2⁶ × 3 (power of 2 × 3)")
    # 320 = 64 × 5 = 2^6 × 5
    observations.append("320 = 64 × 5 = 2⁶ × 5")
    # 384 = 128 × 3 = 2^7 × 3
    observations.append("384 = 128 × 3 = 2⁷ × 3 (row_size × 3)")

    # GCD of mod_576 values
    from math import gcd
    from functools import reduce
    gcd_576 = reduce(gcd, mod_576_values)
    observations.append(f"GCD of all mod_576 values: {gcd_576}")

    # mod_27 patterns
    # 3, 6, 12, 14, 15, 24
    observations.append("mod_27 values: 3, 6, 12, 14, 15, 24 - all divisible by 3 except 14")
    observations.append("Block 12873 (mod_27=14) is the only 'truly random' one")

    results["pattern_analysis"] = {
        "mod_576_distribution": {192: 4, 320: 1, 384: 7},
        "mod_27_distribution": dict(zip(*[list(x) for x in zip(*[(v, mod_27_values.count(v)) for v in sorted(set(mod_27_values))])])),
        "observations": observations
    }

    # Check for temporal patterns
    print("\n" + "=" * 70)
    print("TEMPORAL ANALYSIS")
    print("=" * 70)

    dates = []
    for block in results["blocks"]:
        if "block_info" in block and block["block_info"]:
            date = block["block_info"]["date"]
            dates.append((block["block"], date))

    for block, date in dates:
        print(f"  Block {block:5d}: {date}")

    results["temporal_analysis"] = dates

    # Save results
    script_dir = Path(__file__).parent
    output_path = script_dir / "ANTI_PATTERN_BLOCKS_ANALYSIS.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    unspent_count = sum(1 for b in results["blocks"]
                       if "address_info" in b and b["address_info"]
                       and b["address_info"]["final_balance"] > 0)

    print(f"\nTotal anti-pattern blocks: 12")
    print(f"Unspent (with balance): {unspent_count}")
    print(f"Most common mod_576: 384 (7 blocks)")
    print(f"Most common mod_27: 24 (5 blocks)")

    print("\nKEY INSIGHT:")
    print("384 = 128 × 3 = matrix row size × CFB ternary base")
    print("This suggests the 'exceptions' might still follow a hidden pattern!")


if __name__ == "__main__":
    main()
