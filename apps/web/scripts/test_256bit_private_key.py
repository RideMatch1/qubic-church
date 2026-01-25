#!/usr/bin/env python3
"""
Test 256-Bit Private Key from "I am not Dorian Nakamoto" Troll Post
=====================================================================

This script validates the 256 bits dropped in the infamous troll post:
8bf0059274ca4df83675980c2be9204267bd8669ba7540b5faf2db5a8aa5d160

Source Context:
- Posted on ning.com (P2P Foundation)
- Claims to be educational about verifying cryptographic claims
- "Last but not least, let me drop these 256 bits here"

Analysis Goals:
1. Derive Bitcoin address(es) from this private key
2. Check if address has any blockchain history
3. Analyze patterns (CFB signatures, 21e8 connections)
"""

import hashlib
import json
import requests
from datetime import datetime

# The 256 bits from the troll post
PRIVATE_KEY_HEX = "8bf0059274ca4df83675980c2be9204267bd8669ba7540b5faf2db5a8aa5d160"

# Base58 alphabet for Bitcoin addresses
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def hex_to_bytes(hex_str):
    """Convert hex string to bytes"""
    return bytes.fromhex(hex_str)

def sha256(data):
    """SHA256 hash"""
    return hashlib.sha256(data).digest()

def ripemd160(data):
    """RIPEMD160 hash"""
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def hash160(data):
    """Bitcoin Hash160 = RIPEMD160(SHA256(data))"""
    return ripemd160(sha256(data))

def base58_encode(data):
    """Encode bytes to Base58"""
    num = int.from_bytes(data, 'big')
    result = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        result = BASE58_ALPHABET[remainder] + result

    # Handle leading zeros
    for byte in data:
        if byte == 0:
            result = '1' + result
        else:
            break

    return result

def base58check_encode(version_byte, payload):
    """Encode with Base58Check (version + payload + checksum)"""
    data = bytes([version_byte]) + payload
    checksum = sha256(sha256(data))[:4]
    return base58_encode(data + checksum)

def private_key_to_wif(private_key_bytes, compressed=True):
    """Convert private key to WIF format"""
    if compressed:
        extended = private_key_bytes + b'\x01'
        return base58check_encode(0x80, extended)
    else:
        return base58check_encode(0x80, private_key_bytes)

def get_public_key(private_key_bytes, compressed=True):
    """
    Derive public key from private key using secp256k1
    Using pure Python implementation (no external crypto libs needed)
    """
    # secp256k1 curve parameters
    P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
         0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

    def mod_inverse(a, m):
        """Extended Euclidean Algorithm for modular inverse"""
        if a < 0:
            a = a % m
        g, x, _ = extended_gcd(a, m)
        if g != 1:
            raise Exception('Modular inverse does not exist')
        return x % m

    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    def point_add(p1, p2):
        """Add two points on the curve"""
        if p1 is None:
            return p2
        if p2 is None:
            return p1

        x1, y1 = p1
        x2, y2 = p2

        if x1 == x2 and y1 != y2:
            return None

        if x1 == x2:
            m = (3 * x1 * x1) * mod_inverse(2 * y1, P) % P
        else:
            m = (y2 - y1) * mod_inverse(x2 - x1, P) % P

        x3 = (m * m - x1 - x2) % P
        y3 = (m * (x1 - x3) - y1) % P

        return (x3, y3)

    def scalar_mult(k, point):
        """Multiply point by scalar using double-and-add"""
        result = None
        addend = point

        while k:
            if k & 1:
                result = point_add(result, addend)
            addend = point_add(addend, addend)
            k >>= 1

        return result

    # Convert private key to integer
    private_key_int = int.from_bytes(private_key_bytes, 'big')

    # Validate private key range
    if private_key_int <= 0 or private_key_int >= N:
        raise ValueError("Private key out of valid range")

    # Calculate public key point
    public_key_point = scalar_mult(private_key_int, G)

    if public_key_point is None:
        raise ValueError("Invalid public key")

    x, y = public_key_point

    if compressed:
        # Compressed format: 02/03 prefix + x coordinate
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        return prefix + x.to_bytes(32, 'big')
    else:
        # Uncompressed format: 04 prefix + x + y
        return b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')

def public_key_to_address(public_key_bytes):
    """Convert public key to Bitcoin address"""
    h160 = hash160(public_key_bytes)
    return base58check_encode(0x00, h160), h160

def analyze_pattern(hex_str, name=""):
    """Analyze hex string for CFB/Qubic patterns"""
    patterns = {
        "byte_sum": sum(bytes.fromhex(hex_str)),
        "first_byte": int(hex_str[:2], 16),
        "contains_1cfb": "1cfb" in hex_str.lower(),
        "contains_21e8": "21e8" in hex_str.lower(),
        "contains_7b": "7b" in hex_str.lower(),
        "mod_121": sum(bytes.fromhex(hex_str)) % 121,
        "mod_19": sum(bytes.fromhex(hex_str)) % 19,
        "mod_27": sum(bytes.fromhex(hex_str)) % 27,
    }

    # Check for CFB number signatures
    cfb_numbers = [7, 11, 19, 27, 43, 47, 121, 283, 576, 676, 817, 2299]
    byte_sum = patterns["byte_sum"]

    patterns["cfb_divisors"] = [n for n in cfb_numbers if byte_sum % n == 0]
    patterns["is_2299"] = byte_sum == 2299
    patterns["factorization"] = f"{byte_sum} = " + factorize(byte_sum)

    return patterns

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

def check_blockchain(address):
    """Check address on blockchain via API"""
    try:
        # Try blockchain.info API
        url = f"https://blockchain.info/rawaddr/{address}?limit=5"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return {
                "found": True,
                "balance_satoshi": data.get("final_balance", 0),
                "balance_btc": data.get("final_balance", 0) / 100000000,
                "total_received": data.get("total_received", 0) / 100000000,
                "total_sent": data.get("total_sent", 0) / 100000000,
                "n_tx": data.get("n_tx", 0),
                "first_tx": data.get("txs", [{}])[0].get("time") if data.get("txs") else None
            }
        elif response.status_code == 500:
            # Address not found (no transactions)
            return {"found": False, "balance_btc": 0, "n_tx": 0, "note": "Address has no transaction history"}
        else:
            return {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=" * 70)
    print("256-BIT PRIVATE KEY ANALYSIS")
    print("From 'I am not Dorian Nakamoto' Troll Post")
    print("=" * 70)
    print(f"\nPrivate Key (Hex): {PRIVATE_KEY_HEX}")
    print(f"Length: {len(PRIVATE_KEY_HEX)} hex chars = {len(PRIVATE_KEY_HEX) * 4} bits")

    # Convert to bytes
    private_key_bytes = hex_to_bytes(PRIVATE_KEY_HEX)

    # Analyze the private key itself
    print("\n" + "=" * 70)
    print("PRIVATE KEY PATTERN ANALYSIS")
    print("=" * 70)
    pk_patterns = analyze_pattern(PRIVATE_KEY_HEX, "Private Key")
    for key, value in pk_patterns.items():
        print(f"  {key}: {value}")

    results = {
        "timestamp": datetime.now().isoformat(),
        "source": "I am not Dorian Nakamoto troll post",
        "private_key_hex": PRIVATE_KEY_HEX,
        "private_key_analysis": pk_patterns,
        "addresses": []
    }

    # Generate addresses (compressed and uncompressed)
    for compressed in [True, False]:
        format_name = "Compressed" if compressed else "Uncompressed"
        print(f"\n" + "=" * 70)
        print(f"{format_name.upper()} ADDRESS")
        print("=" * 70)

        try:
            # Get WIF
            wif = private_key_to_wif(private_key_bytes, compressed)
            print(f"  WIF: {wif}")

            # Get public key
            public_key = get_public_key(private_key_bytes, compressed)
            public_key_hex = public_key.hex()
            print(f"  Public Key: {public_key_hex[:20]}...{public_key_hex[-20:]}")

            # Get address
            address, hash160_bytes = public_key_to_address(public_key)
            hash160_hex = hash160_bytes.hex()
            print(f"  Hash160: {hash160_hex}")
            print(f"  Address: {address}")

            # Analyze hash160
            print(f"\n  Hash160 Pattern Analysis:")
            h160_patterns = analyze_pattern(hash160_hex, "Hash160")
            for key, value in h160_patterns.items():
                print(f"    {key}: {value}")

            # Check blockchain
            print(f"\n  Blockchain Check:")
            blockchain_info = check_blockchain(address)
            for key, value in blockchain_info.items():
                print(f"    {key}: {value}")

            # Store results
            results["addresses"].append({
                "format": format_name,
                "wif": wif,
                "public_key_hex": public_key_hex,
                "hash160": hash160_hex,
                "address": address,
                "hash160_analysis": h160_patterns,
                "blockchain": blockchain_info
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            results["addresses"].append({
                "format": format_name,
                "error": str(e)
            })

    # Cross-reference with known addresses
    print("\n" + "=" * 70)
    print("CROSS-REFERENCE CHECK")
    print("=" * 70)

    known_addresses = {
        "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg": "1CFB (CFB Signature Address)",
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa": "Genesis Block",
        "15ubicBBWFnvoZLT7GiU2qxjRaKJPdkDMG": "15ubic Address",
    }

    generated_addresses = [a["address"] for a in results["addresses"] if "address" in a]

    for gen_addr in generated_addresses:
        if gen_addr in known_addresses:
            print(f"  MATCH FOUND: {gen_addr} = {known_addresses[gen_addr]}")
            results["match_found"] = True
            results["match_details"] = known_addresses[gen_addr]
        else:
            # Check if starts with interesting prefixes
            interesting_prefixes = ["1CFB", "1CF", "15ub", "1A1z"]
            for prefix in interesting_prefixes:
                if gen_addr.startswith(prefix):
                    print(f"  INTERESTING PREFIX: {gen_addr} starts with {prefix}")

    if not results.get("match_found"):
        print("  No matches with known CFB/Genesis addresses")

    # Additional 21e8 analysis
    print("\n" + "=" * 70)
    print("21e8 BLOCK CONNECTION ANALYSIS")
    print("=" * 70)

    block_21e8 = "00000000000000000021e800c1e8df51b22c1588e5a624bea17e9faa34b2dc4a"
    print(f"  21e8 Block Hash: {block_21e8}")
    print(f"  Block Number: 528249")
    print(f"  Date: June 19, 2018")

    # Check for common patterns
    common_bytes = set(PRIVATE_KEY_HEX) & set(block_21e8.replace('0', ''))
    print(f"  Common hex chars with private key: {sorted(common_bytes)}")

    # XOR analysis
    pk_int = int(PRIVATE_KEY_HEX, 16)
    block_int = int(block_21e8, 16)
    xor_result = pk_int ^ block_int
    print(f"  XOR result (first 16 chars): {hex(xor_result)[:18]}...")

    results["21e8_analysis"] = {
        "block_hash": block_21e8,
        "block_number": 528249,
        "common_hex_chars": sorted(common_bytes),
        "xor_first_16": hex(xor_result)[:18]
    }

    # Save results
    output_file = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/256BIT_PRIVATE_KEY_RESULTS.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 70)
    print(f"Results saved to: {output_file}")
    print("=" * 70)

    return results

if __name__ == "__main__":
    main()
