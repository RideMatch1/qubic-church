#!/usr/bin/env python3
"""
ENRICH BLOCK SCAN DATA WITH WALLET ADDRESSES
==============================================

Early Bitcoin blocks (0-~200k) use Pay-to-Public-Key (P2PK) scripts,
not P2PKH. The mempool.space API doesn't return scriptpubkey_address
for these. This script derives the address from the raw public key.

P2PK scriptPubKey format:
  <push_len> <pubkey_65_bytes> OP_CHECKSIG(0xac)

Address derivation:
  PubKey → SHA256 → RIPEMD160 → version(0x00) + hash160 → Base58Check

Usage:
    python3 ENRICH_ADDRESSES.py --input block-scan-results/blocks_9000_10000.json

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-27
"""

import json
import hashlib
import sys
import csv
import time
import argparse
import requests
from pathlib import Path
from collections import Counter

# ==============================================================================
# CRYPTO HELPERS
# ==============================================================================

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def ripemd160(data: bytes) -> bytes:
    return hashlib.new('ripemd160', data).digest()

def hash160(data: bytes) -> bytes:
    """Bitcoin Hash160: SHA256 then RIPEMD160"""
    return ripemd160(sha256(data))

def base58_encode(payload: bytes) -> str:
    """Base58 encode (Bitcoin style)"""
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = int.from_bytes(payload, 'big')
    result = []
    while n > 0:
        n, remainder = divmod(n, 58)
        result.append(alphabet[remainder])
    # Leading zero bytes → '1' characters
    for byte in payload:
        if byte == 0:
            result.append('1')
        else:
            break
    return ''.join(reversed(result))

def base58check_encode(version: int, payload: bytes) -> str:
    """Base58Check encode with version byte and checksum"""
    versioned = bytes([version]) + payload
    checksum = sha256(sha256(versioned))[:4]
    return base58_encode(versioned + checksum)

def pubkey_to_address(pubkey_hex: str) -> str:
    """Convert a public key (hex) to a Bitcoin P2PKH address.

    Supports:
    - Uncompressed: 04 + 64 bytes (65 bytes total)
    - Compressed: 02/03 + 32 bytes (33 bytes total)
    """
    try:
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        h160 = hash160(pubkey_bytes)
        return base58check_encode(0x00, h160)  # Mainnet version byte
    except (ValueError, TypeError):
        return ""

def extract_pubkey_from_p2pk(scriptpubkey_hex: str) -> str:
    """Extract public key from P2PK scriptPubKey.

    P2PK format: <push_length> <pubkey> OP_CHECKSIG(ac)

    Uncompressed: 41 <65_bytes_pubkey> ac
    Compressed:   21 <33_bytes_pubkey> ac
    """
    if not scriptpubkey_hex:
        return ""

    # Uncompressed P2PK: 41 + 65 bytes + ac = 134 hex chars
    if len(scriptpubkey_hex) == 134 and scriptpubkey_hex.endswith("ac"):
        push_len = int(scriptpubkey_hex[:2], 16)
        if push_len == 65:
            return scriptpubkey_hex[2:-2]  # Remove push byte and OP_CHECKSIG

    # Compressed P2PK: 21 + 33 bytes + ac = 70 hex chars
    if len(scriptpubkey_hex) == 70 and scriptpubkey_hex.endswith("ac"):
        push_len = int(scriptpubkey_hex[:2], 16)
        if push_len == 33:
            return scriptpubkey_hex[2:-2]

    return ""


# ==============================================================================
# ENRICHMENT - FROM EXISTING SCAN DATA (no API needed)
# ==============================================================================

def enrich_from_scan(input_file: Path) -> dict:
    """
    Enrich blocks with addresses, but our scan doesn't store scriptpubkey.
    We need to re-fetch coinbase tx outputs for the pubkey.
    """
    print("Note: Existing scan data doesn't include scriptpubkey.")
    print("Need to fetch coinbase tx vout data for each block.")
    return None


# ==============================================================================
# FETCH AND ENRICH
# ==============================================================================

class AddressEnricher:
    """Fetches coinbase output pubkeys and derives addresses."""

    def __init__(self, input_file: Path):
        self.input_file = input_file
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "QubicAcademicResearch/1.0"})
        self.last_request = 0
        self.request_count = 0

    def _rate_limit(self, delay=0.12):
        elapsed = time.time() - self.last_request
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self.last_request = time.time()

    def fetch(self, url: str):
        for attempt in range(3):
            self._rate_limit()
            try:
                resp = self.session.get(url, timeout=20)
                self.request_count += 1
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 429:
                    time.sleep(5 * (attempt + 1))
                else:
                    return None
            except Exception as e:
                time.sleep(3)
        return None

    def get_coinbase_outputs(self, block_hash: str) -> list:
        """Fetch coinbase tx outputs for a block."""
        txs = self.fetch(f"https://mempool.space/api/block/{block_hash}/txs/0")
        if not txs or len(txs) == 0:
            return []

        cb_tx = txs[0]
        outputs = []
        for vout in cb_tx.get("vout", []):
            script_hex = vout.get("scriptpubkey", "")
            script_type = vout.get("scriptpubkey_type", "")
            address = vout.get("scriptpubkey_address", "")
            value = vout.get("value", 0)

            # Derive address if not present
            if not address and script_type == "p2pk":
                pubkey = extract_pubkey_from_p2pk(script_hex)
                if pubkey:
                    address = pubkey_to_address(pubkey)

            outputs.append({
                "address": address,
                "value_sat": value,
                "script_type": script_type,
                "pubkey": extract_pubkey_from_p2pk(script_hex) if script_type == "p2pk" else "",
            })

        return outputs

    def run(self):
        """Enrich all blocks with addresses."""
        print("=" * 70)
        print("ENRICHING BLOCK DATA WITH WALLET ADDRESSES")
        print("=" * 70)

        with open(self.input_file) as f:
            data = json.load(f)

        blocks = data.get("blocks", {})
        total = len(blocks)
        print(f"Blocks to process: {total}")
        print(f"API: mempool.space (1 request per block)")
        print()

        t_start = time.time()
        enriched_count = 0
        errors = 0
        address_counter = Counter()

        sorted_heights = sorted(blocks.keys(), key=int)

        for i, height_str in enumerate(sorted_heights):
            block = blocks[height_str]
            block_hash = block.get("hash", "")

            pct = (i + 1) / total * 100
            elapsed = time.time() - t_start
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            remaining = (total - i - 1) / rate if rate > 0 else 0

            sys.stdout.write(
                f"\r[{pct:5.1f}%] Block {height_str} | "
                f"{rate:.1f} blk/s | "
                f"ETA {int(remaining // 60)}m{int(remaining % 60):02d}s | "
                f"Enriched: {enriched_count}"
            )
            sys.stdout.flush()

            if not block_hash:
                errors += 1
                continue

            try:
                outputs = self.get_coinbase_outputs(block_hash)
                if outputs:
                    block["coinbase"]["output_details"] = outputs
                    block["coinbase"]["output_addresses"] = [
                        o["address"] for o in outputs if o["address"]
                    ]
                    enriched_count += 1

                    for o in outputs:
                        if o["address"]:
                            address_counter[o["address"]] += 1
                else:
                    errors += 1

            except KeyboardInterrupt:
                print(f"\n\nInterrupted. Saving partial results...")
                break
            except Exception as e:
                errors += 1

            # Save progress every 100 blocks
            if (i + 1) % 100 == 0:
                data["blocks"] = blocks
                with open(self.input_file, "w") as f:
                    json.dump(data, f, indent=2)

        # Final save
        data["blocks"] = blocks
        data["address_enrichment"] = {
            "enriched": enriched_count,
            "errors": errors,
            "unique_addresses": len(address_counter),
            "api_requests": self.request_count,
        }

        with open(self.input_file, "w") as f:
            json.dump(data, f, indent=2)

        elapsed_total = time.time() - t_start
        print(f"\n\nDone in {elapsed_total:.0f}s ({elapsed_total / 60:.1f}m)")
        print(f"Enriched: {enriched_count}/{total}")
        print(f"Errors: {errors}")
        print(f"Unique addresses: {len(address_counter)}")
        print(f"API requests: {self.request_count}")

        # Address frequency table
        print(f"\n{'=' * 70}")
        print("TOP ADDRESSES BY BLOCK COUNT")
        print(f"{'=' * 70}")
        print(f"{'Address':<36} | {'Blocks':>6} | {'% of total':>8}")
        print("-" * 58)
        for addr, count in address_counter.most_common(30):
            pct = count / total * 100
            print(f"{addr:<36} | {count:>6} | {pct:>7.1f}%")

        # Export address CSV
        output_dir = self.input_file.parent
        start = data.get("scan_range", {}).get("start", 0)
        end = data.get("scan_range", {}).get("end", 0)

        addr_csv = output_dir / f"addresses_{start}_{end}.csv"
        with open(addr_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Block", "Date", "Address", "Value_BTC", "Script_Type", "PubKey"])
            for h in sorted_heights:
                block = blocks[h]
                details = block.get("coinbase", {}).get("output_details", [])
                for o in details:
                    writer.writerow([
                        h,
                        block.get("date", "")[:10],
                        o.get("address", ""),
                        o.get("value_sat", 0) / 1e8,
                        o.get("script_type", ""),
                        o.get("pubkey", "")[:32] + "..." if len(o.get("pubkey", "")) > 32 else o.get("pubkey", ""),
                    ])
        print(f"\nAddress CSV: {addr_csv}")

        # Export address frequency
        freq_csv = output_dir / f"address_frequency_{start}_{end}.csv"
        with open(freq_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Address", "Block_Count", "Percentage"])
            for addr, count in address_counter.most_common():
                writer.writerow([addr, count, round(count / total * 100, 2)])
        print(f"Frequency CSV: {freq_csv}")

        return address_counter


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich block scan with wallet addresses")
    parser.add_argument("--input", type=str, required=True, help="blocks_X_Y.json from BLOCK_RANGE_SCANNER")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    enricher = AddressEnricher(input_path)
    enricher.run()
