#!/usr/bin/env python3
"""
MANHATTAN PROJECT - Phase 5: Resonance Monitor
================================================

Monitors strategic node activity before, during, and after resonance tests.
Tracks balances, incoming/outgoing transactions, and network state.

Features:
- Real-time balance monitoring
- Transaction history tracking
- Tick progression monitoring
- JSON log output for analysis

Author: qubic-academic-docs
Date: 2026-01-16
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("ERROR: requests library required. Install: pip install requests")

# Configuration
RPC_URL = "https://rpc.qubic.org"
TIMEOUT = 10

# Verified strategic nodes (from Phase 1)
STRATEGIC_NODES = {
    "ENTRY": {
        "identity": "VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH",
        "coords": (45, 92),
        "verified": True
    },
    "VOID": {
        "identity": "SCBGQAOHIGFHPCJCMYNYUBIOKJWCKAWGGSLFTXLZSGWZRLOODRUPTDNCYBEB",
        "coords": (0, 0),
        "verified": True
    },
    "GUARDIAN": {
        "identity": "DXASUXXKJAEJVGQEUXLIVNIQWDUCCNFTLEHCDCNZNBVGLPRTJRUQKZDECIPG",
        "coords": (19, 18),
        "verified": True
    },
    "DATE": {
        "identity": "MOHTKRBCAEAASFFQQSKLAFBLMZAAKFEJRHIGOQRLOGFKFXZGOXZNSSVDEOOG",
        "coords": (3, 3),
        "verified": True
    },
    "ORACLE": {
        "identity": "PASOUKIEPXXPXEMUNBKYCPSEIXZBWQCDFZXLUAEBHHENNEHTQNGMMFRGZHHA",
        "coords": (11, 110),
        "verified": True
    },
    "ROOT_ALPHA": {
        "identity": "AHMXRLTHWSCUUGTBCJXRSMRZDOAAZVCKNFIYDYDLQDQRZETRZMAQYHBACSWK",
        "coords": (13, 71),
        "verified": True
    },
    "ROOT_BETA": {
        "identity": "OUMLINFCVWOAFCCPDDRUJARXUKJBJQUYVZFLIUKUUATMEQEIWOIUXHYGQERC",
        "coords": (18, 110),
        "verified": True
    },
    "CORE": {
        "identity": "DWQNESYCKKBXIGOJHQOEHUHMALBADTWFYKNKFRNKOEZYMPEZNJMUEPAFBROB",
        "coords": (6, 33),
        "verified": True,
        "note": "Derived from cartography - not pre-existing"
    }
}


class ResonanceMonitor:
    """Real-time strategic node activity monitor."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent
        self.log_file = self.output_dir / f"resonance_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        self.baseline: Dict[str, dict] = {}
        self.alerts: List[dict] = []

    def log_event(self, event_type: str, data: dict):
        """Log an event to the JSONL log file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tick": self.get_current_tick(),
            "event": event_type,
            "data": data
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def get_current_tick(self) -> Optional[int]:
        """Fetch current tick from RPC."""
        try:
            r = requests.get(f"{RPC_URL}/v1/tick-info", timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json().get('tickInfo', {}).get('tick', 0)
        except:
            pass
        return None

    def get_node_status(self, identity: str) -> Optional[dict]:
        """Fetch balance and activity for a node."""
        try:
            r = requests.get(f"{RPC_URL}/v1/balances/{identity}", timeout=TIMEOUT)
            if r.status_code == 200:
                data = r.json().get('balance', {})
                return {
                    "balance": data.get('balance', 0),
                    "validForTick": data.get('validForTick', 0),
                    "lastInTick": data.get('latestIncomingTransferTick', 0),
                    "lastOutTick": data.get('latestOutgoingTransferTick', 0),
                    "numberOfInTransfers": data.get('numberOfIncomingTransfers', 0),
                    "numberOfOutTransfers": data.get('numberOfOutgoingTransfers', 0)
                }
        except Exception as e:
            return {"error": str(e)}
        return None

    def capture_baseline(self):
        """Capture baseline state of all nodes."""
        print("\n📊 CAPTURING BASELINE STATE")
        print("=" * 60)

        current_tick = self.get_current_tick()
        print(f"Current Tick: {current_tick}")
        print()

        self.baseline = {}

        for name, node in STRATEGIC_NODES.items():
            status = self.get_node_status(node["identity"])
            if status:
                self.baseline[name] = status
                print(f"  {name:12} | Balance: {status.get('balance', 'N/A'):>15} | "
                      f"In: {status.get('lastInTick', 0):>10} | Out: {status.get('lastOutTick', 0):>10}")
            else:
                print(f"  {name:12} | ERROR fetching status")

        # Log baseline
        self.log_event("BASELINE_CAPTURED", {
            "tick": current_tick,
            "nodes": self.baseline
        })

        return self.baseline

    def check_for_changes(self) -> List[dict]:
        """Check for changes since baseline."""
        changes = []

        for name, node in STRATEGIC_NODES.items():
            if name not in self.baseline:
                continue

            current = self.get_node_status(node["identity"])
            if not current or "error" in current:
                continue

            baseline = self.baseline[name]

            # Check for balance change
            if current.get('balance') != baseline.get('balance'):
                changes.append({
                    "node": name,
                    "type": "BALANCE_CHANGE",
                    "old": baseline.get('balance'),
                    "new": current.get('balance')
                })

            # Check for new incoming transfer
            if current.get('lastInTick', 0) > baseline.get('lastInTick', 0):
                changes.append({
                    "node": name,
                    "type": "INCOMING_TRANSFER",
                    "tick": current.get('lastInTick')
                })

            # Check for new outgoing transfer (RESPONSE!)
            if current.get('lastOutTick', 0) > baseline.get('lastOutTick', 0):
                changes.append({
                    "node": name,
                    "type": "OUTGOING_TRANSFER",
                    "tick": current.get('lastOutTick'),
                    "alert": "POSSIBLE RESPONSE DETECTED!"
                })
                self.alerts.append({
                    "time": datetime.now().isoformat(),
                    "node": name,
                    "type": "OUTGOING_TRANSFER",
                    "tick": current.get('lastOutTick')
                })

        return changes

    def single_scan(self):
        """Perform a single scan and report."""
        print("\n" + "=" * 60)
        print("RESONANCE MONITOR - SINGLE SCAN")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")

        current_tick = self.get_current_tick()
        print(f"Current Tick: {current_tick}")
        print()

        print(f"{'Node':<12} {'Balance':>15} {'Last In':>10} {'Last Out':>10} {'# In':>6} {'# Out':>6}")
        print("-" * 70)

        for name, node in STRATEGIC_NODES.items():
            status = self.get_node_status(node["identity"])
            if status and "error" not in status:
                print(f"{name:<12} {status['balance']:>15} {status['lastInTick']:>10} "
                      f"{status['lastOutTick']:>10} {status['numberOfInTransfers']:>6} "
                      f"{status['numberOfOutTransfers']:>6}")
            else:
                print(f"{name:<12} {'ERROR':>15}")

        # Log scan
        self.log_event("SINGLE_SCAN", {"tick": current_tick})

    def monitor_loop(self, interval: int = 30, duration: int = 0):
        """Continuous monitoring loop."""
        print("\n" + "=" * 60)
        print("RESONANCE MONITOR - CONTINUOUS MODE")
        print("=" * 60)
        print(f"Interval: {interval} seconds")
        print(f"Duration: {'Indefinite' if duration == 0 else f'{duration} seconds'}")
        print(f"Log file: {self.log_file}")
        print()
        print("Press Ctrl+C to stop")
        print()

        # Capture baseline
        self.capture_baseline()

        start_time = time.time()
        scan_count = 0

        try:
            while True:
                # Check duration
                if duration > 0 and (time.time() - start_time) >= duration:
                    print("\n⏰ Duration reached. Stopping monitor.")
                    break

                time.sleep(interval)
                scan_count += 1

                # Check for changes
                changes = self.check_for_changes()

                timestamp = datetime.now().strftime("%H:%M:%S")
                tick = self.get_current_tick()

                if changes:
                    print(f"\n[{timestamp}] Tick {tick} - CHANGES DETECTED!")
                    for change in changes:
                        self.log_event("CHANGE_DETECTED", change)
                        if change.get('alert'):
                            print(f"  🚨 {change['node']}: {change['type']} - {change['alert']}")
                        else:
                            print(f"  📍 {change['node']}: {change['type']}")
                else:
                    print(f"[{timestamp}] Tick {tick} - No changes (scan #{scan_count})", end="\r")

        except KeyboardInterrupt:
            print("\n\n⏹️  Monitor stopped by user")

        # Final summary
        print("\n" + "=" * 60)
        print("MONITORING SUMMARY")
        print("=" * 60)
        print(f"Total scans: {scan_count}")
        print(f"Total alerts: {len(self.alerts)}")
        print(f"Log file: {self.log_file}")

        if self.alerts:
            print("\n🚨 ALERTS DETECTED:")
            for alert in self.alerts:
                print(f"  - {alert['time']}: {alert['node']} {alert['type']} at tick {alert['tick']}")

        # Save final state
        self.log_event("MONITOR_STOPPED", {
            "total_scans": scan_count,
            "total_alerts": len(self.alerts),
            "alerts": self.alerts
        })

    def dry_run(self):
        """Dry run - test monitor without continuous loop."""
        print("\n" + "=" * 60)
        print("RESONANCE MONITOR - DRY RUN TEST")
        print("=" * 60)
        print()

        # Test 1: RPC connectivity
        print("[1/4] Testing RPC connectivity...")
        tick = self.get_current_tick()
        if tick:
            print(f"  ✓ Current tick: {tick}")
        else:
            print("  ✗ Failed to fetch tick")
            return 1

        # Test 2: Node status fetch
        print("\n[2/4] Testing node status fetch...")
        test_node = "ENTRY"
        status = self.get_node_status(STRATEGIC_NODES[test_node]["identity"])
        if status and "error" not in status:
            print(f"  ✓ {test_node} balance: {status['balance']}")
        else:
            print(f"  ✗ Failed to fetch {test_node} status")
            return 1

        # Test 3: Baseline capture
        print("\n[3/4] Testing baseline capture...")
        baseline = self.capture_baseline()
        if baseline:
            print(f"  ✓ Captured {len(baseline)} node baselines")
        else:
            print("  ✗ Failed to capture baseline")
            return 1

        # Test 4: Log writing
        print("\n[4/4] Testing log output...")
        self.log_event("DRY_RUN_TEST", {"test": "successful"})
        if self.log_file.exists():
            print(f"  ✓ Log file created: {self.log_file}")
        else:
            print("  ✗ Failed to create log file")
            return 1

        print("\n" + "=" * 60)
        print("DRY RUN COMPLETE - Monitor is ready for use!")
        print("=" * 60)
        return 0


def main():
    parser = argparse.ArgumentParser(description="Resonance Monitor for Anna Matrix Strategic Nodes")
    parser.add_argument("--mode", choices=["scan", "monitor", "dry-run"], default="scan",
                        help="Operation mode: scan (single), monitor (continuous), dry-run (test)")
    parser.add_argument("--interval", type=int, default=30,
                        help="Monitoring interval in seconds (default: 30)")
    parser.add_argument("--duration", type=int, default=0,
                        help="Monitoring duration in seconds (0 = indefinite)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output directory for logs")

    args = parser.parse_args()

    if not REQUESTS_AVAILABLE:
        print("ERROR: requests library required")
        return 1

    monitor = ResonanceMonitor(output_dir=args.output)

    if args.mode == "scan":
        monitor.single_scan()
        return 0
    elif args.mode == "monitor":
        monitor.monitor_loop(interval=args.interval, duration=args.duration)
        return 0
    elif args.mode == "dry-run":
        return monitor.dry_run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
