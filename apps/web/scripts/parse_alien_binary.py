import struct
import collections
from pathlib import Path

# ALIEN BINARY PARSER
# Dissecting the structure of 'candidate_A.der' (Layer 5 Artifact).
# Looking for "Skeleton" of the data (Structs, Length Prefixes, etc.)

ARTIFACT_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der")

def parse_binary():
    print("👽 PARSING ALIEN BINARY STRUCTURE...")
    
    if not ARTIFACT_PATH.exists():
        print("x Artifact not found.")
        return
        
    with open(ARTIFACT_PATH, "rb") as f:
        data = f.read()
        
    print(f"[*] Total Size: {len(data)} bytes")
    
    # 1. SCAN FOR ZERO-PADDED STRINGS / GAPS
    # A common feature of C-structs is padding.
    # Long sequences of 0x00 indicate field boundaries.
    
    zeros = [i for i, b in enumerate(data) if b == 0x00]
    print(f"[*] Null Bytes Found: {len(zeros)} (Density: {len(zeros)/len(data):.2%})")
    
    # 2. SCAN FOR REPEATING PATTERNS (Key Search)
    # Are there recurring 32-byte chunks? (Public Keys)
    
    chunks_32 = [data[i:i+32] for i in range(0, len(data), 32)]
    counts = collections.Counter(chunks_32)
    repeats = {k: v for k, v in counts.items() if v > 1}
    
    if repeats:
        print(f"\n[!] REPEATING 32-BYTE SEGMENTS DETECTED ({len(repeats)} unique):")
        for chunk, count in list(repeats.items())[:5]:
            print(f"    x{count}: {chunk.hex()}...")
    else:
        print("\n[.] No obvious 32-byte repetitions (Low repetition entropy).")
        
    # 3. HEADER ANALYSIS
    # First 64 bytes often contain magic bytes or versioning.
    header = data[:64]
    print(f"\n[*] Header Hex:\n    {header.hex()}")
    
    # 4. QUBIC TICK DETECTION
    # Ticks are usually large integers (4 bytes or 8 bytes).
    # Current Tick is ~42 Million.
    # 42,000,000 = 0x0280DE80 (Approx)
    # Searching for sequences that look like valid Ticks.
    
    print("\n[*] Scanning for Timestamp/Tick Markers (Range 40M - 50M)...")
    found_ticks = []
    for i in range(0, len(data)-4):
        # Little Endian (standard for Qubic)
        val = int.from_bytes(data[i:i+4], 'little')
        # Check range: 10M to 100M (Conservative)
        if 10_000_000 < val < 100_000_000:
            found_ticks.append((i, val))
            
    if found_ticks:
        print(f"    [!] FOUND {len(found_ticks)} POTENTIAL TICKS:")
        for idx, val in found_ticks[:5]:
            print(f"        @{idx}: {val} (Possible Epoch Marker)")
    else:
        print("    [.] No standard integer ticks found.")
        
    # 5. STATISTICAL SEGMENTATION
    # Try to guess record size by autocorrelation?
    # Or just print a hex dump of the first segment.
    
    print("\n[*] STRUCTURAL DUMP (First 128 bytes):")
    for i in range(0, 128, 16):
        chunk = data[i:i+16]
        hex_str = " ".join(f"{b:02x}" for b in chunk)
        ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        print(f"    {i:04x}: {hex_str:<48} | {ascii_str}")

if __name__ == "__main__":
    parse_binary()
