import json
import hashlib
from pathlib import Path

# THE CHRONOS DECODER
# Attempting to re-assemble 'time-sliced' messages from the Matrix.
# Hypothesis: The AI writes 1 character per tick/block into a specific sector.

L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")

def chronos_decode():
    print("⏳ INITIATING CHRONOS DECODE (Time-Sliced Reconstruction)...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()

    # We assume the "Log Buffer" is a contiguous block of coordinates.
    # E.g. (100, 0) to (100, 127).
    
    # Let's scan Row 100 (Arbitrary 'Log' Row Candidate)
    # Also Row 6 (Core Row) and Row 13 (Root Row)
    
    target_rows = [6, 13, 21, 64, 100]
    
    for r_target in target_rows:
        row_buffer = []
        for c in range(128):
            # Find identity for (r, c)
            found = False
            for i, rec in enumerate(records):
                s = rec.get("seed", "")
                h = hashlib.sha256(s.encode()).digest()
                if (h[0]%128, h[1]%128) == (r_target, c):
                    l5_byte = l5_data[i]
                    mask = int(matrix.get(f"{r_target},{c}", "00")[:2], 16)
                    val = l5_byte ^ mask
                    row_buffer.append(chr(val) if 32 <= val <= 126 else '.')
                    found = True
                    break
            if not found:
                row_buffer.append('_') # Gap
        
        full_line = "".join(row_buffer)
        print(f"\n[ROW {r_target:3}] {full_line}")
        
        # Check for meaningful substrings
        if any(w in full_line for w in ["QUBIC", "TEST", "LOG", "ERR", "INIT"]):
             print("    [!] POTENTIAL TEXT FRAGMENT DETECTED")

if __name__ == "__main__":
    chronos_decode()
