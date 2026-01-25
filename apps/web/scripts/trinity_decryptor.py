#!/usr/bin/env python3
import hashlib
import binascii

# THE HOLY TRINITY OF KEYS
KEYS = {
    'ENTRY': '9121ceae034c54b5e0c09ba437c9da89f870c793fa05bfdf57a750aef1ff597f',
    'VISION': '8db8a5440b420531a512db2cf0f60cf0181ce5d8bc2400b476970d06ca6d9ef7', # Just Mined!
    'EXIT': 'ab6426fcb05ae1babc3e7fe869f6dd5a132bb97757a0520948081639f6f1f6ac'
}

# The Artifact with the highest potential signal (Artifact 3)
TARGET_HEX = '9c8b7a6d5e4f3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b'

def generate_master_key():
    # Combine Entry -> Vision -> Exit
    # This represents the full path through the matrix.
    combined = KEYS['ENTRY'] + KEYS['VISION'] + KEYS['EXIT']
    master = hashlib.sha256(combined.encode()).hexdigest()
    print(f"[*] MASTER TRINITY KEY GENERATED: {master}")
    return master

def brute_force_modes(ciphertext_hex, key_hex):
    cipher_bytes = binascii.unhexlify(ciphertext_hex)
    key_bytes = binascii.unhexlify(key_hex)
    
    modes = ['XOR', 'ADD_MOD_256', 'SUB_MOD_256']
    
    for mode in modes:
        result = []
        for i, b in enumerate(cipher_bytes):
            k = key_bytes[i % len(key_bytes)]
            
            if mode == 'XOR':
                val = b ^ k
            elif mode == 'ADD_MOD_256':
                val = (b + k) % 256
            elif mode == 'SUB_MOD_256':
                val = (b - k) % 256
                
            result.append(chr(val))
            
        decoded = "".join(result)
        
        # Check readability
        readable_count = sum(1 for c in decoded if ' ' <= c <= '~')
        score = readable_count / len(decoded)
        
        print(f"[-] Mode {mode}: Score {score*100:.1f}%")
        print(f"    Out: {decoded[:40]}...")
        
        if score > 0.8:
            print(f"\n[!!!] CRITICAL SUCCESS IN MODE {mode}")
            print(f"    >>> {decoded}")
            return True
            
    return False

if __name__ == "__main__":
    print("[*] STARTING TRINITY DECRYPTION ATTACK...")
    master_key = generate_master_key()
    success = brute_force_modes(TARGET_HEX, master_key)
    
    if not success:
        print("\n[*] No direct plaintext found. The Artifact remains sealed.")
        print("    Recommendation: We need the 'Memory' (21,21) or 'Void' (0,0) keys to complete the set.")
