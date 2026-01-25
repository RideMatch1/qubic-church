#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    1CFB ADDRESS INVESTIGATION                                  ║
║                                                                                ║
║  Deep analysis of 1CFB prefix addresses and their matrix correlations         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
import requests
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import time

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

# Blockchain API
MEMPOOL_API = "https://mempool.space/api"
BLOCKCHAIR_API = "https://api.blockchair.com/bitcoin"

# Known 1CFB addresses
CFB_ADDRESSES = [
    "1CFBhVCZsrwKSZMHcFcjvBDYsHzMkPJjRT",  # The signature address
]

# Genesis and comparison addresses
GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
BLOCK1_ADDRESS = "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"

CFB_NUMBERS = [27, 37, 42, 127, 576]
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def base58_decode(s: str) -> bytes:
    num = 0
    for char in s:
        num = num * 58 + BASE58_ALPHABET.index(char)
    result = []
    while num > 0:
        result.append(num % 256)
        num //= 256
    for char in s:
        if char == '1':
            result.append(0)
        else:
            break
    return bytes(reversed(result))

class Matrix:
    def __init__(self):
        with open(MATRIX_FILE, 'r') as f:
            data = json.load(f)
        self.data = data['matrix']

    def query(self, row: int, col: int) -> Optional[int]:
        v = self.data[row % 128][col % 128]
        return v if isinstance(v, int) else None

def is_cfb_related(value: Optional[int]) -> bool:
    if value is None:
        return False
    return value in CFB_NUMBERS or -value in CFB_NUMBERS

# ═══════════════════════════════════════════════════════════════════════════════
# CFB ADDRESS ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

class CFBInvestigator:
    def __init__(self):
        print("═" * 70)
        print("           1CFB ADDRESS INVESTIGATION")
        print("═" * 70)
        self.matrix = Matrix()
        self.discoveries = []

    def log_discovery(self, title: str, data: dict):
        self.discoveries.append({'title': title, 'data': data})
        print(f"\n  ★★★ DISCOVERY: {title}")
        for k, v in data.items():
            print(f"      {k}: {v}")

    def analyze_address_structure(self, address: str, name: str):
        """Deep structure analysis"""
        print(f"\n{'─'*70}")
        print(f"Analyzing: {name}")
        print(f"Address: {address}")
        print("─"*70)

        decoded = base58_decode(address)
        hash160 = decoded[1:21]

        print(f"\nHash160: {hash160.hex()}")
        print(f"Length: {len(hash160)} bytes")

        # Byte-by-byte matrix mapping
        print("\nByte → Matrix analysis:")
        cfb_hits = []
        values = []

        for i, byte in enumerate(hash160):
            # Method 1: byte as row, position as col
            v1 = self.matrix.query(byte % 128, i % 128)
            # Method 2: byte pairs
            if i < 19:
                v2 = self.matrix.query(hash160[i] % 128, hash160[i+1] % 128)
            else:
                v2 = None

            values.append(v1)

            cfb_marker = ""
            if is_cfb_related(v1):
                cfb_marker = " ★ CFB"
                cfb_hits.append((i, byte, v1))

            val_str = f"{v1:+4d}" if v1 is not None else "None"
            print(f"  Byte {i:2d}: 0x{byte:02x} ({byte:3d}) → [{byte%128:3d},{i%128:3d}] = {val_str}{cfb_marker}")

        if cfb_hits:
            print(f"\n  CFB HITS: {len(cfb_hits)}")
            for i, byte, v in cfb_hits:
                self.log_discovery(f"{name} byte {i} gives CFB", {
                    'byte_index': i,
                    'byte_value': byte,
                    'matrix_value': v
                })

        # XOR analysis
        xor_all = 0
        for b in hash160:
            xor_all ^= b
        print(f"\nXOR of all bytes: {xor_all}")
        if xor_all in CFB_NUMBERS:
            self.log_discovery(f"{name} XOR gives CFB", {'xor': xor_all})

        # Sum analysis
        sum_all = sum(hash160)
        print(f"Sum of all bytes: {sum_all}")
        print(f"Sum mod 27: {sum_all % 27}")
        print(f"Sum mod 37: {sum_all % 37}")
        print(f"Sum mod 127: {sum_all % 127}")

        return hash160, values

    def compare_addresses(self, addr1: str, name1: str, addr2: str, name2: str):
        """Compare two addresses for patterns"""
        print(f"\n{'═'*70}")
        print(f"COMPARING: {name1} vs {name2}")
        print("═"*70)

        h1 = base58_decode(addr1)[1:21]
        h2 = base58_decode(addr2)[1:21]

        # XOR comparison
        xor = bytes(a ^ b for a, b in zip(h1, h2))
        print(f"\nXOR result: {xor.hex()}")

        # Check each XOR byte
        print("\nXOR byte analysis:")
        cfb_xor_bytes = []
        for i, b in enumerate(xor):
            marker = ""
            if b in CFB_NUMBERS:
                marker = " ★★★ CFB NUMBER!"
                cfb_xor_bytes.append((i, b))
            elif b == 0:
                marker = " (identical)"
            print(f"  Byte {i:2d}: {b:3d} (0x{b:02x}){marker}")

        if cfb_xor_bytes:
            self.log_discovery(f"XOR of {name1} and {name2} contains CFB", {
                'cfb_bytes': cfb_xor_bytes
            })

        # Difference analysis
        print("\nByte differences:")
        for i, (a, b) in enumerate(zip(h1, h2)):
            diff = (a - b) % 256
            if diff in CFB_NUMBERS or (256 - diff) in CFB_NUMBERS:
                print(f"  Byte {i}: diff = {diff} ★ CFB related")
                self.log_discovery(f"Byte {i} difference is CFB related", {
                    'index': i,
                    'diff': diff
                })

    def analyze_address_as_seed(self, address: str, name: str):
        """Treat address as potential Qubic-style seed"""
        print(f"\n{'─'*70}")
        print(f"ADDRESS AS SEED: {name}")
        print("─"*70)

        # The "1CFB" prefix might be significant
        prefix = address[:4]
        print(f"\nPrefix: {prefix}")

        # Each character position
        positions = [BASE58_ALPHABET.index(c) for c in address]
        print(f"Base58 positions: {positions[:10]}...")

        # Look for patterns
        print("\nPosition patterns:")
        print(f"  Sum of positions: {sum(positions)}")
        print(f"  Sum mod 27: {sum(positions) % 27}")
        print(f"  Sum mod 128: {sum(positions) % 128}")

        # XOR of positions
        xor = 0
        for p in positions:
            xor ^= p
        print(f"  XOR of positions: {xor}")

        if xor in CFB_NUMBERS:
            self.log_discovery(f"{name} position XOR is CFB", {'xor': xor})

        # Adjacent position XORs
        print("\n  Adjacent XORs giving CFB:")
        for i in range(len(positions) - 1):
            x = positions[i] ^ positions[i+1]
            if x in CFB_NUMBERS:
                print(f"    pos[{i}] XOR pos[{i+1}] = {positions[i]} XOR {positions[i+1]} = {x}")
                self.log_discovery(f"{name} adjacent XOR at {i} is CFB", {
                    'index': i,
                    'values': (positions[i], positions[i+1]),
                    'xor': x
                })

    def investigate_cfb_signature(self):
        """Deep dive into the CFB signature address"""
        print(f"\n{'═'*70}")
        print("1CFB SIGNATURE ADDRESS SPECIAL ANALYSIS")
        print("═"*70)

        addr = CFB_ADDRESSES[0]
        print(f"\nAddress: {addr}")
        print(f"Length: {len(addr)}")

        # The "1CFB" prefix
        print("\n'1CFB' prefix analysis:")
        for i, c in enumerate(addr[:4]):
            pos = BASE58_ALPHABET.index(c)
            print(f"  '{c}': position {pos}")

        prefix_positions = [BASE58_ALPHABET.index(c) for c in addr[:4]]
        print(f"  Prefix positions: {prefix_positions}")
        print(f"  Prefix sum: {sum(prefix_positions)}")
        print(f"  Prefix XOR: {prefix_positions[0] ^ prefix_positions[1] ^ prefix_positions[2] ^ prefix_positions[3]}")

        # The rest after "1CFB"
        suffix = addr[4:]
        print(f"\nSuffix (after 1CFB): {suffix}")

        suffix_hash = hashlib.sha256(suffix.encode()).digest()
        row, col = suffix_hash[0] % 128, suffix_hash[1] % 128
        value = self.matrix.query(row, col)
        print(f"  Suffix SHA256 → [{row},{col}] = {value}")

        if is_cfb_related(value):
            self.log_discovery("1CFB suffix hash gives CFB", {'value': value})

        # Character frequency
        print("\nCharacter frequency in address:")
        freq = {}
        for c in addr:
            freq[c] = freq.get(c, 0) + 1
        for c, count in sorted(freq.items(), key=lambda x: -x[1])[:10]:
            print(f"  '{c}': {count}")

    def run_investigation(self):
        """Run full investigation"""

        # Analyze CFB address
        self.analyze_address_structure(CFB_ADDRESSES[0], "1CFB Signature")

        # Analyze as seed
        self.analyze_address_as_seed(CFB_ADDRESSES[0], "1CFB Signature")

        # Compare with Genesis
        self.compare_addresses(CFB_ADDRESSES[0], "1CFB", GENESIS_ADDRESS, "Genesis")

        # Compare with Block 1
        self.compare_addresses(CFB_ADDRESSES[0], "1CFB", BLOCK1_ADDRESS, "Block 1")

        # Special analysis
        self.investigate_cfb_signature()

        # Summary
        print(f"\n{'═'*70}")
        print("INVESTIGATION COMPLETE")
        print("═"*70)
        print(f"\nTotal discoveries: {len(self.discoveries)}")

        if self.discoveries:
            print("\nDISCOVERY SUMMARY:")
            for d in self.discoveries:
                print(f"  ★ {d['title']}")

        # Save
        output = {
            'timestamp': datetime.now().isoformat(),
            'discoveries': self.discoveries
        }
        with open(SCRIPT_DIR / 'cfb_address_results.json', 'w') as f:
            json.dump(output, f, indent=2, default=str)

        return self.discoveries

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    investigator = CFBInvestigator()
    investigator.run_investigation()
