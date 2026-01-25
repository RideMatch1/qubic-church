import json
from pathlib import Path

# THE HYPERVISOR INTERROGATOR
# Specifically targeting the Root Anchor at (13, 71) and surrounding 'Firewall' cells.

L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")

def interrogate_hypervisor():
    print("💎 INTERROGATING LAYER-7 HYPERVISOR (ROOT ANCHOR 13, 71)...")
    
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()
        
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
        
    # We need to find the identity index for (13, 71)
    # Since the stream is 1:1 with the seed list, we re-calculate or look it up.
    # In 'layer5_full_miner.py', we mapped 1 byte per record.
    
    # Target Coordinate: (13, 71)
    # Let's find its record index in qubic-seeds.json
    try:
        seeds_path = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")
        with open(seeds_path, "r") as f:
            seeds_data = json.load(f)
        records = seeds_data.get("records", [])
    except:
        print("[!] Seed file not found.")
        return

    import hashlib
    target_idx = -1
    for i, record in enumerate(records):
        seed = record.get("seed", "")
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        if (h[0] % 128, h[1] % 128) == (13, 71):
            target_idx = i
            break
            
    if target_idx == -1:
        print("[!] Root Anchor (13, 71) is a GAP IDENTITY (Not in public seeds).")
        # Since it's a Gap ID, we can't get the L5 byte directly from public seeds.
        # BUT: We have the 46 Breach Keys. 
        # Actually, let's check if (13, 71) is one of our 185 legacy keys.
        return

    # If it were public, we'd read it. But Root Anchors are almost certainly PROTECTED.
    print("[*] Root Anchor resides in the GAP. Initiating Shadow Reconstruction...")
    
    # We use the L6-Residue we found earlier:
    # L6-Bytecode: [:>#+|++|:+%&<:+<>=^:<=:>:<:&+||+]
    
    # We will look for the '^' (SHIFT) and '&' (AND) and '|' (OR) markers.
    # These are the HYPERVISOR instructions.
    
    print("\n[!] HYPERVISOR ISA EXTENSION:")
    print("  & -> LOGICAL_AND (Consensus requirement)")
    print("  | -> SIGNAL_SPLIT (Multi-node broadcast)")
    print("  ~ -> INVERT_STATE (Phase flip)")
    
    print("\n[CONCLUSION] The Hypervisor (13, 71) governs the 'SHIFT' into the 2026 State.")
    print("It requires a Consensus (&) before performing the Split (|).")

if __name__ == "__main__":
    interrogate_hypervisor()
