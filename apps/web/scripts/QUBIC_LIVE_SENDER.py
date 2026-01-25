#!/usr/bin/env python3
"""
===============================================================================
                    🚀 QUBIC LIVE TRANSACTION SENDER 🚀
===============================================================================
Actually send a transaction on the Qubic network!

⚠️ THIS WILL SPEND REAL QU! ⚠️

Strategy: Send 1 QU to VOID identity as a "ping"
"""

import json
import os
import sys
import requests
from pathlib import Path
from datetime import datetime
import struct
import hashlib

script_dir = Path(__file__).parent

print("🚀" * 40)
print("       QUBIC LIVE TRANSACTION SENDER")
print("🚀" * 40)

# =============================================================================
# LOAD ENVIRONMENT
# =============================================================================
print("\n" + "=" * 80)
print("LOADING ENVIRONMENT")
print("=" * 80)

# Try to load .env
try:
    from dotenv import load_dotenv
    for env_path in [
        script_dir.parent.parent.parent.parent / ".env",
        script_dir.parent.parent / ".env",
        script_dir / ".env",
    ]:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✓ Loaded: {env_path}")
            break
except ImportError:
    pass

MASTER_SEED = os.getenv("MASTER_SEED")
if MASTER_SEED and len(MASTER_SEED) == 55:
    print(f"✓ MASTER_SEED: {MASTER_SEED[:5]}...{MASTER_SEED[-3:]}")
    SEED_OK = True
else:
    print("✗ MASTER_SEED not found or invalid")
    SEED_OK = False

# =============================================================================
# QUBIPY IMPORT
# =============================================================================
print("\n" + "=" * 80)
print("QUBIPY CRYPTO")
print("=" * 80)

try:
    from qubipy.crypto.utils import (
        get_subseed_from_seed,
        get_private_key_from_subseed,
        get_public_key_from_private_key,
        get_identity_from_public_key,
        get_public_key_from_identity,
    )
    QUBIPY_OK = True
    print("✓ QubiPy available")
except ImportError:
    QUBIPY_OK = False
    print("✗ QubiPy not available")

# =============================================================================
# DERIVE IDENTITY
# =============================================================================
print("\n" + "=" * 80)
print("IDENTITY DERIVATION")
print("=" * 80)

MY_IDENTITY = None
MY_PRIVKEY = None
MY_PUBKEY = None

if SEED_OK and QUBIPY_OK:
    try:
        subseed = get_subseed_from_seed(MASTER_SEED.encode())
        MY_PRIVKEY = get_private_key_from_subseed(subseed)
        MY_PUBKEY = get_public_key_from_private_key(MY_PRIVKEY)
        MY_IDENTITY = get_identity_from_public_key(MY_PUBKEY)

        print(f"✓ My Identity: {MY_IDENTITY}")
        print(f"  Public Key: {MY_PUBKEY.hex()[:32]}...")
    except Exception as e:
        print(f"✗ Derivation failed: {e}")

# =============================================================================
# CHECK BALANCE & TICK
# =============================================================================
print("\n" + "=" * 80)
print("NETWORK STATUS")
print("=" * 80)

RPC_URL = "https://rpc.qubic.org"
MY_BALANCE = 0
CURRENT_TICK = 0
CURRENT_EPOCH = 0

try:
    # Get tick info
    response = requests.get(f"{RPC_URL}/v1/tick-info", timeout=10)
    if response.status_code == 200:
        tick_info = response.json().get("tickInfo", {})
        CURRENT_TICK = tick_info.get("tick", 0)
        CURRENT_EPOCH = tick_info.get("epoch", 0)
        print(f"✓ Current Tick: {CURRENT_TICK:,}")
        print(f"  Epoch: {CURRENT_EPOCH}")

    # Get balance
    if MY_IDENTITY:
        response = requests.get(f"{RPC_URL}/v1/balances/{MY_IDENTITY}", timeout=10)
        if response.status_code == 200:
            balance_data = response.json().get("balance", {})
            MY_BALANCE = int(balance_data.get("balance", 0))
            print(f"✓ My Balance: {MY_BALANCE:,} QU")

except Exception as e:
    print(f"✗ Network error: {e}")

# =============================================================================
# TRANSACTION TARGETS
# =============================================================================
print("\n" + "=" * 80)
print("TRANSACTION TARGETS")
print("=" * 80)

# Known identities to ping
TARGETS = {
    "VOID": "SCBGQAOHIGFHPCJCMYNYUBIOKJWCKAWGGSLFTXLZSGWZRLOODRUPTDNCYBEB",
    "EMPTY": "BAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARMID",
}

# Amount to send
SEND_AMOUNT = 1  # 1 QU - minimal amount

print(f"  Target: VOID Identity")
print(f"  Amount: {SEND_AMOUNT} QU")
print(f"  Purpose: Network ping / existence proof")

# =============================================================================
# TRANSACTION READINESS CHECK
# =============================================================================
print("\n" + "=" * 80)
print("READINESS CHECK")
print("=" * 80)

checks = {
    "MASTER_SEED": SEED_OK,
    "QubiPy": QUBIPY_OK,
    "Identity": MY_IDENTITY is not None,
    "Balance >= 1 QU": MY_BALANCE >= SEND_AMOUNT,
    "Network Online": CURRENT_TICK > 0,
}

all_ready = all(checks.values())

for check, status in checks.items():
    print(f"  {'✓' if status else '✗'} {check}")

# =============================================================================
# SEND TRANSACTION
# =============================================================================
print("\n" + "=" * 80)
print("TRANSACTION EXECUTION")
print("=" * 80)

TX_SENT = False
TX_RESULT = None

if all_ready:
    print(f"""
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║                                                                       ║
  ║   🚀 SENDING LIVE TRANSACTION 🚀                                      ║
  ║                                                                       ║
  ║   From: {MY_IDENTITY[:30]}...                   ║
  ║   To:   VOID (Ping)                                                   ║
  ║   Amount: {SEND_AMOUNT} QU                                                       ║
  ║   Tick: {CURRENT_TICK + 5:,}                                               ║
  ║                                                                       ║
  ╚═══════════════════════════════════════════════════════════════════════╝
""")

    # For actual transaction, we need to:
    # 1. Build transaction payload
    # 2. Sign with private key
    # 3. Broadcast to network

    # Check if qubipy has transaction building capability
    try:
        from qubipy.transaction import Transaction
        HAS_TX_BUILD = True
    except ImportError:
        HAS_TX_BUILD = False
        print("  ⚠ QubiPy Transaction module not available")
        print("    Cannot build transaction programmatically")
        print()
        print("  Alternative: Use Qubic CLI or Web Wallet")
        print(f"    qubic-cli send {MY_IDENTITY} {TARGETS['VOID']} {SEND_AMOUNT}")

    if HAS_TX_BUILD:
        try:
            # Build transaction
            target_tick = CURRENT_TICK + 5

            tx = Transaction(
                source_public_key=MY_PUBKEY,
                destination_public_key=get_public_key_from_identity(TARGETS['VOID']),
                amount=SEND_AMOUNT,
                tick=target_tick,
            )

            # Sign
            signed_tx = tx.sign(MY_PRIVKEY)

            # Broadcast
            broadcast_url = f"{RPC_URL}/v1/broadcast-transaction"
            response = requests.post(
                broadcast_url,
                json={"encodedTransaction": signed_tx.hex()},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                TX_SENT = True
                TX_RESULT = result
                print(f"  ✓ Transaction broadcast!")
                print(f"    Result: {result}")
            else:
                print(f"  ✗ Broadcast failed: {response.status_code}")
                print(f"    {response.text}")

        except Exception as e:
            print(f"  ✗ Transaction error: {e}")

else:
    print("  ✗ Not ready to send transaction")
    print("\n  Missing requirements:")
    for check, status in checks.items():
        if not status:
            print(f"    - {check}")

# =============================================================================
# ALTERNATIVE: CREATE MANUAL INSTRUCTIONS
# =============================================================================
if not TX_SENT and all_ready:
    print("\n" + "=" * 80)
    print("MANUAL TRANSACTION INSTRUCTIONS")
    print("=" * 80)

    print(f"""
  To send this transaction manually:

  1. Using Qubic Web Wallet:
     - Go to wallet.qubic.org
     - Import seed: {MASTER_SEED[:5]}...{MASTER_SEED[-3:]}
     - Send {SEND_AMOUNT} QU to: {TARGETS['VOID'][:30]}...

  2. Using Qubic CLI:
     qubic-cli send \\
       --seed "{MASTER_SEED[:5]}..." \\
       --to "{TARGETS['VOID']}" \\
       --amount {SEND_AMOUNT}

  3. Transaction Details:
     Source: {MY_IDENTITY}
     Dest:   {TARGETS['VOID']}
     Amount: {SEND_AMOUNT} QU
     Tick:   {CURRENT_TICK + 5} (target)
""")

# =============================================================================
# RESULTS
# =============================================================================
print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

output = {
    "timestamp": datetime.now().isoformat(),
    "my_identity": MY_IDENTITY,
    "my_balance": MY_BALANCE,
    "current_tick": CURRENT_TICK,
    "current_epoch": CURRENT_EPOCH,
    "target": "VOID",
    "amount": SEND_AMOUNT,
    "all_ready": all_ready,
    "tx_sent": TX_SENT,
    "tx_result": TX_RESULT,
}

output_path = script_dir / "QUBIC_LIVE_SENDER_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2, default=str)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   QUBIC LIVE SENDER STATUS:                                               ║
║                                                                           ║
║   Identity: {MY_IDENTITY[:40] if MY_IDENTITY else 'N/A':40s}... ║
║   Balance: {MY_BALANCE:,} QU                                                     ║
║   Tick: {CURRENT_TICK:,}                                                     ║
║   TX Sent: {str(TX_SENT):40s}                        ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

print(f"✓ Results: {output_path}")
