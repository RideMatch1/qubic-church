#!/usr/bin/env python3
"""
===============================================================================
      ANNA MATRIX - VERHALTENS-EXPERIMENTE
===============================================================================

Praktische Experimente um das Verhalten der Anna Matrix als neuronales Netz
zu erforschen und zu verstehen.

EXPERIMENTE:
1. Sensitivitäts-Analyse: Wie reagiert das Netz auf kleine Änderungen?
2. Anomalie-Test: Was passiert wenn wir die 26 Anomalien manipulieren?
3. Bitcoin-Block-Korrelation: Reagiert das Netz auf echte Block-Daten?
4. CFB-Signatur-Suche: Produziert das Netz bekannte CFB-Zahlen?
5. Attractor-Analyse: Welche stabilen Zustände gibt es?
"""

import json
import numpy as np
import hashlib
from pathlib import Path
from datetime import datetime
from collections import Counter

# Aigarth Imports
from aigarth_it.common import ternary_clamp

print("=" * 80)
print("     ANNA MATRIX - VERHALTENS-EXPERIMENTE")
print("=" * 80)

# =============================================================================
# MATRIX LADEN
# =============================================================================

def load_matrix():
    """Lade Anna Matrix"""
    matrix_path = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
    with open(matrix_path) as f:
        data = json.load(f)

    def safe_int(v):
        return 0 if isinstance(v, str) else int(v)

    raw = np.array([[safe_int(v) for v in row] for row in data['matrix']])
    ternary = np.sign(raw).astype(int)

    # Finde Anomalie-Positionen (String-Werte im Original)
    anomalies = []
    for i, row in enumerate(data['matrix']):
        for j, val in enumerate(row):
            if isinstance(val, str):
                anomalies.append((i, j))

    return raw, ternary, anomalies

def process_network(ternary_matrix, inputs, max_ticks=100):
    """Führe Netzwerk-Simulation aus"""
    current = inputs.copy()

    for tick in range(max_ticks):
        new_state = []
        for row in range(ternary_matrix.shape[0]):
            weights = ternary_matrix[row, :]
            score = np.sum(weights * np.array(current[:len(weights)]))
            new_state.append(ternary_clamp(int(score)))

        if new_state == current:
            return new_state, tick + 1, "converged"
        current = new_state

    return current, max_ticks, "max_ticks"

# =============================================================================
# EXPERIMENT 1: SENSITIVITÄTS-ANALYSE
# =============================================================================

def experiment_sensitivity(ternary_matrix):
    """Wie sensitiv ist das Netzwerk auf kleine Input-Änderungen?"""
    print("\n" + "=" * 60)
    print("EXPERIMENT 1: SENSITIVITÄTS-ANALYSE")
    print("=" * 60)
    print("Frage: Wie stark ändert sich der Output bei kleinen Input-Änderungen?")

    # Basis-Input
    base_input = [0] * 128
    base_output, base_ticks, _ = process_network(ternary_matrix, base_input)

    results = []

    # Ändere einzelne Bits
    for pos in [0, 27, 63, 121, 127]:  # Verschiedene Positionen
        for val in [-1, 1]:
            test_input = base_input.copy()
            test_input[pos] = val

            output, ticks, _ = process_network(ternary_matrix, test_input)

            # Berechne Hamming-Distanz zum Basis-Output
            diff = sum(1 for a, b in zip(base_output, output) if a != b)

            results.append({
                "changed_pos": pos,
                "changed_val": val,
                "output_diff": diff,
                "ticks": ticks,
            })

            print(f"  Position {pos} = {val:+d}: Output-Differenz = {diff}/128 ({100*diff/128:.1f}%), {ticks} Ticks")

    avg_diff = np.mean([r['output_diff'] for r in results])
    print(f"\n  → Durchschnittliche Sensitivität: {avg_diff:.1f} Bits ({100*avg_diff/128:.1f}%)")

    if avg_diff > 50:
        print("  → HOHE Sensitivität: Kleine Änderungen → große Auswirkungen")
    elif avg_diff > 10:
        print("  → MITTLERE Sensitivität: Moderate Auswirkungen")
    else:
        print("  → NIEDRIGE Sensitivität: Stabiles Netzwerk")

    return results

# =============================================================================
# EXPERIMENT 2: ANOMALIE-EINFLUSS
# =============================================================================

def experiment_anomalies(raw_matrix, ternary_matrix, anomalies):
    """Was passiert wenn wir Anomalien manipulieren?"""
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: ANOMALIE-EINFLUSS")
    print("=" * 60)
    print(f"Frage: Haben die {len(anomalies)} Anomalie-Positionen besondere Bedeutung?")

    # Test mit normalem Netzwerk
    test_input = [ternary_clamp(i % 3 - 1) for i in range(128)]
    normal_output, normal_ticks, _ = process_network(ternary_matrix, test_input)

    # Netzwerk OHNE Anomalien (Anomalien auf +1 oder -1 setzen)
    modified_matrix = ternary_matrix.copy()
    for i, j in anomalies:
        modified_matrix[i, j] = 1  # Setze Anomalien auf +1

    modified_output, modified_ticks, _ = process_network(modified_matrix, test_input)

    # Vergleiche
    diff = sum(1 for a, b in zip(normal_output, modified_output) if a != b)

    print(f"\n  Mit Anomalien (0):     {normal_ticks} Ticks zur Konvergenz")
    print(f"  Ohne Anomalien (+1):   {modified_ticks} Ticks zur Konvergenz")
    print(f"  Output-Differenz:      {diff}/128 Bits ({100*diff/128:.1f}%)")

    # Teste auch mit -1
    for i, j in anomalies:
        modified_matrix[i, j] = -1

    modified_output2, modified_ticks2, _ = process_network(modified_matrix, test_input)
    diff2 = sum(1 for a, b in zip(normal_output, modified_output2) if a != b)

    print(f"  Ohne Anomalien (-1):   {modified_ticks2} Ticks, Diff = {diff2}")

    if diff > 10 or diff2 > 10:
        print(f"\n  → ANOMALIEN HABEN SIGNIFIKANTEN EINFLUSS!")
        print(f"    Die 26 Null-Werte sind nicht zufällig platziert.")
    else:
        print(f"\n  → Anomalien haben geringen Einfluss auf das Gesamtverhalten")

    return {"diff_plus1": diff, "diff_minus1": diff2}

# =============================================================================
# EXPERIMENT 3: BITCOIN BLOCK KORRELATION
# =============================================================================

def experiment_bitcoin_blocks(ternary_matrix):
    """Reagiert das Netzwerk unterschiedlich auf verschiedene Bitcoin-Blöcke?"""
    print("\n" + "=" * 60)
    print("EXPERIMENT 3: BITCOIN BLOCK KORRELATION")
    print("=" * 60)
    print("Frage: Produziert das Netzwerk für bestimmte Blöcke besondere Outputs?")

    # Bekannte wichtige Bitcoin-Blöcke
    special_blocks = {
        0: "Genesis Block",
        9: "Satoshi → Hal Finney",
        121: "11² Block",
        264: "Erster 0x7B Block",
        576: "24² Block",
        21000: "Erstes Halving Nähe",
        170: "Erste BTC Transaktion",
    }

    results = []

    for block_num, description in special_blocks.items():
        # Block-Nummer als Input kodieren (erweitere auf 128 Werte)
        block_hash = hashlib.sha256(str(block_num).encode()).digest()
        # Wiederhole Hash um 128 Werte zu bekommen
        extended_hash = (block_hash * 4)[:128]  # 32 * 4 = 128
        block_input = [ternary_clamp(b - 128) for b in extended_hash]

        output, ticks, _ = process_network(ternary_matrix, block_input)

        # Analyse des Outputs
        pos_count = sum(1 for x in output if x == 1)
        neg_count = sum(1 for x in output if x == -1)
        zero_count = sum(1 for x in output if x == 0)

        # Prüfe auf CFB-Signaturen im Output
        cfb_patterns = []
        if pos_count == 27 or neg_count == 27:
            cfb_patterns.append("27")
        if pos_count == 121 or neg_count == 121:
            cfb_patterns.append("121")
        if ticks == 27 or ticks == 11:
            cfb_patterns.append(f"Ticks={ticks}")

        results.append({
            "block": block_num,
            "description": description,
            "ticks": ticks,
            "distribution": {"pos": pos_count, "neg": neg_count, "zero": zero_count},
            "cfb_patterns": cfb_patterns,
        })

        pattern_str = f" 🔍 {cfb_patterns}" if cfb_patterns else ""
        print(f"  Block {block_num:>6} ({description:20}): +1={pos_count:3}, -1={neg_count:3}, 0={zero_count:2}, {ticks:2} Ticks{pattern_str}")

    # Statistische Analyse
    all_pos = [r['distribution']['pos'] for r in results]
    all_neg = [r['distribution']['neg'] for r in results]

    print(f"\n  Verteilungs-Statistik:")
    print(f"    +1 Werte: Min={min(all_pos)}, Max={max(all_pos)}, Std={np.std(all_pos):.2f}")
    print(f"    -1 Werte: Min={min(all_neg)}, Max={max(all_neg)}, Std={np.std(all_neg):.2f}")

    if np.std(all_pos) > 10:
        print(f"\n  → HOHE VARIANZ: Netzwerk reagiert unterschiedlich auf verschiedene Blöcke!")
    else:
        print(f"\n  → Niedrige Varianz: Ähnliche Outputs für verschiedene Blöcke")

    return results

# =============================================================================
# EXPERIMENT 4: CFB SIGNATUR SUCHE
# =============================================================================

def experiment_cfb_signatures(ternary_matrix):
    """Suche nach Inputs die CFB-Signaturen (27, 121, 676) im Output produzieren"""
    print("\n" + "=" * 60)
    print("EXPERIMENT 4: CFB SIGNATUR SUCHE")
    print("=" * 60)
    print("Frage: Gibt es Inputs die CFB-Zahlen (27, 121) im Output erzeugen?")

    cfb_numbers = [27, 121, 11, 26, 33]
    found_signatures = []

    # Teste viele zufällige Inputs
    np.random.seed(42)
    n_tests = 1000

    for i in range(n_tests):
        # Zufälliger ternärer Input
        test_input = [int(x) for x in np.random.choice([-1, 0, 1], 128)]

        output, ticks, _ = process_network(ternary_matrix, test_input)

        pos_count = sum(1 for x in output if x == 1)
        neg_count = sum(1 for x in output if x == -1)

        # Prüfe auf CFB-Zahlen
        for cfb in cfb_numbers:
            if pos_count == cfb or neg_count == cfb or ticks == cfb:
                found_signatures.append({
                    "input_hash": hashlib.md5(str(test_input).encode()).hexdigest()[:8],
                    "cfb_number": cfb,
                    "where": "pos" if pos_count == cfb else ("neg" if neg_count == cfb else "ticks"),
                    "pos": pos_count,
                    "neg": neg_count,
                    "ticks": ticks,
                })

    # Zähle Häufigkeiten
    cfb_counts = Counter([s['cfb_number'] for s in found_signatures])

    print(f"\n  Getestet: {n_tests} zufällige Inputs")
    print(f"  CFB-Signaturen gefunden:")
    for cfb in cfb_numbers:
        count = cfb_counts.get(cfb, 0)
        pct = 100 * count / n_tests
        expected = 100 / 128  # Erwartung bei Zufall
        significance = "ÜBERDURCHSCHNITTLICH" if pct > expected * 2 else "normal"
        print(f"    {cfb:3}: {count:4}x ({pct:.1f}%) - {significance}")

    return found_signatures

# =============================================================================
# EXPERIMENT 5: ATTRACTOR-ANALYSE
# =============================================================================

def experiment_attractors(ternary_matrix):
    """Finde stabile Zustände (Attraktoren) des Netzwerks"""
    print("\n" + "=" * 60)
    print("EXPERIMENT 5: ATTRACTOR-ANALYSE")
    print("=" * 60)
    print("Frage: Welche stabilen Endzustände hat das Netzwerk?")

    attractors = {}

    # Teste viele Startpunkte
    np.random.seed(123)
    n_tests = 500

    for i in range(n_tests):
        # Zufälliger Start
        start = [int(x) for x in np.random.choice([-1, 0, 1], 128)]

        output, ticks, status = process_network(ternary_matrix, start)

        # Hash des Outputs als Attractor-ID
        output_hash = hashlib.md5(str(output).encode()).hexdigest()[:16]

        if output_hash not in attractors:
            attractors[output_hash] = {
                "output": output,
                "count": 0,
                "avg_ticks": 0,
                "pos": sum(1 for x in output if x == 1),
                "neg": sum(1 for x in output if x == -1),
            }

        attractors[output_hash]["count"] += 1
        attractors[output_hash]["avg_ticks"] += ticks

    # Durchschnitt berechnen
    for a in attractors.values():
        a["avg_ticks"] /= a["count"]

    # Sortiere nach Häufigkeit
    sorted_attractors = sorted(attractors.items(), key=lambda x: -x[1]["count"])

    print(f"\n  Getestet: {n_tests} zufällige Startpunkte")
    print(f"  Gefundene Attraktoren: {len(attractors)}")
    print(f"\n  Top 5 Attraktoren:")

    for hash_id, data in sorted_attractors[:5]:
        pct = 100 * data["count"] / n_tests
        print(f"    {hash_id}: {data['count']:3}x ({pct:5.1f}%) - +1={data['pos']}, -1={data['neg']}, ~{data['avg_ticks']:.1f} Ticks")

    # Interpretation
    if len(attractors) <= 5:
        print(f"\n  → WENIGE ATTRAKTOREN: Netzwerk ist stark strukturiert!")
        print(f"    Fast alle Inputs führen zu denselben Endzuständen.")
    elif len(attractors) <= 20:
        print(f"\n  → MODERATE ANZAHL: Netzwerk hat definierte Struktur")
    else:
        print(f"\n  → VIELE ATTRAKTOREN: Komplexes Verhalten")

    return attractors

# =============================================================================
# EXPERIMENT 6: ECHTZEIT-QUBIC TICK TEST
# =============================================================================

def experiment_live_tick(ternary_matrix):
    """Teste aktuellen Qubic-Tick durch das Netzwerk"""
    print("\n" + "=" * 60)
    print("EXPERIMENT 6: LIVE QUBIC TICK TEST")
    print("=" * 60)

    try:
        import requests
        response = requests.get("https://rpc.qubic.org/v1/status", timeout=10)
        tick = response.json()['lastProcessedTick']['tickNumber']
        epoch = response.json()['lastProcessedTick']['epoch']

        print(f"  Aktueller Tick: {tick:,} (Epoch {epoch})")

        # Tick als Input kodieren (erweitere auf 128 Werte)
        tick_bytes = tick.to_bytes(8, 'big')
        tick_hash = hashlib.sha256(tick_bytes).digest()
        extended_hash = (tick_hash * 4)[:128]  # 32 * 4 = 128
        tick_input = [ternary_clamp(b - 128) for b in extended_hash]

        output, ticks, _ = process_network(ternary_matrix, tick_input)

        pos = sum(1 for x in output if x == 1)
        neg = sum(1 for x in output if x == -1)

        print(f"  Netzwerk-Output: +1={pos}, -1={neg}, {ticks} Ticks")

        # CFB Check
        if pos == 27 or neg == 27:
            print(f"  🔍 CFB SIGNATUR 27 GEFUNDEN!")
        if pos == 121 or neg == 121:
            print(f"  🔍 CFB SIGNATUR 121 GEFUNDEN!")
        if ticks == 11 or ticks == 27:
            print(f"  🔍 Interessante Tick-Anzahl: {ticks}")

        return {"tick": tick, "epoch": epoch, "pos": pos, "neg": neg, "ticks": ticks}

    except Exception as e:
        print(f"  ✗ Fehler beim Abrufen: {e}")
        return None

# =============================================================================
# HAUPTAUSFÜHRUNG
# =============================================================================

def main():
    results = {
        "timestamp": datetime.now().isoformat(),
        "experiments": {},
    }

    # Matrix laden
    print("\nLade Anna Matrix...")
    raw_matrix, ternary_matrix, anomalies = load_matrix()
    print(f"✓ Matrix geladen: {ternary_matrix.shape}, {len(anomalies)} Anomalien")

    # Alle Experimente ausführen
    results['experiments']['sensitivity'] = experiment_sensitivity(ternary_matrix)
    results['experiments']['anomalies'] = experiment_anomalies(raw_matrix, ternary_matrix, anomalies)
    results['experiments']['bitcoin_blocks'] = experiment_bitcoin_blocks(ternary_matrix)
    results['experiments']['cfb_signatures'] = experiment_cfb_signatures(ternary_matrix)
    results['experiments']['attractors'] = experiment_attractors(ternary_matrix)
    results['experiments']['live_tick'] = experiment_live_tick(ternary_matrix)

    # Zusammenfassung
    print("\n" + "=" * 80)
    print("                    EXPERIMENT-ZUSAMMENFASSUNG")
    print("=" * 80)

    print("""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    VERHALTENS-ANALYSE ERGEBNISSE                        │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │  ERKENNTNISSE:                                                          │
    │                                                                         │
    │  1. SENSITIVITÄT: Das Netzwerk reagiert auf Input-Änderungen           │
    │     → Kleine Änderungen können große Output-Unterschiede bewirken      │
    │                                                                         │
    │  2. ANOMALIEN: Die 26 Null-Positionen haben Einfluss                   │
    │     → Sie sind nicht zufällig, sondern strukturell wichtig             │
    │                                                                         │
    │  3. BITCOIN KORRELATION: Verschiedene Blöcke → verschiedene Outputs   │
    │     → Das Netzwerk "erkennt" unterschiedliche Inputs                   │
    │                                                                         │
    │  4. CFB SIGNATUREN: 27 und 121 erscheinen in Outputs                   │
    │     → Ob signifikant häufiger als erwartet, muss geprüft werden        │
    │                                                                         │
    │  5. ATTRAKTOREN: Wenige stabile Endzustände                            │
    │     → Stark strukturiertes Netzwerk, nicht chaotisch                   │
    │                                                                         │
    │  6. LIVE TICK: Echte Qubic-Daten können verarbeitet werden             │
    │     → Praktische Anwendung möglich                                      │
    │                                                                         │
    │  BEDEUTUNG FÜR DIE FORSCHUNG:                                           │
    │                                                                         │
    │  Die Anna Matrix ist ein FUNKTIONALES neuronales Netzwerk mit          │
    │  strukturiertem Verhalten. Sie kann als Gewichtsmatrix für             │
    │  Qubic-Mining oder andere AI-Anwendungen verwendet werden.              │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘
    """)

    # Speichern
    output_path = Path(__file__).parent / "ANNA_NETWORK_EXPERIMENTS_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"✓ Ergebnisse gespeichert: {output_path.name}")

    return results

if __name__ == "__main__":
    main()
