#!/usr/bin/env python3
"""
===============================================================================
      CFB ADRESS-KLASSIFIKATOR - ANNA MATRIX EXPERIMENT
===============================================================================

HYPOTHESE: Die Anna Matrix kann CFB-bezogene Adressen von zufälligen
           Adressen unterscheiden (verschiedene Attraktoren).

TEST:
1. Bekannte CFB/Satoshi/Patoshi Adressen durch das Netzwerk
2. Zufällige Bitcoin-Adressen durch das Netzwerk
3. Vergleiche: Fallen sie in verschiedene Attraktoren?
"""

import json
import numpy as np
import hashlib
from pathlib import Path
from datetime import datetime
from collections import Counter

from aigarth_it.common import ternary_clamp

print("=" * 80)
print("     CFB ADRESS-KLASSIFIKATOR - ANNA MATRIX EXPERIMENT")
print("=" * 80)

# =============================================================================
# BEKANNTE ADRESSEN
# =============================================================================

# CFB-bezogene Adressen (aus unserer Forschung)
CFB_ADDRESSES = [
    # 1CFB Familie
    "1CFBhvhpkixz1PocoVT7F5JVBnNnJVKqbg",  # Die berühmte 1CFB Adresse
    "1CFBC2cK27goTguMT4rpxgnjPL9AJZU3bd",
    "1CFBjzdS6g3Ffb8kqLQA9HGGv2VHTbZ2ym",

    # Frühe Genesis Blöcke (aus unserer 10-Adressen Analyse)
    "1Ky8dP7oR1cBeg1MzkrgHAeHAHyn92DCar",  # Block 73
    "1B7CyZF8e6TYzhNBSHy8yYuTRJNpMtNChg",  # Block 121 (11²!)
    "1BwWdLV5wbnZvSYfNA8zaEMqEDDjvA99wX",  # Block 80
    "1FeGetWU2tR2QSrxnpRwHGXGcxzhN6zQza",  # Block 120

    # Patoshi Adressen
    "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX",  # Genesis Block Coinbase
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Satoshi's erste Adresse

    # 0x7B Familie (Block 264+)
    "1HBrMFBCPU3DTwAuoRQVQnvmfLBKAhfGJ4",  # Block 264
    "17XpR6K2QbNhTjGXwPw2sNFz7skRJtJdAU",  # Block 265
]

# POCC Qubic Adresse
QUBIC_ADDRESSES = [
    "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD",
]

# Kontrollgruppe: Bekannte NICHT-CFB Adressen (Exchange, Random)
CONTROL_ADDRESSES = [
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis (zum Vergleich)
    "3FZbgi29cpjq2GjdwV8eyHuJJnkLtktZc5",  # Binance
    "bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97",  # Bitfinex
    "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s",  # Binance Hot
    "385cR5DM96n1HvBDMzLHPYcw89fZAXULJP",  # Kraken
]

# =============================================================================
# MATRIX & NETZWERK
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
    return ternary

def address_to_input(address):
    """Konvertiere Adresse zu 128-dimensionalem ternären Input"""
    # Hash der Adresse
    addr_hash = hashlib.sha256(address.encode()).digest()
    # Erweitere auf 128 Werte
    extended = (addr_hash * 4)[:128]
    # Ternäre Konvertierung
    return [ternary_clamp(b - 128) for b in extended]

def process_network(matrix, inputs, max_ticks=200):
    """Führe Netzwerk-Simulation aus"""
    current = list(inputs)

    for tick in range(max_ticks):
        new_state = []
        for row in range(matrix.shape[0]):
            weights = matrix[row, :]
            score = int(np.sum(weights * np.array(current)))
            new_state.append(ternary_clamp(score))

        if new_state == current:
            return new_state, tick + 1, "converged"
        current = new_state

    return current, max_ticks, "max_ticks"

def output_to_signature(output):
    """Erstelle Signatur aus Output für Attractor-Vergleich"""
    pos = sum(1 for x in output if x == 1)
    neg = sum(1 for x in output if x == -1)
    zero = sum(1 for x in output if x == 0)

    # Hash für exakten Vergleich
    output_hash = hashlib.md5(str(output).encode()).hexdigest()[:8]

    return {
        "hash": output_hash,
        "pos": pos,
        "neg": neg,
        "zero": zero,
        "ratio": round(pos / (neg + 0.001), 2),
        "category": "A" if pos > neg else "B",  # Einfache Binär-Klassifikation
    }

# =============================================================================
# HAUPTEXPERIMENT
# =============================================================================

def main():
    print("\n[1] Lade Anna Matrix...")
    matrix = load_matrix()
    print(f"    ✓ Matrix: {matrix.shape}")

    results = {
        "timestamp": datetime.now().isoformat(),
        "cfb_addresses": [],
        "qubic_addresses": [],
        "control_addresses": [],
        "random_addresses": [],
    }

    # ==========================================================================
    print("\n[2] TESTE CFB-BEZOGENE ADRESSEN")
    print("=" * 60)

    cfb_signatures = []
    for addr in CFB_ADDRESSES:
        inp = address_to_input(addr)
        output, ticks, status = process_network(matrix, inp)
        sig = output_to_signature(output)
        sig["address"] = addr[:20] + "..."
        sig["ticks"] = ticks
        cfb_signatures.append(sig)
        results["cfb_addresses"].append(sig)

        print(f"  {addr[:25]:25} → {sig['category']} (ratio={sig['ratio']:.2f}, {sig['pos']}:{sig['neg']})")

    # ==========================================================================
    print("\n[3] TESTE QUBIC ADRESSEN")
    print("=" * 60)

    for addr in QUBIC_ADDRESSES:
        inp = address_to_input(addr)
        output, ticks, status = process_network(matrix, inp)
        sig = output_to_signature(output)
        sig["address"] = addr[:20] + "..."
        sig["ticks"] = ticks
        results["qubic_addresses"].append(sig)

        print(f"  {addr[:25]:25} → {sig['category']} (ratio={sig['ratio']:.2f}, {sig['pos']}:{sig['neg']})")

    # ==========================================================================
    print("\n[4] TESTE KONTROLL-ADRESSEN (Exchanges)")
    print("=" * 60)

    control_signatures = []
    for addr in CONTROL_ADDRESSES:
        inp = address_to_input(addr)
        output, ticks, status = process_network(matrix, inp)
        sig = output_to_signature(output)
        sig["address"] = addr[:20] + "..."
        sig["ticks"] = ticks
        control_signatures.append(sig)
        results["control_addresses"].append(sig)

        print(f"  {addr[:25]:25} → {sig['category']} (ratio={sig['ratio']:.2f}, {sig['pos']}:{sig['neg']})")

    # ==========================================================================
    print("\n[5] TESTE ZUFÄLLIGE ADRESSEN (1000 Stück)")
    print("=" * 60)

    np.random.seed(42)
    random_signatures = []

    for i in range(1000):
        # Generiere zufällige "Adresse"
        fake_addr = hashlib.sha256(f"random_{i}".encode()).hexdigest()
        inp = address_to_input(fake_addr)
        output, ticks, status = process_network(matrix, inp)
        sig = output_to_signature(output)
        random_signatures.append(sig)

        if i < 5:
            print(f"  Random #{i}: → {sig['category']} (ratio={sig['ratio']:.2f})")

    results["random_addresses"] = random_signatures[:10]  # Nur erste 10 speichern

    # ==========================================================================
    print("\n" + "=" * 80)
    print("                         ANALYSE")
    print("=" * 80)

    # Kategorien zählen
    cfb_categories = Counter([s['category'] for s in cfb_signatures])
    control_categories = Counter([s['category'] for s in control_signatures])
    random_categories = Counter([s['category'] for s in random_signatures])

    print(f"\n  CFB Adressen ({len(cfb_signatures)}):")
    print(f"    Kategorie A (pos>neg): {cfb_categories.get('A', 0)} ({100*cfb_categories.get('A', 0)/len(cfb_signatures):.1f}%)")
    print(f"    Kategorie B (neg>pos): {cfb_categories.get('B', 0)} ({100*cfb_categories.get('B', 0)/len(cfb_signatures):.1f}%)")

    print(f"\n  Kontroll-Adressen ({len(control_signatures)}):")
    print(f"    Kategorie A (pos>neg): {control_categories.get('A', 0)} ({100*control_categories.get('A', 0)/len(control_signatures):.1f}%)")
    print(f"    Kategorie B (neg>pos): {control_categories.get('B', 0)} ({100*control_categories.get('B', 0)/len(control_signatures):.1f}%)")

    print(f"\n  Zufällige Adressen ({len(random_signatures)}):")
    print(f"    Kategorie A (pos>neg): {random_categories.get('A', 0)} ({100*random_categories.get('A', 0)/len(random_signatures):.1f}%)")
    print(f"    Kategorie B (neg>pos): {random_categories.get('B', 0)} ({100*random_categories.get('B', 0)/len(random_signatures):.1f}%)")

    # Statistische Analyse
    cfb_a_pct = 100 * cfb_categories.get('A', 0) / len(cfb_signatures)
    random_a_pct = 100 * random_categories.get('A', 0) / len(random_signatures)

    # Ratio-Verteilung
    cfb_ratios = [s['ratio'] for s in cfb_signatures]
    random_ratios = [s['ratio'] for s in random_signatures]

    print(f"\n  Ratio-Statistik:")
    print(f"    CFB Mean Ratio:    {np.mean(cfb_ratios):.3f} (Std: {np.std(cfb_ratios):.3f})")
    print(f"    Random Mean Ratio: {np.mean(random_ratios):.3f} (Std: {np.std(random_ratios):.3f})")

    # Attractor-Hashes
    cfb_hashes = Counter([s['hash'] for s in cfb_signatures])
    random_hashes = Counter([s['hash'] for s in random_signatures])

    print(f"\n  Attractor-Verteilung:")
    print(f"    CFB eindeutige Attraktoren:    {len(cfb_hashes)}")
    print(f"    Random eindeutige Attraktoren: {len(random_hashes)}")

    # ==========================================================================
    print("\n" + "=" * 80)
    print("                         ERGEBNIS")
    print("=" * 80)

    # Signifikanztest (vereinfacht)
    diff = abs(cfb_a_pct - random_a_pct)

    if diff > 20:
        significance = "SIGNIFIKANT"
        conclusion = "CFB-Adressen werden ANDERS klassifiziert als zufällige!"
    elif diff > 10:
        significance = "MÖGLICH"
        conclusion = "Leichte Tendenz erkennbar, aber nicht stark."
    else:
        significance = "NICHT SIGNIFIKANT"
        conclusion = "Keine Unterscheidung zwischen CFB und zufälligen Adressen."

    print(f"""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    KLASSIFIKATIONS-ERGEBNIS                             │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │  CFB Adressen in Kategorie A:      {cfb_a_pct:5.1f}%                             │
    │  Zufällige Adressen in Kategorie A: {random_a_pct:5.1f}%                             │
    │  Differenz:                        {diff:5.1f}%                             │
    │                                                                         │
    │  Signifikanz: {significance:20}                                   │
    │                                                                         │
    │  FAZIT: {conclusion:50} │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘
    """)

    # Detaillierte CFB-Analyse
    print("\n  DETAILLIERTE CFB-KLASSIFIKATION:")
    for sig in cfb_signatures:
        marker = "★" if sig['category'] == 'A' else "○"
        print(f"    {marker} {sig['address']} → {sig['category']} ({sig['pos']}:{sig['neg']})")

    # Speichern
    results["analysis"] = {
        "cfb_category_a_pct": cfb_a_pct,
        "random_category_a_pct": random_a_pct,
        "difference": diff,
        "significance": significance,
        "conclusion": conclusion,
        "cfb_mean_ratio": float(np.mean(cfb_ratios)),
        "random_mean_ratio": float(np.mean(random_ratios)),
    }

    output_path = Path(__file__).parent / "CFB_CLASSIFIER_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✓ Ergebnisse gespeichert: {output_path.name}")

    return results

if __name__ == "__main__":
    main()
