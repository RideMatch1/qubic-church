#!/usr/bin/env python3
"""
===============================================================================
              🔥 CFB CHAIN FLOW - GUTHABEN DURCH DAS NETZWERK 🔥
===============================================================================

Sendet das Guthaben von jedem Node zum nächsten:
ENTRY → P2 → P3 → ... → P19 → EXIT-F

Am Ende: EXIT-F akkumuliert das gesamte Puzzle-Guthaben.

Author: The Bridge Architect
Date: 2026-01-24
===============================================================================
"""

import json
import time
import base64
import requests
from datetime import datetime
from pathlib import Path

from qubipy.crypto.utils import (
    get_public_key_from_identity,
    get_subseed_from_seed,
    get_private_key_from_subseed,
    get_public_key_from_private_key,
    kangaroo_twelve,
    sign,
    get_identity_from_public_key
)

RPC_URL = "https://rpc.qubic.org"
TIMEOUT = 15

# Die 20 CFB-Puzzle Nodes in Reihenfolge
CFB_CHAIN = [
    {"pair": 1, "coords": [45, 92], "identity": "VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH", "name": "ENTRY"},
    {"pair": 2, "coords": [3, 77], "identity": "LISHDJGYQEQYWEEXJLNMYEQDYXSALKHFTFXESCSHGHAYAOLGZTHFCWCBRJVC", "name": "P2"},
    {"pair": 3, "coords": [14, 58], "identity": "MXCFUHIUQRVWUFCZEPXJCEIFFPWBULUXTITJTTMVPDRLDKIPWECENXSDFXXJ", "name": "P3"},
    {"pair": 4, "coords": [29, 81], "identity": "AWAABIBPQNGBZDMMIMWNMZDKBIOAHJYIZWQPMOPLSCFZXQVNEPIMUBKEKXJC", "name": "P4"},
    {"pair": 5, "coords": [6, 33], "identity": "DWQNESYCKKBXIGOJHQOEHUHMALBADTWFYKNKFRNKOEZYMPEZNJMUEPAFBROB", "name": "CORE"},
    {"pair": 6, "coords": [70, 48], "identity": "CFAAYZNNZYOKRBJZYNSJSLIDMXICLHZBHXFKSXOZXESMCUHMLOIUJBBENVMH", "name": "P6"},
    {"pair": 7, "coords": [95, 22], "identity": "OIRGTWZESOJZHDVRCMQSJLMEQQBDZKTDRVOSITFRLCCKCWHCUPWYXXJHXXIE", "name": "P7"},
    {"pair": 8, "coords": [61, 9], "identity": "GODJAKZUXGDCUFTLKTCUXCNDBZGBZBZGXFSOQEGCMDCREPTFLMCVFGIAYTFK", "name": "P8"},
    {"pair": 9, "coords": [84, 37], "identity": "KGMVFUQSQQTYCCHYQRPOPFCCTHMBERWBOEEXRSNEPDWSFOIOGGXJDLJDHVIB", "name": "EXIT-M"},
    {"pair": 10, "coords": [50, 16], "identity": "KWSWPBOKROVYVEXYYZAOXUUILUCBOKUQBIFPOEEZDCKNBUNQNYLZKYZAGGTB", "name": "P10"},
    {"pair": 11, "coords": [73, 28], "identity": "KUFDFTNVSAJPBAVTGTOEERNSKLQCHCHUXFOSWFONUEOVTHUBVWWBNIODBSDI", "name": "P11"},
    {"pair": 12, "coords": [85, 41], "identity": "OYPEVSVUXVUKTCMESFQAEMLBWRHDRYYBUAYMHLLLYFUKEIEKQZHGRTAFMIJI", "name": "P12"},
    {"pair": 13, "coords": [96, 7], "identity": "AUAYEMNSRHDUFARJNNZYNIRGMMHBMOBOJAFZAYCPLGIDQQQQRNJFYLIHABVH", "name": "P13"},
    {"pair": 14, "coords": [62, 19], "identity": "QQJMQAVNCRLACDVDGNNCQXBHNPICLYGCFCDEJYZMMFAEWHHVZHRHPMAEHLCK", "name": "P14"},
    {"pair": 15, "coords": [74, 30], "identity": "HOWIXXQSALKMPFCOSKEYPOCGJQYBUWEHTIEREXNMUFTYKKQWCBJBPQDGSHDI", "name": "P15"},
    {"pair": 16, "coords": [87, 43], "identity": "TQXTTXTBFKMMHEWVBZZETVZSCOICNAUNHDFYNIIJMGMRZCNYUSZEXQCDTEKD", "name": "P16"},
    {"pair": 17, "coords": [98, 5], "identity": "RHGZDSPLKJBKOGTXOYMYDNWMZAWBLXIPSWEUQKXQGFNSUQXAPQTXOSAHVBZE", "name": "P17"},
    {"pair": 18, "coords": [60, 15], "identity": "EBDHSLAQBOKNMATKMAWQRTOABCCANQCDYLMZQNRTVANWMJPRVDYNMUTGXPJO", "name": "P18"},
    {"pair": 19, "coords": [72, 27], "identity": "XKQJUGHFIDINTBJYKJDRTKVLUOSCTTCEQNGFHDNIACFXPHYPLRZTFFBHGMDC", "name": "P19"},
    {"pair": 20, "coords": [82, 39], "identity": "RDFRUPFEUQKKMFQVNNUYUGMZXJLBIJTHYKMTQTJUIBKENWBKDFSTXYAEJHQI", "name": "EXIT-F"},
]


class ChainFlowExecutor:
    def __init__(self):
        # Load cartography for private keys
        with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json', 'r') as f:
            self.cartography = json.load(f)
        
        self.log_file = Path(__file__).parent / f"CFB_CHAIN_FLOW_LOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        self.transactions = []

    def log(self, event, data):
        entry = {"ts": datetime.now().isoformat(), "event": event, "data": data}
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")

    def get_tick(self):
        r = requests.get(f"{RPC_URL}/v1/tick-info", timeout=TIMEOUT)
        return r.json().get('tickInfo', {}).get('tick', 0)

    def get_balance(self, identity):
        try:
            r = requests.get(f"{RPC_URL}/v1/balances/{identity}", timeout=TIMEOUT)
            if r.status_code == 200:
                return int(r.json().get('balance', {}).get('balance', 0))
        except:
            pass
        return 0

    def get_keys_for_node(self, node):
        """Get private key and derive all needed keys for a node."""
        row, col = node["coords"]
        key_lookup = f"{row},{col}"
        
        if key_lookup not in self.cartography:
            return None
        
        privkey_hex = self.cartography[key_lookup]
        privkey = bytes.fromhex(privkey_hex)
        
        # For Qubic, we need to derive from the private key as a seed
        # The private key in cartography IS the seed
        seed_bytes = privkey[:32] if len(privkey) >= 32 else privkey.ljust(32, b'\x00')
        
        subseed = get_subseed_from_seed(seed_bytes)
        priv_key = get_private_key_from_subseed(subseed)
        pub_key = get_public_key_from_private_key(priv_key)
        identity = get_identity_from_public_key(pub_key)
        
        return {
            "subseed": subseed,
            "priv_key": priv_key,
            "pub_key": pub_key,
            "identity": identity
        }

    def send_from_node(self, from_node, to_identity, amount):
        """Send transaction FROM a puzzle node."""
        keys = self.get_keys_for_node(from_node)
        if not keys:
            return {"success": False, "error": "No keys found"}
        
        try:
            current_tick = self.get_tick()
            target_tick = current_tick + 10
            
            dest_pub_key = get_public_key_from_identity(to_identity)
            
            tx_data = bytearray(80)
            tx_data[0:32] = keys["pub_key"]
            tx_data[32:64] = dest_pub_key
            tx_data[64:72] = amount.to_bytes(8, byteorder='little')
            tx_data[72:76] = target_tick.to_bytes(4, byteorder='little')
            tx_data[76:78] = (0).to_bytes(2, byteorder='little')
            tx_data[78:80] = (0).to_bytes(2, byteorder='little')
            
            digest = kangaroo_twelve(bytes(tx_data), 80, 32)
            signature = sign(keys["subseed"], keys["pub_key"], digest)
            full_tx = bytes(tx_data) + signature
            
            final_digest = kangaroo_twelve(bytes(full_tx), 144, 32)
            tx_id = get_identity_from_public_key(final_digest).lower()
            
            b64_tx = base64.b64encode(full_tx).decode('utf-8')
            resp = requests.post(
                f"{RPC_URL}/v1/broadcast-transaction",
                json={"encodedTransaction": b64_tx},
                timeout=30
            )
            
            if resp.status_code == 200:
                return {"success": True, "tx_id": tx_id, "tick": target_tick}
            return {"success": False, "error": resp.text[:100]}
        
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run(self):
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ██████╗██╗  ██╗ █████╗ ██╗███╗   ██╗    ███████╗██╗      ██████╗ ██╗    ║
║  ██╔════╝██║  ██║██╔══██╗██║████╗  ██║    ██╔════╝██║     ██╔═══██╗██║    ║
║  ██║     ███████║███████║██║██╔██╗ ██║    █████╗  ██║     ██║   ██║██║    ║
║  ██║     ██╔══██║██╔══██║██║██║╚██╗██║    ██╔══╝  ██║     ██║   ██║██║    ║
║  ╚██████╗██║  ██║██║  ██║██║██║ ╚████║    ██║     ███████╗╚██████╔╝███████║
║   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝     ╚══════╝ ╚═════╝ ╚══════╝
║                                                                           ║
║              🔥 ENTRY → ... → EXIT - GUTHABEN FLIESSEN 🔥                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)
        
        print(f"Log: {self.log_file}\n")
        
        # First, check current balances
        print("=" * 70)
        print("PHASE 1: AKTUELLE GUTHABEN PRÜFEN")
        print("=" * 70)
        
        balances = {}
        total_in_chain = 0
        
        for node in CFB_CHAIN:
            bal = self.get_balance(node["identity"])
            balances[node["pair"]] = bal
            total_in_chain += bal
            print(f"  {node['name']:8s}: {bal:4d} QU")
            time.sleep(0.2)
        
        print(f"\n  TOTAL im Puzzle: {total_in_chain} QU")
        
        # Execute chain flow
        print("\n" + "=" * 70)
        print("PHASE 2: CHAIN FLOW AUSFÜHREN")
        print("=" * 70)
        print("\nJeder Node sendet sein Guthaben zum nächsten...\n")
        
        successful = 0
        failed = 0
        
        for i in range(len(CFB_CHAIN) - 1):
            from_node = CFB_CHAIN[i]
            to_node = CFB_CHAIN[i + 1]
            
            balance = balances.get(from_node["pair"], 0)
            
            if balance <= 0:
                print(f"  [{i+1:2d}/19] {from_node['name']:8s} → {to_node['name']:8s}: SKIP (0 QU)")
                continue
            
            # Send all balance to next node
            amount = balance
            
            print(f"  [{i+1:2d}/19] {from_node['name']:8s} → {to_node['name']:8s}: {amount:4d} QU ", end="", flush=True)
            
            result = self.send_from_node(from_node, to_node["identity"], amount)
            
            if result.get("success"):
                print(f"✓ TX: {result['tx_id'][:16]}...")
                successful += 1
                self.transactions.append({
                    "from": from_node["name"],
                    "to": to_node["name"],
                    "amount": amount,
                    "tx_id": result["tx_id"],
                    "success": True
                })
            else:
                print(f"✗ {result.get('error', 'unknown')[:40]}")
                failed += 1
                self.transactions.append({
                    "from": from_node["name"],
                    "to": to_node["name"],
                    "amount": amount,
                    "success": False,
                    "error": result.get("error")
                })
            
            self.log("CHAIN_TX", self.transactions[-1])
            time.sleep(0.5)
        
        # Summary
        print("\n" + "=" * 70)
        print("ZUSAMMENFASSUNG")
        print("=" * 70)
        print(f"\n  Erfolgreich: {successful}")
        print(f"  Fehlgeschlagen: {failed}")
        print(f"  Total bewegt: {sum(t['amount'] for t in self.transactions if t.get('success', False))} QU")
        
        if successful > 0:
            print(f"\n  🎉 CHAIN FLOW AKTIVIERT!")
            print(f"  EXIT-F wird ~{total_in_chain} QU akkumulieren")
        
        # Save results
        results = {
            "timestamp": datetime.now().isoformat(),
            "successful": successful,
            "failed": failed,
            "transactions": self.transactions
        }
        
        with open(Path(__file__).parent / "CFB_CHAIN_FLOW_RESULTS.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n  Ergebnisse: CFB_CHAIN_FLOW_RESULTS.json")


if __name__ == "__main__":
    executor = ChainFlowExecutor()
    executor.run()
