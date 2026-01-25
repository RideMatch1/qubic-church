#!/usr/bin/env python3
"""
===============================================================================
              🔥 CFB FULL PROTOCOL - ALLE 4 SCHRITTE 🔥
===============================================================================

1. Monitor: Überwache alle 20 Nodes auf Aktivität
2. Private Keys analysieren: Entschlüssele die Keys an den Positionen
3. Chain Payload: Sende Signal durch ENTRY → Content → EXIT
4. Anna Query: Sende Anfrage an Anna-Bot

Author: The Bridge Architect
Date: 2026-01-24
===============================================================================
"""

import os
import sys
import json
import time
import base64
import hashlib
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

# Die 20 CFB-Puzzle Nodes
CFB_NODES = [
    {"pair": 1, "coords": [45, 92], "sum": 137, "identity": "VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH", "note": "ENTRY"},
    {"pair": 2, "coords": [3, 77], "sum": 80, "identity": "LISHDJGYQEQYWEEXJLNMYEQDYXSALKHFTFXESCSHGHAYAOLGZTHFCWCBRJVC"},
    {"pair": 3, "coords": [14, 58], "sum": 72, "identity": "MXCFUHIUQRVWUFCZEPXJCEIFFPWBULUXTITJTTMVPDRLDKIPWECENXSDFXXJ"},
    {"pair": 4, "coords": [29, 81], "sum": 110, "identity": "AWAABIBPQNGBZDMMIMWNMZDKBIOAHJYIZWQPMOPLSCFZXQVNEPIMUBKEKXJC"},
    {"pair": 5, "coords": [6, 33], "sum": 39, "identity": "DWQNESYCKKBXIGOJHQOEHUHMALBADTWFYKNKFRNKOEZYMPEZNJMUEPAFBROB", "note": "CORE"},
    {"pair": 6, "coords": [70, 48], "sum": 118, "identity": "CFAAYZNNZYOKRBJZYNSJSLIDMXICLHZBHXFKSXOZXESMCUHMLOIUJBBENVMH"},
    {"pair": 7, "coords": [95, 22], "sum": 117, "identity": "OIRGTWZESOJZHDVRCMQSJLMEQQBDZKTDRVOSITFRLCCKCWHCUPWYXXJHXXIE"},
    {"pair": 8, "coords": [61, 9], "sum": 70, "identity": "GODJAKZUXGDCUFTLKTCUXCNDBZGBZBZGXFSOQEGCMDCREPTFLMCVFGIAYTFK"},
    {"pair": 9, "coords": [84, 37], "sum": 121, "identity": "KGMVFUQSQQTYCCHYQRPOPFCCTHMBERWBOEEXRSNEPDWSFOIOGGXJDLJDHVIB", "note": "EXIT-Mitte"},
    {"pair": 10, "coords": [50, 16], "sum": 66, "identity": "KWSWPBOKROVYVEXYYZAOXUUILUCBOKUQBIFPOEEZDCKNBUNQNYLZKYZAGGTB"},
    {"pair": 11, "coords": [73, 28], "sum": 101, "identity": "KUFDFTNVSAJPBAVTGTOEERNSKLQCHCHUXFOSWFONUEOVTHUBVWWBNIODBSDI"},
    {"pair": 12, "coords": [85, 41], "sum": 126, "identity": "OYPEVSVUXVUKTCMESFQAEMLBWRHDRYYBUAYMHLLLYFUKEIEKQZHGRTAFMIJI"},
    {"pair": 13, "coords": [96, 7], "sum": 103, "identity": "AUAYEMNSRHDUFARJNNZYNIRGMMHBMOBOJAFZAYCPLGIDQQQQRNJFYLIHABVH"},
    {"pair": 14, "coords": [62, 19], "sum": 81, "identity": "QQJMQAVNCRLACDVDGNNCQXBHNPICLYGCFCDEJYZMMFAEWHHVZHRHPMAEHLCK"},
    {"pair": 15, "coords": [74, 30], "sum": 104, "identity": "HOWIXXQSALKMPFCOSKEYPOCGJQYBUWEHTIEREXNMUFTYKKQWCBJBPQDGSHDI"},
    {"pair": 16, "coords": [87, 43], "sum": 130, "identity": "TQXTTXTBFKMMHEWVBZZETVZSCOICNAUNHDFYNIIJMGMRZCNYUSZEXQCDTEKD"},
    {"pair": 17, "coords": [98, 5], "sum": 103, "identity": "RHGZDSPLKJBKOGTXOYMYDNWMZAWBLXIPSWEUQKXQGFNSUQXAPQTXOSAHVBZE"},
    {"pair": 18, "coords": [60, 15], "sum": 75, "identity": "EBDHSLAQBOKNMATKMAWQRTOABCCANQCDYLMZQNRTVANWMJPRVDYNMUTGXPJO"},
    {"pair": 19, "coords": [72, 27], "sum": 99, "identity": "XKQJUGHFIDINTBJYKJDRTKVLUOSCTTCEQNGFHDNIACFXPHYPLRZTFFBHGMDC"},
    {"pair": 20, "coords": [82, 39], "sum": 121, "identity": "RDFRUPFEUQKKMFQVNNUYUGMZXJLBIJTHYKMTQTJUIBKENWBKDFSTXYAEJHQI", "note": "EXIT-Final"},
]

# Bekannte Anna-Bot Adresse
ANNA_BOT = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFXIB"


class CFBFullProtocol:
    def __init__(self):
        self.seed_str = os.getenv("MASTER_SEED")
        if not self.seed_str:
            raise ValueError("MASTER_SEED nicht gefunden!")
        
        seed_bytes = self.seed_str.encode('utf-8')
        self.subseed = get_subseed_from_seed(seed_bytes)
        self.priv_key = get_private_key_from_subseed(self.subseed)
        self.pub_key = get_public_key_from_private_key(self.priv_key)
        self.source_identity = get_identity_from_public_key(self.pub_key)
        
        self.results = {"timestamp": datetime.now().isoformat()}
        self.log_file = Path(__file__).parent / f"CFB_PROTOCOL_LOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        
        # Load matrix cartography
        with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json', 'r') as f:
            self.cartography = json.load(f)

    def log(self, event: str, data: dict):
        entry = {"ts": datetime.now().isoformat(), "event": event, "data": data}
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def get_tick(self) -> int:
        r = requests.get(f"{RPC_URL}/v1/tick-info", timeout=TIMEOUT)
        return r.json().get('tickInfo', {}).get('tick', 0)

    def get_balance(self, identity: str) -> dict:
        try:
            r = requests.get(f"{RPC_URL}/v1/balances/{identity}", timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json().get('balance', {})
        except:
            pass
        return {}

    def send_tx(self, dest_identity: str, amount: int) -> dict:
        """Send transaction."""
        try:
            current_tick = self.get_tick()
            target_tick = current_tick + 10
            dest_pub_key = get_public_key_from_identity(dest_identity)
            
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
                return {"success": True, "tx_id": tx_id, "tick": target_tick, "amount": amount}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # STEP 1: MONITOR - Check all 20 nodes for activity
    # =========================================================================
    def step1_monitor(self):
        print("\n" + "="*70)
        print("STEP 1: MONITOR - Überwache alle 20 CFB-Puzzle Nodes")
        print("="*70)
        
        status = []
        for node in CFB_NODES:
            balance = self.get_balance(node["identity"])
            info = {
                "pair": node["pair"],
                "coords": node["coords"],
                "identity": node["identity"][:20] + "...",
                "balance": int(balance.get("balance", 0)),
                "incoming_tx": int(balance.get("numberOfIncomingTransfers", 0)),
                "outgoing_tx": int(balance.get("numberOfOutgoingTransfers", 0)),
                "last_incoming_tick": balance.get("latestIncomingTransferTick", 0),
                "note": node.get("note", "")
            }
            status.append(info)
            
            mark = "⭐" if node.get("note") else "○"
            print(f"  {mark} Paar {node['pair']:2d}: Balance={info['balance']:4d} QU, IN={info['incoming_tx']}, OUT={info['outgoing_tx']} {node.get('note', '')}")
            time.sleep(0.2)
        
        self.results["step1_monitor"] = status
        self.log("MONITOR_COMPLETE", {"nodes_checked": 20})
        return status

    # =========================================================================
    # STEP 2: ANALYZE PRIVATE KEYS - Extract messages from keys
    # =========================================================================
    def step2_analyze_keys(self):
        print("\n" + "="*70)
        print("STEP 2: PRIVATE KEY ANALYSE")
        print("="*70)
        
        keys_data = []
        all_key_bytes = b""
        
        for node in CFB_NODES:
            row, col = node["coords"]
            key_lookup = f"{row},{col}"
            
            if key_lookup in self.cartography:
                privkey_hex = self.cartography[key_lookup]
                privkey_bytes = bytes.fromhex(privkey_hex)
                all_key_bytes += privkey_bytes
                
                # Analyze key
                ascii_chars = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in privkey_bytes[:16])
                
                keys_data.append({
                    "pair": node["pair"],
                    "coords": node["coords"],
                    "key_preview": privkey_hex[:32] + "...",
                    "ascii_preview": ascii_chars,
                    "sum_bytes": sum(privkey_bytes),
                    "xor_bytes": self._xor_reduce(privkey_bytes)
                })
                
                print(f"  Paar {node['pair']:2d}: {privkey_hex[:24]}... -> '{ascii_chars}'")
        
        # Combined analysis
        print("\n  KOMBINIERTE KEY-ANALYSE:")
        
        # XOR all keys together
        combined_xor = [0] * 32
        for node in CFB_NODES:
            row, col = node["coords"]
            key_lookup = f"{row},{col}"
            if key_lookup in self.cartography:
                key_bytes = bytes.fromhex(self.cartography[key_lookup])
                for i in range(min(32, len(key_bytes))):
                    combined_xor[i] ^= key_bytes[i]
        
        xor_hex = bytes(combined_xor).hex()
        xor_ascii = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in combined_xor)
        print(f"  XOR aller Keys: {xor_hex[:32]}...")
        print(f"  XOR als ASCII:  '{xor_ascii}'")
        
        # Hash of all keys
        all_keys_hash = hashlib.sha256(all_key_bytes).hexdigest()
        print(f"  SHA256 aller Keys: {all_keys_hash[:32]}...")
        
        self.results["step2_keys"] = {
            "keys_analyzed": len(keys_data),
            "combined_xor_hex": xor_hex,
            "combined_xor_ascii": xor_ascii,
            "all_keys_sha256": all_keys_hash,
            "individual_keys": keys_data
        }
        self.log("KEYS_ANALYZED", {"count": len(keys_data)})
        return keys_data

    def _xor_reduce(self, data: bytes) -> int:
        result = 0
        for b in data:
            result ^= b
        return result

    # =========================================================================
    # STEP 3: CHAIN PAYLOAD - Send signal through ENTRY → Content → EXIT
    # =========================================================================
    def step3_chain_payload(self):
        print("\n" + "="*70)
        print("STEP 3: CHAIN PAYLOAD - Signal durch das Netzwerk")
        print("="*70)
        
        # Wir senden an jeden Node einen Betrag der der Pair-Nummer entspricht
        # Das erzeugt ein erkennbares Muster: 1, 2, 3, 4, 5, ... 20 QU
        
        transactions = []
        
        print(f"\n  Sende Signatur-Pattern durch alle 20 Nodes...")
        print(f"  Pattern: Paar N bekommt N QU (1-20)\n")
        
        for node in CFB_NODES:
            pair_num = node["pair"]
            amount = pair_num  # 1 QU für Paar 1, 2 QU für Paar 2, etc.
            
            print(f"  [{pair_num:2d}/20] -> {node['identity'][:20]}... ({amount} QU) ", end="", flush=True)
            
            result = self.send_tx(node["identity"], amount)
            
            if result.get("success"):
                print(f"✓ TX: {result['tx_id'][:16]}...")
                transactions.append({
                    "pair": pair_num,
                    "amount": amount,
                    "tx_id": result["tx_id"],
                    "tick": result["tick"],
                    "success": True
                })
            else:
                print(f"✗ {result.get('error', 'unknown')[:30]}")
                transactions.append({
                    "pair": pair_num,
                    "amount": amount,
                    "success": False,
                    "error": result.get("error")
                })
            
            time.sleep(0.5)
        
        successful = sum(1 for t in transactions if t.get("success"))
        total_sent = sum(t["amount"] for t in transactions if t.get("success"))
        
        print(f"\n  Erfolgreich: {successful}/20")
        print(f"  Total gesendet: {total_sent} QU (erwartet: 210 QU)")
        
        self.results["step3_chain"] = {
            "successful": successful,
            "total_sent": total_sent,
            "transactions": transactions
        }
        self.log("CHAIN_PAYLOAD_SENT", {"successful": successful, "total": total_sent})
        return transactions

    # =========================================================================
    # STEP 4: ANNA QUERY - Send query to Anna-Bot
    # =========================================================================
    def step4_anna_query(self):
        print("\n" + "="*70)
        print("STEP 4: ANNA QUERY - Anfrage an Anna-Bot")
        print("="*70)
        
        # Sende spezielle Beträge die eine Nachricht kodieren
        # 137 QU = ENTRY Summe (Feinstrukturkonstante)
        # Dies signalisiert: "Ich habe das CFB-Puzzle gelöst"
        
        print(f"\n  Anna-Bot Adresse: {ANNA_BOT}")
        print(f"  Sende 137 QU (α⁻¹ = Feinstrukturkonstante) als Signal...")
        
        result = self.send_tx(ANNA_BOT, 137)
        
        if result.get("success"):
            print(f"  ✓ TX gesendet: {result['tx_id']}")
            print(f"  ✓ Tick: {result['tick']}")
        else:
            print(f"  ✗ Fehler: {result.get('error')}")
        
        self.results["step4_anna"] = {
            "target": ANNA_BOT,
            "amount": 137,
            "result": result
        }
        self.log("ANNA_QUERY_SENT", result)
        return result

    # =========================================================================
    # RUN ALL
    # =========================================================================
    def run_all(self):
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ██████╗███████╗██████╗     ███████╗██╗   ██╗██╗     ██╗                 ║
║  ██╔════╝██╔════╝██╔══██╗    ██╔════╝██║   ██║██║     ██║                 ║
║  ██║     █████╗  ██████╔╝    █████╗  ██║   ██║██║     ██║                 ║
║  ██║     ██╔══╝  ██╔══██╗    ██╔══╝  ██║   ██║██║     ██║                 ║
║  ╚██████╗██║     ██████╔╝    ██║     ╚██████╔╝███████╗███████╗            ║
║   ╚═════╝╚═╝     ╚═════╝     ╚═╝      ╚═════╝ ╚══════╝╚══════╝            ║
║                                                                           ║
║              🔥 FULL PROTOCOL - ALLE 4 SCHRITTE 🔥                        ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)
        
        print(f"Source Wallet: {self.source_identity}")
        balance = self.get_balance(self.source_identity)
        print(f"Balance: {int(balance.get('balance', 0)):,} QU")
        print(f"Log: {self.log_file}")
        
        # Execute all steps
        self.step1_monitor()
        self.step2_analyze_keys()
        self.step3_chain_payload()
        self.step4_anna_query()
        
        # Final summary
        print("\n" + "="*70)
        print("ZUSAMMENFASSUNG - FULL PROTOCOL COMPLETE")
        print("="*70)
        
        print(f"""
  ✓ Step 1: Monitor - 20 Nodes überprüft
  ✓ Step 2: Keys - {self.results['step2_keys']['keys_analyzed']} Private Keys analysiert
  ✓ Step 3: Chain - {self.results['step3_chain']['successful']}/20 Transaktionen, {self.results['step3_chain']['total_sent']} QU
  ✓ Step 4: Anna - Query gesendet ({self.results['step4_anna']['result'].get('success', False)})
  
  Total QU gesendet: {self.results['step3_chain']['total_sent'] + 137} QU
  
  XOR aller Keys: {self.results['step2_keys']['combined_xor_ascii']}
        """)
        
        # Save results
        with open(Path(__file__).parent / "CFB_FULL_PROTOCOL_RESULTS.json", 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"Ergebnisse gespeichert in CFB_FULL_PROTOCOL_RESULTS.json")
        return self.results


if __name__ == "__main__":
    protocol = CFBFullProtocol()
    protocol.run_all()
