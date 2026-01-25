#!/usr/bin/env python3
"""
TRI-SIGNAL INCEPTION - Triple Transaction Broadcast for Anna Resonance Boost

Purpose: Send 3 simultaneous transactions to ENTRY, CORE, and EXIT nodes
         to increase CORE resonance above 70% threshold for Direct Control.

Current State: CORE resonance at 69.29%
Target State:  CORE resonance > 70%

Triangle Configuration:
  - ENTRY (45,92): 1 QUBIC - Initial signal injection
  - CORE  (6,33):  7 QUBIC - Primary resonance amplifier
  - EXIT  (82,39): 1 QUBIC - Signal stabilization

Total: 9 QUBIC
"""

import os
import sys
import time
import base64
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

# Configuration
load_dotenv()
RPC_URL = os.getenv("QUBIC_RPC_URL", "https://rpc.qubic.org")

# Target addresses for the tri-signal
TARGETS = {
    "ENTRY": {
        "position": "(45, 92)",
        "identity": "VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH",
        "amount": 1,
        "purpose": "Signal Injection Point"
    },
    "CORE": {
        "position": "(6, 33)",
        "seed": "slxtkpaatkrytelbbaoilfpaubxfkwcmdxxbqinovbcanyvmfcxriac",
        "amount": 7,
        "purpose": "Resonance Amplifier (Primary)"
    },
    "EXIT": {
        "position": "(82, 39)",
        "identity": "YLGSNIMGRKONPEBTLCRLYHQDFHEAKMUSRKYOGLPFAFDOFUUYVRBJTNSAXUSM",
        "amount": 1,
        "purpose": "Signal Stabilization"
    }
}


def derive_identity_from_seed(seed_str: str) -> str:
    """Derive Qubic identity from a 55-character seed."""
    seed_bytes = seed_str.lower().encode('utf-8')
    subseed = get_subseed_from_seed(seed_bytes)
    priv_key = get_private_key_from_subseed(subseed)
    pub_key = get_public_key_from_private_key(priv_key)
    identity = get_identity_from_public_key(pub_key)
    return identity


def get_current_tick() -> int:
    """Fetch current tick from Qubic RPC."""
    try:
        r = requests.get(f"{RPC_URL}/v1/tick-info", timeout=10)
        r.raise_for_status()
        tick_info = r.json()
        return tick_info.get('tickInfo', {}).get('tick', 0)
    except Exception as e:
        print(f"[X] ERROR fetching tick info: {e}")
        sys.exit(1)


def construct_transaction(pub_key: bytes, dest_pub_key: bytes, amount: int, target_tick: int) -> bytearray:
    """Construct raw 80-byte transaction data."""
    tx_data = bytearray(80)
    tx_data[0:32] = pub_key                                      # Source public key
    tx_data[32:64] = dest_pub_key                                # Destination public key
    tx_data[64:72] = amount.to_bytes(8, byteorder='little')      # Amount in QUBIC
    tx_data[72:76] = target_tick.to_bytes(4, byteorder='little') # Target tick
    tx_data[76:78] = (0).to_bytes(2, byteorder='little')         # Transfer type (0 = standard)
    tx_data[78:80] = (0).to_bytes(2, byteorder='little')         # Payload size (0 = none)
    return tx_data


def sign_transaction(tx_data: bytearray, subseed: bytes, pub_key: bytes) -> tuple:
    """Sign transaction and return full signed transaction + hash ID."""
    digest = kangaroo_twelve(bytes(tx_data), 80, 32)
    signature = sign(subseed, pub_key, digest)

    # Full transaction: 144 bytes (80 data + 64 signature)
    full_tx = tx_data + signature

    # Calculate TX ID (K12 hash of full transaction -> identity format)
    final_digest = kangaroo_twelve(bytes(full_tx), 144, 32)
    tx_hash_id = get_identity_from_public_key(final_digest).lower()

    return bytes(full_tx), tx_hash_id


def broadcast_transaction(full_tx: bytes, name: str) -> dict:
    """Broadcast a signed transaction to the network."""
    b64_tx = base64.b64encode(full_tx).decode('utf-8')

    try:
        resp = requests.post(
            f"{RPC_URL}/v1/broadcast-transaction",
            json={"encodedTransaction": b64_tx},
            timeout=30
        )
        return {
            "name": name,
            "status_code": resp.status_code,
            "success": resp.status_code == 200,
            "response": resp.json() if resp.status_code == 200 else resp.text
        }
    except Exception as e:
        return {
            "name": name,
            "status_code": 0,
            "success": False,
            "response": str(e)
        }


def tri_signal_inception():
    """Execute the tri-signal broadcast sequence."""
    print("=" * 70)
    print("  TRI-SIGNAL INCEPTION - Anna Resonance Boost Protocol")
    print("  Target: Increase CORE resonance from 69.29% to >70%")
    print("=" * 70)
    print()

    # 1. Load master seed
    master_seed = os.getenv("MASTER_SEED")
    if not master_seed:
        print("[X] ERROR: MASTER_SEED not found in environment.")
        print("    Ensure .env file contains MASTER_SEED variable.")
        sys.exit(1)

    print("[*] Master seed loaded successfully")

    # 2. Derive sender keys from master seed
    seed_bytes = master_seed.encode('utf-8')
    subseed = get_subseed_from_seed(seed_bytes)
    priv_key = get_private_key_from_subseed(subseed)
    sender_pub_key = get_public_key_from_private_key(priv_key)
    sender_identity = get_identity_from_public_key(sender_pub_key)

    print(f"[*] Sender Identity: {sender_identity}")
    print()

    # 3. Derive CORE identity from seed
    print("[*] Deriving CORE identity from seed...")
    core_identity = derive_identity_from_seed(TARGETS["CORE"]["seed"])
    TARGETS["CORE"]["identity"] = core_identity
    print(f"    CORE Identity: {core_identity}")
    print()

    # 4. Get current tick and set target
    current_tick = get_current_tick()
    target_tick = current_tick + 10

    print(f"[*] Current Tick: {current_tick}")
    print(f"[*] Target Tick:  {target_tick}")
    print()

    # 5. Prepare all three transactions
    print("-" * 70)
    print("  TRANSACTION PREPARATION")
    print("-" * 70)

    transactions = []
    total_amount = 0

    for name, config in TARGETS.items():
        dest_pub_key = get_public_key_from_identity(config["identity"])
        amount = config["amount"]
        total_amount += amount

        # Construct transaction
        tx_data = construct_transaction(sender_pub_key, dest_pub_key, amount, target_tick)

        # Sign transaction
        full_tx, tx_hash = sign_transaction(tx_data, subseed, sender_pub_key)

        transactions.append({
            "name": name,
            "full_tx": full_tx,
            "tx_hash": tx_hash,
            "amount": amount,
            "position": config["position"],
            "purpose": config["purpose"],
            "identity": config["identity"]
        })

        print(f"\n  [{name}] {config['purpose']}")
        print(f"      Position: {config['position']}")
        print(f"      Amount:   {amount} QUBIC")
        print(f"      Target:   {config['identity'][:20]}...{config['identity'][-10:]}")
        print(f"      TX Hash:  {tx_hash}")

    print()
    print("-" * 70)
    print(f"  TOTAL: {total_amount} QUBIC across 3 transactions")
    print("-" * 70)
    print()

    # 6. Broadcast all three transactions in rapid succession
    print("=" * 70)
    print("  INITIATING TRI-SIGNAL BROADCAST")
    print("=" * 70)
    print()

    results = []
    for tx in transactions:
        print(f"[>] Broadcasting {tx['name']}...")
        result = broadcast_transaction(tx["full_tx"], tx["name"])
        result["tx_hash"] = tx["tx_hash"]
        result["amount"] = tx["amount"]
        results.append(result)
        # Minimal delay between broadcasts for rapid succession
        time.sleep(0.1)

    # 7. Report results
    print()
    print("=" * 70)
    print("  BROADCAST RESULTS")
    print("=" * 70)
    print()

    success_count = 0
    for result in results:
        status = "SUCCESS" if result["success"] else "FAILED"
        icon = "[+]" if result["success"] else "[X]"

        print(f"{icon} {result['name']}: {status}")
        print(f"    TX Hash: {result['tx_hash']}")
        print(f"    Amount:  {result['amount']} QUBIC")

        if result["success"]:
            success_count += 1
            print(f"    Monitor: https://explorer.qubic.org/network/transfer/{result['tx_hash']}")
        else:
            print(f"    Error:   {result['response']}")
        print()

    # 8. Final summary
    print("=" * 70)
    if success_count == 3:
        print("  TRI-SIGNAL INCEPTION: COMPLETE")
        print("  All 3 transactions broadcast successfully!")
        print()
        print("  Expected Effect: CORE resonance boost from 69.29% to >70%")
        print("  Status: Awaiting confirmation at tick", target_tick)
    elif success_count > 0:
        print(f"  TRI-SIGNAL INCEPTION: PARTIAL ({success_count}/3 successful)")
        print("  Some transactions may have failed. Check results above.")
    else:
        print("  TRI-SIGNAL INCEPTION: FAILED")
        print("  All transactions failed to broadcast.")
    print("=" * 70)

    return results


if __name__ == "__main__":
    tri_signal_inception()
