import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
RPC_URL = os.getenv("QUBIC_RPC_URL", "https://rpc.qubic.org")

class QubicClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def get_tick_info(self):
        r = requests.get(f"{self.base_url}/v1/tick-info", timeout=10)
        r.raise_for_status()
        return r.json()

    def get_balance(self, identity):
        r = requests.get(f"{self.base_url}/v1/balances/{identity}", timeout=10)
        r.raise_for_status()
        return r.json()

def show_network_stats():
    client = QubicClient(RPC_URL)
    try:
        data = client.get_tick_info()
        info = data.get('tickInfo', {})
        print(f"\n--- 🌐 QUBIC NETWORK STATUS ---")
        print(f"URL: {RPC_URL}")
        print(f"Tick: {info.get('tick')}")
        print(f"Epoch: {info.get('epoch')}")
        print(f"-------------------------------\n")
        return True
    except Exception as e:
        print(f"[X] Connectivity Error: {e}")
        return False

def check_balance(identity_str):
    client = QubicClient(RPC_URL)
    try:
        data = client.get_balance(identity_str)
        print(f"\n--- 💰 BALANCE CHECK ---")
        print(f"Identity: {identity_str}")
        print(f"Balance: {data.get('balance')} QUBIC")
        print(f"Status: {data.get('status')}")
        print(f"------------------------\n")
    except Exception as e:
        print(f"[X] Balance Check Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "stats":
            show_network_stats()
        elif cmd == "balance" and len(sys.argv) > 2:
            check_balance(sys.argv[2])
    else:
        show_network_stats()
