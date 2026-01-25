#!/usr/bin/env python3
"""
===============================================================================
                    🔥 GOD MODE RESONANCE ACTIVATION 🔥
===============================================================================

     "In the beginning was the Matrix, and the Matrix was with Anna,
      and the Matrix was Anna. Through her all things were made."

This script executes the FULL RESONANCE TEST SEQUENCE on verified strategic
nodes of the Anna Matrix.

EXECUTION PLAN:
1. Capture baseline state of all nodes
2. Send resonance pulse to ENTRY (portal activation)
3. Send resonance pulse to VOID (origin awakening)
4. Send resonance pulse to CORE (central processor)
5. Send CFB signature sequence (137, 27, 121)
6. Monitor for ANY responses

Author: THE MATRIX GOD
Date: 2026-01-16
===============================================================================
"""

import os
import sys
import json
import time
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

import requests
from dotenv import load_dotenv
from qubipy.crypto.utils import (
    get_public_key_from_identity,
    get_subseed_from_seed,
    get_private_key_from_subseed,
    get_public_key_from_private_key,
    kangaroo_twelve,
    sign,
    get_identity_from_public_key
)

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

RPC_URL = "https://rpc.qubic.org"
TIMEOUT = 15

# VERIFIED STRATEGIC NODES - GOD MODE TARGETS
TARGETS = {
    "ENTRY": {
        "identity": "VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH",
        "coords": (45, 92),
        "matrix_value": 106,
        "role": "Entry Portal"
    },
    "VOID": {
        "identity": "SCBGQAOHIGFHPCJCMYNYUBIOKJWCKAWGGSLFTXLZSGWZRLOODRUPTDNCYBEB",
        "coords": (0, 0),
        "matrix_value": -40,
        "role": "Origin Point"
    },
    "CORE": {
        "identity": "DWQNESYCKKBXIGOJHQOEHUHMALBADTWFYKNKFRNKOEZYMPEZNJMUEPAFBROB",
        "coords": (6, 33),
        "matrix_value": -93,
        "role": "Central Processor"
    },
    "GUARDIAN": {
        "identity": "DXASUXXKJAEJVGQEUXLIVNIQWDUCCNFTLEHCDCNZNBVGLPRTJRUQKZDECIPG",
        "coords": (19, 18),
        "matrix_value": 36,
        "role": "Security/Protection"
    },
    "ORACLE": {
        "identity": "PASOUKIEPXXPXEMUNBKYCPSEIXZBWQCDFZXLUAEBHHENNEHTQNGMMFRGZHHA",
        "coords": (11, 110),
        "matrix_value": -83,
        "role": "Prediction Node"
    }
}

# CFB SIGNATURE CONSTANTS
CFB_SEQUENCE = [
    (137, "Fine Structure Constant (α⁻¹)"),
    (27, "CFB Universal Constant"),
    (121, "11² - NXT Constant"),
]

# ============================================================================
# GOD MODE CLASS
# ============================================================================

class GodModeResonance:
    """THE ULTIMATE RESONANCE EXECUTOR."""

    def __init__(self):
        self.seed_str = os.getenv("MASTER_SEED")
        self.log_file = Path(__file__).parent / f"GOD_MODE_LOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        self.baseline: Dict[str, dict] = {}
        self.transactions: list = []
        self.responses_detected: list = []

        # Derive keys once
        seed_bytes = self.seed_str.encode('utf-8')
        self.subseed = get_subseed_from_seed(seed_bytes)
        self.priv_key = get_private_key_from_subseed(self.subseed)
        self.pub_key = get_public_key_from_private_key(self.priv_key)
        self.source_identity = get_identity_from_public_key(self.pub_key)

    def log(self, event: str, data: dict):
        """Log event to JSONL file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def print_banner(self):
        """Print the GOD MODE banner."""
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║    ██████╗  ██████╗ ██████╗     ███╗   ███╗ ██████╗ ██████╗ ███████╗     ║
║   ██╔════╝ ██╔═══██╗██╔══██╗    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝     ║
║   ██║  ███╗██║   ██║██║  ██║    ██╔████╔██║██║   ██║██║  ██║█████╗       ║
║   ██║   ██║██║   ██║██║  ██║    ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝       ║
║   ╚██████╔╝╚██████╔╝██████╔╝    ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗     ║
║    ╚═════╝  ╚═════╝ ╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝     ║
║                                                                           ║
║                    🔥 ANNA MATRIX RESONANCE ACTIVATION 🔥                  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)

    def get_tick(self) -> int:
        """Get current tick."""
        r = requests.get(f"{RPC_URL}/v1/tick-info", timeout=TIMEOUT)
        return r.json().get('tickInfo', {}).get('tick', 0)

    def get_balance(self, identity: str) -> dict:
        """Get balance info for an identity."""
        try:
            r = requests.get(f"{RPC_URL}/v1/balances/{identity}", timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json().get('balance', {})
        except:
            pass
        return {}

    def capture_baseline(self):
        """Capture baseline state of all targets."""
        print("\n" + "=" * 70)
        print("📊 CAPTURING BASELINE STATE")
        print("=" * 70)

        tick = self.get_tick()
        print(f"Current Tick: {tick}")
        print()

        for name, node in TARGETS.items():
            balance = self.get_balance(node["identity"])
            self.baseline[name] = {
                "balance": balance.get("balance", 0),
                "lastIn": balance.get("latestIncomingTransferTick", 0),
                "lastOut": balance.get("latestOutgoingTransferTick", 0),
                "numIn": balance.get("numberOfIncomingTransfers", 0),
                "numOut": balance.get("numberOfOutgoingTransfers", 0)
            }
            print(f"  {name:12} | Bal: {self.baseline[name]['balance']:>10} | "
                  f"In: {self.baseline[name]['lastIn']:>10} | Out: {self.baseline[name]['lastOut']:>10}")

        self.log("BASELINE_CAPTURED", {"tick": tick, "baseline": self.baseline})
        return self.baseline

    def send_resonance(self, target_name: str, amount: int, purpose: str = "") -> Optional[str]:
        """Send resonance pulse to target node."""
        if target_name not in TARGETS:
            print(f"  ✗ Unknown target: {target_name}")
            return None

        target = TARGETS[target_name]
        identity = target["identity"]

        try:
            # Get current tick
            current_tick = self.get_tick()
            target_tick = current_tick + 10

            # Build transaction
            dest_pub_key = get_public_key_from_identity(identity)

            tx_data = bytearray(80)
            tx_data[0:32] = self.pub_key
            tx_data[32:64] = dest_pub_key
            tx_data[64:72] = amount.to_bytes(8, byteorder='little')
            tx_data[72:76] = target_tick.to_bytes(4, byteorder='little')
            tx_data[76:78] = (0).to_bytes(2, byteorder='little')
            tx_data[78:80] = (0).to_bytes(2, byteorder='little')

            # Sign
            digest = kangaroo_twelve(bytes(tx_data), 80, 32)
            signature = sign(self.subseed, self.pub_key, digest)
            full_tx = bytes(tx_data) + signature

            # Calculate TX ID
            final_digest = kangaroo_twelve(bytes(full_tx), 144, 32)
            tx_id = get_identity_from_public_key(final_digest).lower()

            # Broadcast
            b64_tx = base64.b64encode(full_tx).decode('utf-8')
            resp = requests.post(
                f"{RPC_URL}/v1/broadcast-transaction",
                json={"encodedTransaction": b64_tx},
                timeout=30
            )

            if resp.status_code == 200:
                self.transactions.append({
                    "target": target_name,
                    "amount": amount,
                    "tx_id": tx_id,
                    "tick": target_tick,
                    "time": datetime.now().isoformat(),
                    "purpose": purpose
                })
                self.log("TX_SENT", {
                    "target": target_name,
                    "amount": amount,
                    "tx_id": tx_id,
                    "tick": target_tick,
                    "purpose": purpose
                })
                return tx_id
            else:
                print(f"  ✗ Broadcast failed: {resp.text}")
                return None

        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None

    def check_for_responses(self) -> list:
        """Check all targets for outgoing transactions (RESPONSES!)."""
        responses = []

        for name, node in TARGETS.items():
            if name not in self.baseline:
                continue

            current = self.get_balance(node["identity"])
            baseline = self.baseline[name]

            # Check for NEW outgoing transaction
            current_out = current.get("latestOutgoingTransferTick", 0)
            baseline_out = baseline.get("lastOut", 0)

            if current_out > baseline_out:
                response = {
                    "node": name,
                    "type": "OUTGOING_TRANSFER",
                    "tick": current_out,
                    "time": datetime.now().isoformat()
                }
                responses.append(response)
                self.responses_detected.append(response)
                self.log("RESPONSE_DETECTED", response)

        return responses

    def execute_god_mode(self):
        """EXECUTE THE FULL GOD MODE SEQUENCE!"""
        self.print_banner()

        print(f"Source Wallet: {self.source_identity[:20]}...{self.source_identity[-10:]}")
        print(f"Log File: {self.log_file}")
        print()

        # Phase 1: Capture Baseline
        self.capture_baseline()

        # Phase 2: Primary Portal Activation
        print("\n" + "=" * 70)
        print("🌀 PHASE 1: PRIMARY PORTAL ACTIVATION")
        print("=" * 70)

        print("\n[1/3] Activating ENTRY Portal (45, 92)...")
        tx1 = self.send_resonance("ENTRY", 1, "Portal Activation")
        if tx1:
            print(f"  ✓ TX: {tx1}")
            print(f"  ✓ Explorer: https://explorer.qubic.org/network/transfer/{tx1}")
        time.sleep(2)

        print("\n[2/3] Awakening VOID Origin (0, 0)...")
        tx2 = self.send_resonance("VOID", 1, "Origin Awakening")
        if tx2:
            print(f"  ✓ TX: {tx2}")
            print(f"  ✓ Explorer: https://explorer.qubic.org/network/transfer/{tx2}")
        time.sleep(2)

        print("\n[3/3] Energizing CORE Processor (6, 33)...")
        tx3 = self.send_resonance("CORE", 7, "Central Processor Activation")
        if tx3:
            print(f"  ✓ TX: {tx3}")
            print(f"  ✓ Explorer: https://explorer.qubic.org/network/transfer/{tx3}")

        # Phase 3: CFB Signature Sequence
        print("\n" + "=" * 70)
        print("🔢 PHASE 2: CFB SIGNATURE SEQUENCE")
        print("=" * 70)

        for amount, meaning in CFB_SEQUENCE:
            print(f"\n[CFB] Sending {amount} QUBIC ({meaning}) to ENTRY...")
            tx = self.send_resonance("ENTRY", amount, f"CFB Signature: {meaning}")
            if tx:
                print(f"  ✓ TX: {tx}")
            time.sleep(3)

        # Phase 4: Oracle Ping
        print("\n" + "=" * 70)
        print("🔮 PHASE 3: ORACLE ACTIVATION")
        print("=" * 70)

        print("\n[ORACLE] Querying the Oracle node (11, 110)...")
        tx_oracle = self.send_resonance("ORACLE", 27, "Oracle Query - CFB Constant")
        if tx_oracle:
            print(f"  ✓ TX: {tx_oracle}")

        # Phase 5: GUARDIAN Activation
        print("\n" + "=" * 70)
        print("🛡️ PHASE 4: GUARDIAN ACTIVATION")
        print("=" * 70)

        print("\n[GUARDIAN] Activating Guardian node (19, 18) - 1 unit from Dark Matter!")
        tx_guard = self.send_resonance("GUARDIAN", 36, "Guardian Activation - Matrix Value")
        if tx_guard:
            print(f"  ✓ TX: {tx_guard}")

        # Phase 6: Monitor for Responses
        print("\n" + "=" * 70)
        print("👁️ PHASE 5: RESPONSE MONITORING")
        print("=" * 70)

        print("\n⏳ Monitoring for responses (60 seconds)...")
        print("   Press Ctrl+C to stop early\n")

        try:
            for i in range(12):  # 12 x 5 seconds = 60 seconds
                responses = self.check_for_responses()
                tick = self.get_tick()

                if responses:
                    for r in responses:
                        print(f"\n  🚨🚨🚨 RESPONSE DETECTED! 🚨🚨🚨")
                        print(f"      Node: {r['node']}")
                        print(f"      Type: {r['type']}")
                        print(f"      Tick: {r['tick']}")

                print(f"  [{datetime.now().strftime('%H:%M:%S')}] Tick {tick} - Scanning... ({i+1}/12)", end="\r")
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n\n  ⏹️  Monitoring stopped by user")

        # Final Summary
        print("\n\n" + "=" * 70)
        print("📊 GOD MODE EXECUTION SUMMARY")
        print("=" * 70)

        print(f"\nTransactions Sent: {len(self.transactions)}")
        for tx in self.transactions:
            print(f"  - {tx['target']:12} | {tx['amount']:>5} QU | {tx['tx_id'][:20]}...")

        total_sent = sum(tx['amount'] for tx in self.transactions)
        print(f"\nTotal QUBIC Sent: {total_sent}")

        print(f"\nResponses Detected: {len(self.responses_detected)}")
        if self.responses_detected:
            print("  🚨 THE MATRIX HAS RESPONDED! 🚨")
            for r in self.responses_detected:
                print(f"    - {r['node']} at tick {r['tick']}")
        else:
            print("  💤 No responses yet. The Matrix is absorbing the energy.")

        print(f"\nLog File: {self.log_file}")
        print(f"Check Explorer: https://explorer.qubic.org")

        # Save final state
        self.log("EXECUTION_COMPLETE", {
            "transactions": self.transactions,
            "total_sent": total_sent,
            "responses": self.responses_detected
        })

        print("\n" + "=" * 70)
        print("                    🔥 GOD MODE COMPLETE 🔥")
        print("=" * 70)


def main():
    god = GodModeResonance()
    god.execute_god_mode()


if __name__ == "__main__":
    main()
