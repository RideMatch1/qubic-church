#!/usr/bin/env python3
"""
Compare Satoshi 145 addresses with our derived Matrix addresses
to find any overlaps/matches.
"""

import json
import os

# Satoshi 145 addresses (from payloads)
SATOSHI_145_ADDRESSES = [
    "1FbPLPR1XoufBQRPGd9JBLPbKLaGjbax5m",
    "19PYG68GkQ9nY99QeUSyUFy6vWxSyPmXA8",
    "12cFuwo1i3FMhkmJoCN8D4SjeCeRsXf96q",
    "1NWRrbPwHhpp28eQeman5YRV84D2aYe1Yw",
    "1MN82eH1Eu3hznewHFkfsAajknhj78Uup5",
    "1DYHUEjrVE5gyKAn7P13wuRhs6x9EeijBX",
    "1KnT26DTvstGKW7P6BxMBEz8QbKa1iix9C",
    "1K3Qs6bx1wnxCjLcb6jxfjk5kksSJh1WyK",
    "1EAGWgwskQB6o3f1GGsbsWShXPr77QiULE",
    "1NVou7bbmdsdVLEphqZadmX2gbR3QCDPAz",
    "1LBUqhwVyUZ8QZw8UCEbgFQjDFjikL1CSB",
    "1MUzEx65ycYArLPPhxecjKBj4pzMmmjfsu",
    "15RJkhWxG3PP5AzfR1AHVWovZxFt3nFysN",
    "1HTUif11qDAwse9fAXwcdM6o4QPx1hqrio",
    "1EuHqvmmDA6dFRmDyu4rzk8b7VkAmEn7Vq",
    "1FTtHk9sc29yJXWcxKJdKz8C6YHyAQMgwU",
    "1NVTcGUYSP6s4zH95ex86ctATzv8peV5mR",
    "1BzknixNDGfyesGcTbFuyEiD2nyCgEY6rS",
    "1LBmJDqhNboEbyJveb8jB5TNKW5GW7qboN",
    "1GgLxr81StVBpRQPNQKnSF25kyEcpHCnz5",
    "1CpkvbaAhn81Vc4vbx1yr9jGuETvetutBj",
    "14CmMfkbvkfzM1cU68wZMVBwJuSE3iN7Ns",
    "12KFCJLu9D7PzbZgBLuNMj2MpfgzdDJ7kR",
    "1HRhFWoCspCQWfnotkHPc7Joi4XHjRBi8Z",
    "1NdmEC5HxfLSH6Z5xoxQUC8h3sfFoTSSRD",
    "1LXUhX4tXfWGekjucDASYWSsPzYLhYM282",
    "1LK8dnWdxZWxLcdTCpqHRebGwwVcMAPo6X",
    "14RdV6JPBrTVeV5MfFqhGgfsZhMhCFotoQ",
    "1MNaNPHzju2KWAoPshfDBxknSSC5dWkfy",
    "1Kynn7w9MF8hUvqdaHRKY4KLWtwnGdH2Uo",
    "17u34144cabkgraRhwLuzKUANYzf7UB5Jq",
    "1HtMsYAjGKqnehgCXpTz8UkAw44ZLGdAJf",
    "1MwWRaka2dQySercEFgZDenBvWpHw3kvCz",
    "1C6BG4rqDdnaC3t3mzapNu46j9yVv1x4Eo",
    "1Ba8UQfeUVjSRw8uHNSJ9wZqAZCSqweP19",
    "17gzLQ924bNxXBHjgJVBaJEQAKVYTqzaR2",
    "13jEwgtkahPdHQkPTtbHwFm6mvC4Vq71Tj",
    "1X5NfjvcBzdidakWzw37YQPXkBqXr4e6X",
    "12CTHhyJtr49LgoUShbWgebLBviLAFj6nj",
    "1M2iLUvkkm12zE1EjARx46XXA1EZzsfxos",
    "16TqRUQtrBRv9jnpuyVFEH43SRKZhqrCQ7",
    "1BPo3xfuLWD5xZRVU61o9bEbW2XXyWLduY",
    "17fH8bs2eBSxYC4fLQgVPWXw2cV5bNrpon",
    "1DkxqjACGihnBHhiWGuJUMVRco6LHFpovT",
    "1AfE9BbPDPGx8egt5qRBo5vLDiy4RrLNeV",
    "1NqxEQi9pgmoCzi5vh43ByT9EgAbQqcW2o",
    "1DpuecprK8vV6A4FtHU6VLqkUs4D2P59PU",
    "14ZiwXFoDVKoxVyKjeZjdtSHsYnJxSRFSH",
    "1PwaHB72F5nb7hurX8jmC93MUDtMqHgdCY",
    "1LWFZazDBRt6bGDb8ukkCo4H9o297S8pma",
    "15zQPNWD3uAa812THBgQP4rVSiYCBRpZ3N",
    "1KkajS3KDciJbfKk2Vg2SjUE6eKdiMktAa",
    "1FxyVmPEsnqnVS8baCjyuTDsdFHB7reTam",
    "1HenciVLZmE9ugshcrW3GtZttP1bqr8W3s",
    "12jaQdf2C29Cobh3XZHj4WoPk8o91MK4jy",
    "1MhpaS75Xxxyqvcv3CLBwz2L76gDDpysJm",
    "1KF7rv8hTcC88MHeYzKwBuACoecWaQJ91m",
    "1Ey9QHtKgcY6aLDLW2xBoMxPJbaXxZcyAK",
    "16BBCJoyBBuyk2bKM64EGCADgiacdpBsKP",
    "1VketozRRbdwxygHPRh4BL4jQgnH3xPWt",
    "18DfVFHfCAVFBhbmBLYxsE3HZqpaSu1Wvw",
    "1F39FW9NU8tuSCVhxVstd7piVSNw4YVGxY",
    "17iZXQzMYjxBxRbThhs36fmgR3cRKuD1yP",
    "1C4Ym7bZZffCCjtRwcwvR6phVzCwQDyEK7",
    "18qJJUcMRWyXhMXR3F18vJXaHJRPYrxwYm",
    "1LHgE4M96DyCt7J5H2wzcVPWNJt9zD1U5f",
    "13forcak6Mv1ZYBo9wv3zeWB8UhDwBJr5S",
    "1LVWSzpeQyoHYPzDuYVktPuH8qJqBiskUF",
    "1MTMH8rnXtfTkPrNt9xpZVy2D95sKf8hYy",
    "12vQPdDVU8KHeXMSXBY7e4rRierNjWETLi",
    "1KH2yPhaxPKKh53Vqkghjn2jfXDJWHRpbJ",
    "1HGHEhR1tFjiF895SC2PHgRiZyGjpTV5dg",
    "1LpCzHxxWasKBUCqbyXRUsKn1RSvNaRupT",
    "1EwiVkDkBLVUaoPuFVzW9NA82iaUUPZruU",
    "13PaeVWHFvEVWjUJiCAono12o39CLeBEEd",
    "1HhHqRamECC7y4qfSEeYNvLJKCRUkxBY1u",
    "1GwaiUArAF6MfSPV8SwCnp5LKEEbu9qrQ9",
    "1zo1ifkrGNggtBKPhCn4486xHaaWBbXUd",
    "12Ft7JjoqV6fTzUA3mRnosDYtJekVqnZpT",
    "18pxRfY6BgE4W4gSfog6FFZBwGs1fcEre5",
    "1H6ou5ZVaKzyoV3ujeiSqQHncJv831RTcz",
    "12MZnJfu7GNrC8bSPuZhgNDr9otmUZnALu",
    "1P5itXj2ET31bwGTwFx4Xb6EMaGaMRgTtP",
    "1D1Ci72Bhde38avQjP2Gyy6ZGhP2mgvoik",
    "1FUjNePwqBv2gcGZFTkCM88jTqD2gWL4NA",
    "15mVDLozNmscibeBCy33yYyH7AKdsuAcKe",
    "15StD6n2ZTygoc7PM2bY13aAkwybNBUwn8",
    "19bf2fMfCt1b3MLbHwahJfdUNoZXTxYd5D",
    "1PDUuvJfhoiijbqnGeHZZwXRJoBCsaQSr9",
    "1NChqEan8XUff1YPtgPYC9q2prfR1rXu9L",
    "1BQqVjRAGndm8tRrwQNwdgJR8yhhDxXzE7",
    "1KC2mZujBHLTD2NPQycfDowSfni895pXL9",
    "12isdcKgXGQt1F42tCYHPevErL7rsax4Uc",
    "1BPqcdb4kzgoPyjpyrL9xzhmMsJS5eQqvw",
    "1CdZDnukUZ4QK3Ynjk5hukupczV2zzrXPh",
    "12JMQYae1sR4FMupqHYafeGqJUY3kf4A3M",
    "1B8tBmGzxLynfxop38RpNaJ8SM5wr3oj4W",
    "1EpU3v1wRsPxBkpCsZCiA8QGa8jYXSREi8",
    "1BMnca8dAqphg9e98ALoZyJch2NmDirvyY",
    "17WSviRk42u6vUbLg1xUixCQfC5t1zgjQX",
    "16cou7Ht6WjTzuFyDBnht9hmvXytg6XdVT"  # The specific address from user query
]

def load_matrix_addresses():
    """Load all addresses from matrix-addresses.json"""
    addresses = set()

    # Files to check
    files_to_check = [
        "../public/data/matrix-addresses.json",
        "../public/data/bitcoin-derived-addresses.json",
        "../public/data/matrix_addresses_with_xor.json",
        "../public/data/patoshi-addresses.json",
        "../public/data/interesting-addresses.json"
    ]

    for filepath in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), filepath)
        if os.path.exists(full_path):
            print(f"\nLoading {filepath}...")
            try:
                with open(full_path, 'r') as f:
                    data = json.load(f)

                # Handle different JSON structures
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, str):
                            addresses.add(item)
                        elif isinstance(item, dict):
                            # Check for address field
                            for key in ['address', 'btc_address', 'bitcoin_address', 'addr']:
                                if key in item:
                                    addresses.add(item[key])
                elif isinstance(data, dict):
                    # Check for addresses array
                    if 'addresses' in data:
                        for addr in data['addresses']:
                            if isinstance(addr, str):
                                addresses.add(addr)
                            elif isinstance(addr, dict) and 'address' in addr:
                                addresses.add(addr['address'])
                    # Check all values recursively
                    def extract_addresses(obj):
                        if isinstance(obj, str) and len(obj) >= 26 and len(obj) <= 35 and obj.startswith('1'):
                            addresses.add(obj)
                        elif isinstance(obj, dict):
                            for v in obj.values():
                                extract_addresses(v)
                        elif isinstance(obj, list):
                            for item in obj:
                                extract_addresses(item)
                    extract_addresses(data)

                print(f"  Loaded, total unique addresses now: {len(addresses)}")
            except Exception as e:
                print(f"  Error loading {filepath}: {e}")

    return addresses

def main():
    print("=" * 60)
    print("SATOSHI 145 vs MATRIX ADDRESSES COMPARISON")
    print("=" * 60)

    # Load matrix addresses
    print("\n1. Loading Matrix/Derived Addresses...")
    matrix_addresses = load_matrix_addresses()
    print(f"\nTotal unique matrix addresses loaded: {len(matrix_addresses)}")

    # Convert Satoshi 145 to set
    satoshi_set = set(SATOSHI_145_ADDRESSES)
    print(f"Total Satoshi 145 addresses: {len(satoshi_set)}")

    # Find intersections
    print("\n" + "=" * 60)
    print("2. SEARCHING FOR MATCHES...")
    print("=" * 60)

    matches = satoshi_set.intersection(matrix_addresses)

    if matches:
        print(f"\n!!! FOUND {len(matches)} MATCHING ADDRESSES !!!")
        print("-" * 40)
        for addr in sorted(matches):
            print(f"  MATCH: {addr}")
    else:
        print("\nNo exact matches found between Satoshi 145 and Matrix addresses.")

    # Partial prefix matching
    print("\n" + "=" * 60)
    print("3. CHECKING PREFIX SIMILARITIES...")
    print("=" * 60)

    prefix_matches = {}
    for sat_addr in satoshi_set:
        prefix = sat_addr[:5]  # First 5 characters
        for mat_addr in matrix_addresses:
            if mat_addr.startswith(prefix):
                if prefix not in prefix_matches:
                    prefix_matches[prefix] = {'satoshi': [], 'matrix': []}
                if sat_addr not in prefix_matches[prefix]['satoshi']:
                    prefix_matches[prefix]['satoshi'].append(sat_addr)
                if mat_addr not in prefix_matches[prefix]['matrix']:
                    prefix_matches[prefix]['matrix'].append(mat_addr)

    if prefix_matches:
        print(f"\nFound {len(prefix_matches)} shared prefixes:")
        for prefix, data in sorted(prefix_matches.items()):
            print(f"\n  Prefix '{prefix}':")
            print(f"    Satoshi 145: {len(data['satoshi'])} addresses")
            print(f"    Matrix:      {len(data['matrix'])} addresses")
            if len(data['matrix']) <= 5:
                for addr in data['matrix'][:5]:
                    print(f"      - {addr}")

    # Check special address
    print("\n" + "=" * 60)
    print("4. SPECIAL ADDRESS CHECK: 16cou7Ht6WjTzuFyDBnht9hmvXytg6XdVT")
    print("=" * 60)

    special_addr = "16cou7Ht6WjTzuFyDBnht9hmvXytg6XdVT"
    if special_addr in matrix_addresses:
        print(f"\n!!! FOUND IN MATRIX ADDRESSES !!!")
    else:
        print(f"\nNOT found in matrix addresses")
        # Check for similar prefixes
        prefix = special_addr[:4]
        similar = [a for a in matrix_addresses if a.startswith(prefix)]
        if similar:
            print(f"\nAddresses with same prefix '{prefix}':")
            for a in similar[:10]:
                print(f"  - {a}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Matrix addresses checked: {len(matrix_addresses)}")
    print(f"Satoshi 145 addresses: {len(satoshi_set)}")
    print(f"Exact matches: {len(matches)}")
    print(f"Shared prefixes: {len(prefix_matches)}")

    # Save results
    results = {
        "matrix_addresses_count": len(matrix_addresses),
        "satoshi_145_count": len(satoshi_set),
        "exact_matches": list(matches),
        "shared_prefixes": {k: {"count_satoshi": len(v['satoshi']), "count_matrix": len(v['matrix'])}
                          for k, v in prefix_matches.items()},
        "special_address_found": special_addr in matrix_addresses
    }

    output_path = os.path.join(os.path.dirname(__file__), "satoshi_145_matrix_comparison.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    main()
