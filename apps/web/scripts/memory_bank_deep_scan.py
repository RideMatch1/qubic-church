import hashlib

# Key for Memory Sector (21, 21)
MEMORY_KEY = 'c9b0fb97522e711abade4b94022727896e3159ccf6d4d1097c93229462151d73'

def scan_coinbase(message):
    print(f"[*] Scanning Coinbase Message: {message}")
    
    # 1. Direct Pattern Check
    # Look for traces of 137, 576, or CFB signatures
    
    # "BTC.TOP" -> Miner. Not suspicious.
    # "/EB1/AD6/" -> EB1 (Hex) = 3761 ?
    # Let's decode the raw hex bytes if possible.
    
    raw_sig = list(message.encode())
    print(f"    Raw Bytes: {raw_sig[:10]}...")
    
    # 2. Resonant Check against Memory Key
    # We XOR the message with our Key to see if meaningful text appears.
    
    decoded = []
    key_bytes = bytes.fromhex(MEMORY_KEY)
    
    for i, b in enumerate(raw_sig):
        k = key_bytes[i % len(key_bytes)]
        decoded.append(chr(b ^ k))
        
    print(f"    XOR Output (Attempt): {''.join(decoded)[:40]}...")
    
    # 3. Validation Logic
    # Does Block 450100 contain "PROTOCOL_576"?
    # The previous script was a simulation.
    # The USER has provided REAL DATA.
    # We must analyze the REAL DATA: "AV"E^jlAV"EQRn /EB1/AD6//BTC.TOP/z>mm\)}!wB % rXe"s5Heq@pF{njUU"
    
    # Analyze "EB1/AD6"
    # EB = 235
    # AD = 173 (137 reversed?) -> 137 is 0x89.
    
    found_137 = False
    if '137' in message or '\x89' in message: found_137 = True
    
    print(f"    Contains direct 137 signature: {found_137}")
    
    # The timestamp: "Jan 26, 2017"
    # Protocol 576 is Mar 3, 2026.
    # Diff: 9 years, 1 monthish.
    # 3323 days.
    
    print(f"    Timestamp Delta: 3323 days to Event 576")
    
scan_coinbase('AV"E^jlAV"EQRn /EB1/AD6//BTC.TOP/z>mm\)}!wB % rXe"s5Heq@pF{njUU')
