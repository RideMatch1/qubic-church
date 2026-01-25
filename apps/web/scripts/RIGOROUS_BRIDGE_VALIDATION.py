#!/usr/bin/env python3
"""
===============================================================================
          RIGOROSE BRIDGE-VALIDIERUNG
===============================================================================

Vollständige Validierung und Verifikation ALLER Behauptungen:

1. Block 264 Hash160 Berechnung EXAKT prüfen
2. 1CFB Adresse Hash160 EXAKT prüfen
3. Byte-für-Byte Vergleich mit Erklärung
4. Statistische Signifikanz berechnen
5. Anomalie-Mapping JEDE Position validieren
6. Falsch-Positiv Prüfung
7. Kontrollgruppe testen
8. Reproduzierbarkeit sicherstellen
"""

import json
import hashlib
import struct
import random
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from collections import Counter
import math

print("=" * 80)
print("         RIGOROSE BRIDGE-VALIDIERUNG")
print("         Jede Behauptung wird exakt geprüft")
print("=" * 80)

# =============================================================================
# KRYPTOGRAPHISCHE GRUNDFUNKTIONEN (VERIFIZIERT)
# =============================================================================

def sha256(data: bytes) -> bytes:
    """SHA256 Hash - Standard Bitcoin"""
    return hashlib.sha256(data).digest()

def ripemd160(data: bytes) -> bytes:
    """RIPEMD160 Hash - Standard Bitcoin"""
    return hashlib.new('ripemd160', data).digest()

def hash160(data: bytes) -> bytes:
    """Hash160 = RIPEMD160(SHA256(x)) - Standard Bitcoin"""
    return ripemd160(sha256(data))

def double_sha256(data: bytes) -> bytes:
    """Double SHA256 - Bitcoin Checksum"""
    return sha256(sha256(data))

def pubkey_to_hash160(pubkey_hex: str) -> bytes:
    """
    Konvertiere Public Key zu Hash160
    VERIFIZIERT gegen Bitcoin Standard
    """
    try:
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        return hash160(pubkey_bytes)
    except Exception as e:
        print(f"  FEHLER bei pubkey_to_hash160: {e}")
        return b''

def hash160_to_address(h160: bytes, version: int = 0x00) -> str:
    """
    Konvertiere Hash160 zu Bitcoin Adresse (Base58Check)
    VERIFIZIERT gegen Bitcoin Standard
    """
    # Version Byte + Hash160
    payload = bytes([version]) + h160

    # Checksum = erste 4 Bytes von Double SHA256
    checksum = double_sha256(payload)[:4]

    # Payload + Checksum
    address_bytes = payload + checksum

    # Base58 Encoding
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    # Konvertiere zu Integer
    num = int.from_bytes(address_bytes, 'big')

    # Base58 Encode
    result = ''
    while num > 0:
        num, rem = divmod(num, 58)
        result = alphabet[rem] + result

    # Leading zeros als '1' kodieren
    for byte in address_bytes:
        if byte == 0:
            result = '1' + result
        else:
            break

    return result

def address_to_hash160(address: str) -> bytes:
    """
    Dekodiere Bitcoin Adresse zu Hash160
    VERIFIZIERT gegen Bitcoin Standard
    """
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    # Base58 Decode
    num = 0
    for char in address:
        num = num * 58 + alphabet.index(char)

    # Zu Bytes konvertieren (25 Bytes: 1 version + 20 hash160 + 4 checksum)
    result = []
    while num > 0:
        result.append(num % 256)
        num //= 256

    # Leading zeros
    for char in address:
        if char == '1':
            result.append(0)
        else:
            break

    decoded = bytes(reversed(result))

    # Padding falls nötig
    while len(decoded) < 25:
        decoded = b'\x00' + decoded

    # Extrahiere Hash160 (skip version byte, remove checksum)
    return decoded[1:21]

# =============================================================================
# VALIDIERUNG 1: Block 264 Hash160
# =============================================================================

def validate_block_264():
    """EXAKTE Validierung von Block 264"""
    print("\n" + "=" * 60)
    print("VALIDIERUNG 1: Block 264 Hash160 Berechnung")
    print("=" * 60)

    # Lade Patoshi Daten
    with open("apps/web/public/data/patoshi-addresses.json") as f:
        data = json.load(f)

    # Finde Block 264
    block_264 = None
    for record in data.get('records', []):
        if record.get('blockHeight') == 264:
            block_264 = record
            break

    if not block_264:
        print("  FEHLER: Block 264 nicht gefunden!")
        return {"valid": False, "error": "Block 264 nicht gefunden"}

    pubkey = block_264.get('pubkey', '')

    print(f"\n  Block 264 Public Key (130 hex chars = 65 bytes uncompressed):")
    print(f"  {pubkey[:64]}")
    print(f"  {pubkey[64:]}")
    print(f"  Länge: {len(pubkey)} chars = {len(pubkey)//2} bytes")

    # Schritt 1: Pubkey zu Bytes
    pubkey_bytes = bytes.fromhex(pubkey)
    print(f"\n  Schritt 1: Pubkey zu Bytes")
    print(f"    Erste 10 Bytes: {pubkey_bytes[:10].hex()}")
    print(f"    Letzte 10 Bytes: {pubkey_bytes[-10:].hex()}")

    # Schritt 2: SHA256
    sha256_result = sha256(pubkey_bytes)
    print(f"\n  Schritt 2: SHA256(pubkey)")
    print(f"    {sha256_result.hex()}")

    # Schritt 3: RIPEMD160
    h160 = ripemd160(sha256_result)
    print(f"\n  Schritt 3: RIPEMD160(SHA256(pubkey)) = Hash160")
    print(f"    {h160.hex()}")

    # Schritt 4: Adresse
    address = hash160_to_address(h160)
    print(f"\n  Schritt 4: Base58Check Encoding")
    print(f"    Adresse: {address}")

    # Validierung
    print(f"\n  VALIDIERUNG:")
    print(f"    Hash160 erstes Byte: 0x{h160[0]:02X} = {h160[0]}")
    print(f"    Hash160 zweites Byte: 0x{h160[1]:02X} = {h160[1]}")

    is_0x7b = h160[0] == 0x7B
    is_0x7b58 = h160[0] == 0x7B and h160[1] == 0x58

    print(f"\n    Beginnt mit 0x7B? {is_0x7b} {'✓' if is_0x7b else '✗'}")
    print(f"    Beginnt mit 0x7B58? {is_0x7b58} {'✓' if is_0x7b58 else '✗'}")

    return {
        "valid": True,
        "pubkey": pubkey,
        "hash160": h160.hex(),
        "address": address,
        "first_byte": h160[0],
        "second_byte": h160[1],
        "is_0x7b": is_0x7b,
        "is_0x7b58": is_0x7b58,
    }

# =============================================================================
# VALIDIERUNG 2: 1CFB Adresse Hash160
# =============================================================================

def validate_1cfb_address():
    """EXAKTE Validierung der 1CFB Adresse"""
    print("\n" + "=" * 60)
    print("VALIDIERUNG 2: 1CFB Adresse Hash160 Berechnung")
    print("=" * 60)

    cfb_address = "1CFBjSVcKwVmsLJeKAmHcZUpiFjBZchPDV"

    print(f"\n  1CFB Adresse: {cfb_address}")
    print(f"  Länge: {len(cfb_address)} Zeichen")

    # Dekodiere Adresse
    h160 = address_to_hash160(cfb_address)

    print(f"\n  Schritt 1: Base58 Decode")
    print(f"    Hash160: {h160.hex()}")
    print(f"    Länge: {len(h160)} bytes")

    # Validierung durch Rück-Kodierung
    reconstructed = hash160_to_address(h160)
    match = reconstructed == cfb_address

    print(f"\n  Schritt 2: Verifikation durch Rück-Kodierung")
    print(f"    Rekonstruiert: {reconstructed}")
    print(f"    Original: {cfb_address}")
    print(f"    Match: {match} {'✓' if match else '✗'}")

    print(f"\n  VALIDIERUNG:")
    print(f"    Hash160 erstes Byte: 0x{h160[0]:02X} = {h160[0]}")
    print(f"    Hash160 zweites Byte: 0x{h160[1]:02X} = {h160[1]}")

    is_0x7b = h160[0] == 0x7B
    is_0x7b58 = h160[0] == 0x7B and h160[1] == 0x58

    print(f"\n    Beginnt mit 0x7B? {is_0x7b} {'✓' if is_0x7b else '✗'}")
    print(f"    Beginnt mit 0x7B58? {is_0x7b58} {'✓' if is_0x7b58 else '✗'}")

    return {
        "valid": match,
        "address": cfb_address,
        "hash160": h160.hex(),
        "first_byte": h160[0],
        "second_byte": h160[1],
        "is_0x7b": is_0x7b,
        "is_0x7b58": is_0x7b58,
    }

# =============================================================================
# VALIDIERUNG 3: Byte-für-Byte Vergleich
# =============================================================================

def validate_byte_comparison(block264_result: Dict, cfb_result: Dict):
    """EXAKTER Byte-für-Byte Vergleich"""
    print("\n" + "=" * 60)
    print("VALIDIERUNG 3: Exakter Byte-für-Byte Vergleich")
    print("=" * 60)

    h160_264 = bytes.fromhex(block264_result["hash160"])
    h160_cfb = bytes.fromhex(cfb_result["hash160"])

    print(f"\n  Block 264: {h160_264.hex()}")
    print(f"  1CFB:      {h160_cfb.hex()}")

    print(f"\n  Byte | Block 264 | 1CFB      | Match")
    print(f"  " + "-" * 45)

    matching_bytes = 0
    matching_positions = []

    for i in range(20):
        b264 = h160_264[i]
        bcfb = h160_cfb[i]
        match = b264 == bcfb

        if match:
            matching_bytes += 1
            matching_positions.append(i)

        marker = "✓" if match else " "
        print(f"    {i:2d} |   0x{b264:02X}    |   0x{bcfb:02X}    | {marker}")

    print(f"\n  ZUSAMMENFASSUNG:")
    print(f"    Übereinstimmende Bytes: {matching_bytes}/20")
    print(f"    Positionen: {matching_positions}")

    # Berechne längste übereinstimmende Präfix-Länge
    prefix_match = 0
    for i in range(20):
        if h160_264[i] == h160_cfb[i]:
            prefix_match += 1
        else:
            break

    print(f"    Längster Präfix-Match: {prefix_match} Bytes")

    return {
        "matching_bytes": matching_bytes,
        "matching_positions": matching_positions,
        "prefix_match_length": prefix_match,
        "block264_hash160": h160_264.hex(),
        "cfb_hash160": h160_cfb.hex(),
    }

# =============================================================================
# VALIDIERUNG 4: Statistische Signifikanz
# =============================================================================

def validate_statistical_significance(prefix_match: int, total_0x7b: int, total_patoshi: int):
    """Berechne statistische Signifikanz"""
    print("\n" + "=" * 60)
    print("VALIDIERUNG 4: Statistische Signifikanz")
    print("=" * 60)

    print(f"\n  Daten:")
    print(f"    Patoshi Blocks gesamt: {total_patoshi:,}")
    print(f"    Blocks mit 0x7B Präfix: {total_0x7b}")
    print(f"    Präfix-Match Länge (Block 264 vs 1CFB): {prefix_match} Bytes")

    # Wahrscheinlichkeit für 1-Byte Match
    prob_1_byte = 1 / 256
    print(f"\n  Wahrscheinlichkeiten:")
    print(f"    1-Byte Match (0x7B): 1/256 = {prob_1_byte:.6f}")

    # Wahrscheinlichkeit für 2-Byte Match
    prob_2_byte = 1 / 65536
    print(f"    2-Byte Match (0x7B58): 1/65536 = {prob_2_byte:.10f}")

    # Erwartete Anzahl mit 0x7B Präfix
    expected_0x7b = total_patoshi / 256
    print(f"\n  Erwartungswerte:")
    print(f"    Erwartete Blocks mit 0x7B: {expected_0x7b:.1f}")
    print(f"    Tatsächliche Blocks mit 0x7B: {total_0x7b}")
    print(f"    Verhältnis: {total_0x7b / expected_0x7b:.2f}x")

    # Chi-Quadrat Test für 0x7B Verteilung
    chi_sq = ((total_0x7b - expected_0x7b) ** 2) / expected_0x7b
    print(f"\n  Chi-Quadrat (0x7B Verteilung): {chi_sq:.4f}")
    print(f"    (< 3.84 = nicht signifikant bei p=0.05)")

    # P-Wert für 2-Byte Match
    # Binomialverteilung: Wahrscheinlichkeit dass mindestens 1 von total_0x7b
    # auch das zweite Byte (0x58) hat
    prob_at_least_one_0x7b58 = 1 - (1 - 1/256) ** total_0x7b
    print(f"\n  P-Wert Analyse:")
    print(f"    P(mind. ein 0x7B58 in {total_0x7b} 0x7B-Blocks): {prob_at_least_one_0x7b58:.4f}")

    # Ist Block 264 speziell?
    print(f"\n  Ist Block 264 speziell?")
    print(f"    Block 264 ist der ERSTE 0x7B Block: Prüfen...")

    return {
        "prob_1_byte": prob_1_byte,
        "prob_2_byte": prob_2_byte,
        "expected_0x7b": expected_0x7b,
        "actual_0x7b": total_0x7b,
        "chi_square": chi_sq,
        "prefix_match_length": prefix_match,
    }

# =============================================================================
# VALIDIERUNG 5: Alle 0x7B Blocks prüfen
# =============================================================================

def validate_all_0x7b_blocks():
    """Validiere ALLE 0x7B Blocks und prüfe auf 0x7B58"""
    print("\n" + "=" * 60)
    print("VALIDIERUNG 5: Alle 0x7B Blocks analysieren")
    print("=" * 60)

    with open("apps/web/public/data/patoshi-addresses.json") as f:
        data = json.load(f)

    records = data.get('records', [])
    total = len(records)

    all_0x7b = []
    all_0x7b58 = []
    first_byte_distribution = Counter()

    print(f"\n  Analysiere {total:,} Patoshi Blocks...")

    for record in records:
        pubkey = record.get('pubkey', '')
        block = record.get('blockHeight', 0)

        if pubkey:
            h160 = pubkey_to_hash160(pubkey)
            if h160:
                first_byte_distribution[h160[0]] += 1

                if h160[0] == 0x7B:
                    entry = {
                        "block": block,
                        "hash160": h160.hex(),
                        "first_two_bytes": f"0x{h160[0]:02X}{h160[1]:02X}",
                        "is_0x7b58": h160[0] == 0x7B and h160[1] == 0x58,
                    }
                    all_0x7b.append(entry)

                    if h160[1] == 0x58:
                        all_0x7b58.append(entry)

    print(f"\n  Ergebnisse:")
    print(f"    Blocks mit 0x7B Präfix: {len(all_0x7b)}")
    print(f"    Blocks mit 0x7B58 Präfix: {len(all_0x7b58)}")

    if all_0x7b58:
        print(f"\n  Blocks mit 0x7B58 (wie 1CFB):")
        for entry in all_0x7b58:
            print(f"    Block {entry['block']}: {entry['hash160'][:20]}...")

    # Ist Block 264 der erste?
    sorted_0x7b = sorted(all_0x7b, key=lambda x: x['block'])
    if sorted_0x7b:
        first_0x7b = sorted_0x7b[0]
        print(f"\n  Erster 0x7B Block: {first_0x7b['block']}")
        print(f"    Block 264 ist erster? {first_0x7b['block'] == 264}")

    # Prüfe ob Block 264 in 0x7B58 Liste
    block_264_in_0x7b58 = any(e['block'] == 264 for e in all_0x7b58)
    print(f"\n  Block 264 hat 0x7B58 Präfix? {block_264_in_0x7b58}")

    return {
        "total_patoshi": total,
        "total_0x7b": len(all_0x7b),
        "total_0x7b58": len(all_0x7b58),
        "all_0x7b_blocks": all_0x7b,
        "all_0x7b58_blocks": all_0x7b58,
        "first_0x7b_block": sorted_0x7b[0] if sorted_0x7b else None,
        "block_264_has_0x7b58": block_264_in_0x7b58,
    }

# =============================================================================
# VALIDIERUNG 6: Anomalie-Mapping Verifikation
# =============================================================================

def validate_anomaly_mapping():
    """EXAKTE Validierung des Anomalie-Mappings"""
    print("\n" + "=" * 60)
    print("VALIDIERUNG 6: Anomalie → Patoshi Block Mapping")
    print("=" * 60)

    # Lade Anna Matrix
    with open("apps/web/public/data/anna-matrix.json") as f:
        anna_data = json.load(f)

    matrix = []
    for row in anna_data['matrix']:
        row_vals = []
        for v in row:
            if isinstance(v, str):
                try:
                    row_vals.append(int(v, 16) if len(v) == 8 else int(v))
                except:
                    row_vals.append(0)
            else:
                row_vals.append(int(v))
        matrix.append(row_vals)

    # Lade Patoshi Blocks
    with open("apps/web/public/data/patoshi-addresses.json") as f:
        patoshi_data = json.load(f)

    patoshi_blocks = {r.get('blockHeight', 0) for r in patoshi_data.get('records', [])}
    min_block = min(patoshi_blocks)
    max_block = max(patoshi_blocks)

    print(f"\n  Patoshi Block Range: {min_block} - {max_block}")

    # Anomalie-Positionen
    anomalies = [
        (19, 127), (20, 22), (21, 22), (22, 22), (23, 22), (24, 22),
        (25, 22), (26, 22), (27, 22), (28, 22), (29, 22), (30, 22),
        (31, 22), (32, 22), (48, 97), (50, 97), (51, 97), (53, 97),
        (54, 97), (55, 97), (56, 97), (57, 97), (58, 97), (59, 97),
        (60, 97), (60, 41), (61, 97), (61, 41), (62, 97), (62, 41),
        (62, 30), (63, 97), (63, 41), (63, 30),
    ]

    print(f"\n  Prüfe {len(anomalies)} Anomalie-Positionen...")
    print(f"\n  Position     | Wert  | Abs  | In Patoshi? | Block existiert?")
    print(f"  " + "-" * 60)

    valid_count = 0
    invalid_count = 0
    in_range_count = 0
    results = []

    for row, col in anomalies:
        if row >= len(matrix) or col >= len(matrix[0]):
            print(f"  ({row:2d},{col:3d})   | OUT OF BOUNDS")
            invalid_count += 1
            continue

        val = matrix[row][col]
        abs_val = abs(val)

        # Prüfe ob abs_val ein Patoshi Block ist
        is_patoshi = abs_val in patoshi_blocks
        in_range = min_block <= abs_val <= max_block

        if is_patoshi:
            valid_count += 1
            marker = "✓"
        elif in_range:
            in_range_count += 1
            marker = "~"  # Im Bereich aber nicht Patoshi
        else:
            invalid_count += 1
            marker = "✗"

        print(f"  ({row:2d},{col:3d})   | {val:+4d} | {abs_val:3d} | {marker:^11} | {is_patoshi}")

        results.append({
            "position": (row, col),
            "value": val,
            "abs_value": abs_val,
            "is_patoshi_block": is_patoshi,
            "in_range": in_range,
        })

    print(f"\n  ZUSAMMENFASSUNG:")
    print(f"    Exakte Patoshi Blocks: {valid_count}/{len(anomalies)}")
    print(f"    Im Bereich aber nicht Patoshi: {in_range_count}")
    print(f"    Außerhalb Bereich: {invalid_count}")

    # Kritische Prüfung: Sind die "Nicht-Patoshi" Werte Lücken?
    non_patoshi = [r for r in results if not r['is_patoshi_block'] and r['in_range']]
    if non_patoshi:
        print(f"\n  WARNUNG: {len(non_patoshi)} Werte im Bereich aber NICHT in Patoshi-Liste:")
        for r in non_patoshi:
            print(f"    Position {r['position']}: Wert {r['abs_value']}")

    return {
        "total_anomalies": len(anomalies),
        "valid_patoshi_blocks": valid_count,
        "in_range_not_patoshi": in_range_count,
        "out_of_range": invalid_count,
        "validation_rate": valid_count / len(anomalies) if anomalies else 0,
        "results": results,
    }

# =============================================================================
# VALIDIERUNG 7: Kontrollgruppe (Zufällige Positionen)
# =============================================================================

def validate_control_group():
    """Teste ob zufällige Positionen auch Patoshi Blocks treffen"""
    print("\n" + "=" * 60)
    print("VALIDIERUNG 7: Kontrollgruppe (Zufällige Positionen)")
    print("=" * 60)

    # Lade Daten
    with open("apps/web/public/data/anna-matrix.json") as f:
        anna_data = json.load(f)

    matrix = []
    for row in anna_data['matrix']:
        row_vals = []
        for v in row:
            if isinstance(v, str):
                try:
                    row_vals.append(int(v, 16) if len(v) == 8 else int(v))
                except:
                    row_vals.append(0)
            else:
                row_vals.append(int(v))
        matrix.append(row_vals)

    with open("apps/web/public/data/patoshi-addresses.json") as f:
        patoshi_data = json.load(f)

    patoshi_blocks = {r.get('blockHeight', 0) for r in patoshi_data.get('records', [])}

    print(f"\n  Generiere 34 zufällige Positionen (wie Anomalien)...")
    print(f"  Wiederhole 1000x für Statistik...")

    trials = 1000
    match_counts = []

    for trial in range(trials):
        random_positions = []
        for _ in range(34):
            r = random.randint(0, 127)
            c = random.randint(0, 127)
            random_positions.append((r, c))

        matches = 0
        for row, col in random_positions:
            val = abs(matrix[row][col])
            if val in patoshi_blocks:
                matches += 1

        match_counts.append(matches)

    avg_matches = sum(match_counts) / len(match_counts)
    max_matches = max(match_counts)
    min_matches = min(match_counts)

    print(f"\n  Ergebnisse aus {trials} Versuchen:")
    print(f"    Durchschnittliche Treffer: {avg_matches:.1f}/34")
    print(f"    Minimum: {min_matches}/34")
    print(f"    Maximum: {max_matches}/34")

    # Vergleich mit Anomalien
    anomaly_result = validate_anomaly_mapping()
    actual_matches = anomaly_result['valid_patoshi_blocks']

    print(f"\n  VERGLEICH:")
    print(f"    Anomalie-Treffer: {actual_matches}/34")
    print(f"    Zufalls-Durchschnitt: {avg_matches:.1f}/34")
    print(f"    Verhältnis: {actual_matches / avg_matches:.2f}x")

    # Ist das Ergebnis signifikant?
    times_anomaly_beaten = sum(1 for c in match_counts if c >= actual_matches)
    p_value = times_anomaly_beaten / trials

    print(f"\n  Statistische Signifikanz:")
    print(f"    P-Wert: {p_value:.4f}")
    print(f"    (Wie oft erreicht Zufall das Anomalie-Ergebnis?)")

    if p_value < 0.05:
        print(f"    → SIGNIFIKANT (p < 0.05)")
    else:
        print(f"    → NICHT signifikant (p >= 0.05)")

    return {
        "trials": trials,
        "avg_random_matches": avg_matches,
        "max_random_matches": max_matches,
        "actual_anomaly_matches": actual_matches,
        "p_value": p_value,
        "significant": p_value < 0.05,
    }

# =============================================================================
# VALIDIERUNG 8: Gesamtbewertung
# =============================================================================

def final_assessment(results: Dict):
    """Finale Bewertung aller Validierungen"""
    print("\n" + "=" * 80)
    print("FINALE BEWERTUNG")
    print("=" * 80)

    checks = []

    # Check 1: Block 264 hat 0x7B
    check1 = results['block264']['is_0x7b']
    checks.append(("Block 264 beginnt mit 0x7B", check1))

    # Check 2: 1CFB hat 0x7B
    check2 = results['cfb']['is_0x7b']
    checks.append(("1CFB beginnt mit 0x7B", check2))

    # Check 3: Beide haben 0x7B58
    check3 = results['block264']['is_0x7b58'] and results['cfb']['is_0x7b58']
    checks.append(("Beide haben 0x7B58 Präfix", check3))

    # Check 4: Block 264 ist in 0x7B58 Liste
    check4 = results['all_0x7b']['block_264_has_0x7b58']
    checks.append(("Block 264 hat exakt 0x7B58", check4))

    # Check 5: Anomalien sind signifikant
    check5 = results['control']['significant']
    checks.append(("Anomalie-Mapping statistisch signifikant", check5))

    print(f"\n  CHECKLISTE:")
    all_passed = True
    for name, passed in checks:
        marker = "✓" if passed else "✗"
        print(f"    [{marker}] {name}")
        if not passed:
            all_passed = False

    print(f"\n  GESAMTERGEBNIS:")
    if all_passed:
        print(f"    ✓ ALLE VALIDIERUNGEN BESTANDEN")
    else:
        print(f"    ✗ EINIGE VALIDIERUNGEN FEHLGESCHLAGEN")

    # Detaillierte Bewertung
    print(f"\n  DETAILLIERTE BEWERTUNG:")

    # Präfix-Match
    prefix_len = results['comparison']['prefix_match_length']
    print(f"\n    Präfix-Match (Block 264 vs 1CFB):")
    print(f"      Übereinstimmende Bytes: {prefix_len}")
    if prefix_len >= 2:
        print(f"      Wahrscheinlichkeit: 1/{256**prefix_len:,}")
        print(f"      → STARKER Hinweis auf Verbindung")
    elif prefix_len == 1:
        print(f"      Wahrscheinlichkeit: 1/256")
        print(f"      → SCHWACHER Hinweis")
    else:
        print(f"      → KEIN direkter Hinweis")

    # 0x7B Verteilung
    expected = results['stats']['expected_0x7b']
    actual = results['stats']['actual_0x7b']
    print(f"\n    0x7B Verteilung in Patoshi:")
    print(f"      Erwartet: {expected:.1f}")
    print(f"      Tatsächlich: {actual}")
    if abs(actual - expected) / expected < 0.2:
        print(f"      → NORMAL (wie erwartet bei Zufall)")
    else:
        print(f"      → AUFFÄLLIG")

    # Anomalie-Mapping
    anomaly_valid = results['anomaly']['valid_patoshi_blocks']
    anomaly_total = results['anomaly']['total_anomalies']
    print(f"\n    Anomalie-Mapping:")
    print(f"      Treffer: {anomaly_valid}/{anomaly_total}")
    print(f"      Rate: {anomaly_valid/anomaly_total*100:.1f}%")

    return {
        "all_checks_passed": all_passed,
        "checks": checks,
        "prefix_match_length": prefix_len,
    }

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "=" * 80)
    print("STARTE RIGOROSE VALIDIERUNG")
    print("=" * 80)

    results = {}

    # Validierung 1: Block 264
    results['block264'] = validate_block_264()

    # Validierung 2: 1CFB
    results['cfb'] = validate_1cfb_address()

    # Validierung 3: Byte-Vergleich
    results['comparison'] = validate_byte_comparison(results['block264'], results['cfb'])

    # Validierung 5: Alle 0x7B Blocks
    results['all_0x7b'] = validate_all_0x7b_blocks()

    # Validierung 4: Statistik
    results['stats'] = validate_statistical_significance(
        results['comparison']['prefix_match_length'],
        results['all_0x7b']['total_0x7b'],
        results['all_0x7b']['total_patoshi']
    )

    # Validierung 6: Anomalie-Mapping (wird in validate_control_group aufgerufen)
    results['anomaly'] = validate_anomaly_mapping()

    # Validierung 7: Kontrollgruppe
    results['control'] = validate_control_group()

    # Finale Bewertung
    results['assessment'] = final_assessment(results)

    # Speichern
    print("\n" + "=" * 80)
    print("ERGEBNISSE SPEICHERN")
    print("=" * 80)

    output = {
        "timestamp": datetime.now().isoformat(),
        "validation_results": {
            "block264": {
                "hash160": results['block264']['hash160'],
                "address": results['block264']['address'],
                "is_0x7b": results['block264']['is_0x7b'],
                "is_0x7b58": results['block264']['is_0x7b58'],
            },
            "cfb": {
                "hash160": results['cfb']['hash160'],
                "address": results['cfb']['address'],
                "is_0x7b": results['cfb']['is_0x7b'],
                "is_0x7b58": results['cfb']['is_0x7b58'],
            },
            "comparison": {
                "matching_bytes": results['comparison']['matching_bytes'],
                "prefix_match_length": results['comparison']['prefix_match_length'],
            },
            "all_0x7b": {
                "total": results['all_0x7b']['total_0x7b'],
                "total_0x7b58": results['all_0x7b']['total_0x7b58'],
                "block_264_has_0x7b58": results['all_0x7b']['block_264_has_0x7b58'],
            },
            "anomaly": {
                "valid_patoshi_blocks": results['anomaly']['valid_patoshi_blocks'],
                "total_anomalies": results['anomaly']['total_anomalies'],
                "validation_rate": results['anomaly']['validation_rate'],
            },
            "control": {
                "p_value": results['control']['p_value'],
                "significant": results['control']['significant'],
            },
            "assessment": {
                "all_passed": results['assessment']['all_checks_passed'],
            },
        },
    }

    with open("apps/web/scripts/RIGOROUS_VALIDATION_RESULTS.json", 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Ergebnisse: RIGOROUS_VALIDATION_RESULTS.json")

    return results

if __name__ == "__main__":
    results = main()
