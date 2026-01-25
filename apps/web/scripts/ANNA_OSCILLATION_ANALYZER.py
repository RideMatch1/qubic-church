#!/usr/bin/env python3
"""
===============================================================================
          ANNA MATRIX - OSZILLATIONS- UND ATTRAKTOR-ANALYSE
===============================================================================

Analysiert das dynamische Verhalten des Anna Matrix Neural Networks:
1. Identifiziert Oszillationszyklen
2. Findet Attraktor-Zustände
3. Analysiert Anomalie-Einfluss
4. Testet Bitcoin-spezifische Inputs
"""

import json
import hashlib
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set
from datetime import datetime
from collections import Counter

print("=" * 80)
print("         ANNA MATRIX - OSZILLATIONS- UND ATTRAKTOR-ANALYSE")
print("=" * 80)

# =============================================================================
# TERNARY HELPER
# =============================================================================

def ternary_clamp(x):
    """Ternäre Aktivierung: -1, 0, oder +1"""
    return 1 if x > 0 else (-1 if x < 0 else 0)

def state_to_hash(state: List[int]) -> str:
    """Erzeuge kurzen Hash eines Zustands"""
    state_bytes = bytes([s + 1 for s in state])
    return hashlib.sha256(state_bytes).hexdigest()[:16]

def state_to_signature(state: List[int]) -> tuple:
    """Erzeuge hashbare Signatur eines Zustands"""
    return tuple(state)

# =============================================================================
# ANNA MATRIX LOADER
# =============================================================================

class AnnaMatrix:
    def __init__(self, path: str):
        with open(path) as f:
            data = json.load(f)

        self.raw_matrix = []
        for row in data['matrix']:
            row_vals = []
            for v in row:
                if isinstance(v, str):
                    try:
                        row_vals.append(int(v, 16) if len(v) == 8 else int(v))
                    except:
                        row_vals.append(0)
                else:
                    row_vals.append(int(v))
            self.raw_matrix.append(row_vals)

        self.rows = len(self.raw_matrix)
        self.cols = len(self.raw_matrix[0])

        # Ternäre Konvertierung
        self.ternary_matrix = [
            [ternary_clamp(v) for v in row]
            for row in self.raw_matrix
        ]

        print(f"✓ Matrix geladen: {self.rows}×{self.cols}")

# =============================================================================
# OSCILLATION-AWARE NETWORK
# =============================================================================

class OscillationAwareNetwork:
    """
    Neuronales Netzwerk mit Oszillations-Tracking
    """

    def __init__(self, weights: List[List[int]], name: str = "AnnaNet"):
        self.name = name
        self.weights = weights
        self.num_neurons = len(weights)
        self.state = [0] * self.num_neurons
        self.history = []  # Zustandshistorie

        print(f"✓ Netzwerk '{name}' erstellt: {self.num_neurons} Neuronen")

    def process_tick(self) -> List[int]:
        """Ein Tick der Verarbeitung"""
        new_state = []

        for i in range(self.num_neurons):
            score = 0
            for j in range(self.num_neurons):
                if j < len(self.weights) and i < len(self.weights[j]):
                    weight = self.weights[j][i]
                    if weight != 0:
                        score += self.state[j] * weight

            new_value = (1 if score > 0 else 0) - (1 if score < 0 else 0)
            new_state.append(new_value)

        return new_state

    def find_cycle(self, max_ticks: int = 2000) -> Dict:
        """
        Führe Simulation aus und finde Oszillationszyklen

        Returns:
            cycle_length: Länge des gefundenen Zyklus
            cycle_start: Tick wo Zyklus beginnt
            states: Alle Zustände im Zyklus
        """
        seen_states = {}  # state_signature -> tick_number
        self.history = [tuple(self.state)]

        for tick in range(max_ticks):
            new_state = self.process_tick()
            sig = tuple(new_state)

            if sig in seen_states:
                # Zyklus gefunden!
                cycle_start = seen_states[sig]
                cycle_length = tick + 1 - cycle_start

                return {
                    "found": True,
                    "cycle_length": cycle_length,
                    "cycle_start": cycle_start,
                    "total_ticks": tick + 1,
                    "unique_states": len(seen_states),
                    "cycle_states": [self.history[i] for i in range(cycle_start, tick + 1)]
                }

            seen_states[sig] = tick + 1
            self.history.append(sig)
            self.state = new_state

        # Kein Zyklus gefunden
        return {
            "found": False,
            "cycle_length": None,
            "cycle_start": None,
            "total_ticks": max_ticks,
            "unique_states": len(seen_states)
        }

    def run_with_tracking(self, initial_state: List[int], max_ticks: int = 1000) -> Dict:
        """Führe Simulation mit vollständigem Tracking aus"""
        self.state = [ternary_clamp(s) for s in initial_state[:self.num_neurons]]
        while len(self.state) < self.num_neurons:
            self.state.append(0)

        return self.find_cycle(max_ticks)

# =============================================================================
# INPUT GENERATORS
# =============================================================================

def bytes_to_trits(data: bytes, size: int) -> List[int]:
    """Konvertiere Bytes zu ternären Werten"""
    trits = []
    for byte in data:
        for bit in range(8):
            trit = 1 if (byte >> bit) & 1 else -1
            trits.append(trit)
            if len(trits) >= size:
                return trits

    while len(trits) < size:
        trits.append(0)

    return trits[:size]

# Bitcoin-relevante Inputs
INPUTS = {
    "zeros": [0] * 128,
    "ones": [1] * 128,
    "minus_ones": [-1] * 128,
    "alternating": [1 if i % 2 == 0 else -1 for i in range(128)],

    # Bitcoin Genesis Block Hash
    "bitcoin_genesis": bytes_to_trits(
        bytes.fromhex("000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"),
        128
    ),

    # 1CFB Adresse Hash160
    "1cfb_hash160": bytes_to_trits(
        bytes.fromhex("7b582a5c61c91befcfe2778b6a7c72fceb937c8c"),
        128
    ),

    # Block 264 (CFB Genesis-Marker)
    "block_264": bytes_to_trits(
        bytes.fromhex("00000000839a8e6886ab5951d76f411475428afc90947ee320161bbf18eb6048"),
        128
    ),

    # 21e8 Block (mysteriöser Hash)
    "block_21e8": bytes_to_trits(
        bytes.fromhex("0000000000000000002ce21e8c01d1eda9d1d5b1edf63b3d5f9c8d8e8f0a1b2c"),
        128
    ),

    # Patoshi Nonce Pattern
    "patoshi_nonce": bytes_to_trits(
        bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000")[:16] +
        bytes([0x08] * 16),  # Patoshi LSB pattern
        128
    ),
}

# =============================================================================
# ATTRACTOR ANALYSIS
# =============================================================================

def analyze_attractors(results: List[Dict]) -> Dict:
    """Analysiere die gefundenen Attraktoren"""

    # Gruppiere nach finalen Zuständen
    final_states = {}

    for r in results:
        if r['result']['found']:
            # Nutze den ersten Zustand im Zyklus als Repräsentant
            cycle_state = r['result']['cycle_states'][0] if r['result']['cycle_states'] else None
            if cycle_state:
                state_hash = state_to_hash(list(cycle_state))

                if state_hash not in final_states:
                    final_states[state_hash] = {
                        "inputs": [],
                        "cycle_length": r['result']['cycle_length'],
                        "distribution": {
                            "positive": sum(1 for s in cycle_state if s == 1),
                            "negative": sum(1 for s in cycle_state if s == -1),
                            "zero": sum(1 for s in cycle_state if s == 0)
                        }
                    }

                final_states[state_hash]["inputs"].append(r['name'])

    return final_states

# =============================================================================
# ANOMALY INFLUENCE TEST
# =============================================================================

def test_anomaly_influence(anna: AnnaMatrix) -> Dict:
    """
    Teste den Einfluss der Anomalien auf das Netzwerk
    """
    print("\n=== ANOMALIE-EINFLUSS TEST ===")

    # Finde Anomalie-Positionen
    anomalies = []
    for r in range(anna.rows):
        for c in range(anna.cols):
            mr = anna.rows - 1 - r
            mc = anna.cols - 1 - c

            if r < mr or (r == mr and c < mc):
                val_sum = anna.raw_matrix[r][c] + anna.raw_matrix[mr][mc]
                if val_sum != -1:
                    anomalies.append({
                        "pos": (r, c),
                        "val": anna.raw_matrix[r][c],
                        "mirror": (mr, mc),
                        "mirror_val": anna.raw_matrix[mr][mc],
                        "sum": val_sum
                    })

    print(f"  Anomalien gefunden: {len(anomalies)}")

    # Erzeuge "reparierte" Matrix (alle Anomalien auf Symmetrie setzen)
    repaired_matrix = [row[:] for row in anna.ternary_matrix]

    for a in anomalies:
        r, c = a["pos"]
        mr, mc = a["mirror"]
        # Setze beide auf die "erwarteten" ternären Werte für perfekte Symmetrie
        repaired_matrix[r][c] = ternary_clamp(a["val"])
        repaired_matrix[mr][mc] = -repaired_matrix[r][c]  # Erzwinge Symmetrie

    # Vergleiche Netzwerk-Verhalten
    original_network = OscillationAwareNetwork(anna.ternary_matrix, "Original")
    repaired_network = OscillationAwareNetwork(repaired_matrix, "Repaired")

    comparison = []

    for name, input_data in INPUTS.items():
        orig_result = original_network.run_with_tracking(input_data.copy(), 500)
        rep_result = repaired_network.run_with_tracking(input_data.copy(), 500)

        comparison.append({
            "input": name,
            "original": {
                "cycle_length": orig_result.get("cycle_length"),
                "unique_states": orig_result.get("unique_states")
            },
            "repaired": {
                "cycle_length": rep_result.get("cycle_length"),
                "unique_states": rep_result.get("unique_states")
            },
            "differs": orig_result.get("cycle_length") != rep_result.get("cycle_length")
        })

        status = "⚠ UNTERSCHIED" if comparison[-1]["differs"] else "="
        print(f"  {name}: Original={orig_result.get('cycle_length')} vs Repaired={rep_result.get('cycle_length')} {status}")

    return {
        "anomaly_count": len(anomalies),
        "anomaly_positions": [(a["pos"], a["mirror"]) for a in anomalies[:10]],
        "comparison": comparison,
        "anomalies_affect_behavior": any(c["differs"] for c in comparison)
    }

# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    print("\n" + "=" * 80)
    print("PHASE 1: MATRIX & NETZWERK LADEN")
    print("=" * 80)

    anna = AnnaMatrix("apps/web/public/data/anna-matrix.json")
    network = OscillationAwareNetwork(anna.ternary_matrix, "AnnaOscillationNet")

    print("\n" + "=" * 80)
    print("PHASE 2: OSZILLATIONS-ANALYSE FÜR ALLE INPUTS")
    print("=" * 80)

    results = []

    for name, input_data in INPUTS.items():
        result = network.run_with_tracking(input_data.copy(), 2000)

        results.append({
            "name": name,
            "result": result
        })

        if result["found"]:
            print(f"  ✓ {name}: Zyklus-Länge={result['cycle_length']}, Start={result['cycle_start']}, Unique={result['unique_states']}")
        else:
            print(f"  ⚠ {name}: Kein Zyklus in 2000 Ticks, Unique={result['unique_states']}")

    print("\n" + "=" * 80)
    print("PHASE 3: ATTRAKTOR-ANALYSE")
    print("=" * 80)

    attractors = analyze_attractors(results)

    print(f"\n  Gefundene Attraktor-Klassen: {len(attractors)}")

    for hash_val, data in attractors.items():
        print(f"\n  Attraktor {hash_val}:")
        print(f"    Zyklus-Länge: {data['cycle_length']}")
        print(f"    Verteilung: +{data['distribution']['positive']}, -{data['distribution']['negative']}, 0={data['distribution']['zero']}")
        print(f"    Inputs: {', '.join(data['inputs'])}")

    print("\n" + "=" * 80)
    print("PHASE 4: ANOMALIE-EINFLUSS")
    print("=" * 80)

    anomaly_result = test_anomaly_influence(anna)

    print("\n" + "=" * 80)
    print("PHASE 5: ERGEBNISSE SPEICHERN")
    print("=" * 80)

    output = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "network_size": network.num_neurons,
            "inputs_tested": len(INPUTS)
        },
        "oscillation_results": [
            {
                "name": r["name"],
                "cycle_found": r["result"]["found"],
                "cycle_length": r["result"].get("cycle_length"),
                "cycle_start": r["result"].get("cycle_start"),
                "unique_states": r["result"].get("unique_states")
            }
            for r in results
        ],
        "attractor_classes": {
            k: {
                "inputs": v["inputs"],
                "cycle_length": v["cycle_length"],
                "distribution": v["distribution"]
            }
            for k, v in attractors.items()
        },
        "anomaly_analysis": {
            "count": anomaly_result["anomaly_count"],
            "affects_behavior": anomaly_result["anomalies_affect_behavior"],
            "comparison_summary": [
                {"input": c["input"], "differs": c["differs"]}
                for c in anomaly_result["comparison"]
            ]
        }
    }

    output_path = Path("apps/web/scripts/ANNA_OSCILLATION_ANALYSIS.json")
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Ergebnisse gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)

    cycles_found = sum(1 for r in results if r["result"]["found"])

    print(f"""
OSZILLATIONEN:
  Inputs getestet: {len(INPUTS)}
  Zyklen gefunden: {cycles_found}/{len(INPUTS)}
  Attraktor-Klassen: {len(attractors)}

ANOMALIEN:
  Anzahl: {anomaly_result['anomaly_count']}
  Beeinflussen Verhalten: {'JA' if anomaly_result['anomalies_affect_behavior'] else 'NEIN'}

BITCOIN-RELEVANTE INPUTS:
  Genesis: {'Zyklus' if any(r['result']['found'] for r in results if r['name'] == 'bitcoin_genesis') else 'Oszilliert'}
  1CFB:    {'Zyklus' if any(r['result']['found'] for r in results if r['name'] == '1cfb_hash160') else 'Oszilliert'}
  Block264: {'Zyklus' if any(r['result']['found'] for r in results if r['name'] == 'block_264') else 'Oszilliert'}
""")

    return output

if __name__ == "__main__":
    results = main()
