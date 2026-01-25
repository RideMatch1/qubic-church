#!/usr/bin/env python3
"""
================================================================================
      CATEGORY A ANATOMY - Was macht die seltenen 0.5% Kategorie A Inputs aus?
================================================================================
Wir wissen jetzt:
- 99.5% der Inputs → Kategorie B
- 0.5% der Inputs → Kategorie A

Frage: Was haben die Kategorie A Inputs gemeinsam?
================================================================================
"""

import json
import hashlib
import os
import random
from datetime import datetime
import statistics

MATRIX_FILE = os.path.join(os.path.dirname(__file__), '..', 'public', 'data', 'anna-matrix.json')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'CATEGORY_A_ANATOMY_RESULTS.json')

def load_matrix():
    with open(MATRIX_FILE, 'r') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'matrix' in data:
        matrix = data['matrix']
    else:
        matrix = data
    return [[int(v) for v in row] for row in matrix]

def run_network(matrix, input_vec, max_iterations=50):
    size = len(matrix)
    current = input_vec[:]
    seen_states = {}

    for iteration in range(max_iterations):
        state_hash = hashlib.sha256(str(current).encode()).hexdigest()[:16]
        pos = sum(1 for v in current if v > 0)
        neg = sum(1 for v in current if v < 0)

        if state_hash in seen_states:
            return "A" if pos > neg else "B", iteration

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
    return "A" if pos > neg else "B", max_iterations

def analyze_input(input_vec):
    """Analyze properties of an input vector"""
    return {
        "sum": sum(input_vec),
        "mean": statistics.mean(input_vec),
        "stdev": statistics.stdev(input_vec) if len(input_vec) > 1 else 0,
        "min": min(input_vec),
        "max": max(input_vec),
        "pos_count": sum(1 for v in input_vec if v > 0),
        "neg_count": sum(1 for v in input_vec if v < 0),
        "zero_count": sum(1 for v in input_vec if v == 0),
        "abs_sum": sum(abs(v) for v in input_vec),
        "first_half_sum": sum(input_vec[:64]),
        "second_half_sum": sum(input_vec[64:]),
        "even_sum": sum(input_vec[::2]),
        "odd_sum": sum(input_vec[1::2]),
    }

def main():
    print("=" * 78)
    print("     CATEGORY A ANATOMY - Die seltenen 0.5%")
    print("=" * 78)

    matrix = load_matrix()

    # Collect Category A samples
    print("\n[1] Sammle Kategorie A Samples (10000 Tests)...")

    random.seed(42)  # Reproducibility

    category_a_inputs = []
    category_b_sample = []

    for i in range(10000):
        input_vec = [random.randint(-128, 127) for _ in range(128)]
        cat, iters = run_network(matrix, input_vec)

        if cat == 'A':
            category_a_inputs.append({
                "input": input_vec,
                "iterations": iters,
                "analysis": analyze_input(input_vec)
            })
        elif len(category_b_sample) < 100:  # Sample of B for comparison
            category_b_sample.append({
                "input": input_vec,
                "iterations": iters,
                "analysis": analyze_input(input_vec)
            })

    print(f"    Gefunden: {len(category_a_inputs)} Kategorie A Inputs")
    print(f"    Sample von Kategorie B: {len(category_b_sample)}")

    # Compare characteristics
    print("\n[2] Vergleiche Eigenschaften...")

    if category_a_inputs:
        # Calculate averages for each property
        a_props = {}
        b_props = {}

        for prop in category_a_inputs[0]["analysis"].keys():
            a_values = [inp["analysis"][prop] for inp in category_a_inputs]
            b_values = [inp["analysis"][prop] for inp in category_b_sample]

            a_props[prop] = {
                "mean": statistics.mean(a_values),
                "stdev": statistics.stdev(a_values) if len(a_values) > 1 else 0
            }
            b_props[prop] = {
                "mean": statistics.mean(b_values),
                "stdev": statistics.stdev(b_values) if len(b_values) > 1 else 0
            }

        print("\n    Eigenschaft          | Kategorie A Mean | Kategorie B Mean | Differenz")
        print("    " + "-" * 70)

        significant_diffs = []

        for prop in a_props.keys():
            a_mean = a_props[prop]["mean"]
            b_mean = b_props[prop]["mean"]
            diff = a_mean - b_mean

            # Calculate effect size (Cohen's d)
            pooled_std = (a_props[prop]["stdev"] + b_props[prop]["stdev"]) / 2
            effect_size = diff / pooled_std if pooled_std > 0 else 0

            print(f"    {prop:20} | {a_mean:16.2f} | {b_mean:16.2f} | {diff:+.2f}")

            if abs(effect_size) > 0.5:  # Medium effect size
                significant_diffs.append({
                    "property": prop,
                    "a_mean": a_mean,
                    "b_mean": b_mean,
                    "effect_size": effect_size
                })

        # Show most distinguishing features
        print("\n[3] Signifikante Unterschiede (|effect size| > 0.5):")
        for diff in sorted(significant_diffs, key=lambda x: -abs(x["effect_size"])):
            direction = "höher" if diff["effect_size"] > 0 else "niedriger"
            print(f"    {diff['property']}: Kat. A ist {direction} (d={diff['effect_size']:.2f})")

        # Show specific examples
        print("\n[4] Beispiele von Kategorie A Inputs...")
        for i, inp in enumerate(category_a_inputs[:3]):
            print(f"\n    Beispiel {i+1}:")
            print(f"      Iterations: {inp['iterations']}")
            print(f"      Sum: {inp['analysis']['sum']}")
            print(f"      Pos/Neg: {inp['analysis']['pos_count']}/{inp['analysis']['neg_count']}")
            print(f"      First 10 values: {inp['input'][:10]}")

        # Find patterns
        print("\n[5] Suche nach Mustern in Kategorie A...")

        # Check position-based patterns
        position_sums = [0] * 128
        for inp in category_a_inputs:
            for i, v in enumerate(inp["input"]):
                position_sums[i] += v

        # Normalize
        position_avgs = [s / len(category_a_inputs) for s in position_sums]

        # Find positions with strongest bias
        strong_positions = []
        for i, avg in enumerate(position_avgs):
            if abs(avg) > 20:  # Significant bias
                strong_positions.append((i, avg))

        print(f"    Positionen mit starkem Bias: {len(strong_positions)}")
        for pos, avg in sorted(strong_positions, key=lambda x: -abs(x[1]))[:10]:
            print(f"      Position {pos}: Durchschnitt = {avg:.1f}")

    else:
        print("    Keine Kategorie A Inputs gefunden!")

    # The insight
    print("\n" + "=" * 78)
    print("     ANATOMIE DER KATEGORIE A")
    print("=" * 78)

    if category_a_inputs and significant_diffs:
        top_feature = sorted(significant_diffs, key=lambda x: -abs(x["effect_size"]))[0]
        print(f"""
    ENTDECKUNG:

    Von 10,000 zufälligen Inputs erreichten {len(category_a_inputs)} Kategorie A (0.5%).

    Das wichtigste Unterscheidungsmerkmal ist:
    → {top_feature['property']}
    → Kategorie A Mean: {top_feature['a_mean']:.2f}
    → Kategorie B Mean: {top_feature['b_mean']:.2f}
    → Effect Size: {top_feature['effect_size']:.2f}

    Die Kategorie A Inputs haben eine spezifische Struktur,
    die sie von den 99.5% Kategorie B unterscheidet.

    Dies könnte bedeuten:
    → CFB hat die Matrix designed um bestimmte Input-Muster
       als "special" zu klassifizieren
    → Kategorie A repräsentiert etwas Bedeutungsvolles
    → Es ist ein verstecktes Auswahlkriterium
    """)
    else:
        print("    Keine signifikanten Unterschiede gefunden.")

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "samples": {
            "category_a_count": len(category_a_inputs),
            "category_b_sample_count": len(category_b_sample),
            "total_tested": 10000
        },
        "significant_differences": significant_diffs if category_a_inputs else [],
        "category_a_examples": [
            {
                "iterations": inp["iterations"],
                "analysis": inp["analysis"],
                "first_10_values": inp["input"][:10]
            }
            for inp in category_a_inputs[:10]
        ]
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n    Ergebnisse gespeichert in: {OUTPUT_FILE}")

    return results

if __name__ == "__main__":
    main()
