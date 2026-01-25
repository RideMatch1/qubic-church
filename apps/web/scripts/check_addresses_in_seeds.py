#!/usr/bin/env python3
"""
🔥 CHECK ADDRESSES IN QUBIC SEEDS DATABASE 🔥
===============================================

BURN ADDRESS: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFXIB
(55 A's + FXIB = 60 chars)

Check if the given addresses are in our 24k qubic seeds!
"""

import json

# Target addresses from user
TARGET_ADDRESSES = [
    "YIROSMBRZQGEACLVKWHTDMJHMLICLNVIHHNQVNUNMEJGHBLYNIFEZYDHDCQH",
    "IEMAMSSZWXIZBACENIUSHDZSBOCDTKWJNTKWFOBWUBROFRCTUQYNSBYDNXBI",
    "ZDTOOKKPTJIFUCTTCHBOHSKVSBRCPZDKDSCVTXPHRESOVAHETHZMXMVBRMSJ",
    "CCNCYCDWBXFSTAKYJHRMEMWDBOTBBNHWWJDBKZJIPBACFDUZFSUKYJIBTSKN",
    "TKTMQAOWTUWANBYQSOPSQJOJTXXBTDPWXDXLJMTFMDUKYYHRVWQNWQJAZFKL",
    "VVLTPLHLYRIIUFQQOOSJWKTNFNOCDIJMLMCVTQIIAFSHGKOMJIJGMAQEJTWF",
    "ONXWEBHCEKWVGDUFULAWGIRBGDTAONNNSEMXPKLFJFTTTOZZYZXRALLGAQIE",
    "CQYCHCDMZSTNOEAYKGACJJGSYIJBNEVAUBGICWTTOFCXSDCFVFORHVYBVVTC",
    "DAMTLNJBDCLKECJMREYFWUODUIXBCNYIWZTTXVSNIDUAGUCHWDYEGCUCOXSI",
]

BURN_ADDRESS = "A" * 55 + "FXIB"

def load_qubic_data():
    """Load qubic seeds and addresses"""
    with open('public/data/qubic-seeds.json', 'r') as f:
        data = json.load(f)
    return data.get('records', [])

def analyze_address_patterns(addresses):
    """Analyze patterns in the addresses"""
    print("="*80)
    print("🔍 ADDRESS PATTERN ANALYSIS")
    print("="*80)
    print()

    for i, addr in enumerate(addresses, 1):
        print(f"\nAddress {i}: {addr}")
        print(f"  Length: {len(addr)}")

        # Character frequency
        from collections import Counter
        freq = Counter(addr)
        most_common = freq.most_common(5)
        print(f"  Most common chars: {', '.join(f'{c}({n})' for c, n in most_common)}")

        # Repeating patterns
        repeats = []
        for j in range(len(addr)-1):
            if addr[j] == addr[j+1]:
                repeats.append(f"{j}:{addr[j]}{addr[j+1]}")
        if repeats:
            print(f"  Consecutive repeats: {', '.join(repeats[:5])}")

        # Sum of numeric values
        char_sum = sum(ord(c) - ord('A') for c in addr if c.isalpha())
        print(f"  Char sum: {char_sum}")
        print(f"  Mod 27: {char_sum % 27}")
        print(f"  Mod 47: {char_sum % 47}")

def check_in_database(target_addresses):
    """Check if addresses are in our database"""
    print("\n" + "="*80)
    print("🔍 CHECKING AGAINST 24K QUBIC SEEDS DATABASE")
    print("="*80)
    print()

    records = load_qubic_data()
    print(f"Loaded {len(records):,} Qubic seed records")
    print()

    # Build lookup sets
    seeds_set = set()
    identities_set = set()

    for record in records:
        seed = record.get('seed', '')
        documented = record.get('documentedIdentity', '')
        real = record.get('realIdentity', '')

        if seed:
            seeds_set.add(seed.upper())
        if documented:
            identities_set.add(documented.upper())
        if real:
            identities_set.add(real.upper())

    print(f"Total unique seeds: {len(seeds_set):,}")
    print(f"Total unique identities: {len(identities_set):,}")
    print()

    # Check each target
    matches = []

    for i, addr in enumerate(target_addresses, 1):
        print(f"\nChecking Address {i}: {addr[:30]}...")

        # Check in seeds
        if addr.upper() in seeds_set:
            print(f"  🔥 FOUND IN SEEDS! 🔥")
            matches.append(('seed', addr))
        # Check in identities
        elif addr.upper() in identities_set:
            print(f"  🔥 FOUND IN IDENTITIES! 🔥")
            matches.append(('identity', addr))
        else:
            print(f"  ❌ Not found")

    return matches

def find_matches_and_details(matches, records):
    """Get full details for matches"""
    if not matches:
        return

    print("\n" + "="*80)
    print("📋 MATCH DETAILS")
    print("="*80)
    print()

    for match_type, addr in matches:
        print(f"\n🔥 MATCH: {addr}")
        print(f"   Type: {match_type.upper()}")

        # Find in records
        for record in records:
            seed = record.get('seed', '').upper()
            documented = record.get('documentedIdentity', '').upper()
            real = record.get('realIdentity', '').upper()

            if addr.upper() in [seed, documented, real]:
                print(f"\n   Record ID: {record.get('id', 'N/A')}")
                print(f"   Seed: {record.get('seed', 'N/A')}")
                print(f"   Documented Identity: {record.get('documentedIdentity', 'N/A')}")
                print(f"   Real Identity: {record.get('realIdentity', 'N/A')}")
                break

def analyze_burn_address():
    """Analyze the burn address"""
    print("\n" + "="*80)
    print("🔥 BURN ADDRESS ANALYSIS")
    print("="*80)
    print()

    print(f"Burn Address: {BURN_ADDRESS}")
    print(f"Length: {len(BURN_ADDRESS)}")
    print(f"Pattern: {'A' * 55} + 'FXIB'")
    print()

    # Character sum
    char_sum = sum(ord(c) - ord('A') for c in BURN_ADDRESS)
    print(f"Character sum: {char_sum}")
    print(f"Mod 27: {char_sum % 27}")
    print(f"Mod 47: {char_sum % 47}")
    print()

    # 'A' = 0 in our encoding, so 55 A's = 0
    # F = 5, X = 23, I = 8, B = 1
    fxib_sum = 5 + 23 + 8 + 1
    print(f"FXIB segment sum: {fxib_sum} (F=5, X=23, I=8, B=1)")
    print(f"FXIB mod 27: {fxib_sum % 27}")
    print()

    print("💡 Significance:")
    print("   - 55 A's = all zeros")
    print("   - FXIB = the only non-zero part")
    print("   - Classic 'burn address' pattern")
    print("   - Tokens sent here are permanently locked")

def check_address_relationships():
    """Check if addresses have mathematical relationships"""
    print("\n" + "="*80)
    print("🔢 ADDRESS RELATIONSHIPS")
    print("="*80)
    print()

    print("Checking for patterns between addresses...")
    print()

    # Check if they're sequential or related
    for i in range(len(TARGET_ADDRESSES) - 1):
        addr1 = TARGET_ADDRESSES[i]
        addr2 = TARGET_ADDRESSES[i + 1]

        # Count different characters
        diff_count = sum(1 for a, b in zip(addr1, addr2) if a != b)
        print(f"Address {i+1} vs {i+2}: {diff_count}/60 chars different")

def main():
    print("\n" + "="*80)
    print("🔥 QUBIC ADDRESS DATABASE CHECK 🔥")
    print("="*80)
    print()

    analyze_burn_address()
    analyze_address_patterns(TARGET_ADDRESSES)
    matches = check_in_database(TARGET_ADDRESSES)

    if matches:
        records = load_qubic_data()
        find_matches_and_details(matches, records)

        print("\n" + "="*80)
        print("✅ SUCCESS! FOUND MATCHES IN DATABASE!")
        print("="*80)
        print()
        print(f"Total matches: {len(matches)}")
        print()
        print("🎯 NEXT STEPS:")
        print("1. Get the seeds for matched addresses")
        print("2. Use K12 derivation to generate private keys")
        print("3. Import into Qubic wallet")
        print("4. Check if they have access to Genesis issuer")
        print("5. CLAIM THE REWARD! 🚀💰")
    else:
        print("\n" + "="*80)
        print("⚠️  NO DIRECT MATCHES FOUND")
        print("="*80)
        print()
        print("These addresses are NOT in our seed database.")
        print()
        print("💡 POSSIBLE MEANINGS:")
        print("1. These are NEW addresses (not from the 24k seeds)")
        print("2. They're generated differently (not K12 from seeds)")
        print("3. They're transaction addresses (smart contract related)")
        print("4. They're related to Genesis token distribution")
        print()
        print("🎯 NEXT APPROACHES:")
        print("1. Check if these are Computor addresses (676 of them)")
        print("2. Look for these on Qubic explorer")
        print("3. Check if they're smart contract addresses")
        print("4. Analyze their transaction history")

    check_address_relationships()

    # Save results
    results = {
        'burn_address': BURN_ADDRESS,
        'target_addresses': TARGET_ADDRESSES,
        'matches_found': len(matches) if matches else 0,
        'matches': matches if matches else []
    }

    with open('address_check_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n✓ Results saved to: address_check_results.json")
    print()

if __name__ == "__main__":
    main()
