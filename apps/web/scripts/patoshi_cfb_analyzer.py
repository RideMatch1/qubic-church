#!/usr/bin/env python3
"""
Patoshi CFB Pattern Analyzer
Analyzes Patoshi addresses for CFB signature patterns

CFB Numbers: 27 (3^3), 121 (11^2), 19, 47, 137, 283, 576, 676, 2299
"""

import json
import hashlib
import sys

# Bitcoin Base58 alphabet
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(data):
    """Encode bytes to Base58 string"""
    num = int.from_bytes(data, 'big')
    result = ''
    while num > 0:
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result

    # Handle leading zeros
    for byte in data:
        if byte == 0:
            result = '1' + result
        else:
            break

    return result

def hash160(data):
    """RIPEMD160(SHA256(data))"""
    sha256_hash = hashlib.sha256(data).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    return ripemd160.digest()

def pubkey_to_address(pubkey_hex):
    """Convert a public key to a Bitcoin P2PKH address"""
    pubkey_bytes = bytes.fromhex(pubkey_hex)

    # Hash160 of public key
    hash160_bytes = hash160(pubkey_bytes)

    # Add version byte (0x00 for mainnet)
    versioned = b'\x00' + hash160_bytes

    # Double SHA256 checksum
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

    # Encode to Base58
    return base58_encode(versioned + checksum)

# CFB-Zahlen
CFB_NUMBERS = {27, 121, 19, 47, 137, 283, 576, 676, 2299}

def get_letter_value(char):
    """Get numeric value for a character in address (only letters count)"""
    if char in 'ABCDEFGHJKLMNPQRSTUVWXYZ':  # uppercase
        idx = 'ABCDEFGHJKLMNPQRSTUVWXYZ'.index(char)
        return idx + 1
    elif char in 'abcdefghijkmnopqrstuvwxyz':  # lowercase
        idx = 'abcdefghijkmnopqrstuvwxyz'.index(char)
        return idx + 1
    return 0  # Digits have value 0 for this analysis

def calculate_letter_product(address):
    """Calculate the product of letter values (ignoring digits)"""
    product = 1
    letter_count = 0
    for char in address:
        val = get_letter_value(char)
        if val > 0:
            product *= val
            letter_count += 1
    return product, letter_count

def is_letters_only(address):
    """Check if address contains only letters (no digits 2-9)"""
    for char in address[1:]:  # Skip first character (always '1')
        if char in '23456789':
            return False
    return True

def check_cfb_mods(product, cfb_numbers):
    """Check if product mod any CFB number equals 0 or 1"""
    matches = []
    for n in cfb_numbers:
        mod = product % n
        if mod in [0, 1]:
            matches.append((n, mod))
    return matches

def main():
    # Lade die Patoshi-Daten
    print("Loading Patoshi data...")
    with open('public/data/patoshi-addresses.json', 'r') as f:
        data = json.load(f)

    print(f"Total records: {data['total']}")

    # Ergebnisse
    results = {
        "total_addresses": 0,
        "letters_only_addresses": [],
        "cfb_pattern_matches": [],
        "prefix_patterns": {
            "1CF": [],
            "1C": [],
            "1QB": [],
            "1A": [],
            "other_notable": []
        },
        "cfb_mod_matches": {
            "mod_27": [],
            "mod_121": [],
            "mod_2299": [],
            "mod_137": [],
            "mod_19": [],
            "mod_47": []
        },
        "anna_matrix_candidates": [],
        "top_cfb_candidates": []
    }

    print("Converting pubkeys to addresses and analyzing...")

    all_addresses = []

    for i, record in enumerate(data['records']):
        pubkey = record['pubkey']
        block = record['blockHeight']

        try:
            address = pubkey_to_address(pubkey)
            results["total_addresses"] += 1

            # Store for further analysis
            product, letter_count = calculate_letter_product(address)
            cfb_matches = check_cfb_mods(product, CFB_NUMBERS)

            addr_data = {
                "address": address,
                "block": block,
                "pubkey": pubkey[:40] + "...",
                "product": product,
                "letter_count": letter_count,
                "letters_only": is_letters_only(address),
                "cfb_matches": cfb_matches,
                "cfb_score": len(cfb_matches)
            }
            all_addresses.append(addr_data)

            # Check prefix patterns
            if address.startswith('1CFB'):
                results["prefix_patterns"]["1CF"].append({
                    "address": address,
                    "block": block,
                    "pubkey": pubkey[:40] + "...",
                    "note": "EXACT 1CFB PREFIX!"
                })
            elif address.startswith('1CF'):
                results["prefix_patterns"]["1CF"].append({
                    "address": address,
                    "block": block,
                    "pubkey": pubkey[:40] + "..."
                })
            elif address.startswith('1C'):
                if len(results["prefix_patterns"]["1C"]) < 100:  # Limit
                    results["prefix_patterns"]["1C"].append({
                        "address": address,
                        "block": block
                    })
            elif address.startswith('1QB'):
                results["prefix_patterns"]["1QB"].append({
                    "address": address,
                    "block": block
                })
            elif address.startswith('1A'):
                if len(results["prefix_patterns"]["1A"]) < 50:
                    results["prefix_patterns"]["1A"].append({
                        "address": address,
                        "block": block
                    })

            # Check if letters only
            if is_letters_only(address):
                results["letters_only_addresses"].append({
                    "address": address,
                    "block": block,
                    "product": product
                })

            # Check specific modulos
            if product % 27 == 0:
                if len(results["cfb_mod_matches"]["mod_27"]) < 100:
                    results["cfb_mod_matches"]["mod_27"].append({
                        "address": address,
                        "block": block,
                        "product": product
                    })
            if product % 121 == 0:
                if len(results["cfb_mod_matches"]["mod_121"]) < 100:
                    results["cfb_mod_matches"]["mod_121"].append({
                        "address": address,
                        "block": block,
                        "product": product
                    })
            if product % 2299 == 0:
                results["cfb_mod_matches"]["mod_2299"].append({
                    "address": address,
                    "block": block,
                    "product": product
                })
            if product % 137 == 0:
                if len(results["cfb_mod_matches"]["mod_137"]) < 100:
                    results["cfb_mod_matches"]["mod_137"].append({
                        "address": address,
                        "block": block,
                        "product": product
                    })
            if product % 19 == 0:
                if len(results["cfb_mod_matches"]["mod_19"]) < 100:
                    results["cfb_mod_matches"]["mod_19"].append({
                        "address": address,
                        "block": block,
                        "product": product
                    })
            if product % 47 == 0:
                if len(results["cfb_mod_matches"]["mod_47"]) < 100:
                    results["cfb_mod_matches"]["mod_47"].append({
                        "address": address,
                        "block": block,
                        "product": product
                    })

            # Check for multiple CFB mod matches (strong candidates)
            if len(cfb_matches) >= 2:
                results["cfb_pattern_matches"].append({
                    "address": address,
                    "block": block,
                    "product": product,
                    "cfb_matches": cfb_matches,
                    "score": len(cfb_matches)
                })

            # Anna-Matrix candidates: addresses with specific patterns
            if len(set(address)) <= 15:
                results["anna_matrix_candidates"].append({
                    "address": address,
                    "block": block,
                    "unique_chars": len(set(address)),
                    "product": product
                })

        except Exception as e:
            pass

        if (i + 1) % 5000 == 0:
            print(f"  Processed {i + 1} records...")

    # Sort by CFB score and get top candidates
    all_addresses.sort(key=lambda x: (-x['cfb_score'], x['block']))
    results["top_cfb_candidates"] = all_addresses[:50]

    # Sort cfb_pattern_matches by score
    results["cfb_pattern_matches"].sort(key=lambda x: (-x['score'], x['block']))

    # Print results
    print(f"\n{'='*60}")
    print("PATOSHI CFB ANALYSIS RESULTS")
    print(f"{'='*60}")
    print(f"Total addresses analyzed: {results['total_addresses']}")

    print(f"\n--- Prefix Patterns ---")
    print(f"Addresses starting with 1CF: {len(results['prefix_patterns']['1CF'])}")
    if results['prefix_patterns']['1CF']:
        for addr in results['prefix_patterns']['1CF']:
            print(f"  * {addr['address']} (block {addr['block']})")

    print(f"Addresses starting with 1C: {len(results['prefix_patterns']['1C'])} (showing first 100)")
    print(f"Addresses starting with 1QB: {len(results['prefix_patterns']['1QB'])}")
    if results['prefix_patterns']['1QB']:
        for addr in results['prefix_patterns']['1QB']:
            print(f"  * {addr['address']} (block {addr['block']})")

    print(f"Addresses starting with 1A: {len(results['prefix_patterns']['1A'])} (showing first 50)")

    print(f"\n--- Letter-Only Addresses (NO digits 2-9) ---")
    print(f"Total: {len(results['letters_only_addresses'])}")
    for addr in results['letters_only_addresses'][:20]:
        print(f"  {addr['address']} (block {addr['block']}, product={addr['product']})")

    print(f"\n--- CFB Mod Matches ---")
    print(f"Product mod 27 = 0: {len(results['cfb_mod_matches']['mod_27'])}")
    print(f"Product mod 121 = 0: {len(results['cfb_mod_matches']['mod_121'])}")
    print(f"Product mod 2299 = 0: {len(results['cfb_mod_matches']['mod_2299'])}")
    print(f"Product mod 137 = 0: {len(results['cfb_mod_matches']['mod_137'])}")
    print(f"Product mod 19 = 0: {len(results['cfb_mod_matches']['mod_19'])}")
    print(f"Product mod 47 = 0: {len(results['cfb_mod_matches']['mod_47'])}")

    if results['cfb_mod_matches']['mod_2299']:
        print(f"\n  Mod 2299 matches (RARE):")
        for m in results['cfb_mod_matches']['mod_2299']:
            print(f"    {m['address']} (block {m['block']})")

    print(f"\n--- Multi-CFB Matches (2+ CFB patterns) ---")
    print(f"Total: {len(results['cfb_pattern_matches'])}")
    for match in results['cfb_pattern_matches'][:30]:
        print(f"  {match['address']} (block {match['block']})")
        print(f"    Score: {match['score']}, Matches: {match['cfb_matches']}")

    print(f"\n--- TOP 20 CFB CANDIDATES ---")
    for i, cand in enumerate(results['top_cfb_candidates'][:20]):
        print(f"{i+1}. {cand['address']} (block {cand['block']})")
        print(f"   Score: {cand['cfb_score']}, Product: {cand['product']}")
        print(f"   Matches: {cand['cfb_matches']}")
        print(f"   Letters only: {cand['letters_only']}")

    print(f"\n--- Anna-Matrix Candidates (low unique chars) ---")
    print(f"Total: {len(results['anna_matrix_candidates'])}")
    results['anna_matrix_candidates'].sort(key=lambda x: x['unique_chars'])
    for addr in results['anna_matrix_candidates'][:10]:
        print(f"  {addr['address']} ({addr['unique_chars']} unique chars, block {addr['block']})")

    # Speichere Ergebnisse
    with open('scripts/PATOSHI_CFB_ANALYSIS.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to scripts/PATOSHI_CFB_ANALYSIS.json")

if __name__ == "__main__":
    main()
