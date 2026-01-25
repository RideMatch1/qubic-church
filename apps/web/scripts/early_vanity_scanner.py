#!/usr/bin/env python3
"""
EARLY VANITY ADDRESS SCANNER
=============================

Scannt die ersten 500 Blöcke nach Vanity-Adressen mit besonderen Eigenschaften.

Bekannte Adressen:
- Block 0: Genesis (1A1zP1...)
- Block 4: 15ubic (enthält "ubic" = QUBIC ohne Q)
- Block 9: Hal Finney (erste non-Satoshi TX)
- Block 264: 1CFB (Master Formula 2299!)

Wir suchen nach:
1. Adressen die mit 1CF, 1NXT, 1Q, etc. beginnen
2. Adressen mit Hash160 Byte Sum = 2299
3. Adressen mit X mod 19 = 0
4. Adressen mit 0x7b Hash160 Start
"""

import hashlib
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor

# Bitcoin Base58 Alphabet
ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def decode_base58(addr):
    """Decode Base58 address to bytes"""
    n = 0
    for c in addr:
        n = n * 58 + ALPHABET.index(c)

    # Convert to bytes
    result = []
    while n > 0:
        result.append(n % 256)
        n //= 256
    result = bytes(reversed(result))

    # Add leading zeros
    pad_size = len(addr) - len(addr.lstrip('1'))
    return b'\x00' * pad_size + result

def get_hash160_from_address(address):
    """Extract Hash160 from Bitcoin address"""
    try:
        decoded = decode_base58(address)
        # Skip version byte (1) and checksum (4)
        return decoded[1:-4]
    except:
        return None

def analyze_address(address):
    """Analyze address for special properties"""
    h160 = get_hash160_from_address(address)
    if h160 is None or len(h160) != 20:
        return None

    byte_sum = sum(h160)
    first_byte = h160[0]

    return {
        "address": address,
        "hash160": h160.hex(),
        "byte_sum": byte_sum,
        "first_byte": hex(first_byte),
        "is_2299": byte_sum == 2299,
        "is_7b": first_byte == 0x7b,
        "mod_121": byte_sum % 121,
        "mod_19": byte_sum % 19,
    }

def get_block_coinbase(height, retries=3):
    """Get coinbase address from block"""
    for attempt in range(retries):
        try:
            # Get block hash
            url = f"https://blockstream.info/api/block-height/{height}"
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                time.sleep(1)
                continue
            block_hash = r.text.strip()

            # Get transactions
            tx_url = f"https://blockstream.info/api/block/{block_hash}/txs/0"
            r = requests.get(tx_url, timeout=10)
            if r.status_code != 200:
                time.sleep(1)
                continue
            txs = r.json()

            if not txs:
                return None

            coinbase = txs[0]
            vout = coinbase.get('vout', [])

            if vout:
                # Get first output address
                scriptpubkey_address = vout[0].get('scriptpubkey_address')
                if scriptpubkey_address:
                    return {
                        "height": height,
                        "address": scriptpubkey_address,
                        "value": vout[0].get('value', 0) / 100000000,
                        "scriptsig": coinbase.get('vin', [{}])[0].get('scriptsig', ''),
                    }

            return None

        except Exception as e:
            time.sleep(1)
            continue

    return None

def is_vanity_address(address):
    """Check if address appears to be a vanity address"""
    # Known vanity patterns
    patterns = [
        "1CFB", "1CFb", "1Cfb",
        "15ubic", "15UBIC",
        "1NXT", "1Nxt",
        "1IOTA", "1Iota",
        "1Qub", "1QUB",
        "1Sat", "1SAT",
        "1Bit", "1BIT",
    ]

    for p in patterns:
        if address.startswith(p):
            return True, p

    # Check for readable words
    readable = address[1:5].lower()
    words = ["love", "hate", "coin", "cash", "gold", "moon", "hodl", "test"]
    for w in words:
        if readable.startswith(w):
            return True, readable

    return False, None

def scan_early_blocks(start=0, end=500):
    """Scan early blocks for interesting addresses"""
    print("=" * 70)
    print("EARLY VANITY ADDRESS SCANNER")
    print("=" * 70)
    print(f"Scanning blocks {start} to {end}...")
    print()

    results = {
        "vanity_addresses": [],
        "master_formula_2299": [],
        "cfb_family_7b": [],
        "special_mod": [],
        "all_addresses": [],
    }

    for height in range(start, end + 1):
        data = get_block_coinbase(height)

        if data is None:
            print(f"  Block {height}: No data")
            continue

        address = data["address"]
        analysis = analyze_address(address)

        if analysis is None:
            print(f"  Block {height}: Cannot analyze {address}")
            continue

        # Merge data
        analysis["block"] = height
        analysis["value_btc"] = data["value"]
        analysis["scriptsig"] = data["scriptsig"]

        results["all_addresses"].append(analysis)

        # Check for vanity
        is_vanity, pattern = is_vanity_address(address)

        # Check for special properties
        flags = []

        if is_vanity:
            flags.append(f"VANITY:{pattern}")
            results["vanity_addresses"].append(analysis)

        if analysis["is_2299"]:
            flags.append("MASTER_FORMULA!")
            results["master_formula_2299"].append(analysis)

        if analysis["is_7b"]:
            flags.append("CFB_FAMILY(0x7b)")
            results["cfb_family_7b"].append(analysis)

        if analysis["mod_121"] == 0 and analysis["mod_19"] == 0:
            flags.append("MOD_SPECIAL")
            results["special_mod"].append(analysis)

        # Print interesting blocks
        if flags or height in [0, 4, 9, 73, 264]:
            print(f"  Block {height}: {address}")
            print(f"    Value: {data['value']:.0f} BTC")
            print(f"    Hash160: {analysis['hash160']}")
            print(f"    Byte Sum: {analysis['byte_sum']}")
            if flags:
                print(f"    FLAGS: {', '.join(flags)}")
            print()

        # Rate limiting
        if height % 10 == 0:
            print(f"  Progress: Block {height}/{end}")
            time.sleep(0.5)

    return results

def main():
    print()
    print("█" * 70)
    print("█  EARLY BITCOIN VANITY ADDRESS SCANNER                            █")
    print("█" * 70)
    print()
    print("Bekannte Adressen:")
    print("  Block   0: Genesis (1A1zP1...)")
    print("  Block   4: 15ubic (QUBIC ohne Q!)")
    print("  Block   9: Hal Finney TX")
    print("  Block 264: 1CFB (Master Formula 2299!)")
    print()

    # Scan first 300 blocks
    results = scan_early_blocks(0, 300)

    print()
    print("=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    print()
    print(f"Gescannte Blöcke: {len(results['all_addresses'])}")
    print(f"Vanity Adressen: {len(results['vanity_addresses'])}")
    print(f"Master Formula (2299): {len(results['master_formula_2299'])}")
    print(f"CFB Familie (0x7b): {len(results['cfb_family_7b'])}")
    print(f"Spezial Mod (121=0, 19=0): {len(results['special_mod'])}")
    print()

    if results["vanity_addresses"]:
        print("VANITY ADRESSEN:")
        print("-" * 70)
        for a in results["vanity_addresses"]:
            print(f"  Block {a['block']:3d}: {a['address']}")
            print(f"           Byte Sum: {a['byte_sum']}, 0x7b: {a['is_7b']}, 2299: {a['is_2299']}")
        print()

    if results["master_formula_2299"]:
        print("MASTER FORMULA (2299) ADRESSEN:")
        print("-" * 70)
        for a in results["master_formula_2299"]:
            print(f"  Block {a['block']:3d}: {a['address']}")
            print(f"           Hash160 starts: {a['first_byte']}")
        print()

    if results["cfb_family_7b"]:
        print("CFB FAMILIE (0x7b START):")
        print("-" * 70)
        for a in results["cfb_family_7b"]:
            print(f"  Block {a['block']:3d}: {a['address']}")
            print(f"           Byte Sum: {a['byte_sum']}, 2299: {a['is_2299']}")
        print()

    # Save results
    output_file = "EARLY_VANITY_SCAN_RESULTS.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Ergebnisse gespeichert: {output_file}")

    # Special analysis
    print()
    print("=" * 70)
    print("SPEZIAL-ANALYSE: Block 4 vs Block 264")
    print("=" * 70)

    block4 = next((a for a in results["all_addresses"] if a["block"] == 4), None)
    block264 = next((a for a in results["all_addresses"] if a["block"] == 264), None)

    if block4 and block264:
        print()
        print("Block 4 (15ubic):")
        print(f"  Adresse: {block4['address']}")
        print(f"  Hash160: {block4['hash160']}")
        print(f"  Byte Sum: {block4['byte_sum']}")
        print(f"  mod 121: {block4['mod_121']}, mod 19: {block4['mod_19']}")
        print(f"  0x7b Start: {block4['is_7b']}")
        print()
        print("Block 264 (1CFB):")
        print(f"  Adresse: {block264['address']}")
        print(f"  Hash160: {block264['hash160']}")
        print(f"  Byte Sum: {block264['byte_sum']}")
        print(f"  mod 121: {block264['mod_121']}, mod 19: {block264['mod_19']}")
        print(f"  0x7b Start: {block264['is_7b']}")
        print()
        print("VERGLEICH:")
        print(f"  15ubic: 'ubic' = QUBIC ohne Q (Block 4 = 2²)")
        print(f"  1CFB:   'CFB' = Come From Beyond (Block 264 = 8×33)")
        print()
        print(f"  15ubic Byte Sum: {block4['byte_sum']} (NICHT 2299)")
        print(f"  1CFB Byte Sum:   {block264['byte_sum']} = 121 × 19 = NXT × QUBIC ✅")
        print()
        if block264['is_7b'] and block264['is_2299']:
            print("  🔥 NUR 1CFB hat BEIDE CFB-Signaturen:")
            print("     - 0x7b Start (CFB Familie)")
            print("     - 2299 Byte Sum (Master Formula)")

    print()

if __name__ == "__main__":
    main()
