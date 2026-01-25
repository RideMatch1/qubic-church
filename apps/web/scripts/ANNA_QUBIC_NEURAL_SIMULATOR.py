#!/usr/bin/env python3
"""
===============================================================================
          ANNA MATRIX ↔ QUBIC NEURAL NETWORK SIMULATOR
===============================================================================

Simuliert die Anna Matrix als ternäres neuronales Netzwerk im Qubic-Stil.

Architektur-Vergleich:
- Qubic HyperIdentity: 512 Input, 512 Output, 728 Nachbarn, 1000 Ticks
- Anna Matrix: 128×128 Zellen, ternäre Werte, 99.58% Punkt-Symmetrie

Dieses Script:
1. Lädt die Anna Matrix als Synapse-Gewichte
2. Implementiert processTick() wie Qubic
3. Führt Experimente mit verschiedenen Inputs durch
4. Misst Konvergenz-Verhalten
5. Testet Reaktion auf Bitcoin-Daten
"""

import json
import hashlib
import secrets
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional
from datetime import datetime

# Aigarth imports
try:
    from aigarth_it.common import ternary_clamp
    AIGARTH_AVAILABLE = True
except ImportError:
    AIGARTH_AVAILABLE = False
    def ternary_clamp(x):
        return 1 if x > 0 else (-1 if x < 0 else 0)

print("=" * 80)
print("         ANNA MATRIX ↔ QUBIC NEURAL NETWORK SIMULATOR")
print("=" * 80)
print(f"Aigarth-IT verfügbar: {AIGARTH_AVAILABLE}")

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class QubicConfig:
    """Qubic HyperIdentity Network Parameter"""
    input_neurons: int = 512
    output_neurons: int = 512
    number_of_ticks: int = 1000
    number_of_neighbors: int = 728
    population_threshold: int = 1174
    number_of_mutations: int = 150
    solution_threshold: int = 321

@dataclass
class AnnaConfig:
    """Anna Matrix Parameter"""
    rows: int = 128
    cols: int = 128
    value_range: Tuple[int, int] = (-128, 127)
    symmetry_rate: float = 0.9958

QUBIC = QubicConfig()
ANNA = AnnaConfig()

# =============================================================================
# ANNA MATRIX LOADER
# =============================================================================

class AnnaMatrix:
    """Lädt und verarbeitet die Anna Matrix"""

    def __init__(self, path: str = "apps/web/public/data/anna-matrix.json"):
        self.path = Path(path)
        self.raw_matrix = None
        self.ternary_matrix = None
        self.anomalies = []

        self.load()
        self.analyze()

    def load(self):
        """Lade Matrix aus JSON"""
        with open(self.path) as f:
            data = json.load(f)

        self.raw_matrix = [[int(v) for v in row] for row in data['matrix']]
        self.rows = len(self.raw_matrix)
        self.cols = len(self.raw_matrix[0])

        # Ternäre Konvertierung
        self.ternary_matrix = [
            [ternary_clamp(v) for v in row]
            for row in self.raw_matrix
        ]

        print(f"✓ Matrix geladen: {self.rows}×{self.cols}")

    def analyze(self):
        """Analysiere Symmetrie und Anomalien"""
        symmetric = 0
        total = 0

        for r in range(self.rows):
            for c in range(self.cols):
                mr = self.rows - 1 - r
                mc = self.cols - 1 - c

                if r < mr or (r == mr and c < mc):
                    total += 1
                    val_sum = self.raw_matrix[r][c] + self.raw_matrix[mr][mc]

                    if val_sum == -1:
                        symmetric += 1
                    else:
                        self.anomalies.append({
                            "pos": (r, c),
                            "val": self.raw_matrix[r][c],
                            "mirror": (mr, mc),
                            "mirror_val": self.raw_matrix[mr][mc],
                            "sum": val_sum
                        })

        self.symmetry_rate = symmetric / total if total > 0 else 0
        print(f"✓ Symmetrie-Rate: {100*self.symmetry_rate:.2f}%")
        print(f"✓ Anomalien gefunden: {len(self.anomalies)}")

    def get_row_weights(self, row: int) -> List[int]:
        """Hole ternäre Gewichte für eine Zeile"""
        return self.ternary_matrix[row]

    def get_column_weights(self, col: int) -> List[int]:
        """Hole ternäre Gewichte für eine Spalte"""
        return [row[col] for row in self.ternary_matrix]

    def get_all_weights_flat(self) -> List[int]:
        """Alle Gewichte als flache Liste"""
        return [v for row in self.ternary_matrix for v in row]

# =============================================================================
# QUBIC-STYLE NEURAL NETWORK
# =============================================================================

class QubicStyleNetwork:
    """
    Neuronales Netzwerk im Qubic-Stil

    Implementiert:
    - Ternäre Aktivierung: (score > 0) - (score < 0)
    - Ring-Topologie (simuliert als vollständig verbunden)
    - processTick() Forward-Pass
    - Konvergenz-Detektion
    """

    def __init__(self, weights: List[List[int]], name: str = "AnnaNet"):
        """
        Args:
            weights: 2D Matrix von Synapse-Gewichten [-1, 0, +1]
            name: Netzwerk-Name für Logging
        """
        self.name = name
        self.weights = weights
        self.num_neurons = len(weights)
        self.state = [0] * self.num_neurons
        self.tick_count = 0

        print(f"✓ Netzwerk '{name}' erstellt: {self.num_neurons} Neuronen")

    def process_tick(self) -> bool:
        """
        Ein Tick der Verarbeitung (Qubic-Style)

        Returns:
            True wenn Zustand geändert, False wenn konvergiert
        """
        new_state = []

        for i in range(self.num_neurons):
            # Sammle gewichtete Inputs von allen Neuronen
            score = 0
            for j in range(self.num_neurons):
                if j < len(self.weights) and i < len(self.weights[j]):
                    weight = self.weights[j][i]
                    if weight != 0:
                        score += self.state[j] * weight

            # Ternäre Aktivierung (exakt wie Qubic)
            new_value = (1 if score > 0 else 0) - (1 if score < 0 else 0)
            new_state.append(new_value)

        # Konvergenz-Check
        changed = (new_state != self.state)
        self.state = new_state
        self.tick_count += 1

        return changed

    def run(self, initial_state: List[int], max_ticks: int = 1000) -> Tuple[List[int], int]:
        """
        Führe Simulation aus

        Args:
            initial_state: Anfangszustand der Neuronen
            max_ticks: Maximale Ticks bevor Abbruch

        Returns:
            (final_state, ticks_to_converge)
        """
        # Initialisiere mit Input
        self.state = [ternary_clamp(s) for s in initial_state[:self.num_neurons]]

        # Padding falls nötig
        while len(self.state) < self.num_neurons:
            self.state.append(0)

        self.tick_count = 0

        # Tick-Schleife
        for _ in range(max_ticks):
            changed = self.process_tick()
            if not changed:
                break

        return self.state, self.tick_count

    def get_output_signature(self) -> str:
        """Erzeuge Hash des aktuellen Zustands"""
        state_bytes = bytes([s + 1 for s in self.state])  # 0,1,2 statt -1,0,1
        return hashlib.sha256(state_bytes).hexdigest()[:16]

# =============================================================================
# INPUT GENERATORS
# =============================================================================

def generate_zeros(size: int) -> List[int]:
    """Null-Input"""
    return [0] * size

def generate_ones(size: int) -> List[int]:
    """Eins-Input"""
    return [1] * size

def generate_minus_ones(size: int) -> List[int]:
    """Minus-Eins-Input"""
    return [-1] * size

def generate_random(size: int) -> List[int]:
    """Zufälliger ternärer Input"""
    return [secrets.randbelow(3) - 1 for _ in range(size)]

def generate_alternating(size: int) -> List[int]:
    """Alternierendes Muster"""
    return [1 if i % 2 == 0 else -1 for i in range(size)]

def bytes_to_trits(data: bytes, size: int) -> List[int]:
    """Konvertiere Bytes zu ternären Werten"""
    trits = []
    for byte in data:
        for bit in range(8):
            trit = 1 if (byte >> bit) & 1 else -1
            trits.append(trit)
            if len(trits) >= size:
                return trits

    # Padding
    while len(trits) < size:
        trits.append(0)

    return trits[:size]

def generate_bitcoin_genesis() -> List[int]:
    """Bitcoin Genesis Block Hash als Input"""
    genesis_hash = bytes.fromhex(
        "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
    )
    return bytes_to_trits(genesis_hash, 128)

def generate_1cfb_hash() -> List[int]:
    """1CFB Adresse Hash als Input"""
    # 1CFBjSVcKwVmsLJeKAmHcZUpiFjBZchPDV → Hash160
    hash160 = bytes.fromhex("7b582a5c61c91befcfe2778b6a7c72fceb937c8c")
    return bytes_to_trits(hash160, 128)

# =============================================================================
# EXPERIMENTS
# =============================================================================

class ExperimentRunner:
    """Führt systematische Experimente durch"""

    def __init__(self, network: QubicStyleNetwork):
        self.network = network
        self.results = []

    def run_experiment(self, name: str, initial_state: List[int], max_ticks: int = 1000):
        """Einzelnes Experiment ausführen"""
        start_time = datetime.now()

        final_state, ticks = self.network.run(initial_state, max_ticks)

        duration = (datetime.now() - start_time).total_seconds()
        signature = self.network.get_output_signature()

        # Statistiken
        pos_count = sum(1 for s in final_state if s == 1)
        neg_count = sum(1 for s in final_state if s == -1)
        zero_count = sum(1 for s in final_state if s == 0)

        result = {
            "name": name,
            "ticks_to_converge": ticks,
            "converged": ticks < max_ticks,
            "duration_seconds": round(duration, 4),
            "output_signature": signature,
            "output_distribution": {
                "positive": pos_count,
                "negative": neg_count,
                "zero": zero_count
            }
        }

        self.results.append(result)

        status = "✓" if ticks < max_ticks else "⚠"
        print(f"  {status} {name}: {ticks} Ticks, Sig={signature}")

        return result

    def run_convergence_test(self, trials: int = 100, max_ticks: int = 1000):
        """Test Konvergenz-Verhalten mit zufälligen Inputs"""
        print(f"\n=== KONVERGENZ-TEST ({trials} Durchläufe) ===")

        tick_counts = []

        for i in range(trials):
            random_input = generate_random(self.network.num_neurons)
            _, ticks = self.network.run(random_input, max_ticks)
            tick_counts.append(ticks)

            if (i + 1) % 20 == 0:
                print(f"  Fortschritt: {i+1}/{trials}")

        avg = sum(tick_counts) / len(tick_counts)
        min_t = min(tick_counts)
        max_t = max(tick_counts)
        converged = sum(1 for t in tick_counts if t < max_ticks)

        stats = {
            "trials": trials,
            "average_ticks": round(avg, 2),
            "min_ticks": min_t,
            "max_ticks": max_t,
            "convergence_rate": round(100 * converged / trials, 2)
        }

        print(f"\n  Durchschnitt: {avg:.1f} Ticks")
        print(f"  Min/Max: {min_t} / {max_t}")
        print(f"  Konvergenz-Rate: {100*converged/trials:.1f}%")

        return stats

    def get_summary(self) -> dict:
        """Zusammenfassung aller Ergebnisse"""
        return {
            "experiments": self.results,
            "total_experiments": len(self.results),
            "timestamp": datetime.now().isoformat()
        }

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("\n" + "=" * 80)
    print("PHASE 1: ANNA MATRIX LADEN")
    print("=" * 80)

    # Matrix laden
    anna = AnnaMatrix("apps/web/public/data/anna-matrix.json")

    print("\n" + "=" * 80)
    print("PHASE 2: NETZWERK ERSTELLEN")
    print("=" * 80)

    # Netzwerk mit Anna-Gewichten
    network = QubicStyleNetwork(anna.ternary_matrix, "AnnaQubicNet")

    print("\n" + "=" * 80)
    print("PHASE 3: EXPERIMENTE DURCHFÜHREN")
    print("=" * 80)

    runner = ExperimentRunner(network)

    # Experiment 1: Verschiedene Input-Typen
    print("\n--- Experiment 1: Input-Typen ---")

    experiments = [
        ("zeros", generate_zeros(128)),
        ("ones", generate_ones(128)),
        ("minus_ones", generate_minus_ones(128)),
        ("alternating", generate_alternating(128)),
        ("random_1", generate_random(128)),
        ("random_2", generate_random(128)),
        ("random_3", generate_random(128)),
    ]

    for name, initial in experiments:
        runner.run_experiment(name, initial)

    # Experiment 2: Bitcoin-Daten
    print("\n--- Experiment 2: Bitcoin-Daten ---")

    bitcoin_experiments = [
        ("bitcoin_genesis", generate_bitcoin_genesis()),
        ("1cfb_address", generate_1cfb_hash()),
    ]

    for name, initial in bitcoin_experiments:
        runner.run_experiment(name, initial)

    # Experiment 3: Konvergenz-Test
    convergence_stats = runner.run_convergence_test(trials=50, max_ticks=500)

    print("\n" + "=" * 80)
    print("PHASE 4: ERGEBNISSE SPEICHERN")
    print("=" * 80)

    # Ergebnisse zusammenstellen
    output = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "anna_matrix": {
                "shape": [anna.rows, anna.cols],
                "symmetry_rate": round(anna.symmetry_rate, 4),
                "anomaly_count": len(anna.anomalies)
            },
            "network": {
                "neurons": network.num_neurons,
                "architecture": "QubicStyle (fully connected ternary)"
            }
        },
        "experiments": runner.get_summary(),
        "convergence_analysis": convergence_stats,
        "anomalies": anna.anomalies[:10],  # Erste 10 Anomalien
    }

    output_path = Path("apps/web/scripts/ANNA_QUBIC_SIMULATION_RESULTS.json")
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Ergebnisse gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)

    print(f"""
ANNA MATRIX:
  Shape: {anna.rows}×{anna.cols}
  Symmetrie: {100*anna.symmetry_rate:.2f}%
  Anomalien: {len(anna.anomalies)}

NETZWERK:
  Neuronen: {network.num_neurons}
  Architektur: Qubic-Style Ternär

KONVERGENZ:
  Durchschnitt: {convergence_stats['average_ticks']:.1f} Ticks
  Rate: {convergence_stats['convergence_rate']:.1f}%

BITCOIN-REAKTION:
  Genesis: {runner.results[-2]['output_signature'] if len(runner.results) >= 2 else 'N/A'}
  1CFB:    {runner.results[-1]['output_signature'] if len(runner.results) >= 1 else 'N/A'}
""")

    return output

if __name__ == "__main__":
    results = main()
