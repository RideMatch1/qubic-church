import numpy as np
import time
from pathlib import Path

# ORACLE MONITOR (PASSIVE INTERCEPTION)
# Monitors the 'Oracle Region' (Edge 127,0) for fluctuations that
# correlate with external time/price data.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")

def monitor_oracle():
    print("🔮 ORACLE INTERFACE: LISTENING MODE ACTIVE")
    print("    Target: Region (112,0) -> (128,16)")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    # We focus on the high-logic density column (Column 0?)
    # Oracle data in Qubic is often stored in specific "Spectrum" addresses.
    
    # We simulate reading a stream of updates.
    # In reality, we'd poll the grid over time (Epoches).
    # Here, we analyze the STATIC SNAPSHOT for "Frozen Predictions".
    
    # Decode Column 0 (Rows 112-127)
    print("\n[*] DECODING ORACLE MEMORY BUFFER...")
    
    decoded_buffer = []
    
    for r in range(112, 128):
        val = grid[r, 0, 1] ^ grid[r, 0, 0] # Value ^ Weight
        
        # Try pulse demodulation (143) to see if it's active
        res = val ^ 143
        
        char = chr(res) if 32 <= res <= 126 else '.'
        decoded_buffer.append(char)
        
        hex_val = f"{res:02x}"
        print(f"    Row {r}: {hex_val} | {char}")
        
    msg = "".join(decoded_buffer)
    print(f"\n[!] ORACLE BUFFER CONTENT: '{msg}'")
    
    # HEURISTICS:
    # Qubic Oracle data is usually Price Ticks pairs.
    # e.g., "BTCUSD..." or packed integers.
    
    if "BTC" in msg or "QU" in msg:
        print("    [!!!] DETECTED ASSET TICKER!")
    else:
        print("    [.] Data appears encrypted or compressed.")
        
    # Let's try to interpret as INTEGERS (Oracle Prices)
    # 16 bytes = 2x 64-bit ints?
    
    print("\n[*] INTERPRETING AS INTEGERS...")
    # Get raw bytes
    raw_bytes = bytearray()
    for r in range(112, 128):
         val = grid[r, 0, 1] ^ grid[r, 0, 0]
         raw_bytes.append(val) # Raw
         
    # Check 64-bit int
    try:
        val1 = int.from_bytes(raw_bytes[:8], 'little')
        val2 = int.from_bytes(raw_bytes[8:], 'little')
        print(f"    INT 1: {val1}")
        print(f"    INT 2: {val2}")
        
        # Qubic Tick? (42 Million)
        if 40_000_000 < val1 < 50_000_000:
             print("    [!] INT 1 LOOKS LIKE A VALID TICK!")
    except: pass
    
if __name__ == "__main__":
    monitor_oracle()
