#!/usr/bin/env python3
"""
BITCOIN ADDRESS GENERATION FROM ANNA MATRIX DATA
=================================================
Generates real P2PKH Bitcoin addresses from Anna Matrix-derived private keys
using ecdsa (SECP256k1) + hashlib, then checks selected addresses on blockchain.

Methods:
  A - Palindrome Seeds (68 asymmetric cells)
  B - Attractor State Seeds (period-4 attractor)
  C - Row Seeds (all 128 rows)
  D - Special Row Seeds (factory rows, anomalous row 26)
  E - Column Pair Seeds (4 asymmetric column pairs)
"""

import json
import hashlib
import struct
import time
import sys
import os
from collections import defaultdict

import ecdsa
from ecdsa import SECP256k1, SigningKey
import numpy as np

# ============================================================
# PATHS
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
MATRIX_PATH = os.path.join(PROJECT_ROOT, "apps/web/public/data/anna-matrix.json")
PATOSHI_PATH = os.path.join(PROJECT_ROOT, "apps/web/public/data/patoshi-addresses.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "BITCOIN_ADDRESS_RESULTS.json")

# ============================================================
# BASE58 ENCODING
# ============================================================
BASE58_ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(data):
    """Encode bytes to Base58."""
    n = int.from_bytes(data, 'big')
    result = []
    while n > 0:
        n, remainder = divmod(n, 58)
        result.append(BASE58_ALPHABET[remainder:remainder+1])
    # Handle leading zero bytes
    for byte in data:
        if byte == 0:
            result.append(b'1')
        else:
            break
    return b''.join(reversed(result)).decode('ascii')


def base58check_encode(version, payload):
    """Base58Check encode with version byte and checksum."""
    versioned = bytes([version]) + payload
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    return base58_encode(versioned + checksum)


# ============================================================
# BITCOIN ADDRESS GENERATION
# ============================================================
def private_key_to_addresses(priv_key_bytes):
    """
    Given a 32-byte private key, generate both compressed and uncompressed
    P2PKH Bitcoin addresses.
    """
    if len(priv_key_bytes) != 32:
        raise ValueError("Private key must be 32 bytes, got %d" % len(priv_key_bytes))

    # Validate private key is in valid range for SECP256k1
    key_int = int.from_bytes(priv_key_bytes, 'big')
    order = SECP256k1.order
    if key_int == 0 or key_int >= order:
        key_int = (key_int % (order - 1)) + 1
        priv_key_bytes = key_int.to_bytes(32, 'big')

    sk = SigningKey.from_string(priv_key_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()

    # Uncompressed public key: 04 + x (32 bytes) + y (32 bytes)
    uncompressed_pub = b'\x04' + vk.to_string()

    # Compressed public key: 02/03 + x (32 bytes)
    x = vk.to_string()[:32]
    y = vk.to_string()[32:]
    y_int = int.from_bytes(y, 'big')
    prefix = b'\x02' if y_int % 2 == 0 else b'\x03'
    compressed_pub = prefix + x

    def pubkey_to_address(pubkey_bytes):
        sha256_hash = hashlib.sha256(pubkey_bytes).digest()
        ripemd160 = hashlib.new('ripemd160', sha256_hash).digest()
        return base58check_encode(0x00, ripemd160)

    return {
        'privkey_hex': priv_key_bytes.hex(),
        'uncompressed_address': pubkey_to_address(uncompressed_pub),
        'compressed_address': pubkey_to_address(compressed_pub),
        'uncompressed_pubkey': uncompressed_pub.hex(),
        'compressed_pubkey': compressed_pub.hex(),
    }


def seed_to_private_key(seed_bytes):
    """SHA256 hash of seed to produce a 32-byte private key."""
    return hashlib.sha256(seed_bytes).digest()


def signed_to_unsigned(val):
    """Convert signed byte to unsigned byte for binary representation."""
    return val & 0xFF


# ============================================================
# LOAD DATA
# ============================================================
print("=" * 70)
print("  BITCOIN ADDRESS GENERATION FROM ANNA MATRIX")
print("=" * 70)

print("\n[1] Loading Anna Matrix...")
with open(MATRIX_PATH, 'r') as f:
    data = json.load(f)
raw_matrix = data['matrix']
assert len(raw_matrix) == 128, "Expected 128 rows, got %d" % len(raw_matrix)
assert len(raw_matrix[0]) == 128, "Expected 128 cols, got %d" % len(raw_matrix[0])

# Convert any non-int values (e.g. '00000000' strings) to 0
matrix = []
non_int_count = 0
for r in range(128):
    row = []
    for c in range(128):
        val = raw_matrix[r][c]
        if isinstance(val, int):
            row.append(val)
        else:
            row.append(0)
            non_int_count += 1
    matrix.append(row)

print("    Matrix loaded: %dx%d" % (len(matrix), len(matrix[0])))
if non_int_count > 0:
    print("    Note: Converted %d non-integer entries to 0" % non_int_count)

# Load Patoshi data
print("\n[2] Loading Patoshi addresses...")
patoshi_pubkeys = []
patoshi_addresses = set()
try:
    with open(PATOSHI_PATH, 'r') as f:
        patoshi_data = json.load(f)
    records = patoshi_data.get('records', [])[:100]
    for rec in records:
        pk_hex = rec.get('pubkey', '')
        if pk_hex:
            patoshi_pubkeys.append(pk_hex)
            pk_bytes = bytes.fromhex(pk_hex)
            sha256_hash = hashlib.sha256(pk_bytes).digest()
            ripemd160 = hashlib.new('ripemd160', sha256_hash).digest()
            addr = base58check_encode(0x00, ripemd160)
            patoshi_addresses.add(addr)
    print("    Loaded %d Patoshi addresses (from first 100 records)" % len(patoshi_addresses))
except Exception as e:
    print("    Warning: Could not load Patoshi data: %s" % e)

# Known POCC/HASV Qubic addresses
POCC_QUBIC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV_QUBIC = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

# ============================================================
# RESULTS STORAGE
# ============================================================
all_results = {
    'metadata': {
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
        'matrix_size': '128x128',
        'methods': ['A_palindrome', 'B_attractor', 'C_rows', 'D_special_rows', 'E_column_pairs'],
    },
    'methods': {},
    'interesting_prefixes': [],
    'patoshi_matches': [],
    'blockchain_checks': [],
    'summary': {},
}

all_addresses = []  # (method, label, compressed_addr, uncompressed_addr, details)

# ============================================================
# METHOD A: Palindrome Seeds (68 Asymmetric Cells)
# ============================================================
print("\n" + "=" * 70)
print("  METHOD A: Palindrome Seeds (68 Asymmetric Cells)")
print("=" * 70)

ASYM_COL_PAIRS = [(0, 127), (22, 105), (30, 97), (41, 86)]

# Find asymmetric cells: M[r,c] + M[127-r,127-c] != -1
asymmetric_cells = []
for r in range(128):
    for c in range(128):
        mr = 127 - r
        mc = 127 - c
        if r < mr or (r == mr and c < mc):
            val1 = matrix[r][c]
            val2 = matrix[mr][mc]
            if val1 + val2 != -1:
                asymmetric_cells.append((r, c, val1, mr, mc, val2))

print("    Found %d asymmetric cell pairs (expecting 34 pairs = 68 cells)" % len(asymmetric_cells))

method_a_results = []

# A1: Concatenate all 34 independent values
independent_vals = [cell[2] for cell in asymmetric_cells]
seed_bytes = bytes([signed_to_unsigned(v) for v in independent_vals])
priv_key = seed_to_private_key(seed_bytes)
addr_data = private_key_to_addresses(priv_key)
label = "A1_all_palindrome_values"
method_a_results.append({
    'label': label,
    'seed_description': 'SHA256 of %d independent asymmetric values' % len(independent_vals),
    'seed_hex': seed_bytes.hex(),
    **addr_data,
})
all_addresses.append(('A', label, addr_data['compressed_address'], addr_data['uncompressed_address'], addr_data))
print("    A1 (all palindrome values): %s" % addr_data['compressed_address'])

# A2: Mirror values concatenated
mirror_vals = [cell[5] for cell in asymmetric_cells]
seed_bytes2 = bytes([signed_to_unsigned(v) for v in mirror_vals])
priv_key2 = seed_to_private_key(seed_bytes2)
addr_data2 = private_key_to_addresses(priv_key2)
label2 = "A2_mirror_palindrome_values"
method_a_results.append({
    'label': label2,
    'seed_description': 'SHA256 of %d mirror asymmetric values' % len(mirror_vals),
    'seed_hex': seed_bytes2.hex(),
    **addr_data2,
})
all_addresses.append(('A', label2, addr_data2['compressed_address'], addr_data2['uncompressed_address'], addr_data2))
print("    A2 (mirror palindrome values): %s" % addr_data2['compressed_address'])

# A3: Each column pair's values separately
for (c1, c2) in ASYM_COL_PAIRS:
    col_vals = [matrix[r][c1] for r in range(128)]
    seed_c1 = bytes([signed_to_unsigned(v) for v in col_vals])
    pk_c1 = seed_to_private_key(seed_c1)
    ad_c1 = private_key_to_addresses(pk_c1)
    lbl_c1 = "A3_col%d_seed" % c1
    method_a_results.append({'label': lbl_c1, 'seed_description': 'SHA256 of column %d' % c1, **ad_c1})
    all_addresses.append(('A', lbl_c1, ad_c1['compressed_address'], ad_c1['uncompressed_address'], ad_c1))

    col_vals2 = [matrix[r][c2] for r in range(128)]
    seed_c2 = bytes([signed_to_unsigned(v) for v in col_vals2])
    pk_c2 = seed_to_private_key(seed_c2)
    ad_c2 = private_key_to_addresses(pk_c2)
    lbl_c2 = "A3_col%d_seed" % c2
    method_a_results.append({'label': lbl_c2, 'seed_description': 'SHA256 of column %d' % c2, **ad_c2})
    all_addresses.append(('A', lbl_c2, ad_c2['compressed_address'], ad_c2['uncompressed_address'], ad_c2))

    combined = col_vals + col_vals2
    seed_pair = bytes([signed_to_unsigned(v) for v in combined])
    pk_pair = seed_to_private_key(seed_pair)
    ad_pair = private_key_to_addresses(pk_pair)
    lbl_pair = "A3_colpair_%d_%d_seed" % (c1, c2)
    method_a_results.append({'label': lbl_pair, 'seed_description': 'SHA256 of columns %d+%d' % (c1, c2), **ad_pair})
    all_addresses.append(('A', lbl_pair, ad_pair['compressed_address'], ad_pair['uncompressed_address'], ad_pair))
    print("    A3 col pair (%d,%d): %s" % (c1, c2, ad_pair['compressed_address']))

# A4: Raw asymmetric values padded to 32 bytes
if len(independent_vals) <= 32:
    raw_key = bytes([signed_to_unsigned(v) for v in independent_vals])
    raw_key = raw_key.ljust(32, b'\x00')
    try:
        ad_raw = private_key_to_addresses(raw_key)
        lbl_raw = "A4_raw_palindrome_padded"
        method_a_results.append({'label': lbl_raw, 'seed_description': 'Raw asymmetric values padded to 32 bytes', **ad_raw})
        all_addresses.append(('A', lbl_raw, ad_raw['compressed_address'], ad_raw['uncompressed_address'], ad_raw))
        print("    A4 (raw padded): %s" % ad_raw['compressed_address'])
    except Exception as e:
        print("    A4 (raw padded): Failed - %s" % e)

all_results['methods']['A_palindrome'] = {
    'description': 'Bitcoin addresses from 68 asymmetric (palindrome) cells',
    'asymmetric_cell_count': len(asymmetric_cells),
    'column_pairs': ASYM_COL_PAIRS,
    'addresses': method_a_results,
}
print("    Total Method A addresses: %d" % len(method_a_results))

# ============================================================
# METHOD B: Attractor State Seeds
# ============================================================
print("\n" + "=" * 70)
print("  METHOD B: Attractor State Seeds (Period-4)")
print("=" * 70)

method_b_results = []

M = np.array(matrix, dtype=np.int8)

# Iterate to find attractor cycle
state = np.ones(128, dtype=np.float64)
state = state / np.linalg.norm(state)

attractor_states = []
for iteration in range(2000):
    new_state = M.astype(np.float64) @ state
    if iteration > 1990:
        clipped = np.clip(np.round(new_state / (np.max(np.abs(new_state)) + 1e-10) * 127), -128, 127).astype(np.int8)
        attractor_states.append(clipped.copy())
    norm = np.linalg.norm(new_state)
    if norm > 0:
        state = new_state / norm
    else:
        state = new_state

if len(attractor_states) >= 4:
    attractor_states = attractor_states[-4:]

attractor_sums = [-43, -42, 43, 42]

for i, astate in enumerate(attractor_states):
    asum = int(np.sum(astate))
    seed_bytes = bytes([signed_to_unsigned(int(v)) for v in astate])
    priv_key = seed_to_private_key(seed_bytes)
    addr_data = private_key_to_addresses(priv_key)
    label = "B1_attractor_state_%d_sum%d" % (i, asum)
    method_b_results.append({
        'label': label,
        'seed_description': 'SHA256 of attractor state %d (sum=%d)' % (i, asum),
        'state_sum': asum,
        **addr_data,
    })
    all_addresses.append(('B', label, addr_data['compressed_address'], addr_data['uncompressed_address'], addr_data))
    print("    B1 state %d (sum=%d): %s" % (i, asum, addr_data['compressed_address']))

# B2: Attractor sums as seeds
for asum in attractor_sums:
    seed = struct.pack('>i', asum)
    priv_key = seed_to_private_key(seed)
    addr_data = private_key_to_addresses(priv_key)
    label = "B2_attractor_sum_%d" % asum
    method_b_results.append({
        'label': label,
        'seed_description': 'SHA256 of attractor sum value %d' % asum,
        **addr_data,
    })
    all_addresses.append(('B', label, addr_data['compressed_address'], addr_data['uncompressed_address'], addr_data))
    print("    B2 sum %d: %s" % (asum, addr_data['compressed_address']))

# B3: All 4 attractor sums concatenated
all_sums_seed = b''.join(struct.pack('>i', s) for s in attractor_sums)
priv_key = seed_to_private_key(all_sums_seed)
addr_data = private_key_to_addresses(priv_key)
label = "B3_all_attractor_sums"
method_b_results.append({
    'label': label,
    'seed_description': 'SHA256 of all 4 attractor sums concatenated',
    **addr_data,
})
all_addresses.append(('B', label, addr_data['compressed_address'], addr_data['uncompressed_address'], addr_data))
print("    B3 (all sums): %s" % addr_data['compressed_address'])

all_results['methods']['B_attractor'] = {
    'description': 'Bitcoin addresses from period-4 attractor states',
    'attractor_sums': attractor_sums,
    'addresses': method_b_results,
}
print("    Total Method B addresses: %d" % len(method_b_results))

# ============================================================
# METHOD C: Row Seeds (all 128 rows)
# ============================================================
print("\n" + "=" * 70)
print("  METHOD C: Row Seeds (All 128 Rows)")
print("=" * 70)

method_c_results = []
for row_idx in range(128):
    row = matrix[row_idx]
    row_sum = sum(row)
    seed_bytes = bytes([signed_to_unsigned(v) for v in row])
    priv_key = seed_to_private_key(seed_bytes)
    addr_data = private_key_to_addresses(priv_key)
    label = "C_row%03d_sum%d" % (row_idx, row_sum)
    method_c_results.append({
        'label': label,
        'row_index': row_idx,
        'row_sum': row_sum,
        **addr_data,
    })
    all_addresses.append(('C', label, addr_data['compressed_address'], addr_data['uncompressed_address'], addr_data))

print("    Generated %d row-based addresses" % len(method_c_results))
for r in method_c_results[:5]:
    print("    %s: %s" % (r['label'], r['compressed_address']))
print("    ...")
for r in method_c_results[-3:]:
    print("    %s: %s" % (r['label'], r['compressed_address']))

all_results['methods']['C_rows'] = {
    'description': 'Bitcoin addresses from each of 128 matrix rows',
    'count': len(method_c_results),
    'addresses': method_c_results,
}

# ============================================================
# METHOD D: Special Rows
# ============================================================
print("\n" + "=" * 70)
print("  METHOD D: Special Row Seeds")
print("=" * 70)

SPECIAL_ROWS = {
    1: "factory_row_neg114",
    9: "factory_row_125",
    49: "factory_row_14",
    57: "factory_row_6",
    26: "anomalous_pacemaker_neuron",
    0: "first_row",
    63: "mid_row_63",
    64: "mid_row_64",
    127: "last_row",
}

method_d_results = []
for row_idx, desc in SPECIAL_ROWS.items():
    row = matrix[row_idx]
    row_sum = sum(row)

    # D1: SHA256 of raw row bytes
    seed_bytes = bytes([signed_to_unsigned(v) for v in row])
    priv_key = seed_to_private_key(seed_bytes)
    addr_data = private_key_to_addresses(priv_key)
    label = "D1_row%d_%s" % (row_idx, desc)
    method_d_results.append({
        'label': label,
        'row_index': row_idx,
        'description': desc,
        'row_sum': row_sum,
        **addr_data,
    })
    all_addresses.append(('D', label, addr_data['compressed_address'], addr_data['uncompressed_address'], addr_data))
    print("    D1 row %3d (%-30s sum=%4d): %s" % (row_idx, desc, row_sum, addr_data['compressed_address']))

    # D2: Double-SHA256 of raw row bytes
    double_hash = hashlib.sha256(hashlib.sha256(seed_bytes).digest()).digest()
    addr_data2 = private_key_to_addresses(double_hash)
    label2 = "D2_row%d_%s_double_sha256" % (row_idx, desc)
    method_d_results.append({
        'label': label2,
        'row_index': row_idx,
        'description': desc + '_double_sha256',
        'row_sum': row_sum,
        **addr_data2,
    })
    all_addresses.append(('D', label2, addr_data2['compressed_address'], addr_data2['uncompressed_address'], addr_data2))

all_results['methods']['D_special_rows'] = {
    'description': 'Bitcoin addresses from special matrix rows',
    'special_rows': {str(k): v for k, v in SPECIAL_ROWS.items()},
    'addresses': method_d_results,
}
print("    Total Method D addresses: %d" % len(method_d_results))

# ============================================================
# METHOD E: Column Pair Seeds
# ============================================================
print("\n" + "=" * 70)
print("  METHOD E: Column Pair Seeds (Asymmetric Columns)")
print("=" * 70)

method_e_results = []
asym_columns = [0, 22, 30, 41, 86, 97, 105, 127]

for col_idx in asym_columns:
    col_vals = [matrix[r][col_idx] for r in range(128)]
    col_sum = sum(col_vals)
    seed_bytes = bytes([signed_to_unsigned(v) for v in col_vals])
    priv_key = seed_to_private_key(seed_bytes)
    addr_data = private_key_to_addresses(priv_key)
    label = "E1_col%03d_sum%d" % (col_idx, col_sum)
    method_e_results.append({
        'label': label,
        'column_index': col_idx,
        'column_sum': col_sum,
        **addr_data,
    })
    all_addresses.append(('E', label, addr_data['compressed_address'], addr_data['uncompressed_address'], addr_data))
    print("    E1 col %3d (sum=%5d): %s" % (col_idx, col_sum, addr_data['compressed_address']))

# E2: Column pairs concatenated
for (c1, c2) in ASYM_COL_PAIRS:
    col1 = [matrix[r][c1] for r in range(128)]
    col2 = [matrix[r][c2] for r in range(128)]
    combined = col1 + col2
    seed_bytes = bytes([signed_to_unsigned(v) for v in combined])
    priv_key = seed_to_private_key(seed_bytes)
    addr_data = private_key_to_addresses(priv_key)
    label = "E2_colpair_%d_%d" % (c1, c2)
    method_e_results.append({'label': label, **addr_data})
    all_addresses.append(('E', label, addr_data['compressed_address'], addr_data['uncompressed_address'], addr_data))
    print("    E2 pair (%3d,%3d): %s" % (c1, c2, addr_data['compressed_address']))

# E3: All asymmetric columns concatenated
all_asym_vals = []
for col_idx in asym_columns:
    all_asym_vals.extend([matrix[r][col_idx] for r in range(128)])
seed_bytes = bytes([signed_to_unsigned(v) for v in all_asym_vals])
priv_key = seed_to_private_key(seed_bytes)
addr_data = private_key_to_addresses(priv_key)
label = "E3_all_asym_columns"
method_e_results.append({
    'label': label,
    'seed_description': 'SHA256 of all %d asymmetric columns concatenated' % len(asym_columns),
    **addr_data,
})
all_addresses.append(('E', label, addr_data['compressed_address'], addr_data['uncompressed_address'], addr_data))
print("    E3 (all asym cols): %s" % addr_data['compressed_address'])

# E4: Full matrix flattened as seed
full_matrix_vals = []
for r in range(128):
    for c in range(128):
        full_matrix_vals.append(matrix[r][c])
seed_bytes = bytes([signed_to_unsigned(v) for v in full_matrix_vals])
priv_key = seed_to_private_key(seed_bytes)
addr_data = private_key_to_addresses(priv_key)
label = "E4_full_matrix"
method_e_results.append({
    'label': label,
    'seed_description': 'SHA256 of entire 128x128 matrix flattened',
    **addr_data,
})
all_addresses.append(('E', label, addr_data['compressed_address'], addr_data['uncompressed_address'], addr_data))
print("    E4 (full matrix): %s" % addr_data['compressed_address'])

all_results['methods']['E_column_pairs'] = {
    'description': 'Bitcoin addresses from asymmetric column pairs and full matrix',
    'asymmetric_columns': asym_columns,
    'addresses': method_e_results,
}
print("    Total Method E addresses: %d" % len(method_e_results))

# ============================================================
# PART 4: Pattern Analysis
# ============================================================
print("\n" + "=" * 70)
print("  PART 4: Pattern Analysis")
print("=" * 70)

INTERESTING_PREFIXES = [
    '1CFB', '1cfb',
    '1Anna', '1anna', '1ANNA',
    '1Qub', '1qub', '1QUB',
    '1Sat', '1sat', '1SAT',
    '1Bit', '1bit', '1BIT',
    '1God', '1god',
    '1Gen', '1gen',
    '1Bri', '1bri',
    '1Mat', '1mat',
    '1Poi', '1poi',
    '1Has', '1has',
    '1Aig', '1aig',
    '1Pal', '1pal',
    '1A1z', '1111',
    '1Nak', '1nak',
]

total_addresses = len(all_addresses)
print("\n    Total address entries: %d" % total_addresses)
print("    (Each has compressed + uncompressed = %d unique Bitcoin addresses)" % (total_addresses * 2))

# Check for interesting prefixes
prefix_matches = defaultdict(list)
for method, label, comp_addr, uncomp_addr, details in all_addresses:
    for prefix in INTERESTING_PREFIXES:
        if comp_addr.startswith(prefix):
            prefix_matches[prefix].append({
                'method': method, 'label': label, 'address': comp_addr, 'type': 'compressed',
            })
        if uncomp_addr.startswith(prefix):
            prefix_matches[prefix].append({
                'method': method, 'label': label, 'address': uncomp_addr, 'type': 'uncompressed',
            })

if prefix_matches:
    print("\n    INTERESTING PREFIX MATCHES FOUND:")
    for prefix, matches in sorted(prefix_matches.items()):
        print("\n    Prefix '%s':" % prefix)
        for m in matches:
            print("      [%s] %s -> %s (%s)" % (m['method'], m['label'], m['address'], m['type']))
        all_results['interesting_prefixes'].extend([
            {'prefix': prefix, **m} for m in matches
        ])
else:
    print("\n    No interesting prefix matches found (expected for SHA256-derived keys)")

# 3-character prefix distribution
print("\n    Checking 3-character prefix distribution...")
prefix_3_counts = defaultdict(int)
prefix_3_examples = defaultdict(list)
for method, label, comp_addr, uncomp_addr, details in all_addresses:
    for addr in [comp_addr, uncomp_addr]:
        p3 = addr[:3]
        prefix_3_counts[p3] += 1
        if len(prefix_3_examples[p3]) < 2:
            prefix_3_examples[p3].append("[%s] %s: %s" % (method, label, addr))

sorted_prefixes = sorted(prefix_3_counts.items(), key=lambda x: -x[1])
print("\n    Top 10 most common 3-char prefixes:")
for prefix, count in sorted_prefixes[:10]:
    print("      %s: %d addresses" % (prefix, count))
    for ex in prefix_3_examples[prefix][:1]:
        print("        e.g. %s" % ex)

# 2-character prefixes of special interest
print("\n    Checking 2-character prefixes of special interest:")
special_2char = ['1C', '1A', '1Q', '1S', '1B', '1G', '1N', '1M', '1H', '1P']
for sp in special_2char:
    count = 0
    examples = []
    for method, label, comp_addr, uncomp_addr, details in all_addresses:
        for addr in [comp_addr, uncomp_addr]:
            if addr.startswith(sp):
                count += 1
                if len(examples) < 1:
                    examples.append(addr)
    if count > 0:
        print("      %s: %d addresses (e.g. %s)" % (sp, count, examples[0] if examples else ""))

# Patoshi check
print("\n    Checking against Patoshi addresses...")
patoshi_match_count = 0
for method, label, comp_addr, uncomp_addr, details in all_addresses:
    if comp_addr in patoshi_addresses:
        print("    *** PATOSHI MATCH (compressed): [%s] %s: %s" % (method, label, comp_addr))
        all_results['patoshi_matches'].append({
            'method': method, 'label': label, 'address': comp_addr, 'type': 'compressed'
        })
        patoshi_match_count += 1
    if uncomp_addr in patoshi_addresses:
        print("    *** PATOSHI MATCH (uncompressed): [%s] %s: %s" % (method, label, uncomp_addr))
        all_results['patoshi_matches'].append({
            'method': method, 'label': label, 'address': uncomp_addr, 'type': 'uncompressed'
        })
        patoshi_match_count += 1

if patoshi_match_count == 0:
    print("    No Patoshi matches found (expected - collision probability ~0)")

# ============================================================
# PART 3: Blockchain Check
# ============================================================
print("\n" + "=" * 70)
print("  PART 3: Blockchain Check (blockstream.info API)")
print("=" * 70)

# Select most interesting addresses to check (max 20)
addresses_to_check = []

# Priority 1: Palindrome-derived (Method A)
for method, label, comp_addr, uncomp_addr, details in all_addresses:
    if method == 'A' and len(addresses_to_check) < 6:
        addresses_to_check.append((method, label, comp_addr, 'compressed'))

# Priority 2: Attractor states (Method B)
for method, label, comp_addr, uncomp_addr, details in all_addresses:
    if method == 'B' and 'B1_' in label and len(addresses_to_check) < 10:
        addresses_to_check.append((method, label, comp_addr, 'compressed'))

# Priority 3: Special rows (Method D)
for method, label, comp_addr, uncomp_addr, details in all_addresses:
    if method == 'D' and 'D1_' in label and len(addresses_to_check) < 16:
        addresses_to_check.append((method, label, comp_addr, 'compressed'))

# Priority 4: Full matrix / all asymmetric (Method E)
for method, label, comp_addr, uncomp_addr, details in all_addresses:
    if method == 'E' and ('E3_' in label or 'E4_' in label) and len(addresses_to_check) < 18:
        addresses_to_check.append((method, label, comp_addr, 'compressed'))

# Also check uncompressed versions of most interesting
for method, label, comp_addr, uncomp_addr, details in all_addresses:
    if method == 'A' and 'A1_' in label and len(addresses_to_check) < 20:
        addresses_to_check.append((method, label, uncomp_addr, 'uncompressed'))
    if method == 'E' and 'E4_' in label and len(addresses_to_check) < 20:
        addresses_to_check.append((method, label, uncomp_addr, 'uncompressed'))

print("\n    Checking %d addresses on blockchain..." % len(addresses_to_check))
print("    Rate limit: 1 request/second, max 20 checks")

import urllib.request
import urllib.error

blockchain_results = []
for i, (method, label, address, addr_type) in enumerate(addresses_to_check[:20]):
    url = "https://blockstream.info/api/address/%s" % address
    print("\n    [%2d/%d] Checking %s... (%s)" % (i+1, min(len(addresses_to_check), 20), address[:25], label[:30]))

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 AnnaMatrix-Research'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_data = json.loads(resp.read().decode())

            tx_count = resp_data.get('chain_stats', {}).get('tx_count', 0)
            funded = resp_data.get('chain_stats', {}).get('funded_txo_sum', 0)
            spent = resp_data.get('chain_stats', {}).get('spent_txo_sum', 0)
            balance = funded - spent

            result = {
                'method': method,
                'label': label,
                'address': address,
                'address_type': addr_type,
                'tx_count': tx_count,
                'funded_satoshis': funded,
                'spent_satoshis': spent,
                'balance_satoshis': balance,
                'has_activity': tx_count > 0,
            }
            blockchain_results.append(result)

            if tx_count > 0:
                print("    *** ACTIVITY FOUND! tx_count=%d, balance=%d sat" % (tx_count, balance))
            else:
                print("        No activity (0 transactions)")

    except urllib.error.HTTPError as e:
        print("        HTTP Error: %d %s" % (e.code, e.reason))
        blockchain_results.append({
            'method': method, 'label': label, 'address': address,
            'address_type': addr_type, 'error': 'HTTP %d' % e.code,
            'has_activity': False,
        })
    except Exception as e:
        print("        Error: %s" % e)
        blockchain_results.append({
            'method': method, 'label': label, 'address': address,
            'address_type': addr_type, 'error': str(e),
            'has_activity': False,
        })

    # Rate limit
    if i < len(addresses_to_check) - 1:
        time.sleep(1.1)

all_results['blockchain_checks'] = blockchain_results

active = [r for r in blockchain_results if r.get('has_activity')]
print("\n    Blockchain check complete.")
print("    Addresses with activity: %d/%d" % (len(active), len(blockchain_results)))
if active:
    print("\n    ACTIVE ADDRESSES:")
    for r in active:
        print("      [%s] %s" % (r['method'], r['label']))
        print("        Address: %s" % r['address'])
        print("        Transactions: %d" % r['tx_count'])
        print("        Balance: %d satoshis" % r['balance_satoshis'])

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("  SUMMARY")
print("=" * 70)

summary = {
    'total_address_entries': total_addresses,
    'total_unique_bitcoin_addresses': total_addresses * 2,
    'method_counts': {
        'A_palindrome': len(all_results['methods']['A_palindrome']['addresses']),
        'B_attractor': len(all_results['methods']['B_attractor']['addresses']),
        'C_rows': len(all_results['methods']['C_rows']['addresses']),
        'D_special_rows': len(all_results['methods']['D_special_rows']['addresses']),
        'E_column_pairs': len(all_results['methods']['E_column_pairs']['addresses']),
    },
    'interesting_prefix_matches': len(all_results['interesting_prefixes']),
    'patoshi_matches': len(all_results['patoshi_matches']),
    'blockchain_checks_performed': len(blockchain_results),
    'addresses_with_activity': len(active),
    'active_addresses': active if active else 'None found',
}

all_results['summary'] = summary

print("\n    Addresses by method:")
for method, count in summary['method_counts'].items():
    print("      %s: %d" % (method, count))
print("\n    Interesting prefix matches: %d" % summary['interesting_prefix_matches'])
print("    Patoshi matches: %d" % summary['patoshi_matches'])
print("    Blockchain checks: %d" % summary['blockchain_checks_performed'])
print("    Addresses with activity: %d" % summary['addresses_with_activity'])

# Save results
print("\n    Saving results to: %s" % OUTPUT_PATH)
with open(OUTPUT_PATH, 'w') as f:
    json.dump(all_results, f, indent=2, default=str)
print("    Results saved successfully.")

# ============================================================
# COMPLETE ADDRESS TABLE
# ============================================================
print("\n" + "=" * 70)
print("  COMPLETE ADDRESS TABLE (First 30)")
print("=" * 70)

print("\n    %-6s %-40s %-36s %-36s" % ('Method', 'Label', 'Compressed Address', 'Uncompressed Address'))
print("    " + "-" * 118)

for i, (method, label, comp, uncomp, _) in enumerate(all_addresses[:30]):
    short_label = label[:38]
    print("    %-6s %-40s %-36s %-36s" % (method, short_label, comp, uncomp))

if len(all_addresses) > 30:
    print("\n    ... and %d more addresses (see JSON output)" % (len(all_addresses) - 30))

print("\n" + "=" * 70)
print("  DONE")
print("=" * 70)
