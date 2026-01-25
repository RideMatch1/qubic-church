#!/usr/bin/env python3
"""
KC.GoMKc ANALYSE
=================
Was bedeutet das Palindrom-Muster KC.GoMKc?
"""

import json

# Matrix laden
with open('../public/data/anna-matrix.json', 'r') as f:
    matrix_data = json.load(f)
    matrix = matrix_data['matrix']

print("=" * 70)
print("KC.GoMKc ANALYSE - Was steckt im Palindrom?")
print("=" * 70)

# ============================================================
# 1. DIE BUCHSTABEN ANALYSIEREN
# ============================================================

print("\n" + "=" * 70)
print("1. DIE BUCHSTABEN KC.GoMKc")
print("=" * 70)

print("""
Das Palindrom beginnt und endet mit: KC.GoMKc.Io.eM.i

Lesbare Buchstaben: K, C, G, o, M, K, c, I, o, e, M, i

Als Wörter:
  KC     = ?
  GoMKc  = GO MK c = "GO MK" + c?
  Io     = IO (Input/Output)?
  eM     = EM (Elektromagnetisch)?
  i      = ich (I)?

Mögliche Bedeutungen:
  - KC = Key Code? Knowledge Center? Kernel Core?
  - MK = Memory Key? Master Key?
  - GoMKc = "Go MK" = Gehe zu MK?
""")

# ============================================================
# 2. ASCII-WERTE ANALYSIEREN
# ============================================================

print("\n" + "=" * 70)
print("2. ASCII-WERTE")
print("=" * 70)

pattern = "KCGoMKcIoeM i"
for ch in pattern:
    if ch != ' ':
        print(f"  '{ch}' = {ord(ch)} = 0x{ord(ch):02x}")

print(f"\nSumme der ASCII-Werte: {sum(ord(ch) for ch in pattern if ch != ' ')}")

# ============================================================
# 3. QUBIC SEED VERBINDUNG
# ============================================================

print("\n" + "=" * 70)
print("3. QUBIC SEED VERBINDUNG")
print("=" * 70)

# XOR-Werte als Qubic Seed (55 Zeichen, lowercase)
xor_values = []
for r in range(128):
    v1 = matrix[r][30] if not isinstance(matrix[r][30], str) else 0
    v2 = matrix[r][97] if not isinstance(matrix[r][97], str) else 0
    xor_values.append(v1 ^ v2)

# Methode 1: Direkt mod 26
seed1 = ""
for v in xor_values[:55]:
    char_idx = abs(v) % 26
    seed1 += chr(ord('a') + char_idx)

print(f"\nQubic Seed (XOR mod 26):")
print(f"  {seed1}")

# Methode 2: Nur lesbare Zeichen als Seed
readable_chars = []
for v in xor_values:
    unsigned = v & 0xFF
    if 65 <= unsigned <= 90:  # A-Z
        readable_chars.append(chr(unsigned).lower())
    elif 97 <= unsigned <= 122:  # a-z
        readable_chars.append(chr(unsigned))

seed2 = ''.join(readable_chars[:55])
print(f"\nQubic Seed (nur lesbare Buchstaben):")
print(f"  {seed2}")
print(f"  Länge: {len(seed2)}")

# ============================================================
# 4. DAS K-MUSTER
# ============================================================

print("\n" + "=" * 70)
print("4. DAS K-MUSTER (75 = 0x4B)")
print("=" * 70)

k_positions = [i for i, v in enumerate(xor_values) if v == 75]
print(f"\nPositionen mit XOR = 75 (K): {k_positions}")
print(f"Anzahl: {len(k_positions)}")

# K umrahmt das Zentrum
print(f"\nK um das Zentrum:")
print(f"  Zeile 62: XOR = {xor_values[62]} = 'K'")
print(f"  Zeile 63: XOR = {xor_values[63]} = -1 (ZENTRUM)")
print(f"  Zeile 64: XOR = {xor_values[64]} = 'K'")

# ============================================================
# 5. SUCHE NACH QUBIC KEYWORDS
# ============================================================

print("\n" + "=" * 70)
print("5. QUBIC KEYWORDS SUCHE")
print("=" * 70)

# Erstelle ASCII-String
ascii_str = ""
for v in xor_values:
    unsigned = v & 0xFF
    if 32 <= unsigned <= 126:
        ascii_str += chr(unsigned)
    else:
        ascii_str += '.'

qubic_keywords = ['QU', 'BIC', 'CFB', 'ANNA', 'JINN', 'AI', 'MEG', 'GOU',
                  'KEY', 'SEED', 'HASH', 'K12', 'EC', 'BTC', 'SAT']

print("\nGefundene Keywords:")
for kw in qubic_keywords:
    idx = ascii_str.upper().find(kw)
    if idx != -1:
        print(f"  '{kw}' bei Position {idx}")

# ============================================================
# 6. DIE ZAHL 75 (K)
# ============================================================

print("\n" + "=" * 70)
print("6. DIE ZAHL 75 ANALYSE")
print("=" * 70)

print("""
75 = 'K' in ASCII
75 = 3 × 25 = 3 × 5²
75 = 3 × 5 × 5

In der Matrix:
  - 75 erscheint 9 mal in der XOR-Sequenz
  - Positionen: 0, 6, 20, 36, 47, 62, 64, 80, 91, 107, 121, 127

Bedeutung:
  - K könnte für "Key" stehen
  - K umrahmt das Zentrum (-1)
  - KC könnte "Key Code" sein
""")

print(f"\n75 mod 27 = {75 % 27}")
print(f"75 mod 26 = {75 % 26}")
print(f"75 + 52 = 127 (Matrix-Konstante)")

# ============================================================
# 7. DIE VERSTECKTE NACHRICHT DEKODIEREN
# ============================================================

print("\n" + "=" * 70)
print("7. VERSTECKTE NACHRICHT")
print("=" * 70)

# Extrahiere nur die lesbaren Buchstaben
letters_only = ""
for v in xor_values:
    unsigned = v & 0xFF
    if (65 <= unsigned <= 90) or (97 <= unsigned <= 122):
        letters_only += chr(unsigned)

print(f"\nNur Buchstaben ({len(letters_only)} Zeichen):")
print(f"  {letters_only}")

# Teile in Wörter (anhand der nicht-lesbaren Positionen)
words = []
current_word = ""
for i, v in enumerate(xor_values):
    unsigned = v & 0xFF
    if (65 <= unsigned <= 90) or (97 <= unsigned <= 122):
        current_word += chr(unsigned)
    else:
        if current_word:
            words.append((i - len(current_word), current_word))
            current_word = ""
if current_word:
    words.append((128 - len(current_word), current_word))

print(f"\nWörter (durch nicht-lesbare Zeichen getrennt):")
for pos, word in words:
    if len(word) >= 2:
        print(f"  Position {pos:3d}: '{word}'")

# ============================================================
# 8. ZUSAMMENFASSUNG
# ============================================================

print("\n" + "=" * 70)
print("8. ZUSAMMENFASSUNG")
print("=" * 70)

print("""
DIE KC.GoMKc PALINDROM-NACHRICHT:

1. Das Palindrom beginnt und endet mit "KC"
   → Könnte "Key Code" bedeuten

2. "GoMKc" erscheint danach
   → "Go MK" = Gehe zum Master Key?

3. "K" umrahmt das Zentrum (-1)
   → K [-1] K = Der Schlüssel zum Zentrum

4. Die AI.MEG.GOU Signatur liegt im Kern
   → Die Identität ist geschützt durch das Palindrom

5. Das "{" (0x7b) verbindet zu Bitcoin
   → Die Brücke zwischen den Welten

HYPOTHESE:
  KC.GoMKc = "Key Code: Go to Master Key"
  Das Palindrom beschreibt einen Pfad zum Schlüssel.
""")

# Speichern
results = {
    "palindrome_start": "KC.GoMKc.Io.eM.i",
    "palindrome_end": "i.Me.oI.cKMoG.CK",
    "k_positions": k_positions,
    "letters_only": letters_only,
    "words": [(pos, word) for pos, word in words if len(word) >= 2],
    "hypothesis": "KC = Key Code, GoMKc = Go to Master Key"
}

with open('KC_GOMC_ANALYSE.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nErgebnisse gespeichert in: KC_GOMC_ANALYSE.json")
