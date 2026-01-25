#!/usr/bin/env python3
"""
Extended Anna-Matrix Lookup for Patoshi CFB Addresses
"""

import json

# Lade Anna-Matrix
with open('public/data/anna-matrix.json', 'r') as f:
    anna_data = json.load(f)

matrix = anna_data['matrix']
print(f"Anna-Matrix Dimensionen: {len(matrix)} x {len(matrix[0])}")

# Lade CFB Analyse
with open('scripts/PATOSHI_CFB_ANALYSIS.json', 'r') as f:
    cfb_data = json.load(f)

# CFB Zahlen
CFB_NUMBERS = [27, 121, 2299, 137, 19, 47, 576, 676, 283]

print("\n=== ANNA-MATRIX LOOKUPS FUER TOP CFB-ADRESSEN ===\n")

def get_anna_value(block, matrix):
    """Hole Anna-Matrix Wert fuer einen Block"""
    row = block // 128
    col = block % 128
    if row < len(matrix) and col < len(matrix[0]):
        return matrix[row][col], row, col
    return None, row, col

# Wichtigste Adressen
key_addresses = [
    {"address": "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg", "block": 264, "note": "EXAKT 1CFB PREFIX"},
    {"address": "16J8NLMTLc1X8tqTE3q2nPCngqtYW1orvG", "block": 19018, "note": "Score 8"},
    {"address": "1LNKBdzwXmisa67qtYCofsZWwgZW2wewmn", "block": 173, "note": "Score 7"},
    {"address": "1H5eAaBYa5dK2TTnPpnBk591hF8WxjWqtL", "block": 721, "note": "Score 7"},
    {"address": "1LWVS3vYAwLFk4UqFwFDNcECEDKvMTnBZV", "block": 805, "note": "Score 7"},
]

# Fuege alle 1CF Adressen hinzu
for addr in cfb_data['prefix_patterns']['1CF']:
    if addr['address'] not in [a['address'] for a in key_addresses]:
        key_addresses.append({
            "address": addr['address'],
            "block": addr['block'],
            "note": "1CF Prefix"
        })

# Fuege alle 1QB Adressen hinzu
for addr in cfb_data['prefix_patterns']['1QB']:
    key_addresses.append({
        "address": addr['address'],
        "block": addr['block'],
        "note": "1QB Prefix"
    })

results = []

for entry in key_addresses:
    addr = entry['address']
    block = entry['block']
    note = entry['note']

    anna_val, row, col = get_anna_value(block, matrix)

    # Pruefe CFB-Beziehungen des Anna-Werts
    cfb_relations = []
    if anna_val is not None:
        for n in CFB_NUMBERS:
            if anna_val % n == 0:
                cfb_relations.append(f"{n}*{anna_val//n}")
            elif anna_val == n:
                cfb_relations.append(f"={n}")
            elif (anna_val + n) in CFB_NUMBERS:
                cfb_relations.append(f"+{n}={anna_val+n}")

    result = {
        "address": addr,
        "block": block,
        "note": note,
        "anna_coords": f"({row},{col})",
        "anna_value": anna_val,
        "cfb_relations": cfb_relations
    }
    results.append(result)

    print(f"Adresse: {addr}")
    print(f"  Block: {block} -> Anna-Koordinaten: ({row}, {col})")
    print(f"  Anna-Matrix Wert: {anna_val}")
    if cfb_relations:
        print(f"  CFB-Relationen: {', '.join(cfb_relations)}")
    print(f"  Notiz: {note}")
    print()

# Finde Blocks mit besonders interessanten Anna-Werten
print("\n=== BLOCKS MIT CFB-ZAHLEN ALS ANNA-WERTE ===\n")

for row in range(min(128, len(matrix))):
    for col in range(min(128, len(matrix[0]))):
        val = matrix[row][col]
        block = row * 128 + col

        if val in CFB_NUMBERS:
            # Pruefe ob dieser Block eine Patoshi-Adresse hat
            for cand in cfb_data['top_cfb_candidates'][:100]:
                if cand['block'] == block:
                    print(f"MATCH! Block {block} ({row},{col}): Anna-Wert = {val} (CFB-Zahl)")
                    print(f"  Adresse: {cand['address']}")
                    break

# Speichere erweiterte Analyse
extended_results = {
    "key_addresses_with_anna": results,
    "cfb_numbers": CFB_NUMBERS,
    "summary": {
        "total_1cf_addresses": len(cfb_data['prefix_patterns']['1CF']),
        "total_1qb_addresses": len(cfb_data['prefix_patterns']['1QB']),
        "top_cfb_candidate": "16J8NLMTLc1X8tqTE3q2nPCngqtYW1orvG (Score 8)",
        "critical_find": "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg in Block 264 (Letters only, 1CFB prefix)"
    }
}

with open('scripts/PATOSHI_CFB_ANNA_EXTENDED.json', 'w') as f:
    json.dump(extended_results, f, indent=2)

print("\nErweiterte Analyse gespeichert in: scripts/PATOSHI_CFB_ANNA_EXTENDED.json")

# Besondere Analyse fuer Block 264
print("\n=== TIEFENANALYSE BLOCK 264 ===")
print(f"Block 264 = 2 * 132 = 4 * 66 = 8 * 33 = 11 * 24")
print(f"264 = 11 * 24 (11^2=121, 24^2=576 - beides CFB-Zahlen!)")
print(f"264 mod 27 = {264 % 27}")
print(f"264 mod 121 = {264 % 121}")
print(f"264 mod 137 = {264 % 137}")

anna_264, r, c = get_anna_value(264, matrix)
print(f"\nAnna-Matrix Position (2, 8): Wert = {anna_264}")

# Umgebung analysieren
print("\nAnna-Matrix Umgebung um (2, 8):")
for dr in range(-2, 3):
    row_vals = []
    for dc in range(-2, 3):
        nr, nc = 2 + dr, 8 + dc
        if 0 <= nr < len(matrix) and 0 <= nc < len(matrix[0]):
            row_vals.append(f"{matrix[nr][nc]:4d}")
        else:
            row_vals.append("   -")
    print(" ".join(row_vals))
