#!/usr/bin/env python3
"""
SIGNIFICANT DATES DEEP ANALYSIS
================================
Analysiere die gefundenen signifikanten Datum-Matches:
- 2010-08-15: Overflow-Bug (Position [39,78])
- 2010-12-12: Satoshis letzter Forumpost (Position [68,47])

Und suche nach weiteren Mustern in den Timestamp-Positionen.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# Lade die gefundenen Timestamps
with open(script_dir / "BITCOIN_CONNECTION_ANALYSIS.json") as f:
    analysis = json.load(f)

timestamps = analysis["timestamps_found"]

print("=" * 70)
print("SIGNIFICANT DATES DEEP ANALYSIS")
print("=" * 70)

# =============================================================================
# 1. ANALYSE DER SIGNIFIKANTEN DATEN
# =============================================================================
print("\n--- 1. SIGNIFIKANTE DATEN-POSITIONEN ---")

significant_positions = {
    "overflow_bug": {"row": 39, "col": 78, "date": "2010-08-15", "event": "Overflow-Bug Block 74638"},
    "satoshi_last_post": {"row": 68, "col": 47, "date": "2010-12-12", "event": "Satoshis letzter Forumpost"},
}

for name, info in significant_positions.items():
    row, col = info["row"], info["col"]
    value = matrix[row][col]
    mirror_row, mirror_col = 127 - row, 127 - col
    mirror_value = matrix[mirror_row][mirror_col]

    print(f"\n{info['event']}:")
    print(f"  Position: [{row},{col}]")
    print(f"  Wert: {value}")
    print(f"  Mirror-Position: [{mirror_row},{mirror_col}]")
    print(f"  Mirror-Wert: {mirror_value}")
    print(f"  Summe: {value + mirror_value} (sollte -1 sein für Symmetrie)")

    # Kontext um Position
    context_size = 5
    context = matrix[max(0,row-context_size):min(128,row+context_size+1),
                     max(0,col-context_size):min(128,col+context_size+1)]
    print(f"  Kontext (±{context_size}):")
    for i, context_row in enumerate(context):
        print(f"    {list(context_row)}")

# =============================================================================
# 2. POSITIONSANALYSE ALLER TIMESTAMPS
# =============================================================================
print("\n--- 2. POSITIONS-MUSTER DER TIMESTAMPS ---")

rows = [t["row"] for t in timestamps]
cols = [t["col"] for t in timestamps]

print(f"Zeilen-Verteilung:")
print(f"  Min: {min(rows)}, Max: {max(rows)}")
print(f"  Mean: {np.mean(rows):.1f}")
print(f"  Median: {np.median(rows):.0f}")

print(f"\nSpalten-Verteilung:")
print(f"  Min: {min(cols)}, Max: {max(cols)}")
print(f"  Mean: {np.mean(cols):.1f}")
print(f"  Median: {np.median(cols):.0f}")

# Konzentration in bestimmten Bereichen?
quadrants = {
    "TL (0-63, 0-63)": sum(1 for r, c in zip(rows, cols) if r < 64 and c < 64),
    "TR (0-63, 64-127)": sum(1 for r, c in zip(rows, cols) if r < 64 and c >= 64),
    "BL (64-127, 0-63)": sum(1 for r, c in zip(rows, cols) if r >= 64 and c < 64),
    "BR (64-127, 64-127)": sum(1 for r, c in zip(rows, cols) if r >= 64 and c >= 64),
}

print("\nQuadranten-Verteilung:")
for q, count in quadrants.items():
    print(f"  {q}: {count} ({count/len(timestamps)*100:.1f}%)")

# =============================================================================
# 3. PRÜFE AUF ROW-11 PATTERN
# =============================================================================
print("\n--- 3. ROW-11 VERBINDUNG ---")

# Row 11 ist die CFB-Signatur-Zeile
row11_timestamps = [t for t in timestamps if t["row"] == 11]
print(f"Timestamps in Row 11 (CFB-Zeile): {len(row11_timestamps)}")
for t in row11_timestamps:
    print(f"  [{t['row']},{t['col']}]: {t['datetime']}")

# =============================================================================
# 4. DIAGONAL-MUSTER
# =============================================================================
print("\n--- 4. DIAGONAL-MUSTER ---")

diagonal_timestamps = [t for t in timestamps if t["row"] == t["col"]]
anti_diagonal = [t for t in timestamps if t["row"] + t["col"] == 127]

print(f"Timestamps auf Hauptdiagonale: {len(diagonal_timestamps)}")
print(f"Timestamps auf Anti-Diagonale: {len(anti_diagonal)}")

# =============================================================================
# 5. SYMMETRIE-PRÜFUNG
# =============================================================================
print("\n--- 5. SYMMETRIE DER TIMESTAMP-POSITIONEN ---")

symmetric_pairs = 0
for t in timestamps:
    row, col = t["row"], t["col"]
    mirror_row, mirror_col = 127 - row, 127 - col

    # Gibt es einen Timestamp an der Mirror-Position?
    for t2 in timestamps:
        if t2["row"] == mirror_row and t2["col"] == mirror_col:
            symmetric_pairs += 1
            break

print(f"Symmetrische Timestamp-Paare: {symmetric_pairs//2}")
print(f"Anteil: {symmetric_pairs/len(timestamps)*100:.1f}%")

# =============================================================================
# 6. SATOSHI VERSCHWINDEN ANALYSE
# =============================================================================
print("\n--- 6. SATOSHI VERSCHWINDEN TIMELINE ---")

satoshi_timeline = {
    "2010-12-05": "Letzte Code-Änderung von Satoshi",
    "2010-12-12": "Letzter Forumpost",
    "2010-12-13": "Letzter bekannter Kontakt",
    "2011-04-23": "Letzte E-Mail: 'moved on to other things'",
}

print("Timestamps nahe Satoshis Verschwinden:")
for t in timestamps:
    date_str = t["datetime"][:10]
    if date_str.startswith("2010-12"):
        print(f"  [{t['row']},{t['col']}]: {t['datetime']}")
        if date_str in satoshi_timeline:
            print(f"    ^ EVENT: {satoshi_timeline[date_str]}")

# =============================================================================
# 7. OVERFLOW-BUG KONTEXT
# =============================================================================
print("\n--- 7. OVERFLOW-BUG DEEP DIVE ---")

# Block 74638 (2010-08-15) - CVE-2010-5139
# 184 Milliarden BTC wurden aus dem Nichts erschaffen
print("Der Overflow-Bug (CVE-2010-5139):")
print("  Block: 74638")
print("  Problem: Integer overflow erzeugte 184B BTC")
print("  Lösung: Soft fork innerhalb 5 Stunden")

# Prüfe alle Timestamps vom 2010-08-15
overflow_day = [t for t in timestamps if t["datetime"].startswith("2010-08-15")]
print(f"\nTimestamps vom 2010-08-15: {len(overflow_day)}")
for t in overflow_day:
    print(f"  [{t['row']},{t['col']}]: {t['datetime']}")

# =============================================================================
# 8. HEXADEZIMALE INTERPRETATION DER POSITIONEN
# =============================================================================
print("\n--- 8. HEXADEZIMALE POSITIONEN ---")

print("Signifikante Positionen in Hex:")
for name, info in significant_positions.items():
    row, col = info["row"], info["col"]
    pos = row * 128 + col
    print(f"  {info['event'][:30]}:")
    print(f"    Pos: {pos} = 0x{pos:04X}")
    print(f"    Row: {row} = 0x{row:02X}")
    print(f"    Col: {col} = 0x{col:02X}")

# =============================================================================
# 9. XOR-ANALYSE DER POSITIONS-WERTE
# =============================================================================
print("\n--- 9. XOR-ANALYSE DER SIGNIFIKANTEN POSITIONEN ---")

for name, info in significant_positions.items():
    row, col = info["row"], info["col"]
    value = matrix[row][col]

    # XOR mit 127
    xor127 = (value ^ 127) & 0x7F
    ch = chr(xor127) if 32 <= xor127 <= 126 else '.'

    print(f"\n{info['event']}:")
    print(f"  Wert: {value}")
    print(f"  XOR 127: {xor127} = '{ch}'")

    # XOR der Position selbst
    row_xor_col = row ^ col
    print(f"  Row XOR Col: {row} ^ {col} = {row_xor_col}")

# =============================================================================
# 10. FAZIT
# =============================================================================
print("\n" + "=" * 70)
print("FAZIT: SIGNIFIKANTE DATEN")
print("=" * 70)

print(f"""
GEFUNDENE SIGNIFIKANTE DATEN:

1. OVERFLOW-BUG (2010-08-15):
   - Position: [39,78]
   - Einer der wichtigsten Bitcoin-Bugs
   - 184 Milliarden BTC aus dem Nichts
   - Innerhalb 5 Stunden gefixt

2. SATOSHIS LETZTER FORUMPOST (2010-12-12):
   - Position: [68,47]
   - 12 Tage vor seinem Verschwinden
   - Markiert das Ende der Satoshi-Ära

INTERPRETATION:
- Die Matrix enthält Bitcoin-historische Timestamps
- Zwei kritische Ereignisse wurden gefunden
- Die Positionen könnten absichtlich gewählt sein
- Weitere Analyse der umliegenden Werte empfohlen
""")

# Speichere Ergebnisse
output = {
    "significant_dates_found": [
        {
            "event": "Overflow-Bug",
            "date": "2010-08-15",
            "position": [39, 78],
            "bitcoin_block": 74638,
            "significance": "Integer overflow created 184B BTC"
        },
        {
            "event": "Satoshi's Last Forum Post",
            "date": "2010-12-12",
            "position": [68, 47],
            "significance": "End of Satoshi era"
        }
    ],
    "position_analysis": {
        "quadrant_distribution": quadrants,
        "symmetric_pairs": symmetric_pairs // 2,
        "row11_timestamps": len(row11_timestamps)
    }
}

output_path = script_dir / "SIGNIFICANT_DATES_ANALYSIS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse gespeichert: {output_path}")
