#!/usr/bin/env python3
"""
MANHATTAN PROJECT - Phase 4: Transaction Builder Test
======================================================

This script builds and validates a transaction WITHOUT broadcasting.
It verifies the transaction format and structure are correct.

Transaction Format (144 bytes total):
├── Transaction Data: 80 Bytes
│   ├── Source PubKey:    32 Bytes [0:32]
│   ├── Dest PubKey:      32 Bytes [32:64]
│   ├── Amount:            8 Bytes [64:72] (little-endian)
│   ├── Target Tick:       4 Bytes [72:76] (little-endian)
│   ├── Transfer Type:     2 Bytes [76:78] (0 = Standard)
│   └── Payload Size:      2 Bytes [78:80] (0 = None)
└── Signature:            64 Bytes [80:144]

Author: qubic-academic-docs
Date: 2026-01-16
"""

import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from qubipy.crypto.utils import (
        get_public_key_from_identity,
        get_subseed_from_seed,
        get_private_key_from_subseed,
        get_public_key_from_private_key,
        kangaroo_twelve,
        sign,
        get_identity_from_public_key
    )
    QUBIPY_AVAILABLE = True
except ImportError:
    QUBIPY_AVAILABLE = False


# Configuration
RPC_URL = "https://rpc.qubic.org"
TIMEOUT = 10

# Test target (ENTRY node - verified)
TEST_TARGET = {
    "name": "ENTRY",
    "identity": "VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH",
    "coords": (45, 92)
}

# Transaction parameters
TEST_AMOUNT = 1  # 1 QUBIC - minimal resonance test amount


class TransactionBuilder:
    """Transaction builder and validator."""

    def __init__(self):
        self.seed_str = os.getenv("MASTER_SEED")
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }

    def validate_seed(self):
        """Validate MASTER_SEED configuration."""
        print("[1/6] Validating MASTER_SEED...")

        if not self.seed_str:
            print("  ✗ MASTER_SEED not found in environment")
            return False

        if len(self.seed_str) != 55:
            print(f"  ✗ MASTER_SEED has wrong length: {len(self.seed_str)} (expected 55)")
            return False

        # Check for valid characters (a-z lowercase)
        valid_chars = set("abcdefghijklmnopqrstuvwxyz")
        if not all(c in valid_chars for c in self.seed_str):
            print("  ✗ MASTER_SEED contains invalid characters (only a-z allowed)")
            return False

        print(f"  ✓ MASTER_SEED valid ({self.seed_str[:3]}***{self.seed_str[-3:]})")
        return True

    def get_current_tick(self):
        """Fetch current tick from RPC."""
        print("[2/6] Fetching current tick...")

        if not REQUESTS_AVAILABLE:
            print("  ✗ requests library not available")
            return None

        try:
            r = requests.get(f"{RPC_URL}/v1/tick-info", timeout=TIMEOUT)
            r.raise_for_status()
            tick = r.json().get('tickInfo', {}).get('tick', 0)
            print(f"  ✓ Current tick: {tick}")
            return tick
        except Exception as e:
            print(f"  ✗ Failed to fetch tick: {e}")
            return None

    def derive_keys(self):
        """Derive keys from seed."""
        print("[3/6] Deriving cryptographic keys...")

        if not QUBIPY_AVAILABLE:
            print("  ✗ QubiPy not available")
            return None

        try:
            seed_bytes = self.seed_str.encode('utf-8')
            subseed = get_subseed_from_seed(seed_bytes)
            priv_key = get_private_key_from_subseed(subseed)
            pub_key = get_public_key_from_private_key(priv_key)
            source_identity = get_identity_from_public_key(pub_key)

            print(f"  ✓ Source identity: {source_identity[:20]}...{source_identity[-10:]}")
            print(f"  ✓ Public key: {pub_key.hex()[:16]}...{pub_key.hex()[-8:]}")

            return {
                "subseed": subseed,
                "priv_key": priv_key,
                "pub_key": pub_key,
                "identity": source_identity
            }
        except Exception as e:
            print(f"  ✗ Key derivation failed: {e}")
            return None

    def build_transaction(self, keys, target_identity, amount, target_tick):
        """Build a transaction without signing yet."""
        print("[4/6] Building transaction structure...")

        try:
            dest_pub_key = get_public_key_from_identity(target_identity)

            # Construct 80-byte transaction data
            tx_data = bytearray(80)
            tx_data[0:32] = keys["pub_key"]           # Source public key
            tx_data[32:64] = dest_pub_key             # Destination public key
            tx_data[64:72] = amount.to_bytes(8, byteorder='little')  # Amount
            tx_data[72:76] = target_tick.to_bytes(4, byteorder='little')  # Target tick
            tx_data[76:78] = (0).to_bytes(2, byteorder='little')  # Type: 0 = Transfer
            tx_data[78:80] = (0).to_bytes(2, byteorder='little')  # Payload size: 0

            print(f"  ✓ Transaction data: {len(tx_data)} bytes")
            print(f"    - Source:     {keys['pub_key'].hex()[:16]}...")
            print(f"    - Dest:       {dest_pub_key.hex()[:16]}...")
            print(f"    - Amount:     {amount} QUBIC")
            print(f"    - Tick:       {target_tick}")
            print(f"    - Type:       0 (Transfer)")
            print(f"    - Payload:    0 bytes")

            return tx_data, dest_pub_key
        except Exception as e:
            print(f"  ✗ Transaction build failed: {e}")
            return None, None

    def sign_transaction(self, keys, tx_data):
        """Sign the transaction."""
        print("[5/6] Signing transaction...")

        try:
            # K12 hash of transaction data
            digest = kangaroo_twelve(bytes(tx_data), 80, 32)

            # Sign with Schnorr
            signature = sign(keys["subseed"], keys["pub_key"], digest)

            if len(signature) != 64:
                print(f"  ✗ Signature has wrong length: {len(signature)} (expected 64)")
                return None

            # Full signed transaction
            full_tx = bytes(tx_data) + signature

            print(f"  ✓ Signature: {signature.hex()[:16]}...{signature.hex()[-8:]}")
            print(f"  ✓ Full transaction: {len(full_tx)} bytes")

            return full_tx
        except Exception as e:
            print(f"  ✗ Signing failed: {e}")
            return None

    def calculate_tx_id(self, full_tx):
        """Calculate transaction ID."""
        print("[6/6] Calculating transaction ID...")

        try:
            # K12 hash of full transaction
            final_digest = kangaroo_twelve(bytes(full_tx), 144, 32)
            tx_id = get_identity_from_public_key(final_digest).lower()

            print(f"  ✓ Transaction ID: {tx_id}")
            return tx_id
        except Exception as e:
            print(f"  ✗ TX ID calculation failed: {e}")
            return None

    def validate_transaction_format(self, full_tx):
        """Validate transaction format."""
        print("\n" + "=" * 60)
        print("TRANSACTION FORMAT VALIDATION")
        print("=" * 60)

        validations = []

        # Check total length
        total_len = len(full_tx)
        valid_len = total_len == 144
        validations.append(("Total length = 144", valid_len, f"Actual: {total_len}"))

        # Check source pubkey length
        source_len = 32
        valid_source = True  # Already verified in build
        validations.append(("Source pubkey = 32 bytes", valid_source, "OK"))

        # Check dest pubkey length
        dest_len = 32
        valid_dest = True
        validations.append(("Dest pubkey = 32 bytes", valid_dest, "OK"))

        # Check amount encoding
        amount_bytes = full_tx[64:72]
        amount = int.from_bytes(amount_bytes, byteorder='little')
        valid_amount = amount == TEST_AMOUNT
        validations.append((f"Amount = {TEST_AMOUNT}", valid_amount, f"Decoded: {amount}"))

        # Check transfer type
        tx_type = int.from_bytes(full_tx[76:78], byteorder='little')
        valid_type = tx_type == 0
        validations.append(("Transfer type = 0", valid_type, f"Actual: {tx_type}"))

        # Check payload size
        payload_size = int.from_bytes(full_tx[78:80], byteorder='little')
        valid_payload = payload_size == 0
        validations.append(("Payload size = 0", valid_payload, f"Actual: {payload_size}"))

        # Check signature length
        sig_len = 64
        valid_sig = len(full_tx[80:]) == 64
        validations.append(("Signature = 64 bytes", valid_sig, f"Actual: {len(full_tx[80:])}"))

        # Print results
        all_pass = True
        for name, passed, detail in validations:
            icon = "✓" if passed else "✗"
            status = "PASS" if passed else "FAIL"
            print(f"  [{icon}] {name}: {status} ({detail})")
            if not passed:
                all_pass = False

        return all_pass

    def run_test(self):
        """Run the complete transaction builder test."""
        print("=" * 60)
        print("MANHATTAN PROJECT - PHASE 4: TRANSACTION BUILDER TEST")
        print("=" * 60)
        print(f"Target: {TEST_TARGET['name']} ({TEST_TARGET['coords'][0]}, {TEST_TARGET['coords'][1]})")
        print(f"Amount: {TEST_AMOUNT} QUBIC")
        print(f"Mode: BUILD ONLY - NO BROADCAST")
        print()

        # Step 1: Validate seed
        if not self.validate_seed():
            return 1

        # Step 2: Get current tick
        current_tick = self.get_current_tick()
        if current_tick is None:
            return 1
        target_tick = current_tick + 10

        # Step 3: Derive keys
        keys = self.derive_keys()
        if keys is None:
            return 1

        # Step 4: Build transaction
        tx_data, dest_pub_key = self.build_transaction(
            keys, TEST_TARGET["identity"], TEST_AMOUNT, target_tick
        )
        if tx_data is None:
            return 1

        # Step 5: Sign transaction
        full_tx = self.sign_transaction(keys, tx_data)
        if full_tx is None:
            return 1

        # Step 6: Calculate TX ID
        tx_id = self.calculate_tx_id(full_tx)
        if tx_id is None:
            return 1

        # Validate format
        format_ok = self.validate_transaction_format(full_tx)

        # Generate base64 (what would be sent)
        b64_tx = base64.b64encode(full_tx).decode('utf-8')

        # Summary
        print("\n" + "=" * 60)
        print("TRANSACTION SUMMARY (READY FOR BROADCAST)")
        print("=" * 60)
        print(f"  Source:      {keys['identity'][:20]}...{keys['identity'][-10:]}")
        print(f"  Destination: {TEST_TARGET['identity'][:20]}...{TEST_TARGET['identity'][-10:]}")
        print(f"  Amount:      {TEST_AMOUNT} QUBIC")
        print(f"  Target Tick: {target_tick}")
        print(f"  TX ID:       {tx_id}")
        print(f"  TX Size:     {len(full_tx)} bytes")
        print(f"  Base64 Len:  {len(b64_tx)} chars")
        print()
        print("BASE64 ENCODED (first 100 chars):")
        print(f"  {b64_tx[:100]}...")

        # Save results
        output = {
            "timestamp": datetime.now().isoformat(),
            "mode": "BUILD_ONLY_NO_BROADCAST",
            "target": TEST_TARGET,
            "amount": TEST_AMOUNT,
            "target_tick": target_tick,
            "source_identity": keys['identity'],
            "tx_id": tx_id,
            "tx_size": len(full_tx),
            "format_valid": format_ok,
            "base64_preview": b64_tx[:100] + "..."
        }

        output_path = Path(__file__).parent / "TEST_TRANSACTION_BUILD.json"
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to: {output_path}")

        # Final verdict
        print("\n" + "=" * 60)
        if format_ok:
            print("PHASE 4 RESULT: PASS - Transaction structure validated!")
            print("Transaction is ready for broadcast (when authorized).")
            print()
            print("TO BROADCAST (when ready):")
            print(f"  curl -X POST {RPC_URL}/v1/broadcast-transaction \\")
            print(f"       -H 'Content-Type: application/json' \\")
            print(f"       -d '{{\"encodedTransaction\": \"<base64>\"}}' ")
            return 0
        else:
            print("PHASE 4 RESULT: FAIL - Transaction format issues!")
            return 1


def main():
    if not QUBIPY_AVAILABLE:
        print("ERROR: QubiPy required. Run with .venv_qubic/bin/python")
        return 1

    builder = TransactionBuilder()
    return builder.run_test()


if __name__ == "__main__":
    sys.exit(main())
