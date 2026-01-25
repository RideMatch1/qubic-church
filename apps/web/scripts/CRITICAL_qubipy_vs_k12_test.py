#!/usr/bin/env python3
"""
CRITICAL TEST: Compare qubipy (official Qubic library) vs K12 script derivation

This test answers the CRITICAL question: Do they produce the same output?

If they DON'T match, the entire K12 derivation research is WRONG.
"""

import sys
import json
from datetime import datetime

# Results will be stored here
RESULTS = {
    "test_date": datetime.now().isoformat(),
    "tests": [],
    "summary": {}
}

def log(msg):
    print(msg)

log("=" * 70)
log("CRITICAL TEST: qubipy vs K12 Script Comparison")
log("=" * 70)

# Test seeds
TEST_SEEDS = [
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",  # 55 'a's - standard test
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",  # 55 'b's
    "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabc",  # alphabet pattern
    "qubicqubicqubicqubicqubicqubicqubicqubicqubicqubicqubic",  # qubic pattern
]

# Try to import qubipy
try:
    from qubipy.crypto.utils import (
        get_subseed_from_seed,
        get_private_key_from_subseed
    )
    QUBIPY_AVAILABLE = True
    log("✓ qubipy library loaded successfully")
except ImportError as e:
    QUBIPY_AVAILABLE = False
    log(f"✗ qubipy not available: {e}")

# Try to import KangarooTwelve
try:
    from Crypto.Hash import KangarooTwelve
    K12_AVAILABLE = True
    log("✓ KangarooTwelve (pycryptodomex) loaded successfully")
except ImportError as e:
    K12_AVAILABLE = False
    log(f"✗ KangarooTwelve not available: {e}")

log("-" * 70)

def k12_derive(seed: str) -> tuple:
    """K12 script method: seed → subseed → private key"""
    # Step 1: Map seed characters to 0-25
    seed_binary = bytes([ord(c) - ord('a') for c in seed.lower()])

    # Step 2: First K12 hash (seed → subseed)
    k12_1 = KangarooTwelve.new()
    k12_1.update(seed_binary)
    subseed = k12_1.read(32)

    # Step 3: Second K12 hash (subseed → private key)
    k12_2 = KangarooTwelve.new()
    k12_2.update(subseed)
    private_key = k12_2.read(32)

    return subseed, private_key

def qubipy_derive(seed: str) -> tuple:
    """qubipy method: seed → subseed → private key"""
    seed_bytes = seed.encode('utf-8')

    # Step 1: Get subseed
    subseed = get_subseed_from_seed(seed_bytes)

    # Step 2: Get private key from subseed
    private_key = get_private_key_from_subseed(subseed)

    return subseed, private_key

def run_tests():
    if not K12_AVAILABLE:
        log("ERROR: Cannot run tests without KangarooTwelve")
        return False

    matches = 0
    mismatches = 0

    for seed in TEST_SEEDS:
        log(f"\nTest seed: {seed[:20]}...{seed[-5:]}")

        test_result = {
            "seed": seed,
            "k12_available": K12_AVAILABLE,
            "qubipy_available": QUBIPY_AVAILABLE
        }

        # K12 derivation
        k12_subseed, k12_privkey = k12_derive(seed)
        test_result["k12_subseed"] = k12_subseed.hex()
        test_result["k12_privkey"] = k12_privkey.hex()
        log(f"  K12 subseed:  {k12_subseed.hex()[:32]}...")
        log(f"  K12 privkey:  {k12_privkey.hex()[:32]}...")

        if QUBIPY_AVAILABLE:
            try:
                qub_subseed, qub_privkey = qubipy_derive(seed)
                test_result["qubipy_subseed"] = qub_subseed.hex()
                test_result["qubipy_privkey"] = qub_privkey.hex()
                log(f"  Qub subseed:  {qub_subseed.hex()[:32]}...")
                log(f"  Qub privkey:  {qub_privkey.hex()[:32]}...")

                # Compare
                subseed_match = k12_subseed == qub_subseed
                privkey_match = k12_privkey == qub_privkey
                test_result["subseed_match"] = subseed_match
                test_result["privkey_match"] = privkey_match

                if subseed_match and privkey_match:
                    log(f"  ✓ MATCH! K12 and qubipy produce IDENTICAL output")
                    matches += 1
                else:
                    log(f"  ✗ MISMATCH!")
                    log(f"    Subseed match: {subseed_match}")
                    log(f"    Privkey match: {privkey_match}")
                    mismatches += 1
            except Exception as e:
                log(f"  ✗ qubipy error: {e}")
                test_result["qubipy_error"] = str(e)
                mismatches += 1
        else:
            log(f"  (qubipy not available for comparison)")
            test_result["qubipy_error"] = "not available"

        RESULTS["tests"].append(test_result)

    return matches, mismatches

if __name__ == "__main__":
    log("\nRunning comparison tests...")
    log("-" * 70)

    if K12_AVAILABLE:
        matches, mismatches = run_tests()

        log("\n" + "=" * 70)
        log("FINAL RESULTS")
        log("=" * 70)

        RESULTS["summary"]["total_tests"] = len(TEST_SEEDS)
        RESULTS["summary"]["k12_available"] = K12_AVAILABLE
        RESULTS["summary"]["qubipy_available"] = QUBIPY_AVAILABLE

        if QUBIPY_AVAILABLE:
            RESULTS["summary"]["matches"] = matches
            RESULTS["summary"]["mismatches"] = mismatches

            if mismatches == 0:
                log(f"✓ ALL {matches} TESTS PASSED - K12 and qubipy are IDENTICAL")
                log("✓ The K12 derivation formula is VERIFIED")
                RESULTS["summary"]["verdict"] = "VERIFIED - K12 matches qubipy"
            else:
                log(f"✗ {mismatches} TESTS FAILED - K12 and qubipy DIFFER!")
                log("✗ The K12 derivation formula is WRONG or INCOMPLETE")
                RESULTS["summary"]["verdict"] = "FAILED - K12 differs from qubipy"
        else:
            log("⚠ Cannot verify - qubipy not available")
            log("K12 outputs generated but NOT compared to official implementation")
            RESULTS["summary"]["verdict"] = "UNVERIFIED - qubipy not available"
    else:
        log("ERROR: KangarooTwelve not available - cannot run tests")
        RESULTS["summary"]["verdict"] = "ERROR - K12 not available"

    # Save results
    output_file = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/QUBIPY_VS_K12_TEST_RESULTS.json"
    with open(output_file, 'w') as f:
        json.dump(RESULTS, f, indent=2)
    log(f"\nResults saved to: {output_file}")
