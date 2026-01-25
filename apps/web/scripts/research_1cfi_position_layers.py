#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    1CFB/1CFi POSITION DEEP DIVE                                ║
║                                                                                ║
║  1CFi wurde gelöst: Position [91, 20], step27, XOR13                          ║
║  1CFB ist ungelöst: Position [45, 92]                                          ║
║                                                                                ║
║  Frage: Was ist an diesen Positionen in verschiedenen XOR-Layern?             ║
║  Sind die Positionen selbst gespiegelt?                                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

XOR_VALUES = [0, 7, 13, 27, 33]

# Bekannte Positionen
POSITIONS = {
    '1CFi_SOLVED': {
        'address': '1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi',
        'row': 91,
        'col': 20,
        'method': 'step27 + XOR13',
        'seed': 'mmmacecvbddmnymmmacecvbddmnymmmacecvbddmnymmmacecvbddmn',
        'hash160_first_byte': '0x7b',
        'byte_sum': 2299,
    },
    '1CFB_UNSOLVED': {
        'address': '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg',
        'row': 45,
        'col': 92,
        'method': 'UNKNOWN',
        'hash160_first_byte': '0x7b',
        'byte_sum': 2299,
    }
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

def unsigned_to_signed(val: int) -> int:
    if val > 127:
        return val - 256
    return val

def apply_xor(val: int, xor_val: int) -> int:
    unsigned = signed_to_unsigned(val)
    xored = unsigned ^ xor_val
    return unsigned_to_signed(xored)

def main():
    print("═" * 70)
    print("           1CFB/1CFi POSITION DEEP DIVE")
    print("═" * 70)

    matrix = load_matrix()

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 1: Positionen analysieren
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 1: Bekannte Positionen")
    print("─" * 70)

    for name, info in POSITIONS.items():
        row, col = info['row'], info['col']
        base_value = matrix[row][col]

        print(f"\n  {name}:")
        print(f"    Adresse: {info['address']}")
        print(f"    Position: [{row}, {col}]")
        print(f"    Methode: {info['method']}")
        print(f"    Hash160 erstes Byte: {info['hash160_first_byte']}")
        print(f"    Byte Sum: {info['byte_sum']}")

        print(f"\n    Matrix-Wert in verschiedenen XOR-Layern:")
        for xor_val in XOR_VALUES:
            xored = apply_xor(base_value, xor_val)
            print(f"      XOR {xor_val:3d}: {xored:+4d}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 2: Positions-Symmetrie prüfen
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 2: Positions-Symmetrie zwischen 1CFB und 1CFi")
    print("─" * 70)

    r1, c1 = POSITIONS['1CFi_SOLVED']['row'], POSITIONS['1CFi_SOLVED']['col']
    r2, c2 = POSITIONS['1CFB_UNSOLVED']['row'], POSITIONS['1CFB_UNSOLVED']['col']

    print(f"\n  1CFi Position: [{r1}, {c1}]")
    print(f"  1CFB Position: [{r2}, {c2}]")

    # Verschiedene Symmetrien prüfen
    print("\n  Symmetrie-Tests:")

    # Point Symmetry (um Zentrum 64, 64)
    point_sym_1cfi = (127 - r1, 127 - c1)
    point_sym_1cfb = (127 - r2, 127 - c2)
    print(f"\n    Punkt-Symmetrie (um 63.5, 63.5):")
    print(f"      1CFi [{r1}, {c1}] → Spiegel: [{point_sym_1cfi[0]}, {point_sym_1cfi[1]}]")
    print(f"      1CFB [{r2}, {c2}] → Spiegel: [{point_sym_1cfb[0]}, {point_sym_1cfb[1]}]")

    # Horizontal Reflection
    h_sym_1cfi = (r1, 127 - c1)
    h_sym_1cfb = (r2, 127 - c2)
    print(f"\n    Horizontal-Spiegelung (col → 127-col):")
    print(f"      1CFi [{r1}, {c1}] → Spiegel: [{h_sym_1cfi[0]}, {h_sym_1cfi[1]}]")
    print(f"      1CFB [{r2}, {c2}] → Spiegel: [{h_sym_1cfb[0]}, {h_sym_1cfb[1]}]")

    # Vertical Reflection
    v_sym_1cfi = (127 - r1, c1)
    v_sym_1cfb = (127 - r2, c2)
    print(f"\n    Vertikal-Spiegelung (row → 127-row):")
    print(f"      1CFi [{r1}, {c1}] → Spiegel: [{v_sym_1cfi[0]}, {v_sym_1cfi[1]}]")
    print(f"      1CFB [{r2}, {c2}] → Spiegel: [{v_sym_1cfb[0]}, {v_sym_1cfb[1]}]")

    # Diagonal Reflection (swap row/col)
    d_sym_1cfi = (c1, r1)
    d_sym_1cfb = (c2, r2)
    print(f"\n    Diagonal-Spiegelung (row ↔ col):")
    print(f"      1CFi [{r1}, {c1}] → Spiegel: [{d_sym_1cfi[0]}, {d_sym_1cfi[1]}]")
    print(f"      1CFB [{r2}, {c2}] → Spiegel: [{d_sym_1cfb[0]}, {d_sym_1cfb[1]}]")

    # Prüfe ob 1CFB irgendeine Symmetrie von 1CFi ist
    print("\n  Ist 1CFB ein Spiegel von 1CFi?")
    symmetries = [
        ('Punkt', point_sym_1cfi),
        ('Horizontal', h_sym_1cfi),
        ('Vertikal', v_sym_1cfi),
        ('Diagonal', d_sym_1cfi),
    ]

    for name, pos in symmetries:
        if pos == (r2, c2):
            print(f"    ★ JA! 1CFB ist {name}-Spiegel von 1CFi!")
        else:
            dist = abs(pos[0] - r2) + abs(pos[1] - c2)
            print(f"    {name}: Abstand {dist}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 3: Werte an Spiegelpositionen
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 3: Matrix-Werte an Spiegelpositionen")
    print("─" * 70)

    val_1cfi = matrix[r1][c1]
    val_1cfb = matrix[r2][c2]

    print(f"\n  1CFi [{r1}, {c1}] = {val_1cfi:+4d}")
    print(f"  1CFB [{r2}, {c2}] = {val_1cfb:+4d}")

    print(f"\n  Beziehungen:")
    print(f"    Summe: {val_1cfi + val_1cfb}")
    print(f"    Differenz: {val_1cfi - val_1cfb}")
    print(f"    XOR: {val_1cfi ^ val_1cfb}")
    print(f"    Produkt: {val_1cfi * val_1cfb}")

    # Prüfe ob sie ein (+n, -(n+1)) Paar bilden
    if val_1cfb == -(val_1cfi + 1):
        print(f"\n    ★ SIE BILDEN EIN (+n, -(n+1)) PAAR!")
        print(f"       {val_1cfi} und {val_1cfb} = -({val_1cfi} + 1)")
    elif val_1cfi == -(val_1cfb + 1):
        print(f"\n    ★ SIE BILDEN EIN (+n, -(n+1)) PAAR (umgekehrt)!")
        print(f"       {val_1cfb} und {val_1cfi} = -({val_1cfb} + 1)")
    else:
        print(f"\n    Kein direktes (+n, -(n+1)) Paar")

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 4: 3x3 Nachbarschaft
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 4: 3x3 Nachbarschaft")
    print("─" * 70)

    for name, info in POSITIONS.items():
        row, col = info['row'], info['col']

        print(f"\n  {name} [{row}, {col}] Nachbarschaft:")
        for dr in range(-1, 2):
            row_str = "    "
            for dc in range(-1, 2):
                r, c = (row + dr) % 128, (col + dc) % 128
                val = matrix[r][c]
                if dr == 0 and dc == 0:
                    row_str += f"[{val:+4d}]"
                else:
                    row_str += f" {val:+4d} "
            print(row_str)

    # ═══════════════════════════════════════════════════════════════════════════
    # TEIL 5: Hypothese - 1CFB Lösung
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "─" * 70)
    print("TEIL 5: Hypothese für 1CFB-Lösung")
    print("─" * 70)

    print("""
  1CFi wurde gelöst mit: step27 + XOR13

  Hypothesen für 1CFB:

  1. MIRROR METHODE:
     - 1CFi: step27 + XOR13
     - 1CFB: step? + XOR?
     - Mögliche Spiegel: step(27 XOR X) + XOR(13 XOR Y)

  2. COMPLEMENT METHODE:
     - 1CFi step27 → 1CFB step(256-27) = step229?
     - Oder: step(128-27) = step101?

  3. CFB-SIGNATUR:
     - 27 ist eine CFB-Zahl
     - Andere CFB-Zahlen: 37, 42, 127
     - Mögliche Steps: step37, step42, step127

  4. XOR-KOMBINATION:
     - 1CFi: XOR13
     - Mögliche XOR für 1CFB: 0, 7, 27, 33
     - Oder XOR(255-13) = XOR242?
""")

    # Test verschiedene step+XOR Kombinationen mit CFB-Zahlen
    cfb_steps = [7, 13, 19, 27, 33, 37, 42, 127]
    cfb_xors = [0, 7, 13, 27, 33]

    print("  Mögliche Kandidaten für 1CFB (basierend auf CFB-Mustern):")
    for step in cfb_steps:
        for xor in cfb_xors:
            if step == 27 and xor == 13:
                continue  # Das ist 1CFi
            print(f"    step{step} + XOR{xor}")

    # ═══════════════════════════════════════════════════════════════════════════
    # FAZIT
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n" + "═" * 70)
    print("FAZIT")
    print("═" * 70)

    print(f"""
  1. POSITIONS-ANALYSE:
     - 1CFi: [{r1}, {c1}], Basis-Wert: {val_1cfi}
     - 1CFB: [{r2}, {c2}], Basis-Wert: {val_1cfb}
     - Row-Summe: {r1 + c1} vs. {r2 + c2}

  2. SYMMETRIE:
     - Die Positionen sind NICHT direkte Spiegel voneinander
     - Aber beide haben: 0x7b first byte, byte sum 2299

  3. WERT-BEZIEHUNG:
     - Summe der Werte: {val_1cfi + val_1cfb}
     - XOR der Werte: {val_1cfi ^ val_1cfb}

  4. EMPFEHLUNG:
     - Teste systematisch step{{7,13,27,33,37,42}} + XOR{{0,7,13,27,33}}
     - Die Lösung für 1CFB könnte eine CFB-Variation von 1CFi sein
""")

    # Speichern
    results = {
        '1CFi': POSITIONS['1CFi_SOLVED'],
        '1CFB': POSITIONS['1CFB_UNSOLVED'],
        'value_1cfi': val_1cfi,
        'value_1cfb': val_1cfb,
        'value_sum': val_1cfi + val_1cfb,
        'value_xor': val_1cfi ^ val_1cfb,
        'position_distance': abs(r1 - r2) + abs(c1 - c2),
    }

    output_file = SCRIPT_DIR / '1CFB_1CFI_POSITION_ANALYSIS.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Ergebnisse gespeichert: {output_file}")

if __name__ == "__main__":
    main()
