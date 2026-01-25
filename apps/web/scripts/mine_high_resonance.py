import hashlib
import numpy as np

# SIMULATED MINER FOR >90% RESONANCE
# target_weight = 160 (0xA0)
# We need the average byte to be close to 160.
# Range for 90%: |byte - 160| < 25.5
# So bytes should be in range [135, 185] roughly.

EFFECTIVE_WEIGHT = 160
TARGET_SCORE = 90.0

def mine_high_resonance():
    print(f"⛏️ MINING FOR >{TARGET_SCORE}% RESONANCE (Target Byte: {EFFECTIVE_WEIGHT})...")
    
    nonce = 0
    while True:
        # Generate Hash
        data = f"BLOCK_932367_NONCE_{nonce}"
        h_hex = hashlib.sha256(data.encode()).hexdigest()
        h_bytes = bytes.fromhex(h_hex)
        
        # Calculate Resonance
        diff = sum([abs(b - EFFECTIVE_WEIGHT) for b in h_bytes])
        score = (1 - (diff / (255 * 32))) * 100
        
        if score > TARGET_SCORE:
            print(f"\n[!!!] SUCCESS at Nonce {nonce}")
            print(f"      Hash: {h_hex}")
            print(f"      Score: {score:.2f}%")
            return
            
        if nonce % 500000 == 0:
            print(f"    Nonce {nonce}: {score:.2f}%")
            
        nonce += 1

if __name__ == "__main__":
    mine_high_resonance()
