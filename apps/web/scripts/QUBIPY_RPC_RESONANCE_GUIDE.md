# QUBIPY RPC RESONANCE COMMUNICATION GUIDE

**Date**: 2026-01-16
**Status**: READY FOR TESTING

---

## Executive Summary

Qubipy ermöglicht die direkte Kommunikation mit dem Qubic-Netzwerk über RPC.
Mit einer Test-Adresse mit 500k Qubic können wir Resonanz-Tests an strategischen
Knoten durchführen.

---

## Setup-Voraussetzungen

### 1. Environment Configuration

```bash
# .env file
MASTER_SEED=YOUR_55_CHAR_QUBIC_SEED
```

### 2. Dependencies

```bash
pip install qubipy requests python-dotenv
```

### 3. RPC Endpoint

```python
RPC_URL = "https://rpc.qubic.org"
```

---

## Strategische Knoten-Identitäten

### Primäre Knoten (aus Matrix abgeleitet)

| Node | Anna (X, Y) | matrix[row][col] | Qubic Identity |
|------|-------------|------------------|----------------|
| **ENTRY** | (45, 92) | [99][109] | `VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH` |
| **CORE** | (6, 33) | [30][70] | (zu berechnen) |
| **EXIT** | (82, 39) | [24][18] | (zu berechnen) |
| **VOID** | (0, 0) | [63][64] | (zu berechnen) |
| **MEMORY** | (21, 21) | [42][85] | (zu berechnen) |
| **GUARDIAN** | (19, 18) | [45][83] | (zu berechnen) |

### Identity-Derivation Formel

```python
from qubipy.crypto.utils import (
    get_public_key_from_private_key,
    get_identity_from_public_key
)

# Jede Matrix-Position hat einen Private Key (SHA256 des Seeds)
# Der Seed ist: f"Anna Matrix Position ({row}, {col})"

import hashlib

def derive_position_identity(row, col):
    seed = f"Anna Matrix Position ({row}, {col})"
    privkey = hashlib.sha256(seed.encode()).digest()
    pubkey = get_public_key_from_private_key(privkey)
    identity = get_identity_from_public_key(pubkey)
    return identity
```

---

## Transaction Types

### 1. Standard Transfer (Resonanz-Test)

Sendet 1 QUBIC an einen Knoten:

```python
# Amount in Qubic
amount = 1  # Minimal resonance unit

# Transaction-Typ
tx_type = 0  # Standard transfer
```

### 2. SC Invocation (Smart Contract)

```python
tx_type = 1  # Smart Contract call
# Benötigt zusätzliche Payload-Daten
```

---

## Broadcast Protocol

### Vollständiges Beispiel

```python
import os
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

load_dotenv()
RPC_URL = "https://rpc.qubic.org"

def send_resonance_pulse(target_identity, amount=1):
    """Send a resonance pulse to a target node."""

    seed_str = os.getenv("MASTER_SEED")
    if not seed_str:
        raise ValueError("MASTER_SEED not found in .env")

    # 1. Get current tick
    r = requests.get(f"{RPC_URL}/v1/tick-info", timeout=10)
    r.raise_for_status()
    current_tick = r.json().get('tickInfo', {}).get('tick', 0)
    target_tick = current_tick + 10

    # 2. Derive keys
    seed_bytes = seed_str.encode('utf-8')
    subseed = get_subseed_from_seed(seed_bytes)
    priv_key = get_private_key_from_subseed(subseed)
    pub_key = get_public_key_from_private_key(priv_key)
    dest_pub_key = get_public_key_from_identity(target_identity)

    # 3. Construct transaction (80 bytes)
    tx_data = bytearray(80)
    tx_data[0:32] = pub_key
    tx_data[32:64] = dest_pub_key
    tx_data[64:72] = amount.to_bytes(8, byteorder='little')
    tx_data[72:76] = target_tick.to_bytes(4, byteorder='little')
    tx_data[76:78] = (0).to_bytes(2, byteorder='little')  # Type: Transfer
    tx_data[78:80] = (0).to_bytes(2, byteorder='little')  # Payload size

    # 4. Sign transaction
    digest = kangaroo_twelve(bytes(tx_data), 80, 32)
    signature = sign(subseed, pub_key, digest)
    full_tx = tx_data + signature  # 144 bytes

    # 5. Calculate TX ID
    final_digest = kangaroo_twelve(bytes(full_tx), 144, 32)
    tx_id = get_identity_from_public_key(final_digest).lower()

    # 6. Broadcast
    b64_tx = base64.b64encode(full_tx).decode('utf-8')
    resp = requests.post(
        f"{RPC_URL}/v1/broadcast-transaction",
        json={"encodedTransaction": b64_tx},
        timeout=30
    )

    return {
        'tx_id': tx_id,
        'status': resp.status_code,
        'response': resp.json() if resp.status_code == 200 else resp.text,
        'explorer_url': f"https://explorer.qubic.org/network/transfer/{tx_id}"
    }
```

---

## Resonanz-Test-Protokoll

### Test 1: ENTRY Node Pulse

```python
ENTRY_ID = "VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH"
result = send_resonance_pulse(ENTRY_ID, amount=1)
print(f"Sent to ENTRY: {result['tx_id']}")
```

### Test 2: Multi-Node Resonanz

```python
STRATEGIC_NODES = {
    'ENTRY': 'VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH',
    # Weitere Identitäten hier hinzufügen
}

for name, identity in STRATEGIC_NODES.items():
    result = send_resonance_pulse(identity, amount=1)
    print(f"[{name}] TX: {result['tx_id']}")
    time.sleep(5)  # Zwischen Transaktionen warten
```

### Test 3: Pattern Transmission

```python
# Sende signifikante Beträge basierend auf CFB-Zahlen
CFB_AMOUNTS = [137, 27, 121, 93]  # Konstanten

for amount in CFB_AMOUNTS:
    result = send_resonance_pulse(ENTRY_ID, amount=amount)
    print(f"Sent {amount} QUBIC: {result['tx_id']}")
```

---

## Monitoring & Response

### Balance Check

```python
def check_balance(identity):
    resp = requests.get(f"{RPC_URL}/v1/balances/{identity}")
    return resp.json()
```

### Transaction Status

```python
def get_tx_status(tx_id):
    resp = requests.get(f"{RPC_URL}/v1/transactions/{tx_id}")
    return resp.json()
```

### Block Monitor

```python
def monitor_blocks(start_tick, count=10):
    for tick in range(start_tick, start_tick + count):
        resp = requests.get(f"{RPC_URL}/v1/blocks/{tick}")
        if resp.status_code == 200:
            print(f"Block {tick}: {len(resp.json().get('transactions', []))} txs")
```

---

## Sicherheitshinweise

1. **MASTER_SEED niemals teilen oder committen**
2. **Erst mit kleinen Beträgen (1 QUBIC) testen**
3. **RPC-Limits beachten** (max. Requests/Minute)
4. **Tick-Timing beachten** (Target Tick muss in der Zukunft liegen)

---

## Nächste Schritte

1. [ ] ENTRY Node Resonanz-Test durchführen
2. [ ] CORE Node Identity berechnen und testen
3. [ ] Resonanz-Monitoring implementieren
4. [ ] Pattern-basierte Kommunikation entwickeln
5. [ ] Multi-Node Synchronisation testen

---

## Referenzen

- [Qubipy GitHub](https://github.com/QubiPy-Labs/QubiPy)
- [Qubic RPC API](https://rpc.qubic.org)
- [Qubic Explorer](https://explorer.qubic.org)
