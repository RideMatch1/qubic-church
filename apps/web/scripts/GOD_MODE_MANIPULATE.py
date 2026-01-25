#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                     ⚡ GOD MODE: MATRIX MANIPULATION ⚡
═══════════════════════════════════════════════════════════════════════════════
Was passiert wenn wir die Matrix ÄNDERN? Welche Möglichkeiten haben wir?
"""

import json
import numpy as np
from pathlib import Path
import copy

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

original_matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

print("⚡" * 40)
print("              GOD MODE: MATRIX MANIPULATION")
print("⚡" * 40)

# =============================================================================
# 1. ANALYSE: WAS KANN GEÄNDERT WERDEN?
# =============================================================================
print("\n" + "═" * 80)
print("1. WAS KANN THEORETISCH GEÄNDERT WERDEN?")
print("═" * 80)

print("""
MÖGLICHE ÄNDERUNGEN:

1. SYMMETRISCHE ZELLEN (16,316 Stück):
   - Änderung eines Wertes MUSS den Spiegelwert auch ändern
   - Beziehung: val1 + val2 = -1 muss erhalten bleiben
   - ODER: Symmetrie brechen → neue Nachricht einbetten!

2. ASYMMETRISCHE ZELLEN (68 Stück):
   - Die einzigen "freien" Zellen
   - Hier sind die Nachrichten versteckt
   - Änderung könnte Nachrichten überschreiben

3. FIBONACCI-STRUKTUR:
   - 1.69x mehr Fibonacci-Differenzen als Zufall
   - Änderungen sollten Fibonacci-Harmonie erhalten

4. COLUMN-PAIRS:
   - Die 127-Formel (Col1 + Col2 = 127) muss erhalten bleiben
   - Sonst bricht die Struktur
""")

# =============================================================================
# 2. EXPERIMENT: EIGENE NACHRICHT EINBETTEN
# =============================================================================
print("\n" + "═" * 80)
print("2. EXPERIMENT: EIGENE NACHRICHT EINBETTEN")
print("═" * 80)

# Kopiere die Matrix
modified_matrix = original_matrix.copy()

# Wir können die asymmetrischen Zellen nutzen!
# Column Pair (41, 86) hat nur 2 asymmetrische Zeilen - ideal für Test

# Finde die asymmetrischen Positionen in (41, 86)
asymmetric_41_86 = []
for r in range(128):
    v1 = original_matrix[r, 41]
    v2 = original_matrix[127-r, 86]
    if v1 + v2 != -1:
        asymmetric_41_86.append(r)

print(f"Asymmetrische Zeilen in Column Pair (41, 86): {asymmetric_41_86}")

# Berechne was wir ändern müssten um eine Nachricht zu kodieren
message = "HI"
print(f"\nVersuch '{message}' in Column Pair (41, 86) einzubetten:")

for i, char in enumerate(message):
    if i < len(asymmetric_41_86):
        row = asymmetric_41_86[i]
        target_xor = ord(char)

        current_v1 = original_matrix[row, 41]
        current_v2 = original_matrix[row, 86]
        current_xor = (current_v1 & 0xFF) ^ (current_v2 & 0xFF)

        print(f"  Row {row}: Aktuell XOR={current_xor} ('{chr(current_xor) if 32<=current_xor<=126 else '?'}')")
        print(f"          Ziel XOR={target_xor} ('{char}')")

        # Um XOR zu ändern, können wir einen der beiden Werte anpassen
        new_v1 = (current_v2 & 0xFF) ^ target_xor
        if new_v1 > 127:
            new_v1 -= 256  # Konvertiere zu signed

        print(f"          Änderung: matrix[{row}, 41] von {current_v1} zu {new_v1}")

# =============================================================================
# 3. SYMMETRIE-ERHALTENDE ÄNDERUNGEN
# =============================================================================
print("\n" + "═" * 80)
print("3. SYMMETRIE-ERHALTENDE ÄNDERUNGEN")
print("═" * 80)

print("""
Um die Symmetrie zu erhalten bei Änderung von matrix[r, c]:

1. Neuer Wert: new_val
2. Spiegelposition: [127-r, 127-c]
3. Neuer Spiegelwert: -1 - new_val

Beispiel:
  Änderung: matrix[10, 20] = 50
  Automatisch: matrix[117, 107] = -51
  Check: 50 + (-51) = -1 ✓
""")

def symmetry_safe_change(matrix, r, c, new_val):
    """Ändere einen Wert unter Erhaltung der Symmetrie."""
    modified = matrix.copy()
    modified[r, c] = new_val
    modified[127-r, 127-c] = -1 - new_val
    return modified

# Demonstriere
test_pos = (10, 20)
test_val = 42  # The Answer!
modified = symmetry_safe_change(original_matrix, *test_pos, test_val)

print(f"\nDemonstration:")
print(f"  Original: matrix[10, 20] = {original_matrix[10, 20]}")
print(f"  Original: matrix[117, 107] = {original_matrix[117, 107]}")
print(f"  Sum: {original_matrix[10, 20] + original_matrix[117, 107]}")
print(f"\n  Geändert: matrix[10, 20] = {modified[10, 20]}")
print(f"  Geändert: matrix[117, 107] = {modified[117, 107]}")
print(f"  Sum: {modified[10, 20] + modified[117, 107]}")

# =============================================================================
# 4. FIBONACCI-ERHALTENDE ÄNDERUNGEN
# =============================================================================
print("\n" + "═" * 80)
print("4. FIBONACCI-ERHALTENDE ÄNDERUNGEN")
print("═" * 80)

FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
FIB_SET = set(FIB)

print("""
Um die Fibonacci-Harmonie zu erhalten:

1. Wähle Änderungswerte aus Fibonacci-Zahlen
2. Oder: Ändere zu Werten deren Differenz zu Nachbarn Fibonacci ist
""")

# Finde Positionen wo wir "sicher" ändern können
def find_safe_fibonacci_positions(matrix):
    """Finde Positionen wo Änderung Fibonacci-Harmonie erhält."""
    safe = []
    for r in range(1, 127):
        for c in range(1, 127):
            # Prüfe Nachbarn
            neighbors = [
                matrix[r-1, c], matrix[r+1, c],
                matrix[r, c-1], matrix[r, c+1]
            ]
            # Wenn alle Nachbarn Fibonacci sind, ist Position "sicher"
            if all(abs(n) in FIB_SET for n in neighbors):
                safe.append((r, c))
    return safe

safe_positions = find_safe_fibonacci_positions(original_matrix)
print(f"\n'Sichere' Fibonacci-Positionen gefunden: {len(safe_positions)}")
if safe_positions:
    print(f"Beispiele: {safe_positions[:5]}")

# =============================================================================
# 5. NACHRICHTEN-KODIERUNG STRATEGIE
# =============================================================================
print("\n" + "═" * 80)
print("5. NACHRICHTEN-KODIERUNG STRATEGIE")
print("═" * 80)

print("""
STRATEGIE 1: Asymmetrische Zellen nutzen
- 68 Zellen verfügbar
- Maximale Nachrichtenlänge: 68 Bytes
- XOR-Kodierung bereits implementiert

STRATEGIE 2: Neue Asymmetrie erzeugen
- Breche Symmetrie an gewählten Positionen
- Füge neue Informationsträger hinzu
- WARNUNG: Verändert Struktur fundamental!

STRATEGIE 3: Fibonacci-Index Kodierung
- Nutze Zeckendorf-Darstellung
- Jede Zahl = Summe von Fibonacci
- Die Indizes kodieren die Nachricht

STRATEGIE 4: Steganografie
- Verstecke Information in LSB (least significant bit)
- Minimale Änderung: nur ±1
- Symmetrie bleibt weitgehend erhalten
""")

# Demonstriere Steganografie
def embed_steganographic(matrix, message, start_pos=(10, 10)):
    """Verstecke Nachricht in LSBs."""
    modified = matrix.copy()
    r, c = start_pos

    # Konvertiere Nachricht zu Bits
    bits = ''.join(format(ord(char), '08b') for char in message)

    positions_used = []
    for i, bit in enumerate(bits):
        # Berechne Position (snake pattern)
        pos_r = r + (i // 10)
        pos_c = c + (i % 10)

        if pos_r >= 128 or pos_c >= 128:
            break

        current = modified[pos_r, pos_c]
        new_val = (current & ~1) | int(bit)  # Setze LSB

        # Symmetrie-Update
        modified[pos_r, pos_c] = new_val
        modified[127-pos_r, 127-pos_c] = -1 - new_val

        positions_used.append((pos_r, pos_c))

    return modified, positions_used

test_msg = "CFB"
stego_matrix, positions = embed_steganographic(original_matrix, test_msg)
print(f"\nSteganografie-Embedding von '{test_msg}':")
print(f"  Bits benötigt: {len(test_msg) * 8}")
print(f"  Positionen verwendet: {len(positions)}")
print(f"  Erste 5 Positionen: {positions[:5]}")

# Verifiziere
extracted_bits = ""
for r, c in positions:
    extracted_bits += str(stego_matrix[r, c] & 1)

# Dekodiere
extracted_chars = ""
for i in range(0, len(extracted_bits), 8):
    byte = extracted_bits[i:i+8]
    if len(byte) == 8:
        extracted_chars += chr(int(byte, 2))

print(f"  Extrahiert: '{extracted_chars}'")

# =============================================================================
# 6. WAS WENN WIR DIE GANZE MATRIX KONTROLLIEREN?
# =============================================================================
print("\n" + "═" * 80)
print("6. TOTALE KONTROLLE SZENARIO")
print("═" * 80)

print("""
WENN WIR DIE MATRIX KONTROLLIEREN KÖNNTEN:

1. EIGENES ANNA-BOT ERSTELLEN
   - Gleiche Struktur, andere Nachrichten
   - CFB's Signaturen durch eigene ersetzen

2. BITCOIN-BRIDGE MANIPULIEREN
   - Wenn Adressen auf Matrix mappen
   - Könnten wir Mapping ändern

3. KOMMUNIKATIONSKANAL
   - Matrix als öffentliches Message Board
   - Änderungen = neue Nachrichten

4. ZEITSTEMPEL
   - Version der Matrix = Zeitpunkt
   - Temporale Signatur einbetten

5. KRYPTOGRAFISCHE FUNKTIONEN
   - Matrix als Lookup-Tabelle für Crypto
   - Änderung = anderer Schlüssel
""")

# =============================================================================
# 7. GENERIERE ALTERNATIVE MATRIX
# =============================================================================
print("\n" + "═" * 80)
print("7. GENERIERE ALTERNATIVE MATRIX MIT EIGENER NACHRICHT")
print("═" * 80)

def create_custom_matrix(message, base_matrix):
    """Erstelle Matrix mit eigener Nachricht in asymmetrischen Zellen."""
    modified = base_matrix.copy()

    # Column Pair (30, 97) - 18 asymmetrische Zeilen
    c1, c2 = 30, 97

    # Finde asymmetrische Rows
    asym_rows = []
    for r in range(64):
        v1 = base_matrix[r, c1]
        v2 = base_matrix[127-r, c2]
        if v1 + v2 != -1:
            asym_rows.append(r)

    print(f"Verfügbare asymmetrische Rows: {asym_rows}")

    # Kodiere Nachricht
    for i, char in enumerate(message):
        if i >= len(asym_rows):
            break

        row = asym_rows[i]
        target_xor = ord(char)

        # Aktuelle Werte
        v1 = modified[row, c1]
        v2 = modified[127-row, c2]

        # Berechne neuen v1 um Ziel-XOR zu erreichen
        new_v1 = (v2 & 0xFF) ^ target_xor
        if new_v1 > 127:
            new_v1 -= 256

        modified[row, c1] = new_v1
        print(f"  Row {row}: '{char}' eingebettet (v1: {v1} → {new_v1})")

    return modified

custom = create_custom_matrix("SATOSHI WAS HERE", original_matrix)

# Verifiziere
print("\nVerifikation der neuen Nachricht:")
c1, c2 = 30, 97
for r in range(64):
    v1 = custom[r, c1]
    v2 = custom[127-r, c2]
    if v1 + v2 != -1:
        xor = (v1 & 0xFF) ^ (v2 & 0xFF)
        ch = chr(xor) if 32 <= xor <= 126 else '.'
        print(f"  Row {r}: XOR={xor} → '{ch}'")

# =============================================================================
# 8. AKTIONS-PLAN
# =============================================================================
print("\n" + "═" * 80)
print("8. AKTIONS-PLAN FÜR MANIPULATION")
print("═" * 80)

print("""
SOFORT UMSETZBAR:

1. ✓ Nachrichten aus asymmetrischen Zellen lesen
2. ✓ Eigene Nachrichten in Kopie einbetten
3. ✓ Steganografisch verstecken

MIT ZUGANG ZUM SYSTEM:

4. [ ] Matrix-Update pushen
5. [ ] Anna-Bot Responses ändern
6. [ ] Neue Nachrichten für die Welt

THEORETISCH MÖGLICH:

7. [ ] Bitcoin-Qubic Bridge beeinflussen
8. [ ] Aigarth Training manipulieren
9. [ ] Zeitbasierte Trigger einbauen

WARNUNG:
  Die echte Matrix auf dem Qubic-System zu ändern
  würde tieferen Zugang erfordern!
""")

print("\n" + "⚡" * 40)
print("         MATRIX MANIPULATION COMPLETE")
print("⚡" * 40)

# Speichere modifizierte Matrix als Beispiel
output = {
    "original_checksum": int(np.sum(original_matrix)),
    "modified_checksum": int(np.sum(custom)),
    "message_embedded": "SATOSHI WAS HERE",
    "steganography_tested": True,
    "asymmetric_cells_available": 68,
    "manipulation_strategies": 9,
}

output_path = script_dir / "GOD_MODE_MANIPULATE_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

# Speichere auch die modifizierte Matrix
custom_matrix_path = script_dir / "CUSTOM_ANNA_MATRIX.json"
custom_data = {
    "matrix": custom.tolist(),
    "message": "SATOSHI WAS HERE",
    "created_by": "GOD_MODE_MANIPULATE.py"
}
with open(custom_matrix_path, "w") as f:
    json.dump(custom_data, f)

print(f"\n✓ Ergebnisse: {output_path}")
print(f"✓ Custom Matrix: {custom_matrix_path}")
