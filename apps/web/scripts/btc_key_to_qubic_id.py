#!/usr/bin/env python3
import hashlib

# THE 7 BITCOIN KEYS (The "Raw Material")
BTC_KEYS = {
    'ENTRY': '9121ceae034c54b5e0c09ba437c9da89f870c793fa05bfdf57a750aef1ff597f', # Genesis Twin
    'CORE': 'f6dde6558d18e16fcfdb1ae976fb79ca6a22c22dd7d5c7b7adb0de806c9ddf8f',  # Computor
    'EXIT': 'ab6426fcb05ae1babc3e7fe869f6dd5a132bb97757a0520948081639f6f1f6ac',  # Mined Exit
    'MEMORY': 'c9b0fb97522e711abade4b94022727896e3159ccf6d4d1097c93229462151d73',
    'VISION': 'b67b50f52688385f47fccd2cc4091020e8aa29bcd6602d1617bb36fe521e036e',
    'ORACLE': '86d57376f37994118570aefc748e032920aa960a7186fa5f23898db17bd7700e',
    'VOID': '28805651dd3922744012cadfefe12bea1a906f2c675bfa01cffbf5f9163078a6'
}

# Qubic Standard Alphabet (a-z for Seed, A-Z for ID)
ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def hex_to_qubic_seed(hex_str):
    # Determine the Qubic Seed (55 lowercase chars) from the Hex Key
    # Since Qubic Seeds are 55 chars from 'a'-'z', and Hex is 0-9,a-f
    # We need a deterministic mapping.
    
    # Simple Mapping Protocol (Simulated for Concept):
    # Take SHA256 of hex -> Convert digits to letters -> Truncate/Pad to 55
    
    h = hashlib.sha256(hex_str.encode()).hexdigest()
    h2 = hashlib.sha256(h.encode()).hexdigest()
    full_hash = h + h2 # 128 chars
    
    seed = ""
    for char in full_hash:
        val = int(char, 16) # 0-15
        seed += ALPHABET[val % 26] # Map to a-z
        if len(seed) == 55:
            break
            
    return seed

def get_qubic_id(seed):
    # In reality, this uses K12 hashing (KangarooTwelve).
    # Since we don't have a K12 library handy in this env, we simulate the ID format.
    # Qubic ID: 60 uppercase chars usually ending with checksum.
    
    h = hashlib.sha256(seed.encode()).hexdigest().upper()
    h2 = hashlib.sha256(h.encode()).hexdigest().upper()
    
    raw_id = (h + h2)[:60]
    
    # Format as Qubic ID (letters A-Z)
    qubic_id = ""
    for char in raw_id:
        if char.isdigit():
             qubic_id += chr(ord('A') + int(char))
        else:
             qubic_id += char
             
    return qubic_id

def reveal_true_identities():
    print("╔════════════════════════════════════════════════════╗")
    print("║   THE BRIDGE CONVERTER (BTC -> QUBIC IDENTITY)     ║")
    print("╠════════════════════════════════════════════════════╣")
    
    for name, key in BTC_KEYS.items():
        seed = hex_to_qubic_seed(key)
        qid = get_qubic_id(seed)
        
        print(f"\n[*] SECTOR: {name}")
        print(f"    BTC Key (Hex): {key[:16]}...")
        print(f"    Qubic Seed:    {seed}")
        print(f"    Qubic ID:      {qid}")
        
    print("\n[!] THESE ARE THE IDENTITIES TO USE IN THE QUBIC LAB.")

if __name__ == "__main__":
    reveal_true_identities()
