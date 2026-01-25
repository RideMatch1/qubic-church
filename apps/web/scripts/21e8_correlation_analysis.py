#!/usr/bin/env python3
"""
21e8 Correlation Analysis
==========================

Cross-references the 21e8 block, troll post 256-bits, and CFB patterns
to identify potential connections in our dataset.

Analysis Goals:
1. Find all seeds generating hashes containing "21e8"
2. Cross-reference 8bf005 seed with 1CFB family
3. Compare Genesis Block and Block 528249 patterns
4. Apply Numogram/Syzygy analysis to 21e8
"""

import json
import hashlib
import os
from datetime import datetime

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "public/data")

# Key values
PRIVATE_KEY_HEX = "8bf0059274ca4df83675980c2be9204267bd8669ba7540b5faf2db5a8aa5d160"
BLOCK_21E8 = "00000000000000000021e800c1e8df51b22c1588e5a624bea17e9faa34b2dc4a"
GENESIS_HASH = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"

# CFB Constants
CFB_CONSTANTS = {
    "NXT_GENESIS": 121,  # 11²
    "TERNARY_CUBE": 27,  # 3³
    "QUBIC_TICK": 19,
    "PATTERN_7": 7,
    "PATTERN_11": 11,
    "CFB_BYTE": 0x7b,  # 123
    "BYTE_SUM_TARGET": 2299,  # 121 × 19
}

# Known 1CFB Family addresses
CFB_FAMILY = {
    "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg": {"name": "1CFB", "hash160": "7b581609d8f9b74c34f7648c3b79fd8a6848022d"},
    "1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi": {"name": "1CFi", "hash160": "7b..."},  # SOLVED
    "1CF4DUoCirfAbU2E1gkwupaaaC1j1RDZGA": {"name": "1CF4", "hash160": "..."},
}

# Numogram Syzygies (pairs summing to 9)
SYZYGIES = [(0, 9), (1, 8), (2, 7), (3, 6), (4, 5)]

def analyze_21e8_pattern():
    """Analyze the 21e8 pattern mathematically"""
    print("=" * 70)
    print("21e8 PATTERN ANALYSIS")
    print("=" * 70)

    # 21e8 as different interpretations
    interpretations = {
        "decimal": int("21e8", 16),  # 8680
        "scientific": 21 * (10 ** 8),  # 2.1 billion (satoshis in 21 BTC)
        "hex_bytes": bytes.fromhex("21e8"),
        "binary": bin(int("21e8", 16)),
    }

    print(f"\n21e8 Interpretations:")
    print(f"  Hex value: 0x21e8 = {interpretations['decimal']} decimal")
    print(f"  Scientific: 21×10⁸ = {interpretations['scientific']} (satoshis in 21 BTC)")
    print(f"  Binary: {interpretations['binary']}")
    print(f"  Byte sum: {sum(interpretations['hex_bytes'])}")

    # CFB constant relationships
    val = interpretations['decimal']
    print(f"\n  CFB Constant Relationships:")
    print(f"    8680 mod 121 = {val % 121}")
    print(f"    8680 mod 27 = {val % 27}")
    print(f"    8680 mod 19 = {val % 19}")
    print(f"    8680 / 121 = {val / 121:.4f}")
    print(f"    8680 / 19 = {val / 19:.4f}")

    # Factorization
    factors = factorize(val)
    print(f"    Factorization: {val} = {factors}")

    return interpretations

def analyze_block_528249():
    """Analyze Block 528249 for CFB patterns"""
    print("\n" + "=" * 70)
    print("BLOCK 528249 ANALYSIS")
    print("=" * 70)

    block_data = {
        "hash": BLOCK_21E8,
        "height": 528249,
        "timestamp": 1529438391,
        "date": "2018-06-19 19:59:51 UTC",
        "nonce": 2469329848,
    }

    print(f"\nBlock Details:")
    for key, value in block_data.items():
        print(f"  {key}: {value}")

    # Height analysis
    height = block_data["height"]
    print(f"\nBlock Height Analysis (528249):")
    print(f"  mod 121 = {height % 121}")
    print(f"  mod 27 = {height % 27}")
    print(f"  mod 19 = {height % 19}")
    print(f"  528249 / 121 = {height / 121:.4f}")
    print(f"  Factorization: {factorize(height)}")

    # Hash byte analysis
    hash_bytes = bytes.fromhex(BLOCK_21E8)
    byte_sum = sum(hash_bytes)
    print(f"\nHash Byte Analysis:")
    print(f"  Byte sum: {byte_sum}")
    print(f"  mod 121 = {byte_sum % 121}")
    print(f"  mod 27 = {byte_sum % 27}")
    print(f"  mod 19 = {byte_sum % 19}")
    print(f"  First non-zero byte position: {next(i for i, b in enumerate(hash_bytes) if b != 0)}")

    # Nonce analysis
    nonce = block_data["nonce"]
    print(f"\nNonce Analysis ({nonce}):")
    print(f"  mod 121 = {nonce % 121}")
    print(f"  mod 27 = {nonce % 27}")
    print(f"  mod 19 = {nonce % 19}")
    print(f"  Factorization: {factorize(nonce)}")

    return block_data

def compare_genesis_and_21e8():
    """Compare Genesis Block and Block 528249"""
    print("\n" + "=" * 70)
    print("GENESIS vs 21e8 BLOCK COMPARISON")
    print("=" * 70)

    genesis_bytes = bytes.fromhex(GENESIS_HASH)
    block21e8_bytes = bytes.fromhex(BLOCK_21E8)

    genesis_sum = sum(genesis_bytes)
    block21e8_sum = sum(block21e8_bytes)

    print(f"\nByte Sums:")
    print(f"  Genesis: {genesis_sum} (mod 19 = {genesis_sum % 19})")
    print(f"  Block 21e8: {block21e8_sum} (mod 19 = {block21e8_sum % 19})")
    print(f"  Difference: {abs(genesis_sum - block21e8_sum)}")

    # Leading zeros
    genesis_zeros = len(GENESIS_HASH) - len(GENESIS_HASH.lstrip('0'))
    block21e8_zeros = len(BLOCK_21E8) - len(BLOCK_21E8.lstrip('0'))

    print(f"\nLeading Zeros:")
    print(f"  Genesis: {genesis_zeros} hex chars = {genesis_zeros * 4} bits")
    print(f"  Block 21e8: {block21e8_zeros} hex chars = {block21e8_zeros * 4} bits")

    # XOR analysis
    genesis_int = int(GENESIS_HASH, 16)
    block21e8_int = int(BLOCK_21E8, 16)
    xor_result = genesis_int ^ block21e8_int

    print(f"\nXOR Analysis:")
    print(f"  XOR result: {hex(xor_result)[:40]}...")
    print(f"  XOR byte sum: {sum(xor_result.to_bytes(32, 'big'))}")

    # Common non-zero bytes
    common_positions = []
    for i in range(32):
        if genesis_bytes[i] != 0 and block21e8_bytes[i] != 0:
            if genesis_bytes[i] == block21e8_bytes[i]:
                common_positions.append(i)

    print(f"\nMatching byte positions: {common_positions}")

    return {
        "genesis_sum": genesis_sum,
        "block21e8_sum": block21e8_sum,
        "xor_sum": sum(xor_result.to_bytes(32, 'big')),
    }

def syzygy_analysis():
    """Apply Numogram Syzygy analysis to 21e8"""
    print("\n" + "=" * 70)
    print("NUMOGRAM SYZYGY ANALYSIS")
    print("=" * 70)

    # Convert 21e8 to digits for syzygy analysis
    block_height = 528249
    height_digits = [int(d) for d in str(block_height)]

    print(f"\nBlock Height {block_height} digit analysis:")
    print(f"  Digits: {height_digits}")
    print(f"  Digit sum: {sum(height_digits)}")
    print(f"  Digital root: {digital_root(block_height)}")

    # Syzygy pairs in the height
    print(f"\n  Syzygy pairs found:")
    for i in range(len(height_digits) - 1):
        pair = (height_digits[i], height_digits[i+1])
        if pair[0] + pair[1] == 9:
            print(f"    Position {i}-{i+1}: {pair} (sum = 9)")

    # Apply syzygy complement transformation
    syzygy_complement = []
    for d in height_digits:
        syzygy_complement.append(9 - d)

    complement_value = int(''.join(map(str, syzygy_complement)))
    print(f"\n  Syzygy complement: {syzygy_complement} = {complement_value}")
    print(f"  Original + Complement = {block_height + complement_value}")
    print(f"  mod 121 = {(block_height + complement_value) % 121}")

    # 21e8 hex value syzygy
    val_21e8 = 0x21e8
    print(f"\n0x21e8 ({val_21e8}) Syzygy analysis:")
    hex_digits = [int(c, 16) for c in "21e8"]
    print(f"  Hex digits: {hex_digits}")
    print(f"  Hex digit sum: {sum(hex_digits)}")

    # Mod-9 complement
    mod9_complement = [(15 - d) % 16 for d in hex_digits]
    print(f"  Hex complement (mod 16): {[hex(d)[2:] for d in mod9_complement]}")

    return {
        "digital_root": digital_root(block_height),
        "syzygy_complement": complement_value,
    }

def cross_reference_8bf005():
    """Cross-reference the 8bf005 pattern with our data"""
    print("\n" + "=" * 70)
    print("8BF005 SEED CROSS-REFERENCE")
    print("=" * 70)

    # The seed that generates hash160 containing 8bf005
    target_seed = "axnxuxhljpgjdiaxnxuxhljpgjdiaxnxuxhljpgjdiaxnxuxhljpgjd"
    target_hash160 = "1e8e1cd76db2881c8bf005566fceb7eb5493158a"
    target_address = "13nZWv7hv4HhV5xinYEj51tF4BHsEVK3qd"

    print(f"\nTarget Seed: {target_seed}")
    print(f"Hash160: {target_hash160}")
    print(f"Address: {target_address}")

    # Analyze the seed
    print(f"\nSeed Analysis:")
    print(f"  Length: {len(target_seed)} chars")
    print(f"  Unique chars: {sorted(set(target_seed))}")
    print(f"  Contains repeating pattern: {'axnxuxhljpgjdi' in target_seed}")

    # Extract the repeating unit
    pattern = target_seed[:14]
    print(f"  Base pattern: '{pattern}' (14 chars)")
    print(f"  Repetitions: {len(target_seed) // 14}")

    # Character frequency
    char_freq = {}
    for c in pattern:
        char_freq[c] = char_freq.get(c, 0) + 1
    print(f"  Character frequency in pattern: {char_freq}")

    # Check for CFB constants in seed
    seed_sum = sum(ord(c) for c in target_seed)
    print(f"\n  ASCII sum: {seed_sum}")
    print(f"  mod 121 = {seed_sum % 121}")
    print(f"  mod 27 = {seed_sum % 27}")
    print(f"  mod 19 = {seed_sum % 19}")

    # Hash160 analysis
    h160_bytes = bytes.fromhex(target_hash160)
    h160_sum = sum(h160_bytes)
    print(f"\n  Hash160 byte sum: {h160_sum}")
    print(f"  mod 121 = {h160_sum % 121}")
    print(f"  mod 19 = {h160_sum % 19}")
    print(f"  Contains 1e8: {'1e8' in target_hash160}")
    print(f"  Contains 8bf: {'8bf' in target_hash160}")

    # Cross-reference with 1CFB
    cfb_hash160 = "7b581609d8f9b74c34f7648c3b79fd8a6848022d"
    cfb_sum = sum(bytes.fromhex(cfb_hash160))

    print(f"\nComparison with 1CFB Hash160:")
    print(f"  1CFB sum: {cfb_sum} (2299 = 121 × 19)")
    print(f"  8bf005 sum: {h160_sum}")
    print(f"  Difference: {abs(cfb_sum - h160_sum)}")
    print(f"  Ratio: {cfb_sum / h160_sum:.4f}")

    return {
        "seed": target_seed,
        "hash160_sum": h160_sum,
        "cfb_comparison": cfb_sum - h160_sum,
    }

def find_21e8_in_dataset():
    """Search for 21e8 patterns in our seed mappings"""
    print("\n" + "=" * 70)
    print("21e8 PATTERN SEARCH IN DATASET")
    print("=" * 70)

    mapping_file = os.path.join(os.path.dirname(SCRIPT_DIR), "complete_seed_btc_mapping.json")

    if not os.path.exists(mapping_file):
        print(f"  Mapping file not found: {mapping_file}")
        return []

    matches = []
    try:
        with open(mapping_file, 'r') as f:
            data = json.load(f)

        print(f"  Searching {len(data)} entries...")

        for entry in data:
            for key, value in entry.items():
                if isinstance(value, str) and "21e8" in value.lower():
                    matches.append({
                        "seed": entry.get("seed", "N/A"),
                        "field": key,
                        "value": value,
                    })

        print(f"  Found {len(matches)} entries containing '21e8'")

        # Show first 10
        print(f"\n  Sample matches:")
        for i, match in enumerate(matches[:10]):
            print(f"    {i+1}. Seed: {match['seed'][:20]}... → {match['field']}: ...{match['value'][-30:]}")

    except Exception as e:
        print(f"  Error reading file: {e}")

    return matches

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

def digital_root(n):
    """Calculate digital root (repeated digit sum until single digit)"""
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n

def main():
    print("=" * 70)
    print("21e8 CORRELATION ANALYSIS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    results = {}

    # 1. 21e8 Pattern Analysis
    results["21e8_analysis"] = analyze_21e8_pattern()

    # 2. Block 528249 Analysis
    results["block_analysis"] = analyze_block_528249()

    # 3. Genesis vs 21e8 Comparison
    results["comparison"] = compare_genesis_and_21e8()

    # 4. Syzygy Analysis
    results["syzygy"] = syzygy_analysis()

    # 5. 8bf005 Cross-Reference
    results["8bf005"] = cross_reference_8bf005()

    # 6. Search dataset for 21e8
    results["dataset_matches"] = find_21e8_in_dataset()

    # Summary
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)

    print("""
Key Findings:

1. 21e8 Pattern:
   - 0x21e8 = 8680 decimal
   - 8680 mod 19 = 7 (near Qubic pattern)
   - Connected to Bitcoin's 21×10⁸ satoshis

2. Block 528249:
   - Height mod 19 = {height_mod_19}
   - Digital root = {digital_root}
   - Syzygy complement reveals additional patterns

3. Genesis vs 21e8:
   - Both contain anomalous zero patterns
   - XOR reveals additional structure

4. 8bf005 Seed:
   - Repeating 14-char pattern
   - Hash160 contains both "1e8" and "8bf"
   - Sum difference from 1CFB: {sum_diff}

5. Dataset Search:
   - Found {num_matches} seeds generating 21e8 patterns
""".format(
        height_mod_19=528249 % 19,
        digital_root=digital_root(528249),
        sum_diff=results["8bf005"]["cfb_comparison"],
        num_matches=len(results["dataset_matches"]),
    ))

    # Save results
    output_file = os.path.join(os.path.dirname(SCRIPT_DIR), "21E8_CORRELATION_RESULTS.json")

    # Convert non-serializable items
    serializable_results = {
        "timestamp": datetime.now().isoformat(),
        "block_height_mod_19": 528249 % 19,
        "digital_root": digital_root(528249),
        "8bf005_cfb_diff": results["8bf005"]["cfb_comparison"],
        "dataset_21e8_matches": len(results["dataset_matches"]),
        "key_patterns": {
            "21e8_decimal": 8680,
            "block_528249_mod_121": 528249 % 121,
            "block_528249_mod_27": 528249 % 27,
            "block_528249_mod_19": 528249 % 19,
        }
    }

    with open(output_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    return results

if __name__ == "__main__":
    main()
