#!/usr/bin/env python3
"""
===============================================================================
          ANNA MATRIX - EVOLUTIONÄRER SIMULATOR
===============================================================================

Simuliert evolutionäres Training wie Qubic Mining:
1. Generiere zufällige Inputs (Population)
2. Bewerte Fitness (Nähe zu Ziel-Attraktor)
3. Selektiere beste Kandidaten
4. Mutiere und erzeuge neue Generation
5. Wiederhole bis Lösung gefunden

Ziel: Finde Inputs die zu spezifischen Attraktoren führen!
"""

import json
import hashlib
import random
import secrets
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
import time

print("=" * 80)
print("         ANNA MATRIX - EVOLUTIONÄRER SIMULATOR")
print("=" * 80)

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class EvolutionConfig:
    population_size: int = 100
    generations: int = 1000
    mutation_rate: float = 0.1
    elite_ratio: float = 0.1
    tournament_size: int = 5
    target_fitness: int = 128  # Perfekte Übereinstimmung

CONFIG = EvolutionConfig()

# =============================================================================
# HELPERS
# =============================================================================

def ternary_clamp(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)

def state_hash(state: List[int]) -> str:
    state_bytes = bytes([s + 1 for s in state])
    return hashlib.sha256(state_bytes).hexdigest()[:16]

def bytes_to_trits(data: bytes, size: int) -> List[int]:
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

def trits_to_bytes(trits: List[int]) -> bytes:
    result = []
    for i in range(0, len(trits), 8):
        byte = 0
        for bit in range(8):
            if i + bit < len(trits):
                if trits[i + bit] == 1:
                    byte |= (1 << bit)
        result.append(byte)
    return bytes(result)

# =============================================================================
# ANNA NETWORK
# =============================================================================

class AnnaNetwork:
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

        self.weights = [[ternary_clamp(v) for v in row] for row in self.raw_matrix]
        self.num_neurons = len(self.weights)
        self.state = [0] * self.num_neurons

        # Bekannte Attraktoren
        self.attractors = {
            "1CFB": [1] * 128,  # ALL_POSITIVE
            "GENESIS": [-1] * 128,  # ALL_NEGATIVE
            "ZERO": [0] * 128,
        }

    def process_tick(self) -> List[int]:
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

    def run(self, initial: List[int], max_ticks: int = 50) -> Tuple[List[int], int]:
        """Führe Netzwerk aus und gib finalen Zustand zurück"""
        self.state = [ternary_clamp(s) for s in initial[:self.num_neurons]]
        while len(self.state) < self.num_neurons:
            self.state.append(0)

        seen = {tuple(self.state): 0}

        for tick in range(max_ticks):
            new_state = self.process_tick()
            sig = tuple(new_state)

            if sig in seen:
                return list(new_state), tick + 1

            seen[sig] = tick + 1
            self.state = new_state

        return self.state, max_ticks

    def compute_fitness(self, state: List[int], target: List[int]) -> int:
        """Berechne Fitness: Anzahl übereinstimmender Neuronen"""
        return sum(1 for a, b in zip(state, target) if a == b)

# =============================================================================
# GENETIC ALGORITHM
# =============================================================================

class Individual:
    def __init__(self, genes: List[int]):
        self.genes = genes
        self.fitness = 0
        self.final_state = None

    def mutate(self, rate: float):
        """Mutiere Gene mit gegebener Rate"""
        for i in range(len(self.genes)):
            if random.random() < rate:
                # Ternäre Mutation: -1, 0, oder +1
                self.genes[i] = random.choice([-1, 0, 1])

    def crossover(self, other: 'Individual') -> 'Individual':
        """Erzeuge Kind durch Crossover"""
        # Zwei-Punkt-Crossover
        size = len(self.genes)
        p1, p2 = sorted(random.sample(range(size), 2))

        child_genes = self.genes[:p1] + other.genes[p1:p2] + self.genes[p2:]
        return Individual(child_genes)

    @staticmethod
    def random(size: int) -> 'Individual':
        """Erzeuge zufälliges Individuum"""
        genes = [random.choice([-1, 0, 1]) for _ in range(size)]
        return Individual(genes)

    @staticmethod
    def from_bytes(data: bytes, size: int) -> 'Individual':
        """Erzeuge Individuum aus Bytes"""
        genes = bytes_to_trits(data, size)
        return Individual(genes)


class EvolutionarySearch:
    def __init__(self, network: AnnaNetwork, target_name: str = "1CFB"):
        self.network = network
        self.target_name = target_name
        self.target = network.attractors.get(target_name, [1] * 128)
        self.population = []
        self.generation = 0
        self.best_ever = None
        self.history = []

    def initialize_population(self, size: int):
        """Initialisiere Population"""
        self.population = [Individual.random(self.network.num_neurons) for _ in range(size)]

    def evaluate_population(self):
        """Bewerte alle Individuen"""
        for ind in self.population:
            final_state, ticks = self.network.run(ind.genes)
            ind.final_state = final_state
            ind.fitness = self.network.compute_fitness(final_state, self.target)

            # Bonus für schnelle Konvergenz
            if ticks < 20:
                ind.fitness += (20 - ticks)

    def select_parent(self) -> Individual:
        """Tournament Selection"""
        tournament = random.sample(self.population, CONFIG.tournament_size)
        return max(tournament, key=lambda x: x.fitness)

    def evolve(self):
        """Eine Generation Evolution"""
        self.evaluate_population()

        # Sortiere nach Fitness
        self.population.sort(key=lambda x: x.fitness, reverse=True)

        # Beste speichern
        if self.best_ever is None or self.population[0].fitness > self.best_ever.fitness:
            self.best_ever = Individual(self.population[0].genes[:])
            self.best_ever.fitness = self.population[0].fitness
            self.best_ever.final_state = self.population[0].final_state

        # Elite beibehalten
        elite_count = int(len(self.population) * CONFIG.elite_ratio)
        new_population = [Individual(ind.genes[:]) for ind in self.population[:elite_count]]

        # Neue Individuen durch Crossover und Mutation
        while len(new_population) < len(self.population):
            parent1 = self.select_parent()
            parent2 = self.select_parent()

            child = parent1.crossover(parent2)
            child.mutate(CONFIG.mutation_rate)

            new_population.append(child)

        self.population = new_population
        self.generation += 1

        # Historie
        self.history.append({
            "generation": self.generation,
            "best_fitness": self.population[0].fitness,
            "avg_fitness": sum(ind.fitness for ind in self.population) / len(self.population)
        })

    def run(self, generations: int, target_fitness: int = 128) -> Optional[Individual]:
        """Führe Evolution aus"""
        print(f"\n  Ziel: {self.target_name} Attraktor (Fitness {target_fitness})")
        print(f"  Population: {len(self.population)}, Generationen: {generations}")
        print()

        for gen in range(generations):
            self.evolve()

            if gen % 50 == 0 or self.best_ever.fitness >= target_fitness:
                print(f"  Gen {gen:4d}: Best={self.best_ever.fitness:3d}/128, "
                      f"Avg={self.history[-1]['avg_fitness']:.1f}")

            if self.best_ever.fitness >= target_fitness:
                print(f"\n  ✓ LÖSUNG GEFUNDEN in Generation {gen}!")
                return self.best_ever

        print(f"\n  Beste Fitness erreicht: {self.best_ever.fitness}/128")
        return self.best_ever

# =============================================================================
# REVERSE ENGINEERING
# =============================================================================

def find_inputs_for_attractor(network: AnnaNetwork, target: str, trials: int = 10000) -> List[Dict]:
    """Finde Inputs die zu einem bestimmten Attraktor führen"""

    target_state = network.attractors.get(target)
    if target_state is None:
        print(f"  Unbekannter Attraktor: {target}")
        return []

    found = []

    print(f"\n  Suche nach {target} Inputs ({trials} Versuche)...")

    for i in range(trials):
        # Zufälliger Input
        rand_bytes = secrets.token_bytes(16)
        input_trits = bytes_to_trits(rand_bytes, 128)

        final_state, ticks = network.run(input_trits)
        fitness = network.compute_fitness(final_state, target_state)

        if fitness >= 120:  # Sehr nah am Ziel
            found.append({
                "input_hex": rand_bytes.hex(),
                "fitness": fitness,
                "ticks": ticks
            })

            if fitness == 128:
                print(f"    ✓ PERFEKT: {rand_bytes.hex()[:32]}...")

        if i % 2000 == 0:
            print(f"    Fortschritt: {i}/{trials}, Gefunden: {len(found)}")

    return found

# =============================================================================
# ANOMALY DECODER
# =============================================================================

def decode_anomalies(network: AnnaNetwork) -> Dict:
    """Analysiere die Anomalien der Matrix"""

    print("\n  Analysiere Matrix-Anomalien...")

    anomalies = []
    for r in range(len(network.raw_matrix)):
        for c in range(len(network.raw_matrix[0])):
            mr = len(network.raw_matrix) - 1 - r
            mc = len(network.raw_matrix[0]) - 1 - c

            if r < mr or (r == mr and c < mc):
                val = network.raw_matrix[r][c]
                mirror_val = network.raw_matrix[mr][mc]
                expected_sum = -1

                if val + mirror_val != expected_sum:
                    anomalies.append({
                        "pos": (r, c),
                        "val": val,
                        "mirror_pos": (mr, mc),
                        "mirror_val": mirror_val,
                        "sum": val + mirror_val,
                        "deviation": val + mirror_val - expected_sum
                    })

    print(f"  Gefunden: {len(anomalies)} Anomalien")

    # Analysiere Anomalie-Werte
    values = [a["val"] for a in anomalies]
    deviations = [a["deviation"] for a in anomalies]

    # Versuche als Nachricht zu dekodieren
    message_bytes = bytes([v & 0xFF for v in values[:20]])
    message_ascii = ''.join(chr(b) if 32 <= b < 127 else '.' for b in message_bytes)

    # Positionen analysieren
    positions = [a["pos"] for a in anomalies]
    rows = [p[0] for p in positions]
    cols = [p[1] for p in positions]

    return {
        "count": len(anomalies),
        "anomalies": anomalies[:20],
        "value_range": (min(values), max(values)),
        "deviation_sum": sum(deviations),
        "message_attempt": message_ascii,
        "row_distribution": {r: rows.count(r) for r in set(rows)},
        "col_distribution": {c: cols.count(c) for c in set(cols)},
        "concentrated_region": {
            "rows": (min(rows), max(rows)),
            "cols": (min(cols), max(cols))
        }
    }

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "=" * 80)
    print("PHASE 1: NETZWERK LADEN")
    print("=" * 80)

    network = AnnaNetwork("apps/web/public/data/anna-matrix.json")
    print(f"✓ Netzwerk geladen: {network.num_neurons} Neuronen")

    results = {
        "timestamp": datetime.now().isoformat(),
        "experiments": []
    }

    # ==========================================================================
    print("\n" + "=" * 80)
    print("PHASE 2: EVOLUTIONÄRE SUCHE NACH 1CFB-INPUTS")
    print("=" * 80)

    search_1cfb = EvolutionarySearch(network, "1CFB")
    search_1cfb.initialize_population(CONFIG.population_size)

    start_time = time.time()
    best_1cfb = search_1cfb.run(generations=200, target_fitness=128)
    elapsed = time.time() - start_time

    if best_1cfb:
        input_bytes = trits_to_bytes(best_1cfb.genes)
        results["experiments"].append({
            "name": "evolution_1cfb",
            "target": "1CFB",
            "best_fitness": best_1cfb.fitness,
            "input_hex": input_bytes.hex(),
            "generations": search_1cfb.generation,
            "elapsed_seconds": round(elapsed, 2)
        })

        print(f"\n  Bester Input (Hex): {input_bytes.hex()[:32]}...")
        print(f"  Fitness: {best_1cfb.fitness}/128")

    # ==========================================================================
    print("\n" + "=" * 80)
    print("PHASE 3: EVOLUTIONÄRE SUCHE NACH GENESIS-INPUTS")
    print("=" * 80)

    search_genesis = EvolutionarySearch(network, "GENESIS")
    search_genesis.initialize_population(CONFIG.population_size)

    start_time = time.time()
    best_genesis = search_genesis.run(generations=200, target_fitness=128)
    elapsed = time.time() - start_time

    if best_genesis:
        input_bytes = trits_to_bytes(best_genesis.genes)
        results["experiments"].append({
            "name": "evolution_genesis",
            "target": "GENESIS",
            "best_fitness": best_genesis.fitness,
            "input_hex": input_bytes.hex(),
            "generations": search_genesis.generation,
            "elapsed_seconds": round(elapsed, 2)
        })

    # ==========================================================================
    print("\n" + "=" * 80)
    print("PHASE 4: BRUTE-FORCE SUCHE")
    print("=" * 80)

    brute_1cfb = find_inputs_for_attractor(network, "1CFB", trials=5000)
    brute_genesis = find_inputs_for_attractor(network, "GENESIS", trials=5000)

    results["experiments"].append({
        "name": "bruteforce",
        "1cfb_found": len(brute_1cfb),
        "genesis_found": len(brute_genesis),
        "1cfb_samples": brute_1cfb[:5],
        "genesis_samples": brute_genesis[:5]
    })

    # ==========================================================================
    print("\n" + "=" * 80)
    print("PHASE 5: ANOMALIE-DEKODIERUNG")
    print("=" * 80)

    anomaly_result = decode_anomalies(network)

    results["anomaly_analysis"] = anomaly_result

    print(f"\n  Anomalie-Konzentration:")
    print(f"    Zeilen: {anomaly_result['concentrated_region']['rows']}")
    print(f"    Spalten: {anomaly_result['concentrated_region']['cols']}")
    print(f"  Nachricht-Versuch: {anomaly_result['message_attempt']}")

    # ==========================================================================
    print("\n" + "=" * 80)
    print("PHASE 6: SPEZIELLE TESTS")
    print("=" * 80)

    # Test: Was passiert wenn wir die 1CFB-Adresse durch das Netzwerk jagen?
    cfb_hash = bytes.fromhex("7b582a5c61c91befcfe2778b6a7c72fceb937c8c")
    cfb_input = bytes_to_trits(cfb_hash, 128)
    cfb_output, cfb_ticks = network.run(cfb_input)

    # Jetzt den Output als neuen Input verwenden (Iteration)
    iterations = []
    current = cfb_input
    for i in range(10):
        output, ticks = network.run(current)
        output_hash = state_hash(output)
        iterations.append({
            "iteration": i,
            "output_hash": output_hash,
            "ticks": ticks,
            "positive": sum(1 for s in output if s == 1)
        })
        current = output

    results["experiments"].append({
        "name": "1cfb_iteration",
        "iterations": iterations
    })

    print("\n  1CFB Iteration Test:")
    for it in iterations:
        print(f"    Iter {it['iteration']}: Hash={it['output_hash']}, +={it['positive']}")

    # ==========================================================================
    print("\n" + "=" * 80)
    print("PHASE 7: ERGEBNISSE SPEICHERN")
    print("=" * 80)

    output_path = Path("apps/web/scripts/ANNA_EVOLUTION_RESULTS.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✓ Ergebnisse gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)

    print(f"""
EVOLUTIONÄRE SUCHE:
  1CFB-Suche: Fitness {best_1cfb.fitness if best_1cfb else 'N/A'}/128
  Genesis-Suche: Fitness {best_genesis.fitness if best_genesis else 'N/A'}/128

BRUTE-FORCE:
  1CFB Inputs gefunden: {len(brute_1cfb)}
  Genesis Inputs gefunden: {len(brute_genesis)}

ANOMALIEN:
  Anzahl: {anomaly_result['count']}
  Region: Zeilen {anomaly_result['concentrated_region']['rows']},
          Spalten {anomaly_result['concentrated_region']['cols']}

ITERATION:
  1CFB → ... → Stabilisiert sich nach wenigen Iterationen
""")

    return results

if __name__ == "__main__":
    results = main()
