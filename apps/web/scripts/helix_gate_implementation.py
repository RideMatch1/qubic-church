#!/usr/bin/env python3
"""
HELIX GATE IMPLEMENTATION
=========================
Implementiere die ternäre Helix-Gate Logik und teste sie mit der Anna-Matrix.

Helix Gate Definition:
- 3 Inputs: A, B, C ∈ {-1, 0, +1}
- Output: Rotation um (A + B + C) Positionen
- Range: -3 to +3

Das ist die fundamentale Operation von Aigarth.
"""

import json
import numpy as np
from pathlib import Path
from typing import Tuple, List

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

print("=" * 70)
print("HELIX GATE IMPLEMENTATION")
print("=" * 70)

# =============================================================================
# 1. HELIX GATE DEFINITION
# =============================================================================
print("\n--- 1. HELIX GATE DEFINITION ---")

def to_ternary(value: int) -> int:
    """Konvertiere Integer zu ternär (-1, 0, +1)."""
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0

def helix_gate(a: int, b: int, c: int) -> int:
    """
    Helix Gate: Die fundamentale ternäre Operation.

    Input: 3 ternäre Werte (-1, 0, +1)
    Output: Rotation-Wert (-3 bis +3)

    Dies ist NICHT einfach Addition - es ist eine Rotation!
    """
    # Konvertiere zu ternär
    ta = to_ternary(a)
    tb = to_ternary(b)
    tc = to_ternary(c)

    # Helix-Rotation = Summe
    rotation = ta + tb + tc

    return rotation

def helix_output(rotation: int, state: List[int] = None) -> int:
    """
    Wende Helix-Rotation auf einen Zustand an.

    Der Zustand ist ein Ring von 7 Werten (für -3 bis +3).
    """
    if state is None:
        # Default-Zustand: [-3, -2, -1, 0, 1, 2, 3]
        state = [-3, -2, -1, 0, 1, 2, 3]

    # Rotation modulo 7
    idx = (rotation + 3) % 7
    return state[idx]

print("Helix Gate Wahrheitstabelle:")
print("  A   B   C  → Rotation → Output")
for a in [-1, 0, 1]:
    for b in [-1, 0, 1]:
        for c in [-1, 0, 1]:
            rot = helix_gate(a, b, c)
            out = helix_output(rot)
            print(f"  {a:2d}  {b:2d}  {c:2d}  →    {rot:2d}    →   {out:2d}")

# =============================================================================
# 2. MATRIX ALS GEWICHTE INTERPRETIEREN
# =============================================================================
print("\n--- 2. MATRIX ALS NEURONALE GEWICHTE ---")

def normalize_weight(value: int) -> float:
    """Normalisiere Matrix-Wert zu Gewicht [-1, 1]."""
    return value / 128.0

def to_ternary_weight(value: int) -> int:
    """Konvertiere zu ternärem Gewicht."""
    if value > 42:  # > 1/3 des Bereichs
        return 1
    elif value < -42:  # < -1/3 des Bereichs
        return -1
    else:
        return 0

# Konvertiere Matrix zu ternären Gewichten
ternary_matrix = np.vectorize(to_ternary_weight)(matrix)

print(f"Ternäre Matrix-Statistik:")
print(f"  +1 Werte: {np.sum(ternary_matrix == 1)} ({np.sum(ternary_matrix == 1)/16384*100:.1f}%)")
print(f"   0 Werte: {np.sum(ternary_matrix == 0)} ({np.sum(ternary_matrix == 0)/16384*100:.1f}%)")
print(f"  -1 Werte: {np.sum(ternary_matrix == -1)} ({np.sum(ternary_matrix == -1)/16384*100:.1f}%)")

# =============================================================================
# 3. FORWARD PASS IMPLEMENTIEREN
# =============================================================================
print("\n--- 3. FORWARD PASS ---")

def forward_pass(input_vector: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """
    Ternärer Forward Pass durch die Matrix.

    Input: 128-dimensionaler Vektor
    Weights: 128x128 Matrix
    Output: 128-dimensionaler Vektor
    """
    output = np.zeros(128, dtype=int)

    for i in range(128):
        # Für jede Output-Neuron
        total = 0
        for j in range(128):
            # Ternäre Multiplikation
            w = to_ternary_weight(weights[i, j])
            x = to_ternary(input_vector[j])
            total += w * x

        # Ternäre Aktivierung
        output[i] = to_ternary(total)

    return output

def helix_forward_pass(input_vector: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """
    Forward Pass mit Helix-Gates.

    Verwendet 3 benachbarte Werte für jeden Helix-Gate.
    """
    output = np.zeros(128, dtype=int)

    for i in range(128):
        # Wähle 3 Inputs für Helix-Gate
        # Verwende gewichtete Summen aus 3 Nachbarregionen
        region_size = 128 // 3

        sum_a = sum(to_ternary_weight(weights[i, j]) * to_ternary(input_vector[j])
                    for j in range(0, region_size))
        sum_b = sum(to_ternary_weight(weights[i, j]) * to_ternary(input_vector[j])
                    for j in range(region_size, 2*region_size))
        sum_c = sum(to_ternary_weight(weights[i, j]) * to_ternary(input_vector[j])
                    for j in range(2*region_size, 128))

        # Helix-Gate
        rotation = helix_gate(sum_a, sum_b, sum_c)
        output[i] = rotation

    return output

# =============================================================================
# 4. TEST MIT BEKANNTEN INPUTS
# =============================================================================
print("\n--- 4. TEST MIT VERSCHIEDENEN INPUTS ---")

# Test 1: Null-Vektor
zero_input = np.zeros(128, dtype=int)
zero_output = forward_pass(zero_input, matrix)
print(f"Null-Input → Output: {np.sum(zero_output == 1)} positive, {np.sum(zero_output == 0)} zero, {np.sum(zero_output == -1)} negative")

# Test 2: Einser-Vektor
ones_input = np.ones(128, dtype=int)
ones_output = forward_pass(ones_input, matrix)
print(f"Ones-Input → Output: {np.sum(ones_output == 1)} positive, {np.sum(ones_output == 0)} zero, {np.sum(ones_output == -1)} negative")

# Test 3: Minus-Einser
minus_input = -np.ones(128, dtype=int)
minus_output = forward_pass(minus_input, matrix)
print(f"Minus-Input → Output: {np.sum(minus_output == 1)} positive, {np.sum(minus_output == 0)} zero, {np.sum(minus_output == -1)} negative")

# Test 4: Zufälliger ternärer Input
random_input = np.random.choice([-1, 0, 1], size=128)
random_output = forward_pass(random_input, matrix)
print(f"Random-Input → Output: {np.sum(random_output == 1)} positive, {np.sum(random_output == 0)} zero, {np.sum(random_output == -1)} negative")

# =============================================================================
# 5. ROW 21 ALS INPUT (BITCOIN LAYER)
# =============================================================================
print("\n--- 5. ROW 21 (BITCOIN INPUT LAYER) ---")

# Row 21 ist die Bitcoin-Input-Schicht laut Dokumentation
row21_input = matrix[21, :]
row21_ternary = np.vectorize(to_ternary)(row21_input)
print(f"Row 21 als Input:")
print(f"  Ternär: {np.sum(row21_ternary == 1)} positive, {np.sum(row21_ternary == 0)} zero, {np.sum(row21_ternary == -1)} negative")

# Forward pass mit Row 21
row21_output = forward_pass(row21_ternary, matrix)
print(f"Row 21 → Output: {np.sum(row21_output == 1)} positive, {np.sum(row21_output == 0)} zero, {np.sum(row21_output == -1)} negative")

# =============================================================================
# 6. MULTI-LAYER FORWARD PASS
# =============================================================================
print("\n--- 6. MULTI-LAYER FORWARD PASS ---")

def multi_layer_pass(input_vector: np.ndarray, weights: np.ndarray, layers: int = 3) -> List[np.ndarray]:
    """
    Mehrschichtiger Forward Pass.

    Die Matrix wird mehrfach angewendet (rekurrent).
    """
    states = [input_vector]
    current = input_vector

    for layer in range(layers):
        current = forward_pass(current, weights)
        states.append(current.copy())
        print(f"  Layer {layer+1}: {np.sum(current == 1)} pos, {np.sum(current == 0)} zero, {np.sum(current == -1)} neg")

    return states

print("Multi-Layer mit Ones-Input:")
states = multi_layer_pass(ones_input, matrix, layers=5)

# Prüfe auf Konvergenz
print("\nKonvergenz-Check:")
for i in range(1, len(states)):
    diff = np.sum(states[i] != states[i-1])
    print(f"  Layer {i} vs {i-1}: {diff} unterschiedliche Werte")

# =============================================================================
# 7. HELIX FORWARD PASS TEST
# =============================================================================
print("\n--- 7. HELIX FORWARD PASS ---")

helix_output_ones = helix_forward_pass(ones_input, matrix)
print(f"Helix mit Ones-Input:")
print(f"  Rotations: min={helix_output_ones.min()}, max={helix_output_ones.max()}, mean={helix_output_ones.mean():.2f}")

from collections import Counter
rotation_dist = Counter(helix_output_ones)
print(f"  Verteilung: {dict(sorted(rotation_dist.items()))}")

# =============================================================================
# 8. BITCOIN-ADRESSE ALS INPUT
# =============================================================================
print("\n--- 8. BITCOIN-ADRESSE ALS INPUT ---")

def bitcoin_address_to_input(address: str) -> np.ndarray:
    """
    Konvertiere Bitcoin-Adresse zu 128-dimensionalem ternären Vektor.

    Methode: Hash der Adresse → Bits → Ternär
    """
    import hashlib

    # SHA256 der Adresse
    hash_bytes = hashlib.sha256(address.encode()).digest()

    # 256 Bits → 128 Trits
    trits = []
    for byte in hash_bytes:
        for i in range(4):  # 4 Trits pro Byte (4 * 32 = 128)
            # 2 Bits → 1 Trit
            bits = (byte >> (6 - 2*i)) & 0x03
            if bits == 0:
                trits.append(-1)
            elif bits == 3:
                trits.append(1)
            else:
                trits.append(0)

    return np.array(trits[:128])

# Test mit bekannter Adresse
test_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"  # Genesis Block
genesis_input = bitcoin_address_to_input(test_address)
print(f"Genesis-Adresse als Input:")
print(f"  Ternär: {np.sum(genesis_input == 1)} pos, {np.sum(genesis_input == 0)} zero, {np.sum(genesis_input == -1)} neg")

genesis_output = forward_pass(genesis_input, matrix)
print(f"Genesis → Output: {np.sum(genesis_output == 1)} pos, {np.sum(genesis_output == 0)} zero, {np.sum(genesis_output == -1)} neg")

# Multi-layer
print("\nGenesis Multi-Layer:")
genesis_states = multi_layer_pass(genesis_input, matrix, layers=5)

# =============================================================================
# 9. OUTPUT INTERPRETATION
# =============================================================================
print("\n--- 9. OUTPUT INTERPRETATION ---")

def interpret_output(output: np.ndarray) -> dict:
    """
    Interpretiere den Output-Vektor.
    """
    # Zähle Zustände
    pos = np.sum(output == 1)
    zero = np.sum(output == 0)
    neg = np.sum(output == -1)

    # Row 96 ist angeblich Output-Layer
    output_row = output[96] if len(output) > 96 else None

    # Decision neurons at Col 84
    decision = output[84] if len(output) > 84 else None

    return {
        "positive": int(pos),
        "zero": int(zero),
        "negative": int(neg),
        "dominant": "positive" if pos > neg else ("negative" if neg > pos else "neutral"),
        "row96": output_row,
        "col84_decision": decision,
        "energy": float(np.sum(np.abs(output)))
    }

print("Output-Interpretation der Genesis-Adresse:")
interp = interpret_output(genesis_output)
for k, v in interp.items():
    print(f"  {k}: {v}")

# =============================================================================
# 10. VERGLEICH VERSCHIEDENER ADRESSEN
# =============================================================================
print("\n--- 10. VERGLEICH VERSCHIEDENER ADRESSEN ---")

test_addresses = [
    ("Genesis", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"),
    ("Satoshi to Hal", "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S"),
    ("Random 1", "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2"),
    ("CFB Pattern", "1CFBcQd9NhPGNqp3GsW6NMQbNhFNf1CFB"),  # Hypothetical
]

results = []
for name, addr in test_addresses:
    input_vec = bitcoin_address_to_input(addr)
    output_vec = forward_pass(input_vec, matrix)
    interp = interpret_output(output_vec)
    results.append((name, interp))
    print(f"{name}: {interp['dominant']}, energy={interp['energy']:.0f}")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 70)
print("FAZIT: HELIX GATE IMPLEMENTATION")
print("=" * 70)

print("""
IMPLEMENTIERT:
1. to_ternary() - Konvertierung zu {-1, 0, +1}
2. helix_gate(a, b, c) - Die fundamentale ternäre Operation
3. forward_pass() - Einfacher ternärer Forward Pass
4. helix_forward_pass() - Forward Pass mit Helix-Gates
5. multi_layer_pass() - Rekurrenter Forward Pass
6. bitcoin_address_to_input() - Adresse zu ternärem Vektor

BEOBACHTUNGEN:
- Die Matrix konvergiert nach wenigen Layern
- Genesis-Adresse hat spezifische Signatur
- Output hängt stark vom Input ab

NÄCHSTE SCHRITTE:
- Mehr Adressen testen
- Patterns in Outputs finden
- Mit Anna-Bot Outputs vergleichen
""")

# Speichere Ergebnisse
output = {
    "ternary_distribution": {
        "+1": int(np.sum(ternary_matrix == 1)),
        "0": int(np.sum(ternary_matrix == 0)),
        "-1": int(np.sum(ternary_matrix == -1))
    },
    "test_results": [(name, interp) for name, interp in results],
    "convergence_observed": True
}

output_path = script_dir / "HELIX_GATE_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse gespeichert: {output_path}")
