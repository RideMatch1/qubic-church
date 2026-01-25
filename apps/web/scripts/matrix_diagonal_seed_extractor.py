#!/usr/bin/env python3
"""
MATRIX DIAGONAL SEED EXTRACTOR

Extract seeds directly from Anna Matrix positions that have ±27 on the main diagonal.
These might be the EXACT seeds used to generate the Genesis addresses!

Strategy:
1. Find all positions where matrix[block, block] = ±27
2. Extract the seed at that position from Anna Matrix
3. Test these seeds DIRECTLY against the Genesis addresses
"""

import json
from pathlib import Path

# ============================================================================
# TARGET BLOCKS WITH ±27 ON DIAGONAL
# ============================================================================

DIAGONAL_27_BLOCKS = {
    73: -27,   # Block 73: matrix[73,73] = -27
    74: -27,   # Block 74: matrix[74,74] = -27
    75: -27,   # Block 75: matrix[75,75] = -27
    80: +27,   # Block 80: matrix[80,80] = +27 ⭐
    89: -27,   # Block 89: matrix[89,89] = -27
    93: -27,   # Block 93: matrix[93,93] = -27
    95: -27,   # Block 95: matrix[95,95] = -27
    96: -27,   # Block 96: matrix[96,96] = -27
    120: +27,  # Block 120: matrix[120,120] = +27 ⭐
    121: -27,  # Block 121: matrix[121,121] = -27 (121=11²!)
}

TARGET_ADDRESSES = {
    73: "1Ky8dP7oR1cBeg1MzkrgHAeHAHyn92DCar",
    74: "1FnbdYntfohuZ1EhZ7f9oiT2R5sDsZBohL",
    75: "14U5EYTN54agAngQu92D9gESvHYfKw8EqA",
    80: "1BwWdLV5wbnZvSYfNA8zaEMqEDDjvA99wX",
    89: "1KSHc1tmsUhS9f1TD6RHR8Kmwg9Zv8WhCt",
    93: "1LNV5xnjneJwXc6jN8X2co586gjiSz6asS",
    95: "18GyZ216oMhpCbZ7JkKZyT8x68v2a8HuNA",
    96: "12XPHPCGYz1WgRhquiAfVeAyjZ7Gbdpih3",
    120: "1FeGetWU2tR2QSrxnpRwHGXGcxzhN6zQza",
    121: "1B7CyZF8e6TYzhNBSHy8yYuTRJNpMtNChg",
    264: "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg",  # 1CFB (separate!)
}

# ============================================================================
# SEED EXTRACTION FROM MATRIX
# ============================================================================

def load_qubic_seeds():
    """Load existing 23,765 seeds"""
    seeds_file = Path("../public/data/qubic-seeds.json")

    if not seeds_file.exists():
        print(f"❌ Seeds file not found: {seeds_file}")
        return {}

    with open(seeds_file) as f:
        data = json.load(f)

    seeds = data.get('records', [])

    # Create lookup by position
    seed_lookup = {}
    for record in seeds:
        batch = record.get('batch', -1)
        index = record.get('index', -1)
        seed = record.get('seed', '')

        if batch >= 0 and index >= 0 and seed:
            # Position in matrix could be batch*something + index
            # Or just sequential: batch * 1000 + index?
            # Let's try different mappings

            # Map 1: Sequential (batch * 1000 + index)
            pos1 = batch * 1000 + index

            # Map 2: Direct index (assuming batches are just groupings)
            pos2 = len(seed_lookup)  # Sequential order in file

            seed_lookup[pos1] = seed
            seed_lookup[pos2] = seed

            # Also store by batch+index tuple
            seed_lookup[(batch, index)] = seed

    print(f"✅ Loaded {len(seeds)} seeds with multiple position mappings")
    return seed_lookup

def find_matrix_position_seeds():
    """
    Find seeds at the exact matrix positions that correspond to our target blocks.

    The Anna Matrix is 128×128, and block numbers map to positions somehow.
    Let's try different mapping strategies.
    """
    print("=" * 80)
    print("🔍 MATRIX DIAGONAL SEED EXTRACTION")
    print("=" * 80)

    seed_lookup = load_qubic_seeds()

    extracted_seeds = {}

    print(f"\n📊 Extracting seeds for {len(DIAGONAL_27_BLOCKS)} target blocks:\n")

    for block_num, diagonal_value in DIAGONAL_27_BLOCKS.items():
        print(f"Block {block_num} (diagonal={diagonal_value:+d}):")

        # Try different position mappings
        candidates = []

        # Strategy 1: Direct block number
        if block_num in seed_lookup:
            candidates.append(('direct', seed_lookup[block_num]))

        # Strategy 2: Block mod 128 (matrix size)
        matrix_pos = block_num % 128
        if matrix_pos in seed_lookup:
            candidates.append(('mod128', seed_lookup[matrix_pos]))

        # Strategy 3: Block - 73 (offset from first target)
        offset = block_num - 73
        if offset in seed_lookup:
            candidates.append(('offset_from_73', seed_lookup[offset]))

        # Strategy 4: Try batch/index combinations
        # Block 73-121 could map to early batches
        for batch in range(0, 5):
            for idx in range(0, 100):
                if (batch, idx) in seed_lookup:
                    candidates.append((f'batch{batch}_idx{idx}', seed_lookup[(batch, idx)]))

        if candidates:
            print(f"   Found {len(candidates)} candidate seeds")
            # Use first candidate for now
            strategy, seed = candidates[0]
            extracted_seeds[block_num] = {
                'seed': seed,
                'strategy': strategy,
                'diagonal_value': diagonal_value,
                'target_address': TARGET_ADDRESSES.get(block_num, 'N/A')
            }
            print(f"   Seed (via {strategy}): {seed[:30]}...")
        else:
            print(f"   ⚠️  No seed found for this position")
        print()

    return extracted_seeds

def extract_batch_24_plus_seeds():
    """
    Extract Batch 24+ seeds from Anna Matrix.

    We have Batches 0-23 (23,765 seeds).
    Original estimate was 24,846 seeds.
    Missing: ~1,081 seeds (Batch 24+)
    """
    print("=" * 80)
    print("🔍 BATCH 24+ SEED EXTRACTION")
    print("=" * 80)

    # Check if there's a full Anna Matrix seed file
    matrix_dir = Path("/Users/lukashertle/Developer/projects/qubic-mystery-lab")

    # Possible locations for additional seeds
    possible_files = [
        matrix_dir / "outputs" / "all_matrix_addresses" / "all_addresses_with_metadata.json",
        matrix_dir / "qubic-anna-lab-research" / "data" / "anna-matrix" / "seeds.json",
        matrix_dir / "outputs" / "comprehensive_analysis" / "all_seeds.json",
    ]

    batch_24_plus = []

    print(f"\n📂 Searching for Batch 24+ seeds...")

    for file_path in possible_files:
        if file_path.exists():
            print(f"   Checking: {file_path.name}")
            try:
                with open(file_path) as f:
                    data = json.load(f)

                # Try different data structures
                if isinstance(data, dict):
                    records = data.get('records', data.get('seeds', []))
                elif isinstance(data, list):
                    records = data
                else:
                    continue

                # Look for seeds with batch >= 24
                for record in records:
                    if isinstance(record, dict):
                        batch = record.get('batch', -1)
                        seed = record.get('seed', '')

                        if batch >= 24 and seed:
                            batch_24_plus.append({
                                'batch': batch,
                                'index': record.get('index', -1),
                                'seed': seed
                            })

                if batch_24_plus:
                    print(f"      ✅ Found {len(batch_24_plus)} Batch 24+ seeds!")
                    break
            except:
                continue

    if not batch_24_plus:
        print(f"\n   ⚠️  No Batch 24+ seeds found in standard locations")
        print(f"   Need to extract from Anna Matrix directly")
        print(f"   (This requires matrix computation access)")

    return batch_24_plus

def save_extracted_seeds(matrix_seeds, batch_24_seeds):
    """Save extracted seeds for testing"""

    output_data = {
        'matrix_diagonal_seeds': matrix_seeds,
        'batch_24_plus_seeds': batch_24_seeds,
        'extraction_timestamp': str(Path(__file__).stat().st_mtime),
    }

    output_file = Path("extracted_matrix_seeds.json")
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n💾 Extracted seeds saved to: {output_file}")

    return output_file

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("🚀 MATRIX-BASED SEED EXTRACTION\n")

    # Extract seeds from matrix diagonal positions
    print("Phase 1: Matrix Diagonal Seeds")
    matrix_seeds = find_matrix_position_seeds()

    print("\n")

    # Extract Batch 24+ seeds
    print("Phase 2: Batch 24+ Seeds")
    batch_24_seeds = extract_batch_24_plus_seeds()

    # Save results
    output_file = save_extracted_seeds(matrix_seeds, batch_24_seeds)

    # Summary
    print("\n" + "=" * 80)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"\n✅ Matrix diagonal seeds: {len(matrix_seeds)}")
    print(f"✅ Batch 24+ seeds: {len(batch_24_seeds)}")
    print(f"\nTotal new seeds to test: {len(matrix_seeds) + len(batch_24_seeds)}")

    if matrix_seeds:
        print(f"\n🎯 Matrix seeds by block:")
        for block, info in sorted(matrix_seeds.items()):
            print(f"   Block {block}: {info['seed'][:40]}... (via {info['strategy']})")

    print("\n" + "=" * 80)
    print("✅ EXTRACTION COMPLETE!")
    print("=" * 80)
    print(f"\nNext step: Test these seeds against Genesis addresses")
    print(f"Run: python test_extracted_matrix_seeds.py")

if __name__ == "__main__":
    main()
