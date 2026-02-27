#!/usr/bin/env python3
"""
MEMPOOL.SPACE COINBASE PATTERN TEST

Uses mempool.space API to fetch coinbase messages from strategic blocks.
Tests pattern: block_height mod 26 = letter_number
"""

import requests
import time

# mempool.space API
API_BLOCK = "https://mempool.space/api/block-height/{}"
API_BLOCK_DATA = "https://mempool.space/api/block/{}"
API_TXS = "https://mempool.space/api/block/{}/txs"

def get_expected_letter(height):
    """Calculate expected letter based on (height mod 26) pattern"""
    mod = height % 26
    if mod == 0:
        mod = 26  # 0 = Z (26th letter)
    return chr(ord('A') + mod - 1)

def fetch_coinbase_mempool(height):
    """Fetch coinbase message from mempool.space API"""
    try:
        # First get block hash from height
        url_hash = API_BLOCK.format(height)
        resp = requests.get(url_hash, timeout=10)
        if resp.status_code != 200:
            return None, f"Hash lookup failed: {resp.status_code}"

        block_hash = resp.text.strip()

        # Then get transactions
        url_txs = API_TXS.format(block_hash)
        resp = requests.get(url_txs, timeout=10)
        if resp.status_code != 200:
            return None, f"TX lookup failed: {resp.status_code}"

        txs = resp.json()
        if len(txs) > 0:
            coinbase_tx = txs[0]  # First tx is always coinbase

            # Get the coinbase scriptsig (input script)
            if 'vin' in coinbase_tx and len(coinbase_tx['vin']) > 0:
                vin = coinbase_tx['vin'][0]
                if 'scriptsig' in vin:
                    scriptsig_hex = vin['scriptsig']

                    # Try to decode as ASCII
                    try:
                        decoded = bytes.fromhex(scriptsig_hex).decode('ascii', errors='ignore')
                        # Get printable characters
                        printable = ''.join(c if c.isprintable() else '?' for c in decoded)
                        first_char = printable[0] if printable else '?'
                        return first_char, printable[:50]
                    except:
                        return '?', scriptsig_hex[:20]

        return None, "No coinbase found"

    except Exception as e:
        return None, str(e)

# Strategic blocks to test
blocks_to_test = [
    # Key mathematical blocks
    (6, "Row 6 Oracle"),
    (26, "YHVH gematria"),
    (43, "28+12+3 = ARK signature"),
    (52, "52 weeks"),
    (79, "Row 79 special"),
    (121, "11² (KNOWN: 'Q')"),
    (138, "6×23 (KNOWN: ',')"),
    (264, "1CFB Address"),
    (676, "26² (KNOWN: 'Z')"),
    (2028, "3×676 = ARK (KNOWN: 'B')"),

    # Early blocks for baseline
    (1, "First block"),
    (2, "Second block"),
    (3, "Third block"),
    (10, "Tenth block"),
]

print("=" * 80)
print("MEMPOOL.SPACE COINBASE PATTERN TEST")
print("=" * 80)
print(f"\nPattern: block_height mod 26 = letter_number")
print(f"Testing {len(blocks_to_test)} strategic blocks...\n")

results = {
    'matches': [],
    'exceptions': [],
    'errors': [],
}

for height, reason in blocks_to_test:
    expected = get_expected_letter(height)
    mod_val = height % 26 if height % 26 != 0 else 26

    print(f"Block {height:5d} ({reason}):")
    print(f"   Expected: '{expected}' ({height} mod 26 = {mod_val})")

    first_char, full_msg = fetch_coinbase_mempool(height)

    if first_char:
        print(f"   Got: '{first_char}' (message: '{full_msg}')")

        if first_char.upper() == expected:
            print(f"   ✅ MATCHES PATTERN!")
            results['matches'].append({
                'height': height,
                'char': first_char,
                'expected': expected,
                'reason': reason,
                'full': full_msg
            })
        else:
            print(f"   ❌ EXCEPTION - breaks pattern!")
            results['exceptions'].append({
                'height': height,
                'char': first_char,
                'expected': expected,
                'reason': reason,
                'full': full_msg
            })
    else:
        print(f"   ⚠️  Error: {full_msg}")
        results['errors'].append({'height': height, 'error': full_msg})

    print()
    time.sleep(0.3)  # Be nice to API

print("=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)

print(f"\n✅ PATTERN MATCHES ({len(results['matches'])}):")
for r in results['matches']:
    print(f"   Block {r['height']:5d}: '{r['char']}' = '{r['expected']}' ✓ ({r['reason']})")

print(f"\n❌ EXCEPTIONS ({len(results['exceptions'])}):")
for r in results['exceptions']:
    print(f"   Block {r['height']:5d}: '{r['char']}' ≠ '{r['expected']}' ({r['reason']})")

if results['errors']:
    print(f"\n⚠️  ERRORS ({len(results['errors'])}):")
    for r in results['errors']:
        print(f"   Block {r['height']:5d}: {r['error']}")

if results['exceptions']:
    exception_chars = ''.join([r['char'] for r in sorted(results['exceptions'], key=lambda x: x['height'])])
    print(f"\n🔥 EXCEPTION CHARACTERS (sorted by block height): '{exception_chars}'")

# Stats
total_tested = len(results['matches']) + len(results['exceptions'])
if total_tested > 0:
    match_pct = len(results['matches']) / total_tested * 100
    print(f"\n📊 STATISTICS (excluding errors):")
    print(f"   Blocks tested: {total_tested}")
    print(f"   Pattern followers: {len(results['matches'])} ({match_pct:.1f}%)")
    print(f"   Exceptions: {len(results['exceptions'])} ({100-match_pct:.1f}%)")

print("\n" + "=" * 80)
print("ANALYSIS")
print("=" * 80)

# Check if known exceptions match
known_exceptions = {138: ',', 2028: 'B'}
known_matches = {121: 'Q', 676: 'Z'}

print("\n🔍 VERIFICATION AGAINST KNOWN VALUES:")
for height, expected_char in known_matches.items():
    found = next((r for r in results['matches'] if r['height'] == height), None)
    if found and found['char'].upper() == expected_char:
        print(f"   ✅ Block {height}: '{found['char']}' confirmed!")
    else:
        print(f"   ❌ Block {height}: Expected '{expected_char}', mismatch!")

for height, expected_char in known_exceptions.items():
    found = next((r for r in results['exceptions'] if r['height'] == height), None)
    if found and found['char'] == expected_char:
        print(f"   ✅ Block {height}: '{found['char']}' confirmed as exception!")
    else:
        print(f"   ❌ Block {height}: Expected '{expected_char}' exception, mismatch!")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
