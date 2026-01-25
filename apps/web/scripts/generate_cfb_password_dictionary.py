#!/usr/bin/env python3
"""
CFB Password Dictionary Generator
==================================

Generates comprehensive password dictionary based on ALL discovered CFB patterns.
Uses mathematical signatures, project names, formulas, and combinations.

Usage:
    python3 generate_cfb_password_dictionary.py

Output:
    cfb_password_dictionary.txt (sorted, unique passwords)
"""

import hashlib
import itertools
from typing import List, Set

def number_to_seed(num: int) -> str:
    """Convert number to Qubic seed format (26 lowercase letters)"""
    h = hashlib.sha256(str(num).encode()).digest()
    seed = ''
    for byte in h[:28]:
        seed += chr(ord('a') + (byte % 26))
    return seed

def generate_cfb_dictionary() -> List[str]:
    """Generate comprehensive CFB password dictionary"""

    passwords: Set[str] = set()

    # ============================================================================
    # CATEGORY 1: Pure CFB Numbers
    # ============================================================================

    cfb_numbers = [
        # Primary signatures
        "27", "283", "47", "137", "121", "43", "7", "19", "14",

        # Formula components
        "625284",  # 283 * 47^2 + 137
        "2209",    # 47^2
        "47squared",

        # Patoshi amounts
        "1100000", "800000", "400000", "1200000",
        "110", "80", "40", "120",  # In 10k BTC

        # Block numbers
        "576", "969", "283block",

        # Timestamps
        "1221069728",  # Pre-Genesis
        "1730588571",  # Genesis Token

        # Matrix
        "2692", "211", "214", "684", "9621", "128",

        # 14 test transactions
        "14", "140", "1410", "14test", "10btc",

        # Anna collision values
        "-114", "114", "-113", "113", "110", "60", "125", "78", "26",

        # Combinations
        "27283", "28347", "283137", "47121", "27121",
        "27+283", "47*47", "121*121", "14*10",
    ]

    passwords.update(cfb_numbers)

    # ============================================================================
    # CATEGORY 2: Project Names & Identities
    # ============================================================================

    project_names = [
        # Projects
        "qubic", "iota", "nxt", "bytecoin", "aigarth", "anna",
        "arb", "arbproxy", "arboracle",

        # Identity
        "cfb", "comefrombeyond", "satoshi", "patoshi",
        "sergey", "ivancheglo", "maria", "bcnext",

        # Combinations with 27
        "qubic27", "iota27", "cfb27", "anna27", "aigarth27",
        "satoshi27", "patoshi27", "nxt27", "bytecoin27",
    ]

    passwords.update(project_names)

    # ============================================================================
    # CATEGORY 3: Mathematical Formulas
    # ============================================================================

    formulas = [
        # Primary formula variations
        "283*47^2+137",
        "283*47*47+137",
        "283x47^2+137",
        "283x47x47+137",
        "283*2209+137",
        "(283*47^2)+137",

        # Result
        "625284",
        "625284=283*47^2+137",

        # Components
        "47squared",
        "47^2",
        "2209",
    ]

    passwords.update(formulas)

    # ============================================================================
    # CATEGORY 4: Address Fragments
    # ============================================================================

    addresses = [
        # 1CFB address
        "1CFBdvaiZgZ",
        "1CFBd",
        "dvaiZgZ",
        "dvaiZgZPTZERqnezAtDQJuGHKoHSzg",

        # Parts
        "1CFB", "CFB", "dvai", "ZgZ", "PTZER",

        # With numbers
        "1CFB27", "1CFBd283", "CFB625284",
    ]

    passwords.update(addresses)

    # ============================================================================
    # CATEGORY 5: Concepts & Phrases
    # ============================================================================

    concepts = [
        # Ternary computing
        "ternary", "ternary27", "helix", "helixgates",
        "ternarylogic", "trinary",

        # Anna's question
        "1+1=-114", "question", "annasquestion",
        "annasplan", "electricity", "vastelectricity",
        "releasedelectricity", "releasedpower",

        # Bridge
        "bridge", "btctoqubic", "qubicbridge",
        "migration", "assetmigration",
        "firstminer", "spendhalf",

        # Cryptography
        "hardcodedkey", "privatekey", "cpuminer",
        "customminer", "artforz", "secretsharing",
        "shamir", "fragments", "multisig",

        # Trolling
        "cfbtroll", "emperor", "wardroids", "swarm",

        # Biblical
        "genesis", "methuselah", "969", "genesis527",

        # Freemason
        "knightoftemple", "templar", "freemason27",
        "27thegree", "33degree",

        # Dates
        "20090103", "20080910", "20260303",
        "jan32009", "sep102008", "mar32026",
    ]

    passwords.update(concepts)

    # ============================================================================
    # CATEGORY 6: Hybrid Combinations (Number + Word)
    # ============================================================================

    numbers_for_hybrid = ["27", "283", "47", "137", "121", "14", "625284"]
    words_for_hybrid = ["qubic", "cfb", "satoshi", "anna", "genesis", "bridge"]
    separators = ["", "-", "_", ".", "*", "^", "+", "=", ":"]

    for num in numbers_for_hybrid:
        for word in words_for_hybrid:
            for sep in separators:
                passwords.add(f"{num}{sep}{word}")
                passwords.add(f"{word}{sep}{num}")

    # ============================================================================
    # CATEGORY 7: Qubic Seed Derivations
    # ============================================================================

    # Convert important numbers to Qubic seed format
    important_numbers = [625284, 283, 27, 47, 137, 121, 14, 1100000]

    for num in important_numbers:
        seed = number_to_seed(num)
        passwords.add(seed)
        passwords.add(seed[:14])  # First half
        passwords.add(seed[14:])  # Second half

    # ============================================================================
    # CATEGORY 8: Advanced Patterns
    # ============================================================================

    advanced = [
        # Multiple component combinations
        "27+283+47+137",
        "27*283*47*137",
        "27-283-47-137",
        "27.283.47.137",

        # Formula components combined
        "283.47.137",
        "47.47.137",
        "2209.137",

        # Transaction patterns
        "14x10btc",
        "140btc",
        "14transactions10btc",

        # Special
        "computor",  # From wallet.dat metadata
        "supercomputer",

        # Full phrases
        "comefrombeyond27283",
        "satoshinakamoto625284",
        "sergeyivancheglo27",
    ]

    passwords.update(advanced)

    # ============================================================================
    # CATEGORY 9: Case Variations (for important ones)
    # ============================================================================

    important_passwords = [
        "qubic", "cfb", "satoshi", "comefrombeyond",
        "aigarth", "anna", "genesis", "bridge"
    ]

    for pwd in important_passwords:
        passwords.add(pwd.lower())
        passwords.add(pwd.upper())
        passwords.add(pwd.capitalize())
        passwords.add(pwd.title())

    # Return sorted unique list
    return sorted(list(passwords))

def main():
    """Generate and save password dictionary"""

    print("="*80)
    print("CFB PASSWORD DICTIONARY GENERATOR")
    print("="*80)
    print()

    print("Generating comprehensive password list...")
    dictionary = generate_cfb_dictionary()

    print(f"✓ Generated {len(dictionary)} unique password candidates")
    print()

    # Save to file
    output_file = "cfb_password_dictionary.txt"
    with open(output_file, 'w') as f:
        for pwd in dictionary:
            f.write(pwd + '\n')

    print(f"✓ Saved to: {output_file}")
    print()

    # Show statistics
    print("Statistics:")
    print(f"  - Total passwords: {len(dictionary)}")
    print(f"  - Shortest: {min(len(p) for p in dictionary)} chars")
    print(f"  - Longest: {max(len(p) for p in dictionary)} chars")
    print(f"  - Average: {sum(len(p) for p in dictionary) / len(dictionary):.1f} chars")
    print()

    # Show first 30
    print("First 30 password candidates:")
    for i, pwd in enumerate(dictionary[:30], 1):
        print(f"  {i:2d}. {pwd}")

    print()
    print("="*80)
    print("READY FOR WALLET.DAT CRACKING")
    print("="*80)
    print()
    print("Next steps:")
    print("1. Run: pywallet --dumpwallet=wallet.txt wallet.dat")
    print("2. Use btcrecover with this dictionary")
    print("3. Or use hashcat with Bitcoin wallet mode")
    print()

if __name__ == "__main__":
    main()
