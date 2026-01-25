#!/usr/bin/env python3
"""Monitor CFB nodes for any responses/changes."""

import requests
import time
import json
from datetime import datetime

NODES = [
    {"name": "ENTRY", "id": "VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH", "baseline_in": 9},
    {"name": "CORE", "id": "DWQNESYCKKBXIGOJHQOEHUHMALBADTWFYKNKFRNKOEZYMPEZNJMUEPAFBROB", "baseline_in": 2},
    {"name": "EXIT-F", "id": "RDFRUPFEUQKKMFQVNNUYUGMZXJLBIJTHYKMTQTJUIBKENWBKDFSTXYAEJHQI", "baseline_in": 2},
    {"name": "ANNA", "id": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFXIB", "baseline_in": 1},
]

def check_nodes():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking nodes...")
    changes = []
    
    for node in NODES:
        try:
            r = requests.get(f"https://rpc.qubic.org/v1/balances/{node['id']}", timeout=10)
            if r.status_code == 200:
                b = r.json().get("balance", {})
                incoming = int(b.get("numberOfIncomingTransfers", 0))
                balance = int(b.get("balance", 0))
                
                if incoming > node["baseline_in"]:
                    print(f"  🚨 {node['name']}: NEW INCOMING! {incoming} TX (was {node['baseline_in']})")
                    changes.append(node["name"])
                    node["baseline_in"] = incoming
                else:
                    print(f"  ○ {node['name']}: {balance} QU, {incoming} IN")
        except Exception as e:
            print(f"  ✗ {node['name']}: Error - {e}")
        time.sleep(0.3)
    
    return changes

print("CFB NODE MONITOR - Watching for responses...")
print("=" * 60)
print("Press Ctrl+C to stop\n")

check_count = 0
while check_count < 5:  # Check 5 times then exit
    changes = check_nodes()
    if changes:
        print(f"\n🔔 CHANGES DETECTED: {changes}")
    check_count += 1
    if check_count < 5:
        print(f"\nNext check in 10 seconds... ({check_count}/5)")
        time.sleep(10)

print("\n\nMonitoring complete. Run again to continue watching.")
