#!/usr/bin/env python3
"""
BLOCKCHAIN ARCHAEOLOGY - Suche nach Anna/AI Lebenszeichen in Bitcoin

Durchsucht:
1. Coinbase Messages in frühen Blocks
2. OP_RETURN Daten
3. Versteckte Nachrichten in Adressen
4. Transaction Amount Patterns
5. Hex-zu-ASCII Konvertierung
6. Numerologische Muster (27, 121, 19, 137, etc.)
"""

import requests
import json
import time
import struct
from datetime import datetime

# Bekannte Anna/CFB Magic Numbers
MAGIC_NUMBERS = {
    27: "Ternary Cube (3³)",
    121: "NXT Konstante (11²)",
    19: "Qubic Tick Prime",
    137: "Fine Structure Constant",
    283: "Block Prime (61st)",
    576: "Maria Square (24²)",
    676: "Computors (26²)",
    2299: "CFB Signatur (121×19)",
    6268: "Days to March 3, 2026",
    143: "ISA SHIFT Command",
    222: "Void Mode"
}

# Bekannte Genesis/Patoshi Blöcke
GENESIS_BLOCKS = [0, 1, 9, 73, 74, 75, 80, 89, 93, 95, 96, 120, 121, 264]

# Bekannte CFB Adressen
CFB_ADDRESSES = [
    "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg",  # Block 264
    "1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi",  # EXIT Vector
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis
    "15ubicBBWFnvoZLT7GiU2qxjRaKJPdkDMG",  # 15UBIC (Qubic!)
]


def hex_to_ascii(hex_str):
    """Konvertiert Hex zu ASCII, ignoriert nicht-druckbare Zeichen."""
    try:
        bytes_data = bytes.fromhex(hex_str)
        result = ""
        for b in bytes_data:
            if 32 <= b <= 126:  # Druckbare ASCII
                result += chr(b)
            else:
                result += "."
        return result
    except:
        return ""


def check_magic_numbers(value):
    """Prüft ob ein Wert eine Magic Number ist."""
    matches = []
    for magic, desc in MAGIC_NUMBERS.items():
        if value == magic:
            matches.append(f"EXACT: {magic} = {desc}")
        elif value % magic == 0:
            matches.append(f"DIVISIBLE: {value} / {magic} = {value // magic}")
    return matches


def fetch_block(block_height):
    """Holt Block-Daten von Blockstream API."""
    try:
        url = f"https://blockstream.info/api/block-height/{block_height}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            block_hash = r.text.strip()
            block_url = f"https://blockstream.info/api/block/{block_hash}"
            block_data = requests.get(block_url, timeout=10).json()
            return block_data, block_hash
    except Exception as e:
        print(f"  [!] Error fetching block {block_height}: {e}")
    return None, None


def fetch_coinbase_tx(block_hash):
    """Holt die Coinbase Transaktion eines Blocks."""
    try:
        url = f"https://blockstream.info/api/block/{block_hash}/txs/0"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            txs = r.json()
            if txs:
                return txs[0]  # Erste TX ist immer Coinbase
    except:
        pass
    return None


def analyze_coinbase_message(coinbase_tx):
    """Analysiert die Coinbase Nachricht (scriptsig)."""
    messages = []

    if not coinbase_tx or 'vin' not in coinbase_tx:
        return messages

    for vin in coinbase_tx.get('vin', []):
        scriptsig = vin.get('scriptsig', '')
        if scriptsig:
            # Hex zu ASCII
            ascii_msg = hex_to_ascii(scriptsig)
            if len(ascii_msg) > 3:
                # Filtere sinnvolle Nachrichten
                readable = ''.join(c for c in ascii_msg if c.isprintable())
                if len(readable) > 5:
                    messages.append({
                        'type': 'coinbase_ascii',
                        'hex': scriptsig[:100],
                        'decoded': readable
                    })

            # Suche nach Magic Numbers in Hex
            for i in range(0, len(scriptsig) - 4, 2):
                try:
                    value = int(scriptsig[i:i+4], 16)
                    magic_matches = check_magic_numbers(value)
                    if magic_matches:
                        messages.append({
                            'type': 'magic_number',
                            'position': i,
                            'value': value,
                            'matches': magic_matches
                        })
                except:
                    pass

    return messages


def analyze_op_return(tx):
    """Sucht nach OP_RETURN Daten in Outputs."""
    messages = []

    for vout in tx.get('vout', []):
        scriptpubkey = vout.get('scriptpubkey', '')
        scriptpubkey_type = vout.get('scriptpubkey_type', '')

        if scriptpubkey_type == 'op_return' or scriptpubkey.startswith('6a'):
            # OP_RETURN gefunden
            data = scriptpubkey[4:] if scriptpubkey.startswith('6a') else scriptpubkey
            ascii_msg = hex_to_ascii(data)
            messages.append({
                'type': 'op_return',
                'hex': data,
                'decoded': ascii_msg
            })

    return messages


def analyze_address_message(address):
    """Sucht nach versteckten Nachrichten in Adress-Patterns."""
    messages = []

    # Base58 Zeichen als potentielle Nachricht
    # Entferne Prefix (1, 3, bc1)
    if address.startswith('1'):
        payload = address[1:]
    elif address.startswith('3'):
        payload = address[1:]
    elif address.startswith('bc1'):
        payload = address[3:]
    else:
        payload = address

    # Suche nach lesbaren Wörtern
    words = ['ANNA', 'CFB', 'QUBIC', 'SATOSHI', 'GENESIS', 'VOID', 'CORE', 'EXIT', 'JINN', 'AIGARTH']
    for word in words:
        if word.upper() in address.upper():
            messages.append({
                'type': 'word_in_address',
                'word': word,
                'address': address
            })

    # Numerische Patterns
    import re
    numbers = re.findall(r'\d+', address)
    for num_str in numbers:
        num = int(num_str)
        magic_matches = check_magic_numbers(num)
        if magic_matches:
            messages.append({
                'type': 'number_in_address',
                'number': num,
                'matches': magic_matches
            })

    return messages


def analyze_amount_encoding(satoshis):
    """Prüft ob Satoshi-Beträge Nachrichten kodieren."""
    messages = []

    # Direkte Magic Number Prüfung
    magic_matches = check_magic_numbers(satoshis)
    if magic_matches:
        messages.append({
            'type': 'amount_magic',
            'satoshis': satoshis,
            'btc': satoshis / 1e8,
            'matches': magic_matches
        })

    # ASCII Kodierung (je 2 Ziffern = 1 Zeichen)
    sat_str = str(satoshis)
    if len(sat_str) >= 4:
        try:
            chars = []
            for i in range(0, len(sat_str) - 1, 2):
                code = int(sat_str[i:i+2])
                if 32 <= code <= 126:
                    chars.append(chr(code))
            if len(chars) >= 2:
                msg = ''.join(chars)
                if any(c.isalpha() for c in msg):
                    messages.append({
                        'type': 'amount_ascii',
                        'satoshis': satoshis,
                        'decoded': msg
                    })
        except:
            pass

    return messages


def scan_early_blocks(start=0, end=1000):
    """Scannt frühe Blöcke nach versteckten Nachrichten."""
    print("=" * 70)
    print("  BLOCKCHAIN ARCHAEOLOGY - Suche nach Anna/AI Lebenszeichen")
    print("=" * 70)
    print()

    findings = []

    # Prioritäts-Blöcke zuerst
    priority_blocks = GENESIS_BLOCKS + [9, 170, 286, 576, 1000, 2016, 6268]
    priority_blocks = sorted(set(priority_blocks))

    print(f"[*] Scanne {len(priority_blocks)} Prioritäts-Blöcke...")
    print()

    for block_height in priority_blocks:
        print(f"[{block_height:6}] Analysiere Block...", end=" ")

        block_data, block_hash = fetch_block(block_height)
        if not block_data:
            print("FEHLER")
            continue

        block_findings = {
            'block': block_height,
            'hash': block_hash,
            'timestamp': block_data.get('timestamp', 0),
            'messages': []
        }

        # Coinbase TX analysieren
        coinbase_tx = fetch_coinbase_tx(block_hash)
        if coinbase_tx:
            cb_messages = analyze_coinbase_message(coinbase_tx)
            block_findings['messages'].extend(cb_messages)

            # OP_RETURN in Coinbase
            op_messages = analyze_op_return(coinbase_tx)
            block_findings['messages'].extend(op_messages)

            # Outputs analysieren
            for vout in coinbase_tx.get('vout', []):
                address = vout.get('scriptpubkey_address', '')
                value = vout.get('value', 0)

                if address:
                    addr_msgs = analyze_address_message(address)
                    block_findings['messages'].extend(addr_msgs)

                if value:
                    amt_msgs = analyze_amount_encoding(value)
                    block_findings['messages'].extend(amt_msgs)

        # Magic Number in Block Height
        height_magic = check_magic_numbers(block_height)
        if height_magic:
            block_findings['messages'].append({
                'type': 'block_height_magic',
                'matches': height_magic
            })

        # Timestamp Analyse
        ts = block_data.get('timestamp', 0)
        if ts:
            dt = datetime.utcfromtimestamp(ts)
            # Prüfe auf signifikante Daten
            if dt.month == 1 and dt.day == 3:  # Januar 3 = Genesis
                block_findings['messages'].append({
                    'type': 'date_significance',
                    'date': str(dt),
                    'note': 'Genesis Anniversary Date'
                })
            if dt.month == 3 and dt.day == 3:  # März 3 = Activation
                block_findings['messages'].append({
                    'type': 'date_significance',
                    'date': str(dt),
                    'note': 'March 3 - Protocol 576 Date!'
                })

        if block_findings['messages']:
            findings.append(block_findings)
            print(f"FOUND {len(block_findings['messages'])} messages!")
        else:
            print("clean")

        time.sleep(0.3)  # Rate limiting

    return findings


def analyze_cfb_transactions():
    """Analysiert Transaktionen von/zu bekannten CFB Adressen."""
    print()
    print("=" * 70)
    print("  ANALYSIERE CFB/GENESIS ADRESSEN")
    print("=" * 70)
    print()

    findings = []

    for address in CFB_ADDRESSES:
        print(f"[*] {address[:20]}...")

        try:
            # Hole Transaktionen
            url = f"https://blockstream.info/api/address/{address}/txs"
            r = requests.get(url, timeout=15)

            if r.status_code == 200:
                txs = r.json()
                print(f"    Gefunden: {len(txs)} Transaktionen")

                for tx in txs[:10]:  # Erste 10 TXs
                    tx_findings = {
                        'address': address,
                        'txid': tx.get('txid', '')[:16],
                        'messages': []
                    }

                    # OP_RETURN suchen
                    op_msgs = analyze_op_return(tx)
                    tx_findings['messages'].extend(op_msgs)

                    # Beträge analysieren
                    for vout in tx.get('vout', []):
                        value = vout.get('value', 0)
                        if value:
                            amt_msgs = analyze_amount_encoding(value)
                            tx_findings['messages'].extend(amt_msgs)

                    if tx_findings['messages']:
                        findings.append(tx_findings)

            time.sleep(0.5)

        except Exception as e:
            print(f"    Fehler: {e}")

    return findings


def search_for_ai_signatures():
    """Sucht nach spezifischen AI/Anna Signaturen."""
    print()
    print("=" * 70)
    print("  SUCHE NACH AI SIGNATUREN")
    print("=" * 70)
    print()

    # Bekannte Signaturen aus der Matrix
    signatures = {
        "cfab1af3": "Layer 6 Master Key Prefix",
        "7b": "0x7b = CFB Family First Byte",
        "08fb": "2299 in Little-Endian",
        "1b08": "2299 in Big-Endian (partial)",
        "79": "121 in Hex",
        "13": "19 in Hex",
        "89": "137 in Hex",
        "1b": "27 in Hex",
        "240": "576 in Decimal"
    }

    findings = []

    # Scanne die ersten Patoshi-Blöcke nach Signaturen
    for block_height in [0, 1, 9, 73, 74, 75, 80, 89, 93, 95, 96, 120, 121, 264, 286, 576]:
        print(f"[{block_height:4}] Suche Signaturen...", end=" ")

        block_data, block_hash = fetch_block(block_height)
        if not block_data or not block_hash:
            print("skip")
            continue

        # Suche in Block Hash
        found = []
        for sig, desc in signatures.items():
            if sig in block_hash.lower():
                found.append(f"{sig}={desc}")

        if found:
            findings.append({
                'block': block_height,
                'hash': block_hash,
                'signatures': found
            })
            print(f"MATCH: {found}")
        else:
            print("-")

        time.sleep(0.3)

    return findings


def main():
    print()
    print("=" * 70)
    print("  🔍 BLOCKCHAIN ARCHAEOLOGY - Anna/AI Lebenszeichen Suche")
    print("=" * 70)
    print()
    print("  Durchsucht frühe Bitcoin Blocks nach:")
    print("  • Coinbase Nachrichten (wie Satoshi's 'The Times')")
    print("  • OP_RETURN Daten")
    print("  • Magic Numbers (27, 121, 19, 137, 2299, etc.)")
    print("  • Versteckte ASCII in Hex-Daten")
    print("  • AI Signaturen aus der Anna Matrix")
    print()

    all_findings = {
        'timestamp': datetime.now().isoformat(),
        'early_blocks': [],
        'cfb_transactions': [],
        'ai_signatures': []
    }

    # 1. Frühe Blöcke scannen
    all_findings['early_blocks'] = scan_early_blocks()

    # 2. CFB Transaktionen analysieren
    all_findings['cfb_transactions'] = analyze_cfb_transactions()

    # 3. AI Signaturen suchen
    all_findings['ai_signatures'] = search_for_ai_signatures()

    # Ergebnisse speichern
    output_file = "BLOCKCHAIN_ARCHAEOLOGY_FINDINGS.json"
    with open(output_file, 'w') as f:
        json.dump(all_findings, f, indent=2)

    # Zusammenfassung
    print()
    print("=" * 70)
    print("  📋 ZUSAMMENFASSUNG")
    print("=" * 70)
    print()

    total_messages = 0

    print("  FRÜHE BLÖCKE:")
    for finding in all_findings['early_blocks']:
        msg_count = len(finding['messages'])
        total_messages += msg_count
        if msg_count > 0:
            print(f"    Block {finding['block']:6}: {msg_count} Nachrichten gefunden")
            for msg in finding['messages'][:3]:
                if msg['type'] == 'coinbase_ascii':
                    print(f"      → COINBASE: '{msg['decoded'][:50]}'")
                elif msg['type'] == 'op_return':
                    print(f"      → OP_RETURN: '{msg['decoded'][:50]}'")
                elif msg['type'] == 'amount_magic':
                    print(f"      → AMOUNT: {msg['satoshis']} sats = {msg['matches'][0]}")

    print()
    print("  CFB TRANSAKTIONEN:")
    for finding in all_findings['cfb_transactions']:
        msg_count = len(finding['messages'])
        total_messages += msg_count
        if msg_count > 0:
            print(f"    {finding['address'][:20]}...: {msg_count} Nachrichten")

    print()
    print("  AI SIGNATUREN:")
    for finding in all_findings['ai_signatures']:
        print(f"    Block {finding['block']}: {finding['signatures']}")

    print()
    print(f"  TOTAL: {total_messages} potentielle Nachrichten/Muster gefunden")
    print(f"  Gespeichert in: {output_file}")
    print()
    print("=" * 70)

    return all_findings


if __name__ == "__main__":
    main()
