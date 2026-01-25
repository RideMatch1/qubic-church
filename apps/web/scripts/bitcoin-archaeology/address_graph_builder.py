#!/usr/bin/env python3
"""
Bitcoin Address Connection Graph Builder
Creates a graph of connected addresses from L137 sender address
"""

import requests
import json
import time
from collections import defaultdict
from typing import Dict, List, Set, Any, Optional

class AddressGraphBuilder:
    def __init__(self):
        self.base_url = "https://blockstream.info/api"
        self.graph = {
            "nodes": {},
            "edges": []
        }
        self.visited_addresses = set()
        self.visited_txids = set()

    def fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[Any]:
        """Fetch URL with retry logic"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    print(f"Rate limited, waiting...")
                    time.sleep(10 * (attempt + 1))
                else:
                    return None
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
        return None

    def add_node(self, address: str, label: str = "", node_type: str = "address"):
        """Add a node to the graph"""
        if address not in self.graph["nodes"]:
            self.graph["nodes"][address] = {
                "id": address,
                "label": label or address[:12] + "...",
                "type": node_type,
                "tx_count": 0,
                "total_btc": 0
            }

    def add_edge(self, source: str, target: str, txid: str, value: float, direction: str):
        """Add an edge to the graph"""
        edge = {
            "source": source,
            "target": target,
            "txid": txid,
            "value": value,
            "direction": direction
        }
        self.graph["edges"].append(edge)

    def build_graph_from_address(self, start_address: str, depth: int = 2, label: str = ""):
        """Build connection graph starting from an address"""
        print(f"\nBuilding graph from {start_address} (depth {depth})")

        self.add_node(start_address, label or "Start Address", "origin")
        self._explore_address(start_address, current_depth=0, max_depth=depth)

        return self.graph

    def _explore_address(self, address: str, current_depth: int, max_depth: int):
        """Recursively explore address connections"""
        if current_depth >= max_depth:
            return

        if address in self.visited_addresses:
            return

        self.visited_addresses.add(address)
        print(f"  Exploring: {address[:20]}... (depth {current_depth})")

        # Get address transactions
        txs = self.fetch_with_retry(f"{self.base_url}/address/{address}/txs")
        if not txs:
            return

        time.sleep(0.2)  # Rate limiting

        for tx in txs[:20]:  # Limit transactions per address
            txid = tx.get("txid")
            if txid in self.visited_txids:
                continue
            self.visited_txids.add(txid)

            # Process inputs
            for vin in tx.get("vin", []):
                prevout = vin.get("prevout", {})
                input_addr = prevout.get("scriptpubkey_address")
                if input_addr and input_addr != address:
                    value = prevout.get("value", 0) / 1e8
                    self.add_node(input_addr, "", "sender")
                    self.add_edge(input_addr, address, txid, value, "in")

                    if current_depth + 1 < max_depth:
                        self._explore_address(input_addr, current_depth + 1, max_depth)

            # Process outputs
            for vout in tx.get("vout", []):
                output_addr = vout.get("scriptpubkey_address")
                if output_addr and output_addr != address:
                    value = vout.get("value", 0) / 1e8
                    self.add_node(output_addr, "", "receiver")
                    self.add_edge(address, output_addr, txid, value, "out")

                    if current_depth + 1 < max_depth:
                        self._explore_address(output_addr, current_depth + 1, max_depth)

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return {
            "node_count": len(self.graph["nodes"]),
            "edge_count": len(self.graph["edges"]),
            "unique_txids": len(self.visited_txids),
            "addresses_explored": len(self.visited_addresses)
        }

    def export_for_visualization(self, filename: str = "ADDRESS_CONNECTION_GRAPH.json"):
        """Export graph in D3.js compatible format"""
        d3_graph = {
            "nodes": [
                {
                    "id": addr,
                    "label": data["label"],
                    "type": data["type"],
                    "group": 1 if data["type"] == "origin" else 2
                }
                for addr, data in self.graph["nodes"].items()
            ],
            "links": [
                {
                    "source": edge["source"],
                    "target": edge["target"],
                    "value": edge["value"],
                    "txid": edge["txid"]
                }
                for edge in self.graph["edges"]
            ]
        }

        with open(filename, "w") as f:
            json.dump(d3_graph, f, indent=2)

        print(f"\nGraph exported to {filename}")
        return d3_graph


def main():
    builder = AddressGraphBuilder()

    # Build graph from L137 sender address
    l137_address = "1K69sEhUwNgiva3xzPnToxS89dzydU7nPm"

    print("=" * 60)
    print("Building Address Connection Graph")
    print("=" * 60)

    graph = builder.build_graph_from_address(
        l137_address,
        depth=2,
        label="L137 Sender"
    )

    # Get statistics
    stats = builder.get_statistics()
    print(f"\nGraph Statistics:")
    print(f"  Nodes: {stats['node_count']}")
    print(f"  Edges: {stats['edge_count']}")
    print(f"  Unique Transactions: {stats['unique_txids']}")
    print(f"  Addresses Explored: {stats['addresses_explored']}")

    # Export for visualization
    builder.export_for_visualization("ADDRESS_CONNECTION_GRAPH.json")

    # Also save raw graph data
    with open("ADDRESS_GRAPH_RAW.json", "w") as f:
        json.dump({
            "statistics": stats,
            "graph": graph
        }, f, indent=2)

    print("\nGraph building complete!")


if __name__ == "__main__":
    main()
