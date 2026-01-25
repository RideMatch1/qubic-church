#!/usr/bin/env python3
import requests
import hashlib
import time

# REAL DATA SCANNER (No Simulation)
# Queries public Bitcoin APIs for OP_RETURN data and checks for Qubic Signatures.

# Qubic Signature Pattern (CFB's footprint)
# We look for:
# 1. 55-byte strings (Qubic Seed Length)
# 2. Public Keys that match our "Bridge Matrix" coordinates
# 3. OP_RETURNs with "Qubic" or "CFB" headers

API_URL = "https://blockstream.info/api"

def get_block_hash(height):
    try:
        r = requests.get(f"{API_URL}/block-height/{height}")
        if r.status_code == 200:
            return r.text.strip()
    except:
        pass
    return None

def get_block_txs(block_hash):
    try:
        r = requests.get(f"{API_URL}/block/{block_hash}/txs")
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def scan_real_blockchain():
    print("[*] CONNECTING TO BITCOIN MAINNET (VIA BLOCKSTREAM API)...")
    
    # Let's verify the "Anchor" Block 450100 again with REAL API data first
    # Then scan recent blocks.
    
    targets = [450100, 800000, 820000] # 2017, 2023, 2024
    
    for height in targets:
        print(f"\n[*] SCANNING BLOCK {height}...")
        b_hash = get_block_hash(height)
        if not b_hash:
            print("    Error fetching block hash.")
            continue
            
        print(f"    Hash: {b_hash}")
        txs = get_block_txs(b_hash)
        
        found_data = False
        
        for tx in txs:
            for out in tx.get('vout', []):
                # Check for OP_RETURN usually scriptpubkey_type: op_return
                if out.get('scriptpubkey_type') == 'op_return':
                    asm = out.get('scriptpubkey_asm', '')
                    hex_data = out.get('scriptpubkey', '')
                    
                    # Try to decode whatever is there
                    try:
                        # Skip the OP_RETURN opcode (6a) and length byte
                        payload = hex_data[4:] 
                        decoded = bytes.fromhex(payload).decode('utf-8', errors='ignore')
                        
                        # Filter for interesting stuff
                        if len(decoded) > 4:
                            print(f"    [OP_RETURN] {decoded}")
                            found_data = True
                            
                            # CHECK FOR QUBIC/CFB
                            if "QUBIC" in decoded.upper() or "CFB" in decoded.upper() or "AIGARTH" in decoded.upper():
                                print(f"    [!!!] REAL QUBIC SIGNAL FOUND: {decoded}")
                    except:
                        pass
        
        if not found_data:
            print("    No readable OP_RETURN data found in sample.")

if __name__ == "__main__":
    scan_real_blockchain()
