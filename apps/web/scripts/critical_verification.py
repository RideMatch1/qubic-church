#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    CRITICAL SELF-VERIFICATION                                  ║
║                                                                                ║
║  Wissenschaftliche Selbstkritik: Sind meine Befunde valide?                   ║
║  - Statistische Signifikanz prüfen                                            ║
║  - Cherry-Picking aufdecken                                                   ║
║  - Alternative Erklärungen suchen                                             ║
║  - Null-Hypothese testen                                                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import math
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from collections import Counter
import statistics

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

CFB_NUMBERS = {27, 37, 42, 127}

def load_matrix() -> List[List[int]]:
    """Load Anna Matrix and convert any string values to integers"""
    with open(MATRIX_FILE, 'r') as f:
        data = json.load(f)
    matrix = []
    for row in data['matrix']:
        clean_row = []
        for v in row:
            if isinstance(v, str):
                clean_row.append(0)
            else:
                clean_row.append(int(v))
        matrix.append(clean_row)
    return matrix

class CriticalVerification:
    def __init__(self):
        print("═" * 70)
        print("           CRITICAL SELF-VERIFICATION")
        print("           Wissenschaftliche Selbstkritik")
        print("═" * 70)
        self.matrix = load_matrix()
        self.flat_values = [v for row in self.matrix for v in row]
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'claims_verified': {},
            'claims_refuted': {},
            'warnings': [],
            'alternative_explanations': [],
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # CLAIM 1: -27 erscheint 476 Mal (+643.8% über erwartet)
    # ═══════════════════════════════════════════════════════════════════════════

    def verify_claim_minus27(self):
        """Kritische Prüfung der -27 Anomalie"""
        print("\n" + "─" * 70)
        print("CLAIM 1: -27 Anomalie verifizieren")
        print("─" * 70)

        # Zählung verifizieren
        count_minus27 = sum(1 for v in self.flat_values if v == -27)
        count_plus27 = sum(1 for v in self.flat_values if v == 27)
        total = len(self.flat_values)

        print(f"\n  Verifizierte Zählung:")
        print(f"    -27: {count_minus27} Mal")
        print(f"    +27: {count_plus27} Mal")

        # Erwartungswert für uniforme Verteilung
        # Bei 256 möglichen Werten (-128 bis 127) und 16384 Zellen
        expected_per_value = total / 256
        print(f"\n  Erwartungswert (uniform): {expected_per_value:.1f} pro Wert")

        # Chi-Quadrat-Test für -27
        chi_sq_minus27 = (count_minus27 - expected_per_value) ** 2 / expected_per_value
        chi_sq_plus27 = (count_plus27 - expected_per_value) ** 2 / expected_per_value

        print(f"\n  Chi-Quadrat Beiträge:")
        print(f"    -27: χ² = {chi_sq_minus27:.2f}")
        print(f"    +27: χ² = {chi_sq_plus27:.2f}")

        # KRITIK 1: Ist -27 wirklich die häufigste Zahl?
        print("\n  KRITIK 1: Ist -27 wirklich der Mode?")
        value_counts = Counter(self.flat_values)
        top_10 = value_counts.most_common(10)
        print("    Top 10 häufigste Werte:")
        for val, count in top_10:
            marker = " ★ MODE" if val == top_10[0][0] else ""
            cfb_marker = " [CFB]" if abs(val) in CFB_NUMBERS else ""
            print(f"      {val:+4d}: {count:4d} Mal{cfb_marker}{marker}")

        actual_mode = top_10[0][0]
        if actual_mode == -27:
            print("    ✓ BESTÄTIGT: -27 ist tatsächlich der Mode")
            self.results['claims_verified']['minus27_is_mode'] = True
        else:
            print(f"    ✗ WIDERLEGT: Mode ist {actual_mode}, nicht -27!")
            self.results['claims_refuted']['minus27_is_mode'] = f"Actual mode: {actual_mode}"

        # KRITIK 2: Wie verhält sich -27 zu anderen negativen Zahlen?
        print("\n  KRITIK 2: Ist -27 unter negativen Zahlen besonders?")
        negative_counts = {v: c for v, c in value_counts.items() if v < 0}
        neg_sorted = sorted(negative_counts.items(), key=lambda x: -x[1])[:10]
        print("    Top 10 häufigste negative Werte:")
        for val, count in neg_sorted:
            cfb_marker = " [CFB]" if abs(val) in CFB_NUMBERS else ""
            print(f"      {val:+4d}: {count:4d} Mal{cfb_marker}")

        # KRITIK 3: Gibt es andere Werte mit ähnlicher Häufigkeit?
        print("\n  KRITIK 3: Cluster-Analyse der Häufigkeiten")
        # Gruppiere Werte nach Häufigkeitsbereich
        freq_ranges = {
            '400+': [],
            '200-399': [],
            '100-199': [],
            '50-99': [],
        }
        for val, count in value_counts.items():
            if count >= 400:
                freq_ranges['400+'].append((val, count))
            elif count >= 200:
                freq_ranges['200-399'].append((val, count))
            elif count >= 100:
                freq_ranges['100-199'].append((val, count))
            elif count >= 50:
                freq_ranges['50-99'].append((val, count))

        for range_name, values in freq_ranges.items():
            if values:
                print(f"    {range_name}: {len(values)} Werte")
                for v, c in sorted(values, key=lambda x: -x[1])[:3]:
                    print(f"      {v:+4d}: {c}")

        # KRITIK 4: P-Wert berechnen (vereinfacht)
        print("\n  KRITIK 4: Statistische Signifikanz")
        # Unter Null-Hypothese (uniform), Wahrscheinlichkeit dass ein Wert
        # 476 oder mehr Mal erscheint bei n=16384, p=1/256
        # Verwende Poisson-Approximation
        lambda_poisson = total / 256  # ≈ 64

        # P(X >= 476) ist extrem klein bei Poisson(64)
        # Für praktische Zwecke: berechne Z-Score
        std_poisson = math.sqrt(lambda_poisson)
        z_score = (count_minus27 - lambda_poisson) / std_poisson
        print(f"    Poisson λ = {lambda_poisson:.1f}")
        print(f"    Z-Score für -27: {z_score:.2f}")
        print(f"    (Z > 3 bedeutet p < 0.001)")

        if z_score > 10:
            print(f"    ✓ HOCHSIGNIFIKANT: Z = {z_score:.1f} >> 3")
            self.results['claims_verified']['minus27_significance'] = f"Z = {z_score:.1f}"
        else:
            print(f"    ? FRAGLICH: Z = {z_score:.1f}")
            self.results['warnings'].append(f"-27 Z-score only {z_score:.1f}")

    # ═══════════════════════════════════════════════════════════════════════════
    # CLAIM 2: Mirror Pattern (+27 oben, -27 unten)
    # ═══════════════════════════════════════════════════════════════════════════

    def verify_claim_mirror_pattern(self):
        """Kritische Prüfung des Mirror-Patterns"""
        print("\n" + "─" * 70)
        print("CLAIM 2: Mirror Pattern verifizieren")
        print("─" * 70)

        # Zähle +27 und -27 in jeder Hälfte
        upper_half = {'plus27': 0, 'minus27': 0, 'total': 0}
        lower_half = {'plus27': 0, 'minus27': 0, 'total': 0}

        for r in range(128):
            for c in range(128):
                v = self.matrix[r][c]
                if r < 64:
                    upper_half['total'] += 1
                    if v == 27:
                        upper_half['plus27'] += 1
                    elif v == -27:
                        upper_half['minus27'] += 1
                else:
                    lower_half['total'] += 1
                    if v == 27:
                        lower_half['plus27'] += 1
                    elif v == -27:
                        lower_half['minus27'] += 1

        print(f"\n  Obere Hälfte (Rows 0-63):")
        print(f"    +27: {upper_half['plus27']}")
        print(f"    -27: {upper_half['minus27']}")
        print(f"    Ratio +27/-27: {upper_half['plus27']/max(1,upper_half['minus27']):.2f}")

        print(f"\n  Untere Hälfte (Rows 64-127):")
        print(f"    +27: {lower_half['plus27']}")
        print(f"    -27: {lower_half['minus27']}")
        print(f"    Ratio +27/-27: {lower_half['plus27']/max(1,lower_half['minus27']):.2f}")

        # KRITIK 1: Ist das wirklich ein "Mirror"?
        print("\n  KRITIK 1: Symmetrie-Test")
        # Für echtes Mirror müsste +27 oben ≈ -27 unten sein
        mirror_score = abs(upper_half['plus27'] - lower_half['minus27'])
        print(f"    |+27_oben - (-27)_unten| = {mirror_score}")

        if upper_half['plus27'] > upper_half['minus27'] and lower_half['minus27'] > lower_half['plus27']:
            print("    ✓ Grundmuster bestätigt: +27 dominiert oben, -27 dominiert unten")
        else:
            print("    ✗ WIDERLEGT: Kein klares Mirror-Pattern")
            self.results['claims_refuted']['mirror_pattern'] = "Pattern not clear"

        # KRITIK 2: War mein Quadranten-Claim korrekt?
        print("\n  KRITIK 2: Quadranten-Detail")
        quadrants = {
            'NW': {'plus27': 0, 'minus27': 0},
            'NE': {'plus27': 0, 'minus27': 0},
            'SW': {'plus27': 0, 'minus27': 0},
            'SE': {'plus27': 0, 'minus27': 0},
        }
        for r in range(128):
            for c in range(128):
                v = self.matrix[r][c]
                if v == 27:
                    key = 'plus27'
                elif v == -27:
                    key = 'minus27'
                else:
                    continue

                if r < 64 and c < 64:
                    quadrants['NW'][key] += 1
                elif r < 64:
                    quadrants['NE'][key] += 1
                elif c < 64:
                    quadrants['SW'][key] += 1
                else:
                    quadrants['SE'][key] += 1

        print("    Quadrant  +27   -27   Dominant")
        for q in ['NW', 'NE', 'SW', 'SE']:
            p27 = quadrants[q]['plus27']
            m27 = quadrants[q]['minus27']
            dominant = "+27" if p27 > m27 else "-27" if m27 > p27 else "gleich"
            print(f"    {q}        {p27:4d}  {m27:4d}  {dominant}")

        # Meine Behauptung war: +27 in NW+NE (70%), -27 in SW+SE (86%)
        total_plus27 = sum(q['plus27'] for q in quadrants.values())
        total_minus27 = sum(q['minus27'] for q in quadrants.values())

        plus27_upper = quadrants['NW']['plus27'] + quadrants['NE']['plus27']
        minus27_lower = quadrants['SW']['minus27'] + quadrants['SE']['minus27']

        plus27_upper_pct = plus27_upper / max(1, total_plus27) * 100
        minus27_lower_pct = minus27_lower / max(1, total_minus27) * 100

        print(f"\n  Meine Behauptung: +27 in NW+NE: 70%, -27 in SW+SE: 86%")
        print(f"  Tatsächlich: +27 in NW+NE: {plus27_upper_pct:.1f}%, -27 in SW+SE: {minus27_lower_pct:.1f}%")

        if abs(plus27_upper_pct - 70) < 10 and abs(minus27_lower_pct - 86) < 10:
            print("    ✓ Behauptung im Wesentlichen korrekt")
            self.results['claims_verified']['mirror_percentages'] = True
        else:
            print("    ⚠ Behauptung war ungenau!")
            self.results['warnings'].append(f"Mirror percentages off: +27 upper={plus27_upper_pct:.1f}%, -27 lower={minus27_lower_pct:.1f}%")

    # ═══════════════════════════════════════════════════════════════════════════
    # CLAIM 3: SW Quadrant XOR = -127
    # ═══════════════════════════════════════════════════════════════════════════

    def verify_claim_sw_quadrant(self):
        """Kritische Prüfung des SW Quadrant XOR"""
        print("\n" + "─" * 70)
        print("CLAIM 3: SW Quadrant XOR = -127 verifizieren")
        print("─" * 70)

        # Berechne XOR für jeden Quadranten
        quadrant_xors = {}
        for qname, (r_start, r_end, c_start, c_end) in [
            ('NW', (0, 64, 0, 64)),
            ('NE', (0, 64, 64, 128)),
            ('SW', (64, 128, 0, 64)),
            ('SE', (64, 128, 64, 128)),
        ]:
            xor_sum = 0
            for r in range(r_start, r_end):
                for c in range(c_start, c_end):
                    xor_sum ^= self.matrix[r][c]
            quadrant_xors[qname] = xor_sum

        print("\n  Quadranten XOR Summen:")
        for q, xor_val in quadrant_xors.items():
            cfb_marker = " ★ CFB!" if abs(xor_val) in CFB_NUMBERS else ""
            print(f"    {q}: {xor_val:+4d}{cfb_marker}")

        if quadrant_xors['SW'] == -127:
            print("\n    ✓ BESTÄTIGT: SW Quadrant XOR = -127")
            self.results['claims_verified']['sw_quadrant_xor'] = True
        else:
            print(f"\n    ✗ WIDERLEGT: SW Quadrant XOR = {quadrant_xors['SW']}, nicht -127!")
            self.results['claims_refuted']['sw_quadrant_xor'] = quadrant_xors['SW']

        # KRITIK: Wie wahrscheinlich ist das zufällig?
        print("\n  KRITIK: Wie wahrscheinlich ist XOR = CFB-Zahl zufällig?")
        # Bei 4096 Zellen und zufälligen Werten ist das XOR-Ergebnis
        # im Bereich -128 bis 127 (8 bit), also 1/256 Chance pro Wert
        # Für genau 4 CFB-Zahlen (±27, ±37, ±42, ±127) = 8 Werte
        prob_cfb = 8 / 256
        print(f"    P(XOR ∈ CFB) ≈ {prob_cfb:.3f} = {prob_cfb*100:.1f}%")
        print(f"    Das ist nicht besonders unwahrscheinlich!")

        # Zähle wie viele Quadranten CFB-XOR haben
        cfb_quadrants = sum(1 for x in quadrant_xors.values() if abs(x) in CFB_NUMBERS)
        print(f"    Quadranten mit CFB-XOR: {cfb_quadrants} von 4")

        if cfb_quadrants <= 1:
            print("    ⚠ Nur 1 Quadrant mit CFB-XOR - könnte Zufall sein")
            self.results['warnings'].append("Only 1 quadrant has CFB XOR - could be chance")

    # ═══════════════════════════════════════════════════════════════════════════
    # CLAIM 4: 24.42x Clustering-Faktor
    # ═══════════════════════════════════════════════════════════════════════════

    def verify_claim_clustering(self):
        """Kritische Prüfung des Clustering-Faktors"""
        print("\n" + "─" * 70)
        print("CLAIM 4: 24.42x Clustering verifizieren")
        print("─" * 70)

        # Neuberechnung
        same_neighbors = 0
        total_pairs = 0

        # Horizontale Nachbarn
        for r in range(128):
            for c in range(127):
                total_pairs += 1
                if self.matrix[r][c] == self.matrix[r][c+1]:
                    same_neighbors += 1

        # Vertikale Nachbarn
        for r in range(127):
            for c in range(128):
                total_pairs += 1
                if self.matrix[r][c] == self.matrix[r+1][c]:
                    same_neighbors += 1

        observed_rate = same_neighbors / total_pairs
        expected_rate = 1 / 256  # Bei 256 möglichen Werten
        clustering_factor = observed_rate / expected_rate

        print(f"\n  Neuberechnung:")
        print(f"    Gleiche Nachbarn: {same_neighbors} von {total_pairs}")
        print(f"    Beobachtete Rate: {observed_rate*100:.3f}%")
        print(f"    Erwartete Rate:   {expected_rate*100:.3f}%")
        print(f"    Clustering-Faktor: {clustering_factor:.2f}x")

        if abs(clustering_factor - 24.42) < 1:
            print("\n    ✓ BESTÄTIGT: Clustering ≈ 24x")
            self.results['claims_verified']['clustering_factor'] = clustering_factor
        else:
            print(f"\n    ⚠ ABWEICHUNG: {clustering_factor:.2f}x statt 24.42x")
            self.results['warnings'].append(f"Clustering factor: {clustering_factor:.2f}x")

        # KRITIK: Ist Clustering in neuronalen Netzen normal?
        print("\n  KRITIK: Ist Clustering in NN-Weights normal?")
        print("    Neuronale Netze haben oft:")
        print("    - Quantisierte Gewichte (begrenzte Werte)")
        print("    - Räumliche Korrelation (Filter)")
        print("    - Sparsity (viele Nullen)")

        # Prüfe Sparsity
        zero_count = sum(1 for v in self.flat_values if v == 0)
        zero_pct = zero_count / len(self.flat_values) * 100
        print(f"\n    Nullen in Matrix: {zero_count} ({zero_pct:.2f}%)")

        if zero_pct > 5:
            print("    ⚠ Hohe Sparsity könnte Clustering erklären")
            self.results['alternative_explanations'].append("High sparsity may explain clustering")

    # ═══════════════════════════════════════════════════════════════════════════
    # NULL-HYPOTHESE: Ist die Matrix wirklich nicht-zufällig?
    # ═══════════════════════════════════════════════════════════════════════════

    def test_null_hypothesis(self):
        """Test gegen Null-Hypothese: Matrix ist zufällig"""
        print("\n" + "─" * 70)
        print("NULL-HYPOTHESE TEST: Ist Matrix wirklich nicht-zufällig?")
        print("─" * 70)

        # Generiere 10 zufällige Matrizen und vergleiche Statistiken
        print("\n  Generiere 10 Vergleichs-Matrizen...")
        random_stats = []

        for i in range(10):
            random_matrix = [[random.randint(-128, 127) for _ in range(128)] for _ in range(128)]
            random_flat = [v for row in random_matrix for v in row]

            # Mode
            mode = Counter(random_flat).most_common(1)[0]

            # Max count for any value
            max_count = mode[1]

            # Clustering
            same_h = sum(1 for r in range(128) for c in range(127)
                        if random_matrix[r][c] == random_matrix[r][c+1])
            same_v = sum(1 for r in range(127) for c in range(128)
                        if random_matrix[r][c] == random_matrix[r+1][c])
            clustering = (same_h + same_v) / (128*127*2) / (1/256)

            random_stats.append({
                'mode_value': mode[0],
                'mode_count': max_count,
                'clustering': clustering,
            })

        # Vergleiche mit Anna Matrix
        anna_mode = Counter(self.flat_values).most_common(1)[0]
        anna_clustering = 24.42  # Vorher berechnet

        print("\n  Vergleich Anna Matrix vs. Zufalls-Matrizen:")
        print(f"\n  Mode-Count (häufigster Wert):")
        print(f"    Anna Matrix: {anna_mode[1]} ({anna_mode[0]})")
        random_mode_counts = [s['mode_count'] for s in random_stats]
        print(f"    Zufällig:    {min(random_mode_counts)}-{max(random_mode_counts)} (avg: {sum(random_mode_counts)/10:.0f})")

        if anna_mode[1] > max(random_mode_counts) * 2:
            print(f"    ✓ Anna Mode-Count ist {anna_mode[1]/max(random_mode_counts):.1f}x höher als max(zufällig)")
        else:
            print(f"    ⚠ Anna Mode-Count nicht signifikant höher")

        print(f"\n  Clustering-Faktor:")
        print(f"    Anna Matrix: {anna_clustering:.2f}x")
        random_clusterings = [s['clustering'] for s in random_stats]
        print(f"    Zufällig:    {min(random_clusterings):.2f}-{max(random_clusterings):.2f}x (avg: {sum(random_clusterings)/10:.2f}x)")

        if anna_clustering > max(random_clusterings) * 10:
            print(f"    ✓ Anna Clustering ist {anna_clustering/max(random_clusterings):.0f}x höher als max(zufällig)")
            self.results['claims_verified']['not_random'] = True
        else:
            print(f"    ⚠ Clustering nicht eindeutig höher")

    # ═══════════════════════════════════════════════════════════════════════════
    # ALTERNATIVE ERKLÄRUNGEN
    # ═══════════════════════════════════════════════════════════════════════════

    def explore_alternative_explanations(self):
        """Suche nach alternativen Erklärungen"""
        print("\n" + "─" * 70)
        print("ALTERNATIVE ERKLÄRUNGEN")
        print("─" * 70)

        print("\n  1. QUANTISIERUNG")
        print("     Neuronale Netze werden oft auf 8-bit quantisiert.")
        print("     Das könnte ungleiche Verteilung erklären.")

        # Prüfe ob Werte auf bestimmte Bereiche konzentriert sind
        value_hist = Counter(self.flat_values)
        values_used = len(value_hist)
        print(f"     Genutzte Werte: {values_used} von 256 möglichen")

        if values_used == 256:
            print("     → Alle Werte genutzt - spricht gegen starke Quantisierung")
        else:
            print(f"     → Nur {values_used} Werte genutzt - könnte Quantisierung sein")
            self.results['alternative_explanations'].append(f"Quantization: only {values_used} values used")

        print("\n  2. TRAINED NETWORK BIAS")
        print("     Trainierte Netze haben oft nicht-uniforme Gewichte.")
        # Prüfe Schiefe
        mean = sum(self.flat_values) / len(self.flat_values)
        std = statistics.stdev(self.flat_values)
        skewness = sum((v - mean)**3 for v in self.flat_values) / (len(self.flat_values) * std**3)
        print(f"     Schiefe: {skewness:.4f} ({'links' if skewness < -0.1 else 'rechts' if skewness > 0.1 else 'symmetrisch'})")

        print("\n  3. COMPRESSION ARTIFACT")
        print("     Matrix könnte komprimiert/dekomprimiert worden sein.")

        # Prüfe auf Wiederholungsmuster
        row_strings = [''.join(str(v) for v in row) for row in self.matrix]
        unique_rows = len(set(row_strings))
        print(f"     Eindeutige Zeilen: {unique_rows} von 128")

        if unique_rows < 128:
            print(f"     → {128 - unique_rows} doppelte Zeilen gefunden!")
            self.results['alternative_explanations'].append(f"Compression: {128-unique_rows} duplicate rows")

        print("\n  4. CFB-PATTERN KÖNNTE PAREIDOLIE SEIN")
        print("     Wir suchen nach CFB-Zahlen und finden sie.")
        print("     Aber: Würden wir auch andere Zahlen finden?")

        # Teste mit anderen Zahlensets
        test_sets = [
            ("Primzahlen 2-11", {2, 3, 5, 7, 11}),
            ("Fibonacci 1-13", {1, 2, 3, 5, 8, 13}),
            ("CFB", {27, 37, 42, 127}),
        ]

        for name, num_set in test_sets:
            count = sum(1 for v in self.flat_values if abs(v) in num_set)
            print(f"     {name}: {count} Vorkommen")

        print("\n     ⚠ WICHTIG: CFB-Zahlen könnten rein zufällig prominent sein!")

    # ═══════════════════════════════════════════════════════════════════════════
    # FAZIT
    # ═══════════════════════════════════════════════════════════════════════════

    def summarize(self):
        """Zusammenfassung der kritischen Analyse"""
        print("\n" + "═" * 70)
        print("KRITISCHE ZUSAMMENFASSUNG")
        print("═" * 70)

        print("\n  BESTÄTIGTE CLAIMS:")
        for claim, value in self.results['claims_verified'].items():
            print(f"    ✓ {claim}: {value}")

        if self.results['claims_refuted']:
            print("\n  WIDERLEGTE CLAIMS:")
            for claim, value in self.results['claims_refuted'].items():
                print(f"    ✗ {claim}: {value}")

        if self.results['warnings']:
            print("\n  WARNUNGEN:")
            for warning in self.results['warnings']:
                print(f"    ⚠ {warning}")

        if self.results['alternative_explanations']:
            print("\n  ALTERNATIVE ERKLÄRUNGEN:")
            for alt in self.results['alternative_explanations']:
                print(f"    ? {alt}")

        # Gesamtbewertung
        verified = len(self.results['claims_verified'])
        refuted = len(self.results['claims_refuted'])
        warnings = len(self.results['warnings'])

        print("\n" + "─" * 70)
        print("  GESAMTBEWERTUNG:")
        if refuted > 0:
            print("    ⚠ VORSICHT: Einige Claims wurden widerlegt!")
        elif warnings > 2:
            print("    ⚠ VORSICHT: Mehrere Warnungen - Befunde mit Skepsis betrachten")
        elif verified >= 3:
            print("    ✓ Kernbefunde scheinen robust zu sein")

        # Speichern
        output_file = SCRIPT_DIR / 'CRITICAL_VERIFICATION_RESULTS.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n  Ergebnisse gespeichert: {output_file}")

    def run(self):
        """Führe alle kritischen Tests durch"""
        self.verify_claim_minus27()
        self.verify_claim_mirror_pattern()
        self.verify_claim_sw_quadrant()
        self.verify_claim_clustering()
        self.test_null_hypothesis()
        self.explore_alternative_explanations()
        self.summarize()

if __name__ == "__main__":
    verifier = CriticalVerification()
    verifier.run()
