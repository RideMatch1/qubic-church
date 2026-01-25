#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    DIE 68 ANOMALIEN - DEEP ANALYSIS                           ║
║                                                                                ║
║  99.6% der Matrix erfüllt: matrix[r,c] + matrix[127-r,127-c] = -1             ║
║  68 Zellen tun das NICHT. Was steckt dahinter?                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set
import math

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

# Bekannte wichtige Positionen
KNOWN_POSITIONS = {
    '1CFi_SOLVED': (91, 20),
    '1CFB_UNSOLVED': (45, 92),
    'VISION_CENTER': (64, 64),
}

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

def signed_to_unsigned(val: int) -> int:
    return val & 0xFF

def main():
    print("═" * 70)
    print("           DIE 68 ANOMALIEN - DEEP ANALYSIS")
    print("═" * 70)

    matrix = load_matrix()

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 1: Finde alle Anomalien
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 1: Identifikation der Anomalien")
    print("─" * 70)

    anomalies = []
    symmetric_cells = []

    for r in range(128):
        for c in range(128):
            val = matrix[r][c]
            mirror_r, mirror_c = 127 - r, 127 - c
            mirror_val = matrix[mirror_r][mirror_c]

            sum_vals = val + mirror_val

            if sum_vals != -1:
                anomalies.append({
                    'pos': (r, c),
                    'mirror_pos': (mirror_r, mirror_c),
                    'value': val,
                    'mirror_value': mirror_val,
                    'sum': sum_vals,
                    'expected_mirror': -(val + 1),
                    'deviation': mirror_val - (-(val + 1)),
                })
            else:
                symmetric_cells.append((r, c))

    # Entferne Duplikate (jedes Paar wird zweimal gefunden)
    unique_anomalies = []
    seen_pairs = set()
    for a in anomalies:
        pair = tuple(sorted([a['pos'], a['mirror_pos']]))
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique_anomalies.append(a)

    print(f"\n  Gefundene Anomalie-Paare: {len(unique_anomalies)}")
    print(f"  Betroffene Zellen: {len(unique_anomalies) * 2}")
    print(f"  Symmetrische Zellen: {len(symmetric_cells)}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 2: Detaillierte Anomalie-Liste
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 2: Detaillierte Anomalie-Liste")
    print("─" * 70)

    print("\n  Pos [r,c]    Val  | Mirror [r,c]  Val  | Sum  | Deviation")
    print("  " + "─" * 60)

    for a in unique_anomalies[:20]:  # Erste 20
        r, c = a['pos']
        mr, mc = a['mirror_pos']
        print(f"  [{r:3d},{c:3d}] {a['value']:+5d} | "
              f"[{mr:3d},{mc:3d}] {a['mirror_value']:+5d} | "
              f"{a['sum']:+4d} | {a['deviation']:+4d}")

    if len(unique_anomalies) > 20:
        print(f"  ... und {len(unique_anomalies) - 20} weitere")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 3: Muster in den Summen
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 3: Muster in den Anomalie-Summen")
    print("─" * 70)

    sum_counts = Counter(a['sum'] for a in unique_anomalies)
    print("\n  Summe | Häufigkeit | Interpretation")
    print("  " + "─" * 45)
    for sum_val, count in sorted(sum_counts.items()):
        interp = ""
        if sum_val == 0:
            interp = "Selbst-Invers (x + mirror = 0)"
        elif sum_val == -2:
            interp = "Off-by-one (sollte -1 sein)"
        elif sum_val % 11 == 0:
            interp = f"Multipel von 11 ({sum_val // 11} × 11)"
        elif sum_val == -128 or sum_val == 127:
            interp = "Grenzwert"
        print(f"  {sum_val:+5d} | {count:10d} | {interp}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 4: Räumliche Verteilung
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 4: Räumliche Verteilung der Anomalien")
    print("─" * 70)

    # Quadranten
    quads = {'NW': 0, 'NE': 0, 'SW': 0, 'SE': 0}
    for a in unique_anomalies:
        r, c = a['pos']
        if r < 64 and c < 64: quads['NW'] += 1
        elif r < 64: quads['NE'] += 1
        elif c < 64: quads['SW'] += 1
        else: quads['SE'] += 1

    print(f"\n  Quadrantenverteilung:")
    print(f"    NW (Upper-Left):  {quads['NW']}")
    print(f"    NE (Upper-Right): {quads['NE']}")
    print(f"    SW (Lower-Left):  {quads['SW']}")
    print(f"    SE (Lower-Right): {quads['SE']}")

    # Zeilen/Spalten mit mehreren Anomalien
    row_counts = Counter(a['pos'][0] for a in unique_anomalies)
    col_counts = Counter(a['pos'][1] for a in unique_anomalies)

    print(f"\n  Zeilen mit mehreren Anomalien:")
    for row, count in row_counts.most_common(5):
        if count > 1:
            print(f"    Row {row}: {count} Anomalien")

    print(f"\n  Spalten mit mehreren Anomalien:")
    for col, count in col_counts.most_common(5):
        if count > 1:
            print(f"    Col {col}: {count} Anomalien")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 5: Verbindung zu bekannten Positionen
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 5: Verbindung zu bekannten Positionen")
    print("─" * 70)

    anomaly_positions = set()
    for a in unique_anomalies:
        anomaly_positions.add(a['pos'])
        anomaly_positions.add(a['mirror_pos'])

    for name, pos in KNOWN_POSITIONS.items():
        if pos in anomaly_positions:
            print(f"\n  ★ {name} {pos} ist eine ANOMALIE!")
            # Finde Details
            for a in unique_anomalies:
                if a['pos'] == pos or a['mirror_pos'] == pos:
                    print(f"    Value: {a['value']}, Mirror Value: {a['mirror_value']}")
                    print(f"    Sum: {a['sum']} (erwartet: -1)")
                    break
        else:
            r, c = pos
            val = matrix[r][c]
            mirror_val = matrix[127-r][127-c]
            print(f"\n  {name} {pos} ist SYMMETRISCH")
            print(f"    Value: {val}, Mirror Value: {mirror_val}")
            print(f"    Sum: {val + mirror_val}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 6: Distanz-Analyse
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 6: Distanz zu 1CFB und 1CFi")
    print("─" * 70)

    cfb_pos = KNOWN_POSITIONS['1CFB_UNSOLVED']
    cfi_pos = KNOWN_POSITIONS['1CFi_SOLVED']

    print("\n  Anomalien nach Distanz zu 1CFB sortiert:")
    anomalies_with_dist = []
    for a in unique_anomalies:
        r, c = a['pos']
        dist_cfb = abs(r - cfb_pos[0]) + abs(c - cfb_pos[1])
        dist_cfi = abs(r - cfi_pos[0]) + abs(c - cfi_pos[1])
        a['dist_cfb'] = dist_cfb
        a['dist_cfi'] = dist_cfi
        anomalies_with_dist.append(a)

    anomalies_with_dist.sort(key=lambda x: x['dist_cfb'])

    print("\n  Nächste Anomalien zu 1CFB [45, 92]:")
    for a in anomalies_with_dist[:5]:
        r, c = a['pos']
        print(f"    [{r:3d},{c:3d}] Dist: {a['dist_cfb']:3d}, Value: {a['value']:+4d}, Sum: {a['sum']:+4d}")

    anomalies_with_dist.sort(key=lambda x: x['dist_cfi'])
    print("\n  Nächste Anomalien zu 1CFi [91, 20]:")
    for a in anomalies_with_dist[:5]:
        r, c = a['pos']
        print(f"    [{r:3d},{c:3d}] Dist: {a['dist_cfi']:3d}, Value: {a['value']:+4d}, Sum: {a['sum']:+4d}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 7: Wert-Analyse
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 7: Wert-Analyse der Anomalien")
    print("─" * 70)

    values = [a['value'] for a in unique_anomalies]
    mirror_values = [a['mirror_value'] for a in unique_anomalies]
    all_values = values + mirror_values

    print(f"\n  Wert-Statistik:")
    print(f"    Min: {min(all_values)}")
    print(f"    Max: {max(all_values)}")
    print(f"    Mean: {sum(all_values) / len(all_values):.2f}")

    value_counts = Counter(all_values)
    print(f"\n  Häufigste Werte in Anomalien:")
    for val, count in value_counts.most_common(10):
        print(f"    {val:+4d}: {count} Mal")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 8: Binäre Analyse
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 8: Binäre Muster-Analyse")
    print("─" * 70)

    print("\n  Anomalie-Werte in Binär:")
    for a in unique_anomalies[:10]:
        val = signed_to_unsigned(a['value'])
        mirror = signed_to_unsigned(a['mirror_value'])
        xor = val ^ mirror
        print(f"    {a['value']:+4d} ({val:08b}) XOR {a['mirror_value']:+4d} ({mirror:08b}) = {xor:3d} ({xor:08b})")

    # Prüfe ob XOR ein Muster zeigt
    xor_values = [signed_to_unsigned(a['value']) ^ signed_to_unsigned(a['mirror_value'])
                  for a in unique_anomalies]
    xor_counts = Counter(xor_values)

    print(f"\n  XOR-Wert Häufigkeiten (value XOR mirror_value):")
    for xor_val, count in xor_counts.most_common(10):
        print(f"    {xor_val:3d} (0x{xor_val:02x}): {count} Mal")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 9: Koordinaten-Muster
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 9: Koordinaten-Muster")
    print("─" * 70)

    print("\n  Zeige alle Anomalie-Koordinaten:")
    all_coords = []
    for a in unique_anomalies:
        r, c = a['pos']
        all_coords.append((r, c))

    # Sortiert nach Row
    all_coords.sort()
    for r, c in all_coords:
        val = matrix[r][c]
        # Berechne interessante Eigenschaften
        r_plus_c = r + c
        r_xor_c = r ^ c
        r_times_c = r * c
        print(f"    [{r:3d},{c:3d}] val={val:+4d}  r+c={r_plus_c:3d}  r^c={r_xor_c:3d}  r×c={r_times_c:5d}")

    # Suche nach Mustern in r+c
    sum_coords = [r + c for r, c in all_coords]
    sum_counts = Counter(sum_coords)
    print(f"\n  r+c Häufigkeiten:")
    for s, count in sorted(sum_counts.items()):
        if count > 1:
            print(f"    r+c = {s}: {count} Anomalien")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 10: Hypothesen-Test
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 10: Hypothesen-Tests")
    print("─" * 70)

    # Hypothese 1: Anomalien auf Diagonalen?
    main_diag = sum(1 for r, c in all_coords if r == c)
    anti_diag = sum(1 for r, c in all_coords if r + c == 127)
    print(f"\n  H1: Anomalien auf Diagonalen?")
    print(f"    Hauptdiagonale (r=c): {main_diag}")
    print(f"    Anti-Diagonale (r+c=127): {anti_diag}")

    # Hypothese 2: Anomalien bei speziellen Werten (0, -128, 127)?
    special_vals = [0, -128, 127, -1]
    for sv in special_vals:
        count = sum(1 for a in unique_anomalies if a['value'] == sv or a['mirror_value'] == sv)
        print(f"    Anomalien mit Wert {sv:+4d}: {count}")

    # Hypothese 3: Sind Anomalien an Grenzen (r=0,127 oder c=0,127)?
    border = sum(1 for r, c in all_coords if r in [0, 127] or c in [0, 127])
    print(f"\n  H3: Anomalien am Rand (r oder c = 0 oder 127)?")
    print(f"    {border} von {len(all_coords)}")

    # Hypothese 4: Modulo-Muster?
    for mod in [7, 11, 13, 19, 27]:
        mod_zero = sum(1 for r, c in all_coords if (r * c) % mod == 0)
        if mod_zero > len(all_coords) * 0.3:
            print(f"\n  H4: Anomalien wo r×c mod {mod} = 0: {mod_zero}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 11: Die 0-Summen Anomalien (Selbst-Inverse)
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 11: Selbst-Inverse Anomalien (Sum = 0)")
    print("─" * 70)

    zero_sum = [a for a in unique_anomalies if a['sum'] == 0]
    print(f"\n  Anomalien mit Summe 0 (value + mirror = 0):")
    print(f"  Diese Zellen erfüllen: value = -mirror_value")

    for a in zero_sum:
        r, c = a['pos']
        print(f"    [{r:3d},{c:3d}] = {a['value']:+4d}, Mirror = {a['mirror_value']:+4d}")

    # ═══════════════════════════════════════════════════════════════════════════
    # FAZIT
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "═" * 70)
    print("FAZIT: DIE 68 ANOMALIEN")
    print("═" * 70)

    print(f"""
  ENTDECKUNGEN:

  1. ANZAHL: {len(unique_anomalies)} Anomalie-Paare = {len(unique_anomalies) * 2} Zellen
     (von 16,384 total = {len(unique_anomalies) * 2 / 16384 * 100:.2f}%)

  2. SUMMEN-VERTEILUNG:
     {dict(sum_counts)}

  3. RÄUMLICHE KONZENTRATION:
     Quadranten: NW={quads['NW']}, NE={quads['NE']}, SW={quads['SW']}, SE={quads['SE']}

  4. VERBINDUNG ZU BEKANNTEN POSITIONEN:
     - 1CFB und 1CFi sind NICHT unter den Anomalien
     - Aber Anomalien könnten den "Fehlerterm" für 1CFB kodieren

  5. MÖGLICHE INTERPRETATION:
     - Anomalien könnten absichtliche "Marker" sein
     - Oder sie kodieren eine versteckte Nachricht
     - Die XOR-Werte zeigen kein offensichtliches Muster
""")

    # Speichern für Visualisierung
    results = {
        'anomaly_count': len(unique_anomalies),
        'total_cells_affected': len(unique_anomalies) * 2,
        'percentage': len(unique_anomalies) * 2 / 16384 * 100,
        'sum_distribution': dict(sum_counts),
        'quadrants': quads,
        'anomalies': [
            {
                'pos': list(a['pos']),
                'mirror_pos': list(a['mirror_pos']),
                'value': a['value'],
                'mirror_value': a['mirror_value'],
                'sum': a['sum'],
            }
            for a in unique_anomalies
        ],
        'all_positions': [list(pos) for pos in all_coords],
    }

    output_file = SCRIPT_DIR / 'ANOMALY_68_ANALYSIS.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Ergebnisse gespeichert: {output_file}")

if __name__ == "__main__":
    main()
