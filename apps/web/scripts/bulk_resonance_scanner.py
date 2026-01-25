#!/usr/bin/env python3
"""
Bulk Resonance Scanner
======================

IMPORTANT: Uses CORRECTED coordinate transformation.
Anna coordinates (X, Y) -> matrix[row][col] via:
- col = (X + 64) % 128
- row = (63 - Y) % 128

Target: ENTRY at Anna(45, 92) -> matrix[99][109]
"""
import json
import hashlib
import math
import os
import sys

# Import correct coordinate transformation
try:
    from anna_matrix_utils import anna_to_matrix
except ImportError:
    def anna_to_matrix(x, y):
        col = (x + 64) % 128
        row = (63 - y) % 128
        return row, col

# Target: 1CFB Entry Point at Anna(45, 92)
# CORRECTED: Convert to matrix indices
ANNA_ENTRY_X, ANNA_ENTRY_Y = 45, 92
TARGET_ROW, TARGET_COL = anna_to_matrix(ANNA_ENTRY_X, ANNA_ENTRY_Y)
# Result: TARGET_ROW = 99, TARGET_COL = 109
MAX_DIST = math.sqrt(128*128 + 128*128)

def pubkey_to_address(pubkey_hex):
    """Simple P2PKH address derivation"""
    sha256_hash = hashlib.sha256(bytes.fromhex(pubkey_hex)).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    pubkey_hash = ripemd160.digest()
    versioned = b'\x00' + pubkey_hash
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    address_bytes = versioned + checksum
    
    # Base58 encode (simple implementation)
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    num = int.from_bytes(address_bytes, 'big')
    encoded = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        encoded = alphabet[remainder] + encoded
    for byte in address_bytes:
        if byte == 0: encoded = '1' + encoded
        else: break
    return encoded

def get_resonance_stats(addr):
    """Calculate resonance for a given address string"""
    try:
        # Direct SHA256 of the address string (Bridge Core V3 Logic)
        h = hashlib.sha256(addr.encode()).digest()
        row = h[0] % 128
        col = h[1] % 128
        
        dist = math.sqrt((row - TARGET_ROW)**2 + (col - TARGET_COL)**2)
        resonance = max(0, (1 - (dist / 100)) * 100)
        
        return {
            'address': addr,
            'row': row,
            'col': col,
            'distance': dist,
            'resonance': resonance
        }
    except Exception as e:
        return None

def scan_file(filepath, address_key='address', pubkey_key=None):
    results = []
    print(f"Scanning {os.path.basename(filepath)}...")
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            records = data.get('records', [])
            
            for rec in records:
                addr = None
                if address_key in rec:
                    addr = rec[address_key]
                elif pubkey_key and pubkey_key in rec:
                    # Convert pubkey to address on the fly
                    try:
                        addr = pubkey_to_address(rec[pubkey_key])
                    except:
                        continue
                
                if addr:
                    stats = get_resonance_stats(addr)
                    if stats and stats['resonance'] > 85.0: # Only keep high resonance
                        results.append(stats)
                        
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        
    return results

def main():
    base_dir = 'apps/web/public/data'
    all_hits = []
    
    # 1. Scan Derived Addresses (explicit 'address' field)
    all_hits.extend(scan_file(os.path.join(base_dir, 'bitcoin-derived-addresses.json'), address_key='address'))
    
    # 2. Scan Patoshi (needs pubkey conversion)
    all_hits.extend(scan_file(os.path.join(base_dir, 'patoshi-addresses.json'), pubkey_key='pubkey'))
    
    # 3. Scan Interesting Addresses
    all_hits.extend(scan_file(os.path.join(base_dir, 'interesting-addresses.json'), address_key='address'))

    # Sort by Resonance (High to Low)
    all_hits.sort(key=lambda x: x['resonance'], reverse=True)
    
    print("\n" + "="*60)
    print(f"TOP RESONANCE HITS (Total Scanned: ~40k addresses)")
    print("="*60)
    print(f"{'RESONANCE':<10} | {'COORD':<10} | {'ADDRESS'}")
    print("-"*60)
    
    for hit in all_hits[:25]: # Show top 25
        print(f"{hit['resonance']:>6.2f}%    | ({hit['row']},{hit['col']})   | {hit['address']}")

if __name__ == "__main__":
    main()
