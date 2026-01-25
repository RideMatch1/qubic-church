#!/usr/bin/env python3
"""
===============================================================================
      UNTERSCHEIDUNGSMERKMAL-ANALYSE
===============================================================================

Findet heraus: Was unterscheidet Adressen, die in Kategorie A fallen,
von denen in Kategorie B?

Analysiert:
- SHA256 Hash Byte-Verteilung
- Bit-Muster
- ASCII-Wert Summen
- Base58 Positionen
- Präfix-Muster
- Entropie

Output: DISTINGUISHING_FEATURES.json
"""

import json
import numpy as np
import hashlib
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import string

from aigarth_it.common import ternary_clamp

print("=" * 80)
print("     UNTERSCHEIDUNGSMERKMAL-ANALYSE")
print("=" * 80)

# =============================================================================
# ANNA MATRIX & KLASSIFIKATION
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
    """Klassifiziere einen String"""
    inp = input_to_ternary(data_string)
    output, ticks, status = process_network(matrix, inp)

    pos = sum(1 for x in output if x == 1)
    neg = sum(1 for x in output if x == -1)

    return "A" if pos > neg else "B", inp, output

# =============================================================================
# FEATURE EXTRACTION
# =============================================================================

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def extract_features(addr):
    """Extrahiere alle möglichen Features einer Adresse"""

    # SHA256 Hash
    addr_hash = hashlib.sha256(addr.encode()).digest()

    features = {}

    # 1. Basis-Statistiken
    features['length'] = len(addr)
    features['ascii_sum'] = sum(ord(c) for c in addr)
    features['ascii_mean'] = features['ascii_sum'] / len(addr)

    # 2. Hash-Statistiken
    features['hash_byte_sum'] = sum(addr_hash)
    features['hash_byte_mean'] = sum(addr_hash) / 32
    features['hash_first_byte'] = addr_hash[0]
    features['hash_last_byte'] = addr_hash[31]
    features['hash_high_bytes'] = sum(1 for b in addr_hash if b > 128)
    features['hash_low_bytes'] = sum(1 for b in addr_hash if b <= 128)

    # 3. Bit-Analyse
    hash_bits = ''.join(format(b, '08b') for b in addr_hash)
    features['bit_ones'] = hash_bits.count('1')
    features['bit_zeros'] = hash_bits.count('0')
    features['bit_ratio'] = features['bit_ones'] / 256

    # 4. Ternäre Input-Statistiken
    extended = (addr_hash * 4)[:128]
    ternary_input = [ternary_clamp(b - 128) for b in extended]
    features['input_pos'] = sum(1 for x in ternary_input if x == 1)
    features['input_neg'] = sum(1 for x in ternary_input if x == -1)
    features['input_zero'] = sum(1 for x in ternary_input if x == 0)
    features['input_balance'] = features['input_pos'] - features['input_neg']

    # 5. Base58 Position-Analyse (für Bitcoin-Adressen)
    base58_positions = []
    for c in addr:
        if c in BASE58_ALPHABET:
            base58_positions.append(BASE58_ALPHABET.index(c))
    if base58_positions:
        features['base58_mean'] = sum(base58_positions) / len(base58_positions)
        features['base58_max'] = max(base58_positions)
        features['base58_min'] = min(base58_positions)
        features['base58_high_count'] = sum(1 for p in base58_positions if p > 29)
    else:
        features['base58_mean'] = 0
        features['base58_max'] = 0
        features['base58_min'] = 0
        features['base58_high_count'] = 0

    # 6. Präfix-Analyse
    features['starts_with_1'] = 1 if addr.startswith('1') else 0
    features['starts_with_3'] = 1 if addr.startswith('3') else 0
    features['starts_with_bc1'] = 1 if addr.startswith('bc1') else 0
    features['prefix_cfb'] = 1 if addr.upper().startswith('1CF') else 0

    # 7. Zeichen-Verteilung
    features['uppercase_count'] = sum(1 for c in addr if c.isupper())
    features['lowercase_count'] = sum(1 for c in addr if c.islower())
    features['digit_count'] = sum(1 for c in addr if c.isdigit())

    # 8. Entropie (Shannon)
    char_counts = Counter(addr)
    total = len(addr)
    entropy = -sum((c/total) * np.log2(c/total) for c in char_counts.values() if c > 0)
    features['entropy'] = entropy

    # 9. Checksum-ähnliche Features
    features['mod_27'] = features['ascii_sum'] % 27
    features['mod_121'] = features['ascii_sum'] % 121
    features['mod_676'] = features['ascii_sum'] % 676

    return features

# =============================================================================
# HAUPTANALYSE
# =============================================================================

def main():
    print("\n[1] Lade Anna Matrix...")
    matrix = load_matrix()
    print(f"    ✓ Matrix: {matrix.shape}")

    results = {
        "timestamp": datetime.now().isoformat(),
        "category_a_samples": [],
        "category_b_samples": [],
        "feature_comparison": {},
        "discriminating_features": [],
        "summary": {},
    }

    # Generiere und klassifiziere viele Adressen
    print("\n[2] GENERIERE UND KLASSIFIZIERE ADRESSEN")
    print("-" * 60)

    category_a = []
    category_b = []

    np.random.seed(42)

    # Test mit 2000 zufälligen Strings
    for i in range(2000):
        addr = hashlib.sha256(f"test_addr_{i}".encode()).hexdigest()[:34]
        cat, inp, out = classify(matrix, addr)
        features = extract_features(addr)

        if cat == "A":
            category_a.append({"address": addr, "features": features})
        else:
            category_b.append({"address": addr, "features": features})

        if i < 5:
            print(f"  {addr[:25]}... → {cat}")

    print(f"\n  Kategorie A: {len(category_a)}")
    print(f"  Kategorie B: {len(category_b)}")

    results['category_a_samples'] = category_a[:100]  # Nur erste 100 speichern
    results['category_b_samples'] = category_b[:100]

    # ==========================================================================
    print("\n[3] FEATURE-VERGLEICH")
    print("-" * 60)

    # Alle Features sammeln
    all_features = list(category_a[0]['features'].keys())

    feature_stats = {}

    for feature in all_features:
        a_values = [s['features'][feature] for s in category_a]
        b_values = [s['features'][feature] for s in category_b]

        a_mean = np.mean(a_values)
        b_mean = np.mean(b_values)
        a_std = np.std(a_values)
        b_std = np.std(b_values)

        # Differenz und Signifikanz
        diff = abs(a_mean - b_mean)
        pooled_std = np.sqrt((a_std**2 + b_std**2) / 2) + 0.001
        effect_size = diff / pooled_std  # Cohen's d

        feature_stats[feature] = {
            "category_a": {"mean": round(a_mean, 4), "std": round(a_std, 4)},
            "category_b": {"mean": round(b_mean, 4), "std": round(b_std, 4)},
            "difference": round(diff, 4),
            "effect_size": round(effect_size, 4),
        }

    results['feature_comparison'] = feature_stats

    # Sortiere nach Effect Size (welche Features unterscheiden am besten?)
    sorted_features = sorted(feature_stats.items(), key=lambda x: -x[1]['effect_size'])

    print("\n  TOP 10 UNTERSCHEIDENDE FEATURES:")
    print("  " + "-" * 56)

    discriminating = []
    for feature, stats in sorted_features[:10]:
        print(f"  {feature:25} | A={stats['category_a']['mean']:8.3f} | B={stats['category_b']['mean']:8.3f} | d={stats['effect_size']:.3f}")
        discriminating.append({
            "feature": feature,
            "effect_size": stats['effect_size'],
            "a_mean": stats['category_a']['mean'],
            "b_mean": stats['category_b']['mean'],
        })

    results['discriminating_features'] = discriminating

    # ==========================================================================
    print("\n[4] DETAILANALYSE DER TOP-FEATURES")
    print("-" * 60)

    # Analysiere die wichtigsten Features im Detail
    top_feature = sorted_features[0][0]
    top_stats = sorted_features[0][1]

    print(f"\n  WICHTIGSTES FEATURE: {top_feature}")
    print(f"    Kategorie A Mean: {top_stats['category_a']['mean']:.4f} (±{top_stats['category_a']['std']:.4f})")
    print(f"    Kategorie B Mean: {top_stats['category_b']['mean']:.4f} (±{top_stats['category_b']['std']:.4f})")
    print(f"    Effect Size (d):  {top_stats['effect_size']:.4f}")

    # Input-Balance als besonderer Focus
    if 'input_balance' in feature_stats:
        ib = feature_stats['input_balance']
        print(f"\n  INPUT BALANCE ANALYSE:")
        print(f"    Kategorie A Mean: {ib['category_a']['mean']:.4f}")
        print(f"    Kategorie B Mean: {ib['category_b']['mean']:.4f}")

        # Histogramm-ähnliche Verteilung
        a_balances = [s['features']['input_balance'] for s in category_a]
        b_balances = [s['features']['input_balance'] for s in category_b]

        print(f"\n    Input Balance Verteilung (Kat. A):")
        for bucket in [(-100, -50), (-50, 0), (0, 50), (50, 100)]:
            count = sum(1 for v in a_balances if bucket[0] <= v < bucket[1])
            print(f"      [{bucket[0]:4} bis {bucket[1]:4}): {count:4} ({100*count/len(a_balances):.1f}%)")

        print(f"\n    Input Balance Verteilung (Kat. B):")
        for bucket in [(-100, -50), (-50, 0), (0, 50), (50, 100)]:
            count = sum(1 for v in b_balances if bucket[0] <= v < bucket[1])
            print(f"      [{bucket[0]:4} bis {bucket[1]:4}): {count:4} ({100*count/len(b_balances):.1f}%)")

    # ==========================================================================
    print("\n[5] MUSTER-ERKENNUNG")
    print("-" * 60)

    # Gibt es bestimmte Muster, die eindeutig sind?
    patterns_a = Counter()
    patterns_b = Counter()

    for s in category_a:
        # Präfix (erste 3 Zeichen)
        patterns_a[s['address'][:3]] += 1
        # Hash Erstes Byte Bereich
        fb = s['features']['hash_first_byte']
        patterns_a[f"fb_{fb//32}"] += 1

    for s in category_b:
        patterns_b[s['address'][:3]] += 1
        fb = s['features']['hash_first_byte']
        patterns_b[f"fb_{fb//32}"] += 1

    print("\n  HASH ERSTES BYTE VERTEILUNG:")
    print("  (fb_0 = 0-31, fb_1 = 32-63, fb_2 = 64-95, fb_3 = 96-127, ...)")
    for i in range(8):
        a_count = patterns_a.get(f"fb_{i}", 0)
        b_count = patterns_b.get(f"fb_{i}", 0)
        a_pct = 100 * a_count / len(category_a)
        b_pct = 100 * b_count / len(category_b)
        diff_pct = a_pct - b_pct
        marker = " ←" if abs(diff_pct) > 3 else ""
        print(f"    fb_{i}: A={a_pct:5.1f}%  B={b_pct:5.1f}%  Diff={diff_pct:+5.1f}%{marker}")

    # ==========================================================================
    print("\n" + "=" * 80)
    print("                    ZUSAMMENFASSUNG")
    print("=" * 80)

    # Schlussfolgerungen
    conclusions = []

    # Prüfe ob input_balance signifikant ist
    if 'input_balance' in feature_stats:
        ib_effect = feature_stats['input_balance']['effect_size']
        if ib_effect > 0.2:
            conclusions.append(f"Input Balance unterscheidet Kategorien (d={ib_effect:.3f})")

    # Top Feature
    if sorted_features[0][1]['effect_size'] > 0.3:
        conclusions.append(f"Stärkstes Unterscheidungsmerkmal: {sorted_features[0][0]} (d={sorted_features[0][1]['effect_size']:.3f})")

    # Allgemeine Schlussfolgerung
    max_effect = max(s['effect_size'] for _, s in sorted_features)
    if max_effect < 0.2:
        interpretation = "KEINE signifikanten Unterscheidungsmerkmale gefunden"
    elif max_effect < 0.5:
        interpretation = "SCHWACHE Unterscheidungsmerkmale gefunden"
    elif max_effect < 0.8:
        interpretation = "MODERATE Unterscheidungsmerkmale gefunden"
    else:
        interpretation = "STARKE Unterscheidungsmerkmale gefunden"

    conclusions.append(interpretation)

    results['summary'] = {
        "total_samples": len(category_a) + len(category_b),
        "category_a_count": len(category_a),
        "category_b_count": len(category_b),
        "top_feature": sorted_features[0][0],
        "top_effect_size": sorted_features[0][1]['effect_size'],
        "max_effect_size": max_effect,
        "interpretation": interpretation,
        "conclusions": conclusions,
    }

    print(f"""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │             UNTERSCHEIDUNGSMERKMAL-ANALYSE - ERGEBNIS                   │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │  GETESTETE ADRESSEN:        {len(category_a) + len(category_b):5}                                       │
    │    Kategorie A:             {len(category_a):5} ({100*len(category_a)/(len(category_a)+len(category_b)):.1f}%)                            │
    │    Kategorie B:             {len(category_b):5} ({100*len(category_b)/(len(category_a)+len(category_b)):.1f}%)                            │
    │                                                                         │
    │  TOP UNTERSCHEIDENDE FEATURES:                                          │""")

    for i, (f, s) in enumerate(sorted_features[:5]):
        print(f"│    {i+1}. {f:20} (d={s['effect_size']:.3f})                         │")

    print(f"""│                                                                         │
    │  MAXIMALER EFFECT SIZE:     {max_effect:.3f}                                    │
    │                                                                         │
    │  INTERPRETATION: {interpretation:40}       │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘
    """)

    # Speichern
    output_path = Path(__file__).parent / "DISTINGUISHING_FEATURES.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"✓ Ergebnisse gespeichert: {output_path.name}")

    return results

if __name__ == "__main__":
    main()
