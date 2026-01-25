#!/usr/bin/env python3
"""
Scan Exit Key
=============

IMPORTANT: Uses CORRECTED coordinate transformation.
Anna coordinates (X, Y) -> matrix[row][col] via:
- col = (X + 64) % 128
- row = (63 - Y) % 128

EXIT at Anna(82, 39) -> matrix[24][18]
"""
import json
import hashlib
import math
import os

# Import correct coordinate transformation
try:
    from anna_matrix_utils import anna_to_matrix
except ImportError:
    def anna_to_matrix(x, y):
        col = (x + 64) % 128
        row = (63 - y) % 128
        return row, col

# Target: Bridge Exit at Anna(82, 39)
# CORRECTED: Convert to matrix indices
ANNA_EXIT_X, ANNA_EXIT_Y = 82, 39
TARGET_ROW, TARGET_COL = anna_to_matrix(ANNA_EXIT_X, ANNA_EXIT_Y)
# Result: TARGET_ROW = 24, TARGET_COL = 18

def get_coords(addr):
    h = hashlib.sha256(addr.encode()).digest()
    row = h[0] % 128
    col = h[1] % 128
    return row, col

def scan_keys_file():
    filepath = 'apps/web/public/data/bitcoin-private-keys.json'
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            records = data.get('records', [])
            
            print(f"Scanning {len(records)} keys for EXIT target Anna({ANNA_EXIT_X}, {ANNA_EXIT_Y}) -> matrix[{TARGET_ROW}][{TARGET_COL}]...")
            
            best_hit = None
            best_res = 0
            
            for rec in records:
                addr = rec['address']
                row, col = get_coords(addr)
                
                # Exit Logic
                dist = math.sqrt((row - TARGET_ROW)**2 + (col - TARGET_COL)**2)
                resonance = max(0, (1 - (dist / 100)) * 100)
                
                if resonance > best_res:
                    best_res = resonance
                    best_hit = rec
                    best_hit['row'] = row
                    best_hit['col'] = col
                    best_hit['resonance'] = resonance

                if row == TARGET_ROW and col == TARGET_COL:
                    print("\n[!!!] PERFECT HIT FOUND [!!!]")
                    print(json.dumps(rec, indent=2))
                    return

            print("\nSCAN COMPLETE.")
            if best_hit:
                print(f"Best Candidate: {best_hit['address']}")
                print(f"Coords: ({best_hit['row']}, {best_hit['col']})")
                print(f"Resonance: {best_hit['resonance']:.2f}%")
                print(f"Key: {best_hit['privateKeyHex']}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scan_keys_file()
