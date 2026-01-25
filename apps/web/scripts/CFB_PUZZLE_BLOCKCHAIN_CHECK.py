#!/usr/bin/env python3
"""
CFB Puzzle - Blockchain Verification

Die vielversprechendsten Adressen auf der Bitcoin-Blockchain prüfen.
"""

import requests
import json
import time
import hashlib

base58_alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

numbers = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

def to_base58_mod(nums):
    return ''.join([base58_alphabet[n % 58] for n in nums])

def check_address(addr):
    """Prüfe eine Bitcoin-Adresse auf Blockchain.info"""
    try:
        url = f"https://blockchain.info/rawaddr/{addr}?limit=1"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "address": addr,
                "valid": True,
                "balance": data.get("final_balance", 0),
                "total_received": data.get("total_received", 0),
                "n_tx": data.get("n_tx", 0)
            }
        else:
            return {"address": addr, "valid": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"address": addr, "valid": False, "error": str(e)}

print("=" * 70)
print("CFB PUZZLE - BLOCKCHAIN VERIFICATION")
print("=" * 70)

# Generiere alle Kandidaten
content = numbers[2:-2]  # 36 Zahlen
content_b58 = to_base58_mod(content)
all_b58 = to_base58_mod(numbers)

candidates = [
    # Die 36-Zeichen Adresse in verschiedenen Varianten
    ("Inhalt 36 direkt", content_b58),
    ("Erste 34 vom Inhalt", content_b58[:34]),
    ("Letzte 34 vom Inhalt", content_b58[2:]),
    ("Mittlere 34 vom Inhalt", content_b58[1:35]),

    # Mit 1 am Anfang (Legacy)
    ("1 + erste 33 vom Inhalt", "1" + content_b58[:33]),
    ("1 + letzte 33 vom Inhalt", "1" + content_b58[3:]),

    # Mit 3 am Anfang (P2SH)
    ("3 + erste 33 vom Inhalt", "3" + content_b58[:33]),

    # Die 40-Zeichen Variante
    ("Alle 40 erste 34", all_b58[:34]),
    ("1 + erste 33 von allen", "1" + all_b58[:33]),
]

# Spezielle Kombinationen basierend auf der Struktur
# PREFIX = 137, SUFFIX = 121
# Was wenn wir "1" als ersten Buchstaben und dann die Zahlen nehmen?

# Die Zahl 3 ist an Position 2 - könnte "1CF..." bedeuten?
# 1 = Position 1 in Base58, C = Position 12 in Base58, F = Position 15
print("\n1. SPEZIELLE STRUKTUR-BASIERTE ADRESSEN:")

# 1CFB... Adresse?
# In Base58: 1=1, C=12, F=14, B=11
# Unsere Zahlen: 45(n), 92(verschlüsselt->34=b), 3(4), ...
print(f"   Suche nach 1CFB-ähnlichen Mustern...")

# Die erste Zahl mod 58 = 45 -> 'n'
# Was wenn wir nach "1" suchen und die richtige Startposition finden?
for i in range(len(numbers) - 33):
    subset = numbers[i:i+33]
    addr = "1" + to_base58_mod(subset)
    if addr.startswith("1CF"):
        print(f"   GEFUNDEN: Position {i}: {addr}")
        candidates.append((f"1CF ab Position {i}", addr))

# Die CFB^9 Werte als Teil einer Adresse
cfb9_values = [84, 16, 9, 60, 27, 5, 70, 22, 33]
cfb9_b58 = to_base58_mod(cfb9_values)
print(f"\n   CFB^9 Werte: {cfb9_values}")
print(f"   Als Base58: {cfb9_b58}")

print("\n2. PRÜFE KANDIDATEN AUF DER BLOCKCHAIN:")
print("-" * 70)

results = []
for name, addr in candidates:
    print(f"\n   Prüfe: {name}")
    print(f"   Adresse: {addr}")

    # Nur prüfen wenn die Länge stimmt (26-35 für Bitcoin)
    if 26 <= len(addr) <= 35:
        result = check_address(addr)
        results.append({"name": name, **result})

        if result.get("valid"):
            print(f"   ✓ GÜLTIG! Balance: {result['balance']} satoshi, TX: {result['n_tx']}")
            if result['n_tx'] > 0:
                print(f"   ⭐ ADRESSE HAT TRANSAKTIONEN!")
        else:
            print(f"   ✗ Ungültig oder nicht gefunden: {result.get('error', 'unknown')}")

        time.sleep(0.5)  # Rate limiting
    else:
        print(f"   ⚠ Übersprungen - Länge {len(addr)} nicht im gültigen Bereich")
        results.append({"name": name, "address": addr, "valid": False, "error": "Invalid length"})

# Zusätzlich: Bekannte CFB-Adressen prüfen
print("\n3. BEKANNTE CFB-VERWANDTE ADRESSEN:")
known_addresses = [
    "1CFBdvaiKgGiVrmPqpDYvHTAaqGcdGCPZ4",
    "1CFBNFP3SfYPhwwPJEBLfhcWdvZ39ipccL",
]

for addr in known_addresses:
    print(f"\n   Prüfe bekannte: {addr}")
    result = check_address(addr)
    if result.get("valid"):
        print(f"   ✓ Balance: {result['balance']} satoshi, TX: {result['n_tx']}")
    else:
        print(f"   ✗ {result.get('error')}")
    time.sleep(0.5)

# Vergleiche unsere dekodierte Adresse mit bekannten
print("\n4. VERGLEICH MIT BEKANNTEN ADRESSEN:")
decoded = content_b58[:34]
for known in known_addresses:
    similarity = sum(1 for a, b in zip(decoded, known) if a == b)
    print(f"   {decoded} vs")
    print(f"   {known}")
    print(f"   Ähnlichkeit: {similarity}/{min(len(decoded), len(known))} Zeichen")

# Zusammenfassung
print("\n" + "=" * 70)
print("ZUSAMMENFASSUNG")
print("=" * 70)

valid_results = [r for r in results if r.get("valid")]
with_tx = [r for r in valid_results if r.get("n_tx", 0) > 0]

print(f"\nGeprüfte Adressen: {len(results)}")
print(f"Gültige Adressen: {len(valid_results)}")
print(f"Mit Transaktionen: {len(with_tx)}")

if with_tx:
    print("\n⭐ ADRESSEN MIT TRANSAKTIONEN:")
    for r in with_tx:
        print(f"   {r['name']}: {r['address']}")
        print(f"   Balance: {r['balance']} sat, TX: {r['n_tx']}")

# Speichere Ergebnisse
with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/CFB_PUZZLE_BLOCKCHAIN_RESULTS.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nErgebnisse gespeichert!")
