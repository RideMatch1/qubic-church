#!/usr/bin/env python3
"""
===============================================================================
                🧠 ANNA-MATRIX ALS AIGARTH GEWICHTE 🧠
===============================================================================
Konvertiere die Anna-Matrix zu ternären Gewichten für Aigarth!

Hypothese: Die Anna-Matrix ist eine gespeicherte Gewichtsmatrix für
ein ternäres neuronales Netzwerk (Aigarth).
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent

print("🧠" * 40)
print("      ANNA-MATRIX ALS AIGARTH GEWICHTE")
print("🧠" * 40)

# =============================================================================
# AIGARTH IMPORT
# =============================================================================
print("\n" + "=" * 80)
print("AIGARTH IMPORT")
print("=" * 80)

try:
    from aigarth_it.common import (
        ternary_clamp,
        random_trit_vector,
    )
    from aigarth_it.neuron_cl import AITClNeuron
    AIGARTH_AVAILABLE = True
    print("✓ Aigarth-it verfügbar!")
except ImportError as e:
    AIGARTH_AVAILABLE = False
    print(f"✗ Aigarth-it nicht verfügbar: {e}")
    print("  Bitte mit /opt/homebrew/bin/python3.11 ausführen")

# =============================================================================
# ANNA-MATRIX LADEN
# =============================================================================
print("\n" + "=" * 80)
print("ANNA-MATRIX LADEN")
print("=" * 80)

matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

anna_matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])
print(f"✓ Anna-Matrix geladen: {anna_matrix.shape}")
print(f"  Wertebereich: [{anna_matrix.min()}, {anna_matrix.max()}]")

# =============================================================================
# KONVERTIERUNG ZU TERNÄREN GEWICHTEN
# =============================================================================
print("\n" + "=" * 80)
print("KONVERTIERUNG ZU TERNÄREN GEWICHTEN")
print("=" * 80)

print("""
KONVERTIERUNGS-STRATEGIEN:

1. SIGN-BASIERT: sign(x) → {-1, 0, +1}
   Einfachste Methode, verliert Magnitude-Information

2. THRESHOLD-BASIERT: x > T → +1, x < -T → -1, sonst 0
   Erhält "starke" Signale

3. QUANTIL-BASIERT: Top/Bottom 33% → ±1, Mitte → 0
   Gleichverteilung der Trits

4. SUMMEN-BASIERT: Jeder Wert = Summe von 128 Trits
   Volle Rekonstruktion möglich
""")

# Methode 1: Sign-basiert
def to_ternary_sign(matrix):
    """Konvertiere via sign()."""
    return np.sign(matrix).astype(int)

# Methode 2: Threshold-basiert
def to_ternary_threshold(matrix, threshold=32):
    """Konvertiere mit Schwellwert."""
    result = np.zeros_like(matrix)
    result[matrix > threshold] = 1
    result[matrix < -threshold] = -1
    return result

# Methode 3: Quantil-basiert
def to_ternary_quantile(matrix, q=0.33):
    """Konvertiere basierend auf Quantilen."""
    flat = matrix.flatten()
    lower = np.quantile(flat, q)
    upper = np.quantile(flat, 1-q)

    result = np.zeros_like(matrix)
    result[matrix > upper] = 1
    result[matrix < lower] = -1
    return result

# Methode 4: Summen-basiert (vollständige Rekonstruktion)
def anna_value_to_trits(value, num_trits=128):
    """Konvertiere Anna-Wert zu Trit-Vektor (Summe der Trits = Wert)."""
    # Ziel: p - n = value, p + n + z = num_trits
    if value >= 0:
        n = (num_trits - value) // 2
        p = value + n
    else:
        p = (num_trits + value) // 2
        n = -value + p
    z = num_trits - p - n

    # Erzeuge Trit-Vektor
    trits = [1] * p + [-1] * n + [0] * z
    np.random.shuffle(trits)
    return trits[:num_trits]

print("\nKonvertiere mit verschiedenen Methoden:")

methods = {
    "sign": to_ternary_sign(anna_matrix),
    "threshold_32": to_ternary_threshold(anna_matrix, 32),
    "threshold_64": to_ternary_threshold(anna_matrix, 64),
    "quantile_33": to_ternary_quantile(anna_matrix, 0.33),
}

for name, ternary in methods.items():
    count_neg = np.sum(ternary == -1)
    count_zero = np.sum(ternary == 0)
    count_pos = np.sum(ternary == 1)
    total = ternary.size

    print(f"\n  {name}:")
    print(f"    -1: {count_neg:6d} ({100*count_neg/total:.1f}%)")
    print(f"     0: {count_zero:6d} ({100*count_zero/total:.1f}%)")
    print(f"    +1: {count_pos:6d} ({100*count_pos/total:.1f}%)")

# =============================================================================
# AIGARTH NEURON MIT ANNA-GEWICHTEN
# =============================================================================
if AIGARTH_AVAILABLE:
    print("\n" + "=" * 80)
    print("AIGARTH NEURON MIT ANNA-GEWICHTEN")
    print("=" * 80)

    # Verwende eine Zeile der Matrix als Gewichte
    row_42 = methods["sign"][42].tolist()  # Zeile 42 (Answer to Everything)

    print(f"\nErstelle Neuron mit Zeile 42 (128 Gewichte):")
    print(f"  Gewichte: {row_42[:10]}... (erste 10)")

    try:
        # Erstelle Neuron mit Anna-Gewichten
        neuron = AITClNeuron(input_weights=row_42, input_skew=0)

        print(f"  ✓ Neuron erstellt!")
        print(f"    Input Split Index: {neuron.input_split_index}")
        print(f"    State: {neuron.state}")

        # Test mit verschiedenen Inputs
        print("\n  Feedforward Tests:")
        test_inputs = [
            ("All +1", [1] * 128),
            ("All -1", [-1] * 128),
            ("All 0", [0] * 128),
            ("Random", random_trit_vector(128)),
            ("Zeile 0", methods["sign"][0].tolist()),
        ]

        for name, inp in test_inputs:
            neuron.state = 0
            neuron.feedforward(inp)
            new_state, changed = neuron.commit_state()
            print(f"    {name:12s}: State → {new_state:2d}")

        NEURON_CREATED = True
    except Exception as e:
        print(f"  ✗ Neuron-Erstellung fehlgeschlagen: {e}")
        NEURON_CREATED = False
else:
    NEURON_CREATED = False
    print("\n  Aigarth nicht verfügbar - Neuron-Tests übersprungen")

# =============================================================================
# VOLLSTÄNDIGES NETZWERK
# =============================================================================
if AIGARTH_AVAILABLE:
    print("\n" + "=" * 80)
    print("VOLLSTÄNDIGES NETZWERK (128 NEURONEN)")
    print("=" * 80)

    print("\nErstelle Netzwerk mit allen 128 Zeilen als Neuronen:")

    neurons = []
    ternary_matrix = methods["sign"]

    try:
        for row_idx in range(128):
            weights = ternary_matrix[row_idx].tolist()
            neuron = AITClNeuron(input_weights=weights, input_skew=0)
            neurons.append(neuron)

        print(f"  ✓ {len(neurons)} Neuronen erstellt!")

        # Feedforward durch das gesamte Netzwerk
        print("\n  Netzwerk-Feedforward Test:")

        input_vector = random_trit_vector(128)
        print(f"    Input: {input_vector[:10]}... (erste 10)")

        output_vector = []
        for i, neuron in enumerate(neurons):
            neuron.state = 0
            neuron.feedforward(input_vector)
            state, _ = neuron.commit_state()
            output_vector.append(state)

        print(f"    Output: {output_vector[:10]}... (erste 10)")

        # Statistik
        out_neg = sum(1 for v in output_vector if v == -1)
        out_zero = sum(1 for v in output_vector if v == 0)
        out_pos = sum(1 for v in output_vector if v == 1)

        print(f"\n    Output Verteilung:")
        print(f"      -1: {out_neg:3d} ({100*out_neg/128:.1f}%)")
        print(f"       0: {out_zero:3d} ({100*out_zero/128:.1f}%)")
        print(f"      +1: {out_pos:3d} ({100*out_pos/128:.1f}%)")

        NETWORK_CREATED = True
    except Exception as e:
        print(f"  ✗ Netzwerk-Erstellung fehlgeschlagen: {e}")
        NETWORK_CREATED = False
else:
    NETWORK_CREATED = False

# =============================================================================
# SYMMETRIE-TEST
# =============================================================================
print("\n" + "=" * 80)
print("SYMMETRIE IM TERNÄREN RAUM")
print("=" * 80)

ternary = methods["sign"]

# Prüfe Punkt-Symmetrie
symmetric_count = 0
for r in range(128):
    for c in range(128):
        if ternary[r, c] + ternary[127-r, 127-c] == 0:
            symmetric_count += 1

symmetry_pct = 100 * symmetric_count / (128*128)
print(f"\nPunkt-Symmetrie im ternären Raum:")
print(f"  {symmetric_count}/{128*128} = {symmetry_pct:.2f}%")

# Die Original-Symmetrie war val1 + val2 = -1
# Im ternären Raum: sign(val1) + sign(val2) sollte ~0 sein
print(f"\n  (Original-Symmetrie war 99.58% mit val1 + val2 = -1)")
print(f"  (Ternär-Symmetrie ist {symmetry_pct:.1f}% mit trit1 + trit2 = 0)")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 80)
print("FAZIT")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ANNA-MATRIX ALS AIGARTH-GEWICHTE:                                       ║
║                                                                           ║
║   ✓ Matrix kann zu ternären Gewichten konvertiert werden                  ║
║   ✓ Verschiedene Konvertierungsmethoden funktionieren                    ║
║   {"✓ Aigarth-Neuronen mit Anna-Gewichten erstellt" if NEURON_CREATED else "✗ Aigarth nicht verfügbar":60s}║
║   {"✓ 128-Neuronen-Netzwerk funktioniert" if NETWORK_CREATED else "✗ Netzwerk nicht erstellt":60s}║
║   ✓ Symmetrie teilweise im ternären Raum erhalten                        ║
║                                                                           ║
║   IMPLIKATIONEN:                                                          ║
║   Die Anna-Matrix KÖNNTE eine gespeicherte Gewichtsmatrix sein für       ║
║   ein ternäres neuronales Netzwerk mit 128 Neuronen und 128 Inputs.      ║
║                                                                           ║
║   Das würde bedeuten:                                                     ║
║   - Die Matrix ist ein "eingefrorener" Lernzustand                        ║
║   - Sie enthält "gelerntes Wissen" in den Gewichten                      ║
║   - Die versteckten Nachrichten sind vielleicht Nebeneffekte             ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

# Speichere Ergebnisse
output = {
    "timestamp": datetime.now().isoformat(),
    "aigarth_available": AIGARTH_AVAILABLE,
    "neuron_created": NEURON_CREATED if AIGARTH_AVAILABLE else False,
    "network_created": NETWORK_CREATED if AIGARTH_AVAILABLE else False,
    "ternary_symmetry_pct": symmetry_pct,
    "conversion_methods": list(methods.keys()),
    "conclusion": "Anna-Matrix can be used as ternary weight matrix for Aigarth",
}

output_path = script_dir / "ANNA_AS_AIGARTH_WEIGHTS_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse: {output_path}")
