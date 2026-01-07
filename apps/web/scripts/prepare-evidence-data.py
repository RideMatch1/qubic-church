#!/usr/bin/env python3
"""
Prepare evidence data for the frontend.
Converts CSV and JSON files to optimized format for virtualized tables.
"""

import csv
import json
from pathlib import Path

# Paths
BASE_DIR = Path("/Users/lukashertle/Developer/projects/qubic-mystery-lab")
OUTPUT_DIR = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data")

def prepare_patoshi_data():
    """Convert Patoshi CSV to JSON array format."""
    csv_path = BASE_DIR / "patoshi-addresses" / "patoshi_pubkeys_COMPLETE.csv"

    records = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "blockHeight": int(row["Block Height"]),
                "outputIndex": int(row["Output Index"]),
                "pubkey": row["Address/Pubkey"],
                "amount": float(row["Amount (BTC)"]),
                "scriptType": row["Script Type"]
            })

    output_path = OUTPUT_DIR / "patoshi-addresses.json"
    with open(output_path, 'w') as f:
        json.dump({
            "total": len(records),
            "records": records
        }, f)

    print(f"Patoshi: {len(records)} records -> {output_path}")
    return len(records)

def prepare_qubic_seeds():
    """Process Qubic seeds for frontend display - INCLUDING PRIVATE SEEDS."""
    json_path = BASE_DIR / "qubic-anna-lab-research" / "outputs" / "derived" / "complete_24846_seeds_to_real_ids_mapping.json"

    with open(json_path, 'r') as f:
        data = json.load(f)

    records = []
    for idx, item in enumerate(data.get("results", [])):
        records.append({
            "id": idx,
            "seed": item.get("seed", ""),  # PRIVATE SEED (55 chars)
            "documentedIdentity": item.get("documented_identity", ""),  # Public ID
            "realIdentity": item.get("real_identity", ""),  # Computed Public ID
            "match": item.get("match", False),
            "source": item.get("source", "")
        })

    output_path = OUTPUT_DIR / "qubic-seeds.json"
    with open(output_path, 'w') as f:
        json.dump({
            "total": len(records),
            "processed": data.get("processed", 0),
            "matches": data.get("matches", 0),
            "matchRate": data.get("match_rate", "0%"),
            "records": records
        }, f)

    print(f"Qubic Seeds: {len(records)} records -> {output_path}")
    return len(records)

def prepare_bitcoin_addresses_with_keys():
    """Process extracted Bitcoin addresses WITH private keys."""
    json_path = BASE_DIR / "outputs" / "all_extracted_bitcoin_addresses.json"

    with open(json_path, 'r') as f:
        data = json.load(f)

    addresses = data.get("addresses", {})
    records = []
    for idx, (address, info) in enumerate(addresses.items()):
        records.append({
            "id": idx,
            "address": address,
            "privateKey": info.get("key", ""),  # Private key hex
            "sequence": info.get("seq", ""),
            "method": info.get("method", "")
        })

    output_path = OUTPUT_DIR / "bitcoin-derived-addresses.json"
    with open(output_path, 'w') as f:
        json.dump({
            "total": len(records),
            "totalSequences": data.get("total_sequences", 0),
            "methods": data.get("methods", []),
            "timestamp": data.get("timestamp", ""),
            "records": records
        }, f)

    print(f"Bitcoin Derived Addresses: {len(records)} records -> {output_path}")
    return len(records)

def prepare_private_keys_database():
    """Process full private keys database with WIF format."""
    json_path = BASE_DIR / "outputs" / "phase11" / "private_keys_database.json"

    with open(json_path, 'r') as f:
        data = json.load(f)

    private_keys = data.get("private_keys", {})
    records = []
    for idx, (address, info) in enumerate(private_keys.items()):
        records.append({
            "id": idx,
            "address": address,
            "privateKeyHex": info.get("private_key_hex", ""),
            "privateKeyWIF": info.get("private_key_wif", ""),
            "position": info.get("position", []),
            "method": info.get("method", ""),
            "xorVariant": info.get("xor_variant", 0),
            "compressed": info.get("compressed", False),
            "hash160": info.get("hash160", ""),
            "cfVariant": info.get("cf_variant", ""),
            "validationStatus": info.get("validation_status", "")
        })

    output_path = OUTPUT_DIR / "bitcoin-private-keys.json"
    with open(output_path, 'w') as f:
        json.dump({
            "total": len(records),
            "extractionDate": data.get("extraction_date", ""),
            "successfullyExtracted": data.get("successfully_extracted", 0),
            "records": records
        }, f)

    print(f"Bitcoin Private Keys: {len(records)} records -> {output_path}")
    return len(records)

def prepare_all_matrix_addresses():
    """Process 900k+ Bitcoin addresses from matrix."""
    json_path = BASE_DIR / "outputs" / "all_matrix_addresses" / "all_unique_addresses.json"

    with open(json_path, 'r') as f:
        data = json.load(f)

    addresses = data.get("addresses", [])

    # For 900k addresses, we'll create a simplified format
    # Just addresses with index for virtualized table
    records = [{"id": i, "address": addr} for i, addr in enumerate(addresses)]

    output_path = OUTPUT_DIR / "matrix-addresses.json"
    with open(output_path, 'w') as f:
        json.dump({
            "total": len(records),
            "generated": data.get("generated", 0),
            "uniqueCount": data.get("unique_count", 0),
            "records": records
        }, f)

    print(f"Matrix Addresses: {len(records)} records -> {output_path}")
    return len(records)

def prepare_interesting_addresses():
    """Process addresses with derivation details."""
    json_path = BASE_DIR / "outputs" / "all_matrix_addresses" / "interesting_addresses_derivations.json"

    with open(json_path, 'r') as f:
        data = json.load(f)

    records = []
    for idx, (address, derivations) in enumerate(data.items()):
        for deriv in derivations:
            records.append({
                "id": idx,
                "address": address,
                "position": deriv.get("position", []),
                "method": deriv.get("method", ""),
                "xor": deriv.get("xor", 0),
                "compressed": deriv.get("compressed", False),
                "hash160": deriv.get("hash160", "")
            })

    output_path = OUTPUT_DIR / "interesting-addresses.json"
    with open(output_path, 'w') as f:
        json.dump({
            "total": len(records),
            "records": records
        }, f)

    print(f"Interesting Addresses: {len(records)} records -> {output_path}")
    return len(records)

def prepare_anna_matrix():
    """Copy Anna Matrix data if it exists."""
    matrix_path = BASE_DIR / "outputs" / "phase4" / "ANNA_MATRIX_128x128.json"

    if matrix_path.exists():
        with open(matrix_path, 'r') as f:
            data = json.load(f)

        output_path = OUTPUT_DIR / "anna-matrix.json"
        with open(output_path, 'w') as f:
            json.dump(data, f)

        print(f"Anna Matrix: copied -> {output_path}")
        return True
    else:
        print(f"Anna Matrix: not found at {matrix_path}")
        # Try alternative locations
        alt_paths = [
            BASE_DIR / "qubic-anna-lab-research" / "outputs" / "ANNA_MATRIX_128x128.json",
            BASE_DIR / "outputs" / "ANNA_MATRIX_128x128.json",
        ]
        for alt_path in alt_paths:
            if alt_path.exists():
                with open(alt_path, 'r') as f:
                    data = json.load(f)
                output_path = OUTPUT_DIR / "anna-matrix.json"
                with open(output_path, 'w') as f:
                    json.dump(data, f)
                print(f"Anna Matrix: copied from {alt_path} -> {output_path}")
                return True

        # Create placeholder
        matrix = [[0 for _ in range(128)] for _ in range(128)]
        output_path = OUTPUT_DIR / "anna-matrix.json"
        with open(output_path, 'w') as f:
            json.dump({"size": 128, "matrix": matrix}, f)
        print(f"Anna Matrix: placeholder created -> {output_path}")
        return False

def create_summary():
    """Create a summary statistics file."""
    summary = {
        "lastUpdated": "2026-01-05",
        "datasets": {
            "patoshi": {"file": "patoshi-addresses.json", "description": "Patoshi-era Bitcoin addresses with public keys"},
            "qubicSeeds": {"file": "qubic-seeds.json", "description": "Qubic seeds with public/private keys"},
            "bitcoinDerived": {"file": "bitcoin-derived-addresses.json", "description": "Bitcoin addresses derived from matrix"},
            "bitcoinPrivateKeys": {"file": "bitcoin-private-keys.json", "description": "Bitcoin addresses with full private keys (WIF)"},
            "matrixAddresses": {"file": "matrix-addresses.json", "description": "900k+ unique addresses from matrix generation"},
            "interestingAddresses": {"file": "interesting-addresses.json", "description": "Addresses with special patterns (1CFB, Patoshi, etc.)"},
            "annaMatrix": {"file": "anna-matrix.json", "size": 128, "description": "128x128 Anna Matrix"}
        }
    }

    output_path = OUTPUT_DIR / "summary.json"
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Summary: created -> {output_path}")

if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Preparing Evidence Data for Frontend")
    print("=" * 60)

    totals = {}
    totals['patoshi'] = prepare_patoshi_data()
    totals['qubic'] = prepare_qubic_seeds()
    totals['derived'] = prepare_bitcoin_addresses_with_keys()
    totals['privateKeys'] = prepare_private_keys_database()
    totals['matrix'] = prepare_all_matrix_addresses()
    totals['interesting'] = prepare_interesting_addresses()
    prepare_anna_matrix()
    create_summary()

    print("=" * 60)
    print("Summary:")
    print(f"  Patoshi addresses:    {totals['patoshi']:>10,}")
    print(f"  Qubic seeds:          {totals['qubic']:>10,}")
    print(f"  Derived BTC:          {totals['derived']:>10,}")
    print(f"  BTC Private Keys:     {totals['privateKeys']:>10,}")
    print(f"  Matrix addresses:     {totals['matrix']:>10,}")
    print(f"  Interesting:          {totals['interesting']:>10,}")
    print(f"  TOTAL:                {sum(totals.values()):>10,}")
    print("=" * 60)
