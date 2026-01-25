#!/usr/bin/env python3
"""
CFB Puzzle - Alle 20 Qubic IDs ableiten

Verwendet QubiPy um aus den Private Keys die Qubic IDs abzuleiten.
"""

import json
import sys

# QubiPy import
from qubipy.crypto.utils import (
    get_public_key_from_private_key,
    get_identity_from_public_key
)

# Die 40 Zahlen aus dem CFB Puzzle
numbers = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]
coords = [(numbers[i], numbers[i+1]) for i in range(0, 40, 2)]

print("=" * 80)
print("CFB PUZZLE - ALLE 20 QUBIC IDS ABLEITEN (mit QubiPy)")
print("=" * 80)

# Lade matrix_cartography.json
with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json', 'r') as f:
    cartography = json.load(f)

print(f"\nMatrix cartography geladen: {len(cartography)} Einträge")

def derive_identity(privkey_hex):
    """Leite Qubic Identity aus Private Key ab."""
    privkey_bytes = bytes.fromhex(privkey_hex)
    pubkey = get_public_key_from_private_key(privkey_bytes)
    identity = get_identity_from_public_key(pubkey)
    return identity

# Sammle alle Ergebnisse
results = []

print("\n" + "=" * 80)
print("ALLE 20 CFB PUZZLE KOORDINATEN -> QUBIC IDS")
print("=" * 80)

for i, (x, y) in enumerate(coords, 1):
    key = f"{x},{y}"
    note = ""
    if x + y == 137:
        note = "⭐ ENTRY (137)"
    elif x + y == 121:
        note = "⭐ EXIT (121)"
    elif (x, y) == (6, 33):
        note = "⭐ CORE"

    if key in cartography:
        private_key = cartography[key]
        identity = derive_identity(private_key)

        result = {
            "pair": i,
            "coords": [x, y],
            "sum": x + y,
            "key": key,
            "private_key": private_key,
            "identity": identity,
            "note": note
        }

        print(f"\n{'='*70}")
        print(f"Paar {i:2d}: ({x:2d}, {y:2d}) = Summe {x+y:3d} {note}")
        print(f"Identity: {identity}")
        print(f"PrivKey:  {private_key[:32]}...")

        results.append(result)
    else:
        print(f"\nPaar {i:2d}: ({x:2d}, {y:2d}) = NICHT GEFUNDEN")
        results.append({
            "pair": i,
            "coords": [x, y],
            "sum": x + y,
            "key": None,
            "private_key": None,
            "identity": None,
            "note": "NOT_FOUND"
        })

# Speichere Ergebnisse
output = {
    "total_pairs": 20,
    "found": len([r for r in results if r.get("private_key")]),
    "pairs": results,
    "identities_list": [r["identity"] for r in results if r.get("identity")]
}

with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/CFB_ALL_20_IDENTITIES.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\n" + "=" * 80)
print("ZUSAMMENFASSUNG - ALLE 20 QUBIC IDs")
print("=" * 80)

print("\nDie vollständige Liste der CFB-Puzzle Qubic IDs:")
print("-" * 70)
for r in results:
    if r.get("identity"):
        note = r.get("note", "")
        print(f"Paar {r['pair']:2d}: {r['identity']} {note}")

print("\n" + "=" * 80)
print(f"Ergebnisse gespeichert in: CFB_ALL_20_IDENTITIES.json")
print(f"Gefunden: {output['found']}/20 Paare")
print("=" * 80)
