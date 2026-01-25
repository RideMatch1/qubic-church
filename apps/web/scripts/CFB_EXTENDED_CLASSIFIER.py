#!/usr/bin/env python3
"""
===============================================================================
      ERWEITERTE CFB KLASSIFIKATION - PATOSHI & MEHR
===============================================================================

Testet:
1. Alle Patoshi-Adressen (145+)
2. Bekannte CFB-Adressen
3. Genesis Block Adressen
4. Exchange-Adressen als Kontrolle
5. Zufällige Adressen als Baseline

Output: CFB_EXTENDED_CLASSIFICATION.json
"""

import json
import numpy as np
import hashlib
from pathlib import Path
from datetime import datetime
from collections import Counter
import scipy.stats as stats

from aigarth_it.common import ternary_clamp

print("=" * 80)
print("     ERWEITERTE CFB KLASSIFIKATION")
print("=" * 80)

# =============================================================================
# ANNA MATRIX & NETZWERK
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

def input_to_ternary(data_string):
    """Konvertiere String zu 128-dimensionalem ternären Input"""
    data_hash = hashlib.sha256(data_string.encode()).digest()
    extended = (data_hash * 4)[:128]
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

def classify(matrix, data_string):
    """Klassifiziere einen String durch das Netzwerk"""
    inp = input_to_ternary(data_string)
    output, ticks, status = process_network(matrix, inp)

    pos = sum(1 for x in output if x == 1)
    neg = sum(1 for x in output if x == -1)

    output_hash = hashlib.md5(str(output).encode()).hexdigest()[:16]

    return {
        "category": "A" if pos > neg else "B",
        "attractor": output_hash,
        "pos": pos,
        "neg": neg,
        "ratio": round(pos / (neg + 0.001), 3),
        "ticks": ticks,
    }

# =============================================================================
# ADRESSEN LADEN
# =============================================================================

def load_patoshi_addresses():
    """Lade Patoshi-Adressen (Public Keys aus frühen Blöcken)"""
    patoshi_path = Path(__file__).parent.parent / "public" / "data" / "patoshi-addresses.json"

    try:
        with open(patoshi_path) as f:
            data = json.load(f)

        # Format: {"total": N, "records": [{blockHeight, pubkey, amount, ...}]}
        if 'records' in data:
            # Extrahiere pubkeys als Strings für Klassifikation
            return [str(r['pubkey']) for r in data['records'] if 'pubkey' in r]
        elif isinstance(data, list):
            return [a['pubkey'] if isinstance(a, dict) and 'pubkey' in a
                    else a['address'] if isinstance(a, dict) and 'address' in a
                    else str(a) for a in data]
        elif 'addresses' in data:
            return [a['address'] if isinstance(a, dict) else str(a) for a in data['addresses']]
        else:
            return [str(v) for v in data.values()] if isinstance(data, dict) else []
    except Exception as e:
        print(f"  Warnung: Patoshi-Adressen nicht geladen: {e}")
        return []

# Bekannte CFB-bezogene Adressen
CFB_ADDRESSES = [
    # Die berühmte 1CFB Familie
    "1CFBhvhpkixz1PocoVT7F5JVBnNnJVKqbg",
    "1CFBC2cK27goTguMT4rpxgnjPL9AJZU3bd",
    "1CFBjzdS6g3Ffb8kqLQA9HGGv2VHTbZ2ym",

    # Frühe Genesis Blöcke (unsere Analyse)
    "1Ky8dP7oR1cBeg1MzkrgHAeHAHyn92DCar",  # Block 73
    "1B7CyZF8e6TYzhNBSHy8yYuTRJNpMtNChg",  # Block 121 (11²!)
    "1BwWdLV5wbnZvSYfNA8zaEMqEDDjvA99wX",  # Block 80
    "1FeGetWU2tR2QSrxnpRwHGXGcxzhN6zQza",  # Block 120

    # Satoshi's bekannte Adressen
    "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX",  # Genesis Block Coinbase
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis Block

    # 0x7B Familie (Block 264+)
    "1HBrMFBCPU3DTwAuoRQVQnvmfLBKAhfGJ4",  # Block 264
    "17XpR6K2QbNhTjGXwPw2sNFz7skRJtJdAU",  # Block 265
]

# Qubic-bezogene Adressen
QUBIC_ADDRESSES = [
    "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD",  # POCC
]

# Exchange/Kontroll-Adressen
CONTROL_ADDRESSES = [
    "3FZbgi29cpjq2GjdwV8eyHuJJnkLtktZc5",   # Binance
    "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s",   # Binance Hot
    "385cR5DM96n1HvBDMzLHPYcw89fZAXULJP",   # Kraken
    "3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6",   # Bitfinex
    "1Kr6QSydW9bFQG1mXiPNNu6WpJGmUa9i1g",   # Coinbase
]

# =============================================================================
# HAUPTEXPERIMENT
# =============================================================================

def main():
    print("\n[1] Lade Anna Matrix...")
    matrix = load_matrix()
    print(f"    ✓ Matrix: {matrix.shape}")

    results = {
        "timestamp": datetime.now().isoformat(),
        "groups": {},
        "summary": {},
    }

    # ==========================================================================
    # GRUPPE 1: PATOSHI ADRESSEN
    # ==========================================================================
    print("\n[2] PATOSHI ADRESSEN")
    print("=" * 60)

    patoshi = load_patoshi_addresses()
    print(f"    Gefunden: {len(patoshi)} Adressen")

    patoshi_results = []
    patoshi_categories = Counter()

    for i, addr in enumerate(patoshi[:200]):  # Max 200
        result = classify(matrix, addr)
        patoshi_results.append({"address": addr, **result})
        patoshi_categories[result['category']] += 1

        if i < 5 or i % 50 == 0:
            symbol = "★" if result['category'] == 'A' else "○"
            print(f"    {symbol} {addr[:25]}... → {result['category']}")

    patoshi_a_pct = 100 * patoshi_categories.get('A', 0) / len(patoshi_results) if patoshi_results else 0
    print(f"\n    Patoshi Kategorie A: {patoshi_categories.get('A', 0)}/{len(patoshi_results)} ({patoshi_a_pct:.1f}%)")

    results['groups']['patoshi'] = {
        "count": len(patoshi_results),
        "results": patoshi_results[:50],  # Nur erste 50 speichern
        "category_a_pct": patoshi_a_pct,
        "categories": dict(patoshi_categories),
    }

    # ==========================================================================
    # GRUPPE 2: BEKANNTE CFB ADRESSEN
    # ==========================================================================
    print("\n[3] BEKANNTE CFB ADRESSEN")
    print("=" * 60)

    cfb_results = []
    cfb_categories = Counter()

    for addr in CFB_ADDRESSES:
        result = classify(matrix, addr)
        cfb_results.append({"address": addr, **result})
        cfb_categories[result['category']] += 1

        symbol = "★" if result['category'] == 'A' else "○"
        print(f"    {symbol} {addr[:25]}... → {result['category']}")

    cfb_a_pct = 100 * cfb_categories.get('A', 0) / len(cfb_results)
    print(f"\n    CFB Kategorie A: {cfb_categories.get('A', 0)}/{len(cfb_results)} ({cfb_a_pct:.1f}%)")

    results['groups']['cfb'] = {
        "count": len(cfb_results),
        "results": cfb_results,
        "category_a_pct": cfb_a_pct,
        "categories": dict(cfb_categories),
    }

    # ==========================================================================
    # GRUPPE 3: QUBIC ADRESSEN
    # ==========================================================================
    print("\n[4] QUBIC ADRESSEN")
    print("=" * 60)

    qubic_results = []
    qubic_categories = Counter()

    for addr in QUBIC_ADDRESSES:
        result = classify(matrix, addr)
        qubic_results.append({"address": addr, **result})
        qubic_categories[result['category']] += 1

        symbol = "★" if result['category'] == 'A' else "○"
        print(f"    {symbol} {addr[:25]}... → {result['category']}")

    results['groups']['qubic'] = {
        "count": len(qubic_results),
        "results": qubic_results,
        "categories": dict(qubic_categories),
    }

    # ==========================================================================
    # GRUPPE 4: KONTROLL-ADRESSEN (EXCHANGES)
    # ==========================================================================
    print("\n[5] KONTROLL-ADRESSEN (EXCHANGES)")
    print("=" * 60)

    control_results = []
    control_categories = Counter()

    for addr in CONTROL_ADDRESSES:
        result = classify(matrix, addr)
        control_results.append({"address": addr, **result})
        control_categories[result['category']] += 1

        symbol = "★" if result['category'] == 'A' else "○"
        print(f"    {symbol} {addr[:25]}... → {result['category']}")

    control_a_pct = 100 * control_categories.get('A', 0) / len(control_results)
    print(f"\n    Control Kategorie A: {control_categories.get('A', 0)}/{len(control_results)} ({control_a_pct:.1f}%)")

    results['groups']['control'] = {
        "count": len(control_results),
        "results": control_results,
        "category_a_pct": control_a_pct,
        "categories": dict(control_categories),
    }

    # ==========================================================================
    # GRUPPE 5: ZUFÄLLIGE ADRESSEN (BASELINE)
    # ==========================================================================
    print("\n[6] ZUFÄLLIGE ADRESSEN (BASELINE)")
    print("=" * 60)

    np.random.seed(42)
    random_results = []
    random_categories = Counter()

    for i in range(1000):
        fake_addr = hashlib.sha256(f"random_extended_{i}".encode()).hexdigest()
        result = classify(matrix, fake_addr)
        random_results.append({"address": fake_addr, **result})
        random_categories[result['category']] += 1

    random_a_pct = 100 * random_categories.get('A', 0) / len(random_results)
    print(f"    Random Kategorie A: {random_categories.get('A', 0)}/{len(random_results)} ({random_a_pct:.1f}%)")

    results['groups']['random'] = {
        "count": len(random_results),
        "results": random_results[:10],  # Nur erste 10 speichern
        "category_a_pct": random_a_pct,
        "categories": dict(random_categories),
    }

    # ==========================================================================
    # STATISTISCHE ANALYSE
    # ==========================================================================
    print("\n" + "=" * 80)
    print("                    STATISTISCHE ANALYSE")
    print("=" * 80)

    # Chi-Square Test für Patoshi vs Random
    if patoshi_results:
        observed_patoshi = [patoshi_categories.get('A', 0), patoshi_categories.get('B', 0)]
        expected_random = [len(patoshi_results) * random_a_pct / 100, len(patoshi_results) * (100 - random_a_pct) / 100]

        try:
            chi2, p_value = stats.chisquare(observed_patoshi, expected_random)
            print(f"\n  Chi-Square Test (Patoshi vs Random):")
            print(f"    Chi² = {chi2:.2f}, p-value = {p_value:.4f}")
            print(f"    {'SIGNIFIKANT' if p_value < 0.05 else 'NICHT SIGNIFIKANT'} (α=0.05)")
        except:
            p_value = 1.0
            print("  Chi-Square Test nicht möglich")
    else:
        p_value = 1.0

    # Zusammenfassung
    print(f"\n  ZUSAMMENFASSUNG KATEGORIE A:")
    print(f"    Patoshi:   {patoshi_a_pct:5.1f}%")
    print(f"    CFB:       {cfb_a_pct:5.1f}%")
    print(f"    Control:   {control_a_pct:5.1f}%")
    print(f"    Random:    {random_a_pct:5.1f}% (Baseline)")

    # Abweichungen
    print(f"\n  ABWEICHUNG VON BASELINE ({random_a_pct:.1f}%):")
    print(f"    Patoshi:   {patoshi_a_pct - random_a_pct:+5.1f}%")
    print(f"    CFB:       {cfb_a_pct - random_a_pct:+5.1f}%")
    print(f"    Control:   {control_a_pct - random_a_pct:+5.1f}%")

    # ==========================================================================
    print("\n" + "=" * 80)
    print("                         ERGEBNIS")
    print("=" * 80)

    # Signifikanz-Bewertung
    patoshi_deviation = abs(patoshi_a_pct - random_a_pct)
    cfb_deviation = abs(cfb_a_pct - random_a_pct)

    print(f"""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │             ERWEITERTE KLASSIFIKATION - ERGEBNIS                        │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │  GETESTETE GRUPPEN:                                                     │
    │                                                                         │
    │    Patoshi Adressen:  {len(patoshi_results):5}  ({patoshi_a_pct:5.1f}% Kat. A)                     │
    │    CFB Adressen:      {len(cfb_results):5}  ({cfb_a_pct:5.1f}% Kat. A)                     │
    │    Qubic Adressen:    {len(qubic_results):5}  (POCC = Kat. A)                       │
    │    Control (Exchange):{len(control_results):5}  ({control_a_pct:5.1f}% Kat. A)                     │
    │    Random Baseline:   {len(random_results):5}  ({random_a_pct:5.1f}% Kat. A)                     │
    │                                                                         │
    │  STATISTISCHE SIGNIFIKANZ:                                              │
    │                                                                         │
    │    Patoshi vs Random: {'SIGNIFIKANT' if p_value < 0.05 else 'NICHT SIGNIFIKANT':20} (p={p_value:.4f})       │
    │    Patoshi Abweichung: {patoshi_deviation:+5.1f}%                                    │
    │    CFB Abweichung:     {cfb_deviation:+5.1f}%                                    │
    │                                                                         │
    │  INTERPRETATION:                                                        │
    │                                                                         │
    │    Die Anna Matrix zeigt {'UNTERSCHIEDLICHE' if patoshi_deviation > 10 else 'ÄHNLICHE':20} Klassifikation      │
    │    für verschiedene Adress-Gruppen.                                     │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘
    """)

    # Summary speichern
    results['summary'] = {
        "patoshi_a_pct": patoshi_a_pct,
        "cfb_a_pct": cfb_a_pct,
        "control_a_pct": control_a_pct,
        "random_a_pct": random_a_pct,
        "patoshi_deviation": patoshi_deviation,
        "cfb_deviation": cfb_deviation,
        "chi2_p_value": p_value,
        "is_significant": p_value < 0.05,
    }

    # Speichern
    output_path = Path(__file__).parent / "CFB_EXTENDED_CLASSIFICATION.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"✓ Ergebnisse gespeichert: {output_path.name}")

    return results

if __name__ == "__main__":
    main()
