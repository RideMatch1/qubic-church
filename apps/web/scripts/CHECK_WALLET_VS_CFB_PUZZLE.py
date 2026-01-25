#!/usr/bin/env python3
"""
Prüfe ob die Test-Wallet (MASTER_SEED) einer der 20 CFB-Puzzle IDs entspricht.
"""

import json
import os
import requests
from dotenv import load_dotenv

# QubiPy für Identity-Ableitung
from qubipy.crypto.utils import (
    get_subseed_from_seed,
    get_private_key_from_subseed,
    get_public_key_from_private_key,
    get_identity_from_public_key
)

# Lade .env
load_dotenv('/Users/lukashertle/Developer/projects/qubic-academic-docs/.env')

print("=" * 80)
print("CHECK: TEST-WALLET VS CFB-PUZZLE IDs")
print("=" * 80)

# Lade die 20 CFB-Puzzle IDs
with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/CFB_ALL_20_IDENTITIES.json', 'r') as f:
    cfb_data = json.load(f)

# Leite Identity aus MASTER_SEED ab
seed = os.getenv("MASTER_SEED")
if not seed:
    print("FEHLER: MASTER_SEED nicht gefunden!")
    exit(1)

print(f"\nMASTER_SEED gefunden: {seed[:3]}***{seed[-3:]} ({len(seed)} Zeichen)")

# Derive identity
seed_bytes = seed.encode('utf-8')
subseed = get_subseed_from_seed(seed_bytes)
privkey = get_private_key_from_subseed(subseed)
pubkey = get_public_key_from_private_key(privkey)
wallet_identity = get_identity_from_public_key(pubkey)

print(f"\nTest-Wallet Identity: {wallet_identity}")

# Prüfe Balance
def check_balance(identity):
    try:
        url = f"https://rpc.qubic.org/v1/balances/{identity}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json().get("balance", {})
            return {
                "balance": int(data.get("balance", 0)),
                "incomingTX": int(data.get("numberOfIncomingTransfers", 0)),
                "outgoingTX": int(data.get("numberOfOutgoingTransfers", 0))
            }
    except:
        pass
    return None

wallet_balance = check_balance(wallet_identity)
if wallet_balance:
    print(f"Balance: {wallet_balance['balance']:,} QU")
    print(f"Incoming TX: {wallet_balance['incomingTX']}, Outgoing TX: {wallet_balance['outgoingTX']}")

# Vergleiche mit allen 20 CFB-Puzzle IDs
print("\n" + "=" * 80)
print("VERGLEICH MIT CFB-PUZZLE IDs:")
print("=" * 80)

match_found = False
for pair in cfb_data["pairs"]:
    cfb_identity = pair.get("identity")
    if cfb_identity == wallet_identity:
        print(f"\n⭐⭐⭐ MATCH GEFUNDEN! ⭐⭐⭐")
        print(f"Paar {pair['pair']}: ({pair['coords'][0]}, {pair['coords'][1]}) = Summe {pair['sum']}")
        print(f"Note: {pair.get('note', 'N/A')}")
        match_found = True
        break

if not match_found:
    print("\nKein direkter Match mit den 20 CFB-Puzzle IDs.")

    # Prüfe ob es vielleicht die EXIT-Node ist (verschiedene Derivation)
    print("\nPrüfe EXIT-Node Varianten...")

    # Die bekannte EXIT-Identity aus VERIFIED_STRATEGIC_NODES
    known_exit = "YLGSNIMGRKONPEBTLCRLYHQDFHEAKMUSRKYOGLPFAFDOFUUYVRBJTNSAXUSM"
    derived_exit = "RDFRUPFEUQKKMFQVNNUYUGMZXJLBIJTHYKMTQTJUIBKENWBKDFSTXYAEJHQI"

    if wallet_identity == known_exit:
        print(f"⭐ MATCH: Wallet = EXIT (bekannte Identity)")
    elif wallet_identity == derived_exit:
        print(f"⭐ MATCH: Wallet = EXIT (abgeleitete Identity)")
    else:
        # Zeige Ähnlichkeit
        for pair in cfb_data["pairs"]:
            cfb_id = pair.get("identity", "")
            matches = sum(1 for a, b in zip(wallet_identity, cfb_id) if a == b)
            if matches > 10:
                print(f"Paar {pair['pair']}: {matches}/60 Zeichen übereinstimmend")

# Zeige alle 20 IDs zum Vergleich
print("\n" + "=" * 80)
print("ALLE 20 CFB-PUZZLE IDs:")
print("=" * 80)
for pair in cfb_data["pairs"]:
    mark = "⭐" if pair.get("note") else ""
    print(f"Paar {pair['pair']:2d}: {pair['identity']} {mark}")

print(f"\nTest-Wallet: {wallet_identity}")
print(f"Balance: {wallet_balance['balance']:,} QU" if wallet_balance else "Balance: N/A")
