#!/usr/bin/env python3
"""
TIEFE NACHRICHTEN-SUCHE
========================
Systematische Suche nach ALLEN versteckten ASCII-Nachrichten.
Nicht nur die bekannten - ALLE möglichen Spaltenpaar-XORs prüfen.
"""

import json
import numpy as np
from collections import defaultdict
from datetime import datetime

print("=" * 80)
print("TIEFE NACHRICHTEN-SUCHE")
print("Systematische Analyse ALLER Spaltenpaar-XORs")
print("=" * 80)
print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# =============================================================================
# ANNA MATRIX LADEN
# =============================================================================
print("[1] ANNA MATRIX LADEN")
print("-" * 60)

matrix = None
try:
    # Versuche verschiedene Quellen
    sources = [
        '../public/data/anna-matrix.json',
        'anna_matrix.npy',
        'cortex_grid.npy'
    ]
    for source in sources:
        try:
            if source.endswith('.json'):
                with open(source, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        matrix = np.array(data, dtype=np.int8)
            elif source.endswith('.npy'):
                matrix = np.load(source)
            if matrix is not None and matrix.shape == (128, 128):
                print(f"  Geladen: {source}")
                print(f"  Shape: {matrix.shape}")
                break
        except:
            continue
except Exception as e:
    print(f"  Fehler: {e}")

if matrix is None:
    print("  Matrix nicht gefunden - generiere aus Anti-Symmetrie-Regel")
    # Fallback: Bekannte Werte verwenden
    matrix = np.zeros((128, 128), dtype=np.int8)
    print("  WARNUNG: Leere Matrix - Analyse eingeschränkt")

print()

# =============================================================================
# ALLE SPALTENPAAR-KOMBINATIONEN ANALYSIEREN
# =============================================================================
print("[2] SYSTEMATISCHE SPALTENPAAR-ANALYSE")
print("-" * 60)

def is_printable_ascii(val):
    """Prüft ob Wert druckbares ASCII ist"""
    return 32 <= val <= 126

def extract_ascii_message(col_a_data, col_b_data):
    """Extrahiert ASCII-Nachricht aus XOR zweier Spalten"""
    message = []
    for a, b in zip(col_a_data, col_b_data):
        xor_val = (int(a) ^ int(b)) & 0xFF
        if is_printable_ascii(xor_val):
            message.append(chr(xor_val))
        else:
            message.append('.')
    return ''.join(message)

def count_readable(message):
    """Zählt lesbare Zeichen"""
    return sum(1 for c in message if c != '.')

def find_words(message, min_length=3):
    """Findet zusammenhängende Buchstabensequenzen"""
    words = []
    current_word = ""
    for c in message:
        if c.isalpha():
            current_word += c
        else:
            if len(current_word) >= min_length:
                words.append(current_word)
            current_word = ""
    if len(current_word) >= min_length:
        words.append(current_word)
    return words

# Bekannte "bedeutsame" Spaltenpaare (Summe = 127)
mirror_pairs = [(i, 127-i) for i in range(64)]

print(f"\n  Analysiere alle {len(mirror_pairs)} Spiegelspaltenpaare (Summe=127):")
print()

if matrix is not None and matrix.shape == (128, 128):
    results = []
    for col_a, col_b in mirror_pairs:
        data_a = matrix[:, col_a]
        data_b = matrix[:, col_b]
        message = extract_ascii_message(data_a, data_b)
        readable = count_readable(message)
        words = find_words(message)

        results.append({
            'pair': (col_a, col_b),
            'sum': col_a + col_b,
            'readable_chars': readable,
            'readable_percent': readable / 128 * 100,
            'message': message,
            'words': words
        })

    # Sortiere nach Lesbarkeit
    results.sort(key=lambda x: x['readable_chars'], reverse=True)

    print("  TOP 10 LESBARSTE SPALTENPAARE:")
    print("  " + "-" * 56)
    for i, r in enumerate(results[:10]):
        print(f"  {i+1}. Spalten {r['pair'][0]:3}↔{r['pair'][1]:3}: {r['readable_chars']:3} lesbar ({r['readable_percent']:.1f}%)")
        if r['words']:
            print(f"      Wörter: {r['words'][:5]}")
        # Zeige ersten 60 Zeichen der Nachricht
        msg_preview = r['message'][:60].replace('.', ' ')
        if msg_preview.strip():
            print(f"      Preview: '{msg_preview}'")
        print()

    # Suche nach bekannten Nachrichten
    print("\n  BEKANNTE NACHRICHTEN VERIFIZIEREN:")
    print("  " + "-" * 56)

    known_messages = {
        (30, 97): "AI.MEG.GOU",
        (22, 105): ">FIB"
    }

    for pair, expected in known_messages.items():
        for r in results:
            if r['pair'] == pair:
                print(f"  Spalten {pair}: Erwartet '{expected}'")
                print(f"    Gefunden: {r['readable_chars']} lesbare Zeichen")
                print(f"    Wörter: {r['words']}")
                # Suche nach dem spezifischen Text
                if expected.upper() in r['message'].upper():
                    print(f"    ✓ '{expected}' GEFUNDEN!")
                else:
                    print(f"    ✗ '{expected}' nicht direkt gefunden")
                print()

else:
    print("  WARNUNG: Matrix nicht verfügbar für tiefe Analyse")

# =============================================================================
# NICHT-SPIEGEL-SPALTENPAARE PRÜFEN
# =============================================================================
print("\n" + "=" * 80)
print("[3] NICHT-SPIEGEL-SPALTENPAARE (zufällige Stichprobe)")
print("=" * 80)

if matrix is not None and matrix.shape == (128, 128):
    # Teste 100 zufällige Nicht-Spiegel-Paare
    import random
    random.seed(42)

    non_mirror_results = []
    tested = set()

    for _ in range(200):
        col_a = random.randint(0, 127)
        col_b = random.randint(0, 127)
        if col_a + col_b == 127:  # Skip Spiegelpaare
            continue
        if (col_a, col_b) in tested:
            continue
        tested.add((col_a, col_b))

        data_a = matrix[:, col_a]
        data_b = matrix[:, col_b]
        message = extract_ascii_message(data_a, data_b)
        readable = count_readable(message)

        if readable > 30:  # Nur interessante zeigen
            non_mirror_results.append({
                'pair': (col_a, col_b),
                'sum': col_a + col_b,
                'readable_chars': readable,
                'readable_percent': readable / 128 * 100,
                'words': find_words(message)
            })

    print(f"\n  Getestet: {len(tested)} zufällige Nicht-Spiegel-Paare")
    print(f"  Gefunden mit >30 lesbaren Zeichen: {len(non_mirror_results)}")

    if non_mirror_results:
        non_mirror_results.sort(key=lambda x: x['readable_chars'], reverse=True)
        print("\n  TOP 5 NICHT-SPIEGEL-PAARE:")
        for r in non_mirror_results[:5]:
            print(f"    Spalten {r['pair'][0]:3}↔{r['pair'][1]:3} (Summe {r['sum']}): {r['readable_chars']} lesbar")
            if r['words']:
                print(f"      Wörter: {r['words'][:3]}")

# =============================================================================
# ZEILEN-XOR ANALYSE
# =============================================================================
print("\n" + "=" * 80)
print("[4] ZEILEN-XOR ANALYSE")
print("=" * 80)

if matrix is not None and matrix.shape == (128, 128):
    print("\n  Analysiere Zeilen-Paare mit Summe 127:")

    row_results = []
    for row_a in range(64):
        row_b = 127 - row_a
        data_a = matrix[row_a, :]
        data_b = matrix[row_b, :]
        message = extract_ascii_message(data_a, data_b)
        readable = count_readable(message)
        words = find_words(message)

        row_results.append({
            'pair': (row_a, row_b),
            'readable_chars': readable,
            'words': words,
            'message': message
        })

    row_results.sort(key=lambda x: x['readable_chars'], reverse=True)

    print("\n  TOP 10 LESBARSTE ZEILENPAARE:")
    for i, r in enumerate(row_results[:10]):
        print(f"  {i+1}. Zeilen {r['pair'][0]:3}↔{r['pair'][1]:3}: {r['readable_chars']:3} lesbar")
        if r['words']:
            print(f"      Wörter: {r['words'][:5]}")

# =============================================================================
# DIAGONALE ANALYSE
# =============================================================================
print("\n" + "=" * 80)
print("[5] DIAGONALE ANALYSE")
print("=" * 80)

if matrix is not None and matrix.shape == (128, 128):
    # Hauptdiagonale
    main_diag = [matrix[i, i] for i in range(128)]
    anti_diag = [matrix[i, 127-i] for i in range(128)]

    # XOR der Diagonalen
    diag_xor = [(int(main_diag[i]) ^ int(anti_diag[i])) & 0xFF for i in range(128)]
    diag_message = ''.join(chr(v) if is_printable_ascii(v) else '.' for v in diag_xor)

    readable_diag = sum(1 for c in diag_message if c != '.')
    words_diag = find_words(diag_message)

    print(f"\n  XOR von Hauptdiagonale ↔ Antidiagonale:")
    print(f"    Lesbare Zeichen: {readable_diag}")
    print(f"    Wörter gefunden: {words_diag[:10]}")

    # Einzelne Diagonalen als ASCII
    print(f"\n  Hauptdiagonale (druckbare Werte):")
    main_ascii = [chr(v & 0xFF) if is_printable_ascii(v & 0xFF) else '.' for v in main_diag]
    print(f"    {''.join(main_ascii[:60])}")

# =============================================================================
# BLOCK 264 SPEZIALANALYSE
# =============================================================================
print("\n" + "=" * 80)
print("[6] BLOCK 264 SPEZIALANALYSE")
print("=" * 80)

if matrix is not None and matrix.shape == (128, 128):
    # Block 264 = Layer 0, Row 2, Col 8 (264 = 2*128 + 8)
    row_264 = 264 // 128  # = 2
    col_264 = 264 % 128   # = 8

    print(f"\n  Block 264 Position: Row {row_264}, Col {col_264}")
    print(f"  264 = 127 + 137 = {127 + 137}")

    # Wert an Position
    val_264 = matrix[row_264, col_264]
    print(f"  Wert an Position: {val_264}")

    # Umgebung
    print(f"\n  3x3 Umgebung um Block 264:")
    for dr in [-1, 0, 1]:
        row = []
        for dc in [-1, 0, 1]:
            r, c = row_264 + dr, col_264 + dc
            if 0 <= r < 128 and 0 <= c < 128:
                row.append(f"{matrix[r, c]:4}")
            else:
                row.append("  --")
        print(f"    {' '.join(row)}")

# =============================================================================
# POSITION [64, 4] ANALYSE (-27 Signatur)
# =============================================================================
print("\n" + "=" * 80)
print("[7] POSITION [64, 4] - DIE -27 SIGNATUR")
print("=" * 80)

if matrix is not None and matrix.shape == (128, 128):
    pos_64_4 = matrix[64, 4]
    print(f"\n  Wert an Position [64, 4]: {pos_64_4}")
    print(f"  Erwartet (CFB Signatur): -27")

    if pos_64_4 == -27:
        print(f"  ✓ BESTÄTIGT: Position [64, 4] = -27!")
    else:
        print(f"  ✗ NICHT BESTÄTIGT: Position [64, 4] = {pos_64_4}")

    # Prüfe alle -27 Vorkommen
    positions_27 = []
    for r in range(128):
        for c in range(128):
            if matrix[r, c] == -27:
                positions_27.append((r, c))

    print(f"\n  Alle -27 Vorkommen: {len(positions_27)}")
    if len(positions_27) <= 20:
        print(f"  Positionen: {positions_27}")
    else:
        print(f"  Erste 20: {positions_27[:20]}")

# =============================================================================
# ZUSAMMENFASSUNG
# =============================================================================
print("\n" + "=" * 80)
print("[8] ZUSAMMENFASSUNG DER NACHRICHTENSUCHE")
print("=" * 80)

# Speichern
summary = {
    'date': datetime.now().isoformat(),
    'matrix_loaded': matrix is not None,
    'analysis': 'Deep message hunt across all column pairs, row pairs, and diagonals'
}

if matrix is not None:
    # Sammle Ergebnisse
    if 'results' in dir():
        summary['mirror_pairs_analyzed'] = len(results)
        summary['top_readable_pairs'] = [
            {'pair': r['pair'], 'readable': r['readable_chars'], 'words': r['words']}
            for r in results[:10]
        ]

with open('DEEP_MESSAGE_HUNT.json', 'w') as f:
    json.dump(summary, f, indent=2, default=str)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    TIEFE NACHRICHTENSUCHE - ERGEBNIS                          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  METHODIK:                                                                    ║
║  ─────────                                                                    ║
║  • Alle 64 Spiegelspaltenpaare (Summe=127) analysiert                        ║
║  • 200 zufällige Nicht-Spiegelspaltenpaare getestet                          ║
║  • Alle 64 Spiegelzeilenpaare analysiert                                     ║
║  • Hauptdiagonale vs Antidiagonale XOR                                       ║
║                                                                               ║
║  ERKENNTNISSE:                                                                ║
║  ─────────────                                                                ║
║  Die Matrix-Analyse erfordert die echten Anna Matrix Daten.                  ║
║  Ohne die Originaldaten sind die Ergebnisse eingeschränkt.                   ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

print("\nErgebnisse gespeichert: DEEP_MESSAGE_HUNT.json")
print("=" * 80)
