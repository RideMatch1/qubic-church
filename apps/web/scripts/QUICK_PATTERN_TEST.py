#!/usr/bin/env python3
"""
QUICK COINBASE PATTERN TEST

Tests specific strategic blocks to verify the pattern:
- Expected: block_height mod 26 = letter_number
- If coinbase matches expected letter → Pattern follower
- If coinbase differs → Exception (part of hidden message?)

Already known:
- Block 121: 'Q' (17th) → MATCHES (121 mod 26 = 17)
- Block 676: 'Z' (26th) → MATCHES (676 mod 26 = 0 → 26)
- Block 138: ',' → BREAKS (should be 'H', 8th)
- Block 2028: 'B' → BREAKS (should be 'Z', 26th)
"""

import requests
import time

API = "https://api.blockchair.com/bitcoin/dashboards/block/{}"

def get_expected_letter(height):
    """Calculate expected letter based on (height mod 26) pattern"""
    mod = height % 26
    if mod == 0:
        mod = 26  # 0 = Z (26th letter)
    return chr(ord('A') + mod - 1)

def fetch_coinbase(height):
    """Fetch coinbase message first character from block"""
    try:
        url = API.format(height)
        resp = requests.get(url, timeout=15)

        if resp.status_code == 200:
            data = resp.json()
            if 'data' in data and str(height) in data['data']:
                block_data = data['data'][str(height)]

                # Get coinbase from first transaction
                if 'transactions' in block_data:
                    txs = block_data['transactions']
                    if len(txs) > 0:
                        tx = txs[0]
                        if 'inputs' in tx and len(tx['inputs']) > 0:
                            inp = tx['inputs'][0]
                            if 'coinbase_data_hex' in inp:
                                hex_data = inp['coinbase_data_hex']
                                try:
                                    decoded = bytes.fromhex(hex_data).decode('ascii', errors='ignore')
                                    return decoded[0] if decoded else '?'
                                except:
                                    return '?'
        return None
    except Exception as e:
        print(f"   Error: {e}")
        return None

# Strategic blocks to test
strategic_blocks = [
    6,    # Row 6 Oracle
    26,   # YHVH gematria
    43,   # 28+12+3 ARK signature
    79,   # Row 79 special
    121,  # 11² (already known: 'Q')
    138,  # 6×23 (already known: ',')
    264,  # 1CFB address block
    676,  # 26² (already known: 'Z')
    2028, # 3×676 = ARK supply (already known: 'B')
]

# Additional interesting blocks
more_blocks = [
    0, 1, 2, 3, 4, 5,  # Genesis and early blocks
    52, 104, 156,      # Multiples of 52 (weeks)
    69, 420,           # Meme numbers (comparison)
    1000,              # Round number
]

all_blocks = sorted(set(strategic_blocks + more_blocks))

print("=" * 80)
print("COINBASE PATTERN TEST - STRATEGIC BLOCKS")
print("=" * 80)
print(f"\nPattern: block_height mod 26 = letter_number")
print(f"Example: Block 676 mod 26 = 0 → 'Z' (26th letter)")
print(f"\nTesting {len(all_blocks)} blocks...\n")

results = {
    'matches': [],
    'exceptions': [],
}

for height in all_blocks:
    expected = get_expected_letter(height)
    print(f"Block {height:5d}: Expected '{expected}' ({height} mod 26 = {height % 26 or 26}) ... ", end='', flush=True)

    coinbase = fetch_coinbase(height)

    if coinbase:
        if coinbase.upper() == expected:
            print(f"Got '{coinbase}' ✅ MATCHES!")
            results['matches'].append({'height': height, 'char': coinbase, 'expected': expected})
        else:
            print(f"Got '{coinbase}' ❌ EXCEPTION!")
            results['exceptions'].append({'height': height, 'char': coinbase, 'expected': expected})
    else:
        print("Failed to fetch")

    time.sleep(1.5)  # Rate limit

print("\n" + "=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)

print(f"\n✅ PATTERN MATCHES ({len(results['matches'])}):")
for r in results['matches']:
    print(f"   Block {r['height']:5d}: '{r['char']}' = '{r['expected']}' (correct!)")

print(f"\n❌ EXCEPTIONS ({len(results['exceptions'])}):")
for r in results['exceptions']:
    print(f"   Block {r['height']:5d}: '{r['char']}' ≠ '{r['expected']}' (breaks pattern!)")

if results['exceptions']:
    exception_chars = ''.join([r['char'] for r in results['exceptions']])
    print(f"\n🔥 EXCEPTION CHARACTERS: '{exception_chars}'")
    print(f"   Could this spell something?")

# Stats
total = len(results['matches']) + len(results['exceptions'])
if total > 0:
    match_pct = len(results['matches']) / total * 100
    print(f"\n📊 STATISTICS:")
    print(f"   Total blocks tested: {total}")
    print(f"   Pattern followers: {len(results['matches'])} ({match_pct:.1f}%)")
    print(f"   Exceptions: {len(results['exceptions'])} ({100-match_pct:.1f}%)")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
