#!/usr/bin/env python3
"""
POCC Connection Investigation Script
=====================================

Checks if the GENESIS issuer (POCC) has connections to suspected addresses.

Addresses to investigate:
1. QGRNNKNCTTKV... (from screenshot)
2. LMEDNGMZKJDA...
3. WHCTXZQGFCYI...
4. PNGZZAVXTNGW...
5. WSSKPGUUHYBS...
6. NWODPWJXIGKR...

Plus: POCC (GENESIS issuer)

Author: qubic-academic-docs
Date: 2026-01-22
"""

import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# RPC Configuration
RPC_URL = "https://rpc.qubic.org"
TIMEOUT = 15

# Addresses to investigate
ADDRESSES = {
    "POCC_GENESIS_ISSUER": "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD",
    "SUSPECT_1_QGRNNK": "QGRNNKNCTTKV​BAACUANWEGRXGPGDOHXYZNMKGEUZSEXBNBBWUBJHAGDGWCSH",
    "SUSPECT_2_LMEDNG": "LMEDNGMZKJDARFHWKSLCPZQXZJHAGWTDQZNSATRYHARXRIWRKCNMUVRDMVMC",
    "SUSPECT_3_WHCTXZ": "WHCTXZQGFCYIHHUFIFJLRCXCUTLCMCQFDTVBHNDZV​FOCEVDSPEBFXWTBIJGA",
    "SUSPECT_4_PNGZZA": "PNGZZAVXTNGWVADZZPJGTMXQERUCUMXQZPBCGNHVKGVIDPPFGTBFLIFGOSKK",
    "SUSPECT_5_WSSKPG": "WSSKPGUUHYBSAFLVRLJEEHNNJCLJABLABRZPSKDLXZFLJNFYEQNQQOHDGKIJC",
    "SUSPECT_6_NWODPW": "NWODPWJXIGKRHEFUPQIFCCIEPXVCBTQNXPJXBSBMCFVFLOCRSKZRUBEFFJSN",
}

# Clean addresses (remove any hidden characters)
def clean_address(addr: str) -> str:
    """Remove any invisible characters from address."""
    return ''.join(c for c in addr if c.isalpha() and c.isupper())

def get_balance(address: str) -> dict:
    """Get balance and transaction info for an address."""
    clean_addr = clean_address(address)

    if len(clean_addr) != 60:
        return {"error": f"Invalid address length: {len(clean_addr)} (expected 60)"}

    try:
        url = f"{RPC_URL}/v1/balances/{clean_addr}"
        response = requests.get(url, timeout=TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            balance_info = data.get('balance', {})
            return {
                "address": clean_addr,
                "balance": balance_info.get('balance', 0),
                "valid_for_tick": balance_info.get('validForTick', 0),
                "latest_incoming_tick": balance_info.get('latestIncomingTransferTick', 0),
                "latest_outgoing_tick": balance_info.get('latestOutgoingTransferTick', 0),
                "incoming_amount": balance_info.get('incomingAmount', 0),
                "outgoing_amount": balance_info.get('outgoingAmount', 0),
                "num_incoming": balance_info.get('numberOfIncomingTransfers', 0),
                "num_outgoing": balance_info.get('numberOfOutgoingTransfers', 0),
                "status": "FOUND"
            }
        elif response.status_code == 404:
            return {
                "address": clean_addr,
                "status": "NOT_FOUND",
                "error": "Address not found or no transactions"
            }
        else:
            return {
                "address": clean_addr,
                "status": "ERROR",
                "error": f"HTTP {response.status_code}"
            }

    except Exception as e:
        return {
            "address": clean_addr,
            "status": "ERROR",
            "error": str(e)
        }

def get_transactions(address: str, start_tick: int = 0, end_tick: int = 99999999) -> dict:
    """Get transactions for an address."""
    clean_addr = clean_address(address)

    try:
        # Try the transactions endpoint
        url = f"{RPC_URL}/v2/identities/{clean_addr}/transfers"
        params = {"startTick": start_tick, "endTick": end_tick}
        response = requests.get(url, params=params, timeout=TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            return {
                "address": clean_addr,
                "transactions": data.get('transactions', []),
                "status": "FOUND"
            }
        else:
            return {
                "address": clean_addr,
                "status": "NO_TRANSACTIONS",
                "error": f"HTTP {response.status_code}"
            }

    except Exception as e:
        return {
            "address": clean_addr,
            "status": "ERROR",
            "error": str(e)
        }

def analyze_connections(results: dict) -> dict:
    """Analyze if any addresses have interacted with POCC."""
    pocc_data = results.get("POCC_GENESIS_ISSUER", {})

    connections = {
        "pocc_has_activity": pocc_data.get("num_incoming", 0) + pocc_data.get("num_outgoing", 0) > 0,
        "suspect_addresses_found": 0,
        "suspect_addresses_with_activity": 0,
        "potential_connections": [],
        "shared_tick_ranges": [],
    }

    pocc_in_tick = pocc_data.get("latest_incoming_tick", 0)
    pocc_out_tick = pocc_data.get("latest_outgoing_tick", 0)

    for name, data in results.items():
        if name == "POCC_GENESIS_ISSUER":
            continue

        if data.get("status") == "FOUND":
            connections["suspect_addresses_found"] += 1

            if data.get("num_incoming", 0) + data.get("num_outgoing", 0) > 0:
                connections["suspect_addresses_with_activity"] += 1

                # Check for overlapping tick ranges
                suspect_in = data.get("latest_incoming_tick", 0)
                suspect_out = data.get("latest_outgoing_tick", 0)

                if suspect_in > 0 and suspect_out > 0:
                    # Check if transactions happened in similar timeframe
                    if abs(suspect_in - pocc_in_tick) < 10000 or abs(suspect_out - pocc_out_tick) < 10000:
                        connections["shared_tick_ranges"].append({
                            "address": name,
                            "suspect_ticks": (suspect_in, suspect_out),
                            "pocc_ticks": (pocc_in_tick, pocc_out_tick)
                        })

    return connections

def main():
    print("=" * 70)
    print("POCC CONNECTION INVESTIGATION")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"RPC Endpoint: {RPC_URL}")
    print()

    results = {}

    # Check each address
    print("CHECKING ADDRESSES...")
    print("-" * 70)

    for name, address in ADDRESSES.items():
        clean_addr = clean_address(address)
        print(f"\n[{name}]")
        print(f"  Address: {clean_addr[:20]}...{clean_addr[-10:]}")
        print(f"  Length: {len(clean_addr)}")

        # Get balance info
        balance_data = get_balance(address)
        results[name] = balance_data

        if balance_data.get("status") == "FOUND":
            print(f"  Status: FOUND")
            balance = balance_data.get('balance', 0)
            if isinstance(balance, str):
                balance = int(balance) if balance.isdigit() else balance
            print(f"  Balance: {balance:,} QUBIC" if isinstance(balance, int) else f"  Balance: {balance} QUBIC")
            print(f"  Incoming TXs: {balance_data.get('num_incoming', 0)}")
            print(f"  Outgoing TXs: {balance_data.get('num_outgoing', 0)}")
            print(f"  Last In Tick: {balance_data.get('latest_incoming_tick', 0)}")
            print(f"  Last Out Tick: {balance_data.get('latest_outgoing_tick', 0)}")
        elif balance_data.get("status") == "NOT_FOUND":
            print(f"  Status: NOT FOUND (no activity)")
        else:
            print(f"  Status: ERROR - {balance_data.get('error', 'Unknown')}")

    # Analyze connections
    print("\n" + "=" * 70)
    print("CONNECTION ANALYSIS")
    print("=" * 70)

    connections = analyze_connections(results)

    print(f"\nPOCC has activity: {connections['pocc_has_activity']}")
    print(f"Suspect addresses found: {connections['suspect_addresses_found']}/6")
    print(f"Suspect addresses with activity: {connections['suspect_addresses_with_activity']}/6")

    if connections['shared_tick_ranges']:
        print("\nPOTENTIAL TEMPORAL CONNECTIONS:")
        for conn in connections['shared_tick_ranges']:
            print(f"  - {conn['address']}: ticks {conn['suspect_ticks']}")
    else:
        print("\nNo overlapping tick ranges found between POCC and suspects.")

    # Assessment
    print("\n" + "=" * 70)
    print("ASSESSMENT")
    print("=" * 70)

    if connections['suspect_addresses_found'] == 0:
        print("\nRESULT: Cannot verify - suspect addresses not found on-chain")
        print("This could mean:")
        print("  1. Addresses were copied incorrectly from screenshot")
        print("  2. Addresses have never been used")
        print("  3. Addresses are on a different network")
    elif connections['suspect_addresses_with_activity'] == 0:
        print("\nRESULT: No direct connection found")
        print("Suspect addresses exist but show no transaction activity.")
    else:
        if connections['shared_tick_ranges']:
            print("\nRESULT: POSSIBLE CONNECTION DETECTED")
            print("Some addresses show activity in similar tick ranges as POCC.")
            print("This requires further investigation of actual transaction data.")
        else:
            print("\nRESULT: No obvious connection")
            print("Addresses have activity but not in overlapping timeframes with POCC.")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "rpc_url": RPC_URL,
        "addresses_checked": results,
        "connection_analysis": connections,
    }

    output_path = Path(__file__).parent / "POCC_CONNECTION_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
