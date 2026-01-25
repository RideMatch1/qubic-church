#!/usr/bin/env python3
"""
OP_RETURN Search Tool
=====================

Searches Bitcoin blockchain for specific OP_RETURN patterns.

Methods:
1. Blockchair API (free tier: 10k requests/day)
2. Mempool.space API (no OP_RETURN search, but TX lookup)
3. Local Bitcoin node (requires full node)

Author: qubic-academic-docs
Date: 2026-01-22
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

# Search patterns (hex encoded)
PATTERNS = {
    "676": "363736",           # "676" in ASCII hex
    "CFB": "434642",           # "CFB" in ASCII hex
    "GENESIS": "47454e45534953",  # "GENESIS" in ASCII hex
    "QUBIC": "5155424943",     # "QUBIC" in ASCII hex
    "1CFB": "31434642",        # "1CFB" in ASCII hex
    "SATOSHI": "5341544f534849", # "SATOSHI" in ASCII hex
    "27": "3237",              # "27" in ASCII hex
    "137": "313337",           # "137" in ASCII hex
}

def search_blockchair(pattern_hex: str, pattern_name: str, limit: int = 100) -> list:
    """
    Search Blockchair for OP_RETURN outputs containing pattern.

    Note: Free API has rate limits (10k/day, 1 req/sec)
    """
    results = []

    # Blockchair API endpoint
    url = "https://api.blockchair.com/bitcoin/outputs"
    params = {
        "q": f"type(nulldata),script_hex(~{pattern_hex})",
        "limit": limit,
        "s": "time(desc)"
    }

    try:
        print(f"Searching for '{pattern_name}' (hex: {pattern_hex})...")
        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            outputs = data.get("data", [])

            for output in outputs:
                script_hex = output.get("script_hex", "")
                # Decode OP_RETURN data (skip first 2 bytes: OP_RETURN + push)
                try:
                    # Find the actual data after OP_RETURN (6a) opcode
                    if script_hex.startswith("6a"):
                        # Skip OP_RETURN and length byte
                        data_start = 4  # 6a + length byte
                        if len(script_hex) > data_start:
                            data_hex = script_hex[data_start:]
                            decoded = bytes.fromhex(data_hex).decode('utf-8', errors='replace')
                        else:
                            decoded = "[empty]"
                    else:
                        decoded = "[non-standard]"
                except:
                    decoded = "[decode error]"

                results.append({
                    "tx_hash": output.get("transaction_hash"),
                    "block": output.get("block_id"),
                    "time": output.get("time"),
                    "script_hex": script_hex,
                    "decoded": decoded,
                    "pattern": pattern_name
                })

            print(f"  Found {len(results)} results for '{pattern_name}'")

        elif response.status_code == 402:
            print(f"  API limit reached for Blockchair")
        else:
            print(f"  Error: HTTP {response.status_code}")

    except Exception as e:
        print(f"  Error: {e}")

    return results


def search_known_interesting_txs() -> list:
    """
    Check known interesting transactions with OP_RETURN data.
    These are manually curated based on research.
    """
    known_txs = [
        # HY-OK-676 transaction
        "ab2b1bc3141a40b3bc88a071411c427b68d1daeef62caefef3c6e410cba5d056",
        # LOST numbers transaction
        "0a99123a22138a69da699c21045058863e8ffc3158da14a94cfa162c9720a899",
        # Block 932366 reference
        "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
        # Other known CFB-related TXs (add more as discovered)
    ]

    results = []

    for txid in known_txs:
        try:
            url = f"https://mempool.space/api/tx/{txid}"
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                tx_data = response.json()

                # Find OP_RETURN outputs
                for vout in tx_data.get("vout", []):
                    script_type = vout.get("scriptpubkey_type", "")
                    if script_type == "op_return":
                        script_asm = vout.get("scriptpubkey_asm", "")

                        # Extract the data after OP_RETURN
                        if "OP_RETURN" in script_asm:
                            parts = script_asm.split("OP_RETURN ")
                            if len(parts) > 1:
                                hex_data = parts[1].replace("OP_PUSHBYTES_", "").strip()
                                # Clean up - get just the hex data
                                hex_parts = hex_data.split()
                                if len(hex_parts) > 1:
                                    hex_data = hex_parts[1]

                                try:
                                    decoded = bytes.fromhex(hex_data).decode('utf-8', errors='replace')
                                except:
                                    decoded = hex_data

                                results.append({
                                    "tx_hash": txid,
                                    "block": tx_data.get("status", {}).get("block_height"),
                                    "time": tx_data.get("status", {}).get("block_time"),
                                    "decoded": decoded,
                                    "script_asm": script_asm[:100]
                                })

            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"Error checking {txid[:16]}...: {e}")

    return results


def search_by_address_history(address: str) -> list:
    """
    Get all transactions for an address and check for OP_RETURN.
    Useful for known CFB-related addresses.
    """
    results = []

    try:
        url = f"https://mempool.space/api/address/{address}/txs"
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            txs = response.json()

            for tx in txs:
                for vout in tx.get("vout", []):
                    if vout.get("scriptpubkey_type") == "op_return":
                        script_asm = vout.get("scriptpubkey_asm", "")

                        results.append({
                            "tx_hash": tx.get("txid"),
                            "block": tx.get("status", {}).get("block_height"),
                            "script_asm": script_asm
                        })

    except Exception as e:
        print(f"Error: {e}")

    return results


def decode_op_return(hex_data: str) -> dict:
    """
    Decode OP_RETURN data and analyze for patterns.
    """
    result = {
        "hex": hex_data,
        "ascii": "",
        "contains_676": False,
        "contains_cfb": False,
        "numeric_values": [],
        "letter_sum": 0
    }

    try:
        # ASCII decode
        ascii_text = bytes.fromhex(hex_data).decode('utf-8', errors='replace')
        result["ascii"] = ascii_text

        # Check patterns
        result["contains_676"] = "676" in ascii_text
        result["contains_cfb"] = "cfb" in ascii_text.lower()

        # Extract numbers
        import re
        numbers = re.findall(r'\d+', ascii_text)
        result["numeric_values"] = [int(n) for n in numbers]

        # Letter sum (A=1, B=2, ...)
        letter_sum = sum(ord(c.upper()) - ord('A') + 1
                        for c in ascii_text if c.isalpha())
        result["letter_sum"] = letter_sum

    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    print("=" * 70)
    print("OP_RETURN PATTERN SEARCH")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    all_results = {
        "timestamp": datetime.now().isoformat(),
        "searches": {},
        "known_txs": [],
        "summary": {}
    }

    # Method 1: Search known transactions
    print("\n[1] CHECKING KNOWN INTERESTING TRANSACTIONS")
    print("-" * 70)
    known_results = search_known_interesting_txs()
    all_results["known_txs"] = known_results

    for r in known_results:
        print(f"  TX: {r['tx_hash'][:16]}... Block: {r.get('block', 'N/A')}")
        print(f"      Decoded: {r.get('decoded', 'N/A')[:50]}")

    # Method 2: Search Blockchair for patterns
    print("\n[2] SEARCHING BLOCKCHAIR FOR PATTERNS")
    print("-" * 70)
    print("Note: Free API has rate limits. Using conservative limits.")

    for pattern_name, pattern_hex in PATTERNS.items():
        time.sleep(1.5)  # Rate limiting
        results = search_blockchair(pattern_hex, pattern_name, limit=25)
        all_results["searches"][pattern_name] = results

        if results:
            print(f"\n  Top results for '{pattern_name}':")
            for r in results[:3]:
                print(f"    - Block {r.get('block')}: {r.get('decoded', '')[:40]}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_found = sum(len(v) for v in all_results["searches"].values())
    total_676 = len(all_results["searches"].get("676", []))

    all_results["summary"] = {
        "total_results": total_found,
        "676_matches": total_676,
        "patterns_searched": list(PATTERNS.keys())
    }

    print(f"Total OP_RETURNs found: {total_found}")
    print(f"Containing '676': {total_676}")

    # Save results
    output_path = Path(__file__).parent / "OP_RETURN_SEARCH_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")

    # Helpful links
    print("\n" + "=" * 70)
    print("MANUAL SEARCH OPTIONS")
    print("=" * 70)
    print("""
1. BLOCKCHAIR (Advanced Search):
   https://blockchair.com/bitcoin/outputs?q=type(nulldata)

2. BLOCKCHAIN.COM (OP_RETURN Explorer):
   https://www.blockchain.com/explorer/search?search=OP_RETURN

3. OPRETURN.NET (Dedicated OP_RETURN Index):
   http://opreturn.net/

4. BTCSCAN (Transaction Search):
   https://btcscan.org/

5. Direct Hex Search for "676":
   https://blockchair.com/bitcoin/outputs?q=type(nulldata),script_hex(~363736)

6. Direct Hex Search for "CFB":
   https://blockchair.com/bitcoin/outputs?q=type(nulldata),script_hex(~434642)
""")

    return 0


if __name__ == "__main__":
    exit(main())
