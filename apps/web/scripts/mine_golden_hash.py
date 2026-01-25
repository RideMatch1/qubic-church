import hashlib
import binascii

# TARGETED MINER (VANITY SEARCH)
# Attempts to find a nonce that produces a Block Hash starting with specific hex bytes.
# We want to match the "Ideal Hash" prefix we calculated.

TARGET_PREFIX = "4aede2ab" # First 4 bytes (8 hex) of the "QUBIC" writing hash
PREV_HASH = "0000000000000000000095b59d3899fb54de5e1d89b98934185c439125994c05"
TX_ID_ROOT = "b24ca" # Short simulated root

def mine_target():
    print(f"⛏️ MINING FOR TARGET PREFIX: {TARGET_PREFIX}...")
    
    nonce = 0
    while True:
        # Simplified Header Structure
        # We vary nonce to change the hash
        header = f"{PREV_HASH}{TX_ID_ROOT}{nonce}"
        h = hashlib.sha256(header.encode()).hexdigest()
        
        if h.startswith(TARGET_PREFIX):
            print(f"\n[!!!] MATCH FOUND at Nonce {nonce}")
            print(f"      Hash: {h}")
            print(f"      Target: {TARGET_PREFIX}...")
            
            with open("golden_block_hash.txt", "w") as f:
                f.write(h)
            return
            
        nonce += 1
        
        if nonce % 1000000 == 0:
            print(f"    Scanning... {nonce/1000000:.1f}M nonces. (Current: {h[:8]})")

if __name__ == "__main__":
    mine_target()
