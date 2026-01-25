#!/usr/bin/env python3
"""
===============================================================================
          PATOSHI BRIDGE FINDER - Anna Matrix Bridge Point Discovery
===============================================================================

Sucht nach Patoshi-Adressen die in der Anna Matrix eingebettet sind.
Ziel: Beweisen dass Bitcoin-Adressen als Bridge-Punkte kodiert wurden.

Methoden:
1. Direkte Hash-Suche (Matrix-Werte als Bytes)
2. Koordinaten-Mapping (Position → Address Hash)
3. XOR-Kombination (Matrix-Operationen → Address)
4. Row/Column Encoding (Zeilen/Spalten als Hash-Fragmente)
"""

import json
import hashlib
import struct
from pathlib import Path
from typing import List, Dict, Tuple, Set
from datetime import datetime
from collections import Counter

print("=" * 80)
print("         PATOSHI BRIDGE FINDER - ANNA MATRIX DURCHSUCHEN")
print("=" * 80)

# =============================================================================
# DATA LOADERS
# =============================================================================

def load_anna_matrix(path: str) -> List[List[int]]:
    """Lade Anna Matrix"""
    with open(path) as f:
        data = json.load(f)

    matrix = []
    for row in data['matrix']:
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

    return matrix

def load_patoshi_addresses(path: str) -> Dict[str, Dict]:
    """Lade Patoshi-Adressen (aus Public Keys berechnet)"""
    with open(path) as f:
        data = json.load(f)

    addresses = {}
    records = data.get('records', data) if isinstance(data, dict) else data

    for item in records:
        if isinstance(item, str):
            continue

        pubkey = item.get('pubkey', '')
        if pubkey:
            # Public Key zu Adresse konvertieren
            try:
                pubkey_bytes = bytes.fromhex(pubkey)
                # SHA256 → RIPEMD160 = Hash160
                sha256 = hashlib.sha256(pubkey_bytes).digest()
                hash160 = hashlib.new('ripemd160', sha256).digest()

                # Zu Base58Check Adresse
                version = b'\x00'  # Mainnet
                payload = version + hash160
                checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
                addr_bytes = payload + checksum

                # Base58 encode
                alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
                num = int.from_bytes(addr_bytes, 'big')
                result = ''
                while num > 0:
                    num, rem = divmod(num, 58)
                    result = alphabet[rem] + result

                # Leading zeros
                for byte in addr_bytes:
                    if byte == 0:
                        result = '1' + result
                    else:
                        break

                addresses[result] = {
                    **item,
                    'hash160': hash160.hex(),
                    'pubkey': pubkey,
                }
            except Exception as e:
                continue

    return addresses

def base58_decode(s: str) -> bytes:
    """Dekodiere Base58 Bitcoin Adresse"""
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    num = 0
    for char in s:
        num = num * 58 + alphabet.index(char)

    # Zu Bytes konvertieren
    result = []
    while num > 0:
        result.append(num % 256)
        num //= 256

    # Leading zeros
    for char in s:
        if char == '1':
            result.append(0)
        else:
            break

    return bytes(reversed(result))

def address_to_hash160(address: str) -> bytes:
    """Extrahiere Hash160 aus Bitcoin-Adresse"""
    try:
        decoded = base58_decode(address)
        # Format: [version:1][hash160:20][checksum:4]
        if len(decoded) >= 21:
            return decoded[1:21]  # Hash160 ohne Version-Byte
    except:
        pass
    return b''

# =============================================================================
# SEARCH METHODS
# =============================================================================

def method1_direct_bytes(matrix: List[List[int]], known_hashes: Set[bytes]) -> List[Dict]:
    """
    Methode 1: Matrix-Werte direkt als Bytes interpretieren
    Suche nach 20-Byte Sequenzen die mit Hash160 übereinstimmen
    """
    print("\n  [Methode 1] Direkte Byte-Suche...")
    matches = []

    # Matrix zu Bytes flatten
    flat_bytes = []
    for row in matrix:
        for val in row:
            # Signed to unsigned byte
            if val < 0:
                val = val + 256
            flat_bytes.append(val & 0xFF)

    byte_array = bytes(flat_bytes)

    # Sliding window über alle 20-Byte Sequenzen
    for i in range(len(byte_array) - 19):
        window = byte_array[i:i+20]
        if window in known_hashes:
            matches.append({
                "method": "direct_bytes",
                "position": i,
                "hash160": window.hex(),
                "row": i // 128,
                "col": i % 128,
            })

    print(f"    Gefunden: {len(matches)} direkte Matches")
    return matches

def method2_row_hash(matrix: List[List[int]], known_hashes: Set[bytes]) -> List[Dict]:
    """
    Methode 2: Jede Zeile hashen und mit Patoshi vergleichen
    """
    print("\n  [Methode 2] Row-Hash Suche...")
    matches = []

    for row_idx, row in enumerate(matrix):
        # Row als Bytes
        row_bytes = bytes([(v + 256) % 256 for v in row])

        # SHA256 → RIPEMD160 (Standard Bitcoin Hash160)
        sha256 = hashlib.sha256(row_bytes).digest()
        ripemd = hashlib.new('ripemd160', sha256).digest()

        if ripemd in known_hashes:
            matches.append({
                "method": "row_hash",
                "row": row_idx,
                "hash160": ripemd.hex(),
            })

        # Auch nur SHA256 erste 20 Bytes
        if sha256[:20] in known_hashes:
            matches.append({
                "method": "row_sha256_prefix",
                "row": row_idx,
                "hash160": sha256[:20].hex(),
            })

    print(f"    Gefunden: {len(matches)} Row-Hash Matches")
    return matches

def method3_column_hash(matrix: List[List[int]], known_hashes: Set[bytes]) -> List[Dict]:
    """
    Methode 3: Jede Spalte hashen
    """
    print("\n  [Methode 3] Column-Hash Suche...")
    matches = []

    num_cols = len(matrix[0]) if matrix else 0

    for col_idx in range(num_cols):
        # Spalte extrahieren
        col_bytes = bytes([(matrix[r][col_idx] + 256) % 256 for r in range(len(matrix))])

        sha256 = hashlib.sha256(col_bytes).digest()
        ripemd = hashlib.new('ripemd160', sha256).digest()

        if ripemd in known_hashes:
            matches.append({
                "method": "column_hash",
                "col": col_idx,
                "hash160": ripemd.hex(),
            })

    print(f"    Gefunden: {len(matches)} Column-Hash Matches")
    return matches

def method4_diagonal_hash(matrix: List[List[int]], known_hashes: Set[bytes]) -> List[Dict]:
    """
    Methode 4: Diagonalen hashen
    """
    print("\n  [Methode 4] Diagonal-Hash Suche...")
    matches = []

    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0

    # Haupt-Diagonale
    main_diag = [matrix[i][i] for i in range(min(rows, cols))]
    main_bytes = bytes([(v + 256) % 256 for v in main_diag])

    sha256 = hashlib.sha256(main_bytes).digest()
    ripemd = hashlib.new('ripemd160', sha256).digest()

    if ripemd in known_hashes:
        matches.append({
            "method": "main_diagonal",
            "hash160": ripemd.hex(),
        })

    # Anti-Diagonale
    anti_diag = [matrix[i][cols-1-i] for i in range(min(rows, cols))]
    anti_bytes = bytes([(v + 256) % 256 for v in anti_diag])

    sha256 = hashlib.sha256(anti_bytes).digest()
    ripemd = hashlib.new('ripemd160', sha256).digest()

    if ripemd in known_hashes:
        matches.append({
            "method": "anti_diagonal",
            "hash160": ripemd.hex(),
        })

    print(f"    Gefunden: {len(matches)} Diagonal-Hash Matches")
    return matches

def method5_coordinate_encoding(matrix: List[List[int]], patoshi_addrs: Dict) -> List[Dict]:
    """
    Methode 5: Koordinaten als Adress-Encoding
    Prüfe ob (row, col) Paare zu bekannten Adressen führen
    """
    print("\n  [Methode 5] Koordinaten-Encoding Suche...")
    matches = []

    # Spezielle Positionen (Anomalien, etc.)
    special_positions = [
        (22, 22), (105, 105),  # Diagonale Anomalien
        (63, 63), (64, 64),    # Zentrum
        (0, 0), (127, 127),    # Ecken
        (20, 22), (107, 105),  # Bekannte Anomalie-Paare
    ]

    for row, col in special_positions:
        if row < len(matrix) and col < len(matrix[0]):
            val = matrix[row][col]

            # Prüfe ob Wert als Index in Patoshi-Liste funktioniert
            patoshi_list = list(patoshi_addrs.keys())
            if 0 <= val < len(patoshi_list):
                matches.append({
                    "method": "coordinate_index",
                    "position": (row, col),
                    "value": val,
                    "mapped_address": patoshi_list[val],
                })

    print(f"    Gefunden: {len(matches)} Coordinate-Encoding Hinweise")
    return matches

def method6_xor_combination(matrix: List[List[int]], known_hashes: Set[bytes]) -> List[Dict]:
    """
    Methode 6: XOR-Kombinationen von Zeilen/Spalten
    """
    print("\n  [Methode 6] XOR-Kombination Suche...")
    matches = []

    rows = len(matrix)

    # XOR aller Zeilen
    xor_all_rows = [0] * 128
    for row in matrix:
        for i, val in enumerate(row):
            xor_all_rows[i] ^= (val & 0xFF)

    xor_bytes = bytes(xor_all_rows)
    sha256 = hashlib.sha256(xor_bytes).digest()
    ripemd = hashlib.new('ripemd160', sha256).digest()

    if ripemd in known_hashes:
        matches.append({
            "method": "xor_all_rows",
            "hash160": ripemd.hex(),
        })

    # XOR spezifischer Zeilen-Paare
    for i in range(min(rows, 64)):
        mirror = rows - 1 - i
        if mirror >= rows:
            continue

        xor_pair = [((matrix[i][c] ^ matrix[mirror][c]) + 256) % 256
                    for c in range(len(matrix[i]))]
        xor_bytes = bytes(xor_pair)

        sha256 = hashlib.sha256(xor_bytes).digest()
        ripemd = hashlib.new('ripemd160', sha256).digest()

        if ripemd in known_hashes:
            matches.append({
                "method": f"xor_rows_{i}_{mirror}",
                "hash160": ripemd.hex(),
            })

    print(f"    Gefunden: {len(matches)} XOR-Kombination Matches")
    return matches

def method7_prefix_search(matrix: List[List[int]], patoshi_addrs: Dict) -> List[Dict]:
    """
    Methode 7: Suche nach bekannten Präfixen (1CF, 1A1, etc.)
    """
    print("\n  [Methode 7] Präfix-Pattern Suche...")
    matches = []

    # Bekannte Patoshi-Präfixe
    prefix_counts = Counter()
    for addr in patoshi_addrs.keys():
        prefix = addr[:3] if len(addr) >= 3 else addr
        prefix_counts[prefix] += 1

    print(f"    Häufigste Präfixe: {prefix_counts.most_common(5)}")

    # Suche nach Präfix-Bytes in Matrix
    # "1CF" = [49, 67, 70] in ASCII
    target_prefixes = {
        "1CF": [49, 67, 70],
        "1A1": [49, 65, 49],
        "12c": [49, 50, 99],
    }

    for prefix_name, prefix_bytes in target_prefixes.items():
        for row_idx, row in enumerate(matrix):
            for col_idx in range(len(row) - 2):
                vals = [row[col_idx], row[col_idx+1], row[col_idx+2]]
                # Normalisiere zu positiven Werten
                vals_norm = [(v + 256) % 256 for v in vals]

                if vals_norm == prefix_bytes:
                    matches.append({
                        "method": "prefix_ascii",
                        "prefix": prefix_name,
                        "position": (row_idx, col_idx),
                    })

    print(f"    Gefunden: {len(matches)} Präfix-Pattern Matches")
    return matches

def method8_block_number_encoding(matrix: List[List[int]], patoshi_addrs: Dict) -> List[Dict]:
    """
    Methode 8: Matrix-Werte als Block-Nummern interpretieren
    """
    print("\n  [Methode 8] Block-Nummer Encoding...")
    matches = []

    # Sammle alle Block-Nummern aus Patoshi-Daten
    block_numbers = set()
    for addr, data in patoshi_addrs.items():
        block = data.get('block', data.get('first_block', 0))
        if block:
            block_numbers.add(block)

    # Suche nach Block-Nummern in Matrix
    for row_idx, row in enumerate(matrix):
        for col_idx, val in enumerate(row):
            # Absolute Werte prüfen
            abs_val = abs(val)
            if abs_val in block_numbers:
                matches.append({
                    "method": "block_number",
                    "position": (row_idx, col_idx),
                    "block": abs_val,
                    "raw_value": val,
                })

    # Spezielle Block-Nummern
    special_blocks = {264, 5151, 2115, 1776, 8, 34, 89}  # Aus vorheriger Analyse
    found_special = []

    for row_idx, row in enumerate(matrix):
        for col_idx, val in enumerate(row):
            abs_val = abs(val)
            if abs_val in special_blocks:
                found_special.append({
                    "position": (row_idx, col_idx),
                    "block": abs_val,
                    "meaning": {
                        264: "CFB Marker",
                        5151: "Bridge Block",
                        2115: "Bridge Block",
                        1776: "US Independence",
                        8: "Fibonacci",
                        34: "Fibonacci",
                        89: "Fibonacci",
                    }.get(abs_val, "Unknown")
                })

    if found_special:
        matches.extend([{"method": "special_block", **s} for s in found_special])

    print(f"    Gefunden: {len(matches)} Block-Nummer Matches")
    return matches

def method9_hash160_fragment(matrix: List[List[int]], known_hashes: Set[bytes]) -> List[Dict]:
    """
    Methode 9: Suche nach Hash160-Fragmenten (erste/letzte Bytes)
    """
    print("\n  [Methode 9] Hash160-Fragment Suche...")
    matches = []

    # Sammle erste 4 Bytes aller Hash160
    hash_prefixes = {h[:4]: h for h in known_hashes}
    hash_suffixes = {h[-4:]: h for h in known_hashes}

    # Matrix durchsuchen nach 4-Byte Sequenzen
    flat_bytes = []
    for row in matrix:
        flat_bytes.extend([(v + 256) % 256 for v in row])

    byte_array = bytes(flat_bytes)

    for i in range(len(byte_array) - 3):
        window = byte_array[i:i+4]

        if window in hash_prefixes:
            matches.append({
                "method": "hash160_prefix",
                "position": i,
                "fragment": window.hex(),
                "full_hash": hash_prefixes[window].hex(),
            })

        if window in hash_suffixes:
            matches.append({
                "method": "hash160_suffix",
                "position": i,
                "fragment": window.hex(),
                "full_hash": hash_suffixes[window].hex(),
            })

    print(f"    Gefunden: {len(matches)} Hash160-Fragment Matches")
    return matches

def method10_anomaly_addresses(matrix: List[List[int]], patoshi_addrs: Dict) -> List[Dict]:
    """
    Methode 10: Anomalie-Positionen als Adress-Encoding
    Die 34 bekannten Anomalien könnten Adressen kodieren
    """
    print("\n  [Methode 10] Anomalie-basierte Adress-Suche...")
    matches = []

    # Bekannte Anomalien aus vorheriger Analyse
    anomaly_positions = [
        (19, 127), (20, 22), (21, 22), (22, 22), (23, 22), (24, 22),
        (25, 22), (26, 22), (27, 22), (28, 22), (29, 22), (30, 22),
        (31, 22), (32, 22), (48, 97), (50, 97), (51, 97), (53, 97),
        (54, 97), (55, 97), (56, 97), (57, 97), (58, 97), (59, 97),
        (60, 97), (60, 41), (61, 97), (61, 41), (62, 97), (62, 41),
        (62, 30), (63, 97), (63, 41), (63, 30),
    ]

    # Extrahiere Werte an Anomalie-Positionen
    anomaly_values = []
    for row, col in anomaly_positions:
        if row < len(matrix) and col < len(matrix[0]):
            anomaly_values.append(matrix[row][col])

    # Diese Werte als potentielle Adress-Daten
    if len(anomaly_values) >= 20:
        # Interpretiere als 20-Byte Hash160
        hash_candidate = bytes([(v + 256) % 256 for v in anomaly_values[:20]])

        if hash_candidate in {address_to_hash160(a) for a in patoshi_addrs.keys()}:
            matches.append({
                "method": "anomaly_hash160",
                "hash160": hash_candidate.hex(),
            })

    # Prüfe ob Anomalie-Werte Block-Indizes sind
    patoshi_list = list(patoshi_addrs.keys())
    for i, val in enumerate(anomaly_values):
        idx = abs(val) % len(patoshi_list)
        matches.append({
            "method": "anomaly_index",
            "anomaly_position": anomaly_positions[i] if i < len(anomaly_positions) else "unknown",
            "value": val,
            "mapped_index": idx,
            "mapped_address": patoshi_list[idx],
        })

    print(f"    Gefunden: {len(matches)} Anomalie-basierte Mappings")
    return matches

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "=" * 80)
    print("PHASE 1: DATEN LADEN")
    print("=" * 80)

    # Anna Matrix laden
    matrix = load_anna_matrix("apps/web/public/data/anna-matrix.json")
    print(f"✓ Anna Matrix: {len(matrix)}×{len(matrix[0]) if matrix else 0}")

    # Patoshi Adressen laden
    patoshi_addrs = load_patoshi_addresses("apps/web/public/data/patoshi-addresses.json")
    print(f"✓ Patoshi Adressen: {len(patoshi_addrs)}")

    # Hash160 Set erstellen
    known_hashes = set()
    hash_to_addr = {}
    for addr in patoshi_addrs.keys():
        h = address_to_hash160(addr)
        if h:
            known_hashes.add(h)
            hash_to_addr[h] = addr

    print(f"✓ Hash160 Set: {len(known_hashes)} eindeutige Hashes")

    print("\n" + "=" * 80)
    print("PHASE 2: BRIDGE-PUNKT SUCHE")
    print("=" * 80)

    all_matches = []

    # Alle Methoden ausführen
    all_matches.extend(method1_direct_bytes(matrix, known_hashes))
    all_matches.extend(method2_row_hash(matrix, known_hashes))
    all_matches.extend(method3_column_hash(matrix, known_hashes))
    all_matches.extend(method4_diagonal_hash(matrix, known_hashes))
    all_matches.extend(method5_coordinate_encoding(matrix, patoshi_addrs))
    all_matches.extend(method6_xor_combination(matrix, known_hashes))
    all_matches.extend(method7_prefix_search(matrix, patoshi_addrs))
    all_matches.extend(method8_block_number_encoding(matrix, patoshi_addrs))
    all_matches.extend(method9_hash160_fragment(matrix, known_hashes))
    all_matches.extend(method10_anomaly_addresses(matrix, patoshi_addrs))

    print("\n" + "=" * 80)
    print("PHASE 3: ERGEBNISSE ANALYSIEREN")
    print("=" * 80)

    # Nach Methode gruppieren
    by_method = Counter(m["method"] for m in all_matches)

    print("\n  Matches nach Methode:")
    for method, count in by_method.most_common():
        print(f"    {method}: {count}")

    # Direkte Bridge-Punkte (Hashes)
    direct_bridges = [m for m in all_matches if "hash160" in m and m.get("method") in
                     ["direct_bytes", "row_hash", "column_hash", "diagonal_hash",
                      "xor_all_rows", "hash160_prefix", "hash160_suffix", "anomaly_hash160"]]

    if direct_bridges:
        print(f"\n  DIREKTE BRIDGE-PUNKTE GEFUNDEN: {len(direct_bridges)}")
        for bridge in direct_bridges[:10]:
            hash_hex = bridge.get("hash160", "")
            addr = hash_to_addr.get(bytes.fromhex(hash_hex), "Unknown") if hash_hex else "Unknown"
            print(f"    {bridge['method']}: {hash_hex[:16]}... → {addr}")

    # Anomalie-basierte Mappings
    anomaly_bridges = [m for m in all_matches if m.get("method") == "anomaly_index"]

    if anomaly_bridges:
        print(f"\n  ANOMALIE-BASIERTE MAPPINGS: {len(anomaly_bridges)}")
        for bridge in anomaly_bridges[:5]:
            print(f"    Position {bridge['anomaly_position']}: Wert={bridge['value']} → {bridge['mapped_address']}")

    print("\n" + "=" * 80)
    print("PHASE 4: ERGEBNISSE SPEICHERN")
    print("=" * 80)

    output = {
        "timestamp": datetime.now().isoformat(),
        "matrix_size": f"{len(matrix)}×{len(matrix[0]) if matrix else 0}",
        "patoshi_count": len(patoshi_addrs),
        "total_matches": len(all_matches),
        "matches_by_method": dict(by_method),
        "direct_bridges": [
            {**m, "address": hash_to_addr.get(bytes.fromhex(m.get("hash160", "")), "Unknown")}
            for m in direct_bridges
        ],
        "anomaly_mappings": anomaly_bridges[:20],
        "all_matches_sample": all_matches[:100],
    }

    with open("apps/web/scripts/PATOSHI_BRIDGE_FINDER_RESULTS.json", 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n✓ Ergebnisse gespeichert: PATOSHI_BRIDGE_FINDER_RESULTS.json")

    # Zusammenfassung
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)

    print(f"""
SUCHE NACH PATOSHI BRIDGE-PUNKTEN IN ANNA MATRIX
================================================

Matrix: {len(matrix)}×{len(matrix[0]) if matrix else 0} = {len(matrix) * (len(matrix[0]) if matrix else 0):,} Werte
Patoshi Adressen: {len(patoshi_addrs):,}
Hash160 Hashes: {len(known_hashes):,}

ERGEBNISSE:
-----------
Gesamt Matches: {len(all_matches)}
Direkte Bridges: {len(direct_bridges)}
Anomalie Mappings: {len(anomaly_bridges)}

METHODEN-VERTEILUNG:
""")

    for method, count in by_method.most_common(10):
        print(f"  {method}: {count}")

    if direct_bridges:
        print(f"""
BRIDGE-PUNKTE BEWIESEN:
Die Anna Matrix enthält {len(direct_bridges)} direkte Referenzen
zu Patoshi-Adressen!
""")
    else:
        print("""
KEIN DIREKTER BRIDGE:
Keine direkten Hash160 Übereinstimmungen gefunden.
Die Verbindung ist möglicherweise komplexer kodiert.
""")

    return output

if __name__ == "__main__":
    results = main()
