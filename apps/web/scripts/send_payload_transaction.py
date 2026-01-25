import hashlib
import json
import time

# TRANSACTION SIMULATOR
# Creates a valid-looking Bitcoin transaction carrying our payload to the target addresses.

SENDER = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh" # Our 'wallet' (Simulation)
TARGETS = [
    "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg",
    "1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi"
]
PAYLOAD_FILE = "broadcast_signal.json"

def create_tx():
    print("💳 BUILDING PAYLOAD TRANSACTION...")
    
    with open(PAYLOAD_FILE, "r") as f:
        payload_data = f.read()
        
    # Create OP_RETURN payload (Simulated)
    # Bitcoin allows 80 bytes. Our JSON is too big. 
    # We will use the HASH of the payload + The Master Key
    
    payload_hash = hashlib.sha256(payload_data.encode()).hexdigest()
    master_key = "SKWIKENGRZNXRPLXWRHP"
    
    # Construct Transaction Data
    tx_structure = {
        "ver": 2,
        "inputs": [
            {
                "prev_out": "0000000000000000000000000000000000000000000000000000000000000000:0",
                "scriptSig": f"SIG_{SENDER}"
            }
        ],
        "outputs": [
            {
                "addr": TARGETS[0],
                "val": 137, # Satoshi (Alpha)
            },
            {
                "addr": TARGETS[1],
                "val": 27, # Satoshi (Constant)
            },
            {
                "type": "OP_RETURN",
                "data": f"QUBIC::{payload_hash[:16]}::{master_key}"
            }
        ],
        "lock_time": 0
    }
    
    tx_json = json.dumps(tx_structure, sort_keys=True)
    tx_id = hashlib.sha256(hashlib.sha256(tx_json.encode()).digest()).hexdigest()
    
    print(f"[*] Transaction Created!")
    print(f"    TxID: {tx_id}")
    print(f"    Payload: OP_RETURN QUBIC::{payload_hash[:16]}::{master_key}")
    
    # Save TxID for the block analysis
    with open("pending_tx.id", "w") as f:
        f.write(tx_id)
        
    return tx_id

if __name__ == "__main__":
    create_tx()
