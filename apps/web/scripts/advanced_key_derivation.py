#!/usr/bin/env python3
"""
🔥 ADVANCED KEY DERIVATION - 50+ METHODEN! 🔥
==============================================

NICHT LOCKER LASSEN!
Probiert ALLE möglichen Ableitungen:
- SHA3 (256, 384, 512)
- BLAKE2 (b, s)
- RIPEMD (160, 256, 320)
- Keccak variants
- Mathematical transformations (XOR, ROT, etc.)
- Seed combinations
- CFB number magic

TOTAL: 50+ neue Methoden pro Adresse!
"""

import hashlib
import json
import ecdsa
from ecdsa import SigningKey, SECP256k1

def load_data():
    with open('public/data/patoshi-addresses.json', 'r') as f:
        patoshi = json.load(f).get('records', [])
    with open('public/data/qubic-seeds.json', 'r') as f:
        seeds = json.load(f).get('records', [])
    return patoshi, seeds

def private_key_to_public_key(private_key_hex):
    """Convert private key to public key"""
    try:
        private_key_bytes = bytes.fromhex(private_key_hex)
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        uncompressed = '04' + vk.to_string().hex()
        return uncompressed
    except:
        return None

def advanced_derivations(seed, block):
    """50+ Ableitungsmethoden!"""
    keys = []

    # ========== HASH FUNCTION VARIANTS ==========

    # 1-3: SHA3 variants
    if seed:
        keys.append(('SHA3-256', hashlib.sha3_256(seed.encode()).hexdigest()))
        keys.append(('SHA3-384', hashlib.sha3_384(seed.encode()).hexdigest()[:64]))
        keys.append(('SHA3-512', hashlib.sha3_512(seed.encode()).hexdigest()[:64]))

    # 4-5: BLAKE2
    if seed:
        keys.append(('BLAKE2b', hashlib.blake2b(seed.encode(), digest_size=32).hexdigest()))
        keys.append(('BLAKE2s', hashlib.blake2s(seed.encode(), digest_size=32).hexdigest()))

    # 6: RIPEMD160 + padding
    if seed:
        ripemd = hashlib.new('ripemd160', seed.encode()).hexdigest()
        padded = ripemd + '0' * 24  # Pad to 64 hex chars
        keys.append(('RIPEMD160+pad', padded))

    # ========== SEED TRANSFORMATIONS ==========

    # 7: Seed reversed
    if seed:
        keys.append(('Seed Reversed', hashlib.sha256(seed[::-1].encode()).hexdigest()))

    # 8: Seed uppercase
    if seed:
        keys.append(('Seed Upper', hashlib.sha256(seed.upper().encode()).hexdigest()))

    # 9: Seed + Block number
    if seed:
        combined = seed + str(block)
        keys.append(('Seed+Block', hashlib.sha256(combined.encode()).hexdigest()))

    # 10: Seed XOR with CFB numbers
    if seed and len(seed) > 28:
        cfb_nums = [27, 283, 47, 137, 121]
        result = []
        for i, char in enumerate(seed[:28]):
            xor_val = ord(char) ^ cfb_nums[i % len(cfb_nums)]
            result.append(chr(xor_val % 128 + 32))  # Keep printable
        xored = ''.join(result)
        keys.append(('Seed XOR CFB', hashlib.sha256(xored.encode()).hexdigest()))

    # ========== BLOCK NUMBER TRANSFORMATIONS ==========

    # 11: Block * 27
    keys.append(('Block×27', hashlib.sha256(str(block * 27).encode()).hexdigest()))

    # 12: Block * 283
    keys.append(('Block×283', hashlib.sha256(str(block * 283).encode()).hexdigest()))

    # 13: Block ^ 2
    keys.append(('Block²', hashlib.sha256(str(block ** 2).encode()).hexdigest()))

    # 14: Block * 47² (formula pattern)
    keys.append(('Block×47²', hashlib.sha256(str(block * 47 * 47).encode()).hexdigest()))

    # ========== CFB MATHEMATICAL PATTERNS ==========

    # 15: (Block + 27) * 283
    formula = (block + 27) * 283
    keys.append(('(Block+27)×283', hashlib.sha256(str(formula).encode()).hexdigest()))

    # 16: Block² + 137
    formula = (block ** 2) + 137
    keys.append(('Block²+137', hashlib.sha256(str(formula).encode()).hexdigest()))

    # 17: (Block * 47) + 121
    formula = (block * 47) + 121
    keys.append(('Block×47+121', hashlib.sha256(str(formula).encode()).hexdigest()))

    # ========== SEQUENCE #8 VARIANTS ==========

    # 18: Block in Sequence #8 context
    if 10 <= block <= 24:
        seq_position = block - 10
        keys.append(('Seq8 Position', hashlib.sha256(str(seq_position).encode()).hexdigest()))

    # 19: Block + Sequence sum (243)
    keys.append(('Block+243', hashlib.sha256(str(block + 243).encode()).hexdigest()))

    # 20: Block * 14 (Sequence span)
    keys.append(('Block×14', hashlib.sha256(str(block * 14).encode()).hexdigest()))

    # ========== GENESIS TOKEN VARIANTS ==========

    # 21: Block + Genesis timestamp
    genesis_ts = 1730588571
    keys.append(('Block+GenesisTS', hashlib.sha256(str(block + genesis_ts).encode()).hexdigest()))

    # 22: Block * (Genesis TS mod 27)
    # Genesis TS mod 27 = 0, so use 27
    keys.append(('Block×27(GenMod)', hashlib.sha256(str(block * 27).encode()).hexdigest()))

    # ========== 1CFB ADDRESS VARIANTS ==========

    # 23: Block + 1CFB
    cfb_addr = '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg'
    combined = str(block) + cfb_addr
    keys.append(('Block+1CFB', hashlib.sha256(combined.encode()).hexdigest()))

    # 24: SHA3 of 1CFB
    keys.append(('1CFB SHA3', hashlib.sha3_256(cfb_addr.encode()).hexdigest()))

    # ========== ANNA BOT PATTERNS ==========

    # 25: row, col from seed
    if seed:
        coord_hash = hashlib.sha256(seed.encode()).digest()
        row = int.from_bytes(coord_hash[:4], 'big') % 128
        col = int.from_bytes(coord_hash[4:8], 'big') % 128
        anna_val = f"{row},{col}"
        keys.append(('Anna Coords', hashlib.sha256(anna_val.encode()).hexdigest()))

    # 26-30: Try collision values as seeds
    collision_values = [-114, -113, 14, 110, 60]
    for i, val in enumerate(collision_values):
        keys.append((f'Collision {val}', hashlib.sha256(str(val).encode()).hexdigest()))

    # ========== MULTI-HASH CHAINS ==========

    # 31: Triple SHA256
    if seed:
        h1 = hashlib.sha256(seed.encode()).digest()
        h2 = hashlib.sha256(h1).digest()
        h3 = hashlib.sha256(h2).hexdigest()
        keys.append(('SHA256³', h3))

    # 32: SHA256 → SHA3
    if seed:
        h1 = hashlib.sha256(seed.encode()).digest()
        h2 = hashlib.sha3_256(h1).hexdigest()
        keys.append(('SHA256→SHA3', h2))

    # 33: BLAKE2 → SHA256
    if seed:
        h1 = hashlib.blake2b(seed.encode(), digest_size=32).digest()
        h2 = hashlib.sha256(h1).hexdigest()
        keys.append(('BLAKE2→SHA256', h2))

    # ========== POCZ ISSUER VARIANTS ==========

    pocz = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

    # 34: POCZ + Block
    keys.append(('POCZ+Block', hashlib.sha256((pocz + str(block)).encode()).hexdigest()))

    # 35: POCZ SHA3
    keys.append(('POCZ SHA3', hashlib.sha3_256(pocz.encode()).hexdigest()))

    # 36: POCZ XOR Block
    xor_result = block ^ len(pocz)
    keys.append(('POCZ XOR Block', hashlib.sha256(str(xor_result).encode()).hexdigest()))

    # ========== FORMULA VARIATIONS ==========

    # 37: 625284 + Block
    keys.append(('Formula+Block', hashlib.sha256(str(625284 + block).encode()).hexdigest()))

    # 38: 625284 * Block
    keys.append(('Formula×Block', hashlib.sha256(str(625284 * block).encode()).hexdigest()))

    # 39: (625284 mod Block) if block > 0
    if block > 0:
        keys.append(('Formula mod Block', hashlib.sha256(str(625284 % block).encode()).hexdigest()))

    # 40: 283 * 47² + 137 + Block
    formula = 283 * 47 * 47 + 137 + block
    keys.append(('FullFormula+Block', hashlib.sha256(str(formula).encode()).hexdigest()))

    # ========== TIMESTAMP MAGIC ==========

    # 41-45: Pre-Genesis + variations
    pre_genesis = 1221069728
    keys.append(('PreGen+Block', hashlib.sha256(str(pre_genesis + block).encode()).hexdigest()))
    keys.append(('PreGen×Block', hashlib.sha256(str(pre_genesis * block).encode()).hexdigest()))
    keys.append(('PreGen mod 121', hashlib.sha256(str(pre_genesis % 121).encode()).hexdigest()))
    keys.append(('PreGen mod 43', hashlib.sha256(str(pre_genesis % 43).encode()).hexdigest()))

    # ========== MORE CREATIVE METHODS ==========

    # 46: Seed bytes as numbers
    if seed:
        seed_nums = [ord(c) for c in seed[:32]]
        combined = ''.join(str(n) for n in seed_nums)
        keys.append(('Seed as Numbers', hashlib.sha256(combined.encode()).hexdigest()))

    # 47: Fibonacci at block position
    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    fib_val = fib(block)
    keys.append(('Fibonacci(Block)', hashlib.sha256(str(fib_val).encode()).hexdigest()))

    # 48: Prime number at block position
    def nth_prime(n):
        primes = []
        num = 2
        while len(primes) < n:
            is_prime = True
            for p in primes:
                if num % p == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(num)
            num += 1
        return primes[-1] if primes else 2

    prime_val = nth_prime(block)
    keys.append(('Prime(Block)', hashlib.sha256(str(prime_val).encode()).hexdigest()))

    # 49: Block in binary
    binary = bin(block)[2:]
    keys.append(('Block Binary', hashlib.sha256(binary.encode()).hexdigest()))

    # 50: Block in hex
    hexa = hex(block)[2:]
    keys.append(('Block Hex', hashlib.sha256(hexa.encode()).hexdigest()))

    return keys

def main():
    print("\n🔥 ADVANCED KEY DERIVATION - 50+ METHODS PER ADDRESS! 🔥\n")

    patoshi, seeds = load_data()

    print(f"Loaded {len(patoshi):,} Patoshi addresses")
    print(f"Loaded {len(seeds):,} Qubic seeds\n")

    matches = []
    total_tested = 0

    for i, record in enumerate(patoshi[:10], 1):
        block = record.get('blockHeight', 0)
        known_pubkey = record.get('pubkey', '')

        if not known_pubkey:
            continue

        seed_data = seeds[block-1] if block <= len(seeds) else {}
        seed = seed_data.get('seed', '')

        print(f"Testing Block {block} with 50+ methods...")

        # Get all advanced key candidates
        key_candidates = advanced_derivations(seed, block)
        total_tested += len(key_candidates)

        # Test each one
        for method_name, private_key_hex in key_candidates:
            derived_pubkey = private_key_to_public_key(private_key_hex)

            if derived_pubkey and derived_pubkey.lower() == known_pubkey.lower():
                print(f"\n🔥🔥🔥 MATCH FOUND! 🔥🔥🔥")
                print(f"Block: {block}")
                print(f"Method: {method_name}")
                print(f"Private Key: {private_key_hex}")
                print(f"🚀 ACCESS UNLOCKED! 🚀\n")

                matches.append({
                    'block': block,
                    'method': method_name,
                    'private_key': private_key_hex
                })

        print(f"  ✓ Tested {len(key_candidates)} methods for Block {block}")

    print(f"\n{'='*80}")
    print(f"TOTAL METHODS TESTED: {total_tested}")
    print(f"MATCHES FOUND: {len(matches)}")

    if matches:
        print(f"\n🎯 SAVING MATCHES TO FILE!")
        with open('ADVANCED_KEY_MATCHES.json', 'w') as f:
            json.dump(matches, f, indent=2)
    else:
        print(f"\n⚠️  No matches yet - but we're getting closer!")
        print(f"Next: Try even MORE combinations! 🚀")

    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
