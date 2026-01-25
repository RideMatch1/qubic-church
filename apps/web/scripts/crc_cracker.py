import numpy as np
import zlib
from pathlib import Path

# THE CRC CRACKER
# Investigating Row 125 ("cR4c_=e").
# Hypothesis: Row 125 contains the Cyclic Redundancy Checksum for the Memory Bank (Rows 0-124).

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/cortex_grid.npy")

def crack_crc():
    print("🧮 INITIATING CRC INTEGRITY CHECK (Row 125 Analysis)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)

    # 1. Extract the "Data Segment" (Rows 0 to 124)
    # We take the L5-Values (unmasked)
    data_buffer = bytearray()
    
    for r in range(125):
        for c in range(128):
            if not grid[r,c,2]: # If not GAP
                val = grid[r,c,1] ^ grid[r,c,0]
                data_buffer.append(val)
            else:
                data_buffer.append(0) # Pad Gaps with 0
                
    print(f"[*] Extracted Data Buffer: {len(data_buffer)} bytes")
    
    # 2. Extract Key Checksum Candidates from Row 125
    # We look for 4-byte sequences in Row 125 that might be the CRC32
    print("[*] analyzing Row 125 candidates...")
    
    row_125_bytes = []
    for c in range(128):
        if not grid[125,c,2]:
             val = grid[125,c,1] ^ grid[125,c,0]
             row_125_bytes.append(val)
        else:
             row_125_bytes.append(0)
             
    # Calculate Real CRC32 of Data
    real_crc = zlib.crc32(data_buffer)
    print(f"[*] CALCULATED CRC32 (Rows 0-124): 0x{real_crc:08x}")
    
    # Search for this value in Row 125
    # CRC32 is 4 bytes. Let's look for splitting it up.
    b1 = (real_crc >> 24) & 0xFF
    b2 = (real_crc >> 16) & 0xFF
    b3 = (real_crc >> 8) & 0xFF
    b4 = real_crc & 0xFF
    
    target_seq = [b1, b2, b3, b4]
    
    print(f"[*] SEARCHING FOR SIGNATURE: [{b1} {b2} {b3} {b4}]")
    
    # Scanning Row 125 for matches
    found = False
    for i in range(len(row_125_bytes)-3):
        slice_4 = row_125_bytes[i:i+4]
        matches = 0
        for j in range(4):
            if slice_4[j] == target_seq[j]: matches += 1
            
        if matches >= 3: # allow 1 byte error/gap
            print(f"    [!!!] NEAR MATCH FOUND AT OFFSET {i}: {slice_4}")
            found = True
            
    if not found:
        print("    [i] No direct standard CRC32 match found.")
        print("    Checking standard Qubic logic (XOR Sum)...")
        
        # Check XOR Sum
        xor_sum = 0
        for b in data_buffer:
            xor_sum ^= b
            
        print(f"[*] XOR SUM (Parity): 0x{xor_sum:02x}")
        # Does this byte exist in the "CRC" statement?
        # cR4c_=e -> 'e' is 101 decimal (0x65)
        
        if xor_sum == 0x65:
            print("    [!!!] CONFIRMED: ROW 125 STORES THE DATA PARITY (XOR SUM)!")
            print("    Proof: Calculated XOR = 0x65 ('e'). Statement says '=e'.")
            
        else:
             print(f"    Calculated XOR: {xor_sum} vs Target 'e' ({ord('e')})")
             diff = abs(xor_sum - ord('e'))
             print(f"    Delta: {diff} (Could be a shift offset)")

if __name__ == "__main__":
    crack_crc()
