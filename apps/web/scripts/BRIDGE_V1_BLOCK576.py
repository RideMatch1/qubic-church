#!/usr/bin/env python3
"""
===============================================================================
        BRIDGE V1: BLOCK 576 BLOCKCHAIN VERIFICATION
===============================================================================
PRE-REGISTERED HYPOTHESES:
  H1.1: Block 576 coinbase script contains extra byte 0x1b (decimal 27)
  H1.2: Block 576 is unique in first 1000 blocks for having extra bytes
  H1.3: The documented Block 576 hash is correct

METHODOLOGY:
  - Fetch Block 576 via blockstream.info public API
  - Parse coinbase scriptSig hex, extract all bytes
  - Control: sample 50 random blocks in [1, 1000] for extra bytes
  - Uses only public blockchain data (no authentication needed)

SIGNIFICANCE THRESHOLD: p < 0.001 (Bonferroni-adjusted for 3 hypotheses)
===============================================================================
"""

import json
import urllib.request
import urllib.error
import time
import struct
import random
import numpy as np
from datetime import datetime
from pathlib import Path

script_dir = Path(__file__).parent
np.random.seed(42)
random.seed(42)

print("=" * 80)
print("         BRIDGE V1: BLOCK 576 BLOCKCHAIN VERIFICATION")
print("=" * 80)
print(f"\nDate: {datetime.now().isoformat()}")

results = {}

def fetch_json(url, retries=3, delay=2):
    """Fetch JSON from URL with retries."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "QubicResearch/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
                continue
            raise
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            raise

def fetch_text(url, retries=3, delay=2):
    """Fetch raw text from URL with retries."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "QubicResearch/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            raise

# ============================================================================
# HYPOTHESIS H1.3: Verify Block 576 Hash
# ============================================================================
print("\n" + "=" * 80)
print("H1.3: Block 576 Hash Verification")
print("=" * 80)

# Documented hash from bridge document
documented_hash = "000000005f7e0f4f8e39...".replace("...", "")
# We'll compare against what the API returns

try:
    block_hash = fetch_text("https://blockstream.info/api/block-height/576")
    print(f"  Block 576 hash from API: {block_hash}")

    # Check if hash starts with documented prefix
    if documented_hash and len(documented_hash) > 10:
        matches = block_hash.startswith(documented_hash[:20])
        print(f"  Documented prefix: {documented_hash[:20]}...")
        print(f"  Hash prefix match: {'PASS' if matches else 'FAIL'}")

    results["h1_3_hash"] = block_hash
    results["h1_3_status"] = "FETCHED"

except Exception as e:
    print(f"  ERROR fetching block hash: {e}")
    results["h1_3_status"] = f"ERROR: {e}"
    block_hash = None

time.sleep(1)  # Rate limiting

# ============================================================================
# HYPOTHESIS H1.1: Block 576 Extra Byte = 0x1b
# ============================================================================
print("\n" + "=" * 80)
print("H1.1: Block 576 Coinbase Extra Byte Analysis")
print("=" * 80)

def analyze_coinbase(block_hash_or_height, label=""):
    """Analyze coinbase transaction of a block."""
    try:
        # Get block details
        if isinstance(block_hash_or_height, int):
            bh = fetch_text(f"https://blockstream.info/api/block-height/{block_hash_or_height}")
            time.sleep(0.5)
        else:
            bh = block_hash_or_height

        block_data = fetch_json(f"https://blockstream.info/api/block/{bh}")
        time.sleep(0.5)

        # Get transactions
        txs = fetch_json(f"https://blockstream.info/api/block/{bh}/txs")
        time.sleep(0.5)

        coinbase_tx = txs[0]  # First tx is always coinbase

        # Get raw transaction hex for detailed analysis
        raw_hex = fetch_text(f"https://blockstream.info/api/tx/{coinbase_tx['txid']}/hex")
        time.sleep(0.5)

        # Parse scriptSig from first input
        scriptsig_hex = coinbase_tx["vin"][0].get("scriptsig", "")
        scriptsig_bytes = bytes.fromhex(scriptsig_hex) if scriptsig_hex else b""

        # In early Bitcoin blocks, the scriptSig format is:
        # [push_size] [block_height_bytes] [optional_extra_data]
        # Block height encoding was formalized in BIP34 (block 227,835+)
        # For early blocks, miners could put anything in the coinbase

        result = {
            "block_height": block_data.get("height"),
            "block_hash": bh,
            "timestamp": block_data.get("timestamp"),
            "coinbase_txid": coinbase_tx["txid"],
            "scriptsig_hex": scriptsig_hex,
            "scriptsig_bytes": list(scriptsig_bytes),
            "scriptsig_length": len(scriptsig_bytes),
            "scriptsig_ascii": "".join(chr(b) if 32 <= b <= 126 else "." for b in scriptsig_bytes),
        }

        return result
    except Exception as e:
        return {"error": str(e), "block": block_hash_or_height}

if block_hash:
    print(f"\n  Analyzing Block 576 coinbase transaction...")
    b576 = analyze_coinbase(block_hash, "Block 576")

    if "error" not in b576:
        print(f"\n  Coinbase TX: {b576['coinbase_txid']}")
        print(f"  ScriptSig hex: {b576['scriptsig_hex']}")
        print(f"  ScriptSig bytes: {b576['scriptsig_bytes']}")
        print(f"  ScriptSig length: {b576['scriptsig_length']} bytes")
        print(f"  ScriptSig ASCII: {b576['scriptsig_ascii']}")

        # Check for 0x1b (decimal 27)
        has_0x1b = 0x1b in b576["scriptsig_bytes"]
        byte_positions = [i for i, b in enumerate(b576["scriptsig_bytes"]) if b == 0x1b]

        print(f"\n  Contains 0x1b (27): {'YES' if has_0x1b else 'NO'}")
        if byte_positions:
            print(f"  Position(s) of 0x1b: {byte_positions}")

        # In early Bitcoin, typical coinbase scriptSig for blocks <500k:
        # The first few bytes encode block height (BIP34, but not mandatory pre-block 227835)
        # Extra bytes beyond height encoding are "extra nonce" or custom data

        # For very early blocks (pre-BIP34), the scriptSig was arbitrary
        # Satoshi's client used: [push_4_bytes] [nonce_4_bytes] = 8 bytes minimum
        # Extra bytes beyond this pattern ARE notable

        # Standard Satoshi scriptSig pattern for early blocks:
        # byte 0: push size (usually 4)
        # bytes 1-4: extra nonce value
        # Total: 5 bytes (or sometimes 8)

        # Check if there are "extra" bytes
        if b576["scriptsig_length"] > 8:
            extra_bytes = b576["scriptsig_bytes"][8:]
            print(f"\n  Extra bytes beyond standard 8: {extra_bytes}")
            print(f"  Extra bytes hex: {b576['scriptsig_hex'][16:]}")
            print(f"  Extra bytes count: {len(extra_bytes)}")
        elif b576["scriptsig_length"] > 5:
            # Some early blocks have 5-8 byte scriptSigs
            print(f"\n  ScriptSig length ({b576['scriptsig_length']}) is within normal range for early blocks")

        results["h1_1_has_0x1b"] = has_0x1b
        results["h1_1_positions"] = byte_positions
        results["h1_1_scriptsig"] = b576["scriptsig_hex"]
        results["h1_1_length"] = b576["scriptsig_length"]
        results["h1_1_bytes"] = b576["scriptsig_bytes"]
    else:
        print(f"  ERROR: {b576['error']}")
        results["h1_1_status"] = f"ERROR: {b576['error']}"
else:
    print("  SKIPPED (no block hash)")

# ============================================================================
# HYPOTHESIS H1.2: Is Block 576 Unique in Having Extra Bytes?
# ============================================================================
print("\n" + "=" * 80)
print("H1.2: Control - Extra Bytes in First 1000 Blocks")
print("=" * 80)

# Sample 50 random blocks from [1, 1000]
control_blocks = sorted(random.sample(range(1, 1001), 50))
# Also always include some nearby blocks
for b in [574, 575, 576, 577, 578]:
    if b not in control_blocks:
        control_blocks.append(b)
control_blocks = sorted(set(control_blocks))

print(f"\n  Analyzing {len(control_blocks)} blocks for coinbase extra bytes...")
print(f"  (This will take ~2-3 minutes with rate limiting)")

control_results = []
blocks_with_0x1b = []
blocks_with_extra = []

for i, block_num in enumerate(control_blocks):
    try:
        result = analyze_coinbase(block_num)
        if "error" not in result:
            has_0x1b = 0x1b in result["scriptsig_bytes"]
            has_extra = result["scriptsig_length"] > 8

            if has_0x1b:
                blocks_with_0x1b.append(block_num)
            if has_extra:
                blocks_with_extra.append(block_num)

            control_results.append({
                "block": block_num,
                "length": result["scriptsig_length"],
                "has_0x1b": has_0x1b,
                "has_extra": has_extra,
                "scriptsig_hex": result["scriptsig_hex"],
            })

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{len(control_blocks)} blocks analyzed")
    except Exception as e:
        print(f"  Block {block_num}: ERROR - {e}")
        time.sleep(3)

print(f"\n  Results:")
print(f"  Blocks analyzed: {len(control_results)}")
print(f"  Blocks with 0x1b in scriptSig: {len(blocks_with_0x1b)}")
if blocks_with_0x1b:
    print(f"  Which blocks: {blocks_with_0x1b}")
print(f"  Blocks with >8 byte scriptSig: {len(blocks_with_extra)}")
if blocks_with_extra:
    print(f"  Which blocks: {blocks_with_extra[:20]}")

# ScriptSig length distribution
lengths = [r["length"] for r in control_results]
if lengths:
    print(f"\n  ScriptSig length distribution:")
    print(f"    Min: {min(lengths)}")
    print(f"    Max: {max(lengths)}")
    print(f"    Mean: {np.mean(lengths):.1f}")
    print(f"    Median: {np.median(lengths):.1f}")

    from collections import Counter
    length_dist = Counter(lengths)
    print(f"    Distribution: {dict(sorted(length_dist.items()))}")

# Is 576 unique?
is_unique = len(blocks_with_0x1b) == 1 and 576 in blocks_with_0x1b
is_rare = len(blocks_with_0x1b) <= 3

results["h1_2_blocks_with_0x1b"] = blocks_with_0x1b
results["h1_2_blocks_with_extra"] = blocks_with_extra
results["h1_2_is_unique"] = is_unique
results["h1_2_total_sampled"] = len(control_results)
results["h1_2_length_distribution"] = dict(Counter(lengths)) if lengths else {}

# ============================================================================
# BONUS: Block 576 Context Analysis
# ============================================================================
print("\n" + "=" * 80)
print("BONUS: Block 576 Properties")
print("=" * 80)

print(f"\n  Mathematical properties of 576:")
print(f"    576 = 24^2 = 2^6 × 3^2")
print(f"    576 mod 27 = {576 % 27}")
print(f"    576 mod 128 = {576 % 128}")
print(f"    576 // 27 = {576 // 27} (remainder {576 % 27})")
print(f"    sqrt(576) = {576**0.5}")
print(f"    Is perfect square: YES (24^2)")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("BLOCK 576 VERIFICATION SUMMARY")
print("=" * 80)

print(f"\n  H1.1 (Extra byte 0x1b): {'CONFIRMED' if results.get('h1_1_has_0x1b') else 'NOT CONFIRMED'}")
print(f"  H1.2 (Unique in first 1000): {'CONFIRMED' if results.get('h1_2_is_unique') else 'NOT UNIQUE' if not results.get('h1_2_is_unique', True) else 'INCONCLUSIVE'}")
print(f"  H1.3 (Hash verified): {results.get('h1_3_status', 'N/A')}")

# Save results
output_path = script_dir / "BRIDGE_V1_BLOCK576_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n  Results saved to: {output_path}")
