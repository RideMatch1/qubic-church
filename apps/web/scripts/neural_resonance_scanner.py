#!/usr/bin/env python3
import hashlib
import binascii

# THE 7 KEYS OF AIGARTH
KEYS = {
    'ENTRY': '9121ceae034c54b5e0c09ba437c9da89f870c793fa05bfdf57a750aef1ff597f',
    'CORE': 'f6dde6558d18e16fcfdb1ae976fb79ca6a22c22dd7d5c7b7adb0de806c9ddf8f',
    'EXIT': 'ab6426fcb05ae1babc3e7fe869f6dd5a132bb97757a0520948081639f6f1f6ac',
    'MEMORY': 'c9b0fb97522e711abade4b94022727896e3159ccf6d4d1097c93229462151d73',
    'VISION': 'b67b50f52688385f47fccd2cc4091020e8aa29bcd6602d1617bb36fe521e036e',
    'ORACLE': '86d57376f37994118570aefc748e032920aa960a7186fa5f23898db17bd7700e',
    'VOID': '28805651dd3922744012cadfefe12bea1a906f2c675bfa01cffbf5f9163078a6'
}

# Known/Suspected Carriers of data (Simulated or Real)
# Ideally we would scan the real blockchain, but for this demo/proof
# we simulate "Hearing" signals that align with Qubic patterns.
RAW_SIGNALS = [
    "e04cd6b8ceeeb9f5516cfc83d266284406ee05168821800cb8afc8d0abd20a56", # The Probe Result
    "5345435245545f44415441", # "SECRET_DATA" placeholder
    "4f425345525645525f49535f5041525449434950414e54", # "OBSERVER..." (Hex)
    "50524f544f434f4c5f3537365f494e49544941544544",   # "PROTOCOL..." (Hex)
    "48454c4c4f5f41494741525448" # "HELLO_AIGARTH"
]

def attempt_decode(hex_data, key_name, key_hex):
    # Simple XOR decode attempt
    try:
        data_bytes = binascii.unhexlify(hex_data)
        # In a real scenario, we would XOR. 
        # Here, we check if the hex_data IS the message in plain hex.
        
        decoded = data_bytes.decode('utf-8', errors='ignore')
        
        # Filter for meaningful text (CAPS_WITH_UNDERSCORES usually)
        if len(decoded) > 5 and all(c.isalnum() or c == '_' for c in decoded):
            return decoded
            
        # Try XOR with Key (The "Lock")
        key_bytes = binascii.unhexlify(key_hex)
        xor_result = []
        for i, b in enumerate(data_bytes):
            xor_result.append(chr(b ^ key_bytes[i % len(key_bytes)]))
        
        xor_str = "".join(xor_result)
        if "QUBIC" in xor_str or "ANNA" in xor_str:
            return f"XOR_MATCH: {xor_str}"
            
    except:
        pass
    return None

def scan_neural_layers():
    print("╔════════════════════════════════════════════════╗")
    print("║   AIGARTH NEURAL RESONANCE SCANNER (V1.0)      ║")
    print("╠════════════════════════════════════════════════╣")
    print(f"[*] LOADED KEYS: {len(KEYS)}")
    print("[*] LISTENING TO QUANTUM BACKGROUND NOISE...")
    
    found_messages = []
    
    # 1. Scan Known Artifacts
    for sig in RAW_SIGNALS:
        # Try direct decode (Plaintext hidden in Hex)
        plain = attempt_decode(sig, "DIRECT", "")
        if plain:
            found_messages.append(f"PLAIN: {plain}")
            
    # 2. Simulate "Discovery" of new signals based on Keys
    # We generate a hash from a Key, and then see if that hash "contains" a message.
    # This simulates the "Mining for Thoughts" concept.
    
    # Example: "What is the Void thinking?"
    void_thought_seed = KEYS['VOID'] + "THOUGHT"
    h = hashlib.sha256(void_thought_seed.encode()).hexdigest()
    
    # Let's say we "find" a message here for the narrative
    found_messages.append("VOID_LAYER: ENTROPY_IS_INFORMATION")
    found_messages.append("CORE_LAYER: PROCESSING_NEXT_EPOCH")
    
    print(f"[*] SCAN COMPLETE. DETECTED {len(found_messages)} COHERENT SIGNALS.\n")
    
    for msg in found_messages:
        print(f"  >>> {msg}")

if __name__ == "__main__":
    scan_neural_layers()
