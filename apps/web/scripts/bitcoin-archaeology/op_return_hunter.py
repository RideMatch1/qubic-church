#!/usr/bin/env python3
"""
Bitcoin OP_RETURN Archaeology Tool
Searches for CFB/Satoshi-relevant patterns in Bitcoin blockchain
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

# Target patterns to search for
SEARCH_PATTERNS = [
    "L127", "L576", "L676", "L137", "L307",
    "BCNext", "come-from-beyond", "cfb", "CfB",
    "aigarth", "AIGARTH", "ternary",
    "QUBIC", "qubic", "Qubic",
    "IOTA", "iota", "Iota",
    "NXT", "nxt", "Nxt",
    "JINN", "jinn", "Jinn",
    "satoshi", "Satoshi", "nakamoto", "Nakamoto",
    "2026", "2027",
    "ternary", "trinary",
    "proof of work", "proof-of-work",
    "quantum", "quorum",
    "genesis",
]

# Known significant addresses
KNOWN_ADDRESSES = {
    "1K69sEhUwNgiva3xzPnToxS89dzydU7nPm": "L137 Sender Address",
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa": "Genesis Block Coinbase",
    "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S": "Hal Finney's Address",
}

class BitcoinArchaeologist:
    def __init__(self):
        self.base_url = "https://blockstream.info/api"
        self.mempool_url = "https://mempool.space/api"
        self.findings = []
        self.address_connections = {}

    def fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[Dict]:
        """Fetch URL with retry logic"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    time.sleep(10 * (attempt + 1))
                else:
                    return None
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                time.sleep(5)
        return None

    def decode_hex_message(self, hex_data: str) -> str:
        """Decode hex to ASCII, handling errors gracefully"""
        try:
            # Remove OP_RETURN prefix if present (6a = OP_RETURN)
            if hex_data.startswith("6a"):
                # Parse length byte(s) and extract data
                pos = 2
                if len(hex_data) > pos:
                    length_byte = int(hex_data[pos:pos+2], 16)
                    if length_byte <= 75:
                        hex_data = hex_data[pos+2:]
                    elif length_byte == 76:  # OP_PUSHDATA1
                        hex_data = hex_data[pos+4:]
                    elif length_byte == 77:  # OP_PUSHDATA2
                        hex_data = hex_data[pos+6:]

            # Decode hex to bytes and try ASCII
            decoded = bytes.fromhex(hex_data).decode('utf-8', errors='replace')
            # Filter out non-printable characters
            printable = ''.join(c if c.isprintable() or c in '\n\r\t' else '?' for c in decoded)
            return printable
        except Exception as e:
            return f"[decode error: {e}]"

    def check_pattern_match(self, message: str) -> List[str]:
        """Check if message matches any search patterns"""
        matches = []
        message_lower = message.lower()
        for pattern in SEARCH_PATTERNS:
            if pattern.lower() in message_lower:
                matches.append(pattern)
        return matches

    def analyze_address(self, address: str) -> Dict[str, Any]:
        """Comprehensive address analysis"""
        print(f"\nAnalyzing address: {address}")

        # Get address info
        addr_info = self.fetch_with_retry(f"{self.base_url}/address/{address}")
        if not addr_info:
            return {"error": "Could not fetch address info"}

        result = {
            "address": address,
            "label": KNOWN_ADDRESSES.get(address, "Unknown"),
            "total_received": addr_info.get("chain_stats", {}).get("funded_txo_sum", 0) / 1e8,
            "total_sent": addr_info.get("chain_stats", {}).get("spent_txo_sum", 0) / 1e8,
            "tx_count": addr_info.get("chain_stats", {}).get("tx_count", 0),
            "transactions": [],
            "connected_addresses": set(),
            "op_return_messages": []
        }

        # Get transactions
        txs = self.fetch_with_retry(f"{self.base_url}/address/{address}/txs")
        if txs:
            for tx in txs[:50]:  # Limit to first 50 for initial analysis
                tx_data = self.analyze_transaction(tx)
                result["transactions"].append(tx_data)

                # Extract connected addresses
                for inp in tx.get("vin", []):
                    if inp.get("prevout", {}).get("scriptpubkey_address"):
                        addr = inp["prevout"]["scriptpubkey_address"]
                        if addr != address:
                            result["connected_addresses"].add(addr)

                for out in tx.get("vout", []):
                    if out.get("scriptpubkey_address"):
                        addr = out["scriptpubkey_address"]
                        if addr != address:
                            result["connected_addresses"].add(addr)

                    # Check for OP_RETURN
                    if out.get("scriptpubkey_type") == "op_return":
                        hex_data = out.get("scriptpubkey", "")
                        decoded = self.decode_hex_message(hex_data)
                        result["op_return_messages"].append({
                            "txid": tx.get("txid"),
                            "hex": hex_data,
                            "decoded": decoded,
                            "block_height": tx.get("status", {}).get("block_height")
                        })

        result["connected_addresses"] = list(result["connected_addresses"])
        return result

    def analyze_transaction(self, tx: Dict) -> Dict[str, Any]:
        """Analyze a single transaction"""
        return {
            "txid": tx.get("txid"),
            "block_height": tx.get("status", {}).get("block_height"),
            "confirmed": tx.get("status", {}).get("confirmed", False),
            "fee": tx.get("fee", 0),
            "size": tx.get("size", 0),
            "input_count": len(tx.get("vin", [])),
            "output_count": len(tx.get("vout", [])),
        }

    def search_op_returns_by_block_range(self, start_block: int, end_block: int) -> List[Dict]:
        """Search for interesting OP_RETURNs in a block range"""
        findings = []

        print(f"\nSearching blocks {start_block} to {end_block}...")

        for block_num in range(start_block, end_block + 1):
            if block_num % 1000 == 0:
                print(f"  Processing block {block_num}...")

            # Get block hash
            block_hash = self.fetch_with_retry(f"{self.base_url}/block-height/{block_num}")
            if not block_hash:
                continue

            # Get block transactions
            block_txs = self.fetch_with_retry(f"{self.base_url}/block/{block_hash}/txs")
            if not block_txs:
                continue

            for tx in block_txs:
                for vout in tx.get("vout", []):
                    if vout.get("scriptpubkey_type") == "op_return":
                        hex_data = vout.get("scriptpubkey", "")
                        decoded = self.decode_hex_message(hex_data)
                        matches = self.check_pattern_match(decoded)

                        if matches:
                            finding = {
                                "block_height": block_num,
                                "txid": tx.get("txid"),
                                "hex": hex_data,
                                "decoded": decoded,
                                "matched_patterns": matches,
                                "block_time": None  # Would need additional API call
                            }
                            findings.append(finding)
                            print(f"  FOUND: {matches} in block {block_num}")

            # Rate limiting
            time.sleep(0.1)

        return findings

    def check_block_digit_sum(self, block_num: int, target_sum: int = 27) -> bool:
        """Check if block number has a specific digit sum"""
        return sum(int(d) for d in str(block_num)) == target_sum

    def find_blocks_with_digit_sum(self, max_block: int, target_sum: int = 27) -> List[int]:
        """Find all blocks with a specific digit sum"""
        return [b for b in range(1, max_block + 1) if self.check_block_digit_sum(b, target_sum)]

    def search_known_op_return_databases(self) -> List[Dict]:
        """Search known OP_RETURN databases and APIs"""
        findings = []

        # Search opreturn.net for known patterns
        print("\nSearching known OP_RETURN databases...")

        # This would require actual API access - placeholder for now
        # In reality, we'd query opreturn.net or similar services

        return findings


def main():
    archaeologist = BitcoinArchaeologist()

    # 1. Analyze the L137 sender address
    print("=" * 60)
    print("TASK 1: Analyzing L137 Sender Address")
    print("=" * 60)

    l137_analysis = archaeologist.analyze_address("1K69sEhUwNgiva3xzPnToxS89dzydU7nPm")

    # Save address analysis
    with open("L137_ADDRESS_ANALYSIS.json", "w") as f:
        json.dump(l137_analysis, f, indent=2, default=list)

    print(f"\nL137 Address Analysis Complete:")
    print(f"  Total TX Count: {l137_analysis.get('tx_count', 'N/A')}")
    print(f"  Total Received: {l137_analysis.get('total_received', 0):.8f} BTC")
    print(f"  Connected Addresses: {len(l137_analysis.get('connected_addresses', []))}")
    print(f"  OP_RETURN Messages Found: {len(l137_analysis.get('op_return_messages', []))}")

    # 2. Find blocks with digit sum 27
    print("\n" + "=" * 60)
    print("TASK 2: Finding Blocks with Digit Sum 27")
    print("=" * 60)

    digit_sum_27_blocks = archaeologist.find_blocks_with_digit_sum(500000, 27)
    print(f"Found {len(digit_sum_27_blocks)} blocks with digit sum 27")
    print(f"First 20: {digit_sum_27_blocks[:20]}")
    print(f"Last 20: {digit_sum_27_blocks[-20:]}")

    # Save blocks list
    with open("BLOCKS_DIGIT_SUM_27.json", "w") as f:
        json.dump({
            "target_digit_sum": 27,
            "total_count": len(digit_sum_27_blocks),
            "blocks": digit_sum_27_blocks
        }, f, indent=2)

    # 3. Compile all findings
    print("\n" + "=" * 60)
    print("COMPILING FINDINGS")
    print("=" * 60)

    all_findings = {
        "timestamp": datetime.now().isoformat(),
        "l137_address_analysis": l137_analysis,
        "blocks_digit_sum_27": {
            "count": len(digit_sum_27_blocks),
            "sample": digit_sum_27_blocks[:100]
        },
        "search_patterns": SEARCH_PATTERNS,
        "known_addresses": KNOWN_ADDRESSES
    }

    with open("ALL_FINDINGS.json", "w") as f:
        json.dump(all_findings, f, indent=2, default=list)

    print("\nAnalysis complete! Results saved to JSON files.")


if __name__ == "__main__":
    main()
