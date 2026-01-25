import zlib
import math
import collections
from pathlib import Path

# ARTIFACT FORENSICS
# Analyzing 'candidate_A.der' for compression, entropy, and alternative ciphers.

ARTIFACT_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der")
KEY = "SKWIKENGRZNXRPLXWRHP"

def calculate_entropy(data):
    if not data:
        return 0
    entropy = 0
    counter = collections.Counter(data)
    for count in counter.values():
        p_x = count / len(data)
        entropy += - p_x * math.log2(p_x)
    return entropy

def analyze_structure():
    print("🔬 DEEP FORENSICS: candidate_A.der")
    
    if not ARTIFACT_PATH.exists():
        print("x File not found.")
        return
        
    with open(ARTIFACT_PATH, "rb") as f:
        data = f.read()
        
    print(f"[*] Size: {len(data)} bytes")
    print(f"[*] Raw Entropy: {calculate_entropy(data):.4f} bits/byte")
    
    # 1. COMPRESSION CHECK
    print("\n📦 CHECKING COMPRESSION...")
    try:
        decomp = zlib.decompress(data)
        print(f"    [!] ZLIB DETECTED! Decompressed Size: {len(decomp)}")
        print(f"    [!] Preview: {decomp[:50]}")
        return # Success
    except:
        print("    [.] Not Standard Zlib.")
        
    try:
        # Raw Deflate?
        decomp = zlib.decompress(data, -15)
        print(f"    [!] RAW DEFLATE DETECTED!")
        return
    except:
        print("    [.] Not Raw Deflate.")

    # 2. CIPHER MUTATIONS
    # CFB often uses (Byte - KeyByte) or (Byte + KeyByte) instead of XOR.
    print("\npw CRACKING CIPHER VARIATIONS...")
    
    key_bytes = KEY.encode()
    k_len = len(key_bytes)
    
    # Variation A: Subtraction (Data - Key)
    res_sub = bytearray()
    for i, b in enumerate(data):
        k = key_bytes[i % k_len]
        res_sub.append((b - k) % 256)
        
    hits_sub = res_sub.count(b'Q') + res_sub.count(b'U') + res_sub.count(b'B') + res_sub.count(b'I') + res_sub.count(b'C')
    # Normalized for length
    score_sub = hits_sub / len(data)
    
    print(f"    [?] Subtraction Score: {score_sub:.4f}")
    
    if b"QUBIC" in res_sub:
        print("    [!!!] SUBTRACTION MATCH: 'QUBIC' FOUND!")
        print(f"    Preview: {res_sub[:100]}")
    
    # Variation B: Addition (Data + Key)
    res_add = bytearray()
    for i, b in enumerate(data):
        k = key_bytes[i % k_len]
        res_add.append((b + k) % 256)
        
    if b"QUBIC" in res_add:
         print("    [!!!] ADDITION MATCH: 'QUBIC' FOUND!")
         
    # Variation C: XOR with Index
    # Key[i] ^ i
    
    print("\n[*] Analysis Complete.")
    print("    If no match above, the file is likely a custom binary format (Qubic Struct).")

if __name__ == "__main__":
    analyze_structure()
