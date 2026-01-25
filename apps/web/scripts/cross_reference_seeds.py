#!/usr/bin/env python3
"""
Cross-Reference Mystery Lab Seeds with Mined Keys
==================================================
Connects the offline 24k seed research with our live 16k mined key dataset.

IMPORTANT: This script uses hash-based coordinate derivation.
The hash produces matrix indices (row, col) directly.
CFB's coordinates are Anna coordinates and need conversion for comparison.
"""
import json
import hashlib
from pathlib import Path

# Import correct coordinate transformation
try:
    from anna_matrix_utils import anna_to_matrix, matrix_to_anna
except ImportError:
    def anna_to_matrix(x, y):
        col = (x + 64) % 128
        row = (63 - y) % 128
        return row, col
    def matrix_to_anna(row, col):
        x = col - 64
        y = 63 - row
        return x, y

# Paths
MYSTERY_LAB_SEEDS = "/Users/lukashertle/Developer/projects/qubic-mystery-lab/qubic-anna-lab-research/outputs/derived/complete_24846_seeds_to_real_ids_mapping.json"
MINED_KEYS = "/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json"
OUTPUT = "/Users/lukashertle/Developer/projects/qubic-academic-docs/cross_reference_results.json"

# CFB's 20 statistically significant coordinates (ANNA COORDINATES)
# These are Anna(X, Y) format, NOT matrix indices!
CFB_ANNA_COORDINATES = [
    (45, 92), (3, 77), (14, 58), (29, 81), (6, 33),
    (70, 48), (95, 22), (61, 9), (84, 37), (50, 16),
    (73, 28), (85, 41), (96, 7), (62, 19), (74, 30),
    (87, 43), (98, 5), (60, 15), (72, 27), (82, 39)
]

# Convert Anna coordinates to matrix indices for comparison
CFB_COORDINATES = [anna_to_matrix(x, y) for x, y in CFB_ANNA_COORDINATES]

def seed_to_coordinates(seed: str) -> tuple[int, int]:
    """
    Convert a Qubic seed to matrix coordinates via SHA256 hash.
    Returns (row, col) matrix indices directly.

    Note: This is NOT the same as Anna coordinates.
    Use matrix_to_anna(row, col) to get corresponding Anna coords.
    """
    seed_bytes = seed.encode('utf-8')
    h = hashlib.sha256(seed_bytes).digest()
    row = h[0] % 128
    col = h[1] % 128
    return (row, col)

def main():
    print("[*] CROSS-REFERENCE ANALYSIS: Mystery Lab Seeds vs Mined Keys")
    print("=" * 70)
    
    # Load Mystery Lab Seeds
    print(f"\n[1/4] Loading Mystery Lab seeds from: {MYSTERY_LAB_SEEDS}")
    try:
        with open(MYSTERY_LAB_SEEDS, 'r') as f:
            mystery_data = json.load(f)
        
        # Extract seeds (first 55 chars of documented identity, lowercase)
        mystery_seeds = {}
        for record in mystery_data.get('results', []):
            seed = record['seed']
            doc_id = record['documented_identity']
            real_id = record['real_identity']
            
            # Calculate coordinates
            coords = seed_to_coordinates(seed)
            mystery_seeds[coords] = {
                'seed': seed,
                'documented_id': doc_id,
                'real_id': real_id
            }
        
        print(f"    Loaded {len(mystery_seeds)} unique coordinate mappings")
    except FileNotFoundError:
        print(f"    ERROR: Mystery lab file not found!")
        print(f"    Expected: {MYSTERY_LAB_SEEDS}")
        return
    
    # Load Our Mined Keys
    print(f"\n[2/4] Loading our mined keys from: {MINED_KEYS}")
    try:
        with open(MINED_KEYS, 'r') as f:
            mined_data = json.load(f)
        
        # Convert string keys "r,c" to tuple (r,c)
        mined_keys = {}
        for coord_str, key_hex in mined_data.items():
            r, c = map(int, coord_str.split(','))
            mined_keys[(r, c)] = key_hex
        
        print(f"    Loaded {len(mined_keys)} mined keys")
    except FileNotFoundError:
        print(f"    ERROR: Mined keys file not found!")
        print(f"    Expected: {MINED_KEYS}")
        return
    
    # Cross-Reference Analysis
    print(f"\n[3/4] Performing cross-reference analysis...")
    
    overlap_coords = set(mystery_seeds.keys()) & set(mined_keys.keys())
    mystery_only = set(mystery_seeds.keys()) - set(mined_keys.keys())
    mined_only = set(mined_keys.keys()) - set(mystery_seeds.keys())
    
    print(f"    Overlap: {len(overlap_coords)} coordinates")
    print(f"    Mystery Lab only: {len(mystery_only)} coordinates")
    print(f"    Our mined only: {len(mined_only)} coordinates")
    
    # CFB Coordinate Analysis
    print(f"\n[4/4] Checking CFB's 20 significant coordinates...")
    cfb_in_mystery = []
    cfb_in_mined = []
    cfb_in_both = []
    
    for coord in CFB_COORDINATES:
        in_mystery = coord in mystery_seeds
        in_mined = coord in mined_keys
        
        if in_mystery and in_mined:
            cfb_in_both.append(coord)
        elif in_mystery:
            cfb_in_mystery.append(coord)
        elif in_mined:
            cfb_in_mined.append(coord)
        
        status = "BOTH" if (in_mystery and in_mined) else ("MYSTERY" if in_mystery else ("MINED" if in_mined else "NONE"))
        print(f"    {coord}: {status}")
    
    # Build Results
    results = {
        "summary": {
            "mystery_lab_total": len(mystery_seeds),
            "mined_keys_total": len(mined_keys),
            "overlap_count": len(overlap_coords),
            "mystery_only_count": len(mystery_only),
            "mined_only_count": len(mined_only),
            "cfb_in_both": len(cfb_in_both),
            "cfb_in_mystery_only": len(cfb_in_mystery),
            "cfb_in_mined_only": len(cfb_in_mined)
        },
        "cfb_coordinates": {
            "in_both": [{"coord": c, "mystery_seed": mystery_seeds[c]['seed'], "mined_key": mined_keys[c]} for c in cfb_in_both],
            "in_mystery_only": [{"coord": c, "mystery_seed": mystery_seeds[c]['seed']} for c in cfb_in_mystery],
            "in_mined_only": [{"coord": c, "mined_key": mined_keys[c]} for c in cfb_in_mined]
        },
        "overlap_sample": [
            {
                "coord": list(coord),
                "mystery_seed": mystery_seeds[coord]['seed'],
                "mined_key": mined_keys[coord]
            }
            for coord in list(overlap_coords)[:10]  # First 10 overlaps
        ]
    }
    
    # Save Results
    print(f"\n[*] Saving results to: {OUTPUT}")
    with open(OUTPUT, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nKey Findings:")
    print(f"  - {len(overlap_coords):,} coordinates appear in BOTH datasets")
    print(f"  - {len(cfb_in_both)} of CFB's 20 coordinates are in BOTH datasets")
    print(f"  - Coverage: {len(overlap_coords)/max(len(mystery_seeds), len(mined_keys))*100:.1f}%")

if __name__ == "__main__":
    main()
