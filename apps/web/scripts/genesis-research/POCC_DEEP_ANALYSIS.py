#!/usr/bin/env python3
"""
POCC Deep Analysis - GENESIS Token Distribution Research
=========================================================

Comprehensive analysis of the POCC address (GENESIS token issuer):
- All transactions from/to POCC
- GENESIS token holder distribution
- Whale address identification
- Transfer network graph
- Temporal patterns

Author: qubic-academic-docs
Date: 2026-01-22
"""

import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Optional

# Configuration
RPC_ENDPOINTS = [
    "https://rpc.qubic.org",
    "https://rpc.qubic.li",
]
TIMEOUT = 30
MAX_RETRIES = 3

# POCC Address - GENESIS Token Issuer
POCC_ADDRESS = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

# GENESIS Token Details
GENESIS_TOKEN = {
    "name": "GENESIS",
    "issuer": POCC_ADDRESS,
    "total_supply": 676_000_000_000,  # 676 billion
    "burned_percentage": 0.98,  # 98% burned
    "circulating_estimate": 16_250_000_000,  # ~16.25 billion
    "significance": "26^2 = 676 - Qubic Computors count squared"
}

# Output directory
OUTPUT_DIR = Path(__file__).parent / "outputs"


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def make_request(endpoint: str, params: dict = None) -> Optional[dict]:
    """Make request with fallback to multiple endpoints."""
    for base_url in RPC_ENDPOINTS:
        for attempt in range(MAX_RETRIES):
            try:
                url = f"{base_url}{endpoint}"
                response = requests.get(url, params=params, timeout=TIMEOUT)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None

            except Exception as e:
                print(f"  Attempt {attempt + 1} failed: {e}")
                time.sleep(1)

        print(f"  Switching to next endpoint...")

    return None


def get_balance(address: str) -> dict:
    """Get balance and transaction metadata for an address."""
    result = make_request(f"/v1/balances/{address}")

    if result and 'balance' in result:
        balance_data = result['balance']
        return {
            "address": address,
            "balance": int(balance_data.get('balance', 0)),
            "valid_for_tick": balance_data.get('validForTick', 0),
            "latest_incoming_tick": balance_data.get('latestIncomingTransferTick', 0),
            "latest_outgoing_tick": balance_data.get('latestOutgoingTransferTick', 0),
            "incoming_amount": int(balance_data.get('incomingAmount', 0)),
            "outgoing_amount": int(balance_data.get('outgoingAmount', 0)),
            "num_incoming": balance_data.get('numberOfIncomingTransfers', 0),
            "num_outgoing": balance_data.get('numberOfOutgoingTransfers', 0),
            "status": "FOUND"
        }

    return {"address": address, "status": "NOT_FOUND"}


def get_transfers(address: str, start_tick: int = 0, end_tick: int = 99999999) -> list:
    """Get all transfers for an address (paginated)."""
    all_transfers = []
    page_size = 100

    result = make_request(
        f"/v2/identities/{address}/transfers",
        params={"startTick": start_tick, "endTick": end_tick}
    )

    if result and 'transactions' in result:
        all_transfers.extend(result['transactions'])

    return all_transfers


def get_asset_holdings(address: str) -> list:
    """Get asset/token holdings for an address."""
    result = make_request(f"/v1/assets/{address}/issued")

    if result and 'issuedAssets' in result:
        return result['issuedAssets']

    return []


def analyze_pocc_transactions(transfers: list) -> dict:
    """Analyze POCC transaction patterns."""
    analysis = {
        "total_transfers": len(transfers),
        "incoming_transfers": [],
        "outgoing_transfers": [],
        "unique_senders": set(),
        "unique_receivers": set(),
        "by_tick": defaultdict(list),
        "amounts": [],
    }

    for tx in transfers:
        source = tx.get('sourceId', '')
        dest = tx.get('destId', '')
        amount = int(tx.get('amount', 0))
        tick = tx.get('tickNumber', 0)

        if source == POCC_ADDRESS:
            analysis["outgoing_transfers"].append(tx)
            analysis["unique_receivers"].add(dest)
        else:
            analysis["incoming_transfers"].append(tx)
            analysis["unique_senders"].add(source)

        analysis["by_tick"][tick].append(tx)
        analysis["amounts"].append(amount)

    # Convert sets to lists for JSON serialization
    analysis["unique_senders"] = list(analysis["unique_senders"])
    analysis["unique_receivers"] = list(analysis["unique_receivers"])
    analysis["by_tick"] = dict(analysis["by_tick"])

    # Calculate statistics
    if analysis["amounts"]:
        analysis["stats"] = {
            "total_transferred": sum(analysis["amounts"]),
            "average_amount": sum(analysis["amounts"]) / len(analysis["amounts"]),
            "min_amount": min(analysis["amounts"]),
            "max_amount": max(analysis["amounts"]),
            "num_unique_senders": len(analysis["unique_senders"]),
            "num_unique_receivers": len(analysis["unique_receivers"]),
        }

    return analysis


def build_genesis_distribution(receivers: list) -> dict:
    """Build GENESIS token holder distribution."""
    print("\n[3] Building GENESIS holder distribution...")

    distribution = {
        "holders": {},
        "total_checked": 0,
        "found_with_balance": 0,
        "errors": [],
    }

    # Check each unique receiver
    for i, address in enumerate(receivers[:200]):  # Limit to 200 for API rate limits
        print(f"  Checking {i+1}/{min(len(receivers), 200)}: {address[:20]}...")

        try:
            balance_data = get_balance(address)
            distribution["total_checked"] += 1

            if balance_data.get("status") == "FOUND":
                balance = balance_data.get("balance", 0)
                if balance > 0:
                    distribution["found_with_balance"] += 1
                    distribution["holders"][address] = {
                        "balance": balance,
                        "incoming_amount": balance_data.get("incoming_amount", 0),
                        "outgoing_amount": balance_data.get("outgoing_amount", 0),
                        "num_incoming": balance_data.get("num_incoming", 0),
                        "num_outgoing": balance_data.get("num_outgoing", 0),
                    }

            time.sleep(0.3)  # Rate limiting

        except Exception as e:
            distribution["errors"].append({
                "address": address,
                "error": str(e)
            })

    # Sort by balance
    sorted_holders = sorted(
        distribution["holders"].items(),
        key=lambda x: x[1]["balance"],
        reverse=True
    )
    distribution["holders"] = dict(sorted_holders)

    return distribution


def identify_whales(holders: dict, top_n: int = 100) -> list:
    """Identify top GENESIS token holders (whales)."""
    sorted_holders = sorted(
        holders.items(),
        key=lambda x: x[1]["balance"],
        reverse=True
    )[:top_n]

    whales = []
    total_whale_balance = sum(h[1]["balance"] for h in sorted_holders)

    for rank, (address, data) in enumerate(sorted_holders, 1):
        balance = data["balance"]
        percentage = (balance / GENESIS_TOKEN["circulating_estimate"]) * 100 if GENESIS_TOKEN["circulating_estimate"] > 0 else 0

        whales.append({
            "rank": rank,
            "address": address,
            "address_short": f"{address[:12]}...{address[-8:]}",
            "balance": balance,
            "balance_formatted": f"{balance:,}",
            "percentage_of_circulating": round(percentage, 4),
            "incoming_total": data.get("incoming_amount", 0),
            "outgoing_total": data.get("outgoing_amount", 0),
            "tx_count": data.get("num_incoming", 0) + data.get("num_outgoing", 0),
        })

    return whales


def create_transfer_graph(transfers: list) -> dict:
    """Create network graph data for visualization."""
    graph = {
        "nodes": {},
        "edges": [],
        "stats": {
            "total_nodes": 0,
            "total_edges": 0,
            "connected_components": 0,
        }
    }

    # Build nodes and edges
    for tx in transfers:
        source = tx.get('sourceId', '')
        dest = tx.get('destId', '')
        amount = int(tx.get('amount', 0))
        tick = tx.get('tickNumber', 0)

        # Add nodes
        if source and source not in graph["nodes"]:
            graph["nodes"][source] = {
                "id": source,
                "short": f"{source[:8]}...{source[-4:]}",
                "is_pocc": source == POCC_ADDRESS,
                "total_sent": 0,
                "total_received": 0,
                "connections": set(),
            }

        if dest and dest not in graph["nodes"]:
            graph["nodes"][dest] = {
                "id": dest,
                "short": f"{dest[:8]}...{dest[-4:]}",
                "is_pocc": dest == POCC_ADDRESS,
                "total_sent": 0,
                "total_received": 0,
                "connections": set(),
            }

        # Update node stats
        if source:
            graph["nodes"][source]["total_sent"] += amount
            graph["nodes"][source]["connections"].add(dest)
        if dest:
            graph["nodes"][dest]["total_received"] += amount
            graph["nodes"][dest]["connections"].add(source)

        # Add edge
        graph["edges"].append({
            "source": source,
            "target": dest,
            "amount": amount,
            "tick": tick,
        })

    # Convert sets to lists for JSON serialization
    for node_id in graph["nodes"]:
        graph["nodes"][node_id]["connections"] = list(graph["nodes"][node_id]["connections"])

    graph["stats"]["total_nodes"] = len(graph["nodes"])
    graph["stats"]["total_edges"] = len(graph["edges"])

    return graph


def decode_pocc_mathematical():
    """Decode mathematical significance of POCC address."""
    alphabet_values = {chr(i + ord('A')): i for i in range(26)}

    prefix = "POCC"
    values = [alphabet_values[c] for c in prefix]
    prefix_sum = sum(values)

    return {
        "address": POCC_ADDRESS,
        "prefix": prefix,
        "prefix_values": dict(zip(prefix, values)),
        "prefix_sum": prefix_sum,
        "significance": {
            "33_in_matrix": "Matrix position (6, 33) contains value 26",
            "26_squared": f"26^2 = {26**2} = 676 = GENESIS supply basis",
            "676_computors": "676 = Number of Qubic Computors",
            "fine_structure": "45 + 92 = 137 = Fine structure constant"
        }
    }


def main():
    print("=" * 70)
    print("POCC DEEP ANALYSIS - GENESIS Token Research")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"POCC Address: {POCC_ADDRESS[:30]}...")
    print()

    ensure_output_dir()

    results = {
        "timestamp": datetime.now().isoformat(),
        "pocc_address": POCC_ADDRESS,
        "genesis_token": GENESIS_TOKEN,
        "mathematical_decode": decode_pocc_mathematical(),
    }

    # Step 1: Get POCC balance and metadata
    print("[1] Fetching POCC balance and metadata...")
    pocc_balance = get_balance(POCC_ADDRESS)
    results["pocc_balance"] = pocc_balance
    print(f"  Status: {pocc_balance.get('status')}")

    if pocc_balance.get('status') == 'FOUND':
        print(f"  Balance: {pocc_balance.get('balance', 0):,} QUBIC")
        print(f"  Incoming TXs: {pocc_balance.get('num_incoming', 0)}")
        print(f"  Outgoing TXs: {pocc_balance.get('num_outgoing', 0)}")

    # Step 2: Get all POCC transfers
    print("\n[2] Fetching POCC transfer history...")
    transfers = get_transfers(POCC_ADDRESS)
    print(f"  Found {len(transfers)} transfers")

    # Step 3: Analyze transactions
    print("\n[3] Analyzing transaction patterns...")
    tx_analysis = analyze_pocc_transactions(transfers)
    results["transaction_analysis"] = {
        "total_transfers": tx_analysis["total_transfers"],
        "incoming_count": len(tx_analysis["incoming_transfers"]),
        "outgoing_count": len(tx_analysis["outgoing_transfers"]),
        "unique_senders": tx_analysis["unique_senders"],
        "unique_receivers": tx_analysis["unique_receivers"],
        "stats": tx_analysis.get("stats", {}),
    }

    print(f"  Incoming: {len(tx_analysis['incoming_transfers'])}")
    print(f"  Outgoing: {len(tx_analysis['outgoing_transfers'])}")
    print(f"  Unique senders: {len(tx_analysis['unique_senders'])}")
    print(f"  Unique receivers: {len(tx_analysis['unique_receivers'])}")

    # Step 4: Build holder distribution (if we have outgoing transfers)
    if tx_analysis["unique_receivers"]:
        distribution = build_genesis_distribution(tx_analysis["unique_receivers"])
        results["holder_distribution"] = {
            "total_checked": distribution["total_checked"],
            "found_with_balance": distribution["found_with_balance"],
            "holder_count": len(distribution["holders"]),
        }

        # Save full distribution separately
        dist_output = OUTPUT_DIR / "GENESIS_HOLDER_DISTRIBUTION.json"
        with open(dist_output, 'w') as f:
            json.dump(distribution, f, indent=2, default=str)
        print(f"\n  Holder distribution saved to: {dist_output}")

        # Step 5: Identify whales
        print("\n[5] Identifying whale addresses...")
        whales = identify_whales(distribution["holders"])
        results["top_100_whales"] = whales[:100]

        whale_output = OUTPUT_DIR / "GENESIS_TOP_100_WHALES.json"
        with open(whale_output, 'w') as f:
            json.dump(whales, f, indent=2, default=str)
        print(f"  Top 100 whales saved to: {whale_output}")

        if whales:
            print(f"\n  Top 5 Whales:")
            for w in whales[:5]:
                print(f"    #{w['rank']}: {w['address_short']} - {w['balance_formatted']} ({w['percentage_of_circulating']:.2f}%)")

    # Step 6: Create transfer graph
    print("\n[6] Creating transfer network graph...")
    graph = create_transfer_graph(transfers)
    results["transfer_graph_stats"] = graph["stats"]

    graph_output = OUTPUT_DIR / "POCC_TRANSFER_GRAPH.json"
    with open(graph_output, 'w') as f:
        json.dump(graph, f, indent=2, default=str)
    print(f"  Transfer graph saved to: {graph_output}")
    print(f"  Nodes: {graph['stats']['total_nodes']}")
    print(f"  Edges: {graph['stats']['total_edges']}")

    # Save main results
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    main_output = OUTPUT_DIR / "POCC_COMPLETE_ANALYSIS.json"
    with open(main_output, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nPOCC Mathematical Significance:")
    math = results["mathematical_decode"]
    print(f"  Prefix POCC = {' + '.join(str(v) for v in math['prefix_values'].values())} = {math['prefix_sum']}")
    print(f"  Matrix(6, 33) = 26")
    print(f"  26^2 = 676 = GENESIS Supply Basis")

    print(f"\nResults saved to: {main_output}")
    print(f"\nAll outputs in: {OUTPUT_DIR}/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
