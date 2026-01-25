#!/usr/bin/env python3
"""
CFB Puzzle + Master Key = Qubic ID?

Kombiniere:
- CFB Puzzle dekodiert: TODZOGDDGHSWRWJJGLYQVCHPSHKTWEJRUFIPUBEN (40 Zeichen)
- Master Key: SKWIKENGRZNXRPLXWRHP (20 Zeichen)
- Zusammen: 60 Zeichen = Qubic ID Länge!
"""

import hashlib
import requests
import json
import time

# Die beiden Fragmente
cfb_puzzle = "TODZOGDDGHSWRWJJGLYQVCHPSHKTWEJRUFIPUBEN"  # 40 Zeichen
master_key = "SKWIKENGRZNXRPLXWRHP"  # 20 Zeichen

print("=" * 70)
print("CFB PUZZLE + MASTER KEY = QUBIC ID?")
print("=" * 70)

print(f"\n1. DIE BEIDEN FRAGMENTE:")
print(f"   CFB Puzzle: {cfb_puzzle} ({len(cfb_puzzle)} Zeichen)")
print(f"   Master Key: {master_key} ({len(master_key)} Zeichen)")
print(f"   Zusammen:   {len(cfb_puzzle) + len(master_key)} Zeichen (Qubic ID = 60)")

# Alle möglichen Kombinationen
print(f"\n2. MÖGLICHE KOMBINATIONEN:")

combinations = [
    ("CFB + Master", cfb_puzzle + master_key),
    ("Master + CFB", master_key + cfb_puzzle),
    ("Interleaved 1", ''.join([a+b for a,b in zip(cfb_puzzle[:20], master_key)] + list(cfb_puzzle[20:]))),
    ("Interleaved 2", ''.join([b+a for a,b in zip(cfb_puzzle[:20], master_key)] + list(cfb_puzzle[20:]))),
]

# Füge auch Varianten mit anderen dekodierten Strings hinzu
other_decodings = {
    "X+Y mod 26": "HCUGNONSROXWZDAAZXVR",  # 20 Zeichen
    "XOR mod 26": "JAAYNOVAJIHUZTGUZZFN",  # 20 Zeichen
}

for name, decoded in other_decodings.items():
    combinations.append((f"Master + {name}", master_key + decoded + cfb_puzzle[:20]))
    combinations.append((f"{name} + Master", decoded + master_key + cfb_puzzle[:20]))

# Prüfe auch die 55-Zeichen Seeds (Qubic Seeds sind 55 lowercase)
print("\n3. ALS QUBIC SEEDS (55 Zeichen, lowercase):")

seed_candidates = [
    ("CFB ohne letzte 5", cfb_puzzle[:-5].lower()),
    ("CFB ohne erste 5", cfb_puzzle[5:].lower() + cfb_puzzle[:20].lower()),
    ("Master + CFB erste 35", (master_key + cfb_puzzle[:35]).lower()),
    ("CFB erste 35 + Master", (cfb_puzzle[:35] + master_key).lower()),
]

# Die originalen Zahlen für alternative Dekodierungen
numbers = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

# Konvertiere zu lowercase a-z (mod 26)
cfb_lowercase = ''.join([chr((n % 26) + ord('a')) for n in numbers])
print(f"\n   CFB als lowercase: {cfb_lowercase} ({len(cfb_lowercase)} Zeichen)")

# Master Key lowercase
master_lower = master_key.lower()
print(f"   Master Key lowercase: {master_lower}")

# Kombinationen für Seeds
seed_combinations = [
    ("CFB_lower + Master_lower[:15]", cfb_lowercase + master_lower[:15]),
    ("Master_lower + CFB_lower[:35]", master_lower + cfb_lowercase[:35]),
    ("CFB_lower[:35] + Master_lower", cfb_lowercase[:35] + master_lower),
]

print("\n4. ALLE QUBIC ID KANDIDATEN (60 Zeichen, uppercase):")
print("-" * 70)

valid_candidates = []
for name, combo in combinations:
    # Stelle sicher, dass es 60 Zeichen sind und nur A-Z
    combo_upper = combo.upper()
    if len(combo_upper) == 60 and combo_upper.isalpha():
        print(f"\n   {name}:")
        print(f"   {combo_upper}")
        valid_candidates.append({"name": name, "id": combo_upper})
    else:
        print(f"\n   {name}: Länge {len(combo_upper)} (übersprungen)")

# Spezielle Kombinationen die genau 60 Zeichen ergeben
print("\n5. SPEZIELLE 60-ZEICHEN KOMBINATIONEN:")

# CFB Puzzle ist 40, Master Key ist 20 -> perfekt!
combo1 = cfb_puzzle + master_key
combo2 = master_key + cfb_puzzle

print(f"\n   Kombination 1: CFB + Master")
print(f"   {combo1}")
print(f"   Länge: {len(combo1)}")

print(f"\n   Kombination 2: Master + CFB")
print(f"   {combo2}")
print(f"   Länge: {len(combo2)}")

# Die X+Y und XOR Strings haben auch 20 Zeichen!
xy_string = "HCUGNONSROXWZDAAZXVR"  # 20 Zeichen
xor_string = "JAAYNOVAJIHUZTGUZZFN"  # 20 Zeichen

combo3 = cfb_puzzle + xy_string
combo4 = cfb_puzzle + xor_string
combo5 = xy_string + cfb_puzzle
combo6 = xor_string + cfb_puzzle

print(f"\n   Kombination 3: CFB + X+Y String")
print(f"   {combo3}")

print(f"\n   Kombination 4: CFB + XOR String")
print(f"   {combo4}")

print(f"\n   Kombination 5: X+Y + CFB")
print(f"   {combo5}")

print(f"\n   Kombination 6: XOR + CFB")
print(f"   {combo6}")

# Alle Kandidaten sammeln
all_candidates = [
    ("CFB + Master", combo1),
    ("Master + CFB", combo2),
    ("CFB + X+Y", combo3),
    ("CFB + XOR", combo4),
    ("X+Y + CFB", combo5),
    ("XOR + CFB", combo6),
]

# Prüfe auf Qubic Blockchain
print("\n6. BLOCKCHAIN VERIFICATION:")
print("-" * 70)

def check_qubic_id(identity):
    """Prüfe eine Qubic ID auf dem Explorer"""
    try:
        url = f"https://rpc.qubic.org/v1/balances/{identity}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "valid": True,
                "balance": data.get("balance", {}).get("balance", 0),
                "data": data
            }
        return {"valid": False, "status": response.status_code}
    except Exception as e:
        return {"valid": False, "error": str(e)}

results = []
for name, qubic_id in all_candidates:
    print(f"\n   Prüfe: {name}")
    print(f"   ID: {qubic_id}")

    if len(qubic_id) == 60 and qubic_id.isalpha() and qubic_id.isupper():
        result = check_qubic_id(qubic_id)
        results.append({"name": name, "id": qubic_id, **result})

        if result.get("valid"):
            balance = result.get("balance", 0)
            print(f"   ✓ GÜLTIGE ID! Balance: {balance}")
            if balance > 0:
                print(f"   ⭐⭐⭐ HAT BALANCE! ⭐⭐⭐")
        else:
            print(f"   ✗ Ungültig oder leer: {result}")

        time.sleep(0.5)
    else:
        print(f"   ⚠ Übersprungen (Länge: {len(qubic_id)}, Alpha: {qubic_id.isalpha()})")

# Auch bekannte Qubic IDs aus früheren Analysen testen
print("\n7. VERGLEICH MIT BEKANNTEN QUBIC IDS:")
known_ids = [
    "HEVCNLWFNUIBPFFMBZWVCQIKLNNAAJWLSESNYGWHGDEGBKOZMLZNQESDDYRM",
    "AAQHJEYCCOQJYFXQFAYTWJBYYENAUUNXGUMJTIVYCHQXEBYXPSHWLIJERSMB",
]

for known in known_ids:
    for name, candidate in all_candidates:
        # Berechne Ähnlichkeit
        matches = sum(1 for a, b in zip(known, candidate) if a == b)
        if matches > 10:  # Nur wenn mehr als 10 Zeichen übereinstimmen
            print(f"   {name} vs bekannte ID: {matches}/60 Übereinstimmungen")

# Zusammenfassung
print("\n" + "=" * 70)
print("ZUSAMMENFASSUNG")
print("=" * 70)
print(f"""
CFB Puzzle Dekodierung: {cfb_puzzle} (40 Zeichen)
Master Key:             {master_key} (20 Zeichen)
X+Y Dekodierung:        {xy_string} (20 Zeichen)
XOR Dekodierung:        {xor_string} (20 Zeichen)

BESTE QUBIC ID KANDIDATEN (60 Zeichen):
1. {combo1}
2. {combo2}
3. {combo3}
4. {combo4}
""")

# Speichere Ergebnisse
output = {
    "cfb_puzzle": cfb_puzzle,
    "master_key": master_key,
    "xy_string": xy_string,
    "xor_string": xor_string,
    "candidates": all_candidates,
    "blockchain_results": results
}

with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/CFB_QUBIC_ID_RESULTS.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)
print("\nErgebnisse gespeichert!")
