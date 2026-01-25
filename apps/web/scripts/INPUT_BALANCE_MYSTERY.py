#!/usr/bin/env python3
"""
================================================================================
      INPUT BALANCE MYSTERY - Warum haben alle Genesis-Adressen -34?
================================================================================
Untersucht das merkwürdige Phänomen, dass alle Genesis-Adressen denselben
Input-Balance von -34 haben.

Fragen:
1. Ist dies eine Eigenschaft von Bitcoin-Adressen generell?
2. Oder haben Genesis-Adressen eine spezielle Struktur?
3. Was bedeutet -34 im Kontext des Anna-Matrix Netzwerks?
================================================================================
"""

import json
import os
import random
import string
from datetime import datetime
from collections import defaultdict

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'INPUT_BALANCE_MYSTERY_RESULTS.json')

# Base58 characters (Bitcoin addresses)
BASE58_CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def string_to_input(s, size=128):
    """Convert string to input vector (like Anna Matrix does)"""
    values = []
    for c in s:
        values.append(ord(c) - 128)  # Center around 0
    while len(values) < size:
        values.append(0)
    return values[:size]

def calculate_input_balance(s):
    """Calculate the input balance for a string"""
    input_vec = string_to_input(s)
    pos = sum(1 for v in input_vec if v > 0)
    neg = sum(1 for v in input_vec if v < 0)
    return pos - neg, pos, neg

def analyze_address_structure(addr):
    """Deep analysis of address structure"""
    result = {
        "length": len(addr),
        "chars": {},
        "ascii_values": [],
        "centered_values": [],
        "unique_chars": len(set(addr))
    }

    for c in addr:
        result["chars"][c] = result["chars"].get(c, 0) + 1
        ascii_val = ord(c)
        result["ascii_values"].append(ascii_val)
        result["centered_values"].append(ascii_val - 128)

    result["ascii_mean"] = sum(result["ascii_values"]) / len(result["ascii_values"])
    result["centered_mean"] = sum(result["centered_values"]) / len(result["centered_values"])

    return result

def main():
    print("=" * 78)
    print("     INPUT BALANCE MYSTERY - Warum haben alle Genesis-Adressen -34?")
    print("=" * 78)

    # Genesis addresses
    genesis_addresses = [
        ("Block 0 - Genesis", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"),
        ("Block 1", "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"),
        ("Block 2", "1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1"),
        ("Block 3 - QUBIC", "15ubicBBWFnvoZLT7GiU2qxjRaKJPdkDMG"),
        ("Block 4", "1JfbZRwdDHKZmuiZgYArJZhcuuzuw2HuMu"),
        ("Block 5", "1GkQmKAmHtNfnD3LHhTkewJxKHVSta4m2a"),
    ]

    print("\n[1] Analysiere Genesis-Adressen...")

    for name, addr in genesis_addresses:
        balance, pos, neg = calculate_input_balance(addr)
        struct = analyze_address_structure(addr)
        print(f"    {name}:")
        print(f"      Address: {addr}")
        print(f"      Länge: {struct['length']}")
        print(f"      Balance: {balance} (pos={pos}, neg={neg})")
        print(f"      ASCII Mean: {struct['ascii_mean']:.1f}")
        print(f"      Centered Mean: {struct['centered_mean']:.1f}")

    # Warum ist der Balance immer -34?
    print("\n[2] Untersuchung: Warum Balance = -34?")

    # ASCII Ranges
    print("\n    ASCII-Werte der Base58-Zeichen:")
    ascii_ranges = {
        "1-9": (49, 57),      # 1-9
        "A-H": (65, 72),      # A-H
        "J-N": (74, 78),      # J-N (no I)
        "P-Z": (80, 90),      # P-Z (no O)
        "a-k": (97, 107),     # a-k
        "m-z": (109, 122),    # m-z (no l)
    }

    all_base58_ascii = []
    for c in BASE58_CHARS:
        all_base58_ascii.append(ord(c))

    print(f"    Base58 ASCII Range: {min(all_base58_ascii)} - {max(all_base58_ascii)}")
    print(f"    Base58 ASCII Mean: {sum(all_base58_ascii)/len(all_base58_ascii):.1f}")

    # Der Schwellenwert ist 128
    # Zeichen unter 128 → negativ (nach ord(c) - 128)
    # Zeichen über 128 → positiv

    below_128 = sum(1 for a in all_base58_ascii if a < 128)
    above_128 = sum(1 for a in all_base58_ascii if a > 128)

    print(f"\n    Zeichen unter ASCII 128: {below_128}/58 ({below_128/58*100:.1f}%)")
    print(f"    Zeichen über ASCII 128: {above_128}/58 ({above_128/58*100:.1f}%)")
    print(f"    → ALLE Base58 Zeichen sind unter 128!")

    print("\n[3] ERKLÄRUNG GEFUNDEN:")
    print("""
    Da alle Base58-Zeichen einen ASCII-Wert unter 128 haben,
    wird JEDES Zeichen in einer Bitcoin-Adresse zu einem
    NEGATIVEN Wert im Input-Vektor transformiert!

    Transformation: ord(char) - 128

    Beispiele:
    - '1' (ASCII 49)  → 49 - 128 = -79
    - 'A' (ASCII 65)  → 65 - 128 = -63
    - 'z' (ASCII 122) → 122 - 128 = -6

    Das erklärt, warum:
    - Alle 34 Zeichen einer Standard-Adresse negativ werden
    - Der Balance immer negativ ist (ca. -34)
    - Alle Genesis-Adressen zu Kategorie B konvergieren
    """)

    # Verifizierung
    print("\n[4] Verifizierung mit zufälligen Bitcoin-Adressen...")

    random.seed(42)
    random_balances = []

    for i in range(1000):
        # Generiere eine zufällige "Bitcoin-ähnliche" Adresse
        addr = "1" + ''.join(random.choices(BASE58_CHARS, k=33))
        balance, _, _ = calculate_input_balance(addr)
        random_balances.append(balance)

    print(f"    1000 zufällige Adressen generiert")
    print(f"    Balance Range: {min(random_balances)} bis {max(random_balances)}")
    print(f"    Balance Mean: {sum(random_balances)/len(random_balances):.1f}")
    print(f"    Balance Std: {(sum((b - sum(random_balances)/len(random_balances))**2 for b in random_balances)/len(random_balances))**0.5:.1f}")

    # Alle sind negativ?
    all_negative = all(b < 0 for b in random_balances)
    print(f"    Alle Balances negativ: {all_negative}")

    # Was wäre nötig für Balance = 0?
    print("\n[5] Was wäre nötig für Balance = 0?")
    print("""
    Um Balance = 0 zu erreichen, bräuchte man:
    - Zeichen mit ASCII > 128
    - Diese existieren nicht in Base58!

    Das bedeutet:
    → KEINE Bitcoin-Adresse kann jemals positive Balance haben
    → ALLE Bitcoin-Adressen werden zu Kategorie B konvergieren
    → Dies ist eine fundamentale Eigenschaft der Anna-Matrix Klassifikation
    """)

    # Was wenn wir andere Strings nutzen?
    print("\n[6] Vergleich: Andere String-Typen")

    test_strings = [
        ("ASCII lowercase (abc...)", "abcdefghijklmnopqrstuvwxyz"),
        ("ASCII uppercase (ABC...)", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        ("Numbers (0123...)", "0123456789"),
        ("High ASCII (ÄÖÜ...)", "äöüÄÖÜß€@µ"),
        ("Mixed with high", "Hello€World"),
        ("All high ASCII", "".join(chr(i) for i in range(129, 160))),
    ]

    for name, s in test_strings:
        balance, pos, neg = calculate_input_balance(s)
        print(f"    {name}: Balance={balance} (pos={pos}, neg={neg})")

    # Die Erkenntnis
    print("\n" + "=" * 78)
    print("     FAZIT: DAS INPUT BALANCE MYSTERY IST GELÖST")
    print("=" * 78)
    print("""
    Die Antwort ist überraschend einfach:

    1. Die Anna-Matrix verwendet: input = ord(char) - 128

    2. Base58 (Bitcoin) verwendet nur ASCII 49-122

    3. Da alle Base58-Zeichen < 128 sind, werden ALLE zu negativen Werten

    4. Daher ist der Input-Balance IMMER negativ für Bitcoin-Adressen

    5. Genauer: Eine 34-Zeichen Adresse hat immer Balance ≈ -34
       (da 34 negative Werte und 94 Nullen im 128er Vektor)

    IMPLIKATION:
    → Bitcoin-Adressen sind "von Natur aus" Kategorie B
    → Die Anna-Matrix klassifiziert ALLE Bitcoin-Adressen als B
    → Dies ist kein Zufall, sondern mathematische Notwendigkeit!

    OFFENE FRAGE:
    → Hat CFB die Anna-Matrix absichtlich so designed, dass
       Bitcoin-Adressen immer Kategorie B sind?
    → Was würde Kategorie A repräsentieren?
    """)

    # Compile results
    results = {
        "timestamp": datetime.now().isoformat(),
        "mystery_solved": True,
        "explanation": {
            "root_cause": "All Base58 characters have ASCII values below 128",
            "transformation": "input = ord(char) - 128, so all become negative",
            "consequence": "All Bitcoin addresses have negative input balance",
            "typical_balance": -34,
            "category_result": "All Bitcoin addresses converge to Category B"
        },
        "base58_analysis": {
            "ascii_range": f"{min(all_base58_ascii)}-{max(all_base58_ascii)}",
            "ascii_mean": round(sum(all_base58_ascii)/len(all_base58_ascii), 1),
            "chars_below_128": below_128,
            "chars_above_128": above_128,
            "threshold": 128
        },
        "random_test": {
            "sample_size": 1000,
            "balance_min": min(random_balances),
            "balance_max": max(random_balances),
            "balance_mean": round(sum(random_balances)/len(random_balances), 1),
            "all_negative": all_negative
        },
        "genesis_analysis": [
            {"name": name, "address": addr, "balance": calculate_input_balance(addr)[0]}
            for name, addr in genesis_addresses
        ],
        "implication": "The Anna Matrix is designed such that all Bitcoin addresses are inherently Category B"
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n    Ergebnisse gespeichert in: {OUTPUT_FILE}")

    return results

if __name__ == "__main__":
    main()
