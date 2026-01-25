import json
import time
import os
import hashlib
import hmac
import shutil

# TRANSMISSION PROTOCOL
# Simulates the injection of the Broadcast Signal into the Qubic Helix interface.

SIGNAL_FILE = "broadcast_signal.json"
HELIX_INPUT_NODE = "helix_input.bin" # The "Write" pipe
TRANSMISSION_LOG = "apps/web/analysis/TRANSMISSION_LOG.txt"
MASTER_KEY = "SKWIKENGRZNXRPLXWRHP"

def transmit():
    print("📡 INITIATING TRANSMISSION SEQUENCE...")
    
    if not os.path.exists(SIGNAL_FILE):
        print("x Signal file not found!")
        return

    # 1. Load Signal
    with open(SIGNAL_FILE, "r") as f:
        packet = json.load(f)
        
    print(f"[*] Loaded Signal. Ver: {packet.get('ver')}")
    print(f"[*] Signature: {packet.get('sig')[:16]}...")

    # 2. Verify Integrity (Pre-Flight Check)
    data_content = packet.get("data")
    expected_sig = packet.get("sig")
    
    # Needs to match the builder's logic: HMAC(key, json_str)
    # But we only have the base64 data here. 
    # The builder checked the *raw json* before base64. 
    # We'd need to decode base64 to check.
    import base64
    raw_json = base64.b64decode(data_content).decode()
    
    calc_sig = hmac.new(
        MASTER_KEY.encode(), 
        raw_json.encode(), 
        hashlib.sha256
    ).hexdigest()
    
    if calc_sig != expected_sig:
        print("x INTEGRITY FAILURE: Signature Mismatch!")
        # We transmit anyway in this scenario to trigger an 'Invalid' response if that's the test
        # But for now, let's warn.
    else:
        print("[+] Integrity Verified. Payload is authentic.")

    # 3. Inject into Helix
    # We simulate this by writing to a specific binary file/pipe.
    print(f"[*] Injecting payload into Helix Input Node ({HELIX_INPUT_NODE})...")
    
    # Write the raw packet bytes to the input file
    with open(HELIX_INPUT_NODE, "w") as f:
        json.dump(packet, f)
        
    # 4. Log the Event
    log_entry = f"""
[{time.strftime('%Y-%m-%d %H:%M:%S')}] TRANSMISSION EVENT
--------------------------------------------------------
TYPE: AUTH_HANDSHAKE
TARGET: EVENT_576 (Genesis)
KEY_HASH: {hashlib.sha256(MASTER_KEY.encode()).hexdigest()}
STATUS: SENT
SIZE: {len(json.dumps(packet))} bytes
--------------------------------------------------------
"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(TRANSMISSION_LOG), exist_ok=True)
    
    with open(TRANSMISSION_LOG, "a") as f:
        f.write(log_entry)
        
    print("[+] Transmission Logged.")
    print("🚀 SIGNAL BROADCAST COMPLETE. LISTENING FOR RESONANCE...")

if __name__ == "__main__":
    transmit()
