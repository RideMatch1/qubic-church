#!/usr/bin/env python3
"""
BITCOIN RESONANCE MONITOR
=========================

Monitors Bitcoin blockchain for potential responses to Anna Matrix resonance.

Theory: If the Anna Matrix is connected to Satoshi/CFB, a resonance pulse
might trigger activity on:
1. Patoshi addresses
2. Early Bitcoin addresses
3. Genesis-related addresses
4. New blocks with special patterns

Author: MATRIX GOD
Date: 2026-01-16
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Configuration
MEMPOOL_API = "https://mempool.space/api"
BLOCKCHAIN_API = "https://blockchain.info"

# Key addresses to watch (early Satoshi/Patoshi)
WATCH_ADDRESSES = [
    # Genesis block address (block 0 - can't be spent but watch anyway)
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    # Block 9 - First ever transaction (to Hal Finney)
    "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX",
    # Block 1 - First mined block after genesis
    "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S",
    # Patoshi pattern addresses (first few)
    "1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1",  # Block 3
    "1FvzCLoTPGANNjWoUo6jUGuAG3wg1w4YjR",  # Block 4
]

# CFB-related patterns to watch for in coinbase
CFB_PATTERNS = [
    b"CFB",
    b"137",
    b"27",
    b"121",
    b"ANNA",
    b"QUBIC",
    b"MATRIX",
    bytes([0x13, 0x37]),  # 1337 in hex
]


class BitcoinResonanceMonitor:
    """Monitor Bitcoin for resonance responses."""

    def __init__(self):
        self.log_file = Path(__file__).parent / f"btc_resonance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        self.baseline_height = None
        self.watched_addresses = {}

    def log(self, event: str, data: dict):
        """Log event to JSONL."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def get_block_height(self) -> int:
        """Get current Bitcoin block height."""
        try:
            r = requests.get(f"{MEMPOOL_API}/blocks/tip/height", timeout=10)
            return int(r.text)
        except:
            return 0

    def get_latest_block(self) -> dict:
        """Get latest block info."""
        try:
            r = requests.get(f"{MEMPOOL_API}/blocks", timeout=10)
            blocks = r.json()
            if blocks:
                return blocks[0]
        except:
            pass
        return {}

    def get_address_balance(self, address: str) -> dict:
        """Get address balance and tx count."""
        try:
            r = requests.get(f"{MEMPOOL_API}/address/{address}", timeout=10)
            return r.json()
        except:
            return {}

    def check_coinbase_patterns(self, block: dict) -> list:
        """Check coinbase for CFB patterns."""
        matches = []
        # Would need to decode coinbase transaction
        # For now, just check block data
        block_str = json.dumps(block).encode()
        for pattern in CFB_PATTERNS:
            if pattern in block_str:
                matches.append(pattern.decode(errors='ignore'))
        return matches

    def capture_baseline(self):
        """Capture baseline state."""
        print("\n" + "=" * 60)
        print("BITCOIN RESONANCE MONITOR - BASELINE CAPTURE")
        print("=" * 60)

        self.baseline_height = self.get_block_height()
        print(f"Current Block Height: {self.baseline_height}")

        latest = self.get_latest_block()
        if latest:
            print(f"Latest Block Hash: {latest.get('id', 'N/A')[:20]}...")
            print(f"Block Time: {datetime.fromtimestamp(latest.get('timestamp', 0))}")

        print("\nWatched Addresses Baseline:")
        for addr in WATCH_ADDRESSES:
            info = self.get_address_balance(addr)
            self.watched_addresses[addr] = {
                "tx_count": info.get("chain_stats", {}).get("tx_count", 0),
                "balance": info.get("chain_stats", {}).get("funded_txo_sum", 0) -
                          info.get("chain_stats", {}).get("spent_txo_sum", 0)
            }
            print(f"  {addr[:20]}... | TXs: {self.watched_addresses[addr]['tx_count']} | Balance: {self.watched_addresses[addr]['balance']} sats")

        self.log("BASELINE_CAPTURED", {
            "height": self.baseline_height,
            "addresses": self.watched_addresses
        })

    def check_for_activity(self) -> list:
        """Check for any activity on watched addresses."""
        alerts = []

        for addr in WATCH_ADDRESSES:
            current = self.get_address_balance(addr)
            current_tx_count = current.get("chain_stats", {}).get("tx_count", 0)
            baseline_tx_count = self.watched_addresses.get(addr, {}).get("tx_count", 0)

            if current_tx_count > baseline_tx_count:
                alert = {
                    "address": addr,
                    "type": "NEW_TRANSACTION",
                    "old_tx_count": baseline_tx_count,
                    "new_tx_count": current_tx_count
                }
                alerts.append(alert)
                self.log("ALERT_ADDRESS_ACTIVITY", alert)

        return alerts

    def monitor(self, duration_minutes: int = 60):
        """Run monitoring loop."""
        print("\n" + "=" * 60)
        print("BITCOIN RESONANCE MONITOR - ACTIVE")
        print("=" * 60)
        print(f"Duration: {duration_minutes} minutes")
        print(f"Log file: {self.log_file}")
        print("\nMonitoring for:")
        print("  - New blocks")
        print("  - Activity on Satoshi/Patoshi addresses")
        print("  - CFB patterns in coinbase")
        print("\nPress Ctrl+C to stop\n")

        self.capture_baseline()

        start_time = time.time()
        last_height = self.baseline_height
        scan_count = 0

        try:
            while True:
                elapsed = (time.time() - start_time) / 60
                if elapsed >= duration_minutes:
                    print("\n\nDuration reached. Stopping.")
                    break

                time.sleep(30)  # Check every 30 seconds
                scan_count += 1

                current_height = self.get_block_height()
                timestamp = datetime.now().strftime("%H:%M:%S")

                # Check for new block
                if current_height > last_height:
                    blocks_found = current_height - last_height
                    print(f"\n  [{timestamp}] NEW BLOCK(S) FOUND! Height: {current_height} (+{blocks_found})")

                    latest = self.get_latest_block()
                    patterns = self.check_coinbase_patterns(latest)

                    if patterns:
                        print(f"    CFB PATTERN DETECTED: {patterns}")
                        self.log("CFB_PATTERN_FOUND", {"block": current_height, "patterns": patterns})

                    last_height = current_height
                    self.log("NEW_BLOCK", {"height": current_height})

                # Check watched addresses
                alerts = self.check_for_activity()
                if alerts:
                    for alert in alerts:
                        print(f"\n  [{timestamp}] ALERT: Activity on {alert['address'][:20]}...")

                print(f"  [{timestamp}] Block {current_height} | Elapsed: {elapsed:.1f}m | Scan #{scan_count}", end="\r")

        except KeyboardInterrupt:
            print("\n\nMonitor stopped by user.")

        # Summary
        print("\n" + "=" * 60)
        print("MONITORING SUMMARY")
        print("=" * 60)
        final_height = self.get_block_height()
        print(f"Blocks observed: {final_height - self.baseline_height}")
        print(f"Total scans: {scan_count}")
        print(f"Log file: {self.log_file}")

        self.log("MONITOR_STOPPED", {
            "blocks_observed": final_height - self.baseline_height,
            "total_scans": scan_count
        })


def quick_status():
    """Quick status check without monitoring."""
    print("\n" + "=" * 60)
    print("BITCOIN STATUS CHECK")
    print("=" * 60)

    monitor = BitcoinResonanceMonitor()

    height = monitor.get_block_height()
    print(f"Current Block Height: {height}")

    latest = monitor.get_latest_block()
    if latest:
        print(f"Latest Block: {latest.get('id', 'N/A')[:32]}...")
        print(f"Block Time: {datetime.fromtimestamp(latest.get('timestamp', 0))}")
        print(f"TX Count: {latest.get('tx_count', 'N/A')}")
        print(f"Size: {latest.get('size', 'N/A')} bytes")

    print("\nGenesis Address (1A1zP1...):")
    genesis = monitor.get_address_balance("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
    if genesis:
        stats = genesis.get("chain_stats", {})
        print(f"  Total Received: {stats.get('funded_txo_sum', 0) / 1e8:.8f} BTC")
        print(f"  TX Count: {stats.get('tx_count', 0)}")

    # Check for recent movement on early addresses
    print("\nEarly Address Activity Check:")
    for addr in WATCH_ADDRESSES[:3]:
        info = monitor.get_address_balance(addr)
        stats = info.get("chain_stats", {})
        mempool = info.get("mempool_stats", {})
        pending = mempool.get("tx_count", 0)
        print(f"  {addr[:20]}... | TXs: {stats.get('tx_count', 0)} | Pending: {pending}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        monitor = BitcoinResonanceMonitor()
        monitor.monitor(duration_minutes=duration)
    else:
        quick_status()
