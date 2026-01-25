#!/usr/bin/env python3
"""
================================================================================
      ATTRACTOR PATHWAY ANALYSIS - Wie finden Inputs ihre Attraktoren?
================================================================================
Untersucht die genauen Pfade, die verschiedene Inputs durch das Anna-Matrix
Netzwerk nehmen, um zu den 4 stabilen Attraktoren zu gelangen.

Fragestellungen:
1. Wie viele Iterationen brauchen verschiedene Input-Typen?
2. Gibt es "Highways" - bevorzugte Pfade?
3. Können wir die Kategorie schon nach wenigen Iterationen vorhersagen?
4. Gibt es "Grenzfälle" die zwischen Kategorien oszillieren?
================================================================================
"""

import json
import hashlib
import os
from datetime import datetime
from collections import defaultdict
import random

# Constants
MATRIX_FILE = os.path.join(os.path.dirname(__file__), '..', 'public', 'data', 'anna-matrix.json')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'ATTRACTOR_PATHWAYS_RESULTS.json')

# Known attractors from previous research
KNOWN_ATTRACTORS = {
    "33a020d0b94ce744": {"category": "A", "pos": 85, "neg": 43},
    "6f0807b87bd06a73": {"category": "B", "pos": 43, "neg": 85},
    "83a33a494bc9ef5d": {"category": "B", "pos": 42, "neg": 85},
    "73ee64980731ccdd": {"category": "A", "pos": 85, "neg": 42}
}

def load_matrix():
    """Load Anna Matrix"""
    with open(MATRIX_FILE, 'r') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'matrix' in data:
        matrix = data['matrix']
    else:
        matrix = data

    # Ensure all values are integers
    return [[int(v) for v in row] for row in matrix]

def matrix_hash(matrix):
    """Generate hash of matrix state"""
    flat = ''.join(str(v) for row in matrix for v in row)
    return hashlib.sha256(flat.encode()).hexdigest()[:16]

def string_to_input(s, size=128):
    """Convert string to input vector"""
    values = []
    for c in s:
        values.append(ord(c) - 128)
    while len(values) < size:
        values.append(0)
    return values[:size]

def analyze_signature(matrix):
    """Analyze matrix signature - count positive/negative values"""
    pos, neg, zero = 0, 0, 0
    for row in matrix:
        for v in row:
            if v > 0: pos += 1
            elif v < 0: neg += 1
            else: zero += 1
    category = "A" if pos > neg else "B"
    return {"pos": pos, "neg": neg, "zero": zero, "category": category}

def run_iteration(matrix, input_vec):
    """Run one iteration of the neural network"""
    size = len(matrix)
    output = []
    for i in range(size):
        total = 0
        for j in range(size):
            if j < len(input_vec):
                total += matrix[i][j] * input_vec[j]
        # Normalize
        if total > 127:
            total = 127
        elif total < -128:
            total = -128
        output.append(total)
    return output

def trace_pathway(matrix, input_vec, max_iterations=50):
    """Trace the complete pathway from input to attractor"""
    history = []
    current = input_vec[:]
    seen_states = {}

    for i in range(max_iterations):
        state_hash = hashlib.sha256(str(current).encode()).hexdigest()[:16]
        sig = analyze_signature([[v] for v in current])  # Treat as column vector for analysis

        history.append({
            "iteration": i,
            "state_hash": state_hash,
            "pos": sum(1 for v in current if v > 0),
            "neg": sum(1 for v in current if v < 0),
            "zero": sum(1 for v in current if v == 0),
            "sum": sum(current),
            "max": max(current),
            "min": min(current)
        })

        if state_hash in seen_states:
            # Found cycle
            cycle_start = seen_states[state_hash]
            return {
                "converged": True,
                "iterations": i,
                "cycle_length": i - cycle_start,
                "final_state_hash": state_hash,
                "history": history
            }

        seen_states[state_hash] = i
        current = run_iteration(matrix, current)

    # Didn't converge in max_iterations
    return {
        "converged": False,
        "iterations": max_iterations,
        "cycle_length": 0,
        "final_state_hash": hashlib.sha256(str(current).encode()).hexdigest()[:16],
        "history": history
    }

def analyze_early_prediction(pathways):
    """Can we predict the final category from early iterations?"""
    results = {
        "iteration_accuracy": {},
        "earliest_reliable_prediction": None
    }

    for iteration in range(1, 11):  # Check first 10 iterations
        correct = 0
        total = 0

        for pathway in pathways:
            if len(pathway["trace"]["history"]) > iteration:
                # Predict based on positive/negative balance at this iteration
                state = pathway["trace"]["history"][iteration]
                predicted_category = "A" if state["pos"] > state["neg"] else "B"
                actual_category = pathway["final_category"]

                if predicted_category == actual_category:
                    correct += 1
                total += 1

        accuracy = correct / total if total > 0 else 0
        results["iteration_accuracy"][iteration] = {
            "correct": correct,
            "total": total,
            "accuracy": round(accuracy * 100, 1)
        }

        # Mark first iteration with >90% accuracy
        if accuracy >= 0.90 and results["earliest_reliable_prediction"] is None:
            results["earliest_reliable_prediction"] = iteration

    return results

def find_highway_patterns(pathways):
    """Find common state sequences (highways)"""
    state_counts = defaultdict(lambda: {"count": 0, "next_states": defaultdict(int)})

    for pathway in pathways:
        history = pathway["trace"]["history"]
        for i, state in enumerate(history[:-1]):
            current_hash = state["state_hash"]
            next_hash = history[i + 1]["state_hash"]

            state_counts[current_hash]["count"] += 1
            state_counts[current_hash]["next_states"][next_hash] += 1

    # Find most common states (highways)
    highways = []
    for state_hash, data in sorted(state_counts.items(), key=lambda x: -x[1]["count"])[:20]:
        most_common_next = max(data["next_states"].items(), key=lambda x: x[1]) if data["next_states"] else (None, 0)
        highways.append({
            "state_hash": state_hash,
            "frequency": data["count"],
            "most_likely_next": most_common_next[0],
            "next_probability": round(most_common_next[1] / data["count"] * 100, 1) if data["count"] > 0 else 0
        })

    return highways

def analyze_boundary_cases(pathways):
    """Find inputs that are on the boundary between categories"""
    boundary_cases = []

    for pathway in pathways:
        history = pathway["trace"]["history"]

        # Check for sign flips in the pathway
        flips = 0
        prev_sign = None
        for state in history:
            current_sign = "A" if state["pos"] > state["neg"] else "B"
            if prev_sign is not None and current_sign != prev_sign:
                flips += 1
            prev_sign = current_sign

        if flips >= 2:  # Multiple category changes = boundary case
            boundary_cases.append({
                "input": pathway["input"],
                "flips": flips,
                "final_category": pathway["final_category"],
                "iterations_to_converge": pathway["trace"]["iterations"]
            })

    return sorted(boundary_cases, key=lambda x: -x["flips"])[:10]

def main():
    print("=" * 78)
    print("     ATTRACTOR PATHWAY ANALYSIS")
    print("=" * 78)

    # Load matrix
    print("\n[1] Loading Anna Matrix...")
    matrix = load_matrix()
    print(f"    Matrix loaded: {len(matrix)}x{len(matrix[0])}")

    # Test inputs
    test_inputs = []

    # 1. CFB-related addresses
    cfb_addresses = [
        "1CFBpVEhYMfGXPr2kJVWqGPe53vBPsLZhu",
        "1CFBQ5cNaU7fJjKM2bca9551iP7haNAYEk",
        "1CFB6ysHTD6ULhE9rKNSePXkWYbxr2sYGU",
    ]
    for addr in cfb_addresses:
        test_inputs.append({"input": addr, "type": "CFB"})

    # 2. Patoshi addresses
    patoshi = [
        "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX",
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis
    ]
    for addr in patoshi:
        test_inputs.append({"input": addr, "type": "Patoshi"})

    # 3. Random inputs for comparison
    for i in range(50):
        random_input = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=34))
        test_inputs.append({"input": random_input, "type": "Random"})

    # 4. Boundary-seeking inputs (specific patterns)
    patterns = [
        "0" * 32,  # All zeros (low)
        "Z" * 32,  # All high
        "AaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAa",  # Alternating
        "MMMMMMMMMMMMMMMMmmmmmmmmmmmmmmmm",  # Half high, half low
    ]
    for p in patterns:
        test_inputs.append({"input": p, "type": "Pattern"})

    print(f"\n[2] Testing {len(test_inputs)} inputs...")

    # Trace all pathways
    pathways = []
    category_counts = {"A": 0, "B": 0}
    iteration_stats = []

    for i, test in enumerate(test_inputs):
        input_vec = string_to_input(test["input"])
        trace = trace_pathway(matrix, input_vec)

        # Determine final category from last state
        final_state = trace["history"][-1]
        final_category = "A" if final_state["pos"] > final_state["neg"] else "B"
        category_counts[final_category] += 1
        iteration_stats.append(trace["iterations"])

        pathways.append({
            "input": test["input"],
            "type": test["type"],
            "trace": trace,
            "final_category": final_category
        })

        if (i + 1) % 20 == 0:
            print(f"    Processed {i + 1}/{len(test_inputs)}")

    print(f"\n[3] Analyzing pathways...")

    # Convergence statistics
    avg_iterations = sum(iteration_stats) / len(iteration_stats)
    converged_count = sum(1 for p in pathways if p["trace"]["converged"])

    print(f"    Average iterations to converge: {avg_iterations:.1f}")
    print(f"    Converged: {converged_count}/{len(pathways)}")
    print(f"    Category A: {category_counts['A']}, Category B: {category_counts['B']}")

    # Early prediction analysis
    print("\n[4] Early prediction analysis...")
    prediction_results = analyze_early_prediction(pathways)
    print(f"    Earliest reliable prediction at iteration: {prediction_results['earliest_reliable_prediction']}")
    for it, data in list(prediction_results["iteration_accuracy"].items())[:5]:
        print(f"    Iteration {it}: {data['accuracy']}% accuracy")

    # Highway analysis
    print("\n[5] Finding highway patterns...")
    highways = find_highway_patterns(pathways)
    print(f"    Found {len(highways)} common intermediate states")
    for h in highways[:5]:
        print(f"    State {h['state_hash']}: seen {h['frequency']}x, next state prob: {h['next_probability']}%")

    # Boundary case analysis
    print("\n[6] Analyzing boundary cases...")
    boundary_cases = analyze_boundary_cases(pathways)
    print(f"    Found {len(boundary_cases)} boundary cases with multiple category flips")
    for bc in boundary_cases[:3]:
        print(f"    Input '{bc['input'][:20]}...': {bc['flips']} flips → {bc['final_category']}")

    # Type-specific analysis
    print("\n[7] Type-specific analysis...")
    type_stats = defaultdict(lambda: {"A": 0, "B": 0, "iterations": []})
    for p in pathways:
        t = p["type"]
        type_stats[t][p["final_category"]] += 1
        type_stats[t]["iterations"].append(p["trace"]["iterations"])

    for t, stats in type_stats.items():
        total = stats["A"] + stats["B"]
        a_pct = stats["A"] / total * 100 if total > 0 else 0
        avg_iter = sum(stats["iterations"]) / len(stats["iterations"]) if stats["iterations"] else 0
        print(f"    {t}: {a_pct:.1f}% Category A, avg {avg_iter:.1f} iterations")

    # Compile results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_inputs": len(test_inputs),
        "convergence": {
            "converged_count": converged_count,
            "average_iterations": round(avg_iterations, 2),
            "max_iterations": max(iteration_stats),
            "min_iterations": min(iteration_stats)
        },
        "category_distribution": category_counts,
        "early_prediction": prediction_results,
        "highways": highways[:10],
        "boundary_cases": boundary_cases,
        "type_analysis": {
            t: {
                "category_a_percent": round(stats["A"] / (stats["A"] + stats["B"]) * 100, 1) if (stats["A"] + stats["B"]) > 0 else 0,
                "category_a_count": stats["A"],
                "category_b_count": stats["B"],
                "avg_iterations": round(sum(stats["iterations"]) / len(stats["iterations"]), 2) if stats["iterations"] else 0
            }
            for t, stats in type_stats.items()
        },
        "sample_pathways": [
            {
                "input": p["input"][:40],
                "type": p["type"],
                "final_category": p["final_category"],
                "iterations": p["trace"]["iterations"],
                "converged": p["trace"]["converged"]
            }
            for p in pathways[:10]
        ]
    }

    # Save results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[8] Results saved to {OUTPUT_FILE}")

    print("\n" + "=" * 78)
    print("     ZUSAMMENFASSUNG")
    print("=" * 78)
    print(f"""
    KONVERGENZ-STATISTIKEN:
    - {converged_count}/{len(pathways)} Inputs konvergierten zu Attraktoren
    - Durchschnittliche Iterationen: {avg_iterations:.1f}
    - Früheste zuverlässige Vorhersage: Iteration {prediction_results['earliest_reliable_prediction']}

    KATEGORIE-VERTEILUNG:
    - Kategorie A: {category_counts['A']} ({category_counts['A']/len(pathways)*100:.1f}%)
    - Kategorie B: {category_counts['B']} ({category_counts['B']/len(pathways)*100:.1f}%)

    HIGHWAY-STRUKTUR:
    - {len(highways)} häufige Zwischenzustände identifiziert
    - Top Highway wird in {highways[0]['frequency'] if highways else 0} Pfaden benutzt

    GRENZFÄLLE:
    - {len(boundary_cases)} Inputs zeigen oszillierendes Verhalten
    """)

    return results

if __name__ == "__main__":
    main()
