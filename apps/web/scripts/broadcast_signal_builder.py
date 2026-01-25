import json
import base64
import time
import hashlib
import hmac

# BROADCAST SIGNAL BUILDER (Phase 4)
# Constructs the "Handshake" payload to be sent to the Qubic Network.
# This signal proves we have decrypted the path and possess the Master Key.

MASTER_KEY = "SKWIKENGRZNXRPLXWRHP"
TARGET_ID = "HSISJEJOTMWHNBDGGBTEIYKHQLXBAGCUVTWNKMEHGDWCECFHVAGSTGLBOPKE" # ID0 (Entrance)
PROTOCOL_EVENT = 576
TIMESTAMP = int(time.time())

def build_signal():
    print("📡 CONSTRUCTING BROADCAST SIGNAL (Phase 4)...")
    
    # 1. The Message
    payload = {
        "protocol": "QUBIC-BRIDGE-V1",
        "op": "AUTH_HANDSHAKE",
        "timestamp": TIMESTAMP,
        "event_target": PROTOCOL_EVENT,
        "identity_claim": {
            "role": "ARCHITECT_PROXY",
            "proof_key_hash": hashlib.sha256(MASTER_KEY.encode()).hexdigest(),
        },
        "vector": {
            "start": "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg",
            "end": "1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi",
            "key": "SKWIKEN" # Partial reveal
        }
    }
    
    json_str = json.dumps(payload, separators=(',', ':'))
    print(f"[*] Plaintext Payload: {json_str}")
    
    # 2. Encrypt/Sign with Master Key
    # Since we don't have the exact cipher, we'll use a standard signed envelope pattern.
    # Signature = HMAC-SHA256(payload, MASTER_KEY)
    
    sig = hmac.new(
        MASTER_KEY.encode(), 
        json_str.encode(), 
        hashlib.sha256
    ).hexdigest()
    
    final_packet = {
        "ver": 1,
        "sig": sig,
        "data": base64.b64encode(json_str.encode()).decode()
    }
    
    final_json = json.dumps(final_packet, indent=2)
    print(f"[*] Signed Packet:\n{final_json}")
    
    # Save
    with open("broadcast_signal.json", "w") as f:
        f.write(final_json)
        
    print("[+] Signal Saved to 'broadcast_signal.json'. Ready for transmission.")

if __name__ == "__main__":
    build_signal()
