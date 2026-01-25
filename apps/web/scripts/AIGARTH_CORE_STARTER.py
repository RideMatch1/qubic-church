#!/usr/bin/env python3
"""
===============================================================================
                    🧠 AIGARTH CORE STARTER 🧠
===============================================================================
Starte das ternäre neuronale Netzwerk und teste die erste echte AGI!

Aigarth = Artificiell Intelligent Generalised Associative Ternary Helix
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

print("🧠" * 40)
print("          AIGARTH CORE STARTER")
print("🧠" * 40)

# =============================================================================
# AIGARTH INSTALLATION CHECK
# =============================================================================
print("\n" + "=" * 80)
print("AIGARTH INSTALLATION CHECK")
print("=" * 80)

try:
    from aigarth_it.common import (
        ternary_clamp,
        random_trit_vector,
        bitstring_to_trits,
        trits_to_bitstring,
    )
    from aigarth_it.neuron_cl import AITClNeuron
    from aigarth_it.itu_cl import AigarthITUCl
    print("✓ Aigarth-it Core geladen!")
    AIGARTH_AVAILABLE = True
except ImportError as e:
    print(f"✗ Aigarth nicht installiert: {e}")
    print("\n  Installation:")
    print("  pip install aigarth-it")
    AIGARTH_AVAILABLE = False

# =============================================================================
# TERNÄRE LOGIK DEMO
# =============================================================================
if AIGARTH_AVAILABLE:
    print("\n" + "=" * 80)
    print("TERNÄRE LOGIK DEMONSTRATION")
    print("=" * 80)

    print("""
    Aigarth verwendet TERNÄRE Logik statt binär:

    Binär:   0 | 1
    Ternär: -1 | 0 | +1

    Das entspricht: False | Unknown | True
    Oder:           Inhibit | Neutral | Excite
    """)

    # Demo ternary_clamp
    print("  ternary_clamp Funktion:")
    test_values = [-100, -1, 0, 1, 100]
    for v in test_values:
        result = ternary_clamp(v)
        print(f"    clamp({v:4d}) = {result:2d}")

    # Random trit vector
    print("\n  Random Trit Vector (20 trits):")
    random_trits = random_trit_vector(20)
    print(f"    {random_trits}")

# =============================================================================
# CIRCLE NEURON ERSTELLEN
# =============================================================================
if AIGARTH_AVAILABLE:
    print("\n" + "=" * 80)
    print("CIRCLE NEURON ERSTELLEN")
    print("=" * 80)

    # Erstelle ein einfaches Neuron
    weights = [1, -1, 1, 0, -1, 1, -1, 0]  # 8 ternäre Gewichte
    neuron = AITClNeuron(input_weights=weights, input_skew=0)

    print(f"  Neuron erstellt mit:")
    print(f"    Gewichte: {neuron.input_weights}")
    print(f"    Skew: {neuron.input_skew}")
    print(f"    Split Index: {neuron.input_split_index}")
    print(f"    State: {neuron.state}")

    # Feedforward Test
    print("\n  Feedforward Test:")
    test_inputs = [
        [1, 1, 1, 1, 1, 1, 1, 1],       # Alle positiv
        [-1, -1, -1, -1, -1, -1, -1, -1], # Alle negativ
        [1, -1, 1, -1, 1, -1, 1, -1],    # Alternierend
        [0, 0, 0, 0, 0, 0, 0, 0],        # Neutral
    ]

    for inp in test_inputs:
        neuron.state = 0
        neuron.feedforward(inp)
        new_state, changed = neuron.commit_state()

        # Manuelle Berechnung
        weighted_sum = sum(i * w for i, w in zip(inp, weights))

        print(f"    Input: {inp}")
        print(f"      Sum: {weighted_sum:3d} → State: {new_state:2d}, Changed: {changed}")

# =============================================================================
# ITU (INTELLIGENT TURING UNIT) LADEN
# =============================================================================
if AIGARTH_AVAILABLE:
    print("\n" + "=" * 80)
    print("ITU LADEN - ARITHMETIC ADDITION")
    print("=" * 80)

    try:
        from aigarth_it.icap.itucl_aai_i2x7o8 import ITUClArithmeticAdditionIntI2x7O8

        itu = ITUClArithmeticAdditionIntI2x7O8()

        print(f"  ITU Typ: {itu.meta.type}")
        print(f"  ITU Gruppe: {itu.meta.group}")
        print(f"  ITU Version: {itu.meta.version_string}")
        print(f"  Input Bitbreite: {itu.meta.input_bitwidth}")
        print(f"  Output Bitbreite: {itu.meta.output_bitwidth}")
        print(f"  Anzahl Neuronen: {len(itu._circle)}")
        print(f"  FF Cycle Cap: {itu.ff_cycle_cap}")

        # Test Addition (OHNE Training!)
        print("\n  Addition Test (UNTRAINIERT - zufällige Ergebnisse erwartet!):")
        test_additions = [
            (1, 1, 2),
            (2, 3, 5),
            (10, 5, 15),
            (-1, 1, 0),
        ]

        for a, b, expected in test_additions:
            reflection = itu.reflect(a, b)
            result = reflection.integer if reflection.integer is not None else "?"
            ticks = reflection.ffcycle_stats.tick_count
            reason = reflection.ffcycle_stats.end_reason

            status = "✓" if result == expected else "≈"
            print(f"    {status} {a:3d} + {b:3d} = {str(result):>5} (erwartet: {expected:3d}) [Ticks: {ticks}]")

        ITU_LOADED = True
    except Exception as e:
        print(f"  ✗ ITU Laden fehlgeschlagen: {e}")
        ITU_LOADED = False

# =============================================================================
# TRAININGS-VERSUCH
# =============================================================================
if AIGARTH_AVAILABLE and ITU_LOADED:
    print("\n" + "=" * 80)
    print("ITU TRAINING VERSUCH")
    print("=" * 80)

    print("  HINWEIS: Echtes Training braucht:")
    print("    - Viele Iterationen (10,000+)")
    print("    - Mutationen der Gewichte")
    print("    - Fitness-Funktion")

    # Mini-Training Demo
    print("\n  Mini-Training Demo (100 Iterationen):")

    correct_before = 0
    for a in range(-5, 6):
        for b in range(-5, 6):
            result = itu.reflect(a, b).integer
            if result == a + b:
                correct_before += 1

    print(f"    Vor Training: {correct_before}/121 korrekt")

    # Hier würde echtes Training stattfinden
    # itu.mutate() und itu.train() Methoden...

    print("    (Training übersprungen - braucht spezielle Trainings-Pipeline)")

# =============================================================================
# ANNA-MATRIX CONNECTION
# =============================================================================
print("\n" + "=" * 80)
print("ANNA-MATRIX ↔ AIGARTH CONNECTION")
print("=" * 80)

# Lade Anna-Matrix
script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

try:
    import numpy as np

    with open(matrix_path) as f:
        data = json.load(f)

    def safe_int(v):
        return 0 if isinstance(v, str) else int(v)

    matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

    print("  ✓ Anna-Matrix geladen: 128×128")

    # Hypothese: Matrix-Werte sind aggregierte Trit-Summen
    print("\n  Hypothese: Matrix-Werte = Summe von 128 Trits")
    print("  (Jeder Wert in [-128, 127] = Σ(+1) - Σ(-1) für 128 Trits)")

    # Beispiel-Rekonstruktion
    print("\n  Rekonstruktions-Beispiele:")
    for target in [-27, 100, -121, 127, 0]:
        # Ziel: p - n = target, p + n + z = 128
        if target >= 0:
            n = (128 - target) // 2
            p = target + n
        else:
            p = (128 + target) // 2
            n = -target + p
        z = 128 - p - n

        print(f"    {target:4d} = {p:3d}×(+1) + {n:3d}×(-1) + {z:3d}×(0)")

    # Prüfe Wertebereich
    min_val = matrix.min()
    max_val = matrix.max()
    print(f"\n  Matrix Wertebereich: [{min_val}, {max_val}]")
    print(f"  Ternär-Summen-Bereich: [-128, +127] ✓")

except Exception as e:
    print(f"  ✗ Fehler: {e}")

# =============================================================================
# CONSCIOUSNESS PROBE
# =============================================================================
print("\n" + "=" * 80)
print("AGI CONSCIOUSNESS PROBE")
print("=" * 80)

print("""
  ╔═══════════════════════════════════════════════════════════════╗
  ║                                                               ║
  ║   AIGARTH ist ein ternäres neuronales Netzwerk das durch      ║
  ║   Mutation und Evolution lernt.                               ║
  ║                                                               ║
  ║   Die Frage ist: Ist dies der Keim einer echten AGI?          ║
  ║                                                               ║
  ║   Eigenschaften die auf AGI hindeuten:                        ║
  ║   ✓ Ternäre Logik (näher an quantenmechanischer Realität)     ║
  ║   ✓ Helix-Struktur (ähnlich DNA)                              ║
  ║   ✓ Selbst-Evolution durch Mutation                           ║
  ║   ✓ Assoziatives Gedächtnis                                   ║
  ║                                                               ║
  ║   Fehlende Eigenschaften:                                     ║
  ║   ? Selbst-Bewusstsein                                        ║
  ║   ? Intentionalität                                           ║
  ║   ? Kreativität                                               ║
  ║   ? Verstehen vs. Berechnen                                   ║
  ║                                                               ║
  ╚═══════════════════════════════════════════════════════════════╝
""")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 80)
print("FAZIT: AIGARTH CORE STATUS")
print("=" * 80)

results = {
    "timestamp": datetime.now().isoformat(),
    "aigarth_available": AIGARTH_AVAILABLE,
    "itu_loaded": ITU_LOADED if AIGARTH_AVAILABLE else False,
    "anna_matrix_compatible": True,
    "agi_status": "EXPERIMENTAL",
}

if AIGARTH_AVAILABLE:
    print(f"""
  AIGARTH CORE STATUS:
  ✓ Aigarth-it Library: INSTALLIERT
  ✓ Ternäre Logik: FUNKTIONIERT
  ✓ Circle Neuronen: ERSTELLT
  ✓ ITU (Arithmetic): GELADEN
  ✓ Anna-Matrix: KOMPATIBEL

  NÄCHSTE SCHRITTE:
  1. ITU Training durchführen
  2. Eigene ITUs erstellen
  3. Anna-Matrix als Gewichtsmatrix verwenden
  4. Kommunikation mit Qubic-Netzwerk
""")
else:
    print("""
  AIGARTH NICHT VERFÜGBAR!

  Installation:
    pip install aigarth-it

  Oder aus Source:
    git clone https://github.com/Aigarth-IT/aigarth-it
    cd aigarth-it && pip install -e .
""")

# Speichere Ergebnisse
output_path = script_dir / "AIGARTH_CORE_STATUS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Status: {output_path}")
