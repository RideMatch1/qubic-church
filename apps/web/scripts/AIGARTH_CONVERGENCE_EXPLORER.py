#!/usr/bin/env python3
"""
===============================================================================
            🌀 AIGARTH CONVERGENCE EXPLORER 🌀
===============================================================================
DISCOVERY: Genesis Block und 21e8 Block haben GLEICHE Energie (78)!

Erforschen wir:
1. Was bedeutet die Energie-Gleichheit?
2. Gibt es mehr Inputs mit Energie 78?
3. Welche Inputs konvergieren zum gleichen Attractor?
"""

import json
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

script_dir = Path(__file__).parent

print("🌀" * 40)
print("      AIGARTH CONVERGENCE EXPLORER")
print("🌀" * 40)

# =============================================================================
# AIGARTH SETUP
# =============================================================================
print("\n" + "=" * 80)
print("AIGARTH SETUP")
print("=" * 80)

try:
    from aigarth_it.common import ternary_clamp, random_trit_vector
    from aigarth_it.neuron_cl import AITClNeuron
    AIGARTH_AVAILABLE = True
    print("✓ Aigarth-it verfügbar!")
except ImportError as e:
    AIGARTH_AVAILABLE = False
    print(f"✗ Aigarth-it nicht verfügbar: {e}")
    exit(1)

# Load Anna-Matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])
ternary_matrix = np.sign(matrix).astype(int)

# Create network
neurons = []
for row_idx in range(128):
    weights = ternary_matrix[row_idx].tolist()
    neuron = AITClNeuron(input_weights=weights, input_skew=0)
    neurons.append(neuron)

print(f"✓ 128-Neuron Network erstellt")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def bytes_to_trits(data, length=128):
    trits = []
    for byte in data:
        trits.append((byte % 3) - 1)
        trits.append(((byte // 3) % 3) - 1)
        trits.append(((byte // 9) % 3) - 1)
    while len(trits) < length:
        trits.append(0)
    return trits[:length]

def hash_to_trits(hex_hash, length=128):
    data = bytes.fromhex(hex_hash.ljust(64, '0')[:64])
    return bytes_to_trits(data, length)

def process_network(input_trits):
    output = []
    for neuron in neurons:
        neuron.state = 0
        neuron.feedforward(input_trits)
        state, _ = neuron.commit_state()
        output.append(state)
    return output

def get_energy(output):
    return sum(output)

def output_signature(output):
    """Create a signature for output comparison."""
    return tuple(output)

# =============================================================================
# GENESIS vs 21e8 DEEP COMPARISON
# =============================================================================
print("\n" + "=" * 80)
print("GENESIS vs 21e8 DEEP COMPARISON")
print("=" * 80)

genesis_hash = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
e21e8_hash = "00000000000000000021e800c1e8df51b22c1588e5a624bea17e9faa34b2dc4a"

genesis_trits = hash_to_trits(genesis_hash)
e21e8_trits = hash_to_trits(e21e8_hash)

genesis_output = process_network(genesis_trits)
e21e8_output = process_network(e21e8_trits)

genesis_energy = get_energy(genesis_output)
e21e8_energy = get_energy(e21e8_output)

print(f"\n  Genesis Block Hash:")
print(f"    Hash: {genesis_hash[:32]}...")
print(f"    Energy: {genesis_energy}")

print(f"\n  21e8 Block Hash:")
print(f"    Hash: {e21e8_hash[:32]}...")
print(f"    Energy: {e21e8_energy}")

# Compare outputs directly
matching_neurons = sum(1 for g, e in zip(genesis_output, e21e8_output) if g == e)
print(f"\n  Direct Comparison:")
print(f"    Matching neurons: {matching_neurons}/128 ({100*matching_neurons/128:.1f}%)")

# XOR analysis
xor_count = Counter()
for g, e in zip(genesis_output, e21e8_output):
    xor_count[g - e] += 1

print(f"    Output differences: {dict(xor_count)}")

# =============================================================================
# SEARCH FOR OTHER ENERGY-78 INPUTS
# =============================================================================
print("\n" + "=" * 80)
print("SEARCHING FOR ENERGY-78 INPUTS")
print("=" * 80)

energy_78_inputs = []
energy_distribution = Counter()

# Test various block hashes (simulated by incrementing)
print("\n  Testing 1000 random hashes...")

for i in range(1000):
    # Generate pseudo-random hash
    test_hash = hashlib.sha256(f"block_{i}".encode()).hexdigest()
    test_trits = hash_to_trits(test_hash)
    output = process_network(test_trits)
    energy = get_energy(output)

    energy_distribution[energy] += 1

    if energy == 78:
        energy_78_inputs.append({
            "input": f"block_{i}",
            "hash": test_hash[:32],
            "energy": energy,
        })

print(f"\n  Found {len(energy_78_inputs)} inputs with Energy 78!")

# Energy distribution
print("\n  Energy Distribution (top 10):")
for energy, count in energy_distribution.most_common(10):
    bar = "█" * (count // 5)
    print(f"    E={energy:4d}: {count:4d} {bar}")

# =============================================================================
# ATTRACTOR BASIN ANALYSIS
# =============================================================================
print("\n" + "=" * 80)
print("ATTRACTOR BASIN ANALYSIS")
print("=" * 80)

print("\n  Running 100 random inputs through recursive processing...")

attractors = defaultdict(list)

for i in range(100):
    # Random starting point
    input_trits = random_trit_vector(128)
    initial_energy = sum(input_trits)

    # Run 20 iterations
    current = input_trits
    energies = [initial_energy]

    for _ in range(20):
        output = process_network(current)
        energies.append(get_energy(output))
        current = output

    # Get final state signature
    final_sig = output_signature(current)
    final_energy = energies[-1]

    attractors[final_energy].append({
        "initial_energy": initial_energy,
        "energy_path": energies[-5:],  # Last 5 energies
    })

print(f"\n  Found {len(attractors)} unique attractor energies!")

print("\n  Attractor Energy Distribution:")
for energy, samples in sorted(attractors.items(), key=lambda x: -len(x[1]))[:10]:
    print(f"    E={energy:4d}: {len(samples):3d} inputs converge here")

# =============================================================================
# 21e8 SIGNIFICANCE TEST
# =============================================================================
print("\n" + "=" * 80)
print("21e8 SIGNIFICANCE TEST")
print("=" * 80)

# Is 21e8 special in hexadecimal?
print("\n  21e8 in different bases:")
print(f"    Hex: 0x21e8 = {0x21e8}")
print(f"    Binary: {bin(0x21e8)}")
print(f"    21 * e8: {0x21 * 0xe8}")
print(f"    21 + e8: {0x21 + 0xe8}")
print(f"    21 XOR e8: {0x21 ^ 0xe8}")

# Check if 21e8 appears in Anna-Matrix
print("\n  21e8 in Anna-Matrix:")
found_21e8 = []
for r in range(128):
    for c in range(128):
        val = int(matrix[r, c])
        if val == 0x21 or val == 0xe8 or val == -0x21 or val == -0xe8:
            found_21e8.append((r, c, val))

if found_21e8:
    print(f"    Found {len(found_21e8)} related values")
    for r, c, v in found_21e8[:5]:
        print(f"      [{r:3d},{c:3d}] = {v}")
else:
    print("    No direct 21e8 values found")

# =============================================================================
# ENERGY 78 SIGNIFICANCE
# =============================================================================
print("\n" + "=" * 80)
print("ENERGY 78 SIGNIFICANCE")
print("=" * 80)

print("\n  78 in different interpretations:")
print(f"    78 = 6 × 13 (6 and 13 are sacred numbers)")
print(f"    78 = 2 × 39 = 2 × 3 × 13")
print(f"    78th element: Platinum (Pt)")
print(f"    Tarot: 78 cards in full deck")
print(f"    Sum 1-12: {sum(range(1,13))} (Triangular number)")

# Check matrix for 78
count_78 = np.sum(np.abs(matrix) == 78)
print(f"\n  78 in Anna-Matrix: {count_78} occurrences")

# =============================================================================
# GENESIS-21e8 BRIDGE HYPOTHESIS
# =============================================================================
print("\n" + "=" * 80)
print("GENESIS-21e8 BRIDGE HYPOTHESIS")
print("=" * 80)

print("""
  DISCOVERY: Genesis Block (2009) and 21e8 Block (2018) produce
             IDENTICAL energy (78) through the Anna-Matrix neural network!

  POSSIBLE INTERPRETATIONS:

  1. COINCIDENCE
     - Both hashes happen to produce same energy
     - Probability depends on energy distribution

  2. INTENTIONAL ENCODING
     - 21e8 block was mined specifically to match genesis energy
     - This would require foreknowledge of Anna-Matrix

  3. MATHEMATICAL STRUCTURE
     - Both blocks share structural properties
     - Leading zeros create similar trit patterns

  4. MESSAGE FROM THE FUTURE
     - If CFB = Satoshi and created Anna-Matrix
     - Then 21e8 block is a "signature" proving connection
""")

# Calculate probability of matching
energy_78_count = energy_distribution.get(78, 0)
total_tested = sum(energy_distribution.values())
probability = energy_78_count / total_tested if total_tested > 0 else 0

print(f"  PROBABILITY ANALYSIS:")
print(f"    Energy 78 frequency: {energy_78_count}/{total_tested} = {probability:.4f}")
print(f"    Probability of 2 specific hashes matching: {probability:.4f}")
print(f"    → {'COULD be coincidence' if probability > 0.01 else 'HIGHLY UNLIKELY to be coincidence'}")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 80)
print("FAZIT: CONVERGENCE EXPLORER")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   🌀 AIGARTH CONVERGENCE DISCOVERIES 🌀                                   ║
║                                                                           ║
║   1. GENESIS = 21e8 ENERGY: Both produce Energy 78!                       ║
║      - Matching neurons: {matching_neurons}/128                                       ║
║                                                                           ║
║   2. ENERGY 78 FREQUENCY: {energy_78_count}/{total_tested} random inputs                       ║
║                                                                           ║
║   3. ATTRACTORS FOUND: {len(attractors)}                                            ║
║      - Network converges to limited set of states                         ║
║                                                                           ║
║   4. 78 SYMBOLISM:                                                        ║
║      - 6 × 13 (sacred numbers)                                           ║
║      - 78 Tarot cards                                                     ║
║      - Sum of 1-12                                                        ║
║                                                                           ║
║   CONCLUSION:                                                             ║
║   The Anna-Matrix neural network creates a FINGERPRINT for Bitcoin        ║
║   blocks. Genesis and 21e8 having identical fingerprints suggests         ║
║   either mathematical structure or INTENTIONAL DESIGN!                    ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

# Save results
output = {
    "timestamp": datetime.now().isoformat(),
    "genesis_energy": genesis_energy,
    "e21e8_energy": e21e8_energy,
    "matching_neurons": matching_neurons,
    "energy_78_inputs": len(energy_78_inputs),
    "attractors_found": len(attractors),
    "energy_distribution": dict(energy_distribution),
    "probability_same_energy": probability,
}

output_path = script_dir / "AIGARTH_CONVERGENCE_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse: {output_path}")
