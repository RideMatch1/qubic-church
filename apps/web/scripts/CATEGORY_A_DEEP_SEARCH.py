#!/usr/bin/env python3
"""
================================================================================
      CATEGORY A DEEP SEARCH - Systematische Suche nach Kategorie A
================================================================================
Selbst mit positivem Input-Balance konvergiert alles zu B!
Wir müssen die Matrix-Dynamik verstehen.
================================================================================
"""

import json
import hashlib
import os
import random
from datetime import datetime

MATRIX_FILE = os.path.join(os.path.dirname(__file__), '..', 'public', 'data', 'anna-matrix.json')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'CATEGORY_A_DEEP_SEARCH_RESULTS.json')

def load_matrix():
    """Load Anna Matrix"""
    with open(MATRIX_FILE, 'r') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'matrix' in data:
        matrix = data['matrix']
    else:
        matrix = data
    return [[int(v) for v in row] for row in matrix]

def run_network(matrix, input_vec, max_iterations=50):
    """Run the neural network until convergence"""
    size = len(matrix)
    current = input_vec[:]
    seen_states = {}
    history = []

    for iteration in range(max_iterations):
        state_hash = hashlib.sha256(str(current).encode()).hexdigest()[:16]
        pos = sum(1 for v in current if v > 0)
        neg = sum(1 for v in current if v < 0)

        history.append({
            "iteration": iteration,
            "pos": pos,
            "neg": neg,
            "category": "A" if pos > neg else "B"
        })

        if state_hash in seen_states:
            return {
                "final_category": "A" if pos > neg else "B",
                "iterations": iteration,
                "final_pos": pos,
                "final_neg": neg,
                "history": history
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
        "final_neg": neg,
        "history": history
    }

def main():
    print("=" * 78)
    print("     CATEGORY A DEEP SEARCH")
    print("=" * 78)

    # Load matrix
    print("\n[1] Loading Anna Matrix...")
    matrix = load_matrix()
    size = len(matrix)

    # Analyze matrix structure
    print("\n[2] Analysiere Matrix-Struktur...")

    matrix_pos = sum(1 for row in matrix for v in row if v > 0)
    matrix_neg = sum(1 for row in matrix for v in row if v < 0)
    matrix_zero = sum(1 for row in matrix for v in row if v == 0)

    print(f"    Matrix Größe: {size}x{size} = {size*size} Werte")
    print(f"    Positive Werte: {matrix_pos} ({matrix_pos/(size*size)*100:.1f}%)")
    print(f"    Negative Werte: {matrix_neg} ({matrix_neg/(size*size)*100:.1f}%)")
    print(f"    Null-Werte: {matrix_zero} ({matrix_zero/(size*size)*100:.1f}%)")
    print(f"    Matrix Balance: {matrix_pos - matrix_neg}")

    # Eigenvalue analysis (simplified)
    matrix_sum = sum(sum(row) for row in matrix)
    print(f"    Matrix Summe: {matrix_sum}")

    # Test: Direkter numerischer Input statt Strings
    print("\n[3] Teste direkte numerische Inputs...")

    test_cases = [
        ("All zeros", [0] * 128),
        ("All positive (127)", [127] * 128),
        ("All negative (-128)", [-128] * 128),
        ("Alternating +-", [127 if i % 2 == 0 else -128 for i in range(128)]),
        ("First half +, second -", [127] * 64 + [-128] * 64),
        ("Random positive", [random.randint(1, 127) for _ in range(128)]),
        ("Random negative", [random.randint(-128, -1) for _ in range(128)]),
        ("Single spike at 0", [127] + [0] * 127),
        ("Single spike at 64", [0] * 64 + [127] + [0] * 63),
    ]

    random.seed(42)  # Reproducibility

    category_a_found = []
    category_b_found = []

    for name, input_vec in test_cases:
        input_pos = sum(1 for v in input_vec if v > 0)
        input_neg = sum(1 for v in input_vec if v < 0)
        result = run_network(matrix, input_vec)

        print(f"\n    {name}:")
        print(f"      Input: pos={input_pos}, neg={input_neg}")
        print(f"      Final: Category {result['final_category']}, iterations={result['iterations']}")

        if result['final_category'] == 'A':
            category_a_found.append(name)
            print(f"      ⭐ KATEGORIE A!")
        else:
            category_b_found.append(name)

    # Massive random search
    print("\n[4] Massive Random Search (10000 Inputs)...")

    a_count = 0
    b_count = 0

    random.seed(12345)
    for i in range(10000):
        # Generate random input
        input_vec = [random.randint(-128, 127) for _ in range(128)]
        result = run_network(matrix, input_vec)

        if result['final_category'] == 'A':
            a_count += 1
        else:
            b_count += 1

    print(f"    Kategorie A: {a_count}/10000 ({a_count/100:.1f}%)")
    print(f"    Kategorie B: {b_count}/10000 ({b_count/100:.1f}%)")

    # Search for Category A more systematically
    print("\n[5] Systematische Kategorie A Suche...")

    # Try different input patterns
    found_a = []

    patterns_to_try = [
        # Extremwerte
        ("Max positive", [127] * 128),
        ("Max negative", [-128] * 128),

        # Verschiedene Muster
        ("Positive gradient", list(range(0, 128))),
        ("Negative gradient", list(range(0, -128, -1)) + [0] * 0),

        # Spezielle Werte
        ("All 1s", [1] * 128),
        ("All -1s", [-1] * 128),
        ("All 64", [64] * 128),
        ("All -64", [-64] * 128),
    ]

    for name, pattern in patterns_to_try:
        # Ensure length is 128
        input_vec = (pattern * 2)[:128]
        result = run_network(matrix, input_vec)

        if result['final_category'] == 'A':
            found_a.append({
                "name": name,
                "pattern_sample": input_vec[:10],
                "result": result
            })
            print(f"    ⭐ {name}: KATEGORIE A!")

    # Die Erkenntnis
    print("\n" + "=" * 78)
    print("     ERKENNTNIS")
    print("=" * 78)

    if a_count == 0 and len(found_a) == 0:
        print("""
    WICHTIGE ENTDECKUNG:

    Die Anna-Matrix ist so strukturiert, dass PRAKTISCH ALLE
    Inputs zu Kategorie B konvergieren!

    Das bedeutet:
    1. Kategorie A ist EXTREM SELTEN oder nicht erreichbar
    2. Die Matrix hat eine starke "B-Attraktor" Tendenz
    3. Die 4 "stabilen Attraktoren" aus früheren Tests sind
       wahrscheinlich ALLE Kategorie B!

    IMPLIKATION:
    → Die Matrix ist ein "B-Klassifizierer"
    → Sie wurde designed um fast alles als B zu klassifizieren
    → Kategorie A könnte ein theoretisches Konstrukt sein
       oder einen sehr speziellen Fall repräsentieren
    """)
    else:
        print(f"""
    ERGEBNIS:

    Kategorie A gefunden: {a_count}/10000 random + {len(found_a)} patterns
    Kategorie B gefunden: {b_count}/10000 random

    Die Matrix zeigt eine starke Tendenz zu Kategorie B,
    aber Kategorie A ist unter bestimmten Bedingungen erreichbar.
    """)

    # Compile results
    results = {
        "timestamp": datetime.now().isoformat(),
        "matrix_analysis": {
            "size": size,
            "positive_values": matrix_pos,
            "negative_values": matrix_neg,
            "zero_values": matrix_zero,
            "matrix_balance": matrix_pos - matrix_neg,
            "matrix_sum": matrix_sum
        },
        "random_search": {
            "sample_size": 10000,
            "category_a": a_count,
            "category_b": b_count,
            "a_percentage": a_count / 100
        },
        "category_a_patterns": found_a,
        "conclusion": "Matrix strongly favors Category B convergence"
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n    Ergebnisse gespeichert in: {OUTPUT_FILE}")

    return results

if __name__ == "__main__":
    main()
