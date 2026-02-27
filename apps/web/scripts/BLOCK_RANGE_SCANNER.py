#!/usr/bin/env python3
"""
BITCOIN BLOCK RANGE SCANNER
============================

Scans a configurable range of Bitcoin blocks and extracts:
- Coinbase scriptSig (hex + ASCII decode)
- OP_RETURN outputs from all transactions
- Block metadata (hash, timestamp, tx count, size)

Primary API: mempool.space (most reliable, ~10 req/s)
Fallback: blockstream.info

Features:
- Resumable progress (saves state to JSON)
- Rate limiting with backoff
- Full results export

Usage:
    python3 BLOCK_RANGE_SCANNER.py --start 9000 --end 10000
    python3 BLOCK_RANGE_SCANNER.py --start 9000 --end 10000 --resume
    python3 BLOCK_RANGE_SCANNER.py --start 9000 --end 10000 --export-csv

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-26
"""

import requests
import json
import time
import csv
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# ==============================================================================
# CONFIGURATION
# ==============================================================================

MEMPOOL_API = "https://mempool.space/api"
BLOCKSTREAM_API = "https://blockstream.info/api"
RATE_LIMIT = 0.15  # seconds between requests (safe for mempool.space)
RETRY_DELAY = 5    # seconds on 429/error
MAX_RETRIES = 3

OUTPUT_DIR = Path(__file__).parent / "block-scan-results"


# ==============================================================================
# API LAYER
# ==============================================================================

class BlockchainAPI:
    """Handles API calls with retry logic and rate limiting."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "QubicAcademicResearch/1.0"})
        self.request_count = 0
        self.last_request_time = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT:
            time.sleep(RATE_LIMIT - elapsed)
        self.last_request_time = time.time()

    def fetch(self, url: str, as_text: bool = False) -> Optional[any]:
        for attempt in range(MAX_RETRIES):
            self._rate_limit()
            try:
                resp = self.session.get(url, timeout=20)
                self.request_count += 1

                if resp.status_code == 200:
                    return resp.text.strip() if as_text else resp.json()
                elif resp.status_code == 429:
                    wait = RETRY_DELAY * (attempt + 1)
                    print(f"  Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                    else:
                        return None
            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"  Network error: {e}")
                    return None
        return None

    def get_block_hash(self, height: int) -> Optional[str]:
        return self.fetch(f"{MEMPOOL_API}/block-height/{height}", as_text=True)

    def get_block(self, block_hash: str) -> Optional[Dict]:
        return self.fetch(f"{MEMPOOL_API}/block/{block_hash}")

    def get_block_txs(self, block_hash: str, start_index: int = 0) -> Optional[List]:
        return self.fetch(f"{MEMPOOL_API}/block/{block_hash}/txs/{start_index}")


# ==============================================================================
# DATA EXTRACTION
# ==============================================================================

def decode_hex_to_ascii(hex_str: str) -> str:
    """Decode hex string to printable ASCII, replacing non-printable with dots."""
    try:
        raw = bytes.fromhex(hex_str)
        return "".join(chr(b) if 32 <= b <= 126 else "." for b in raw)
    except (ValueError, TypeError):
        return ""


def extract_coinbase_data(tx: Dict) -> Dict:
    """Extract coinbase information from the first transaction."""
    result = {
        "txid": tx.get("txid", ""),
        "scriptsig_hex": "",
        "scriptsig_ascii": "",
        "scriptsig_bytes": [],
        "witness": [],
        "output_value_sat": 0,
        "output_addresses": [],
    }

    # Coinbase input
    if "vin" in tx and len(tx["vin"]) > 0:
        vin = tx["vin"][0]
        scriptsig = vin.get("scriptsig", "") or vin.get("scriptsig_asm", "")

        if scriptsig:
            result["scriptsig_hex"] = scriptsig
            result["scriptsig_ascii"] = decode_hex_to_ascii(scriptsig)

            # Byte-level breakdown (first 64 bytes max)
            try:
                raw = bytes.fromhex(scriptsig)
                result["scriptsig_bytes"] = [
                    {"pos": i, "hex": f"{b:02x}", "dec": b, "char": chr(b) if 32 <= b <= 126 else "."}
                    for i, b in enumerate(raw[:64])
                ]
            except ValueError:
                pass

        # Witness data (SegWit coinbase)
        if "witness" in vin:
            result["witness"] = vin["witness"]

    # Outputs
    if "vout" in tx:
        for vout in tx["vout"]:
            result["output_value_sat"] += vout.get("value", 0)
            addr = vout.get("scriptpubkey_address", "")
            if addr:
                result["output_addresses"].append(addr)

    return result


def extract_op_returns(txs: List[Dict]) -> List[Dict]:
    """Extract all OP_RETURN outputs from a list of transactions."""
    op_returns = []

    for tx in txs:
        if "vout" not in tx:
            continue

        for vout_idx, vout in enumerate(tx["vout"]):
            script_type = vout.get("scriptpubkey_type", "")
            script_hex = vout.get("scriptpubkey", "")

            # OP_RETURN starts with 0x6a
            if script_type == "op_return" or (script_hex and script_hex.startswith("6a")):
                # Extract data after OP_RETURN opcode
                data_hex = ""
                if script_hex.startswith("6a"):
                    pos = 2
                    if len(script_hex) > pos + 2:
                        length_byte = int(script_hex[pos:pos + 2], 16)
                        if length_byte <= 75:
                            data_hex = script_hex[pos + 2:]
                        elif length_byte == 0x4c:  # OP_PUSHDATA1
                            data_hex = script_hex[pos + 4:]
                        elif length_byte == 0x4d:  # OP_PUSHDATA2
                            data_hex = script_hex[pos + 6:]
                        else:
                            data_hex = script_hex[pos + 2:]
                    else:
                        data_hex = script_hex[pos:]

                op_returns.append({
                    "txid": tx.get("txid", ""),
                    "vout_index": vout_idx,
                    "script_hex": script_hex,
                    "data_hex": data_hex,
                    "data_ascii": decode_hex_to_ascii(data_hex) if data_hex else "",
                    "value_sat": vout.get("value", 0),
                })

    return op_returns


# ==============================================================================
# SCANNER
# ==============================================================================

class BlockRangeScanner:
    """Scans a range of Bitcoin blocks and extracts data."""

    def __init__(self, start: int, end: int, output_dir: Path = OUTPUT_DIR):
        self.start = start
        self.end = end
        self.api = BlockchainAPI()
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.progress_file = self.output_dir / f"progress_{start}_{end}.json"
        self.results_file = self.output_dir / f"blocks_{start}_{end}.json"

        self.results = {}
        self.errors = []

    def load_progress(self) -> int:
        """Load previous progress, returns last completed block height."""
        if self.progress_file.exists():
            with open(self.progress_file, "r") as f:
                data = json.load(f)
            self.results = data.get("results", {})
            self.errors = data.get("errors", [])
            return data.get("last_completed", self.start - 1)
        return self.start - 1

    def save_progress(self, last_completed: int):
        """Save current progress."""
        with open(self.progress_file, "w") as f:
            json.dump({
                "last_completed": last_completed,
                "start": self.start,
                "end": self.end,
                "scan_time": datetime.now(timezone.utc).isoformat(),
                "results": self.results,
                "errors": self.errors,
            }, f, indent=2)

    def save_results(self):
        """Save final results."""
        summary = {
            "scan_range": {"start": self.start, "end": self.end},
            "total_blocks": len(self.results),
            "total_errors": len(self.errors),
            "total_op_returns": sum(
                len(b.get("op_returns", [])) for b in self.results.values()
            ),
            "coinbase_messages": [],
            "scan_completed": datetime.now(timezone.utc).isoformat(),
            "api_requests": self.api.request_count,
            "blocks": self.results,
            "errors": self.errors,
        }

        # Collect non-empty coinbase messages
        for height_str, block in sorted(self.results.items(), key=lambda x: int(x[0])):
            cb = block.get("coinbase", {})
            ascii_msg = cb.get("scriptsig_ascii", "").strip(".")
            if ascii_msg and len(ascii_msg) > 2:
                summary["coinbase_messages"].append({
                    "block": int(height_str),
                    "message": ascii_msg,
                    "hex": cb.get("scriptsig_hex", ""),
                })

        with open(self.results_file, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\nResults saved to: {self.results_file}")
        return summary

    def scan_block(self, height: int) -> Optional[Dict]:
        """Scan a single block."""
        # 1. Get block hash
        block_hash = self.api.get_block_hash(height)
        if not block_hash:
            return None

        # 2. Get block metadata
        block_data = self.api.get_block(block_hash)
        if not block_data:
            return None

        # 3. Get transactions
        txs = self.api.get_block_txs(block_hash)
        if not txs:
            return None

        # 4. Extract coinbase
        coinbase = extract_coinbase_data(txs[0]) if txs else {}

        # 5. Extract OP_RETURNs from all txs
        op_returns = extract_op_returns(txs)

        # 6. If more than 25 txs, fetch remaining pages
        tx_count = block_data.get("tx_count", len(txs))
        if tx_count > 25:
            for offset in range(25, tx_count, 25):
                more_txs = self.api.get_block_txs(block_hash, offset)
                if more_txs:
                    op_returns.extend(extract_op_returns(more_txs))

        timestamp = block_data.get("timestamp", 0)

        return {
            "height": height,
            "hash": block_hash,
            "timestamp": timestamp,
            "date": datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat() if timestamp else "",
            "tx_count": tx_count,
            "size": block_data.get("size", 0),
            "weight": block_data.get("weight", 0),
            "nonce": block_data.get("nonce", 0),
            "difficulty": block_data.get("difficulty", 0),
            "coinbase": coinbase,
            "op_returns": op_returns,
        }

    def run(self, resume: bool = False):
        """Run the scanner."""
        last_done = self.load_progress() if resume else self.start - 1
        start_from = last_done + 1
        total = self.end - self.start + 1
        done_count = start_from - self.start

        print("=" * 70)
        print(f"BITCOIN BLOCK RANGE SCANNER")
        print(f"Range: {self.start} - {self.end} ({total} blocks)")
        if resume and done_count > 0:
            print(f"Resuming from block {start_from} ({done_count} already done)")
        print(f"API: mempool.space")
        print(f"Output: {self.output_dir}")
        print("=" * 70)
        print()

        t_start = time.time()

        for height in range(start_from, self.end + 1):
            progress = height - self.start + 1
            pct = progress / total * 100

            # Status line
            elapsed = time.time() - t_start
            blocks_done = height - start_from + 1
            rate = blocks_done / elapsed if elapsed > 0 else 0
            remaining = (self.end - height) / rate if rate > 0 else 0

            sys.stdout.write(
                f"\r[{pct:5.1f}%] Block {height}/{self.end} | "
                f"{rate:.1f} blk/s | "
                f"ETA {int(remaining // 60)}m{int(remaining % 60):02d}s | "
                f"OP_RET: {sum(len(b.get('op_returns', [])) for b in self.results.values())} | "
                f"Errors: {len(self.errors)}"
            )
            sys.stdout.flush()

            try:
                block = self.scan_block(height)

                if block:
                    self.results[str(height)] = block

                    # Print interesting findings inline
                    cb_ascii = block["coinbase"].get("scriptsig_ascii", "")
                    clean = cb_ascii.replace(".", "").strip()
                    if len(clean) > 3:
                        print(f"\n  >> Block {height} coinbase: {cb_ascii[:80]}")

                    if block["op_returns"]:
                        for opr in block["op_returns"]:
                            print(f"\n  >> Block {height} OP_RETURN: {opr['data_ascii'][:80]}")
                else:
                    self.errors.append({"height": height, "error": "fetch_failed"})

            except KeyboardInterrupt:
                print(f"\n\nInterrupted at block {height}. Saving progress...")
                self.save_progress(height - 1)
                self.save_results()
                print("You can resume with --resume")
                sys.exit(0)

            except Exception as e:
                self.errors.append({"height": height, "error": str(e)})
                print(f"\n  Error at block {height}: {e}")

            # Save progress every 50 blocks
            if height % 50 == 0:
                self.save_progress(height)

        # Final save
        self.save_progress(self.end)
        summary = self.save_results()

        elapsed_total = time.time() - t_start
        print(f"\n\nDone in {elapsed_total:.0f}s ({elapsed_total/60:.1f}m)")
        print(f"Blocks scanned: {len(self.results)}")
        print(f"Errors: {len(self.errors)}")
        print(f"OP_RETURNs found: {summary['total_op_returns']}")
        print(f"Coinbase messages: {len(summary['coinbase_messages'])}")
        print(f"API requests: {self.api.request_count}")

        return summary


def export_csv(results_file: Path):
    """Export results to CSV for easy viewing."""
    with open(results_file, "r") as f:
        data = json.load(f)

    csv_file = results_file.with_suffix(".csv")
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Block", "Hash", "Date", "TX Count", "Nonce",
            "Coinbase ASCII", "Coinbase Hex",
            "OP_RETURN Count", "OP_RETURN Data"
        ])

        for height_str, block in sorted(data["blocks"].items(), key=lambda x: int(x[0])):
            cb = block.get("coinbase", {})
            op_rets = block.get("op_returns", [])
            op_ret_text = " | ".join(o.get("data_ascii", "") for o in op_rets) if op_rets else ""

            writer.writerow([
                block["height"],
                block["hash"][:16] + "...",
                block.get("date", ""),
                block.get("tx_count", 0),
                block.get("nonce", 0),
                cb.get("scriptsig_ascii", ""),
                cb.get("scriptsig_hex", "")[:64] + "..." if len(cb.get("scriptsig_hex", "")) > 64 else cb.get("scriptsig_hex", ""),
                len(op_rets),
                op_ret_text[:200],
            ])

    print(f"CSV exported to: {csv_file}")


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bitcoin Block Range Scanner")
    parser.add_argument("--start", type=int, default=9000, help="Start block height (default: 9000)")
    parser.add_argument("--end", type=int, default=10000, help="End block height (default: 10000)")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--export-csv", action="store_true", help="Export existing results to CSV")
    args = parser.parse_args()

    if args.export_csv:
        results_path = OUTPUT_DIR / f"blocks_{args.start}_{args.end}.json"
        if results_path.exists():
            export_csv(results_path)
        else:
            print(f"No results found at {results_path}")
            print("Run the scanner first.")
        sys.exit(0)

    scanner = BlockRangeScanner(args.start, args.end)
    scanner.run(resume=args.resume)

    # Auto-export CSV
    if scanner.results_file.exists():
        export_csv(scanner.results_file)
