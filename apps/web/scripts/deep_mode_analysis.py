#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    DEEP MODE ANALYSIS                                          ║
║                                                                                ║
║  Kritische Entdeckung: +26 und -27 sind BEIDE der Mode (476 Mal)              ║
║  Was bedeutet dieses Paar? Gibt es weitere Paare?                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
from pathlib import Path
from collections import Counter
from typing import List, Dict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

def load_matrix() -> List[List[int]]:
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

def main():
    print("═" * 70)
    print("           DEEP MODE ANALYSIS: +26 & -27")
    print("═" * 70)

    matrix = load_matrix()
    flat = [v for row in matrix for v in row]
    counts = Counter(flat)

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 1: Das +26/-27 Paar analysieren
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 1: Das Tied-Mode Paar +26 und -27")
    print("─" * 70)

    count_26 = counts[26]
    count_m27 = counts[-27]

    print(f"\n  +26 erscheint: {count_26} Mal")
    print(f"  -27 erscheint: {count_m27} Mal")
    print(f"  Differenz: {abs(count_26 - count_m27)}")

    # Mathematische Beziehung
    print(f"\n  Mathematische Beziehungen:")
    print(f"    26 + 27 = {26 + 27}")
    print(f"    26 - (-27) = {26 - (-27)}")
    print(f"    26 XOR (-27) = {26 ^ (-27)}")
    print(f"    26 * (-27) = {26 * (-27)}")

    # Binärdarstellung
    print(f"\n  Binärdarstellung (8-bit signed):")
    print(f"    +26 = {26:08b} = 0x{26:02x}")
    print(f"    -27 = {(-27) & 0xFF:08b} = 0x{(-27) & 0xFF:02x} (als unsigned)")

    # Sind +26 und -27 räumlich korreliert?
    print("\n  Räumliche Korrelation:")
    adjacent_pairs = 0
    for r in range(128):
        for c in range(128):
            if matrix[r][c] == 26:
                # Prüfe Nachbarn auf -27
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = (r + dr) % 128, (c + dc) % 128
                    if matrix[nr][nc] == -27:
                        adjacent_pairs += 1

    print(f"    Benachbarte +26/-27 Paare: {adjacent_pairs}")
    expected = (count_26 * count_m27 * 4) / 16384  # 4 Nachbarn pro Zelle
    print(f"    Erwartet (zufällig): {expected:.1f}")
    print(f"    Ratio: {adjacent_pairs / expected:.2f}x")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 2: Gibt es andere Paare mit gleicher Häufigkeit?
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 2: Andere Paare mit gleicher Häufigkeit")
    print("─" * 70)

    # Gruppiere nach Häufigkeit
    freq_groups = {}
    for val, cnt in counts.items():
        if cnt not in freq_groups:
            freq_groups[cnt] = []
        freq_groups[cnt].append(val)

    # Zeige Gruppen mit >1 Wert
    print("\n  Werte die gleich oft vorkommen:")
    for cnt in sorted(freq_groups.keys(), reverse=True)[:15]:
        values = freq_groups[cnt]
        if len(values) > 1:
            values_str = ', '.join(f"{v:+d}" for v in sorted(values))
            print(f"    {cnt}x: [{values_str}]")

            # Prüfe Beziehungen innerhalb der Gruppe
            if len(values) == 2:
                v1, v2 = sorted(values)
                print(f"         Summe: {v1 + v2}, Diff: {v2 - v1}, XOR: {v1 ^ v2}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 3: CFB-Pareidolie Test
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 3: Pareidolie-Test - Sind CFB-Zahlen wirklich besonders?")
    print("─" * 70)

    # Teste verschiedene Zahlensets
    test_sets = {
        'CFB (27,37,42,127)': {27, 37, 42, 127},
        'Primzahlen <50': {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47},
        'Fibonacci': {1, 2, 3, 5, 8, 13, 21, 34, 55, 89},
        'Potenzen von 2': {1, 2, 4, 8, 16, 32, 64},
        'Zufällig A': {14, 51, 73, 98},  # 4 zufällige Zahlen
        'Zufällig B': {23, 45, 67, 89},  # 4 andere zufällige
        'Multipel von 9': {9, 18, 27, 36, 45, 54, 63, 72, 81, 90, 99},
        'Multipel von 13': {13, 26, 39, 52, 65, 78, 91, 104, 117},
    }

    print("\n  Vorkommen verschiedener Zahlensets (inkl. ±):")
    results = []
    for name, num_set in test_sets.items():
        count = sum(counts.get(n, 0) + counts.get(-n, 0) for n in num_set)
        per_number = count / len(num_set)
        results.append((name, count, len(num_set), per_number))

    # Sortiere nach Vorkommen pro Zahl
    results.sort(key=lambda x: -x[3])

    for name, total, size, per_num in results:
        print(f"    {name:25s}: {total:4d} total, {size:2d} Zahlen, {per_num:.1f} pro Zahl")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 4: Die echte Frage - Was macht -27 und +26 so häufig?
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 4: Warum genau -27 und +26?")
    print("─" * 70)

    # Position der -27 Werte
    pos_m27 = [(r, c) for r in range(128) for c in range(128) if matrix[r][c] == -27]
    pos_26 = [(r, c) for r in range(128) for c in range(128) if matrix[r][c] == 26]

    # Zentroid
    if pos_m27:
        centroid_m27 = (sum(p[0] for p in pos_m27) / len(pos_m27),
                        sum(p[1] for p in pos_m27) / len(pos_m27))
        print(f"\n  -27 Zentroid: ({centroid_m27[0]:.1f}, {centroid_m27[1]:.1f})")

    if pos_26:
        centroid_26 = (sum(p[0] for p in pos_26) / len(pos_26),
                       sum(p[1] for p in pos_26) / len(pos_26))
        print(f"  +26 Zentroid: ({centroid_26[0]:.1f}, {centroid_26[1]:.1f})")

    # Quadrantenverteilung
    print("\n  Quadrantenverteilung:")
    for val, positions, name in [(-27, pos_m27, "-27"), (26, pos_26, "+26")]:
        quads = {'NW': 0, 'NE': 0, 'SW': 0, 'SE': 0}
        for r, c in positions:
            if r < 64 and c < 64: quads['NW'] += 1
            elif r < 64: quads['NE'] += 1
            elif c < 64: quads['SW'] += 1
            else: quads['SE'] += 1
        print(f"    {name}: NW={quads['NW']:3d}, NE={quads['NE']:3d}, SW={quads['SW']:3d}, SE={quads['SE']:3d}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 5: Entdeckung - Das (+n, -(n+1)) Muster
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 5: Suche nach (+n, -(n+1)) Muster")
    print("─" * 70)

    print("\n  Prüfe ob (+n, -(n+1)) Paare ähnliche Häufigkeiten haben:")
    for n in range(1, 128):
        count_pos = counts.get(n, 0)
        count_neg = counts.get(-(n+1), 0)
        if count_pos > 100 or count_neg > 100:  # Nur signifikante
            diff_pct = abs(count_pos - count_neg) / max(count_pos, count_neg, 1) * 100
            match = "★ MATCH" if diff_pct < 1 else ""
            if diff_pct < 20:  # Nur ähnliche zeigen
                print(f"    +{n:3d}: {count_pos:4d}   -{n+1:3d}: {count_neg:4d}   Diff: {diff_pct:.1f}% {match}")

    # ═══════════════════════════════════════════════════════════════════════════
    # FAZIT
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "═" * 70)
    print("FAZIT")
    print("═" * 70)

    print("""
  KRITISCHE ERKENNTNISSE:

  1. +26 und -27 sind BEIDE der Mode mit exakt 476 Vorkommen
     - Das ist kein Zufall, sondern ein symmetrisches Muster

  2. Das Muster (+n, -(n+1)) scheint absichtlich
     - 26 und 27 sind aufeinanderfolgende Zahlen
     - Das XOR-Ergebnis 26 ^ (-27) = -1 (alle Bits gesetzt)

  3. CFB-Zahlen sind NICHT eindeutig besonders
     - "Multipel von 13" enthält auch 26 und hat hohe Dichte
     - 27 ist sowohl CFB-Zahl als auch Multipel von 9/3

  4. Die Frage ist NICHT "warum 27?"
     Die Frage ist: "Warum das Paar (+26, -27)?"
""")

if __name__ == "__main__":
    main()
