#!/usr/bin/env python3
"""
Analyze all transactions from the L137 address
Address: 1K69sEhUwNgiva3xzPnToxS89dzydU7nPm
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

ADDRESS = "1K69sEhUwNgiva3xzPnToxS89dzydU7nPm"

def get_all_transactions():
    """Fetch all transactions for the address."""
    all_txs = []

    # Mempool.space API
    url = f"https://mempool.space/api/address/{ADDRESS}/txs"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            txs = response.json()
            all_txs.extend(txs)
            print(f"Fetched {len(txs)} transactions")

            # Check if there are more (pagination)
            while len(txs) == 25:  # Default page size
                last_txid = txs[-1]['txid']
                url_next = f"https://mempool.space/api/address/{ADDRESS}/txs/chain/{last_txid}"
                time.sleep(0.5)
                response = requests.get(url_next, timeout=30)
                if response.status_code == 200:
                    txs = response.json()
                    all_txs.extend(txs)
                    print(f"Fetched {len(txs)} more, total: {len(all_txs)}")
                else:
                    break

    except Exception as e:
        print(f"Error: {e}")

    return all_txs

def decode_op_return(script_hex):
    """Decode OP_RETURN script to text."""
    try:
        # Remove OP_RETURN opcode (6a) and length bytes
        if script_hex.startswith('6a'):
            # Find the data start
            idx = 2
            # Skip length byte(s)
            if len(script_hex) > idx:
                length_byte = int(script_hex[idx:idx+2], 16)
                if length_byte <= 75:
                    idx += 2
                elif length_byte == 76:  # OP_PUSHDATA1
                    idx += 4
                elif length_byte == 77:  # OP_PUSHDATA2
                    idx += 6

                data_hex = script_hex[idx:]
                decoded = bytes.fromhex(data_hex).decode('utf-8', errors='replace')
                return decoded
    except Exception as e:
        return f"[decode error: {e}]"

    return None

def analyze_transactions(txs):
    """Analyze all transactions for OP_RETURN data."""
    results = []

    for tx in txs:
        txid = tx.get('txid', '')
        block_height = tx.get('status', {}).get('block_height', 0)
        block_time = tx.get('status', {}).get('block_time', 0)

        # Find OP_RETURN outputs
        for vout in tx.get('vout', []):
            script_type = vout.get('scriptpubkey_type', '')
            if script_type == 'op_return':
                script_hex = vout.get('scriptpubkey', '')
                decoded = decode_op_return(script_hex)

                if decoded:
                    results.append({
                        'txid': txid,
                        'block': block_height,
                        'timestamp': datetime.fromtimestamp(block_time).isoformat() if block_time else None,
                        'message': decoded,
                        'script_hex': script_hex
                    })

    return results

def find_patterns(messages):
    """Find interesting patterns in the messages."""
    patterns = {
        'contains_137': [],
        'contains_127': [],
        'contains_576': [],
        'contains_676': [],
        'contains_27': [],
        'contains_satoshi': [],
        'contains_cfb': [],
        'contains_ai': [],
        'contains_future': [],
        'contains_genesis': [],
        'numeric_codes': [],
    }

    for msg in messages:
        text = msg['message'].lower()

        if '137' in text:
            patterns['contains_137'].append(msg)
        if '127' in text:
            patterns['contains_127'].append(msg)
        if '576' in text:
            patterns['contains_576'].append(msg)
        if '676' in text:
            patterns['contains_676'].append(msg)
        if '27' in text and '127' not in text:
            patterns['contains_27'].append(msg)
        if 'satoshi' in text:
            patterns['contains_satoshi'].append(msg)
        if 'cfb' in text:
            patterns['contains_cfb'].append(msg)
        if ' ai' in text or 'ai ' in text or text.endswith('ai'):
            patterns['contains_ai'].append(msg)
        if 'future' in text:
            patterns['contains_future'].append(msg)
        if 'genesis' in text:
            patterns['contains_genesis'].append(msg)

        # Extract L### numbers
        if msg['message'].startswith('L') and len(msg['message']) > 1:
            parts = msg['message'].split(',')
            if parts[0].startswith('L') and parts[0][1:].isdigit():
                patterns['numeric_codes'].append({
                    'code': parts[0],
                    'number': int(parts[0][1:]),
                    'message': msg
                })

    return patterns

def main():
    print("=" * 70)
    print(f"ANALYZING ADDRESS: {ADDRESS}")
    print("=" * 70)
    print()

    # Get all transactions
    print("[1] Fetching transactions...")
    txs = get_all_transactions()
    print(f"Total transactions: {len(txs)}")

    # Analyze for OP_RETURN
    print("\n[2] Analyzing OP_RETURN messages...")
    messages = analyze_transactions(txs)
    print(f"Found {len(messages)} OP_RETURN messages")

    # Find patterns
    print("\n[3] Searching for patterns...")
    patterns = find_patterns(messages)

    # Print all messages
    print("\n" + "=" * 70)
    print("ALL OP_RETURN MESSAGES")
    print("=" * 70)

    for msg in sorted(messages, key=lambda x: x['block'] or 0):
        print(f"\nBlock {msg['block']} | {msg['timestamp']}")
        print(f"  Message: {msg['message'][:100]}{'...' if len(msg['message']) > 100 else ''}")
        print(f"  TX: {msg['txid'][:16]}...")

    # Print pattern findings
    print("\n" + "=" * 70)
    print("PATTERN MATCHES")
    print("=" * 70)

    for pattern_name, matches in patterns.items():
        if matches and pattern_name != 'numeric_codes':
            print(f"\n{pattern_name.upper()}: {len(matches)} matches")
            for m in matches[:3]:
                if isinstance(m, dict) and 'message' in m:
                    print(f"  - {m['message'][:60]}...")

    # Analyze L### numbering
    print("\n" + "=" * 70)
    print("L### CODE ANALYSIS")
    print("=" * 70)

    codes = patterns['numeric_codes']
    if codes:
        codes_sorted = sorted(codes, key=lambda x: x['number'])
        print(f"Total L codes: {len(codes)}")
        print(f"Range: L{codes_sorted[0]['number']} to L{codes_sorted[-1]['number']}")

        # Find gaps
        numbers = [c['number'] for c in codes_sorted]
        expected = set(range(min(numbers), max(numbers) + 1))
        found = set(numbers)
        missing = expected - found

        if missing:
            print(f"Missing codes: {sorted(missing)}")

        # Find special numbers
        special = [137, 127, 108, 64, 27, 42, 23]
        print("\nSpecial number codes:")
        for s in special:
            matches = [c for c in codes if c['number'] == s]
            if matches:
                for m in matches:
                    print(f"  L{s}: {m['message']['message'][:50]}...")

    # Save results
    output = {
        'address': ADDRESS,
        'timestamp': datetime.now().isoformat(),
        'total_transactions': len(txs),
        'op_return_messages': messages,
        'patterns': {k: len(v) for k, v in patterns.items()},
        'l_codes': [{'code': c['code'], 'number': c['number']} for c in patterns['numeric_codes']]
    }

    output_path = Path(__file__).parent / "L137_ADDRESS_ANALYSIS.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n\nResults saved to: {output_path}")

    return 0

if __name__ == "__main__":
    exit(main())
