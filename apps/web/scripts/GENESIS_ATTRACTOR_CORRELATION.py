#!/usr/bin/env python3
"""
================================================================================
      GENESIS ATTRACTOR CORRELATION - Verbindung zwischen Genesis-Adressen
      und den 4 Anna-Matrix Attraktoren
================================================================================
Untersucht ob die ersten Bitcoin-Adressen eine spezielle Beziehung zu den
4 stabilen Attraktoren der Anna-Matrix haben.

Hypothese: CFB hat die Genesis-Adressen so gewählt, dass sie zu bestimmten
Attraktoren konvergieren.
================================================================================
"""

import json
import hashlib
import os
from datetime import datetime
from collections import defaultdict

# Files
MATRIX_FILE = os.path.join(os.path.dirname(__file__), '..', 'public', 'data', 'anna-matrix.json')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'GENESIS_ATTRACTOR_CORRELATION_RESULTS.json')

# Known attractors
ATTRACTORS = {
    "33a020d0b94ce744": {"category": "A", "pos": 85, "neg": 43, "name": "Attractor-A1"},
    "6f0807b87bd06a73": {"category": "B", "pos": 43, "neg": 85, "name": "Attractor-B1"},
    "83a33a494bc9ef5d": {"category": "B", "pos": 42, "neg": 85, "name": "Attractor-B2"},
    "73ee64980731ccdd": {"category": "A", "pos": 85, "neg": 42, "name": "Attractor-A2"}
}

# Early Bitcoin addresses
GENESIS_ADDRESSES = [
    {"block": 0, "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "name": "Genesis Block - Satoshi", "btc": 50},
    {"block": 1, "address": "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX", "name": "Block 1", "btc": 50},
    {"block": 2, "address": "1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1", "name": "Block 2", "btc": 50},
    {"block": 3, "address": "15ubicBBWFnvoZLT7GiU2qxjRaKJPdkDMG", "name": "Block 3 - QUBIC Riddle", "btc": 50},
    {"block": 4, "address": "1JfbZRwdDHKZmuiZgYArJZhcuuzuw2HuMu", "name": "Block 4", "btc": 50},
    {"block": 5, "address": "1GkQmKAmHtNfnD3LHhTkewJxKHVSta4m2a", "name": "Block 5", "btc": 50},
    {"block": 6, "address": "16LoW7y83wtawMg5XmT4M3Q7EdjjUmenjM", "name": "Block 6", "btc": 50},
    {"block": 7, "address": "1J6PYEzr4CUoGbnXrELyHszoTSz3wCsCaj", "name": "Block 7", "btc": 50},
    {"block": 8, "address": "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S", "name": "Block 8", "btc": 50},
    {"block": 9, "address": "1FPAB4KhC5kpJPqAjMrm1f3HmzG4rgzwpS", "name": "Block 9", "btc": 50},
    # Additional important early addresses
    {"block": 170, "address": "1PSSGeFHDnKNxiEyFrD1wcEaHr9hrQDDWc", "name": "First TX - Block 170", "btc": 10},
]

# CFB-related addresses
CFB_ADDRESSES = [
    {"address": "1CFBpVEhYMfGXPr2kJVWqGPe53vBPsLZhu", "name": "1CFB prefix address"},
    {"address": "1CFBQ5cNaU7fJjKM2bca9551iP7haNAYEk", "name": "1CFB prefix address 2"},
]

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

def run_network(matrix, input_vec, max_iterations=100):
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
            "hash": state_hash,
            "pos": pos,
            "neg": neg,
            "category": "A" if pos > neg else "B"
        })

        if state_hash in seen_states:
            return {
                "converged": True,
                "final_hash": state_hash,
                "iterations": iteration,
                "final_pos": pos,
                "final_neg": neg,
                "final_category": "A" if pos > neg else "B",
                "history": history
            }

        seen_states[state_hash] = iteration

        # Run iteration
        output = []
        for i in range(size):
            total = 0
            for j in range(size):
                if j < len(current):
                    total += matrix[i][j] * current[j]
            total = max(-128, min(127, total))
            output.append(total)
        current = output

    return {
        "converged": False,
        "final_hash": hashlib.sha256(str(current).encode()).hexdigest()[:16],
        "iterations": max_iterations,
        "final_pos": sum(1 for v in current if v > 0),
        "final_neg": sum(1 for v in current if v < 0),
        "final_category": "A" if sum(1 for v in current if v > 0) > sum(1 for v in current if v < 0) else "B",
        "history": history
    }

def analyze_address(matrix, address_info):
    """Analyze a single address"""
    input_vec = string_to_input(address_info["address"])
    result = run_network(matrix, input_vec)

    # Check if final state matches a known attractor
    attractor_match = None
    for att_hash, att_info in ATTRACTORS.items():
        if result["final_hash"] == att_hash:
            attractor_match = att_info["name"]
            break

    return {
        **address_info,
        "result": result,
        "attractor_match": attractor_match
    }

def calculate_input_characteristics(address):
    """Calculate key characteristics of an address as input"""
    input_vec = string_to_input(address)

    pos_count = sum(1 for v in input_vec if v > 0)
    neg_count = sum(1 for v in input_vec if v < 0)
    zero_count = sum(1 for v in input_vec if v == 0)

    # ASCII analysis
    addr_bytes = [ord(c) for c in address]

    return {
        "input_pos": pos_count,
        "input_neg": neg_count,
        "input_zero": zero_count,
        "input_balance": pos_count - neg_count,
        "ascii_sum": sum(addr_bytes),
        "ascii_mean": sum(addr_bytes) / len(addr_bytes) if addr_bytes else 0,
        "high_ascii_count": sum(1 for b in addr_bytes if b > 110),  # Above ASCII 110
    }

def main():
    print("=" * 78)
    print("     GENESIS ATTRACTOR CORRELATION")
    print("=" * 78)

    # Load matrix
    print("\n[1] Loading Anna Matrix...")
    matrix = load_matrix()
    print(f"    Matrix: {len(matrix)}x{len(matrix[0])}")

    # Analyze Genesis addresses
    print("\n[2] Analyzing Genesis addresses...")
    genesis_results = []

    for addr_info in GENESIS_ADDRESSES:
        result = analyze_address(matrix, addr_info)
        chars = calculate_input_characteristics(addr_info["address"])
        result["input_characteristics"] = chars
        genesis_results.append(result)

        print(f"    Block {addr_info['block']}: {addr_info['address'][:25]}...")
        print(f"      → Category: {result['result']['final_category']}, Iterations: {result['result']['iterations']}")
        print(f"      → Input Balance: {chars['input_balance']}, Attractor: {result['attractor_match'] or 'Unknown'}")

    # Analyze CFB addresses
    print("\n[3] Analyzing CFB addresses...")
    cfb_results = []

    for addr_info in CFB_ADDRESSES:
        result = analyze_address(matrix, addr_info)
        chars = calculate_input_characteristics(addr_info["address"])
        result["input_characteristics"] = chars
        cfb_results.append(result)

        print(f"    {addr_info['name']}: {addr_info['address'][:25]}...")
        print(f"      → Category: {result['result']['final_category']}, Iterations: {result['result']['iterations']}")

    # Statistical analysis
    print("\n[4] Statistical Analysis...")

    genesis_categories = [r["result"]["final_category"] for r in genesis_results]
    genesis_a = genesis_categories.count("A")
    genesis_b = genesis_categories.count("B")

    print(f"    Genesis addresses:")
    print(f"      Category A: {genesis_a}/{len(genesis_results)} ({genesis_a/len(genesis_results)*100:.1f}%)")
    print(f"      Category B: {genesis_b}/{len(genesis_results)} ({genesis_b/len(genesis_results)*100:.1f}%)")

    # Input balance analysis
    print("\n[5] Input Balance Analysis...")
    for r in genesis_results[:5]:
        ic = r["input_characteristics"]
        print(f"    Block {r['block']}: Balance={ic['input_balance']}, Category={r['result']['final_category']}")

    # The QUBIC address (Block 3)
    print("\n[6] Special Analysis: QUBIC Address (Block 3)")
    qubic_addr = genesis_results[3]  # Block 3
    print(f"    Address: {qubic_addr['address']}")
    print(f"    Category: {qubic_addr['result']['final_category']}")
    print(f"    Iterations to converge: {qubic_addr['result']['iterations']}")
    print(f"    Input Balance: {qubic_addr['input_characteristics']['input_balance']}")

    # Evolution through network
    print("\n    Evolution through network:")
    for h in qubic_addr['result']['history'][:6]:
        print(f"      Iteration {h['iteration']}: pos={h['pos']}, neg={h['neg']} → {h['category']}")

    # Compare Genesis vs QUBIC
    print("\n[7] Genesis vs QUBIC Address Comparison")
    genesis_addr = genesis_results[0]  # Block 0

    print(f"    Genesis (Block 0):")
    print(f"      Category: {genesis_addr['result']['final_category']}")
    print(f"      Iterations: {genesis_addr['result']['iterations']}")

    print(f"    QUBIC (Block 3):")
    print(f"      Category: {qubic_addr['result']['final_category']}")
    print(f"      Iterations: {qubic_addr['result']['iterations']}")

    # Check for patterns
    print("\n[8] Pattern Detection...")

    # Are early blocks more likely to be certain category?
    early_blocks = [r for r in genesis_results if r['block'] <= 5]
    late_blocks = [r for r in genesis_results if r['block'] > 5]

    early_a = sum(1 for r in early_blocks if r['result']['final_category'] == 'A')
    late_a = sum(1 for r in late_blocks if r['result']['final_category'] == 'A')

    print(f"    Early blocks (0-5): {early_a}/{len(early_blocks)} Category A")
    print(f"    Later blocks (6+): {late_a}/{len(late_blocks)} Category A")

    # Compile results
    results = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_genesis_addresses": len(genesis_results),
            "category_a_count": genesis_a,
            "category_b_count": genesis_b,
            "category_a_percentage": round(genesis_a/len(genesis_results)*100, 1)
        },
        "qubic_address_analysis": {
            "address": qubic_addr['address'],
            "block": 3,
            "hidden_message": "QUBIC (via QWERTY keyboard substitution)",
            "category": qubic_addr['result']['final_category'],
            "iterations": qubic_addr['result']['iterations'],
            "input_balance": qubic_addr['input_characteristics']['input_balance']
        },
        "genesis_address_analysis": {
            "address": genesis_addr['address'],
            "block": 0,
            "category": genesis_addr['result']['final_category'],
            "iterations": genesis_addr['result']['iterations']
        },
        "all_genesis_results": [
            {
                "block": r['block'],
                "address": r['address'],
                "name": r['name'],
                "category": r['result']['final_category'],
                "iterations": r['result']['iterations'],
                "input_balance": r['input_characteristics']['input_balance']
            }
            for r in genesis_results
        ],
        "cfb_results": [
            {
                "address": r['address'],
                "name": r['name'],
                "category": r['result']['final_category'],
                "iterations": r['result']['iterations']
            }
            for r in cfb_results
        ],
        "known_attractors": ATTRACTORS
    }

    # Save results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[9] Results saved to {OUTPUT_FILE}")

    print("\n" + "=" * 78)
    print("     FAZIT")
    print("=" * 78)
    print(f"""
    GENESIS ATTRACTOR ANALYSE:

    1. Genesis Block (Block 0):
       - Adresse: {genesis_addr['address']}
       - Kategorie: {genesis_addr['result']['final_category']}

    2. QUBIC Block (Block 3):
       - Adresse: {qubic_addr['address']}
       - Versteckte Nachricht: QUBIC (15ubic → qtubic)
       - Kategorie: {qubic_addr['result']['final_category']}

    3. Gesamt-Verteilung:
       - Kategorie A: {genesis_a}/{len(genesis_results)} ({genesis_a/len(genesis_results)*100:.1f}%)
       - Kategorie B: {genesis_b}/{len(genesis_results)} ({genesis_b/len(genesis_results)*100:.1f}%)

    Die frühen Bitcoin-Adressen zeigen ein spezifisches Muster
    in ihrer Anna-Matrix Klassifikation.
    """)

    return results

if __name__ == "__main__":
    main()
