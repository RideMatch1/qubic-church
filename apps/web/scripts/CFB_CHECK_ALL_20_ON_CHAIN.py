#!/usr/bin/env python3
"""
CFB Puzzle - Prüfe alle 20 Qubic IDs auf der Blockchain

Prüft, welche der 20 CFB-Puzzle IDs echte Transaktionen haben.
Eine ID "existiert" nur, wenn numberOfIncomingTransfers > 0!
"""

import json
import requests
import time

# Lade die abgeleiteten IDs
with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/CFB_ALL_20_IDENTITIES.json', 'r') as f:
    data = json.load(f)

print("=" * 80)
print("CFB PUZZLE - BLOCKCHAIN VERIFICATION ALLER 20 IDs")
print("=" * 80)

def check_qubic_id(identity):
    """Prüfe eine Qubic ID auf der Blockchain."""
    try:
        url = f"https://rpc.qubic.org/v1/balances/{identity}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            balance_data = result.get("balance", {})
            return {
                "valid": True,
                "balance": int(balance_data.get("balance", 0)),
                "incomingAmount": int(balance_data.get("incomingAmount", 0)),
                "outgoingAmount": int(balance_data.get("outgoingAmount", 0)),
                "numberOfIncomingTransfers": int(balance_data.get("numberOfIncomingTransfers", 0)),
                "numberOfOutgoingTransfers": int(balance_data.get("numberOfOutgoingTransfers", 0)),
                "latestIncomingTransferTick": balance_data.get("latestIncomingTransferTick", 0),
                "latestOutgoingTransferTick": balance_data.get("latestOutgoingTransferTick", 0)
            }
        return {"valid": False, "status": response.status_code, "error": response.text}
    except Exception as e:
        return {"valid": False, "error": str(e)}

results = []
active_ids = []

print("\nPrüfe alle 20 Qubic IDs...\n")

for pair in data["pairs"]:
    identity = pair.get("identity")
    if not identity:
        continue

    print(f"Paar {pair['pair']:2d}: ({pair['coords'][0]:2d}, {pair['coords'][1]:2d}) = {pair['sum']:3d}")
    print(f"   ID: {identity}")

    result = check_qubic_id(identity)
    pair["blockchain_check"] = result
    results.append(pair)

    if result.get("valid"):
        n_incoming = result.get("numberOfIncomingTransfers", 0)
        balance = result.get("balance", 0)

        if n_incoming > 0:
            print(f"   ⭐⭐⭐ AKTIV! Balance: {balance} QU, Incoming TX: {n_incoming} ⭐⭐⭐")
            active_ids.append(pair)
        else:
            print(f"   Format gültig, aber KEINE eingehenden Transaktionen")
    else:
        print(f"   Fehler: {result.get('error', 'unknown')}")

    time.sleep(0.5)  # Rate limiting

# Zusammenfassung
print("\n" + "=" * 80)
print("ZUSAMMENFASSUNG")
print("=" * 80)

print(f"\nGeprüft: {len(results)} IDs")
print(f"Aktive IDs (mit eingehenden Transaktionen): {len(active_ids)}")

if active_ids:
    print("\n🌟 AKTIVE CFB-PUZZLE QUBIC IDs:")
    print("-" * 80)
    for pair in active_ids:
        bc = pair["blockchain_check"]
        print(f"\nPaar {pair['pair']}: ({pair['coords'][0]}, {pair['coords'][1]}) = {pair['sum']}")
        print(f"   ID: {pair['identity']}")
        print(f"   Balance: {bc.get('balance', 0)} QU")
        print(f"   Incoming TX: {bc.get('numberOfIncomingTransfers', 0)}")
        print(f"   Note: {pair.get('note', '')}")

# Speichere Ergebnisse
output = {
    "checked": len(results),
    "active": len(active_ids),
    "all_results": results,
    "active_ids": active_ids
}

with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/CFB_BLOCKCHAIN_VERIFICATION.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nErgebnisse gespeichert in: CFB_BLOCKCHAIN_VERIFICATION.json")
