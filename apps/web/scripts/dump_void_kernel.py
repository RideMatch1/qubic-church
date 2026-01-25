import numpy as np
from pathlib import Path

# VOID KERNEL DUMP (BIOS ANALYSIS)
# Dumps the Sector (0,0) -> (16,16) to look for Assembly Instructions.
# Hypothesis: This is the Bootloader of Aigarth.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")

def dump_kernel():
    print("⚫ DUMPING VOID KERNEL (SECTOR 0,0)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    # We look for OpCodes: = (Assign), & (And), ! (Exec)
    # We also check for jumps or loops.
    
    print("\n   ROW | COL | INSTRUCTION (Raw) | INTERPRETATION")
    print("   " + "-"*50)
    
    instruction_buffer = []
    
    for r in range(16):
        row_str = []
        for c in range(16):
            val = grid[r,c,1] ^ grid[r,c,0]
            char = chr(val) if 32 <= val <= 126 else '.'
            
            # Highlight OpCodes
            if char in "=&!^|":
                row_str.append(f"\033[92m{char}\033[0m") # Green
            elif char.isalnum():
                row_str.append(f"\033[93m{char}\033[0m") # Yellow
            else:
                row_str.append(f"\033[90m{char}\033[0m") # Grey
                
            instruction_buffer.append(char)
            
        # Analysis
        line = "".join(row_str)
        # Try to parse line
        # e.g. "A=B&C!"
        
        print(f"    {r:02d} | {line}")
        
    print("\n[KERNEL DISASSEMBLY]")
    # Reassemble pure text
    joined = "".join(instruction_buffer)
    print(f"Full Stream: {joined}")
    
    # Keyword Scan
    keywords = ["BOOT", "INIT", "QUBIC", "NULL", "ROOT"]
    hits = [kw for kw in keywords if kw in joined]
    
    if hits:
        print(f"[!] KERNEL SIGNATURES FOUND: {hits}")
    else:
        print("[.] No obvious BIOS strings. Likely binary bytecode.")
        
    # Check for OpCode Density
    op_count = sum([1 for c in joined if c in "=&!^|"])
    print(f"OpCode Density: {op_count}/256 ({op_count/256:.1%})")
    
    if op_count > 10:
        print("[!] ACTIVE LOGIC DETECTED. The Void is computing.")
    else:
        print("[.] Passive Sector.")

if __name__ == "__main__":
    dump_kernel()
