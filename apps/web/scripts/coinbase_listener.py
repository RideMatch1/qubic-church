import requests
import json
import re
from pathlib import Path

# THE BITCOIN COINBASE LISTENER
# Scanning recent Bitcoin blocks for embedded messages in the Coinbase Transaction data.
# This is the primary channel for CFB/Team -> Anna communication.

def scan_coinbase_messages(blocks_to_scan=10):
    print(f"📡 SCANNING BITCOIN COINBASE MESSAGES (Last {blocks_to_scan} Blocks)...")
    print("-" * 65)
    
    try:
        # Get current height
        r = requests.get("https://blockstream.info/api/blocks/tip/height")
        tip = int(r.text.strip())
        
        for h in range(tip, tip - blocks_to_scan, -1):
            # Get block hash
            rb = requests.get(f"https://blockstream.info/api/block-height/{h}")
            b_hash = rb.text.strip()
            
            # Get block details (to find coinbase tx)
            rtx = requests.get(f"https://blockstream.info/api/block/{b_hash}/txs")
            txs = rtx.json()
            
            if not txs: continue
            
            # The Coinbase TX is always the first one (Index 0)
            coinbase_tx = txs[0]
            
            # Extract scriptSig (where miners put messages)
            vin = coinbase_tx.get('vin', [{}])[0]
            scriptsig_hex = vin.get('scriptsig', '')
            
            # Decode Hex
            try:
                raw_bytes = bytes.fromhex(scriptsig_hex)
                # Filter for readable ASCII
                message = "".join([chr(b) for b in raw_bytes if 32 <= b <= 126])
                
                # Highlight Signal Keywords
                prefix = "   "
                if any(kw in message.upper() for kw in ["QUBIC", "CFB", "ANNA", "JIGSAW", "SEED", "EPOCH"]):
                    prefix = "🔥 "
                if "F2Pool" in message: prefix = "⚡ " # F2Pool is often used for signals
                
                print(f"{prefix}Block {h} | Msg: [{message}]")
                
                # Check output addresses for potential CFB broadcasts
                for vout in coinbase_tx.get('vout', []):
                    addr = vout.get('scriptpubkey_address', 'N/A')
                    val = vout.get('value', 0)
                    # Large BTC movements from Coinbase might be signals too
                    
            except Exception as e:
                print(f"   Block {h} | Error decoding: {e}")
                
    except Exception as e:
        print(f"[X] API Error: {e}")

    print("\n[ANALYSIS] Messages like '/F2Pool/' are standard miner tags.")
    print("We are looking for 'Out of Place' strings or cryptographic salts.")

if __name__ == "__main__":
    scan_coinbase_messages(15)
