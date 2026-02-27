#!/usr/bin/env python3
"""
QUBIC ADDRESS SIGNIFICANCE ANALYSIS
====================================
Analysiert ob POCC und HASV Adressen statistisch besonders sind
und ob sie mit der Bitcoin Genesis-Adresse zusammenhängen.
"""

import json
import numpy as np
from collections import Counter
import hashlib
import random

# Load the Anna Matrix
MATRIX_FILE = "../public/data/anna-matrix.json"
with open(MATRIX_FILE, 'r') as f:
    data = json.load(f)
    matrix = np.array(data['matrix'], dtype=np.int8)

# Die zu analysierenden Adressen
POCC_ADDRESS = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV_ADDRESS = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"
BITCOIN_GENESIS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"

def char_to_num(c):
    """Convert character to 0-based number"""
    return ord(c.upper()) - ord('A')

def analyze_address_deep(address, name):
    """Tiefenanalyse einer Adresse"""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {name}")
    print(f"{'='*80}")
    print(f"Address: {address}")
    print(f"Length: {len(address)} chars")
    print()

    results = {
        'name': name,
        'address': address,
        'char_sum_0based': 0,
        'char_sum_1based': 0,
        'diagonal_values': [],
        'row6_lookups': [],
        'unique_patterns': set(),
        'special_chunks': []
    }

    # 1. Gesamtsumme der Zeichen
    results['char_sum_0based'] = sum(char_to_num(c) for c in address if c.isalpha())
    results['char_sum_1based'] = sum(char_to_num(c) + 1 for c in address if c.isalpha())

    print(f"[1] CHARACTER ANALYSIS")
    print(f"-" * 60)
    print(f"Sum (0-based): {results['char_sum_0based']}")
    print(f"Sum (1-based): {results['char_sum_1based']}")
    print(f"Average char value: {results['char_sum_0based'] / len(address):.2f}")
    print()

    # 2. Diagonal Values (jeder Buchstabe -> matrix[char][char])
    print(f"[2] DIAGONAL MATRIX VALUES (matrix[char][char])")
    print(f"-" * 60)
    diagonal_sum = 0
    for i, c in enumerate(address):
        if c.isalpha():
            idx = char_to_num(c)
            if 0 <= idx < 128:
                val = matrix[idx][idx]
                diagonal_sum += val
                results['diagonal_values'].append((c, idx, val))

    print(f"Diagonal sum: {diagonal_sum}")
    print(f"First 10 diagonal values:")
    for c, idx, val in results['diagonal_values'][:10]:
        print(f"  {c} (idx {idx:2d}) -> matrix[{idx}][{idx}] = {val:4d}")
    print()

    # 3. Row 6 Lookups für 4-char windows
    print(f"[3] ROW 6 LOOKUPS (4-char windows)")
    print(f"-" * 60)
    row6_sum = 0
    row6_values = []
    for i in range(len(address) - 3):
        chunk = address[i:i+4]
        chunk_sum = sum(char_to_num(c) for c in chunk if c.isalpha())

        if 0 <= chunk_sum < 128:
            row6_val = matrix[6][chunk_sum]
            row6_sum += row6_val
            row6_values.append(row6_val)
            results['row6_lookups'].append({
                'chunk': chunk,
                'sum': chunk_sum,
                'row6_value': row6_val
            })

    print(f"Total Row 6 sum: {row6_sum}")
    print(f"Average Row 6 value: {row6_sum / len(row6_values):.2f}")
    print(f"Row 6 value distribution: {Counter(row6_values).most_common(5)}")
    print()

    # 4. Spezielle Chunks finden
    print(f"[4] SPECIAL PATTERNS")
    print(f"-" * 60)

    # Chunks die auf sich selbst zeigen
    self_ref = [r for r in results['row6_lookups'] if r['sum'] == r['row6_value']]
    if self_ref:
        print(f"Self-referential chunks: {len(self_ref)}")
        for r in self_ref[:5]:
            print(f"  {r['chunk']} -> sum={r['sum']} -> [6,{r['sum']}]={r['row6_value']} (SELF!)")
    else:
        print("Self-referential chunks: 0")

    # Chunks mit extremen Werten
    sorted_by_row6 = sorted(results['row6_lookups'], key=lambda x: abs(x['row6_value']), reverse=True)
    print(f"\nHighest Row 6 values:")
    for r in sorted_by_row6[:5]:
        print(f"  {r['chunk']} -> [6,{r['sum']}] = {r['row6_value']}")

    print()

    # 5. Modulo-Analyse
    print(f"[5] MODULO PATTERNS")
    print(f"-" * 60)
    print(f"Sum mod 26: {results['char_sum_0based'] % 26}")
    print(f"Sum mod 128: {results['char_sum_0based'] % 128}")
    print(f"Sum mod 256: {results['char_sum_0based'] % 256}")
    print(f"Sum mod 676: {results['char_sum_0based'] % 676}")  # Qubic Computor count
    print()

    return results

def compare_addresses(pocc_results, hasv_results):
    """Vergleiche die beiden Adressen"""
    print(f"\n{'='*80}")
    print(f"CROSS-ADDRESS COMPARISON")
    print(f"{'='*80}")
    print()

    # 1. Summen-Vergleich
    print(f"[1] SUM COMPARISON")
    print(f"-" * 60)
    print(f"POCC sum (0-based): {pocc_results['char_sum_0based']}")
    print(f"HASV sum (0-based): {hasv_results['char_sum_0based']}")
    print(f"Difference: {abs(pocc_results['char_sum_0based'] - hasv_results['char_sum_0based'])}")
    print(f"Ratio: {pocc_results['char_sum_0based'] / hasv_results['char_sum_0based']:.4f}")
    print()

    # 2. Gemeinsame Row 6 Values
    print(f"[2] SHARED ROW 6 VALUES")
    print(f"-" * 60)
    pocc_row6_vals = set(r['row6_value'] for r in pocc_results['row6_lookups'])
    hasv_row6_vals = set(r['row6_value'] for r in hasv_results['row6_lookups'])
    common_vals = pocc_row6_vals & hasv_row6_vals
    print(f"Common Row 6 values: {len(common_vals)}")
    print(f"Examples: {list(common_vals)[:10]}")
    print()

    # 3. XOR der Summen
    print(f"[3] XOR ANALYSIS")
    print(f"-" * 60)
    xor_sum = pocc_results['char_sum_0based'] ^ hasv_results['char_sum_0based']
    print(f"POCC ⊕ HASV = {xor_sum}")
    print(f"Binary: {bin(xor_sum)}")
    print()

    # 4. Shared chunks (gleiche 4-char sequences)
    print(f"[4] SHARED CHUNKS")
    print(f"-" * 60)
    pocc_chunks = set(r['chunk'] for r in pocc_results['row6_lookups'])
    hasv_chunks = set(r['chunk'] for r in hasv_results['row6_lookups'])
    shared_chunks = pocc_chunks & hasv_chunks
    if shared_chunks:
        print(f"Shared 4-char chunks: {len(shared_chunks)}")
        for chunk in list(shared_chunks)[:10]:
            print(f"  {chunk}")
    else:
        print("No shared 4-char chunks")
    print()

def bitcoin_connection_test(pocc_results, hasv_results):
    """Teste Verbindung zur Bitcoin Genesis"""
    print(f"\n{'='*80}")
    print(f"BITCOIN GENESIS CONNECTION TEST")
    print(f"{'='*80}")
    print()

    # Bitcoin Genesis Block Details
    genesis_timestamp = 1231006505  # Unix timestamp
    genesis_height = 0
    genesis_bits = 0x1d00ffff
    genesis_nonce = 2083236893

    print(f"Bitcoin Genesis Block:")
    print(f"  Timestamp: {genesis_timestamp}")
    print(f"  Height: {genesis_height}")
    print(f"  Bits: {hex(genesis_bits)}")
    print(f"  Nonce: {genesis_nonce}")
    print()

    # Test ob Summen irgendwie mit Genesis korrelieren
    print(f"[1] TIMESTAMP MODULO TEST")
    print(f"-" * 60)
    print(f"POCC sum mod genesis_timestamp: {pocc_results['char_sum_0based'] % genesis_timestamp}")
    print(f"HASV sum mod genesis_timestamp: {hasv_results['char_sum_0based'] % genesis_timestamp}")
    print()

    print(f"[2] NONCE TEST")
    print(f"-" * 60)
    print(f"POCC sum mod nonce: {pocc_results['char_sum_0based'] % genesis_nonce}")
    print(f"HASV sum mod nonce: {hasv_results['char_sum_0based'] % genesis_nonce}")
    print()

    # Hash test
    print(f"[3] HASH DERIVATION TEST")
    print(f"-" * 60)
    pocc_hash = hashlib.sha256(POCC_ADDRESS.encode()).hexdigest()
    hasv_hash = hashlib.sha256(HASV_ADDRESS.encode()).hexdigest()
    bitcoin_addr_hash = hashlib.sha256(BITCOIN_GENESIS.encode()).hexdigest()

    print(f"POCC SHA256: {pocc_hash[:32]}...")
    print(f"HASV SHA256: {hasv_hash[:32]}...")
    print(f"BTC  SHA256: {bitcoin_addr_hash[:32]}...")
    print()

    # Check for any byte overlaps
    pocc_bytes = bytes.fromhex(pocc_hash)
    hasv_bytes = bytes.fromhex(hasv_hash)
    btc_bytes = bytes.fromhex(bitcoin_addr_hash)

    pocc_btc_xor = bytes(a ^ b for a, b in zip(pocc_bytes, btc_bytes))
    hasv_btc_xor = bytes(a ^ b for a, b in zip(hasv_bytes, btc_bytes))

    print(f"POCC ⊕ BTC (first 16 bytes): {pocc_btc_xor[:16].hex()}")
    print(f"HASV ⊕ BTC (first 16 bytes): {hasv_btc_xor[:16].hex()}")
    print()

def statistical_significance_test(pocc_results, hasv_results):
    """Teste ob diese Adressen statistisch besonders sind"""
    print(f"\n{'='*80}")
    print(f"STATISTICAL SIGNIFICANCE TEST")
    print(f"{'='*80}")
    print()

    print(f"Generating 1000 random addresses for comparison...")

    random.seed(42)
    random_sums = []
    random_row6_sums = []

    for i in range(1000):
        random_addr = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=60))

        # Sum
        addr_sum = sum(char_to_num(c) for c in random_addr)
        random_sums.append(addr_sum)

        # Row 6 sum
        row6_sum = 0
        for j in range(len(random_addr) - 3):
            chunk = random_addr[j:j+4]
            chunk_sum = sum(char_to_num(c) for c in chunk)
            if 0 <= chunk_sum < 128:
                row6_sum += matrix[6][chunk_sum]
        random_row6_sums.append(row6_sum)

    # Calculate percentiles
    random_sums.sort()
    random_row6_sums.sort()

    pocc_percentile = sum(1 for x in random_sums if x < pocc_results['char_sum_0based']) / 1000 * 100
    hasv_percentile = sum(1 for x in random_sums if x < hasv_results['char_sum_0based']) / 1000 * 100

    pocc_row6_sum = sum(r['row6_value'] for r in pocc_results['row6_lookups'])
    hasv_row6_sum = sum(r['row6_value'] for r in hasv_results['row6_lookups'])

    pocc_row6_percentile = sum(1 for x in random_row6_sums if x < pocc_row6_sum) / 1000 * 100
    hasv_row6_percentile = sum(1 for x in random_row6_sums if x < hasv_row6_sum) / 1000 * 100

    print(f"[1] CHARACTER SUM PERCENTILES")
    print(f"-" * 60)
    print(f"POCC sum: {pocc_results['char_sum_0based']} (percentile: {pocc_percentile:.1f}%)")
    print(f"HASV sum: {hasv_results['char_sum_0based']} (percentile: {hasv_percentile:.1f}%)")
    print(f"Random mean: {np.mean(random_sums):.1f} ± {np.std(random_sums):.1f}")
    print(f"Random range: [{min(random_sums)}, {max(random_sums)}]")
    print()

    print(f"[2] ROW 6 SUM PERCENTILES")
    print(f"-" * 60)
    print(f"POCC Row 6 sum: {pocc_row6_sum} (percentile: {pocc_row6_percentile:.1f}%)")
    print(f"HASV Row 6 sum: {hasv_row6_sum} (percentile: {hasv_row6_percentile:.1f}%)")
    print(f"Random mean: {np.mean(random_row6_sums):.1f} ± {np.std(random_row6_sums):.1f}")
    print(f"Random range: [{min(random_row6_sums)}, {max(random_row6_sums)}]")
    print()

    # Verdict
    print(f"[3] VERDICT")
    print(f"-" * 60)
    unusual_count = sum([
        pocc_percentile > 95 or pocc_percentile < 5,
        hasv_percentile > 95 or hasv_percentile < 5,
        pocc_row6_percentile > 95 or pocc_row6_percentile < 5,
        hasv_row6_percentile > 95 or hasv_row6_percentile < 5
    ])

    if unusual_count == 0:
        print("✓ BOTH ADDRESSES ARE STATISTICALLY NORMAL")
        print("  No evidence of special encoding or selection bias")
    elif unusual_count <= 2:
        print("⚠️ WEAK EVIDENCE OF UNUSUAL PROPERTIES")
        print("  Some metrics outside normal range, but could be chance")
    else:
        print("🔍 STATISTICALLY UNUSUAL ADDRESSES")
        print("  Multiple metrics exceed 95th percentile threshold")
        print("  Warrants deeper investigation")
    print()

def main():
    print("=" * 80)
    print("QUBIC ADDRESS SIGNIFICANCE ANALYSIS")
    print("=" * 80)
    print()
    print("Analyzing two key Qubic addresses:")
    print("  1. POCC (GENESIS Token Issuer)")
    print("  2. HASV (Discovered Address)")
    print()
    print("Questions:")
    print("  - Are these addresses statistically special?")
    print("  - Do they relate to Bitcoin Genesis?")
    print("  - What patterns exist in the Anna Matrix?")
    print()

    # Analyze both addresses
    pocc_results = analyze_address_deep(POCC_ADDRESS, "POCC (GENESIS Issuer)")
    hasv_results = analyze_address_deep(HASV_ADDRESS, "HASV (Discovered)")

    # Compare them
    compare_addresses(pocc_results, hasv_results)

    # Bitcoin connection
    bitcoin_connection_test(pocc_results, hasv_results)

    # Statistical test
    statistical_significance_test(pocc_results, hasv_results)

    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
