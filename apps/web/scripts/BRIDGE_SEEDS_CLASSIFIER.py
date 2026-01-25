#!/usr/bin/env python3
"""
===============================================================================
      BRIDGE SEEDS KLASSIFIKATOR - 165 SEEDS DURCH ANNA MATRIX
===============================================================================

Klassifiziert alle 165 Bridge Seeds durch das Anna Matrix Netzwerk.
Testet sowohl Bitcoin-Adressen als auch Qubic-Seeds.

Output: BRIDGE_SEEDS_CLASSIFICATION.json
"""

import json
import numpy as np
import hashlib
from pathlib import Path
from datetime import datetime
from collections import Counter

from aigarth_it.common import ternary_clamp

print("=" * 80)
print("     BRIDGE SEEDS KLASSIFIKATOR - 165 SEEDS")
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
    zero = sum(1 for x in output if x == 0)

    output_hash = hashlib.md5(str(output).encode()).hexdigest()[:16]

    return {
        "category": "A" if pos > neg else "B",
        "attractor": output_hash,
        "distribution": {"pos": pos, "neg": neg, "zero": zero},
        "ratio": round(pos / (neg + 0.001), 3),
        "ticks": ticks,
        "status": status,
    }

# =============================================================================
# BRIDGE SEEDS LADEN
# =============================================================================

def load_bridge_seeds():
    """Lade die 165 Bridge Seeds"""
    bridge_path = Path(__file__).parent / "COMPLETE_BRIDGE_DATASET.json"

    with open(bridge_path) as f:
        data = json.load(f)

    return data['bridges'], data['metadata'], data['statistics']

# =============================================================================
# HAUPTEXPERIMENT
# =============================================================================

def main():
    print("\n[1] Lade Anna Matrix...")
    matrix = load_matrix()
    print(f"    ✓ Matrix: {matrix.shape}")

    print("\n[2] Lade Bridge Seeds...")
    bridges, metadata, stats = load_bridge_seeds()
    print(f"    ✓ {len(bridges)} Bridge Seeds geladen")
    print(f"    By type: Column={stats['by_type']['column']}, Row={stats['by_type']['row']}, XOR={stats['by_type']['xor_pair']}")

    results = {
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata,
        "total_bridges": len(bridges),
        "classifications": [],
        "summary": {},
    }

    # Zähler
    btc_categories = Counter()
    qubic_xor_categories = Counter()
    qubic_direct_categories = Counter()
    attractor_counts = Counter()
    cfb_special = []

    print("\n[3] KLASSIFIZIERE ALLE BRIDGES")
    print("=" * 60)

    for i, bridge in enumerate(bridges):
        bridge_id = bridge['id']
        bridge_name = bridge['name']
        bridge_type = bridge['type']

        # Bitcoin-Adresse klassifizieren
        btc_addr = bridge['bitcoin']['address']
        btc_result = classify(matrix, btc_addr)
        btc_categories[btc_result['category']] += 1
        attractor_counts[btc_result['attractor']] += 1

        # Qubic XOR Seed klassifizieren (falls vorhanden)
        if 'qubic_xor' in bridge and bridge['qubic_xor'].get('seed'):
            qubic_xor = bridge['qubic_xor']['seed']
            xor_result = classify(matrix, qubic_xor)
            qubic_xor_categories[xor_result['category']] += 1
        else:
            qubic_xor = None
            xor_result = {"category": "N/A", "attractor": "none", "distribution": {}, "ratio": 0, "ticks": 0, "status": "skipped"}

        # Qubic Direct Seed klassifizieren (falls vorhanden)
        if 'qubic_direct' in bridge and bridge['qubic_direct'].get('seed'):
            qubic_direct = bridge['qubic_direct']['seed']
            direct_result = classify(matrix, qubic_direct)
            qubic_direct_categories[direct_result['category']] += 1
        else:
            qubic_direct = None
            direct_result = {"category": "N/A", "attractor": "none", "distribution": {}, "ratio": 0, "ticks": 0, "status": "skipped"}

        # Spezielle CFB-Adressen markieren
        is_cfb = btc_addr.startswith('1CF')
        is_special = btc_result['category'] == 'A'

        if is_cfb or is_special:
            cfb_special.append({
                "id": bridge_id,
                "name": bridge_name,
                "address": btc_addr,
                "category": btc_result['category'],
                "is_cfb": is_cfb,
            })

        # Ergebnis speichern
        classification = {
            "id": bridge_id,
            "name": bridge_name,
            "type": bridge_type,
            "bitcoin": {
                "address": btc_addr,
                **btc_result,
            },
            "qubic_xor": {
                "seed": qubic_xor,
                **xor_result,
            },
            "qubic_direct": {
                "seed": qubic_direct,
                **direct_result,
            },
            "correlation": {
                "btc_xor_match": btc_result['category'] == xor_result['category'] if xor_result['category'] != "N/A" else None,
                "btc_direct_match": btc_result['category'] == direct_result['category'] if direct_result['category'] != "N/A" else None,
                "all_same": (btc_result['category'] == xor_result['category'] == direct_result['category']) if xor_result['category'] != "N/A" and direct_result['category'] != "N/A" else None,
                "has_qubic_seeds": qubic_xor is not None,
            },
            "is_cfb": is_cfb,
            "position_3d": bridge.get('3d', {}).get('position', [0, 0, 0]),
        }
        results['classifications'].append(classification)

        # Progress
        if (i + 1) % 20 == 0 or i < 5:
            symbol = "★" if btc_result['category'] == 'A' else "○"
            print(f"  {symbol} #{bridge_id:3}: {bridge_name:20} BTC={btc_result['category']} XOR={xor_result['category']} DIR={direct_result['category']}")

    # ==========================================================================
    print("\n" + "=" * 80)
    print("                         ANALYSE")
    print("=" * 80)

    # Bitcoin-Adressen Statistik
    total = len(bridges)
    btc_a_pct = 100 * btc_categories.get('A', 0) / total
    btc_b_pct = 100 * btc_categories.get('B', 0) / total

    print(f"\n  BITCOIN-ADRESSEN ({total}):")
    print(f"    Kategorie A: {btc_categories.get('A', 0)} ({btc_a_pct:.1f}%)")
    print(f"    Kategorie B: {btc_categories.get('B', 0)} ({btc_b_pct:.1f}%)")

    # Qubic Seeds Statistik
    xor_a_pct = 100 * qubic_xor_categories.get('A', 0) / total
    direct_a_pct = 100 * qubic_direct_categories.get('A', 0) / total

    print(f"\n  QUBIC XOR SEEDS ({total}):")
    print(f"    Kategorie A: {qubic_xor_categories.get('A', 0)} ({xor_a_pct:.1f}%)")
    print(f"    Kategorie B: {qubic_xor_categories.get('B', 0)} ({100-xor_a_pct:.1f}%)")

    print(f"\n  QUBIC DIRECT SEEDS ({total}):")
    print(f"    Kategorie A: {qubic_direct_categories.get('A', 0)} ({direct_a_pct:.1f}%)")
    print(f"    Kategorie B: {qubic_direct_categories.get('B', 0)} ({100-direct_a_pct:.1f}%)")

    # Korrelation (nur für Bridges mit Qubic Seeds)
    correlations = [c['correlation'] for c in results['classifications']]
    correlations_with_seeds = [c for c in correlations if c.get('has_qubic_seeds')]
    all_same_count = sum(1 for c in correlations_with_seeds if c.get('all_same'))

    seeds_total = len(correlations_with_seeds)
    print(f"\n  KORRELATION (nur Bridges mit Qubic Seeds: {seeds_total}):")
    print(f"    BTC ↔ XOR gleich:    {sum(1 for c in correlations_with_seeds if c.get('btc_xor_match'))}/{seeds_total}")
    print(f"    BTC ↔ Direct gleich: {sum(1 for c in correlations_with_seeds if c.get('btc_direct_match'))}/{seeds_total}")
    print(f"    Alle 3 gleich:       {all_same_count}/{seeds_total} ({100*all_same_count/seeds_total:.1f}%)" if seeds_total > 0 else "    Keine Seeds")

    # Attraktoren
    print(f"\n  ATTRAKTOREN (Bitcoin-Adressen):")
    for attr, count in attractor_counts.most_common(5):
        print(f"    {attr}: {count}x ({100*count/total:.1f}%)")

    # Spezielle Adressen
    if cfb_special:
        print(f"\n  SPEZIELLE ADRESSEN (CFB oder Kategorie A):")
        for item in cfb_special[:10]:
            marker = "★ CFB" if item['is_cfb'] else "○"
            print(f"    {marker} {item['address'][:25]}... → {item['category']}")

    # ==========================================================================
    print("\n" + "=" * 80)
    print("                         ERGEBNIS")
    print("=" * 80)

    # Vergleich mit Zufalls-Baseline (50%)
    deviation = abs(btc_a_pct - 50)

    if deviation > 15:
        significance = "HOCH SIGNIFIKANT"
    elif deviation > 5:
        significance = "SIGNIFIKANT"
    else:
        significance = "NICHT SIGNIFIKANT"

    print(f"""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │              BRIDGE SEEDS KLASSIFIKATION - ERGEBNIS                     │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │  Gesamt Bridge Seeds:     {total:5}                                        │
    │                                                                         │
    │  BITCOIN-ADRESSEN:                                                      │
    │    Kategorie A:           {btc_categories.get('A', 0):5} ({btc_a_pct:5.1f}%)                            │
    │    Kategorie B:           {btc_categories.get('B', 0):5} ({btc_b_pct:5.1f}%)                            │
    │                                                                         │
    │  QUBIC XOR SEEDS:                                                       │
    │    Kategorie A:           {qubic_xor_categories.get('A', 0):5} ({xor_a_pct:5.1f}%)                            │
    │                                                                         │
    │  KORRELATION BTC ↔ QUBIC: {all_same_count:3}/{total} ({100*all_same_count/total:.1f}%)                          │
    │                                                                         │
    │  Abweichung von 50%:      {deviation:5.1f}%                                   │
    │  Signifikanz:             {significance:20}                    │
    │                                                                         │
    │  CFB-Adressen gefunden:   {sum(1 for x in cfb_special if x['is_cfb']):5}                                        │
    │  Kategorie A (besonders): {len([x for x in cfb_special if x['category']=='A']):5}                                        │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘
    """)

    # Summary speichern
    results['summary'] = {
        "bitcoin_categories": dict(btc_categories),
        "qubic_xor_categories": dict(qubic_xor_categories),
        "qubic_direct_categories": dict(qubic_direct_categories),
        "attractor_distribution": dict(attractor_counts),
        "btc_category_a_pct": btc_a_pct,
        "qubic_xor_category_a_pct": xor_a_pct,
        "qubic_direct_category_a_pct": direct_a_pct,
        "correlation_all_same_pct": 100 * all_same_count / total,
        "deviation_from_random": deviation,
        "significance": significance,
        "cfb_addresses_found": sum(1 for x in cfb_special if x['is_cfb']),
        "special_category_a": len([x for x in cfb_special if x['category'] == 'A']),
    }

    # Speichern
    output_path = Path(__file__).parent / "BRIDGE_SEEDS_CLASSIFICATION.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"✓ Ergebnisse gespeichert: {output_path.name}")

    # Auch für Visualisierung speichern
    viz_data = {
        "nodes": [],
        "metadata": {
            "generated": datetime.now().isoformat(),
            "total": total,
            "categories": dict(btc_categories),
        }
    }

    for c in results['classifications']:
        viz_data['nodes'].append({
            "id": c['id'],
            "name": c['name'],
            "type": c['type'],
            "position": c['position_3d'],
            "category": c['bitcoin']['category'],
            "attractor": c['bitcoin']['attractor'],
            "is_cfb": c['is_cfb'],
            "bitcoin_address": c['bitcoin']['address'],
            "correlation": c['correlation']['all_same'],
        })

    viz_path = Path(__file__).parent.parent / "public" / "data" / "bridge-classification.json"
    with open(viz_path, 'w') as f:
        json.dump(viz_data, f, indent=2)

    print(f"✓ Visualisierungs-Daten: public/data/bridge-classification.json")

    return results

if __name__ == "__main__":
    main()
