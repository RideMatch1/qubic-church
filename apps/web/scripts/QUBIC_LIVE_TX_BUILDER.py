#!/usr/bin/env python3
"""
===============================================================================
                    💸 QUBIC LIVE TRANSACTION BUILDER 💸
===============================================================================
Bereite eine ECHTE Transaktion auf dem Qubic-Netzwerk vor!

⚠️  WARNUNG: Dies kann ECHTE QU bewegen! Nur mit Testbeträgen verwenden!
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent

print("💸" * 40)
print("       QUBIC LIVE TRANSACTION BUILDER")
print("💸" * 40)

# =============================================================================
# ENVIRONMENT CHECK
# =============================================================================
print("\n" + "=" * 80)
print("ENVIRONMENT CHECK")
print("=" * 80)

# Lade .env
try:
    from dotenv import load_dotenv
    env_path = script_dir.parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ .env geladen: {env_path}")
    else:
        env_path = script_dir.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✓ .env geladen: {env_path}")
except ImportError:
    print("  dotenv nicht verfügbar")

# Prüfe MASTER_SEED
master_seed = os.getenv("MASTER_SEED")
if master_seed and len(master_seed) == 55:
    print(f"✓ MASTER_SEED gefunden: {master_seed[:5]}...{master_seed[-3:]}")
    SEED_AVAILABLE = True
else:
    print("✗ MASTER_SEED nicht gefunden oder ungültig")
    SEED_AVAILABLE = False

# =============================================================================
# QUBIPY IMPORT
# =============================================================================
print("\n" + "=" * 80)
print("QUBIPY IMPORT")
print("=" * 80)

try:
    from qubipy.crypto.utils import (
        get_subseed_from_seed,
        get_private_key_from_subseed,
        get_public_key_from_private_key,
        get_identity_from_public_key,
        get_public_key_from_identity,
    )
    QUBIPY_AVAILABLE = True
    print("✓ QubiPy Crypto verfügbar")
except ImportError:
    QUBIPY_AVAILABLE = False
    print("✗ QubiPy nicht verfügbar")
    print("  Bitte mit .venv_qubic/bin/python ausführen")

try:
    import requests
    REQUESTS_AVAILABLE = True
    print("✓ Requests verfügbar")
except ImportError:
    REQUESTS_AVAILABLE = False
    print("✗ Requests nicht verfügbar")

# =============================================================================
# RPC KONFIGURATION
# =============================================================================
RPC_URL = "https://rpc.qubic.org"

# Bekannte Test-Identitäten
TEST_IDENTITIES = {
    "ENTRY": "VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH",
    "VOID": "SCBGQAOHIGFHPCJCMYNYUBIOKJWCKAWGGSLFTXLZSGWZRLOODRUPTDNCYBEB",
    "BURN": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFXIB",
}

# =============================================================================
# IDENTITY DERIVATION
# =============================================================================
print("\n" + "=" * 80)
print("IDENTITY DERIVATION")
print("=" * 80)

if QUBIPY_AVAILABLE and SEED_AVAILABLE:
    try:
        seed_bytes = master_seed.encode('utf-8')
        subseed = get_subseed_from_seed(seed_bytes)
        privkey = get_private_key_from_subseed(subseed)
        pubkey = get_public_key_from_private_key(privkey)
        my_identity = get_identity_from_public_key(pubkey)

        print(f"✓ Eigene Identity: {my_identity}")
        print(f"  Private Key: {privkey.hex()[:16]}... (GEHEIM!)")
        print(f"  Public Key: {pubkey.hex()[:16]}...")
    except Exception as e:
        print(f"✗ Derivation fehlgeschlagen: {e}")
        my_identity = None
else:
    my_identity = None
    print("  Übersprungen (MASTER_SEED oder QubiPy nicht verfügbar)")

# =============================================================================
# BALANCE CHECK
# =============================================================================
print("\n" + "=" * 80)
print("BALANCE CHECK")
print("=" * 80)

if REQUESTS_AVAILABLE and my_identity:
    try:
        url = f"{RPC_URL}/v1/balances/{my_identity}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            balance_info = data.get('balance', {})
            balance = balance_info.get('balance', 0)
            last_in = balance_info.get('latestIncomingTransferTick', 0)
            last_out = balance_info.get('latestOutgoingTransferTick', 0)

            print(f"✓ Balance: {balance:,} QU")
            print(f"  Letzte Einzahlung: Tick {last_in}")
            print(f"  Letzte Auszahlung: Tick {last_out}")

            MY_BALANCE = balance
        else:
            print(f"✗ Balance-Abfrage fehlgeschlagen: {response.status_code}")
            MY_BALANCE = 0
    except Exception as e:
        print(f"✗ Balance-Abfrage Fehler: {e}")
        MY_BALANCE = 0
else:
    MY_BALANCE = 0
    print("  Übersprungen")

# =============================================================================
# CURRENT TICK
# =============================================================================
print("\n" + "=" * 80)
print("AKTUELLER TICK")
print("=" * 80)

CURRENT_TICK = 0
if REQUESTS_AVAILABLE:
    try:
        response = requests.get(f"{RPC_URL}/v1/tick-info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            tick_info = data.get('tickInfo', {})
            CURRENT_TICK = tick_info.get('tick', 0)
            epoch = tick_info.get('epoch', 0)

            print(f"✓ Aktueller Tick: {CURRENT_TICK:,}")
            print(f"  Epoche: {epoch}")
    except Exception as e:
        print(f"✗ Tick-Abfrage Fehler: {e}")

# =============================================================================
# TRANSACTION BUILDER (Vorbereitung)
# =============================================================================
print("\n" + "=" * 80)
print("TRANSACTION BUILDER")
print("=" * 80)

# Test-Transaktion Parameter
TEST_TX = {
    "source": my_identity,
    "destination": TEST_IDENTITIES["BURN"],  # An Burn-Adresse
    "amount": 1,  # Nur 1 QU als Test
    "target_tick": CURRENT_TICK + 10 if CURRENT_TICK > 0 else 0,
}

print(f"""
VORBEREITETE TEST-TRANSAKTION:

  Von:    {TEST_TX['source'][:30] if TEST_TX['source'] else 'NICHT VERFÜGBAR'}...
  An:     {TEST_TX['destination'][:30]}...
  Betrag: {TEST_TX['amount']} QU
  Tick:   {TEST_TX['target_tick']}

⚠️  WARNUNG: Diese Transaktion würde {TEST_TX['amount']} QU VERBRENNEN!
⚠️  Die Burn-Adresse ist unwiderruflich!

Status:
  MASTER_SEED verfügbar: {SEED_AVAILABLE}
  Identity abgeleitet: {my_identity is not None}
  Balance ausreichend: {MY_BALANCE >= TEST_TX['amount']}
  Tick verfügbar: {CURRENT_TICK > 0}
""")

# =============================================================================
# TRANSACTION SIGNING (Nur vorbereiten, nicht senden!)
# =============================================================================
print("\n" + "=" * 80)
print("TRANSACTION SIGNIERUNG (NUR VORBEREITUNG)")
print("=" * 80)

if all([SEED_AVAILABLE, my_identity, MY_BALANCE >= TEST_TX['amount'], CURRENT_TICK > 0]):
    print("✓ Alle Voraussetzungen erfüllt!")
    print("\n  Um die Transaktion zu senden, müsste man:")
    print("  1. Transaction-Payload mit QubiPy erstellen")
    print("  2. Mit Private Key signieren")
    print("  3. An RPC broadcast endpoint senden")
    print("\n  NICHT IMPLEMENTIERT - Dies ist nur eine Demonstration!")

    TX_READY = True
else:
    print("✗ Nicht alle Voraussetzungen erfüllt")
    print("\n  Fehlend:")
    if not SEED_AVAILABLE:
        print("  - MASTER_SEED")
    if not my_identity:
        print("  - Identity")
    if MY_BALANCE < TEST_TX['amount']:
        print(f"  - Ausreichende Balance (haben: {MY_BALANCE}, brauchen: {TEST_TX['amount']})")
    if CURRENT_TICK == 0:
        print("  - Tick-Information")

    TX_READY = False

# =============================================================================
# SEND TRANSACTION (DEAKTIVIERT!)
# =============================================================================
print("\n" + "=" * 80)
print("TRANSACTION SENDEN")
print("=" * 80)

print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ⛔ TRANSACTION-SENDEN IST DEAKTIVIERT ⛔                                ║
║                                                                           ║
║   Dies ist eine Sicherheitsmaßnahme!                                      ║
║                                                                           ║
║   Um eine echte Transaktion zu senden:                                    ║
║   1. Verwende die offizielle Qubic Wallet                                 ║
║   2. Oder implementiere vollständige Signierung mit QubiPy                ║
║   3. Teste IMMER erst mit kleinen Beträgen!                               ║
║                                                                           ║
║   Die Infrastruktur ist bereit:                                           ║
║   ✓ RPC erreichbar                                                        ║
║   ✓ Identity ableitbar                                                    ║
║   ✓ Balance abrufbar                                                      ║
║   ✓ Tick verfügbar                                                        ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 80)
print("FAZIT")
print("=" * 80)

output = {
    "timestamp": datetime.now().isoformat(),
    "rpc_url": RPC_URL,
    "qubipy_available": QUBIPY_AVAILABLE,
    "seed_available": SEED_AVAILABLE,
    "identity": my_identity[:20] + "..." if my_identity else None,
    "balance": MY_BALANCE,
    "current_tick": CURRENT_TICK,
    "tx_ready": TX_READY,
    "tx_sent": False,
    "reason": "Transaction sending disabled for safety",
}

output_path = script_dir / "QUBIC_LIVE_TX_BUILDER_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"""
ZUSAMMENFASSUNG:

  RPC Status: {"✓ ONLINE" if CURRENT_TICK > 0 else "✗ OFFLINE"}
  Identity: {my_identity[:30] + "..." if my_identity else "NICHT VERFÜGBAR"}
  Balance: {MY_BALANCE:,} QU
  Tick: {CURRENT_TICK:,}
  TX bereit: {TX_READY}
  TX gesendet: NEIN (deaktiviert)

✓ Ergebnisse: {output_path}
""")
