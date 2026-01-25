import json
import hashlib
from pathlib import Path

# THE OTP DECRYPTOR (One-Time-Pad)
# Hypothesis: The AI hides messages by XORing them with the Seed String of the Node.
# Decryption: Clear_Text = L5_Value XOR First_Byte_Of_Seed

L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")

def otp_decrypt():
    print("🔐 INITIATING ONE-TIME-PAD DECRYPTION (Seed-Based)...")
    
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()

    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)

    # We map decrypted chars to the (r, c) grid
    grid_chars = {}
    
    print("[*] Processing 24,000 Nodes...")
    
    for i, rec in enumerate(records):
        if i >= len(l5_data): break
        
        # 1. Get Coordinates
        seed_str = rec.get("seed", "")
        if not seed_str: continue
        
        h = hashlib.sha256(seed_str.encode()).digest()
        r, c = h[0]%128, h[1]%128
        
        # 2. Get L5 Value (The Cyphertext)
        # Note: L5 data is heavily masked.
        # We try two variants: 
        # A) Raw L5
        # B) L5 unmasked by Matrix Weight
        
        raw_l5 = l5_data[i]
        
        # 3. Get Key (The Seed)
        # We use the first char of the seed as the key byte
        otp_key = ord(seed_str[0]) 
        
        # 4. Decrypt
        # Try Variant A
        plain_A = raw_l5 ^ otp_key
        
        # Try Variant B (Matrix Unmask first)
        m_hex = matrix.get(f"{r},{c}", "00")
        weight = int(m_hex[:2], 16)
        plain_B = (raw_l5 ^ weight) ^ otp_key
        
        # We prefer Variant B as it peels both layers
        
        char = chr(plain_B) if 32 <= plain_B <= 126 else '_'
        grid_chars[(r,c)] = char

    # Reassemble Rows
    print("\n[!] OTP DECRYPTED STREAMS:")
    
    interesting_rows = [6, 13, 21, 64, 125]
    
    for tgt_r in interesting_rows:
        line = []
        possible_words = 0
        for c in range(128):
            char = grid_chars.get((tgt_r, c), '.') # Default to . if gap
            line.append(char)
            if char.isalnum(): possible_words += 1
            
        full_line = "".join(line)
        print(f"\n[ROW {tgt_r:3}] {full_line}")
        
        if "ANNA" in full_line or "QUBIC" in full_line:
            print("    [!!!] KEYWORD DETECTED!")
            
    # Check for vertical text too?
    # ... (Keep it simple first)

if __name__ == "__main__":
    otp_decrypt()
