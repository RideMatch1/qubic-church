#!/usr/bin/env python3
"""
RESONANCE MONITOR
=================
Continuously monitors resonance at strategic matrix nodes until CORE reaches >70%.

Strategic Nodes:
- ENTRY (45,92)  - Entry point for signals
- CORE (6,33)   - Central processing node (target: >70%)
- EXIT (82,39)  - Output gateway
- MEMORY (21,21) - State storage

Author: Resonance Analysis System
"""

import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
BTC_API_URL = "https://blockstream.info/api"
MATRIX_DATA_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
LOG_FILE_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/resonance_log.json")

# Monitoring parameters
CHECK_INTERVAL_SECONDS = 30
MAX_RUNTIME_MINUTES = 30
CORE_THRESHOLD = 70.0

# Strategic nodes to monitor
STRATEGIC_NODES = {
    "ENTRY": (45, 92),
    "CORE": (6, 33),
    "EXIT": (82, 39),
    "MEMORY": (21, 21)
}


class ResonanceMonitor:
    """Continuous resonance monitoring system for strategic matrix nodes."""

    def __init__(self):
        self.matrix_cache = None
        self.measurements = []
        self.start_time = None
        self.core_threshold_reached = False

    def load_matrix(self):
        """Load matrix data from file (cached after first load)."""
        if self.matrix_cache is None:
            try:
                with open(MATRIX_DATA_PATH, "r") as f:
                    self.matrix_cache = json.load(f)
                print(f"[+] Matrix loaded: {len(self.matrix_cache)} coordinates")
            except Exception as e:
                print(f"[!] Failed to load matrix: {e}")
                return False
        return True

    def get_latest_btc_hash(self):
        """Fetch the latest Bitcoin block hash."""
        try:
            response = requests.get(f"{BTC_API_URL}/blocks/tip/hash", timeout=10)
            if response.status_code == 200:
                return response.text.strip()
        except requests.RequestException as e:
            print(f"[!] BTC API Error: {e}")
        return None

    def get_btc_block_height(self):
        """Fetch current Bitcoin block height."""
        try:
            response = requests.get(f"{BTC_API_URL}/blocks/tip/height", timeout=10)
            if response.status_code == 200:
                return int(response.text.strip())
        except requests.RequestException as e:
            print(f"[!] BTC Height API Error: {e}")
        return None

    def compute_resonance(self, btc_hash, coord):
        """
        Calculate resonance score between Bitcoin entropy and matrix coordinate.

        Formula: Resonance = normalized XOR distance between BTC hash bytes and matrix weight
        """
        coord_key = f"{coord[0]},{coord[1]}"
        matrix_hex = self.matrix_cache.get(coord_key, "")

        if not matrix_hex:
            return 0.0

        # Extract weight from first byte of matrix value
        weight = int(matrix_hex[:2], 16)

        # Convert BTC hash to bytes
        btc_bytes = bytes.fromhex(btc_hash)

        # Calculate XOR-based distance
        diff = sum(abs(b - weight) for b in btc_bytes)

        # Normalize: lower difference = higher resonance
        max_diff = 255 * len(btc_bytes)
        score = (1 - (diff / max_diff)) * 100

        return round(score, 2)

    def measure_all_nodes(self, btc_hash, block_height):
        """Measure resonance at all strategic nodes."""
        timestamp = datetime.now().isoformat()

        measurements = {
            "timestamp": timestamp,
            "btc_hash": btc_hash,
            "btc_block_height": block_height,
            "nodes": {}
        }

        for name, coord in STRATEGIC_NODES.items():
            score = self.compute_resonance(btc_hash, coord)
            measurements["nodes"][name] = {
                "coord": coord,
                "resonance": score,
                "status": self._get_status(name, score)
            }

        return measurements

    def _get_status(self, node_name, score):
        """Determine status based on node type and resonance score."""
        if node_name == "CORE":
            if score > CORE_THRESHOLD:
                return "CRITICAL_THRESHOLD_REACHED"
            elif score > 60:
                return "APPROACHING"
            elif score > 45:
                return "ACTIVE"
            else:
                return "DORMANT"
        else:
            if score > 60:
                return "HIGH"
            elif score > 45:
                return "ACTIVE"
            else:
                return "DORMANT"

    def display_measurement(self, measurement):
        """Display current measurement to console."""
        print("\n" + "=" * 70)
        print(f"  RESONANCE MEASUREMENT - {measurement['timestamp']}")
        print(f"  BTC Block: {measurement['btc_block_height']} | Hash: {measurement['btc_hash'][:16]}...")
        print("=" * 70)

        for name in ["ENTRY", "CORE", "EXIT", "MEMORY"]:
            node = measurement["nodes"][name]
            coord_str = f"({node['coord'][0]:3},{node['coord'][1]:3})"
            score = node["resonance"]
            status = node["status"]

            # Visual bar
            bar_len = int(score / 2)
            bar = "#" * bar_len + "-" * (50 - bar_len)

            # Highlight CORE specially
            if name == "CORE":
                threshold_marker = "|" if score < CORE_THRESHOLD else ">"
                print(f"\n  >>> {name:6} {coord_str} [{bar}] {score:6.2f}% {status}")
                print(f"      Target: {CORE_THRESHOLD}% {threshold_marker} Current: {score:.2f}%")
            else:
                print(f"      {name:6} {coord_str} [{bar}] {score:6.2f}% {status}")

        # Check CORE threshold
        core_score = measurement["nodes"]["CORE"]["resonance"]
        if core_score > CORE_THRESHOLD:
            print("\n" + "*" * 70)
            print("  *** ALERT: CORE THRESHOLD EXCEEDED! ***")
            print(f"  *** CORE resonance at {core_score:.2f}% (target: >{CORE_THRESHOLD}%) ***")
            print("*" * 70)
            self.core_threshold_reached = True

    def save_log(self):
        """Save all measurements to log file."""
        log_data = {
            "monitor_session": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": datetime.now().isoformat(),
                "total_measurements": len(self.measurements),
                "core_threshold": CORE_THRESHOLD,
                "core_threshold_reached": self.core_threshold_reached
            },
            "measurements": self.measurements
        }

        try:
            with open(LOG_FILE_PATH, "w") as f:
                json.dump(log_data, f, indent=2)
            print(f"\n[+] Log saved to: {LOG_FILE_PATH}")
        except Exception as e:
            print(f"[!] Failed to save log: {e}")

    def run(self):
        """Main monitoring loop."""
        print("\n" + "=" * 70)
        print("  RESONANCE MONITOR - STRATEGIC NODE SURVEILLANCE")
        print("=" * 70)
        print(f"  Monitoring interval: {CHECK_INTERVAL_SECONDS} seconds")
        print(f"  Max runtime: {MAX_RUNTIME_MINUTES} minutes")
        print(f"  CORE target threshold: >{CORE_THRESHOLD}%")
        print(f"  Log file: {LOG_FILE_PATH}")
        print("=" * 70)

        # Load matrix data
        if not self.load_matrix():
            print("[!] ABORT: Cannot load matrix data")
            return

        # Verify strategic nodes exist in matrix
        print("\n[*] Verifying strategic nodes...")
        for name, coord in STRATEGIC_NODES.items():
            coord_key = f"{coord[0]},{coord[1]}"
            if coord_key in self.matrix_cache:
                print(f"    [{name}] ({coord[0]},{coord[1]}) - FOUND")
            else:
                print(f"    [{name}] ({coord[0]},{coord[1]}) - NOT FOUND (will return 0%)")

        self.start_time = datetime.now()
        end_time = self.start_time + timedelta(minutes=MAX_RUNTIME_MINUTES)
        measurement_count = 0

        print(f"\n[*] Starting monitoring at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[*] Will run until CORE >{CORE_THRESHOLD}% or {end_time.strftime('%H:%M:%S')}")
        print("\nPress Ctrl+C to stop early...\n")

        try:
            while datetime.now() < end_time and not self.core_threshold_reached:
                measurement_count += 1

                # Get current Bitcoin state
                btc_hash = self.get_latest_btc_hash()
                block_height = self.get_btc_block_height()

                if not btc_hash:
                    print(f"[!] Measurement #{measurement_count}: Failed to get BTC data, retrying...")
                    time.sleep(CHECK_INTERVAL_SECONDS)
                    continue

                # Take measurement
                measurement = self.measure_all_nodes(btc_hash, block_height)
                self.measurements.append(measurement)

                # Display results
                print(f"\n[Measurement #{measurement_count}]", end="")
                self.display_measurement(measurement)

                # Check if we should stop
                if self.core_threshold_reached:
                    print("\n[+] CORE threshold reached! Stopping monitor.")
                    break

                # Calculate time remaining
                remaining = end_time - datetime.now()
                remaining_mins = remaining.total_seconds() / 60
                print(f"\n  Next check in {CHECK_INTERVAL_SECONDS}s | Time remaining: {remaining_mins:.1f} minutes")

                # Wait for next interval
                time.sleep(CHECK_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\n\n[!] Monitor interrupted by user")

        # Final summary
        print("\n" + "=" * 70)
        print("  MONITORING SESSION COMPLETE")
        print("=" * 70)
        print(f"  Duration: {(datetime.now() - self.start_time).total_seconds() / 60:.1f} minutes")
        print(f"  Total measurements: {len(self.measurements)}")
        print(f"  CORE threshold reached: {'YES' if self.core_threshold_reached else 'NO'}")

        if self.measurements:
            # Calculate averages
            avg_core = sum(m["nodes"]["CORE"]["resonance"] for m in self.measurements) / len(self.measurements)
            max_core = max(m["nodes"]["CORE"]["resonance"] for m in self.measurements)
            min_core = min(m["nodes"]["CORE"]["resonance"] for m in self.measurements)

            print(f"\n  CORE Statistics:")
            print(f"    Average: {avg_core:.2f}%")
            print(f"    Maximum: {max_core:.2f}%")
            print(f"    Minimum: {min_core:.2f}%")

        # Save log
        self.save_log()
        print("\n[*] Monitor shutdown complete.")


def main():
    """Entry point."""
    monitor = ResonanceMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
