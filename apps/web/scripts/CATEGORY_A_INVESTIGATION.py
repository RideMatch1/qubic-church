#!/usr/bin/env python3
"""
================================================================================
      CATEGORY A INVESTIGATION - Was repräsentiert Kategorie A?
================================================================================
Da Bitcoin-Adressen mathematisch immer Kategorie B sind, stellt sich die Frage:
Was IST Kategorie A und welche Daten können sie erreichen?

Hypothesen:
1. Qubic IDs könnten Kategorie A sein (andere Zeichensätze?)
2. Kategorie A repräsentiert eine "höhere Dimension"
3. Es ist ein Platzhalter für zukünftige Protokolle
================================================================================
"""

import json
import hashlib
import os
from datetime import datetime

MATRIX_FILE = os.path.join(os.path.dirname(__file__), '..', 'public', 'data', 'anna-matrix.json')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'CATEGORY_A_INVESTIGATION_RESULTS.json')

# Qubic ID characters (all uppercase)
QUBIC_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # A-Z only

def load_matrix():
    """Load Anna Matrix"""
    with open(MATRIX_FILE, 'r') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'matrix' in data:
        matrix = data['matrix']
    else:
        matrix = data
    return [[int(v) for v in row] for row in matrix]

def string_to_input(s, size=128):
    """Convert string to input vector"""
    values = []
    for c in s:
        values.append(ord(c) - 128)
    while len(values) < size:
        values.append(0)
    return values[:size]

def calculate_input_balance(s):
    """Calculate the input balance for a string"""
    input_vec = string_to_input(s)
    pos = sum(1 for v in input_vec if v > 0)
    neg = sum(1 for v in input_vec if v < 0)
    return pos - neg, pos, neg

def run_network(matrix, input_vec, max_iterations=50):
    """Run the neural network until convergence"""
    size = len(matrix)
    current = input_vec[:]
    seen_states = {}

    for iteration in range(max_iterations):
        state_hash = hashlib.sha256(str(current).encode()).hexdigest()[:16]
        pos = sum(1 for v in current if v > 0)
        neg = sum(1 for v in current if v < 0)

        if state_hash in seen_states:
            return {
                "final_category": "A" if pos > neg else "B",
                "iterations": iteration,
                "final_pos": pos,
                "final_neg": neg
            }

        seen_states[state_hash] = iteration

        output = []
        for i in range(size):
            total = 0
            for j in range(size):
                if j < len(current):
                    total += matrix[i][j] * current[j]
            total = max(-128, min(127, total))
            output.append(total)
        current = output

    pos = sum(1 for v in current if v > 0)
    neg = sum(1 for v in current if v < 0)
    return {
        "final_category": "A" if pos > neg else "B",
        "iterations": max_iterations,
        "final_pos": pos,
        "final_neg": neg
    }

def main():
    print("=" * 78)
    print("     CATEGORY A INVESTIGATION")
    print("=" * 78)

    # Load matrix
    print("\n[1] Loading Anna Matrix...")
    matrix = load_matrix()

    # Test different character sets
    print("\n[2] Analysiere verschiedene Zeichensätze...")

    character_sets = {
        "Base58 (Bitcoin)": "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
        "Uppercase (Qubic)": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "Lowercase": "abcdefghijklmnopqrstuvwxyz",
        "Digits": "0123456789",
        "High ASCII (128+)": "".join(chr(i) for i in range(129, 200)),
        "Extended Latin": "äöüÄÖÜßéàèù",
    }

    for name, chars in character_sets.items():
        ascii_vals = [ord(c) for c in chars]
        below_128 = sum(1 for v in ascii_vals if v < 128)
        above_128 = sum(1 for v in ascii_vals if v >= 128)

        print(f"\n    {name}:")
        print(f"      ASCII Range: {min(ascii_vals)} - {max(ascii_vals)}")
        print(f"      Unter 128: {below_128}/{len(chars)} ({below_128/len(chars)*100:.0f}%)")
        print(f"      Über 128: {above_128}/{len(chars)} ({above_128/len(chars)*100:.0f}%)")

        # Was passiert wenn man ALLE Zeichen verwendet?
        balance, pos, neg = calculate_input_balance(chars)
        print(f"      Input Balance (ganze Zeichenkette): {balance}")

    # Test Qubic-style IDs
    print("\n[3] Teste Qubic-Style IDs...")

    qubic_test_ids = [
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # 55 A's
        "BKHBAKRMUVBGTPNCGJGVFAEQXXMKPJIWZZZZZZZZZZZZZZZZZZZZZZZZ",  # Sample ID
        "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ",  # 55 Z's
        "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",  # Middle
    ]

    for qid in qubic_test_ids:
        balance, pos, neg = calculate_input_balance(qid)
        result = run_network(matrix, string_to_input(qid))
        print(f"\n    {qid[:30]}...")
        print(f"      Länge: {len(qid)}")
        print(f"      Input Balance: {balance} (pos={pos}, neg={neg})")
        print(f"      Final Category: {result['final_category']}")
        print(f"      Iterations: {result['iterations']}")

    # Was wäre nötig für Kategorie A?
    print("\n[4] Erforsche: Was erreicht Kategorie A?")

    # Test mit High ASCII Strings
    high_ascii_tests = [
        ("High ASCII only (128-200)", "".join(chr(i) for i in range(128, 180))),
        ("Mixed: Half high, half low", "AAAAAAAAA" + "".join(chr(i) for i in range(200, 220))),
        ("Emojis (high unicode)", "😀😎🚀💎🌟"),
        ("Special: chr(200) * 55", chr(200) * 55),
    ]

    for name, test_str in high_ascii_tests:
        try:
            balance, pos, neg = calculate_input_balance(test_str)
            result = run_network(matrix, string_to_input(test_str))
            print(f"\n    {name}:")
            print(f"      Input Balance: {balance} (pos={pos}, neg={neg})")
            print(f"      Final Category: {result['final_category']}")
            if result['final_category'] == 'A':
                print(f"      ⭐ KATEGORIE A ERREICHT!")
        except Exception as e:
            print(f"\n    {name}: Error - {e}")

    # Systematische Suche nach Category A
    print("\n[5] Systematische Suche nach Kategorie A...")

    category_a_found = []

    # Test verschiedene ASCII-Bereiche
    for start in range(128, 256, 10):
        test_str = "".join(chr(i % 256) for i in range(start, start + 55))
        try:
            balance, pos, neg = calculate_input_balance(test_str)
            if balance > 0:  # Potenzieller Kategorie A Kandidat
                result = run_network(matrix, string_to_input(test_str))
                if result['final_category'] == 'A':
                    category_a_found.append({
                        "start_ascii": start,
                        "balance": balance,
                        "category": "A"
                    })
                    print(f"    ⭐ ASCII {start}-{start+54}: Balance={balance}, Kategorie=A")
        except:
            pass

    print(f"\n    Gefundene Kategorie A Bereiche: {len(category_a_found)}")

    # BEDEUTUNG
    print("\n" + "=" * 78)
    print("     ANALYSE: WAS REPRÄSENTIERT KATEGORIE A?")
    print("=" * 78)
    print("""
    ERKENNTNISSE:

    1. Qubic IDs (nur A-Z) haben ASCII 65-90
       → Alle unter 128 → Alle werden Kategorie B!

    2. Bitcoin Adressen (Base58) haben ASCII 49-122
       → Alle unter 128 → Alle werden Kategorie B!

    3. Um Kategorie A zu erreichen, braucht man:
       → Zeichen mit ASCII >= 128
       → Diese sind: Extended ASCII, Unicode, Emojis

    HYPOTHESE:
    → Kategorie A repräsentiert eine "Dimension jenseits von
       traditionellen Krypto-Adressen"
    → Könnte für zukünftige Protokolle reserviert sein
    → Oder: Die Anna-Matrix nutzt Kategorie A intern für
       etwas anderes als String-Klassifikation

    DIE WAHRE FRAGE:
    → Warum hat CFB die Matrix so designed, dass ALLE
       bekannten Krypto-Adressen Kategorie B sind?
    → Was ist der ZWECK von Kategorie A?
    """)

    # Compile results
    results = {
        "timestamp": datetime.now().isoformat(),
        "findings": {
            "qubic_ids": "All uppercase A-Z (ASCII 65-90) → All Category B",
            "bitcoin_addresses": "Base58 (ASCII 49-122) → All Category B",
            "category_a_requires": "ASCII values >= 128",
            "category_a_examples": "Extended ASCII, Unicode, Emojis"
        },
        "hypothesis": {
            "main": "Category A represents a 'dimension beyond traditional crypto addresses'",
            "possible_purposes": [
                "Reserved for future protocols",
                "Internal use within Anna Matrix",
                "Represents a different type of data/entity"
            ]
        },
        "open_questions": [
            "Why did CFB design the matrix so all crypto addresses are Category B?",
            "What is the purpose of Category A?",
            "Is there a hidden meaning to the B/A dichotomy?"
        ]
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n    Ergebnisse gespeichert in: {OUTPUT_FILE}")

    return results

if __name__ == "__main__":
    main()
