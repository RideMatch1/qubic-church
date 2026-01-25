#!/usr/bin/env python3
"""
CFB Puzzle - Alle 20 Qubic IDs ableiten

Verwendet QubiPy um aus den Private Keys die Qubic IDs abzuleiten.
"""

import json
import sys

# Die 40 Zahlen aus dem CFB Puzzle
numbers = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]
coords = [(numbers[i], numbers[i+1]) for i in range(0, 40, 2)]

print("=" * 80)
print("CFB PUZZLE - ALLE 20 QUBIC IDS ABLEITEN")
print("=" * 80)

# Lade matrix_cartography.json
with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json', 'r') as f:
    cartography = json.load(f)

print(f"\nMatrix cartography geladen: {len(cartography)} Einträge")

# Versuche QubiPy zu importieren
try:
    from qubipy.crypto import get_identity_from_priv_key
    QUBIPY_AVAILABLE = True
    print("QubiPy verfügbar - kann IDs ableiten!")
except ImportError:
    QUBIPY_AVAILABLE = False
    print("QubiPy nicht verfügbar - zeige nur Private Keys")

# Sammle alle Ergebnisse
results = []

print("\n" + "=" * 80)
print("ALLE 20 CFB PUZZLE KOORDINATEN -> QUBIC IDS")
print("=" * 80)

for i, (x, y) in enumerate(coords, 1):
    key = f"{x},{y}"
    note = ""
    if x + y == 137:
        note = "ENTRY"
    elif x + y == 121:
        note = "EXIT"
    elif (x, y) == (6, 33):
        note = "CORE"

    if key in cartography:
        private_key = cartography[key]

        result = {
            "pair": i,
            "coords": [x, y],
            "sum": x + y,
            "key": key,
            "private_key": private_key,
            "note": note
        }

        if QUBIPY_AVAILABLE:
            try:
                # QubiPy erwartet bytes
                if isinstance(private_key, str):
                    priv_bytes = bytes.fromhex(private_key)
                else:
                    priv_bytes = private_key

                identity = get_identity_from_priv_key(priv_bytes)
                result["identity"] = identity
                print(f"\nPaar {i:2d}: ({x:2d}, {y:2d}) = {x+y:3d} {note}")
                print(f"         ID: {identity}")
            except Exception as e:
                result["identity"] = None
                result["error"] = str(e)
                print(f"\nPaar {i:2d}: ({x:2d}, {y:2d}) = {x+y:3d} {note}")
                print(f"         Fehler: {e}")
        else:
            print(f"\nPaar {i:2d}: ({x:2d}, {y:2d}) = {x+y:3d} {note}")
            print(f"         Key: {private_key[:40]}...")

        results.append(result)
    else:
        print(f"\nPaar {i:2d}: ({x:2d}, {y:2d}) = NICHT GEFUNDEN")
        results.append({
            "pair": i,
            "coords": [x, y],
            "sum": x + y,
            "key": None,
            "private_key": None,
            "note": "NOT_FOUND"
        })

# Speichere Ergebnisse
output = {
    "total_pairs": 20,
    "found": len([r for r in results if r.get("private_key")]),
    "qubipy_available": QUBIPY_AVAILABLE,
    "pairs": results
}

with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/CFB_ALL_20_IDENTITIES.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\n" + "=" * 80)
print("ERGEBNISSE GESPEICHERT")
print("=" * 80)
print(f"\nGefunden: {output['found']}/20 Paare")
print(f"QubiPy: {'Verfügbar' if QUBIPY_AVAILABLE else 'Nicht verfügbar'}")
print(f"Datei: CFB_ALL_20_IDENTITIES.json")
