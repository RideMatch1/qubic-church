#!/usr/bin/env python3
"""
TROLL POST KEY DEEP ANALYSIS
=============================

Der "Satoshi" Troll-Post hat diesen Private Key geleaked:
8bf0059274ca4df83675980c2be9204267bd8669ba7540b5faf2db5a8aa5d160

Adresse: 19N9TXyXmWg8yrytAKDvWKr1CSyqGAr4rp
Hash160: 5bc0cd29d481c6aa3529260d4cc6a3b5f4820a2f

Wir müssen:
1. Mirror-Operationen durchführen (wie bei 1CFB)
2. Mit unseren bekannten Adressen vergleichen
3. Matrix-Position finden
4. XOR mit Genesis, 1CFB, 15ubic
5. Pattern-Suche in unseren Seeds
"""

import hashlib
import json
import os
from datetime import datetime

# Die Schlüsseldaten
PRIVATE_KEY_HEX = "8bf0059274ca4df83675980c2be9204267bd8669ba7540b5faf2db5a8aa5d160"
ADDRESS = "19N9TXyXmWg8yrytAKDvWKr1CSyqGAr4rp"
HASH160 = "5bc0cd29d481c6aa3529260d4cc6a3b5f4820a2f"

# Bekannte Vergleichsadressen
KNOWN_ADDRESSES = {
    "1CFB": {
        "address": "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg",
        "hash160": "7b581609d8f9b74c34f7648c3b79fd8a6848022d",
    },
    "Genesis": {
        "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "hash160": "62e907b15cbf27d5425399ebf6f0fb50ebb88f18",
    },
    "15ubic": {
        "address": "15ubicBBWFnvoZLT7GiU2qxjRaKJPdkDMG",
        "hash160": "334c4aaba19236a991f356f5898ab6865b94b791",
    },
    "1CFi": {
        "address": "1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi",
        "hash160": "7b4f5d5c8d8a6b5c4d3e2f1a0b9c8d7e6f5a4b3c",  # Placeholder
    },
}

# CFB Constants
CFB_CONSTANTS = [7, 11, 13, 19, 27, 33, 43, 47, 121, 283, 576, 676, 817, 2299]

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def reverse_bytes(hex_str):
    """Reverse byte order"""
    b = bytes.fromhex(hex_str)
    return b[::-1].hex()

def complement_bytes(hex_str):
    """Bitwise complement"""
    b = bytes.fromhex(hex_str)
    return bytes([~byte & 0xff for byte in b]).hex()

def xor_bytes(hex1, hex2):
    """XOR two hex strings"""
    b1 = bytes.fromhex(hex1)
    b2 = bytes.fromhex(hex2)
    # Pad shorter one
    max_len = max(len(b1), len(b2))
    b1 = b1.ljust(max_len, b'\x00')
    b2 = b2.ljust(max_len, b'\x00')
    return bytes([a ^ b for a, b in zip(b1, b2)]).hex()

def rotate_bytes(hex_str, n):
    """Rotate bytes by n positions"""
    b = bytes.fromhex(hex_str)
    n = n % len(b)
    return (b[n:] + b[:n]).hex()

def analyze_byte_patterns(hex_str, name=""):
    """Analyze a hex string for CFB patterns"""
    b = bytes.fromhex(hex_str)
    byte_sum = sum(b)

    result = {
        "name": name,
        "hex": hex_str,
        "byte_sum": byte_sum,
        "first_byte": b[0],
        "first_byte_hex": hex(b[0]),
        "last_byte": b[-1],
        "length": len(b),
    }

    # CFB constant analysis
    result["mod_analysis"] = {}
    for c in CFB_CONSTANTS:
        result["mod_analysis"][f"mod_{c}"] = byte_sum % c

    # Divisibility
    result["divisible_by"] = [c for c in CFB_CONSTANTS if byte_sum % c == 0]

    # Factorization
    result["factorization"] = factorize(byte_sum)

    # Special checks
    result["is_2299"] = byte_sum == 2299
    result["contains_7b"] = "7b" in hex_str
    result["contains_21e8"] = "21e8" in hex_str
    result["starts_with_1"] = hex_str.startswith("1")

    return result

def factorize(n):
    """Simple factorization"""
    if n <= 1:
        return str(n)
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    if len(factors) == 1:
        return f"{n} (prime)"
    return " × ".join(map(str, factors))

def find_common_bytes(hex1, hex2):
    """Find common byte positions"""
    b1 = bytes.fromhex(hex1)
    b2 = bytes.fromhex(hex2)
    min_len = min(len(b1), len(b2))

    matches = []
    for i in range(min_len):
        if b1[i] == b2[i]:
            matches.append({"position": i, "value": hex(b1[i])})

    return matches

def hamming_distance(hex1, hex2):
    """Calculate Hamming distance (different bits)"""
    b1 = bytes.fromhex(hex1)
    b2 = bytes.fromhex(hex2)
    min_len = min(len(b1), len(b2))

    distance = 0
    for i in range(min_len):
        xor = b1[i] ^ b2[i]
        distance += bin(xor).count('1')

    return distance

def search_in_matrix_seeds(target_hash160):
    """Search for connections in our seed database"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mapping_file = os.path.join(os.path.dirname(script_dir), "complete_seed_btc_mapping.json")

    if not os.path.exists(mapping_file):
        return {"error": "Mapping file not found"}

    matches = []
    partial_matches = []

    try:
        with open(mapping_file, 'r') as f:
            content = f.read()
            # Search for partial matches
            target_parts = [target_hash160[i:i+4] for i in range(0, len(target_hash160), 4)]

            for part in target_parts:
                if part in content:
                    partial_matches.append(part)

        return {
            "exact_match": target_hash160 in content,
            "partial_matches": partial_matches,
            "match_ratio": len(partial_matches) / len(target_parts)
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=" * 80)
    print("TROLL POST KEY DEEP ANALYSIS")
    print("=" * 80)
    print(f"\nPrivate Key: {PRIVATE_KEY_HEX}")
    print(f"Address: {ADDRESS}")
    print(f"Hash160: {HASH160}")
    print(f"\nTimestamp: {datetime.now().isoformat()}")

    results = {
        "timestamp": datetime.now().isoformat(),
        "source": "Satoshi Troll Post on ning.com",
        "private_key": PRIVATE_KEY_HEX,
        "address": ADDRESS,
        "hash160": HASH160,
    }

    # 1. ANALYZE THE HASH160
    print("\n" + "=" * 80)
    print("1. HASH160 PATTERN ANALYSIS")
    print("=" * 80)

    h160_analysis = analyze_byte_patterns(HASH160, "Troll Post Hash160")
    results["hash160_analysis"] = h160_analysis

    print(f"\n  Byte Sum: {h160_analysis['byte_sum']}")
    print(f"  Factorization: {h160_analysis['factorization']}")
    print(f"  First Byte: {h160_analysis['first_byte_hex']} ({h160_analysis['first_byte']})")
    print(f"  Divisible by CFB constants: {h160_analysis['divisible_by']}")
    print(f"\n  Mod Analysis:")
    for key, val in h160_analysis['mod_analysis'].items():
        if val == 0 or val in [7, 11, 13, 19, 21, 27]:
            print(f"    {key} = {val} ⭐")
        else:
            print(f"    {key} = {val}")

    # 2. MIRROR OPERATIONS
    print("\n" + "=" * 80)
    print("2. MIRROR OPERATIONS (wie bei 1CFB)")
    print("=" * 80)

    mirrors = {
        "original": HASH160,
        "reversed": reverse_bytes(HASH160),
        "complement": complement_bytes(HASH160),
        "rotate_19": rotate_bytes(HASH160, 19),
        "rotate_27": rotate_bytes(HASH160, 27),
        "rotate_121": rotate_bytes(HASH160, 121 % 20),  # mod length
    }

    results["mirror_operations"] = {}

    for name, mirrored in mirrors.items():
        analysis = analyze_byte_patterns(mirrored, name)
        results["mirror_operations"][name] = analysis

        print(f"\n  {name}:")
        print(f"    Hex: {mirrored}")
        print(f"    Byte Sum: {analysis['byte_sum']} = {analysis['factorization']}")
        if analysis['divisible_by']:
            print(f"    Divisible by: {analysis['divisible_by']} ⭐")

    # 3. XOR WITH KNOWN ADDRESSES
    print("\n" + "=" * 80)
    print("3. XOR MIT BEKANNTEN ADRESSEN")
    print("=" * 80)

    results["xor_analysis"] = {}

    for name, data in KNOWN_ADDRESSES.items():
        if len(data["hash160"]) != 40:
            continue

        xor_result = xor_bytes(HASH160, data["hash160"])
        xor_analysis = analyze_byte_patterns(xor_result, f"XOR with {name}")

        # Common bytes
        common = find_common_bytes(HASH160, data["hash160"])

        # Hamming distance
        hamming = hamming_distance(HASH160, data["hash160"])

        results["xor_analysis"][name] = {
            "xor_result": xor_result,
            "xor_byte_sum": xor_analysis["byte_sum"],
            "common_bytes": common,
            "hamming_distance": hamming,
        }

        print(f"\n  XOR with {name}:")
        print(f"    {name} Hash160: {data['hash160']}")
        print(f"    XOR Result: {xor_result}")
        print(f"    XOR Byte Sum: {xor_analysis['byte_sum']} = {xor_analysis['factorization']}")
        print(f"    Common Bytes: {len(common)} positions")
        print(f"    Hamming Distance: {hamming} bits")

        if xor_analysis['divisible_by']:
            print(f"    Divisible by: {xor_analysis['divisible_by']} ⭐")

    # 4. PRIVATE KEY ANALYSIS
    print("\n" + "=" * 80)
    print("4. PRIVATE KEY PATTERN ANALYSIS")
    print("=" * 80)

    pk_analysis = analyze_byte_patterns(PRIVATE_KEY_HEX, "Private Key")
    results["private_key_analysis"] = pk_analysis

    print(f"\n  Byte Sum: {pk_analysis['byte_sum']}")
    print(f"  Factorization: {pk_analysis['factorization']}")
    print(f"  First Byte: {pk_analysis['first_byte_hex']} ({pk_analysis['first_byte']})")
    print(f"  Contains 7b: {pk_analysis['contains_7b']}")
    print(f"  Divisible by: {pk_analysis['divisible_by']}")

    # 5. XOR PRIVATE KEY WITH KNOWN HASHES
    print("\n" + "=" * 80)
    print("5. PRIVATE KEY XOR OPERATIONS")
    print("=" * 80)

    # XOR private key with 1CFB hash160 (padded)
    cfb_h160_padded = KNOWN_ADDRESSES["1CFB"]["hash160"].ljust(64, '0')
    genesis_h160_padded = KNOWN_ADDRESSES["Genesis"]["hash160"].ljust(64, '0')

    pk_xor_cfb = xor_bytes(PRIVATE_KEY_HEX, cfb_h160_padded)
    pk_xor_genesis = xor_bytes(PRIVATE_KEY_HEX, genesis_h160_padded)

    print(f"\n  PK XOR 1CFB Hash160:")
    print(f"    Result: {pk_xor_cfb}")
    pk_xor_cfb_analysis = analyze_byte_patterns(pk_xor_cfb, "PK XOR 1CFB")
    print(f"    Byte Sum: {pk_xor_cfb_analysis['byte_sum']} = {pk_xor_cfb_analysis['factorization']}")

    print(f"\n  PK XOR Genesis Hash160:")
    print(f"    Result: {pk_xor_genesis}")
    pk_xor_genesis_analysis = analyze_byte_patterns(pk_xor_genesis, "PK XOR Genesis")
    print(f"    Byte Sum: {pk_xor_genesis_analysis['byte_sum']} = {pk_xor_genesis_analysis['factorization']}")

    results["private_key_xor"] = {
        "xor_1cfb": pk_xor_cfb,
        "xor_1cfb_sum": pk_xor_cfb_analysis['byte_sum'],
        "xor_genesis": pk_xor_genesis,
        "xor_genesis_sum": pk_xor_genesis_analysis['byte_sum'],
    }

    # 6. SEARCH IN OUR DATABASE
    print("\n" + "=" * 80)
    print("6. SUCHE IN UNSERER SEED-DATENBANK")
    print("=" * 80)

    db_search = search_in_matrix_seeds(HASH160)
    results["database_search"] = db_search

    print(f"\n  Exact Match: {db_search.get('exact_match', 'N/A')}")
    print(f"  Partial Matches: {db_search.get('partial_matches', [])}")
    print(f"  Match Ratio: {db_search.get('match_ratio', 0):.2%}")

    # 7. ADDRESS CHARACTER ANALYSIS
    print("\n" + "=" * 80)
    print("7. ADRESS-ZEICHEN ANALYSE")
    print("=" * 80)

    # Compare address characters with 1CFB
    cfb_addr = KNOWN_ADDRESSES["1CFB"]["address"]

    common_chars = set(ADDRESS) & set(cfb_addr)
    common_positions = []
    for i, (c1, c2) in enumerate(zip(ADDRESS, cfb_addr)):
        if c1 == c2:
            common_positions.append((i, c1))

    print(f"\n  Troll Address: {ADDRESS}")
    print(f"  1CFB Address:  {cfb_addr}")
    print(f"  Common Chars: {sorted(common_chars)}")
    print(f"  Same Position Matches: {common_positions}")

    results["address_comparison"] = {
        "common_chars": list(common_chars),
        "same_position_matches": common_positions,
    }

    # 8. NUMERICAL RELATIONSHIPS
    print("\n" + "=" * 80)
    print("8. NUMERISCHE BEZIEHUNGEN")
    print("=" * 80)

    troll_sum = sum(bytes.fromhex(HASH160))  # 2432
    cfb_sum = 2299
    genesis_sum = sum(bytes.fromhex(KNOWN_ADDRESSES["Genesis"]["hash160"]))

    print(f"\n  Troll Hash160 Sum: {troll_sum}")
    print(f"  1CFB Hash160 Sum: {cfb_sum}")
    print(f"  Genesis Hash160 Sum: {genesis_sum}")
    print(f"\n  Differenzen:")
    print(f"    Troll - 1CFB = {troll_sum - cfb_sum} = {factorize(abs(troll_sum - cfb_sum))}")
    print(f"    Troll - Genesis = {troll_sum - genesis_sum} = {factorize(abs(troll_sum - genesis_sum))}")
    print(f"    1CFB - Genesis = {cfb_sum - genesis_sum} = {factorize(abs(cfb_sum - genesis_sum))}")

    print(f"\n  Verhältnisse:")
    print(f"    Troll / 1CFB = {troll_sum / cfb_sum:.6f}")
    print(f"    Troll / 121 = {troll_sum / 121:.6f}")
    print(f"    Troll / 19 = {troll_sum / 19:.6f}")

    # Check if difference has meaning
    diff_cfb = abs(troll_sum - cfb_sum)
    print(f"\n  Differenz 133 Analyse:")
    print(f"    133 = {factorize(133)}")
    print(f"    133 mod 19 = {133 % 19}")
    print(f"    133 mod 27 = {133 % 27}")
    print(f"    133 mod 7 = {133 % 7}")

    results["numerical_relationships"] = {
        "troll_sum": troll_sum,
        "cfb_sum": cfb_sum,
        "genesis_sum": genesis_sum,
        "diff_troll_cfb": troll_sum - cfb_sum,
        "diff_troll_genesis": troll_sum - genesis_sum,
    }

    # 9. CRITICAL DISCOVERY CHECK
    print("\n" + "=" * 80)
    print("9. KRITISCHE ENTDECKUNGEN")
    print("=" * 80)

    discoveries = []

    # Check for 2299
    if troll_sum == 2299:
        discoveries.append("Hash160 Sum = 2299 (CFB Signature!)")

    # Check divisibility
    if troll_sum % 19 == 0:
        discoveries.append(f"Hash160 Sum divisible by 19: {troll_sum} = {troll_sum // 19} × 19")

    if troll_sum % 121 == 0:
        discoveries.append(f"Hash160 Sum divisible by 121: {troll_sum} = {troll_sum // 121} × 121")

    # Check for 7b in any result
    for name, data in results.get("mirror_operations", {}).items():
        if "7b" in data.get("hex", ""):
            discoveries.append(f"Mirror '{name}' contains 7b!")

    # Check XOR results for patterns
    for name, data in results.get("xor_analysis", {}).items():
        xor_sum = data.get("xor_byte_sum", 0)
        if xor_sum in CFB_CONSTANTS or xor_sum == 2299:
            discoveries.append(f"XOR with {name} = {xor_sum} (CFB constant!)")

    # Special: 2432 = 2^7 × 19
    if troll_sum == 2432:
        discoveries.append("Hash160 Sum = 2432 = 2^7 × 19 (Power of 2 × Qubic Prime!)")

    results["discoveries"] = discoveries

    if discoveries:
        print("\n  GEFUNDENE PATTERNS:")
        for d in discoveries:
            print(f"    ⭐ {d}")
    else:
        print("\n  Keine offensichtlichen CFB-Signaturen gefunden.")

    # Save results
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "../TROLL_POST_KEY_ANALYSIS.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n" + "=" * 80)
    print(f"Results saved to: {output_file}")
    print("=" * 80)

    return results

if __name__ == "__main__":
    main()
