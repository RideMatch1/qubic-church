#!/usr/bin/env python3
"""
COINBASE PATTERN TEST - FIXED

The coinbase scriptsig structure:
1. Block height (varint, little-endian)
2. Extra nonce or miner message (ASCII)

We need to skip the height bytes and get the FIRST PRINTABLE ASCII character.
"""

import requests
import time
import re

API_BLOCK = "https://mempool.space/api/block-height/{}"
API_TXS = "https://mempool.space/api/block/{}/txs"

def get_expected_letter(height):
    """Calculate expected letter based on (height mod 26) pattern"""
    mod = height % 26
    if mod == 0:
        mod = 26
    return chr(ord('A') + mod - 1)

def extract_first_printable(scriptsig_hex):
    """
    Extract the first printable ASCII letter from coinbase scriptsig.
    Skip the block height bytes at the beginning.
    """
    try:
        raw_bytes = bytes.fromhex(scriptsig_hex)

        # The first byte tells us how many bytes encode the block height
        # For early blocks (< 256), it's usually 1-2 bytes
        # For blocks > 256, it's 2-3 bytes

        # Find the first printable ASCII character (A-Z, a-z, or punctuation)
        for i, b in enumerate(raw_bytes):
            # Skip if it's likely a height/length byte (0x01-0x08)
            if i < 4 and b < 32:
                continue
            # Check if it's a printable ASCII character
            if 32 <= b <= 126:
                char = chr(b)
                # Return only letters or common punctuation
                if char.isalpha() or char in ',.!?;:-_':
                    return char, i, raw_bytes[:20].hex()

        return None, -1, raw_bytes[:20].hex()

    except Exception as e:
        return None, -1, str(e)

def fetch_coinbase(height):
    """Fetch coinbase data from mempool.space"""
    try:
        # Get block hash
        resp = requests.get(API_BLOCK.format(height), timeout=10)
        if resp.status_code != 200:
            return None, None, f"Block hash error: {resp.status_code}"

        block_hash = resp.text.strip()

        # Get transactions
        resp = requests.get(API_TXS.format(block_hash), timeout=10)
        if resp.status_code != 200:
            return None, None, f"TX error: {resp.status_code}"

        txs = resp.json()
        if txs and 'vin' in txs[0] and txs[0]['vin']:
            scriptsig = txs[0]['vin'][0].get('scriptsig', '')
            char, pos, hex_sample = extract_first_printable(scriptsig)
            return char, pos, hex_sample

        return None, None, "No scriptsig"

    except Exception as e:
        return None, None, str(e)

# Strategic blocks
blocks_to_test = [
    # Known values (from previous research)
    (121, "11² - KNOWN: 'Q'"),
    (138, "6×23 - KNOWN: ','"),
    (676, "26² - KNOWN: 'Z'"),
    (2028, "3×676 - KNOWN: 'B'"),

    # Mathematical significance
    (6, "Row 6 Oracle"),
    (26, "YHVH gematria"),
    (43, "28+12+3 ARK signature"),
    (52, "52 weeks"),
    (79, "Row 79"),
    (264, "1CFB Address"),

    # More samples
    (1, "Block 1"),
    (13, "Fibonacci"),
    (21, "Fibonacci"),
    (100, "Round number"),
    (500, "Sample"),
    (1000, "Sample"),
]

print("=" * 80)
print("COINBASE PATTERN TEST - FIXED EXTRACTION")
print("=" * 80)
print("\nPattern hypothesis: First printable ASCII = letter for (height mod 26)")
print()

results = {'matches': [], 'exceptions': [], 'errors': []}

for height, reason in blocks_to_test:
    expected = get_expected_letter(height)
    mod_val = height % 26 if height % 26 != 0 else 26

    char, pos, hex_sample = fetch_coinbase(height)

    print(f"Block {height:5d}: Expected '{expected}' (mod 26 = {mod_val})")

    if char:
        if char.upper() == expected:
            status = "✅ MATCH"
            results['matches'].append({
                'height': height, 'char': char, 'expected': expected,
                'reason': reason, 'pos': pos
            })
        else:
            status = "❌ EXCEPTION"
            results['exceptions'].append({
                'height': height, 'char': char, 'expected': expected,
                'reason': reason, 'pos': pos
            })
        print(f"   Got: '{char}' at byte {pos} | {status} | {reason}")
        print(f"   Hex: {hex_sample}")
    else:
        print(f"   Error: {hex_sample}")
        results['errors'].append({'height': height, 'error': hex_sample})

    print()
    time.sleep(0.3)

# Summary
print("=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)

print(f"\n✅ MATCHES ({len(results['matches'])}):")
for r in results['matches']:
    print(f"   Block {r['height']:5d}: '{r['char']}' = '{r['expected']}' ✓ | {r['reason']}")

print(f"\n❌ EXCEPTIONS ({len(results['exceptions'])}):")
for r in sorted(results['exceptions'], key=lambda x: x['height']):
    print(f"   Block {r['height']:5d}: '{r['char']}' (expected '{r['expected']}') | {r['reason']}")

# Extract message from exceptions
if results['exceptions']:
    chars = [r['char'] for r in sorted(results['exceptions'], key=lambda x: x['height'])]
    print(f"\n🔥 EXCEPTION CHARACTERS (by block order): '{''.join(chars)}'")

# Verification of known values
print("\n" + "=" * 80)
print("VERIFICATION OF KNOWN VALUES")
print("=" * 80)

known = {
    121: ('Q', 'match'),
    676: ('Z', 'match'),
    138: (',', 'exception'),
    2028: ('B', 'exception'),
}

for height, (expected_char, expected_type) in known.items():
    found_match = next((r for r in results['matches'] if r['height'] == height), None)
    found_exc = next((r for r in results['exceptions'] if r['height'] == height), None)

    if found_match and found_match['char'].upper() == expected_char.upper():
        print(f"✅ Block {height}: '{found_match['char']}' confirmed as PATTERN MATCH")
    elif found_exc and found_exc['char'] == expected_char:
        print(f"✅ Block {height}: '{found_exc['char']}' confirmed as EXCEPTION")
    else:
        actual = found_match['char'] if found_match else (found_exc['char'] if found_exc else 'ERROR')
        print(f"❌ Block {height}: Expected '{expected_char}', got '{actual}'")

print("\n" + "=" * 80)
print("COMPLETE")
print("=" * 80)
