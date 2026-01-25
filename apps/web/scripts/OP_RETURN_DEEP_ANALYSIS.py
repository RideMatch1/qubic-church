#!/usr/bin/env python3
"""
OP_RETURN Deep Analysis
=======================

Analyzes discovered Bitcoin OP_RETURN messages for CFB/Satoshi patterns.

Author: qubic-academic-docs
Date: 2026-01-22
"""

import json
from datetime import datetime
from pathlib import Path

# Discovered transactions with interesting OP_RETURN data
DISCOVERED_TXS = {
    "L137_SATOSHI": {
        "txid": "9c4e11988146ef28bba410b6192ad1fee6179bee9455b8d36ddf20468c21463e",
        "block": 445417,
        "date": "2016-12-28",
        "op_return": "L137,Free speech and free enterprise! Thank you Satoshi",
        "address": "1K69sEhUwNgiva3xzPnToxS89dzydU7nPm",
        "significance": [
            "137 = Fine structure constant (α ≈ 1/137)",
            "137 = Anna Matrix Z-Score (137.06)",
            "137 = CFB coordinates sum (45+92)",
            "Direct 'Thank you Satoshi' message",
            "Cypherpunk philosophy reference"
        ]
    },
    "CHINESE_576": {
        "txid": "f26977c61231bc6fbded42524b33ee8e3d37166ceab3ca74aecf9615e1c85203",
        "block": 397703,
        "date": "2016-02-10",
        "op_return": "我是富，千年后万年，我们一起牵手-18576611569",
        "translation": "I am rich, after thousands of years, we are together -18576611569",
        "address": "COINBASE (Mining reward)",
        "significance": [
            "Phone number contains 576!",
            "18-576-611-569",
            "576 = 24² = Maria Square",
            "576 = MT576 SWIFT protocol",
            "Coinbase TX = Miner embedded this!"
        ]
    },
    "CFB9_HASH": {
        "txid": "bb9e09e7d08820e806584d04523ec63df4a97a64cc037a5772570ec190b1b96a",
        "block": 399349,
        "date": "2016-02-20",
        "op_return": "EW b84403154e03dd36203a369198516e6703c0dea75274e6322f024e10cfb9044a",
        "address": "1AhiR2MxLq4NFAsSrM5AXN3n3VC7i99sHA",
        "significance": [
            "Hash contains 'cfb9' - CFB signature!",
            "EternalWall (EW) protocol message",
            "Could be intentionally mined hash"
        ]
    },
    "HY_OK_676": {
        "txid": "ab2b1bc3141a40b3bc88a071411c427b68d1daeef62caefef3c6e410cba5d056",
        "block": 456806,
        "date": "2017-03-11",
        "op_return": "HY-OK-676",
        "address": "Multiple (consolidation TX)",
        "significance": [
            "676 = 26² = GENESIS supply basis",
            "676 = Qubic Computors count",
            "HY-OK = 'Hey OK' confirmation?",
            "43.6 BTC main output"
        ]
    },
    "LOST_NUMBERS": {
        "txid": "0a99123a22138a69da699c21045058863e8ffc3158da14a94cfa162c9720a899",
        "block": 441375,
        "date": "2016-12-13",
        "op_return": "EW 4 8 15 16 23 42",
        "address": "Unknown",
        "significance": [
            "LOST TV series numbers",
            "Sum = 108",
            "108 = 4 × 27",
            "27 = 3³ = CFB ternary constant"
        ]
    },
    "GNSHA_4576": {
        "txid": "e053a849ba998c963901c461e8ec68b33dcb667f34e7fb6fcabb9a763db0e95f",
        "block": 417801,
        "date": "2016-06-24",
        "op_return": "EW GNSHA-461b209145f9ad9b1ef6b5bd92b81e4a4e16abd14576cec06c4fdd85e3c7cda8",
        "address": "18B3Gw2CzouVjbJLQroxW6Nw2b39ALhHvQ",
        "significance": [
            "Contains '4576' in hash",
            "GNSHA could be 'Genesis SHA'?",
            "EternalWall protocol"
        ]
    },
    "SATOSHI_SARAHAH": {
        "txid": "415899756078393a6c756032c6391337d6cd96a26296a417694b36461cc6c71e",
        "block": 482476,
        "date": "2017-08-29",
        "op_return": "EW satoshinakamoto is on sarahah",
        "address": "1EckDngeiuew1MYsgmRJ9RJwTXVLfHfBHe",
        "significance": [
            "Direct Satoshi Nakamoto reference",
            "Sarahah = anonymous feedback app (2017)",
            "Could be joke or hint"
        ]
    }
}

def analyze_phone_number():
    """Analyze the Chinese phone number for patterns."""
    phone = "18576611569"

    analysis = {
        "full_number": phone,
        "segments": {
            "prefix": "185",      # China Mobile prefix
            "key_segment": "766",  # Contains 76
            "middle": "115",       # Contains 11, 15
            "suffix": "69",        # 69 = E in ASCII
        },
        "patterns_found": [],
        "digit_sum": sum(int(d) for d in phone),
        "contains_576": "576" in phone,
        "contains_137": "137" in phone,
        "contains_27": "27" in phone,
    }

    # Check for specific patterns
    if "576" in phone:
        analysis["patterns_found"].append("576 (Maria Square, MT576)")
        idx = phone.index("576")
        analysis["576_position"] = idx

    # Digit sum analysis
    analysis["digit_sum_factors"] = []
    ds = analysis["digit_sum"]
    for i in range(1, ds + 1):
        if ds % i == 0:
            analysis["digit_sum_factors"].append(i)

    return analysis

def analyze_block_numbers():
    """Analyze block numbers for mathematical significance."""
    blocks = {
        445417: "L137 Satoshi",
        397703: "Chinese 576",
        399349: "cfb9 hash",
        456806: "HY-OK-676",
        441375: "LOST numbers",
        417801: "GNSHA-4576",
        482476: "Satoshi Sarahah"
    }

    analysis = {}
    for block, name in blocks.items():
        digits = [int(d) for d in str(block)]
        digit_sum = sum(digits)

        analysis[block] = {
            "name": name,
            "digit_sum": digit_sum,
            "digit_product": 1,
            "is_prime": is_prime(block),
            "factors": factorize(block),
            "contains_27": "27" in str(block),
            "contains_137": "137" in str(block),
            "contains_576": "576" in str(block),
            "contains_676": "676" in str(block),
        }

        for d in digits:
            if d > 0:
                analysis[block]["digit_product"] *= d

    return analysis

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def factorize(n):
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def generate_search_patterns():
    """Generate comprehensive list of search patterns."""

    patterns = {
        "TIER_1_HIGH_PRIORITY": {
            "description": "Most likely to yield CFB/Satoshi results",
            "patterns": [
                ("L137", "Fine structure constant prefix"),
                ("L127", "Anna Matrix symmetry key"),
                ("L108", "LOST numbers sum"),
                ("L576", "Maria Square prefix"),
                ("L676", "GENESIS supply prefix"),
                ("OK-676", "From HY-OK-676 pattern"),
                ("OK-137", "Possible variant"),
                ("-676", "Suffix pattern"),
                ("-137", "Suffix pattern"),
                ("Thank you Satoshi", "Direct reference"),
                ("BCNext", "CFB's NXT pseudonym"),
                ("come-from-beyond", "CFB full handle"),
                ("CfB", "Case-sensitive CFB"),
            ]
        },
        "TIER_2_MATHEMATICAL": {
            "description": "Mathematical constants and CFB numbers",
            "patterns": [
                ("26^2", "676 mathematical"),
                ("24^2", "576 mathematical"),
                ("3^3", "27 = ternary"),
                ("2^7", "128 = matrix size"),
                ("alpha=", "Fine structure"),
                ("1/137", "Fine structure inverse"),
                ("fibonacci", "Sequence reference"),
                ("golden", "Golden ratio"),
                ("euler", "Euler's number"),
                ("pi=3.14", "Pi reference"),
            ]
        },
        "TIER_3_PROJECT_NAMES": {
            "description": "CFB project references",
            "patterns": [
                ("QUBIC", "Direct reference"),
                ("qubic", "Lowercase"),
                ("IOTA", "CFB's IOTA project"),
                ("iota", "Lowercase"),
                ("NXT", "CFB's first project"),
                ("nxt", "Lowercase"),
                ("JINN", "CFB hardware project"),
                ("jinn", "Lowercase"),
                ("aigarth", "CFB's AI project"),
                ("AIGARTH", "Uppercase"),
                ("ternary", "CFB's favorite concept"),
                ("tryte", "IOTA data format"),
                ("tangle", "IOTA DAG"),
            ]
        },
        "TIER_4_DATES_TIMES": {
            "description": "Significant dates",
            "patterns": [
                ("2026", "GENESIS unlock year"),
                ("03.03", "March 3 (time-lock?)"),
                ("030326", "03.03.2026 compact"),
                ("20260303", "ISO format"),
                ("03-03-2026", "Dash format"),
                ("2009", "Bitcoin genesis year"),
                ("3jan2009", "Bitcoin birthday"),
                ("jan2009", "Genesis month"),
            ]
        },
        "TIER_5_CRYPTO_TERMS": {
            "description": "Cryptographic terminology",
            "patterns": [
                ("genesis", "Genesis reference"),
                ("GENESIS", "Uppercase"),
                ("nakamoto", "Satoshi surname"),
                ("satoshi", "First name"),
                ("hash160", "Bitcoin address hash"),
                ("secp256", "Curve reference"),
                ("sha256", "Hash algorithm"),
                ("k12", "KangarooTwelve"),
                ("kangaroo", "K12 full name"),
            ]
        },
        "TIER_6_ETERNAL_WALL": {
            "description": "EternalWall specific patterns",
            "patterns": [
                ("EW 137", "EW + fine structure"),
                ("EW 676", "EW + GENESIS"),
                ("EW 576", "EW + Maria"),
                ("EW 27", "EW + ternary"),
                ("EW CFB", "EW + CFB"),
                ("EW qubic", "EW + qubic"),
                ("EW satoshi", "EW + satoshi"),
                ("EW genesis", "EW + genesis"),
            ]
        },
        "TIER_7_NUMERIC_SEQUENCES": {
            "description": "Number sequences",
            "patterns": [
                ("4 8 15 16 23 42", "LOST full"),
                ("4 8 15", "LOST prefix"),
                ("23 42", "LOST suffix"),
                ("27 64 125", "Perfect cubes"),
                ("1 1 2 3 5 8", "Fibonacci"),
                ("3 9 27 81", "Powers of 3"),
                ("128 256 512", "Powers of 2"),
            ]
        },
        "TIER_8_HEX_PATTERNS": {
            "description": "Hex-encoded searches (for Blockchair)",
            "hex_patterns": [
                ("4c313337", "L137"),
                ("4c313237", "L127"),
                ("4c353736", "L576"),
                ("4c363736", "L676"),
                ("4f4b2d363736", "OK-676"),
                ("5468616e6b20796f75205361746f736869", "Thank you Satoshi"),
                ("42434e657874", "BCNext"),
                ("636f6d652d66726f6d2d6265796f6e64", "come-from-beyond"),
                ("515542494", "QUBIC"),
                ("494f5441", "IOTA"),
                ("61696761727468", "aigarth"),
            ]
        }
    }

    return patterns

def analyze_address_patterns():
    """Analyze the discovered addresses for patterns."""
    addresses = [
        "1K69sEhUwNgiva3xzPnToxS89dzydU7nPm",  # L137 sender
        "1AhiR2MxLq4NFAsSrM5AXN3n3VC7i99sHA",  # cfb9 hash sender
        "18B3Gw2CzouVjbJLQroxW6Nw2b39ALhHvQ",  # GNSHA sender
        "1EckDngeiuew1MYsgmRJ9RJwTXVLfHfBHe",  # Satoshi Sarahah sender
    ]

    analysis = {}
    for addr in addresses:
        # Check for interesting substrings
        analysis[addr] = {
            "length": len(addr),
            "starts_with": addr[:4],
            "ends_with": addr[-4:],
            "contains_cfb": "cfb" in addr.lower(),
            "contains_676": "676" in addr,
            "contains_137": "137" in addr,
            "numeric_chars": sum(c.isdigit() for c in addr),
            "checksum": addr[-4:],
        }

    return analysis

def main():
    print("=" * 70)
    print("OP_RETURN DEEP ANALYSIS")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    results = {
        "timestamp": datetime.now().isoformat(),
        "discovered_transactions": DISCOVERED_TXS,
        "phone_analysis": analyze_phone_number(),
        "block_analysis": analyze_block_numbers(),
        "search_patterns": generate_search_patterns(),
        "address_patterns": analyze_address_patterns(),
    }

    # Print key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)

    print("\n[1] PHONE NUMBER ANALYSIS (18576611569)")
    phone = results["phone_analysis"]
    print(f"    Contains 576: {phone['contains_576']} ✓" if phone['contains_576'] else "    Contains 576: No")
    print(f"    Digit Sum: {phone['digit_sum']}")
    print(f"    576 Position: index {phone.get('576_position', 'N/A')}")

    print("\n[2] BLOCK NUMBER ANALYSIS")
    for block, data in results["block_analysis"].items():
        print(f"    Block {block} ({data['name']})")
        print(f"        Digit Sum: {data['digit_sum']}")
        print(f"        Factors: {data['factors']}")
        if data['contains_27'] or data['contains_137'] or data['contains_576']:
            patterns = []
            if data['contains_27']: patterns.append("27")
            if data['contains_137']: patterns.append("137")
            if data['contains_576']: patterns.append("576")
            print(f"        Contains: {', '.join(patterns)}")

    print("\n[3] RECOMMENDED SEARCH PATTERNS")
    patterns = results["search_patterns"]
    for tier, data in patterns.items():
        print(f"\n    {tier}: {data['description']}")
        if "patterns" in data:
            for pattern, meaning in data["patterns"][:5]:
                print(f"        '{pattern}' - {meaning}")
            if len(data["patterns"]) > 5:
                print(f"        ... and {len(data['patterns']) - 5} more")

    # Save results
    output_path = Path(__file__).parent / "OP_RETURN_DEEP_ANALYSIS_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n\nFull results saved to: {output_path}")

    # Print search URLs
    print("\n" + "=" * 70)
    print("TOP 20 SEARCH PATTERNS (Copy & Paste)")
    print("=" * 70)

    top_patterns = [
        ("L137", "4c313337"),
        ("L127", "4c313237"),
        ("L576", "4c353736"),
        ("L676", "4c363736"),
        ("OK-676", "4f4b2d363736"),
        ("OK-137", "4f4b2d313337"),
        ("-676", "2d363736"),
        ("-137", "2d313337"),
        ("BCNext", "42434e657874"),
        ("CfB", "436642"),
        ("QUBIC", "5155424943"),
        ("qubic", "7175626963"),
        ("IOTA", "494f5441"),
        ("aigarth", "61696761727468"),
        ("genesis", "67656e65736973"),
        ("nakamoto", "6e616b616d6f746f"),
        ("ternary", "7465726e617279"),
        ("2026", "32303236"),
        ("03.03.2026", "30332e30332e32303236"),
        ("EW 137", "455720313337"),
    ]

    print("\nText searches (blockchain.com):")
    for text, _ in top_patterns[:10]:
        print(f"    {text}")

    print("\nHex searches (blockchair.com):")
    for text, hex_val in top_patterns[:10]:
        print(f"    {text}: script_hex(~{hex_val})")

    return 0

if __name__ == "__main__":
    exit(main())
