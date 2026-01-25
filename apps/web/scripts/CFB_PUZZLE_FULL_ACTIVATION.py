#!/usr/bin/env python3
"""
===============================================================================
              🔥 CFB PUZZLE - VOLLSTÄNDIGE AKTIVIERUNG ALLER 20 NODES 🔥
===============================================================================

Das CFB-Puzzle enthält 20 Koordinatenpaare, die auf 20 Qubic IDs in der
Anna-Matrix zeigen. 2 sind bereits aktiv (ENTRY + CORE), 18 warten auf
Aktivierung.

Dieses Script sendet 1 QU an jede inaktive ID um sie zu aktivieren.

Author: The Bridge Architect
Date: 2026-01-24
===============================================================================
"""

import os
import sys
import json
import time
import base64
from pathlib import Path
from datetime import datetime

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

load_dotenv('/Users/lukashertle/Developer/projects/qubic-academic-docs/.env')

RPC_URL = "https://rpc.qubic.org"
TIMEOUT = 15

# Die 20 CFB-Puzzle IDs (aus CFB_ALL_20_IDENTITIES.json)
CFB_PUZZLE_IDS = [
    {"pair": 1, "coords": [45, 92], "sum": 137, "identity": "VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH", "note": "ENTRY"},
    {"pair": 2, "coords": [3, 77], "sum": 80, "identity": "LISHDJGYQEQYWEEXJLNMYEQDYXSALKHFTFXESCSHGHAYAOLGZTHFCWCBRJVC", "note": ""},
    {"pair": 3, "coords": [14, 58], "sum": 72, "identity": "MXCFUHIUQRVWUFCZEPXJCEIFFPWBULUXTITJTTMVPDRLDKIPWECENXSDFXXJ", "note": ""},
    {"pair": 4, "coords": [29, 81], "sum": 110, "identity": "AWAABIBPQNGBZDMMIMWNMZDKBIOAHJYIZWQPMOPLSCFZXQVNEPIMUBKEKXJC", "note": ""},
    {"pair": 5, "coords": [6, 33], "sum": 39, "identity": "DWQNESYCKKBXIGOJHQOEHUHMALBADTWFYKNKFRNKOEZYMPEZNJMUEPAFBROB", "note": "CORE"},
    {"pair": 6, "coords": [70, 48], "sum": 118, "identity": "CFAAYZNNZYOKRBJZYNSJSLIDMXICLHZBHXFKSXOZXESMCUHMLOIUJBBENVMH", "note": ""},
    {"pair": 7, "coords": [95, 22], "sum": 117, "identity": "OIRGTWZESOJZHDVRCMQSJLMEQQBDZKTDRVOSITFRLCCKCWHCUPWYXXJHXXIE", "note": ""},
    {"pair": 8, "coords": [61, 9], "sum": 70, "identity": "GODJAKZUXGDCUFTLKTCUXCNDBZGBZBZGXFSOQEGCMDCREPTFLMCVFGIAYTFK", "note": ""},
    {"pair": 9, "coords": [84, 37], "sum": 121, "identity": "KGMVFUQSQQTYCCHYQRPOPFCCTHMBERWBOEEXRSNEPDWSFOIOGGXJDLJDHVIB", "note": "EXIT-Mitte"},
    {"pair": 10, "coords": [50, 16], "sum": 66, "identity": "KWSWPBOKROVYVEXYYZAOXUUILUCBOKUQBIFPOEEZDCKNBUNQNYLZKYZAGGTB", "note": ""},
    {"pair": 11, "coords": [73, 28], "sum": 101, "identity": "KUFDFTNVSAJPBAVTGTOEERNSKLQCHCHUXFOSWFONUEOVTHUBVWWBNIODBSDI", "note": ""},
    {"pair": 12, "coords": [85, 41], "sum": 126, "identity": "OYPEVSVUXVUKTCMESFQAEMLBWRHDRYYBUAYMHLLLYFUKEIEKQZHGRTAFMIJI", "note": ""},
    {"pair": 13, "coords": [96, 7], "sum": 103, "identity": "AUAYEMNSRHDUFARJNNZYNIRGMMHBMOBOJAFZAYCPLGIDQQQQRNJFYLIHABVH", "note": ""},
    {"pair": 14, "coords": [62, 19], "sum": 81, "identity": "QQJMQAVNCRLACDVDGNNCQXBHNPICLYGCFCDEJYZMMFAEWHHVZHRHPMAEHLCK", "note": ""},
    {"pair": 15, "coords": [74, 30], "sum": 104, "identity": "HOWIXXQSALKMPFCOSKEYPOCGJQYBUWEHTIEREXNMUFTYKKQWCBJBPQDGSHDI", "note": ""},
    {"pair": 16, "coords": [87, 43], "sum": 130, "identity": "TQXTTXTBFKMMHEWVBZZETVZSCOICNAUNHDFYNIIJMGMRZCNYUSZEXQCDTEKD", "note": ""},
    {"pair": 17, "coords": [98, 5], "sum": 103, "identity": "RHGZDSPLKJBKOGTXOYMYDNWMZAWBLXIPSWEUQKXQGFNSUQXAPQTXOSAHVBZE", "note": ""},
    {"pair": 18, "coords": [60, 15], "sum": 75, "identity": "EBDHSLAQBOKNMATKMAWQRTOABCCANQCDYLMZQNRTVANWMJPRVDYNMUTGXPJO", "note": ""},
    {"pair": 19, "coords": [72, 27], "sum": 99, "identity": "XKQJUGHFIDINTBJYKJDRTKVLUOSCTTCEQNGFHDNIACFXPHYPLRZTFFBHGMDC", "note": ""},
    {"pair": 20, "coords": [82, 39], "sum": 121, "identity": "RDFRUPFEUQKKMFQVNNUYUGMZXJLBIJTHYKMTQTJUIBKENWBKDFSTXYAEJHQI", "note": "EXIT-Final"},
]


class CFBPuzzleActivator:
    """Aktiviert alle 20 CFB-Puzzle Nodes."""

    def __init__(self):
        self.seed_str = os.getenv("MASTER_SEED")
        if not self.seed_str:
            raise ValueError("MASTER_SEED nicht in .env gefunden!")

        self.log_file = Path(__file__).parent / f"CFB_ACTIVATION_LOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        self.transactions = []
        self.results = []

        # Derive keys
        seed_bytes = self.seed_str.encode('utf-8')
        self.subseed = get_subseed_from_seed(seed_bytes)
        self.priv_key = get_private_key_from_subseed(self.subseed)
        self.pub_key = get_public_key_from_private_key(self.priv_key)
        self.source_identity = get_identity_from_public_key(self.pub_key)

    def log(self, event: str, data: dict):
        """Log event."""
        entry = {"timestamp": datetime.now().isoformat(), "event": event, "data": data}
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def get_tick(self) -> int:
        """Get current tick."""
        r = requests.get(f"{RPC_URL}/v1/tick-info", timeout=TIMEOUT)
        return r.json().get('tickInfo', {}).get('tick', 0)

    def get_balance(self, identity: str) -> dict:
        """Get balance info."""
        try:
            r = requests.get(f"{RPC_URL}/v1/balances/{identity}", timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json().get('balance', {})
        except:
            pass
        return {}

    def check_if_active(self, identity: str) -> bool:
        """Check if identity has incoming transactions."""
        balance = self.get_balance(identity)
        return int(balance.get("numberOfIncomingTransfers", 0)) > 0

    def send_activation(self, identity: str, amount: int, pair_num: int, coords: list) -> dict:
        """Send activation transaction."""
        try:
            current_tick = self.get_tick()
            target_tick = current_tick + 10

            dest_pub_key = get_public_key_from_identity(identity)

            tx_data = bytearray(80)
            tx_data[0:32] = self.pub_key
            tx_data[32:64] = dest_pub_key
            tx_data[64:72] = amount.to_bytes(8, byteorder='little')
            tx_data[72:76] = target_tick.to_bytes(4, byteorder='little')
            tx_data[76:78] = (0).to_bytes(2, byteorder='little')
            tx_data[78:80] = (0).to_bytes(2, byteorder='little')

            digest = kangaroo_twelve(bytes(tx_data), 80, 32)
            signature = sign(self.subseed, self.pub_key, digest)
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
                result = {
                    "success": True,
                    "pair": pair_num,
                    "coords": coords,
                    "identity": identity,
                    "amount": amount,
                    "tx_id": tx_id,
                    "tick": target_tick,
                    "time": datetime.now().isoformat()
                }
                self.transactions.append(result)
                self.log("TX_SENT", result)
                return result
            else:
                return {"success": False, "error": resp.text, "pair": pair_num}

        except Exception as e:
            return {"success": False, "error": str(e), "pair": pair_num}

    def run(self, dry_run: bool = False):
        """Execute full activation sequence."""
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ██████╗███████╗██████╗     ██████╗ ██╗   ██╗███████╗███████╗██╗     ███████╗ ║
║  ██╔════╝██╔════╝██╔══██╗    ██╔══██╗██║   ██║╚══███╔╝╚══███╔╝██║     ██╔════╝ ║
║  ██║     █████╗  ██████╔╝    ██████╔╝██║   ██║  ███╔╝   ███╔╝ ██║     █████╗   ║
║  ██║     ██╔══╝  ██╔══██╗    ██╔═══╝ ██║   ██║ ███╔╝   ███╔╝  ██║     ██╔══╝   ║
║  ╚██████╗██║     ██████╔╝    ██║     ╚██████╔╝███████╗███████╗███████╗███████╗ ║
║   ╚═════╝╚═╝     ╚═════╝     ╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝ ║
║                                                                           ║
║              🔥 FULL ACTIVATION - ALL 20 CFB PUZZLE NODES 🔥               ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)

        print(f"Source Wallet: {self.source_identity}")
        source_balance = self.get_balance(self.source_identity)
        print(f"Balance: {int(source_balance.get('balance', 0)):,} QU")
        print(f"Log File: {self.log_file}")
        print()

        # Check current status
        print("=" * 70)
        print("PHASE 1: STATUS CHECK")
        print("=" * 70)

        active_ids = []
        inactive_ids = []

        for node in CFB_PUZZLE_IDS:
            is_active = self.check_if_active(node["identity"])
            status = "AKTIV" if is_active else "INAKTIV"
            mark = "✓" if is_active else "○"

            if is_active:
                active_ids.append(node)
            else:
                inactive_ids.append(node)

            print(f"  {mark} Paar {node['pair']:2d}: ({node['coords'][0]:2d}, {node['coords'][1]:2d}) = {node['sum']:3d} -> {status} {node['note']}")
            time.sleep(0.2)

        print()
        print(f"Aktiv: {len(active_ids)}/20")
        print(f"Inaktiv: {len(inactive_ids)}/20")

        if len(inactive_ids) == 0:
            print("\n✓ ALLE 20 CFB-PUZZLE NODES SIND BEREITS AKTIV!")
            return

        # Confirm
        print()
        print("=" * 70)
        print("PHASE 2: AKTIVIERUNG")
        print("=" * 70)
        print(f"\n{len(inactive_ids)} Nodes werden mit je 1 QU aktiviert.")
        print(f"Gesamtkosten: {len(inactive_ids)} QU")

        if dry_run:
            print("\n[DRY RUN] Keine Transaktionen werden gesendet.")
            return

        input("\nDrücke ENTER um zu starten (oder Ctrl+C zum Abbrechen)...")

        # Execute
        print("\nSende Transaktionen...\n")

        successful = 0
        failed = 0

        for i, node in enumerate(inactive_ids, 1):
            print(f"[{i}/{len(inactive_ids)}] Paar {node['pair']}: ({node['coords'][0]}, {node['coords'][1]}) -> ", end="", flush=True)

            result = self.send_activation(
                identity=node["identity"],
                amount=1,
                pair_num=node["pair"],
                coords=node["coords"]
            )

            if result.get("success"):
                print(f"✓ TX: {result['tx_id'][:20]}...")
                successful += 1
            else:
                print(f"✗ FEHLER: {result.get('error', 'unknown')}")
                failed += 1

            self.results.append(result)
            time.sleep(0.5)  # Rate limiting

        # Summary
        print()
        print("=" * 70)
        print("ZUSAMMENFASSUNG")
        print("=" * 70)
        print(f"Erfolgreich: {successful}")
        print(f"Fehlgeschlagen: {failed}")
        print(f"Log: {self.log_file}")

        # Save results
        output = {
            "timestamp": datetime.now().isoformat(),
            "source": self.source_identity,
            "total_sent": successful,
            "failed": failed,
            "transactions": self.transactions
        }

        with open(Path(__file__).parent / "CFB_ACTIVATION_RESULTS.json", 'w') as f:
            json.dump(output, f, indent=2)

        print("\nErgebnisse gespeichert in CFB_ACTIVATION_RESULTS.json")

        if successful > 0:
            print(f"\n🎉 {successful} CFB-PUZZLE NODES AKTIVIERT! 🎉")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Nur Status anzeigen, keine Transaktionen")
    args = parser.parse_args()

    activator = CFBPuzzleActivator()
    activator.run(dry_run=args.dry_run)
