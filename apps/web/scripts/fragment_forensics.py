import math
import binascii
from pathlib import Path
from collections import Counter

# THE FRAGMENT FORENSICS AUDIT
# Deep analysis of the extracted ASN.1 BLOB (219 bytes) before usage.
# Checks: Entropy, Known Structures, Seed-Pattern Matching.

FRAGMENT_PATH = Path("extracted_cert.der")

def calculate_entropy(data):
    if not data: return 0
    entropy = 0
    for x in range(256):
        p_x = float(data.count(bytes([x]))) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy

def forensic_audit():
    print("🔬 INITIATING FORENSIC AUDIT (Fragment Analysis)...")
    
    if not FRAGMENT_PATH.exists():
        print("[X] Fragment missing.")
        return
        
    with open(FRAGMENT_PATH, "rb") as f:
        blob = f.read()
        
    print(f"[*] Blob Size: {len(blob)} bytes")
    print(f"[*] Hex Head: {binascii.hexlify(blob[:16]).decode()}")
    
    # 1. ENTROPY CHECK
    # Keys have high entropy (>7.5). Structured data has lower (<6.0).
    ent = calculate_entropy(blob)
    print(f"[*] Shannon Entropy: {ent:.4f} bits/byte")
    
    if ent > 7.5:
        print("    -> HIGH ENTROPY: Likely Compressed Data or Encrypted Key.")
    elif ent > 6.0:
        print("    -> MEDIUM ENTROPY: Likely Machine Code or Base64.")
    else:
        print("    -> LOW ENTROPY: Likely Structured Data (Text/JSON/XML).")
        
    # 2. SEED PATTERN CHECK (24 words = ~55 chars?)
    # Qubic Seeds are lowercase [a-z] only structure.
    # Let's check byte ranges.
    
    range_cnt = Counter()
    for b in blob:
        if 97 <= b <= 122: range_cnt['lowercase'] += 1
        elif 65 <= b <= 90: range_cnt['uppercase'] += 1
        elif 48 <= b <= 57: range_cnt['digit'] += 1
        else: range_cnt['symbol'] += 1
        
    print(f"[*] Byte Distribution: {dict(range_cnt)}")
    
    total_alpha = range_cnt['lowercase'] + range_cnt['uppercase']
    if total_alpha / len(blob) > 0.8:
        print("    -> TEXT-HEAVY: Looks like a Seed or Identity String!")
    else:
        print("    -> BINARY-HEAVY: Looks like a Raw Key or Hash.")
            
    # 3. KNOWN QUBIC HEADER CHECK
    # Qubic Packets often start with specific bytes.
    # Is it a "Qubic Transfer"?
    
    # 4. DUPLICATE CHECK
    # Does this blob repeat internally? Is it a looped signal?
    
    chunks = [blob[i:i+16] for i in range(0, len(blob), 16)]
    unique_chunks = len(set(chunks))
    if unique_chunks < len(chunks):
        print(f"    -> REPEATING PATTERNS DETECTED ({len(chunks)-unique_chunks} repeats)")
    else:
        print("    -> No internal repetition (Good for Key data).")

if __name__ == "__main__":
    forensic_audit()
